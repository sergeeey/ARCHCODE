#!/usr/bin/env python3
"""
Calculate ATP proxy from RNA-seq data (TCGA).

ATP Proxy = mean expression of OXPHOS genes + mitochondrial markers.

Usage:
    python atp_proxy.py --rnaseq data/tcga_rnaseq.csv --output data/processed/atp_proxy.csv

Author: Sergey Boyko
Created: 2026-04-25
"""

import argparse
from pathlib import Path

import pandas as pd
import numpy as np


# OXPHOS genes (from SPEC.md)
OXPHOS_GENES = [
    # Complex I (NADH dehydrogenase)
    "NDUFB1",
    "NDUFB2",
    "NDUFB3",
    # Complex IV (Cytochrome c oxidase)
    "COX1",
    "COX2",
    "COX3",
    "COX4I1",
    "COX5A",
    "COX6A1",
    "COX7A1",
    "COX8A",
    # Complex V (ATP synthase)
    "ATP5F1A",
    "ATP5F1B",
    "ATP5F1C",
    "ATP5F1D",
    "ATP5F1E",
]

# Mitochondrial stress markers (from SPEC.md v2.0)
MITO_STRESS_GENES = [
    "PINK1",  # Mitophagy initiator
    "PARKIN",  # E3 ubiquitin ligase (mitophagy)
    "LONP1",  # Mitochondrial protease (stress response)
]

# Glycolysis markers (shift to glycolysis = mitochondrial stress)
GLYCOLYSIS_GENES = [
    "HK2",  # Hexokinase 2 (Warburg effect)
    "PKM2",  # Pyruvate kinase M2
    "LDHA",  # Lactate dehydrogenase A
]


def calculate_atp_proxy(rnaseq_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ATP proxy from RNA-seq expression data.

    Args:
        rnaseq_df: RNA-seq data with samples as rows, genes as columns

    Returns:
        DataFrame with columns: sample_id, atp_proxy, oxphos_score, mito_stress_score
    """
    print(f"Calculating ATP proxy for {len(rnaseq_df)} samples...")

    # Check which genes are available
    available_oxphos = [g for g in OXPHOS_GENES if g in rnaseq_df.columns]
    available_stress = [g for g in MITO_STRESS_GENES if g in rnaseq_df.columns]
    available_glyco = [g for g in GLYCOLYSIS_GENES if g in rnaseq_df.columns]

    print(f"  OXPHOS genes available: {len(available_oxphos)}/{len(OXPHOS_GENES)}")
    print(f"  Stress genes available: {len(available_stress)}/{len(MITO_STRESS_GENES)}")
    print(f"  Glycolysis genes available: {len(available_glyco)}/{len(GLYCOLYSIS_GENES)}")

    if len(available_oxphos) < 5:
        raise ValueError(
            f"Too few OXPHOS genes available ({len(available_oxphos)}). Need at least 5."
        )

    # OXPHOS score = mean expression of OXPHOS genes
    oxphos_score = rnaseq_df[available_oxphos].mean(axis=1)

    # Mitochondrial stress score = mean expression of stress markers
    if available_stress:
        mito_stress_score = rnaseq_df[available_stress].mean(axis=1)
    else:
        mito_stress_score = np.zeros(len(rnaseq_df))

    # Glycolysis score (inverse proxy for OXPHOS)
    if available_glyco:
        glycolysis_score = rnaseq_df[available_glyco].mean(axis=1)
    else:
        glycolysis_score = np.zeros(len(rnaseq_df))

    # ATP proxy = high OXPHOS + low stress + low glycolysis
    # Formula: Z(oxphos) - Z(stress) - Z(glycolysis)
    from scipy import stats

    z_oxphos = stats.zscore(oxphos_score)
    z_stress = stats.zscore(mito_stress_score) if available_stress else 0
    z_glyco = stats.zscore(glycolysis_score) if available_glyco else 0

    atp_proxy = z_oxphos - z_stress - z_glyco

    result = pd.DataFrame(
        {
            "sample_id": rnaseq_df.index,
            "atp_proxy": atp_proxy,
            "oxphos_score": oxphos_score,
            "mito_stress_score": mito_stress_score,
            "glycolysis_score": glycolysis_score,
        }
    )

    print(f"  ATP proxy range: {atp_proxy.min():.2f} to {atp_proxy.max():.2f}")
    print(f"  Mean: {atp_proxy.mean():.2f}, Std: {atp_proxy.std():.2f}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Calculate ATP proxy from RNA-seq")
    parser.add_argument(
        "--rnaseq", type=Path, required=True, help="Input RNA-seq CSV (samples x genes)"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")

    args = parser.parse_args()

    print(f"Loading RNA-seq data from {args.rnaseq}...")
    rnaseq_df = pd.read_csv(args.rnaseq, index_col=0)
    print(f"  Shape: {rnaseq_df.shape} (samples x genes)")

    result = calculate_atp_proxy(rnaseq_df)

    result.to_csv(args.output, index=False)
    print(f"✓ Saved ATP proxy scores to {args.output}")


if __name__ == "__main__":
    main()
