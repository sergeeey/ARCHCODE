"""Example: Using VIZIR configs in ARCHCODE pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs
from src.vizir.config_loader import VIZIRConfigLoader


def main() -> None:
    """Example of VIZIR config integration."""
    print("=" * 60)
    print("VIZIR Config Integration Example")
    print("=" * 60)

    # Initialize VIZIR config loader
    loader = VIZIRConfigLoader()

    # Load all Engineering Unknowns
    print("\n1. Loading Engineering Unknowns...")
    physical_configs = loader.load_all_physical()
    structural_configs = loader.load_all_structural()
    logical_configs = loader.load_all_logical()

    print(f"   Physical: {list(physical_configs.keys())}")
    print(f"   Structural: {list(structural_configs.keys())}")
    print(f"   Logical: {list(logical_configs.keys())}")

    # Load specific unknown
    print("\n2. Loading P1 (Extrusion Symmetry)...")
    p1 = loader.load_physical("P1")
    print(f"   Unknown ID: {p1['unknown_id']}")
    print(f"   Uncertainty: {p1['uncertainty']}")
    print(f"   Impact: {p1['impact_on_model']}")
    print(f"   Priority: {p1['priority']}")

    # Get integration info
    print("\n3. Integration information:")
    integration = loader.get_integration_path("P1", "physical")
    print(f"   Module: {integration.get('archcode_core', {}).get('module')}")
    print(f"   Parameter path: {integration.get('archcode_core', {}).get('parameter_path')}")

    # Load hypothesis
    print("\n4. Loading Hypothesis A for P1...")
    hypothesis_a = loader.load_hypothesis("P1", "hypothesis_a", "physical")
    print(f"   Name: {hypothesis_a['name']}")
    print(f"   Description: {hypothesis_a['description']}")

    # Use in pipeline
    print("\n5. Using VIZIR configs in ARCHCODE pipeline...")
    archcode_config, stability_config = load_pipeline_configs()

    # Combine all VIZIR configs
    vizir_configs = {
        **physical_configs,
        **structural_configs,
        **logical_configs,
    }

    # Create pipeline (would use vizir_configs if integrated)
    pipeline = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    # Add boundaries
    pipeline.add_boundary(position=100000, strength=0.9, barrier_type="ctcf")
    pipeline.add_boundary(position=200000, strength=0.7, barrier_type="ctcf")

    print(f"   Added {len(pipeline.boundaries)} boundaries")

    # Show VIZIR config summary
    print("\n6. VIZIR Config Summary:")
    for unknown_id, config in vizir_configs.items():
        print(f"   {unknown_id}: {config.get('description', '')[:50]}...")

    print("\n" + "=" * 60)
    print("✅ VIZIR Integration Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()







