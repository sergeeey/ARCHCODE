"""
RS-13: Multi-Condition Benchmark

Compares ARCHCODE predictions with multiple real Hi-C conditions:
- WT (Wild-type)
- CdLS (NIPBL haploinsufficiency)
- WAPL-KO (WAPL knockout)

For each condition:
1. Loads real Hi-C data
2. Computes bio-metrics (insulation, P(s), APA, boundaries)
3. Runs ARCHCODE simulation with condition-specific parameters
4. Compares metrics and generates figures
"""

import json
import sys
import warnings
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import cooler
from experiments.compute_real_insulation import (
    compute_insulation_score,
    compute_ps_scaling,
)
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.archcode_core.cell_cycle import CellCyclePhase
from src.vizir.config_loader import VIZIRConfigLoader

warnings.filterwarnings("ignore")


class RS13MultiConditionBenchmark:
    """Multi-condition benchmark comparing ARCHCODE with real Hi-C data."""

    def __init__(self, config_path: Path | str = "configs/rs13_multi_condition.yaml"):
        """Initialize benchmark."""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.output_dir = Path(self.config["output_dir"])
        self.figures_dir = Path(self.config.get("figures_dir", "figures/RS13"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        # Load VIZIR configs
        loader = VIZIRConfigLoader()
        self.vizir_configs = {
            **loader.load_all_physical(),
            **loader.load_all_structural(),
            **loader.load_all_logical(),
        }

        self.results = {}

    def _load_config(self) -> dict:
        """Load configuration from YAML."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _check_file_exists(self, filepath: str) -> bool:
        """Check if file exists, return False if not."""
        path = Path(filepath)
        if not path.exists():
            return False
        return True

    def load_real_hic(self, cooler_path: str) -> cooler.Cooler | None:
        """Load real Hi-C cooler file."""
        if not self._check_file_exists(cooler_path):
            return None

        try:
            c = cooler.Cooler(cooler_path)
            print(f"  ✅ Loaded: {c.info.get('genome-assembly', 'Unknown')}")
            print(f"     Bins: {c.info['nbins']:,}, Contacts: {c.info['nnz']:,}")
            return c
        except Exception as e:
            print(f"  ❌ Error loading cooler: {e}")
            return None

    def compute_real_metrics(
        self, cooler_obj: cooler.Cooler, condition_id: str
    ) -> dict[str, Any]:
        """Compute bio-metrics from real Hi-C data."""
        print(f"\n📊 Computing real Hi-C metrics for {condition_id}...")

        metrics = {}
        metrics_config = self.config.get("metrics", {})

        # Insulation Score
        if metrics_config.get("compute_insulation", True):
            try:
                insulation_df = compute_insulation_score(
                    cooler_obj, window_size=500000, resolution=1000000
                )
                metrics["insulation"] = insulation_df
                print(f"  ✅ Insulation: {len(insulation_df)} windows")
            except Exception as e:
                print(f"  ⚠️  Insulation error: {e}")
                metrics["insulation"] = None

        # P(s) curve
        if metrics_config.get("compute_ps", True):
            try:
                ps_df = compute_ps_scaling(cooler_obj, max_distance=10000000)
                metrics["ps"] = ps_df
                print(f"  ✅ P(s): {len(ps_df)} distance bins")
            except Exception as e:
                print(f"  ⚠️  P(s) error: {e}")
                metrics["ps"] = None

        # APA (simplified - aggregate peak analysis)
        if metrics_config.get("compute_apa", True):
            try:
                # Simple APA: mean contact enrichment around boundaries
                apa_score = self._compute_simple_apa(cooler_obj)
                metrics["apa_score"] = apa_score
                print(f"  ✅ APA score: {apa_score:.3f}")
            except Exception as e:
                print(f"  ⚠️  APA error: {e}")
                metrics["apa_score"] = None

        return metrics

    def _compute_simple_apa(self, cooler_obj: cooler.Cooler) -> float:
        """Compute simplified APA score (mean enrichment around boundaries)."""
        # Get insulation to find boundaries
        try:
            insulation_df = compute_insulation_score(
                cooler_obj, window_size=500000, resolution=1000000
            )
            # Find boundaries (local minima in insulation)
            boundaries = insulation_df.nsmallest(10, "insulation_score")["start"].values

            # Compute mean contact enrichment around boundaries
            apa_scores = []
            for boundary in boundaries[:5]:  # Use top 5 boundaries
                try:
                    # Get region around boundary (±500kb)
                    region_start = max(0, boundary - 500000)
                    region_end = boundary + 500000

                    # Extract contact matrix around boundary
                    matrix = cooler_obj.matrix(balance=True).fetch(
                        f"chr8:{region_start}-{region_end}"
                    )
                    if matrix.size > 0:
                        # Mean off-diagonal contacts (enrichment)
                        n = len(matrix)
                        off_diag = matrix[np.triu_indices(n, k=1)]
                        apa_scores.append(np.mean(off_diag))
                except Exception:
                    continue

            return np.mean(apa_scores) if apa_scores else 0.0
        except Exception:
            return 0.0

    def run_archcode_simulation(
        self, condition_config: dict, condition_id: str
    ) -> dict[str, Any]:
        """Run ARCHCODE simulation for given condition."""
        print(f"\n🔬 Running ARCHCODE simulation for {condition_id}...")

        sim_params = condition_config.get("sim_params", {})
        nipbl_velocity = sim_params.get("nipbl_velocity", 1.0)
        wapl_lifetime = sim_params.get("wapl_lifetime", 1.0)
        bookmarking_fraction = sim_params.get("bookmarking_fraction", 0.8)

        # Default boundaries (chr8 test region)
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

        # Create pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=self.vizir_configs)

        # Add boundaries
        for pos, strength, btype in boundaries_data:
            pipeline.pipeline.add_boundary(
                position=pos, strength=strength, barrier_type=btype
            )

        # Run analysis
        predictions = pipeline.pipeline.analyze_all_boundaries(
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
            cell_cycle_phase=CellCyclePhase.INTERPHASE,
            enable_bookmarking=True,
        )

        # Extract simulated metrics
        sim_metrics = {
            "boundaries": [
                {
                    "position": b.position,
                    "strength": b.strength,
                    "stability": getattr(b, "stability_score", 0.0),
                }
                for b in pipeline.pipeline.boundaries
            ],
            "nipbl_velocity": nipbl_velocity,
            "wapl_lifetime": wapl_lifetime,
            "processivity": nipbl_velocity * wapl_lifetime,
            "bookmarking_fraction": bookmarking_fraction,
        }

        print(f"  ✅ Simulated {len(sim_metrics['boundaries'])} boundaries")
        return sim_metrics

    def compare_metrics(
        self, real_metrics: dict, sim_metrics: dict, condition_id: str
    ) -> dict[str, Any]:
        """Compare real and simulated metrics."""
        comparison = {
            "condition_id": condition_id,
            "metrics": {},
        }

        # P(s) comparison
        if real_metrics.get("ps") is not None:
            try:
                real_ps = real_metrics["ps"]
                # Compute correlation (simplified - would need simulated P(s))
                # For now, just store real P(s) data
                comparison["metrics"]["ps"] = {
                    "real_data_points": len(real_ps),
                    "ps_correlation": None,  # Would compute if we had sim P(s)
                }
            except Exception as e:
                print(f"  ⚠️  P(s) comparison error: {e}")

        # Insulation comparison
        if real_metrics.get("insulation") is not None:
            try:
                real_ins = real_metrics["insulation"]
                # Compute correlation with simulated boundary strengths
                sim_boundaries = {
                    b["position"]: b["stability"]
                    for b in sim_metrics.get("boundaries", [])
                }

                # Match positions and compute correlation
                matched_scores = []
                for _, row in real_ins.iterrows():
                    pos = row["start"]
                    # Find closest simulated boundary
                    closest_pos = min(
                        sim_boundaries.keys(), key=lambda x: abs(x - pos)
                    )
                    if abs(closest_pos - pos) < 500000:  # Within 500kb
                        matched_scores.append(
                            (row["insulation_score"], sim_boundaries[closest_pos])
                        )

                if matched_scores:
                    real_vals, sim_vals = zip(*matched_scores)
                    correlation = np.corrcoef(real_vals, sim_vals)[0, 1]
                    comparison["metrics"]["insulation"] = {
                        "correlation": float(correlation),
                        "matched_points": len(matched_scores),
                    }
            except Exception as e:
                print(f"  ⚠️  Insulation comparison error: {e}")

        # APA comparison
        if real_metrics.get("apa_score") is not None:
            comparison["metrics"]["apa"] = {
                "real_score": float(real_metrics["apa_score"]),
                "sim_score": None,  # Would compute from sim if needed
            }

        return comparison

    def plot_comparison(
        self, real_metrics: dict, sim_metrics: dict, condition_id: str
    ) -> list[Path]:
        """Generate comparison figures."""
        figures = []

        # P(s) plot
        if real_metrics.get("ps") is not None:
            try:
                fig, ax = plt.subplots(figsize=(8, 6))
                ps_df = real_metrics["ps"]
                ax.loglog(ps_df["distance"], ps_df["contact_prob"], "b-", label="Real")
                ax.set_xlabel("Genomic Distance (bp)")
                ax.set_ylabel("Contact Probability P(s)")
                ax.set_title(f"P(s) Scaling - {condition_id}")
                ax.legend()
                ax.grid(True, alpha=0.3)

                fig_path = self.figures_dir / f"RS13_ps_{condition_id}.png"
                fig.savefig(fig_path, dpi=150, bbox_inches="tight")
                plt.close(fig)
                figures.append(fig_path)
                print(f"  ✅ Saved: {fig_path.name}")
            except Exception as e:
                print(f"  ⚠️  P(s) plot error: {e}")

        # Insulation plot
        if real_metrics.get("insulation") is not None:
            try:
                fig, ax = plt.subplots(figsize=(12, 4))
                ins_df = real_metrics["insulation"]
                ax.plot(ins_df["start"], ins_df["insulation_score"], "b-", label="Real")
                # Add simulated boundaries
                sim_boundaries = sim_metrics.get("boundaries", [])
                for b in sim_boundaries:
                    ax.axvline(
                        b["position"],
                        color="r",
                        linestyle="--",
                        alpha=0.5,
                        label="ARCHCODE" if b == sim_boundaries[0] else "",
                    )
                ax.set_xlabel("Genomic Position (bp)")
                ax.set_ylabel("Insulation Score")
                ax.set_title(f"Insulation Score - {condition_id}")
                ax.legend()
                ax.grid(True, alpha=0.3)

                fig_path = self.figures_dir / f"RS13_insulation_{condition_id}.png"
                fig.savefig(fig_path, dpi=150, bbox_inches="tight")
                plt.close(fig)
                figures.append(fig_path)
                print(f"  ✅ Saved: {fig_path.name}")
            except Exception as e:
                print(f"  ⚠️  Insulation plot error: {e}")

        return figures

    def run_benchmark(self) -> dict[str, Any]:
        """Run complete multi-condition benchmark."""
        print("=" * 80)
        print("RS-13: MULTI-CONDITION BENCHMARK")
        print("=" * 80)
        print()

        conditions = self.config.get("conditions", [])
        all_results = {}

        for condition_config in conditions:
            condition_id = condition_config["id"]
            condition_name = condition_config.get("name", condition_id)
            cooler_path = condition_config["cooler"]
            required = condition_config.get("required", True)

            print(f"\n{'='*80}")
            print(f"Condition: {condition_name} ({condition_id})")
            print(f"{'='*80}")

            # Check if file exists
            if not self._check_file_exists(cooler_path):
                if required:
                    print(f"❌ Required file not found: {cooler_path}")
                    print("   Skipping condition...")
                    continue
                else:
                    print(f"⚠️  Optional file not found: {cooler_path}")
                    print("   Skipping condition...")
                    continue

            # Load real Hi-C
            cooler_obj = self.load_real_hic(cooler_path)
            if cooler_obj is None:
                continue

            # Compute real metrics
            real_metrics = self.compute_real_metrics(cooler_obj, condition_id)

            # Run ARCHCODE simulation
            sim_metrics = self.run_archcode_simulation(condition_config, condition_id)

            # Compare metrics
            comparison = self.compare_metrics(real_metrics, sim_metrics, condition_id)

            # Generate figures
            figures = self.plot_comparison(real_metrics, sim_metrics, condition_id)

            # Store results
            condition_result = {
                "condition_id": condition_id,
                "condition_name": condition_name,
                "real_metrics": {
                    k: (
                        v.to_dict() if isinstance(v, pd.DataFrame) else v
                        for k, v in real_metrics.items()
                    )
                    if isinstance(real_metrics, dict)
                    else {},
                },
                "sim_metrics": sim_metrics,
                "comparison": comparison,
                "figures": [str(f) for f in figures],
            }

            # Save individual condition result
            condition_file = (
                self.output_dir / f"RS13_{condition_id}_comparison.json"
            )
            with open(condition_file, "w") as f:
                json.dump(condition_result, f, indent=2, default=str)

            all_results[condition_id] = condition_result

        # Save summary
        summary = {
            "total_conditions": len(conditions),
            "processed_conditions": len(all_results),
            "conditions": list(all_results.keys()),
            "results": all_results,
        }

        summary_file = self.output_dir / "RS13_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print("\n" + "=" * 80)
        print("RS-13 BENCHMARK COMPLETE")
        print("=" * 80)
        print(f"✅ Processed {len(all_results)} conditions")
        print(f"💾 Summary: {summary_file}")
        print(f"📊 Figures: {self.figures_dir}")

        return summary


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RS-13: Multi-Condition Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/rs13_multi_condition.yaml",
        help="Path to configuration file",
    )

    args = parser.parse_args()

    benchmark = RS13MultiConditionBenchmark(config_path=args.config)
    results = benchmark.run_benchmark()

    print("\n✅ RS-13 Multi-Condition Benchmark completed successfully!")


if __name__ == "__main__":
    main()

