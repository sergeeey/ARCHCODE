"""Factor Aggregator - Aggregate stability factors from ARCHCODE modules."""

from dataclasses import dataclass


@dataclass
class StabilityFactors:
    """Aggregated factors affecting boundary stability."""

    ctcf_strength: float  # 0.0-1.0: CTCF site strength
    energy_barrier: float  # 0.0-1.0: Combined non-B DNA barrier strength
    epigenetic_context: float  # 0.0-1.0: Methylation/histone modifications
    te_motif_effect: float  # -1.0 to +1.0: TE motif stabilization/destruction
    temporal_factor: float  # 0.0-1.0: Temporal order factor
    # v1.1: NIPBL-WAPL Dynamics
    nipbl_velocity_factor: float = 1.0  # 0.0-2.0: NIPBL velocity multiplier (processivity rate)
    wapl_lifetime_factor: float = 1.0  # 0.0-2.0: WAPL lifetime multiplier (processivity duration)


class FactorAggregator:
    """
    Aggregate stability factors from different ARCHCODE modules.

    Collects data from:
    - archcode_core: CTCF sites
    - nonB_logic: Energy barriers
    - epigenetic_compiler: Methylation
    - te_grammar: TE motifs
    - Temporal dynamics: Order of events
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize factor aggregator.

        Args:
            config: Configuration from boundary_stability.yaml
        """
        self.config = config
        self.factor_weights = config.get("factor_weights", {})

    def aggregate_from_ctcf(
        self, ctcf_site_strength: float, position: int
    ) -> float:
        """
        Get CTCF strength factor.

        Args:
            ctcf_site_strength: CTCF site strength from archcode_core
            position: Genomic position

        Returns:
            CTCF strength factor (0.0-1.0)
        """
        # Normalize CTCF strength
        return min(1.0, max(0.0, ctcf_site_strength))

    def aggregate_from_energy_barriers(
        self, barrier_strengths: list[float], position: int
    ) -> float:
        """
        Aggregate energy barrier factors from nonB_logic.

        Args:
            barrier_strengths: List of barrier strengths (G4, Z-DNA, R-loops)
            position: Genomic position

        Returns:
            Combined energy barrier factor (0.0-1.0)
        """
        if not barrier_strengths:
            return 0.0

        # Combine barriers (additive or max, configurable)
        combination_mode = self.config.get("barrier_combination", "additive")
        if combination_mode == "additive":
            combined = sum(barrier_strengths)
        elif combination_mode == "max":
            combined = max(barrier_strengths)
        else:
            combined = sum(barrier_strengths)  # Default

        # Normalize to 0.0-1.0
        return min(1.0, combined)

    def aggregate_from_epigenetics(
        self, methylation_level: float, histone_modifications: float | None = None
    ) -> float:
        """
        Aggregate epigenetic context factor.

        Args:
            methylation_level: CpG methylation level (0.0-1.0)
            histone_modifications: Histone modification score (0.0-1.0) or None

        Returns:
            Epigenetic context factor (0.0-1.0)
        """
        # Methylation reduces stability (inverse relationship)
        methylation_factor = 1.0 - methylation_level

        # Histone modifications enhance stability
        histone_factor = histone_modifications if histone_modifications else 1.0

        # Combined epigenetic context
        return (methylation_factor * 0.6 + histone_factor * 0.4)

    def aggregate_from_te_motifs(
        self, motif_effects: list[float], position: int
    ) -> float:
        """
        Aggregate TE motif effects.

        Args:
            motif_effects: List of motif effects (-1.0 to +1.0)
            position: Genomic position

        Returns:
            Combined TE motif effect (-1.0 to +1.0)
        """
        if not motif_effects:
            return 0.0

        # Sum motif effects (can be positive or negative)
        combined = sum(motif_effects)

        # Clamp to valid range
        return max(-1.0, min(1.0, combined))

    def calculate_temporal_factor(
        self, event_order: int, total_events: int
    ) -> float:
        """
        Calculate temporal factor based on event order.

        Early events → higher stability
        Late events → lower stability

        Args:
            event_order: Order of this event (1 = first, N = last)
            total_events: Total number of events

        Returns:
            Temporal factor (0.0-1.0)
        """
        if total_events == 0:
            return 1.0

        # Early events get higher factor
        # Linear decay: first event = 1.0, last event = 0.5
        normalized_order = (event_order - 1) / max(1, total_events - 1)
        return 1.0 - (normalized_order * 0.5)

    def aggregate_all_factors(
        self,
        ctcf_strength: float,
        barrier_strengths: list[float],
        methylation_level: float,
        te_motif_effects: list[float],
        event_order: int = 1,
        total_events: int = 1,
        histone_modifications: float | None = None,
        nipbl_velocity_factor: float = 1.0,  # v1.1: NIPBL velocity multiplier
        wapl_lifetime_factor: float = 1.0,  # v1.1: WAPL lifetime multiplier
    ) -> StabilityFactors:
        """
        Aggregate all stability factors.

        Args:
            ctcf_strength: CTCF site strength
            barrier_strengths: List of energy barrier strengths
            methylation_level: CpG methylation level
            te_motif_effects: List of TE motif effects
            event_order: Order of this event
            total_events: Total number of events
            histone_modifications: Histone modification score (optional)

        Returns:
            Aggregated StabilityFactors
        """
        return StabilityFactors(
            ctcf_strength=self.aggregate_from_ctcf(ctcf_strength, 0),
            energy_barrier=self.aggregate_from_energy_barriers(
                barrier_strengths, 0
            ),
            epigenetic_context=self.aggregate_from_epigenetics(
                methylation_level, histone_modifications
            ),
            te_motif_effect=self.aggregate_from_te_motifs(
                te_motif_effects, 0
            ),
            temporal_factor=self.calculate_temporal_factor(
                event_order, total_events
            ),
            nipbl_velocity_factor=nipbl_velocity_factor,  # v1.1
            wapl_lifetime_factor=wapl_lifetime_factor,  # v1.1
        )

