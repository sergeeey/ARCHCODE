#!/usr/bin/env python3
"""
Task #22: Dosage-Sensitivity Correlation Validation
====================================================
Statistical tests for codeword distance vs dosage-sensitivity hypothesis.

Tests:
  - Mann-Whitney U: pairwise LSSIM distribution comparisons
  - Cohen's d: effect sizes
  - Kruskal-Wallis: overall difference across loci

Hypothesis: Dosage-sensitive loci show higher structural robustness
Expected: HBB > TP53 > BRCA1 in median LSSIM

Usage:
    python scripts/dosage_sensitivity_correlation.py
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_lssim_data(locus: str) -> pd.Series:
    """Load LSSIM values for a locus"""
    atlas_paths = {
        "HBB": RESULTS_DIR / "HBB_Unified_Atlas.csv",
        "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
        "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    }

    atlas_path = atlas_paths.get(locus)
    if not atlas_path or not atlas_path.exists():
        raise FileNotFoundError(f"Atlas not found: {atlas_path}")

    df = pd.read_csv(atlas_path)
    lssim = df["ARCHCODE_LSSIM"].dropna()

    print(f"✅ {locus}: n={len(lssim)}, median={lssim.median():.4f}")
    return lssim


def cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """Compute Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    return (group1.mean() - group2.mean()) / pooled_std


def main():
    print("=" * 70)
    print("TASK #22: DOSAGE-SENSITIVITY CORRELATION VALIDATION")
    print("=" * 70)
    print()

    # Load data
    print("Loading LSSIM distributions...")
    hbb_lssim = load_lssim_data("HBB")
    tp53_lssim = load_lssim_data("TP53")
    brca1_lssim = load_lssim_data("BRCA1")
    print()

    # Summary statistics
    print("=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)
    print()

    loci_data = {
        "HBB": hbb_lssim,
        "TP53": tp53_lssim,
        "BRCA1": brca1_lssim,
    }

    summary = []
    for locus, lssim in loci_data.items():
        summary.append(
            {
                "Locus": locus,
                "N": len(lssim),
                "Mean": lssim.mean(),
                "Median": lssim.median(),
                "Std": lssim.std(),
                "Min": lssim.min(),
                "Q25": lssim.quantile(0.25),
                "Q75": lssim.quantile(0.75),
                "Max": lssim.max(),
            }
        )

    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))
    print()

    # Kruskal-Wallis test (overall difference)
    print("=" * 70)
    print("KRUSKAL-WALLIS TEST (Overall Difference)")
    print("=" * 70)
    print()

    h_stat, p_kruskal = stats.kruskal(hbb_lssim, tp53_lssim, brca1_lssim)
    print(f"H-statistic: {h_stat:.4f}")
    print(f"p-value: {p_kruskal:.6f}")

    if p_kruskal < 0.05:
        print("✅ Significant overall difference between loci")
    else:
        print("❌ No significant overall difference")
    print()

    # Pairwise Mann-Whitney U tests
    print("=" * 70)
    print("PAIRWISE MANN-WHITNEY U TESTS")
    print("=" * 70)
    print()

    pairs = [
        ("HBB", hbb_lssim, "TP53", tp53_lssim),
        ("HBB", hbb_lssim, "BRCA1", brca1_lssim),
        ("TP53", tp53_lssim, "BRCA1", brca1_lssim),
    ]

    results = []

    for locus1, data1, locus2, data2 in pairs:
        u_stat, p_value = stats.mannwhitneyu(data1, data2, alternative="two-sided")
        d = cohens_d(data1, data2)

        # Effect size interpretation
        if abs(d) < 0.2:
            effect = "negligible"
        elif abs(d) < 0.5:
            effect = "small"
        elif abs(d) < 0.8:
            effect = "medium"
        else:
            effect = "large"

        results.append(
            {
                "Comparison": f"{locus1} vs {locus2}",
                "U-statistic": u_stat,
                "p-value": p_value,
                "Cohen's d": d,
                "Effect": effect,
                "Significant": "✅" if p_value < 0.05 else "❌",
            }
        )

        print(f"{locus1} vs {locus2}:")
        print(f"  U-statistic: {u_stat:.1f}")
        print(f"  p-value: {p_value:.6f}")
        print(f"  Cohen's d: {d:.4f} ({effect})")
        print(f"  Median diff: {data1.median() - data2.median():.4f}")
        print()

    # Dosage-sensitivity hypothesis test
    print("=" * 70)
    print("DOSAGE-SENSITIVITY HYPOTHESIS")
    print("=" * 70)
    print()

    print("Expected ranking (median LSSIM):")
    print("  HBB (dosage-sensitive) > TP53 (tumor suppressor) > BRCA1 (large gene)")
    print()

    actual_ranking = sorted(
        [(locus, lssim.median()) for locus, lssim in loci_data.items()],
        key=lambda x: x[1],
        reverse=True,
    )

    print("Actual ranking (median LSSIM):")
    for i, (locus, median) in enumerate(actual_ranking, 1):
        print(f"  {i}. {locus}: {median:.4f}")
    print()

    # Hypothesis verdict
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    hbb_median = hbb_lssim.median()
    brca1_median = brca1_lssim.median()

    # Check HBB > BRCA1 (primary hypothesis)
    hbb_vs_brca1 = [r for r in results if "HBB vs BRCA1" in r["Comparison"]][0]

    criteria = {
        "Overall difference exists (Kruskal-Wallis p<0.05)": p_kruskal < 0.05,
        "HBB median > BRCA1 median": hbb_median > brca1_median,
        "HBB vs BRCA1 significant (p<0.05)": hbb_vs_brca1["p-value"] < 0.05,
        "HBB vs BRCA1 effect size ≥ small (|d|≥0.2)": abs(hbb_vs_brca1["Cohen's d"]) >= 0.2,
    }

    all_pass = all(criteria.values())

    for criterion, passed in criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {criterion}")
    print()

    if all_pass:
        print("🎉 DOSAGE-SENSITIVITY HYPOTHESIS: SUPPORTED")
        print("\nHBB shows higher structural robustness than BRCA1,")
        print("consistent with dosage-sensitivity constraints.")
    else:
        print("❌ DOSAGE-SENSITIVITY HYPOTHESIS: NOT SUPPORTED")
        print("\nNo strong evidence for dosage-sensitivity → codeword distance link.")

    # Save results
    results_df = pd.DataFrame(results)
    output_path = RESULTS_DIR / "dosage_sensitivity_correlation.csv"
    results_df.to_csv(output_path, index=False)

    print(f"\n📄 Results saved: {output_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
