"""Epigenetic Memory Module for RS-11.

Implements the second channel of architectural memory: epigenetic/transcriptional memory.
This complements CTCF bookmarking (first channel) to enable multichannel memory model.
"""

import random
from typing import Literal

import numpy as np

from src.archcode_core.extrusion_engine import Boundary


def initialize_epigenetic_memory(
    boundaries: list[Boundary],
    mode: Literal["uniform", "random", "correlated_with_strength"] = "uniform",
    strength: float = 0.5,
    seed: int | None = None,
    **kwargs,
) -> dict[int, float]:
    """
    Initialize epigenetic memory scores for boundaries.

    Epigenetic memory score ∈ [0, 1] represents how well a boundary
    "remembers" its position through mitosis via epigenetic marks
    (histone modifications, transcriptional activity, enhancer memory).

    Args:
        boundaries: List of boundaries to initialize
        mode: Initialization mode:
            - 'uniform': All boundaries get the same score (strength)
            - 'random': Random scores from uniform distribution [0, strength]
            - 'correlated_with_strength': Strong boundaries get higher scores
        strength: Base strength for uniform mode, or max strength for random mode
        seed: Random seed for reproducibility
        **kwargs: Additional parameters:
            - min_score: Minimum score (default: 0.0)
            - max_score: Maximum score (default: 1.0)
            - correlation_factor: For correlated mode (default: 0.8)

    Returns:
        Dictionary mapping boundary position -> epigenetic_memory_score
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    min_score = kwargs.get("min_score", 0.0)
    max_score = kwargs.get("max_score", 1.0)
    correlation_factor = kwargs.get("correlation_factor", 0.8)

    epigenetic_scores = {}

    if mode == "uniform":
        # All boundaries get the same score
        score = max(min_score, min(max_score, strength))
        for boundary in boundaries:
            epigenetic_scores[boundary.position] = score

    elif mode == "random":
        # Random scores from uniform distribution [0, strength]
        for boundary in boundaries:
            score = random.uniform(min_score, min(max_score, strength))
            epigenetic_scores[boundary.position] = score

    elif mode == "correlated_with_strength":
        # Strong boundaries get higher epigenetic memory scores
        # Formula: score = min_score + (boundary.strength * correlation_factor * (max_score - min_score))
        for boundary in boundaries:
            base_score = boundary.strength * correlation_factor
            score = min_score + base_score * (max_score - min_score)
            score = max(min_score, min(max_score, score))
            epigenetic_scores[boundary.position] = score

    else:
        raise ValueError(f"Unknown mode: {mode}")

    return epigenetic_scores


def restore_with_epigenetic_memory(
    boundaries: list[Boundary],
    epigenetic_scores: dict[int, float],
    rng: random.Random | None = None,
    params: dict | None = None,
) -> tuple[list[Boundary], dict[int, float]]:
    """
    Restore boundaries after mitosis using epigenetic memory channel.

    This function complements CTCF bookmarking:
    - Bookmarked boundaries: Restored via CTCF bookmarking (handled separately)
    - Non-bookmarked boundaries: Can be restored via epigenetic memory with probability
      proportional to their epigenetic_memory_score

    Args:
        boundaries: List of boundaries before mitosis
        epigenetic_scores: Dictionary mapping position -> epigenetic_memory_score
        rng: Random number generator (if None, uses global random)
        params: Parameters dictionary:
            - bookmarking_fraction: Fraction of boundaries that are CTCF-bookmarked (default: 0.0)
            - epigenetic_strength: Global multiplier for epigenetic restoration (default: 1.0)
            - restoration_function: 'linear' or 'sigmoid' (default: 'linear')
            - boundary_loss_rate: Base loss rate for non-bookmarked, non-epigenetic (default: 0.2)
            - boundary_shift_std: Standard deviation for position shift (default: 15000.0)

    Returns:
        Tuple of:
        - restored_boundaries: List of restored boundaries
        - restoration_probabilities: Dictionary mapping position -> restoration probability
    """
    if rng is None:
        rng = random.Random()

    if params is None:
        params = {}

    bookmarking_fraction = params.get("bookmarking_fraction", 0.0)
    epigenetic_strength = params.get("epigenetic_strength", 1.0)
    restoration_function = params.get("restoration_function", "linear")
    boundary_loss_rate = params.get("boundary_loss_rate", 0.2)
    boundary_shift_std = params.get("boundary_shift_std", 15000.0)

    restored_boundaries = []
    restoration_probabilities = {}

    # Separate bookmarked and non-bookmarked boundaries
    bookmarked_boundaries = [b for b in boundaries if b.is_bookmarked]
    non_bookmarked_boundaries = [b for b in boundaries if not b.is_bookmarked]

    # Bookmarked boundaries: restored via CTCF bookmarking (100% probability)
    for boundary in bookmarked_boundaries:
        restoration_probabilities[boundary.position] = 1.0
        restored_boundaries.append(boundary)

    # Non-bookmarked boundaries: restored via epigenetic memory
    for boundary in non_bookmarked_boundaries:
        # Get epigenetic score (default to 0.0 if not found)
        epigenetic_score = epigenetic_scores.get(boundary.position, 0.0)

        # Calculate restoration probability based on epigenetic score
        if restoration_function == "linear":
            # Linear: P(restore) = epigenetic_score * epigenetic_strength
            restore_prob = epigenetic_score * epigenetic_strength
        elif restoration_function == "sigmoid":
            # Sigmoid: P(restore) = sigmoid(epigenetic_score * epigenetic_strength)
            # Using tanh for sigmoid-like behavior: (tanh(x) + 1) / 2 maps [0, inf] -> [0.5, 1.0]
            # We scale to [0, 1] by: (tanh(2 * score * strength) + 1) / 2
            scaled = 2.0 * epigenetic_score * epigenetic_strength
            restore_prob = (np.tanh(scaled) + 1.0) / 2.0
        else:
            raise ValueError(f"Unknown restoration_function: {restoration_function}")

        # Clamp probability to [0, 1]
        restore_prob = max(0.0, min(1.0, restore_prob))
        restoration_probabilities[boundary.position] = restore_prob

        # Decide whether to restore this boundary
        if rng.random() < restore_prob:
            # Boundary is restored, but may have position shift
            # Stronger epigenetic memory = less shift
            shift_factor = 1.0 - epigenetic_score  # Higher score = less shift
            shift = rng.gauss(0.0, boundary_shift_std * shift_factor)
            boundary.position = int(boundary.position + shift)

            # Strength variation (smaller for high epigenetic memory)
            strength_variation = rng.uniform(-0.15, 0.15) * (1.0 - epigenetic_score)
            boundary.strength = max(0.0, min(1.0, boundary.strength * (1.0 + strength_variation)))
            boundary.effective_strength = boundary.strength

            restored_boundaries.append(boundary)
        # else: boundary is lost (not restored)

    return restored_boundaries, restoration_probabilities


def update_epigenetic_memory(
    epigenetic_scores: dict[int, float],
    boundaries: list[Boundary],
    update_mode: Literal["static", "decay", "reinforcement"] = "static",
    decay_rate: float = 0.01,
    reinforcement_factor: float = 0.05,
    **kwargs,
) -> dict[int, float]:
    """
    Update epigenetic memory scores based on boundary stability.

    This function allows epigenetic memory to evolve over multiple cycles:
    - 'static': No change (default for RS-11A)
    - 'decay': Scores decay over time
    - 'reinforcement': Stable boundaries get stronger epigenetic memory

    Args:
        epigenetic_scores: Current epigenetic scores
        boundaries: Current boundaries (for stability assessment)
        update_mode: Update mode
        decay_rate: Decay rate per cycle (for 'decay' mode)
        reinforcement_factor: Reinforcement strength (for 'reinforcement' mode)
        **kwargs: Additional parameters

    Returns:
        Updated epigenetic scores dictionary
    """
    updated_scores = epigenetic_scores.copy()

    if update_mode == "static":
        # No change
        return updated_scores

    elif update_mode == "decay":
        # All scores decay
        for position in updated_scores:
            updated_scores[position] = max(0.0, updated_scores[position] - decay_rate)

    elif update_mode == "reinforcement":
        # Stable boundaries get reinforced
        # This requires stability information from boundaries
        # For now, we'll use boundary strength as proxy
        for boundary in boundaries:
            position = boundary.position
            if position in updated_scores:
                # Reinforce based on boundary strength
                reinforcement = boundary.strength * reinforcement_factor
                updated_scores[position] = min(1.0, updated_scores[position] + reinforcement)

    else:
        raise ValueError(f"Unknown update_mode: {update_mode}")

    return updated_scores

