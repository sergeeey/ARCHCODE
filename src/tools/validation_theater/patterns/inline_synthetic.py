"""
Inline Synthetic Patterns — Detection of Embedded Test Data

Harder to detect than file-based synthetic (no function names like create_synthetic_*).
These patterns catch test data INSIDE validation code (highest theater risk).
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class InlineSyntheticPattern:
    """Pattern for detecting inline synthetic data."""

    name: str
    pattern: str  # Regex pattern
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    description: str
    confidence_base: float  # Base confidence (0.0-1.0)

    def match(self, text: str) -> List[Tuple[int, str, float]]:
        """
        Find matches in text.

        Returns:
            List of (line_number, matched_text, confidence)
        """
        matches = []
        lines = text.split("\n")

        for idx, line in enumerate(lines, start=1):
            match_obj = re.search(self.pattern, line, re.IGNORECASE)
            if match_obj:
                # Adjust confidence based on context
                confidence = self._adjust_confidence(line)
                matches.append((idx, line.strip(), confidence))

        return matches

    def _adjust_confidence(self, line: str) -> float:
        """Adjust confidence based on context clues."""
        confidence = self.confidence_base

        # Boost if claiming validation/verification
        if any(
            word in line.lower() for word in ["verified", "validated", "real data", "production"]
        ):
            confidence = min(1.0, confidence + 0.2)

        # Reduce if clearly a test
        if any(word in line.lower() for word in ["test", "demo", "example"]):
            confidence = max(0.1, confidence - 0.15)

        return confidence


# Embedded test cases (inline arrays with labels)
EMBEDDED_TEST_CASES = [
    InlineSyntheticPattern(
        name="inline_test_array_init",
        pattern=r"(abstracts|examples|test_cases|test_data|validation_set)\s*=\s*\[",
        severity="HIGH",
        description="Inline test array initialization: abstracts/examples/test_cases = [ — likely embedded test data",
        confidence_base=0.75,
    ),
    InlineSyntheticPattern(
        name="inline_labeled_tuples",
        pattern=r'(abstracts|examples|test_cases|data)\s*=\s*\[\s*\(\s*["\'].*["\']\s*,\s*["\'].*["\']\s*\)',
        severity="HIGH",
        description="Embedded test cases: [(text, label), ...] — inline synthetic validation",
        confidence_base=0.85,
    ),
    InlineSyntheticPattern(
        name="inline_dict_examples",
        pattern=r'(examples|test_data|validation_set)\s*=\s*\[\s*\{\s*["\'].*["\']\s*:\s*["\']',
        severity="HIGH",
        description="Embedded dict examples: [{'input': 'X', 'label': 'Y'}, ...] — inline synthetic",
        confidence_base=0.85,
    ),
    InlineSyntheticPattern(
        name="inline_text_array",
        pattern=r'(texts|documents|abstracts)\s*=\s*\[\s*["\'][^"\']{20,}["\']',
        severity="MEDIUM",
        description="Inline text array: texts = ['long text 1', ...] — embedded examples",
        confidence_base=0.7,
    ),
]


# Hardcoded expected results (circular logic indicator)
HARDCODED_ANSWERS = [
    InlineSyntheticPattern(
        name="expected_equals_assert",
        pattern=r"expected\s*=\s*.+\n.*assert.*==\s*expected",
        severity="HIGH",
        description="expected = X; assert result == expected — circular validation",
        confidence_base=0.9,
    ),
    InlineSyntheticPattern(
        name="answer_key_lookup",
        pattern=r"answer_key\s*=\s*\{.*\}.*\n.*assert.*answer_key\[",
        severity="HIGH",
        description="answer_key = {...}; assert X == answer_key[Y] — circular lookup",
        confidence_base=0.85,
    ),
    InlineSyntheticPattern(
        name="ground_truth_embedded",
        pattern=r"ground_truth\s*=\s*\[.*\].*\n.*(?:assert|compare).*ground_truth",
        severity="HIGH",
        description="ground_truth = [...]; compare to ground_truth — circular comparison",
        confidence_base=0.85,
    ),
]


# Heredoc / multi-line string synthetic (python -c or python <<EOF patterns)
HEREDOC_SYNTHETIC = [
    InlineSyntheticPattern(
        name="heredoc_validation",
        pattern=r"python\s+<<\s*EOF.*(?:test_data|examples|abstracts)\s*=",
        severity="HIGH",
        description="Heredoc with embedded test data: python <<EOF ... test_data = [...] — inline synthetic",
        confidence_base=0.9,
    ),
    InlineSyntheticPattern(
        name="python_c_inline",
        pattern=r'python\s+-c\s+["\'].*(?:test_data|examples)\s*=\s*\[',
        severity="HIGH",
        description="python -c with inline data: python -c 'test_data = [...]' — synthetic validation",
        confidence_base=0.9,
    ),
]


# Small dataset hardcoded (N < 20 — too small for real validation)
SMALL_DATASET_HARDCODED = [
    InlineSyntheticPattern(
        name="tiny_validation_set",
        pattern=r"(?:validation|test)_(?:data|set)\s*=\s*\[(?:[^]]{0,200})\].*\n.*(?:len|size).*[<≤]\s*20",
        severity="MEDIUM",
        description="Validation set with N < 20 — too small for robust validation",
        confidence_base=0.65,
    ),
]


# Success claims with no external data source
NO_EXTERNAL_SOURCE = [
    InlineSyntheticPattern(
        name="no_api_call",
        pattern=r"(?:F1|precision|recall|accuracy)\s*[=:]\s*(?:0\.\d{3}|1\.0)(?!.*(?:requests\.get|pd\.read_csv|load|fetch))",
        severity="MEDIUM",
        description="Perfect metric without external data source (no requests.get, pd.read_csv) — suspicious",
        confidence_base=0.6,
    ),
    InlineSyntheticPattern(
        name="no_file_load",
        pattern=r"(?:validated|verified).*(?!.*\.csv|\.json|\.txt|\.parquet|\.feather)",
        severity="LOW",
        description='"validated" claim with no file extension cited — source unclear',
        confidence_base=0.4,
    ),
]


def get_all_patterns() -> Dict[str, List[InlineSyntheticPattern]]:
    """
    Get all inline synthetic patterns grouped by category.

    Returns:
        Dict with keys: "embedded", "hardcoded", "heredoc", "small_dataset", "no_source"
    """
    return {
        "embedded": EMBEDDED_TEST_CASES,
        "hardcoded": HARDCODED_ANSWERS,
        "heredoc": HEREDOC_SYNTHETIC,
        "small_dataset": SMALL_DATASET_HARDCODED,
        "no_source": NO_EXTERNAL_SOURCE,
    }


def scan_inline_synthetic(text: str, categories: List[str] = None) -> Dict[str, Dict]:
    """
    Scan text for inline synthetic patterns (harder to detect).

    Parameters:
    -----------
    text : str
        Text to scan (code, validation script, notebook)
    categories : List[str], optional
        Which categories to scan. If None, scans all.

    Returns:
    --------
    Dict[str, Dict]
        {pattern_name: {"matches": [...], "severity": "...", "description": "..."}}
    """
    if categories is None:
        categories = ["embedded", "hardcoded", "heredoc", "small_dataset", "no_source"]

    all_patterns = get_all_patterns()
    results = {}

    for category in categories:
        if category not in all_patterns:
            continue

        for pattern in all_patterns[category]:
            matches = pattern.match(text)
            if matches:
                results[pattern.name] = {
                    "matches": matches,
                    "severity": pattern.severity,
                    "description": pattern.description,
                }

    return results


# Example usage
if __name__ == "__main__":
    # Test case: ТОП-10 theater scenario
    test_code = """
