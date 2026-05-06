"""
DepMap Real Data Analysis — Λ-index vs CRISPR Dependency
Week 1, Day 2

Hypothesis: High Λ-index → high dependency on helicase genes (synthetic lethality)

Pipeline:
1. Load expression → calculate Λ-index
2. Load CRISPR → extract WRN/BLM/BRIP1/DHX36/PIF1/RTEL1 dependency
3. Test: Λ predicts helicase dependency (AUC, Spearman)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import spearmanr
import matplotlib.pyplot as plt
import re

# Configuration
DATA_DIR = Path("../data/depmap")
OUTPUT_DIR = Path("../results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Core G4 helicases (specific)
G4_HELICASES = ["WRN", "BLM", "BRIP1", "DHX36", "PIF1", "RTEL1"]
HR_GENES = ["RAD51", "BRCA1", "BRCA2", "PALB2"]
CONTROL_GENES = ["MYC", "EGFR", "TP53"]

CLEARANCE_GENES = G4_HELICASES + HR_GENES


def load_expression() -> pd.DataFrame:
    """Load DepMap expression data."""
    print("[EXPRESSION] Loading...")
    expr_file = DATA_DIR / "OmicsExpressionTPMLogp1HumanProteinCodingGenes.csv"

    # Read full file
    df = pd.read_csv(expr_file)

    print(f"  Shape: {df.shape}")

    # Extract cell line ID (use ModelID as index)
    df = df.set_index("ModelID")

    # Filter to target genes
    target_cols = []
    gene_map = {}

    for gene in CLEARANCE_GENES + CONTROL_GENES:
        matches = [c for c in df.columns if re.match(f"{gene} \(", c)]
        if matches:
            target_cols.append(matches[0])
            gene_map[matches[0]] = gene

    df_filtered = df[target_cols]

    # Rename columns to gene symbols
    df_filtered = df_filtered.rename(columns=gene_map)

    print(f"  Filtered: {df_filtered.shape[0]} cell lines × {df_filtered.shape[1]} genes")
    print(f"  Genes: {', '.join(df_filtered.columns)}")

    return df_filtered


def load_crispr() -> pd.DataFrame:
    """Load CRISPR gene effect data (Chronos scores)."""
    print("\n[CRISPR] Loading...")
    crispr_file = DATA_DIR / "CRISPRGeneEffect.csv"

    df = pd.read_csv(crispr_file)

    print(f"  Shape: {df.shape}")

    # Cell line ID
    df = df.rename(columns={"Unnamed: 0": "ModelID"})
    df = df.set_index("ModelID")

    # Filter to helicase genes
    target_cols = []
    gene_map = {}

    for gene in G4_HELICASES:
        matches = [c for c in df.columns if re.match(f"{gene} \(", c)]
        if matches:
            target_cols.append(matches[0])
            gene_map[matches[0]] = gene

    df_filtered = df[target_cols]
    df_filtered = df_filtered.rename(columns=gene_map)

    print(f"  Filtered: {df_filtered.shape[0]} cell lines × {df_filtered.shape[1]} genes")
    print(f"  Genes: {', '.join(df_filtered.columns)}")
    print(f"  Gene effect range: {df_filtered.min().min():.2f} to {df_filtered.max().max():.2f}")
    print(f"  (Negative = essential, Positive = non-essential)")

    return df_filtered


def calculate_lambda(expr_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Λ-index."""
    print("\n[Λ-INDEX] Calculating...")

    # G4 load proxy: MYC + EGFR expression (high transcription = high G4 load)
    if "MYC" in expr_df.columns and "EGFR" in expr_df.columns:
        g4_load = expr_df["MYC"] * 10 + expr_df["EGFR"] * 5 + 100
    else:
        # Fallback: constant
        g4_load = pd.Series(100.0, index=expr_df.index)
        print("  Warning: Using constant G4 load (MYC/EGFR missing)")

    # Helicase capacity
    clearance_genes = [g for g in CLEARANCE_GENES if g in expr_df.columns]
    helicase_capacity = expr_df[clearance_genes].sum(axis=1)

    # Λ = load / capacity
    lambda_index = g4_load / (helicase_capacity + 1e-6)  # Avoid division by zero

    print(f"  Range: {lambda_index.min():.3f} - {lambda_index.max():.3f}")
    print(f"  Mean: {lambda_index.mean():.3f}, Median: {lambda_index.median():.3f}")

    # Combine into DataFrame
    results = pd.DataFrame(
        {
            "lambda_index": lambda_index,
            "g4_load": g4_load,
            "helicase_capacity": helicase_capacity,
        }
    )

    # Add individual gene expression
    for gene in clearance_genes:
        results[f"{gene}_expr"] = expr_df[gene]

    return results


