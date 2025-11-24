"""Stability Calculator - Main interface for boundary stability prediction."""

from src.boundary_stability.factor_aggregator import FactorAggregator, StabilityFactors
from src.boundary_stability.stability_model import StabilityModel, StabilityPrediction


class StabilityCalculator:
    """
    Main calculator for boundary stability prediction.

    Integrates factor aggregation and stability modeling.
    """

    def __init__(self, config: dict, vizir_configs: dict | None = None) -> None:
        """
        Initialize stability calculator.

        Args:
            config: Configuration from boundary_stability.yaml
            vizir_configs: Optional VIZIR P/S/L configs (for P3 velocity, S2 lifetime)
        """
        self.config = config
        self.vizir_configs = vizir_configs or {}
        self.aggregator = FactorAggregator(config)
        self.model = StabilityModel(config, vizir_configs=vizir_configs)
        
        # Extract NIPBL-WAPL factors from VIZIR configs
        self.default_nipbl_velocity = 1.0
        self.default_wapl_lifetime = 1.0
        self._extract_processivity_factors()
    
    def _extract_processivity_factors(self) -> None:
        """Extract NIPBL velocity and WAPL lifetime from VIZIR configs."""
        # P3: NIPBL velocity multiplier
        if "P3" in self.vizir_configs:
            p3_params = self.vizir_configs["P3"].get("parameters", {})
            if "nipbl_velocity_multiplier" in p3_params:
                multipliers = p3_params["nipbl_velocity_multiplier"]
                # ИСПРАВЛЕНИЕ: Приоритет wild_type, но если есть cdls_haploinsufficient и нет wild_type, используем его
                # Для CdLS эксперимента нужно явно указать использование cdls_haploinsufficient
                if "wild_type" in multipliers:
                    self.default_nipbl_velocity = multipliers["wild_type"]
                elif "cdls_haploinsufficient" in multipliers:
                    # Если wild_type нет, но есть cdls - используем cdls (для CdLS симуляции)
                    self.default_nipbl_velocity = multipliers["cdls_haploinsufficient"]
                else:
                    self.default_nipbl_velocity = 1.0
        
        # S2: WAPL lifetime factor (if available)
        if "S2" in self.vizir_configs:
            s2_params = self.vizir_configs["S2"].get("parameters", {})
            if "wapl_lifetime_factor" in s2_params:
                factors = s2_params["wapl_lifetime_factor"]
                self.default_wapl_lifetime = factors.get("wild_type", 1.0)

    def calculate_stability(
        self,
        position: int,
        ctcf_strength: float,
        barrier_strengths: list[float] | None = None,
        methylation_level: float = 0.0,
        te_motif_effects: list[float] | None = None,
        event_order: int = 1,
        total_events: int = 1,
        histone_modifications: float | None = None,
        nipbl_velocity_factor: float | None = None,  # v1.1: Override default
        wapl_lifetime_factor: float | None = None,  # v1.1: Override default
    ) -> StabilityPrediction:
        """
        Calculate boundary stability for a single position.

        Args:
            position: Genomic position
            ctcf_strength: CTCF site strength (0.0-1.0)
            barrier_strengths: List of energy barrier strengths (optional)
            methylation_level: CpG methylation level (0.0-1.0)
            te_motif_effects: List of TE motif effects (optional)
            event_order: Order of this event (1 = first)
            total_events: Total number of events
            histone_modifications: Histone modification score (optional)

        Returns:
            StabilityPrediction
        """
        # Default values
        if barrier_strengths is None:
            barrier_strengths = []
        if te_motif_effects is None:
            te_motif_effects = []

        # Use defaults if not provided
        nipbl_vel = nipbl_velocity_factor if nipbl_velocity_factor is not None else self.default_nipbl_velocity
        wapl_life = wapl_lifetime_factor if wapl_lifetime_factor is not None else self.default_wapl_lifetime
        
        # Aggregate factors (v1.1: includes processivity factors)
        factors = self.aggregator.aggregate_all_factors(
            ctcf_strength=ctcf_strength,
            barrier_strengths=barrier_strengths,
            methylation_level=methylation_level,
            te_motif_effects=te_motif_effects,
            event_order=event_order,
            total_events=total_events,
            histone_modifications=histone_modifications,
            nipbl_velocity_factor=nipbl_vel,
            wapl_lifetime_factor=wapl_life,
        )

        # Predict stability
        return self.model.predict(factors, position)

    def calculate_stability_from_factors(
        self, factors: StabilityFactors, position: int
    ) -> StabilityPrediction:
        """
        Calculate stability from pre-aggregated factors.

        Args:
            factors: Aggregated StabilityFactors
            position: Genomic position

        Returns:
            StabilityPrediction
        """
        return self.model.predict(factors, position)

    def calculate_batch(
        self,
        positions: list[int],
        ctcf_strengths: list[float],
        barrier_strengths_list: list[list[float]] | None = None,
        methylation_levels: list[float] | None = None,
        te_motif_effects_list: list[list[float]] | None = None,
        event_orders: list[int] | None = None,
        total_events: int = 1,
    ) -> list[StabilityPrediction]:
        """
        Calculate stability for multiple boundaries.

        Args:
            positions: List of genomic positions
            ctcf_strengths: List of CTCF strengths
            barrier_strengths_list: List of barrier strength lists (optional)
            methylation_levels: List of methylation levels (optional)
            te_motif_effects_list: List of TE motif effect lists (optional)
            event_orders: List of event orders (optional)
            total_events: Total number of events

        Returns:
            List of StabilityPredictions
        """
        if len(positions) != len(ctcf_strengths):
            raise ValueError("Positions and CTCF strengths must have same length")

        # Default values
        if barrier_strengths_list is None:
            barrier_strengths_list = [[]] * len(positions)
        if methylation_levels is None:
            methylation_levels = [0.0] * len(positions)
        if te_motif_effects_list is None:
            te_motif_effects_list = [[]] * len(positions)
        if event_orders is None:
            event_orders = list(range(1, len(positions) + 1))

        # Aggregate factors for all positions
        factors_list = []
        for i, _pos in enumerate(positions):
            factors = self.aggregator.aggregate_all_factors(
                ctcf_strength=ctcf_strengths[i],
                barrier_strengths=barrier_strengths_list[i],
                methylation_level=methylation_levels[i],
                te_motif_effects=te_motif_effects_list[i],
                event_order=event_orders[i],
                total_events=total_events,
            )
            factors_list.append(factors)

        # Predict for all
        return self.model.predict_batch(factors_list, positions)

