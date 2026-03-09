#!/usr/bin/env python3
"""
ENCODE rE2G Overlay — Q2b vs Q3 variant intersection with ABC/rE2G enhancer predictions.

Source: ENCODE rE2G (Engreitz lab, Stanford) — ENCSR627ANP / ENCFF976OKL
Based on: Nasser et al. 2021, Nature 593 (ABC Model)

ПОЧЕМУ rE2G: These are experimentally-informed enhancer-gene link predictions.
If Q2b variants (structural blind spots) overlap HBB-linked enhancers at higher
rates than Q3 variants, that is independent evidence that Q2b disrupts real
regulatory elements — not arbitrary genomic positions.
"""

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

BASE = Path(r"D:\ДНК")
ANALYSIS = BASE / "analysis"
RESULTS = BASE / "results"
RE2G_FILE = BASE / "data" / "abc" / "ENCFF976OKL.bed.gz"

Q2B_PATH = ANALYSIS / "Q2b_true_blindspots.csv"
ATLAS_PATH = RESULTS / "HBB_Unified_Atlas_95kb.csv"

OUTPUT_CSV = ANALYSIS / "abc_q2b_overlap.csv"
OUTPUT_JSON = ANALYSIS / "abc_q2b_summary.json"

LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20


def load_re2g_regions(path: Path):
    """Load ENCODE rE2G enhancer regions from gzipped BED file."""
    hbb_regions = []
    broad_regions = []

    with gzip.open(path, "rt") as f:
        header = next(f).rstrip().split("\t")
        print(f"rE2G columns: {header[:8]}...")

        for line in f:
            parts = line.rstrip().split("\t")
            chrom = parts[0]
            start = int(parts[1])
            end = int(parts[2])
            gene = parts[5]
            re2g_score = float(parts[-1])  # Score column
            abc_feat = float(parts[13])  # ABC.Score.Feature
            elem_class = parts[4]
            is_promoter = parts[8] == "TRUE"

            # HBB-targeted enhancers
            if gene == "HBB":
                hbb_regions.append(
                    {
                        "chrom": chrom,
                        "start": start,
                        "end": end,
                        "name": parts[3],
                        "class": elem_class,
                        "gene": gene,
                        "abc_score_feature": abc_feat,
                        "re2g_score": re2g_score,
                        "is_self_promoter": is_promoter,
                    }
                )

            # All enhancers in HBB locus (5.15-5.35 Mb)
            if chrom == "chr11" and end >= 5150000 and start <= 5350000:
                broad_regions.append(
                    {
                        "chrom": chrom,
                        "start": start,
                        "end": end,
                        "name": parts[3],
                    }
                )

    return hbb_regions, broad_regions


def load_variants():
    """Load Q2b (HBB only) and Q3 (HBB) variants."""
    # Q2b from blindspots
    q2b_all = pd.read_csv(Q2B_PATH)
    q2b = q2b_all[q2b_all["Locus"] == "HBB"].copy()
    print(
        f"Q2b HBB: {len(q2b)} variants, positions {q2b['Position'].min()}-{q2b['Position'].max()}"
    )

    # Q3 from atlas: LSSIM >= 0.95 AND (VEP >= 0.5 OR CADD >= 20)
    atlas = pd.read_csv(ATLAS_PATH)
    lssim = atlas["ARCHCODE_LSSIM"]
    vep = atlas["VEP_Score"]
    cadd = pd.to_numeric(atlas["CADD_Phred"], errors="coerce")

    archcode_high = lssim < LSSIM_THRESHOLD
    seq_high = (vep >= VEP_THRESHOLD) | (cadd >= CADD_THRESHOLD).fillna(False)

    q3 = atlas[(~archcode_high) & seq_high].copy()
    q3 = q3.rename(columns={"Position_GRCh38": "Position"})
    print(f"Q3 HBB: {len(q3)} variants, positions {q3['Position'].min()}-{q3['Position'].max()}")

    return q2b, q3


def count_overlaps(positions, regions, chrom="chr11"):
    """Count how many positions fall within enhancer regions (BED 0-based)."""
    n_in = 0
    details = []
    for pos in positions:
        bed_pos = pos - 1  # ClinVar 1-based -> BED 0-based
        hits = [r for r in regions if r["chrom"] == chrom and r["start"] <= bed_pos < r["end"]]
        in_enh = len(hits) > 0
        if in_enh:
            n_in += 1
        details.append(
            {
                "Position": pos,
                "In_Enhancer": in_enh,
                "N_Overlaps": len(hits),
                "Enhancer_Names": ";".join(h["name"] for h in hits) if hits else "",
            }
        )
    return n_in, details


