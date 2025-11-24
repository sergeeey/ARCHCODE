"""
Call TAD boundaries from Insulation Score data.

TADs (Topologically Associating Domains) are identified as local minima
in the Insulation Score.
"""

import numpy as np
from typing import Any


def call_tads(insulation_data: dict[str, Any], threshold: float = 0.1) -> dict[str, Any]:
    """
    Call TAD boundaries from insulation score data.

    Args:
        insulation_data: Dictionary from compute_insulation()
        threshold: Fraction of mean insulation to use as threshold

    Returns:
        Dictionary with:
            - tad_boundaries: list of TAD boundary positions
            - tad_domains: list of TAD domains (start, end)
            - num_boundaries: number of boundaries found
            - num_domains: number of TADs found
    """
    insulation_scores = np.array(insulation_data["insulation_scores"])
    bin_positions = insulation_data["bin_positions"]

    # Find local minima (TAD boundaries)
    # A boundary is a local minimum below threshold
    mean_insulation = np.mean(insulation_scores)
    threshold_value = mean_insulation * (1 - threshold)

    boundaries = []
    for i in range(1, len(insulation_scores) - 1):
        # Check if local minimum
        if (
            insulation_scores[i] < insulation_scores[i - 1]
            and insulation_scores[i] < insulation_scores[i + 1]
            and insulation_scores[i] < threshold_value
        ):
            boundaries.append(i)

    # Convert to genomic positions
    tad_boundaries = []
    for idx in boundaries:
        tad_boundaries.append({
            "chrom": bin_positions[idx]["chrom"],
            "position": bin_positions[idx]["start"],
            "insulation_score": float(insulation_scores[idx]),
            "bin_index": int(idx),
        })

    # Define TAD domains (between boundaries)
    tad_domains = []
    if len(boundaries) > 0:
        # First domain: start of chromosome to first boundary
        if boundaries[0] > 0:
            tad_domains.append({
                "chrom": bin_positions[0]["chrom"],
                "start": bin_positions[0]["start"],
                "end": bin_positions[boundaries[0]]["start"],
                "domain_index": 0,
            })

        # Middle domains: between boundaries
        for i in range(len(boundaries) - 1):
            tad_domains.append({
                "chrom": bin_positions[boundaries[i]]["chrom"],
                "start": bin_positions[boundaries[i]]["start"],
                "end": bin_positions[boundaries[i + 1]]["start"],
                "domain_index": i + 1,
            })

        # Last domain: last boundary to end of chromosome
        if boundaries[-1] < len(bin_positions) - 1:
            tad_domains.append({
                "chrom": bin_positions[boundaries[-1]]["chrom"],
                "start": bin_positions[boundaries[-1]]["start"],
                "end": bin_positions[-1]["end"],
                "domain_index": len(boundaries),
            })

    return {
        "tad_boundaries": tad_boundaries,
        "tad_domains": tad_domains,
        "num_boundaries": len(boundaries),
        "num_domains": len(tad_domains),
        "threshold": float(threshold),
        "threshold_value": float(threshold_value),
    }

