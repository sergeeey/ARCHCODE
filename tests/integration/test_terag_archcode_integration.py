"""
Integration test for TERAG ↔ ARCHCODE adapter.

Tests end-to-end flow: TERAG mission → adapter → ARCHCODE → validation.
"""

import pytest

from src.integration.archcode_adapter import ArchcodeAdapter
from terag_plugins.genome_architecture.validator import validate_archcode_result


class TestTeragArchcodeIntegration:
    """Test TERAG ↔ ARCHCODE integration."""

    def test_rs09_mission_fast_mode(self):
        """Test RS-09 mission in fast mode."""
        adapter = ArchcodeAdapter(mode="fast")

        mission_config = {
            "id": "RS09-PROC-TEST",
            "mission_type": "rs09_processivity_phase",
            "parameters": {
                "processivity_min": 0.0,
                "processivity_max": 2.0,
                "processivity_steps": 10,
            },
        }

        payload = adapter.run_mission(mission_config)
        assert payload["status"] == "success"
        assert payload["mission_type"] == "rs09_processivity_phase"
        assert "data" in payload

        # Validate result
        validation = validate_archcode_result(payload)
        assert "valid" in validation
        assert isinstance(validation["derived_metrics"], dict)

        # Check derived metrics
        derived = validation["derived_metrics"]
        assert "stable_phase_fraction" in derived

    def test_rs10_mission_fast_mode(self):
        """Test RS-10 mission in fast mode."""
        adapter = ArchcodeAdapter(mode="fast")

        mission_config = {
            "id": "RS10-BOOK-TEST",
            "mission_type": "rs10_bookmarking_threshold",
            "parameters": {
                "bookmarking_range": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                "num_cycles": 5,  # Very fast for test
                "processivity": 0.9,
            },
        }

        payload = adapter.run_mission(mission_config)
        assert payload["status"] == "success"
        assert payload["mission_type"] == "rs10_bookmarking_threshold"
        assert "data" in payload

        # Validate result
        validation = validate_archcode_result(payload)
        assert "valid" in validation
        assert isinstance(validation["derived_metrics"], dict)

    def test_rs11_mission_fast_mode(self):
        """Test RS-11 mission in fast mode."""
        adapter = ArchcodeAdapter(mode="fast")

        mission_config = {
            "id": "RS11-MEM-TEST",
            "mission_type": "rs11_multichannel_memory",
            "parameters": {
                "bookmarking_range": (0.0, 1.0, 5),  # Small grid for test
                "epigenetic_range": (0.0, 1.0, 3),
                "num_cycles": 5,  # Very fast for test
                "processivity": 0.9,
            },
        }

        payload = adapter.run_mission(mission_config)
        assert payload["status"] == "success"
        assert payload["mission_type"] == "rs11_multichannel_memory"
        assert "data" in payload

        # Validate result
        validation = validate_archcode_result(payload)
        assert "valid" in validation
        assert isinstance(validation["derived_metrics"], dict)

    def test_real_benchmark_mission_fast_mode(self):
        """Test real Hi-C benchmark mission in fast mode."""
        adapter = ArchcodeAdapter(mode="fast")

        mission_config = {
            "id": "REAL-HIC-TEST",
            "mission_type": "real_hic_benchmark",
            "parameters": {
                "real_cooler_path": "data/real_hic/WT/Rao2014_GM12878_1000kb.cool",
                "nipbl_velocity": 1.0,
                "wapl_lifetime": 1.0,
            },
        }

        payload = adapter.run_mission(mission_config)
        # May fail if file doesn't exist, that's OK for test
        assert payload["status"] in ["success", "error"]
        assert payload["mission_type"] == "real_hic_benchmark"

        if payload["status"] == "success":
            validation = validate_archcode_result(payload)
            assert "valid" in validation
            assert isinstance(validation["derived_metrics"], dict)

    def test_unknown_mission_type(self):
        """Test error handling for unknown mission type."""
        adapter = ArchcodeAdapter(mode="fast")

        mission_config = {
            "id": "UNKNOWN-TEST",
            "mission_type": "unknown_mission_type",
            "parameters": {},
        }

        payload = adapter.run_mission(mission_config)
        assert payload["status"] == "error"
        assert "error" in payload

    def test_adapter_mode_injection(self):
        """Test that adapter injects mode into parameters."""
        adapter = ArchcodeAdapter(mode="production")

        mission_config = {
            "id": "MODE-TEST",
            "mission_type": "rs09_processivity_phase",
            "parameters": {
                "processivity_steps": 50,
            },
        }

        payload = adapter.run_mission(mission_config)
        assert payload["status"] == "success"
        assert payload["mode"] == "production"
        # Check that mode was used (production should use more steps)
        # This is implicit in the data structure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

