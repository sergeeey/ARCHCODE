#!/usr/bin/env python3
"""
Final Validation Checks — Last Attempt
Three critical tests before archive/continue decision.

CHECK 1: Effective Independence Collapse
- Group HBB pearls by genomic windows (10/25/50/100 bp)
- Keep one representative per cluster
- Recalculate Mann-Whitney, Cohen's d, effect size
- Verdict: PASS if signal survives cluster-level, WEAK if p-value lost, FAIL if one hotspot

CHECK 2: Orthogonality Matrix
- 2D quadrant: SSIM high/low × CAGE high/low
- Test if dual-high enriches pathogenic
- Test if CAGE-only explains everything
- Verdict: PASS if 2D adds value, WEAK if CAGE-only, FAIL if random quadrants

CHECK 3: Blind Mini-Panel (deferred, requires new API calls)
- Pre-register 10 regulatory + 10 coding + 10 control from non-HBB/TERT loci
- AlphaGenome CAGE predictions
- Test mechanism specificity on new variants
- Verdict: PASS if regulatory>coding, WEAK if locus-specific, FAIL if HBB-only
"""

import json
import numpy as np
import scipy.stats as stats
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


# ============================================================================
# CHECK 1: EFFECTIVE INDEPENDENCE COLLAPSE
# ============================================================================


def group_by_genomic_windows(
    variants: List[Dict], window_sizes: List[int] = [10, 25, 50, 100]
) -> Dict:
    """Group variants by genomic proximity windows."""

    results = {}

    for window_bp in window_sizes:
        # Sort by position
        sorted_vars = sorted(variants, key=lambda x: x["position"])

        clusters = []
        current_cluster = [sorted_vars[0]]

        for var in sorted_vars[1:]:
            if var["position"] - current_cluster[-1]["position"] <= window_bp:
                current_cluster.append(var)
            else:
                clusters.append(current_cluster)
                current_cluster = [var]

        clusters.append(current_cluster)

        # Keep one representative per cluster: max |CAGE delta|
        representatives = []
        for cluster in clusters:
            rep = max(cluster, key=lambda x: abs(x["cage_pct"]))
            representatives.append(rep)

        results[window_bp] = {
            "n_clusters": len(clusters),
            "n_representatives": len(representatives),
            "representatives": representatives,
            "cluster_sizes": [len(c) for c in clusters],
        }

    return results


def recalculate_statistics(pearls: List[Dict], controls: List[Dict]) -> Dict:
    """Recalculate Mann-Whitney, Cohen's d on collapsed representatives."""

    pearl_cage = np.array([p["cage_pct"] for p in pearls])
    control_cage = np.array([c["cage_pct"] for c in controls])

    # Mann-Whitney U test (one-sided: pearls < controls)
    u_stat, p_value = stats.mannwhitneyu(pearl_cage, control_cage, alternative="less")

    # Cohen's d
    pooled_std = np.sqrt(
        (
            (len(pearl_cage) - 1) * np.var(pearl_cage, ddof=1)
            + (len(control_cage) - 1) * np.var(control_cage, ddof=1)
        )
        / (len(pearl_cage) + len(control_cage) - 2)
    )
    cohen_d = (np.mean(pearl_cage) - np.mean(control_cage)) / pooled_std

    # Fold difference
    fold_diff = (
        np.mean(pearl_cage) / np.mean(control_cage) if np.mean(control_cage) != 0 else np.inf
    )

    return {
        "n_pearls": len(pearl_cage),
        "n_controls": len(control_cage),
        "pearl_mean": float(np.mean(pearl_cage)),
        "control_mean": float(np.mean(control_cage)),
        "mann_whitney_u": float(u_stat),
        "mann_whitney_p": float(p_value),
        "cohen_d": float(cohen_d),
        "fold_difference": float(fold_diff),
    }


