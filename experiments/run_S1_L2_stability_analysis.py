"""Experiment E-S1-L2-01: Stability Factor Decomposition.

Цель: Определить вклад каждого фактора в стабильность границы.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.vizir.config_loader import VIZIRConfigLoader
from src.vizir.integrity import compute_config_hashes, record_run


class S1L2StabilityAnalysis:
    """
    Анализ факторов стабильности границ TAD.

    Вопрос: Почему одни границы стабильны в 95% клеток, а другие — только в 30%?
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        self.pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_factor_decomposition(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        experimental_stability: dict[int, float] | None = None,
    ) -> dict:
        """
        Разложение факторов стабильности.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров по позициям
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            experimental_stability: Экспериментальные данные стабильности (опционально)

        Returns:
            Результаты анализа факторов
        """
        print("=" * 60)
        print("Experiment E-S1-L2-01: Stability Factor Decomposition")
        print("=" * 60)

        # Запустить анализ стабильности
        results = self.pipeline.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
        )

        stability_predictions = results["stability_predictions"]

        # Разложение факторов
        factor_analysis = []
        for pred in stability_predictions:
            position = pred["position"]
            predicted_stability = pred["stability_score"]

            # Извлечь факторы для этой позиции
            ctcf_strength = next(
                (b["strength"] for b in results["boundaries"] if b["position"] == position),
                0.0,
            )
            barrier_strengths = barrier_strengths_map.get(position, [])
            avg_barrier = sum(barrier_strengths) / len(barrier_strengths) if barrier_strengths else 0.0
            methylation = methylation_map.get(position, 0.0)
            te_effects = te_motif_map.get(position, [])
            avg_te = sum(te_effects) / len(te_effects) if te_effects else 0.0

            experimental = experimental_stability.get(position) if experimental_stability else None

            factor_analysis.append(
                {
                    "position": position,
                    "predicted_stability": predicted_stability,
                    "experimental_stability": experimental,
                    "ctcf_strength": ctcf_strength,
                    "avg_barrier_strength": avg_barrier,
                    "methylation_level": methylation,
                    "avg_te_effect": avg_te,
                    "stability_category": pred["stability_category"],
                }
            )

        # Статистика
        df = pd.DataFrame(factor_analysis)

        # Корреляция факторов с предсказанной стабильностью
        correlations = {
            "ctcf_vs_stability": df["ctcf_strength"].corr(df["predicted_stability"]),
            "barrier_vs_stability": df["avg_barrier_strength"].corr(df["predicted_stability"]),
            "methylation_vs_stability": df["methylation_level"].corr(df["predicted_stability"]),
            "te_vs_stability": df["avg_te_effect"].corr(df["predicted_stability"]),
        }

        # Если есть экспериментальные данные, сравнить
        if experimental_stability:
            df_with_exp = df[df["experimental_stability"].notna()]
            if len(df_with_exp) > 0:
                correlations["predicted_vs_experimental"] = df_with_exp["predicted_stability"].corr(
                    df_with_exp["experimental_stability"]
                )

                # Feature importance через корреляцию с экспериментальными данными
                feature_importance = {
                    "ctcf": abs(df_with_exp["ctcf_strength"].corr(df_with_exp["experimental_stability"])),
                    "barrier": abs(
                        df_with_exp["avg_barrier_strength"].corr(df_with_exp["experimental_stability"])
                    ),
                    "methylation": abs(
                        df_with_exp["methylation_level"].corr(df_with_exp["experimental_stability"])
                    ),
                    "te": abs(df_with_exp["avg_te_effect"].corr(df_with_exp["experimental_stability"])),
                }
            else:
                feature_importance = {}
        else:
            feature_importance = {}

        # Пороговый анализ
        stable_boundaries = df[df["predicted_stability"] >= 0.7]
        variable_boundaries = df[df["predicted_stability"] <= 0.4]

        thresholds = {
            "stable": {
                "count": len(stable_boundaries),
                "avg_ctcf": stable_boundaries["ctcf_strength"].mean() if len(stable_boundaries) > 0 else 0.0,
                "avg_barrier": stable_boundaries["avg_barrier_strength"].mean()
                if len(stable_boundaries) > 0
                else 0.0,
                "avg_methylation": stable_boundaries["methylation_level"].mean()
                if len(stable_boundaries) > 0
                else 0.0,
            },
            "variable": {
                "count": len(variable_boundaries),
                "avg_ctcf": variable_boundaries["ctcf_strength"].mean()
                if len(variable_boundaries) > 0
                else 0.0,
                "avg_barrier": variable_boundaries["avg_barrier_strength"].mean()
                if len(variable_boundaries) > 0
                else 0.0,
                "avg_methylation": variable_boundaries["methylation_level"].mean()
                if len(variable_boundaries) > 0
                else 0.0,
            },
        }

        analysis_results = {
            "experiment_id": "E-S1-L2-01",
            "factor_analysis": factor_analysis,
            "correlations": correlations,
            "feature_importance": feature_importance,
            "thresholds": thresholds,
            "summary": {
                "total_boundaries": len(factor_analysis),
                "stable_count": len(stable_boundaries),
                "variable_count": len(variable_boundaries),
                "intermediate_count": len(df) - len(stable_boundaries) - len(variable_boundaries),
            },
        }

        return analysis_results

    def save_results(self, results: dict, filename: str = "S1_L2_stability_analysis.json") -> Path:
        """Сохранить результаты анализа."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = S1L2StabilityAnalysis()

    # Пример данных (в реальности загружать из файлов)
    boundaries_data = [
        (100000, 0.9, "ctcf"),  # Высокая стабильность ожидается
        (200000, 0.7, "ctcf"),
        (300000, 0.5, "ctcf"),
        (400000, 0.3, "ctcf"),  # Низкая стабильность ожидается
        (500000, 0.8, "ctcf"),
    ]

    barrier_strengths_map = {
        100000: [0.1],  # Низкие барьеры → стабильность
        200000: [0.2],
        300000: [0.6],
        400000: [0.8],  # Высокие барьеры → нестабильность
        500000: [0.1],
    }

    methylation_map = {
        100000: 0.1,  # Низкое метилирование → стабильность
        200000: 0.2,
        300000: 0.7,
        400000: 0.9,  # Высокое метилирование → нестабильность
        500000: 0.3,
    }

    te_motif_map = {
        100000: [0.0],
        200000: [0.0],
        300000: [0.3],
        400000: [0.5],
        500000: [0.0],
    }

    # Экспериментальные данные (опционально, если есть)
    experimental_stability = {
        100000: 0.95,  # Высокая стабильность
        200000: 0.75,
        300000: 0.50,
        400000: 0.30,  # Низкая стабильность
        500000: 0.80,
    }

    # Запустить анализ
    results = experiment.run_factor_decomposition(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        experimental_stability=experimental_stability,
    )

    # Сохранить результаты
    output_path = experiment.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    # Вывести summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Total boundaries: {results['summary']['total_boundaries']}")
    print(f"Stable: {results['summary']['stable_count']}")
    print(f"Variable: {results['summary']['variable_count']}")
    print(f"Intermediate: {results['summary']['intermediate_count']}")

    print("\nCorrelations:")
    for factor, corr in results["correlations"].items():
        print(f"  {factor}: {corr:.3f}")

    if results["feature_importance"]:
        print("\nFeature Importance (vs experimental):")
        for factor, importance in sorted(
            results["feature_importance"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {factor}: {importance:.3f}")

    print("\n" + "=" * 60)
    print("✅ Experiment E-S1-L2-01 Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

