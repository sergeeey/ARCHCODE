"""Boundary Collapse Scenarios - Predefined collapse scenarios."""

from src.boundary_collapse.models import (
    BoundaryState,
    EnhancerPromoterPair,
)


class CollapseScenarios:
    """Predefined collapse scenarios for common cases."""

    @staticmethod
    def zrs_shh_scenario() -> dict:
        """
        ZRS/Shh enhancer hijacking scenario.

        Returns:
            Scenario configuration
        """
        return {
            "name": "ZRS/Shh Enhancer Hijacking",
            "description": "Methylation-induced collapse at ZRS enhancer boundary",
            "boundary_position": 155000000,  # Approximate ZRS position
            "events": [
                {"type": "methylation_spike", "delta": 0.5},
            ],
            "enhancer_promoter_pairs": [
                EnhancerPromoterPair(
                    enhancer_position=155000000,
                    promoter_position=155700000,
                    gene_name="SHH",
                    distance=700000,
                    is_oncogenic=False,
                ),
            ],
        }

    @staticmethod
    def auts2_scenario() -> dict:
        """
        AUTS2 boundary collapse scenario.

        Returns:
            Scenario configuration
        """
        return {
            "name": "AUTS2 Boundary Collapse",
            "description": "TE insertion causes AUTS2 boundary collapse",
            "boundary_position": 70000000,  # Approximate AUTS2 position
            "events": [
                {"type": "te_insertion", "wapl_recruiting": True},
            ],
            "enhancer_promoter_pairs": [],
        }

    @staticmethod
    def myc_tert_scenario() -> dict:
        """
        MYC-TERT oncogenic contact scenario.

        Returns:
            Scenario configuration
        """
        return {
            "name": "MYC-TERT Oncogenic Contact",
            "description": "Boundary collapse enables MYC enhancer → TERT contact",
            "boundary_position": 128750000,  # Between MYC and TERT
            "events": [
                {"type": "ctcf_loss", "effect": "affinity_drop"},
                {"type": "methylation_spike", "delta": 0.4},
            ],
            "enhancer_promoter_pairs": [
                EnhancerPromoterPair(
                    enhancer_position=128750000,
                    promoter_position=1253250,  # TERT promoter
                    gene_name="TERT",
                    distance=127496750,
                    is_oncogenic=True,
                ),
            ],
        }

    @staticmethod
    def create_boundary_state(
        position: int,
        ctcf_strength: float = 0.8,
        methylation_level: float = 0.2,
        stability_score: float = 0.7,
    ) -> BoundaryState:
        """
        Create boundary state for scenario.

        Args:
            position: Boundary position
            ctcf_strength: CTCF strength
            methylation_level: Methylation level
            stability_score: Stability score

        Returns:
            BoundaryState
        """
        return BoundaryState(
            position=position,
            ctcf_strength=ctcf_strength,
            methylation_level=methylation_level,
            stability_score=stability_score,
            barrier_strengths=[],
            te_motif_effects=[],
        )







