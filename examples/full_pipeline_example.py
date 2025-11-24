"""Example: Full ARCHCODE Pipeline - Extrusion → Stability → Collapse → Risk."""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.boundary_collapse import EnhancerPromoterPair
from src.output import ARCHCODEExporter
from src.vizir.config_loader import VIZIRConfigLoader
from src.vizir.integrity import compute_config_hashes


def main() -> None:
    """Example of full ARCHCODE pipeline."""
    print("=" * 60)
    print("ARCHCODE Full Pipeline Example")
    print("=" * 60)

    # Load VIZIR configs
    loader = VIZIRConfigLoader()
    vizir_configs = {
        **loader.load_all_physical(),
        **loader.load_all_structural(),
        **loader.load_all_logical(),
    }

    # Initialize full pipeline
    pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)

    # Define boundaries
    boundaries_data = [
        (100000, 0.9, "ctcf"),  # Strong, stable
        (200000, 0.7, "ctcf"),  # Medium
        (300000, 0.5, "ctcf"),  # Weak, variable
        (400000, 0.3, "ctcf"),  # Very weak
        (500000, 0.8, "ctcf"),  # Strong
    ]

    # Define factors
    barrier_strengths_map = {
        100000: [0.5, 0.3],  # G4 + Z-DNA
        200000: [0.3],
        300000: [0.2],
        400000: [0.1],
        500000: [0.4, 0.2],
    }

    methylation_map = {
        100000: 0.1,  # Low methylation
        200000: 0.3,
        300000: 0.6,  # High methylation
        400000: 0.8,  # Very high
        500000: 0.2,
    }

    te_motif_map = {
        100000: [0.2, 0.1],  # Positive motifs
        200000: [0.1],
        300000: [0.0],
        400000: [-0.3],  # Negative (WAPL-recruiting)
        500000: [0.15],
    }

    # Define collapse events
    collapse_events = {
        300000: [{"type": "methylation_spike", "delta": 0.3}],  # Trigger collapse
        400000: [
            {"type": "methylation_spike", "delta": 0.2},
            {"type": "ctcf_loss", "affinity_drop": 0.3},
        ],
    }

    # Define enhancer-promoter pairs (for risk calculation)
    enhancer_promoter_pairs = [
        EnhancerPromoterPair(
            enhancer_position=300000,
            promoter_position=350000,
            gene_name="TEST_GENE",
            distance=50000,
            is_oncogenic=False,
        ),
        EnhancerPromoterPair(
            enhancer_position=400000,
            promoter_position=450000,
            gene_name="ONCO_GENE",
            distance=50000,
            is_oncogenic=True,
        ),
    ]

    print("\n1. Running full pipeline analysis...")
    results = pipeline.run_full_analysis(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        collapse_events=collapse_events,
        enhancer_promoter_pairs=enhancer_promoter_pairs,
    )

    # Display results
    print("\n2. Results Summary:")
    summary = results["summary"]
    print(f"   Total boundaries: {summary['total_boundaries']}")
    print(f"   Stable: {summary['stable_boundaries']}")
    print(f"   Variable: {summary['variable_boundaries']}")
    print(f"   Avg stability: {summary['avg_stability_score']:.3f}")
    print(f"   Collapsed: {summary['collapsed_boundaries']}")
    print(f"   High risk: {summary['high_risk_boundaries']}")

    print("\n3. Stability Predictions:")
    for pred in results["stability_predictions"]:
        print(
            f"   Position {pred['position']:6d}: "
            f"{pred['stability_category']:12s} "
            f"(score={pred['stability_score']:.3f})"
        )

    print("\n4. Collapse Results:")
    for pos, collapse in results["collapse_results"].items():
        print(f"   Position {pos}:")
        print(f"     Collapse probability: {collapse['collapse_probability']:.3f}")
        print(f"     Collapse occurred: {collapse['collapse_occurred']}")
        print(f"     Hijacking risk: {collapse['enhancer_hijacking_risk']:.3f}")
        print(f"     Oncogenic risk: {collapse['oncogenic_risk']:.3f}")
        print(f"     Total risk: {collapse['total_risk_score']:.3f}")

    # Export results
    print("\n5. Exporting results...")
    exporter = ARCHCODEExporter()
    config_hash = hashlib.sha256(
        json.dumps(compute_config_hashes(), sort_keys=True).encode()
    ).hexdigest()

    exported = exporter.export_full_pipeline_results(
        results=results,
        experiment_id="full_pipeline_demo",
        formats=["json", "csv", "vizir"],
        config_hash=config_hash,
    )

    print("   Exported files:")
    for format_name, path in exported.items():
        print(f"     {format_name}: {path}")

    print("\n" + "=" * 60)
    print("✅ Full Pipeline Example Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
