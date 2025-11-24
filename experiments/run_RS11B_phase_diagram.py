"""
RS-11B: Phase Diagram for Multichannel Architectural Memory.

Builds 2D/3D phase diagram showing memory retention as a function of:
- Bookmarking fraction (X-axis)
- Epigenetic strength (Y-axis)
- Processivity (Z-axis or color)

Finds critical line separating stable memory from memory collapse.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.bookmarking import assign_bookmarking, apply_stochastic_recovery
from src.archcode_core.cell_cycle import CellCyclePhase
from src.archcode_core.epigenetic_memory import (
    initialize_epigenetic_memory,
    restore_with_epigenetic_memory,
)
from src.archcode_core.extrusion_engine import Boundary
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.memory_metrics import (
    calculate_jaccard_stable_boundaries,
    get_stable_boundaries,
)
from src.vizir.config_loader import VIZIRConfigLoader


class RS11BPhaseDiagram:
    """Build phase diagram for multichannel memory."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize phase diagram builder."""
        self.output_dir = output_dir or Path("data/output/RS11")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load VIZIR configs
        loader = VIZIRConfigLoader()
        self.vizir_configs = {
            **loader.load_all_physical(),
            **loader.load_all_structural(),
            **loader.load_all_logical(),
        }

        # Test boundaries
        self.boundaries_data = [
            (127100000, 0.8, "ctcf"),
            (127200000, 0.7, "ctcf"),
            (127300000, 0.6, "ctcf"),
            (127400000, 0.5, "ctcf"),
            (127500000, 0.9, "ctcf"),
        ]

        self.barrier_strengths_map = {pos: [0.5] for pos, _, _ in self.boundaries_data}
        self.methylation_map = {pos: 0.5 for pos, _, _ in self.boundaries_data}
        self.te_motif_map = {pos: [0.0] for pos, _, _ in self.boundaries_data}

    def simulate_memory_retention(
        self,
        bookmarking_fraction: float,
        epigenetic_strength: float,
        processivity: float = 0.9,
        num_cycles: int = 50,
        seed: int = 42,
    ) -> float:
        """
        Simulate memory retention for given parameters.

        Args:
            bookmarking_fraction: Fraction of bookmarked boundaries
            epigenetic_strength: Strength of epigenetic memory channel
            processivity: Processivity (NIPBL × WAPL)
            num_cycles: Number of cell cycles to simulate
            seed: Random seed

        Returns:
            Memory retention score (Jaccard after N cycles)
        """
        import random

        rng = random.Random(seed)

        # Derive velocity and lifetime from processivity
        nipbl_velocity = np.sqrt(processivity)  # Simplified
        wapl_lifetime = np.sqrt(processivity)

        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

        # Add boundaries
        for pos, strength, btype in self.boundaries_data:
            pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

        # Baseline stable boundaries
        baseline_predictions = pipeline.pipeline.analyze_all_boundaries(
            barrier_strengths_map=self.barrier_strengths_map,
            methylation_map=self.methylation_map,
            te_motif_map=self.te_motif_map,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
            cell_cycle_phase=CellCyclePhase.INTERPHASE,
            enable_bookmarking=False,
        )

        baseline_stable = get_stable_boundaries(
            pipeline.pipeline.boundaries, stability_threshold=0.7
        )

        # Initialize epigenetic memory
        epigenetic_scores = initialize_epigenetic_memory(
            pipeline.pipeline.boundaries,
            mode="correlated_with_strength",
            strength=1.0,
            seed=seed,
        )

        # Simulate cycles
        current_boundaries = pipeline.pipeline.boundaries.copy()

        for cycle in range(num_cycles):
            # Assign bookmarking
            assign_bookmarking(current_boundaries, fraction=bookmarking_fraction, seed=cycle)

            # Mitosis: low processivity
            mitosis_velocity = 0.3
            mitosis_lifetime = 0.3

            # Multichannel restoration
            boundaries_before = [
                Boundary(b.position, b.strength, b.barrier_type, b.insulation_score, b.is_bookmarked)
                for b in current_boundaries
            ]

            restored_boundaries, _ = restore_with_epigenetic_memory(
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

            current_boundaries = restored_boundaries

            # Update epigenetic scores (simplified: static for now)
            # In future: could evolve based on stability

        # Final stable boundaries
        final_stable = get_stable_boundaries(
            current_boundaries, stability_threshold=0.7
        )

        # Calculate memory retention (Jaccard)
        jaccard = calculate_jaccard_stable_boundaries(baseline_stable, final_stable)

        return jaccard

    def build_phase_diagram(
        self,
        bookmarking_range: tuple[float, float, int] = (0.0, 1.0, 11),
        epigenetic_range: tuple[float, float, int] = (0.0, 1.0, 11),
        processivity: float = 0.9,
        num_cycles: int = 50,
    ) -> dict:
        """
        Build 2D phase diagram.

        Args:
            bookmarking_range: (min, max, num_points) for bookmarking fraction
            epigenetic_range: (min, max, num_points) for epigenetic strength
            processivity: Fixed processivity value
            num_cycles: Number of cycles to simulate

        Returns:
            Dictionary with phase diagram data
        """
        print("=" * 80)
        print("RS-11B: BUILDING PHASE DIAGRAM")
        print("=" * 80)

        bookmarking_min, bookmarking_max, bookmarking_steps = bookmarking_range
        epigenetic_min, epigenetic_max, epigenetic_steps = epigenetic_range

        bookmarking_values = np.linspace(bookmarking_min, bookmarking_max, bookmarking_steps)
        epigenetic_values = np.linspace(epigenetic_min, epigenetic_max, epigenetic_steps)

        # Create meshgrid
        B, E = np.meshgrid(bookmarking_values, epigenetic_values)

        # Calculate memory retention for each point
        memory_matrix = np.zeros_like(B)
        total_points = B.size
        current_point = 0

        print(f"\n📊 Computing memory retention for {total_points} points...")
        print(f"   Processivity: {processivity}")
        print(f"   Cycles: {num_cycles}")

        for i in range(len(epigenetic_values)):
            for j in range(len(bookmarking_values)):
                bookmarking_frac = bookmarking_values[j]
                epigenetic_str = epigenetic_values[i]

                # Simulate (use grid position as seed for reproducibility)
                seed = i * len(bookmarking_values) + j
                memory_retention = self.simulate_memory_retention(
                    bookmarking_fraction=bookmarking_frac,
                    epigenetic_strength=epigenetic_str,
                    processivity=processivity,
                    num_cycles=num_cycles,
                    seed=seed,
                )

                memory_matrix[i, j] = memory_retention

                current_point += 1
                if current_point % 10 == 0:
                    print(f"   Progress: {current_point}/{total_points} ({current_point*100/total_points:.1f}%)")

        # Find critical line (memory retention = 0.5 threshold)
        critical_line = []
        for i in range(len(epigenetic_values)):
            for j in range(len(bookmarking_values) - 1):
                if memory_matrix[i, j] < 0.5 <= memory_matrix[i, j + 1]:
                    # Interpolate
                    b1 = bookmarking_values[j]
                    b2 = bookmarking_values[j + 1]
                    m1 = memory_matrix[i, j]
                    m2 = memory_matrix[i, j + 1]
                    # Linear interpolation
                    b_critical = b1 + (0.5 - m1) * (b2 - b1) / (m2 - m1) if m2 != m1 else b1
                    critical_line.append((epigenetic_values[i], b_critical))

        results = {
            "bookmarking_values": bookmarking_values.tolist(),
            "epigenetic_values": epigenetic_values.tolist(),
            "memory_matrix": memory_matrix.tolist(),
            "critical_line": critical_line,
            "processivity": processivity,
            "num_cycles": num_cycles,
        }

        return results

    def visualize_phase_diagram(self, results: dict) -> Path:
        """Visualize phase diagram."""
        print("\n📊 Creating visualizations...")

        bookmarking_values = np.array(results["bookmarking_values"])
        epigenetic_values = np.array(results["epigenetic_values"])
        memory_matrix = np.array(results["memory_matrix"])
        critical_line = results["critical_line"]

        # Create figure with 2 panels
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Panel 1: 2D Heatmap
        ax1 = axes[0]
        B, E = np.meshgrid(bookmarking_values, epigenetic_values)
        im = ax1.contourf(B, E, memory_matrix, levels=20, cmap="RdYlGn")
        ax1.contour(B, E, memory_matrix, levels=[0.5], colors="black", linewidths=2)

        # Plot critical line
        if critical_line:
            critical_epi, critical_book = zip(*critical_line)
            ax1.plot(critical_book, critical_epi, "k--", linewidth=2, label="Critical Line (50%)")

        ax1.set_xlabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Epigenetic Strength", fontsize=12, fontweight="bold")
        ax1.set_title("Memory Retention Phase Diagram", fontsize=14, fontweight="bold")
        ax1.legend()
        plt.colorbar(im, ax=ax1, label="Memory Retention (Jaccard)")

        # Panel 2: 3D Surface
        ax2 = axes[1]
        ax2 = fig.add_subplot(122, projection="3d")
        surf = ax2.plot_surface(
            B, E, memory_matrix, cmap="RdYlGn", alpha=0.8, linewidth=0, antialiased=True
        )
        ax2.set_xlabel("Bookmarking Fraction", fontsize=11)
        ax2.set_ylabel("Epigenetic Strength", fontsize=11)
        ax2.set_zlabel("Memory Retention", fontsize=11)
        ax2.set_title("3D Memory Surface", fontsize=12, fontweight="bold")

        plt.tight_layout()

        # Save
        figure_path = self.output_dir / "RS11B_phase_diagram.png"
        plt.savefig(figure_path, dpi=300, bbox_inches="tight")
        print(f"   ✅ Figure saved: {figure_path}")

        plt.close()

        return figure_path

    def run(self) -> dict:
        """Run RS-11B phase diagram analysis."""
        # Build phase diagram
        # Для полной валидации используйте:
        # bookmarking_range=(0.0, 1.0, 50), epigenetic_range=(0.0, 1.0, 50), num_cycles=100
        # Для быстрого прототипа (текущие параметры):
        results = self.build_phase_diagram(
            bookmarking_range=(0.0, 1.0, 11),  # Полная валидация: 50
            epigenetic_range=(0.0, 1.0, 11),   # Полная валидация: 50
            processivity=0.9,
            num_cycles=50,  # Полная валидация: 100
        )

        # Visualize
        figure_path = self.visualize_phase_diagram(results)

        # Save results
        results_file = self.output_dir / "RS11B_phase_diagram.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved: {results_file}")
        print(f"📊 Figure saved: {figure_path}")

        print("\n" + "=" * 80)
        print("✅ RS-11B PHASE DIAGRAM COMPLETE")
        print("=" * 80)

        return results


if __name__ == "__main__":
    builder = RS11BPhaseDiagram()
    results = builder.run()

