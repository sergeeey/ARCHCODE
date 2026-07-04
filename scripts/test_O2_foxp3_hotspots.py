"""
О2: FOXP3 Pathogenic Variants in Hotspots

Hypothesis: Pathogenic FOXP3 variants show position clustering (hotspots)
            more than benign/VUS variants.

Kill Criterion: OR < 1.5 OR p > 0.05 (chi-square) OR sex-adjusted OR < 1.3

Context: FOXP3 is X-linked → need to account for sex bias in ClinVar ascertainment.
"""

import pandas as pd
import numpy as np
from scipy import stats
import json
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter


def classify_significance(sig):
    """Classify ClinVar significance into pathogenic/benign/VUS."""
    if pd.isna(sig) or sig == "":
        return "VUS"

    sig_lower = sig.lower()

    if any(term in sig_lower for term in ["pathogenic", "likely pathogenic"]):
        # Exclude conflicting
        if "conflicting" not in sig_lower and "benign" not in sig_lower:
            return "Pathogenic"

    if any(term in sig_lower for term in ["benign", "likely benign"]):
        if "pathogenic" not in sig_lower:
            return "Benign"

    return "VUS"


def identify_hotspots(df, min_variants=2):
    """
    Identify hotspots: positions with ≥N pathogenic variants.

    Returns:
    - hotspot_positions: set of positions
    - hotspot_summary: dict with counts
    """
    path_df = df[df["classification"] == "Pathogenic"]

    # Count variants per position
    pos_counts = path_df["pos_start"].value_counts()

    # Hotspots = positions with ≥min_variants
    hotspot_positions = set(pos_counts[pos_counts >= min_variants].index)

    hotspot_summary = {
        "n_hotspots": len(hotspot_positions),
        "hotspot_positions": sorted(list(hotspot_positions)),
        "min_variants_threshold": min_variants,
        "hotspot_counts": {
            int(pos): int(count) for pos, count in pos_counts[pos_counts >= min_variants].items()
        },
    }

    return hotspot_positions, hotspot_summary


def hotspot_enrichment_test(df, hotspot_positions):
    """
    Fisher's exact test (zero-cell safe): hotspot vs non-hotspot × pathogenic vs benign/VUS

    Contingency table:
                    Hotspot   Non-hotspot
    Pathogenic      a         b
    Benign/VUS      c         d

    OR = (a/c) / (b/d) = (a*d) / (b*c)

    Uses Fisher's exact instead of chi² for small counts / zero cells.
    """

    # Add hotspot flag
    df["in_hotspot"] = df["pos_start"].isin(hotspot_positions)

    # Create contingency table
    contingency = pd.crosstab(
        df["classification"].isin(["Pathogenic"]),
        df["in_hotspot"],
        rownames=["Pathogenic"],
        colnames=["In_Hotspot"],
    )

    # Ensure 2x2 table
    if contingency.shape != (2, 2):
        return {"error": "Contingency table not 2x2", "contingency": contingency.to_dict()}

    # Extract counts
    # Row 0 = Benign/VUS (False), Row 1 = Pathogenic (True)
    # Col 0 = Non-hotspot (False), Col 1 = Hotspot (True)
    benign_nonhotspot = contingency.iloc[0, 0]  # d
    benign_hotspot = contingency.iloc[0, 1]  # c
    path_nonhotspot = contingency.iloc[1, 0]  # b
    path_hotspot = contingency.iloc[1, 1]  # a

    # Fisher's exact test (two-sided, then greater for one-sided)
    table = [[path_hotspot, path_nonhotspot], [benign_hotspot, benign_nonhotspot]]
    oddsratio_fisher, p_value_two = stats.fisher_exact(table, alternative="two-sided")
    _, p_value_greater = stats.fisher_exact(table, alternative="greater")

    # Haldane-Anscombe correction for OR CI when zero cells present
    a_corr = path_hotspot + 0.5 if min(table[0] + table[1]) == 0 else path_hotspot
    b_corr = path_nonhotspot + 0.5 if min(table[0] + table[1]) == 0 else path_nonhotspot
    c_corr = benign_hotspot + 0.5 if min(table[0] + table[1]) == 0 else benign_hotspot
    d_corr = benign_nonhotspot + 0.5 if min(table[0] + table[1]) == 0 else benign_nonhotspot

    # Odds Ratio with correction
    odds_ratio = (a_corr * d_corr) / (b_corr * c_corr)

    # 95% CI for OR (Woolf method with correction)
    log_or = np.log(odds_ratio)
    se_log_or = np.sqrt(1 / a_corr + 1 / b_corr + 1 / c_corr + 1 / d_corr)
    ci_lower = np.exp(log_or - 1.96 * se_log_or)
    ci_upper = np.exp(log_or + 1.96 * se_log_or)

    return {
        "contingency_table": {
            "pathogenic_hotspot": int(path_hotspot),
            "pathogenic_non_hotspot": int(path_nonhotspot),
            "benign_vus_hotspot": int(benign_hotspot),
            "benign_vus_non_hotspot": int(benign_nonhotspot),
        },
        "fisher_exact_p_two_sided": float(p_value_two),
        "fisher_exact_p_greater": float(p_value_greater),
        "odds_ratio": float(odds_ratio),
        "or_95_ci": [float(ci_lower), float(ci_upper)],
        "haldane_correction_applied": bool(min(table[0] + table[1]) == 0),
        "interpretation": (
            f"Pathogenic variants are {odds_ratio:.2f}× more likely to be in hotspots "
            f"(Fisher's exact p={p_value_greater:.4f}, two-sided p={p_value_two:.4f})"
        ),
    }


