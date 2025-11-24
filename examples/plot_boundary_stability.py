"""Visualization: Boundary Stability Profile."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt

from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs


def plot_stability_profile(
    pipeline: ARCHCODEPipeline,
    chromosome_length: int = 1000000,
    output_file: str = "boundary_stability_profile.png",
) -> None:
    """
    Plot boundary stability profile along chromosome.

    Args:
        pipeline: ARCHCODE pipeline with analyzed boundaries
        chromosome_length: Length of chromosome region
        output_file: Output file path
    """
    if not pipeline.stability_predictions:
        print("No stability predictions available")
        return

    # Extract data
    positions = [p.position for p in pipeline.stability_predictions]
    stability_scores = [p.stability_score for p in pipeline.stability_predictions]
    ctcf_strengths = [b.strength for b in pipeline.boundaries[: len(positions)]]

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot 1: Stability Score
    ax1.plot(positions, stability_scores, "o-", color="blue", linewidth=2, markersize=8)
    ax1.axhline(y=0.7, color="green", linestyle="--", label="Stable threshold")
    ax1.axhline(y=0.4, color="red", linestyle="--", label="Variable threshold")
    ax1.fill_between(
        positions,
        0.7,
        1.0,
        alpha=0.2,
        color="green",
        label="Stable region",
    )
    ax1.fill_between(
        positions,
        0.0,
        0.4,
        alpha=0.2,
        color="red",
        label="Variable region",
    )
    ax1.set_ylabel("Stability Score", fontsize=12)
    ax1.set_title("Boundary Stability Profile", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 1.1)

    # Plot 2: CTCF Strength vs Stability
    ax2.plot(positions, ctcf_strengths, "s-", color="orange", linewidth=2, markersize=8, label="CTCF Strength")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(
        positions,
        stability_scores,
        "o-",
        color="blue",
        linewidth=2,
        markersize=8,
        label="Stability Score",
    )
    ax2.set_xlabel("Genomic Position (bp)", fontsize=12)
    ax2.set_ylabel("CTCF Strength", fontsize=12, color="orange")
    ax2_twin.set_ylabel("Stability Score", fontsize=12, color="blue")
    ax2.set_title("CTCF Strength vs Stability Score", fontsize=14, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="orange")
    ax2_twin.tick_params(axis="y", labelcolor="blue")
    ax2.grid(True, alpha=0.3)

    # Add legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✅ Plot saved to {output_file}")
    plt.close()


def plot_stability_categories(
    pipeline: ARCHCODEPipeline,
    output_file: str = "boundary_stability_categories.png",
) -> None:
    """
    Plot stability categories distribution.

    Args:
        pipeline: ARCHCODE pipeline
        output_file: Output file path
    """
    if not pipeline.stability_predictions:
        print("No stability predictions available")
        return

    # Count categories
    categories = {}
    for pred in pipeline.stability_predictions:
        cat = pred.stability_category
        categories[cat] = categories.get(cat, 0) + 1

    # Create pie chart
    fig, ax = plt.subplots(figsize=(8, 8))

    colors = {"stable": "green", "variable": "red", "intermediate": "yellow"}
    labels = list(categories.keys())
    sizes = list(categories.values())
    colors_list = [colors.get(label, "gray") for label in labels]

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors_list,
    )
    ax.set_title("Boundary Stability Categories Distribution", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"✅ Plot saved to {output_file}")
    plt.close()


def main() -> None:
    """Generate boundary stability visualizations."""
    print("=" * 60)
    print("Boundary Stability Visualization")
    print("=" * 60)

    # Load configurations and create pipeline
    archcode_config, stability_config = load_pipeline_configs()
    pipeline = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    # Add sample boundaries
    boundaries_data = [
        (100000, 0.9, "ctcf"),
        (200000, 0.7, "ctcf"),
        (300000, 0.5, "ctcf"),
        (400000, 0.3, "ctcf"),
        (500000, 0.8, "ctcf"),
        (600000, 0.6, "ctcf"),
        (700000, 0.4, "ctcf"),
        (800000, 0.85, "ctcf"),
    ]

    for pos, strength, btype in boundaries_data:
        pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

    # Analyze stability
    barrier_strengths_map = {
        100000: [0.5, 0.3],
        200000: [0.3],
        300000: [0.2],
        400000: [0.1],
        500000: [0.4, 0.2],
        600000: [0.25],
        700000: [0.15],
        800000: [0.45, 0.3],
    }

    methylation_map = {
        100000: 0.1,
        200000: 0.3,
        300000: 0.6,
        400000: 0.8,
        500000: 0.2,
        600000: 0.5,
        700000: 0.7,
        800000: 0.15,
    }

    te_motif_map = {
        100000: [0.2, 0.1],
        200000: [0.1],
        300000: [0.0],
        400000: [-0.3],
        500000: [0.15],
        600000: [0.05],
        700000: [-0.2],
        800000: [0.2, 0.1],
    }

    pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
    )

    # Generate plots
    print("\nGenerating visualizations...")
    plot_stability_profile(pipeline, chromosome_length=900000)
    plot_stability_categories(pipeline)

    print("\n" + "=" * 60)
    print("✅ Visualization Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