# Validation of 10 niches (H2 Legal classifier example)

abstracts = [
    ("Legal case 1 about contract dispute", "LEGAL"),
    ("Legal case 2 about intellectual property", "LEGAL"),
    ("Non-legal text about cooking recipes", "NOT_LEGAL"),
]

# Validation
for abstract, expected_label in abstracts:
    result = classifier(abstract)
    assert result == expected_label  # Circular logic!

# Results
print("✅ All 3 test cases passed")
print("Precision: 1.0, Recall: 1.0, F1: 1.000")
print("[VERIFIED] 100% SUCCESS on validated dataset")
    """

    print("Inline Synthetic Pattern Detection — Demo\n")
    print("=" * 70)

    results = scan_inline_synthetic(test_code)

    if not results:
        print("✅ No inline synthetic patterns detected")
    else:
        print(f"⚠️  Found {len(results)} inline synthetic patterns:\n")

        for pattern_name, info in results.items():
            print(f"Pattern: {pattern_name}")
            print(f"  Severity: {info['severity']}")
            print(f"  Description: {info['description']}")
            print(f"  Matches:")
            for line_num, text, confidence in info["matches"]:
                print(f"    Line {line_num} (conf={confidence:.2f}): {text[:70]}...")
            print()

    print("=" * 70)
