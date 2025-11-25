"""Memory Metrics for RS-11.

Standardized metrics for measuring architectural memory retention
across multiple cell cycles.
"""

from typing import Literal

import numpy as np

from src.archcode_core.extrusion_engine import Boundary


def calculate_jaccard_stable_boundaries(
    stable_baseline: set[int], stable_cycle_n: set[int]
) -> float:
    """
    Calculate Jaccard index of stable boundaries between baseline and cycle N.

    Jaccard = |intersection| / |union|

    Args:
        stable_baseline: Set of stable boundary positions at baseline (cycle 0)
        stable_cycle_n: Set of stable boundary positions at cycle N

    Returns:
        Jaccard index (0.0-1.0)
    """
    if not stable_baseline and not stable_cycle_n:
        return 1.0  # Both empty = perfect match

    intersection = len(stable_baseline & stable_cycle_n)
    union = len(stable_baseline | stable_cycle_n)

    return intersection / union if union > 0 else 0.0


def calculate_drift_distance(
    boundaries_before: list[Boundary], boundaries_after: list[Boundary]
) -> float:
    """
    Calculate average drift distance (position shift) between cycles.

    Args:
        boundaries_before: Boundaries before cycle
        boundaries_after: Boundaries after cycle

    Returns:
        Average drift distance (bp)
    """
    if not boundaries_before or not boundaries_after:
        return 0.0

    # Match boundaries by closest position
    positions_before = {b.position for b in boundaries_before}
    positions_after = {b.position for b in boundaries_after}

    # Find matched boundaries (within 50kb tolerance)
    matched_drifts = []
    tolerance = 50000

    for b_after in boundaries_after:
        closest_before = None
        min_dist = float("inf")

        for b_before in boundaries_before:
            dist = abs(b_before.position - b_after.position)
            if dist < min_dist and dist < tolerance:
                min_dist = dist
                closest_before = b_before

        if closest_before:
            matched_drifts.append(abs(closest_before.position - b_after.position))

    return sum(matched_drifts) / len(matched_drifts) if matched_drifts else 0.0


def calculate_entropy(
    boundaries: list[Boundary],
    bins: int = 10,
    entropy_type: Literal["position", "category"] = "position",
) -> float:
    """
    Calculate Shannon entropy of boundary configuration.

    Args:
        boundaries: List of boundaries
        bins: Number of bins for histogram (for position entropy)
        entropy_type: Type of entropy:
            - 'position': Entropy of boundary positions (spatial spread)
            - 'category': Entropy of stability categories (stable/variable/collapsed)

    Returns:
        Normalized entropy (0.0-1.0)
    """
    if not boundaries:
        return 0.0

    if entropy_type == "position":
        return _calculate_position_entropy(boundaries, bins)
    elif entropy_type == "category":
        return _calculate_category_entropy(boundaries)
    else:
        raise ValueError(f"Unknown entropy_type: {entropy_type}")


def _calculate_position_entropy(boundaries: list[Boundary], bins: int) -> float:
    """Calculate entropy of boundary positions."""
    positions = [b.position for b in boundaries]
    if len(positions) < 2:
        return 0.0

    # Normalize positions to [0, 1] range
    min_pos = min(positions)
    max_pos = max(positions)
    if max_pos == min_pos:
        return 0.0

    normalized = [(p - min_pos) / (max_pos - min_pos) for p in positions]

    # Create histogram
    hist, _ = np.histogram(normalized, bins=bins, range=(0.0, 1.0))
    hist = hist.astype(float)
    hist = hist / hist.sum() if hist.sum() > 0 else hist

    # Calculate Shannon entropy
    entropy = 0.0
    for p in hist:
        if p > 0:
            entropy -= p * np.log2(p)

    # Normalize to [0, 1]
    max_entropy = np.log2(bins)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def _calculate_category_entropy(boundaries: list[Boundary]) -> float:
    """Calculate entropy of stability categories."""
    # Categorize boundaries based on strength
    # This is a simplified categorization - can be enhanced
    categories = {"stable": 0, "variable": 0, "collapsed": 0}

    for boundary in boundaries:
        if boundary.strength >= 0.7:
            categories["stable"] += 1
        elif boundary.strength >= 0.3:
            categories["variable"] += 1
        else:
            categories["collapsed"] += 1

    total = sum(categories.values())
    if total == 0:
        return 0.0

    # Calculate Shannon entropy
    entropy = 0.0
    for count in categories.values():
        if count > 0:
            p = count / total
            entropy -= p * np.log2(p)

    # Normalize to [0, 1] (max entropy = log2(3) for 3 categories)
    max_entropy = np.log2(3)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def calculate_memory_retention_score(
    jaccard: float,
    entropy: float,
    drift_distance: float,
    max_drift: float = 50000.0,
) -> float:
    """
    Calculate composite memory retention score.

    Formula: M = Jaccard * (1 - normalized_entropy) * (1 - normalized_drift)

    Args:
        jaccard: Jaccard index of stable boundaries
        entropy: Normalized entropy (0.0-1.0)
        drift_distance: Average drift distance (bp)
        max_drift: Maximum expected drift for normalization (bp)

    Returns:
        Memory retention score (0.0-1.0)
    """
    # Normalize drift distance to [0, 1]
    normalized_drift = min(1.0, drift_distance / max_drift) if max_drift > 0 else 0.0

    # Calculate memory retention score
    memory_score = jaccard * (1.0 - entropy) * (1.0 - normalized_drift)

    return max(0.0, min(1.0, memory_score))


def find_cycle_to_collapse(
    jaccard_trajectory: list[float],
    threshold: float = 0.3,
) -> int | None:
    """
    Find the cycle number when Jaccard falls below threshold.

    Args:
        jaccard_trajectory: List of Jaccard values per cycle [J(0), J(1), ..., J(N)]
        threshold: Collapse threshold (default: 0.3)

    Returns:
        Cycle number when collapse occurs, or None if never collapses
    """
    for cycle, jaccard in enumerate(jaccard_trajectory):
        if jaccard < threshold:
            return cycle

    return None  # Never collapsed


def calculate_boundary_category_distribution(
    boundaries: list[Boundary],
) -> dict[str, int]:
    """
    Calculate distribution of boundaries by stability category.

    Args:
        boundaries: List of boundaries

    Returns:
        Dictionary with counts: {"stable": N, "variable": M, "collapsed": K}
    """
    categories = {"stable": 0, "variable": 0, "collapsed": 0}

    for boundary in boundaries:
        if boundary.strength >= 0.7:
            categories["stable"] += 1
        elif boundary.strength >= 0.3:
            categories["variable"] += 1
        else:
            categories["collapsed"] += 1

    return categories


def get_stable_boundaries(
    boundaries: list[Boundary], stability_threshold: float = 0.7
) -> set[int]:
    """
    Extract set of stable boundary positions.

    Args:
        boundaries: List of boundaries
        stability_threshold: Minimum strength for "stable" category

    Returns:
        Set of stable boundary positions
    """
    stable = set()
    for boundary in boundaries:
        if boundary.strength >= stability_threshold:
            stable.add(boundary.position)

    return stable


