#!/usr/bin/env python3
"""
ARCHCODE RNA-seq QC Pipeline
Step 1: FastQC quality control

Usage:
    python scripts/rnaseq_qc.py

Input:
    fastq_data/raw/*.fastq.gz

Output:
    fastq_data/qc/fastqc/
"""

import subprocess
import os
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

FASTQ_DIR = Path("D:/ДНК/fastq_data/raw")
OUTPUT_DIR = Path("D:/ДНК/fastq_data/qc/fastqc")

# ============================================================================
# Check FastQC availability
# ============================================================================

def check_fastqc():
    """Check if FastQC is installed."""
    try:
        result = subprocess.run(
            ["fastqc", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"✅ FastQC found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ FastQC not found!")
        print()
        print("Install FastQC:")
        print("  - Windows: https://www.bioinformatics.babraham.ac.uk/projects/fastqc/")
        print("  - Or: conda install -c bioconda fastqc")
        return False
    except Exception as e:
        print(f"❌ Error checking FastQC: {e}")
        return False

# ============================================================================
# Run FastQC
# ============================================================================

def run_fastqc(fastq_file: Path, output_dir: Path):
    """Run FastQC on a single FASTQ file."""
    
    cmd = [
        "fastqc",
        str(fastq_file),
        "--outdir", str(output_dir),
        "--extract",
        "--quiet"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print(f"  ✅ {fastq_file.name}")
            return True
        else:
            print(f"  ❌ {fastq_file.name}: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  TIMEOUT: {fastq_file.name}")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {fastq_file.name} - {e}")
        return False

# ============================================================================
# Main pipeline
# ============================================================================

def main():
    print("=" * 70)
    print("  ARCHCODE RNA-seq QC Pipeline — Step 1: FastQC")
    print("=" * 70)
    print()
    
    # Check FastQC
    if not check_fastqc():
        print()
        print("⚠️  FastQC not available. Skipping QC step.")
        print("   You can still proceed with alignment (STAR).")
        return False
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print()
    
    # Find FASTQ files
    fastq_files = list(FASTQ_DIR.glob("*.fastq.gz"))
    
    if not fastq_files:
        print(f"❌ No FASTQ files found in {FASTQ_DIR}")
        return False
    
    print(f"📊 Found {len(fastq_files)} FASTQ files")
    print()
    
    # Run FastQC
    print("Running FastQC...")
    print()
    
    results = {}
    for fastq_file in sorted(fastq_files):
        success = run_fastqc(fastq_file, OUTPUT_DIR)
        results[fastq_file.name] = success
    
    print()
    print("=" * 70)
    print("  QC Complete")
    print("=" * 70)
    print()
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    
    if successful == total:
        print()
        print("🎉 All files passed QC!")
        print()
        print("📁 Output files:")
        print(f"   {OUTPUT_DIR}/*.html")
        print(f"   {OUTPUT_DIR}/*.zip")
        print()
        print("👉 Next step: STAR alignment")
        print("   python scripts/rnaseq_star_align.py")
        print()
        return True
    else:
        print()
        print("⚠️  Some files failed QC. Check reports:")
        for name, success in results.items():
            if not success:
                print(f"   - {name}")
        print()
        return False

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
