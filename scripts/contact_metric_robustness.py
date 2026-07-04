"""
EXP-006: Contact Metric Robustness
====================================
Tests whether pearl identification is robust across contact comparison metrics.
Uses 4 pre-computed metrics from atlas CSVs: SSIM, LSSIM, DeltaInsulation, LoopIntegrity.
Also derives: 1-SSIM (disruption score), 1-LSSIM (local disruption score).

If pearls are SSIM-specific artifacts, other metrics won't separate P/LP from B/LB.
Metric-independence confirms the structural signal is real biology, not an SSIM quirk.

Usage: python scripts/contact_metric_robustness.py
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

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

# Metrics to compare: name -> (column, direction)
# direction: "lower_is_disrupted" means lower values = more disruption (pathogenic)
# direction: "higher_is_disrupted" means higher values = more disruption
METRICS = {
    "SSIM": ("ARCHCODE_SSIM", "lower_is_disrupted"),
    "LSSIM": ("ARCHCODE_LSSIM", "lower_is_disrupted"),
    "DeltaInsulation": ("ARCHCODE_DeltaInsulation", "higher_is_disrupted"),
    "LoopIntegrity": ("ARCHCODE_LoopIntegrity", "higher_is_disrupted"),
}


def load_labeled(path):
    """Load atlas, return labeled subset with binary label."""
    df = pd.read_csv(path)
    plp = df["ClinVar_Significance"].str.contains("athogenic", na=False)
    blb = df["ClinVar_Significance"].str.contains("enign", na=False)
    mask = plp | blb
    df_out = df[mask].copy()
    df_out["label"] = plp[mask].astype(int)
    return df_out


def safe_auc(y_true, y_score):
    if len(set(y_true)) < 2:
        return np.nan
    try:
        return roc_auc_score(y_true, y_score)
    except ValueError:
        return np.nan


def find_structural_calls(values, labels, direction, target_fpr=0.01):
    """Find threshold where FPR ≤ target_fpr, return call set."""
    benign_vals = values[labels == 0]
    if len(benign_vals) == 0:
        return np.zeros(len(values), dtype=bool), 0.0

    if direction == "lower_is_disrupted":
        # Lower values = disrupted → threshold = low percentile of benign
        threshold = np.percentile(benign_vals, target_fpr * 100)
        calls = values < threshold
    else:
        # Higher values = disrupted → threshold = high percentile of benign
        threshold = np.percentile(benign_vals, (1 - target_fpr) * 100)
        calls = values > threshold

    return calls, threshold


def jaccard(set_a, set_b):
    """Jaccard similarity between two boolean arrays."""
    intersection = (set_a & set_b).sum()
    union = (set_a | set_b).sum()
    if union == 0:
        return 1.0  # both empty = identical
    return intersection / union


def main():
    print("=" * 70)
    print("EXP-006: Contact Metric Robustness")
    print("=" * 70)

    # Load all loci
    all_dfs = []
    per_locus = {}
    for locus, path in ATLAS_FILES.items():
        if not os.path.exists(path):
            print(f"  SKIP {locus}: file not found")
            continue
        df = load_labeled(path)
        # Check all metrics exist
        missing = [m for m, (col, _) in METRICS.items() if col not in df.columns]
        if missing:
            print(f"  SKIP {locus}: missing columns {missing}")
            continue
        # Drop rows with NaN in any metric
        metric_cols = [col for col, _ in METRICS.values()]
        df = df.dropna(subset=metric_cols)
        if len(df) < 10:
            print(f"  SKIP {locus}: only {len(df)} labeled variants")
            continue
        df["locus"] = locus
        all_dfs.append(df)
        per_locus[locus] = df
        n_plp = int(df["label"].sum())
        n_blb = len(df) - n_plp
        print(f"  Loaded {locus}: {len(df)} labeled ({n_plp} P/LP, {n_blb} B/LB)")

    if not all_dfs:
        print("ERROR: No data loaded")
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\n  Combined: {len(combined)} variants across {len(per_locus)} loci")

    # ── 1. Per-metric AUC (combined) ─────────────────────────────
    print("\n" + "=" * 70)
    print("=== 1. Per-Metric AUC (Combined Across Loci) ===\n")

    metric_results = {}
    for metric_name, (col, direction) in METRICS.items():
        values = combined[col].values
        labels = combined["label"].values

        # For AUC: score should be higher for pathogenic
        if direction == "lower_is_disrupted":
            scores = 1 - values  # invert: lower SSIM → higher disruption score
        else:
            scores = values

        auc = safe_auc(labels, scores)
        metric_results[metric_name] = {"auc_combined": round(auc, 4) if not np.isnan(auc) else None}
        print(
            f"  {metric_name:20s}  AUC = {auc:.4f}"
            if not np.isnan(auc)
            else f"  {metric_name:20s}  AUC = N/A"
        )

    # ── 2. Per-locus AUC per metric ──────────────────────────────
    print("\n" + "=" * 70)
    print("=== 2. Per-Locus AUC Per Metric ===\n")

    locus_metric_aucs = {}
    header = f"  {'Locus':8s}"
    for m in METRICS:
        header += f"  {m:18s}"
    print(header)
    print("  " + "-" * (8 + 20 * len(METRICS)))

    for locus, df in sorted(per_locus.items()):
        labels = df["label"].values
        row = f"  {locus:8s}"
        locus_metric_aucs[locus] = {}
        for metric_name, (col, direction) in METRICS.items():
            values = df[col].values
            if direction == "lower_is_disrupted":
                scores = 1 - values
            else:
                scores = values
            auc = safe_auc(labels, scores)
            auc_str = f"{auc:.4f}" if not np.isnan(auc) else "N/A"
            row += f"  {auc_str:18s}"
            locus_metric_aucs[locus][metric_name] = round(auc, 4) if not np.isnan(auc) else None
        print(row)

    # ── 3. Pearl set concordance (Jaccard) ───────────────────────
    print("\n" + "=" * 70)
    print("=== 3. Structural Call Concordance (Jaccard Similarity) ===\n")

    # Focus on HBB (richest pearl set)
    if "HBB" in per_locus:
        hbb = per_locus["HBB"]
        labels = hbb["label"].values
        call_sets = {}

        for metric_name, (col, direction) in METRICS.items():
            values = hbb[col].values
            calls, threshold = find_structural_calls(values, labels, direction)
            call_sets[metric_name] = calls
            n_calls = int(calls.sum())
            n_tp = int((calls & (labels == 1)).sum())
            print(
                f"  {metric_name:20s}  calls={n_calls:4d}  TP={n_tp:4d}  threshold={threshold:.4f}"
            )

        # Pairwise Jaccard
        print("\n  Pairwise Jaccard similarity:")
        metric_names = list(METRICS.keys())
        jaccard_matrix = {}
        header = f"  {'':20s}"
        for m in metric_names:
            header += f"  {m:12s}"
        print(header)
        for m1 in metric_names:
            row = f"  {m1:20s}"
            jaccard_matrix[m1] = {}
            for m2 in metric_names:
                j = jaccard(call_sets[m1], call_sets[m2])
                row += f"  {j:12.3f}"
                jaccard_matrix[m1][m2] = round(j, 4)
            print(row)
    else:
        jaccard_matrix = {}

    # ── 4. Metric correlation analysis ───────────────────────────
    print("\n" + "=" * 70)
    print("=== 4. Inter-Metric Correlation (Spearman) ===\n")

    from scipy.stats import spearmanr

    metric_names = list(METRICS.keys())
    corr_matrix = {}
    header = f"  {'':20s}"
    for m in metric_names:
        header += f"  {m:12s}"
    print(header)
    for m1 in metric_names:
        corr_matrix[m1] = {}
        row = f"  {m1:20s}"
        for m2 in metric_names:
            col1 = METRICS[m1][0]
            col2 = METRICS[m2][0]
            rho, _ = spearmanr(combined[col1].values, combined[col2].values)
            row += f"  {rho:12.3f}"
            corr_matrix[m1][m2] = round(rho, 4)
        print(row)

    # ── 5. Sensitivity at matched specificity ────────────────────
    print("\n" + "=" * 70)
    print("=== 5. Sensitivity at 99% Specificity (Combined) ===\n")

    sensitivity_results = {}
    for metric_name, (col, direction) in METRICS.items():
        values = combined[col].values
        labels = combined["label"].values

        if direction == "lower_is_disrupted":
            scores = 1 - values
        else:
            scores = values

        # Find sensitivity at FPR ≤ 1%
        fpr_arr, tpr_arr, _ = roc_curve(labels, scores)
        # Find closest FPR ≤ 0.01
        valid = fpr_arr <= 0.01
        if valid.any():
            sens = tpr_arr[valid][-1]
        else:
            sens = 0.0

        sensitivity_results[metric_name] = round(sens, 4)
        print(f"  {metric_name:20s}  Sensitivity@99%Spec = {sens:.4f}")

    # ── 6. Metric agreement on pathogenic vs benign ──────────────
    print("\n" + "=" * 70)
    print("=== 6. Mean Metric Values: Pathogenic vs Benign ===\n")

    mean_comparison = {}
    for metric_name, (col, direction) in METRICS.items():
        plp_mean = combined.loc[combined["label"] == 1, col].mean()
        blb_mean = combined.loc[combined["label"] == 0, col].mean()
        delta = plp_mean - blb_mean
        mean_comparison[metric_name] = {
            "plp_mean": round(plp_mean, 6),
            "blb_mean": round(blb_mean, 6),
            "delta": round(delta, 6),
        }
        print(
            f"  {metric_name:20s}  P/LP={plp_mean:.6f}  B/LB={blb_mean:.6f}  "
            f"Δ={delta:+.6f}  {'↓' if delta < 0 else '↑'}"
        )

    # ── Save results ─────────────────────────────────────────────
    os.makedirs("analysis", exist_ok=True)

    summary = {
        "experiment": "EXP-006: Contact Metric Robustness",
        "n_loci": len(per_locus),
        "n_variants": len(combined),
        "metrics_compared": list(METRICS.keys()),
        "combined_auc": {m: metric_results[m]["auc_combined"] for m in METRICS},
        "per_locus_auc": locus_metric_aucs,
        "sensitivity_at_99spec": sensitivity_results,
        "mean_comparison": mean_comparison,
        "spearman_correlation": corr_matrix,
        "jaccard_concordance_hbb": jaccard_matrix,
    }

    with open("analysis/contact_metric_robustness_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: analysis/contact_metric_robustness_summary.json")

    # ── Figure ───────────────────────────────────────────────────
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Panel A: Combined AUC per metric
        ax = axes[0]
        metric_names_plot = list(METRICS.keys())
        aucs_plot = [
            metric_results[m]["auc_combined"] if metric_results[m]["auc_combined"] else 0.5
            for m in metric_names_plot
        ]
        colors = ["#2196F3", "#E53935", "#4CAF50", "#FF9800"]
        bars = ax.bar(
            metric_names_plot, aucs_plot, color=colors, alpha=0.85, edgecolor="black", linewidth=0.5
        )
        ax.axhline(0.5, color="gray", linewidth=1, linestyle="--", label="Random")
        ax.set_ylabel("AUC (Combined)")
        ax.set_title("A. AUC Per Contact Metric", fontweight="bold")
        ax.set_ylim(0.4, 0.75)
        for bar, auc_val in zip(bars, aucs_plot):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f"{auc_val:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        # Panel B: Per-locus AUC heatmap
        ax = axes[1]
        loci_list = sorted(per_locus.keys())
        heatmap_data = []
        for locus in loci_list:
            row = []
            for m in metric_names_plot:
                val = locus_metric_aucs[locus].get(m)
                row.append(val if val is not None else 0.5)
            heatmap_data.append(row)
        heatmap_arr = np.array(heatmap_data)
        im = ax.imshow(heatmap_arr, cmap="RdYlGn", vmin=0.3, vmax=1.0, aspect="auto")
        ax.set_xticks(range(len(metric_names_plot)))
        ax.set_xticklabels(metric_names_plot, rotation=45, ha="right")
        ax.set_yticks(range(len(loci_list)))
        ax.set_yticklabels(loci_list)
        ax.set_title("B. Per-Locus AUC Heatmap", fontweight="bold")
        # Add text annotations
        for i in range(len(loci_list)):
            for j in range(len(metric_names_plot)):
                val = heatmap_arr[i, j]
                color = "white" if val < 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7, color=color)
        plt.colorbar(im, ax=ax, shrink=0.8, label="AUC")

        # Panel C: Spearman correlation matrix
        ax = axes[2]
        corr_data = []
        for m1 in metric_names_plot:
            row = [corr_matrix[m1][m2] for m2 in metric_names_plot]
            corr_data.append(row)
        corr_arr = np.array(corr_data)
        im2 = ax.imshow(corr_arr, cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(metric_names_plot)))
        ax.set_xticklabels(metric_names_plot, rotation=45, ha="right")
        ax.set_yticks(range(len(metric_names_plot)))
        ax.set_yticklabels(metric_names_plot)
        ax.set_title("C. Inter-Metric Spearman ρ", fontweight="bold")
        for i in range(len(metric_names_plot)):
            for j in range(len(metric_names_plot)):
                ax.text(j, i, f"{corr_arr[i, j]:.2f}", ha="center", va="center", fontsize=9)
        plt.colorbar(im2, ax=ax, shrink=0.8, label="Spearman ρ")

        plt.tight_layout()
        os.makedirs("figures", exist_ok=True)
        plt.savefig("figures/fig_contact_metric_robustness.pdf", bbox_inches="tight", dpi=300)
        plt.savefig("figures/fig_contact_metric_robustness.png", bbox_inches="tight", dpi=200)
        plt.close()
        print("Saved: figures/fig_contact_metric_robustness.pdf + .png")
    except ImportError:
        print("matplotlib not available — skipping figure")


if __name__ == "__main__":
    main()
