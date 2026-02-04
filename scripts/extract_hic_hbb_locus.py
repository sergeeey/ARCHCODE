#!/usr/bin/env python3
"""
Extract HBB Locus from HUDEP2 Hi-C Data (Ground Truth)

Input: GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic
Output: data/hudep2_wt_hic_hbb_locus.npy (contact matrix)

Region: chr11:5,200,000-5,250,000 (50 KB window around HBB)
Resolution: 5 KB bins (10 x 10 matrix)

Usage: python scripts/extract_hic_hbb_locus.py
"""

import numpy as np
import sys
from pathlib import Path

# Check if hicstraw is installed
try:
    import hicstraw
    print("✅ hicstraw found")
except ImportError:
    print("❌ hicstraw not installed")
    print("   Install: pip install hic-straw")
    sys.exit(1)

# HBB locus parameters
HBB_LOCUS = {
    'chromosome': 'chr11',
    'start': 5200000,
    'end': 5250000,
    'resolution': 5000,  # 5 KB bins
}

# Input file
HIC_FILE = Path("C:/Users/serge/Desktop/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_contact_matrix():
    """Extract HBB locus contact matrix from .hic file"""

    print("═══════════════════════════════════════════")
    print("  Extract Hi-C Ground Truth (HUDEP2 WT)")
    print("═══════════════════════════════════════════\n")

    print(f"📁 Input: {HIC_FILE.name}")
    print(f"📍 Locus: {HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}")
    print(f"📏 Resolution: {HBB_LOCUS['resolution']} bp\n")

    # Check if file exists
    if not HIC_FILE.exists():
        print(f"❌ Error: File not found: {HIC_FILE}")
        print("   Check path and try again.")
        sys.exit(1)

    print("🔄 Loading .hic file...")

    try:
        # Open .hic file
        hic = hicstraw.HiCFile(str(HIC_FILE))

        # Get available resolutions
        resolutions = hic.getResolutions()
        print(f"✅ Available resolutions: {resolutions}")

        # Check if our resolution is available
        if HBB_LOCUS['resolution'] not in resolutions:
            print(f"⚠️  Resolution {HBB_LOCUS['resolution']} not available")
            print(f"   Using closest: {min(resolutions, key=lambda x: abs(x - HBB_LOCUS['resolution']))}")
            HBB_LOCUS['resolution'] = min(resolutions, key=lambda x: abs(x - HBB_LOCUS['resolution']))

        # Extract contact matrix
        print(f"\n🔄 Extracting contacts (resolution: {HBB_LOCUS['resolution']} bp)...")

        # Get matrix zoom data
        # normalization: "KR" (Knight-Ruiz), "VC" (Vanilla Coverage), or "NONE"
        matrix_object = hic.getMatrixZoomData(
            HBB_LOCUS['chromosome'],
            HBB_LOCUS['chromosome'],
            "observed",
            "KR",  # Knight-Ruiz normalization (removes bias)
            "BP",
            HBB_LOCUS['resolution']
        )

        # Get records (sparse format)
        records = matrix_object.getRecords(
            HBB_LOCUS['start'],
            HBB_LOCUS['end'],
            HBB_LOCUS['start'],
            HBB_LOCUS['end']
        )

        print(f"✅ Extracted {len(records)} non-zero contacts\n")

        # Convert to dense matrix
        n_bins = (HBB_LOCUS['end'] - HBB_LOCUS['start']) // HBB_LOCUS['resolution']
        contact_matrix = np.zeros((n_bins, n_bins))

        for record in records:
            # Convert genomic position to bin index
            i = (record.binX - HBB_LOCUS['start']) // HBB_LOCUS['resolution']
            j = (record.binY - HBB_LOCUS['start']) // HBB_LOCUS['resolution']

            # Check bounds
            if 0 <= i < n_bins and 0 <= j < n_bins:
                contact_matrix[i, j] = record.counts
                contact_matrix[j, i] = record.counts  # Symmetric

        # Save matrix
        output_path = OUTPUT_DIR / "hudep2_wt_hic_hbb_locus.npy"
        np.save(output_path, contact_matrix)

        # Save metadata
        metadata = {
            'source': str(HIC_FILE.name),
            'locus': f"{HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}",
            'resolution': HBB_LOCUS['resolution'],
            'n_bins': n_bins,
            'normalization': 'KR',
            'non_zero_contacts': len(records),
        }

        metadata_path = OUTPUT_DIR / "hudep2_wt_hic_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print("═══════════════════════════════════════════")
        print("  Extraction Complete")
        print("═══════════════════════════════════════════\n")

        print(f"📊 Matrix shape: {contact_matrix.shape}")
        print(f"📊 Non-zero elements: {np.count_nonzero(contact_matrix)}")
        print(f"📊 Max contact: {np.max(contact_matrix):.2f}")
        print(f"📊 Mean contact: {np.mean(contact_matrix[contact_matrix > 0]):.2f}\n")

        print(f"💾 Saved to: {output_path}")
        print(f"💾 Metadata: {metadata_path}\n")

        print("Next step: Run ARCHCODE simulation")
        print("  npx tsx scripts/simulate_wt_hbb_validation.ts\n")

        return contact_matrix

    except Exception as e:
        print(f"\n❌ Error extracting Hi-C data: {e}")
        print("   Check .hic file format and chromosome naming")
        sys.exit(1)

if __name__ == "__main__":
    extract_contact_matrix()
