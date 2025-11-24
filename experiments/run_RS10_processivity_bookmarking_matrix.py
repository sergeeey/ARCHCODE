"""RS-10 Experiment B: Processivity × Bookmarking Matrix.

Систематический перебор параметров для построения фазовой диаграммы
восстановления архитектуры после митоза.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.boundary_collapse import EnhancerPromoterPair
from src.vizir.config_loader import VIZIRConfigLoader


def jaccard_index(set1: set, set2: set) -> float:
    """
    Calculate Jaccard index (intersection over union).

    Args:
        set1: First set
        set2: Second set

    Returns:
        Jaccard index (0.0-1.0)
    """
    if not set1 and not set2:
        return 1.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0


def assign_bookmarking(boundaries: list[Boundary], fraction: float, seed: int = 42) -> None:
    """
    Assign bookmarking status to boundaries based on fraction.

    Args:
        boundaries: List of boundaries
        fraction: Fraction of boundaries to mark as bookmarked (0.0-1.0)
        seed: Random seed for reproducibility
    """
    n = len(boundaries)
    k = int(n * fraction)

    # Deterministic: mark first k boundaries
    for i, boundary in enumerate(boundaries):
        boundary.is_bookmarked = i < k


class RS10ProcessivityBookmarkingMatrix:
    """
    RS-10 Experiment B: Processivity × Bookmarking Matrix.

    Systematic sweep across parameter space to build phase diagram
    of architectural recovery after mitosis.
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_matrix_experiment(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        collapse_events_map: dict[int, list[dict]],
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
        nipbl_range: list[float] | None = None,
        wapl_range: list[float] | None = None,
        bookmarking_fractions: list[float] | None = None,
    ) -> dict:
        """
        Запустить матричный эксперимент.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            collapse_events_map: Карта событий коллапса
            enhancer_promoter_pairs: Пары enhancer-promoter
            nipbl_range: Диапазон NIPBL velocity (default: [0.3, 0.6, 1.0, 1.3])
            wapl_range: Диапазон WAPL lifetime (default: [0.3, 0.6, 1.0, 1.3])
            bookmarking_fractions: Доли bookmarking (default: [0.0, 0.25, 0.5, 0.75, 1.0])

        Returns:
            Результаты матричного эксперимента
        """
        print("=" * 60)
        print("RS-10 Experiment B: Processivity × Bookmarking Matrix")
        print("=" * 60)

        # Default parameter ranges
        if nipbl_range is None:
            nipbl_range = [0.3, 0.6, 1.0, 1.3]
        if wapl_range is None:
            wapl_range = [0.3, 0.6, 1.0, 1.3]
        if bookmarking_fractions is None:
            bookmarking_fractions = [0.0, 0.25, 0.5, 0.75, 1.0]

        total_combinations = len(nipbl_range) * len(wapl_range) * len(bookmarking_fractions)
        print(f"\nParameter ranges:")
        print(f"  NIPBL velocity: {nipbl_range}")
        print(f"  WAPL lifetime:  {wapl_range}")
        print(f"  Bookmarking fractions: {bookmarking_fractions}")
        print(f"  Total combinations: {total_combinations}")

        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Baseline: Get stable boundaries before mitosis
        print("\n" + "=" * 60)
        print("Computing baseline (before mitosis)...")
        print("=" * 60)

        pipeline_baseline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        results_baseline = pipeline_baseline.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=1.0,  # WT baseline
            wapl_lifetime_factor=1.0,
        )

        baseline_summary = results_baseline["summary"]
        baseline_stability = baseline_summary.get("avg_stability_score", 0.0)

        # Extract stable boundary positions
        stable_boundaries_baseline = set()
        for pred in results_baseline.get("stability_predictions", []):
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_boundaries_baseline.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_boundaries_baseline.add(pred.position)

        print(f"  Baseline stability: {baseline_stability:.3f}")
        print(f"  Stable boundaries: {len(stable_boundaries_baseline)}")
        print(f"  Stable positions: {sorted(stable_boundaries_baseline)}")

        # Matrix sweep
        print("\n" + "=" * 60)
        print("Starting matrix sweep...")
        print("=" * 60)

        grid_results = []
        current = 0

        for nipbl_vel in nipbl_range:
            for wapl_life in wapl_range:
                processivity = nipbl_vel * wapl_life

                for bookmarking_frac in bookmarking_fractions:
                    current += 1
                    print(
                        f"\n[{current}/{total_combinations}] "
                        f"P={processivity:.2f} (NIPBL={nipbl_vel:.1f}×WAPL={wapl_life:.1f}), "
                        f"B={bookmarking_frac:.2f}"
                    )

                    try:
                        # Create fresh pipeline for this combination
                        pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)

                        # Add boundaries and assign bookmarking
                        for pos, strength, btype in boundaries_data:
                            boundary = pipeline.pipeline.add_boundary(
                                position=pos, strength=strength, barrier_type=btype
                            )
                            # Bookmarking will be assigned below

                        # Assign bookmarking fraction
                        assign_bookmarking(pipeline.pipeline.boundaries, bookmarking_frac)

                        # Step 1: Mitosis (collapse)
                        # Use low processivity for mitosis simulation
                        nipbl_mitosis = 0.3
                        wapl_mitosis = 0.3
                        processivity_mitosis = nipbl_mitosis * wapl_mitosis

                        # Analyze in mitosis phase
                        mitosis_predictions = pipeline.pipeline.analyze_all_boundaries(
                            barrier_strengths_map=barrier_strengths_map,
                            methylation_map=methylation_map,
                            te_motif_map=te_motif_map,
                            nipbl_velocity_factor=nipbl_mitosis,
                            wapl_lifetime_factor=wapl_mitosis,
                            cell_cycle_phase=CellCyclePhase.MITOSIS,
                            enable_bookmarking=True,
                        )

                        mitosis_stability = (
                            sum(
                                p.stability_score if hasattr(p, "stability_score") else 0.0
                                for p in mitosis_predictions
                            )
                            / len(mitosis_predictions)
                            if mitosis_predictions
                            else 0.0
                        )

                        # Step 2: G1 Early recovery
                        g1_early_predictions = pipeline.pipeline.analyze_all_boundaries(
                            barrier_strengths_map=barrier_strengths_map,
                            methylation_map=methylation_map,
                            te_motif_map=te_motif_map,
                            nipbl_velocity_factor=nipbl_vel,  # Restored processivity
                            wapl_lifetime_factor=wapl_life,
                            cell_cycle_phase=CellCyclePhase.G1_EARLY,
                            enable_bookmarking=True,
                        )

                        # Step 3: G1 Late recovery (final state)
                        g1_late_predictions = pipeline.pipeline.analyze_all_boundaries(
                            barrier_strengths_map=barrier_strengths_map,
                            methylation_map=methylation_map,
                            te_motif_map=te_motif_map,
                            nipbl_velocity_factor=nipbl_vel,
                            wapl_lifetime_factor=wapl_life,
                            cell_cycle_phase=CellCyclePhase.G1_LATE,
                            enable_bookmarking=True,
                        )

                        # Calculate metrics after recovery
                        if g1_late_predictions:
                            avg_stability_after = sum(
                                p.stability_score if hasattr(p, "stability_score") else 0.0
                                for p in g1_late_predictions
                            ) / len(g1_late_predictions)

                            stable_boundaries_after = set()
                            for pred in g1_late_predictions:
                                if isinstance(pred, dict):
                                    if pred.get("stability_category") == "stable":
                                        stable_boundaries_after.add(pred.get("position"))
                                elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                                    stable_boundaries_after.add(pred.position)

                            stable_count_after = len(stable_boundaries_after)
                            matched_stable = len(stable_boundaries_baseline & stable_boundaries_after)
                            jaccard_stable = jaccard_index(
                                stable_boundaries_baseline, stable_boundaries_after
                            )

                            # Calculate collapse events (simplified: count low stability)
                            collapse_events = sum(
                                1
                                for p in g1_late_predictions
                                if (p.stability_score if hasattr(p, "stability_score") else 0.0) < 0.4
                            )

                            # Calculate average risk (simplified: use stability as proxy)
                            # Note: Risk scoring would come from collapse simulator if integrated
                            avg_risk = 1.0 - avg_stability_after  # Inverse of stability as proxy

                        else:
                            avg_stability_after = 0.0
                            stable_count_after = 0
                            matched_stable = 0
                            jaccard_stable = 0.0
                            collapse_events = 0
                            avg_risk = 0.0

                        # Store result
                        grid_results.append(
                            {
                                "nipbl_velocity": nipbl_vel,
                                "wapl_lifetime": wapl_life,
                                "bookmarking_fraction": bookmarking_frac,
                                "processivity": processivity,
                                "metrics": {
                                    "avg_stability_after": avg_stability_after,
                                    "stable_boundaries_after": stable_count_after,
                                    "matched_stable": matched_stable,
                                    "jaccard_stable": jaccard_stable,
                                    "collapse_events": collapse_events,
                                    "risk": avg_risk,
                                },
                            }
                        )

                        print(
                            f"  → Stability: {avg_stability_after:.3f}, "
                            f"Matched: {matched_stable}/{len(stable_boundaries_baseline)}, "
                            f"Jaccard: {jaccard_stable:.3f}"
                        )

                    except Exception as e:
                        print(f"  ⚠ Error: {e}")
                        # Store error state
                        grid_results.append(
                            {
                                "nipbl_velocity": nipbl_vel,
                                "wapl_lifetime": wapl_life,
                                "bookmarking_fraction": bookmarking_frac,
                                "processivity": processivity,
                                "error": str(e),
                            }
                        )

        # Build final results
        results = {
            "experiment_id": "RS-10-ExpB",
            "parameter_ranges": {
                "nipbl_range": nipbl_range,
                "wapl_range": wapl_range,
                "bookmarking_fractions": bookmarking_fractions,
                "total_combinations": total_combinations,
            },
            "baseline": {
                "avg_stability": baseline_stability,
                "stable_boundaries": len(stable_boundaries_baseline),
                "stable_positions": sorted(stable_boundaries_baseline),
            },
            "grid": grid_results,
        }

        return results

    def save_results(
        self, results: dict, filename: str = "RS10_processivity_bookmarking_matrix.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = RS10ProcessivityBookmarkingMatrix()

    # Test data (same as RS-09/RS-10-A for consistency)
    boundaries_data = [
        (100000, 0.9, "ctcf"),
        (200000, 0.8, "ctcf"),
        (300000, 0.7, "ctcf"),
        (400000, 0.6, "ctcf"),
        (500000, 0.9, "ctcf"),
    ]

    barrier_strengths_map = {
        100000: [0.1],
        200000: [0.2],
        300000: [0.6],
        400000: [0.8],
        500000: [0.1],
    }

    methylation_map = {
        100000: 0.1,
        200000: 0.2,
        300000: 0.7,
        400000: 0.9,
        500000: 0.3,
    }

    te_motif_map = {
        100000: [0.0],
        200000: [0.0],
        300000: [0.3],
        400000: [0.5],
        500000: [0.0],
    }

    collapse_events_map = {
        300000: [{"type": "methylation_spike", "delta": 0.4}],
        400000: [{"type": "ctcf_loss", "effect": 0.6}],
    }

    enhancer_promoter_pairs = [
        EnhancerPromoterPair(
            enhancer_position=300000,
            promoter_position=350000,
            gene_name="GENE_X",
            distance=50000,
            is_oncogenic=False,
        ),
        EnhancerPromoterPair(
            enhancer_position=400000,
            promoter_position=480000,
            gene_name="ONCOGENE_Y",
            distance=80000,
            is_oncogenic=True,
        ),
    ]

    # Run matrix experiment
    results = experiment.run_matrix_experiment(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        collapse_events_map=collapse_events_map,
        enhancer_promoter_pairs=enhancer_promoter_pairs,
    )

    # Save results
    output_path = experiment.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    successful_runs = [r for r in results["grid"] if "error" not in r]
    print(f"Successful runs: {len(successful_runs)}/{len(results['grid'])}")

    if successful_runs:
        jaccard_values = [r["metrics"]["jaccard_stable"] for r in successful_runs]
        stability_values = [r["metrics"]["avg_stability_after"] for r in successful_runs]
        print(f"Jaccard range: {min(jaccard_values):.3f} - {max(jaccard_values):.3f}")
        print(f"Stability range: {min(stability_values):.3f} - {max(stability_values):.3f}")

    print("\n" + "=" * 60)
    print("✅ RS-10 Experiment B Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- Matrix of processivity × bookmarking combinations")
    print("- Identification of recovery zones")
    print("- Critical thresholds for architectural memory")


if __name__ == "__main__":
    main()

