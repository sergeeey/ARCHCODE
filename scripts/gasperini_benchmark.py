"""
EXP-008: Gasperini CRISPRi Gold Standard Benchmark
=====================================================
Maps Gasperini 2019 CRISPRi perturbation sites to ARCHCODE atlas positions.
Tests whether ARCHCODE structural predictions correlate with experimental
enhancer-gene effect sizes from the largest published CRISPRi screen (K562).

Gasperini et al. 2019, Cell: 5,920 CRISPRi elements → 629K enhancer-gene pairs.
ARCHCODE: 9 loci with LSSIM scores.

Key question: Do CRISPRi-confirmed functional elements show lower LSSIM
(more structural disruption) than non-functional elements?

Usage: python scripts/gasperini_benchmark.py
"""

import gzip
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

ATLAS_FILES = {
    "HBB": ("results/HBB_Unified_Atlas.csv", "chr11", 5225000, 5260000),
    "BRCA1": ("results/BRCA1_Unified_Atlas_400kb.csv", "chr17", 43044000, 43170000),
    "TP53": ("results/TP53_Unified_Atlas_300kb.csv", "chr17", 7565000, 7590000),
    "TERT": ("results/TERT_Unified_Atlas_300kb.csv", "chr5", 1253000, 1295000),
    "MLH1": ("results/MLH1_Unified_Atlas_300kb.csv", "chr3", 36993000, 37050000),
    "CFTR": ("results/CFTR_Unified_Atlas_317kb.csv", "chr7", 117480000, 117668000),
    "SCN5A": ("results/SCN5A_Unified_Atlas_400kb.csv", "chr3", 38550000, 38691000),
    "GJB2": ("results/GJB2_Unified_Atlas_300kb.csv", "chr13", 20761000, 20767000),
    "LDLR": ("results/LDLR_Unified_Atlas_300kb.csv", "chr19", 11089000, 11133000),
}

GASPERINI_FILE = "analysis/gasperini2019/GSE120861_all_deg_results.at_scale.txt.gz"
ABC_FILE = "data/abc/ENCFF976OKL.bed.gz"


def load_gasperini():
    """Load Gasperini DEG results, extract significant hits."""
    print("  Loading Gasperini 2019 CRISPRi results...")
    df = pd.read_csv(GASPERINI_FILE, sep="\t", compression="gzip")
    print(f"  Raw: {len(df):,} enhancer-gene pairs")

    # Parse target site coordinates (filter out NTC = non-targeting controls)
    df = df[df["target_site.start"].apply(lambda x: str(x).isdigit())].copy()
    df["target_chr"] = df["target_site.chr"].astype(str)
    df["target_start"] = df["target_site.start"].astype(int)
    df["target_stop"] = df["target_site.stop"].astype(int)
    df["target_mid"] = (df["target_start"] + df["target_stop"]) // 2
    print(f"  After removing NTC controls: {len(df):,}")

    # Coerce numeric columns (some rows have string artifacts)
    for col in [
        "pvalue.empirical.adjusted",
        "pvalue.raw",
        "pvalue.empirical",
        "beta",
        "fold_change.transcript_remaining",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Significance: empirical adjusted p-value
    df["significant"] = df["pvalue.empirical.adjusted"] < 0.05
    df["strong_hit"] = (df["pvalue.empirical.adjusted"] < 0.01) & (
        df["fold_change.transcript_remaining"] < 0.8
    )

    n_sig = df["significant"].sum()
    n_strong = df["strong_hit"].sum()
    print(f"  Significant (adj.p < 0.05): {n_sig:,}")
    print(f"  Strong hits (adj.p < 0.01 & FC < 0.8): {n_strong:,}")

    # Filter out TSS controls and outlier genes
    df_enh = df[df["site_type"] == "DHS"].copy()
    print(f"  DHS enhancer sites only: {len(df_enh):,}")

    return df, df_enh


def load_atlas(locus, path):
    """Load atlas with position column."""
    df = pd.read_csv(path)
    # Position column name varies
    pos_col = None
    for candidate in ["Position_GRCh38", "Position", "Pos"]:
        if candidate in df.columns:
            pos_col = candidate
            break
    if pos_col is None:
        return None
    df["position"] = df[pos_col].astype(int)
    return df


def map_gasperini_to_atlas(gasp_df, atlas_df, chrom, start, end, locus_name, window=1000):
    """Map Gasperini CRISPRi targets to ARCHCODE atlas positions within a locus."""
    # Filter Gasperini to this locus region
    gasp_locus = gasp_df[
        (gasp_df["target_chr"] == chrom)
        & (gasp_df["target_mid"] >= start)
        & (gasp_df["target_mid"] <= end)
    ].copy()

    if len(gasp_locus) == 0:
        return None

    # For each Gasperini target, find nearest ARCHCODE variant within window
    atlas_positions = atlas_df["position"].values
    atlas_lssim = atlas_df["ARCHCODE_LSSIM"].values

    matches = []
    for _, row in gasp_locus.iterrows():
        target_pos = row["target_mid"]
        distances = np.abs(atlas_positions - target_pos)
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]

        if min_dist <= window:
            matches.append(
                {
                    "locus": locus_name,
                    "gasperini_site": row["gRNA_group"],
                    "target_pos": target_pos,
                    "atlas_pos": int(atlas_positions[min_idx]),
                    "distance": int(min_dist),
                    "beta": row["beta"],
                    "fold_change": row["fold_change.transcript_remaining"],
                    "pval_adj": row["pvalue.empirical.adjusted"],
                    "significant": bool(row["significant"]),
                    "gene": row["gene_short_name"],
                    "lssim": float(atlas_lssim[min_idx]),
                }
            )

    if not matches:
        return None

    return pd.DataFrame(matches)


