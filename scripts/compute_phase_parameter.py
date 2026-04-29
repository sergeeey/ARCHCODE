#!/usr/bin/env python3
"""
H2: Compute Φ Phase Parameter for Each Genomic Bin
===================================================
Reads parameter sweep results and computes spatial Φ distribution.

Φ = τ_cohesin × E_promoter / P_barrier

For each bin in HBB locus:
  - τ: cohesin residence time (from k_base)
  - E: local enhancer occupancy
  - P: CTCF barrier density

Output: results/phase_boundary/phi_spatial_distribution.csv

Usage:
    python scripts/compute_phase_parameter.py --locus HBB
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_sweep_results(locus: str) -> pd.DataFrame:
    """Load parameter sweep grid search results"""
    sweep_path = RESULTS_DIR / "phase_boundary" / "grid_search.csv"
    if not sweep_path.exists():
        raise FileNotFoundError(
            f"Grid search results not found: {sweep_path}\n"
            f"Run: npx tsx scripts/phase_boundary_parameter_sweep.ts --locus={locus}"
        )

    df = pd.read_csv(sweep_path)
    print(f"✅ Loaded grid search: {len(df)} parameter combinations")
    return df


def compute_spatial_phi_distribution(locus: str) -> pd.DataFrame:
    """
    Compute Φ for each genomic bin using baseline parameters

    For HBB:
    - Bins: 50 (30kb / 600bp resolution)
    - τ: constant (global cohesin residence time)
    - E: local enhancer occupancy
    - P: local CTCF barrier density
    """

    # Locus configuration (matches TypeScript)
    config = {
        "HBB": {
            "start": 5210000,
            "end": 5240000,
            "resolution": 600,
            "enhancers": [
                {"position": 5227000, "occupancy": 0.85, "name": "HBB_promoter"},
                {"position": 5225500, "occupancy": 0.75, "name": "3prime_HS1"},
                {"position": 5230000, "occupancy": 0.70, "name": "LCR_HS2"},
                {"position": 5233000, "occupancy": 0.65, "name": "LCR_HS3"},
            ],
            "ctcf_sites": [5212000, 5218000, 5224000, 5228000, 5232000, 5236000],
        }
    }

    locus_config = config.get(locus)
    if not locus_config:
        raise ValueError(f"Unknown locus: {locus}")

    start = locus_config["start"]
    end = locus_config["end"]
    resolution = locus_config["resolution"]
    n_bins = int(np.ceil((end - start) / resolution))

    print(f"\n📍 Computing spatial Φ distribution for {locus}")
    print(f"   Window: chr11:{start:,}-{end:,} ({n_bins} bins)")

    # Initialize arrays
    bins = []
    phi_values = []

    # Baseline τ (global, same for all bins)
    tau_baseline = 1.0

    for i in range(n_bins):
        genomic_pos = start + i * resolution

        # E: local enhancer occupancy
        E_local = 0.1  # background
        for enh in locus_config["enhancers"]:
            dist_bp = abs(genomic_pos - enh["position"])
            if dist_bp < 3000:  # 3kb window
                sigma = 1000  # bp
                E_local += enh["occupancy"] * np.exp(-0.5 * (dist_bp / sigma) ** 2)

        # P: local CTCF barrier density (count sites within ±3kb)
        P_local = 0.1  # background
        for ctcf_pos in locus_config["ctcf_sites"]:
            dist_bp = abs(genomic_pos - ctcf_pos)
            if dist_bp < 3000:
                P_local += 1.0 * np.exp(-0.5 * (dist_bp / 1000) ** 2)

        # Φ = τ × E / P
        phi = (tau_baseline * E_local) / max(P_local, 0.01)  # avoid division by zero

        bins.append(i)
        phi_values.append(phi)

    df = pd.DataFrame(
        {
            "bin": bins,
            "genomic_position": [start + i * resolution for i in bins],
            "Phi": phi_values,
        }
    )

    return df


def main():
    parser = argparse.ArgumentParser(description="Compute phase parameter Φ")
    parser.add_argument("--locus", default="HBB", help="Locus to analyze")
    args = parser.parse_args()

    print("=" * 70)
    print(f"H2: PHASE PARAMETER Φ COMPUTATION — {args.locus}")
    print("=" * 70)

    # Load parameter sweep results
    sweep_df = load_sweep_results(args.locus)

    print(f"\n📊 Parameter sweep statistics:")
    print(f"   Φ range: [{sweep_df['Phi'].min():.3f}, {sweep_df['Phi'].max():.3f}]")
    print(f"   Mean LSSIM: {sweep_df['mean_LSSIM'].mean():.4f}")

    # Compute spatial Φ distribution
    phi_spatial = compute_spatial_phi_distribution(args.locus)

    # Find critical regime bins (Φ ≈ 1)
    critical_bins = phi_spatial[(phi_spatial["Phi"] >= 0.7) & (phi_spatial["Phi"] <= 1.5)]

    print(f"\n🎯 Critical regime (Φ ∈ [0.7, 1.5]):")
    print(
        f"   {len(critical_bins)}/{len(phi_spatial)} bins ({len(critical_bins)*100/len(phi_spatial):.1f}%)"
    )
    print(f"   Genomic positions:")
    for _, row in critical_bins.iterrows():
        print(f"     chr11:{row['genomic_position']:,} (bin {row['bin']:.0f}, Φ={row['Phi']:.3f})")

    # Save results
    output_path = RESULTS_DIR / "phase_boundary" / "phi_spatial_distribution.csv"
    phi_spatial.to_csv(output_path, index=False)

    print(f"\n✅ Φ spatial distribution saved: {output_path}")
    print(f"   Total bins: {len(phi_spatial)}")
    print(f"   Φ range: [{phi_spatial['Phi'].min():.3f}, {phi_spatial['Phi'].max():.3f}]")
    print(f"   Φ mean: {phi_spatial['Phi'].mean():.3f}")

    return 0


if __name__ == "__main__":
    exit(main())
