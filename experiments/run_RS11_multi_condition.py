"""RS-11 Multi-Condition Benchmarking.

Runner script для генерации полного набора Figure 4 для всех условий.
"""

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.benchmark_vs_real import create_figure_4
from src.archcode_core.full_pipeline import ARCHCODEFullPipeline
from src.vizir.config_loader import VIZIRConfigLoader

# Определяем регион для анализа.
# СОВЕТ: Для теста берем chr8 (MYC locus) или chr2.
# Это богатые генами регионы с четкими TADs.
TEST_REGION = "chr8:127000000-130000000"  # 3 Mb регион

# Конфигурация условий для бенчмарка
CONDITIONS = [
    # 1. Wild Type (Эталон)
    {
        "name": "WT_GM12878",
        # Обратите внимание на URI синтаксис для mcool
        "real_path": "data/real/WT_GM12878.mcool::/resolutions/10000",
        "region": TEST_REGION,
        # Параметры модели для WT (Stable Phase)
        "sim_params": {
            "processivity": 1.0,  # NIPBL * WAPL
            "bookmarking": 0.8,  # High memory
            "ctcf_occupancy": 0.9,  # High insulation
        },
    },
    # 2. CdLS-like (NIPBL depletion)
    {
        "name": "CdLS_HCT116_Auxin",
        "real_path": "data/real/CdLS_Like_HCT116.mcool::/resolutions/10000",
        "region": TEST_REGION,
        # Параметры модели для CdLS (Unstable Phase)
        "sim_params": {
            "processivity": 0.5,  # LOW processivity (Unstable)
            "bookmarking": 0.8,  # Память не страдает, страдает архитектура
            "ctcf_occupancy": 0.9,
        },
    },
    # 3. WAPL-KO (Hyper-stability)
    {
        "name": "WAPL_KO_HAP1",
        # Для .cool (после конвертации из .hic) суффикс разрешения не нужен,
        # так как мы конвертировали сразу в 10kb
        "real_path": "data/real/WAPL_KO_HAP1_10kb.cool",
        "region": TEST_REGION,
        # Параметры модели для WAPL-KO (Hyper-Stable Phase)
        "sim_params": {
            "processivity": 2.0,  # HIGH processivity (Vermicelli)
            "bookmarking": 0.8,
            "ctcf_occupancy": 0.9,
        },
    },
]


