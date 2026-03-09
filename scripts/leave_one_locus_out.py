"""
EXP-002: Leave-One-Locus-Out Evaluation
========================================
For each of 9 primary loci: derive threshold from 8, test on 1.
Reports per-locus AUC, sensitivity at FPR ≤ 1%, and pearl detection rate.

Tests whether HBB-derived insights generalize — or whether HBB is an outlier.

Usage: python scripts/leave_one_locus_out.py
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ATLAS_FILES = {
    "HBB": "results/HBB_Unified_Atlas.csv",
    "BRCA1": "results/BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "results/TP53_Unified_Atlas_300kb.csv",
    "TERT": "results/TERT_Unified_Atlas_300kb.csv",
    "MLH1": "results/MLH1_Unified_Atlas_300kb.csv",
    "CFTR": "results/CFTR_Unified_Atlas_317kb.csv",
    "SCN5A": "results/SCN5A_Unified_Atlas_400kb.csv",
    "GJB2": "results/GJB2_Unified_Atlas_300kb.csv",
    "LDLR": "results/LDLR_Unified_Atlas_300kb.csv",
}


def load_labeled(path):
    """Load atlas, return labeled subset with binary label."""
    df = pd.read_csv(path)
    plp = df["ClinVar_Significance"].str.contains("athogenic", na=False)
    blb = df["ClinVar_Significance"].str.contains("enign", na=False)
    mask = plp | blb
    df_out = df[mask].copy()
    df_out["label"] = plp[mask].astype(int)
    df_out = df_out.dropna(subset=["ARCHCODE_LSSIM"])
    return df_out


def find_threshold_at_fpr(lssim, labels, target_fpr=0.01):
    """Find LSSIM threshold where FPR ≤ target on training data.
    Lower LSSIM = more disruptive = positive prediction.
    """
    benign_lssim = lssim[labels == 0]
    if len(benign_lssim) == 0:
        return 0.95  # fallback
    # Threshold = percentile of benign LSSIM distribution
    # FPR ≤ 1% means ≤1% of benign below threshold
    threshold = np.percentile(benign_lssim, target_fpr * 100)
    return threshold


def safe_auc(y_true, y_score):
    if len(set(y_true)) < 2:
        return np.nan
    try:
        return roc_auc_score(y_true, y_score)
    except ValueError:
        return np.nan


def main():
    print("=" * 70)
    print("EXP-002: Leave-One-Locus-Out Evaluation")
    print("=" * 70)

    # Load all loci
    all_loci = {}
    for locus, path in ATLAS_FILES.items():
        if os.path.exists(path):
            df = load_labeled(path)
            if len(df) >= 5:
                all_loci[locus] = df
                print(
                    f"  Loaded {locus}: {len(df)} labeled variants "
                    f"({int(df['label'].sum())} P/LP, {int((1 - df['label']).sum())} B/LB)"
                )

    locus_names = sorted(all_loci.keys())
    results = []

    print(f"\nRunning {len(locus_names)}-fold leave-one-locus-out...\n")

    for held_out in locus_names:
        # Train: all loci except held_out
        train_dfs = [all_loci[l] for l in locus_names if l != held_out]
        train = pd.concat(train_dfs, ignore_index=True)

        test = all_loci[held_out]

        train_lssim = train["ARCHCODE_LSSIM"].values
        train_labels = train["label"].values
        test_lssim = test["ARCHCODE_LSSIM"].values
        test_labels = test["label"].values

        # Derive threshold from training data at FPR ≤ 1%
        threshold = find_threshold_at_fpr(train_lssim, train_labels, target_fpr=0.01)

        # Score: 1 - LSSIM (higher = more disrupted)
        test_scores = 1 - test_lssim

        # AUC on held-out locus
        auc = safe_auc(test_labels, test_scores)

        # Predictions at derived threshold
        predictions = test_lssim < threshold

        # Sensitivity (recall for pathogenic)
        n_plp = int(test_labels.sum())
        n_blb = int((1 - test_labels).sum())
        tp = int((predictions & (test_labels == 1)).sum())
        fp = int((predictions & (test_labels == 0)).sum())
        sensitivity = tp / n_plp if n_plp > 0 else 0.0
        fpr = fp / n_blb if n_blb > 0 else 0.0

        # Pearl detection: how many pearls (if any) in held-out locus
        has_pearl_col = "Pearl" in test.columns
        if has_pearl_col:
            pearl_mask = test["Pearl"].fillna(False).astype(bool)
            n_pearls_total = int(pearl_mask.sum())
            n_pearls_detected = int((pearl_mask & predictions).sum())
        else:
            n_pearls_total = 0
            n_pearls_detected = 0

        result = {
            "held_out_locus": held_out,
            "n_train": len(train),
            "n_test": len(test),
            "n_plp_test": n_plp,
            "n_blb_test": n_blb,
            "threshold_derived": round(threshold, 4),
            "auc_test": round(auc, 4) if not np.isnan(auc) else None,
            "sensitivity_at_fpr1pct": round(sensitivity, 4),
            "actual_fpr": round(fpr, 4),
            "tp": tp,
            "fp": fp,
            "n_pearls_total": n_pearls_total,
            "n_pearls_detected": n_pearls_detected,
        }
        results.append(result)

        pearl_str = f"  Pearls: {n_pearls_detected}/{n_pearls_total}" if n_pearls_total > 0 else ""
        auc_str = f"{auc:.4f}" if not np.isnan(auc) else "N/A"
        print(
            f"  {held_out:8s}  threshold={threshold:.4f}  AUC={auc_str}  "
            f"sens={sensitivity:.3f}  FPR={fpr:.3f}  TP={tp} FP={fp}{pearl_str}"
        )

    # ── Summary statistics ───────────────────────────────────
    print("\n" + "=" * 70)
    print("=== Summary ===")

    aucs = [r["auc_test"] for r in results if r["auc_test"] is not None]
    sensitivities = [r["sensitivity_at_fpr1pct"] for r in results]

    if aucs:
        print(f"  Mean AUC across held-out loci: {np.mean(aucs):.4f} (±{np.std(aucs):.4f})")
        print(
            f"  Min AUC: {min(aucs):.4f} ({results[[r['auc_test'] for r in results].index(min(aucs))]['held_out_locus']})"
        )
        print(
            f"  Max AUC: {max(aucs):.4f} ({results[[r['auc_test'] for r in results].index(max(aucs))]['held_out_locus']})"
        )
    print(f"  Mean sensitivity: {np.mean(sensitivities):.4f}")

    # HBB-excluded analysis
    aucs_no_hbb = [
        r["auc_test"] for r in results if r["auc_test"] is not None and r["held_out_locus"] != "HBB"
    ]
    if aucs_no_hbb:
        print(f"\n  Without HBB held-out:")
        print(f"    Mean AUC: {np.mean(aucs_no_hbb):.4f} (±{np.std(aucs_no_hbb):.4f})")

    hbb_result = next((r for r in results if r["held_out_locus"] == "HBB"), None)
    if hbb_result and hbb_result["auc_test"] is not None:
        print(f"\n  HBB as held-out:")
        print(f"    AUC: {hbb_result['auc_test']}")
        print(f"    Threshold (from 8 other loci): {hbb_result['threshold_derived']}")
        print(
            f"    Pearls detected: {hbb_result['n_pearls_detected']}/{hbb_result['n_pearls_total']}"
        )

    # ── Save ─────────────────────────────────────────────────
    os.makedirs("analysis", exist_ok=True)

    df_results = pd.DataFrame(results)
    df_results.to_csv("analysis/leave_one_locus_out_results.csv", index=False)
    print(f"\nSaved: analysis/leave_one_locus_out_results.csv")

    summary = {
        "experiment": "EXP-002: Leave-One-Locus-Out",
        "date": "2026-03-09",
        "n_loci": len(results),
        "mean_auc": round(np.mean(aucs), 4) if aucs else None,
        "std_auc": round(np.std(aucs), 4) if aucs else None,
        "mean_sensitivity": round(np.mean(sensitivities), 4),
        "per_locus": results,
    }

    with open("analysis/leave_one_locus_out_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved: analysis/leave_one_locus_out_summary.json")

    # ── Figure ───────────────────────────────────────────────
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        loci = [r["held_out_locus"] for r in results]
        x = np.arange(len(loci))

        # Panel A: AUC per held-out locus
        ax = axes[0]
        auc_vals = [r["auc_test"] if r["auc_test"] is not None else 0.5 for r in results]
        colors = ["#E53935" if l == "HBB" else "#2196F3" for l in loci]
        ax.bar(x, auc_vals, color=colors, alpha=0.85, edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="gray", linewidth=1, linestyle="--", label="Random")
        if aucs:
            ax.axhline(
                np.mean(aucs),
                color="green",
                linewidth=1.5,
                linestyle="-",
                label=f"Mean AUC={np.mean(aucs):.3f}",
            )
        ax.set_xticks(x)
        ax.set_xticklabels(loci, rotation=45, ha="right")
        ax.set_ylabel("AUC on Held-Out Locus")
        ax.set_title("A. Leave-One-Locus-Out AUC", fontweight="bold")
        ax.legend(fontsize=9)
        ax.set_ylim(0.3, 1.05)

        # Panel B: Sensitivity + FPR
        ax = axes[1]
        sens_vals = [r["sensitivity_at_fpr1pct"] for r in results]
        fpr_vals = [r["actual_fpr"] for r in results]
        w = 0.35
        ax.bar(x - w / 2, sens_vals, w, label="Sensitivity", color="#4CAF50", alpha=0.85)
        ax.bar(x + w / 2, fpr_vals, w, label="FPR", color="#FF5722", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(loci, rotation=45, ha="right")
        ax.set_ylabel("Rate")
        ax.set_title("B. Sensitivity & FPR at Train-Derived Threshold", fontweight="bold")
        ax.legend(fontsize=9)
        ax.axhline(0.01, color="gray", linewidth=0.5, linestyle="--")
        ax.annotate("Target FPR=1%", (0, 0.015), fontsize=7, color="gray")

        plt.tight_layout()
        plt.savefig("figures/fig_leave_one_locus_out.pdf", bbox_inches="tight", dpi=300)
        plt.savefig("figures/fig_leave_one_locus_out.png", bbox_inches="tight", dpi=200)
        plt.close()
        print("Saved: figures/fig_leave_one_locus_out.pdf + .png")
    except ImportError:
        print("matplotlib not available — skipping figure")


if __name__ == "__main__":
    main()
