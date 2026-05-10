#!/usr/bin/env python3
"""
Quick Visual Verification Script — Monday 08:30 Pre-Submission Check
"""

import sys
from pathlib import Path

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def check_file(file_path: Path, checks: list) -> bool:
    if not file_path.exists():
        print(f"{RED}✗{RESET} File not found: {file_path}")
        return False

    content = file_path.read_text(encoding='utf-8')
    all_passed = True

    print(f"\n{BOLD}Checking: {file_path.name}{RESET}")

    for description, search_string, context in checks:
        if search_string in content:
            print(f"  {GREEN}✓{RESET} {description}")
        else:
            print(f"  {RED}✗{RESET} {description}")
            print(f"    Expected: {context}")
            all_passed = False

    return all_passed


def main():
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}ARCHCODE Pre-Submission Visual Verification{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    manuscript_dir = Path(__file__).parent

    # Check 1: Title
    title_checks = [
        ("Title: Falsification-First Framework", "A Falsification-First Framework for Evaluating 3D Chromatin Signals", "Should NOT contain 'Reveals'"),
    ]

    # Check 2: Abstract
    abstract_checks = [
        ("Pearl count: 20 (not 25/27)", "20 high-confidence HBB", "Abstract line ~10"),
        ("VEP threshold: < 0.30", "score less than 0.30", "Abstract line ~11"),
        ("LSSIM threshold: < 0.95", "LSSIM less than 0.95", "Abstract line ~12"),
        ("gnomAD count: 19/20", "19/20 verified", "Abstract line ~13"),
    ]

    # Check 3: Figure 3 caption (CRITICAL)
    body_checks = [
        ("Figure 3: 'low LSSIM (< 0.95, structurally disrupted)'", "low LSSIM (< 0.95, structurally disrupted)", "Must say LOW not HIGH"),
        ("Figure 3: 'low VEP score (< 0.30, VEP-blind)'", "low VEP score (< 0.30, VEP-blind)", "Q4 quadrant definition"),
        ("ACMG: PP3_supporting (not PS3)", "PP3_supporting (Computational evidence): 1 point", "Computational evidence only"),
        ("ACMG: PS3 limitation", "PS3 requires wet-lab validation", "Honest limitation"),
    ]

    # Run checks
    results = []
    results.append(check_file(manuscript_dir / "main.typ", title_checks))
    results.append(check_file(manuscript_dir / "abstract_content.typ", abstract_checks))
    results.append(check_file(manuscript_dir / "body_content.typ", body_checks))

    # Summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    if all(results):
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED — Ready for arXiv{RESET}")
        print(f"\nNext: Execute PRE_SUBMISSION_CHECKLIST.md (7 steps, 30 min)")
        return 0
    else:
        print(f"{RED}{BOLD}✗ CHECKS FAILED — Review corrections{RESET}")
        print(f"\nAction: Re-read CORRECTIONS_FINAL.md and re-run")
        return 1


if __name__ == "__main__":
    sys.exit(main())
