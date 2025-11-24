"""Benchmark ARCHCODE Simulation vs Real Hi-C Data.

CLI tool для генерации Figure 4 (single condition).
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_benchmark.hi_c_benchmark import (
    compute_metrics,
    load_real_cooler,
    simulation_to_cooler,
    synchronize_bins,
)


def setup_publication_style() -> None:
    """Setup matplotlib for publication-quality figures."""
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["font.size"] = 10
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 9
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False


def normalize_p_s_curves(
    p_s_real: np.ndarray,
    p_s_sim: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Normalize P(s) curves to start at same Y-value for slope comparison.

    Args:
        p_s_real: Real P(s) values
        p_s_sim: Simulated P(s) values

    Returns:
        (normalized_real, normalized_sim)
    """
    # Find first non-zero value for normalization
    real_first = p_s_real[p_s_real > 0][0] if np.any(p_s_real > 0) else 1.0
    sim_first = p_s_sim[p_s_sim > 0][0] if np.any(p_s_sim > 0) else 1.0

    # Normalize to start at 1.0
    normalized_real = p_s_real / real_first
    normalized_sim = p_s_sim / sim_first

    return normalized_real, normalized_sim


def calculate_shared_vmax(
    matrix_real: np.ndarray,
    matrix_sim: np.ndarray,
    percentile: float = 98.0,
) -> float:
    """
    Calculate shared vmax for fair contrast comparison.

    Args:
        matrix_real: Real contact matrix
        matrix_sim: Simulated contact matrix
        percentile: Percentile to use for vmax (default: 98th)

    Returns:
        Shared vmax value
    """
    # Combine both matrices
    combined = np.concatenate([matrix_real.flatten(), matrix_sim.flatten()])
    # Remove zeros and NaNs
    combined = combined[combined > 0]
    combined = combined[~np.isnan(combined)]

    if len(combined) == 0:
        return 1.0

    vmax = np.percentile(combined, percentile)
    return float(vmax)


def create_figure_4(
    real_cooler_path: str,
    sim_matrix_path: str,
    region: Optional[str] = None,
    output_path: str = "Figure_4.png",
    condition_name: str = "WT",
) -> None:
    """
    Generate Figure 4: Benchmark comparison.

    Args:
        real_cooler_path: Path to real Hi-C cooler file
        sim_matrix_path: Path to simulated matrix (.npy)
        region: Optional region string
        output_path: Output path for figure
        condition_name: Name of condition (for title)
    """
    setup_publication_style()

    print(f"[Benchmark] Loading real Hi-C data: {real_cooler_path}")
    real_cooler = load_real_cooler(real_cooler_path, region=region)

    print(f"[Benchmark] Loading simulated matrix: {sim_matrix_path}")
    sim_matrix = np.load(sim_matrix_path)

    # Synchronize bins
    print("[Benchmark] Synchronizing bins...")
    sim_resolution = 10000  # Default, should be configurable
    real_cooler_sync, sim_matrix_sync = synchronize_bins(
        real_cooler, sim_matrix, sim_resolution
    )

    print(f"[Benchmark] Synchronized: {len(real_cooler_sync.bins())} bins")

    # Compute metrics
    print("[Benchmark] Computing metrics...")
    metrics_real = compute_metrics(real_cooler_sync)
    sim_cooler = simulation_to_cooler(
        sim_matrix_sync, sim_resolution, chrom_name="chrSim"
    )
    metrics_sim = compute_metrics(sim_cooler)

    # Extract matrices for visualization
    matrix_real = real_cooler_sync.matrix(balance=False)[:]
    matrix_sim = sim_matrix_sync

    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Panel A: P(s) scaling
    ax1 = axes[0]
    p_s_real = metrics_real.p_s
    p_s_sim = metrics_sim.p_s

    # Extract distances and counts
    dist_real = p_s_real["dist"].values
    count_real = p_s_real["count.avg"].values
    dist_sim = p_s_sim["dist"].values
    count_sim = p_s_sim["count.avg"].values

    # Normalize for slope comparison
    count_real_norm, count_sim_norm = normalize_p_s_curves(count_real, count_sim)

    ax1.loglog(dist_real, count_real_norm, "o-", label="Real", linewidth=2, markersize=4)
    ax1.loglog(dist_sim, count_sim_norm, "s-", label="Simulated", linewidth=2, markersize=4)
    ax1.set_xlabel("Genomic Distance (bp)", fontweight="bold")
    ax1.set_ylabel("Normalized Contact Frequency", fontweight="bold")
    ax1.set_title("A) P(s) Scaling", fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3, which="both")

    # Panel B: Insulation Score histogram
    ax2 = axes[1]
    insulation_real = metrics_real.insulation["insulation_score"].values
    insulation_sim = metrics_sim.insulation["insulation_score"].values

    # Remove NaNs and zeros
    insulation_real = insulation_real[~np.isnan(insulation_real)]
    insulation_sim = insulation_sim[~np.isnan(insulation_sim)]
    insulation_real = insulation_real[insulation_real > 0]
    insulation_sim = insulation_sim[insulation_sim > 0]

    ax2.hist(
        insulation_real,
        bins=50,
        alpha=0.6,
        label="Real",
        density=True,
        color="blue",
    )
    ax2.hist(
        insulation_sim,
        bins=50,
        alpha=0.6,
        label="Simulated",
        density=True,
        color="red",
    )
    ax2.set_xlabel("Insulation Score", fontweight="bold")
    ax2.set_ylabel("Density", fontweight="bold")
    ax2.set_title("B) Insulation Distribution", fontweight="bold")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Panel C: Split heatmap
    ax3 = axes[2]
    vmax = calculate_shared_vmax(matrix_real, matrix_sim, percentile=98.0)

    # Create combined matrix (upper = real, lower = sim)
    n = matrix_real.shape[0]
    combined_matrix = np.zeros_like(matrix_real)
    # Upper triangle: real
    combined_matrix[np.triu_indices(n)] = matrix_real[np.triu_indices(n)]
    # Lower triangle: simulated
    combined_matrix[np.tril_indices(n, k=-1)] = matrix_sim[np.tril_indices(n, k=-1)]

    im = ax3.imshow(
        combined_matrix,
        cmap="RdBu_r",
        vmax=vmax,
        aspect="auto",
        origin="lower",
    )
    ax3.set_xlabel("Genomic Position (bins)", fontweight="bold")
    ax3.set_ylabel("Genomic Position (bins)", fontweight="bold")
    ax3.set_title("C) Contact Maps (Upper: Real, Lower: Sim)", fontweight="bold")
    plt.colorbar(im, ax=ax3, label="Contact Frequency")

    plt.suptitle(f"Figure 4: {condition_name}", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()

    # Save
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[Benchmark] Figure saved: {output_path}")

    plt.close()


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark ARCHCODE simulation vs real Hi-C data"
    )
    parser.add_argument(
        "--real-cooler",
        type=str,
        required=True,
        help="Path to real Hi-C cooler file (or URI)",
    )
    parser.add_argument(
        "--sim-matrix",
        type=str,
        required=True,
        help="Path to simulated matrix (.npy)",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Optional region string (e.g., 'chr1:1000000-2000000')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="Figure_4.png",
        help="Output path for figure",
    )
    parser.add_argument(
        "--condition",
        type=str,
        default="WT",
        help="Condition name (for title)",
    )

    args = parser.parse_args()

    create_figure_4(
        real_cooler_path=args.real_cooler,
        sim_matrix_path=args.sim_matrix,
        region=args.region,
        output_path=args.output,
        condition_name=args.condition,
    )


if __name__ == "__main__":
    main()