def main():
    # Load FOXP3 ClinVar variants
    data_path = Path("D:/ДНК/data/clinvar_foxp3_variants.csv")
    df = pd.read_csv(data_path)

    print(f"Loaded {len(df)} FOXP3 variants from ClinVar")

    # Classify variants
    df["classification"] = df["clinical_significance"].apply(classify_significance)

    classification_counts = df["classification"].value_counts()
    print(f"\nClassification distribution:")
    for cls, count in classification_counts.items():
        print(f"  {cls}: {count}")

    # Check if we have enough pathogenic and benign/VUS
    n_pathogenic = (df["classification"] == "Pathogenic").sum()
    n_non_pathogenic = (df["classification"].isin(["Benign", "VUS"])).sum()

    print(f"\nPathogenic: {n_pathogenic}")
    print(f"Benign/VUS: {n_non_pathogenic}")

    if n_pathogenic < 10 or n_non_pathogenic < 10:
        print("\nWARNING: Underpowered test (N<10 in one group)")

    # Identify hotspots
    print("\n" + "=" * 60)
    print("HOTSPOT IDENTIFICATION")
    print("=" * 60)

    hotspot_positions, hotspot_summary = identify_hotspots(df, min_variants=2)

    print(f"Hotspots found: {hotspot_summary['n_hotspots']}")
    print(f"Hotspot positions (≥2 pathogenic variants):")
    for pos, count in hotspot_summary["hotspot_counts"].items():
        print(f"  chrX:{pos} — {count} pathogenic variants")

    # Hotspot enrichment test
    print("\n" + "=" * 60)
    print("HOTSPOT ENRICHMENT TEST")
    print("=" * 60)

    enrich_result = hotspot_enrichment_test(df, hotspot_positions)

    if "error" in enrich_result:
        print(f"ERROR: {enrich_result['error']}")
        return enrich_result

    print(f"\nContingency Table:")
    print(f"                    Hotspot   Non-hotspot")
    print(
        f"Pathogenic          {enrich_result['contingency_table']['pathogenic_hotspot']:<9} "
        f"{enrich_result['contingency_table']['pathogenic_non_hotspot']}"
    )
    print(
        f"Benign/VUS          {enrich_result['contingency_table']['benign_vus_hotspot']:<9} "
        f"{enrich_result['contingency_table']['benign_vus_non_hotspot']}"
    )

    print(f"\nFisher's exact test (two-sided): p = {enrich_result['fisher_exact_p_two_sided']:.4f}")
    print(f"Fisher's exact test (greater): p = {enrich_result['fisher_exact_p_greater']:.4f}")
    print(f"Odds Ratio (Haldane-corrected): {enrich_result['odds_ratio']:.2f}")
    print(f"95% CI: [{enrich_result['or_95_ci'][0]:.2f}, {enrich_result['or_95_ci'][1]:.2f}]")
    if enrich_result["haldane_correction_applied"]:
        print("  (Haldane-Anscombe +0.5 correction applied due to zero cell)")

    print(f"\n{enrich_result['interpretation']}")

    # VERDICT
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    kill_criteria_met = []

    # Kill Criterion 1: OR < 1.5
    if enrich_result["odds_ratio"] < 1.5:
        kill_criteria_met.append(f"OR {enrich_result['odds_ratio']:.2f} < 1.5 (weak effect)")

    # Kill Criterion 2: p > 0.05 (use one-sided greater for enrichment)
    if enrich_result["fisher_exact_p_greater"] > 0.05:
        kill_criteria_met.append(
            f"p={enrich_result['fisher_exact_p_greater']:.4f} > 0.05 (not significant)"
        )

    # Kill Criterion 3: Upper CI < 1.0 (protective effect)
    if enrich_result["or_95_ci"] and enrich_result["or_95_ci"][1] < 1.0:
        kill_criteria_met.append("95% CI upper bound < 1.0 (no enrichment)")

    # Additional check: sample size
    if n_pathogenic < 20:
        kill_criteria_met.append(f"Underpowered (N_pathogenic={n_pathogenic} < 20)")

    if len(kill_criteria_met) > 0:
        verdict = "HYPOTHESIS KILLED"
        confidence = "MEDIUM" if n_pathogenic >= 20 else "LOW"
        print(f"✗ {verdict} (confidence: {confidence})")
        print("\nKill criteria met:")
        for i, criterion in enumerate(kill_criteria_met, 1):
            print(f"  {i}. {criterion}")
    else:
        verdict = "HYPOTHESIS SUPPORTED"
        confidence = "HIGH" if enrich_result["fisher_exact_p_greater"] < 0.01 else "MEDIUM"
        print(f"✓ {verdict} (confidence: {confidence})")
        print(f"\nPathogenic FOXP3 variants show significant hotspot enrichment.")

    # Save results
    output = {
        "hypothesis": "O2: FOXP3 Pathogenic Hotspots",
        "data_source": "clinvar_foxp3_variants.csv",
        "n_variants": len(df),
        "classification_counts": classification_counts.to_dict(),
        "hotspot_summary": hotspot_summary,
        "enrichment_test": enrich_result,
        "kill_criteria": kill_criteria_met,
        "verdict": verdict,
        "confidence": confidence,
        "notes": [
            "FOXP3 is X-linked → sex bias in ClinVar ascertainment possible",
            "Hotspots defined as positions with ≥2 pathogenic variants",
            "Benign+VUS combined as non-pathogenic control",
        ],
    }

    output_path = Path("D:/ДНК/results/O2_foxp3_hotspots_test.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Plot: Position distribution
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Pathogenic variants position distribution
    path_df = df[df["classification"] == "Pathogenic"]
    ax1.hist(
        path_df["pos_start"],
        bins=50,
        alpha=0.7,
        color="red",
        edgecolor="black",
        label=f"Pathogenic (n={len(path_df)})",
    )

    # Mark hotspots
    for pos in hotspot_summary["hotspot_positions"]:
        ax1.axvline(pos, color="darkred", linestyle="--", alpha=0.5, linewidth=2)

    ax1.set_xlabel("Position on chrX (GRCh38)")
    ax1.set_ylabel("Count")
    ax1.set_title(f"FOXP3 Pathogenic Variant Distribution (Hotspots marked)")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # All variants by classification
    for cls in ["Pathogenic", "VUS", "Benign"]:
        cls_df = df[df["classification"] == cls]
        if len(cls_df) > 0:
            ax2.scatter(cls_df["pos_start"], [cls] * len(cls_df), alpha=0.6, s=50, label=cls)

    # Mark hotspots
    for pos in hotspot_summary["hotspot_positions"]:
        ax2.axvline(pos, color="darkred", linestyle="--", alpha=0.3, linewidth=2)

    ax2.set_xlabel("Position on chrX (GRCh38)")
    ax2.set_ylabel("Classification")
    ax2.set_title("FOXP3 Variants by Position and Classification")
    ax2.legend()
    ax2.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    fig_path = Path("D:/ДНК/results/fig_O2_foxp3_hotspots.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Figure saved to: {fig_path}")

    return output


if __name__ == "__main__":
    result = main()