def check_1_independence_collapse(data_path: Path) -> Dict:
    """Execute CHECK 1: Effective Independence Collapse."""

    print("=" * 70)
    print("CHECK 1: EFFECTIVE INDEPENDENCE COLLAPSE")
    print("=" * 70)

    # Load data
    with open(data_path) as f:
        data = json.load(f)

    # Split groups
    pearls = [r for r in data["results"] if r["group"] == "PEARL"]
    controls = [r for r in data["results"] if r["group"] == "CONTROL"]

    print(f"\nOriginal (variant-level):")
    print(f"  Pearls: {len(pearls)}")
    print(f"  Controls: {len(controls)}")
    print(f"  Pearl mean CAGE: {data['pearl_mean_cage_pct']:.2f}%")
    print(f"  Control mean CAGE: {data['control_mean_cage_pct']:.2f}%")
    print(f"  Mann-Whitney p: {data['mann_whitney_p']:.6f}")
    print(f"  Cohen's d: {data['cohen_d']:.3f}")

    # Group pearls by genomic windows
    print("\n" + "-" * 70)
    print("Grouping pearls by genomic windows...")
    print("-" * 70)

    window_results = group_by_genomic_windows(pearls)

    collapse_stats = {}

    for window_bp, window_data in window_results.items():
        print(f"\n{window_bp}bp window:")
        print(f"  {len(pearls)} variants → {window_data['n_clusters']} clusters")
        print(f"  Cluster sizes: {window_data['cluster_sizes']}")

        # Recalculate statistics with representatives
        stats_result = recalculate_statistics(window_data["representatives"], controls)

        print(
            f"  Effective N: {stats_result['n_pearls']} pearls vs {stats_result['n_controls']} controls"
        )
        print(f"  Pearl mean CAGE: {stats_result['pearl_mean']:.2f}%")
        print(f"  Control mean CAGE: {stats_result['control_mean']:.2f}%")
        print(f"  Mann-Whitney p: {stats_result['mann_whitney_p']:.6f}")
        print(f"  Cohen's d: {stats_result['cohen_d']:.3f}")

        collapse_stats[window_bp] = {
            "window_bp": window_bp,
            "n_variants_original": len(pearls),
            "n_clusters": window_data["n_clusters"],
            "effective_n": stats_result["n_pearls"],
            "cluster_sizes": window_data["cluster_sizes"],
            **stats_result,
        }

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT:")
    print("=" * 70)

    # Check 100bp window (most conservative)
    conservative = collapse_stats[100]

    if conservative["mann_whitney_p"] < 0.001 and abs(conservative["cohen_d"]) > 0.8:
        verdict = "PASS"
        interpretation = (
            f"Signal survives cluster-level collapse at 100bp window.\n"
            f"  Effective N = {conservative['effective_n']} (from {len(pearls)} variants)\n"
            f"  p = {conservative['mann_whitney_p']:.6f} (still significant)\n"
            f"  Cohen's d = {conservative['cohen_d']:.3f} (large effect)\n"
            f"  → HBB signal is NOT one non-independent hotspot."
        )
    elif conservative["mann_whitney_p"] < 0.05:
        verdict = "WEAK"
        interpretation = (
            f"Effect survives but p-value weakened by cluster collapse.\n"
            f"  Effective N = {conservative['effective_n']} (from {len(pearls)} variants)\n"
            f"  p = {conservative['mann_whitney_p']:.6f} (marginal)\n"
            f"  → Signal exists but effective independence limited."
        )
    else:
        verdict = "FAIL"
        interpretation = (
            f"Signal lost after cluster-level collapse.\n"
            f"  Effective N = {conservative['effective_n']} (too few)\n"
            f"  p = {conservative['mann_whitney_p']:.3f} (not significant)\n"
            f"  → Entire result held by one genomic hotspot cluster."
        )

    print(f"  {verdict}")
    print()
    for line in interpretation.split("\n"):
        print(f"  {line}")

    return {
        "check": "CHECK_1_INDEPENDENCE_COLLAPSE",
        "verdict": verdict,
        "interpretation": interpretation,
        "original_stats": {
            "n_variants": len(pearls),
            "pearl_mean_cage_pct": data["pearl_mean_cage_pct"],
            "control_mean_cage_pct": data["control_mean_cage_pct"],
            "mann_whitney_p": data["mann_whitney_p"],
            "cohen_d": data["cohen_d"],
        },
        "collapse_stats": collapse_stats,
    }


# ============================================================================
# CHECK 2: ORTHOGONALITY MATRIX
# ============================================================================


