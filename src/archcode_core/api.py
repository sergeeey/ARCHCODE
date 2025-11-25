"""
ARCHCODE API Layer for External Integration.

Provides standardized functions for running ARCHCODE experiments
and returning JSON-serializable results for TERAG integration.
"""

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.bookmarking import assign_bookmarking, apply_stochastic_recovery
from src.archcode_core.epigenetic_memory import (
    initialize_epigenetic_memory,
    restore_with_epigenetic_memory,
)
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.memory_metrics import (
    calculate_jaccard_stable_boundaries,
    get_stable_boundaries,
)
from src.vizir.config_loader import VIZIRConfigLoader

# Import experiment runners
from experiments.run_RS11B_phase_diagram import RS11BPhaseDiagram
from experiments.compare_archcode_vs_real import ARCHCODEvsRealComparison


def run_rs09_summary(config: dict[str, Any]) -> dict[str, Any]:
    """
    Запускает RS-09 (processivity sweep) и возвращает краткий summary.

    Args:
        config: Configuration dictionary with:
            - processivity_range: tuple(min, max, steps) or list of values
            - nipbl_velocity_range: optional
            - wapl_lifetime_range: optional
            - mode: "fast" | "production"
            - boundaries_data: optional (uses default if not provided)

    Returns:
        Dictionary with:
            - phase_diagram: {processivity: phase_category}
            - critical_points: {collapse_threshold, transition_threshold, stable_threshold}
            - stability_metrics: {mean_stability, std_stability, ...}
            - stable_fraction: fraction of processivity range in stable phase
    """
    mode = config.get("mode", "fast")
    
    # Determine grid size based on mode
    if mode == "fast":
        processivity_steps = config.get("processivity_steps", 10)
    else:
        processivity_steps = config.get("processivity_steps", 50)
    
    # Get processivity range
    if "processivity_range" in config:
        p_min, p_max, steps = config["processivity_range"]
        processivity_values = [p_min + i * (p_max - p_min) / (steps - 1) for i in range(steps)]
    else:
        p_min = config.get("processivity_min", 0.0)
        p_max = config.get("processivity_max", 2.0)
        processivity_values = [p_min + i * (p_max - p_min) / (processivity_steps - 1) 
                             for i in range(processivity_steps)]
    
    # Load VIZIR configs
    loader = VIZIRConfigLoader()
    vizir_configs = {
        **loader.load_all_physical(),
        **loader.load_all_structural(),
        **loader.load_all_logical(),
    }
    
    # Default boundaries
    boundaries_data = config.get("boundaries_data", [
        (127100000, 0.8, "ctcf"),
        (127200000, 0.7, "ctcf"),
        (127300000, 0.6, "ctcf"),
        (127400000, 0.5, "ctcf"),
        (127500000, 0.9, "ctcf"),
    ])
    
    barrier_strengths_map = {pos: [0.5] for pos, _, _ in boundaries_data}
    methylation_map = {pos: 0.5 for pos, _, _ in boundaries_data}
    te_motif_map = {pos: [0.0] for pos, _, _ in boundaries_data}
    
    # Sweep processivity
    phase_diagram = {}
    stability_scores = []
    
    for processivity in processivity_values:
        # Derive velocity and lifetime
        nipbl_velocity = config.get("nipbl_velocity", processivity ** 0.5)
        wapl_lifetime = config.get("wapl_lifetime", processivity ** 0.5)
        
        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        
        # Add boundaries
        for pos, strength, btype in boundaries_data:
            pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)
        
        # Analyze
        predictions = pipeline.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
            cell_cycle_phase=CellCyclePhase.INTERPHASE,
            enable_bookmarking=False,
        )
        
        # Calculate average stability
        if predictions:
            avg_stability = sum(
                p.stability_score if hasattr(p, "stability_score") else 0.0
                for p in predictions
            ) / len(predictions)
            stability_scores.append(avg_stability)
            
            # Classify phase
            if processivity < 0.5:
                phase = "collapse"
            elif processivity < 1.0:
                phase = "transition"
            else:
                phase = "stable"
            
            phase_diagram[float(processivity)] = {
                "phase": phase,
                "stability": float(avg_stability),
            }
        else:
            stability_scores.append(0.0)
            phase_diagram[float(processivity)] = {
                "phase": "unknown",
                "stability": 0.0,
            }
    
    # Find critical points
    critical_points = {}
    for i, p in enumerate(processivity_values):
        if i > 0:
            prev_phase = phase_diagram[processivity_values[i-1]]["phase"]
            curr_phase = phase_diagram[p]["phase"]
            
            if prev_phase != curr_phase:
                if prev_phase == "collapse" and curr_phase == "transition":
                    critical_points["collapse_threshold"] = float((processivity_values[i-1] + p) / 2)
                elif prev_phase == "transition" and curr_phase == "stable":
                    critical_points["stable_threshold"] = float((processivity_values[i-1] + p) / 2)
    
    # Calculate metrics
    import statistics
    stable_fraction = sum(1 for v in phase_diagram.values() if v["phase"] == "stable") / len(phase_diagram)
    
    return {
        "phase_diagram": {str(k): v for k, v in phase_diagram.items()},
        "critical_points": critical_points,
        "stability_metrics": {
            "mean": float(statistics.mean(stability_scores)) if stability_scores else 0.0,
            "std": float(statistics.stdev(stability_scores)) if len(stability_scores) > 1 else 0.0,
            "min": float(min(stability_scores)) if stability_scores else 0.0,
            "max": float(max(stability_scores)) if stability_scores else 0.0,
        },
        "stable_fraction": float(stable_fraction),
        "processivity_range": {
            "min": float(min(processivity_values)),
            "max": float(max(processivity_values)),
            "steps": len(processivity_values),
        },
    }


