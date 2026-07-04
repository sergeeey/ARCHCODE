"""
О1: Tissue Match → AUC ↑

Hypothesis: Adding tissue_match as a feature improves classifier AUC.

Kill Criterion: ΔAUC < 0.02 OR category-matched control shows ΔAUC < 0.01

Context: Risk of category artifact (H2 showed category alone → AUC 0.98)
         Need category-matched control to avoid circularity.

Approach:
1. Baseline classifier: LSSIM + category → AUC_baseline
2. +tissue classifier: LSSIM + category + tissue_match → AUC_tissue
3. ΔAUC = AUC_tissue - AUC_baseline
4. Category-matched control: within each category, tissue_match adds signal?
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, classification_report, roc_curve
import json
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter


def load_hbb_atlas():
    """Load HBB Unified Atlas with LSSIM and category."""
    atlas_path = Path("D:/ДНК/results/HBB_Unified_Atlas.csv")
    df = pd.read_csv(atlas_path)

    # Filter to pathogenic vs benign (exclude VUS)
    df = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()

    # Encode label
    df["label_binary"] = (df["Label"] == "Pathogenic").astype(int)

    # Extract category
    df["category_code"] = df["Category"].fillna("unknown")

    # Tissue match: HBB in K562 (erythroid) = always matched
    # For this test, we'll use a synthetic tissue_match feature based on category
    # Promoter/regulatory variants = high tissue specificity (1)
    # Coding variants = lower tissue specificity (0)
    df["tissue_match"] = df["category_code"].apply(
        lambda x: 1
        if "promoter" in x.lower() or "regulatory" in x.lower() or "utr" in x.lower()
        else 0
    )

    return df


def category_matched_control(df, category):
    """
    Test ΔAUC within a single category (to avoid category leakage).

    Within category, compare:
    - Baseline: LSSIM only
    - +tissue: LSSIM + tissue_match
    """
    cat_df = df[df["category_code"] == category].copy()

    if len(cat_df) < 50:
        return None  # Too small for reliable test

    X_base = cat_df[["ARCHCODE_LSSIM"]]
    X_tissue = cat_df[["ARCHCODE_LSSIM", "tissue_match"]]
    y = cat_df["label_binary"]

    # Check class balance
    if y.sum() < 10 or (len(y) - y.sum()) < 10:
        return None  # Imbalanced

    # Cross-validation AUC
    clf_base = LogisticRegression(max_iter=1000, random_state=42)
    clf_tissue = LogisticRegression(max_iter=1000, random_state=42)

    try:
        auc_base = cross_val_score(clf_base, X_base, y, cv=5, scoring="roc_auc").mean()
        auc_tissue = cross_val_score(clf_tissue, X_tissue, y, cv=5, scoring="roc_auc").mean()
    except:
        return None

    return {
        "category": category,
        "n": len(cat_df),
        "n_pathogenic": int(y.sum()),
        "n_benign": int(len(y) - y.sum()),
        "auc_baseline": float(auc_base),
        "auc_tissue": float(auc_tissue),
        "delta_auc": float(auc_tissue - auc_base),
    }


def main():
    # Load data
    df = load_hbb_atlas()

    print(f"Loaded {len(df)} HBB variants (pathogenic/benign)")
    print(f"Pathogenic: {(df['label_binary'] == 1).sum()}")
    print(f"Benign: {(df['label_binary'] == 0).sum()}")

    # Category distribution
    print(f"\nCategory distribution:")
    print(df["category_code"].value_counts())

    # Tissue match distribution
    print(f"\nTissue match distribution:")
    print(f"  tissue_match=1: {(df['tissue_match'] == 1).sum()}")
    print(f"  tissue_match=0: {(df['tissue_match'] == 0).sum()}")

    # Check category × tissue_match correlation
    tissue_by_cat = df.groupby("category_code")["tissue_match"].mean()
    print(f"\nTissue match rate by category:")
    for cat, rate in tissue_by_cat.items():
        print(f"  {cat}: {rate:.2%}")

    # WARNING: If tissue_match ≈ category, this is H2 (category artifact) repeat
    if tissue_by_cat.max() - tissue_by_cat.min() > 0.8:
        print("\n⚠️  WARNING: tissue_match highly correlated with category!")
        print("   Risk of category artifact (H2 repeat).")

    # Encode category
    le = LabelEncoder()
    df["category_encoded"] = le.fit_transform(df["category_code"])

    # Prepare features
    X_base = df[["ARCHCODE_LSSIM", "category_encoded"]]
    X_tissue = df[["ARCHCODE_LSSIM", "category_encoded", "tissue_match"]]
    y = df["label_binary"]

    # Train/test split
    X_base_train, X_base_test, y_train, y_test = train_test_split(
        X_base, y, test_size=0.3, random_state=42, stratify=y
    )
    X_tissue_train, X_tissue_test, _, _ = train_test_split(
        X_tissue, y, test_size=0.3, random_state=42, stratify=y
    )

    # Baseline classifier
    print("\n" + "=" * 60)
    print("BASELINE CLASSIFIER (LSSIM + Category)")
    print("=" * 60)

    clf_base = LogisticRegression(max_iter=1000, random_state=42)
    clf_base.fit(X_base_train, y_train)

    y_pred_base = clf_base.predict(X_base_test)
    y_prob_base = clf_base.predict_proba(X_base_test)[:, 1]
    auc_base = roc_auc_score(y_test, y_prob_base)

    print(f"AUC (baseline): {auc_base:.4f}")
    print(classification_report(y_test, y_pred_base, target_names=["Benign", "Pathogenic"]))

    # +Tissue classifier
    print("\n" + "=" * 60)
    print("+TISSUE CLASSIFIER (LSSIM + Category + Tissue Match)")
    print("=" * 60)

    clf_tissue = LogisticRegression(max_iter=1000, random_state=42)
    clf_tissue.fit(X_tissue_train, y_train)

    y_pred_tissue = clf_tissue.predict(X_tissue_test)
    y_prob_tissue = clf_tissue.predict_proba(X_tissue_test)[:, 1]
    auc_tissue = roc_auc_score(y_test, y_prob_tissue)

    print(f"AUC (+tissue): {auc_tissue:.4f}")
    print(classification_report(y_test, y_pred_tissue, target_names=["Benign", "Pathogenic"]))

    # ΔAUC
    delta_auc = auc_tissue - auc_base
    print(f"\nΔAUC: {delta_auc:+.4f}")

    # Feature importance
    print(f"\nFeature coefficients (+tissue model):")
    feature_names = ["LSSIM", "Category", "Tissue Match"]
    for name, coef in zip(feature_names, clf_tissue.coef_[0]):
        print(f"  {name}: {coef:.4f}")

    # Category-matched control
    print("\n" + "=" * 60)
    print("CATEGORY-MATCHED CONTROL")
    print("=" * 60)

    category_results = []
    for cat in df["category_code"].unique():
        result = category_matched_control(df, cat)
        if result:
            category_results.append(result)
            print(f"\n{result['category']} (n={result['n']}):")
            print(f"  AUC baseline: {result['auc_baseline']:.4f}")
            print(f"  AUC +tissue: {result['auc_tissue']:.4f}")
            print(f"  ΔAUC: {result['delta_auc']:+.4f}")

    # Average category-matched ΔAUC
    if category_results:
        mean_delta_matched = np.mean([r["delta_auc"] for r in category_results])
        print(f"\nMean ΔAUC (category-matched): {mean_delta_matched:+.4f}")
    else:
        mean_delta_matched = None
        print("\nNo category-matched results (insufficient data)")

    # VERDICT
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    kill_criteria_met = []

    # Kill Criterion 1: ΔAUC < 0.02
    if delta_auc < 0.02:
        kill_criteria_met.append(f"ΔAUC {delta_auc:+.4f} < 0.02 (weak improvement)")

    # Kill Criterion 2: Category-matched ΔAUC < 0.01
    if mean_delta_matched is not None and mean_delta_matched < 0.01:
        kill_criteria_met.append(
            f"Category-matched ΔAUC {mean_delta_matched:+.4f} < 0.01 (category artifact)"
        )

    # Kill Criterion 3: tissue_match ≈ category (correlation check)
    tissue_category_corr = df[["tissue_match", "category_encoded"]].corr().iloc[0, 1]
    if abs(tissue_category_corr) > 0.7:
        kill_criteria_met.append(
            f"tissue_match × category correlation {tissue_category_corr:.2f} > 0.7 "
            "(tissue_match = category proxy, H2 artifact)"
        )

    if len(kill_criteria_met) > 0:
        verdict = "HYPOTHESIS KILLED"
        confidence = "HIGH"
        print(f"✗ {verdict} (confidence: {confidence})")
        print("\nKill criteria met:")
        for i, criterion in enumerate(kill_criteria_met, 1):
            print(f"  {i}. {criterion}")
    else:
        verdict = "HYPOTHESIS SUPPORTED"
        confidence = "HIGH" if delta_auc > 0.05 else "MEDIUM"
        print(f"✓ {verdict} (confidence: {confidence})")
        print(f"\nTissue match improves AUC by {delta_auc:+.4f}.")

    # Save results
    output = {
        "hypothesis": "O1: Tissue Match → AUC ↑",
        "data_source": "HBB_Unified_Atlas.csv",
        "n_variants": len(df),
        "n_pathogenic": int((df["label_binary"] == 1).sum()),
        "n_benign": int((df["label_binary"] == 0).sum()),
        "baseline_auc": float(auc_base),
        "tissue_auc": float(auc_tissue),
        "delta_auc": float(delta_auc),
        "category_matched_results": category_results,
        "mean_delta_matched": float(mean_delta_matched) if mean_delta_matched is not None else None,
        "tissue_category_correlation": float(tissue_category_corr),
        "kill_criteria": kill_criteria_met,
        "verdict": verdict,
        "confidence": confidence,
        "notes": [
            "Tissue match defined as: promoter/regulatory/UTR = 1, coding = 0",
            "HBB in K562 (erythroid) = always tissue-matched (synthetic feature for test)",
            "Category-matched control tests within-category ΔAUC to avoid H2 artifact",
        ],
    }

    output_path = Path("D:/ДНК/results/O1_tissue_match_auc_test.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Plot ROC curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ROC curve comparison
    fpr_base, tpr_base, _ = roc_curve(y_test, y_prob_base)
    fpr_tissue, tpr_tissue, _ = roc_curve(y_test, y_prob_tissue)

    ax1.plot(fpr_base, tpr_base, label=f"Baseline (AUC={auc_base:.3f})", linewidth=2)
    ax1.plot(fpr_tissue, tpr_tissue, label=f"+Tissue (AUC={auc_tissue:.3f})", linewidth=2)
    ax1.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random")
    ax1.set_xlabel("False Positive Rate")
    ax1.set_ylabel("True Positive Rate")
    ax1.set_title(f"ROC Curves (ΔAUC={delta_auc:+.4f})")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Category-matched ΔAUC
    if category_results:
        categories = [r["category"] for r in category_results]
        deltas = [r["delta_auc"] for r in category_results]

        ax2.barh(categories, deltas, alpha=0.7)
        ax2.axvline(0, color="red", linestyle="--", linewidth=2)
        ax2.axvline(0.01, color="orange", linestyle="--", alpha=0.5, label="Kill threshold (0.01)")
        ax2.set_xlabel("ΔAUC (category-matched)")
        ax2.set_title("Within-Category Tissue Match Effect")
        ax2.legend()
        ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    fig_path = Path("D:/ДНК/results/fig_O1_tissue_match_auc.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to: {fig_path}")

    return output


if __name__ == "__main__":
    result = main()
