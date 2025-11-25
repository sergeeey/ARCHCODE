"""
Compute Aggregate Peak Analysis (APA) for loop detection.

APA aggregates contact frequencies around putative loop anchors
to validate loop calls.
"""

import numpy as np
from pathlib import Path
from typing import Any

try:
    import cooler
except ImportError:
    cooler = None


def compute_apa(cool_file: str | Path, loops_list: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute Aggregate Peak Analysis (APA) for loop validation.

    Args:
        cool_file: Path to .cool or .mcool file
        loops_list: List of loop dictionaries with:
            - chrom: chromosome name
            - start1: start of first anchor (bp)
            - end1: end of first anchor (bp)
            - start2: start of second anchor (bp)
            - end2: end of second anchor (bp)

    Returns:
        Dictionary with:
            - apa_matrix: aggregated contact matrix around loops
            - mean_peak_strength: mean peak strength
            - peak_detection_rate: fraction of loops with peaks
            - num_loops: number of loops analyzed
    """
    if cooler is None:
        raise ImportError("cooler library is required. Install with: pip install cooler")

    cool_file = Path(cool_file)

    # Handle .mcool files
    if cool_file.suffix == ".mcool":
        c = cooler.Cooler(str(cool_file) + "::/resolutions/10000")  # Higher resolution for loops
    else:
        c = cooler.Cooler(str(cool_file))

    bin_size = c.binsize
    window_size = 5  # bins around loop center

    # Aggregate contacts around loops
    apa_matrices = []

    for loop in loops_list:
        chrom = loop["chrom"]
        start1 = loop["start1"]
        end1 = loop["end1"]
        start2 = loop["start2"]
        end2 = loop["end2"]

        # Find bin indices
        bins_df = c.bins()[:]
        chrom_bins = bins_df[bins_df["chrom"] == chrom]

        # Find bins containing anchors
        bin1_idx = None
        bin2_idx = None

        for idx, row in chrom_bins.iterrows():
            if row["start"] <= start1 <= row["end"]:
                bin1_idx = idx
            if row["start"] <= start2 <= row["end"]:
                bin2_idx = idx

        if bin1_idx is None or bin2_idx is None:
            continue

        # Extract matrix around loop
        try:
            chrom_matrix = c.matrix(balance=True).fetch(chrom)

            # Get window around loop
            i1_start = max(0, bin1_idx - window_size)
            i1_end = min(len(chrom_matrix), bin1_idx + window_size + 1)
            i2_start = max(0, bin2_idx - window_size)
            i2_end = min(len(chrom_matrix), bin2_idx + window_size + 1)

            window_matrix = chrom_matrix[i1_start:i1_end, i2_start:i2_end]
            apa_matrices.append(window_matrix)
        except Exception:
            continue

    if len(apa_matrices) == 0:
        return {
            "apa_matrix": [],
            "mean_peak_strength": 0.0,
            "peak_detection_rate": 0.0,
            "num_loops": 0,
        }

    # Aggregate matrices
    # Align by loop center
    aggregated = np.zeros((window_size * 2 + 1, window_size * 2 + 1))
    peak_strengths = []

    for mat in apa_matrices:
        # Center the matrix
        center_i = mat.shape[0] // 2
        center_j = mat.shape[1] // 2

        # Extract centered window
        start_i = max(0, center_i - window_size)
        end_i = min(mat.shape[0], center_i + window_size + 1)
        start_j = max(0, center_j - window_size)
        end_j = min(mat.shape[1], center_j + window_size + 1)

        window = mat[start_i:end_i, start_j:end_j]

        # Pad if necessary
        if window.shape[0] < window_size * 2 + 1:
            pad_before = (window_size * 2 + 1 - window.shape[0]) // 2
            pad_after = window_size * 2 + 1 - window.shape[0] - pad_before
            window = np.pad(window, ((pad_before, pad_after), (0, 0)), mode="constant")

        if window.shape[1] < window_size * 2 + 1:
            pad_before = (window_size * 2 + 1 - window.shape[1]) // 2
            pad_after = window_size * 2 + 1 - window.shape[1] - pad_before
            window = np.pad(window, ((0, 0), (pad_before, pad_after)), mode="constant")

        aggregated += window

        # Peak strength = center value / mean
        center_val = window[window_size, window_size]
        mean_val = np.mean(window)
        if mean_val > 0:
            peak_strength = center_val / mean_val
            peak_strengths.append(float(peak_strength))

    # Normalize
    aggregated = aggregated / len(apa_matrices)

    # Compute statistics
    mean_peak_strength = float(np.mean(peak_strengths)) if peak_strengths else 0.0
    peak_detection_rate = sum(1 for ps in peak_strengths if ps > 1.5) / len(peak_strengths) if peak_strengths else 0.0

    return {
        "apa_matrix": [[float(x) for x in row] for row in aggregated],
        "mean_peak_strength": mean_peak_strength,
        "peak_detection_rate": peak_detection_rate,
        "num_loops": len(apa_matrices),
        "window_size": window_size,
    }




