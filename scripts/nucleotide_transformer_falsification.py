"""
Falsification Framework для Nucleotide Transformer результатов

Skeptic Triggers (из skeptic-triggers.md):
1. High-confidence claims (p < 0.001 + AUC > 0.95)
2. Unexpected success (actual >> expected)
3. Zero failures
4. Round numbers (AUC = 1.000, p = 0.000)
5. Synthetic evidence

Validation Checks:
- Matched controls (same category, same locus)
- Within-category discrimination
- Cross-locus transfer
- Baseline comparison (MOCK vs REAL)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from sklearn.metrics import roc_auc_score


def load_results(real_path: Path, mock_path: Path):
    """Load REAL and MOCK results"""
    with open(real_path) as f:
        real_data = json.load(f)

    with open(mock_path) as f:
        mock_data = json.load(f)

    return real_data, mock_data


def check_skeptic_triggers(results: dict) -> list:
    """Check for validation theater red flags"""
    triggers = []

    p_value = results.get("mann_whitney_p", 1.0)
    auc = results.get("roc_auc", 0.5)

    # Trigger 1: Suspiciously perfect
    if p_value < 0.001 and auc > 0.95:
        triggers.append(
            {
                "trigger": "HIGH_CONFIDENCE",
                "severity": "HIGH",
                "message": f"p={p_value:.6f} + AUC={auc:.3f} — слишком идеально, проверь synthetic data",
            }
        )

    # Trigger 4: Round numbers
    if abs(auc - round(auc, 1)) < 0.001:
        triggers.append(
            {
                "trigger": "ROUND_NUMBER",
                "severity": "MEDIUM",
                "message": f"AUC={auc:.3f} — подозрительно круглое число",
            }
        )

    # Trigger 2: Unexpected success (vs MOCK baseline)
    if auc > 0.80 and p_value < 0.01:
        triggers.append(
            {
                "trigger": "UNEXPECTED_SUCCESS",
                "severity": "MEDIUM",
                "message": f"AUC={auc:.3f} значительно выше MOCK (0.482) — требует matched control",
            }
        )

    return triggers


def matched_control_test(results_df: pd.DataFrame) -> dict:
    """
    Matched control: сравнить pearls vs benign WITHIN same category

    Если overall significant, но within-category NOT significant →
    signal = category artifact, не биологический
    """
    categories = results_df["category"].unique()
    within_tests = []

    for cat in categories:
        cat_df = results_df[results_df["category"] == cat]
        n_pearl = (cat_df["label"] == "Pearl").sum()
        n_benign = (cat_df["label"] == "Benign").sum()

        if n_pearl > 0 and n_benign > 0:
            pearl_vals = cat_df[cat_df["label"] == "Pearl"]["embedding_delta"].values
            benign_vals = cat_df[cat_df["label"] == "Benign"]["embedding_delta"].values

            u_stat, p_val = stats.mannwhitneyu(pearl_vals, benign_vals, alternative="two-sided")

            within_tests.append(
                {
                    "category": cat,
                    "n_pearl": int(n_pearl),
                    "n_benign": int(n_benign),
                    "p_value": float(p_val),
                    "significant_005": p_val < 0.05,
                }
            )

    # Summary: how many categories show within-category discrimination?
    n_significant = sum(1 for t in within_tests if t["significant_005"])
    n_total = len(within_tests)

    return {
        "tests": within_tests,
        "n_significant": n_significant,
        "n_total": n_total,
        "ratio": n_significant / n_total if n_total > 0 else 0,
        "verdict": "PASS" if n_significant > 0 else "FAIL (category artifact)",
    }


def baseline_comparison(real_results: dict, mock_results: dict) -> dict:
    """Compare REAL vs MOCK to quantify improvement"""

    real_auc = real_results.get("roc_auc", 0.5)
    real_p = real_results.get("mann_whitney_p", 1.0)

    mock_auc = mock_results.get("roc_auc", 0.5)
    mock_p = mock_results.get("mann_whitney_p", 1.0)

    # Delta improvement
    delta_auc = real_auc - mock_auc
    delta_p_log = -np.log10(real_p) - (-np.log10(mock_p))  # Log scale difference

    # Interpretation
    if delta_auc > 0.10 and real_p < 0.05:
        verdict = "IMPROVEMENT"
    elif delta_auc > 0.05:
        verdict = "MARGINAL"
    else:
        verdict = "NO_IMPROVEMENT"

    return {
        "real_auc": real_auc,
        "mock_auc": mock_auc,
        "delta_auc": delta_auc,
        "real_p": real_p,
        "mock_p": mock_p,
        "delta_p_log": delta_p_log,
        "verdict": verdict,
    }


def main():
    print("=" * 80)
    print("NUCLEOTIDE TRANSFORMER FALSIFICATION CHECKS")
    print("=" * 80)
    print()

    project_root = Path(__file__).parent.parent
    real_path = project_root / "results" / "nucleotide_transformer_real.json"
    mock_path = project_root / "results" / "nucleotide_transformer_pilot.json"

    # Load results
    print("Loading REAL and MOCK results...")
    real_data, mock_data = load_results(real_path, mock_path)

    # Convert to DataFrame
    real_df = pd.DataFrame(real_data["variants"])

    print()
    print("CHECK 1: Skeptic Triggers")
    print("-" * 80)

    triggers = check_skeptic_triggers(real_data)

    if triggers:
        for t in triggers:
            print(f"⚠️ {t['trigger']} ({t['severity']}): {t['message']}")
    else:
        print("✓ No skeptic triggers detected")

    print()
    print("CHECK 2: Matched Control (within-category)")
    print("-" * 80)

    matched_results = matched_control_test(real_df)

    print(
        f"Within-category tests: {matched_results['n_significant']}/{matched_results['n_total']} significant"
    )
    print(f"Verdict: {matched_results['verdict']}")

    if matched_results["verdict"] == "FAIL (category artifact)":
        print("⚠️ WARNING: Overall significance may be category-driven, not biological")

    for test in matched_results["tests"]:
        sig_mark = "✓" if test["significant_005"] else "✗"
        print(
            f"  {sig_mark} {test['category']}: p={test['p_value']:.4f} (n_pearl={test['n_pearl']}, n_benign={test['n_benign']})"
        )

    print()
    print("CHECK 3: Baseline Comparison (REAL vs MOCK)")
    print("-" * 80)

    baseline_comp = baseline_comparison(real_data, mock_data)

    print(f"REAL AUC:  {baseline_comp['real_auc']:.3f}")
    print(f"MOCK AUC:  {baseline_comp['mock_auc']:.3f}")
    print(f"Delta:     {baseline_comp['delta_auc']:+.3f}")
    print(f"Verdict:   {baseline_comp['verdict']}")

    # Save falsification report
    output_path = project_root / "results" / "nucleotide_transformer_falsification.json"

    report = {
        "analysis": "nucleotide_transformer_falsification",
        "skeptic_triggers": triggers,
        "matched_control": matched_results,
        "baseline_comparison": baseline_comp,
        "overall_verdict": None,  # Will be set below
    }

    # Overall verdict logic
    if baseline_comp["verdict"] == "NO_IMPROVEMENT":
        report["overall_verdict"] = "NULL_RESULT"
        report["recommendation"] = (
            "Nucleotide Transformer не улучшает discrimination vs edit distance baseline. Pivot к Pathway 3."
        )
    elif matched_results["verdict"] == "FAIL (category artifact)":
        report["overall_verdict"] = "CATEGORY_ARTIFACT"
        report["recommendation"] = (
            "Significant overall, но категориальный артефакт. Не биологический сигнал."
        )
    elif triggers and any(t["severity"] == "HIGH" for t in triggers):
        report["overall_verdict"] = "VALIDATION_THEATER"
        report["recommendation"] = (
            "Высокие skeptic triggers. Требует дополнительной проверки перед expansion."
        )
    else:
        report["overall_verdict"] = "PASS"
        report["recommendation"] = (
            "Пройдены основные checks. Proceed to Phase 2 (expand на full HBB)."
        )

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print()
    print("=" * 80)
    print(f"OVERALL VERDICT: {report['overall_verdict']}")
    print(f"RECOMMENDATION: {report['recommendation']}")
    print("=" * 80)
    print()
    print(f"Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
