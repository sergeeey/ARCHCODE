"""Example: ARCHCODE Pipeline Integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs


def main() -> None:
    """Example of integrated ARCHCODE pipeline."""
    print("=" * 60)
    print("ARCHCODE Pipeline Integration Example")
    print("=" * 60)

    # Load configurations
    archcode_config, stability_config = load_pipeline_configs()

    # Initialize pipeline
    pipeline = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    # Add boundaries (simulated TAD boundaries)
    print("\n1. Adding boundaries...")
    boundaries_data = [
        (100000, 0.9, "ctcf"),  # Strong CTCF
        (200000, 0.7, "ctcf"),  # Medium CTCF
        (300000, 0.5, "ctcf"),  # Weak CTCF
        (400000, 0.3, "ctcf"),  # Very weak CTCF
        (500000, 0.8, "ctcf"),  # Strong CTCF
    ]

    for pos, strength, btype in boundaries_data:
        pipeline.add_boundary(
            position=pos,
            strength=strength,
            barrier_type=btype,
            insulation_score=strength * 0.8,
        )
        print(f"  Added boundary at {pos}: strength={strength:.2f}")

    # Analyze stability for all boundaries
    print("\n2. Analyzing boundary stability...")

    # Simulate barrier strengths (from nonB_logic)
    barrier_strengths_map = {
        100000: [0.5, 0.3],  # G4 + Z-DNA barriers
        200000: [0.3],
        300000: [0.2],
        400000: [0.1],
        500000: [0.4, 0.2],
    }

    # Simulate methylation levels (from epigenetic_compiler)
    methylation_map = {
        100000: 0.1,  # Low methylation
        200000: 0.3,
        300000: 0.6,
        400000: 0.8,  # High methylation
        500000: 0.2,
    }

    # Simulate TE motif effects (from te_grammar)
    te_motif_map = {
        100000: [0.2, 0.1],  # Positive motifs
        200000: [0.1],
        300000: [0.0],
        400000: [-0.3],  # Negative motifs (WAPL-recruiting)
        500000: [0.15],
    }

    predictions = pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
    )

    # Display results
    print("\n3. Stability Predictions:")
    print("-" * 60)
    for pred in predictions:
        print(
            f"Position {pred.position:6d}: "
            f"Score={pred.stability_score:.3f} "
            f"({pred.stability_category:12s}) "
            f"Confidence={pred.confidence:.3f}"
        )

    # Get stable and variable boundaries
    print("\n4. Boundary Categories:")
    stable = pipeline.get_stable_boundaries()
    variable = pipeline.get_variable_boundaries()

    print(f"  Stable boundaries: {len(stable)}")
    for b in stable:
        print(f"    - Position {b.position}, strength={b.strength:.2f}")

    print(f"\n  Variable boundaries: {len(variable)}")
    for b in variable:
        print(f"    - Position {b.position}, strength={b.strength:.2f}")

    # Pipeline summary
    print("\n5. Pipeline Summary:")
    summary = pipeline.get_pipeline_summary()
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("✅ Pipeline Integration Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

