"""
Retrodiction Test Base Classes

Pattern borrowed from DNA2 Genomic Signal Decoder:
https://github.com/shootthesound/DNA2.git

Validates ARCHCODE tools by replicating known genomic discoveries.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from scipy import stats


@dataclass
class Assertion:
    """Single testable claim with pass/fail verdict."""

    description: str
    passed: bool
    detail: str
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None


@dataclass
class TestResult:
    """Result of a retrodiction test."""

    name: str
    passed: bool
    assertions: List[Assertion] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    error: Optional[str] = None

    def add_assertion(
        self,
        description: str,
        condition: bool,
        detail: str,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
    ):
        """Add an assertion to the test result."""
        self.assertions.append(
            Assertion(
                description=description,
                passed=condition,
                detail=detail,
                metric_name=metric_name,
                metric_value=metric_value,
            )
        )
        if metric_name and metric_value is not None:
            self.metrics[metric_name] = metric_value

    def finalize(self):
        """Compute final pass/fail verdict."""
        if self.error:
            self.passed = False
        else:
            self.passed = all(a.passed for a in self.assertions)


class RetrodictionTest:
    """
    Base class for retrodiction tests.

    A retrodiction test validates ARCHCODE analysis tools by checking
    whether they can detect known genomic patterns that have been
    previously discovered and published.

    Example:
        class RETRO_HBB_73bp_Cluster(RetrodictionTest):
            name = "RETRO-01: HBB 73bp Cluster Regulatory"
            locus = "HBB"

            def run(self) -> TestResult:
                # Fetch known regulatory variants
                # Run AlphaGenome
                # Assert: regulatory → CAGE disruption
                # Assert: coding → NULL
    """

    name: str = ""
    locus: Optional[str] = None
    expected_mechanism: Optional[str] = None

    def run(self) -> TestResult:
        """Execute the retrodiction test. Must be implemented by subclass."""
        raise NotImplementedError(f"{self.__class__.__name__}.run() not implemented")

    @staticmethod
    def mann_whitney_test(group_a: List[float], group_b: List[float]) -> float:
        """
        Mann-Whitney U test for difference between two groups.

        Returns:
            p-value (two-tailed)
        """
        if len(group_a) < 3 or len(group_b) < 3:
            return 1.0  # Not enough data

        statistic, p_value = stats.mannwhitneyu(group_a, group_b, alternative="two-sided")
        return p_value

    @staticmethod
    def spearman_correlation(x: List[float], y: List[float]) -> tuple[float, float]:
        """
        Spearman rank correlation.

        Returns:
            (rho, p-value)
        """
        if len(x) < 3 or len(y) < 3:
            return (0.0, 1.0)

        rho, p_value = stats.spearmanr(x, y)
        return (rho, p_value)

    @staticmethod
    def effect_size_cohens_d(group_a: List[float], group_b: List[float]) -> float:
        """
        Cohen's d effect size.

        Returns:
            d (standardized mean difference)
        """
        mean_a = np.mean(group_a)
        mean_b = np.mean(group_b)
        std_a = np.std(group_a, ddof=1)
        std_b = np.std(group_b, ddof=1)

        # Pooled standard deviation
        n_a = len(group_a)
        n_b = len(group_b)
        pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))

        if pooled_std == 0:
            return 0.0

        return (mean_a - mean_b) / pooled_std


def generate_report(test_results: List[TestResult], output_path: Path):
    """
    Generate markdown report from test results.

    Args:
        test_results: List of TestResult objects
        output_path: Path to write report markdown
    """
    from datetime import datetime

    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.passed)
    total_assertions = sum(len(r.assertions) for r in test_results)
    passed_assertions = sum(sum(1 for a in r.assertions if a.passed) for r in test_results)

    lines = [
        "# ARCHCODE Retrodiction Suite — Results",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Tests:** {passed_tests}/{total_tests} passed",
        f"**Assertions:** {passed_assertions}/{total_assertions} passed",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Test | Status | Assertions | Details |",
        "|------|--------|------------|---------|",
    ]

    for result in test_results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        assertions = f"{sum(1 for a in result.assertions if a.passed)}/{len(result.assertions)}"
        error_msg = f" (Error: {result.error})" if result.error else ""
        lines.append(f"| {result.name} | {status} | {assertions} | {error_msg} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Detailed Results",
            "",
        ]
    )

    for result in test_results:
        lines.append(f"### {result.name}")
        lines.append("")
        lines.append(f"**Status:** {'✅ PASS' if result.passed else '❌ FAIL'}")
        lines.append("")

        if result.error:
            lines.append(f"**Error:** {result.error}")
            lines.append("")
            continue

        if result.metrics:
            lines.append("**Metrics:**")
            for key, value in result.metrics.items():
                lines.append(
                    f"- `{key}`: {value:.6f}" if isinstance(value, float) else f"- `{key}`: {value}"
                )
            lines.append("")

        lines.append("**Assertions:**")
        for i, assertion in enumerate(result.assertions, 1):
            status = "✅" if assertion.passed else "❌"
            lines.append(f"{i}. {status} **{assertion.description}**")
            lines.append(f"   - {assertion.detail}")
            if assertion.metric_name and assertion.metric_value is not None:
                lines.append(
                    f"   - Metric: `{assertion.metric_name}` = {assertion.metric_value:.6f}"
                )
        lines.append("")
        lines.append("---")
        lines.append("")

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ Report written to {output_path}")
    print(f"   {passed_tests}/{total_tests} tests passed")
    print(f"   {passed_assertions}/{total_assertions} assertions passed")
