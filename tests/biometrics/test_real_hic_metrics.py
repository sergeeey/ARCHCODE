"""
Test bio-metrics engine for real Hi-C data analysis.

Tests all metric computation functions with mock or real data.
"""

import pytest
from pathlib import Path

from archcode_bio.analysis import (
    compute_insulation,
    call_tads,
    compute_compartments,
    compute_ps_curve,
    compute_pearson_matrix,
    compute_apa,
)


class TestBioMetricsEngine:
    """Test bio-metrics computation functions."""

    @pytest.fixture
    def sample_cooler_path(self):
        """Path to sample cooler file (if available)."""
        # Try to find a real cooler file
        test_paths = [
            "data/real_hic/WT/Rao2014_GM12878_1000kb.cool",
            "data/real/WT_GM12878.mcool",
        ]

        for path in test_paths:
            if Path(path).exists():
                return path

        pytest.skip("No cooler file found for testing")

    def test_compute_insulation(self, sample_cooler_path):
        """Test insulation score computation."""
        result = compute_insulation(sample_cooler_path, window=5)

        assert isinstance(result, dict)
        assert "insulation_scores" in result
        assert "bin_positions" in result
        assert "mean_insulation" in result
        assert isinstance(result["insulation_scores"], list)
        assert len(result["insulation_scores"]) > 0

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_call_tads(self, sample_cooler_path):
        """Test TAD calling from insulation data."""
        insulation_data = compute_insulation(sample_cooler_path, window=5)
        result = call_tads(insulation_data, threshold=0.1)

        assert isinstance(result, dict)
        assert "tad_boundaries" in result
        assert "tad_domains" in result
        assert "num_boundaries" in result
        assert isinstance(result["tad_boundaries"], list)

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_compute_compartments(self, sample_cooler_path):
        """Test compartment computation."""
        result = compute_compartments(sample_cooler_path)

        assert isinstance(result, dict)
        assert "compartment_labels" in result
        assert "pc1_scores" in result
        assert "compartment_strength" in result
        assert isinstance(result["compartment_labels"], list)
        assert len(result["compartment_labels"]) > 0

        # Check labels are A or B
        for label in result["compartment_labels"]:
            assert label in ["A", "B"]

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_compute_ps_curve(self, sample_cooler_path):
        """Test P(s) curve computation."""
        result = compute_ps_curve(sample_cooler_path, bins=20)

        assert isinstance(result, dict)
        assert "distances" in result
        assert "ps_values" in result
        assert "scaling_exponent" in result
        assert isinstance(result["distances"], list)
        assert isinstance(result["ps_values"], list)
        assert len(result["distances"]) == len(result["ps_values"])

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_compute_pearson_matrix(self, sample_cooler_path):
        """Test Pearson correlation matrix computation."""
        result = compute_pearson_matrix(sample_cooler_path)

        assert isinstance(result, dict)
        assert "correlation_matrix" in result
        assert "mean_correlation" in result
        assert isinstance(result["correlation_matrix"], list)

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_compute_apa(self, sample_cooler_path):
        """Test APA computation."""
        # Create sample loops
        loops_list = [
            {
                "chrom": "chr8",
                "start1": 127100000,
                "end1": 127200000,
                "start2": 127400000,
                "end2": 127500000,
            },
        ]

        result = compute_apa(sample_cooler_path, loops_list)

        assert isinstance(result, dict)
        assert "apa_matrix" in result
        assert "mean_peak_strength" in result
        assert "peak_detection_rate" in result
        assert "num_loops" in result

        # Check JSON serializability
        import json

        json_str = json.dumps(result)
        assert len(json_str) > 0

    def test_all_functions_json_serializable(self, sample_cooler_path):
        """Test that all functions return JSON-serializable results."""
        import json

        functions = [
            (compute_insulation, {"cool_file": sample_cooler_path, "window": 5}),
            (compute_compartments, {"cool_file": sample_cooler_path}),
            (compute_ps_curve, {"cool_file": sample_cooler_path, "bins": 20}),
            (compute_pearson_matrix, {"cool_file": sample_cooler_path}),
        ]

        for func, kwargs in functions:
            result = func(**kwargs)
            json_str = json.dumps(result)
            assert len(json_str) > 0

        # Test TAD calling separately (needs insulation data)
        insulation_data = compute_insulation(sample_cooler_path, window=5)
        tad_result = call_tads(insulation_data, threshold=0.1)
        json_str = json.dumps(tad_result)
        assert len(json_str) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




