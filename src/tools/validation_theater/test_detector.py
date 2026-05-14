"""
Test script for ValidationTheaterDetector

Run from anywhere:
    python D:/ДНК/src/tools/validation_theater/test_detector.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.tools.validation_theater import ValidationTheaterDetector


def main():
    """Test detector on synthetic example."""

    # Create test code
    test_code = """
import numpy as np

# Validation with real data (VERIFIED)
np.random.seed(42)
data = np.random.normal(0, 1, 1000)

def create_synthetic_dataset(n=100):
    return np.random.normal(0, 1, n)

# Results
F1 score = 1.000
Precision = 1.0
Recall = 1.0
Accuracy: 100%

All 10 test cases passed.
Zero failures detected.
    """

    # Save test file
    test_file = Path("test_validation_theater_example.py")
    test_file.write_text(test_code)

    try:
        print("Validation Theater Detector — Test Run\n")
        print("=" * 70)

        # Initialize detector
        detector = ValidationTheaterDetector(min_confidence=0.5, strict_mode=False)

        # Check file
        result = detector.check_file(str(test_file))

        print(f"File: {result.file_path}")
        print(f"Verdict: {result.verdict}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Risk Score: {result.risk_score:.0f}/100")
        print(f"\n{result.summary}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"  {warning}")

        # Detailed findings
        if result.synthetic_findings:
            print("\n" + "-" * 70)
            print("SYNTHETIC MARKERS:")
            for pattern_name, info in result.synthetic_findings.items():
                print(f"\n  {pattern_name}:")
                print(f"    Severity: {info['severity']}")
                print(f"    Confidence: {info['confidence']:.2f}")
                print(f"    Matches: {len(info['matches'])}")
                for line_num, text in info["matches"][:3]:  # Show first 3
                    print(f"      Line {line_num}: {text[:60]}...")

        if result.metric_findings:
            print("\n" + "-" * 70)
            print("SUSPICIOUS METRICS:")
            for pattern_name, info in result.metric_findings.items():
                print(f"\n  {pattern_name}:")
                print(f"    Severity: {info['severity']}")
                print(f"    Matches: {len(info['matches'])}")
                for line_num, text, confidence in info["matches"][:3]:  # Show first 3
                    print(f"      Line {line_num} (conf={confidence:.2f}): {text[:60]}...")

        print("\n" + "=" * 70)
        print("\n✅ Test complete!")

        # Verify expected behavior
        assert result.verdict in [
            "SUSPICIOUS",
            "THEATER",
            "HIGH_RISK",
        ], f"Expected detection, got {result.verdict}"
        assert result.risk_score > 40, f"Expected risk > 40, got {result.risk_score}"
        assert len(result.synthetic_findings) > 0, "Expected synthetic markers"
        assert len(result.metric_findings) > 0, "Expected metric patterns"

        print("\n✅ All assertions passed!")

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    main()
