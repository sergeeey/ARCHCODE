"""RS-09 NIPBL Mechanisms Comparison.

Сравнение разных механизмов действия NIPBL (velocity vs density vs mixed).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.nipbl_mechanisms import (
    NIPBLMechanism,
    calculate_effective_processivity_from_mechanism,
)
from src.vizir.config_loader import VIZIRConfigLoader


class RS09NIPBLMechanismsComparison:
    """Comparison of NIPBL mechanisms."""

    def __init__(self) -> None:
        """Инициализация."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_comparison(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        nipbl_factors: list[float] | None = None,
        wapl_factors: list[float] | None = None,
    ) -> dict:
        """
        Запустить сравнение механизмов.

        Args:
            boundaries_data: Границы
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            nipbl_factors: Значения NIPBL factor
            wapl_factors: Значения WAPL lifetime

        Returns:
            Результаты сравнения
        """
        print("=" * 60)
        print("RS-09 NIPBL Mechanisms Comparison")
        print("=" * 60)

        if nipbl_factors is None:
            nipbl_factors = [0.3, 0.5, 0.7, 1.0, 1.3]
        if wapl_factors is None:
            wapl_factors = [0.3, 0.6, 1.0, 1.3]

        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        results = {
            "velocity_only": [],
            "density_only": [],
            "mixed": [],
        }

        mechanisms = [
            NIPBLMechanism.VELOCITY_ONLY,
            NIPBLMechanism.DENSITY_ONLY,
            NIPBLMechanism.MIXED,
        ]

        # Limited sweep: 3×3 = 9 points per mechanism
        test_nipbl = [0.3, 0.7, 1.3]
        test_wapl = [0.3, 1.0, 1.3]

        for mechanism in mechanisms:
            mechanism_name = mechanism.value
            print(f"\n{mechanism_name.upper()}:")
            print("-" * 60)

            for nipbl_factor in test_nipbl:
                for wapl_factor in test_wapl:
                    # Calculate effective processivity
                    effective_p = calculate_effective_processivity_from_mechanism(
                        nipbl_factor=nipbl_factor,
                        wapl_lifetime_factor=wapl_factor,
                        mechanism=mechanism,
                    )

                    # Determine phase
                    if effective_p < 0.5:
                        phase = "unstable"
                    elif effective_p < 1.0:
                        phase = "transitional"
                    else:
                        phase = "stable"

                    # Run simulation
                    pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
                    results_sim = pipeline.run_full_analysis(
                        boundaries_data=boundaries_data,
                        barrier_strengths_map=barrier_strengths_map,
                        methylation_map=methylation_map,
                        te_motif_map=te_motif_map,
                        collapse_events=None,
                        enhancer_promoter_pairs=None,
                        nipbl_velocity_factor=nipbl_factor,  # Use factor directly
                        wapl_lifetime_factor=wapl_factor,
                    )

                    summary = results_sim["summary"]
                    avg_stability = summary.get("avg_stability_score", 0.0)
                    collapse_prob = summary.get("collapse_probability", 0.0)

                    results[mechanism_name].append(
                        {
                            "nipbl_factor": nipbl_factor,
                            "wapl_factor": wapl_factor,
                            "effective_processivity": effective_p,
                            "avg_stability": avg_stability,
                            "collapse_probability": collapse_prob,
                            "phase": phase,
                        }
                    )

                    print(
                        f"  NIPBL={nipbl_factor:.1f}, WAPL={wapl_factor:.1f} → "
                        f"P_eff={effective_p:.2f}, phase={phase}, "
                        f"stability={avg_stability:.3f}"
                    )

        return results

    def save_results(
        self, results: dict, filename: str = "RS09_nipbl_mechanisms_comparison.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск сравнения."""
    experiment = RS09NIPBLMechanismsComparison()

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

    # Run comparison
    results = experiment.run_comparison(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
    )

    # Save results
    output_path = experiment.save_results(results)
    print(f"\n✅ Результаты сохранены: {output_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    for mechanism_name, mechanism_results in results.items():
        print(f"\n{mechanism_name}:")
        phases = [r["phase"] for r in mechanism_results]
        print(f"  Phases: {set(phases)}")
        avg_stabilities = [r["avg_stability"] for r in mechanism_results]
        print(f"  Stability range: {min(avg_stabilities):.3f} - {max(avg_stabilities):.3f}")

    print("\n" + "=" * 60)
    print("✅ RS-09 NIPBL Mechanisms Comparison Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()









