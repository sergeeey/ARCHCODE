#!/usr/bin/env python3
"""
ROC Curve + Quadrant Analysis for ARCHCODE.

Ground truth: ClinVar Pathogenic/LP = 1, Benign/LB = 0
Predictor: 1 - ARCHCODE_SSIM (higher = more pathogenic)

Output:
  - results/figures/fig_roc_curve.png
  - results/roc_analysis.json
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

COMBINED_CSV = Path(__file__).parent.parent / "results" / "HBB_Combined_Atlas.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "results" / "figures"
OUTPUT_JSON = Path(__file__).parent.parent / "results" / "roc_analysis.json"


def main():
    print("Loading combined atlas...")
    df = pd.read_csv(COMBINED_CSV)
    print(f"  Total: {len(df)} variants ({df['Label'].value_counts().to_dict()})")

    # Ground truth: 1 = Pathogenic, 0 = Benign
    y_true = (df["Label"] == "Pathogenic").astype(int).values
    ssim = df["ARCHCODE_SSIM"].astype(float).values

    # Predictor: 1 - SSIM (higher = more disrupted = more pathogenic)
    y_score = 1.0 - ssim

    # === ROC CURVE ===
    fpr, tpr, thresholds_roc = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    # Youden's J statistic: optimal threshold
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    best_threshold_disruption = thresholds_roc[best_idx]
    best_ssim_threshold = 1.0 - best_threshold_disruption
    best_sensitivity = tpr[best_idx]
    best_specificity = 1.0 - fpr[best_idx]

    print(f"\n--- ROC Analysis ---")
    print(f"  AUC: {roc_auc:.4f}")
    print(f"  Youden optimal threshold (1-SSIM): {best_threshold_disruption:.4f}")
    print(f"  Youden optimal SSIM threshold: {best_ssim_threshold:.4f}")
    print(f"  Sensitivity at optimal: {best_sensitivity:.4f}")
    print(f"  Specificity at optimal: {best_specificity:.4f}")

    # Check specific thresholds
    specific_thresholds = {
        "0.85": 1.0 - 0.85,
        "0.92": 1.0 - 0.92,
        "0.95": 1.0 - 0.95,
        "0.96": 1.0 - 0.96,
        "0.99": 1.0 - 0.99,
    }

    threshold_results = {}
    for label, thresh in specific_thresholds.items():
        idx = np.argmin(np.abs(thresholds_roc - thresh))
        sens = tpr[idx]
        spec = 1.0 - fpr[idx]
        j = sens + spec - 1
        threshold_results[f"SSIM_{label}"] = {
            "sensitivity": round(float(sens), 4),
            "specificity": round(float(spec), 4),
            "youden_j": round(float(j), 4),
        }
        print(f"  SSIM < {label}: Sens={sens:.3f}, Spec={spec:.3f}, J={j:.3f}")

    # === PRECISION-RECALL ===
    precision, recall, _ = precision_recall_curve(y_true, y_score)
    ap = average_precision_score(y_true, y_score)
    print(f"  Average Precision (AP): {ap:.4f}")

    # === QUADRANT ANALYSIS ===
    print(f"\n--- Quadrant Analysis ---")
    vep_scores = df["VEP_Score"].astype(float).values

    # Thresholds for quadrants
    ssim_thresh = 0.95
    vep_thresh = 0.30

    q1 = np.sum((ssim < ssim_thresh) & (vep_scores >= vep_thresh))  # Both detect
    q2 = np.sum((ssim < ssim_thresh) & (vep_scores < vep_thresh))   # ARCHCODE only (pearls)
    q3 = np.sum((ssim >= ssim_thresh) & (vep_scores >= vep_thresh))  # VEP only
    q4 = np.sum((ssim >= ssim_thresh) & (vep_scores < vep_thresh))   # Neither detects

    print(f"  Q1 (ARCHCODE + VEP detect): {q1}")
    print(f"  Q2 (ARCHCODE only / pearls): {q2}")
    print(f"  Q3 (VEP only): {q3}")
    print(f"  Q4 (Neither): {q4}")
    print(f"  Total: {q1 + q2 + q3 + q4}")

    # Quadrants by label
    for label_name in ["Pathogenic", "Benign"]:
        mask = df["Label"] == label_name
        sq1 = np.sum((ssim[mask] < ssim_thresh) & (vep_scores[mask] >= vep_thresh))
        sq2 = np.sum((ssim[mask] < ssim_thresh) & (vep_scores[mask] < vep_thresh))
        sq3 = np.sum((ssim[mask] >= ssim_thresh) & (vep_scores[mask] >= vep_thresh))
        sq4 = np.sum((ssim[mask] >= ssim_thresh) & (vep_scores[mask] < vep_thresh))
        print(f"  {label_name}: Q1={sq1}, Q2={sq2}, Q3={sq3}, Q4={sq4}")

    # === PLOT ROC CURVE ===
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: ROC Curve
    ax = axes[0]
    ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'ARCHCODE (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5, label='Random (AUC = 0.5)')
    ax.plot(fpr[best_idx], tpr[best_idx], 'ro', markersize=10,
            label=f'Youden optimum (SSIM = {best_ssim_threshold:.3f})')

    # Mark specific thresholds
    for label, thresh in [("0.95", 1.0 - 0.95), ("0.92", 1.0 - 0.92)]:
        idx = np.argmin(np.abs(thresholds_roc - thresh))
        ax.plot(fpr[idx], tpr[idx], 's', markersize=8, label=f'SSIM < {label}')

    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=12)
    ax.set_ylabel('True Positive Rate (Sensitivity)', fontsize=12)
    ax.set_title('A. ROC Curve: ARCHCODE Structural Pathogenicity', fontsize=13)
    ax.legend(loc='lower right', fontsize=9)
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.02])
    ax.grid(True, alpha=0.3)

    # Panel B: SSIM Distribution by Label
    ax2 = axes[1]
    path_ssim = ssim[y_true == 1]
    benign_ssim = ssim[y_true == 0]

    ax2.hist(benign_ssim, bins=50, alpha=0.7, color='green', label=f'Benign (n={len(benign_ssim)})',
             density=True, edgecolor='darkgreen', linewidth=0.5)
    ax2.hist(path_ssim, bins=50, alpha=0.7, color='red', label=f'Pathogenic (n={len(path_ssim)})',
             density=True, edgecolor='darkred', linewidth=0.5)

    ax2.axvline(best_ssim_threshold, color='black', linestyle='--', linewidth=1.5,
                label=f'Youden threshold = {best_ssim_threshold:.3f}')
    ax2.axvline(0.95, color='blue', linestyle=':', linewidth=1.5,
                label='Current threshold = 0.95')

    ax2.set_xlabel('ARCHCODE SSIM', fontsize=12)
    ax2.set_ylabel('Density', fontsize=12)
    ax2.set_title('B. SSIM Distribution: Pathogenic vs Benign', fontsize=13)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "fig_roc_curve.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {fig_path}")

    # === SAVE RESULTS ===
    results = {
        "roc": {
            "auc": round(float(roc_auc), 4),
            "youden_optimal_ssim_threshold": round(float(best_ssim_threshold), 4),
            "youden_sensitivity": round(float(best_sensitivity), 4),
            "youden_specificity": round(float(best_specificity), 4),
            "average_precision": round(float(ap), 4),
        },
        "thresholds": threshold_results,
        "quadrants": {
            "ssim_threshold": ssim_thresh,
            "vep_threshold": vep_thresh,
            "total": {
                "Q1_both_detect": int(q1),
                "Q2_archcode_only": int(q2),
                "Q3_vep_only": int(q3),
                "Q4_neither": int(q4),
            },
        },
        "dataset": {
            "total": len(df),
            "pathogenic": int(np.sum(y_true == 1)),
            "benign": int(np.sum(y_true == 0)),
            "pathogenic_mean_ssim": round(float(path_ssim.mean()), 4),
            "benign_mean_ssim": round(float(benign_ssim.mean()), 4),
        },
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {OUTPUT_JSON}")

    return 0


if __name__ == "__main__":
    exit(main())
