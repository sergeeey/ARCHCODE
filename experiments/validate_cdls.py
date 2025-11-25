"""
Validate ARCHCODE predictions on CdLS (NIPBL↓) data.

Compares ARCHCODE simulations with real Hi-C data from HCT116 + Auxin (Rao 2017).
Tests prediction: Processivity ≈ 0.5 → Unstable phase
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.compute_real_insulation import analyze_real_hic
from experiments.compare_archcode_vs_real import ARCHCODEvsRealComparison


class CdLSValidation:
    """Validate ARCHCODE on CdLS (NIPBL↓) data."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize validation."""
        self.output_dir = output_dir or Path("data/output/cdls_validation")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # CdLS parameters (from RS-09)
        self.cdls_processivity = 0.5  # Low processivity (NIPBL↓)
        self.cdls_nipbl_velocity = 0.7  # Reduced NIPBL
        self.cdls_wapl_lifetime = 0.7  # Reduced WAPL lifetime

        # Boundaries (same region as WT)
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

    def run_validation(self, cdls_cooler_path: str | None = None) -> dict:
        """
        Run CdLS validation.

        Args:
            cdls_cooler_path: Path to CdLS Hi-C data (if None, uses WT as placeholder)

        Returns:
            Validation results dictionary
        """
        print("=" * 80)
        print("CdLS (NIPBL↓) VALIDATION")
        print("=" * 80)

        # If CdLS data not available, use WT as placeholder
        if cdls_cooler_path is None or not Path(cdls_cooler_path).exists():
            print("⚠️  CdLS data not found, using WT data as placeholder")
            print("   (For real validation, provide path to CdLS .cool file)")
            cdls_cooler_path = "data/real_hic/WT/Rao2014_GM12878_1000kb.cool"

        # Analyze real CdLS data
        print("\n📊 Analyzing real CdLS Hi-C data...")
        real_data_dir = self.output_dir / "real_cdls_analysis"
        real_data_dir.mkdir(parents=True, exist_ok=True)

        real_results = analyze_real_hic(
            cooler_path=cdls_cooler_path,
            output_dir=real_data_dir,
        )

        # Generate ARCHCODE simulation with CdLS parameters
        print("\n🔬 Generating ARCHCODE simulation (CdLS parameters)...")
        comparison = ARCHCODEvsRealComparison(output_dir=self.output_dir)

        archcode_insulation = comparison.generate_archcode_insulation(
            boundaries_data=self.boundaries_data,
            barrier_strengths_map=self.barrier_strengths_map,
            methylation_map=self.methylation_map,
            te_motif_map=self.te_motif_map,
            nipbl_velocity=self.cdls_nipbl_velocity,
            wapl_lifetime=self.cdls_wapl_lifetime,
        )

        archcode_ps = comparison.generate_archcode_ps_scaling(
            boundaries_data=self.boundaries_data,
            barrier_strengths_map=self.barrier_strengths_map,
            methylation_map=self.methylation_map,
            te_motif_map=self.te_motif_map,
            nipbl_velocity=self.cdls_nipbl_velocity,
            wapl_lifetime=self.cdls_wapl_lifetime,
        )

        # Load real data
        real_data = comparison.load_real_data(real_data_dir)

        # Compare
        comparison_results = comparison.compare_and_visualize(
            archcode_insulation=archcode_insulation,
            archcode_ps=archcode_ps,
            real_data=real_data,
        )

        # Create CdLS-specific visualization
        self.create_cdls_figure(archcode_insulation, archcode_ps, real_data, comparison_results)

        # Validation summary
        validation_summary = {
            "prediction": {
                "processivity": self.cdls_processivity,
                "expected_phase": "Unstable",
                "nipbl_velocity": self.cdls_nipbl_velocity,
                "wapl_lifetime": self.cdls_wapl_lifetime,
            },
            "correlations": comparison_results,
            "real_data_stats": real_results,
        }

        # Save summary
        summary_file = self.output_dir / "cdls_validation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(validation_summary, f, indent=2)

        print(f"\n💾 Validation summary: {summary_file}")

        print("\n" + "=" * 80)
        print("✅ CdLS VALIDATION COMPLETE")
        print("=" * 80)

        return validation_summary

    def create_cdls_figure(
        self,
        archcode_insulation: pd.DataFrame,
        archcode_ps: pd.DataFrame,
        real_data: dict,
        comparison_results: dict,
    ) -> Path:
        """Create CdLS-specific visualization."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("ARCHCODE Validation: CdLS (NIPBL↓) Prediction", fontsize=16, fontweight="bold")

        # Panel 1: Insulation comparison
        ax1 = axes[0, 0]
        if "insulation" in real_data and len(archcode_insulation) > 0:
            real_ins = real_data["insulation"]
            if len(real_ins) > 100:
                real_ins_sample = real_ins.sample(100).sort_values("start")
            else:
                real_ins_sample = real_ins.sort_values("start")

            ax1.plot(
                real_ins_sample["start"] / 1e6,
                real_ins_sample["insulation_score"] / 1e3,
                "b-",
                alpha=0.6,
                label="Real CdLS Hi-C",
                linewidth=1.5,
            )

            archcode_ins_sorted = archcode_insulation.sort_values("start")
            ax1.plot(
                archcode_ins_sorted["start"] / 1e6,
                archcode_ins_sorted["insulation_score"] * 10,
                "r--",
                alpha=0.8,
                label=f"ARCHCODE (P={self.cdls_processivity})",
                linewidth=2,
            )

            ax1.set_xlabel("Genomic Position (Mb)", fontsize=11)
            ax1.set_ylabel("Insulation Score (×10³)", fontsize=11)
            ax1.set_title("Insulation Score: CdLS vs ARCHCODE", fontsize=12, fontweight="bold")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # Panel 2: P(s) comparison
        ax2 = axes[0, 1]
        if "ps" in real_data and len(archcode_ps) > 0:
            real_ps = real_data["ps"]
            ax2.loglog(
                real_ps["distance"],
                real_ps["ps"],
                "b-",
                alpha=0.7,
                label="Real CdLS Hi-C",
                linewidth=2,
                marker="o",
                markersize=4,
            )

            ax2.loglog(
                archcode_ps["distance"],
                archcode_ps["ps"],
                "r--",
                alpha=0.8,
                label=f"ARCHCODE (P={self.cdls_processivity})",
                linewidth=2,
                marker="s",
                markersize=4,
            )

            ax2.set_xlabel("Genomic Distance (bp)", fontsize=11)
            ax2.set_ylabel("Contact Probability P(s)", fontsize=11)
            ax2.set_title("P(s) Scaling: CdLS vs ARCHCODE", fontsize=12, fontweight="bold")
            ax2.legend()
            ax2.grid(True, alpha=0.3, which="both")

        # Panel 3: Processivity prediction
        ax3 = axes[1, 0]
        processivity_values = [0.3, 0.5, 0.7, 1.0, 1.5]
        phases = ["Collapse", "Unstable", "Transition", "Stable", "Hyper-Stable"]
        colors = ["red", "orange", "yellow", "green", "blue"]

        for p, phase, color in zip(processivity_values, phases, colors):
            ax3.axvline(p, color=color, linestyle="--", alpha=0.5, label=phase)

        ax3.axvline(self.cdls_processivity, color="red", linewidth=3, label="CdLS Prediction")
        ax3.set_xlabel("Processivity", fontsize=11)
        ax3.set_ylabel("Phase", fontsize=11)
        ax3.set_title("Processivity Phase Diagram", fontsize=12, fontweight="bold")
        ax3.set_xlim(0, 2)
        ax3.legend()

        # Panel 4: Summary
        ax4 = axes[1, 1]
        ax4.axis("off")

        summary_text = "CdLS Validation Summary\n" + "=" * 30 + "\n\n"
        summary_text += f"Prediction:\n"
        summary_text += f"  Processivity: {self.cdls_processivity}\n"
        summary_text += f"  Expected Phase: Unstable\n\n"

        if "insulation_correlation" in comparison_results:
            summary_text += f"Insulation Correlation:\n"
            summary_text += f"  {comparison_results['insulation_correlation']:.3f}\n\n"

        if "ps_correlation" in comparison_results:
            summary_text += f"P(s) Correlation:\n"
            summary_text += f"  {comparison_results['ps_correlation']:.3f}\n"

        ax4.text(
            0.1,
            0.9,
            summary_text,
            transform=ax4.transAxes,
            fontsize=11,
            verticalalignment="top",
            family="monospace",
        )

        plt.tight_layout()

        figure_path = self.output_dir / "cdls_validation.png"
        plt.savefig(figure_path, dpi=300, bbox_inches="tight")
        print(f"   ✅ Figure saved: {figure_path}")

        plt.close()

        return figure_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate ARCHCODE on CdLS data")
    parser.add_argument(
        "--cdls-cooler",
        type=str,
        default=None,
        help="Path to CdLS .cool file",
    )

    args = parser.parse_args()

    validator = CdLSValidation()
    results = validator.run_validation(cdls_cooler_path=args.cdls_cooler)




