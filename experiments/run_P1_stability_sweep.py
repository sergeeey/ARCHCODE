"""Experiment E-P1-S1-01: P1 Hypothesis Impact on Boundary Stability."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.base_experiment import BaseExperiment, ExperimentResult
from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs


class P1StabilitySweep(BaseExperiment):
    """
    Experiment: Compare P1 hypotheses impact on boundary stability.

    Tests:
    - Hypothesis A: Transcription-driven asymmetry
    - Hypothesis B: NIPBL site selection

    Metrics:
    - Distribution of stability scores
    - Number of stable/variable boundaries
    - Average stability score
    """

    def __init__(self) -> None:
        """Initialize experiment."""
        super().__init__("E-P1-S1-01")

    def run(self) -> ExperimentResult:
        """Run experiment."""
        print("=" * 60)
        print(f"Experiment: {self.experiment_id}")
        print("=" * 60)

        # Load base configs
        archcode_config, stability_config = load_pipeline_configs()

        # Test boundaries
        boundaries_data = [
            (100000, 0.9, "ctcf"),
            (200000, 0.7, "ctcf"),
            (300000, 0.5, "ctcf"),
            (400000, 0.3, "ctcf"),
            (500000, 0.8, "ctcf"),
        ]

        results = {}

        # Test Hypothesis A
        print("\n1. Testing Hypothesis A (Transcription-driven)...")
        self.load_hypothesis_profile("P1", "hypothesis_a", "physical")
        self.profiles["P1"] = "hypothesis_a"

        pipeline_a = ARCHCODEPipeline(
            archcode_config=archcode_config,
            stability_config=stability_config,
        )

        for pos, strength, btype in boundaries_data:
            pipeline_a.add_boundary(position=pos, strength=strength, barrier_type=btype)

        # Analyze stability
        predictions_a = pipeline_a.analyze_all_boundaries(
            methylation_map={pos: 0.3 for pos, _, _ in boundaries_data},
        )

        stable_count_a = sum(1 for p in predictions_a if p.stability_score >= 0.7)
        variable_count_a = sum(1 for p in predictions_a if p.stability_score <= 0.4)
        avg_stability_a = sum(p.stability_score for p in predictions_a) / len(
            predictions_a
        )

        results["hypothesis_a"] = {
            "stable_count": stable_count_a,
            "variable_count": variable_count_a,
            "avg_stability": avg_stability_a,
            "stability_scores": [p.stability_score for p in predictions_a],
        }

        print(f"   Stable: {stable_count_a}, Variable: {variable_count_a}")
        print(f"   Avg stability: {avg_stability_a:.3f}")

        # Test Hypothesis B
        print("\n2. Testing Hypothesis B (NIPBL site selection)...")
        self.load_hypothesis_profile("P1", "hypothesis_b", "physical")
        self.profiles["P1"] = "hypothesis_b"

        pipeline_b = ARCHCODEPipeline(
            archcode_config=archcode_config,
            stability_config=stability_config,
        )

        for pos, strength, btype in boundaries_data:
            pipeline_b.add_boundary(position=pos, strength=strength, barrier_type=btype)

        predictions_b = pipeline_b.analyze_all_boundaries(
            methylation_map={pos: 0.3 for pos, _, _ in boundaries_data},
        )

        stable_count_b = sum(1 for p in predictions_b if p.stability_score >= 0.7)
        variable_count_b = sum(1 for p in predictions_b if p.stability_score <= 0.4)
        avg_stability_b = sum(p.stability_score for p in predictions_b) / len(
            predictions_b
        )

        results["hypothesis_b"] = {
            "stable_count": stable_count_b,
            "variable_count": variable_count_b,
            "avg_stability": avg_stability_b,
            "stability_scores": [p.stability_score for p in predictions_b],
        }

        print(f"   Stable: {stable_count_b}, Variable: {variable_count_b}")
        print(f"   Avg stability: {avg_stability_b:.3f}")

        # Comparison
        print("\n3. Comparison:")
        print(
            f"   Stability difference: {abs(avg_stability_a - avg_stability_b):.3f}"
        )
        print(
            f"   Stable count difference: {abs(stable_count_a - stable_count_b)}"
        )

        # Record run
        config_hash = self.record_experiment_run()

        # Create result
        result = ExperimentResult(
            experiment_id=self.experiment_id,
            timestamp=datetime.now().isoformat(),
            profiles=self.profiles,
            hypotheses=self.hypotheses,
            metrics=results,
            config_hash=config_hash,
        )

        # Save result
        result_path = self.save_result(result)
        print(f"\n✅ Result saved to: {result_path}")

        return result


if __name__ == "__main__":
    experiment = P1StabilitySweep()
    result = experiment.run()

