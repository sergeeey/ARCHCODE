"""
ARCHCODE Regression Test Suite - Level 2 Validation.

Runs RS-09, RS-10, and RS-11 experiments multiple times to ensure stability.
Checks for hidden bugs and parameter sensitivity.
"""

import json
import statistics
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.bookmarking import assign_bookmarking, apply_stochastic_recovery
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.memory_metrics import (
    calculate_jaccard_stable_boundaries,
    get_stable_boundaries,
)
from src.vizir.config_loader import VIZIRConfigLoader


class RegressionTestSuite:
    """Regression test suite for ARCHCODE experiments."""

    def __init__(self, num_iterations: int = 20, output_dir: Path | None = None):
        """
        Initialize regression test suite.

        Args:
            num_iterations: Number of iterations per experiment
            output_dir: Output directory for results
        """
        self.num_iterations = num_iterations
        self.output_dir = output_dir or Path("data/output/regression")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load VIZIR configs
        loader = VIZIRConfigLoader()
        self.vizir_configs = {
            **loader.load_all_physical(),
            **loader.load_all_structural(),
            **loader.load_all_logical(),
        }

        # Test boundaries (chr8:127000000-130000000 region)
        self.boundaries_data = [
            (127100000, 0.8, "ctcf"),
            (127200000, 0.7, "ctcf"),
            (127300000, 0.6, "ctcf"),
            (127400000, 0.5, "ctcf"),
            (127500000, 0.9, "ctcf"),
        ]

        self.barrier_strengths_map = {pos: [0.5] for pos, _, _ in self.boundaries_data}
        self.methylation_map = {pos: 0.5 for pos, _, _ in self.boundaries_data}
        self.te_motif_map = {pos: [0.0] for pos, _, _ in self.boundaries_data}

    def run_RS09_regression(self) -> dict[str, Any]:
        """
        Run RS-09 (Processivity) regression test.

        Tests stability across multiple runs with same parameters.
        """
        print("\n" + "=" * 80)
        print("RS-09 Regression Test: Processivity Stability")
        print("=" * 80)

        results = {
            "experiment": "RS-09",
            "num_iterations": self.num_iterations,
            "parameters": {
                "processivity": 1.0,
                "nipbl_velocity": 1.0,
                "wapl_lifetime": 1.0,
            },
            "iterations": [],
            "statistics": {},
        }

        stability_scores = []
        insulation_scores = []
        drift_distances = []
        jaccard_scores = []

        for iteration in range(self.num_iterations):
            print(f"\n[{iteration + 1}/{self.num_iterations}] RS-09 iteration...")

            # Create fresh pipeline
            pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

            # Add boundaries
            for pos, strength, btype in self.boundaries_data:
                pipeline.pipeline.add_boundary(
                    position=pos, strength=strength, barrier_type=btype
                )

            # Run analysis
            predictions = pipeline.pipeline.analyze_all_boundaries(
                barrier_strengths_map=self.barrier_strengths_map,
                methylation_map=self.methylation_map,
                te_motif_map=self.te_motif_map,
                nipbl_velocity_factor=1.0,
                wapl_lifetime_factor=1.0,
                cell_cycle_phase=CellCyclePhase.INTERPHASE,
                enable_bookmarking=False,
            )

            # Extract metrics
            if predictions:
                avg_stability = sum(
                    p.stability_score if hasattr(p, "stability_score") else 0.0
                    for p in predictions
                ) / len(predictions)

                stable_boundaries = get_stable_boundaries(
                    pipeline.pipeline.boundaries, stability_threshold=0.7
                )
                jaccard = 1.0 if stable_boundaries else 0.0

                stability_scores.append(avg_stability)
                jaccard_scores.append(jaccard)

                # Calculate insulation (simplified)
                avg_insulation = sum(
                    b.insulation_score for b in pipeline.pipeline.boundaries
                ) / len(pipeline.pipeline.boundaries)
                insulation_scores.append(avg_insulation)

                results["iterations"].append({
                    "iteration": iteration,
                    "avg_stability": avg_stability,
                    "insulation_score": avg_insulation,
                    "jaccard": jaccard,
                    "stable_count": len(stable_boundaries),
                })
            else:
                stability_scores.append(0.0)
                insulation_scores.append(0.0)
                jaccard_scores.append(0.0)

        # Calculate statistics
        results["statistics"] = {
            "stability": {
                "mean": statistics.mean(stability_scores),
                "std": statistics.stdev(stability_scores) if len(stability_scores) > 1 else 0.0,
                "cv": (statistics.stdev(stability_scores) / statistics.mean(stability_scores))
                if statistics.mean(stability_scores) > 0
                else 0.0,
            },
            "insulation": {
                "mean": statistics.mean(insulation_scores),
                "std": statistics.stdev(insulation_scores) if len(insulation_scores) > 1 else 0.0,
                "cv": (statistics.stdev(insulation_scores) / statistics.mean(insulation_scores))
                if statistics.mean(insulation_scores) > 0
                else 0.0,
            },
            "jaccard": {
                "mean": statistics.mean(jaccard_scores),
                "std": statistics.stdev(jaccard_scores) if len(jaccard_scores) > 1 else 0.0,
            },
        }

        # Check pass/fail criteria
        stability_cv = results["statistics"]["stability"]["cv"]
        insulation_cv = results["statistics"]["insulation"]["cv"]

        results["passed"] = stability_cv < 0.10 and insulation_cv < 0.10

        print(f"\n✅ RS-09 Regression Results:")
        print(f"   Stability CV: {stability_cv:.3f} ({'PASS' if stability_cv < 0.10 else 'FAIL'})")
        print(f"   Insulation CV: {insulation_cv:.3f} ({'PASS' if insulation_cv < 0.10 else 'FAIL'})")

        return results

    def run_RS10_regression(self) -> dict[str, Any]:
        """
        Run RS-10 (Bookmarking) regression test.

        Tests critical threshold stability at bookmarking = 0.3, 0.4, 0.5.
        """
        print("\n" + "=" * 80)
        print("RS-10 Regression Test: Bookmarking Threshold Stability")
        print("=" * 80)

        results = {
            "experiment": "RS-10",
            "num_iterations": self.num_iterations,
            "bookmarking_fractions": [0.3, 0.4, 0.5],
            "results": {},
        }

        for bookmarking_frac in results["bookmarking_fractions"]:
            print(f"\n--- Testing bookmarking = {bookmarking_frac} ---")

            jaccard_scores = []
            memory_scores = []

            for iteration in range(self.num_iterations):
                # Create fresh pipeline
                pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

                # Add boundaries
                for pos, strength, btype in self.boundaries_data:
                    pipeline.pipeline.add_boundary(
                        position=pos, strength=strength, barrier_type=btype
                    )

                # Assign bookmarking
                assign_bookmarking(pipeline.pipeline.boundaries, fraction=bookmarking_frac, seed=iteration)

                # Baseline
                baseline_stable = get_stable_boundaries(
                    pipeline.pipeline.boundaries, stability_threshold=0.7
                )

                # Simulate one cycle
                boundaries_before = [
                    Boundary(b.position, b.strength, b.barrier_type, b.insulation_score, b.is_bookmarked)
                    for b in pipeline.pipeline.boundaries
                ]

                # Mitosis
                mitosis_predictions = pipeline.pipeline.analyze_all_boundaries(
                    barrier_strengths_map=self.barrier_strengths_map,
                    methylation_map=self.methylation_map,
                    te_motif_map=self.te_motif_map,
                    nipbl_velocity_factor=0.3,
                    wapl_lifetime_factor=0.3,
                    cell_cycle_phase=CellCyclePhase.MITOSIS,
                    enable_bookmarking=True,
                )

                # Recovery
                recovered_boundaries = apply_stochastic_recovery(
                    boundaries_before,
                    boundary_loss_rate=0.2,
                    boundary_shift_std=15000.0,
                    seed=iteration,
                )

                pipeline.pipeline.boundaries = recovered_boundaries

                # G1 Late
                g1_late_predictions = pipeline.pipeline.analyze_all_boundaries(
                    barrier_strengths_map=self.barrier_strengths_map,
                    methylation_map=self.methylation_map,
                    te_motif_map=self.te_motif_map,
                    nipbl_velocity_factor=1.0,
                    wapl_lifetime_factor=1.0,
                    cell_cycle_phase=CellCyclePhase.G1_LATE,
                    enable_bookmarking=True,
                )

                # Calculate metrics
                final_stable = get_stable_boundaries(
                    recovered_boundaries, stability_threshold=0.7
                )
                jaccard = calculate_jaccard_stable_boundaries(
                    baseline_stable, final_stable
                )
                jaccard_scores.append(jaccard)

                # Memory score (simplified)
                memory_score = jaccard * (1.0 - len(final_stable) / max(len(baseline_stable), 1))
                memory_scores.append(memory_score)

            # Statistics
            results["results"][f"bookmarking_{bookmarking_frac}"] = {
                "jaccard": {
                    "mean": statistics.mean(jaccard_scores),
                    "std": statistics.stdev(jaccard_scores) if len(jaccard_scores) > 1 else 0.0,
                    "cv": (statistics.stdev(jaccard_scores) / statistics.mean(jaccard_scores))
                    if statistics.mean(jaccard_scores) > 0
                    else 0.0,
                },
                "memory_score": {
                    "mean": statistics.mean(memory_scores),
                    "std": statistics.stdev(memory_scores) if len(memory_scores) > 1 else 0.0,
                },
            }

            jaccard_cv = results["results"][f"bookmarking_{bookmarking_frac}"]["jaccard"]["cv"]
            print(f"   Jaccard CV: {jaccard_cv:.3f} ({'PASS' if jaccard_cv < 0.10 else 'FAIL'})")

        # Check threshold stability
        jaccard_03 = results["results"]["bookmarking_0.3"]["jaccard"]["mean"]
        jaccard_04 = results["results"]["bookmarking_0.4"]["jaccard"]["mean"]
        jaccard_05 = results["results"]["bookmarking_0.5"]["jaccard"]["mean"]

        # Threshold should be between 0.3 and 0.4
        threshold_detected = jaccard_03 < 0.5 < jaccard_05
        results["threshold_detected"] = threshold_detected
        results["passed"] = threshold_detected and all(
            r["jaccard"]["cv"] < 0.10
            for r in results["results"].values()
        )

        print(f"\n✅ RS-10 Regression Results:")
        print(f"   Threshold detected: {threshold_detected} ({'PASS' if threshold_detected else 'FAIL'})")

        return results

    def run_RS11A_regression(self) -> dict[str, Any]:
        """
        Run RS-11A (Multichannel Memory) regression test.

        Tests epigenetic_strength = 0.0, 0.5, 1.0
        """
        print("\n" + "=" * 80)
        print("RS-11A Regression Test: Multichannel Memory Stability")
        print("=" * 80)

        results = {
            "experiment": "RS-11A",
            "num_iterations": self.num_iterations,
            "epigenetic_strengths": [0.0, 0.5, 1.0],
            "bookmarking_fraction": 0.4,  # Fixed
            "results": {},
        }

        from src.archcode_core.epigenetic_memory import (
            initialize_epigenetic_memory,
            restore_with_epigenetic_memory,
        )

        for epigenetic_str in results["epigenetic_strengths"]:
            print(f"\n--- Testing epigenetic_strength = {epigenetic_str} ---")

            jaccard_scores = []
            memory_scores = []

            for iteration in range(self.num_iterations):
                # Create fresh pipeline
                pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

                # Add boundaries
                for pos, strength, btype in self.boundaries_data:
                    pipeline.pipeline.add_boundary(
                        position=pos, strength=strength, barrier_type=btype
                    )

                # Initialize epigenetic memory
                epigenetic_scores = initialize_epigenetic_memory(
                    pipeline.pipeline.boundaries,
                    mode="correlated_with_strength",
                    strength=1.0,
                    seed=iteration,
                )

                # Baseline
                baseline_stable = get_stable_boundaries(
                    pipeline.pipeline.boundaries, stability_threshold=0.7
                )

                # Assign bookmarking
                assign_bookmarking(
                    pipeline.pipeline.boundaries,
                    fraction=results["bookmarking_fraction"],
                    seed=iteration,
                )

                # Simulate cycle with multichannel restoration
                boundaries_before = [
                    Boundary(b.position, b.strength, b.barrier_type, b.insulation_score, b.is_bookmarked)
                    for b in pipeline.pipeline.boundaries
                ]

                import random
                rng = random.Random(iteration)

                # Multichannel restoration
                restored_boundaries, _ = restore_with_epigenetic_memory(
                    boundaries_before,
                    epigenetic_scores,
                    rng=rng,
                    params={
                        "bookmarking_fraction": results["bookmarking_fraction"],
                        "epigenetic_strength": epigenetic_str,
                        "restoration_function": "linear",
                        "boundary_loss_rate": 0.2,
                        "boundary_shift_std": 15000.0,
                    },
                )

                # Calculate metrics
                final_stable = get_stable_boundaries(
                    restored_boundaries, stability_threshold=0.7
                )
                jaccard = calculate_jaccard_stable_boundaries(
                    baseline_stable, final_stable
                )
                jaccard_scores.append(jaccard)

                memory_score = jaccard * (1.0 - len(final_stable) / max(len(baseline_stable), 1))
                memory_scores.append(memory_score)

            # Statistics
            results["results"][f"epigenetic_{epigenetic_str}"] = {
                "jaccard": {
                    "mean": statistics.mean(jaccard_scores),
                    "std": statistics.stdev(jaccard_scores) if len(jaccard_scores) > 1 else 0.0,
                    "cv": (statistics.stdev(jaccard_scores) / statistics.mean(jaccard_scores))
                    if statistics.mean(jaccard_scores) > 0
                    else 0.0,
                },
                "memory_score": {
                    "mean": statistics.mean(memory_scores),
                    "std": statistics.stdev(memory_scores) if len(memory_scores) > 1 else 0.0,
                },
            }

            jaccard_cv = results["results"][f"epigenetic_{epigenetic_str}"]["jaccard"]["cv"]
            print(f"   Jaccard CV: {jaccard_cv:.3f} ({'PASS' if jaccard_cv < 0.10 else 'FAIL'})")

        # Check stability
        results["passed"] = all(
            r["jaccard"]["cv"] < 0.10 for r in results["results"].values()
        )

        print(f"\n✅ RS-11A Regression Results:")
        print(f"   All CVs < 0.10: {results['passed']} ({'PASS' if results['passed'] else 'FAIL'})")

        return results

    def run_all(self) -> dict[str, Any]:
        """Run all regression tests."""
        print("=" * 80)
        print("ARCHCODE REGRESSION TEST SUITE")
        print("=" * 80)
        print(f"Iterations per test: {self.num_iterations}")
        print(f"Output directory: {self.output_dir}")

        all_results = {
            "rs09": self.run_RS09_regression(),
            "rs10": self.run_RS10_regression(),
            "rs11a": self.run_RS11A_regression(),
        }

        # Overall status
        all_passed = all(r.get("passed", False) for r in all_results.values())
        all_results["overall_passed"] = all_passed

        # Save results
        output_file = self.output_dir / "regression_results.json"
        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2)

        print("\n" + "=" * 80)
        print("REGRESSION TEST SUITE COMPLETE")
        print("=" * 80)
        print(f"\n✅ Overall Status: {'PASS' if all_passed else 'FAIL'}")
        print(f"📄 Results saved to: {output_file}")

        return all_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ARCHCODE regression test suite")
    parser.add_argument(
        "--iterations",
        type=int,
        default=20,
        help="Number of iterations per test (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: data/output/regression)",
    )

    args = parser.parse_args()

    suite = RegressionTestSuite(
        num_iterations=args.iterations,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )

    results = suite.run_all()


