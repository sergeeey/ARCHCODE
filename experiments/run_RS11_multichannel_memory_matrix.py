"""RS-11A: Multichannel Memory Matrix Experiment.

Sweep over (bookmarking_fraction, epigenetic_strength) space to build
memory retention matrix across multiple cell cycles.
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.bookmarking import assign_bookmarking
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.epigenetic_memory import (
    initialize_epigenetic_memory,
    restore_with_epigenetic_memory,
)
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.memory_metrics import (
    calculate_drift_distance,
    calculate_entropy,
    calculate_jaccard_stable_boundaries,
    calculate_memory_retention_score,
    get_stable_boundaries,
)
from src.vizir.config_loader import VIZIRConfigLoader


def simulate_multichannel_cycle(
    pipeline: ARCHCODEFullPipeline,
    boundaries_data: list[tuple[int, float, str]],
    barrier_strengths_map: dict[int, list[float]],
    methylation_map: dict[int, float],
    te_motif_map: dict[int, list[float]],
    bookmarking_fraction: float,
    epigenetic_strength: float,
    epigenetic_scores: dict[int, float],
    nipbl_velocity: float,
    wapl_lifetime: float,
    cycle_number: int,
    rng: random.Random,
) -> tuple[list[Boundary], dict]:
    """
    Simulate one cell cycle with multichannel memory (CTCF + Epigenetic).

    Args:
        pipeline: ARCHCODE pipeline
        boundaries_data: Boundary definitions
        barrier_strengths_map: Barrier strengths map
        methylation_map: Methylation map
        te_motif_map: TE motif map
        bookmarking_fraction: Fraction of CTCF-bookmarked boundaries
        epigenetic_strength: Global epigenetic memory strength multiplier
        epigenetic_scores: Dictionary of epigenetic scores per boundary
        nipbl_velocity: NIPBL velocity factor
        wapl_lifetime: WAPL lifetime factor
        cycle_number: Current cycle number
        rng: Random number generator

    Returns:
        Tuple of (restored_boundaries, metrics_dict)
    """
    # Assign bookmarking
    assign_bookmarking(pipeline.pipeline.boundaries, bookmarking_fraction)

    # Store baseline boundaries for comparison
    boundaries_before = [Boundary(
        position=b.position,
        strength=b.strength,
        barrier_type=b.barrier_type,
        insulation_score=b.insulation_score,
        is_bookmarked=b.is_bookmarked,
    ) for b in pipeline.pipeline.boundaries]

    # Mitosis: Low processivity
    nipbl_mitosis = 0.3
    wapl_mitosis = 0.3

    mitosis_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_mitosis,
        wapl_lifetime_factor=wapl_mitosis,
        cell_cycle_phase=CellCyclePhase.MITOSIS,
        enable_bookmarking=True,
    )

    # G1 Early recovery
    g1_early_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_velocity,
        wapl_lifetime_factor=wapl_lifetime,
        cell_cycle_phase=CellCyclePhase.G1_EARLY,
        enable_bookmarking=True,
    )

    # Multichannel restoration: CTCF bookmarking + Epigenetic memory
    restored_boundaries, restoration_probs = restore_with_epigenetic_memory(
        boundaries_before,
        epigenetic_scores,
        rng=rng,
        params={
            "bookmarking_fraction": bookmarking_fraction,
            "epigenetic_strength": epigenetic_strength,
            "restoration_function": "linear",
            "boundary_loss_rate": 0.2,
            "boundary_shift_std": 15000.0,
        },
    )

    # Update pipeline boundaries
    pipeline.pipeline.boundaries = restored_boundaries

    # G1 Late recovery (final state)
    g1_late_predictions = pipeline.pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity_factor=nipbl_velocity,
        wapl_lifetime_factor=wapl_lifetime,
        cell_cycle_phase=CellCyclePhase.G1_LATE,
        enable_bookmarking=True,
    )

    # Calculate metrics
    stable_before = get_stable_boundaries(boundaries_before, stability_threshold=0.7)
    stable_after = get_stable_boundaries(restored_boundaries, stability_threshold=0.7)

    jaccard = calculate_jaccard_stable_boundaries(stable_before, stable_after)
    drift = calculate_drift_distance(boundaries_before, restored_boundaries)
    entropy = calculate_entropy(restored_boundaries, entropy_type="position")
    memory_score = calculate_memory_retention_score(jaccard, entropy, drift)

    metrics = {
        "jaccard": jaccard,
        "drift_distance": drift,
        "entropy": entropy,
        "memory_retention_score": memory_score,
        "stable_count_before": len(stable_before),
        "stable_count_after": len(stable_after),
        "restored_count": len(restored_boundaries),
        "restoration_probabilities": restoration_probs,
    }

    return restored_boundaries, metrics


def run_RS11A_matrix(
    num_cycles: int = 50,
    bookmarking_fractions: list[float] | None = None,
    epigenetic_strengths: list[float] | None = None,
    processivity: float = 0.9,
    output_dir: Path | None = None,
    seed: int = 42,
) -> dict:
    """
    Run RS-11A: Multichannel Memory Matrix experiment.

    Args:
        num_cycles: Number of cell cycles to simulate
        bookmarking_fractions: List of bookmarking fractions to test
        epigenetic_strengths: List of epigenetic strengths to test
        processivity: Fixed processivity value (NIPBL × WAPL)
        output_dir: Output directory for results
        seed: Random seed

    Returns:
        Dictionary with results matrix
    """
    if bookmarking_fractions is None:
        bookmarking_fractions = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    if epigenetic_strengths is None:
        epigenetic_strengths = [0.0, 0.25, 0.5, 0.75, 1.0]

    if output_dir is None:
        output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Derive NIPBL and WAPL from processivity (assuming balanced)
    nipbl_velocity = (processivity ** 0.5)  # sqrt(processivity)
    wapl_lifetime = (processivity ** 0.5)  # sqrt(processivity)

    # Setup test boundaries (chr8:127000000-130000000 region)
    base_positions = [127100000, 127200000, 127300000, 127400000, 127500000]
    boundaries_data = [
        (pos, 0.8, "ctcf") for pos in base_positions
    ]

    barrier_strengths_map = {pos: [0.5] for pos in base_positions}
    methylation_map = {pos: 0.5 for pos in base_positions}
    te_motif_map = {pos: [0.0] for pos in base_positions}

    # Load VIZIR configs
    loader = VIZIRConfigLoader()
    vizir_configs = {
        **loader.load_all_physical(),
        **loader.load_all_structural(),
        **loader.load_all_logical(),
    }

    # Initialize random number generator
    rng = random.Random(seed)

    # Results storage
    results = {
        "parameters": {
            "num_cycles": num_cycles,
            "processivity": processivity,
            "nipbl_velocity": nipbl_velocity,
            "wapl_lifetime": wapl_lifetime,
            "bookmarking_fractions": bookmarking_fractions,
            "epigenetic_strengths": epigenetic_strengths,
            "seed": seed,
        },
        "results": {},
    }

    total_combinations = len(bookmarking_fractions) * len(epigenetic_strengths)
    current = 0

    print("=" * 80)
    print("RS-11A: Multichannel Memory Matrix Experiment")
    print("=" * 80)
    print(f"Cycles: {num_cycles}")
    print(f"Processivity: {processivity:.2f} (NIPBL={nipbl_velocity:.2f}, WAPL={wapl_lifetime:.2f})")
    print(f"Total combinations: {total_combinations}")
    print("=" * 80)

    # Sweep over parameter space
    for bookmarking_frac in bookmarking_fractions:
        for epigenetic_str in epigenetic_strengths:
            current += 1
            key = f"{bookmarking_frac:.2f}_{epigenetic_str:.2f}"

            print(
                f"\n[{current}/{total_combinations}] "
                f"B={bookmarking_frac:.2f}, E={epigenetic_str:.2f}"
            )

            # Create fresh pipeline
            pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)

            # Add boundaries
            for pos, strength, btype in boundaries_data:
                pipeline.pipeline.add_boundary(
                    position=pos, strength=strength, barrier_type=btype
                )

            # Initialize epigenetic memory scores (correlated with strength)
            epigenetic_scores = initialize_epigenetic_memory(
                pipeline.pipeline.boundaries,
                mode="correlated_with_strength",
                strength=1.0,
                seed=seed,
            )

            # Store baseline stable boundaries
            # First analyze baseline to get predictions
            baseline_predictions = pipeline.pipeline.analyze_all_boundaries(
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                nipbl_velocity_factor=nipbl_velocity,
                wapl_lifetime_factor=wapl_lifetime,
                cell_cycle_phase=CellCyclePhase.G1_LATE,
                enable_bookmarking=True,
            )
            
            baseline_stable = set()
            if baseline_predictions:
                for pred in baseline_predictions:
                    if isinstance(pred, dict):
                        if pred.get("stability_category") == "stable":
                            pos = pred.get("position")
                            if pos:
                                baseline_stable.add(pos)
                    elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                        baseline_stable.add(pred.position)
            
            # If no stable boundaries found, use all boundaries as baseline
            if not baseline_stable:
                baseline_stable = {b.position for b in pipeline.pipeline.boundaries}

            # Track metrics across cycles
            cycle_metrics = []

            # Simulate N cycles
            for cycle in range(num_cycles):
                restored_boundaries, metrics = simulate_multichannel_cycle(
                    pipeline=pipeline,
                    boundaries_data=boundaries_data,
                    barrier_strengths_map=barrier_strengths_map,
                    methylation_map=methylation_map,
                    te_motif_map=te_motif_map,
                    bookmarking_fraction=bookmarking_frac,
                    epigenetic_strength=epigenetic_str,
                    epigenetic_scores=epigenetic_scores,
                    nipbl_velocity=nipbl_velocity,
                    wapl_lifetime=wapl_lifetime,
                    cycle_number=cycle,
                    rng=rng,
                )

                # Calculate Jaccard vs baseline
                # Get predictions from the cycle simulation
                # The predictions are stored in metrics, but we need to get them from the pipeline
                # Re-analyze to get current predictions
                current_predictions = pipeline.pipeline.analyze_all_boundaries(
                    barrier_strengths_map=barrier_strengths_map,
                    methylation_map=methylation_map,
                    te_motif_map=te_motif_map,
                    nipbl_velocity_factor=nipbl_velocity,
                    wapl_lifetime_factor=wapl_lifetime,
                    cell_cycle_phase=CellCyclePhase.G1_LATE,
                    enable_bookmarking=True,
                )
                
                # Extract stable boundaries from predictions
                current_stable = set()
                if current_predictions:
                    for pred in current_predictions:
                        if isinstance(pred, dict):
                            if pred.get("stability_category") == "stable":
                                pos = pred.get("position")
                                if pos:
                                    current_stable.add(pos)
                        elif hasattr(pred, "stability_category") and pred.stability_category == "stable":
                            current_stable.add(pred.position)
                
                # Fallback: use boundary positions if no predictions
                if not current_stable:
                    current_stable = {b.position for b in restored_boundaries}
                
                jaccard_vs_baseline = calculate_jaccard_stable_boundaries(
                    baseline_stable, current_stable
                )

                cycle_metrics.append({
                    "cycle": cycle,
                    "jaccard": metrics["jaccard"],
                    "jaccard_vs_baseline": jaccard_vs_baseline,
                    "drift_distance": metrics["drift_distance"],
                    "entropy": metrics["entropy"],
                    "memory_retention_score": metrics["memory_retention_score"],
                    "stable_count": metrics["stable_count_after"],
                })

            # Store final metrics (after N cycles)
            final_metrics = cycle_metrics[-1]
            results["results"][key] = {
                "bookmarking_fraction": bookmarking_frac,
                "epigenetic_strength": epigenetic_str,
                "final_jaccard": final_metrics["jaccard"],
                "final_jaccard_vs_baseline": final_metrics["jaccard_vs_baseline"],
                "final_drift_distance": final_metrics["drift_distance"],
                "final_entropy": final_metrics["entropy"],
                "final_memory_retention_score": final_metrics["memory_retention_score"],
                "final_stable_count": final_metrics["stable_count"],
                "trajectory": cycle_metrics,
            }

            print(
                f"  Final Jaccard (vs baseline): {final_metrics['jaccard_vs_baseline']:.3f}, "
                f"Memory Score: {final_metrics['memory_retention_score']:.3f}"
            )

    # Save results
    output_file = output_dir / "RS11_multichannel_memory_matrix.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Results saved to: {output_file}")

    return results


if __name__ == "__main__":
    # Quick test run with fewer cycles
    print("Running RS-11A test (10 cycles, reduced parameter space)...")
    results = run_RS11A_matrix(
        num_cycles=10,
        bookmarking_fractions=[0.0, 0.3, 0.6],
        epigenetic_strengths=[0.0, 0.5, 1.0],
        processivity=0.9,
        seed=42,
    )
    print("\n✅ Test run completed!")

