"""
Self-Audit Script for ARCHCODE Project.

Comprehensive check of:
- Pipeline results
- Test status
- Data availability
- Publication readiness
- Code quality
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SelfAudit:
    """Comprehensive self-audit of ARCHCODE project."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
        self.base_dir = Path("data/output/pipeline_runs")

    def check_pipeline_results(self):
        """Check if pipeline results exist and are valid."""
        print("\n" + "=" * 80)
        print("1. PIPELINE RESULTS CHECK")
        print("=" * 80)

        checks = {
            "rs09": False,
            "rs10": False,
            "rs11": False,
            "real_hic": False,
            "comparison": False,
        }

        # RS-09
        rs09_file = self.base_dir / "RS09" / "rs09_results.json"
        if rs09_file.exists():
            try:
                data = json.load(open(rs09_file))
                if data.get("status") == "success":
                    checks["rs09"] = True
                    self.successes.append("RS-09: Results valid")
                else:
                    self.issues.append(f"RS-09: Status = {data.get('status')}")
            except Exception as e:
                self.issues.append(f"RS-09: Error loading - {e}")
        else:
            self.warnings.append("RS-09: Results file not found")

        # RS-10
        rs10_file = self.base_dir / "RS10" / "rs10_results.json"
        if rs10_file.exists():
            try:
                data = json.load(open(rs10_file))
                if data.get("status") == "success":
                    checks["rs10"] = True
                    self.successes.append("RS-10: Results valid")
                else:
                    self.issues.append(f"RS-10: Status = {data.get('status')}")
            except Exception as e:
                self.issues.append(f"RS-10: Error loading - {e}")
        else:
            self.warnings.append("RS-10: Results file not found")

        # RS-11
        rs11_file = self.base_dir / "RS11" / "rs11_results.json"
        if rs11_file.exists():
            try:
                data = json.load(open(rs11_file))
                if data.get("status") == "success":
                    data_content = data.get("data", {})
                    memory_matrix = data_content.get("memory_matrix", [])
                    if len(memory_matrix) > 0:
                        checks["rs11"] = True
                        self.successes.append(f"RS-11: Results valid ({len(memory_matrix)}×{len(memory_matrix[0]) if memory_matrix else 0} grid)")
                    else:
                        self.warnings.append("RS-11: Empty memory matrix")
                else:
                    self.issues.append(f"RS-11: Status = {data.get('status')}")
            except Exception as e:
                self.issues.append(f"RS-11: Error loading - {e}")
        else:
            self.warnings.append("RS-11: Results file not found")

        # Real Hi-C
        real_hic_summary = self.base_dir / "real_hic_analysis" / "analysis_summary.json"
        if real_hic_summary.exists():
            try:
                data = json.load(open(real_hic_summary))
                if data.get("cooler_info"):
                    checks["real_hic"] = True
                    self.successes.append("Real Hi-C: Analysis complete")
                else:
                    self.warnings.append("Real Hi-C: Missing cooler_info")
            except Exception as e:
                self.issues.append(f"Real Hi-C: Error loading - {e}")
        else:
            self.warnings.append("Real Hi-C: Analysis summary not found")

        # Comparison
        comparison_summary = self.base_dir / "comparison" / "comparison_summary.json"
        comparison_fig = self.base_dir / "comparison" / "archcode_vs_real_comparison.png"
        if comparison_summary.exists() and comparison_fig.exists():
            checks["comparison"] = True
            self.successes.append("Comparison: Figure and summary exist")
        else:
            self.warnings.append("Comparison: Missing files")

        return checks

    def check_tests(self):
        """Check test status."""
        print("\n" + "=" * 80)
        print("2. TEST STATUS CHECK")
        print("=" * 80)

        # Run unit tests
        print("   Running unit tests...")
        try:
            result = pytest.main(["-v", "tests/unit/", "--tb=short", "-q"])
            if result == 0:
                self.successes.append("Unit tests: All passed")
            else:
                self.issues.append(f"Unit tests: {result} failures")
        except Exception as e:
            self.issues.append(f"Unit tests: Error - {e}")

        # Run regression tests
        print("   Running regression tests...")
        try:
            result = pytest.main(["-v", "tests/regression/", "--tb=short", "-q"])
            if result == 0:
                self.successes.append("Regression tests: All passed")
            else:
                self.issues.append(f"Regression tests: {result} failures")
        except Exception as e:
            self.issues.append(f"Regression tests: Error - {e}")

    def check_publication_readiness(self):
        """Check publication readiness."""
        print("\n" + "=" * 80)
        print("3. PUBLICATION READINESS CHECK")
        print("=" * 80)

        # Check figures
        fig_dir = Path("figures/publication")
        if fig_dir.exists():
            figures = list(fig_dir.glob("*.png"))
            if figures:
                self.successes.append(f"Publication figures: {len(figures)} found")
                for fig in figures:
                    size_kb = fig.stat().st_size / 1024
                    if size_kb > 100:  # Reasonable size for publication
                        self.successes.append(f"  ✓ {fig.name} ({size_kb:.1f} KB)")
                    else:
                        self.warnings.append(f"  ⚠ {fig.name} seems small ({size_kb:.1f} KB)")
            else:
                self.warnings.append("Publication figures: No figures found")
        else:
            self.warnings.append("Publication figures: Directory not found")

        # Check reports
        reports_dir = Path("docs/reports")
        if reports_dir.exists():
            reports = list(reports_dir.glob("PIPELINE_SUMMARY_*.md"))
            if reports:
                latest = max(reports, key=lambda p: p.stat().st_mtime)
                self.successes.append(f"Pipeline reports: {len(reports)} found (latest: {latest.name})")
            else:
                self.warnings.append("Pipeline reports: No reports found")

        # Check RS-11 full mode results
        rs11_file = self.base_dir / "RS11" / "rs11_results.json"
        if rs11_file.exists():
            try:
                data = json.load(open(rs11_file))
                data_content = data.get("data", {})
                memory_matrix = data_content.get("memory_matrix", [])
                if len(memory_matrix) >= 20:  # Full mode should have 50×50
                    self.successes.append(f"RS-11: Full mode results ({len(memory_matrix)}×{len(memory_matrix[0]) if memory_matrix else 0})")
                else:
                    self.warnings.append(f"RS-11: Fast mode results ({len(memory_matrix)}×{len(memory_matrix[0]) if memory_matrix else 0}), consider full mode")
            except Exception as e:
                self.issues.append(f"RS-11: Error checking - {e}")

    def check_data_quality(self):
        """Check data quality and correlations."""
        print("\n" + "=" * 80)
        print("4. DATA QUALITY CHECK")
        print("=" * 80)

        # Check comparison correlations
        comparison_summary = self.base_dir / "comparison" / "comparison_summary.json"
        if comparison_summary.exists():
            try:
                data = json.load(open(comparison_summary))
                ps_corr = data.get("ps_correlation", 0.0)
                ins_corr = data.get("insulation_correlation", 0.0)

                if ps_corr != 0.0:
                    if abs(ps_corr) > 0.5:
                        self.successes.append(f"P(s) correlation: {ps_corr:.3f} (good)")
                    else:
                        self.warnings.append(f"P(s) correlation: {ps_corr:.3f} (low)")
                else:
                    self.warnings.append("P(s) correlation: 0.000 (needs investigation)")

                if ins_corr != 0.0:
                    if abs(ins_corr) > 0.5:
                        self.successes.append(f"Insulation correlation: {ins_corr:.3f} (good)")
                    else:
                        self.warnings.append(f"Insulation correlation: {ins_corr:.3f} (low)")
                else:
                    self.warnings.append("Insulation correlation: 0.000 (needs investigation)")
            except Exception as e:
                self.issues.append(f"Comparison: Error checking correlations - {e}")

        # Check RS-11 phase regimes
        rs11_file = self.base_dir / "RS11" / "rs11_results.json"
        if rs11_file.exists():
            try:
                data = json.load(open(rs11_file))
                data_content = data.get("data", {})
                phase_regimes = data_content.get("phase_regimes", {})
                stable = phase_regimes.get("stable_memory", 0)
                drift = phase_regimes.get("drift", 0)
                if stable > 0:
                    self.successes.append(f"RS-11: Stable memory points = {stable}")
                if drift > 0:
                    self.successes.append(f"RS-11: Drift points = {drift}")
            except Exception as e:
                self.issues.append(f"RS-11: Error checking phase regimes - {e}")

    def check_file_structure(self):
        """Check critical file structure."""
        print("\n" + "=" * 80)
        print("5. FILE STRUCTURE CHECK")
        print("=" * 80)

        critical_files = [
            "src/archcode/cli.py",
            "configs/pipeline_fast.yaml",
            "configs/pipeline_full.yaml",
            "experiments/generate_publication_figures.py",
            "tools/build_validation_report.py",
        ]

        for file_path in critical_files:
            path = Path(file_path)
            if path.exists():
                self.successes.append(f"File exists: {file_path}")
            else:
                self.issues.append(f"File missing: {file_path}")

    def generate_report(self):
        """Generate audit report."""
        print("\n" + "=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)

        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes:
            print(f"   ✓ {success}")

        print(f"\n⚠️  Warnings: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"   ⚠ {warning}")

        print(f"\n❌ Issues: {len(self.issues)}")
        for issue in self.issues:
            print(f"   ✗ {issue}")

        # Overall status
        print("\n" + "=" * 80)
        if len(self.issues) == 0:
            if len(self.warnings) == 0:
                status = "✅ EXCELLENT"
            elif len(self.warnings) <= 3:
                status = "✅ GOOD"
            else:
                status = "⚠️  NEEDS ATTENTION"
        else:
            status = "❌ ISSUES FOUND"

        print(f"OVERALL STATUS: {status}")
        print("=" * 80)

        # Save report
        report_path = Path("docs/reports") / f"SELF_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# ARCHCODE Self-Audit Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(f"## Overall Status: {status}\n\n")
            f.write(f"- ✅ Successes: {len(self.successes)}\n")
            f.write(f"- ⚠️  Warnings: {len(self.warnings)}\n")
            f.write(f"- ❌ Issues: {len(self.issues)}\n\n")
            f.write("---\n\n")
            f.write("## Successes\n\n")
            for success in self.successes:
                f.write(f"- ✅ {success}\n")
            f.write("\n---\n\n")
            f.write("## Warnings\n\n")
            for warning in self.warnings:
                f.write(f"- ⚠️  {warning}\n")
            f.write("\n---\n\n")
            f.write("## Issues\n\n")
            for issue in self.issues:
                f.write(f"- ❌ {issue}\n")

        print(f"\n📄 Report saved: {report_path}")

    def run(self):
        """Run complete audit."""
        print("=" * 80)
        print("ARCHCODE SELF-AUDIT")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        self.check_pipeline_results()
        self.check_tests()
        self.check_publication_readiness()
        self.check_data_quality()
        self.check_file_structure()
        self.generate_report()


def main():
    """Main entry point."""
    audit = SelfAudit()
    audit.run()


if __name__ == "__main__":
    main()

