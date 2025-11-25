"""RS-10 Bookmarking Threshold Analysis.

Детальный анализ порога bookmarking и проверка перколяционного перехода.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.run_RS10_pathological_bookmarking import (
    RS10PathologicalBookmarking,
)


class RS10BookmarkingThresholdAnalysis:
    """Analysis of bookmarking threshold."""

    def __init__(self) -> None:
        """Инициализация."""
        self.experiment = RS10PathologicalBookmarking()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_threshold_analysis(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        bookmarking_fractions: list[float] | None = None,
        num_cycles: int = 20,
    ) -> dict:
        """
        Запустить анализ порога bookmarking.

        Args:
            boundaries_data: Границы
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            bookmarking_fractions: Доли bookmarking для анализа
            num_cycles: Количество циклов

        Returns:
            Результаты анализа порога
        """
        print("=" * 60)
        print("RS-10 Bookmarking Threshold Analysis")
        print("=" * 60)

        if bookmarking_fractions is None:
            bookmarking_fractions = [
                0.1,
                0.15,
                0.2,
                0.25,
                0.3,
                0.35,
                0.4,
                0.45,
                0.5,
                0.6,
            ]

        results = []

        for bookmarking_frac in bookmarking_fractions:
            print(f"\nTesting bookmarking fraction: {bookmarking_frac:.2f}")

            # Run multi-cycle simulation
            scenario_result = self.experiment.simulate_multiple_cycles(
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

            cycles = scenario_result["cycles"]
            summary = scenario_result["summary"]

            # Extract metrics after N cycles
            final_cycle = cycles[-1] if cycles else None
            if final_cycle:
                final_jaccard = final_cycle.get("jaccard_vs_baseline", 0.0)
                final_entropy = final_cycle.get("entropy", 0.0)
                final_memory_retention = final_cycle.get("memory_retention_score", 0.0)
            else:
                final_jaccard = 0.0
                final_entropy = 0.0
                final_memory_retention = 0.0

            # Calculate largest connected stable component (simplified)
            # Count stable boundaries in final cycle
            stable_count_final = final_cycle.get("stable_count", 0) if final_cycle else 0

            results.append(
                {
                    "bookmarking_fraction": bookmarking_frac,
                    "num_cycles": num_cycles,
                    "final_jaccard": final_jaccard,
                    "final_entropy": final_entropy,
                    "final_memory_retention": final_memory_retention,
                    "stable_count_final": stable_count_final,
                    "cycles_to_collapse": summary.get("cycles_to_collapse"),
                    "total_drift": summary.get("total_drift", 0.0),
                    "cycles": cycles,  # Full cycle data
                }
            )

            print(
                f"  Final Jaccard: {final_jaccard:.3f}, "
                f"Entropy: {final_entropy:.3f}, "
                f"Memory Retention: {final_memory_retention:.3f}"
            )

        # Detect percolation threshold
        # Find sharp transition point
        threshold_estimate = None
        for i in range(len(results) - 1):
            jaccard_before = results[i]["final_jaccard"]
            jaccard_after = results[i + 1]["final_jaccard"]
            frac_before = results[i]["bookmarking_fraction"]
            frac_after = results[i + 1]["bookmarking_fraction"]

            # Sharp transition: large change in Jaccard
            jaccard_change = abs(jaccard_after - jaccard_before)
            if jaccard_change > 0.3:  # Threshold for "sharp"
                threshold_estimate = (frac_before + frac_after) / 2
                print(f"\n⚠ Percolation-like transition detected around: {threshold_estimate:.2f}")
                break

        return {
            "experiment_id": "RS-10-Threshold-Analysis",
            "threshold_estimate": threshold_estimate,
            "results": results,
        }

    def save_results(
        self, results: dict, filename: str = "RS10_bookmarking_threshold_analysis.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск анализа."""
    analysis = RS10BookmarkingThresholdAnalysis()

    # Test data
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

    # Run analysis
    results = analysis.run_threshold_analysis(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        num_cycles=20,
    )

    # Save results
    output_path = analysis.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if results["threshold_estimate"]:
        print(f"\n⚠ Estimated percolation threshold: {results['threshold_estimate']:.2f}")

    print("\nFinal metrics by bookmarking fraction:")
    for r in results["results"]:
        print(
            f"  B={r['bookmarking_fraction']:.2f}: "
            f"Jaccard={r['final_jaccard']:.3f}, "
            f"Entropy={r['final_entropy']:.3f}"
        )

    print("\n" + "=" * 60)
    print("✅ RS-10 Bookmarking Threshold Analysis Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()







