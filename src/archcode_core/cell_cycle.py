"""Cell Cycle Management for ARCHCODE.

Manages cell cycle phases and phase-dependent logic for TAD boundary stability.
"""

from enum import Enum


class CellCyclePhase(Enum):
    """Cell cycle phases."""

    MITOSIS = "mitosis"
    G1_EARLY = "g1_early"
    G1_LATE = "g1_late"
    INTERPHASE = "interphase"  # Default stable state (G1 late / S phase)


class CellCycleManager:
    """
    Manages cell cycle phase transitions.
    
    For RS-10: Simple phase switcher without complex time dynamics.
    """

    def __init__(self, initial_phase: CellCyclePhase = CellCyclePhase.INTERPHASE) -> None:
        """
        Initialize cell cycle manager.

        Args:
            initial_phase: Starting phase
        """
        self.phase = initial_phase

    def set_phase(self, phase: CellCyclePhase) -> None:
        """
        Set current cell cycle phase.

        Args:
            phase: Phase to set
        """
        self.phase = phase

    def get_phase(self) -> CellCyclePhase:
        """
        Get current cell cycle phase.

        Returns:
            Current phase
        """
        return self.phase

    def is_mitosis(self) -> bool:
        """
        Check if currently in mitosis.

        Returns:
            True if in mitosis
        """
        return self.phase == CellCyclePhase.MITOSIS

    def is_g1_early(self) -> bool:
        """
        Check if in early G1.

        Returns:
            True if in early G1
        """
        return self.phase == CellCyclePhase.G1_EARLY

    def is_g1_late(self) -> bool:
        """
        Check if in late G1 (or interphase).

        Returns:
            True if in late G1 or interphase
        """
        return self.phase == CellCyclePhase.G1_LATE or self.phase == CellCyclePhase.INTERPHASE






