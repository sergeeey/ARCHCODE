#!/usr/bin/env python3
"""
Dataset Count Verification Script
==================================

Resolves discrepancy between:
- Manuscript: "25,850 variants from 9 loci"
- README: "30,318 ClinVar variants, 9 loci"
- CSV files: 85,383 total rows (with duplicates)

Counts unique VCV IDs across all Unified Atlas CSV files.
"""

import pandas as pd
import glob
from pathlib import Path
from collections import defaultdict


def main():
    print("=" * 70)
    print("ARCHCODE Dataset Count Verification")
    print("=" * 70)

    # Find all Unified Atlas CSV files
    results_dir = Path(__file__).parent.parent / "results"
    atlas_files = list(results_dir.glob("*_Unified_Atlas*.csv"))

    print(f"\nFound {len(atlas_files)} Unified Atlas CSV files:")
    for f in sorted(atlas_files):
        print(f"  - {f.name}")

    # Count unique VCV IDs
    all_vcv_ids = set()
    locus_counts = defaultdict(set)
    file_counts = {}

    for csv_file in atlas_files:
        df = pd.read_csv(csv_file)

        # Find VCV column (various naming conventions)
        vcv_col = None
        for col in df.columns:
            if "ClinVar_ID" in col or "VCV" in col or "Variation_ID" in col or "VariationID" in col:
                vcv_col = col
                break

        if vcv_col is None:
            print(f"  ⚠️  No VCV column in {csv_file.name}, skipping")
            continue

        # Extract VCV IDs
        vcv_ids = set(df[vcv_col].dropna().unique())
        file_counts[csv_file.name] = len(vcv_ids)
        all_vcv_ids.update(vcv_ids)

        # Extract locus from filename
        locus_name = csv_file.name.split("_")[0]
        locus_counts[locus_name].update(vcv_ids)

    print("\n" + "=" * 70)
    print("Results")
    print("=" * 70)

    # Per-file counts
    print("\nPer-file unique VCV counts:")
    for fname, count in sorted(file_counts.items()):
        print(f"  {fname:<50} {count:>6} variants")

    # Per-locus counts
    print("\nPer-locus unique VCV counts:")
    for locus, vcv_set in sorted(locus_counts.items()):
        print(f"  {locus:<15} {len(vcv_set):>6} unique variants")

    # Total unique
    total_unique = len(all_vcv_ids)

    print("\n" + "=" * 70)
    print("DEFINITIVE COUNT")
    print("=" * 70)
    print(f"\nTotal UNIQUE variants across all files: {total_unique:,}")

    # Compare with claims
    manuscript_claim = 25850
    readme_claim = 30318

    print("\n" + "=" * 70)
    print("Comparison with Documentation")
    print("=" * 70)
    print(f"\nManuscript claim (line 19):  {manuscript_claim:>7,}")
    print(f"README claim (line 24):      {readme_claim:>7,}")
    print(f"Actual unique VCV count:     {total_unique:>7,}")

    # Calculate discrepancies
    manuscript_diff = total_unique - manuscript_claim
    readme_diff = total_unique - readme_claim

    print(
        f"\nDiscrepancy from manuscript: {manuscript_diff:>+7,} ({abs(manuscript_diff)/manuscript_claim*100:.1f}%)"
    )
    print(
        f"Discrepancy from README:     {readme_diff:>+7,} ({abs(readme_diff)/readme_claim*100:.1f}%)"
    )

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    if abs(manuscript_diff) < abs(readme_diff):
        print(f"\n✅ Manuscript claim ({manuscript_claim:,}) is CLOSER to actual count")
        print(
            f"   Discrepancy: {abs(manuscript_diff):,} variants ({abs(manuscript_diff)/manuscript_claim*100:.1f}%)"
        )
        print(f"\n❌ README claim ({readme_claim:,}) is FURTHER from actual count")
        print(
            f"   Discrepancy: {abs(readme_diff):,} variants ({abs(readme_diff)/readme_claim*100:.1f}%)"
        )
        print(f"\n📝 ACTION: Update README to {total_unique:,} variants")
    elif abs(readme_diff) < abs(manuscript_diff):
        print(f"\n✅ README claim ({readme_claim:,}) is CLOSER to actual count")
        print(
            f"   Discrepancy: {abs(readme_diff):,} variants ({abs(readme_diff)/readme_claim*100:.1f}%)"
        )
        print(f"\n❌ Manuscript claim ({manuscript_claim:,}) is FURTHER from actual count")
        print(
            f"   Discrepancy: {abs(manuscript_diff):,} variants ({abs(manuscript_diff)/manuscript_claim*100:.1f}%)"
        )
        print(f"\n📝 ACTION: Update manuscript line 19 to {total_unique:,} variants")
    else:
        print(f"\n⚠️  Both claims equally far from actual count")
        print(f"\n📝 ACTION: Update BOTH to {total_unique:,} variants")

    # Check for major loci (9 core loci)
    core_loci = ["HBB", "TP53", "BRCA1", "MLH1", "TERT", "GJB2", "CFTR", "GATA1", "PTEN"]
    print("\n" + "=" * 70)
    print("Core 9 Loci Check")
    print("=" * 70)

    core_total = 0
    missing_loci = []

    for locus in core_loci:
        if locus in locus_counts:
            count = len(locus_counts[locus])
            core_total += count
            print(f"  {locus:<10} {count:>6,} variants")
        else:
            missing_loci.append(locus)
            print(f"  {locus:<10} {'MISSING':>6}")

    print(f"\n  {'CORE TOTAL':<10} {core_total:>6,} variants")

    if missing_loci:
        print(f"\n⚠️  Missing loci: {', '.join(missing_loci)}")

    # Save results
    output_file = results_dir / "dataset_count_verification.txt"
    with open(output_file, "w") as f:
        f.write(f"Total unique variants: {total_unique}\n")
        f.write(f"Manuscript claim: {manuscript_claim}\n")
        f.write(f"README claim: {readme_claim}\n")
        f.write(f"Manuscript discrepancy: {manuscript_diff:+}\n")
        f.write(f"README discrepancy: {readme_diff:+}\n")
        f.write(f"\nPer-locus counts:\n")
        for locus, vcv_set in sorted(locus_counts.items()):
            f.write(f"  {locus}: {len(vcv_set)}\n")

    print(f"\n📊 Results saved to: {output_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
