#!/usr/bin/env python3
"""
H1 Cross-Locus Validation: TP53 and BRCA1

Tests Hypothesis 1 generalization:
- TP53 splice_region (positive control): Expected AUC > 0.60
- BRCA1 synonymous (negative control): Expected AUC ≈ 0.50

Usage:
    python scripts/validate_h1_cross_locus.py --locus tp53 --category splice_region
    python scripts/validate_h1_cross_locus.py --locus brca1 --category synonymous
"""

import argparse
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score
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
    parser = argparse.ArgumentParser(description="H1 cross-locus validation")
    parser.add_argument(
        "--locus",
        required=True,
        choices=["tp53", "brca1", "hbb"],
        help="Locus to validate",
    )
    parser.add_argument(
        "--category",
        help="Category filter (e.g., splice_region, synonymous)",
    )
    args = parser.parse_args()

    locus_upper = args.locus.upper()
    locus_dir = "TP53" if args.locus == "tp53" else "BRCA1" if args.locus == "brca1" else "30KB"

    print("=" * 70)
    print(f"H1 CROSS-LOCUS VALIDATION: {locus_upper}")
    if args.category:
        print(f"Category: {args.category}")
    print("=" * 70)

    # Load SFI results
    sfi_path = RESULTS_DIR / f"sfi_{locus_dir.lower()}_all.csv"
    if not sfi_path.exists():
        print(f"ERROR: SFI results not found: {sfi_path}")
        print(f"Run: python scripts/spectral_fragility_batch.py --locus {locus_dir} --subset all")
        return 1

    sfi = pd.read_csv(sfi_path)
    print(f"\n✅ Loaded SFI results: {len(sfi)} variants")

    # Load atlas
    atlas_path = (
        RESULTS_DIR
        / f"{locus_upper}_Unified_Atlas{'_400kb' if args.locus == 'brca1' else '_300kb' if args.locus == 'tp53' else ''}.csv"
    )
    if not atlas_path.exists():
        print(f"ERROR: Atlas not found: {atlas_path}")
        return 1

    atlas = pd.read_csv(atlas_path)

    # Merge SFI with labels
    sfi_labeled = sfi.merge(atlas[["ClinVar_ID", "Label", "Category"]], on="ClinVar_ID", how="left")

    # Category filter
    if args.category:
        sfi_labeled = sfi_labeled[sfi_labeled["Category"] == args.category]
        print(f"   Filtered to category '{args.category}': {len(sfi_labeled)} variants")

    # Split pathogenic vs benign
    pathogenic = sfi_labeled[sfi_labeled["Label"] == "Pathogenic"]
    benign = sfi_labeled[sfi_labeled["Label"] == "Benign"]

    print(f"\n📊 Sample sizes:")
    print(f"   Pathogenic: {len(pathogenic)}")
    print(f"   Benign: {len(benign)}")

    if len(pathogenic) < 3 or len(benign) < 3:
        print("ERROR: Insufficient data (need ≥3 per group)")
        return 1

    # Descriptive statistics
    print(f"\n📈 SFI Descriptive Statistics:")
    print(f"\n   Pathogenic:")
    print(f"      Mean: {pathogenic['SFI'].mean():.4f}")
    print(f"      Median: {pathogenic['SFI'].median():.4f}")
    print(f"      SD: {pathogenic['SFI'].std():.4f}")
    print(f"      Range: [{pathogenic['SFI'].min():.4f}, {pathogenic['SFI'].max():.4f}]")

    print(f"\n   Benign:")
    print(f"      Mean: {benign['SFI'].mean():.4f}")
    print(f"      Median: {benign['SFI'].median():.4f}")
    print(f"      SD: {benign['SFI'].std():.4f}")
    print(f"      Range: [{benign['SFI'].min():.4f}, {benign['SFI'].max():.4f}]")

    # Mann-Whitney U test
    u_stat, p_value = stats.mannwhitneyu(pathogenic["SFI"], benign["SFI"], alternative="greater")

    print(f"\n🔬 Mann-Whitney U Test:")
    print(f"   U statistic: {u_stat:.1f}")
    print(f"   p-value (one-tailed): {p_value:.6f}")

    # Cohen's d effect size
    d = cohens_d(pathogenic["SFI"].values, benign["SFI"].values)
    print(f"\n📏 Cohen's d: {d:.4f}")

    if abs(d) < 0.2:
        effect_size = "negligible"
    elif abs(d) < 0.5:
        effect_size = "small"
    elif abs(d) < 0.8:
        effect_size = "medium"
    else:
        effect_size = "large"

    print(f"   Interpretation: {effect_size} effect size")

    # ROC AUC (if both classes present)
    labels = sfi_labeled["Label"].map({"Pathogenic": 1, "Benign": 0})
    if labels.nunique() == 2:
        auc = roc_auc_score(labels, sfi_labeled["SFI"])
        print(f"\n📊 ROC AUC: {auc:.4f}")
    else:
        auc = None

    # Decision criteria (locus-specific)
    if args.locus == "tp53":
        # TP53: positive control, expect signal
        success_criteria = {
            "p < 0.05": p_value < 0.05,
            "AUC > 0.60 (if computable)": auc is None or auc > 0.60,
        }
        expected = "SIGNAL DETECTED"
    elif args.locus == "brca1" and args.category == "synonymous":
        # BRCA1 synonymous: negative control, expect null
        success_criteria = {
            "p > 0.05 (null expected)": p_value > 0.05,
            "AUC ≈ 0.5 (if computable)": auc is None or (0.45 <= auc <= 0.55),
        }
        expected = "NULL (correct)"
    else:
        # Generic: expect signal
        success_criteria = {"p < 0.05": p_value < 0.05}
        expected = "SIGNAL"

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    all_pass = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {criterion}")

    print()

    if all_pass:
        print(f"🎉 {expected}: PASS")
        verdict = "PASS"
    else:
        print(f"❌ {expected}: FAIL")
        verdict = "FAIL"

    # Save results
    output_name = f"H1_{locus_upper}{'_' + args.category if args.category else ''}_validation.txt"
    output_path = RESULTS_DIR / output_name

    with open(output_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write(f"H1 Cross-Locus Validation: {locus_upper}\n")
        if args.category:
            f.write(f"Category: {args.category}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Sample sizes: Pathogenic={len(pathogenic)}, Benign={len(benign)}\n\n")

        f.write("SFI Statistics:\n")
        f.write(f"  Path: Mean={pathogenic['SFI'].mean():.4f}, SD={pathogenic['SFI'].std():.4f}\n")
        f.write(f"  Ben:  Mean={benign['SFI'].mean():.4f}, SD={benign['SFI'].std():.4f}\n\n")

        f.write(f"Mann-Whitney: U={u_stat:.1f}, p={p_value:.6f}\n")
        f.write(f"Cohen's d: {d:.4f} ({effect_size})\n")
        if auc:
            f.write(f"ROC AUC: {auc:.4f}\n")
        f.write(f"\nVERDICT: {verdict}\n")

    print(f"\n📄 Results saved: {output_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
