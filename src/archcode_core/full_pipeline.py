"""ARCHCODE Full Pipeline - Complete causal chain from extrusion to risk."""

from pathlib import Path
from typing import Any

import yaml

from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs
from src.boundary_collapse import (
    BoundaryCollapseSimulator,
    BoundaryState,
    RiskScorer,
)
from typing import Optional


class ARCHCODEFullPipeline:
    """
    Full ARCHCODE Pipeline: Extrusion → Stability → Collapse → Risk.

    Complete causal chain:
    1. Loop extrusion simulation
    2. Boundary stability prediction
    3. Collapse simulation (optional events)
    4. Risk scoring (hijacking, oncogenic)
    5. Output generation
    """

    def __init__(
        self,
        archcode_config: dict | None = None,
        stability_config: dict | None = None,
        collapse_config: dict | None = None,
        vizir_configs: dict | None = None,
    ) -> None:
        """
        Initialize full pipeline.

        Args:
            archcode_config: ARCHCODE core configuration
            stability_config: Boundary stability configuration
            collapse_config: Boundary collapse configuration
            vizir_configs: VIZIR P/S/L configs
        """
        # Load configs if not provided
        if archcode_config is None or stability_config is None:
            archcode_config, stability_config = load_pipeline_configs()

        if collapse_config is None:
            collapse_config_path = Path("config/boundary_collapse.yaml")
            if collapse_config_path.exists():
                with open(collapse_config_path, encoding="utf-8") as f:
                    collapse_config = yaml.safe_load(f)
            else:
                collapse_config = {}

        # Initialize components
        # v1.1: Pass vizir_configs for NIPBL-WAPL dynamics
        self.pipeline = ARCHCODEPipeline(
            archcode_config=archcode_config,
            stability_config=stability_config,
            vizir_configs=vizir_configs,
        )

        self.collapse_simulator = BoundaryCollapseSimulator(
            config=collapse_config, vizir_configs=vizir_configs
        )
        self.risk_scorer = RiskScorer(config=collapse_config)
        self.vizir_configs = vizir_configs or {}

    def run_full_analysis(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]] | None = None,
        methylation_map: dict[int, float] | None = None,
        te_motif_map: dict[int, list[float]] | None = None,
        collapse_events: dict[int, list[dict[str, Any]]] | None = None,
        enhancer_promoter_pairs: list | None = None,
        nipbl_velocity_factor: float | None = None,  # v1.1: Direct velocity override
        wapl_lifetime_factor: float | None = None,  # v1.1: Direct lifetime override
        cell_cycle_phase: Optional[CellCyclePhase] = None,  # RS-10: Cell cycle phase
        enable_bookmarking: bool = True,  # RS-10: Enable bookmarking
    ) -> dict[str, Any]:
        """
        Run full pipeline analysis.

        Args:
            boundaries_data: List of (position, strength, barrier_type)
            barrier_strengths_map: Map of position -> barrier strengths
            methylation_map: Map of position -> methylation level
            te_motif_map: Map of position -> TE motif effects
            collapse_events: Map of position -> collapse events
            enhancer_promoter_pairs: List of enhancer-promoter pairs

        Returns:
            Complete analysis results
        """
        # Stage 1: Add boundaries
        for pos, strength, btype in boundaries_data:
            self.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )

        # Stage 2: Analyze stability
        # v1.1: Pass velocity/lifetime overrides directly
        stability_predictions = self.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity_factor,
            wapl_lifetime_factor=wapl_lifetime_factor,
        )

        # Stage 3: Simulate collapse (if events provided)
        collapse_results = {}
        if collapse_events:
            for boundary in self.pipeline.boundaries:
                if boundary.position in collapse_events:
                    boundary_state = BoundaryState(
                        position=boundary.position,
                        ctcf_strength=boundary.strength,
                        methylation_level=methylation_map.get(
                            boundary.position, 0.0
                        )
                        if methylation_map
                        else 0.0,
                        stability_score=next(
                            (
                                p.stability_score
                                for p in stability_predictions
                                if p.position == boundary.position
                            ),
                            0.5,
                        ),
                        barrier_strengths=barrier_strengths_map.get(
                            boundary.position, []
                        )
                        if barrier_strengths_map
                        else [],
                        te_motif_effects=te_motif_map.get(boundary.position, [])
                        if te_motif_map
                        else [],
                    )

                    collapse_result = self.collapse_simulator.run_collapse_scenario(
                        boundary_id=f"chr1:{boundary.position}",
                        boundary_state=boundary_state,
                        events=collapse_events[boundary.position],
                    )

                    # Calculate risks if enhancer-promoter pairs provided
                    if enhancer_promoter_pairs:
                        collapse_result = (
                            self.risk_scorer.update_collapse_result_with_risks(
                                collapse_result, enhancer_promoter_pairs
                            )
                        )

                    collapse_results[boundary.position] = collapse_result

        # Compile results
        results = {
            "boundaries": [
                {
                    "position": b.position,
                    "strength": b.strength,
                    "barrier_type": b.barrier_type,
                }
                for b in self.pipeline.boundaries
            ],
            "stability_predictions": [
                {
                    "position": p.position,
                    "stability_score": p.stability_score,
                    "stability_category": p.stability_category,
                    "confidence": p.confidence,
                }
                for p in stability_predictions
            ],
            "collapse_results": {
                pos: {
                    "collapse_probability": r.collapse_probability,
                    "collapse_occurred": r.collapse_occurred,
                    "enhancer_hijacking_risk": r.enhancer_hijacking_risk,
                    "oncogenic_risk": r.oncogenic_risk,
                    "total_risk_score": r.total_risk_score,
                    "stability_before": r.stability_before,
                    "stability_after": r.stability_after,
                }
                for pos, r in collapse_results.items()
            },
            "summary": self._generate_summary(
                stability_predictions, collapse_results
            ),
        }

        return results

    def _generate_summary(
        self, stability_predictions: list, collapse_results: dict
    ) -> dict[str, Any]:
        """
        Generate summary statistics.

        Args:
            stability_predictions: List of stability predictions
            collapse_results: Dictionary of collapse results

        Returns:
            Summary dictionary
        """
        if not stability_predictions:
            return {}

        stable_count = sum(
            1 for p in stability_predictions if p.stability_score >= 0.7
        )
        variable_count = sum(
            1 for p in stability_predictions if p.stability_score <= 0.4
        )
        intermediate_count = len(stability_predictions) - stable_count - variable_count

        avg_stability = (
            sum(p.stability_score for p in stability_predictions)
            / len(stability_predictions)
        )

        collapse_count = sum(1 for r in collapse_results.values() if r.collapse_occurred)
        avg_collapse_prob = (
            sum(r.collapse_probability for r in collapse_results.values())
            / len(collapse_results)
            if collapse_results
            else 0.0
        )

        high_risk_count = sum(
            1
            for r in collapse_results.values()
            if r.total_risk_score >= 0.7
        )

        return {
            "total_boundaries": len(stability_predictions),
            "stable_boundaries": stable_count,
            "variable_boundaries": variable_count,
            "intermediate_boundaries": intermediate_count,
            "avg_stability_score": avg_stability,
            "collapsed_boundaries": collapse_count,
            "avg_collapse_probability": avg_collapse_prob,
            "high_risk_boundaries": high_risk_count,
        }

