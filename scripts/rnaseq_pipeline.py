#!/usr/bin/env python3
"""
ARCHCODE RNA-seq Analysis Pipeline
Master script that runs all steps

Usage:
    python scripts/rnaseq_pipeline.py

Steps:
    1. FastQC (QC check)
    2. STAR alignment
    3. Splice junction analysis
"""

import subprocess
import sys
from pathlib import Path

# ============================================================================
# Pipeline steps
# ============================================================================

STEPS = [
    {
        "name": "FastQC Quality Control",
        "script": "rnaseq_qc.py",
        "required": False,  # Can skip if FastQC not installed
    },
    {
        "name": "STAR Alignment",
        "script": "rnaseq_star_align.py",
        "required": True,   # Must succeed to continue
    },
    {
        "name": "Splice Junction Analysis",
        "script": "analyze_splice_junctions.py",
        "required": True,   # Final analysis
    },
]

# ============================================================================
# Run step
# ============================================================================

def run_step(step: dict) -> bool:
    """Run a single pipeline step."""
    
    print()
    print("=" * 70)
    print(f"  STEP: {step['name']}")
    print("=" * 70)
    print()
    
    script_path = Path(__file__).parent / step["script"]
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True,
            timeout=14400  # 4 hours total
        )
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT: {step['name']} (>4 hours)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {step['name']} - {e}")
        return False

# ============================================================================
# Main pipeline
# ============================================================================

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "ARCHCODE RNA-seq Analysis Pipeline" + " " * 22 + "║")
    print("║" + " " * 15 + "'Loop That Stayed' Hypothesis Test" + " " * 17 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    print("📋 Pipeline Steps:")
    print()
    
    for i, step in enumerate(STEPS, 1):
        required = "Required" if step["required"] else "Optional"
        print(f"  {i}. {step['name']} ({required})")
    
    print()
    print("-" * 70)
    print()
    
    # Run each step
    results = {}
    
    for step in STEPS:
        success = run_step(step)
        results[step["name"]] = success
        
        if success:
            print()
            print(f"✅ {step['name']}: SUCCESS")
        else:
            print()
            print(f"❌ {step['name']}: FAILED")
            
            if step["required"]:
                print()
                print("⚠️  Required step failed. Stopping pipeline.")
                print()
                
                # Summary
                print("=" * 70)
                print("  PIPELINE SUMMARY")
                print("=" * 70)
                print()
                
                for name, success in results.items():
                    status = "✅" if success else "❌"
                    print(f"  {status} {name}")
                
                print()
                return False
            else:
                print()
                print("⚠️  Optional step skipped. Continuing...")
                print()
    
    # All steps completed
    print()
    print("=" * 70)
    print("  🎉 PIPELINE COMPLETE")
    print("=" * 70)
    print()
    
    # Summary
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    
    print()
    print("📁 Output files:")
    print("   fastq_data/qc/fastqc/*.html  (QC reports)")
    print("   fastq_data/aligned/*.bam     (Aligned reads)")
    print("   fastq_data/junctions/*       (Splice junctions)")
    print("   fastq_data/results/*         (Analysis results)")
    print()
    print("📄 Report:")
    print("   fastq_data/results/splice_analysis_report.md")
    print()
    print("👉 Next step: Review results and update manuscript")
    print("   docs/MANUSCRIPT_UPDATE_PLAN.md")
    print()
    
    return True

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
