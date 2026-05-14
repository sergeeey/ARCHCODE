"""
ARCHCODE Retrodiction Test Cases

10 test cases validating AlphaGenome mechanism specificity
by replicating known genomic discoveries.
"""

import sys
from pathlib import Path
from typing import List, Optional

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from validation.retrodiction_base import RetrodictionTest, TestResult


class RETRO_01_HBB_73bp_Cluster(RetrodictionTest):
    """
    Known Discovery: HBB IVS-II-1 family (73bp cluster) = regulatory mechanism

    Source: ADR-027 category-matched validation (2026-05-08)
    Published: Treisman et al. 1982 (Cell) — IVS-II-1 splice site mutation

    Expected Result:
    - Regulatory variants (IVS-II-1 family) → AlphaGenome CAGE disruption (p < 0.05)
    - Coding variants (missense, nonsense) → NULL (p > 0.05, orthogonal mechanism)
    - Mechanism specificity: 100% (regulatory PASS, coding NULL)
    """

    name = "RETRO-01: HBB 73bp Cluster Regulatory"
    locus = "HBB"
    expected_mechanism = "regulatory"

    def run(self) -> TestResult:
        result = TestResult(name=self.name, passed=False)

        try:
            # Import ARCHCODE database query interface
            from ARCHCODE.db.query import ARCHCODEDatabase

            # Connect to database
            with ARCHCODEDatabase() as db:
                # Fetch HBB validation results (ADR-027)
                validations = db.get_validation_results(gene_symbol="HBB")

                if not validations:
                    result.error = "No validation results found for HBB"
                    result.finalize()
                    return result

                # Get most recent validation
                validation = validations[0]

                # Extract metrics from validation
                alphagenome_p = validation.alphag_mann_whitney_p
                archcode_p = validation.archcode_mann_whitney_p
                spearman_rho = validation.spearman_rho

                # Assertion 1: AlphaGenome detects regulatory mechanism (p < 0.05)
                result.add_assertion(
                    description="AlphaGenome detects regulatory variants (p < 0.05)",
                    condition=alphagenome_p < 0.05,
                    detail=f"Mann-Whitney p-value: {alphagenome_p:.6f} (threshold: 0.05)",
                    metric_name="alphagenome_p_value",
                    metric_value=alphagenome_p,
                )

                # Assertion 2: ARCHCODE shows weak signal on THIS dataset (p > 0.05)
                # Known from ADR-027: pearls selected by category (promoter), not structural disruption
                # → ARCHCODE SSIM low variation (CV = 3.4%)
                result.add_assertion(
                    description="ARCHCODE weak on category-selected dataset (p > 0.05)",
                    condition=archcode_p > 0.05,
                    detail=f"Mann-Whitney p-value: {archcode_p:.6f} (expected >0.05 due to category selection bias)",
                    metric_name="archcode_p_value",
                    metric_value=archcode_p,
                )

                # Assertion 3: Low correlation (orthogonality) between methods (|ρ| < 0.3)
                # Known from ADR-028: ρ = 0.077 (WEAK-ORTHOGONAL)
                result.add_assertion(
                    description="Low correlation confirms orthogonality (|ρ| < 0.3)",
                    condition=abs(spearman_rho) < 0.3,
                    detail=f"Spearman ρ: {spearman_rho:.3f} (WEAK-ORTHOGONAL classification)",
                    metric_name="spearman_rho",
                    metric_value=spearman_rho,
                )

                # Assertion 4: Mechanism classification = WEAK-ORTHOGONAL
                classification = validation.classification
                result.add_assertion(
                    description="Classification = WEAK-ORTHOGONAL (one method strong)",
                    condition=classification == "WEAK-ORTHOGONAL",
                    detail=f"Classification: {classification} (AlphaGenome strong, ARCHCODE weak)",
                )

                # Store additional metrics
                result.metrics.update(
                    {
                        "alphagenome_p": alphagenome_p,
                        "archcode_p": archcode_p,
                        "spearman_rho": spearman_rho,
                        "classification": classification,
                        "locus": self.locus,
                    }
                )

        except Exception as e:
            result.error = str(e)

        result.finalize()
        return result


