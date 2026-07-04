#!/usr/bin/env python3
"""
ABC Model Overlay — Q2b/Q3 variant intersection with ABC enhancer predictions.

Source: Nasser et al. 2021 (Nature 593) — Activity-by-Contact Model.
Primary: streaming download + gzip filtering (~2.5GB file).
Fallback: ENCODE Portal REST API (rE2G predictions for HBB/K562).

ПОЧЕМУ ABC Model: ABC predictions are experimentally validated enhancer-gene
links. If Q2b variants (structural blind spots) overlap ABC enhancers at
higher rates than Q3 variants, that's independent evidence that Q2b disrupts
real regulatory elements, not arbitrary genomic positions.
"""

import gzip
import json
import zlib
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

BASE = Path(r"D:\ДНК")
RESULTS = BASE / "results"
ANALYSIS = BASE / "analysis"
DATA_ABC = BASE / "data" / "abc"

ABC_URL = (
    "https://ftp.broadinstitute.org/outgoing/lincRNA/ABC/"
    "AllPredictions.AvgHiC.ABC0.015.minus150.ForABCPaperV3.txt.gz"
)
ABC_LOCAL = DATA_ABC / "ABC_HBB_K562.tsv"

Q2B_PATH = ANALYSIS / "Q2b_true_blindspots.csv"
ATLAS_PATH = RESULTS / "HBB_Unified_Atlas_95kb.csv"

OUTPUT_CSV = ANALYSIS / "abc_q2b_overlap.csv"
OUTPUT_JSON = ANALYSIS / "abc_q2b_summary.json"

LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20


# ── Download + filter ABC ────────────────────────────────────────


def download_abc_streaming(url: str, output: Path, timeout: int = 60) -> bool:
    """Stream-download ABC gzip file, filtering for HBB+K562 rows on the fly."""
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading ABC predictions from {url}...")

    try:
        req = Request(
            url,
            headers={
                "User-Agent": "ARCHCODE-pipeline/1.0",
                "Accept-Encoding": "identity",
            },
        )
        with urlopen(req, timeout=timeout) as resp:
            decomp = zlib.decompressobj(wbits=47)  # gzip auto-detect
            text_buf = ""
            header = None
            gene_idx = cell_idx = None
            rows = 0
            total_bytes = 0

            with open(output, "w", encoding="utf-8") as f:
                while True:
                    chunk = resp.read(131072)
                    if not chunk:
                        break
                    total_bytes += len(chunk)

                    try:
                        text_buf += decomp.decompress(chunk).decode("utf-8", errors="replace")
                    except zlib.error:
                        text_buf += chunk.decode("utf-8", errors="replace")

                    nl = text_buf.rfind("\n")
                    if nl == -1:
                        continue

                    lines = text_buf[: nl + 1]
                    text_buf = text_buf[nl + 1 :]

                    for line in lines.splitlines():
                        if not line:
                            continue
                        if header is None:
                            header = line
                            cols = {c.strip(): i for i, c in enumerate(line.split("\t"))}
                            gene_idx = cols.get("TargetGene")
                            cell_idx = cols.get("CellType")
                            f.write(header + "\n")
                            print(
                                f"  Header parsed: {len(cols)} columns, gene@{gene_idx}, cell@{cell_idx}"
                            )
                            continue
                        if gene_idx is None or cell_idx is None:
                            continue
                        parts = line.split("\t")
                        if len(parts) <= max(gene_idx, cell_idx):
                            continue
                        if "HBB" in parts[gene_idx] and "K562" in parts[cell_idx]:
                            f.write(line + "\n")
                            rows += 1

                    if total_bytes % (100 * 1024 * 1024) < 131072:
                        print(f"  {total_bytes // (1024 * 1024)} MB read, {rows} HBB/K562 rows")

            print(f"Download complete: {total_bytes // (1024 * 1024)} MB, {rows} rows saved")
            return rows > 0

    except (URLError, TimeoutError, OSError) as e:
        print(f"Download failed: {e}")
        return False


# ── ENCODE API fallback ──────────────────────────────────────────