def run_rs10_summary(config: dict[str, Any]) -> dict[str, Any]:
    """
    Запускает RS-10 (bookmarking / drift / pathological) и возвращает summary.

    Args:
        config: Configuration dictionary with:
            - bookmarking_fractions: list of bookmarking values or range tuple
            - num_cycles: number of cell cycles to simulate
            - processivity: fixed processivity value
            - mode: "fast" | "production"

    Returns:
        Dictionary with:
            - bookmarking_grid: {fraction: metrics}
            - drift_curves: {fraction: [drift_per_cycle]}
            - entropy: {fraction: entropy_value}
            - estimated_threshold: critical bookmarking fraction
    """
    mode = config.get("mode", "fast")
    
    # Determine parameters based on mode
    if mode == "fast":
        bookmarking_steps = config.get("bookmarking_steps", 7)
        num_cycles = config.get("num_cycles", 10)
    else:
        bookmarking_steps = config.get("bookmarking_steps", 20)
        num_cycles = config.get("num_cycles", 50)
    
    # Get bookmarking fractions
    if "bookmarking_fractions" in config:
        bookmarking_fractions = config["bookmarking_fractions"]
    elif "bookmarking_range" in config:
        bookmarking_range = config["bookmarking_range"]
        # Handle both tuple/list format [min, max, steps] and explicit list
        if isinstance(bookmarking_range, (list, tuple)) and len(bookmarking_range) == 3:
            # Tuple format: [min, max, steps]
            b_min, b_max, steps = bookmarking_range
            bookmarking_fractions = [b_min + i * (b_max - b_min) / (steps - 1) for i in range(steps)]
        elif isinstance(bookmarking_range, list) and len(bookmarking_range) > 3:
            # Explicit list of fractions
            bookmarking_fractions = bookmarking_range
        else:
            # Fallback: use default steps
            bookmarking_fractions = [i / (bookmarking_steps - 1) for i in range(bookmarking_steps)]
    else:
        bookmarking_fractions = [i / (bookmarking_steps - 1) for i in range(bookmarking_steps)]
    
    processivity = config.get("processivity", 0.9)
    nipbl_velocity = config.get("nipbl_velocity", processivity ** 0.5)
    wapl_lifetime = config.get("wapl_lifetime", processivity ** 0.5)
    
    # Load VIZIR configs
    loader = VIZIRConfigLoader()
    vizir_configs = {
        **loader.load_all_physical(),
        **loader.load_all_structural(),
        **loader.load_all_logical(),
    }
    
    # Default boundaries
    boundaries_data = config.get("boundaries_data", [
        (127100000, 0.8, "ctcf"),
        (127200000, 0.7, "ctcf"),
        (127300000, 0.6, "ctcf"),
        (127400000, 0.5, "ctcf"),
        (127500000, 0.9, "ctcf"),
    ])
    
    barrier_strengths_map = {pos: [0.5] for pos, _, _ in boundaries_data}
    methylation_map = {pos: 0.5 for pos, _, _ in boundaries_data}
    te_motif_map = {pos: [0.0] for pos, _, _ in boundaries_data}
    
    # Sweep bookmarking
    bookmarking_grid = {}
    drift_curves = {}
    entropy_values = {}
    
    for bookmarking_frac in bookmarking_fractions:
        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        
        # Add boundaries
        for pos, strength, btype in boundaries_data:
            pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)
        
        # Baseline
        baseline_stable = get_stable_boundaries(
            pipeline.pipeline.boundaries, stability_threshold=0.7
        )
        
        # Simulate cycles
        current_boundaries = pipeline.pipeline.boundaries.copy()
        drift_per_cycle = []
        
        for cycle in range(num_cycles):
            # Assign bookmarking
            assign_bookmarking(current_boundaries, fraction=bookmarking_frac, seed=cycle)
            
            # Mitosis
            mitosis_predictions = pipeline.pipeline.analyze_all_boundaries(
                barrier_strengths_map=barrier_strengths_map,
                methylation_map=methylation_map,
                te_motif_map=te_motif_map,
                nipbl_velocity_factor=0.3,
                wapl_lifetime_factor=0.3,
                cell_cycle_phase=CellCyclePhase.MITOSIS,
                enable_bookmarking=True,
            )
            
            # Recovery
            boundaries_before = [
                Boundary(b.position, b.strength, b.barrier_type, b.insulation_score, b.is_bookmarked)
                for b in current_boundaries
            ]
            
            recovered_boundaries = apply_stochastic_recovery(
                boundaries_before,
                boundary_loss_rate=0.2,
                boundary_shift_std=15000.0,
                seed=cycle,
            )
            
            current_boundaries = recovered_boundaries
            
            # Calculate drift
            final_stable = get_stable_boundaries(
                current_boundaries, stability_threshold=0.7
            )
            jaccard = calculate_jaccard_stable_boundaries(baseline_stable, final_stable)
            drift_per_cycle.append(1.0 - jaccard)
        
        # Final metrics
        final_stable = get_stable_boundaries(
            current_boundaries, stability_threshold=0.7
        )
        final_jaccard = calculate_jaccard_stable_boundaries(baseline_stable, final_stable)
        
        from src.archcode_core.memory_metrics import calculate_entropy
        entropy = calculate_entropy(current_boundaries, entropy_type="position")
        
        bookmarking_grid[float(bookmarking_frac)] = {
            "final_jaccard": float(final_jaccard),
            "mean_drift": float(sum(drift_per_cycle) / len(drift_per_cycle)) if drift_per_cycle else 0.0,
            "entropy": float(entropy),
        }
        drift_curves[float(bookmarking_frac)] = [float(d) for d in drift_per_cycle]
        entropy_values[float(bookmarking_frac)] = float(entropy)
    
    # Estimate threshold (where jaccard drops below 0.5)
    estimated_threshold = None
    for frac in sorted(bookmarking_fractions):
        if bookmarking_grid[frac]["final_jaccard"] < 0.5:
            estimated_threshold = float(frac)
            break
    
    return {
        "bookmarking_grid": {str(k): v for k, v in bookmarking_grid.items()},
        "drift_curves": {str(k): v for k, v in drift_curves.items()},
        "entropy": {str(k): v for k, v in entropy_values.items()},
        "estimated_threshold": float(estimated_threshold) if estimated_threshold else None,
        "num_cycles": num_cycles,
    }


