"""Smoke tests for validation theater detector core engine."""

import pytest
from pathlib import Path
import tempfile
import sys

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.tools.validation_theater_detector.core import detect_theater, Severity


def test_detect_random_seed():
    """Should detect np.random.seed() as synthetic marker."""
    code = """
import numpy as np

np.random.seed(42)
data = np.random.randn(100, 10)
F1 = 1.000  # Perfect score
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        findings = detect_theater(f.name)

        # Should detect: random seed + perfect F1
        assert len(findings) >= 2

        # At least one HIGH severity (F1=1.000)
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        assert len(high_findings) >= 1

        # Cleanup handled by tempfile on Windows (file lock issue)


def test_detect_embedded_test_data():
    """Should detect embedded test data without external source."""
    code = """
# Embedded test data (no external source cited)
test_cases = [
    ("abstract 1", "POSITIVE"),
    ("abstract 2", "NEGATIVE"),
    ("abstract 3", "POSITIVE"),
]

# Validation
for text, label in test_cases:
    result = classifier(text)
    assert result == label
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        findings = detect_theater(f.name)

        # Should detect embedded test data
        assert len(findings) >= 1

        # Should be HIGH severity
        embedded = [f for f in findings if f.pattern == "embedded_test_data"]
        assert len(embedded) >= 1
        assert embedded[0].severity == Severity.HIGH

        # Cleanup handled by tempfile on Windows (file lock issue)


def test_no_false_positive_with_external_source():
    """Should NOT flag code with external data source citation."""
    code = """
import requests

# External source cited
response = requests.get("https://api.example.com/data")
data = response.json()

# Validation on REAL data
F1 = 0.987  # Not perfect
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        findings = detect_theater(f.name)

        # Should NOT detect high severity (external source + imperfect metric)
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        assert len(high_findings) == 0

        # Cleanup handled by tempfile on Windows (file lock issue)


def test_detect_100_percent_success():
    """Should detect 100% success claims."""
    code = """
# Validation results
print("All tests passed")
print("100% success rate")
print("Zero failures detected")
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        findings = detect_theater(f.name)

        # Should detect zero-failure patterns
        assert len(findings) >= 2

        # Check for specific patterns
        patterns = [f.pattern for f in findings]
        assert any("zero_failure" in p for p in patterns)

        # Cleanup handled by tempfile on Windows (file lock issue)


def test_confidence_boost_multiple_patterns():
    """Confidence should increase when multiple patterns detected in same file."""
    code = """
import numpy as np

np.random.seed(42)
mock_data = np.random.randn(100, 10)

# Validation
F1 = 1.000
precision = 1.0
print("All tests passed")
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        findings = detect_theater(f.name)

        # Multiple patterns → confidence boost
        # Should have at least 3 findings (seed, F1, precision, all_passed)
        assert len(findings) >= 3

        # At least one finding should have boosted confidence (≥0.7)
        high_confidence = [f for f in findings if f.confidence >= 0.7]
        assert len(high_confidence) >= 1

        # Cleanup handled by tempfile on Windows (file lock issue)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
