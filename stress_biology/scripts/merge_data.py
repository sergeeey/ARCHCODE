#!/usr/bin/env python3
"""
Merge mutation rates with doubling times.

Usage:
    python merge_data.py --mutations data/processed/ --doubling data/processed/doubling_times.csv --output data/merged.csv
"""

import argparse
from pathlib import Path
import pandas as pd


def merge_datasets(mutations_dir: Path, doubling_path: Path, output_path: Path) -> None:
    """
    Merge mutation rates from multiple tissue CSVs with doubling times.

    Args:
        mutations_dir: Directory containing {tissue}_mutations.csv files
        doubling_path: Path to doubling_times.csv
        output_path: Where to save merged data
    """
    # Load doubling times
    doubling_df = pd.read_csv(doubling_path)
    print(f"Loaded {len(doubling_df)} tissue doubling times")

    # Find all mutation CSV files
    mutation_files = list(mutations_dir.glob("*_mutations.csv"))
    print(f"Found {len(mutation_files)} mutation files")

    # Collect all mutation data
    all_mutations = []

    for mf in mutation_files:
        # Extract tissue code from filename (e.g., "coad_mutations.csv" -> "COAD")
        tissue_code = mf.stem.replace("_mutations", "").upper()

        # Load mutations
        mut_df = pd.read_csv(mf)

        # Add tissue column
        mut_df["tissue"] = tissue_code

        all_mutations.append(mut_df)

    # Combine all mutations
    combined_mutations = pd.concat(all_mutations, ignore_index=True)
    print(f"  Total samples: {len(combined_mutations)}")

    # Merge with doubling times
    merged = combined_mutations.merge(
        doubling_df[["tissue", "doubling_time_hours"]], on="tissue", how="left"
    )

    # Check for missing doubling times
    missing = merged[merged["doubling_time_hours"].isna()]
    if len(missing) > 0:
        print(f"  WARNING: {len(missing)} samples have no doubling time data")
        print(f"    Tissues: {missing['tissue'].unique()}")

    # Save
    merged.to_csv(output_path, index=False)
    print(f"✓ Saved {len(merged)} samples to {output_path}")

    # Summary stats
    print("\nSummary:")
    summary = (
        merged.groupby("tissue")
        .agg({"mutations_per_mb": ["count", "mean", "std"], "doubling_time_hours": "first"})
        .round(2)
    )
    print(summary)


def main():
    parser = argparse.ArgumentParser(description="Merge mutation rates with doubling times")
    parser.add_argument(
        "--mutations", type=Path, required=True, help="Directory with mutation CSV files"
    )
    parser.add_argument("--doubling", type=Path, required=True, help="Doubling times CSV")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")

    args = parser.parse_args()

    merge_datasets(args.mutations, args.doubling, args.output)


if __name__ == "__main__":
    main()