def fetch_encode_re2g() -> list[dict]:
    """Fetch rE2G enhancer-gene predictions from ENCODE Portal for HBB/K562."""
    import urllib.request

    url = (
        "https://www.encodeproject.org/search/"
        "?type=RegulatoryElementToGeneLink"
        "&target_gene.symbol=HBB"
        "&biosample_ontology.term_name=K562"
        "&format=json&limit=all"
    )
    print(f"ENCODE API fallback: {url}")
    try:
        req = Request(url, headers={"Accept": "application/json", "User-Agent": "ARCHCODE/1.0"})
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        hits = data.get("@graph", [])
        print(f"  ENCODE returned {len(hits)} hits")

        regions = []
        for h in hits:
            reg = h.get("regulatory_element", {})
            chrom = reg.get("chromosome", "")
            start = reg.get("start", 0)
            end = reg.get("end", 0)
            score = h.get("score", 0.0) or 0.0
            if chrom and start and end:
                regions.append(
                    {
                        "chrom": chrom if chrom.startswith("chr") else f"chr{chrom}",
                        "start": int(start),
                        "end": int(end),
                        "abc_score": float(score),
                        "name": h.get("@id", "encode_re2g"),
                    }
                )
        print(f"  Parsed {len(regions)} enhancer regions")
        return regions
    except Exception as e:
        print(f"  ENCODE API failed: {e}")
        return []


# ── Load ABC from TSV ────────────────────────────────────────────


def load_abc_regions(path: Path) -> list[dict]:
    """Load pre-filtered ABC predictions from local TSV."""
    df = pd.read_csv(path, sep="\t", low_memory=False)
    print(f"ABC TSV: {len(df)} rows, columns: {df.columns.tolist()[:8]}")

    # Column name mapping (ABC file versions differ)
    col_map = {}
    for target, aliases in {
        "chrom": ["chr", "chrom", "#chr"],
        "start": ["start", "Start"],
        "end": ["end", "End"],
        "abc_score": ["ABC.Score", "ABCScore", "abc_score", "score"],
        "name": ["name", "Name", "ElementName"],
    }.items():
        for a in aliases:
            if a in df.columns:
                col_map[target] = a
                break

    regions = []
    for _, row in df.iterrows():
        try:
            c = str(row[col_map.get("chrom", df.columns[0])])
            regions.append(
                {
                    "chrom": c if c.startswith("chr") else f"chr{c}",
                    "start": int(row[col_map.get("start", df.columns[1])]),
                    "end": int(row[col_map.get("end", df.columns[2])]),
                    "abc_score": float(row.get(col_map.get("abc_score", ""), 0) or 0),
                    "name": str(row.get(col_map.get("name", ""), "abc")),
                }
            )
        except (ValueError, KeyError):
            pass
    return regions


# ── Load variants ────────────────────────────────────────────────


