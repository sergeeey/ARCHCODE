"""
Compute Insulation Score from Hi-C data.

Insulation Score measures local contact density and identifies TAD boundaries.
"""

import numpy as np
from pathlib import Path
from typing import Any

try:
    import cooler
    import bioframe
except ImportError:
    cooler = None
    bioframe = None


def compute_insulation(cool_file: str | Path, window: int = 5) -> dict[str, Any]:
    """
    Compute Insulation Score from Hi-C cooler file.

    Args:
        cool_file: Path to .cool or .mcool file
        window: Window size in bins for insulation calculation

    Returns:
        Dictionary with:
            - insulation_scores: list of insulation values per bin
            - bin_positions: list of bin positions (chrom, start, end)
            - mean_insulation: mean insulation score
            - std_insulation: standard deviation
            - min_insulation: minimum value
            - max_insulation: maximum value
    """
    if cooler is None:
        raise ImportError("cooler library is required. Install with: pip install cooler")

    cool_file = Path(cool_file)

    # Handle .mcool files
    if cool_file.suffix == ".mcool":
        # Open at specific resolution (default: 100kb)
        c = cooler.Cooler(str(cool_file) + "::/resolutions/100000")
    else:
        c = cooler.Cooler(str(cool_file))

    # Get bins
    bins = c.bins()[:]
    chroms = bins["chrom"].unique()

    insulation_scores = []
    bin_positions = []

    # Compute insulation for each chromosome
    for chrom in chroms:
        chrom_bins = bins[bins["chrom"] == chrom]
        chrom_matrix = c.matrix(balance=True).fetch(chrom)

        # Compute insulation score
        # Insulation = sum of contacts in window around each bin
        n_bins = len(chrom_bins)
        chrom_insulation = []

        for i in range(n_bins):
            # Define window around bin i
            start = max(0, i - window)
            end = min(n_bins, i + window + 1)

            # Sum contacts in window (excluding diagonal)
            window_contacts = 0
            for j in range(start, end):
                for k in range(start, end):
                    if j != k:  # Exclude diagonal
                        window_contacts += chrom_matrix[j, k]

            chrom_insulation.append(float(window_contacts))

            # Store bin position
            bin_positions.append({
                "chrom": str(chrom),
                "start": int(chrom_bins.iloc[i]["start"]),
                "end": int(chrom_bins.iloc[i]["end"]),
            })

        insulation_scores.extend(chrom_insulation)

    # Compute statistics
    insulation_array = np.array(insulation_scores)
    mean_insulation = float(np.mean(insulation_array))
    std_insulation = float(np.std(insulation_array))
    min_insulation = float(np.min(insulation_array))
    max_insulation = float(np.max(insulation_array))

    return {
        "insulation_scores": [float(x) for x in insulation_scores],
        "bin_positions": bin_positions,
        "mean_insulation": mean_insulation,
        "std_insulation": std_insulation,
        "min_insulation": min_insulation,
        "max_insulation": max_insulation,
        "window_size": window,
        "num_bins": len(insulation_scores),
    }