def do_fisher(n_in_a, n_total_a, n_in_b, n_total_b, label):
    """Fisher exact test: is Q2b enriched in enhancers vs Q3?"""
    table = [[n_in_a, n_total_a - n_in_a], [n_in_b, n_total_b - n_in_b]]
    odds, p = fisher_exact(table, alternative="greater")
    pct_a = n_in_a / n_total_a * 100 if n_total_a else 0
    pct_b = n_in_b / n_total_b * 100 if n_total_b else 0
    print(f"\n{label}:")
    print(f"  Q2b in enhancers: {n_in_a}/{n_total_a} ({pct_a:.1f}%)")
    print(f"  Q3  in enhancers: {n_in_b}/{n_total_b} ({pct_b:.1f}%)")
    print(f"  Contingency: {table}")
    print(f"  Fisher exact (Q2b > Q3): OR={odds:.4f}, p={p:.4e}")
    return odds, p, table


def main():
    print("=" * 60)
    print("ENCODE rE2G OVERLAY -- Q2b vs Q3 enrichment")
    print("=" * 60)

    # Step 1: Load enhancer regions
    hbb_regions, broad_regions = load_re2g_regions(RE2G_FILE)
    print(f"\nHBB-targeted enhancers: {len(hbb_regions)}")
    for r in hbb_regions:
        tag = " [PROMOTER]" if r["is_self_promoter"] else ""
        print(
            f"  {r['name']}  {r['class']}{tag}  ABC={r['abc_score_feature']:.4f}  rE2G={r['re2g_score']:.4f}"
        )
    print(f"All locus enhancers (5.15-5.35Mb): {len(broad_regions)}")

    # Step 2: Load variants
    q2b, q3 = load_variants()

    # Step 3: Compute overlaps
    n_q2b_hbb, det_q2b_hbb = count_overlaps(q2b["Position"].tolist(), hbb_regions)
    n_q3_hbb, det_q3_hbb = count_overlaps(q3["Position"].tolist(), hbb_regions)
    n_q2b_broad, det_q2b_broad = count_overlaps(q2b["Position"].tolist(), broad_regions)
    n_q3_broad, det_q3_broad = count_overlaps(q3["Position"].tolist(), broad_regions)

    # Step 4: Fisher tests
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    or_hbb, p_hbb, tab_hbb = do_fisher(
        n_q2b_hbb, len(q2b), n_q3_hbb, len(q3), "TEST 1: HBB-targeted rE2G enhancers (20 regions)"
    )
    or_broad, p_broad, tab_broad = do_fisher(
        n_q2b_broad,
        len(q2b),
        n_q3_broad,
        len(q3),
        "TEST 2: All locus enhancers (134 regions, 5.15-5.35Mb)",
    )

    # Step 5: Build per-variant detail CSV
    recs = []
    for _, row in q2b.iterrows():
        pos = row["Position"]
        d_hbb = next((d for d in det_q2b_hbb if d["Position"] == pos), {})
        d_broad = next((d for d in det_q2b_broad if d["Position"] == pos), {})
        bed_pos = pos - 1
        hits = [
            r for r in hbb_regions if r["chrom"] == "chr11" and r["start"] <= bed_pos < r["end"]
        ]
        best_re2g = max((h["re2g_score"] for h in hits), default=None)
        best_abc = max((h["abc_score_feature"] for h in hits), default=None)
        recs.append(
            {
                "ClinVar_ID": row.get("ClinVar_ID", ""),
                "Position": pos,
                "Group": "Q2b",
                "In_HBB_Enhancer": d_hbb.get("In_Enhancer", False),
                "In_Locus_Enhancer": d_broad.get("In_Enhancer", False),
                "N_HBB_Overlaps": d_hbb.get("N_Overlaps", 0),
                "Best_rE2G_Score": best_re2g,
                "Best_ABC_Score": best_abc,
                "Enhancer_Names": d_hbb.get("Enhancer_Names", ""),
            }
        )

    for _, row in q3.iterrows():
        pos = row["Position"]
        d_hbb = next((d for d in det_q3_hbb if d["Position"] == pos), {})
        d_broad = next((d for d in det_q3_broad if d["Position"] == pos), {})
        bed_pos = pos - 1
        hits = [
            r for r in hbb_regions if r["chrom"] == "chr11" and r["start"] <= bed_pos < r["end"]
        ]
        best_re2g = max((h["re2g_score"] for h in hits), default=None)
        best_abc = max((h["abc_score_feature"] for h in hits), default=None)
        recs.append(
            {
                "ClinVar_ID": row.get("ClinVar_ID", ""),
                "Position": pos,
                "Group": "Q3",
                "In_HBB_Enhancer": d_hbb.get("In_Enhancer", False),
                "In_Locus_Enhancer": d_broad.get("In_Enhancer", False),
                "N_HBB_Overlaps": d_hbb.get("N_Overlaps", 0),
                "Best_rE2G_Score": best_re2g,
                "Best_ABC_Score": best_abc,
                "Enhancer_Names": d_hbb.get("Enhancer_Names", ""),
            }
        )

    detail_df = pd.DataFrame(recs)
    detail_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved: {OUTPUT_CSV} ({len(detail_df)} rows)")

    # Print hits
    q2b_hits = detail_df[(detail_df["Group"] == "Q2b") & (detail_df["In_HBB_Enhancer"])]
    if len(q2b_hits):
        print("\nQ2b variants IN HBB enhancers:")
        for _, h in q2b_hits.iterrows():
            print(
                f"  {h['ClinVar_ID']} pos={h['Position']} rE2G={h['Best_rE2G_Score']:.4f} enh={h['Enhancer_Names']}"
            )
    else:
        print("\nNo Q2b variants overlap HBB-targeted enhancers.")

    q3_hits = detail_df[(detail_df["Group"] == "Q3") & (detail_df["In_HBB_Enhancer"])]
    print(f"Q3 variants in HBB enhancers: {len(q3_hits)}")
    if len(q3_hits):
        for _, h in q3_hits.iterrows():
            print(f"  {h['ClinVar_ID']} pos={h['Position']} rE2G={h['Best_rE2G_Score']:.4f}")

    # Step 6: Summary JSON
    q2b_re2g = [
        r["Best_rE2G_Score"]
        for r in recs
        if r["Group"] == "Q2b" and r["Best_rE2G_Score"] is not None
    ]
    q3_re2g = [
        r["Best_rE2G_Score"]
        for r in recs
        if r["Group"] == "Q3" and r["Best_rE2G_Score"] is not None
    ]

    summary = {
        "data_source": "ENCODE_rE2G_ENCSR627ANP_ENCFF976OKL",
        "file_description": "Thresholded element-gene links, ENCODE-rE2G, K562 DNase-seq",
        "reference": "Nasser et al. 2021, Nature 593; ENCODE rE2G (Engreitz lab, Stanford)",
        "genome_assembly": "GRCh38",
        "n_hbb_enhancer_regions": len(hbb_regions),
        "n_locus_enhancer_regions": len(broad_regions),
        "hbb_enhancer_test": {
            "n_q2b_total": int(len(q2b)),
            "n_q2b_in_enhancer": int(n_q2b_hbb),
            "frac_q2b": round(n_q2b_hbb / len(q2b), 4) if len(q2b) else 0,
            "n_q3_total": int(len(q3)),
            "n_q3_in_enhancer": int(n_q3_hbb),
            "frac_q3": round(n_q3_hbb / len(q3), 4) if len(q3) else 0,
            "fisher_odds_ratio": round(or_hbb, 4) if np.isfinite(or_hbb) else str(or_hbb),
            "fisher_p_value": float(f"{p_hbb:.6e}"),
            "contingency_table": [[int(x) for x in row] for row in tab_hbb],
        },
        "broad_locus_test": {
            "n_q2b_in_enhancer": int(n_q2b_broad),
            "frac_q2b": round(n_q2b_broad / len(q2b), 4) if len(q2b) else 0,
            "n_q3_in_enhancer": int(n_q3_broad),
            "frac_q3": round(n_q3_broad / len(q3), 4) if len(q3) else 0,
            "fisher_odds_ratio": round(or_broad, 4) if np.isfinite(or_broad) else str(or_broad),
            "fisher_p_value": float(f"{p_broad:.6e}"),
            "contingency_table": [[int(x) for x in row] for row in tab_broad],
        },
        "mean_re2g_q2b_overlaps": round(np.mean(q2b_re2g), 4) if q2b_re2g else None,
        "mean_re2g_q3_overlaps": round(np.mean(q3_re2g), 4) if q3_re2g else None,
        "enhancer_regions": [
            {
                "name": r["name"],
                "start": r["start"],
                "end": r["end"],
                "class": r["class"],
                "abc_score_feature": round(r["abc_score_feature"], 6),
                "re2g_score": round(r["re2g_score"], 6),
                "is_self_promoter": r["is_self_promoter"],
            }
            for r in sorted(hbb_regions, key=lambda x: x["start"])
        ],
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved: {OUTPUT_JSON}")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