class RETRO_02_MLH1_Promoter(RetrodictionTest):
    """
    Known Discovery: MLH1 promoter variants = regulatory mechanism

    Source: ADR-029 cross-locus validation (2026-05-08)
    Published: Peltomaki 2003 — MLH1 promoter hypermethylation in Lynch syndrome

    Expected Result:
    - Promoter variants → AlphaGenome CAGE disruption
    - Mechanism specificity confirmed (similar to HBB)
    """

    name = "RETRO-02: MLH1 Promoter Regulatory"
    locus = "MLH1"
    expected_mechanism = "regulatory"

    def run(self) -> TestResult:
        result = TestResult(name=self.name, passed=False)

        try:
            from ARCHCODE.db.query import ARCHCODEDatabase

            with ARCHCODEDatabase() as db:
                validations = db.get_validation_results(gene_symbol="MLH1")

                if not validations:
                    result.error = "No validation results found for MLH1"
                    result.finalize()
                    return result

                validation = validations[0]
                alphagenome_p = validation.alphag_mann_whitney_p
                classification = validation.classification

                # Assertion 1: AlphaGenome detects regulatory (p < 0.05)
                result.add_assertion(
                    description="AlphaGenome detects MLH1 promoter variants (p < 0.05)",
                    condition=alphagenome_p < 0.05,
                    detail=f"Mann-Whitney p-value: {alphagenome_p:.6f}",
                    metric_name="alphagenome_p_value",
                    metric_value=alphagenome_p,
                )

                # Assertion 2: Mechanism = regulatory (consistent with HBB)
                result.add_assertion(
                    description="Mechanism classification = regulatory",
                    condition=classification in ["ORTHOGONAL", "WEAK-ORTHOGONAL"],
                    detail=f"Classification: {classification} (AlphaGenome detects regulatory)",
                )

                result.metrics.update(
                    {
                        "alphagenome_p": alphagenome_p,
                        "classification": classification,
                        "locus": self.locus,
                    }
                )

        except Exception as e:
            result.error = str(e)

        result.finalize()
        return result


class RETRO_03_TERT_Hotspots(RetrodictionTest):
    """
    Known Discovery: TERT C228T/C250T hotspots = regulatory gain-of-function

    Source: ADR-030 TERT sampling bias + hotspot validation (2026-05-09)
    Published: Horn et al. 2013 (Science) — TERT promoter mutations in melanoma

    Expected Result:
    - C228T/C250T → CAGE increase (+33.7%, +53.1%)
    - Gain-of-function detection (not just disruption)
    - Mechanism = regulatory (ETS binding site creation)
    """

    name = "RETRO-03: TERT Hotspots Gain-of-Function"
    locus = "TERT"
    expected_mechanism = "regulatory_gain"

    def run(self) -> TestResult:
        result = TestResult(name=self.name, passed=False)

        try:
            from ARCHCODE.db.query import ARCHCODEDatabase

            with ARCHCODEDatabase() as db:
                # Fetch TERT C228T variant (VCV000428864)
                c228t = db.get_variant(vcv_id="VCV000428864")

                # Fetch TERT C250T variant (VCV000428865)
                c250t = db.get_variant(vcv_id="VCV000428865")

                if not c228t or not c250t:
                    result.error = "TERT hotspot variants not found in database"
                    result.finalize()
                    return result

                # Assertion 1: C228T shows CAGE increase (gain-of-function)
                c228t_cage_delta = c228t.cage_delta_pct
                result.add_assertion(
                    description="C228T shows CAGE gain-of-function (positive delta)",
                    condition=c228t_cage_delta > 0,
                    detail=f"CAGE Δ: +{c228t_cage_delta:.1f}% (expected +33.7%)",
                    metric_name="c228t_cage_delta",
                    metric_value=c228t_cage_delta,
                )

                # Assertion 2: C250T shows CAGE increase (stronger)
                c250t_cage_delta = c250t.cage_delta_pct
                result.add_assertion(
                    description="C250T shows CAGE gain-of-function (positive delta)",
                    condition=c250t_cage_delta > 0,
                    detail=f"CAGE Δ: +{c250t_cage_delta:.1f}% (expected +53.1%)",
                    metric_name="c250t_cage_delta",
                    metric_value=c250t_cage_delta,
                )

                # Assertion 3: Both hotspots > +30% threshold
                result.add_assertion(
                    description="Both hotspots exceed +30% CAGE increase",
                    condition=(c228t_cage_delta > 30) and (c250t_cage_delta > 30),
                    detail=f"C228T: +{c228t_cage_delta:.1f}%, C250T: +{c250t_cage_delta:.1f}%",
                )

                # Assertion 4: AlphaGenome detects regulatory mechanism (p < 0.05)
                validations = db.get_validation_results(gene_symbol="TERT")
                if validations:
                    alphagenome_p = validations[0].alphag_mann_whitney_p
                    result.add_assertion(
                        description="AlphaGenome detects TERT regulatory mechanism (p < 0.05)",
                        condition=alphagenome_p < 0.05,
                        detail=f"Mann-Whitney p-value: {alphagenome_p:.6f}",
                        metric_name="alphagenome_p_value",
                        metric_value=alphagenome_p,
                    )

                result.metrics.update(
                    {
                        "c228t_cage_delta": c228t_cage_delta,
                        "c250t_cage_delta": c250t_cage_delta,
                        "locus": self.locus,
                    }
                )

        except Exception as e:
            result.error = str(e)

        result.finalize()
        return result


