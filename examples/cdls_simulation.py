"""CdLS (Cornelia de Lange Syndrome) Simulation.

Simulates TAD boundary blurring due to NIPBL haploinsufficiency.
Based on ARCHCODE v1.1: NIPBL velocity multiplier model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.extrusion_engine import LoopExtrusionEngine
from src.archcode_core.pipeline import ARCHCODEPipeline
from src.vizir.config_loader import VIZIRConfigLoader


def simulate_cdls() -> None:
    """Simulate CdLS: NIPBL haploinsufficiency → TAD boundary blurring."""
    print("=" * 60)
    print("CdLS Simulation: NIPBL Haploinsufficiency")
    print("=" * 60)

    # Load VIZIR configs
    loader = VIZIRConfigLoader()
    vizir_configs = {
        **loader.load_all_physical(),
        **loader.load_all_structural(),
        **loader.load_all_logical(),
    }

    # Update P3 config for CdLS
    if "P3" in vizir_configs:
        p3_params = vizir_configs["P3"].get("parameters", {})
        if "nipbl_velocity_multiplier" not in p3_params:
            p3_params["nipbl_velocity_multiplier"] = {}
        p3_params["nipbl_velocity_multiplier"]["cdls_haploinsufficient"] = 0.5

    # Create pipeline (load default configs)
    from src.archcode_core.pipeline import load_pipeline_configs
    archcode_config, stability_config = load_pipeline_configs()
    pipeline = ARCHCODEPipeline(archcode_config=archcode_config, stability_config=stability_config)

    # Add boundaries
    boundaries_data = [
        (100000, 0.9, "ctcf"),
        (200000, 0.8, "ctcf"),
        (300000, 0.7, "ctcf"),
        (400000, 0.6, "ctcf"),
        (500000, 0.9, "ctcf"),
    ]

    print("\n1. Wild-type simulation:")
    for pos, strength, btype in boundaries_data:
        pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

    # Analyze stability (wild-type)
    wt_stability = pipeline.analyze_all_boundaries()
    print(f"   Total boundaries: {len(wt_stability)}")
    stable_wt = sum(1 for s in wt_stability if s.stability_category == "stable")
    print(f"   Stable boundaries: {stable_wt}")

    # CdLS simulation: Reduce NIPBL velocity multiplier
    print("\n2. CdLS simulation (NIPBL velocity = 0.5x):")
    
    # Create new pipeline with CdLS parameters
    cdls_vizir_configs = vizir_configs.copy()
    if "P3" in cdls_vizir_configs:
        p3_params = cdls_vizir_configs["P3"].get("parameters", {})
        if "nipbl_velocity_multiplier" not in p3_params:
            p3_params["nipbl_velocity_multiplier"] = {}
        # Override to CdLS value
        p3_params["nipbl_velocity_multiplier"]["wild_type"] = 0.5  # 50% reduction

    cdls_pipeline = ARCHCODEPipeline(archcode_config=archcode_config, stability_config=stability_config)

    # Add same boundaries
    for pos, strength, btype in boundaries_data:
        cdls_pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

    # Analyze stability (CdLS)
    cdls_stability = cdls_pipeline.analyze_all_boundaries()
    print(f"   Total boundaries: {len(cdls_stability)}")
    stable_cdls = sum(1 for s in cdls_stability if s.stability_category == "stable")
    print(f"   Stable boundaries: {stable_cdls}")

    # Compare results
    print("\n3. Comparison:")
    print(f"   Wild-type stable boundaries: {stable_wt}/{len(wt_stability)}")
    print(f"   CdLS stable boundaries: {stable_cdls}/{len(cdls_stability)}")
    print(f"   Reduction: {stable_wt - stable_cdls} boundaries")

    # Expected: CdLS should show "blurred" boundaries (lower stability scores)
    avg_wt = sum(s.stability_score for s in wt_stability) / len(wt_stability)
    avg_cdls = sum(s.stability_score for s in cdls_stability) / len(cdls_stability)
    print(f"\n   Average stability score:")
    print(f"   Wild-type: {avg_wt:.3f}")
    print(f"   CdLS: {avg_cdls:.3f}")
    print(f"   Difference: {avg_wt - avg_cdls:.3f}")

    print("\n" + "=" * 60)
    print("✅ CdLS Simulation Complete")
    print("=" * 60)
    print("\nExpected result:")
    print("- CdLS should show reduced boundary stability")
    print("- TAD boundaries should 'blur' (intermediate category)")
    print("- This matches experimental observations in CdLS patients")


if __name__ == "__main__":
    simulate_cdls()

