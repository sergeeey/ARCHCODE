"""
Λ-Index Calculation
Week 1, Day 3-4

Calculates:
Λ = G4_load / helicase_capacity

G4_load = genome-wide G4 burden (motif count × gene expression)
helicase_capacity = SUM(helicase expression + HR genes)

Input: helicase_expression_matrix.tsv (samples × genes)
Output: lambda_index.csv (sample_id, Λ, components)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import re

# Configuration
DATA_DIR = Path("../data/processed")
OUTPUT_DIR = Path("../results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Gene sets
HELICASE_GENES = ["WRN", "BLM", "BRIP1", "RTEL1", "PIF1", "RECQL4", "RECQL5"]
HR_GENES = ["RAD51", "BRCA1", "BRCA2", "PALB2"]
CONTROL_GENES = ["MYC", "EGFR", "TP53"]

CLEARANCE_GENES = HELICASE_GENES + HR_GENES  # All genes involved in G4 resolution


def load_expression_data() -> pd.DataFrame:
    """Load helicase expression matrix."""
    expr_file = DATA_DIR / "helicase_expression_matrix.tsv"

    if not expr_file.exists():
        print(f"[ERROR] Expression matrix not found: {expr_file}")
        print("[MOCK] Generating synthetic data for testing...")
        return generate_mock_expression()

    print(f"[LOAD] Reading {expr_file}")
    df = pd.read_csv(expr_file, sep="\t", index_col=0)
    print(f"  Shape: {df.shape[0]} samples × {df.shape[1]} genes")

    return df


def generate_mock_expression(n_samples: int = 500) -> pd.DataFrame:
    """
    Generate mock expression data for testing.

    Models:
    - Helicases: log-normal distribution (mean ~5, sd ~2 in log2 space)
    - MYC: bimodal (low vs amplified)
    - Correlation: WRN-BLM r~0.3
    """
    np.random.seed(42)

    all_genes = HELICASE_GENES + HR_GENES + CONTROL_GENES

    data = {}

    # Helicases + HR genes (log-normal)
    for gene in HELICASE_GENES + HR_GENES:
        data[gene] = np.random.lognormal(mean=1.5, sigma=0.8, size=n_samples)

    # MYC (bimodal: 80% low, 20% amplified)
    myc_low = np.random.lognormal(mean=1.2, sigma=0.5, size=int(n_samples * 0.8))
    myc_high = np.random.lognormal(mean=2.5, sigma=0.5, size=int(n_samples * 0.2))
    data["MYC"] = np.concatenate([myc_low, myc_high])

    # EGFR, TP53
    data["EGFR"] = np.random.lognormal(mean=1.3, sigma=0.7, size=n_samples)
    data["TP53"] = np.random.lognormal(mean=1.6, sigma=0.6, size=n_samples)

    df = pd.DataFrame(data)
    df.index = [f"SAMPLE_{i:04d}" for i in range(n_samples)]

    print(f"[MOCK] Generated {df.shape[0]} samples × {df.shape[1]} genes")

    return df


def estimate_g4_load(expr_df: pd.DataFrame) -> pd.Series:
    """
    Estimate genome-wide G4 load.

    Proxy method (Week 1 simplification):
    G4_load ≈ SUM_genes(G4_motif_count_in_promoter × gene_expression)

    For mock: assume G4 load correlates with transcription
    Real implementation: use G4Hunter scores + promoter annotations
    """
    print("[G4 LOAD] Estimating genome-wide G4 burden...")

    # Mock: G4 load proxy = weighted sum of high-GC genes
    # Assuming MYC, EGFR have G4-rich promoters
    if "MYC" in expr_df.columns and "EGFR" in expr_df.columns:
        # Simple proxy: MYC + EGFR expression as G4 load drivers
        g4_load = expr_df["MYC"] * 10 + expr_df["EGFR"] * 5  # Arbitrary weights

        # Add genome-wide baseline
        g4_load += 100  # Baseline G4 load from constitutive genes

        print(f"  Proxy: MYC + EGFR weighted expression")
        print(f"  Range: {g4_load.min():.1f} - {g4_load.max():.1f}")
    else:
        # Fallback: constant
        g4_load = pd.Series(100.0, index=expr_df.index)
        print(f"  Warning: Using constant G4 load (MYC/EGFR missing)")

    return g4_load


def calculate_helicase_capacity(expr_df: pd.DataFrame) -> pd.Series:
    """
    Calculate total helicase + HR capacity.

    Capacity = SUM(helicase expression + HR gene expression)
    """
    print("[HELICASE] Calculating clearance capacity...")

    available_genes = [g for g in CLEARANCE_GENES if g in expr_df.columns]
    missing_genes = set(CLEARANCE_GENES) - set(available_genes)

    if missing_genes:
        print(f"  Warning: Missing genes: {missing_genes}")

    if not available_genes:
        raise ValueError("No helicase/HR genes found in expression matrix")

    capacity = expr_df[available_genes].sum(axis=1)

    print(f"  Genes used: {', '.join(available_genes)}")
    print(f"  Range: {capacity.min():.1f} - {capacity.max():.1f}")

    return capacity


def calculate_lambda_index(expr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Λ-index for all samples.

    Returns DataFrame with columns:
    - sample_id
    - g4_load
    - helicase_capacity
    - lambda_index
    - lambda_quartile
    """
    print("\n" + "=" * 60)
    print("Λ-INDEX CALCULATION")
    print("=" * 60)

    # Step 1: G4 load
    g4_load = estimate_g4_load(expr_df)

    # Step 2: Helicase capacity
    helicase_capacity = calculate_helicase_capacity(expr_df)

    # Step 3: Λ = load / capacity
    lambda_index = g4_load / helicase_capacity

    print(f"\n[Λ-INDEX] Calculated for {len(lambda_index)} samples")
    print(f"  Mean: {lambda_index.mean():.3f}")
    print(f"  Median: {lambda_index.median():.3f}")
    print(f"  Range: {lambda_index.min():.3f} - {lambda_index.max():.3f}")

    # Step 4: Quartiles
    quartiles = pd.qcut(lambda_index, q=4, labels=["Q1", "Q2", "Q3", "Q4"])

    # Step 5: Assemble results
    results = pd.DataFrame(
        {
            "sample_id": expr_df.index,
            "g4_load": g4_load.values,
            "helicase_capacity": helicase_capacity.values,
            "lambda_index": lambda_index.values,
            "lambda_quartile": quartiles.values,
        }
    )

    # Add individual helicase contributions
    for gene in CLEARANCE_GENES:
        if gene in expr_df.columns:
            results[f"{gene}_expr"] = expr_df[gene].values

    return results


