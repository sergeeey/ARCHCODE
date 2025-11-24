"""
Adapter between external orchestration system (TERAG) and ARCHCODE core.

Provides standardized interface for running ARCHCODE experiments
and returning JSON-serializable results.
"""

import time
from typing import Any

from src.archcode_core.api import (
    run_rs09_summary,
    run_rs10_summary,
    run_rs11_summary,
    run_real_benchmark_summary,
)


class ArchcodeAdapter:
    """
    Adapter between external orchestration system (TERAG) and ARCHCODE core.
    """

    def __init__(self, mode: str = "fast"):
        """
        Initialize adapter.

        Args:
            mode: 'fast' | 'production'
                fast       — минимальная сетка, быстрые прогоны (для разработки)
                production — полная сетка, тяжелые прогоны (ночные / пакетные)
        """
        self.mode = mode

    def run_mission(self, mission_config: dict[str, Any]) -> dict[str, Any]:
        """
        Entry point called by TERAG.

        Args:
            mission_config: Dictionary with:
                - id: mission identifier
                - mission_type: one of:
                    - "rs09_processivity_phase"
                    - "rs10_bookmarking_threshold"
                    - "rs11_multichannel_memory"
                    - "real_hic_benchmark"
                - parameters: dictionary with experiment-specific parameters

        Returns:
            Dictionary with:
                - status: "success" | "error"
                - mission_id: mission identifier
                - mission_type: mission type
                - mode: execution mode
                - execution_time_sec: execution time
                - data: experiment results (if success)
                - error: error message (if error)
        """
        mission_type = mission_config.get("mission_type")
        params = mission_config.get("parameters", {}) or {}

        # Inject mode into parameters (TERAG may not know details)
        params.setdefault("mode", self.mode)

        t0 = time.time()

        try:
            if mission_type == "rs09_processivity_phase":
                data = run_rs09_summary(params)
            elif mission_type == "rs10_bookmarking_threshold":
                data = run_rs10_summary(params)
            elif mission_type == "rs11_multichannel_memory":
                data = run_rs11_summary(params)
            elif mission_type == "real_hic_benchmark":
                data = run_real_benchmark_summary(params)
            elif mission_type == "rs12_scihic_validation":
                # RS-12: Sci-Hi-C validation
                from experiments.run_RS12_sci_hic_benchmark import RS12SciHiCBenchmark
                benchmark = RS12SciHiCBenchmark()
                data = benchmark.run_benchmark()
            elif mission_type == "rs13_multi_condition":
                # RS-13: Multi-condition benchmark
                from experiments.run_RS11_multi_condition import RS11MultiConditionBenchmark
                benchmark = RS11MultiConditionBenchmark()
                datasets = params.get("datasets", [])
                data = benchmark.run_multi_condition_benchmark(conditions_config=datasets)
            else:
                raise ValueError(f"Unknown mission_type: {mission_type}")

            elapsed = round(time.time() - t0, 2)

            # Export phase maps for 3D visualization if applicable
            phase_map = None
            if mission_type in ["rs09_processivity_phase", "rs10_bookmarking_threshold", "rs11_multichannel_memory"]:
                try:
                    from src.archcode_core.visual.export_phase_maps import (
                        export_rs09_phase_map,
                        export_rs10_threshold_curve,
                        export_rs11_memory_surface,
                    )

                    if mission_type == "rs09_processivity_phase":
                        phase_map = export_rs09_phase_map(data)
                    elif mission_type == "rs10_bookmarking_threshold":
                        phase_map = export_rs10_threshold_curve(data)
                    elif mission_type == "rs11_multichannel_memory":
                        phase_map = export_rs11_memory_surface(data)
                except Exception:
                    # If export fails, continue without phase_map
                    pass

            result = {
                "status": "success",
                "mission_id": mission_config.get("id"),
                "mission_type": mission_type,
                "mode": self.mode,
                "execution_time_sec": elapsed,
                "data": data,
            }

            if phase_map:
                result["phase_map"] = phase_map

            return result

        except Exception as e:
            elapsed = round(time.time() - t0, 2)
            return {
                "status": "error",
                "mission_id": mission_config.get("id"),
                "mission_type": mission_type,
                "mode": self.mode,
                "execution_time_sec": elapsed,
                "error": str(e),
            }

