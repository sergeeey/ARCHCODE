#!/usr/bin/env python3
"""
Extract HBB Locus from HUDEP2 Hi-C Data (Ground Truth)
Using hictkpy library (alternative to hic-straw)

Input: GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic
Output: data/hudep2_wt_hic_hbb_locus.npy (contact matrix)

Region: chr11:5,200,000-5,250,000 (50 KB window around HBB)
Resolution: Auto-detect closest available

Usage: python scripts/extract_hic_hbb_locus_hictk.py
"""

import numpy as np
import sys
import json
from pathlib import Path

# Check if hictkpy is installed
try:
    import hictkpy
    print("✅ hictkpy found")
except ImportError:
    print("❌ hictkpy not installed")
    print("   Install: pip install hictkpy")
    sys.exit(1)

# HBB locus parameters
HBB_LOCUS = {
    'chromosome': 'chr11',
    'start': 5200000,
    'end': 5250000,
    'target_resolution': 5000,  # 5 KB bins (target, will use closest available)
}

# Input file (updated path)
HIC_FILE = Path("D:/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic")

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_contact_matrix():
    """Extract HBB locus contact matrix from .hic file using hictkpy"""

    print("═══════════════════════════════════════════")
    print("  Extract Hi-C Ground Truth (HUDEP2 WT)")
    print("  Library: hictkpy (hictk Python bindings)")
    print("═══════════════════════════════════════════\n")

    print(f"📁 Input: {HIC_FILE}")
    print(f"   Size: {HIC_FILE.stat().st_size / 1e9:.2f} GB")
    print(f"📍 Locus: {HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}")
    print(f"📏 Target Resolution: {HBB_LOCUS['target_resolution']} bp\n")

    # Check if file exists
    if not HIC_FILE.exists():
        print(f"❌ Error: File not found: {HIC_FILE}")
        print("   Check path and try again.")
        sys.exit(1)

    print("🔄 Loading .hic file...")

    try:
        # Open .hic file with hictkpy
        hic = hictkpy.File(str(HIC_FILE))

        # Get available resolutions
        resolutions = hic.resolutions()
        print(f"✅ Available resolutions: {resolutions}")

        # Get chromosomes
        chromosomes = hic.chromosomes()
        chr_names = [chrom.name for chrom in chromosomes]
        print(f"✅ Available chromosomes: {chr_names[:10]}...")  # Show first 10

        # Check if our chromosome exists
        if HBB_LOCUS['chromosome'] not in chr_names:
            print(f"⚠️  Chromosome {HBB_LOCUS['chromosome']} not found")
            # Try without 'chr' prefix
            alt_name = HBB_LOCUS['chromosome'].replace('chr', '')
            if alt_name in chr_names:
                print(f"   Using: {alt_name} instead")
                HBB_LOCUS['chromosome'] = alt_name
            else:
                print(f"❌ Error: Chromosome not found in file")
                sys.exit(1)

        # Find closest resolution
        closest_resolution = min(resolutions, key=lambda x: abs(x - HBB_LOCUS['target_resolution']))
        actual_resolution = closest_resolution

        if actual_resolution != HBB_LOCUS['target_resolution']:
            print(f"⚠️  Target resolution {HBB_LOCUS['target_resolution']} not available")
            print(f"   Using closest: {actual_resolution} bp")
        else:
            print(f"✅ Using resolution: {actual_resolution} bp")

        # Fetch matrix data
        print(f"\n🔄 Extracting contacts...")
        print(f"   Region: {HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}")
        print(f"   Resolution: {actual_resolution} bp")

        # Get selector for the region
        selector = hic.fetch(
            HBB_LOCUS['chromosome'],
            HBB_LOCUS['start'],
            HBB_LOCUS['end'],
            resolution=actual_resolution,
            normalization='KR'  # Knight-Ruiz balanced (removes biases)
        )

        # Convert to dense matrix
        n_bins = (HBB_LOCUS['end'] - HBB_LOCUS['start']) // actual_resolution
        contact_matrix = np.zeros((n_bins, n_bins), dtype=np.float64)

        # Fill matrix with contacts
        record_count = 0
        for pixel in selector:
            # pixel is (bin1, bin2, count)
            # Convert genomic bins to matrix indices
            i = (pixel.bin1_id * actual_resolution - HBB_LOCUS['start']) // actual_resolution
            j = (pixel.bin2_id * actual_resolution - HBB_LOCUS['start']) // actual_resolution

            # Check bounds
            if 0 <= i < n_bins and 0 <= j < n_bins:
                contact_matrix[i, j] = pixel.count
                if i != j:  # Make symmetric
                    contact_matrix[j, i] = pixel.count
                record_count += 1

        print(f"✅ Extracted {record_count} records\n")

        # Calculate statistics
        non_zero_count = np.count_nonzero(contact_matrix)
        max_contact = np.max(contact_matrix)
        min_contact = np.min(contact_matrix[contact_matrix > 0]) if non_zero_count > 0 else 0
        mean_contact = np.mean(contact_matrix[contact_matrix > 0]) if non_zero_count > 0 else 0

        # Save matrix
        output_path = OUTPUT_DIR / "hudep2_wt_hic_hbb_locus.npy"
        np.save(output_path, contact_matrix)

        # Save metadata
        metadata = {
            'source_file': str(HIC_FILE.name),
            'source_size_gb': HIC_FILE.stat().st_size / 1e9,
            'locus': f"{HBB_LOCUS['chromosome']}:{HBB_LOCUS['start']}-{HBB_LOCUS['end']}",
            'target_resolution': HBB_LOCUS['target_resolution'],
            'actual_resolution': int(actual_resolution),
            'n_bins': int(n_bins),
            'matrix_shape': list(contact_matrix.shape),
            'normalization': 'KR',
            'records_extracted': int(record_count),
            'non_zero_elements': int(non_zero_count),
            'min_contact': float(min_contact),
            'max_contact': float(max_contact),
            'mean_contact': float(mean_contact),
            'library': 'hictkpy',
        }

        metadata_path = OUTPUT_DIR / "hudep2_wt_hic_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print("═══════════════════════════════════════════")
        print("  Extraction Complete")
        print("═══════════════════════════════════════════\n")

        print("📊 FACTUAL MEASUREMENTS (no interpretation):")
        print(f"   Matrix shape: {contact_matrix.shape}")
        print(f"   Non-zero elements: {non_zero_count}")
        print(f"   Min contact (non-zero): {min_contact:.6f}")
        print(f"   Max contact: {max_contact:.6f}")
        print(f"   Mean contact (non-zero): {mean_contact:.6f}")
        print(f"   Total sum: {np.sum(contact_matrix):.2f}\n")

        print(f"💾 Saved to: {output_path.absolute()}")
        print(f"💾 Metadata: {metadata_path.absolute()}\n")

        print("✅ Ground truth data extraction complete")
        print("   No synthetic data generated")
        print("   All values are factual measurements\n")

        return contact_matrix, metadata

    except Exception as e:
        print(f"\n❌ Error extracting Hi-C data:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        print("\nStack trace:")
        traceback.print_exc()
        print("\n⚠️  No workaround applied - reporting factual error")
        sys.exit(1)

if __name__ == "__main__":
    matrix, metadata = extract_contact_matrix()
