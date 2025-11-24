"""
Create Figure 1: Two-Axis Genome Theory.

Visualizes the unified model where architectural stability is governed by:
- Axis X: Processivity (NIPBL × WAPL) → stability
- Axis Y: Bookmarking (CTCF memory) → memory

Creates publication-quality figure showing phase diagram and key regions.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


class Figure1TwoAxisTheory:
    """Create Figure 1 for Two-Axis Genome Theory."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize figure creator."""
        self.output_dir = output_dir or Path("figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_figure(self) -> Path:
        """Create Figure 1: Two-Axis Genome Theory."""
        print("=" * 80)
        print("CREATING FIGURE 1: TWO-AXIS GENOME THEORY")
        print("=" * 80)

        # Create figure with 4 panels
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Panel A: Two-Axis Phase Diagram
        ax1 = fig.add_subplot(gs[0:2, 0])
        self.create_phase_diagram(ax1)

        # Panel B: Processivity Law
        ax2 = fig.add_subplot(gs[0, 1])
        self.create_processivity_law(ax2)

        # Panel C: Bookmarking Memory Law
        ax3 = fig.add_subplot(gs[1, 1])
        self.create_bookmarking_law(ax3)

        # Panel D: Clinical Applications
        ax4 = fig.add_subplot(gs[2, :])
        self.create_clinical_applications(ax4)

        # Overall title
        fig.suptitle(
            "Two-Axis Genome Theory: Unified Model of Architectural Stability",
            fontsize=18,
            fontweight="bold",
            y=0.98,
        )

        # Save
        figure_path = self.output_dir / "Figure1_TwoAxisTheory.png"
        plt.savefig(figure_path, dpi=300, bbox_inches="tight")
        print(f"\n✅ Figure saved: {figure_path}")

        plt.close()

        return figure_path

    def create_phase_diagram(self, ax):
        """Create main phase diagram."""
        # Create meshgrid
        processivity = np.linspace(0, 2, 100)
        bookmarking = np.linspace(0, 1, 100)
        P, B = np.meshgrid(processivity, bookmarking)

        # Calculate stability score (simplified model)
        # Stability = f(processivity) × f(bookmarking)
        stability = np.zeros_like(P)

        for i in range(len(bookmarking)):
            for j in range(len(processivity)):
                p = processivity[j]
                b = bookmarking[i]

                # Processivity contribution
                if p < 0.5:
                    proc_contrib = 0.0  # Collapse
                elif p < 1.0:
                    proc_contrib = (p - 0.5) / 0.5  # Transition
                else:
                    proc_contrib = 1.0  # Stable

                # Bookmarking contribution
                if b < 0.3:
                    book_contrib = 0.0  # No memory
                elif b < 0.7:
                    book_contrib = (b - 0.3) / 0.4  # Partial memory
                else:
                    book_contrib = 1.0  # Full memory

                # Combined stability
                stability[i, j] = proc_contrib * 0.6 + book_contrib * 0.4

        # Plot contour
        contour = ax.contourf(P, B, stability, levels=20, cmap="RdYlGn", alpha=0.8)
        ax.contour(P, B, stability, levels=[0.3, 0.5, 0.7], colors="black", linewidths=1, alpha=0.5)

        # Mark key regions
        ax.axvline(0.5, color="red", linestyle="--", linewidth=2, alpha=0.7, label="Unstable Threshold")
        ax.axvline(1.0, color="green", linestyle="--", linewidth=2, alpha=0.7, label="Stable Threshold")
        ax.axhline(0.3, color="orange", linestyle="--", linewidth=2, alpha=0.7, label="Memory Threshold")

        # Mark clinical cases
        ax.plot(0.5, 0.8, "ro", markersize=12, label="CdLS", zorder=5)
        ax.plot(1.0, 0.8, "go", markersize=12, label="WT", zorder=5)
        ax.plot(1.5, 0.8, "bo", markersize=12, label="WAPL-KO", zorder=5)

        ax.set_xlabel("Processivity (NIPBL × WAPL)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Bookmarking Fraction (CTCF Memory)", fontsize=13, fontweight="bold")
        ax.set_title("A. Two-Axis Phase Diagram", fontsize=14, fontweight="bold", loc="left")
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(True, alpha=0.3)

        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label("Architectural Stability Score", fontsize=11)

    def create_processivity_law(self, ax):
        """Create Processivity Law visualization."""
        # Processivity = NIPBL × WAPL
        nipbl = np.linspace(0, 2, 100)
        wapl = np.linspace(0, 2, 100)
        processivity = nipbl * wapl

        # Plot
        ax.plot(nipbl, processivity, "b-", linewidth=2, label="Processivity Law")
        ax.fill_between(nipbl, 0, 0.5, alpha=0.2, color="red", label="Unstable")
        ax.fill_between(nipbl, 0.5, 1.0, alpha=0.2, color="yellow", label="Transition")
        ax.fill_between(nipbl, 1.0, 4.0, alpha=0.2, color="green", label="Stable")

        ax.axhline(0.5, color="red", linestyle="--", linewidth=1)
        ax.axhline(1.0, color="green", linestyle="--", linewidth=1)

        ax.set_xlabel("NIPBL Velocity", fontsize=11)
        ax.set_ylabel("Processivity (λ)", fontsize=11)
        ax.set_title("B. Processivity Law: λ = NIPBL × WAPL", fontsize=12, fontweight="bold", loc="left")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 4)

    def create_bookmarking_law(self, ax):
        """Create Bookmarking Memory Law visualization."""
        # Memory retention ∝ (bookmarking_fraction)^n
        bookmarking = np.linspace(0, 1, 100)
        n = 2.0  # Exponent
        memory = bookmarking ** n

        # Plot
        ax.plot(bookmarking, memory, "r-", linewidth=2, label="Memory Retention")
        ax.fill_between(bookmarking, 0, 0.3, alpha=0.2, color="red", label="No Memory")
        ax.fill_between(bookmarking, 0.3, 0.7, alpha=0.2, color="yellow", label="Partial Memory")
        ax.fill_between(bookmarking, 0.7, 1.0, alpha=0.2, color="green", label="Full Memory")

        ax.axhline(0.3, color="orange", linestyle="--", linewidth=1)
        ax.axhline(0.7, color="green", linestyle="--", linewidth=1)

        ax.set_xlabel("Bookmarking Fraction", fontsize=11)
        ax.set_ylabel("Memory Retention", fontsize=11)
        ax.set_title("C. Bookmarking Memory Law: M ∝ B^n", fontsize=12, fontweight="bold", loc="left")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    def create_clinical_applications(self, ax):
        """Create clinical applications panel."""
        ax.axis("off")

        text = """
TWO-AXIS GENOME THEORY: CLINICAL APPLICATIONS

1. DIAGNOSTICS
   • Measure Processivity (NIPBL × WAPL) → Early detection of architectural defects
   • Measure Bookmarking → Predict memory retention through cell divisions

2. THERAPEUTICS
   • Regulate NIPBL/WAPL → Restore architectural stability
   • Enhance Bookmarking → Improve memory retention in aging cells

3. SYNTHETIC BIOLOGY
   • Design genomes with specified architecture
   • Optimize architecture for therapeutic purposes

KEY PREDICTIONS:
   • CdLS (Processivity ≈ 0.5): Unstable phase → Architectural collapse
   • WAPL-KO (Processivity > 1.5): Hyper-stable → Vermicelli-like structure
   • Low Bookmarking (< 0.3): Memory loss → Drift over cycles
        """

        ax.text(
            0.05,
            0.95,
            text,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
        )

    def run(self) -> Path:
        """Run figure creation."""
        figure_path = self.create_figure()

        print("\n" + "=" * 80)
        print("✅ FIGURE 1 CREATED")
        print("=" * 80)

        return figure_path


if __name__ == "__main__":
    creator = Figure1TwoAxisTheory()
    figure_path = creator.run()
    print(f"\n📊 Figure saved: {figure_path}")

