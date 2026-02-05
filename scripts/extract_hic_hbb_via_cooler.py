#!/usr/bin/env python3
"""
Extract HBB Locus from HUDEP2 Hi-C Data via cooler format
Strategy: .hic → .cool conversion → extraction

Input: GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic
Output: data/hudep2_wt_hic_hbb_locus.npy

Region: chr11:5,200,000-5,250,000
Resolution: Auto-detect from .hic file

Usage: python scripts/extract_hic_hbb_via_cooler.py
"""

import numpy as np
import sys
import json
import subprocess
from pathlib import Path

# Check dependencies
try:
    import cooler
    print(f"✅ cooler {cooler.__version__}")
except ImportError:
    print("❌ cooler not installed")
    sys.exit(1)

# HBB locus
HBB_LOCUS = {
    'chromosome': 'chr11',
    'start': 5200000,
    'end': 5250000,
}

# Paths
HIC_FILE = Path("D:/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic")
TEMP_COOL = Path("D:/ДНК/data/temp_hudep2_wt.cool")
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_contact_matrix():
    """Extract via .hic → .cool → matrix"""

    print("═══════════════════════════════════════════")
    print("  Extract Hi-C via cooler")
    print("  Strategy: .hic → .cool → matrix")
    print("═══════════════════════════════════════════\n")

    print(f"📁 Input: {HIC_FILE}")
    print(f"   Size: {HIC_FILE.stat().st_size / 1e9:.2f} GB")
    print(f"📍 Locus: {HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}\n")

    if not HIC_FILE.exists():
        print(f"❌ File not found: {HIC_FILE}")
        sys.exit(1)

    # Step 1: Convert .hic to .cool (if not exists)
    if not TEMP_COOL.exists():
        print("🔄 Converting .hic to .cool format...")
        print("   This may take several minutes...\n")

        try:
            # Use hic2cool command-line tool
            result = subprocess.run([
                "hic2cool",
                "convert",  # Mode: convert
                str(HIC_FILE),
                str(TEMP_COOL),
                "-r", "5000",  # 5kb resolution
            ], capture_output=True, text=True, timeout=600)

            if result.returncode != 0:
                print(f"❌ hic2cool failed:")
                print(result.stderr)
                sys.exit(1)

            print(f"✅ Converted to: {TEMP_COOL}\n")

        except FileNotFoundError:
            print("❌ hic2cool command not found")
            print("   Try: pip install hic2cool")
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print("❌ Conversion timeout (>10 minutes)")
            sys.exit(1)
    else:
        print(f"✅ Using existing .cool: {TEMP_COOL}\n")

    # Step 2: Extract matrix from .cool
    print("🔄 Extracting contact matrix from .cool...")

    try:
        c = cooler.Cooler(str(TEMP_COOL))

        # Get resolution
        resolution = c.binsize
        print(f"✅ Resolution: {resolution} bp")

        # Get matrix for region
        matrix = c.matrix(balance=True).fetch(
            f"{HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}"
        )

        # Convert to numpy array
        contact_matrix = np.array(matrix)

        # Statistics
        non_zero = np.count_nonzero(contact_matrix)
        min_val = np.min(contact_matrix[contact_matrix > 0]) if non_zero > 0 else 0
        max_val = np.max(contact_matrix)
        mean_val = np.mean(contact_matrix[contact_matrix > 0]) if non_zero > 0 else 0

        print(f"✅ Extracted matrix\n")

        # Save
        output_path = OUTPUT_DIR / "hudep2_wt_hic_hbb_locus.npy"
        np.save(output_path, contact_matrix)

        # Metadata
        metadata = {
            'source_file': HIC_FILE.name,
            'source_size_gb': HIC_FILE.stat().st_size / 1e9,
            'locus': f"{HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}",
            'resolution': int(resolution),
            'matrix_shape': list(contact_matrix.shape),
            'normalization': 'balanced',
            'non_zero_elements': int(non_zero),
            'min_contact': float(min_val),
            'max_contact': float(max_val),
            'mean_contact': float(mean_val),
            'total_sum': float(np.sum(contact_matrix)),
            'library': 'cooler',
        }

        metadata_path = OUTPUT_DIR / "hudep2_wt_hic_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print("═══════════════════════════════════════════")
        print("  Extraction Complete")
        print("═══════════════════════════════════════════\n")

        print("📊 FACTUAL MEASUREMENTS:")
        print(f"   Matrix shape: {contact_matrix.shape}")
        print(f"   Resolution: {resolution} bp")
        print(f"   Non-zero elements: {non_zero}")
        print(f"   Min contact (non-zero): {min_val:.6f}")
        print(f"   Max contact: {max_val:.6f}")
        print(f"   Mean contact (non-zero): {mean_val:.6f}")
        print(f"   Total sum: {np.sum(contact_matrix):.2f}\n")

        print(f"💾 Matrix: {output_path.absolute()}")
        print(f"💾 Metadata: {metadata_path.absolute()}\n")

        return contact_matrix, metadata

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    extract_contact_matrix()