def run_rs11_summary(config: dict[str, Any]) -> dict[str, Any]:
    """
    Запускает RS-11 (multichannel memory) и возвращает summary.

    Args:
        config: Configuration dictionary with:
            - bookmarking_range: tuple(min, max, steps)
            - epigenetic_range: tuple(min, max, steps)
            - processivity: fixed processivity value
            - num_cycles: number of cycles
            - mode: "fast" | "production"

    Returns:
        Dictionary with:
            - memory_matrix: 2D matrix of memory retention
            - critical_surface: points on critical line
            - phase_regimes: classification of regimes
    """
    mode = config.get("mode", "fast")
    
    # Determine grid size based on mode
    if mode == "fast":
        bookmarking_steps = config.get("bookmarking_steps", 7)
        epigenetic_steps = config.get("epigenetic_steps", 5)
        num_cycles = config.get("num_cycles", 20)
    else:
        bookmarking_steps = config.get("bookmarking_steps", 50)
        epigenetic_steps = config.get("epigenetic_steps", 50)
        num_cycles = config.get("num_cycles", 100)
    
    # Get ranges
    bookmarking_range = config.get("bookmarking_range", (0.0, 1.0, bookmarking_steps))
    epigenetic_range = config.get("epigenetic_range", (0.0, 1.0, epigenetic_steps))
    
    processivity = config.get("processivity", 0.9)
    
    # Use RS11BPhaseDiagram builder
    builder = RS11BPhaseDiagram()
    
    # Build phase diagram
    results = builder.build_phase_diagram(
        bookmarking_range=bookmarking_range,
        epigenetic_range=epigenetic_range,
        processivity=processivity,
        num_cycles=num_cycles,
    )
    
    # Extract critical surface
    critical_surface = {}
    memory_matrix = results["memory_matrix"]
    bookmarking_values = results["bookmarking_values"]
    epigenetic_values = results["epigenetic_values"]
    
    for i, epi_val in enumerate(epigenetic_values):
        for j, book_val in enumerate(bookmarking_values):
            memory_val = memory_matrix[i][j]
            if 0.4 <= memory_val <= 0.6:  # Near threshold
                key = f"bookmark_{book_val:.2f}_epi_{epi_val:.2f}"
                critical_surface[key] = float(memory_val)
    
    # Classify phase regimes
    phase_regimes = {
        "stable_memory": 0,
        "partial_memory": 0,
        "drift": 0,
    }
    
    for row in memory_matrix:
        for val in row:
            if val > 0.7:
                phase_regimes["stable_memory"] += 1
            elif val > 0.3:
                phase_regimes["partial_memory"] += 1
            else:
                phase_regimes["drift"] += 1
    
    return {
        "memory_matrix": [[float(v) for v in row] for row in memory_matrix],
        "bookmarking_values": [float(v) for v in bookmarking_values],
        "epigenetic_values": [float(v) for v in epigenetic_values],
        "critical_surface": critical_surface,
        "phase_regimes": phase_regimes,
        "critical_line": results.get("critical_line", []),
        "processivity": float(processivity),
        "num_cycles": num_cycles,
    }


