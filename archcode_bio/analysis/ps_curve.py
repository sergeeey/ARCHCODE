"""
Compute P(s) curve (contact probability vs genomic distance).

P(s) is the probability of contact at genomic distance s.
"""

import numpy as np
from pathlib import Path
from typing import Any

try:
    import cooler
except ImportError:
    cooler = None


def compute_ps_curve(cool_file: str | Path, bins: int = 50) -> dict[str, Any]:
    """
    Compute P(s) curve from Hi-C cooler file.

    Args:
        cool_file: Path to .cool or .mcool file
        bins: Number of distance bins (logarithmic spacing)

    Returns:
        Dictionary with:
            - distances: list of genomic distances (bp)
            - ps_values: list of contact probabilities
            - scaling_exponent: power-law exponent (alpha in P(s) ~ s^(-alpha))
    """
    if cooler is None:
        raise ImportError("cooler library is required. Install with: pip install cooler")

    cool_file = Path(cool_file)

    # Handle .mcool files
    if cool_file.suffix == ".mcool":
        c = cooler.Cooler(str(cool_file) + "::/resolutions/100000")
    else:
        c = cooler.Cooler(str(cool_file))

    # Get bin size
    bin_size = c.binsize

    # Get all chromosomes
    bins_df = c.bins()[:]
    chroms = bins_df["chrom"].unique()

    # Collect all contacts and distances
    all_distances = []
    all_contacts = []

    for chrom in chroms:
        chrom_matrix = c.matrix(balance=True).fetch(chrom)
        n_bins = len(chrom_matrix)

        for i in range(n_bins):
            for j in range(i + 1, n_bins):
                distance = abs(j - i) * bin_size
                contact = chrom_matrix[i, j]

                if contact > 0:  # Only non-zero contacts
                    all_distances.append(distance)
                    all_contacts.append(contact)

    # Bin distances logarithmically
    if len(all_distances) == 0:
        return {
            "distances": [],
            "ps_values": [],
            "scaling_exponent": 0.0,
            "num_contacts": 0,
        }

    min_dist = min(all_distances)
    max_dist = max(all_distances)

    # Logarithmic bins
    log_bins = np.logspace(np.log10(min_dist), np.log10(max_dist), bins + 1)
    bin_centers = (log_bins[:-1] + log_bins[1:]) / 2

    # Compute P(s) for each bin
    ps_values = []
    for i in range(len(log_bins) - 1):
        bin_start = log_bins[i]
        bin_end = log_bins[i + 1]

        # Find contacts in this distance bin
        mask = (np.array(all_distances) >= bin_start) & (np.array(all_distances) < bin_end)
        bin_contacts = np.array(all_contacts)[mask]

        if len(bin_contacts) > 0:
            ps = float(np.mean(bin_contacts))
        else:
            ps = 0.0

        ps_values.append(ps)

    # Fit power-law: P(s) ~ s^(-alpha)
    # Use log-log linear regression
    valid_mask = np.array(ps_values) > 0
    if np.sum(valid_mask) > 2:
        log_distances = np.log10(bin_centers[valid_mask])
        log_ps = np.log10(np.array(ps_values)[valid_mask])

        # Linear fit
        coeffs = np.polyfit(log_distances, log_ps, 1)
        scaling_exponent = float(-coeffs[0])  # Negative slope
    else:
        scaling_exponent = 0.0

    return {
        "distances": [float(d) for d in bin_centers],
        "ps_values": ps_values,
        "scaling_exponent": scaling_exponent,
        "num_contacts": len(all_contacts),
        "num_bins": bins,
    }