def create_2d_quadrants(
    variants: List[Dict], ssim_threshold: float = None, cage_threshold: float = None
) -> Dict:
    """Create 2D quadrant classification: SSIM high/low × CAGE high/low."""

    # Extract values
    ssim_values = np.array([v["archcode_ssim"] for v in variants])
    cage_values = np.array([v["cage_pct"] for v in variants])

    # Auto-thresholds if not provided (median)
    if ssim_threshold is None:
        ssim_threshold = 1 - np.median(1 - ssim_values)  # Median fragility

    if cage_threshold is None:
        cage_threshold = np.median(cage_values)

    # Classify
    quadrants = {
        "A_dual_high": [],  # High structural + high CAGE
        "B_structural_only": [],  # High structural, low CAGE
        "C_cage_only": [],  # Low structural, high CAGE
        "D_dual_low": [],  # Low structural, low CAGE
    }

    for v in variants:
        structural_high = v["archcode_ssim"] < ssim_threshold  # Low SSIM = high fragility
        cage_high = v["cage_pct"] < cage_threshold  # Negative CAGE = disruption

        if structural_high and cage_high:
            quadrants["A_dual_high"].append(v)
        elif structural_high and not cage_high:
            quadrants["B_structural_only"].append(v)
        elif not structural_high and cage_high:
            quadrants["C_cage_only"].append(v)
        else:
            quadrants["D_dual_low"].append(v)

    return quadrants, ssim_threshold, cage_threshold


