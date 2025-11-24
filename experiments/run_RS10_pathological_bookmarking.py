"""RS-10 Experiment C: Pathological Bookmarking Defects & Multi-Cycle Drift.

Симуляция многократных клеточных циклов с дефектами bookmarking.
Анализ деградации архитектурной памяти через N циклов.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.bookmarking import (
    apply_stochastic_recovery,
    calculate_drift_distance,
    calculate_entropy_of_positions,
)
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


def calculate_architecture_entropy(stable_before: set, stable_after: set) -> float:
    """
    Calculate architecture entropy (measure of "drift").

    Entropy = 1 - Jaccard_index
    Higher entropy = more architectural drift.

    Args:
        stable_before: Stable boundaries before
        stable_after: Stable boundaries after

    Returns:
        Entropy (0.0-1.0)
    """
    jaccard = jaccard_index(stable_before, stable_after)
    return 1.0 - jaccard


def assign_bookmarking(boundaries: list[Boundary], fraction: float) -> None:
    """
    Assign bookmarking status to boundaries based on fraction.

    Args:
        boundaries: List of boundaries
        fraction: Fraction of boundaries to mark as bookmarked (0.0-1.0)
    """
    n = len(boundaries)
    k = int(n * fraction)

    # Deterministic: mark first k boundaries
    for i, boundary in enumerate(boundaries):
        boundary.is_bookmarked = i < k


def simulate_single_cycle(
    pipeline: ARCHCODEFullPipeline,
    boundaries_data: list[tuple[int, float, str]],
    barrier_strengths_map: dict[int, list[float]],
    methylation_map: dict[int, float],
    te_motif_map: dict[int, list[float]],
    bookmarking_fraction: float,
    nipbl_velocity: float,
    wapl_lifetime: float,
    boundary_loss_rate: float = 0.2,
    boundary_shift_std: float = 15000.0,
    cycle_number: int = 0,
) -> dict:
    """
    Симулировать один клеточный цикл: Mitosis → G1_EARLY → G1_LATE.

    Args:
        pipeline: ARCHCODE pipeline
        boundaries_data: Границы
        barrier_strengths_map: Карта барьеров
        methylation_map: Карта метилирования
        te_motif_map: Карта TE мотивов
        bookmarking_fraction: Доля bookmarking
        nipbl_velocity: NIPBL velocity
        wapl_lifetime: WAPL lifetime

    Returns:
        Метрики после цикла
    """
    # Assign bookmarking
    assign_bookmarking(pipeline.pipeline.boundaries, bookmarking_fraction)

    # Mitosis: Low processivity
    nipbl_mitosis = 0.3
    wapl_mitosis = 0.3

    mitosis_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_mitosis,
        wapl_lifetime_factor=wapl_mitosis,
        cell_cycle_phase=CellCyclePhase.MITOSIS,
        enable_bookmarking=True,
    )

    # G1 Early recovery
    g1_early_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_velocity,
        wapl_lifetime_factor=wapl_lifetime,
        cell_cycle_phase=CellCyclePhase.G1_EARLY,
        enable_bookmarking=True,
    )

    # Store original boundaries for drift calculation
    boundaries_before = [b for b in pipeline.pipeline.boundaries]

    # Apply stochastic recovery for non-bookmarked boundaries
    recovered_boundaries = apply_stochastic_recovery(
        boundaries_before,
        boundary_loss_rate=boundary_loss_rate,
        boundary_shift_std=boundary_shift_std,
        seed=cycle_number,  # Deterministic per cycle
    )

    # Update pipeline boundaries
    pipeline.pipeline.boundaries = recovered_boundaries

    # G1 Late recovery (final state) - after stochastic recovery
    g1_late_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_velocity,
        wapl_lifetime_factor=wapl_lifetime,
        cell_cycle_phase=CellCyclePhase.G1_LATE,
        enable_bookmarking=True,
    )

    # Calculate metrics
    if g1_late_predictions:
        avg_stability = sum(
            p.stability_score if hasattr(p, "stability_score") else 0.0
            for p in g1_late_predictions
        ) / len(g1_late_predictions)

        stable_boundaries = set()
        for pred in g1_late_predictions:
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_boundaries.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_boundaries.add(pred.position)

        stable_count = len(stable_boundaries)
    else:
        avg_stability = 0.0
        stable_boundaries = set()
        stable_count = 0

    # Calculate additional metrics
    entropy = calculate_entropy_of_positions(recovered_boundaries)
    drift_distance = calculate_drift_distance(boundaries_before, recovered_boundaries)

    return {
        "avg_stability": avg_stability,
        "stable_boundaries": stable_boundaries,
        "stable_count": stable_count,
        "entropy": entropy,
        "drift_distance": drift_distance,
        "recovered_boundaries": recovered_boundaries,
    }


class RS10PathologicalBookmarking:
    """
    RS-10 Experiment C: Pathological Bookmarking Defects & Multi-Cycle Drift.

    Симулирует многократные клеточные циклы с дефектами bookmarking.
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def simulate_multiple_cycles(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        bookmarking_fraction: float,
        nipbl_velocity: float,
        wapl_lifetime: float,
        num_cycles: int = 10,
        boundary_loss_rate: float = 0.2,
        boundary_shift_std: float = 15000.0,
    ) -> dict:
        """
        Симулировать N клеточных циклов.

        Args:
            boundaries_data: Границы
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            bookmarking_fraction: Доля bookmarking
            nipbl_velocity: NIPBL velocity
            wapl_lifetime: WAPL lifetime
            num_cycles: Количество циклов
            boundary_loss_rate: Вероятность потери non-bookmarked границ
            boundary_shift_std: Стандартное отклонение для сдвига позиций (bp)

        Returns:
            Результаты всех циклов
        """
        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Initial baseline (before any cycles)
        pipeline_baseline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        baseline_results = pipeline_baseline.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=None,
            enhancer_promoter_pairs=None,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
        )

        # Extract baseline stable boundaries
        stable_baseline_original = set()
        for pred in baseline_results.get("stability_predictions", []):
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_baseline_original.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_baseline_original.add(pred.position)

        # Simulate cycles
        cycles_results = []
        stable_previous = stable_baseline_original.copy()

        for cycle in range(num_cycles):
            # Create fresh pipeline for this cycle
            pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)

            # Add boundaries
            for pos, strength, btype in boundaries_data:
                pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

            # Simulate cycle
            cycle_metrics = simulate_single_cycle(
                pipeline=pipeline,
                boundaries_data=boundaries_data,
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                bookmarking_fraction=bookmarking_fraction,
                nipbl_velocity=nipbl_velocity,
                wapl_lifetime=wapl_lifetime,
                boundary_loss_rate=boundary_loss_rate,
                boundary_shift_std=boundary_shift_std,
                cycle_number=cycle,
            )

            stable_current = cycle_metrics["stable_boundaries"]

            # Calculate metrics
            jaccard_vs_baseline = jaccard_index(stable_baseline_original, stable_current)
            jaccard_vs_previous = jaccard_index(stable_previous, stable_current)
            matched_stable = len(stable_baseline_original & stable_current)
            architecture_entropy = calculate_architecture_entropy(
                stable_baseline_original, stable_current
            )

            # Calculate memory retention score
            memory_retention_score = jaccard_vs_baseline * (1.0 - architecture_entropy)

            cycle_result = {
                "cycle": cycle + 1,
                "avg_stability": cycle_metrics["avg_stability"],
                "stable_count": cycle_metrics["stable_count"],
                "jaccard_vs_baseline": jaccard_vs_baseline,
                "jaccard_vs_previous": jaccard_vs_previous,
                "matched_stable": matched_stable,
                "entropy": architecture_entropy,
                "position_entropy": cycle_metrics.get("entropy", 0.0),
                "drift_distance": cycle_metrics.get("drift_distance", 0.0),
                "memory_retention_score": memory_retention_score,
            }

            cycles_results.append(cycle_result)

            # Update previous for next cycle
            # Use recovered boundaries for next cycle baseline
            stable_previous = stable_current.copy()

            # Update boundaries_data for next cycle (positions may have shifted)
            if cycle_metrics.get("recovered_boundaries"):
                boundaries_data = [
                    (b.position, b.strength, b.barrier_type)
                    for b in cycle_metrics["recovered_boundaries"]
                ]

            print(
                f"  Cycle {cycle + 1}/{num_cycles}: "
                f"Jaccard={jaccard_vs_baseline:.3f}, "
                f"Stability={cycle_metrics['avg_stability']:.3f}, "
                f"Drift={jaccard_vs_previous:.3f}"
            )

        # Calculate summary
        final_jaccard = cycles_results[-1]["jaccard_vs_baseline"]
        total_drift = 1.0 - final_jaccard

        # Find cycle where collapse occurs (Jaccard < 0.3)
        cycles_to_collapse = None
        for cycle_result in cycles_results:
            if cycle_result["jaccard_vs_baseline"] < 0.3:
                cycles_to_collapse = cycle_result["cycle"]
                break

        # Determine stability trend
        if len(cycles_results) >= 2:
            first_stability = cycles_results[0]["avg_stability"]
            last_stability = cycles_results[-1]["avg_stability"]
            if last_stability > first_stability * 1.05:
                stability_trend = "increasing"
            elif last_stability < first_stability * 0.95:
                stability_trend = "decreasing"
            else:
                stability_trend = "stable"
        else:
            stability_trend = "unknown"

        summary = {
            "final_jaccard": final_jaccard,
            "total_drift": total_drift,
            "cycles_to_collapse": cycles_to_collapse,
            "stability_trend": stability_trend,
            "initial_stability": cycles_results[0]["avg_stability"],
            "final_stability": cycles_results[-1]["avg_stability"],
        }

        # Add baseline cycle (cycle 0)
        baseline_cycle = {
            "cycle": 0,
            "avg_stability": baseline_results["summary"].get("avg_stability_score", 0.0),
            "stable_count": len(stable_baseline_original),
            "jaccard_vs_baseline": 1.0,
            "jaccard_vs_previous": 1.0,
            "matched_stable": len(stable_baseline_original),
            "entropy": 0.0,
            "position_entropy": 0.0,
            "drift_distance": 0.0,
            "memory_retention_score": 1.0,
        }

        return {
            "cycles": [baseline_cycle] + cycles_results,
            "summary": summary,
            "baseline_stable": sorted(stable_baseline_original),
        }

    def run_pathological_scenarios(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        num_cycles: int = 10,
    ) -> dict:
        """
        Запустить все патологические сценарии.

        Args:
            boundaries_data: Границы
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            num_cycles: Количество циклов

        Returns:
            Результаты всех сценариев
        """
        print("=" * 60)
        print("RS-10 Experiment C: Pathological Bookmarking Defects")
        print("=" * 60)

        scenarios = []

        # Scenario 1: Complete Bookmarking Loss
        print("\n" + "=" * 60)
        print("Scenario 1: Complete Bookmarking Loss (0.0)")
        print("=" * 60)
        print(f"  Bookmarking: 0.0, Processivity: 1.0, Cycles: {num_cycles}")

        scenario1 = self.simulate_multiple_cycles(
            boundaries_data=boundaries_data.copy(),
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            bookmarking_fraction=0.0,
            nipbl_velocity=1.0,
            wapl_lifetime=1.0,
            num_cycles=num_cycles,
            boundary_loss_rate=0.2,
            boundary_shift_std=15000.0,
        )

        scenarios.append(
            {
                "scenario_name": "complete_loss",
                "bookmarking_fraction": 0.0,
                "processivity": 1.0,
                "num_cycles": num_cycles,
                **scenario1,
            }
        )

        # Scenario 2: Partial Bookmarking Defect
        print("\n" + "=" * 60)
        print("Scenario 2: Partial Bookmarking Defect (0.3)")
        print("=" * 60)
        print(f"  Bookmarking: 0.3, Processivity: 1.0, Cycles: {num_cycles}")

        scenario2 = self.simulate_multiple_cycles(
            boundaries_data=boundaries_data.copy(),
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            bookmarking_fraction=0.3,
            nipbl_velocity=1.0,
            wapl_lifetime=1.0,
            num_cycles=num_cycles,
            boundary_loss_rate=0.2,
            boundary_shift_std=15000.0,
        )

        scenarios.append(
            {
                "scenario_name": "partial_defect",
                "bookmarking_fraction": 0.3,
                "processivity": 1.0,
                "num_cycles": num_cycles,
                **scenario2,
            }
        )

        # Scenario 3: Critical Threshold Sweep
        print("\n" + "=" * 60)
        print("Scenario 3: Critical Threshold Sweep")
        print("=" * 60)

        bookmarking_sweep = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        for bookmarking_frac in bookmarking_sweep:
            print(f"\n  Testing bookmarking fraction: {bookmarking_frac:.1f}")

            scenario_sweep = self.simulate_multiple_cycles(
                boundaries_data=boundaries_data.copy(),
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                bookmarking_fraction=bookmarking_frac,
                nipbl_velocity=1.0,
                wapl_lifetime=1.0,
                num_cycles=num_cycles,
                boundary_loss_rate=0.2,
                boundary_shift_std=15000.0,
            )

            scenarios.append(
                {
                    "scenario_name": f"threshold_sweep_{bookmarking_frac:.1f}",
                    "bookmarking_fraction": bookmarking_frac,
                    "processivity": 1.0,
                    "num_cycles": num_cycles,
                    **scenario_sweep,
                }
            )

        # Scenario 4: Processivity Compensation
        print("\n" + "=" * 60)
        print("Scenario 4: Processivity Compensation")
        print("=" * 60)
        print("  Bookmarking: 0.3 (defect), Testing processivity compensation")

        processivity_levels = [0.5, 0.7, 1.0, 1.3]
        for processivity in processivity_levels:
            # Calculate NIPBL and WAPL for this processivity
            # Assume balanced: NIPBL = WAPL = sqrt(processivity)
            nipbl = wapl = processivity**0.5

            print(f"\n  Testing processivity: {processivity:.2f} (NIPBL={nipbl:.2f}, WAPL={wapl:.2f})")

            scenario_comp = self.simulate_multiple_cycles(
                boundaries_data=boundaries_data.copy(),
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                bookmarking_fraction=0.3,
                nipbl_velocity=nipbl,
                wapl_lifetime=wapl,
                num_cycles=num_cycles,
                boundary_loss_rate=0.2,
                boundary_shift_std=15000.0,
            )

            scenarios.append(
                {
                    "scenario_name": f"compensation_p{processivity:.2f}",
                    "bookmarking_fraction": 0.3,
                    "processivity": processivity,
                    "num_cycles": num_cycles,
                    **scenario_comp,
                }
            )

        return {"experiment_id": "RS-10-ExpC", "scenarios": scenarios}

    def save_results(
        self, results: dict, filename: str = "RS10_pathological_bookmarking.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = RS10PathologicalBookmarking()

    # Test data (same as RS-09/RS-10 for consistency)
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

    # Run all scenarios
    results = experiment.run_pathological_scenarios(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        num_cycles=10,
    )

    # Save results
    output_path = experiment.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for scenario in results["scenarios"]:
        summary = scenario["summary"]
        print(f"\n{scenario['scenario_name']}:")
        print(f"  Final Jaccard: {summary['final_jaccard']:.3f}")
        print(f"  Total Drift: {summary['total_drift']:.3f}")
        print(f"  Cycles to Collapse: {summary['cycles_to_collapse']}")
        print(f"  Stability Trend: {summary['stability_trend']}")

    print("\n" + "=" * 60)
    print("✅ RS-10 Experiment C Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- Complete loss: Architecture drifts completely")
    print("- Partial defect: Gradual degradation")
    print("- Threshold sweep: Critical bookmarking level identified")
    print("- Compensation: High processivity can compensate low bookmarking")


if __name__ == "__main__":
    main()

