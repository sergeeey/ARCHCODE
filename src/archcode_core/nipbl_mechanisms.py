"""NIPBL Mechanisms Module for Risk Mitigation.

Альтернативные сценарии влияния NIPBL на экструзию.
"""

from enum import Enum


class NIPBLMechanism(Enum):
    """Mechanisms of NIPBL action."""

    VELOCITY_ONLY = "velocity_only"  # Текущий режим
    DENSITY_ONLY = "density_only"  # Влияние на density экструдеров
    MIXED = "mixed"  # Комбинированный


def calculate_effective_extrusion_rate(
    nipbl_factor: float,
    mechanism: NIPBLMechanism,
    base_velocity: float = 1.0,
    base_density: float = 1.0,
) -> tuple[float, float]:
    """
    Calculate effective extrusion rate and density.

    Args:
        nipbl_factor: NIPBL activity factor (0.0-2.0)
        mechanism: Mechanism of NIPBL action
        base_velocity: Base extrusion velocity
        base_density: Base density of active extruders

    Returns:
        (effective_velocity, effective_density)
    """
    if mechanism == NIPBLMechanism.VELOCITY_ONLY:
        return (base_velocity * nipbl_factor, base_density)
    elif mechanism == NIPBLMechanism.DENSITY_ONLY:
        return (base_velocity, base_density * nipbl_factor)
    elif mechanism == NIPBLMechanism.MIXED:
        # Например: 70% velocity, 70% density
        # Это дает: velocity_factor = nipbl^0.7, density_factor = nipbl^0.7
        # Итоговый эффект: velocity * density = nipbl^1.4 ≈ nipbl (при малых изменениях)
        velocity_factor = nipbl_factor**0.7
        density_factor = nipbl_factor**0.7
        return (
            base_velocity * velocity_factor,
            base_density * density_factor,
        )
    else:
        raise ValueError(f"Unknown mechanism: {mechanism}")


def calculate_effective_processivity_from_mechanism(
    nipbl_factor: float,
    wapl_lifetime_factor: float,
    mechanism: NIPBLMechanism,
    base_velocity: float = 1.0,
    base_density: float = 1.0,
) -> float:
    """
    Calculate effective processivity from NIPBL mechanism.

    Args:
        nipbl_factor: NIPBL activity factor
        wapl_lifetime_factor: WAPL lifetime factor
        mechanism: Mechanism of NIPBL action
        base_velocity: Base velocity
        base_density: Base density

    Returns:
        Effective processivity
    """
    effective_velocity, effective_density = calculate_effective_extrusion_rate(
        nipbl_factor, mechanism, base_velocity, base_density
    )

    # Effective extrusion rate combines velocity and density
    # For simplicity, we use: rate = velocity * sqrt(density)
    # This captures that both contribute to overall extrusion activity
    effective_extrusion_rate = effective_velocity * (effective_density**0.5)

    # Processivity = effective_extrusion_rate × lifetime
    effective_processivity = effective_extrusion_rate * wapl_lifetime_factor

    return effective_processivity






