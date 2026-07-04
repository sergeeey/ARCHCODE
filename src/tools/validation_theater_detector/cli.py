#!/usr/bin/env python3
"""Command-line interface for Validation Theater Detector.

Usage:
    vt-detector <path> [options]

Examples:
    # Scan single file
    vt-detector validation.py

    # Scan directory recursively
    vt-detector src/ --recursive

    # Strict mode (HIGH severity only)
    vt-detector src/ --strict

    # JSON output (for CI/CD)
    vt-detector src/ --json > findings.json

    # Exit code 1 if HIGH findings (for pre-commit)
    vt-detector src/ --strict --exit-code
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.tools.validation_theater_detector.core import (
    detect_theater,
    TheaterFinding,
    Severity,
)


def format_finding_text(finding: TheaterFinding, show_context: bool = True) -> str:
    """Format finding as human-readable text."""
    severity_icons = {
        Severity.HIGH: "🔴",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🔵",
        Severity.INFO: "ℹ️",
    }

    icon = severity_icons.get(finding.severity, "•")

    lines = [
        f"{icon} {finding.severity.value} — {finding.file}:{finding.line}:{finding.column}",
        f"   Pattern: {finding.pattern}",
        f"   Message: {finding.message}",
        f"   Confidence: {finding.confidence:.2f}",
        f"   Suggestion: {finding.suggestion}",
    ]

    if show_context and finding.context:
        lines.append(f"   Context: {finding.context}")

    return "\n".join(lines)


def format_finding_json(finding: TheaterFinding) -> dict:
    """Format finding as JSON-serializable dict."""
    return {
        "file": finding.file,
        "line": finding.line,
        "column": finding.column,
        "severity": finding.severity.value,
        "pattern": finding.pattern,
        "message": finding.message,
        "confidence": round(finding.confidence, 3),
        "suggestion": finding.suggestion,
        "context": finding.context,
    }


def filter_by_severity(
    findings: List[TheaterFinding], min_severity: Severity
) -> List[TheaterFinding]:
    """Filter findings by minimum severity level."""
    severity_order = {
        Severity.LOW: 0,
        Severity.INFO: 0,
        Severity.MEDIUM: 1,
        Severity.HIGH: 2,
    }

    min_level = severity_order.get(min_severity, 0)

    return [f for f in findings if severity_order.get(f.severity, 0) >= min_level]


def group_by_severity(findings: List[TheaterFinding]) -> dict[Severity, List[TheaterFinding]]:
    """Group findings by severity level."""
    groups = {
        Severity.HIGH: [],
        Severity.MEDIUM: [],
        Severity.LOW: [],
        Severity.INFO: [],
    }

    for finding in findings:
        groups[finding.severity].append(finding)

    return groups


def print_summary(findings: List[TheaterFinding], show_context: bool = True):
    """Print findings grouped by severity."""
    if not findings:
        print("✅ No validation theater patterns detected")
        return

    groups = group_by_severity(findings)

    # Print summary header
    total = len(findings)
    high_count = len(groups[Severity.HIGH])
    medium_count = len(groups[Severity.MEDIUM])
    low_count = len(groups[Severity.LOW])

    print(f"\n{'='*70}")
    print(f"VALIDATION THEATER DETECTOR — {total} findings")
    print(f"{'='*70}\n")

    print(f"🔴 HIGH:   {high_count}")
    print(f"🟡 MEDIUM: {medium_count}")
    print(f"🔵 LOW:    {low_count}\n")

    # Print HIGH severity first (most important)
    if groups[Severity.HIGH]:
        print(f"{'='*70}")
        print("🔴 HIGH SEVERITY (validation theater detected)")
        print(f"{'='*70}\n")
        for finding in groups[Severity.HIGH]:
            print(format_finding_text(finding, show_context))
            print()

    # Then MEDIUM
    if groups[Severity.MEDIUM]:
        print(f"{'='*70}")
        print("🟡 MEDIUM SEVERITY (suspicious patterns)")
        print(f"{'='*70}\n")
        for finding in groups[Severity.MEDIUM]:
            print(format_finding_text(finding, show_context))
            print()

    # Finally LOW
    if groups[Severity.LOW]:
        print(f"{'='*70}")
        print("🔵 LOW SEVERITY (informational)")
        print(f"{'='*70}\n")
        for finding in groups[Severity.LOW]:
            print(format_finding_text(finding, show_context))
            print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Detect validation theater patterns in Python code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validation.py              # Scan single file
  %(prog)s src/ --recursive           # Scan directory recursively
  %(prog)s src/ --strict              # Only HIGH severity
  %(prog)s src/ --json > report.json  # JSON output
  %(prog)s src/ --exit-code           # Exit 1 if HIGH findings

Severity Levels:
  HIGH   🔴 - Validation theater detected (synthetic data as [VERIFIED])
  MEDIUM 🟡 - Suspicious patterns (perfect metrics, zero failures)
  LOW    🔵 - Informational (context unclear)

Exit Codes:
  0 - No HIGH severity findings (or success with --strict)
  1 - HIGH severity findings detected
  2 - Error (file not found, invalid arguments)
        """,
    )

    parser.add_argument("path", type=Path, help="File or directory to scan")

    parser.add_argument("-r", "--recursive", action="store_true", help="Scan directory recursively")

    parser.add_argument("--strict", action="store_true", help="Only report HIGH severity findings")

    parser.add_argument(
        "--json", action="store_true", help="Output JSON format (for CI/CD integration)"
    )

    parser.add_argument("--no-context", action="store_true", help="Hide code context snippets")

    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if HIGH severity findings detected",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    args = parser.parse_args()

    # Validate path
    if not args.path.exists():
        print(f"❌ Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(2)

    # Run detection
    try:
        findings = detect_theater(args.path, recursive=args.recursive)
    except Exception as e:
        print(f"❌ Error during detection: {e}", file=sys.stderr)
        sys.exit(2)

    # Filter by severity if strict mode
    if args.strict:
        findings = filter_by_severity(findings, Severity.HIGH)

    # Output results
    if args.json:
        # JSON output
        output = {
            "total": len(findings),
            "high": len([f for f in findings if f.severity == Severity.HIGH]),
            "medium": len([f for f in findings if f.severity == Severity.MEDIUM]),
            "low": len([f for f in findings if f.severity == Severity.LOW]),
            "findings": [format_finding_json(f) for f in findings],
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        print_summary(findings, show_context=not args.no_context)

    # Exit code handling
    if args.exit_code:
        high_findings = [f for f in findings if f.severity == Severity.HIGH]
        if high_findings:
            sys.exit(1)  # HIGH findings detected
        else:
            sys.exit(0)  # Success


if __name__ == "__main__":
    main()