def load_variants():
    """Load Q2b and Q3 HBB variants."""
    # Q2b from true blindspots file
    q2b_all = pd.read_csv(Q2B_PATH)
    q2b = q2b_all[q2b_all["Locus"] == "HBB"].copy()
    print(f"Q2b HBB: {len(q2b)} variants")

    # Q3 from HBB atlas — need to recompute quadrants
    atlas = pd.read_csv(ATLAS_PATH)
    atlas["ARCHCODE_HIGH"] = atlas["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD
    vep_high = atlas["VEP_Score"] >= VEP_THRESHOLD
    cadd = pd.to_numeric(atlas["CADD_Phred"], errors="coerce")
    atlas["SEQ_HIGH"] = vep_high | (cadd >= CADD_THRESHOLD).fillna(False)
    q3 = atlas[(~atlas["ARCHCODE_HIGH"]) & (atlas["SEQ_HIGH"])].copy()
    q3 = q3.rename(columns={"Position_GRCh38": "Position"})
    print(f"Q3 HBB: {len(q3)} variants")

    return q2b, q3


# ── Overlap computation ──────────────────────────────────────────


def compute_overlap(q2b, q3, regions):
    """Compute overlap stats and Fisher exact test."""

    def count_overlaps(df, pos_col, chrom="chr11"):
        records = []
        n_in = 0
        scores = []
        for _, row in df.iterrows():
            pos = int(row[pos_col])
            # BED is 0-based; VCF/ClinVar is 1-based
            bed_pos = pos - 1
            hits = [r for r in regions if r["chrom"] == chrom and r["start"] <= bed_pos < r["end"]]
            in_abc = len(hits) > 0
            best = max((r["abc_score"] for r in hits), default=None)
            if in_abc:
                n_in += 1
                if best is not None:
                    scores.append(best)
            records.append(
                {
                    "ClinVar_ID": row.get("ClinVar_ID", ""),
                    "Position": pos,
                    "In_ABC": in_abc,
                    "N_ABC_Overlaps": len(hits),
                    "Best_ABC_Score": best,
                }
            )
        return n_in, scores, records

    n_q2b_in, scores_q2b, recs_q2b = count_overlaps(q2b, "Position")
    n_q3_in, scores_q3, recs_q3 = count_overlaps(q3, "Position")

    n_q2b = len(q2b)
    n_q3 = len(q3)

    # Fisher exact test
    table = [[n_q2b_in, n_q2b - n_q2b_in], [n_q3_in, n_q3 - n_q3_in]]
    odds, p = fisher_exact(table, alternative="greater")

    print(f"\n{'=' * 60}")
    print("ABC MODEL OVERLAY RESULTS")
    print(f"{'=' * 60}")
    print(f"ABC enhancer regions: {len(regions)}")
    print(f"Q2b in ABC: {n_q2b_in}/{n_q2b} ({n_q2b_in / n_q2b * 100:.1f}%)" if n_q2b else "Q2b: 0")
    print(f"Q3  in ABC: {n_q3_in}/{n_q3} ({n_q3_in / n_q3 * 100:.1f}%)" if n_q3 else "Q3: 0")
    print(f"Fisher exact (Q2b > Q3): OR={odds:.3f}, p={p:.4e}")
    if scores_q2b:
        print(f"Mean ABC score (Q2b overlaps): {np.mean(scores_q2b):.4f}")
    if scores_q3:
        print(f"Mean ABC score (Q3 overlaps): {np.mean(scores_q3):.4f}")

    # Combine records
    for r in recs_q2b:
        r["Group"] = "Q2b"
    for r in recs_q3:
        r["Group"] = "Q3"
    detail = pd.DataFrame(recs_q2b + recs_q3)

    summary = {
        "n_abc_regions": len(regions),
        "n_q2b_total": n_q2b,
        "n_q2b_in_abc": n_q2b_in,
        "frac_q2b_in_abc": round(n_q2b_in / n_q2b, 4) if n_q2b else 0,
        "n_q3_total": n_q3,
        "n_q3_in_abc": n_q3_in,
        "frac_q3_in_abc": round(n_q3_in / n_q3, 4) if n_q3 else 0,
        "fisher_odds_ratio": round(odds, 4),
        "fisher_p_value": float(f"{p:.4e}"),
        "mean_abc_q2b": round(np.mean(scores_q2b), 4) if scores_q2b else None,
        "mean_abc_q3": round(np.mean(scores_q3), 4) if scores_q3 else None,
        "reference": "Nasser et al. 2021, Nature 593 (ABC Model)",
    }

    return summary, detail


# ── Main ─────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("ABC MODEL OVERLAY — Q2b vs Q3 enrichment")
    print("=" * 60)

    DATA_ABC.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    # Step 1: Get ABC regions
    regions = []
    source = "none"

    if ABC_LOCAL.exists() and ABC_LOCAL.stat().st_size > 100:
        print(f"Using cached ABC file: {ABC_LOCAL}")
        regions = load_abc_regions(ABC_LOCAL)
        source = "ABC_local_cache"

    if not regions:
        success = download_abc_streaming(ABC_URL, ABC_LOCAL, timeout=120)
        if success:
            regions = load_abc_regions(ABC_LOCAL)
            source = "ABC_download"

    if not regions:
        print("Bulk download failed, trying ENCODE API fallback...")
        regions = fetch_encode_re2g()
        source = "ENCODE_API"

    if not regions:
        print("\nWARNING: No ABC data available. Creating empty results.")
        print(f"Manual download: {ABC_URL}")
        print(f"Save filtered output to: {ABC_LOCAL}")
        source = "no_data"

    print(f"\nABC regions loaded: {len(regions)} (source: {source})")

    # Step 2: Load variants
    q2b, q3 = load_variants()

    # Step 3: Compute overlap
    summary, detail = compute_overlap(q2b, q3, regions)
    summary["data_source"] = source

    # Step 4: Save
    detail.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved: {OUTPUT_CSV} ({len(detail)} rows)")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
