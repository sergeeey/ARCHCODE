"""
GWAS Catalog Overlay для ARCHCODE — пересечение GWAS-хитов с окнами 9 локусов
и детекция перекрытий со структурными слепыми пятнами (Q2b варианты, Class B).

Метод: EBI GWAS Catalog REST API per-locus (9 запросов вместо загрузки 300MB TSV).
Endpoint: /gwas/rest/api/singleNucleotidePolymorphisms/search/findByChromBpLocationRange

Запуск: python scripts/gwas_catalog_overlay.py
"""

import csv
import json
import pathlib
import sys
import time
from dataclasses import dataclass, field

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import requests

BASE_DIR = pathlib.Path("D:/ДНК")
ANALYSIS_DIR = BASE_DIR / "analysis"
FIGURES_DIR = BASE_DIR / "figures" / "taxonomy"
CACHE_DIR = BASE_DIR / "data" / "gwas_cache"

Q2_CSV = ANALYSIS_DIR / "Q2_structural_blindspots.csv"
OUTPUT_JSON = ANALYSIS_DIR / "gwas_archcode_overlay.json"
OUTPUT_CSV = ANALYSIS_DIR / "gwas_archcode_overlap.csv"
OUTPUT_PDF = FIGURES_DIR / "fig_gwas_overlay.pdf"
OUTPUT_PNG = FIGURES_DIR / "fig_gwas_overlay.png"

GWAS_API_BASE = (
    "https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms"
    "/search/findByChromBpLocationRange"
)
GWAS_API_PAGE_SIZE = 500

POSITION_WINDOW_BP = 1000

# ARCHCODE locus windows (GRCh38)
LOCUS_WINDOWS: dict[str, tuple[str, int, int]] = {
    "HBB": ("11", 5_225_000, 5_320_000),
    "BRCA1": ("17", 42_900_000, 43_300_000),
    "TP53": ("17", 7_550_000, 7_750_000),
    "TERT": ("5", 1_150_000, 1_450_000),
    "MLH1": ("3", 36_900_000, 37_100_000),
    "CFTR": ("7", 117_100_000, 117_400_000),
    "SCN5A": ("3", 38_500_000, 38_750_000),
    "GJB2": ("13", 20_150_000, 20_250_000),
    "LDLR": ("19", 11_050_000, 11_300_000),
}

COLOR_NORMAL = "#4C72B0"
COLOR_BLINDSPOT = "#DD4444"


@dataclass
class GwasSNP:
    chr_id: str
    chr_pos: int
    rsid: str
    traits: list[str]
    risk_allele: str = ""
    p_value: str = ""
    mapped_gene: str = ""


@dataclass
class LocusResult:
    locus: str
    chrom: str
    start: int
    end: int
    gwas_hits: list[GwasSNP] = field(default_factory=list)
    blindspot_overlaps: list[dict] = field(default_factory=list)

    @property
    def n_gwas(self) -> int:
        return len(self.gwas_hits)

    @property
    def n_unique_rsids(self) -> int:
        return len({s.rsid for s in self.gwas_hits})

    @property
    def n_blindspot(self) -> int:
        return len(self.blindspot_overlaps)


def fetch_gwas_locus(chrom: str, start: int, end: int, locus_name: str) -> list[GwasSNP]:
    """Fetch GWAS SNPs for a locus via EBI REST API with pagination."""
    cache_file = CACHE_DIR / f"gwas_{locus_name}_{chrom}_{start}_{end}.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Use cache if exists and recent
    if cache_file.exists():
        age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
        if age_hours < 24:
            print(f"  [{locus_name}] Using cache ({age_hours:.1f}h old)")
            with open(cache_file) as f:
                cached = json.load(f)
            return [GwasSNP(**s) for s in cached]

    all_snps = []
    page = 0

    while True:
        url = f"{GWAS_API_BASE}?chrom={chrom}&bpStart={start}&bpEnd={end}&size={GWAS_API_PAGE_SIZE}&page={page}"
        print(f"  [{locus_name}] API page {page}...")

        try:
            resp = requests.get(url, timeout=60, headers={"Accept": "application/json"})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [{locus_name}] API error: {e}")
            break

        snps_data = data.get("_embedded", {}).get("singleNucleotidePolymorphisms", [])
        page_info = data.get("page", {})

        for snp_raw in snps_data:
            rsid = snp_raw.get("rsId", "")

            # Extract positions from locations
            positions = []
            for loc in snp_raw.get("locations", []):
                pos = loc.get("chromosomePosition")
                if pos is not None:
                    positions.append(int(pos))

            # Extract traits from associations
            traits = set()
            risk_alleles = []
            p_values = []

            for assoc in snp_raw.get("_embedded", {}).get("associations", []):
                # Trait from efoTraits
                for trait in assoc.get("efoTraits", []):
                    traits.add(trait.get("trait", ""))
                # P-value
                pv = assoc.get("pvalue")
                if pv:
                    p_values.append(str(pv))
                # Risk allele
                for ra in assoc.get("riskAlleles", []):
                    risk_alleles.append(ra.get("riskAlleleName", ""))

            for pos in positions:
                if start <= pos <= end:
                    all_snps.append(
                        GwasSNP(
                            chr_id=chrom,
                            chr_pos=pos,
                            rsid=rsid,
                            traits=list(traits),
                            risk_allele=risk_alleles[0] if risk_alleles else "",
                            p_value=p_values[0] if p_values else "",
                            mapped_gene=snp_raw.get("_embedded", {})
                            .get("genes", [{}])[0]
                            .get("geneName", "")
                            if snp_raw.get("_embedded", {}).get("genes")
                            else "",
                        )
                    )

        total_pages = page_info.get("totalPages", 1)
        if page + 1 >= total_pages:
            break
        page += 1
        time.sleep(0.5)

    # Cache results
    cache_data = [
        {
            "chr_id": s.chr_id,
            "chr_pos": s.chr_pos,
            "rsid": s.rsid,
            "traits": s.traits,
            "risk_allele": s.risk_allele,
            "p_value": s.p_value,
            "mapped_gene": s.mapped_gene,
        }
        for s in all_snps
    ]
    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"  [{locus_name}] {len(all_snps)} SNPs found, cached")
    return all_snps