class RETRO_04_GJB2_Coding_NULL(RetrodictionTest):
    """
    Known Discovery: GJB2 coding variants = coding mechanism (NOT regulatory)

    Source: AlphaGenome mechanism specificity validation (2026-05-09)
    Published: Kelsell et al. 1997 — Connexin 26 mutations in hearing loss

    Expected Result:
    - Coding variants (missense, nonsense) → NULL (p > 0.05)
    - AlphaGenome orthogonal to coding mechanism
    - Mechanism specificity: coding locus correctly classified as NULL
    """

    name = "RETRO-04: GJB2 Coding NULL (Orthogonal)"
    locus = "GJB2"
    expected_mechanism = "coding"

    def run(self) -> TestResult:
        result = TestResult(name=self.name, passed=False)

        try:
            from ARCHCODE.db.query import ARCHCODEDatabase

            with ARCHCODEDatabase() as db:
                validations = db.get_validation_results(gene_symbol="GJB2")

                if not validations:
                    result.error = "No validation results found for GJB2"
                    result.finalize()
                    return result

                validation = validations[0]
                alphagenome_p = validation.alphag_mann_whitney_p
                classification = validation.classification

                # Assertion 1: AlphaGenome shows NULL (p > 0.05)
                result.add_assertion(
                    description="AlphaGenome NULL for coding locus (p > 0.05)",
                    condition=alphagenome_p > 0.05,
                    detail=f"Mann-Whitney p-value: {alphagenome_p:.6f} (orthogonal mechanism)",
                    metric_name="alphagenome_p_value",
                    metric_value=alphagenome_p,
                )

                # Assertion 2: Mechanism specificity correct (coding classified as NULL)
                # GJB2 is coding → AlphaGenome should NOT detect (regulatory-specific tool)
                result.add_assertion(
                    description="Mechanism specificity: coding correctly classified as NULL",
                    condition=alphagenome_p > 0.05,
                    detail="GJB2 coding variants orthogonal to AlphaGenome (CAGE-based, regulatory-specific)",
                )

                result.metrics.update(
                    {
                        "alphagenome_p": alphagenome_p,
                        "classification": classification,
                        "locus": self.locus,
                        "expected_mechanism": self.expected_mechanism,
                    }
                )

        except Exception as e:
            result.error = str(e)

        result.finalize()
        return result


# ============================================================================
# Test Suite Runner
# ============================================================================

ALL_TESTS = [
    RETRO_01_HBB_73bp_Cluster,
    RETRO_02_MLH1_Promoter,
    RETRO_03_TERT_Hotspots,
    RETRO_04_GJB2_Coding_NULL,
    # RETRO_05-10 to be implemented
]


def run_test_suite(test_classes: Optional[List[type]] = None) -> List[TestResult]:
    """
    Run retrodiction test suite.

    Args:
        test_classes: List of test classes to run (default: ALL_TESTS)

    Returns:
        List of TestResult objects
    """
    if test_classes is None:
        test_classes = ALL_TESTS

    results = []

    for i, test_class in enumerate(test_classes, 1):
        print(f"\n[{i}/{len(test_classes)}] Running {test_class.name}...")
        test = test_class()
        result = test.run()
        results.append(result)

        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(
            f"    {status} — {len([a for a in result.assertions if a.passed])}/{len(result.assertions)} assertions"
        )

        if result.error:
            print(f"    Error: {result.error}")

    return results


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from validation.retrodiction_base import generate_report

    parser = argparse.ArgumentParser(description="ARCHCODE Retrodiction Suite")
    parser.add_argument("--test", type=str, help="Run specific test (e.g., RETRO_01)", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        help="Output report path",
        default=Path("results/reports/retrodiction_report.md"),
    )
    args = parser.parse_args()

    # Select tests to run
    if args.test:
        test_map = {cls.__name__: cls for cls in ALL_TESTS}
        if args.test not in test_map:
            print(f"❌ Test {args.test} not found")
            print(f"Available tests: {', '.join(test_map.keys())}")
            sys.exit(1)
        test_classes = [test_map[args.test]]
    else:
        test_classes = ALL_TESTS

    # Run tests
    print(f"\n{'='*60}")
    print(f"ARCHCODE Retrodiction Suite")
    print(f"Running {len(test_classes)} test(s)...")
    print(f"{'='*60}")

    results = run_test_suite(test_classes)

    # Generate report
    print(f"\n{'='*60}")
    generate_report(results, args.output)
    print(f"{'='*60}\n")

    # Exit code
    all_passed = all(r.passed for r in results)
    sys.exit(0 if all_passed else 1)
