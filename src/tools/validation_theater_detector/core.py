"""Core detection engine for validation theater patterns.

Analyzes Python code (AST + regex) to detect synthetic data marked as [VERIFIED].
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union


class Severity(Enum):
    """Finding severity levels."""

    HIGH = "HIGH"  # Block commit — synthetic data + [VERIFIED] marker
    MEDIUM = "MEDIUM"  # Warning — suspicious patterns
    LOW = "LOW"  # Info — unclear context
    INFO = "INFO"  # Informational only


@dataclass
class TheaterFinding:
    """A single validation theater detection result."""

    file: str
    line: int
    column: int
    severity: Severity
    pattern: str
    message: str
    confidence: float
    suggestion: str
    context: Optional[str] = None  # Surrounding code snippet


class TheaterDetector:
    """Main detection engine."""

    # Synthetic data markers (regex patterns)
    SYNTHETIC_PATTERNS = {
        "random_seed": r"np\.random\.seed\(",
        "mock_prefix": r"\b(mock_|MOCK_|create_synthetic_|generate_test_)",
        "synthetic_dataset": r"(synthetic|mock|fake|dummy)_?(data|dataset|examples?)",
    }

    # Perfect metric patterns
    METRIC_PATTERNS = {
        "f1_perfect": r"F1\s*[=:]\s*1\.0{3,}",
        "precision_perfect": r"precision\s*[=:]\s*1\.0+",
        "recall_perfect": r"recall\s*[=:]\s*1\.0+",
        "accuracy_100": r"(accuracy|success)\s*[=:]\s*(100\.0*%?|1\.0{3,})",
        "auc_perfect": r"AUC\s*[=:]\s*1\.0{3,}",
    }

    # Zero-failure patterns
    ZERO_FAILURE_PATTERNS = {
        "all_passed": r"all.*tests?\s+(passed|succeeded)",
        "zero_failures": r"(zero|0)\s+failures?",
        "100_percent": r"100%\s+(success|passed|correct)",
        "perfect_score": r"perfect\s+(score|result|accuracy)",
    }

    def __init__(self):
        self.findings: List[TheaterFinding] = []

    def detect_file(self, file_path: Union[str, Path]) -> List[TheaterFinding]:
        """Detect validation theater patterns in a single file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix not in {".py", ".ipynb"}:
            return []  # Skip non-Python files

        content = file_path.read_text(encoding="utf-8")

        # Reset findings for this file
        self.findings = []

        # Stage 1: Regex-based pattern detection
        self._detect_synthetic_markers(content, str(file_path))
        self._detect_perfect_metrics(content, str(file_path))
        self._detect_zero_failures(content, str(file_path))

        # Stage 2: AST-based detection (embedded test data)
        try:
            tree = ast.parse(content, filename=str(file_path))
            self._detect_embedded_test_data(tree, str(file_path), content)
        except SyntaxError:
            # Skip files with syntax errors
            pass

        # Stage 3: Calculate confidence scores and adjust severity
        self._adjust_severity_by_confidence()

        return self.findings

    def _detect_synthetic_markers(self, content: str, file_path: str):
        """Detect synthetic data code patterns via regex."""
        for pattern_name, pattern in self.SYNTHETIC_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[: match.start()].count("\n") + 1
                col = match.start() - content[: match.start()].rfind("\n") - 1

                # Extract context (surrounding line)
                lines = content.split("\n")
                context = lines[line_num - 1] if line_num <= len(lines) else ""

                self.findings.append(
                    TheaterFinding(
                        file=file_path,
                        line=line_num,
                        column=col,
                        severity=Severity.MEDIUM,  # Will adjust later
                        pattern=f"synthetic_marker_{pattern_name}",
                        message=f"Synthetic data marker detected: {match.group()}",
                        confidence=0.3,  # Base confidence
                        suggestion="If this is validation code, cite external data source or mark as [VERIFIED-SYNTHETIC]",
                        context=context.strip(),
                    )
                )

    def _detect_perfect_metrics(self, content: str, file_path: str):
        """Detect suspiciously perfect metrics (F1=1.000, 100% accuracy)."""
        for pattern_name, pattern in self.METRIC_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[: match.start()].count("\n") + 1
                col = match.start() - content[: match.start()].rfind("\n") - 1

                lines = content.split("\n")
                context = lines[line_num - 1] if line_num <= len(lines) else ""

                self.findings.append(
                    TheaterFinding(
                        file=file_path,
                        line=line_num,
                        column=col,
                        severity=Severity.HIGH,  # Perfect metrics are high priority
                        pattern=f"perfect_metric_{pattern_name}",
                        message=f"Suspiciously perfect metric: {match.group()}",
                        confidence=0.5,  # Higher confidence for perfect metrics
                        suggestion="Verify this metric on real-world data, not synthetic",
                        context=context.strip(),
                    )
                )

    def _detect_zero_failures(self, content: str, file_path: str):
        """Detect zero-failure claims (all tests passed, 100% success)."""
        for pattern_name, pattern in self.ZERO_FAILURE_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[: match.start()].count("\n") + 1
                col = match.start() - content[: match.start()].rfind("\n") - 1

                lines = content.split("\n")
                context = lines[line_num - 1] if line_num <= len(lines) else ""

                self.findings.append(
                    TheaterFinding(
                        file=file_path,
                        line=line_num,
                        column=col,
                        severity=Severity.MEDIUM,
                        pattern=f"zero_failure_{pattern_name}",
                        message=f"Zero-failure claim detected: {match.group()}",
                        confidence=0.3,
                        suggestion="Real data ALWAYS has edge cases — verify claim with external dataset",
                        context=context.strip(),
                    )
                )

    def _detect_embedded_test_data(self, tree: ast.AST, file_path: str, content: str):
        """Detect embedded test data (AST-based): inline arrays/dicts without external source."""

        class TestDataVisitor(ast.NodeVisitor):
            def __init__(self, detector: "TheaterDetector", file_path: str, content: str):
                self.detector = detector
                self.file_path = file_path
                self.content = content
                self.lines = content.split("\n")

            def visit_Assign(self, node: ast.Assign):
                """Check variable assignments for embedded test data."""
                # Look for patterns like: data = [("input", "label"), ...]
                if isinstance(node.value, (ast.List, ast.Dict)):
                    # Check if this looks like test data
                    if self._looks_like_test_data(node.value):
                        # Check if there's an external source citation nearby
                        if not self._has_external_source(node.lineno):
                            self.detector.findings.append(
                                TheaterFinding(
                                    file=self.file_path,
                                    line=node.lineno,
                                    column=node.col_offset,
                                    severity=Severity.HIGH,
                                    pattern="embedded_test_data",
                                    message="Embedded test data without external source citation",
                                    confidence=0.7,  # High confidence — clear pattern
                                    suggestion="Cite external dataset (URL, API call, file path) or mark as [VERIFIED-SYNTHETIC]",
                                    context=self.lines[node.lineno - 1].strip()
                                    if node.lineno <= len(self.lines)
                                    else "",
                                )
                            )

                self.generic_visit(node)

            def _looks_like_test_data(self, node: Union[ast.List, ast.Dict]) -> bool:
                """Heuristic: does this look like test data?"""
                if isinstance(node, ast.List):
                    # List of tuples/lists = likely test data
                    if len(node.elts) >= 3:  # At least 3 examples
                        if all(isinstance(elt, (ast.Tuple, ast.List)) for elt in node.elts[:3]):
                            return True

                    # List of dicts with "input"/"expected" keys
                    if len(node.elts) >= 2:
                        if all(isinstance(elt, ast.Dict) for elt in node.elts[:2]):
                            return True

                elif isinstance(node, ast.Dict):
                    # Dict with "input", "expected", "label" keys
                    if node.keys:
                        key_names = [
                            k.s
                            if isinstance(k, ast.Str)
                            else (k.value if isinstance(k, ast.Constant) else None)
                            for k in node.keys
                        ]
                        test_data_keywords = {"input", "expected", "label", "output", "test"}
                        if any(k in test_data_keywords for k in key_names if k):
                            return True

                return False

            def _has_external_source(self, lineno: int) -> bool:
                """Check if nearby code cites external source (API call, file read, URL)."""
                # Check ±5 lines for external source indicators
                start = max(0, lineno - 5)
                end = min(len(self.lines), lineno + 5)

                nearby_code = "\n".join(self.lines[start:end])

                # External source patterns
                external_patterns = [
                    r"requests\.get\(",
                    r"pd\.read_csv\(",
                    r"open\(['\"].*['\"],\s*['\"]r['\"]",
                    r"https?://",
                    r"api\.",
                    r"urllib",
                ]

                for pattern in external_patterns:
                    if re.search(pattern, nearby_code, re.IGNORECASE):
                        return True

                return False

        visitor = TestDataVisitor(self, file_path, content)
        visitor.visit(tree)

    def _adjust_severity_by_confidence(self):
        """Adjust severity based on confidence scores and pattern combinations."""
        # Look for multiple patterns in same file → boost confidence
        file_pattern_counts = {}

        for finding in self.findings:
            key = finding.file
            if key not in file_pattern_counts:
                file_pattern_counts[key] = []
            file_pattern_counts[key].append(finding.pattern)

        # Boost confidence if multiple patterns detected
        for finding in self.findings:
            pattern_count = len(file_pattern_counts[finding.file])

            if pattern_count >= 3:
                finding.confidence = min(1.0, finding.confidence + 0.3)
            elif pattern_count == 2:
                finding.confidence = min(1.0, finding.confidence + 0.15)

            # Adjust severity based on final confidence
            if finding.confidence >= 0.7:
                finding.severity = Severity.HIGH
            elif finding.confidence >= 0.4:
                finding.severity = Severity.MEDIUM
            else:
                finding.severity = Severity.LOW


def detect_theater(path: Union[str, Path], recursive: bool = False) -> List[TheaterFinding]:
    """
    Detect validation theater patterns in file or directory.

    Args:
        path: File or directory path to scan
        recursive: If True, scan directory recursively

    Returns:
        List of TheaterFinding objects

    Example:
        >>> findings = detect_theater("src/", recursive=True)
        >>> high_severity = [f for f in findings if f.severity == Severity.HIGH]
        >>> if high_severity:
        ...     print(f"⛔ {len(high_severity)} HIGH severity findings")
    """
    path = Path(path)
    detector = TheaterDetector()
    all_findings = []

    if path.is_file():
        all_findings = detector.detect_file(path)

    elif path.is_dir():
        pattern = "**/*.py" if recursive else "*.py"
        for py_file in path.glob(pattern):
            if py_file.is_file():
                findings = detector.detect_file(py_file)
                all_findings.extend(findings)

    else:
        raise ValueError(f"Path not found: {path}")

    return all_findings
