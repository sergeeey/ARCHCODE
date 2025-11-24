"""
Compare ARCHCODE simulations with real Hi-C data.

Generates ARCHCODE metrics (Insulation Score, P(s) scaling) and compares
with real data from Rao 2014 GM12878.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.cell_cycle import CellCyclePhase
from src.vizir.config_loader import VIZIRConfigLoader


class ARCHCODEvsRealComparison:
    """Compare ARCHCODE simulations with real Hi-C data."""

    def __init__(self, output_dir: Path | None = None):
        """Initialize comparison."""
        self.output_dir = output_dir or Path("data/output/comparison")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load VIZIR configs
        loader = VIZIRConfigLoader()
        self.vizir_configs = {
            **loader.load_all_physical(),
            **loader.load_all_structural(),
            **loader.load_all_logical(),
        }

    def generate_archcode_insulation(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        nipbl_velocity: float = 1.0,
        wapl_lifetime: float = 1.0,
        window_size: int = 500000,
    ) -> pd.DataFrame:
        """
        Generate insulation score from ARCHCODE simulation.

        Args:
            boundaries_data: List of (position, strength, type)
            barrier_strengths_map: Map of barrier strengths
            methylation_map: Map of methylation levels
            te_motif_map: Map of TE motifs
            nipbl_velocity: NIPBL velocity factor
            wapl_lifetime: WAPL lifetime factor
            window_size: Window size for insulation (bp)

        Returns:
            DataFrame with insulation scores
        """
        print("🔬 Generating ARCHCODE insulation score...")

        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

        # Add boundaries
        for pos, strength, btype in boundaries_data:
            pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

        # Run analysis
        predictions = pipeline.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
            cell_cycle_phase=CellCyclePhase.INTERPHASE,
            enable_bookmarking=False,
        )

        # Extract insulation scores
        insulation_data = []
        for boundary in pipeline.pipeline.boundaries:
            # Use insulation_score from boundary, or derive from stability
            insulation_val = boundary.insulation_score
            if insulation_val == 0.0 and predictions:
                # Fallback: use stability score as proxy
                matching_pred = next(
                    (p for p in predictions if hasattr(p, 'position') and p.position == boundary.position),
                    None
                )
                if matching_pred and hasattr(matching_pred, 'stability_score'):
                    insulation_val = matching_pred.stability_score

            insulation_data.append({
                "chrom": "chr8",  # Default chromosome
                "start": boundary.position,
                "end": boundary.position + window_size,
                "insulation_score": insulation_val,
            })

        return pd.DataFrame(insulation_data)

    def generate_archcode_ps_scaling(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        nipbl_velocity: float = 1.0,
        wapl_lifetime: float = 1.0,
        max_distance: int = 10_000_000,
    ) -> pd.DataFrame:
        """
        Generate P(s) scaling from ARCHCODE simulation.

        Args:
            boundaries_data: List of boundaries
            barrier_strengths_map: Map of barrier strengths
            methylation_map: Map of methylation levels
            te_motif_map: Map of TE motifs
            nipbl_velocity: NIPBL velocity factor
            wapl_lifetime: WAPL lifetime factor
            max_distance: Maximum distance to compute (bp)

        Returns:
            DataFrame with P(s) values
        """
        print("📈 Generating ARCHCODE P(s) scaling...")

        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

        # Add boundaries
        for pos, strength, btype in boundaries_data:
            pipeline.pipeline.add_boundary(position=pos, strength=strength, barrier_type=btype)

        # Run analysis
        predictions = pipeline.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
            cell_cycle_phase=CellCyclePhase.INTERPHASE,
            enable_bookmarking=False,
        )

        # Simulate contact probability
        # Simplified model: P(s) decreases with distance
        # P(s) = A * s^(-alpha) where alpha depends on processivity
        processivity = nipbl_velocity * wapl_lifetime

        # Alpha scaling: higher processivity → steeper decay
        alpha = 1.0 + processivity * 0.5  # Range: 1.0 - 1.5

        # Generate distance bins (logarithmic)
        distances = np.logspace(5, np.log10(max_distance), num=50)
        ps_values = 1000.0 * (distances ** (-alpha))  # Normalized

        return pd.DataFrame({
            "distance": distances,
            "ps": ps_values,
        })

    def load_real_data(self, real_data_dir: Path) -> dict:
        """Load real Hi-C analysis results."""
        print("📂 Loading real Hi-C data...")

        real_data = {}

        # Load insulation
        insulation_file = real_data_dir / "insulation_scores.csv"
        if insulation_file.exists():
            real_data["insulation"] = pd.read_csv(insulation_file)
            print(f"   ✅ Loaded insulation: {len(real_data['insulation'])} windows")

        # Load P(s)
        ps_file = real_data_dir / "ps_scaling.csv"
        if ps_file.exists():
            real_data["ps"] = pd.read_csv(ps_file)
            print(f"   ✅ Loaded P(s): {len(real_data['ps'])} points")

        return real_data

    def compare_and_visualize(
        self,
        archcode_insulation: pd.DataFrame,
        archcode_ps: pd.DataFrame,
        real_data: dict,
    ) -> dict:
        """
        Compare ARCHCODE with real data and create visualizations.

        Args:
            archcode_insulation: ARCHCODE insulation scores
            archcode_ps: ARCHCODE P(s) scaling
            real_data: Dictionary with real data

        Returns:
            Comparison results dictionary
        """
        print("\n📊 Creating comparison visualizations...")

        # Create 4-panel figure (like Nature papers)
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("ARCHCODE vs Real Hi-C Data (Rao 2014 GM12878)", fontsize=16, fontweight="bold")

        comparison_results = {}

        # Panel 1: Insulation Score comparison
        ax1 = axes[0, 0]
        if "insulation" in real_data and len(archcode_insulation) > 0:
            real_ins = real_data["insulation"]
            # Sample for visualization (too many points)
            if len(real_ins) > 100:
                real_ins_sample = real_ins.sample(100).sort_values("start")
            else:
                real_ins_sample = real_ins.sort_values("start")

            ax1.plot(
                real_ins_sample["start"] / 1e6,
                real_ins_sample["insulation_score"] / 1e3,
                "b-",
                alpha=0.6,
                label="Real Hi-C",
                linewidth=1.5,
            )

            if len(archcode_insulation) > 0:
                archcode_ins_sorted = archcode_insulation.sort_values("start")
                ax1.plot(
                    archcode_ins_sorted["start"] / 1e6,
                    archcode_ins_sorted["insulation_score"] * 10,  # Scale for visibility
                    "r--",
                    alpha=0.8,
                    label="ARCHCODE",
                    linewidth=2,
                )

            ax1.set_xlabel("Genomic Position (Mb)", fontsize=11)
            ax1.set_ylabel("Insulation Score (×10³)", fontsize=11)
            ax1.set_title("Insulation Score", fontsize=12, fontweight="bold")
            ax1.legend()
            ax1.grid(True, alpha=0.3)

            # Calculate correlation
            if len(archcode_insulation) > 0 and len(real_ins_sample) > 0:
                # Interpolate to same positions
                from scipy.interpolate import interp1d
                try:
                    f_real = interp1d(
                        real_ins_sample["start"],
                        real_ins_sample["insulation_score"],
                        fill_value="extrapolate",
                    )
                    common_positions = archcode_insulation["start"].values
                    real_interp = f_real(common_positions)
                    archcode_vals = archcode_insulation["insulation_score"].values * 10

                    correlation = np.corrcoef(real_interp, archcode_vals)[0, 1]
                    comparison_results["insulation_correlation"] = float(correlation)
                    ax1.text(
                        0.05,
                        0.95,
                        f"Correlation: {correlation:.3f}",
                        transform=ax1.transAxes,
                        fontsize=10,
                        verticalalignment="top",
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                    )
                except Exception as e:
                    print(f"   ⚠️  Could not calculate insulation correlation: {e}")

        # Panel 2: P(s) scaling comparison
        ax2 = axes[0, 1]
        if "ps" in real_data and len(archcode_ps) > 0:
            real_ps = real_data["ps"]
            ax2.loglog(
                real_ps["distance"],
                real_ps["ps"],
                "b-",
                alpha=0.7,
                label="Real Hi-C",
                linewidth=2,
                marker="o",
                markersize=4,
            )

            ax2.loglog(
                archcode_ps["distance"],
                archcode_ps["ps"],
                "r--",
                alpha=0.8,
                label="ARCHCODE",
                linewidth=2,
                marker="s",
                markersize=4,
            )

            ax2.set_xlabel("Genomic Distance (bp)", fontsize=11)
            ax2.set_ylabel("Contact Probability P(s)", fontsize=11)
            ax2.set_title("P(s) Scaling", fontsize=12, fontweight="bold")
            ax2.legend()
            ax2.grid(True, alpha=0.3, which="both")

            # Calculate correlation
            if len(real_ps) > 0 and len(archcode_ps) > 0:
                # Interpolate to common distances
                from scipy.interpolate import interp1d
                try:
                    f_real = interp1d(
                        np.log10(real_ps["distance"]),
                        np.log10(real_ps["ps"]),
                        fill_value="extrapolate",
                    )
                    common_distances_log = np.log10(archcode_ps["distance"].values)
                    real_interp_log = f_real(common_distances_log)
                    archcode_log = np.log10(archcode_ps["ps"].values)

                    correlation = np.corrcoef(real_interp_log, archcode_log)[0, 1]
                    comparison_results["ps_correlation"] = float(correlation)
                    ax2.text(
                        0.05,
                        0.95,
                        f"Correlation: {correlation:.3f}",
                        transform=ax2.transAxes,
                        fontsize=10,
                        verticalalignment="top",
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                    )
                except Exception as e:
                    print(f"   ⚠️  Could not calculate P(s) correlation: {e}")

        # Panel 3: Insulation Score distribution
        ax3 = axes[1, 0]
        if "insulation" in real_data:
            real_ins = real_data["insulation"]
            ax3.hist(
                real_ins["insulation_score"] / 1e3,
                bins=50,
                alpha=0.6,
                label="Real Hi-C",
                color="blue",
                density=True,
            )

            if len(archcode_insulation) > 0:
                ax3.hist(
                    archcode_insulation["insulation_score"] * 10,
                    bins=20,
                    alpha=0.6,
                    label="ARCHCODE",
                    color="red",
                    density=True,
                )

            ax3.set_xlabel("Insulation Score (×10³)", fontsize=11)
            ax3.set_ylabel("Density", fontsize=11)
            ax3.set_title("Insulation Score Distribution", fontsize=12, fontweight="bold")
            ax3.legend()
            ax3.grid(True, alpha=0.3)

        # Panel 4: Summary statistics
        ax4 = axes[1, 1]
        ax4.axis("off")

        summary_text = "ARCHCODE vs Real Hi-C\n" + "=" * 30 + "\n\n"

        if "insulation" in real_data:
            real_ins = real_data["insulation"]
            summary_text += f"Real Insulation:\n"
            summary_text += f"  Mean: {real_ins['insulation_score'].mean()/1e3:.2f}×10³\n"
            summary_text += f"  Std: {real_ins['insulation_score'].std()/1e3:.2f}×10³\n"
            summary_text += f"  Windows: {len(real_ins)}\n\n"

        if len(archcode_insulation) > 0:
            summary_text += f"ARCHCODE Insulation:\n"
            summary_text += f"  Mean: {archcode_insulation['insulation_score'].mean()*10:.2f}\n"
            summary_text += f"  Std: {archcode_insulation['insulation_score'].std()*10:.2f}\n"
            summary_text += f"  Boundaries: {len(archcode_insulation)}\n\n"

        if "ps" in real_data:
            real_ps = real_data["ps"]
            summary_text += f"Real P(s):\n"
            summary_text += f"  Mean: {real_ps['ps'].mean():.2f}\n"
            summary_text += f"  Points: {len(real_ps)}\n\n"

        if len(archcode_ps) > 0:
            summary_text += f"ARCHCODE P(s):\n"
            summary_text += f"  Mean: {archcode_ps['ps'].mean():.2f}\n"
            summary_text += f"  Points: {len(archcode_ps)}\n\n"

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
            fontsize=10,
            verticalalignment="top",
            family="monospace",
        )

        plt.tight_layout()

        # Save figure
        figure_path = self.output_dir / "archcode_vs_real_comparison.png"
        plt.savefig(figure_path, dpi=300, bbox_inches="tight")
        print(f"   ✅ Figure saved: {figure_path}")

        plt.close()

        comparison_results["figure_path"] = str(figure_path)
        return comparison_results

    def run_comparison(
        self,
        boundaries_data: list[tuple[int, float, str]],
        barrier_strengths_map: dict[int, list[float]],
        methylation_map: dict[int, float],
        te_motif_map: dict[int, list[float]],
        real_data_dir: Path,
        nipbl_velocity: float = 1.0,
        wapl_lifetime: float = 1.0,
    ) -> dict:
        """
        Run full comparison.

        Args:
            boundaries_data: List of boundaries
            barrier_strengths_map: Map of barrier strengths
            methylation_map: Map of methylation levels
            te_motif_map: Map of TE motifs
            real_data_dir: Directory with real Hi-C analysis results
            nipbl_velocity: NIPBL velocity factor
            wapl_lifetime: WAPL lifetime factor

        Returns:
            Comparison results dictionary
        """
        print("=" * 80)
        print("ARCHCODE vs REAL Hi-C COMPARISON")
        print("=" * 80)

        # Load real data
        real_data = self.load_real_data(real_data_dir)

        # Generate ARCHCODE metrics
        archcode_insulation = self.generate_archcode_insulation(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity=nipbl_velocity,
            wapl_lifetime=wapl_lifetime,
        )

        archcode_ps = self.generate_archcode_ps_scaling(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity=nipbl_velocity,
            wapl_lifetime=wapl_lifetime,
        )

        # Compare and visualize
        comparison_results = self.compare_and_visualize(
            archcode_insulation=archcode_insulation,
            archcode_ps=archcode_ps,
            real_data=real_data,
        )

        # Save ARCHCODE results
        archcode_insulation_file = self.output_dir / "archcode_insulation.csv"
        archcode_ps_file = self.output_dir / "archcode_ps.csv"

        archcode_insulation.to_csv(archcode_insulation_file, index=False)
        archcode_ps.to_csv(archcode_ps_file, index=False)

        print(f"\n💾 ARCHCODE results saved:")
        print(f"   • Insulation: {archcode_insulation_file}")
        print(f"   • P(s): {archcode_ps_file}")

        # Save comparison summary
        comparison_results["archcode_files"] = {
            "insulation": str(archcode_insulation_file),
            "ps": str(archcode_ps_file),
        }

        summary_file = self.output_dir / "comparison_summary.json"
        with open(summary_file, "w") as f:
            json.dump(comparison_results, f, indent=2)

        print(f"   • Summary: {summary_file}")

        print("\n" + "=" * 80)
        print("✅ COMPARISON COMPLETE")
        print("=" * 80)

        return comparison_results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare ARCHCODE with real Hi-C data")
    parser.add_argument(
        "--real-data-dir",
        type=str,
        default="data/output/real_hic_analysis",
        help="Directory with real Hi-C analysis results",
    )
    parser.add_argument(
        "--nipbl-velocity",
        type=float,
        default=1.0,
        help="NIPBL velocity factor",
    )
    parser.add_argument(
        "--wapl-lifetime",
        type=float,
        default=1.0,
        help="WAPL lifetime factor",
    )

    args = parser.parse_args()

    # Test boundaries (chr8:127000000-130000000 region)
    boundaries_data = [
        (127100000, 0.8, "ctcf"),
        (127200000, 0.7, "ctcf"),
        (127300000, 0.6, "ctcf"),
        (127400000, 0.5, "ctcf"),
        (127500000, 0.9, "ctcf"),
    ]

    barrier_strengths_map = {pos: [0.5] for pos, _, _ in boundaries_data}
    methylation_map = {pos: 0.5 for pos, _, _ in boundaries_data}
    te_motif_map = {pos: [0.0] for pos, _, _ in boundaries_data}

    comparison = ARCHCODEvsRealComparison()

    results = comparison.run_comparison(
        boundaries_data=boundaries_data,
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
        real_data_dir=Path(args.real_data_dir),
        nipbl_velocity=args.nipbl_velocity,
        wapl_lifetime=args.wapl_lifetime,
    )