class RS11MultiConditionBenchmark:
    """Multi-condition benchmarking runner."""

    def __init__(self) -> None:
        """Инициализация."""
        self.loader = VIZIRConfigLoader()
        self.output_dir = Path("figures/RS11")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = Path("data/output/RS11")
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def generate_simulation_matrix(
        self,
        condition_name: str,
        processivity: float,
        bookmarking: float = 0.8,
        ctcf_occupancy: float = 0.9,
    ) -> np.ndarray:
        """
        Generate simulation matrix for condition.

        Args:
            condition_name: Name of condition
            processivity: Processivity factor (NIPBL * WAPL)
            bookmarking: Bookmarking fraction (0-1)
            ctcf_occupancy: CTCF occupancy factor (0-1)

        Returns:
            Contact matrix (numpy array)
        """
        print(f"\n[RS-11] Generating simulation for {condition_name}...")
        print(f"  Processivity={processivity:.2f}, Bookmarking={bookmarking:.2f}, CTCF={ctcf_occupancy:.2f}")

        # Convert processivity to NIPBL and WAPL factors
        # For simplicity: processivity = NIPBL * WAPL
        # We assume NIPBL controls velocity, WAPL controls lifetime
        # For WT: nipbl=1.0, wapl=1.0 → processivity=1.0
        # For CdLS: nipbl=0.5, wapl=1.0 → processivity=0.5
        # For WAPL-KO: nipbl=1.0, wapl=2.0 → processivity=2.0
        if processivity <= 1.0:
            # Low processivity: reduce NIPBL
            nipbl_velocity = processivity
            wapl_lifetime = 1.0
        else:
            # High processivity: increase WAPL lifetime
            nipbl_velocity = 1.0
            wapl_lifetime = processivity

        bookmarking_fraction = bookmarking

        # Test data - adjust CTCF occupancy based on parameter
        # Scale barrier positions and strengths based on region size
        # For chr8:127000000-130000000 (3Mb region)
        base_positions = [127100000, 127200000, 127300000, 127400000, 127500000]
        ctcf_strengths = [ctcf_occupancy * 0.9, ctcf_occupancy * 0.8, ctcf_occupancy * 0.7, 
                         ctcf_occupancy * 0.6, ctcf_occupancy * 0.9]
        
        boundaries_data = [
            (pos, strength, "ctcf") for pos, strength in zip(base_positions, ctcf_strengths)
        ]

        barrier_strengths_map = {
            base_positions[0]: [0.1 * ctcf_occupancy],
            base_positions[1]: [0.2 * ctcf_occupancy],
            base_positions[2]: [0.6 * ctcf_occupancy],
            base_positions[3]: [0.8 * ctcf_occupancy],
            base_positions[4]: [0.1 * ctcf_occupancy],
        }

        methylation_map = {
            base_positions[0]: 0.1,
            base_positions[1]: 0.2,
            base_positions[2]: 0.7,
            base_positions[3]: 0.9,
            base_positions[4]: 0.3,
        }

        te_motif_map = {
            base_positions[0]: [0.0],
            base_positions[1]: [0.0],
            base_positions[2]: [0.3],
            base_positions[3]: [0.5],
            base_positions[4]: [0.0],
        }

        # Load VIZIR configs
        vizir_configs = {
            **self.loader.load_all_physical(),
            **self.loader.load_all_structural(),
            **self.loader.load_all_logical(),
        }

        # Run pipeline
        pipeline = ARCHCODEFullPipeline(vizir_configs=vizir_configs)
        results = pipeline.run_full_analysis(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            collapse_events=None,
            enhancer_promoter_pairs=None,
            nipbl_velocity_factor=nipbl_velocity,
            wapl_lifetime_factor=wapl_lifetime,
        )

        # Generate contact matrix from stability predictions
        # This is a simplified version - in real implementation,
        # you would use the actual extrusion engine output
        n_bins = 100  # Default size
        matrix = np.zeros((n_bins, n_bins))

        # Fill matrix based on stability predictions
        stability_predictions = results.get("stability_predictions", [])
        for pred in stability_predictions:
            if isinstance(pred, dict):
                pos = pred.get("position", 0)
                stability = pred.get("stability_score", 0.0)
            else:
                pos = pred.position
                stability = pred.stability_score

            # Convert position to bin index
            bin_idx = min(int(pos / 10000), n_bins - 1)

            # Fill diagonal and nearby bins
            for i in range(max(0, bin_idx - 5), min(n_bins, bin_idx + 6)):
                for j in range(max(0, bin_idx - 5), min(n_bins, bin_idx + 6)):
                    dist = abs(i - j)
                    if dist > 0:
                        matrix[i, j] += stability / (dist**0.5)

        # Symmetrize
        matrix = (matrix + matrix.T) / 2

        return matrix

    def run_multi_condition_benchmark(
        self,
        conditions_config: list[dict[str, Any]] | None = None,
    ) -> dict:
        """
        Run benchmarking for all conditions from configuration.

        Args:
            conditions_config: List of condition configurations.
                             If None, uses global CONDITIONS.

        Returns:
            Results dictionary
        """
        print("=" * 60)
        print("RS-11 Multi-Condition Benchmarking")
        print("=" * 60)

        if conditions_config is None:
            conditions_config = CONDITIONS

        results = {}

        for condition_config in conditions_config:
            condition_name = condition_config["name"]
            real_path = condition_config["real_path"]
            region = condition_config.get("region", TEST_REGION)
            sim_params = condition_config["sim_params"]

            print(f"\n{'=' * 60}")
            print(f"Condition: {condition_name}")
            print(f"{'=' * 60}")
            print(f"Real data: {real_path}")
            print(f"Region: {region}")
            print(f"Sim params: {sim_params}")

            # Check if real file exists
            # Extract file path from URI if needed
            file_path = real_path.split("::")[0]
            if not Path(file_path).exists():
                print(f"⚠️  Warning: Real data file not found: {file_path}")
                print(f"   Skipping {condition_name}...")
                results[condition_name] = {
                    "status": "skipped",
                    "reason": f"File not found: {file_path}",
                }
                continue

            # Generate simulation matrix
            sim_matrix = self.generate_simulation_matrix(
                condition_name=condition_name,
                processivity=sim_params["processivity"],
                bookmarking=sim_params["bookmarking"],
                ctcf_occupancy=sim_params["ctcf_occupancy"],
            )

            # Save simulation matrix
            sim_matrix_path = self.data_dir / f"{condition_name}_matrix.npy"
            np.save(sim_matrix_path, sim_matrix)
            print(f"[RS-11] Saved simulation matrix: {sim_matrix_path}")

            # Generate Figure 4
            output_path = self.output_dir / f"Figure_4_{condition_name}.png"
            try:
                create_figure_4(
                    real_cooler_path=real_path,
                    sim_matrix_path=str(sim_matrix_path),
                    region=region,
                    output_path=str(output_path),
                    condition_name=condition_name,
                )
                results[condition_name] = {
                    "status": "success",
                    "figure_path": str(output_path),
                    "sim_matrix_path": str(sim_matrix_path),
                    "real_path": real_path,
                    "region": region,
                }
            except Exception as e:
                print(f"[RS-11] Error generating figure: {e}")
                import traceback
                traceback.print_exc()
                results[condition_name] = {
                    "status": "error",
                    "error": str(e),
                }

        return results

    def save_results(
        self, results: dict, filename: str = "RS11_multi_condition_results.json"
    ) -> Path:
        """Сохранить результаты."""
        output_path = self.data_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        return output_path