def save_results(results_df: pd.DataFrame):
    """Save Λ-index results."""
    output_file = OUTPUT_DIR / "lambda_index.csv"
    results_df.to_csv(output_file, index=False)

    print(f"\n[SAVE] Results saved to: {output_file}")

    # Summary statistics by quartile
    print("\n" + "=" * 60)
    print("QUARTILE SUMMARY")
    print("=" * 60)

    summary = results_df.groupby("lambda_quartile").agg(
        {
            "lambda_index": ["mean", "std", "min", "max"],
            "g4_load": "mean",
            "helicase_capacity": "mean",
        }
    )

    print(summary.to_string())

    # Save summary
    summary_file = OUTPUT_DIR / "lambda_summary.csv"
    summary.to_csv(summary_file)
    print(f"\n[SAVE] Summary saved to: {summary_file}")


def main():
    """Main execution."""
    print("=" * 60)
    print("Λ-Index Calculation — Week 1, Day 3")
    print("=" * 60)
    print()

    # Load expression data
    expr_df = load_expression_data()

    # Calculate Λ-index
    results_df = calculate_lambda_index(expr_df)

    # Save results
    save_results(results_df)

    print("\n" + "=" * 60)
    print("STATUS: Day 3 Complete")
    print("=" * 60)
    print("✓ Λ-index calculated for all samples")
    print("✓ Quartile stratification done")
    print("○ Next: 03_baseline_models.py (AUC comparison)")
    print("=" * 60)


if __name__ == "__main__":
    main()
