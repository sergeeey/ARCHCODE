"""ARCHCODE Core Pipeline - Integrated analysis pipeline."""

from pathlib import Path
from typing import Optional

import yaml

from src.archcode_core.bookmarking import adjust_barrier_for_phase, reset_barriers_to_baseline
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.extrusion_engine import Boundary, LoopExtrusionEngine
from src.boundary_stability import StabilityCalculator


class ARCHCODEPipeline:
    """
    Integrated ARCHCODE analysis pipeline.

    Pipeline flow:
    Sequence → Feature Extraction → TE Grammar → Non-B Logic →
    Epigenetic Compiler → Boundary Stability → Output
    """

    def __init__(
        self,
        archcode_config: dict,
        stability_config: dict | None = None,
        vizir_configs: dict | None = None,  # v1.1: For NIPBL-WAPL dynamics
    ) -> None:
        """
        Initialize ARCHCODE pipeline.

        Args:
            archcode_config: Configuration for archcode_core
            stability_config: Configuration for boundary_stability (optional)
        """
        self.archcode_config = archcode_config
        self.stability_config = stability_config

        # Initialize core engine
        self.extrusion_engine = LoopExtrusionEngine(archcode_config)

        # Store vizir_configs for passing to components
        self.vizir_configs = vizir_configs or {}
        
        # Initialize stability calculator if config provided
        # v1.1: Pass vizir_configs for NIPBL-WAPL dynamics
        self.stability_calculator: StabilityCalculator | None = None
        if stability_config:
            self.stability_calculator = StabilityCalculator(stability_config, vizir_configs=self.vizir_configs)

        # Pipeline state
        self.boundaries: list[Boundary] = []
        self.stability_predictions: list = []

    def add_boundary(
        self,
        position: int,
        strength: float,
        barrier_type: str = "ctcf",
        insulation_score: float = 0.0,
    ) -> Boundary:
        """
        Add boundary to pipeline.

        Args:
            position: Genomic position
            strength: Boundary strength
            barrier_type: Type of barrier
            insulation_score: Insulation score

        Returns:
            Created Boundary object
        """
        boundary = Boundary(
            position=position,
            strength=strength,
            barrier_type=barrier_type,
            insulation_score=insulation_score,
        )
        self.boundaries.append(boundary)
        self.extrusion_engine.boundaries.append(boundary)
        return boundary

    def analyze_boundary_stability(
        self,
        boundary: Boundary,
        barrier_strengths: list[float] | None = None,
        methylation_level: float = 0.0,
        te_motif_effects: list[float] | None = None,
        event_order: int = 1,
        total_events: int | None = None,
        nipbl_velocity_factor: float | None = None,  # v1.1: Override velocity
        wapl_lifetime_factor: float | None = None,  # v1.1: Override lifetime
    ) -> object | None:
        """
        Analyze stability for a single boundary.

        Args:
            boundary: Boundary to analyze
            barrier_strengths: Energy barrier strengths (optional)
            methylation_level: CpG methylation level
            te_motif_effects: TE motif effects (optional)
            event_order: Order of this event
            total_events: Total number of events (defaults to len(boundaries))

        Returns:
            StabilityPrediction if calculator available, None otherwise
        """
        if not self.stability_calculator:
            return None

        if total_events is None:
            total_events = len(self.boundaries)

        prediction = self.stability_calculator.calculate_stability(
            position=boundary.position,
            ctcf_strength=boundary.strength,
            barrier_strengths=barrier_strengths or [],
            methylation_level=methylation_level,
            te_motif_effects=te_motif_effects or [],
            event_order=event_order,
            total_events=total_events,
            nipbl_velocity_factor=nipbl_velocity_factor,  # v1.1: Pass override
            wapl_lifetime_factor=wapl_lifetime_factor,  # v1.1: Pass override
        )

        self.stability_predictions.append(prediction)
        return prediction

    def analyze_all_boundaries(
        self,
        barrier_strengths_map: dict[int, list[float]] | None = None,
        methylation_map: dict[int, float] | None = None,
        te_motif_map: dict[int, list[float]] | None = None,
        nipbl_velocity_factor: float | None = None,  # v1.1: Direct override
        wapl_lifetime_factor: float | None = None,  # v1.1: Direct override
        cell_cycle_phase: Optional[CellCyclePhase] = None,  # RS-10: Cell cycle phase
        enable_bookmarking: bool = True,  # RS-10: Enable bookmarking
    ) -> list:
        """
        Analyze stability for all boundaries.

        Args:
            barrier_strengths_map: Map of position -> barrier strengths
            methylation_map: Map of position -> methylation level
            te_motif_map: Map of position -> TE motif effects

        Returns:
            List of StabilityPredictions
        """
        if not self.stability_calculator:
            return []

        predictions = []
        for i, boundary in enumerate(self.boundaries):
            barrier_strengths = (
                barrier_strengths_map.get(boundary.position, [])
                if barrier_strengths_map
                else []
            )
            methylation_level = (
                methylation_map.get(boundary.position, 0.0)
                if methylation_map
                else 0.0
            )
            te_motif_effects = (
                te_motif_map.get(boundary.position, [])
                if te_motif_map
                else []
            )

            # v1.1: Use direct override if provided, otherwise extract from config
            nipbl_velocity_override = nipbl_velocity_factor
            wapl_lifetime_override = wapl_lifetime_factor
            
            # If not provided directly, extract from VIZIR configs
            if nipbl_velocity_override is None and "P3" in self.vizir_configs:
                p3_params = self.vizir_configs["P3"].get("parameters", {})
                if "nipbl_velocity_multiplier" in p3_params:
                    multipliers = p3_params["nipbl_velocity_multiplier"]
                    # Priority: wild_type for WT, cdls_haploinsufficient for CdLS
                    if "wild_type" in multipliers:
                        nipbl_velocity_override = multipliers["wild_type"]
                    elif "cdls_haploinsufficient" in multipliers:
                        nipbl_velocity_override = multipliers["cdls_haploinsufficient"]
            
            if wapl_lifetime_override is None and "S2" in self.vizir_configs:
                s2_params = self.vizir_configs["S2"].get("parameters", {})
                if "wapl_lifetime_factor" in s2_params:
                    factors = s2_params["wapl_lifetime_factor"]
                    if "wild_type" in factors:
                        wapl_lifetime_override = factors["wild_type"]
            
            prediction = self.analyze_boundary_stability(
                boundary=boundary,
                barrier_strengths=barrier_strengths,
                methylation_level=methylation_level,
                te_motif_effects=te_motif_effects,
                event_order=i + 1,
                total_events=len(self.boundaries),
                nipbl_velocity_factor=nipbl_velocity_override,  # v1.1: Pass velocity override
                wapl_lifetime_factor=wapl_lifetime_override,  # v1.1: Pass lifetime override
            )

            if prediction:
                predictions.append(prediction)

        return predictions

    def get_stable_boundaries(self, threshold: float = 0.7) -> list[Boundary]:
        """
        Get boundaries predicted as stable.

        Args:
            threshold: Stability threshold (default 0.7)

        Returns:
            List of stable boundaries
        """
        stable = []
        for i, boundary in enumerate(self.boundaries):
            if i < len(self.stability_predictions):
                pred = self.stability_predictions[i]
                if pred.stability_score >= threshold:
                    stable.append(boundary)
        return stable

    def get_variable_boundaries(self, threshold: float = 0.4) -> list[Boundary]:
        """
        Get boundaries predicted as variable.

        Args:
            threshold: Stability threshold (default 0.4)

        Returns:
            List of variable boundaries
        """
        variable = []
        for i, boundary in enumerate(self.boundaries):
            if i < len(self.stability_predictions):
                pred = self.stability_predictions[i]
                if pred.stability_score <= threshold:
                    variable.append(boundary)
        return variable

    def run_extrusion_simulation(
        self, time_steps: int = 100, time_step_size: float = 1.0
    ) -> None:
        """
        Run loop extrusion simulation.

        Args:
            time_steps: Number of time steps
            time_step_size: Size of each time step
        """
        for _ in range(time_steps):
            self.extrusion_engine.update_extrusion(time_step_size)

    def detect_tads(self) -> list[tuple[int, int]]:
        """
        Detect TAD boundaries from current state.

        Returns:
            List of (start, end) TAD positions
        """
        return self.extrusion_engine.detect_tads()

    def get_pipeline_summary(self) -> dict:
        """
        Get summary of pipeline state.

        Returns:
            Dictionary with pipeline summary
        """
        summary = {
            "total_boundaries": len(self.boundaries),
            "extrusion_events": len(self.extrusion_engine.extrusion_events),
            "current_time": self.extrusion_engine.current_time,
        }

        if self.stability_predictions:
            stable_count = sum(
                1 for p in self.stability_predictions if p.stability_score >= 0.7
            )
            variable_count = sum(
                1 for p in self.stability_predictions if p.stability_score <= 0.4
            )
            intermediate_count = len(self.stability_predictions) - stable_count - variable_count

            summary.update(
                {
                    "stability_predictions": len(self.stability_predictions),
                    "stable_boundaries": stable_count,
                    "variable_boundaries": variable_count,
                    "intermediate_boundaries": intermediate_count,
                    "avg_stability_score": sum(
                        p.stability_score for p in self.stability_predictions
                    )
                    / len(self.stability_predictions),
                }
            )

        return summary


def load_pipeline_configs() -> tuple[dict, dict]:
    """
    Load pipeline configurations.

    Returns:
        Tuple of (archcode_config, stability_config)
    """
    archcode_path = Path("config/archcode_engine.yaml")
    stability_path = Path("config/boundary_stability.yaml")

    with open(archcode_path, encoding="utf-8") as f:
        archcode_config = yaml.safe_load(f)

    stability_config = None
    if stability_path.exists():
        with open(stability_path, encoding="utf-8") as f:
            stability_config = yaml.safe_load(f)

    return archcode_config, stability_config