def load_q2_positions(q2_csv: pathlib.Path) -> dict[str, list[int]]:
    """Load Q2 structural blindspot positions."""
    q2_by_locus: dict[str, list[int]] = {}
    if not q2_csv.exists():
        print(f"WARNING: Q2 CSV not found: {q2_csv}")
        return q2_by_locus

    with open(q2_csv, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            locus = (row.get("Locus", "") or "").strip().upper()
            pos_raw = row.get("Position_GRCh38", "") or ""
            try:
                pos = int(float(pos_raw.split(";")[0].strip()))
            except (ValueError, TypeError):
                continue
            if pos and locus:
                q2_by_locus.setdefault(locus, []).append(pos)

    for locus, positions in q2_by_locus.items():
        print(f"  Q2 loaded: {locus} = {len(positions)} positions")
    return q2_by_locus


def find_blindspot_overlaps(
    results: dict[str, LocusResult],
    q2_by_locus: dict[str, list[int]],
    window_bp: int = POSITION_WINDOW_BP,
) -> None:
    """Find GWAS hits within ±window_bp of Q2 blind spot positions."""
    for locus_name, result in results.items():
        q2_positions = q2_by_locus.get(locus_name, [])
        if not q2_positions:
            continue

        for snp in result.gwas_hits:
            for q2_pos in q2_positions:
                if abs(snp.chr_pos - q2_pos) <= window_bp:
                    result.blindspot_overlaps.append(
                        {
                            "gwas_rsid": snp.rsid,
                            "gwas_pos": snp.chr_pos,
                            "gwas_traits": snp.traits,
                            "gwas_p_value": snp.p_value,
                            "q2_pos": q2_pos,
                            "distance_bp": abs(snp.chr_pos - q2_pos),
                            "locus": locus_name,
                        }
                    )
                    break


def generate_figure(results: dict[str, LocusResult]) -> None:
    """Generate stacked bar chart: GWAS hits per locus with blind-spot highlights."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    loci = list(results.keys())
    n_gwas = [results[name].n_gwas for name in loci]
    n_bs = [results[name].n_blindspot for name in loci]
    n_normal = [g - b for g, b in zip(n_gwas, n_bs)]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(loci))

    ax.bar(x, n_normal, color=COLOR_NORMAL, label="GWAS hits", width=0.6)
    ax.bar(
        x,
        n_bs,
        bottom=n_normal,
        color=COLOR_BLINDSPOT,
        label=f"Overlaps with Q2 blind spots (±{POSITION_WINDOW_BP}bp)",
        width=0.6,
    )

    for i, (total, bs) in enumerate(zip(n_gwas, n_bs)):
        if total > 0:
            ax.text(
                i, total + 0.3, str(total), ha="center", va="bottom", fontsize=9, fontweight="bold"
            )
        if bs > 0:
            ax.text(
                i,
                n_normal[i] + bs / 2,
                str(bs),
                ha="center",
                va="center",
                fontsize=8,
                color="white",
                fontweight="bold",
            )

    ax.set_xticks(list(x))
    ax.set_xticklabels(loci, fontsize=11)
    ax.set_ylabel("Number of GWAS Catalog SNPs", fontsize=12)
    ax.set_title(
        "GWAS Catalog SNPs within ARCHCODE Locus Windows\n"
        f"(GRCh38, ±{POSITION_WINDOW_BP}bp blind-spot overlap)",
        fontsize=13,
        pad=12,
    )

    legend_patches = [
        mpatches.Patch(color=COLOR_NORMAL, label="GWAS SNPs"),
        mpatches.Patch(
            color=COLOR_BLINDSPOT,
            label=f"Overlap with ARCHCODE Q2 blind spots (±{POSITION_WINDOW_BP} bp)",
        ),
    ]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(-0.5, len(loci) - 0.5)
    ax.set_ylim(0, max(n_gwas) * 1.15 + 2 if max(n_gwas) > 0 else 10)

    plt.tight_layout()
    fig.savefig(OUTPUT_PDF, format="pdf", bbox_inches="tight", dpi=300)
    fig.savefig(OUTPUT_PNG, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Figure saved: {OUTPUT_PDF} / {OUTPUT_PNG}")


def main() -> None:
    print("=" * 60)
    print("GWAS CATALOG OVERLAY — ARCHCODE (REST API)")
    print("=" * 60)

    # Step 1: Fetch GWAS SNPs per locus via REST API
    results: dict[str, LocusResult] = {}
    for locus_name, (chrom, start, end) in LOCUS_WINDOWS.items():
        print(f"\n--- {locus_name} (chr{chrom}:{start:,}-{end:,}) ---")
        snps = fetch_gwas_locus(chrom, start, end, locus_name)
        result = LocusResult(locus=locus_name, chrom=chrom, start=start, end=end, gwas_hits=snps)
        results[locus_name] = result
        time.sleep(1)  # Rate limiting

    # Step 2: Load Q2 blind spot positions
    print("\n--- Loading Q2 structural blind spots ---")
    q2_by_locus = load_q2_positions(Q2_CSV)

    # Step 3: Find overlaps
    find_blindspot_overlaps(results, q2_by_locus)

    # Step 4: Summary table
    print("\n" + "=" * 76)
    print(f"{'GWAS CATALOG OVERLAY — ARCHCODE LOCI':^76}")
    print("=" * 76)
    print(
        f"{'Locus':<10} {'Chr':<6} {'Window (Mb)':<22} {'GWAS SNPs':<12} {'Unique rsIDs':<14} {'Q2 Overlaps':<12}"
    )
    print("-" * 76)

    total_gwas = 0
    total_unique = 0
    total_bs = 0
    for name, r in results.items():
        window_str = f"{r.start / 1e6:.2f}–{r.end / 1e6:.2f}"
        bs_mark = " ★" if r.n_blindspot > 0 else ""
        print(
            f"{name:<10} chr{r.chrom:<4} {window_str:<22} {r.n_gwas:<12} {r.n_unique_rsids:<14} {str(r.n_blindspot) + bs_mark:<12}"
        )
        total_gwas += r.n_gwas
        total_unique += r.n_unique_rsids
        total_bs += r.n_blindspot

    print("-" * 76)
    print(f"{'TOTAL':<10} {'':6} {'':22} {total_gwas:<12} {total_unique:<14} {total_bs:<12}")
    print("=" * 76)
    print(f"★ = GWAS SNPs overlapping ARCHCODE Q2 structural blind spots (±{POSITION_WINDOW_BP}bp)")

    # Step 5: Save JSON
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "metadata": {
            "source": "EBI GWAS Catalog REST API",
            "api_endpoint": GWAS_API_BASE,
            "q2_file": str(Q2_CSV),
            "overlap_window_bp": POSITION_WINDOW_BP,
            "genome_build": "GRCh38",
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "totals": {
            "gwas_snps": total_gwas,
            "unique_rsids": total_unique,
            "q2_blindspot_overlaps": total_bs,
        },
        "loci": {},
    }
    for name, r in results.items():
        all_traits = set()
        for s in r.gwas_hits:
            all_traits.update(s.traits)
        summary["loci"][name] = {
            "chrom": r.chrom,
            "start": r.start,
            "end": r.end,
            "n_gwas_snps": r.n_gwas,
            "n_unique_rsids": r.n_unique_rsids,
            "n_q2_overlaps": r.n_blindspot,
            "traits": sorted(all_traits),
            "blindspot_overlaps": r.blindspot_overlaps,
        }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nJSON saved: {OUTPUT_JSON}")

    # Step 6: Save overlap CSV
    rows = []
    for r in results.values():
        rows.extend(r.blindspot_overlaps)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        else:
            f.write("locus,gwas_rsid,gwas_pos,gwas_traits,gwas_p_value,q2_pos,distance_bp\n")
    print(f"Overlap CSV saved: {OUTPUT_CSV} ({len(rows)} overlaps)")

    # Step 7: Figure
    generate_figure(results)

    print(f"\nDone. Total: {total_gwas} GWAS SNPs, {total_bs} Q2 overlaps across 9 loci.")


if __name__ == "__main__":
    main()
