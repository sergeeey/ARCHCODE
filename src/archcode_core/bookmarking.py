"""CTCF Bookmarking Logic for RS-10.

Manages bookmarking-dependent barrier strength adjustments through cell cycle phases.
"""

import random

import numpy as np

from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.extrusion_engine import Boundary


def adjust_barrier_for_phase(
    barrier: Boundary, phase: CellCyclePhase, enable_bookmarking: bool = True
) -> None:
    """
    Modify effective barrier strength based on cell cycle phase and bookmarking.

    Phase-dependent logic:
    - INTERPHASE/WT baseline: effective_strength = strength
    - MITOSIS:
      * if bookmarked: effective_strength = strength * 0.4
      * else: effective_strength = strength * 0.0 (completely disabled)
    - G1_EARLY:
      * if bookmarked: effective_strength = strength * 0.7
      * else: strength * 0.2
    - G1_LATE:
      * effective_strength = strength * 1.0 for all

    Args:
        barrier: Boundary to adjust
        phase: Current cell cycle phase
        enable_bookmarking: Whether bookmarking is enabled (if False, treat all as non-bookmarked)
    """
    # Determine bookmarking status
    is_bookmarked = barrier.is_bookmarked if enable_bookmarking else False

    # Phase-dependent multipliers
    if phase == CellCyclePhase.INTERPHASE:
        # Baseline: normal strength
        barrier.effective_strength = barrier.strength

    elif phase == CellCyclePhase.MITOSIS:
        # Mitosis: barriers weakened, bookmarked partially active
        if is_bookmarked:
            barrier.effective_strength = barrier.strength * 0.4
        else:
            barrier.effective_strength = barrier.strength * 0.0  # Completely disabled

    elif phase == CellCyclePhase.G1_EARLY:
        # Early G1: bookmarked recover faster
        if is_bookmarked:
            barrier.effective_strength = barrier.strength * 0.7
        else:
            barrier.effective_strength = barrier.strength * 0.2

    elif phase == CellCyclePhase.G1_LATE:
        # Late G1: all barriers restored to normal
        barrier.effective_strength = barrier.strength * 1.0

    else:
        # Default: use original strength
        barrier.effective_strength = barrier.strength


def reset_barriers_to_baseline(boundaries: list[Boundary]) -> None:
    """
    Reset all barriers to baseline (interphase) strength.

    Args:
        boundaries: List of boundaries to reset
    """
    for barrier in boundaries:
        barrier.effective_strength = barrier.strength


def assign_bookmarking(boundaries: list[Boundary], fraction: float, seed: int | None = None) -> None:
    """
    Assign bookmarking status to boundaries based on fraction.

    Args:
        boundaries: List of boundaries
        fraction: Fraction of boundaries to mark as bookmarked (0.0-1.0)
        seed: Random seed for reproducibility (if None, uses deterministic assignment)
    """
    if seed is not None:
        random.seed(seed)

    n = len(boundaries)
    k = int(n * fraction)

    if seed is None:
        # Deterministic: mark first k boundaries
        for i, boundary in enumerate(boundaries):
            boundary.is_bookmarked = i < k
    else:
        # Random assignment with seed
        indices = list(range(n))
        random.shuffle(indices)
        bookmarked_indices = set(indices[:k])
        for i, boundary in enumerate(boundaries):
            boundary.is_bookmarked = i in bookmarked_indices


def apply_stochastic_recovery(
    boundaries: list[Boundary],
    boundary_loss_rate: float = 0.2,
    boundary_shift_std: float = 15000.0,
    seed: int | None = None,
) -> list[Boundary]:
    """
    Apply stochastic recovery after mitosis for non-bookmarked boundaries.

    For non-bookmarked boundaries:
    - Probability of loss: boundary_loss_rate
    - Position shift: Gaussian noise with std=boundary_shift_std
    - Strength variation: ±5-15% random

    For bookmarked boundaries:
    - Position fixed
    - Strength fully restored

    Args:
        boundaries: List of boundaries
        boundary_loss_rate: Probability of losing non-bookmarked boundary (0.0-1.0)
        boundary_shift_std: Standard deviation for position shift (bp)
        seed: Random seed for reproducibility

    Returns:
        List of recovered boundaries (some may be lost, positions shifted)
    """
    if seed is not None:
        random.seed(seed)

    recovered_boundaries = []

    for boundary in boundaries:
        if boundary.is_bookmarked:
            # Bookmarked: fully restored, position fixed
            boundary.effective_strength = boundary.strength
            recovered_boundaries.append(boundary)
        else:
            # Non-bookmarked: stochastic recovery
            # Check if boundary is lost
            if random.random() < boundary_loss_rate:
                # Boundary is lost
                continue

            # Apply position shift
            shift = random.gauss(0.0, boundary_shift_std)
            boundary.position = int(boundary.position + shift)

            # Apply strength variation (±5-15%)
            strength_variation = random.uniform(-0.15, 0.15)
            boundary.strength = max(0.0, min(1.0, boundary.strength * (1.0 + strength_variation)))
            boundary.effective_strength = boundary.strength

            recovered_boundaries.append(boundary)

    return recovered_boundaries


def calculate_entropy_of_positions(boundaries: list[Boundary], bins: int = 10) -> float:
    """
    Calculate Shannon entropy of boundary positions (measure of "spread").

    Args:
        boundaries: List of boundaries
        bins: Number of bins for histogram

    Returns:
        Entropy (0.0-1.0, normalized)
    """
    if not boundaries:
        return 0.0

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

