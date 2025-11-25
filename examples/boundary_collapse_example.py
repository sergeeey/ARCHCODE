"""Example: Boundary Collapse Simulation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from src.boundary_collapse import (
    BoundaryCollapseSimulator,
    CollapseScenarios,
    RiskScorer,
    BoundaryState,
)


def main() -> None:
    """Example of boundary collapse simulation."""
    print("=" * 60)
    print("Boundary Collapse Simulation Example")
    print("=" * 60)

    # Load configuration
    config_path = Path("config/boundary_collapse.yaml")
    with open(config_path, encoding="utf-8") as f:
        collapse_config = yaml.safe_load(f)

    # Initialize simulator
    simulator = BoundaryCollapseSimulator(collapse_config)
    risk_scorer = RiskScorer(collapse_config)

    # Example 1: Methylation-induced collapse
    print("\n1. Methylation-induced collapse...")
    boundary_state = BoundaryState(
        position=100000,
        ctcf_strength=0.8,
        methylation_level=0.2,
        stability_score=0.7,
        barrier_strengths=[],
        te_motif_effects=[],
    )

    result = simulator.run_collapse_scenario(
        boundary_id="chr1:100000",
        boundary_state=boundary_state,
        events=[{"type": "methylation_spike", "delta": 0.5}],
    )

    print(f"   Collapse probability: {result.collapse_probability:.3f}")
    print(f"   Collapse occurred: {result.collapse_occurred}")
    print(f"   Stability before: {result.stability_before:.3f}")
    print(f"   Stability after: {result.stability_after:.3f}")

    # Example 2: CTCF loss
    print("\n2. CTCF loss scenario...")
    boundary_state2 = BoundaryState(
        position=200000,
        ctcf_strength=0.9,
        methylation_level=0.1,
        stability_score=0.85,
        barrier_strengths=[],
        te_motif_effects=[],
    )

    result2 = simulator.run_collapse_scenario(
        boundary_id="chr1:200000",
        boundary_state=boundary_state2,
        events=[{"type": "ctcf_loss", "effect": "affinity_drop"}],
    )

    print(f"   Collapse probability: {result2.collapse_probability:.3f}")
    print(f"   Collapse occurred: {result2.collapse_occurred}")

    # Example 3: MYC-TERT oncogenic scenario
    print("\n3. MYC-TERT oncogenic scenario...")
    scenario = CollapseScenarios.myc_tert_scenario()
    boundary_state3 = CollapseScenarios.create_boundary_state(
        position=scenario["boundary_position"],
        ctcf_strength=0.7,
        methylation_level=0.3,
        stability_score=0.6,
    )

    result3 = simulator.run_collapse_scenario(
        boundary_id="chr8:128750000",
        boundary_state=boundary_state3,
        events=scenario["events"],
    )

    # Calculate risks
    result3 = risk_scorer.update_collapse_result_with_risks(
        result3, scenario["enhancer_promoter_pairs"]
    )

    print(f"   Collapse probability: {result3.collapse_probability:.3f}")
    print(f"   Enhancer hijacking risk: {result3.enhancer_hijacking_risk:.3f}")
    print(f"   Oncogenic risk: {result3.oncogenic_risk:.3f}")
    print(f"   Total risk score: {result3.total_risk_score:.3f}")

    print("\n" + "=" * 60)
    print("✅ Boundary Collapse Simulation Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()