def run_real_benchmark_summary(config: dict[str, Any]) -> dict[str, Any]:
    """
    Запускает сравнение ARCHCODE vs реальный Hi-C и возвращает summary.

    Args:
        config: Configuration dictionary with:
            - real_cooler_path: path to real Hi-C .cool file
            - nipbl_velocity: NIPBL velocity factor
            - wapl_lifetime: WAPL lifetime factor
            - region: optional genomic region

    Returns:
        Dictionary with:
            - insulation_correlation: correlation coefficient
            - ps_correlation: P(s) correlation coefficient
            - summary_stats: statistics
            - pass_fail: validation flags
    """
    real_cooler_path = config.get("real_cooler_path", "data/real_hic/WT/Rao2014_GM12878_1000kb.cool")
    nipbl_velocity = config.get("nipbl_velocity", 1.0)
    wapl_lifetime = config.get("wapl_lifetime", 1.0)
    
    # Default boundaries
    boundaries_data = config.get("boundaries_data", [
        (127100000, 0.8, "ctcf"),
        (127200000, 0.7, "ctcf"),
        (127300000, 0.6, "ctcf"),
        (127400000, 0.5, "ctcf"),
        (127500000, 0.9, "ctcf"),
    ])
    
    barrier_strengths_map = {pos: [0.5] for pos, _, _ in boundaries_data}
    methylation_map = {pos: 0.5 for pos, _, _ in boundaries_data}
    te_motif_map = {pos: [0.0] for pos, _, _ in boundaries_data}
    
    # Run comparison
    comparison = ARCHCODEvsRealComparison()
    
    # Analyze real data
    from experiments.compute_real_insulation import analyze_real_hic
    real_data_dir = Path("data/output/real_hic_analysis_temp")
    real_results = analyze_real_hic(
        cooler_path=real_cooler_path,
        output_dir=real_data_dir,
    )
    
    # Generate ARCHCODE metrics
    archcode_insulation = comparison.generate_archcode_insulation(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity=nipbl_velocity,
        wapl_lifetime=wapl_lifetime,
    )
    
    archcode_ps = comparison.generate_archcode_ps_scaling(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        nipbl_velocity=nipbl_velocity,
        wapl_lifetime=wapl_lifetime,
    )
    
    # Load real data
    real_data = comparison.load_real_data(real_data_dir)
    
    # Compare
    comparison_results = comparison.compare_and_visualize(
        archcode_insulation=archcode_insulation,
        archcode_ps=archcode_ps,
        real_data=real_data,
    )
    
    # Extract correlations
    insulation_corr = comparison_results.get("insulation_correlation", 0.0)
    ps_corr = comparison_results.get("ps_correlation", 0.0)
    
    # Pass/fail criteria
    pass_fail = {
        "insulation_pass": insulation_corr >= 0.7,
        "ps_pass": ps_corr >= 0.9,
        "overall_pass": insulation_corr >= 0.7 and ps_corr >= 0.9,
    }
    
    return {
        "insulation_correlation": float(insulation_corr),
        "ps_correlation": float(ps_corr),
        "summary_stats": {
            "real_insulation_mean": float(real_results.get("insulation", {}).get("mean", 0.0)) if real_results else 0.0,
            "archcode_boundaries": len(archcode_insulation),
            "real_windows": real_results.get("insulation", {}).get("count", 0) if real_results else 0,
        },
        "pass_fail": pass_fail,
    }


