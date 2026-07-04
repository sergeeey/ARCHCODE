"""
Command-line interface for Validation Theater Detector

Usage:
    validation-theater-detector <file_or_directory>
    validation-theater-detector src/ --recursive --strict
    validation-theater-detector . --fail-on THEATER --output json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .detector import ValidationTheaterDetector, DetectionResult


def format_text_output(results: List[DetectionResult], verbose: bool = False) -> str:
    """Format results as human-readable text."""
    output = []

    # Summary
    total = len(results)
    clean = sum(1 for r in results if r.verdict == "CLEAN")
    suspicious = sum(1 for r in results if r.verdict == "SUSPICIOUS")
    theater = sum(1 for r in results if r.verdict == "THEATER")
    high_risk = sum(1 for r in results if r.verdict == "HIGH_RISK")

    output.append("=" * 70)
    output.append("Validation Theater Detector — Scan Results")
    output.append("=" * 70)
    output.append(f"\nScanned {total} file(s):")
    output.append(f"  ✅ CLEAN: {clean}")
    output.append(f"  ⚠️  SUSPICIOUS: {suspicious}")
    output.append(f"  🎭 THEATER: {theater}")
    output.append(f"  🚨 HIGH_RISK: {high_risk}")

    # Details for non-clean files
    problematic = [r for r in results if r.verdict != "CLEAN"]

    if problematic:
        output.append("\n" + "=" * 70)
        output.append("DETAILED FINDINGS:")
        output.append("=" * 70)

        for result in problematic:
            output.append(f"\n📁 {result.file_path}")
            output.append(f"   Verdict: {result.verdict}")
            output.append(
                f"   Risk: {result.risk_score:.0f}/100 (confidence: {result.confidence:.2f})"
            )

            if verbose:
                # Show pattern details
                if result.synthetic_findings:
                    output.append(f"\n   Synthetic markers ({len(result.synthetic_findings)}):")
                    for name, info in result.synthetic_findings.items():
                        output.append(
                            f"     • {name}: {info['severity']} (conf={info['confidence']:.2f})"
                        )

                if result.metric_findings:
                    output.append(f"\n   Metric patterns ({len(result.metric_findings)}):")
                    for name, info in result.metric_findings.items():
                        output.append(
                            f"     • {name}: {info['severity']} ({len(info['matches'])} matches)"
                        )

                if result.inline_synthetic_findings:
                    output.append(
                        f"\n   Inline synthetic patterns ({len(result.inline_synthetic_findings)}):"
                    )
                    for name, info in result.inline_synthetic_findings.items():
                        output.append(
                            f"     • {name}: {info['severity']} ({len(info['matches'])} matches)"
                        )

            if result.warnings:
                output.append("\n   Warnings:")
                for warning in result.warnings:
                    output.append(f"     {warning}")
    else:
        output.append("\n✅ All files CLEAN — no validation theater detected")

    output.append("\n" + "=" * 70)

    return "\n".join(output)


def format_json_output(results: List[DetectionResult]) -> str:
    """Format results as JSON."""
    output = {
        "summary": {
            "total": len(results),
            "clean": sum(1 for r in results if r.verdict == "CLEAN"),
            "suspicious": sum(1 for r in results if r.verdict == "SUSPICIOUS"),
            "theater": sum(1 for r in results if r.verdict == "THEATER"),
            "high_risk": sum(1 for r in results if r.verdict == "HIGH_RISK"),
        },
        "files": [
            {
                "path": r.file_path,
                "verdict": r.verdict,
                "risk_score": r.risk_score,
                "confidence": r.confidence,
                "synthetic_findings": r.synthetic_findings,
                "metric_findings": r.metric_findings,
                "inline_synthetic_findings": r.inline_synthetic_findings,
                "warnings": r.warnings,
            }
            for r in results
        ],
    }
    return json.dumps(output, indent=2)


def format_summary_output(results: List[DetectionResult]) -> str:
    """Format results as compact summary."""
    total = len(results)
    clean = sum(1 for r in results if r.verdict == "CLEAN")
    suspicious = sum(1 for r in results if r.verdict == "SUSPICIOUS")
    theater = sum(1 for r in results if r.verdict == "THEATER")
    high_risk = sum(1 for r in results if r.verdict == "HIGH_RISK")

    lines = [
        f"Scanned {total} files: {clean} clean, {suspicious} suspicious, {theater} theater, {high_risk} high-risk"
    ]

    # List problematic files
    problematic = [r for r in results if r.verdict != "CLEAN"]
    if problematic:
        lines.append("\nProblematic files:")
        for r in problematic:
            lines.append(f"  [{r.verdict}] {r.file_path} (risk={r.risk_score:.0f})")

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validation Theater Detector — Catch synthetic data marked as [VERIFIED]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan single file
  validation-theater-detector script.py

  # Scan directory recursively
  validation-theater-detector src/ --recursive

  # Strict mode (lower thresholds)
  validation-theater-detector . --recursive --strict

  # Fail on specific verdict
  validation-theater-detector src/ --fail-on THEATER

  # JSON output for CI integration
  validation-theater-detector . --recursive --output json --fail-on HIGH_RISK
        """,
    )

    parser.add_argument("path", type=str, help="File or directory to scan")

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Scan directories recursively (default: False)",
    )

    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="Strict mode: lower thresholds for THEATER verdict (default: False)",
    )

    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold for reporting findings (0.0-1.0, default: 0.5)",
    )

    parser.add_argument(
        "--fail-on",
        type=str,
        choices=["SUSPICIOUS", "THEATER", "HIGH_RISK"],
        default=None,
        help="Exit with code 1 if any file has verdict >= this level",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output: show pattern details (only for text output)",
    )

    parser.add_argument(
        "--patterns",
        type=str,
        nargs="+",
        default=["*.py", "*.ipynb", "*.txt", "*.log"],
        help="File patterns to scan (default: *.py *.ipynb *.txt *.log)",
    )

    args = parser.parse_args()

    # Initialize detector
    detector = ValidationTheaterDetector(
        min_confidence=args.min_confidence, strict_mode=args.strict
    )

    # Scan
    path = Path(args.path)

    if not path.exists():
        print(f"❌ Error: Path not found: {path}", file=sys.stderr)
        return 1

    if path.is_file():
        results = [detector.check_file(str(path))]
    else:
        results = detector.check_directory(
            str(path), recursive=args.recursive, file_patterns=args.patterns
        )

    # Format output
    if args.output == "json":
        print(format_json_output(results))
    elif args.output == "summary":
        print(format_summary_output(results))
    else:  # text
        print(format_text_output(results, verbose=args.verbose))

    # Check fail condition
    if args.fail_on:
        verdict_levels = {
            "SUSPICIOUS": ["SUSPICIOUS", "THEATER", "HIGH_RISK"],
            "THEATER": ["THEATER", "HIGH_RISK"],
            "HIGH_RISK": ["HIGH_RISK"],
        }

        fail_verdicts = verdict_levels[args.fail_on]
        failures = [r for r in results if r.verdict in fail_verdicts]

        if failures:
            print(
                f"\n❌ FAILED: {len(failures)} file(s) with verdict >= {args.fail_on}",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
