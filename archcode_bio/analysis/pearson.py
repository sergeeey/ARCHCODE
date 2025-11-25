"""
Compute Pearson correlation matrix from Hi-C data.

Pearson correlation matrix is used for compartment analysis and
identifying long-range interactions.
"""

import numpy as np
from pathlib import Path
from typing import Any

try:
    import cooler
except ImportError:
    cooler = None


def compute_pearson_matrix(cool_file: str | Path) -> dict[str, Any]:
    """
    Compute Pearson correlation matrix from Hi-C cooler file.

    Args:
        cool_file: Path to .cool or .mcool file

    Returns:
        Dictionary with:
            - correlation_matrix: 2D array of correlations
            - mean_correlation: mean correlation value
            - std_correlation: standard deviation
            - bin_positions: list of bin positions
    """
    if cooler is None:
        raise ImportError("cooler library is required. Install with: pip install cooler")

    cool_file = Path(cool_file)

    # Handle .mcool files
    if cool_file.suffix == ".mcool":
        c = cooler.Cooler(str(cool_file) + "::/resolutions/100000")
    else:
        c = cooler.Cooler(str(cool_file))

    # Get bins
    bins = c.bins()[:]
    chroms = bins["chrom"].unique()

    all_correlations = []
    bin_positions = []

    # Compute correlation for each chromosome
    for chrom in chroms:
        chrom_bins = bins[bins["chrom"] == chrom]
        chrom_matrix = c.matrix(balance=True).fetch(chrom)

        # Compute Pearson correlation
        corr_matrix = np.corrcoef(chrom_matrix)
        corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)

        # Flatten and store
        all_correlations.extend(corr_matrix.flatten().tolist())

        # Store bin positions
        for _, row in chrom_bins.iterrows():
            bin_positions.append({
                "chrom": str(chrom),
                "start": int(row["start"]),
                "end": int(row["end"]),
            })

    # Compute statistics
    corr_array = np.array(all_correlations)
    mean_correlation = float(np.mean(corr_array))
    std_correlation = float(np.std(corr_array))

    return {
        "correlation_matrix": [[float(x) for x in row] for row in corr_matrix],
        "mean_correlation": mean_correlation,
        "std_correlation": std_correlation,
        "bin_positions": bin_positions,
        "matrix_shape": list(corr_matrix.shape),
    }




