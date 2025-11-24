"""Example: Using Boundary Stability Predictor."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from src.boundary_stability import StabilityCalculator


def main() -> None:
    """Example usage of boundary stability predictor."""
    # Load configuration
    config_path = Path("config/boundary_stability.yaml")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Initialize calculator
    calculator = StabilityCalculator(config)

    # Example 1: Stable boundary
    # High CTCF, strong barriers, low methylation, positive TE motifs, early event
    print("=" * 60)
    print("Example 1: Stable Boundary")
    print("=" * 60)
    prediction1 = calculator.calculate_stability(
        position=100000,
        ctcf_strength=0.9,
        barrier_strengths=[0.5, 0.3],  # G4 + Z-DNA barriers
        methylation_level=0.1,  # Low methylation
        te_motif_effects=[0.2, 0.1],  # Positive TE motifs
        event_order=1,  # Early event
        total_events=10,
    )
    print(f"Position: {prediction1.position}")
    print(f"Stability Score: {prediction1.stability_score:.3f}")
    print(f"Category: {prediction1.stability_category}")
    print(f"Confidence: {prediction1.confidence:.3f}")

    # Example 2: Variable boundary
    # Low CTCF, weak barriers, high methylation, negative TE motifs, late event
    print("\n" + "=" * 60)
    print("Example 2: Variable Boundary")
    print("=" * 60)
    prediction2 = calculator.calculate_stability(
        position=200000,
        ctcf_strength=0.3,
        barrier_strengths=[0.1],  # Weak barriers
        methylation_level=0.8,  # High methylation
        te_motif_effects=[-0.3],  # Negative TE motifs (WAPL-recruiting)
        event_order=9,  # Late event
        total_events=10,
    )
    print(f"Position: {prediction2.position}")
    print(f"Stability Score: {prediction2.stability_score:.3f}")
    print(f"Category: {prediction2.stability_category}")
    print(f"Confidence: {prediction2.confidence:.3f}")

    # Example 3: Batch prediction
    print("\n" + "=" * 60)
    print("Example 3: Batch Prediction")
    print("=" * 60)
    positions = [300000, 400000, 500000]
    ctcf_strengths = [0.7, 0.5, 0.4]
    barrier_strengths_list = [[0.3, 0.2], [0.2], [0.1]]
    methylation_levels = [0.3, 0.6, 0.7]

    predictions = calculator.calculate_batch(
        positions=positions,
        ctcf_strengths=ctcf_strengths,
        barrier_strengths_list=barrier_strengths_list,
        methylation_levels=methylation_levels,
    )

    for pred in predictions:
        print(
            f"Pos {pred.position}: {pred.stability_score:.3f} "
            f"({pred.stability_category}, conf={pred.confidence:.3f})"
        )

    print("\n" + "=" * 60)
    print("✅ Boundary Stability Predictor Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

