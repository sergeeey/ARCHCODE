"""Experiment E-P3-S2-01: CdLS Simulation.

Симуляция эффектов синдрома Корнелии де Ланге (NIPBL haploinsufficiency).
Гипотеза: снижение NIPBL на 50% размывает TAD границы.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.boundary_collapse import EnhancerPromoterPair
from src.vizir.config_loader import VIZIRConfigLoader


class P3S2CdLSSimulation:
    """
    CdLS Simulation: NIPBL Haploinsufficiency → TAD Boundary Blurring.
    
    Based on ARCHCODE v1.1: NIPBL velocity multiplier model.
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_cdls_comparison(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        collapse_events_map: dict[int, list[dict]],
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> dict:
        """
        Сравнение Wild-type vs CdLS.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            collapse_events_map: Карта событий коллапса
            enhancer_promoter_pairs: Пары enhancer-promoter

        Returns:
            Результаты сравнения WT vs CdLS
        """
        print("=" * 60)
        print("Experiment E-P3-S2-01: CdLS Simulation")
        print("=" * 60)

        # Load VIZIR configs
        vizir_configs_wt = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Modify P3 for CdLS (50% NIPBL velocity)
        # ИСПРАВЛЕНИЕ: Deep copy для правильного разделения конфигов
        import copy
        vizir_configs_cdls = copy.deepcopy(vizir_configs_wt)
        if "P3" in vizir_configs_cdls:
            p3_params = vizir_configs_cdls["P3"].get("parameters", {})
            if "nipbl_velocity_multiplier" not in p3_params:
                p3_params["nipbl_velocity_multiplier"] = {}
            # Убеждаемся, что wild_type = 1.0 для WT (не перезаписываем)
            if "wild_type" not in p3_params["nipbl_velocity_multiplier"]:
                p3_params["nipbl_velocity_multiplier"]["wild_type"] = 1.0
            # Используем правильный ключ для CdLS
            p3_params["nipbl_velocity_multiplier"]["cdls_haploinsufficient"] = 0.5  # 50% reduction
            
            # Debug: print extracted values
            print(f"   WT NIPBL velocity: {vizir_configs_wt['P3']['parameters']['nipbl_velocity_multiplier'].get('wild_type', 1.0)}")
            print(f"   CdLS NIPBL velocity: {p3_params['nipbl_velocity_multiplier'].get('cdls_haploinsufficient', 0.5)}")

        # Run Wild-type simulation
        print("\n1. Wild-type simulation (NIPBL velocity = 1.0x):")
        pipeline_wt = ARCHCODEFullPipeline(vizir_configs=vizir_configs_wt)
        results_wt = pipeline_wt.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=1.0,  # v1.1: Explicit WT velocity
        )

        # Run CdLS simulation
        print("\n2. CdLS simulation (NIPBL velocity = 0.5x):")
        pipeline_cdls = ARCHCODEFullPipeline(vizir_configs=vizir_configs_cdls)
        results_cdls = pipeline_cdls.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=0.5,  # v1.1: Explicit CdLS velocity (50% reduction)
        )

        # Compare results
        print("\n3. Comparison:")
        wt_summary = results_wt["summary"]
        cdls_summary = results_cdls["summary"]

        comparison = {
            "experiment_id": "E-P3-S2-01",
            "wild_type": {
                "avg_stability": wt_summary.get("avg_stability_score", 0.0),
                "stable_boundaries": wt_summary.get("stable_boundaries", 0),
                "variable_boundaries": wt_summary.get("variable_boundaries", 0),
                "collapsed_boundaries": wt_summary.get("collapsed_boundaries", 0),
                "high_risk_boundaries": wt_summary.get("high_risk_boundaries", 0),
            },
            "cdls": {
                "avg_stability": cdls_summary.get("avg_stability_score", 0.0),
                "stable_boundaries": cdls_summary.get("stable_boundaries", 0),
                "variable_boundaries": cdls_summary.get("variable_boundaries", 0),
                "collapsed_boundaries": cdls_summary.get("collapsed_boundaries", 0),
                "high_risk_boundaries": cdls_summary.get("high_risk_boundaries", 0),
            },
            "differences": {
                "stability_delta": cdls_summary.get("avg_stability_score", 0.0)
                - wt_summary.get("avg_stability_score", 0.0),
                "stability_percent_change": (
                    (cdls_summary.get("avg_stability_score", 0.0) - wt_summary.get("avg_stability_score", 0.0))
                    / wt_summary.get("avg_stability_score", 0.0)
                    * 100
                    if wt_summary.get("avg_stability_score", 0.0) > 0
                    else 0.0
                ),
                "stable_boundaries_delta": cdls_summary.get("stable_boundaries", 0)
                - wt_summary.get("stable_boundaries", 0),
                "collapsed_boundaries_delta": cdls_summary.get("collapsed_boundaries", 0)
                - wt_summary.get("collapsed_boundaries", 0),
                "high_risk_delta": cdls_summary.get("high_risk_boundaries", 0)
                - wt_summary.get("high_risk_boundaries", 0),
            },
        }

        # Print summary
        print(f"   Average stability:")
        print(f"     Wild-type: {comparison['wild_type']['avg_stability']:.3f}")
        print(f"     CdLS:      {comparison['cdls']['avg_stability']:.3f}")
        print(f"     Change:    {comparison['differences']['stability_delta']:.3f} ({comparison['differences']['stability_percent_change']:.1f}%)")

        print(f"\n   Stable boundaries:")
        print(f"     Wild-type: {comparison['wild_type']['stable_boundaries']}")
        print(f"     CdLS:      {comparison['cdls']['stable_boundaries']}")
        print(f"     Change:    {comparison['differences']['stable_boundaries_delta']}")

        print(f"\n   Collapsed boundaries:")
        print(f"     Wild-type: {comparison['wild_type']['collapsed_boundaries']}")
        print(f"     CdLS:      {comparison['cdls']['collapsed_boundaries']}")
        print(f"     Change:    {comparison['differences']['collapsed_boundaries_delta']}")

        print(f"\n   High-risk boundaries:")
        print(f"     Wild-type: {comparison['wild_type']['high_risk_boundaries']}")
        print(f"     CdLS:      {comparison['cdls']['high_risk_boundaries']}")
        print(f"     Change:    {comparison['differences']['high_risk_delta']}")

        return {
            "comparison": comparison,
            "wild_type_results": results_wt,
            "cdls_results": results_cdls,
        }

    def save_results(self, results: dict, filename: str = "P3_S2_cdls_comparison.json") -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = P3S2CdLSSimulation()

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

    # Run comparison
    results = experiment.run_cdls_comparison(
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

    print("\n" + "=" * 60)
    print("✅ Experiment E-P3-S2-01 Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- CdLS shows reduced boundary stability")
    print("- TAD boundaries 'blur' (intermediate category)")
    print("- Increased collapse probability")
    print("- Higher oncogenic risk")


if __name__ == "__main__":
    main()

