"""RS-09 Environmental Factors Robustness Analysis.

Проверка устойчивости фазовой структуры к локальным env-факторам.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.environmental_factors import (
    calculate_ctcf_density_map,
    calculate_effective_processivity,
    create_synthetic_compartment_mask,
)
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.vizir.config_loader import VIZIRConfigLoader


class RS09EnvFactorRobustness:
    """Robustness analysis for environmental factors."""

    def __init__(self) -> None:
        """Инициализация."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_robustness_analysis(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        global_processivity_values: list[float] | None = None,
    ) -> dict:
        """
        Запустить robustness-анализ.

        Args:
            boundaries_data: Границы
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            global_processivity_values: Значения global processivity для теста

        Returns:
            Результаты анализа
        """
        print("=" * 60)
        print("RS-09 Environmental Factors Robustness Analysis")
        print("=" * 60)

        if global_processivity_values is None:
            global_processivity_values = [0.3, 0.5, 0.7, 1.0, 1.3]

        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Prepare environmental factors
        # Create boundaries objects for density calculation
        from src.archcode_core.extrusion_engine import Boundary

        boundaries = [
            Boundary(
                position=pos,
                strength=strength,
                barrier_type=btype,
                insulation_score=0.5,
            )
            for pos, strength, btype in boundaries_data
        ]

        ctcf_density_map = calculate_ctcf_density_map(boundaries)
        compartment_mask = create_synthetic_compartment_mask(
            [pos for pos, _, _ in boundaries_data]
        )

        results = {"baseline": [], "with_env_factors": []}

        for global_p in global_processivity_values:
            print(f"\nTesting global processivity: {global_p:.2f}")

            # Calculate NIPBL and WAPL for this processivity
            # Assume balanced: NIPBL = WAPL = sqrt(processivity)
            nipbl = wapl = global_p**0.5

            # Baseline: без env_factors
            print("  Baseline (no env factors)...")
            pipeline_baseline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
            results_baseline = pipeline_baseline.run_full_analysis(
                boundaries_data=boundaries_data,
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                collapse_events=None,
                enhancer_promoter_pairs=None,
                nipbl_velocity_factor=nipbl,
                wapl_lifetime_factor=wapl,
            )

            baseline_summary = results_baseline["summary"]
            baseline_stability = baseline_summary.get("avg_stability_score", 0.0)
            baseline_collapse = baseline_summary.get("collapse_probability", 0.0)

            # Determine phase
            if global_p < 0.5:
                phase = "unstable"
            elif global_p < 1.0:
                phase = "transitional"
            else:
                phase = "stable"

            results["baseline"].append(
                {
                    "global_processivity": global_p,
                    "nipbl_velocity": nipbl,
                    "wapl_lifetime": wapl,
                    "avg_stability": baseline_stability,
                    "collapse_probability": baseline_collapse,
                    "phase": phase,
                }
            )

            # With env_factors
            print("  With env factors...")
            # Calculate effective processivity for each boundary
            effective_processivities = []
            for pos, _, _ in boundaries_data:
                eff_p = calculate_effective_processivity(
                    global_processivity=global_p,
                    position=pos,
                    ctcf_density_map=ctcf_density_map,
                    compartment_mask=compartment_mask,
                )
                effective_processivities.append(eff_p)

            # Average effective processivity
            avg_effective_p = sum(effective_processivities) / len(effective_processivities)

            # Run with adjusted processivity
            # For simplicity, we adjust NIPBL based on average effective factor
            effective_factor = avg_effective_p / global_p if global_p > 0 else 1.0
            adjusted_nipbl = nipbl * effective_factor

            pipeline_env = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
            results_env = pipeline_env.run_full_analysis(
                boundaries_data=boundaries_data,
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                collapse_events=None,
                enhancer_promoter_pairs=None,
                nipbl_velocity_factor=adjusted_nipbl,
                wapl_lifetime_factor=wapl,
            )

            env_summary = results_env["summary"]
            env_stability = env_summary.get("avg_stability_score", 0.0)
            env_collapse = env_summary.get("collapse_probability", 0.0)

            # Determine phase (using effective processivity)
            if avg_effective_p < 0.5:
                env_phase = "unstable"
            elif avg_effective_p < 1.0:
                env_phase = "transitional"
            else:
                env_phase = "stable"

            results["with_env_factors"].append(
                {
                    "global_processivity": global_p,
                    "effective_processivity": avg_effective_p,
                    "effective_factor": effective_factor,
                    "nipbl_velocity": adjusted_nipbl,
                    "wapl_lifetime": wapl,
                    "avg_stability": env_stability,
                    "collapse_probability": env_collapse,
                    "phase": env_phase,
                }
            )

            print(
                f"    Baseline: stability={baseline_stability:.3f}, phase={phase}"
            )
            print(
                f"    With env: stability={env_stability:.3f}, phase={env_phase}, "
                f"eff_factor={effective_factor:.3f}"
            )

        return results

    def save_results(
        self, results: dict, filename: str = "RS09_env_factor_robustness.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск анализа."""
    experiment = RS09EnvFactorRobustness()

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
    results = experiment.run_robustness_analysis(
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

    print("\nBaseline phases:")
    for r in results["baseline"]:
        print(f"  P={r['global_processivity']:.2f} → {r['phase']}")

    print("\nWith env factors phases:")
    for r in results["with_env_factors"]:
        print(
            f"  P={r['global_processivity']:.2f} → "
            f"P_eff={r['effective_processivity']:.2f} → {r['phase']}"
        )

    print("\n" + "=" * 60)
    print("✅ RS-09 Environmental Factors Robustness Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()






