#!/usr/bin/env python3
"""
H4: Compute Codeword Distance (Error-Correcting Code Hypothesis)
=================================================================
Codeword distance = minimum LSSIM disruption required to perturb function

Hypothesis: Dosage-sensitive loci (HBB, TP53) have higher "error correction"
            → require larger perturbations to cross LSSIM threshold

Metrics per locus:
  - Minimum LSSIM (most disruptive variant)
  - 10th percentile LSSIM (robustness to outliers)
  - Fraction variants < 0.95 threshold (sensitivity)

Output: results/codeword_distances.csv

Usage:
    python scripts/compute_codeword_distance.py --loci HBB,TP53,BRCA1
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_atlas(locus: str) -> pd.DataFrame:
    """Load unified atlas for locus"""
    atlas_paths = {
        "HBB": RESULTS_DIR / "HBB_Unified_Atlas.csv",
        "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
        "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    }

    atlas_path = atlas_paths.get(locus)
    if not atlas_path or not atlas_path.exists():
        raise FileNotFoundError(f"Atlas not found for {locus}: {atlas_path}")

    df = pd.read_csv(atlas_path)
    return df


def compute_codeword_metrics(atlas: pd.DataFrame, locus: str) -> dict:
    """
    Compute codeword distance metrics

    Codeword distance = how hard to disrupt function
    - Lower minimum LSSIM = easier to disrupt = lower error correction
    - Higher minimum LSSIM = harder to disrupt = higher error correction
    """

    if "ARCHCODE_LSSIM" not in atlas.columns:
        return {
            "locus": locus,
            "error": "No ARCHCODE_LSSIM column",
        }

    lssim = atlas["ARCHCODE_LSSIM"].dropna()

    if len(lssim) == 0:
        return {
            "locus": locus,
            "error": "No LSSIM data",
        }

    # Codeword distance metrics
    metrics = {
        "locus": locus,
        "n_variants": len(lssim),
        "min_lssim": lssim.min(),
        "p10_lssim": lssim.quantile(0.10),
        "p25_lssim": lssim.quantile(0.25),
        "median_lssim": lssim.median(),
        "mean_lssim": lssim.mean(),
        "p75_lssim": lssim.quantile(0.75),
        "p90_lssim": lssim.quantile(0.90),
        "max_lssim": lssim.max(),
        "frac_below_095": (lssim < 0.95).sum() / len(lssim),
        "frac_below_090": (lssim < 0.90).sum() / len(lssim),
    }

    # Codeword distance = 1 - min_lssim (larger = more robust)
    metrics["codeword_distance"] = 1 - metrics["min_lssim"]

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Compute codeword distance")
    parser.add_argument(
        "--loci",
        default="HBB,TP53,BRCA1",
        help="Comma-separated list of loci",
    )
    args = parser.parse_args()

    loci = [l.strip() for l in args.loci.split(",")]

    print("=" * 70)
    print("H4: CODEWORD DISTANCE COMPUTATION")
    print("=" * 70)
    print(f"\nAnalyzing {len(loci)} loci: {', '.join(loci)}\n")

    results = []

    for locus in loci:
        print(f"Processing {locus}...")
        try:
            atlas = load_atlas(locus)
            metrics = compute_codeword_metrics(atlas, locus)
            results.append(metrics)

            if "error" not in metrics:
                print(f"  ✅ {metrics['n_variants']} variants")
                print(f"     Min LSSIM: {metrics['min_lssim']:.4f}")
                print(f"     P10 LSSIM: {metrics['p10_lssim']:.4f}")
                print(f"     Codeword distance: {metrics['codeword_distance']:.4f}")
                print(f"     Sensitive variants (<0.95): {metrics['frac_below_095']*100:.1f}%")
            else:
                print(f"  ❌ {metrics['error']}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({"locus": locus, "error": str(e)})

        print()

    # Create DataFrame
    df = pd.DataFrame(results)

    # Summary table
    print("=" * 70)
    print("CODEWORD DISTANCE SUMMARY")
    print("=" * 70)
    print()

    valid_df = df[df["error"].isna()] if "error" in df.columns else df

    if len(valid_df) > 0:
        print(
            valid_df[
                [
                    "locus",
                    "n_variants",
                    "min_lssim",
                    "p10_lssim",
                    "median_lssim",
                    "codeword_distance",
                    "frac_below_095",
                ]
            ].to_string(index=False)
        )

        # Dosage-sensitivity hypothesis test
        print("\n" + "=" * 70)
        print("DOSAGE-SENSITIVITY HYPOTHESIS TEST")
        print("=" * 70)

        print("\n🧬 Expected ranking (dosage-sensitive → dosage-tolerant):")
        print("   Higher codeword distance = more robust = harder to disrupt")
        print("   HBB (dosage-sensitive) > TP53 (tumor suppressor) > BRCA1 (large gene)")

        if len(valid_df) >= 2:
            sorted_df = valid_df.sort_values("codeword_distance", ascending=False)

            print(f"\n📊 Actual ranking by codeword distance:")
            for idx, (i, row) in enumerate(sorted_df.iterrows(), 1):
                print(f"   {idx}. {row['locus']}: {row['codeword_distance']:.4f}")

            # Simple hypothesis test
            if "HBB" in valid_df["locus"].values and "BRCA1" in valid_df["locus"].values:
                hbb_cd = valid_df[valid_df["locus"] == "HBB"]["codeword_distance"].iloc[0]
                brca1_cd = valid_df[valid_df["locus"] == "BRCA1"]["codeword_distance"].iloc[0]

                print(f"\n🎯 HBB vs BRCA1:")
                print(f"   HBB codeword distance: {hbb_cd:.4f}")
                print(f"   BRCA1 codeword distance: {brca1_cd:.4f}")
                print(f"   Ratio (HBB/BRCA1): {hbb_cd/brca1_cd if brca1_cd > 0 else 'N/A':.2f}×")

                if hbb_cd > brca1_cd:
                    print(f"   ✅ HBB > BRCA1 (hypothesis supported)")
                else:
                    print(f"   ❌ HBB ≤ BRCA1 (hypothesis NOT supported)")

    # Save results
    output_path = RESULTS_DIR / "codeword_distances.csv"
    df.to_csv(output_path, index=False)

    print(f"\n📄 Results saved: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
