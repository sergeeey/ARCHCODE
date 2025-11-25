"""Experiment E-P3-S2-02: WAPL Overactivation Test.

Симуляция эффектов избыточного WAPL recruitment → сокращение lifetime когезина.
Гипотеза: избыточный WAPL recruitment (70% reduction lifetime) → петли не успевают расти → нестабильность границ.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.boundary_collapse import EnhancerPromoterPair
from src.vizir.config_loader import VIZIRConfigLoader


class P3S2WAPLOveractivation:
    """
    WAPL Overactivation Simulation: Excess WAPL Recruitment → Reduced Cohesin Lifetime.
    
    Based on ARCHCODE v1.1: WAPL lifetime factor model.
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_wapl_comparison(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        collapse_events_map: dict[int, list[dict]],
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
        wapl_lifetime_wt: float = 1.0,
        wapl_lifetime_overactivation: float = 0.3,  # 70% reduction
    ) -> dict:
        """
        Сравнение Wild-type vs WAPL Overactivation.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            collapse_events_map: Карта событий коллапса
            enhancer_promoter_pairs: Пары enhancer-promoter
            wapl_lifetime_wt: WAPL lifetime для wild-type (default: 1.0)
            wapl_lifetime_overactivation: WAPL lifetime для overactivation (default: 0.3 = 70% reduction)

        Returns:
            Результаты сравнения WT vs WAPL Overactivation
        """
        print("=" * 60)
        print("Experiment E-P3-S2-02: WAPL Overactivation Test")
        print("=" * 60)

        # Load VIZIR configs
        vizir_configs_wt = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Deep copy for WAPL overactivation config
        import copy
        vizir_configs_overactivation = copy.deepcopy(vizir_configs_wt)

        # Modify S2 for WAPL overactivation (30% lifetime = 70% reduction)
        if "S2" in vizir_configs_overactivation:
            s2_params = vizir_configs_overactivation["S2"].get("parameters", {})
            if "wapl_lifetime_factor" not in s2_params:
                s2_params["wapl_lifetime_factor"] = {}
            # Ensure wild_type = 1.0 for WT
            if "wild_type" not in s2_params["wapl_lifetime_factor"]:
                s2_params["wapl_lifetime_factor"]["wild_type"] = 1.0
            # Set overactivation value
            s2_params["wapl_lifetime_factor"]["overactivation"] = wapl_lifetime_overactivation

            print(f"   WT WAPL lifetime: {vizir_configs_wt['S2']['parameters'].get('wapl_lifetime_factor', {}).get('wild_type', 1.0)}")
            print(f"   Overactivation WAPL lifetime: {wapl_lifetime_overactivation}")

        # Run Wild-type simulation
        print("\n1. Wild-type simulation (WAPL lifetime = 1.0x):")
        pipeline_wt = ARCHCODEFullPipeline(vizir_configs=vizir_configs_wt)
        results_wt = pipeline_wt.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=1.0,  # Standard WT velocity
            wapl_lifetime_factor=wapl_lifetime_wt,  # v1.1: Explicit WT lifetime
        )

        # Run WAPL Overactivation simulation
        print("\n2. WAPL Overactivation simulation (WAPL lifetime = 0.3x, 70% reduction):")
        pipeline_overactivation = ARCHCODEFullPipeline(vizir_configs=vizir_configs_overactivation)
        results_overactivation = pipeline_overactivation.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=1.0,  # Standard WT velocity
            wapl_lifetime_factor=wapl_lifetime_overactivation,  # v1.1: Explicit overactivation lifetime
        )

        # Compare results
        print("\n3. Comparison:")
        wt_summary = results_wt["summary"]
        overactivation_summary = results_overactivation["summary"]

        # Calculate processivity
        processivity_wt = 1.0 * wapl_lifetime_wt  # NIPBL=1.0 × WAPL=1.0
        processivity_overactivation = 1.0 * wapl_lifetime_overactivation  # NIPBL=1.0 × WAPL=0.3

        comparison = {
            "experiment_id": "E-P3-S2-02",
            "wild_type": {
                "nipbl_velocity": 1.0,
                "wapl_lifetime": wapl_lifetime_wt,
                "processivity": processivity_wt,
                "avg_stability": wt_summary.get("avg_stability_score", 0.0),
                "stable_boundaries": wt_summary.get("stable_boundaries", 0),
                "variable_boundaries": wt_summary.get("variable_boundaries", 0),
                "collapsed_boundaries": wt_summary.get("collapsed_boundaries", 0),
                "high_risk_boundaries": wt_summary.get("high_risk_boundaries", 0),
            },
            "wapl_overactivation": {
                "nipbl_velocity": 1.0,
                "wapl_lifetime": wapl_lifetime_overactivation,
                "processivity": processivity_overactivation,
                "avg_stability": overactivation_summary.get("avg_stability_score", 0.0),
                "stable_boundaries": overactivation_summary.get("stable_boundaries", 0),
                "variable_boundaries": overactivation_summary.get("variable_boundaries", 0),
                "collapsed_boundaries": overactivation_summary.get("collapsed_boundaries", 0),
                "high_risk_boundaries": overactivation_summary.get("high_risk_boundaries", 0),
            },
            "differences": {
                "processivity_delta": processivity_overactivation - processivity_wt,
                "processivity_percent_change": (
                    (processivity_overactivation - processivity_wt) / processivity_wt * 100
                    if processivity_wt > 0
                    else 0.0
                ),
                "stability_delta": overactivation_summary.get("avg_stability_score", 0.0)
                - wt_summary.get("avg_stability_score", 0.0),
                "stability_percent_change": (
                    (overactivation_summary.get("avg_stability_score", 0.0) - wt_summary.get("avg_stability_score", 0.0))
                    / wt_summary.get("avg_stability_score", 0.0)
                    * 100
                    if wt_summary.get("avg_stability_score", 0.0) > 0
                    else 0.0
                ),
                "stable_boundaries_delta": overactivation_summary.get("stable_boundaries", 0)
                - wt_summary.get("stable_boundaries", 0),
                "collapsed_boundaries_delta": overactivation_summary.get("collapsed_boundaries", 0)
                - wt_summary.get("collapsed_boundaries", 0),
                "high_risk_delta": overactivation_summary.get("high_risk_boundaries", 0)
                - wt_summary.get("high_risk_boundaries", 0),
            },
        }

        # Print summary
        print(f"   Processivity:")
        print(f"     Wild-type:        {comparison['wild_type']['processivity']:.2f} (NIPBL={comparison['wild_type']['nipbl_velocity']:.1f} × WAPL={comparison['wild_type']['wapl_lifetime']:.1f})")
        print(f"     Overactivation:   {comparison['wapl_overactivation']['processivity']:.2f} (NIPBL={comparison['wapl_overactivation']['nipbl_velocity']:.1f} × WAPL={comparison['wapl_overactivation']['wapl_lifetime']:.1f})")
        print(f"     Change:          {comparison['differences']['processivity_delta']:.2f} ({comparison['differences']['processivity_percent_change']:.1f}%)")

        print(f"\n   Average stability:")
        print(f"     Wild-type:        {comparison['wild_type']['avg_stability']:.3f}")
        print(f"     Overactivation:   {comparison['wapl_overactivation']['avg_stability']:.3f}")
        print(f"     Change:          {comparison['differences']['stability_delta']:.3f} ({comparison['differences']['stability_percent_change']:.1f}%)")

        print(f"\n   Stable boundaries:")
        print(f"     Wild-type:        {comparison['wild_type']['stable_boundaries']}")
        print(f"     Overactivation:   {comparison['wapl_overactivation']['stable_boundaries']}")
        print(f"     Change:          {comparison['differences']['stable_boundaries_delta']}")

        print(f"\n   Collapsed boundaries:")
        print(f"     Wild-type:        {comparison['wild_type']['collapsed_boundaries']}")
        print(f"     Overactivation:   {comparison['wapl_overactivation']['collapsed_boundaries']}")
        print(f"     Change:          {comparison['differences']['collapsed_boundaries_delta']}")

        print(f"\n   High-risk boundaries:")
        print(f"     Wild-type:        {comparison['wild_type']['high_risk_boundaries']}")
        print(f"     Overactivation:   {comparison['wapl_overactivation']['high_risk_boundaries']}")
        print(f"     Change:          {comparison['differences']['high_risk_delta']}")

        return {
            "comparison": comparison,
            "wild_type_results": results_wt,
            "wapl_overactivation_results": results_overactivation,
        }

    def save_results(
        self, results: dict, filename: str = "P3_S2_wapl_overactivation.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = P3S2WAPLOveractivation()

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

    # Run comparison
    results = experiment.run_wapl_comparison(
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
    print("✅ Experiment E-P3-S2-02 Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- WAPL overactivation shows reduced boundary stability")
    print("- Processivity drops from 1.0 to 0.3 (70% reduction)")
    print("- Increased collapse probability")
    print("- Higher oncogenic risk")
    print("- Demonstrates opposite effect to CdLS (NIPBL↓) but same processivity mechanism")


if __name__ == "__main__":
    main()









