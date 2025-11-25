"""
Regression tests for TERAG missions.

Tests that TERAG missions run successfully, adapter works,
and data format is not broken.
"""

import json
import yaml
from pathlib import Path

import pytest

from src.integration.archcode_adapter import ArchcodeAdapter


def load_mission(mission_path: str | Path) -> dict:
    """Load mission configuration from YAML file."""
    mission_path = Path(mission_path)
    with open(mission_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestTeragMissionsRegression:
    """Regression tests for TERAG missions."""

    def test_rs09_phase_mission(self):
        """Test RS-09 processivity phase mission."""
        mission_path = Path("terag_missions/rs09_processivity_phase.yaml")
        if not mission_path.exists():
            pytest.skip(f"Mission file not found: {mission_path}")

        mission = load_mission(mission_path)
        adapter = ArchcodeAdapter(mode="fast")

        # Prepare mission config
        mission_config = {
            "id": mission.get("mission", {}).get("id", "RS09-TEST"),
            "mission_type": mission.get("parameters", {}).get("mission_type"),
            "parameters": mission.get("parameters", {}),
        }

        result = adapter.run_mission(mission_config)

        # Check status
        assert result["status"] == "success", f"Mission failed: {result.get('error')}"

        # Check data structure
        data = result.get("data", {})
        assert "phase_diagram" in data, "phase_diagram missing"
        assert "critical_points" in data, "critical_points missing"
        assert "stability_metrics" in data, "stability_metrics missing"

        # Check phase_diagram structure
        phase_diagram = data["phase_diagram"]
        assert isinstance(phase_diagram, dict), "phase_diagram should be dict"
        assert len(phase_diagram) > 0, "phase_diagram should not be empty"

        # Check for NaN/None in critical values
        for proc_str, phase_data in phase_diagram.items():
            assert isinstance(phase_data, dict), f"Phase data should be dict for {proc_str}"
            assert "phase" in phase_data, f"Phase label missing for {proc_str}"
            assert "stability" in phase_data, f"Stability missing for {proc_str}"
            assert phase_data["stability"] is not None, f"Stability is None for {proc_str}"
            assert not (
                isinstance(phase_data["stability"], float) and phase_data["stability"] != phase_data["stability"]
            ), f"Stability is NaN for {proc_str}"

        # Check phase_map if present
        if "phase_map" in result:
            phase_map = result["phase_map"]
            assert "nodes" in phase_map, "phase_map.nodes missing"
            assert "values" in phase_map, "phase_map.values missing"
            assert len(phase_map["nodes"]) > 0, "phase_map.nodes should not be empty"

        # Check JSON serializability
        json_str = json.dumps(result)
        assert len(json_str) > 0, "Result should be JSON-serializable"

    def test_rs11_memory_mission(self):
        """Test RS-11 multichannel memory mission."""
        mission_path = Path("terag_missions/rs11_multichannel_memory.yaml")
        if not mission_path.exists():
            pytest.skip(f"Mission file not found: {mission_path}")

        mission = load_mission(mission_path)
        adapter = ArchcodeAdapter(mode="fast")

        # Prepare mission config
        mission_config = {
            "id": mission.get("mission", {}).get("id", "RS11-TEST"),
            "mission_type": mission.get("parameters", {}).get("mission_type"),
            "parameters": mission.get("parameters", {}),
        }

        result = adapter.run_mission(mission_config)

        # Check status
        assert result["status"] == "success", f"Mission failed: {result.get('error')}"

        # Check data structure
        data = result.get("data", {})
        assert "memory_matrix" in data, "memory_matrix missing"
        assert "bookmarking_values" in data, "bookmarking_values missing"
        assert "epigenetic_values" in data, "epigenetic_values missing"
        assert "phase_regimes" in data, "phase_regimes missing"

        # Check memory_matrix structure
        memory_matrix = data["memory_matrix"]
        assert isinstance(memory_matrix, list), "memory_matrix should be list"
        assert len(memory_matrix) > 0, "memory_matrix should not be empty"

        # Check for NaN/None in matrix
        for i, row in enumerate(memory_matrix):
            assert isinstance(row, list), f"Row {i} should be list"
            for j, val in enumerate(row):
                assert val is not None, f"Value at [{i}][{j}] is None"
                assert not (isinstance(val, float) and val != val), f"Value at [{i}][{j}] is NaN"
                assert isinstance(val, (int, float)), f"Value at [{i}][{j}] should be number"

        # Check phase_map if present
        if "phase_map" in result:
            phase_map = result["phase_map"]
            assert "nodes" in phase_map, "phase_map.nodes missing"
            assert "mesh" in phase_map, "phase_map.mesh missing"
            assert len(phase_map["nodes"]) > 0, "phase_map.nodes should not be empty"

            # Check mesh structure
            mesh = phase_map["mesh"]
            assert "vertices" in mesh, "mesh.vertices missing"
            assert "faces" in mesh, "mesh.faces missing"

        # Check JSON serializability
        json_str = json.dumps(result)
        assert len(json_str) > 0, "Result should be JSON-serializable"

    def test_rs10_bookmarking_mission(self):
        """Test RS-10 bookmarking threshold mission."""
        mission_path = Path("terag_missions/rs10_bookmarking_threshold.yaml")
        if not mission_path.exists():
            pytest.skip(f"Mission file not found: {mission_path}")

        mission = load_mission(mission_path)
        adapter = ArchcodeAdapter(mode="fast")

        # Prepare mission config
        mission_config = {
            "id": mission.get("mission", {}).get("id", "RS10-TEST"),
            "mission_type": mission.get("parameters", {}).get("mission_type"),
            "parameters": mission.get("parameters", {}),
        }

        result = adapter.run_mission(mission_config)

        # Check status
        assert result["status"] == "success", f"Mission failed: {result.get('error')}"

        # Check data structure
        data = result.get("data", {})
        assert "bookmarking_grid" in data, "bookmarking_grid missing"
        assert "estimated_threshold" in data, "estimated_threshold missing"

        # Check bookmarking_grid structure
        bookmarking_grid = data["bookmarking_grid"]
        assert isinstance(bookmarking_grid, dict), "bookmarking_grid should be dict"
        assert len(bookmarking_grid) > 0, "bookmarking_grid should not be empty"

        # Check for NaN/None
        for frac_str, metrics in bookmarking_grid.items():
            assert isinstance(metrics, dict), f"Metrics should be dict for {frac_str}"
            assert "final_jaccard" in metrics, f"final_jaccard missing for {frac_str}"
            jaccard = metrics["final_jaccard"]
            assert jaccard is not None, f"jaccard is None for {frac_str}"
            assert not (isinstance(jaccard, float) and jaccard != jaccard), f"jaccard is NaN for {frac_str}"

        # Check JSON serializability
        json_str = json.dumps(result)
        assert len(json_str) > 0, "Result should be JSON-serializable"

    def test_all_missions_json_serializable(self):
        """Test that all mission results are JSON-serializable."""
        mission_files = [
            "terag_missions/rs09_processivity_phase.yaml",
            "terag_missions/rs10_bookmarking_threshold.yaml",
            "terag_missions/rs11_multichannel_memory.yaml",
        ]

        adapter = ArchcodeAdapter(mode="fast")

        for mission_file in mission_files:
            mission_path = Path(mission_file)
            if not mission_path.exists():
                continue

            mission = load_mission(mission_path)
            mission_config = {
                "id": mission.get("mission", {}).get("id", "TEST"),
                "mission_type": mission.get("parameters", {}).get("mission_type"),
                "parameters": mission.get("parameters", {}),
            }

            result = adapter.run_mission(mission_config)

            # Try to serialize
            try:
                json_str = json.dumps(result, default=str)
                assert len(json_str) > 0, f"Result for {mission_file} should be JSON-serializable"
            except Exception as e:
                pytest.fail(f"Failed to serialize result for {mission_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