def check_2_orthogonality_matrix(data_path: Path) -> Dict:
    """Execute CHECK 2: Orthogonality Matrix."""

    print("\n" + "=" * 70)
    print("CHECK 2: ORTHOGONALITY MATRIX")
    print("=" * 70)

    # Load data
    with open(data_path) as f:
        data = json.load(f)

    all_variants = data["results"]

    # Create 2D quadrants
    quadrants, ssim_thresh, cage_thresh = create_2d_quadrants(all_variants)

    print(f"\nThresholds:")
    print(f"  SSIM < {ssim_thresh:.4f} = high structural fragility")
    print(f"  CAGE < {cage_thresh:.2f}% = high disruption")

    print(f"\nQuadrant Distribution:")
    for quad_name, quad_vars in quadrants.items():
        print(f"  {quad_name}: {len(quad_vars)} variants")

    # Enrichment analysis
    print("\n" + "-" * 70)
    print("Enrichment Analysis:")
    print("-" * 70)

    # Count pathogenic/pearl/control in each quadrant
    enrichment = {}

    for quad_name, quad_vars in quadrants.items():
        n_pearls = sum(1 for v in quad_vars if v["group"] == "PEARL")
        n_controls = sum(1 for v in quad_vars if v["group"] == "CONTROL")

        pearl_rate = n_pearls / len(quad_vars) if len(quad_vars) > 0 else 0

        enrichment[quad_name] = {
            "n_total": len(quad_vars),
            "n_pearls": n_pearls,
            "n_controls": n_controls,
            "pearl_rate": pearl_rate,
        }

        print(f"\n{quad_name}:")
        print(f"  Total: {len(quad_vars)}")
        print(f"  Pearls: {n_pearls} ({pearl_rate*100:.1f}%)")
        print(
            f"  Controls: {n_controls} ({(n_controls/len(quad_vars)*100 if len(quad_vars)>0 else 0):.1f}%)"
        )

    # Test: Is A (dual-high) enriched for pearls?
    a_pearl_rate = enrichment["A_dual_high"]["pearl_rate"]
    overall_pearl_rate = len([v for v in all_variants if v["group"] == "PEARL"]) / len(all_variants)

    print(f"\nOverall pearl rate: {overall_pearl_rate*100:.1f}%")
    print(f"Dual-high (A) pearl rate: {a_pearl_rate*100:.1f}%")
    print(f"Enrichment: {a_pearl_rate / overall_pearl_rate:.2f}×")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT:")
    print("=" * 70)

    if a_pearl_rate > 2 * overall_pearl_rate and enrichment["A_dual_high"]["n_pearls"] >= 5:
        verdict = "PASS"
        interpretation = (
            f"2D quadrant model adds value over CAGE-only.\n"
            f"  Dual-high (A) enriches pearls: {a_pearl_rate/overall_pearl_rate:.2f}× baseline\n"
            f"  → ARCHCODE and AlphaGenome are complementary, not redundant."
        )
    elif enrichment["C_cage_only"]["pearl_rate"] > a_pearl_rate:
        verdict = "WEAK"
        interpretation = (
            f"CAGE-only (C) explains pearls better than dual-high (A).\n"
            f"  CAGE-only pearl rate: {enrichment['C_cage_only']['pearl_rate']*100:.1f}%\n"
            f"  → ARCHCODE adds minimal orthogonal value."
        )
    else:
        verdict = "FAIL"
        interpretation = (
            f"Quadrants show no systematic enrichment.\n"
            f"  Pearl distribution appears random across 2D space.\n"
            f"  → No evidence of complementary mechanisms."
        )

    print(f"  {verdict}")
    print()
    for line in interpretation.split("\n"):
        print(f"  {line}")

    return {
        "check": "CHECK_2_ORTHOGONALITY_MATRIX",
        "verdict": verdict,
        "interpretation": interpretation,
        "thresholds": {"ssim_threshold": float(ssim_thresh), "cage_threshold": float(cage_thresh)},
        "quadrant_counts": {k: v["n_total"] for k, v in enrichment.items()},
        "enrichment": enrichment,
    }


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Execute final validation checks."""

    print("\n" + "=" * 70)
    print("FINAL VALIDATION CHECKS — LAST ATTEMPT")
    print("=" * 70)
    print()
    print("This is the final decision point for ARCHCODE project.")
    print("Three critical tests before archive/continue decision.")
    print()

    data_path = RESULTS_DIR / "alphagenome_pearl_vs_control.json"

    if not data_path.exists():
        print(f"ERROR: Data file not found: {data_path}")
        return

    # Execute checks
    results = {}

    # CHECK 1
    results["check_1"] = check_1_independence_collapse(data_path)

    # CHECK 2
    results["check_2"] = check_2_orthogonality_matrix(data_path)

    # CHECK 3 (deferred)
    print("\n" + "=" * 70)
    print("CHECK 3: BLIND MINI-PANEL")
    print("=" * 70)
    print("\nSTATUS: DEFERRED (requires new AlphaGenome API calls)")
    print()
    print("IF CHECK 1 and CHECK 2 both PASS or WEAK:")
    print("  → Proceed to blind mini-panel (10 regulatory + 10 coding + 10 control)")
    print("  → Cost: ~$20-40 USD AlphaGenome API")
    print()
    print("IF CHECK 1 or CHECK 2 FAIL:")
    print("  → No point spending money on blind panel")
    print("  → Archive project as falsification artifact")

    results["check_3"] = {
        "check": "CHECK_3_BLIND_MINI_PANEL",
        "status": "DEFERRED",
        "reason": "Waiting for CHECK 1 and CHECK 2 results",
    }

    # Overall verdict
    print("\n" + "=" * 70)
    print("OVERALL VERDICT:")
    print("=" * 70)

    c1_verdict = results["check_1"]["verdict"]
    c2_verdict = results["check_2"]["verdict"]

    if c1_verdict == "PASS" and c2_verdict in ["PASS", "WEAK"]:
        overall = "CONTINUE"
        recommendation = (
            "Both critical checks survived.\n"
            "  CHECK 1: Signal survives cluster-level collapse\n"
            f"  CHECK 2: {c2_verdict}\n"
            "\n"
            "RECOMMENDED ACTION:\n"
            "  1. Execute CHECK 3 (blind mini-panel) to validate mechanism specificity\n"
            "  2. If CHECK 3 PASS → 4-week paper sprint\n"
            "  3. If CHECK 3 FAIL → Archive as HBB-specific case study"
        )
    elif c1_verdict in ["PASS", "WEAK"] and c2_verdict == "FAIL":
        overall = "WEAK"
        recommendation = (
            "Mixed results.\n"
            f"  CHECK 1: {c1_verdict}\n"
            "  CHECK 2: FAIL (no orthogonality)\n"
            "\n"
            "RECOMMENDED ACTION:\n"
            "  Proceed with caution: AlphaGenome standalone may be the real signal.\n"
            "  ARCHCODE may add minimal value.\n"
            "  Consider reframing as 'AlphaGenome CAGE validation' rather than ARCHCODE paper."
        )
    else:
        overall = "ARCHIVE"
        recommendation = (
            "Critical checks failed.\n"
            f"  CHECK 1: {c1_verdict}\n"
            f"  CHECK 2: {c2_verdict}\n"
            "\n"
            "RECOMMENDED ACTION:\n"
            "  Archive project as falsification artifact.\n"
            "  Do NOT spend more resources on blind panel or wet-lab outreach.\n"
            "  Document as honest negative result case study.\n"
            "  Move to next priority (PyPop Paper 2, MemGraph, or new project)."
        )

    print(f"\n  {overall}")
    print()
    for line in recommendation.split("\n"):
        print(f"  {line}")

    results["overall"] = {"verdict": overall, "recommendation": recommendation}

    # Save results
    output_path = RESULTS_DIR / "final_validation_checks.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved: {output_path}")
    print()
    print("=" * 70)
    print("FINAL VALIDATION CHECKS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
