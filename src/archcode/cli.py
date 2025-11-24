"""
ARCHCODE Command-Line Interface.

Provides unified entry point for running complete ARCHCODE pipeline.
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.integration.archcode_adapter import ArchcodeAdapter


def load_config(config_path: Path) -> dict:
    """Load pipeline configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_unit_tests() -> dict:
    """Run unit tests and return summary."""
    import subprocess

    print("=" * 80)
    print("STEP 1: UNIT TESTS")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["pytest", "tests/unit/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Parse output
        output_lines = result.stdout.split("\n")
        passed = sum(1 for line in output_lines if "PASSED" in line)
        failed = sum(1 for line in output_lines if "FAILED" in line)

        print(f"✅ Unit tests: {passed} passed, {failed} failed")
        if result.returncode != 0:
            print("⚠️  Some tests failed (see output above)")

        return {
            "status": "success" if result.returncode == 0 else "warning",
            "passed": passed,
            "failed": failed,
            "output": result.stdout,
        }
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return {"status": "error", "error": str(e)}


def run_regression_tests() -> dict:
    """Run regression tests and return summary."""
    import subprocess

    print("\n" + "=" * 80)
    print("STEP 2: REGRESSION TESTS")
    print("=" * 80)

    try:
        result = subprocess.run(
            ["pytest", "tests/regression/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=600,
        )

        output_lines = result.stdout.split("\n")
        passed = sum(1 for line in output_lines if "PASSED" in line)
        failed = sum(1 for line in output_lines if "FAILED" in line)

        print(f"✅ Regression tests: {passed} passed, {failed} failed")

        return {
            "status": "success" if result.returncode == 0 else "warning",
            "passed": passed,
            "failed": failed,
            "output": result.stdout,
        }
    except Exception as e:
        print(f"❌ Error running regression tests: {e}")
        return {"status": "error", "error": str(e)}


def run_rs09_simulation(config: dict, output_dir: Path) -> dict:
    """Run RS-09 processivity phase simulation."""
    if not config.get("rs09", {}).get("enabled", True):
        print("\n⏭️  RS-09: Skipped (disabled in config)")
        return {"status": "skipped"}

    print("\n" + "=" * 80)
    print("STEP 3: RS-09 PROCESSIVITY PHASE DIAGRAM")
    print("=" * 80)

    try:
        adapter = ArchcodeAdapter(mode="fast")
        rs09_config = config.get("rs09", {})

        mission_config = {
            "id": "RS09-PIPELINE",
            "mission_type": "rs09_processivity_phase",
            "parameters": {
                "processivity_min": rs09_config.get("processivity_min", 0.0),
                "processivity_max": rs09_config.get("processivity_max", 2.0),
                "processivity_steps": rs09_config.get("grid_size", 11),
                "mode": "fast",
            },
        }

        result = adapter.run_mission(mission_config)

        if result["status"] == "success":
            # Save results
            rs09_dir = output_dir / "RS09"
            rs09_dir.mkdir(parents=True, exist_ok=True)

            with open(rs09_dir / "rs09_results.json", "w") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ RS-09 completed in {result['execution_time_sec']}s")
            print(f"💾 Results saved: {rs09_dir / 'rs09_results.json'}")

        return result
    except Exception as e:
        print(f"❌ Error in RS-09: {e}")
        return {"status": "error", "error": str(e)}


def run_rs10_simulation(config: dict, output_dir: Path) -> dict:
    """Run RS-10 bookmarking threshold simulation."""
    if not config.get("rs10", {}).get("enabled", True):
        print("\n⏭️  RS-10: Skipped (disabled in config)")
        return {"status": "skipped"}

    print("\n" + "=" * 80)
    print("STEP 4: RS-10 BOOKMARKING THRESHOLD")
    print("=" * 80)

    try:
        adapter = ArchcodeAdapter(mode="fast")
        rs10_config = config.get("rs10", {})

        bookmarking_values = rs10_config.get("bookmarking_values", [0.0, 0.1, 0.2, 0.3, 0.4, 0.5])

        mission_config = {
            "id": "RS10-PIPELINE",
            "mission_type": "rs10_bookmarking_threshold",
            "parameters": {
                "bookmarking_range": bookmarking_values,
                "num_cycles": rs10_config.get("cycles", 10),
                "processivity": rs10_config.get("processivity", 0.9),
                "mode": "fast",
            },
        }

        result = adapter.run_mission(mission_config)

        if result["status"] == "success":
            rs10_dir = output_dir / "RS10"
            rs10_dir.mkdir(parents=True, exist_ok=True)

            with open(rs10_dir / "rs10_results.json", "w") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ RS-10 completed in {result['execution_time_sec']}s")
            print(f"💾 Results saved: {rs10_dir / 'rs10_results.json'}")

        return result
    except Exception as e:
        print(f"❌ Error in RS-10: {e}")
        return {"status": "error", "error": str(e)}


def run_rs11_simulation(config: dict, output_dir: Path) -> dict:
    """Run RS-11 multichannel memory simulation."""
    if not config.get("rs11", {}).get("enabled", True):
        print("\n⏭️  RS-11: Skipped (disabled in config)")
        return {"status": "skipped"}

    print("\n" + "=" * 80)
    print("STEP 5: RS-11 MULTICHANNEL MEMORY")
    print("=" * 80)

    try:
        adapter = ArchcodeAdapter(mode="fast")
        rs11_config = config.get("rs11", {})

        bookmarking_range = rs11_config.get("bookmarking_range", [0.0, 1.0, 7])
        epigenetic_range = rs11_config.get("epigenetic_range", [0.0, 1.0, 5])

        mission_config = {
            "id": "RS11-PIPELINE",
            "mission_type": "rs11_multichannel_memory",
            "parameters": {
                "bookmarking_range": bookmarking_range,
                "epigenetic_range": epigenetic_range,
                "num_cycles": rs11_config.get("cycles", 20),
                "processivity": rs11_config.get("processivity", 0.9),
                "mode": "fast",
            },
        }

        result = adapter.run_mission(mission_config)

        if result["status"] == "success":
            rs11_dir = output_dir / "RS11"
            rs11_dir.mkdir(parents=True, exist_ok=True)

            with open(rs11_dir / "rs11_results.json", "w") as f:
                json.dump(result, f, indent=2, default=str)

            print(f"✅ RS-11 completed in {result['execution_time_sec']}s")
            print(f"💾 Results saved: {rs11_dir / 'rs11_results.json'}")

        return result
    except Exception as e:
        print(f"❌ Error in RS-11: {e}")
        return {"status": "error", "error": str(e)}


def run_real_hic_analysis(config: dict, output_dir: Path) -> dict:
    """Run real Hi-C data analysis."""
    validation_config = config.get("validation", {})
    cooler_path = validation_config.get("real_hic_cooler")

    if not cooler_path or not Path(cooler_path).exists():
        print("\n⏭️  Real Hi-C Analysis: Skipped (file not found)")
        print(f"   Expected path: {cooler_path}")
        return {"status": "skipped", "reason": "file_not_found"}

    print("\n" + "=" * 80)
    print("STEP 6: REAL Hi-C DATA ANALYSIS")
    print("=" * 80)

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiments.compute_real_insulation import analyze_real_hic

        real_dir = output_dir / "real_hic_analysis"
        real_dir.mkdir(parents=True, exist_ok=True)
        
        result = analyze_real_hic(cooler_path=cooler_path, output_dir=real_dir)

        print(f"✅ Real Hi-C analysis completed")
        print(f"💾 Results saved: {real_dir}")

        return {"status": "success", "data": result}
    except Exception as e:
        import traceback
        print(f"❌ Error in real Hi-C analysis: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def run_archcode_vs_real_comparison(config: dict, output_dir: Path) -> dict:
    """Run ARCHCODE vs real Hi-C comparison."""
    validation_config = config.get("validation", {})
    cooler_path = validation_config.get("real_hic_cooler")

    if not cooler_path or not Path(cooler_path).exists():
        print("\n⏭️  ARCHCODE vs Real: Skipped (file not found)")
        print(f"   Expected path: {cooler_path}")
        return {"status": "skipped", "reason": "file_not_found"}

    print("\n" + "=" * 80)
    print("STEP 7: ARCHCODE ↔ REAL Hi-C COMPARISON")
    print("=" * 80)

    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from experiments.compare_archcode_vs_real import ARCHCODEvsRealComparison

        comparison = ARCHCODEvsRealComparison(output_dir=output_dir / "comparison")

        # Default boundaries
        boundaries_data = [
            (127100000, 0.8, "ctcf"),
            (127200000, 0.7, "ctcf"),
            (127300000, 0.6, "ctcf"),
            (127400000, 0.5, "ctcf"),
            (127500000, 0.9, "ctcf"),
        ]

        barrier_strengths_map = {pos: [0.5] for pos, _, _ in boundaries_data}
        methylation_map = {pos: 0.5 for pos, _, _ in boundaries_data}
        te_motif_map = {pos: [0.0] for pos, _, _ in boundaries_data}

        result = comparison.run_comparison(
            boundaries_data=boundaries_data,
            barrier_strengths_map=barrier_strengths_map,
            methylation_map=methylation_map,
            te_motif_map=te_motif_map,
            real_data_dir=Path(cooler_path).parent,
            nipbl_velocity=1.0,
            wapl_lifetime=1.0,
        )

        print(f"✅ Comparison completed")
        print(f"💾 Results saved: {output_dir / 'comparison'}")

        return {"status": "success", "data": result}
    except Exception as e:
        import traceback
        print(f"❌ Error in comparison: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def run_rs13_benchmark(config: dict, output_dir: Path) -> dict:
    """Run RS-13 multi-condition benchmark."""
    if not config.get("rs13", {}).get("enabled", True):
        print("\n⏭️  RS-13: Skipped (disabled in config)")
        return {"status": "skipped"}

    print("\n" + "=" * 80)
    print("STEP 8: RS-13 MULTI-CONDITION BENCHMARK")
    print("=" * 80)

    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from experiments.run_RS13_multi_condition_benchmark import (
            RS13MultiConditionBenchmark,
        )

        rs13_config_path = config.get("rs13", {}).get(
            "config", "configs/rs13_multi_condition.yaml"
        )
        benchmark = RS13MultiConditionBenchmark(config_path=rs13_config_path)
        result = benchmark.run_benchmark()

        print(f"✅ RS-13 completed")
        print(f"💾 Results saved: {benchmark.output_dir}")

        return {"status": "success", "data": result}
    except Exception as e:
        import traceback
        print(f"❌ Error in RS-13: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def run_rs12_robustness(config: dict, output_dir: Path) -> dict:
    """Run RS-12 scHi-C robustness test."""
    if not config.get("rs12", {}).get("enabled", True):
        print("\n⏭️  RS-12: Skipped (disabled in config)")
        return {"status": "skipped"}

    print("\n" + "=" * 80)
    print("STEP 9: RS-12 scHi-C ROBUSTNESS")
    print("=" * 80)

    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from experiments.run_RS12_scihic_robustness import RS12SciHiCRobustness

        validation_config = config.get("validation", {})
        cooler_path = validation_config.get("real_hic_cooler")

        if not cooler_path or not Path(cooler_path).exists():
            print("\n⏭️  RS-12: Skipped (cooler file not found)")
            return {"status": "skipped", "reason": "file_not_found"}

        test = RS12SciHiCRobustness()
        result = test.run_robustness_test(cooler_path)

        print(f"✅ RS-12 completed")
        print(f"💾 Results saved: {test.output_dir}")

        return {"status": "success", "data": result}
    except Exception as e:
        import traceback
        print(f"❌ Error in RS-12: {e}")
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def generate_summary_report(
    config: dict,
    results: dict,
    start_time: float,
    output_dir: Path,
    reports_dir: Path,
) -> Path:
    """Generate pipeline summary report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"PIPELINE_SUMMARY_{timestamp}.md"

    elapsed_time = time.time() - start_time

    # Determine overall status
    overall_status = "OK"
    if results["unit_tests"]["status"] == "error":
        overall_status = "FAIL"
    elif any(r.get("status") == "error" for r in results.values() if isinstance(r, dict)):
        overall_status = "WARNING"

    report_content = f"""# ARCHCODE Pipeline Summary Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Mode:** {config.get('mode', 'fast')}  
**Execution Time:** {elapsed_time:.2f} seconds  
**Status:** {overall_status}

---

## 📊 Pipeline Status

**Overall:** {overall_status}

---

## 1. Unit Tests

**Status:** {results['unit_tests'].get('status', 'unknown')}  
**Passed:** {results['unit_tests'].get('passed', 0)}  
**Failed:** {results['unit_tests'].get('failed', 0)}

---

## 2. Regression Tests

**Status:** {results['regression_tests'].get('status', 'unknown')}  
**Passed:** {results['regression_tests'].get('passed', 0)}  
**Failed:** {results['regression_tests'].get('failed', 0)}

---

## 3. RS-09: Processivity Phase Diagram

**Status:** {results['rs09'].get('status', 'unknown')}

"""

    if results["rs09"].get("status") == "success":
        rs09_data = results["rs09"].get("data", {})
        critical_points = rs09_data.get("critical_points", {})
        stable_fraction = rs09_data.get("stable_fraction", 0.0)

        report_content += f"""
**Results:**
- Stable Fraction: {stable_fraction:.3f}
- Collapse Threshold: {critical_points.get('collapse_threshold', 'N/A')}
- Stable Threshold: {critical_points.get('stable_threshold', 'N/A')}

**Files:**
- Results: `{output_dir / 'RS09' / 'rs09_results.json'}`
"""

    report_content += "\n---\n\n## 4. RS-10: Bookmarking Threshold\n\n"
    report_content += f"**Status:** {results['rs10'].get('status', 'unknown')}\n\n"

    if results["rs10"].get("status") == "success":
        rs10_data = results["rs10"].get("data", {})
        threshold = rs10_data.get("estimated_threshold")

        report_content += f"""
**Results:**
- Estimated Threshold: {threshold if threshold else 'Not detected'}

**Files:**
- Results: `{output_dir / 'RS10' / 'rs10_results.json'}`
"""

    report_content += "\n---\n\n## 5. RS-11: Multichannel Memory\n\n"
    report_content += f"**Status:** {results['rs11'].get('status', 'unknown')}\n\n"

    if results["rs11"].get("status") == "success":
        rs11_data = results["rs11"].get("data", {})
        phase_regimes = rs11_data.get("phase_regimes", {})

        report_content += f"""
**Results:**
- Stable Memory Points: {phase_regimes.get('stable_memory', 0)}
- Partial Memory Points: {phase_regimes.get('partial_memory', 0)}
- Drift Points: {phase_regimes.get('drift', 0)}

**Files:**
- Results: `{output_dir / 'RS11' / 'rs11_results.json'}`
"""

    report_content += "\n---\n\n## 6. Real Hi-C Analysis\n\n"
    report_content += f"**Status:** {results['real_hic'].get('status', 'unknown')}\n\n"

    report_content += "\n---\n\n## 7. ARCHCODE ↔ Real Hi-C Comparison\n\n"
    report_content += f"**Status:** {results['comparison'].get('status', 'unknown')}\n\n"

    if results["comparison"].get("status") == "success":
        comp_data = results["comparison"].get("data", {})
        insulation_corr = comp_data.get("insulation_correlation", 0.0)
        ps_corr = comp_data.get("ps_correlation", 0.0)

        report_content += f"""
**Results:**
- Insulation Correlation: {insulation_corr:.3f}
- P(s) Correlation: {ps_corr:.3f}

**Files:**
- Comparison: `{output_dir / 'comparison' / 'archcode_vs_real_comparison.png'}`
"""

    report_content += f"""

---

## 📁 Output Directory

All results saved to: `{output_dir}`

---

## ✅ Next Steps

1. Review generated figures in `{output_dir}`
2. Check detailed JSON results in subdirectories
3. Use results for publication or further analysis

---

*Report generated automatically by ARCHCODE Pipeline v1.0*
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path


def run_pipeline(mode: str = "fast"):
    """
    Run complete ARCHCODE pipeline.

    Args:
        mode: "fast" or "full"
    """
    print("=" * 80)
    print("ARCHCODE REPRODUCIBLE SCIENCE PACKAGE v1.0")
    print("=" * 80)
    print(f"Mode: {mode}")
    print("=" * 80)
    print()

    start_time = time.time()

    # Load config
    config_path = Path("configs") / f"pipeline_{mode}.yaml"
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("   Creating default config...")
        create_default_config(config_path, mode)
        print(f"   ✅ Created: {config_path}")
        print("   Please review and adjust if needed.")
        print()

    config = load_config(config_path)
    config["mode"] = mode

    # Setup output directories
    output_config = config.get("output", {})
    output_dir = Path(output_config.get("base_dir", "data/output/pipeline_runs"))
    output_dir.mkdir(parents=True, exist_ok=True)

    reports_dir = Path("docs/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Run pipeline steps
    results = {}

    # Step 1: Unit tests
    results["unit_tests"] = run_unit_tests()

    # Step 2: Regression tests
    results["regression_tests"] = run_regression_tests()

    # Step 3: RS-09
    results["rs09"] = run_rs09_simulation(config, output_dir)

    # Step 4: RS-10
    results["rs10"] = run_rs10_simulation(config, output_dir)

    # Step 5: RS-11
    results["rs11"] = run_rs11_simulation(config, output_dir)

    # Step 6: Real Hi-C analysis
    results["real_hic"] = run_real_hic_analysis(config, output_dir)

    # Step 7: Comparison
    results["comparison"] = run_archcode_vs_real_comparison(config, output_dir)

    # Step 8: RS-13 Multi-Condition Benchmark (optional)
    if config.get("rs13", {}).get("enabled", False):
        results["rs13"] = run_rs13_benchmark(config, output_dir)

    # Step 9: RS-12 scHi-C Robustness (optional)
    if config.get("rs12", {}).get("enabled", False):
        results["rs12"] = run_rs12_robustness(config, output_dir)

    # Generate summary report
    print("\n" + "=" * 80)
    print("GENERATING SUMMARY REPORT")
    print("=" * 80)

    report_path = generate_summary_report(config, results, start_time, output_dir, reports_dir)
    print(f"✅ Summary report: {report_path}")

    # Generate validation report if RS-13 or RS-12 were run
    if results.get("rs13", {}).get("status") == "success" or results.get("rs12", {}).get("status") == "success":
        print("\n" + "=" * 80)
        print("GENERATING VALIDATION REPORT")
        print("=" * 80)
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from tools.build_validation_report import ValidationReportBuilder
            builder = ValidationReportBuilder(output_dir=reports_dir)
            validation_report = builder.build_report()
            validation_path = builder.save_report(validation_report)
            print(f"✅ Validation report: {validation_path}")
        except Exception as e:
            print(f"⚠️  Could not generate validation report: {e}")

    # Final status
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)
    elapsed = time.time() - start_time
    print(f"Total execution time: {elapsed:.2f} seconds")
    print(f"Results directory: {output_dir}")
    print(f"Summary report: {report_path}")
    print("=" * 80)


def create_default_config(config_path: Path, mode: str):
    """Create default configuration file."""
    if mode == "fast":
        config_content = """# ARCHCODE Pipeline Configuration - Fast Mode
# Optimized for quick validation (15-30 minutes)

rs09:
  enabled: true
  processivity_min: 0.0
  processivity_max: 2.0
  grid_size: 11

rs10:
  enabled: true
  bookmarking_values: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
  cycles: 10
  processivity: 0.9

rs11:
  enabled: true
  bookmarking_range: [0.0, 1.0, 7]
  epigenetic_range: [0.0, 1.0, 5]
  cycles: 20
  processivity: 0.9

validation:
  real_hic_cooler: "data/real_hic/WT/Rao2014_GM12878_1000kb.cool"

output:
  base_dir: "data/output/pipeline_runs"
  figures_dir: "figures/pipeline"
"""
    else:
        config_content = """# ARCHCODE Pipeline Configuration - Full Mode
# Full validation for publication (hours)

rs09:
  enabled: true
  processivity_min: 0.0
  processivity_max: 2.0
  grid_size: 50

rs10:
  enabled: true
  bookmarking_values: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  cycles: 50
  processivity: 0.9

rs11:
  enabled: true
  bookmarking_range: [0.0, 1.0, 50]
  epigenetic_range: [0.0, 1.0, 50]
  cycles: 100
  processivity: 0.9

validation:
  real_hic_cooler: "data/real_hic/WT/Rao2014_GM12878_1000kb.cool"

output:
  base_dir: "data/output/pipeline_runs"
  figures_dir: "figures/pipeline"
"""

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ARCHCODE Reproducible Science Package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run pipeline in fast mode (15-30 minutes)
  python -m archcode.cli run-pipeline --mode fast

  # Run pipeline in full mode (hours, for publication)
  python -m archcode.cli run-pipeline --mode full
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # run-pipeline command
    p_pipeline = subparsers.add_parser("run-pipeline", help="Run complete ARCHCODE pipeline")
    p_pipeline.add_argument(
        "--mode",
        choices=["fast", "full"],
        default="fast",
        help="Pipeline mode: fast (15-30 min) or full (hours)",
    )

    args = parser.parse_args()

    if args.command == "run-pipeline":
        run_pipeline(mode=args.mode)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

