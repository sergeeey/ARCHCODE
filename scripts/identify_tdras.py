#!/usr/bin/env python3
"""
H3: Identify TDRA (Topology-Dependent Regulatory Allele) Candidates
====================================================================
TDRA = variants showing structural disruption (LSSIM<0.95) but MPRA-null
        (require endogenous 3D context to show effect)

Criteria:
  - LSSIM < 0.95 (structural disruption in ARCHCODE)
  - MPRA effect size < 0.2 (MPRA-null, no function in plasmid context)
  - ClinVar pathogenic (expected to have function)

Output: results/tdra_candidates.csv

Usage:
    python scripts/identify_tdras.py --locus HBB
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"


def load_lssim_results(locus: str) -> pd.DataFrame:
    """Load LSSIM results from unified atlas"""
    atlas_paths = {
        "HBB": RESULTS_DIR / "HBB_Unified_Atlas.csv",
        "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
        "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    }

    atlas_path = atlas_paths.get(locus)
    if not atlas_path or not atlas_path.exists():
        raise FileNotFoundError(f"Atlas not found for {locus}: {atlas_path}")

    df = pd.read_csv(atlas_path)
    print(f"✅ Loaded {locus} atlas: {len(df)} variants")

    return df


def load_mpra_results(locus: str) -> pd.DataFrame:
    """Load MPRA experimental results"""
    mpra_files = {
        "HBB": DATA_DIR / "mpra_kircher_hbb_raw.csv",
    }

    mpra_path = mpra_files.get(locus)
    if not mpra_path or not mpra_path.exists():
        print(f"⚠️  No MPRA data for {locus}, skipping MPRA filter")
        return None

    df = pd.read_csv(mpra_path)
    print(f"✅ Loaded MPRA results: {len(df)} variants")

    return df


def identify_tdra_candidates(
    atlas: pd.DataFrame,
    mpra: pd.DataFrame = None,
    lssim_threshold: float = 0.95,
    mpra_threshold: float = 0.2,
) -> pd.DataFrame:
    """
    Identify TDRA candidates

    TDRA = LSSIM<0.95 (structure disrupted) + MPRA-null (no plasmid effect)
           + Pathogenic (expected function)
    """

    # Filter 1: Structural disruption (LSSIM < threshold)
    if "LSSIM" in atlas.columns:
        structural = atlas[atlas["LSSIM"] < lssim_threshold].copy()
    else:
        print("⚠️  No LSSIM column, using all variants")
        structural = atlas.copy()

    print(f"\n📊 Filter 1 — Structural disruption (LSSIM<{lssim_threshold}):")
    print(f"   {len(structural)}/{len(atlas)} variants ({len(structural)*100/len(atlas):.1f}%)")

    # Filter 2: MPRA-null (if MPRA data available)
    if mpra is not None:
        # Merge MPRA data
        structural = structural.merge(
            mpra[["ClinVar_ID", "effect_size"]],
            on="ClinVar_ID",
            how="left",
        )

        mpra_null = structural[
            (structural["effect_size"].notna()) & (structural["effect_size"].abs() < mpra_threshold)
        ]

        print(f"\n📊 Filter 2 — MPRA-null (|effect|<{mpra_threshold}):")
        print(f"   {len(mpra_null)}/{len(structural)} variants with MPRA data")
        print(f"   {len(mpra_null)} MPRA-null candidates")

        candidates = mpra_null
    else:
        # No MPRA data, use structural disruption only
        candidates = structural
        print(f"\n📊 Filter 2 — MPRA data not available, using structural filter only")

    # Filter 3: Pathogenic (expected to have function)
    if "Label" in candidates.columns:
        pathogenic_tdras = candidates[candidates["Label"] == "Pathogenic"]

        print(f"\n📊 Filter 3 — Pathogenic:")
        print(f"   {len(pathogenic_tdras)}/{len(candidates)} variants")

        candidates = pathogenic_tdras

    # Add TDRA flag
    candidates["TDRA_candidate"] = True

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Identify TDRA candidates")
    parser.add_argument("--locus", default="HBB", help="Locus to analyze")
    parser.add_argument(
        "--lssim-threshold",
        type=float,
        default=0.95,
        help="LSSIM threshold for structural disruption",
    )
    parser.add_argument(
        "--mpra-threshold",
        type=float,
        default=0.2,
        help="MPRA effect size threshold for null",
    )
    args = parser.parse_args()

    print("=" * 70)
    print(f"H3: TDRA CANDIDATE IDENTIFICATION — {args.locus}")
    print("=" * 70)

    # Load data
    atlas = load_lssim_results(args.locus)
    mpra = load_mpra_results(args.locus)

    # Identify TDRA candidates
    tdra_candidates = identify_tdra_candidates(
        atlas,
        mpra,
        lssim_threshold=args.lssim_threshold,
        mpra_threshold=args.mpra_threshold,
    )

    # Summary statistics
    print("\n" + "=" * 70)
    print("TDRA CANDIDATE SUMMARY")
    print("=" * 70)

    print(f"\n✅ Total TDRA candidates: {len(tdra_candidates)}")

    if len(tdra_candidates) > 0:
        print(f"\n📊 LSSIM statistics:")
        print(f"   Mean: {tdra_candidates['LSSIM'].mean():.4f}")
        print(f"   Median: {tdra_candidates['LSSIM'].median():.4f}")
        print(
            f"   Range: [{tdra_candidates['LSSIM'].min():.4f}, {tdra_candidates['LSSIM'].max():.4f}]"
        )

        if "effect_size" in tdra_candidates.columns:
            mpra_present = tdra_candidates[tdra_candidates["effect_size"].notna()]
            if len(mpra_present) > 0:
                print(f"\n📊 MPRA effect size (n={len(mpra_present)}):")
                print(f"   Mean: {mpra_present['effect_size'].mean():.4f}")
                print(f"   Median: {mpra_present['effect_size'].median():.4f}")
                print(
                    f"   Range: [{mpra_present['effect_size'].min():.4f}, {mpra_present['effect_size'].max():.4f}]"
                )

        # Top candidates
        print(f"\n🎯 Top 10 TDRA candidates (lowest LSSIM):")
        top_candidates = tdra_candidates.nsmallest(10, "LSSIM")

        for idx, row in top_candidates.iterrows():
            mpra_str = ""
            if "effect_size" in row and pd.notna(row["effect_size"]):
                mpra_str = f", MPRA={row['effect_size']:.3f}"

            print(
                f"   {row['ClinVar_ID']}: LSSIM={row['LSSIM']:.4f}{mpra_str} ({row.get('Category', 'N/A')})"
            )

        # Save results
        output_path = RESULTS_DIR / f"tdra_candidates_{args.locus}.csv"
        tdra_candidates.to_csv(output_path, index=False)

        print(f"\n📄 TDRA candidates saved: {output_path}")

    else:
        print("\n⚠️  No TDRA candidates found with current criteria")
        print(f"   Try relaxing thresholds:")
        print(f"     --lssim-threshold 0.98 (current: {args.lssim_threshold})")
        print(f"     --mpra-threshold 0.3 (current: {args.mpra_threshold})")

    return 0


if __name__ == "__main__":
    exit(main())
