#!/usr/bin/env python3
"""
H1 Validation: Spectral Fragility Index — Matched-Control Test

Tests Hypothesis 1: HBB pearls show elevated SFI vs matched benign controls.

Success criteria:
- Mann-Whitney p < 0.05
- Cohen's d > 0.5 (medium effect size)

Usage:
    python scripts/validate_h1_matched_control.py
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def cohens_d(group1, group2):
    """Calculate Cohen's d effect size"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def main():
    print("=" * 70)
    print("H1 VALIDATION: Spectral Fragility Matched-Control Test")
    print("=" * 70)

    # Load SFI results
    sfi_path = RESULTS_DIR / "sfi_30kb_pilot.csv"
    if not sfi_path.exists():
        print(f"ERROR: SFI results not found: {sfi_path}")
        print("Run: python scripts/spectral_fragility_batch.py --locus 30KB --subset pilot")
        return 1

    sfi = pd.read_csv(sfi_path)
    print(f"\n✅ Loaded SFI results: {len(sfi)} variants")

    # Load atlas to get labels
    atlas_path = RESULTS_DIR / "HBB_Unified_Atlas.csv"
    if not atlas_path.exists():
        print(f"ERROR: Atlas not found: {atlas_path}")
        return 1

    atlas = pd.read_csv(atlas_path)

    # Merge SFI with labels
    sfi_labeled = sfi.merge(atlas[["ClinVar_ID", "Label", "Pearl"]], on="ClinVar_ID", how="left")

    # Split into pearls vs benign
    pearls = sfi_labeled[sfi_labeled["Pearl"] == True]
    benign = sfi_labeled[sfi_labeled["Label"] == "Benign"]

    print(f"\n📊 Sample sizes:")
    print(f"   Pearls: {len(pearls)}")
    print(f"   Benign controls: {len(benign)}")

    if len(pearls) == 0 or len(benign) == 0:
        print("ERROR: Insufficient data for comparison")
        return 1

    # Descriptive statistics
    print(f"\n📈 SFI Descriptive Statistics:")
    print(f"\n   Pearls:")
    print(f"      Mean: {pearls['SFI'].mean():.4f}")
    print(f"      Median: {pearls['SFI'].median():.4f}")
    print(f"      SD: {pearls['SFI'].std():.4f}")
    print(f"      Range: [{pearls['SFI'].min():.4f}, {pearls['SFI'].max():.4f}]")

    print(f"\n   Benign:")
    print(f"      Mean: {benign['SFI'].mean():.4f}")
    print(f"      Median: {benign['SFI'].median():.4f}")
    print(f"      SD: {benign['SFI'].std():.4f}")
    print(f"      Range: [{benign['SFI'].min():.4f}, {benign['SFI'].max():.4f}]")

    # Mann-Whitney U test (non-parametric, no normality assumption)
    u_stat, p_value = stats.mannwhitneyu(pearls["SFI"], benign["SFI"], alternative="greater")

    print(f"\n🔬 Mann-Whitney U Test:")
    print(f"   U statistic: {u_stat:.1f}")
    print(f"   p-value (one-tailed): {p_value:.6f}")

    # Cohen's d effect size
    d = cohens_d(pearls["SFI"].values, benign["SFI"].values)
    print(f"\n📏 Cohen's d: {d:.4f}")

    # Effect size interpretation
    if abs(d) < 0.2:
        effect_size = "negligible"
    elif abs(d) < 0.5:
        effect_size = "small"
    elif abs(d) < 0.8:
        effect_size = "medium"
    else:
        effect_size = "large"

    print(f"   Interpretation: {effect_size} effect size")

    # T-test (for comparison, assumes normality)
    t_stat, t_pvalue = stats.ttest_ind(pearls["SFI"], benign["SFI"], alternative="greater")
    print(f"\n📊 Independent t-test (for comparison):")
    print(f"   t statistic: {t_stat:.4f}")
    print(f"   p-value (one-tailed): {t_pvalue:.6f}")

    # Decision
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    success_criteria = {
        "Mann-Whitney p < 0.05": p_value < 0.05,
        "Cohen's d > 0.5": abs(d) > 0.5,
    }

    all_pass = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {criterion}")

    print()

    if all_pass:
        print("🎉 HYPOTHESIS 1: PASS")
        print("\nPearls show elevated spectral fragility compared to benign controls.")
        print("SFI is a valid discriminative metric for HBB pearls.")
        verdict = "PASS"
    else:
        print("❌ HYPOTHESIS 1: FAIL")
        print("\nPearls do NOT show significantly elevated SFI.")
        print("Spectral fragility may not add value beyond LSSIM for HBB.")
        verdict = "FAIL"

    # Save results
    output_path = RESULTS_DIR / "H1_matched_control_test.txt"
    with open(output_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("H1 VALIDATION: Spectral Fragility Matched-Control Test\n")
        f.write("=" * 70 + "\n\n")

        f.write("Hypothesis: HBB pearls show elevated SFI vs benign controls\n\n")

        f.write("Sample sizes:\n")
        f.write(f"  Pearls: {len(pearls)}\n")
        f.write(f"  Benign: {len(benign)}\n\n")

        f.write("SFI Statistics:\n")
        f.write(f"  Pearls:  Mean={pearls['SFI'].mean():.4f}, SD={pearls['SFI'].std():.4f}\n")
        f.write(f"  Benign:  Mean={benign['SFI'].mean():.4f}, SD={benign['SFI'].std():.4f}\n\n")

        f.write(f"Mann-Whitney U test: U={u_stat:.1f}, p={p_value:.6f}\n")
        f.write(f"Cohen's d: {d:.4f} ({effect_size})\n")
        f.write(f"T-test: t={t_stat:.4f}, p={t_pvalue:.6f}\n\n")

        f.write("Success criteria:\n")
        for criterion, passed in success_criteria.items():
            status = "PASS" if passed else "FAIL"
            f.write(f"  [{status}] {criterion}\n")

        f.write(f"\nVERDICT: {verdict}\n")

    print(f"\n📄 Results saved: {output_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
