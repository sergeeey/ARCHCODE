"""
Metric Patterns — Detection of Suspiciously Perfect Metrics

Round perfect numbers (F1=1.000, 100%) often indicate synthetic data
or circular logic in validation.
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class MetricPattern:
    """Pattern for detecting suspicious metrics."""

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
                matched_value = match_obj.group(1) if match_obj.groups() else match_obj.group(0)

                # Adjust confidence based on context
                confidence = self._adjust_confidence(line, matched_value)

                matches.append((idx, line.strip(), confidence))

        return matches

    def _adjust_confidence(self, line: str, value: str) -> float:
        """
        Adjust confidence based on context clues.

        Examples:
        - If line contains "synthetic" or "mock" → HIGHER confidence (real claim on synthetic)
        - If line contains "test" or "demo" → LOWER confidence (legitimate test)
        """
        confidence = self.confidence_base

        # Boost confidence if claiming REAL validation
        if any(
            word in line.lower() for word in ["verified", "validated", "real data", "production"]
        ):
            confidence = min(1.0, confidence + 0.2)

        # Reduce confidence if clearly a test/demo
        if any(word in line.lower() for word in ["test", "demo", "example", "mock", "synthetic"]):
            confidence = max(0.1, confidence - 0.2)

        return confidence


# Perfect decimal metrics (F1=1.000, precision=1.0)
PERFECT_METRICS = [
    MetricPattern(
        name="f1_perfect",
        pattern=r"\bf1[_\s]*(?:score)?[_\s]*[=:]\s*(1\.0+|1\.000+)\b",
        severity="HIGH",
        description="F1 score = 1.000 (suspiciously perfect)",
        confidence_base=0.85,
    ),
    MetricPattern(
        name="precision_perfect",
        pattern=r"\bprecision[_\s]*[=:]\s*(1\.0+|1\.000+)\b",
        severity="HIGH",
        description="Precision = 1.0 (suspiciously perfect)",
        confidence_base=0.85,
    ),
    MetricPattern(
        name="recall_perfect",
        pattern=r"\brecall[_\s]*[=:]\s*(1\.0+|1\.000+)\b",
        severity="HIGH",
        description="Recall = 1.0 (suspiciously perfect)",
        confidence_base=0.85,
    ),
    MetricPattern(
        name="accuracy_perfect",
        pattern=r"\baccuracy[_\s]*[=:]\s*(1\.0+|1\.000+|100(?:\.0+)?%)\b",
        severity="HIGH",
        description="Accuracy = 1.0 or 100% (suspiciously perfect)",
        confidence_base=0.8,
    ),
    MetricPattern(
        name="auc_perfect",
        pattern=r"\b(?:auc|roc[_\s]*auc|auroc)[_\s]*[=:]\s*(1\.0+|1\.000+)\b",
        severity="HIGH",
        description="AUC/AUROC = 1.0 (suspiciously perfect)",
        confidence_base=0.85,
    ),
]


# Round percentage success (100%, all X passed)
ROUND_SUCCESS = [
    MetricPattern(
        name="hundred_percent",
        pattern=r"\b(100(?:\.0+)?%|100\s+percent)\b.*\b(success|pass|correct|accurate)\b",
        severity="HIGH",
        description="100% success rate (suspiciously perfect)",
        confidence_base=0.75,
    ),
    MetricPattern(
        name="all_passed",
        pattern=r"\ball\s+(?:\d+\s+)?(?:tests?|cases?|scenarios?)\s+(?:passed|succeeded|correct)\b",
        severity="MEDIUM",
        description='"All tests passed" (no failures = suspicious)',
        confidence_base=0.6,
    ),
    MetricPattern(
        name="zero_failures",
        pattern=r"\b(?:zero|0)\s+(?:failures?|errors?|false\s+positives?)\b",
        severity="MEDIUM",
        description="Zero failures/errors (no edge cases found = suspicious)",
        confidence_base=0.6,
    ),
]


# Round correlation coefficients (R²=0.99, ρ=1.0)
ROUND_CORRELATION = [
    MetricPattern(
        name="r_squared_perfect",
        pattern=r"\b(?:r[²2]|r[_\s]*squared|r[_\s]*2)[_\s]*[=:]\s*(0\.99+|1\.0+)\b",
        severity="HIGH",
        description="R² = 0.99 or 1.0 (suspiciously perfect fit)",
        confidence_base=0.8,
    ),
    MetricPattern(
        name="correlation_perfect",
        pattern=r"\b(?:corr(?:elation)?|ρ|rho|pearson|spearman)[_\s]*[=:]\s*(1\.0+|0\.99+)\b",
        severity="MEDIUM",
        description="Correlation ≥ 0.99 (suspiciously high)",
        confidence_base=0.7,
    ),
]


# Trailing zeros (metrics ending in .000 or .00)
TRAILING_ZEROS = [
    MetricPattern(
        name="trailing_three_zeros",
        pattern=r"\b(?:f1|precision|recall|accuracy|auc|mse|rmse)[_\s]*[=:]\s*(\d+\.\d\d\d0+)\b",
        severity="MEDIUM",
        description="Metric ends in .000+ (suspiciously round)",
        confidence_base=0.6,
    ),
]


# Success claims without numbers (but suspicious phrasing)
SUCCESS_CLAIMS = [
    MetricPattern(
        name="perfect_success",
        pattern=r"\bperfect\s+(?:success|accuracy|precision|recall|classification)\b",
        severity="MEDIUM",
        description='"Perfect success/accuracy/precision" claim',
        confidence_base=0.65,
    ),
    MetricPattern(
        name="flawless_claim",
        pattern=r"\b(?:flawless|flawlessly|without\s+any\s+errors?)\b",
        severity="LOW",
        description='"Flawless" or "without any errors" claim',
        confidence_base=0.5,
    ),
]


def get_all_patterns() -> Dict[str, List[MetricPattern]]:
    """
    Get all metric patterns grouped by category.

    Returns:
        Dict with keys: "perfect", "round_success", "correlation", "trailing_zeros", "claims"
    """
    return {
        "perfect": PERFECT_METRICS,
        "round_success": ROUND_SUCCESS,
        "correlation": ROUND_CORRELATION,
        "trailing_zeros": TRAILING_ZEROS,
        "claims": SUCCESS_CLAIMS,
    }


def scan_metrics(text: str, categories: List[str] = None) -> Dict[str, List]:
    """
    Scan text for suspicious metrics.

    Parameters:
    -----------
    text : str
        Text to scan (code, logs, notebook, paper)
    categories : List[str], optional
        Which categories to scan. If None, scans all.

    Returns:
    --------
    Dict[str, List]
        {pattern_name: [(line_number, matched_text, confidence), ...]}
    """
    if categories is None:
        categories = ["perfect", "round_success", "correlation", "trailing_zeros", "claims"]

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
    test_text = """
# Validation Results (VERIFIED with real data)

F1 score = 1.000  # Perfect classification
Precision = 1.0
Recall = 1.0
Accuracy: 100%

All 10 test cases passed successfully.
Zero failures detected.

Correlation analysis: R² = 0.99, ρ = 1.0

The model achieved perfect success on the validation set.

# Note: These results are from synthetic data (TODO: test on real)
    """

    print("Metric Pattern Detection Demo\n")
    print("=" * 70)

    results = scan_metrics(test_text)

    if not results:
        print("✅ No suspicious metrics detected")
    else:
        print(f"⚠️  Found {len(results)} suspicious metric patterns:\n")

        for pattern_name, info in results.items():
            print(f"Pattern: {pattern_name}")
            print(f"  Severity: {info['severity']}")
            print(f"  Description: {info['description']}")
            print(f"  Matches:")
            for line_num, text, confidence in info["matches"]:
                print(f"    Line {line_num} (conf={confidence:.2f}): {text}")
            print()

    print("=" * 70)
