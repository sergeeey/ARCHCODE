#!/usr/bin/env python3
"""
Check for existing RNA-seq alignment data
Looks for BAM files, junction files, or any previous analysis
"""

import os
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

FASTQ_DIR = Path("D:/ДНК/fastq_data")
SEARCH_DIRS = [
    FASTQ_DIR / "raw",
    FASTQ_DIR / "aligned",
    FASTQ_DIR / "junctions",
    FASTQ_DIR / "results",
    FASTQ_DIR / "qc",
]

# ============================================================================
# Search
# ============================================================================

def search_files():
    """Search for RNA-seq related files."""
    
    print("=" * 70)
    print("  Searching for Existing RNA-seq Data")
    print("=" * 70)
    print()
    
    extensions = {
        ".bam": "BAM alignment",
        ".sam": "SAM alignment",
        ".cram": "CRAM alignment",
        ".tab": "Junctions (STAR)",
        ".tsv": "Junctions (TSV)",
        ".txt": "Junctions (TXT)",
        ".junction": "Junctions",
        ".fastq.gz": "FASTQ",
        ".fq.gz": "FASTQ",
    }
    
    found = {ext: [] for ext in extensions.keys()}
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists():
            continue
        
        print(f"📁 Scanning: {search_dir}")
        
        for file in search_dir.rglob("*"):
            if file.is_file():
                # Check extension
                name = file.name.lower()
                for ext, description in extensions.items():
                    if name.endswith(ext):
                        size_mb = file.stat().st_size / (1024 * 1024)
                        found[ext].append({
                            "path": file,
                            "size_mb": size_mb,
                            "description": description
                        })
        
        print()
    
    # Report findings
    print("=" * 70)
    print("  Summary")
    print("=" * 70)
    print()
    
    total_files = 0
    total_size = 0
    
    for ext, files in found.items():
        if files:
            print(f"✅ {extensions[ext]} ({ext}): {len(files)} files")
            for f in files:
                size_str = f"{f['size_mb']:.1f} MB" if f['size_mb'] < 1024 else f"{f['size_mb']/1024:.2f} GB"
                print(f"   - {f['path'].relative_to(FASTQ_DIR.parent)} ({size_str})")
                total_files += 1
                total_size += f['size_mb']
            print()
        else:
            print(f"❌ {extensions[ext]} ({ext}): 0 files")
    
    print()
    print("-" * 70)
    print(f"Total: {total_files} files, {total_size/1024:.2f} GB")
    print()
    
    # Recommendations
    print("=" * 70)
    print("  Recommendations")
    print("=" * 70)
    print()
    
    # Check for usable junctions
    junction_files = found.get(".tab", []) + found.get(".tsv", []) + found.get(".txt", [])
    
    if junction_files:
        print("✅ JUNCTIONS FOUND!")
        print()
        print("You can proceed with splice analysis:")
        print("  python scripts\\analyze_splice_junctions.py")
        print()
        return "JUNCTIONS_READY"
    
    # Check for BAM files
    bam_files = found.get(".bam", [])
    
    if bam_files:
        # Check if any BAM is non-empty
        non_empty_bam = [f for f in bam_files if f['size_mb'] > 1]
        
        if non_empty_bam:
            print("✅ NON-EMPTY BAM FILES FOUND!")
            print()
            print("Options:")
            print("  1. Extract junctions from BAM (requires samtools)")
            print("  2. Use Galaxy to re-align")
            print()
            print("To extract junctions:")
            print("  samtools view BAM_FILE | python scripts/extract_junctions.py")
            print()
            return "BAM_READY"
        else:
            print("⚠️  BAM FILES FOUND BUT EMPTY (0 bytes)")
            print()
            print("These are from failed alignment attempts.")
            print("Need to re-align with Galaxy or local STAR.")
            print()
            return "BAM_EMPTY"
    
    # Check for FASTQ
    fastq_files = found.get(".fastq.gz", []) + found.get(".fq.gz", [])
    
    if fastq_files:
        print("✅ FASTQ FILES FOUND!")
        print()
        print("FASTQ files ready for alignment.")
        print()
        print("Options:")
        print("  1. Galaxy (recommended): docs\\GALAXY_RNASEQ_GUIDE.md")
        print("  2. Local STAR (requires reference): reference\\SETUP_REFERENCE.md")
        print()
        return "FASTQ_READY"
    
    print("❌ NO RNA-SEQ DATA FOUND")
    print()
    print("Need to download FASTQ files first.")
    print()
    return "NO_DATA"

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    status = search_files()
    
    print()
    print("=" * 70)
    print(f"  Status: {status}")
    print("=" * 70)
    print()
    
    if status == "JUNCTIONS_READY":
        print("👉 Next: python scripts\\analyze_splice_junctions.py")
    elif status == "BAM_READY":
        print("👉 Next: Extract junctions from BAM")
    elif status == "BAM_EMPTY":
        print("👉 Next: Use Galaxy for alignment")
        print("   See: docs\\GALAXY_RNASEQ_GUIDE.md")
    elif status == "FASTQ_READY":
        print("👉 Next: Align with Galaxy")
        print("   See: docs\\GALAXY_RNASEQ_GUIDE.md")
    else:
        print("👉 Next: Download FASTQ files")
    
    print()
