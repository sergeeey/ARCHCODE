#!/usr/bin/env python3
"""
Experiment X.1: H6 Compactness Hypothesis Test

Test: Does gene compactness (gene_size_kb) correlate with within-category AUC?
H6 Prediction: Smaller genes show higher within-category AUC (negative correlation)
Kill-criterion: r > -0.3 OR p > 0.05 (no significant negative correlation)
Support-criterion: r < -0.5 AND p < 0.05 (strong negative correlation)
"""

import json
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def main():
    # Gene sizes (kb) - from locus_selection_research.json + known values
    gene_sizes = {
        "HBB": 1.6,  # chr11:5,225,464-5,227,071 (GRCh38)
        "GJB2": 5.5,  # chr13:20,189,155-20,194,653
        "TP53": 19,  # from locus_selection_research.json
        "TERT": 42,  # chr5:1,253,147-1,295,162
        "LDLR": 44,  # from locus_selection_research.json
        "MLH1": 57,  # from locus_selection_research.json
        "SCN5A": 102,  # from tier2_candidates
        "BRCA1": 126,  # from locus_selection_research.json
        "CFTR": 250,  # chr7:117,120,016-117,370,094 (very large)
    }

    # Within-category AUC - from within_category_analysis.json
    within_aucs = {
        "HBB": 0.6227,
        "TP53": 0.6228,
        "SCN5A": 0.5002,
        "BRCA1": 0.4934,
        "MLH1": 0.4771,
        "CFTR": 0.4654,
        "TERT": 0.4646,
        "LDLR": 0.4119,
        "GJB2": 0.2824,
    }

    # Align data
    loci = sorted(gene_sizes.keys())
    sizes = np.array([gene_sizes[loc] for loc in loci])
    aucs = np.array([within_aucs[loc] for loc in loci])

    # Spearman correlation (rank-based, robust to outliers)
    r_spearman, p_spearman = stats.spearmanr(sizes, aucs)

    # Pearson correlation (parametric)
    r_pearson, p_pearson = stats.pearsonr(sizes, aucs)

    # Log-transform gene size (compactness may have log relationship)
    log_sizes = np.log10(sizes)
    r_log, p_log = stats.spearmanr(log_sizes, aucs)

    print("=" * 60)
    print("EXPERIMENT X.1: H6 COMPACTNESS HYPOTHESIS TEST")
    print("=" * 60)
    print()
    print("Dataset:")
    print(f"  N loci: {len(loci)}")
    print(f"  Gene size range: {sizes.min():.1f} - {sizes.max():.0f} kb")
    print(f"  Within-AUC range: {aucs.min():.4f} - {aucs.max():.4f}")
    print()

    print("Locus-by-locus:")
    for loc in loci:
        print(f"  {loc:6s}: {gene_sizes[loc]:6.1f} kb, AUC={within_aucs[loc]:.4f}")
    print()

    print("Correlation Results:")
    print(f"  Spearman r = {r_spearman:+.4f}, p = {p_spearman:.4f}")
    print(f"  Pearson  r = {r_pearson:+.4f}, p = {p_pearson:.4f}")
    print(f"  Log(size) Spearman r = {r_log:+.4f}, p = {p_log:.4f}")
    print()

    # Decision criteria
    print("H6 Decision Criteria:")
    print(f"  Kill-criterion:    r > -0.3 OR p > 0.05")
    print(f"  Support-criterion: r < -0.5 AND p < 0.05")
    print()

    # Verdict
    if r_spearman > -0.3 or p_spearman > 0.05:
        verdict = "❌ H6 KILLED"
        interpretation = (
            "No significant negative correlation between gene size and within-category AUC.\n"
            "  → H2 (Category Artifact) dominates completely.\n"
            "  → Compactness does NOT explain residual structural signal.\n"
            "  → Paper framing: Pure falsification (3D models fail; category artifact wins)."
        )
    elif r_spearman < -0.5 and p_spearman < 0.05:
        verdict = "✅ H6 SUPPORTED"
        interpretation = (
            "Strong negative correlation: smaller genes show higher within-category AUC.\n"
            "  → H2 + H6 combination: Category artifact dominates, but compact domains show residual signal.\n"
            "  → Paper framing: 'Category artifacts dominate, but compact regulatory domains retain measurable structural effects.'\n"
            "  → Recommendation: 2 days deeper analysis (stratify by category within compactness bins)."
        )
    else:
        verdict = "⚠️ H6 MARGINAL"
        interpretation = (
            "Weak/marginal correlation detected.\n"
            "  → -0.5 < r < -0.3: trend present but not strong.\n"
            "  → Document as exploratory finding, do not overinterpret.\n"
            "  → Paper framing: Lean toward pure falsification, mention compactness as potential modifier in Discussion."
        )

    print("VERDICT:")
    print(f"  {verdict}")
    print()
    print("Interpretation:")
    for line in interpretation.split("\n"):
        print(f"  {line}")
    print()

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Linear scale
    ax1 = axes[0]
    ax1.scatter(sizes, aucs, s=100, alpha=0.6, edgecolors="black")
    for i, loc in enumerate(loci):
        ax1.annotate(
            loc, (sizes[i], aucs[i]), xytext=(5, 5), textcoords="offset points", fontsize=9
        )

    # Fit line
    z = np.polyfit(sizes, aucs, 1)
    p = np.poly1d(z)
    x_line = np.linspace(sizes.min(), sizes.max(), 100)
    ax1.plot(x_line, p(x_line), "r--", alpha=0.5, label=f"Linear fit (r={r_pearson:.3f})")

    ax1.set_xlabel("Gene Size (kb)", fontsize=12)
    ax1.set_ylabel("Within-Category AUC", fontsize=12)
    ax1.set_title(
        f"H6 Compactness Test (Linear)\nSpearman r={r_spearman:.3f}, p={p_spearman:.4f}",
        fontsize=11,
    )
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.axhline(y=0.5, color="gray", linestyle=":", alpha=0.5, label="Chance (AUC=0.5)")

    # Plot 2: Log scale
    ax2 = axes[1]
    ax2.scatter(log_sizes, aucs, s=100, alpha=0.6, edgecolors="black")
    for i, loc in enumerate(loci):
        ax2.annotate(
            loc, (log_sizes[i], aucs[i]), xytext=(5, 5), textcoords="offset points", fontsize=9
        )

    # Fit line
    z_log = np.polyfit(log_sizes, aucs, 1)
    poly_log = np.poly1d(z_log)
    x_log_line = np.linspace(log_sizes.min(), log_sizes.max(), 100)
    ax2.plot(
        x_log_line, poly_log(x_log_line), "r--", alpha=0.5, label=f"Linear fit (r={r_log:.3f})"
    )

    ax2.set_xlabel("log10(Gene Size) [kb]", fontsize=12)
    ax2.set_ylabel("Within-Category AUC", fontsize=12)
    ax2.set_title(f"H6 Compactness Test (Log)\nSpearman r={r_log:.3f}, p={p_log:.4f}", fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.axhline(y=0.5, color="gray", linestyle=":", alpha=0.5)

    plt.tight_layout()

    # Save plot
    plot_path = RESULTS_DIR / "h6_compactness_test.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved: {plot_path}")

    # Save results JSON
    results = {
        "experiment": "H6 Compactness Hypothesis Test (Experiment X.1)",
        "date": "2026-05-09",
        "hypothesis": "Smaller genes (compact domains) show higher within-category AUC",
        "data": {
            "loci": loci,
            "gene_sizes_kb": sizes.tolist(),
            "within_category_auc": aucs.tolist(),
        },
        "statistics": {
            "spearman_r": float(r_spearman),
            "spearman_p": float(p_spearman),
            "pearson_r": float(r_pearson),
            "pearson_p": float(p_pearson),
            "log_spearman_r": float(r_log),
            "log_spearman_p": float(p_log),
        },
        "decision_criteria": {
            "kill_criterion": "r > -0.3 OR p > 0.05",
            "support_criterion": "r < -0.5 AND p < 0.05",
        },
        "verdict": verdict.replace("❌", "").replace("✅", "").replace("⚠️", "").strip(),
        "interpretation": interpretation.strip(),
        "next_action": (
            "PROJECT_FREEZE + pure falsification paper"
            if "KILLED" in verdict
            else "2 days deeper analysis + modified paper"
            if "SUPPORTED" in verdict
            else "Document as exploratory, lean toward falsification paper"
        ),
    }

    results_path = RESULTS_DIR / "h6_compactness_test.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved: {results_path}")
    print()
    print("=" * 60)
    print("EXPERIMENT X.1 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
