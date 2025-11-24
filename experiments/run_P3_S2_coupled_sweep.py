"""Experiment E-P3-S2-03: Coupled Dynamics Sweep.

Построение фазовой диаграммы стабильности TAD границ в пространстве
(NIPBL velocity × WAPL lifetime).

Гипотеза: Существует фазовый переход в пространстве параметров processivity.
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.boundary_collapse import EnhancerPromoterPair
from src.vizir.config_loader import VIZIRConfigLoader


class P3S2CoupledSweep:
    """
    Coupled Dynamics Sweep: NIPBL velocity × WAPL lifetime → Stability Landscape.
    
    Based on ARCHCODE v1.1: Processivity = Rate × Lifetime model.
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_sweep(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        collapse_events_map: dict[int, list[dict]],
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
        nipbl_range: list[float] | None = None,
        wapl_range: list[float] | None = None,
    ) -> dict[str, Any]:
        """
        Выполнить sweep по параметрам NIPBL velocity и WAPL lifetime.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            collapse_events_map: Карта событий коллапса
            enhancer_promoter_pairs: Пары enhancer-promoter
            nipbl_range: Диапазон значений NIPBL velocity (по умолчанию [0.3, 0.5, 0.7, 1.0, 1.3])
            wapl_range: Диапазон значений WAPL lifetime (по умолчанию [0.3, 0.5, 0.7, 1.0, 1.5, 2.0])

        Returns:
            Результаты sweep: фазовая карта стабильности, коллапсов, рисков
        """
        print("=" * 60)
        print("Experiment E-P3-S2-03: Coupled Dynamics Sweep")
        print("=" * 60)

        # Default ranges from RS-09 spec
        if nipbl_range is None:
            nipbl_range = [0.3, 0.5, 0.7, 1.0, 1.3]
        if wapl_range is None:
            wapl_range = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

        print(f"\nSweep parameters:")
        print(f"  NIPBL velocity: {nipbl_range}")
        print(f"  WAPL lifetime:  {wapl_range}")
        print(f"  Total combinations: {len(nipbl_range) * len(wapl_range)}")

        # Load base VIZIR configs
        vizir_configs_base = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Initialize results storage
        stability_landscape: list[dict[str, Any]] = []
        collapse_map: list[dict[str, Any]] = []
        risk_map: list[dict[str, Any]] = []

        total_combinations = len(nipbl_range) * len(wapl_range)
        current = 0

        # Sweep over all combinations
        for nipbl_vel in nipbl_range:
            for wapl_life in wapl_range:
                current += 1
                processivity = nipbl_vel * wapl_life

                print(f"\n[{current}/{total_combinations}] NIPBL={nipbl_vel:.2f}, WAPL={wapl_life:.2f}, Processivity={processivity:.2f}")

                # Initialize pipeline with base configs
                pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs_base)

                # Run full analysis with specific velocity/lifetime
                try:
                    results = pipeline.run_full_analysis(
                        boundaries_data=boundaries_data,
                        barrier_strengths_map=barrier_strengths_map,
                        methylation_map=methylation_map,
                        te_motif_map=te_motif_map,
                        collapse_events=collapse_events_map,
                        enhancer_promoter_pairs=enhancer_promoter_pairs,
                        nipbl_velocity_factor=nipbl_vel,
                        wapl_lifetime_factor=wapl_life,
                    )

                    summary = results.get("summary", {})
                    stability_predictions = results.get("stability_predictions", [])

                    # Extract metrics
                    avg_stability = summary.get("avg_stability_score", 0.0)
                    stable_count = summary.get("stable_boundaries", 0)
                    variable_count = summary.get("variable_boundaries", 0)
                    collapsed_count = summary.get("collapsed_boundaries", 0)
                    high_risk_count = summary.get("high_risk_boundaries", 0)
                    total_boundaries = len(stability_predictions)

                    # Calculate collapse probability (if collapse events exist)
                    collapse_prob = 0.0
                    if collapse_events_map and total_boundaries > 0:
                        collapse_prob = collapsed_count / total_boundaries

                    # Calculate average risk
                    avg_risk = 0.0
                    if stability_predictions:
                        risk_scores = [
                            pred.get("risk_score", 0.0)
                            for pred in stability_predictions
                            if isinstance(pred, dict)
                        ]
                        if risk_scores:
                            avg_risk = sum(risk_scores) / len(risk_scores)

                    # Store results
                    stability_landscape.append({
                        "nipbl_velocity": nipbl_vel,
                        "wapl_lifetime": wapl_life,
                        "processivity": processivity,
                        "avg_stability": avg_stability,
                        "stable_boundaries": stable_count,
                        "variable_boundaries": variable_count,
                        "total_boundaries": total_boundaries,
                    })

                    collapse_map.append({
                        "nipbl_velocity": nipbl_vel,
                        "wapl_lifetime": wapl_life,
                        "processivity": processivity,
                        "collapse_probability": collapse_prob,
                        "collapsed_boundaries": collapsed_count,
                    })

                    risk_map.append({
                        "nipbl_velocity": nipbl_vel,
                        "wapl_lifetime": wapl_life,
                        "processivity": processivity,
                        "avg_risk": avg_risk,
                        "high_risk_boundaries": high_risk_count,
                    })

                    print(f"  → Stability: {avg_stability:.3f}, Collapse: {collapse_prob:.3f}, Risk: {avg_risk:.3f}")

                except Exception as e:
                    print(f"  ⚠ Error: {e}")
                    # Store error state
                    stability_landscape.append({
                        "nipbl_velocity": nipbl_vel,
                        "wapl_lifetime": wapl_life,
                        "processivity": processivity,
                        "avg_stability": 0.0,
                        "error": str(e),
                    })

        # Build phase diagram data
        print("\n" + "=" * 60)
        print("Building phase diagram...")
        print("=" * 60)

        # Create 2D matrices for heatmaps
        stability_matrix = self._build_matrix(
            stability_landscape, nipbl_range, wapl_range, "avg_stability"
        )
        collapse_matrix = self._build_matrix(
            collapse_map, nipbl_range, wapl_range, "collapse_probability"
        )
        risk_matrix = self._build_matrix(
            risk_map, nipbl_range, wapl_range, "avg_risk"
        )

        # Find phase transitions (critical points)
        phase_transitions = self._find_phase_transitions(
            stability_matrix, nipbl_range, wapl_range
        )

        results = {
            "experiment_id": "E-P3-S2-03",
            "sweep_parameters": {
                "nipbl_range": nipbl_range,
                "wapl_range": wapl_range,
                "total_combinations": total_combinations,
            },
            "raw_data": {
                "stability_landscape": stability_landscape,
                "collapse_map": collapse_map,
                "risk_map": risk_map,
            },
            "phase_diagrams": {
                "stability_matrix": stability_matrix,
                "collapse_matrix": collapse_matrix,
                "risk_matrix": risk_matrix,
            },
            "phase_transitions": phase_transitions,
            "summary": {
                "min_stability": min(
                    (d["avg_stability"] for d in stability_landscape if "error" not in d),
                    default=0.0,
                ),
                "max_stability": max(
                    (d["avg_stability"] for d in stability_landscape if "error" not in d),
                    default=0.0,
                ),
                "min_collapse": min(
                    (d["collapse_probability"] for d in collapse_map),
                    default=0.0,
                ),
                "max_collapse": max(
                    (d["collapse_probability"] for d in collapse_map),
                    default=0.0,
                ),
                "critical_processivity": phase_transitions.get("critical_processivity", []),
            },
        }

        return results

    def _build_matrix(
        self,
        data: list[dict[str, Any]],
        nipbl_range: list[float],
        wapl_range: list[float],
        metric_key: str,
    ) -> list[list[float]]:
        """Построить 2D матрицу для heatmap."""
        matrix: list[list[float]] = []

        # Create lookup dict
        lookup: dict[tuple[float, float], float] = {}
        for item in data:
            nipbl = item["nipbl_velocity"]
            wapl = item["wapl_lifetime"]
            value = item.get(metric_key, 0.0)
            lookup[(nipbl, wapl)] = value

        # Build matrix: rows = WAPL, cols = NIPBL
        for wapl in wapl_range:
            row: list[float] = []
            for nipbl in nipbl_range:
                value = lookup.get((nipbl, wapl), 0.0)
                row.append(value)
            matrix.append(row)

        return matrix

    def _find_phase_transitions(
        self,
        stability_matrix: list[list[float]],
        nipbl_range: list[float],
        wapl_range: list[float],
    ) -> dict[str, Any]:
        """Найти критические точки фазовых переходов."""
        transitions: list[dict[str, Any]] = []
        critical_processivity: list[float] = []

        # Threshold для "стабильной" фазы (можно настроить)
        stability_threshold = 0.5

        # Ищем границы между стабильными и нестабильными зонами
        for i, wapl in enumerate(wapl_range):
            for j, nipbl in enumerate(nipbl_range):
                stability = stability_matrix[i][j]
                processivity = nipbl * wapl

                # Проверяем соседние точки на фазовый переход
                if j > 0:  # Слева
                    left_stability = stability_matrix[i][j - 1]
                    if (stability >= stability_threshold) != (
                        left_stability >= stability_threshold
                    ):
                        transitions.append({
                            "nipbl_velocity": nipbl,
                            "wapl_lifetime": wapl,
                            "processivity": processivity,
                            "stability": stability,
                            "transition_type": "stability_boundary",
                        })
                        critical_processivity.append(processivity)

                if i > 0:  # Сверху
                    top_stability = stability_matrix[i - 1][j]
                    if (stability >= stability_threshold) != (
                        top_stability >= stability_threshold
                    ):
                        transitions.append({
                            "nipbl_velocity": nipbl,
                            "wapl_lifetime": wapl,
                            "processivity": processivity,
                            "stability": stability,
                            "transition_type": "stability_boundary",
                        })
                        critical_processivity.append(processivity)

        return {
            "transitions": transitions,
            "critical_processivity": sorted(set(critical_processivity)),
            "stability_threshold": stability_threshold,
        }

    def save_results(
        self, results: dict[str, Any], filename: str = "P3_S2_coupled_sweep.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path

    def print_summary(self, results: dict[str, Any]) -> None:
        """Вывести краткую сводку результатов."""
        summary = results["summary"]
        transitions = results["phase_transitions"]

        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Stability range: {summary['min_stability']:.3f} - {summary['max_stability']:.3f}")
        print(f"Collapse range: {summary['min_collapse']:.3f} - {summary['max_collapse']:.3f}")
        print(f"\nPhase transitions found: {len(transitions['transitions'])}")
        if transitions["critical_processivity"]:
            print(f"Critical processivity values: {transitions['critical_processivity']}")
        print(f"Stability threshold: {transitions['stability_threshold']:.2f}")


def main() -> None:
    """Запуск эксперимента."""
    experiment = P3S2CoupledSweep()

    # Test data (same as CdLS experiment for consistency)
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

    # Run sweep
    results = experiment.run_sweep(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        collapse_events_map=collapse_events_map,
        enhancer_promoter_pairs=enhancer_promoter_pairs,
    )

    # Print summary
    experiment.print_summary(results)

    # Save results
    output_path = experiment.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    print("\n" + "=" * 60)
    print("✅ Experiment E-P3-S2-03 Complete")
    print("=" * 60)
    print("\nExpected outcomes:")
    print("- Phase diagram showing stability landscape")
    print("- Identification of phase transition boundaries")
    print("- Critical processivity values")
    print("- Risk and collapse probability maps")


if __name__ == "__main__":
    main()
