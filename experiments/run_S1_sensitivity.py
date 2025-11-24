"""Experiment E-S1-01: S1 Stability Threshold Sensitivity Analysis."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime

from experiments.base_experiment import BaseExperiment, ExperimentResult
from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs


class S1SensitivityAnalysis(BaseExperiment):
    """
    Experiment: Sensitivity analysis of S1 stability thresholds.

    Tests different threshold values:
    - stable_threshold: [0.6, 0.65, 0.7, 0.75, 0.8]
    - variable_threshold: [0.3, 0.35, 0.4, 0.45, 0.5]

    Metrics:
    - Number of boundaries in each category
    - Threshold sensitivity
    """

    def __init__(self) -> None:
        """Initialize experiment."""
        super().__init__("E-S1-01")

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
            (600000, 0.6, "ctcf"),
            (700000, 0.4, "ctcf"),
        ]

        # Test different threshold combinations
        stable_thresholds = [0.6, 0.65, 0.7, 0.75, 0.8]
        variable_thresholds = [0.3, 0.35, 0.4, 0.45, 0.5]

        results = {}

        for stable_thresh in stable_thresholds:
            for variable_thresh in variable_thresholds:
                if variable_thresh >= stable_thresh:
                    continue  # Skip invalid combinations

                # Update config
                test_config = stability_config.copy()
                test_config["stable_threshold"] = stable_thresh
                test_config["variable_threshold"] = variable_thresh

                # Create pipeline
                pipeline = ARCHCODEPipeline(
                    archcode_config=archcode_config,
                    stability_config=test_config,
                )

                for pos, strength, btype in boundaries_data:
                    pipeline.add_boundary(
                        position=pos, strength=strength, barrier_type=btype
                    )

                # Analyze
                predictions = pipeline.analyze_all_boundaries(
                    methylation_map={pos: 0.3 for pos, _, _ in boundaries_data},
                )

                stable_count = sum(
                    1 for p in predictions if p.stability_score >= stable_thresh
                )
                variable_count = sum(
                    1 for p in predictions if p.stability_score <= variable_thresh
                )
                intermediate_count = len(predictions) - stable_count - variable_count

                key = f"stable_{stable_thresh}_var_{variable_thresh}"
                results[key] = {
                    "stable_threshold": stable_thresh,
                    "variable_threshold": variable_thresh,
                    "stable_count": stable_count,
                    "variable_count": variable_count,
                    "intermediate_count": intermediate_count,
                    "distribution": {
                        "stable": stable_count / len(predictions),
                        "variable": variable_count / len(predictions),
                        "intermediate": intermediate_count / len(predictions),
                    },
                }

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
        print(f"   Tested {len(results)} threshold combinations")

        return result


if __name__ == "__main__":
    experiment = S1SensitivityAnalysis()
    result = experiment.run()







