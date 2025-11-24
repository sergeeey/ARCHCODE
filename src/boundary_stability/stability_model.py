"""Stability Model - Multiplicative model for boundary stability prediction."""

from dataclasses import dataclass

from src.boundary_stability.factor_aggregator import StabilityFactors


@dataclass
class StabilityPrediction:
    """Stability prediction result."""

    position: int
    stability_score: float  # 0.0-1.0
    stability_category: str  # "stable", "variable", "intermediate"
    confidence: float  # 0.0-1.0: Prediction confidence


class StabilityModel:
    """
    Multiplicative stability model.

    Formula (v1.1):
        Stability = S_ctcf × (1 + E_barrier) × E_epi × (1 + M_te) × T_time × V_nipbl × L_wapl

    Where:
        - S_ctcf: CTCF strength (0.0-1.0)
        - E_barrier: Energy barrier strength (0.0-1.0)
        - E_epi: Epigenetic context (0.0-1.0)
        - M_te: TE motif effect (-1.0 to +1.0)
        - T_time: Temporal factor (0.0-1.0)
        - V_nipbl: NIPBL velocity factor (0.0-2.0) - v1.1: processivity rate
        - L_wapl: WAPL lifetime factor (0.0-2.0) - v1.1: processivity duration
    """

    def __init__(self, config: dict, vizir_configs: dict | None = None) -> None:
        """
        Initialize stability model.

        Args:
            config: Configuration from boundary_stability.yaml
            vizir_configs: Optional VIZIR S1 config
        """
        self.config = config
        self.stable_threshold = config.get("stable_threshold", 0.7)
        self.variable_threshold = config.get("variable_threshold", 0.4)
        self.barrier_multiplier = config.get("barrier_multiplier", 1.0)
        self.te_multiplier = config.get("te_multiplier", 1.0)
        
        # Load VIZIR configs if provided
        self.vizir_configs = vizir_configs or {}
        self._apply_vizir_configs()

    def _apply_vizir_configs(self) -> None:
        """Apply VIZIR Engineering Unknown configurations."""
        # S1: TAD Boundary Determinism
        if "S1" in self.vizir_configs:
            s1 = self.vizir_configs["S1"]
            params = s1.get("parameters", {})
            if "thresholds" in params:
                self.stable_threshold = params["thresholds"].get("stable_threshold", 0.7)
                self.variable_threshold = params["thresholds"].get("variable_threshold", 0.4)

    def predict(self, factors: StabilityFactors, position: int) -> StabilityPrediction:
        """
        Predict boundary stability from aggregated factors.

        Args:
            factors: Aggregated stability factors
            position: Genomic position

        Returns:
            StabilityPrediction with score and category
        """
        # Multiplicative model (v1.1: includes NIPBL-WAPL dynamics)
        # Processivity = Rate(NIPBL) × Lifetime(WAPL)
        base_stability = (
            factors.ctcf_strength
            * (1.0 + factors.energy_barrier * self.barrier_multiplier)
            * factors.epigenetic_context
            * (1.0 + factors.te_motif_effect * self.te_multiplier)
            * factors.temporal_factor
        )
        
        # v1.1: Apply processivity factors
        # Lower velocity or lifetime → lower stability (processivity effect)
        processivity_factor = factors.nipbl_velocity_factor * factors.wapl_lifetime_factor
        stability = base_stability * processivity_factor

        # Clamp to valid range
        stability = max(0.0, min(1.0, stability))

        # Categorize
        if stability >= self.stable_threshold:
            category = "stable"
        elif stability <= self.variable_threshold:
            category = "variable"
        else:
            category = "intermediate"

        # Calculate confidence based on how far from thresholds
        if category == "stable":
            confidence = min(1.0, (stability - self.stable_threshold) / (1.0 - self.stable_threshold))
        elif category == "variable":
            confidence = min(1.0, (self.variable_threshold - stability) / self.variable_threshold)
        else:
            # Intermediate: lower confidence
            distance_to_stable = abs(stability - self.stable_threshold)
            distance_to_variable = abs(stability - self.variable_threshold)
            min_distance = min(distance_to_stable, distance_to_variable)
            confidence = min(1.0, min_distance / 0.15)  # Normalize by threshold gap

        return StabilityPrediction(
            position=position,
            stability_score=stability,
            stability_category=category,
            confidence=confidence,
        )

    def predict_batch(
        self, factors_list: list[StabilityFactors], positions: list[int]
    ) -> list[StabilityPrediction]:
        """
        Predict stability for multiple boundaries.

        Args:
            factors_list: List of aggregated factors
            positions: List of genomic positions

        Returns:
            List of StabilityPredictions
        """
        if len(factors_list) != len(positions):
            raise ValueError("Factors and positions must have same length")

        return [
            self.predict(factors, pos)
            for factors, pos in zip(factors_list, positions, strict=True)
        ]

