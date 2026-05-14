"""
Н1: ARCHCODE + VEP Router

Hypothesis: VEP as upstream router improves precision without losing recall.

Kill Criterion:
- Precision < 0.90 on VEP-routed cases OR
- Recall@99% precision не улучшается vs ARCHCODE alone

Approach:
1. VEP filter: HIGH/MODERATE impact → route to ARCHCODE, else → benign
2. Measure: precision, recall, F1 vs ARCHCODE baseline
3. Find optimal VEP threshold for routing
"""

import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc
import json
from pathlib import Path
import matplotlib.pyplot as plt


def classify_archcode(row):
    """ARCHCODE verdict classification."""
    verdict = row["ARCHCODE_Verdict"]
    if pd.isna(verdict):
        return "VUS"

    verdict_lower = str(verdict).lower()

    if "pathogenic" in verdict_lower:
        return "Pathogenic"
    elif "benign" in verdict_lower:
        return "Benign"
    else:
        return "VUS"


def vep_router(row, impact_threshold="MODERATE", score_threshold=0.5):
    """
    VEP router decision.

    Returns: 'route_to_archcode' or 'benign_fast_path'
    """
    vep_impact = row["VEP_Impact"]
    vep_score = row["VEP_Score"]

    # Impact priority (HIGH > MODERATE > LOW > MODIFIER)
    impact_levels = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "MODIFIER": 0}

    impact_val = impact_levels.get(vep_impact, 0)
    threshold_val = impact_levels.get(impact_threshold, 2)

    # Route to ARCHCODE if HIGH/MODERATE impact OR VEP score > threshold
    if impact_val >= threshold_val or vep_score >= score_threshold:
        return "route_to_archcode"
    else:
        return "benign_fast_path"


def evaluate_router(df, impact_threshold="MODERATE", score_threshold=0.5):
    """Evaluate VEP router performance."""

    # Apply router
    df["vep_route"] = df.apply(
        lambda row: vep_router(row, impact_threshold, score_threshold), axis=1
    )

    # Router predictions
    # If routed to ARCHCODE → use ARCHCODE verdict
    # If fast path → predict benign
    df["router_prediction"] = df.apply(
        lambda row: row["archcode_prediction"]
        if row["vep_route"] == "route_to_archcode"
        else "Benign",
        axis=1,
    )

    # Metrics
    y_true = (df["Label"] == "Pathogenic").astype(int)
    y_pred_archcode = (df["archcode_prediction"] == "Pathogenic").astype(int)
    y_pred_router = (df["router_prediction"] == "Pathogenic").astype(int)

    # ARCHCODE baseline
    archcode_precision = precision_score(y_true, y_pred_archcode, zero_division=0)
    archcode_recall = recall_score(y_true, y_pred_archcode, zero_division=0)
    archcode_f1 = f1_score(y_true, y_pred_archcode, zero_division=0)

    # VEP router
    router_precision = precision_score(y_true, y_pred_router, zero_division=0)
    router_recall = recall_score(y_true, y_pred_router, zero_division=0)
    router_f1 = f1_score(y_true, y_pred_router, zero_division=0)

    # Routing statistics
    n_routed = (df["vep_route"] == "route_to_archcode").sum()
    n_fast = (df["vep_route"] == "benign_fast_path").sum()

    # Fast path accuracy
    fast_df = df[df["vep_route"] == "benign_fast_path"]
    fast_accuracy = (fast_df["Label"] == "Benign").sum() / len(fast_df) if len(fast_df) > 0 else 0.0

    # Routed accuracy
    routed_df = df[df["vep_route"] == "route_to_archcode"]
    routed_accuracy = (
        (routed_df["router_prediction"] == routed_df["Label"]).sum() / len(routed_df)
        if len(routed_df) > 0
        else 0.0
    )

    return {
        "impact_threshold": impact_threshold,
        "score_threshold": score_threshold,
        "archcode": {
            "precision": float(archcode_precision),
            "recall": float(archcode_recall),
            "f1": float(archcode_f1),
        },
        "router": {
            "precision": float(router_precision),
            "recall": float(router_recall),
            "f1": float(router_f1),
        },
        "routing_stats": {
            "n_routed_to_archcode": int(n_routed),
            "n_fast_path": int(n_fast),
            "percent_routed": float(n_routed / len(df) * 100),
            "fast_path_accuracy": float(fast_accuracy),
            "routed_accuracy": float(routed_accuracy),
        },
        "delta": {
            "precision": float(router_precision - archcode_precision),
            "recall": float(router_recall - archcode_recall),
            "f1": float(router_f1 - archcode_f1),
        },
    }


