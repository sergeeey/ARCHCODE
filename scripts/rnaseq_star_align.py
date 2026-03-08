#!/usr/bin/env python3
"""
ARCHCODE RNA-seq Alignment Pipeline
Step 2: STAR alignment to hg38

Usage:
    python scripts/rnaseq_star_align.py

Input:
    fastq_data/raw/*.fastq.gz

Output:
    fastq_data/aligned/
    fastq_data/junctions/
"""

import subprocess
import os
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

FASTQ_DIR = Path("D:/ДНК/fastq_data/raw")
REFERENCE_DIR = Path("D:/ДНК/reference/hg38")
ALIGNED_DIR = Path("D:/ДНК/fastq_data/aligned")
JUNCTIONS_DIR = Path("D:/ДНК/fastq_data/junctions")

# STAR parameters
STAR_PARAMS = {
    "genomeDir": REFERENCE_DIR / "star_index",
    "runThreadN": 8,
    "readFilesCommand": "zcat",
    "outSAMtype": "BAM SortedByCoordinate",
    "outFileNamePrefix": "",
    "outWigType": "bedGraph",
    "outWigStrand": "Stranded",
    "alignSJoverhangMin": 8,
    "alignSJDBoverhangMin": 1,
    "outFilterMismatchNmax": 999,
    "outFilterMismatchNoverReadLmax": 0.04,
    "alignIntronMin": 20,
    "alignIntronMax": 1000000,
    "alignMatesGapMax": 1000000,
}

# ============================================================================
# Check STAR availability
# ============================================================================