def main():
    print("=" * 70)
    print("EXP-008: Gasperini CRISPRi Gold Standard Benchmark")
    print("=" * 70)

    # Load Gasperini data
    gasp_full, gasp_enh = load_gasperini()

    # Load and map each locus
    all_matches = []
    locus_stats = {}

    print(f"\n  Mapping CRISPRi targets to ARCHCODE atlases...\n")

    for locus, (path, chrom, start, end) in ATLAS_FILES.items():
        if not os.path.exists(path):
            continue

        atlas = load_atlas(locus, path)
        if atlas is None:
            continue

        # Map using both full and enhancer-only Gasperini data
        matches = map_gasperini_to_atlas(gasp_full, atlas, chrom, start, end, locus)

        if matches is not None and len(matches) > 0:
            # Deduplicate by gasperini_site + gene
            matches = matches.drop_duplicates(subset=["gasperini_site", "gene"])
            all_matches.append(matches)
            n_sig = matches["significant"].sum()
            locus_stats[locus] = {
                "n_mapped": len(matches),
                "n_significant": int(n_sig),
                "n_nonsignificant": len(matches) - int(n_sig),
            }
            print(
                f"  {locus:8s}  mapped={len(matches):4d}  significant={n_sig:3d}  "
                f"non-sig={len(matches) - n_sig:4d}"
            )
        else:
            locus_stats[locus] = {"n_mapped": 0, "n_significant": 0, "n_nonsignificant": 0}
            print(f"  {locus:8s}  mapped=   0  (no CRISPRi targets in locus region)")

    if not all_matches:
        print("\nNo CRISPRi targets mapped to any ARCHCODE locus.")
        return

    combined = pd.concat(all_matches, ignore_index=True)
    print(f"\n  Total mapped: {len(combined)} CRISPRi-atlas pairs")

    # ── Analysis 1: LSSIM in significant vs non-significant CRISPRi hits ──
    print("\n" + "=" * 70)
    print("=== 1. LSSIM: Significant vs Non-Significant CRISPRi Hits ===\n")

    sig = combined[combined["significant"]]
    nonsig = combined[~combined["significant"]]

    if len(sig) > 0 and len(nonsig) > 0:
        sig_lssim = sig["lssim"].values
        nonsig_lssim = nonsig["lssim"].values
        stat, pval = mannwhitneyu(sig_lssim, nonsig_lssim, alternative="less")
        print(
            f"  Significant CRISPRi hits:     n={len(sig):4d}  mean LSSIM={np.mean(sig_lssim):.6f}"
        )
        print(
            f"  Non-significant:              n={len(nonsig):4d}  mean LSSIM={np.mean(nonsig_lssim):.6f}"
        )
        print(f"  ΔLSSIM = {np.mean(sig_lssim) - np.mean(nonsig_lssim):+.6f}")
        print(f"  Mann-Whitney U test (sig < nonsig): U={stat:.0f}, p={pval:.4e}")
    else:
        pval = None
        print(f"  Insufficient data (sig={len(sig)}, nonsig={len(nonsig)})")

    # ── Analysis 2: Correlation of LSSIM with CRISPRi effect size ──
    print("\n" + "=" * 70)
    print("=== 2. LSSIM vs CRISPRi Effect Size (Beta) ===\n")

    # Beta is negative for CRISPRi knockdown (more negative = stronger effect)
    # LSSIM: lower = more disrupted
    # Expectation: more negative beta ↔ lower LSSIM (positive correlation)
    valid = combined.dropna(subset=["beta", "lssim"])
    if len(valid) > 10:
        rho, rho_p = spearmanr(valid["lssim"].values, valid["beta"].values)
        print(f"  Spearman ρ(LSSIM, beta): {rho:.4f} (p={rho_p:.4e})")
        print(f"  n = {len(valid)}")
        print(f"  Interpretation: {'positive' if rho > 0 else 'negative'} correlation")
        print(f"    (positive ρ = CRISPRi knockdown targets have lower LSSIM → concordant)")

        # Also correlation with fold change
        rho_fc, rho_fc_p = spearmanr(valid["lssim"].values, valid["fold_change"].values)
        print(f"\n  Spearman ρ(LSSIM, fold_change): {rho_fc:.4f} (p={rho_fc_p:.4e})")
    else:
        rho, rho_p = np.nan, np.nan
        rho_fc, rho_fc_p = np.nan, np.nan
        print(f"  Insufficient data (n={len(valid)})")

    # ── Analysis 3: Per-locus breakdown ──────────────────────────
    print("\n" + "=" * 70)
    print("=== 3. Per-Locus Breakdown ===\n")

    per_locus_results = {}
    for locus in sorted(locus_stats.keys()):
        if locus_stats[locus]["n_mapped"] == 0:
            per_locus_results[locus] = {"n_mapped": 0}
            continue
        ldf = combined[combined["locus"] == locus]
        sig_l = ldf[ldf["significant"]]
        nonsig_l = ldf[~ldf["significant"]]

        result = {
            "n_mapped": len(ldf),
            "n_significant": len(sig_l),
            "mean_lssim_sig": round(float(sig_l["lssim"].mean()), 6) if len(sig_l) > 0 else None,
            "mean_lssim_nonsig": round(float(nonsig_l["lssim"].mean()), 6)
            if len(nonsig_l) > 0
            else None,
            "unique_genes": int(ldf["gene"].nunique()),
        }
        per_locus_results[locus] = result

        sig_str = (
            f"sig={len(sig_l):3d} LSSIM={result['mean_lssim_sig']:.4f}"
            if len(sig_l) > 0
            else "sig=  0"
        )
        nonsig_str = (
            f"nonsig={len(nonsig_l):4d} LSSIM={result['mean_lssim_nonsig']:.4f}"
            if len(nonsig_l) > 0
            else ""
        )
        print(f"  {locus:8s}  {sig_str}  {nonsig_str}  genes={result['unique_genes']}")

    # ── Analysis 4: Enrichment at enhancer-proximal positions ────
    print("\n" + "=" * 70)
    print("=== 4. CRISPRi Hit Rate at Structurally Disrupted Positions ===\n")

    if len(combined) > 0:
        # Define "structurally disrupted" as LSSIM < 0.99
        disrupted = combined["lssim"] < 0.99
        intact = combined["lssim"] >= 0.99

        n_dis_sig = (disrupted & combined["significant"]).sum()
        n_dis_total = disrupted.sum()
        n_int_sig = (intact & combined["significant"]).sum()
        n_int_total = intact.sum()

        rate_dis = n_dis_sig / n_dis_total if n_dis_total > 0 else 0
        rate_int = n_int_sig / n_int_total if n_int_total > 0 else 0

        print(
            f"  Structurally disrupted (LSSIM < 0.99):  {n_dis_sig}/{n_dis_total} = {rate_dis:.3f} CRISPRi hit rate"
        )
        print(
            f"  Structurally intact (LSSIM ≥ 0.99):     {n_int_sig}/{n_int_total} = {rate_int:.3f} CRISPRi hit rate"
        )

        if rate_int > 0:
            enrichment = rate_dis / rate_int
            print(f"  Enrichment: {enrichment:.2f}×")
        else:
            enrichment = None

        # Fisher's exact test
        from scipy.stats import fisher_exact

        table = [[n_dis_sig, n_dis_total - n_dis_sig], [n_int_sig, n_int_total - n_int_sig]]
        odds, fisher_p = fisher_exact(table)
        print(f"  Fisher's exact: OR={odds:.2f}, p={fisher_p:.4e}")

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs("analysis", exist_ok=True)

    combined.to_csv("analysis/gasperini_benchmark_matches.csv", index=False)
    print(f"\nSaved: analysis/gasperini_benchmark_matches.csv")

    summary = {
        "experiment": "EXP-008: Gasperini CRISPRi Gold Standard Benchmark",
        "gasperini_total_pairs": len(gasp_full),
        "gasperini_enhancer_pairs": len(gasp_enh),
        "total_mapped": len(combined),
        "per_locus": per_locus_results,
        "lssim_vs_beta_spearman": {
            "rho": round(rho, 4) if not np.isnan(rho) else None,
            "p": float(rho_p) if not np.isnan(rho_p) else None,
        },
        "lssim_vs_foldchange_spearman": {
            "rho": round(rho_fc, 4) if not np.isnan(rho_fc) else None,
            "p": float(rho_fc_p) if not np.isnan(rho_fc_p) else None,
        },
        "mann_whitney_sig_vs_nonsig": {
            "p": float(pval) if pval is not None else None,
        },
    }

    with open("analysis/gasperini_benchmark_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved: analysis/gasperini_benchmark_summary.json")

    # ── Figure ───────────────────────────────────────────────────
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Panel A: LSSIM distribution for significant vs non-significant
        ax = axes[0]
        if len(sig) > 0:
            ax.hist(
                sig["lssim"].values,
                bins=30,
                alpha=0.7,
                color="#E53935",
                label=f"Significant (n={len(sig)})",
                density=True,
            )
        if len(nonsig) > 0:
            ax.hist(
                nonsig["lssim"].values,
                bins=30,
                alpha=0.5,
                color="#2196F3",
                label=f"Non-significant (n={len(nonsig)})",
                density=True,
            )
        ax.set_xlabel("ARCHCODE LSSIM")
        ax.set_ylabel("Density")
        ax.set_title("A. LSSIM: CRISPRi Hits vs Non-Hits", fontweight="bold")
        ax.legend(fontsize=9)

        # Panel B: LSSIM vs beta scatter
        ax = axes[1]
        ax.scatter(valid["lssim"].values, valid["beta"].values, alpha=0.15, s=5, color="#666")
        # Highlight significant
        sig_valid = valid[valid["significant"]]
        if len(sig_valid) > 0:
            ax.scatter(
                sig_valid["lssim"].values,
                sig_valid["beta"].values,
                alpha=0.5,
                s=10,
                color="#E53935",
                label="Significant",
            )
        ax.set_xlabel("ARCHCODE LSSIM")
        ax.set_ylabel("CRISPRi Beta (effect size)")
        ax.set_title("B. LSSIM vs CRISPRi Effect Size", fontweight="bold")
        if not np.isnan(rho):
            ax.text(
                0.05,
                0.95,
                f"ρ = {rho:.3f}\np = {rho_p:.2e}",
                transform=ax.transAxes,
                fontsize=9,
                va="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
            )
        ax.legend(fontsize=9)

        # Panel C: Per-locus mapped counts
        ax = axes[2]
        loci_with_data = [
            l for l in sorted(per_locus_results.keys()) if per_locus_results[l]["n_mapped"] > 0
        ]
        if loci_with_data:
            x = np.arange(len(loci_with_data))
            sig_counts = [per_locus_results[l].get("n_significant", 0) for l in loci_with_data]
            total_counts = [per_locus_results[l]["n_mapped"] for l in loci_with_data]
            nonsig_counts = [t - s for t, s in zip(total_counts, sig_counts)]
            ax.bar(x, sig_counts, label="Significant", color="#E53935", alpha=0.85)
            ax.bar(
                x,
                nonsig_counts,
                bottom=sig_counts,
                label="Non-significant",
                color="#2196F3",
                alpha=0.85,
            )
            ax.set_xticks(x)
            ax.set_xticklabels(loci_with_data, rotation=45, ha="right")
            ax.set_ylabel("Mapped CRISPRi Pairs")
            ax.set_title("C. CRISPRi Coverage Per Locus", fontweight="bold")
            ax.legend(fontsize=9)

        plt.tight_layout()
        os.makedirs("figures", exist_ok=True)
        plt.savefig("figures/fig_gasperini_benchmark.pdf", bbox_inches="tight", dpi=300)
        plt.savefig("figures/fig_gasperini_benchmark.png", bbox_inches="tight", dpi=200)
        plt.close()
        print("Saved: figures/fig_gasperini_benchmark.pdf + .png")
    except ImportError:
        print("matplotlib not available — skipping figure")


if __name__ == "__main__":
    main()