def grid_search_thresholds(df):
    """Grid search for optimal VEP thresholds."""

    impact_thresholds = ["HIGH", "MODERATE", "LOW"]
    score_thresholds = [0.3, 0.5, 0.7, 0.9]

    results = []

    for impact in impact_thresholds:
        for score in score_thresholds:
            result = evaluate_router(df, impact, score)
            result["config"] = f"{impact}+{score}"
            results.append(result)

    return results


def main():
    # Load HBB Atlas
    atlas_path = Path("D:/ДНК/results/HBB_Unified_Atlas.csv")
    df = pd.read_csv(atlas_path)

    print(f"Loaded {len(df)} HBB variants")

    # Filter to pathogenic/benign
    df = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()

    print(f"Pathogenic/Benign: {len(df)}")
    print(f"  Pathogenic: {(df['Label'] == 'Pathogenic').sum()}")
    print(f"  Benign: {(df['Label'] == 'Benign').sum()}")

    # ARCHCODE predictions
    df["archcode_prediction"] = df.apply(classify_archcode, axis=1)

    # VEP distribution
    print(f"\nVEP Impact distribution:")
    print(df["VEP_Impact"].value_counts())

    print(f"\nVEP Score stats:")
    print(df["VEP_Score"].describe())

    # Baseline ARCHCODE performance
    print("\n" + "=" * 60)
    print("BASELINE: ARCHCODE ALONE")
    print("=" * 60)

    y_true = (df["Label"] == "Pathogenic").astype(int)
    y_pred = (df["archcode_prediction"] == "Pathogenic").astype(int)

    baseline_precision = precision_score(y_true, y_pred, zero_division=0)
    baseline_recall = recall_score(y_true, y_pred, zero_division=0)
    baseline_f1 = f1_score(y_true, y_pred, zero_division=0)

    print(f"Precision: {baseline_precision:.4f}")
    print(f"Recall: {baseline_recall:.4f}")
    print(f"F1: {baseline_f1:.4f}")

    # Grid search
    print("\n" + "=" * 60)
    print("VEP ROUTER GRID SEARCH")
    print("=" * 60)

    grid_results = grid_search_thresholds(df)

    # Find best configuration
    best_f1 = max(grid_results, key=lambda x: x["router"]["f1"])
    best_precision = max(grid_results, key=lambda x: x["router"]["precision"])

    print(f"\nBest F1 configuration: {best_f1['config']}")
    print(f"  Router F1: {best_f1['router']['f1']:.4f} (ARCHCODE: {best_f1['archcode']['f1']:.4f})")
    print(f"  ΔF1: {best_f1['delta']['f1']:+.4f}")
    print(f"  Routed: {best_f1['routing_stats']['percent_routed']:.1f}%")

    print(f"\nBest Precision configuration: {best_precision['config']}")
    print(f"  Router Precision: {best_precision['router']['precision']:.4f}")
    print(f"  Router Recall: {best_precision['router']['recall']:.4f}")
    print(f"  Routed: {best_precision['routing_stats']['percent_routed']:.1f}%")

    # Evaluate best config in detail
    best_config = best_f1  # Use best F1 as default

    impact_th = best_config["impact_threshold"]
    score_th = best_config["score_threshold"]

    df["vep_route"] = df.apply(lambda row: vep_router(row, impact_th, score_th), axis=1)
    df["router_prediction"] = df.apply(
        lambda row: row["archcode_prediction"]
        if row["vep_route"] == "route_to_archcode"
        else "Benign",
        axis=1,
    )

    print("\n" + "=" * 60)
    print(f"DETAILED ANALYSIS: {best_config['config']}")
    print("=" * 60)

    # Confusion matrix
    routed_df = df[df["vep_route"] == "route_to_archcode"]
    fast_df = df[df["vep_route"] == "benign_fast_path"]

    print(f"\nRouted to ARCHCODE: {len(routed_df)} ({len(routed_df)/len(df)*100:.1f}%)")
    print(f"  Pathogenic: {(routed_df['Label'] == 'Pathogenic').sum()}")
    print(f"  Benign: {(routed_df['Label'] == 'Benign').sum()}")

    print(f"\nFast path (auto-benign): {len(fast_df)} ({len(fast_df)/len(df)*100:.1f}%)")
    print(f"  Pathogenic (missed): {(fast_df['Label'] == 'Pathogenic').sum()}")
    print(f"  Benign (correct): {(fast_df['Label'] == 'Benign').sum()}")
    print(f"  Fast path accuracy: {best_config['routing_stats']['fast_path_accuracy']:.4f}")

    # VERDICT
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    kill_criteria_met = []

    # Kill Criterion 1: Precision < 0.90
    if best_precision["router"]["precision"] < 0.90:
        kill_criteria_met.append(
            f"Router precision {best_precision['router']['precision']:.4f} < 0.90"
        )

    # Kill Criterion 2: No recall improvement
    if best_config["delta"]["recall"] <= 0:
        kill_criteria_met.append(
            f"Router recall {best_config['router']['recall']:.4f} ≤ "
            f"ARCHCODE recall {best_config['archcode']['recall']:.4f}"
        )

    # Kill Criterion 3: F1 decreases
    if best_config["delta"]["f1"] < 0:
        kill_criteria_met.append(
            f"Router F1 {best_config['router']['f1']:.4f} < "
            f"ARCHCODE F1 {best_config['archcode']['f1']:.4f}"
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
        confidence = "HIGH" if best_config["delta"]["f1"] > 0.05 else "MEDIUM"
        print(f"✓ {verdict} (confidence: {confidence})")
        print(f"\nVEP router improves F1 by {best_config['delta']['f1']:+.4f}")
        print(
            f"Computational savings: {best_config['routing_stats']['n_fast_path']} variants "
            f"({100 - best_config['routing_stats']['percent_routed']:.1f}%) skip ARCHCODE"
        )

    # Save results
    output = {
        "hypothesis": "H1: ARCHCODE + VEP Router",
        "data_source": "HBB_Unified_Atlas.csv",
        "n_variants": len(df),
        "baseline_archcode": {
            "precision": float(baseline_precision),
            "recall": float(baseline_recall),
            "f1": float(baseline_f1),
        },
        "best_config": best_config,
        "grid_search_results": grid_results,
        "kill_criteria": kill_criteria_met,
        "verdict": verdict,
        "confidence": confidence,
        "notes": [
            "VEP scores already cached in HBB Atlas (ENCFF* datasets)",
            "Router: VEP HIGH/MODERATE → ARCHCODE, else → benign",
            "Computational savings from fast path (benign predictions)",
        ],
    }

    output_path = Path("D:/ДНК/results/H1_vep_router_test.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Precision-Recall tradeoff
    configs = [r["config"] for r in grid_results]
    precisions = [r["router"]["precision"] for r in grid_results]
    recalls = [r["router"]["recall"] for r in grid_results]
    f1s = [r["router"]["f1"] for r in grid_results]

    ax1.scatter(recalls, precisions, c=f1s, cmap="viridis", s=100, alpha=0.7)
    ax1.scatter(
        [baseline_recall],
        [baseline_precision],
        marker="*",
        s=300,
        c="red",
        label="ARCHCODE baseline",
        edgecolor="black",
    )

    # Annotate best
    ax1.scatter(
        [best_config["router"]["recall"]],
        [best_config["router"]["precision"]],
        marker="D",
        s=200,
        c="gold",
        label="Best router",
        edgecolor="black",
    )

    ax1.set_xlabel("Recall")
    ax1.set_ylabel("Precision")
    ax1.set_title("VEP Router: Precision-Recall Tradeoff")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_xlim([0, 1.05])
    ax1.set_ylim([0, 1.05])

    # Routing efficiency
    percents_routed = [r["routing_stats"]["percent_routed"] for r in grid_results]

    ax2.scatter(percents_routed, f1s, s=100, alpha=0.7)
    ax2.axhline(baseline_f1, color="red", linestyle="--", label="ARCHCODE F1")
    ax2.scatter(
        [best_config["routing_stats"]["percent_routed"]],
        [best_config["router"]["f1"]],
        marker="D",
        s=200,
        c="gold",
        label="Best config",
        edgecolor="black",
    )

    ax2.set_xlabel("% Variants Routed to ARCHCODE")
    ax2.set_ylabel("F1 Score")
    ax2.set_title("VEP Router: Efficiency vs Performance")
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    fig_path = Path("D:/ДНК/results/fig_H1_vep_router.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to: {fig_path}")

    return output


if __name__ == "__main__":
    result = main()
