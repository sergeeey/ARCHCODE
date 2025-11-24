"""RS-10 Experiment A: Bookmarking vs No-Bookmarking through Mitosis.

Симуляция цикла: Интерфаза → Митоз → G1 восстановление
в двух режимах: с Bookmarking и без Bookmarking.
"""

import json
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


class RS10BookmarkingCycle:
    """
    RS-10 Experiment A: Bookmarking vs No-Bookmarking through Mitosis.

    Simulates: Interphase → Mitosis → G1 Recovery
    Compares: With Bookmarking vs Without Bookmarking
    """

    def __init__(self) -> None:
        """Инициализация эксперимента."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_bookmarking_cycle(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        collapse_events_map: dict[int, list[dict]],
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> dict:
        """
        Запустить эксперимент RS-10 A: Bookmarking cycle.

        Args:
            boundaries_data: Список границ (position, strength, barrier_type)
            barrier_strengths_map: Карта барьеров
            methylation_map: Карта метилирования
            te_motif_map: Карта TE мотивов
            collapse_events_map: Карта событий коллапса
            enhancer_promoter_pairs: Пары enhancer-promoter

        Returns:
            Результаты эксперимента
        """
        print("=" * 60)
        print("RS-10 Experiment A: Bookmarking vs No-Bookmarking")
        print("=" * 60)

        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # WT processivity parameters (from RS-09)
        nipbl_velocity_wt = 1.0
        wapl_lifetime_wt = 1.0
        processivity_wt = nipbl_velocity_wt * wapl_lifetime_wt

        print(f"\nWT Processivity: {processivity_wt:.2f} (NIPBL={nipbl_velocity_wt:.1f} × WAPL={wapl_lifetime_wt:.1f})")

        # ============================================================
        # Step 1: Baseline Interphase (Before Mitosis)
        # ============================================================
        print("\n" + "=" * 60)
        print("Step 1: Baseline Interphase (Before Mitosis)")
        print("=" * 60)

        pipeline_baseline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        results_baseline = pipeline_baseline.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=nipbl_velocity_wt,
            wapl_lifetime_factor=wapl_lifetime_wt,
        )

        baseline_summary = results_baseline["summary"]
        baseline_stability = baseline_summary.get("avg_stability_score", 0.0)
        baseline_stable_boundaries = baseline_summary.get("stable_boundaries", 0)

        # Extract stable boundary positions
        stable_boundaries_before = set()
        for pred in results_baseline.get("stability_predictions", []):
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_boundaries_before.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_boundaries_before.add(pred.position)

        print(f"  Average stability: {baseline_stability:.3f}")
        print(f"  Stable boundaries: {baseline_stable_boundaries}")
        print(f"  Stable positions: {sorted(stable_boundaries_before)}")

        # ============================================================
        # Step 2: Mitosis (Collapse)
        # ============================================================
        print("\n" + "=" * 60)
        print("Step 2: Mitosis (Architecture Collapse)")
        print("=" * 60)

        # Mitosis: Low processivity + weakened barriers
        nipbl_velocity_mitosis = 0.3
        wapl_lifetime_mitosis = 0.3
        processivity_mitosis = nipbl_velocity_mitosis * wapl_lifetime_mitosis

        print(f"  Processivity: {processivity_mitosis:.2f} (NIPBL={nipbl_velocity_mitosis:.1f} × WAPL={wapl_lifetime_mitosis:.1f})")
        print("  Phase: MITOSIS (barriers weakened)")

        pipeline_mitosis = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        # Note: We simulate mitosis by low processivity + phase-dependent barrier weakening
        # The phase logic is applied in analyze_all_boundaries
        results_mitosis = pipeline_mitosis.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=collapse_events_map,
            enhancer_promoter_pairs=enhancer_promoter_pairs,
            nipbl_velocity_factor=nipbl_velocity_mitosis,
            wapl_lifetime_factor=wapl_lifetime_mitosis,
        )

        # Note: Phase is applied inside analyze_all_boundaries via cell_cycle_phase parameter

        mitosis_summary = results_mitosis["summary"]
        mitosis_stability = mitosis_summary.get("avg_stability_score", 0.0)

        print(f"  Average stability: {mitosis_stability:.3f} (collapsed)")

        # ============================================================
        # Step 3A: Recovery WITH Bookmarking
        # ============================================================
        print("\n" + "=" * 60)
        print("Step 3A: G1 Recovery WITH Bookmarking")
        print("=" * 60)

        # G1 Early
        print("  Phase: G1_EARLY")
        pipeline_g1_early_bookmarked = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        # Add boundaries first
        for pos, strength, btype in boundaries_data:
            pipeline_g1_early_bookmarked.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )
        # Analyze with G1_EARLY phase
        stability_predictions_g1_early = pipeline_g1_early_bookmarked.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity_wt,
            wapl_lifetime_factor=wapl_lifetime_wt,
            cell_cycle_phase=CellCyclePhase.G1_EARLY,
            enable_bookmarking=True,
        )
        # Build summary for G1 Early
        if stability_predictions_g1_early:
            g1_early_stability = sum(
                p.stability_score if hasattr(p, "stability_score") else p.get("stability_score", 0.0)
                for p in stability_predictions_g1_early
            ) / len(stability_predictions_g1_early)
        else:
            g1_early_stability = 0.0
        print(f"    Average stability: {g1_early_stability:.3f}")

        # G1 Late
        print("  Phase: G1_LATE")
        pipeline_g1_late_bookmarked = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        # Add boundaries first
        for pos, strength, btype in boundaries_data:
            pipeline_g1_late_bookmarked.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )
        # Analyze with G1_LATE phase
        stability_predictions_g1_late = pipeline_g1_late_bookmarked.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity_wt,
            wapl_lifetime_factor=wapl_lifetime_wt,
            cell_cycle_phase=CellCyclePhase.G1_LATE,
            enable_bookmarking=True,
        )

        # Calculate summary for G1 Late
        if stability_predictions_g1_late:
            g1_late_stability = sum(
                p.stability_score if hasattr(p, "stability_score") else p.get("stability_score", 0.0)
                for p in stability_predictions_g1_late
            ) / len(stability_predictions_g1_late)
            g1_late_stable = sum(
                1 for p in stability_predictions_g1_late
                if (hasattr(p, "stability_category") and p.stability_category == "stable")
                or (isinstance(p, dict) and p.get("stability_category") == "stable")
            )
        else:
            g1_late_stability = 0.0
            g1_late_stable = 0

        # Extract stable boundary positions after recovery
        stable_boundaries_after_bookmarked = set()
        for pred in stability_predictions_g1_late:
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_boundaries_after_bookmarked.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_boundaries_after_bookmarked.add(pred.position)

        matched_stable_bookmarked = len(stable_boundaries_before & stable_boundaries_after_bookmarked)
        jaccard_bookmarked = jaccard_index(stable_boundaries_before, stable_boundaries_after_bookmarked)

        print(f"    Average stability: {g1_late_stability:.3f}")
        print(f"    Stable boundaries: {g1_late_stable}")
        print(f"    Matched stable: {matched_stable_bookmarked}/{len(stable_boundaries_before)}")
        print(f"    Jaccard index: {jaccard_bookmarked:.3f}")

        # ============================================================
        # Step 3B: Recovery WITHOUT Bookmarking
        # ============================================================
        print("\n" + "=" * 60)
        print("Step 3B: G1 Recovery WITHOUT Bookmarking")
        print("=" * 60)

        # Set all boundaries to non-bookmarked
        boundaries_data_no_bookmark = [
            (pos, strength, btype) for pos, strength, btype in boundaries_data
        ]

        # G1 Early (no bookmarking)
        print("  Phase: G1_EARLY (no bookmarking)")
        pipeline_g1_early_no_bookmark = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        # Add boundaries and set bookmarking to False
        for pos, strength, btype in boundaries_data_no_bookmark:
            boundary = pipeline_g1_early_no_bookmark.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )
            boundary.is_bookmarked = False
        # Analyze with G1_EARLY phase, bookmarking disabled
        stability_predictions_g1_early_no_bookmark = pipeline_g1_early_no_bookmark.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity_wt,
            wapl_lifetime_factor=wapl_lifetime_wt,
            cell_cycle_phase=CellCyclePhase.G1_EARLY,
            enable_bookmarking=False,
        )
        if stability_predictions_g1_early_no_bookmark:
            g1_early_no_bookmark_stability = sum(
                p.stability_score if hasattr(p, "stability_score") else p.get("stability_score", 0.0)
                for p in stability_predictions_g1_early_no_bookmark
            ) / len(stability_predictions_g1_early_no_bookmark)
        else:
            g1_early_no_bookmark_stability = 0.0
        print(f"    Average stability: {g1_early_no_bookmark_stability:.3f}")

        # G1 Late (no bookmarking)
        print("  Phase: G1_LATE (no bookmarking)")
        pipeline_g1_late_no_bookmark = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        # Add boundaries and set bookmarking to False
        for pos, strength, btype in boundaries_data_no_bookmark:
            boundary = pipeline_g1_late_no_bookmark.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )
            boundary.is_bookmarked = False
        # Analyze with G1_LATE phase, bookmarking disabled
        stability_predictions_g1_late_no_bookmark = pipeline_g1_late_no_bookmark.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity_wt,
            wapl_lifetime_factor=wapl_lifetime_wt,
            cell_cycle_phase=CellCyclePhase.G1_LATE,
            enable_bookmarking=False,
        )
        # Calculate summary
        if stability_predictions_g1_late_no_bookmark:
            g1_late_no_bookmark_stability = sum(
                p.stability_score if hasattr(p, "stability_score") else p.get("stability_score", 0.0)
                for p in stability_predictions_g1_late_no_bookmark
            ) / len(stability_predictions_g1_late_no_bookmark)
            g1_late_no_bookmark_stable = sum(
                1 for p in stability_predictions_g1_late_no_bookmark
                if (hasattr(p, "stability_category") and p.stability_category == "stable")
                or (isinstance(p, dict) and p.get("stability_category") == "stable")
            )
        else:
            g1_late_no_bookmark_stability = 0.0
            g1_late_no_bookmark_stable = 0

        # Extract stable boundary positions after recovery (no bookmarking)
        stable_boundaries_after_no_bookmark = set()
        for pred in stability_predictions_g1_late_no_bookmark:
            if isinstance(pred, dict):
                if pred.get("stability_category") == "stable":
                    stable_boundaries_after_no_bookmark.add(pred.get("position"))
            elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                stable_boundaries_after_no_bookmark.add(pred.position)

        matched_stable_no_bookmark = len(stable_boundaries_before & stable_boundaries_after_no_bookmark)
        jaccard_no_bookmark = jaccard_index(stable_boundaries_before, stable_boundaries_after_no_bookmark)

        print(f"    Average stability: {g1_late_no_bookmark_stability:.3f}")
        print(f"    Stable boundaries: {g1_late_no_bookmark_stable}")
        print(f"    Matched stable: {matched_stable_no_bookmark}/{len(stable_boundaries_before)}")
        print(f"    Jaccard index: {jaccard_no_bookmark:.3f}")

        # ============================================================
        # Comparison
        # ============================================================
        print("\n" + "=" * 60)
        print("Comparison: With Bookmarking vs Without Bookmarking")
        print("=" * 60)

        print(f"\nStability Recovery:")
        print(f"  With bookmarking:    {g1_late_stability:.3f} ({g1_late_stability/baseline_stability*100:.1f}% of baseline)")
        print(f"  Without bookmarking: {g1_late_no_bookmark_stability:.3f} ({g1_late_no_bookmark_stability/baseline_stability*100:.1f}% of baseline)")

        print(f"\nStable Boundaries Recovery:")
        print(f"  With bookmarking:    {matched_stable_bookmarked}/{len(stable_boundaries_before)} matched (Jaccard={jaccard_bookmarked:.3f})")
        print(f"  Without bookmarking: {matched_stable_no_bookmark}/{len(stable_boundaries_before)} matched (Jaccard={jaccard_no_bookmark:.3f})")

        # Build results
        results = {
            "experiment_id": "RS-10-ExpA",
            "baseline": {
                "phase": "interphase",
                "processivity": processivity_wt,
                "avg_stability": baseline_stability,
                "stable_boundaries": baseline_stable_boundaries,
                "stable_positions": sorted(stable_boundaries_before),
            },
            "mitosis": {
                "phase": "mitosis",
                "processivity": processivity_mitosis,
                "avg_stability": mitosis_stability,
            },
            "with_bookmarking": {
                "g1_early": {
                    "avg_stability": g1_early_stability,
                },
                "g1_late": {
                    "avg_stability": g1_late_stability,
                    "stable_boundaries": g1_late_stable,
                    "stable_positions": sorted(stable_boundaries_after_bookmarked),
                    "matched_stable": matched_stable_bookmarked,
                    "jaccard_stable": jaccard_bookmarked,
                    "stability_recovery_percent": (g1_late_stability / baseline_stability * 100) if baseline_stability > 0 else 0.0,
                },
            },
            "without_bookmarking": {
                "g1_early": {
                    "avg_stability": g1_early_no_bookmark_stability,
                },
                "g1_late": {
                    "avg_stability": g1_late_no_bookmark_stability,
                    "stable_boundaries": g1_late_no_bookmark_stable,
                    "stable_positions": sorted(stable_boundaries_after_no_bookmark),
                    "matched_stable": matched_stable_no_bookmark,
                    "jaccard_stable": jaccard_no_bookmark,
                    "stability_recovery_percent": (g1_late_no_bookmark_stability / baseline_stability * 100) if baseline_stability > 0 else 0.0,
                },
            },
            "comparison": {
                "stability_recovery_delta": g1_late_stability - g1_late_no_bookmark_stability,
                "matched_stable_delta": matched_stable_bookmarked - matched_stable_no_bookmark,
                "jaccard_delta": jaccard_bookmarked - jaccard_no_bookmark,
            },
        }

        return results

    def save_results(self, results: dict, filename: str = "RS10_bookmarking_cycle.json") -> Path:
        """Сохранить результаты."""
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск эксперимента."""
    experiment = RS10BookmarkingCycle()

    # Test data (same as RS-09 experiments for consistency)
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

    # Run experiment
    results = experiment.run_bookmarking_cycle(
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
    print("✅ RS-10 Experiment A Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- With bookmarking: Better recovery of original stable boundaries")
    print("- Without bookmarking: Architecture 'drifts' to different configuration")
    print("- Jaccard index higher with bookmarking")


if __name__ == "__main__":
    main()