def merge_data(lambda_df: pd.DataFrame, crispr_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Λ-index with CRISPR dependency."""
    print("\n[MERGE] Combining data...")

    # Inner join on ModelID (cell line)
    merged = lambda_df.join(crispr_df, how="inner", rsuffix="_crispr")

    print(f"  Common cell lines: {len(merged)}")

    # Add mean helicase dependency
    helicase_cols = [c for c in merged.columns if c in G4_HELICASES]
    merged["mean_helicase_dependency"] = merged[helicase_cols].mean(axis=1)

    return merged


def test_hypothesis(merged_df: pd.DataFrame):
    """
    Test: High Λ → high helicase dependency (negative gene effect).

    CRISPR gene effect:
    - Negative = gene is essential (knockout kills cell)
    - More negative = more essential

    Hypothesis: High Λ → more negative helicase dependency
    """
    print("\n" + "=" * 60)
    print("HYPOTHESIS TEST")
    print("=" * 60)

    lambda_index = merged_df["lambda_index"].values
    helicase_dep = merged_df["mean_helicase_dependency"].values

    # Spearman correlation (expect negative: high Λ → more negative dependency)
    rho, pval = spearmanr(lambda_index, helicase_dep)

    print(f"\nSpearman correlation:")
    print(f"  ρ(Λ, helicase_dependency) = {rho:.3f} (p={pval:.2e})")

    if rho < -0.2:
        print(f"  ✓ Negative correlation (as expected)")
    else:
        print(f"  ✗ Weak/positive correlation (unexpected)")

    # Per-gene correlations
    print(f"\nPer-gene dependency:")
    for gene in G4_HELICASES:
        if gene in merged_df.columns:
            rho_gene, p_gene = spearmanr(lambda_index, merged_df[gene])
            sig = (
                "***" if p_gene < 0.001 else "**" if p_gene < 0.01 else "*" if p_gene < 0.05 else ""
            )
            print(f"  {gene:10s}: ρ={rho_gene:6.3f}, p={p_gene:.2e} {sig}")

    # AUC test: Can Λ predict essential vs non-essential?
    # Split by median dependency
    median_dep = helicase_dep.mean()
    essential = (helicase_dep < median_dep).astype(int)  # More negative = essential

    try:
        auc = roc_auc_score(essential, lambda_index)
        print(f"\nAUC (Λ predicts essentiality):")
        print(f"  AUC = {auc:.3f}")

        if auc > 0.65:
            print(f"  ✓ PASS (above threshold)")
        else:
            print(f"  ✗ WEAK (below 0.65)")
    except Exception as e:
        print(f"\n  AUC calculation failed: {e}")

    # Quartile analysis
    print(f"\n" + "=" * 60)
    print("QUARTILE ANALYSIS")
    print("=" * 60)

    merged_df["lambda_quartile"] = pd.qcut(
        merged_df["lambda_index"], q=4, labels=["Q1", "Q2", "Q3", "Q4"]
    )

    quartile_summary = merged_df.groupby("lambda_quartile").agg(
        {
            "lambda_index": ["mean", "std"],
            "mean_helicase_dependency": ["mean", "std"],
        }
    )

    print(quartile_summary)

    # Q4 vs Q1 effect size
    q1_dep = merged_df[merged_df["lambda_quartile"] == "Q1"]["mean_helicase_dependency"].mean()
    q4_dep = merged_df[merged_df["lambda_quartile"] == "Q4"]["mean_helicase_dependency"].mean()

    print(f"\nQ4 vs Q1:")
    print(f"  Q1 (low Λ) dependency: {q1_dep:.3f}")
    print(f"  Q4 (high Λ) dependency: {q4_dep:.3f}")
    print(f"  Difference: {q4_dep - q1_dep:.3f}")

    if q4_dep < q1_dep - 0.1:
        print(f"  ✓ Q4 more dependent (more negative)")
    else:
        print(f"  ✗ No clear difference")


def plot_results(merged_df: pd.DataFrame):
    """Plot Λ vs helicase dependency."""
    print("\n[PLOT] Generating figures...")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Λ vs mean helicase dependency
    ax = axes[0]
    ax.scatter(
        merged_df["lambda_index"],
        merged_df["mean_helicase_dependency"],
        alpha=0.5,
        s=10,
    )
    ax.set_xlabel("Λ-index (G4 load / helicase capacity)")
    ax.set_ylabel("Mean helicase dependency (CRISPR)")
    ax.set_title("Λ-index vs Helicase Dependency")
    ax.grid(alpha=0.3)

    # Add correlation
    rho, pval = spearmanr(merged_df["lambda_index"], merged_df["mean_helicase_dependency"])
    ax.text(
        0.05,
        0.95,
        f"ρ = {rho:.3f}\np = {pval:.2e}",
        transform=ax.transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    # Plot 2: Quartile boxplot
    ax = axes[1]
    quartile_data = [
        merged_df[merged_df["lambda_quartile"] == q]["mean_helicase_dependency"]
        for q in ["Q1", "Q2", "Q3", "Q4"]
    ]
    ax.boxplot(quartile_data, labels=["Q1", "Q2", "Q3", "Q4"])
    ax.set_xlabel("Λ-index Quartile")
    ax.set_ylabel("Mean helicase dependency")
    ax.set_title("Helicase Dependency by Λ Quartile")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    output_file = OUTPUT_DIR / "lambda_crispr_real_data.png"
    plt.savefig(output_file, dpi=150)
    print(f"  Saved: {output_file}")


def main():
    """Main execution."""
    print("=" * 60)
    print("DepMap Real Data — Λ-index vs CRISPR Dependency")
    print("=" * 60)
    print()

    # Load data
    expr_df = load_expression()
    crispr_df = load_crispr()

    # Calculate Λ-index
    lambda_df = calculate_lambda(expr_df)

    # Merge
    merged_df = merge_data(lambda_df, crispr_df)

    # Save merged data
    output_file = OUTPUT_DIR / "lambda_crispr_merged.csv"
    merged_df.to_csv(output_file)
    print(f"\n[SAVE] Merged data: {output_file}")

    # Test hypothesis
    test_hypothesis(merged_df)

    # Plot
    plot_results(merged_df)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