def check_star():
    """Check if STAR is installed."""
    try:
        result = subprocess.run(
            ["STAR", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"✅ STAR found: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("❌ STAR not found!")
        print()
        print("Install STAR:")
        print("  - GitHub: https://github.com/alexdobin/STAR")
        print("  - Or: conda install -c bioconda star")
        return False
    except Exception as e:
        print(f"❌ Error checking STAR: {e}")
        return False

# ============================================================================
# Check reference genome
# ============================================================================

def check_reference():
    """Check if STAR index exists."""
    
    index_file = STAR_PARAMS["genomeDir"] / "SA"
    
    if not index_file.exists():
        print("❌ STAR index not found!")
        print()
        print(f"Expected: {index_file}")
        print()
        print("Generate STAR index:")
        print("  STAR --runThreadN 8 \\")
        print("       --runMode genomeGenerate \\")
        print("       --genomeDir reference/hg38/star_index \\")
        print("       --genomeFastaFiles reference/hg38/Homo_sapiens.GRCh38.dna.primary_assembly.fa \\")
        print("       --sjdbGTFfile reference/hg38/Homo_sapiens.GRCh38.107.gtf \\")
        print("       --sjdbOverhang 149")
        return False
    
    print(f"✅ STAR index found: {STAR_PARAMS['genomeDir']}")
    return True

# ============================================================================
# Run STAR alignment
# ============================================================================

def run_star(sample_name: str, fastq_r1: Path, fastq_r2: Path, output_dir: Path):
    """Run STAR alignment for a single sample."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "STAR",
        "--genomeDir", str(STAR_PARAMS["genomeDir"]),
        "--runThreadN", str(STAR_PARAMS["runThreadN"]),
        "--readFilesIn", str(fastq_r1), str(fastq_r2),
        "--readFilesCommand", "zcat",
        "--outSAMtype", "BAM", "SortedByCoordinate",
        "--outFileNamePrefix", str(output_dir / f"{sample_name}."),
        "--outWigType", "bedGraph",
        "--outWigStrand", "Stranded",
        "--alignSJoverhangMin", str(STAR_PARAMS["alignSJoverhangMin"]),
        "--alignSJDBoverhangMin", str(STAR_PARAMS["alignSJDBoverhangMin"]),
        "--outFilterMismatchNmax", str(STAR_PARAMS["outFilterMismatchNmax"]),
        "--outFilterMismatchNoverReadLmax", str(STAR_PARAMS["outFilterMismatchNoverReadLmax"]),
        "--alignIntronMin", str(STAR_PARAMS["alignIntronMin"]),
        "--alignIntronMax", str(STAR_PARAMS["alignIntronMax"]),
        "--alignMatesGapMax", str(STAR_PARAMS["alignMatesGapMax"]),
        "--outFilterType", "BySJout",
        "--quantMode", "GeneCounts"
    ]
    
    print(f"  🚀 Running STAR for {sample_name}...")
    print(f"     R1: {fastq_r1.name}")
    print(f"     R2: {fastq_r2.name}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours per sample
        )
        
        # Check for successful completion
        bam_file = output_dir / f"{sample_name}.Aligned.sortedByCoord.out.bam"
        
        if bam_file.exists():
            bam_size = bam_file.stat().st_size / (1024 * 1024)  # MB
            print(f"  ✅ {sample_name}: BAM created ({bam_size:.0f} MB)")
            
            # Copy junctions file
            sj_file = output_dir / f"{sample_name}.SJ.out.tab"
            if sj_file.exists():
                junctions_file = JUNCTIONS_DIR / f"{sample_name}_junctions.tab"
                junctions_file.write_text(sj_file.read_text())
                print(f"     Junctions: {sj_file.stat().st_size / 1024:.0f} KB")
            
            return True
        else:
            print(f"  ❌ {sample_name}: BAM file not created")
            if result.stderr:
                print(f"     Error: {result.stderr[:500]}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  TIMEOUT: {sample_name} (>2 hours)")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {sample_name} - {e}")
        return False

# ============================================================================
# Main pipeline
# ============================================================================

def main():
    print("=" * 70)
    print("  ARCHCODE RNA-seq Alignment Pipeline — Step 2: STAR")
    print("=" * 70)
    print()
    
    # Check STAR
    if not check_star():
        print()
        print("⚠️  STAR not available. Cannot proceed with alignment.")
        return False
    
    # Check reference
    if not check_reference():
        print()
        print("⚠️  Reference genome not ready. Generate STAR index first.")
        return False
    
    # Create output directories
    ALIGNED_DIR.mkdir(parents=True, exist_ok=True)
    JUNCTIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Aligned output: {ALIGNED_DIR}")
    print(f"📁 Junctions output: {JUNCTIONS_DIR}")
    print()
    
    # Find FASTQ files and group by sample
    fastq_files = list(FASTQ_DIR.glob("*.fastq.gz"))
    
    if not fastq_files:
        print(f"❌ No FASTQ files found in {FASTQ_DIR}")
        return False
    
    # Group paired-end files
    samples = {}
    for f in fastq_files:
        # Extract sample name and read number
        name = f.stem.replace(".fastq", "")
        parts = name.split("_")
        if len(parts) >= 2:
            sample = "_".join(parts[:-1])  # Everything except last part
            read = parts[-1]  # 1 or 2
            
            if sample not in samples:
                samples[sample] = {}
            samples[sample][read] = f
    
    print(f"📊 Found {len(samples)} samples")
    print()
    
    # Run STAR for each sample
    results = {}
    for sample, reads in sorted(samples.items()):
        if "1" in reads and "2" in reads:
            success = run_star(sample, reads["1"], reads["2"], ALIGNED_DIR)
            results[sample] = success
        else:
            print(f"  ⚠️  {sample}: Missing paired-end files, skipping")
            results[sample] = False
    
    print()
    print("=" * 70)
    print("  Alignment Complete")
    print("=" * 70)
    print()
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    
    if successful > 0:
        print()
        print("📁 Output files:")
        print(f"   {ALIGNED_DIR}/*.bam")
        print(f"   {JUNCTIONS_DIR}/*_junctions.tab")
        print()
        print("👉 Next step: Splice junction analysis")
        print("   python scripts/analyze_splice_junctions.py")
        print()
        return True
    else:
        print()
        print("❌ All alignments failed. Check logs.")
        return False

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
