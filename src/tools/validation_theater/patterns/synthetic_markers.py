"""
Synthetic Data Markers — Detection Rules

Patterns that indicate synthetic/mock data in validation code.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SyntheticPattern:
    """Pattern for detecting synthetic data markers."""

    name: str
    pattern: str  # Regex pattern
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    description: str
    confidence: float  # 0.0-1.0

    def match(self, code: str) -> List[Tuple[int, str]]:
        """
        Find matches in code.

        Returns:
            List of (line_number, matched_text)
        """
        matches = []
        lines = code.split("\n")

        for idx, line in enumerate(lines, start=1):
            if re.search(self.pattern, line, re.IGNORECASE):
                matches.append((idx, line.strip()))

        return matches


# File-level synthetic markers (e.g., MOCK_data.csv, synthetic_test.py)
FILE_PATTERNS = [
    SyntheticPattern(
        name="mock_prefix",
        pattern=r"^(mock|fake|dummy|test)_.*\.(py|csv|json|txt)$",
        severity="MEDIUM",
        description="Filename starts with mock/fake/dummy/test",
        confidence=0.6,
    ),
    SyntheticPattern(
        name="synthetic_suffix",
        pattern=r".*_(mock|synthetic|fake|dummy|test)\.(py|csv|json|txt)$",
        severity="MEDIUM",
        description="Filename ends with _mock/_synthetic/_fake/_dummy/_test",
        confidence=0.6,
    ),
]


# Code-level synthetic markers (e.g., np.random.seed, create_synthetic_dataset)
CODE_PATTERNS = [
    # Random generators
    SyntheticPattern(
        name="numpy_random_seed",
        pattern=r"np\.random\.seed\s*\(",
        severity="HIGH",
        description="np.random.seed() — deterministic synthetic data",
        confidence=0.9,
    ),
    SyntheticPattern(
        name="random_seed",
        pattern=r"random\.seed\s*\(",
        severity="HIGH",
        description="random.seed() — deterministic synthetic data",
        confidence=0.9,
    ),
    SyntheticPattern(
        name="random_normal",
        pattern=r"(np\.random\.|random\.)(normal|uniform|randint|choice)\s*\(",
        severity="MEDIUM",
        description="Random data generation (normal/uniform/randint/choice)",
        confidence=0.7,
    ),
    # Mock/synthetic functions
    SyntheticPattern(
        name="mock_function",
        pattern=r"def\s+(mock|fake|dummy|synthetic)_\w+",
        severity="HIGH",
        description="Function defined with mock_/fake_/dummy_/synthetic_ prefix",
        confidence=0.85,
    ),
    SyntheticPattern(
        name="create_synthetic",
        pattern=r"create_(synthetic|mock|fake|dummy)_\w+",
        severity="HIGH",
        description="Function call: create_synthetic_*/create_mock_*",
        confidence=0.9,
    ),
    # Embedded test data (inline arrays/dicts)
    SyntheticPattern(
        name="inline_test_array",
        pattern=r"(test_data|examples|test_cases)\s*=\s*\[",
        severity="MEDIUM",
        description="Inline test data array (test_data = [...])",
        confidence=0.6,
    ),
    SyntheticPattern(
        name="inline_test_dict",
        pattern=r"(test_data|examples|test_cases)\s*=\s*\{",
        severity="MEDIUM",
        description="Inline test data dict (test_data = {...})",
        confidence=0.6,
    ),
    # Mock libraries
    SyntheticPattern(
        name="unittest_mock",
        pattern=r"from\s+unittest\.mock\s+import|import\s+unittest\.mock",
        severity="LOW",
        description="unittest.mock import (legitimate use for unit tests)",
        confidence=0.3,
    ),
    SyntheticPattern(
        name="pytest_mock",
        pattern=r"from\s+pytest_mock\s+import|import\s+pytest_mock",
        severity="LOW",
        description="pytest-mock import (legitimate use for unit tests)",
        confidence=0.3,
    ),
    # Hardcoded "answers" in validation
    SyntheticPattern(
        name="expected_result",
        pattern=r"expected_result\s*=\s*.+\n.*assert.*==.*expected",
        severity="HIGH",
        description="expected_result = X; assert Y == expected (circular logic)",
        confidence=0.8,
    ),
]


# Comment markers (e.g., # SYNTHETIC, # TODO: replace with real data)
COMMENT_PATTERNS = [
    SyntheticPattern(
        name="synthetic_comment",
        pattern=r"#.*\b(synthetic|mock|fake|dummy|placeholder)\b",
        severity="LOW",
        description="Comment mentions synthetic/mock/fake/dummy/placeholder",
        confidence=0.4,
    ),
    SyntheticPattern(
        name="todo_replace",
        pattern=r"#.*TODO.*\b(replace|use real|get actual)\b",
        severity="MEDIUM",
        description="TODO comment: 'replace with real data' or 'use real'",
        confidence=0.6,
    ),
]


# String patterns (e.g., "data_type": "synthetic")
STRING_PATTERNS = [
    SyntheticPattern(
        name="synthetic_label",
        pattern=r'["\']data_type["\']\s*:\s*["\']synthetic["\']',
        severity="HIGH",
        description='"data_type": "synthetic" in JSON/dict',
        confidence=0.95,
    ),
    SyntheticPattern(
        name="mock_label",
        pattern=r'["\']mode["\']\s*:\s*["\']mock["\']',
        severity="HIGH",
        description='"mode": "mock" in config',
        confidence=0.9,
    ),
]


def get_all_patterns() -> Dict[str, List[SyntheticPattern]]:
    """
    Get all detection patterns grouped by category.

    Returns:
        Dict with keys: "file", "code", "comment", "string"
    """
    return {
        "file": FILE_PATTERNS,
        "code": CODE_PATTERNS,
        "comment": COMMENT_PATTERNS,
        "string": STRING_PATTERNS,
    }


def scan_code(code: str, categories: List[str] = None) -> Dict[str, List[Tuple[int, str]]]:
    """
    Scan code for synthetic markers.

    Parameters:
    -----------
    code : str
        Source code to scan
    categories : List[str], optional
        Which categories to scan ("code", "comment", "string").
        If None, scans all categories.

    Returns:
    --------
    Dict[str, List[Tuple[int, str]]]
        {pattern_name: [(line_number, matched_text), ...]}
    """
    if categories is None:
        categories = ["code", "comment", "string"]

    all_patterns = get_all_patterns()
    results = {}

    for category in categories:
        if category not in all_patterns:
            continue

        for pattern in all_patterns[category]:
            matches = pattern.match(code)
            if matches:
                results[pattern.name] = {
                    "matches": matches,
                    "severity": pattern.severity,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                }

    return results


# Example usage
if __name__ == "__main__":
    test_code = """
import numpy as np
import pandas as pd

# Validation test with synthetic data
np.random.seed(42)

def create_synthetic_dataset(n=100):
    '''Generate fake data for testing'''
    return np.random.normal(0, 1, n)

# TODO: replace with real data from API
test_data = [
    ("example 1", "positive"),
    ("example 2", "negative"),
]

config = {"data_type": "synthetic", "mode": "mock"}

# Run validation
data = create_synthetic_dataset()
expected_result = 0.95
result = calculate_metric(data)
assert result == expected_result  # Circular logic!
    """

    print("Synthetic Marker Detection Demo\n")
    print("=" * 70)

    results = scan_code(test_code)

    if not results:
        print("✅ No synthetic markers detected")
    else:
        print(f"⚠️  Found {len(results)} synthetic patterns:\n")

        for pattern_name, info in results.items():
            print(f"Pattern: {pattern_name}")
            print(f"  Severity: {info['severity']}")
            print(f"  Confidence: {info['confidence']:.2f}")
            print(f"  Description: {info['description']}")
            print(f"  Matches:")
            for line_num, text in info["matches"]:
                print(f"    Line {line_num}: {text}")
            print()

    print("=" * 70)
