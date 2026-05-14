"""
Validation Theater Detector — Core Engine

Combines synthetic markers + metric patterns to detect validation theater.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .patterns import synthetic_markers
from .patterns import metric_patterns


@dataclass
class DetectionResult:
    """Result of validation theater detection."""

    file_path: str
    verdict: str  # "CLEAN" | "SUSPICIOUS" | "THEATER" | "HIGH_RISK"
    confidence: float  # 0.0-1.0
    risk_score: float  # 0-100
    synthetic_findings: Dict = field(default_factory=dict)
    metric_findings: Dict = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    summary: str = ""

    def __str__(self) -> str:
        return f"{self.verdict} (conf={self.confidence:.2f}, risk={self.risk_score:.0f}/100)"


class ValidationTheaterDetector:
    """
    Main detector class.

    Scans code/notebooks/logs for validation theater patterns:
    - Synthetic data markers
    - Suspiciously perfect metrics
    - Circular logic indicators
    """

    def __init__(
        self,
        min_confidence: float = 0.5,
        strict_mode: bool = False,
    ):
        """
        Initialize detector.

        Parameters:
        -----------
        min_confidence : float
            Minimum confidence threshold for reporting findings (0.0-1.0)
        strict_mode : bool
            If True, lower thresholds for THEATER verdict (more sensitive)
        """
        self.min_confidence = min_confidence
        self.strict_mode = strict_mode

        # Verdict thresholds
        if strict_mode:
            self.theater_threshold = 60  # risk score
            self.suspicious_threshold = 30
        else:
            self.theater_threshold = 70
            self.suspicious_threshold = 40

    def check_file(self, file_path: str) -> DetectionResult:
        """
        Check a single file for validation theater.

        Parameters:
        -----------
        file_path : str
            Path to file (Python, Jupyter notebook, log, etc.)

        Returns:
        --------
        DetectionResult
        """
        file_path = Path(file_path)

        if not file_path.exists():
            return DetectionResult(
                file_path=str(file_path),
                verdict="ERROR",
                confidence=0.0,
                risk_score=0,
                warnings=[f"File not found: {file_path}"],
            )

        # Read file
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return DetectionResult(
                file_path=str(file_path),
                verdict="ERROR",
                confidence=0.0,
                risk_score=0,
                warnings=[f"Failed to read file: {e}"],
            )

        # Scan patterns
        synthetic_findings = synthetic_markers.scan_code(content)
        metric_findings = metric_patterns.scan_metrics(content)

        # Calculate risk score
        risk_score, confidence, warnings = self._calculate_risk(
            synthetic_findings, metric_findings, file_path.name
        )

        # Determine verdict
        verdict = self._determine_verdict(risk_score)

        # Generate summary
        summary = self._generate_summary(verdict, risk_score, synthetic_findings, metric_findings)

        return DetectionResult(
            file_path=str(file_path),
            verdict=verdict,
            confidence=confidence,
            risk_score=risk_score,
            synthetic_findings=synthetic_findings,
            metric_findings=metric_findings,
            warnings=warnings,
            summary=summary,
        )

    def check_directory(
        self, dir_path: str, recursive: bool = True, file_patterns: List[str] = None
    ) -> List[DetectionResult]:
        """
        Check all files in a directory.

        Parameters:
        -----------
        dir_path : str
            Path to directory
        recursive : bool
            If True, scan subdirectories
        file_patterns : List[str]
            Glob patterns for files to scan (default: ["*.py", "*.ipynb", "*.txt"])

        Returns:
        --------
        List[DetectionResult]
        """
        if file_patterns is None:
            file_patterns = ["*.py", "*.ipynb", "*.txt", "*.log"]

        dir_path = Path(dir_path)
        results = []

        for pattern in file_patterns:
            if recursive:
                files = dir_path.rglob(pattern)
            else:
                files = dir_path.glob(pattern)

            for file in files:
                result = self.check_file(str(file))
                results.append(result)

        return results

    def _calculate_risk(
        self, synthetic_findings: Dict, metric_findings: Dict, filename: str
    ) -> Tuple[float, float, List[str]]:
        """
        Calculate risk score and confidence.

        Returns:
        --------
        (risk_score, confidence, warnings)
        """
        risk_score = 0.0
        warnings = []
        evidence_count = 0

        # Synthetic markers contribution
        for pattern_name, info in synthetic_findings.items():
            pattern_confidence = info["confidence"]
            pattern_severity = info["severity"]

            # Skip low-confidence findings
            if pattern_confidence < self.min_confidence:
                continue

            # Weight by severity
            severity_weight = {"HIGH": 20, "MEDIUM": 10, "LOW": 5}

            weight = severity_weight.get(pattern_severity, 5)
            risk_score += weight * pattern_confidence
            evidence_count += 1

        # Metric patterns contribution
        for pattern_name, info in metric_findings.items():
            pattern_severity = info["severity"]
            matches = info["matches"]

            # Average confidence across matches
            avg_confidence = sum(m[2] for m in matches) / len(matches)

            # Skip low-confidence
            if avg_confidence < self.min_confidence:
                continue

            # Weight by severity
            severity_weight = {"HIGH": 25, "MEDIUM": 12, "LOW": 6}

            weight = severity_weight.get(pattern_severity, 6)
            risk_score += weight * avg_confidence
            evidence_count += 1

        # Cap risk score at 100
        risk_score = min(100, risk_score)

        # Confidence = how many pieces of evidence
        if evidence_count == 0:
            confidence = 0.0
        elif evidence_count == 1:
            confidence = 0.5
        elif evidence_count == 2:
            confidence = 0.7
        elif evidence_count >= 3:
            confidence = min(1.0, 0.7 + (evidence_count - 3) * 0.1)

        # Warnings
        if risk_score > 80:
            warnings.append("⚠️ HIGH RISK: Multiple high-confidence theater patterns detected")
        elif risk_score > 50:
            warnings.append("⚠️ MODERATE RISK: Synthetic patterns + perfect metrics combination")

        # Filename check (bonus risk)
        filename_lower = filename.lower()
        if any(word in filename_lower for word in ["mock", "synthetic", "fake", "dummy"]):
            warnings.append(f"⚠️ Filename contains synthetic indicator: {filename}")
            risk_score = min(100, risk_score + 10)

        return risk_score, confidence, warnings

    def _determine_verdict(self, risk_score: float) -> str:
        """
        Determine verdict based on risk score.

        Returns:
        --------
        "CLEAN" | "SUSPICIOUS" | "THEATER" | "HIGH_RISK"
        """
        if risk_score >= 85:
            return "HIGH_RISK"
        elif risk_score >= self.theater_threshold:
            return "THEATER"
        elif risk_score >= self.suspicious_threshold:
            return "SUSPICIOUS"
        else:
            return "CLEAN"

    def _generate_summary(
        self, verdict: str, risk_score: float, synthetic_findings: Dict, metric_findings: Dict
    ) -> str:
        """Generate human-readable summary."""

        n_synthetic = len(synthetic_findings)
        n_metrics = len(metric_findings)

        if verdict == "CLEAN":
            return f"✅ No significant validation theater patterns detected (risk={risk_score:.0f}/100)"

        summary = f"{verdict} (risk={risk_score:.0f}/100)\n\n"

        if n_synthetic > 0:
            summary += f"Synthetic markers found: {n_synthetic}\n"
            high_conf = [
                name for name, info in synthetic_findings.items() if info["confidence"] > 0.7
            ]
            if high_conf:
                summary += f"  High-confidence: {', '.join(high_conf[:3])}\n"

        if n_metrics > 0:
            summary += f"Suspicious metrics found: {n_metrics}\n"
            high_sev = [
                name for name, info in metric_findings.items() if info["severity"] == "HIGH"
            ]
            if high_sev:
                summary += f"  High-severity: {', '.join(high_sev[:3])}\n"

        if verdict == "THEATER":
            summary += "\n⚠️ VALIDATION THEATER DETECTED\n"
            summary += "Evidence suggests synthetic data marked as validated.\n"
            summary += "Recommendation: Re-validate with real-world data + external sources.\n"

        elif verdict == "HIGH_RISK":
            summary += "\n🚨 HIGH RISK: STRONG VALIDATION THEATER INDICATORS\n"
            summary += "Multiple high-confidence patterns detected.\n"
            summary += "Action: Block submission until validated with real data.\n"

        return summary


# Convenience functions
def check_file(file_path: str, **kwargs) -> DetectionResult:
    """
    Quick check of a single file.

    Parameters:
    -----------
    file_path : str
        Path to file
    **kwargs :
        Additional parameters for ValidationTheaterDetector

    Returns:
    --------
    DetectionResult
    """
    detector = ValidationTheaterDetector(**kwargs)
    return detector.check_file(file_path)


def check_directory(dir_path: str, **kwargs) -> List[DetectionResult]:
    """
    Quick check of a directory.

    Parameters:
    -----------
    dir_path : str
        Path to directory
    **kwargs :
        Additional parameters for ValidationTheaterDetector

    Returns:
    --------
    List[DetectionResult]
    """
    detector = ValidationTheaterDetector(**kwargs)
    return detector.check_directory(dir_path, **kwargs)


# Example usage
if __name__ == "__main__":
    # Create test file
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
    test_file = "test_validation_theater_example.py"
    with open(test_file, "w") as f:
        f.write(test_code)

    print("Validation Theater Detector — Demo\n")
    print("=" * 70)

    # Check file
    detector = ValidationTheaterDetector(min_confidence=0.5, strict_mode=False)
    result = detector.check_file(test_file)

    print(f"File: {result.file_path}")
    print(f"Verdict: {result.verdict}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Risk Score: {result.risk_score:.0f}/100")
    print(f"\n{result.summary}")

    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  {warning}")

    print("\n" + "=" * 70)

    # Cleanup
    os.remove(test_file)

    print("\n✅ Demo complete!")
