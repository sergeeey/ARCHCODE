#!/usr/bin/env python3
"""
H2: Phase Boundary Correlation Analysis
========================================
Tests hypothesis: Pearl hotspots cluster in Φ≈1 critical regime.

Correlation test:
  - X: Φ parameter (phase boundary proximity)
  - Y: Pearl density (pearls per bin)
  - Expected: Spearman r > 0.4 if hypothesis valid

Success criteria:
  - Pearls cluster in Φ ∈ [0.7, 1.5] (narrow critical regime)
  - Spearman r > 0.4 between Φ and pearl density
  - p < 0.05 (statistically significant)

Usage:
    python scripts/phase_boundary_correlation.py --locus HBB
"""

import argparse
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_phi_distribution(locus: str) -> pd.DataFrame:
    """Load Φ spatial distribution"""
    phi_path = RESULTS_DIR / "phase_boundary" / "phi_spatial_distribution.csv"
    if not phi_path.exists():
        raise FileNotFoundError(
            f"Φ distribution not found: {phi_path}\n"
            f"Run: python scripts/compute_phase_parameter.py --locus {locus}"
        )

    df = pd.read_csv(phi_path)
    print(f"✅ Loaded Φ distribution: {len(df)} bins")
    return df


def load_pearl_positions(locus: str) -> pd.DataFrame:
    """Load pearl variant positions"""
    atlas_path = {
        "HBB": RESULTS_DIR / "HBB_Unified_Atlas.csv",
        "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
        "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    }.get(locus)

    if not atlas_path or not atlas_path.exists():
        raise FileNotFoundError(f"Atlas not found for {locus}: {atlas_path}")

    atlas = pd.read_csv(atlas_path)

    # Filter to pearls (HBB-specific column)
    if "Pearl" in atlas.columns:
        pearls = atlas[atlas["Pearl"] == True]
    else:
        # For other loci, use pathogenic as proxy
        pearls = atlas[atlas["Label"] == "Pathogenic"]

    print(f"✅ Loaded pearls: {len(pearls)} variants")
    return pearls


def compute_pearl_density_per_bin(
    phi_df: pd.DataFrame,
    pearls: pd.DataFrame,
    resolution: int = 600,
) -> pd.DataFrame:
    """Count pearls per genomic bin"""

    phi_df = phi_df.copy()
    phi_df["pearl_count"] = 0

    for idx, row in phi_df.iterrows():
        bin_start = row["genomic_position"]
        bin_end = bin_start + resolution

        # Count pearls in this bin
        pearls_in_bin = pearls[
            (pearls["Position_GRCh38"] >= bin_start) & (pearls["Position_GRCh38"] < bin_end)
        ]

        phi_df.at[idx, "pearl_count"] = len(pearls_in_bin)

    # Compute density (pearls per kb)
    phi_df["pearl_density"] = phi_df["pearl_count"] / (resolution / 1000)

    return phi_df


def main():
    parser = argparse.ArgumentParser(description="Phase boundary correlation analysis")
    parser.add_argument("--locus", default="HBB", help="Locus to analyze")
    args = parser.parse_args()

    print("=" * 70)
    print(f"H2: PHASE BOUNDARY CORRELATION — {args.locus}")
    print("=" * 70)

    # Load data
    phi_df = load_phi_distribution(args.locus)
    pearls = load_pearl_positions(args.locus)

    # Compute pearl density per bin
    data = compute_pearl_density_per_bin(phi_df, pearls)

    print(f"\n📊 Pearl distribution:")
    print(f"   Total pearls: {pearls.shape[0]}")
    print(f"   Bins with pearls: {(data['pearl_count'] > 0).sum()}/{len(data)}")
    print(f"   Max pearls per bin: {data['pearl_count'].max():.0f}")

    # Identify critical regime bins (Φ ≈ 1)
    critical_mask = (data["Phi"] >= 0.7) & (data["Phi"] <= 1.5)
    critical_bins = data[critical_mask]
    non_critical_bins = data[~critical_mask]

    pearls_in_critical = critical_bins["pearl_count"].sum()
    pearls_in_non_critical = non_critical_bins["pearl_count"].sum()

    print(f"\n🎯 Critical regime (Φ ∈ [0.7, 1.5]):")
    print(f"   Bins: {len(critical_bins)}/{len(data)} ({len(critical_bins)*100/len(data):.1f}%)")
    print(
        f"   Pearls in critical: {pearls_in_critical}/{len(pearls)} ({pearls_in_critical*100/len(pearls):.1f}%)"
    )
    print(f"   Pearls in non-critical: {pearls_in_non_critical}")

    # Enrichment test (Fisher's exact or chi-square)
    if len(critical_bins) > 0 and len(non_critical_bins) > 0:
        contingency = np.array(
            [
                [pearls_in_critical, len(critical_bins) - pearls_in_critical],
                [pearls_in_non_critical, len(non_critical_bins) - pearls_in_non_critical],
            ]
        )

        from scipy.stats import fisher_exact

        odds_ratio, p_fisher = fisher_exact(contingency, alternative="greater")

        print(f"\n📈 Enrichment test (Fisher's exact):")
        print(f"   Odds ratio: {odds_ratio:.2f}")
        print(f"   p-value: {p_fisher:.6f}")

        if p_fisher < 0.05:
            print(f"   ✅ Pearls significantly enriched in Φ≈1 regime")
        else:
            print(f"   ❌ No significant enrichment")

    # Spearman correlation: Φ vs pearl density
    rho, p_spearman = stats.spearmanr(data["Phi"], data["pearl_density"])

    print(f"\n🔬 Spearman correlation:")
    print(f"   Φ vs pearl_density: ρ = {rho:.4f}, p = {p_spearman:.6f}")

    # Interpretation
    if abs(rho) < 0.2:
        strength = "negligible"
    elif abs(rho) < 0.4:
        strength = "weak"
    elif abs(rho) < 0.6:
        strength = "moderate"
    else:
        strength = "strong"

    print(f"   Interpretation: {strength} correlation")

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    success_criteria = {
        "Pearls enriched in Φ ∈ [0.7, 1.5]": (
            pearls_in_critical > 0 and pearls_in_critical >= 0.5 * len(pearls)
        ),
        "Spearman r > 0.4": abs(rho) > 0.4,
        "p < 0.05": p_spearman < 0.05,
    }

    all_pass = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {criterion}")

    print()

    if all_pass:
        print("🎉 H2 HYPOTHESIS: PASS")
        print("\nPearls cluster in phase-transition regime (Φ≈1).")
        print("Critical sensitivity to loop extrusion parameters confirmed.")
        verdict = "PASS"
    else:
        print("❌ H2 HYPOTHESIS: FAIL")
        print("\nNo evidence for phase boundary clustering.")
        print("Pearls may be position-dependent, not parameter-sensitive.")
        verdict = "FAIL"

    # Save results
    output_path = RESULTS_DIR / "phase_boundary" / "correlation_results.txt"
    with open(output_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write(f"H2: Phase Boundary Correlation — {args.locus}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Pearls: {len(pearls)}\n")
        f.write(f"Critical bins (Φ∈[0.7,1.5]): {len(critical_bins)}/{len(data)}\n")
        f.write(f"Pearls in critical: {pearls_in_critical}/{len(pearls)}\n\n")

        f.write(f"Spearman ρ: {rho:.4f}, p={p_spearman:.6f}\n")
        if len(critical_bins) > 0:
            f.write(f"Fisher's exact: OR={odds_ratio:.2f}, p={p_fisher:.6f}\n")

        f.write(f"\nVERDICT: {verdict}\n")

    print(f"\n📄 Results saved: {output_path}")

    # Save detailed data
    data_path = RESULTS_DIR / "phase_boundary" / "phi_with_pearls.csv"
    data.to_csv(data_path, index=False)
    print(f"📄 Data saved: {data_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    exit(main())
