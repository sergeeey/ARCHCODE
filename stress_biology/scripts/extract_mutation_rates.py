#!/usr/bin/env python3
"""
Extract mutation rates from TCGA MAF files.

Parses MAF (Mutation Annotation Format) and calculates mutations per megabase.

Usage:
    python extract_mutation_rates.py --maf data/raw/COAD.maf --output data/processed/mutation_rates.csv

Author: Sergey Boyko
Created: 2026-04-25
"""

import argparse
from pathlib import Path
import pandas as pd


def parse_maf(maf_path: Path) -> pd.DataFrame:
    """
    Parse TCGA MAF file and extract mutation counts per sample.

    Args:
        maf_path: Path to MAF file

    Returns:
        DataFrame with columns: sample_id, n_mutations
    """
    print(f"  Reading MAF file: {maf_path.name}")

    # MAF files may be gzipped
    if maf_path.suffix == ".gz":
        import gzip

        opener = gzip.open
    else:
        opener = open

    # Skip comment lines (start with #)
    with opener(maf_path, "rt") as f:
        lines = [line for line in f if not line.startswith("#")]

    # Parse as TSV
    from io import StringIO

    maf_df = pd.read_csv(StringIO("".join(lines)), sep="\t", low_memory=False)

    print(f"  Loaded {len(maf_df):,} mutations")

    # Filter to somatic mutations only (exclude Silent)
    if "Variant_Classification" in maf_df.columns:
        before = len(maf_df)
        maf_df = maf_df[maf_df["Variant_Classification"] != "Silent"]
        print(f"  Filtered out {before - len(maf_df):,} silent mutations")

    # Count mutations per sample
    sample_col = "Tumor_Sample_Barcode"
    if sample_col not in maf_df.columns:
        # Try alternative column names
        alt_cols = [c for c in maf_df.columns if "sample" in c.lower() or "barcode" in c.lower()]
        if alt_cols:
            sample_col = alt_cols[0]
            print(f"  Using sample column: {sample_col}")
        else:
            raise ValueError(
                f"Cannot find sample ID column in MAF. Columns: {list(maf_df.columns)}"
            )

    mutation_counts = maf_df[sample_col].value_counts().reset_index()
    mutation_counts.columns = ["sample_id", "n_mutations"]

    print(f"  Found {len(mutation_counts)} unique samples")

    return mutation_counts


def calculate_mutation_rate(maf_df: pd.DataFrame, coverage_mb: float = 30.0) -> pd.DataFrame:
    """
    Calculate mutations per megabase.

    Args:
        maf_df: Parsed MAF data (with columns: sample_id, n_mutations)
        coverage_mb: Sequencing coverage in megabases (default: 30 Mb for exome)

    Returns:
        DataFrame with columns: sample_id, mutations_per_mb
    """
    print(f"  Calculating mutation rates (coverage: {coverage_mb} Mb)...")

    maf_df["mutations_per_mb"] = maf_df["n_mutations"] / coverage_mb

    print(f"  Mean: {maf_df['mutations_per_mb'].mean():.2f} mut/Mb")
    print(f"  Median: {maf_df['mutations_per_mb'].median():.2f} mut/Mb")
    print(
        f"  Range: {maf_df['mutations_per_mb'].min():.2f} - {maf_df['mutations_per_mb'].max():.2f}"
    )

    return maf_df[["sample_id", "mutations_per_mb"]]


def main():
    parser = argparse.ArgumentParser(description="Extract mutation rates from MAF")
    parser.add_argument("--maf", type=Path, required=True, help="Input MAF file")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")

    args = parser.parse_args()

    print(f"Parsing MAF file: {args.maf}...")
    maf_df = parse_maf(args.maf)

    print("Calculating mutation rates...")
    rates_df = calculate_mutation_rate(maf_df)

    rates_df.to_csv(args.output, index=False)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
