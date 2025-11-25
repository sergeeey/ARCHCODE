"""
Compute A/B compartments from Hi-C data.

Compartments are identified using Principal Component Analysis (PCA)
on the correlation matrix of Hi-C contacts.
"""

import numpy as np
from pathlib import Path
from typing import Any

try:
    import cooler
    from sklearn.decomposition import PCA
except ImportError:
    cooler = None
    PCA = None


def compute_compartments(cool_file: str | Path) -> dict[str, Any]:
    """
    Compute A/B compartments from Hi-C cooler file.

    Args:
        cool_file: Path to .cool or .mcool file

    Returns:
        Dictionary with:
            - compartment_labels: list of 'A' or 'B' per bin
            - pc1_scores: first principal component scores
            - compartment_strength: separation strength between A/B
            - compartment_fraction: fraction of genome in A compartment
    """
    if cooler is None:
        raise ImportError("cooler library is required. Install with: pip install cooler")
    if PCA is None:
        raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")

    cool_file = Path(cool_file)

    # Handle .mcool files
    if cool_file.suffix == ".mcool":
        c = cooler.Cooler(str(cool_file) + "::/resolutions/100000")
    else:
        c = cooler.Cooler(str(cool_file))

    # Get bins
    bins = c.bins()[:]
    chroms = bins["chrom"].unique()

    all_pc1_scores = []
    all_labels = []
    bin_positions = []

    # Compute compartments for each chromosome
    for chrom in chroms:
        chrom_bins = bins[bins["chrom"] == chrom]
        chrom_matrix = c.matrix(balance=True).fetch(chrom)

        # Convert to correlation matrix
        # Use Pearson correlation
        corr_matrix = np.corrcoef(chrom_matrix)

        # Replace NaN with 0
        corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

        # PCA on correlation matrix
        pca = PCA(n_components=1)
        pc1 = pca.fit_transform(corr_matrix).flatten()

        # Assign compartments based on PC1 sign
        # Positive = A compartment, Negative = B compartment
        labels = ["A" if score > 0 else "B" for score in pc1]

        all_pc1_scores.extend([float(x) for x in pc1])
        all_labels.extend(labels)

        # Store bin positions
        for _, row in chrom_bins.iterrows():
            bin_positions.append({
                "chrom": str(chrom),
                "start": int(row["start"]),
                "end": int(row["end"]),
            })

    # Compute compartment statistics
    pc1_array = np.array(all_pc1_scores)
    compartment_strength = float(np.std(pc1_array))  # Separation strength
    compartment_fraction = sum(1 for l in all_labels if l == "A") / len(all_labels)

    return {
        "compartment_labels": all_labels,
        "pc1_scores": all_pc1_scores,
        "compartment_strength": compartment_strength,
        "compartment_fraction": compartment_fraction,
        "bin_positions": bin_positions,
        "num_bins": len(all_labels),
    }