def main() -> None:
    """Запуск multi-condition benchmarking."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RS-11 Multi-Condition Benchmarking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all conditions from configuration
  python experiments/run_RS11_multi_condition.py

  # Run single condition (legacy mode)
  python experiments/run_RS11_multi_condition.py \\
      --real-cooler "data/real/WT_GM12878.mcool::/resolutions/10000" \\
      --region "chr8:127000000-130000000"
        """,
    )
    parser.add_argument(
        "--real-cooler",
        type=str,
        default=None,
        help="Path to real Hi-C cooler file (or URI). If not provided, uses CONDITIONS config.",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Optional region string (overrides config if provided)",
    )
    parser.add_argument(
        "--condition",
        type=str,
        default=None,
        help="Run specific condition by name (from CONDITIONS config)",
    )

    args = parser.parse_args()

    benchmark = RS11MultiConditionBenchmark()

    # If --real-cooler provided, use legacy single-condition mode
    if args.real_cooler:
        # Legacy mode: single condition
        print("[RS-11] Running in legacy single-condition mode")
        condition_name = args.condition or "WT"
        sim_params = {
            "processivity": 1.0,
            "bookmarking": 0.8,
            "ctcf_occupancy": 0.9,
        }
        
        # Generate simulation
        sim_matrix = benchmark.generate_simulation_matrix(
            condition_name=condition_name,
            **sim_params,
        )
        
        sim_matrix_path = benchmark.data_dir / f"{condition_name}_matrix.npy"
        np.save(sim_matrix_path, sim_matrix)
        
        # Generate figure
        output_path = benchmark.output_dir / f"Figure_4_{condition_name}.png"
        create_figure_4(
            real_cooler_path=args.real_cooler,
            sim_matrix_path=str(sim_matrix_path),
            region=args.region,
            output_path=str(output_path),
            condition_name=condition_name,
        )
        
        results = {condition_name: {"status": "success", "figure_path": str(output_path)}}
    else:
        # New mode: use CONDITIONS config
        conditions_to_run = CONDITIONS
        
        # Filter by --condition if specified
        if args.condition:
            conditions_to_run = [c for c in CONDITIONS if c["name"] == args.condition]
            if not conditions_to_run:
                print(f"❌ Error: Condition '{args.condition}' not found in CONDITIONS")
                print(f"Available conditions: {[c['name'] for c in CONDITIONS]}")
                return
        
        # Override region if provided
        if args.region:
            for cond in conditions_to_run:
                cond["region"] = args.region
        
        results = benchmark.run_multi_condition_benchmark(conditions_config=conditions_to_run)

    # Save results
    output_path = benchmark.save_results(results)
    print(f"\n✅ Results saved: {output_path}")

    print("\n" + "=" * 60)
    print("✅ RS-11 Multi-Condition Benchmarking Complete")
    print("=" * 60)
    
    # Print summary
    print("\n📊 Summary:")
    for name, result in results.items():
        status = result.get("status", "unknown")
        if status == "success":
            print(f"  ✅ {name}: {result.get('figure_path', 'N/A')}")
        elif status == "skipped":
            print(f"  ⏭️  {name}: {result.get('reason', 'Skipped')}")
        else:
            print(f"  ❌ {name}: {result.get('error', 'Failed')}")


if __name__ == "__main__":
    main()


