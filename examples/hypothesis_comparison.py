"""Example: Compare hypotheses using VIZIR configs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs
from src.vizir.config_loader import VIZIRConfigLoader


def compare_hypotheses() -> None:
    """Compare different hypotheses for Engineering Unknowns."""
    print("=" * 60)
    print("VIZIR Hypothesis Comparison Example")
    print("=" * 60)

    # Initialize config loader
    loader = VIZIRConfigLoader()

    # Load P1 (Extrusion Symmetry) hypotheses
    print("\n1. Comparing P1 (Extrusion Symmetry) hypotheses...")
    p1_config = loader.load_physical("P1")

    hypothesis_a = loader.load_hypothesis("P1", "hypothesis_a", "physical")
    hypothesis_b = loader.load_hypothesis("P1", "hypothesis_b", "physical")

    print(f"\n   Hypothesis A: {hypothesis_a['name']}")
    print(f"   Description: {hypothesis_a['description']}")
    print(f"   Parameters: {hypothesis_a['parameters']}")

    print(f"\n   Hypothesis B: {hypothesis_b['name']}")
    print(f"   Description: {hypothesis_b['description']}")
    print(f"   Parameters: {hypothesis_b['parameters']}")

    # Load L1 (Z-DNA Formation) hypotheses
    print("\n2. Comparing L1 (Z-DNA Formation) hypotheses...")
    l1_config = loader.load_logical("L1")

    hypothesis_a_l1 = loader.load_hypothesis("L1", "hypothesis_a", "logical")
    hypothesis_b_l1 = loader.load_hypothesis("L1", "hypothesis_b", "logical")

    print(f"\n   Hypothesis A: {hypothesis_a_l1['name']}")
    print(f"   Description: {hypothesis_a_l1['description']}")

    print(f"\n   Hypothesis B: {hypothesis_b_l1['name']}")
    print(f"   Description: {hypothesis_b_l1['description']}")

    # Example: Run simulation with different hypotheses
    print("\n3. Running simulation with Hypothesis A...")

    # Load base configs
    archcode_config, stability_config = load_pipeline_configs()

    # Create config with Hypothesis A
    vizir_configs_a = {
        "P1": p1_config,
        "L1": l1_config,
    }
    # Override with hypothesis A parameters
    vizir_configs_a["P1"]["parameters"].update(hypothesis_a["parameters"])
    vizir_configs_a["L1"]["parameters"].update(hypothesis_a_l1["parameters"])

    pipeline_a = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    # Add test boundary
    pipeline_a.add_boundary(position=100000, strength=0.8, barrier_type="ctcf")

    # Analyze with Hypothesis A
    prediction_a = pipeline_a.analyze_boundary_stability(
        boundary=pipeline_a.boundaries[0],
        methylation_level=0.3,
    )

    print(f"   Result: {prediction_a.stability_category} (score={prediction_a.stability_score:.3f})")

    # Run with Hypothesis B
    print("\n4. Running simulation with Hypothesis B...")

    vizir_configs_b = {
        "P1": p1_config,
        "L1": l1_config,
    }
    vizir_configs_b["P1"]["parameters"].update(hypothesis_b["parameters"])
    vizir_configs_b["L1"]["parameters"].update(hypothesis_b_l1["parameters"])

    pipeline_b = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    pipeline_b.add_boundary(position=100000, strength=0.8, barrier_type="ctcf")

    prediction_b = pipeline_b.analyze_boundary_stability(
        boundary=pipeline_b.boundaries[0],
        methylation_level=0.3,
    )

    print(f"   Result: {prediction_b.stability_category} (score={prediction_b.stability_score:.3f})")

    # Compare results
    print("\n5. Comparison:")
    print(f"   Hypothesis A score: {prediction_a.stability_score:.3f}")
    print(f"   Hypothesis B score: {prediction_b.stability_score:.3f}")
    print(f"   Difference: {abs(prediction_a.stability_score - prediction_b.stability_score):.3f}")

    print("\n" + "=" * 60)
    print("✅ Hypothesis Comparison Complete")
    print("=" * 60)


if __name__ == "__main__":
    compare_hypotheses()










