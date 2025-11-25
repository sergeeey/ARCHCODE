"""Environmental Factors Module for Risk Mitigation.

Локальные модификаторы processivity для учета CTCF density и A/B compartments.
"""


def calculate_effective_processivity(
    global_processivity: float,
    position: int,
    ctcf_density_map: dict[int, float],
    compartment_mask: dict[int, str] | None = None,
) -> float:
    """
    Calculate effective processivity with local environmental factors.

    Args:
        global_processivity: Global processivity (NIPBL × WAPL)
        position: Genomic position
        ctcf_density_map: Map of CTCF site density (0.0-1.0)
        compartment_mask: Optional A/B compartment mask

    Returns:
        Effective processivity (0.0-2.0)
    """
    # Base: CTCF density factor (0.5-1.5)
    ctcf_density = ctcf_density_map.get(position, 0.5)
    ctcf_factor = 0.5 + ctcf_density  # Range: 0.5-1.5

    # Optional: Compartment factor
    compartment_factor = 1.0
    if compartment_mask:
        compartment = compartment_mask.get(position, "B")
        # A compartments: slightly higher processivity
        compartment_factor = 1.1 if compartment == "A" else 0.95

    env_factor = ctcf_factor * compartment_factor
    effective_processivity = global_processivity * env_factor

    return max(0.0, min(2.0, effective_processivity))


def create_synthetic_compartment_mask(
    positions: list[int],
    compartment_size: int = 500000,
) -> dict[int, str]:
    """
    Create synthetic A/B compartment mask.

    Alternating A/B compartments of given size.

    Args:
        positions: List of genomic positions
        compartment_size: Size of each compartment (bp)

    Returns:
        Dictionary mapping position -> compartment ("A" or "B")
    """
    mask = {}
    for pos in positions:
        compartment_idx = pos // compartment_size
        mask[pos] = "A" if compartment_idx % 2 == 0 else "B"
    return mask


def calculate_ctcf_density_map(
    boundaries: list,
    window_size: int = 100000,
) -> dict[int, float]:
    """
    Calculate CTCF density map from boundaries.

    Args:
        boundaries: List of boundaries (with position attribute)
        window_size: Window size for density calculation (bp)

    Returns:
        Dictionary mapping position -> CTCF density (0.0-1.0)
    """
    if not boundaries:
        return {}

    # Get all positions
    positions = sorted(set(b.position for b in boundaries if hasattr(b, "position")))

    density_map = {}
    for pos in positions:
        # Count CTCF boundaries in window
        window_start = max(0, pos - window_size // 2)
        window_end = pos + window_size // 2

        ctcf_count = sum(
            1
            for b in boundaries
            if hasattr(b, "position")
            and hasattr(b, "barrier_type")
            and b.barrier_type == "ctcf"
            and window_start <= b.position <= window_end
        )

        # Normalize to 0.0-1.0 (assuming max ~10 CTCF sites per 100kb)
        max_expected = 10
        density = min(1.0, ctcf_count / max_expected)
        density_map[pos] = density

    return density_map









