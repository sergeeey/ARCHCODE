#!/usr/bin/env python3
"""
Extract HBB and SOX2 regions from K562 Hi-C mcool file.

ПОЧЕМУ: ARCHCODE v1.0 Hi-C validation used GM12878 (r=0.16, not significant).
HBB is expressed in erythroid cells — K562 (erythroleukemia) is the correct cell line.
Extracting the HBB contact matrix from K562 Hi-C is the highest-impact action
for improving the weakest point of the paper.

Input:  data/reference/4DNFI18UHVRO.mcool (K562 Hi-C, 4DN)
Output: data/reference/HBB_K562_HiC_{res}bp.npy
        data/reference/HBB_K562_HiC_metadata.json
        data/reference/K562_CTCF_HBB.bed (filtered CTCF peaks)
        data/reference/K562_MED1_HBB.bed (filtered MED1 peaks)

Usage: python scripts/extract_k562_hbb.py [--locus 30kb|95kb]
"""

import sys
import json
import gzip
import argparse
from pathlib import Path

import numpy as np

try:
    import cooler
except ImportError:
    print("ERROR: cooler not installed. Run: pip install cooler")
    sys.exit(1)

from lib.locus_config import resolve_locus_path, load_locus_config, add_locus_argument

# === Parse arguments ===
_parser = argparse.ArgumentParser(description="Extract HBB region from K562 Hi-C mcool")
add_locus_argument(_parser)
_args = _parser.parse_args()

# === Load locus config ===
_config_path = resolve_locus_path(_args.locus)
LOCUS = load_locus_config(_config_path)

# ARCHCODE simulation window — from locus config
ARCHCODE_REGION = {
    "chrom": LOCUS["window"]["chromosome"],
    "start": LOCUS["window"]["start"],
    "end": LOCUS["window"]["end"],
    "resolution": LOCUS["window"]["resolution_bp"],
}

# Extended HBB locus for context (LCR through 3' HS)
# Always use a superset of the locus window
HBB_EXTENDED = {
    "chrom": "chr11",
    "start": min(5_200_000, ARCHCODE_REGION["start"] - 10_000),
    "end": max(5_260_000, ARCHCODE_REGION["end"] + 10_000),
}

# SOX2 region for future cross-locus validation (ADR-004)
SOX2_REGION = {
    "chrom": "chr3",
    "start": 181_500_000,
    "end": 181_850_000,
}

DATA_DIR = Path(__file__).parent.parent / "data" / "reference"
MCOOL_PATH = DATA_DIR / "4DNFI18UHVRO.mcool"


def list_resolutions(mcool_path: Path) -> list[int]:
    """List available resolutions in mcool file."""
    coolers = cooler.fileops.list_coolers(str(mcool_path))
    resolutions = []
    for uri in coolers:
        # URIs look like '/resolutions/1000'
        parts = uri.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "resolutions":
            resolutions.append(int(parts[1]))
    return sorted(resolutions)


def pick_best_resolution(available: list[int], target: int = 600) -> int:
    """Pick resolution closest to ARCHCODE bin size (600bp).

    ПОЧЕМУ 600bp: ARCHCODE simulates 30kb / 50 bins = 600bp.
    Hi-C typically has 1kb, 5kb, 10kb... resolutions.
    We want the finest available (likely 1000bp) for maximum spatial detail.
    """
    # Prefer the smallest resolution >= target, or the smallest available
    candidates = [r for r in available if r >= target]
    if candidates:
        return min(candidates)
    return min(available)


def extract_region(
    mcool_path: Path,
    resolution: int,
    chrom: str,
    start: int,
    end: int,
    label: str,
) -> tuple[np.ndarray, dict]:
    """Extract contact matrix for a genomic region.

    Returns (matrix, metadata) tuple.
    """
    uri = f"{mcool_path}::resolutions/{resolution}"
    print(f"\n  Opening {uri}")
    c = cooler.Cooler(uri)

    region_str = f"{chrom}:{start}-{end}"
    print(f"  Fetching {region_str} (balance=True, KR normalization)")

    # Fetch balanced (KR-normalized) matrix
    try:
        matrix = c.matrix(balance=True).fetch(region_str)
    except Exception as e:
        print(f"  WARNING: balanced fetch failed ({e}), trying raw counts")
        matrix = c.matrix(balance=False).fetch(region_str)

    matrix = np.array(matrix, dtype=np.float64)

    # Replace NaN with 0 (common in sparse Hi-C data at edges)
    nan_count = np.isnan(matrix).sum()
    if nan_count > 0:
        print(f"  Note: {nan_count} NaN values replaced with 0")
        matrix = np.nan_to_num(matrix, nan=0.0)

    # Basic QC
    n = matrix.shape[0]
    expected_bins = (end - start) // resolution
    non_zero = np.count_nonzero(matrix)
    total_elements = n * n

    # Check symmetry
    is_symmetric = np.allclose(matrix, matrix.T, atol=1e-10)

    metadata = {
        "label": label,
        "source": "4DNFI18UHVRO.mcool",
        "source_portal": "4DN Data Portal",
        "cell_line": "K562",
        "cell_type": "erythroleukemia (erythroid lineage)",
        "assay": "Hi-C",
        "genome_assembly": "hg38",
        "region": region_str,
        "chrom": chrom,
        "start": start,
        "end": end,
        "resolution_bp": resolution,
        "matrix_shape": list(matrix.shape),
        "expected_bins": expected_bins,
        "normalization": "KR (balanced)",
        "non_zero_elements": int(non_zero),
        "total_elements": int(total_elements),
        "sparsity": round(1.0 - non_zero / total_elements, 4),
        "is_symmetric": bool(is_symmetric),
        "nan_replaced": int(nan_count),
        "min_value": float(np.min(matrix)),
        "max_value": float(np.max(matrix)),
        "mean_nonzero": float(np.mean(matrix[matrix > 0])) if non_zero > 0 else 0.0,
    }

    print(f"  Matrix: {matrix.shape} ({non_zero}/{total_elements} non-zero)")
    print(f"  Range: [{metadata['min_value']:.6f}, {metadata['max_value']:.6f}]")
    print(f"  Symmetric: {is_symmetric}")

    return matrix, metadata


def filter_chipseq_peaks(
    bed_gz_path: Path, chrom: str, start: int, end: int, output_path: Path
) -> int:
    """Filter ChIP-seq peaks overlapping a genomic region.

    Returns number of peaks found.
    """
    if not bed_gz_path.exists():
        print(f"  SKIP: {bed_gz_path.name} not found (download with --chipseq)")
        return 0

    peaks = []
    with gzip.open(bed_gz_path, "rt") as f:
        for line in f:
            if line.startswith("#") or line.startswith("track"):
                continue
            fields = line.strip().split("\t")
            if len(fields) < 3:
                continue
            p_chrom = fields[0]
            p_start = int(fields[1])
            p_end = int(fields[2])
            # Check overlap
            if p_chrom == chrom and p_start < end and p_end > start:
                peaks.append(line.strip())

    with open(output_path, "w") as f:
        for peak in peaks:
            f.write(peak + "\n")

    return len(peaks)


def main():
    window_kb = (ARCHCODE_REGION["end"] - ARCHCODE_REGION["start"]) // 1000
    size_tag = f"_{window_kb}kb" if window_kb != 30 else ""

    print("=" * 60)
    print("  ARCHCODE: Extract K562 Hi-C — HBB Region")
    print("=" * 60)
    print(f"  Locus config: {LOCUS['id']} ({LOCUS['name']})")
    print(f"  Window: {ARCHCODE_REGION['chrom']}:{ARCHCODE_REGION['start']}-{ARCHCODE_REGION['end']} ({window_kb}kb)")

    if not MCOOL_PATH.exists():
        print(f"\nERROR: mcool file not found: {MCOOL_PATH}")
        print("Run first: bash scripts/download_k562_hic.sh --hic")
        sys.exit(1)

    file_size_gb = MCOOL_PATH.stat().st_size / 1e9
    print(f"\nInput: {MCOOL_PATH.name} ({file_size_gb:.2f} GB)")

    # Step 1: List resolutions
    print("\n--- Step 1: Available resolutions ---")
    resolutions = list_resolutions(MCOOL_PATH)
    print(f"  Found {len(resolutions)} resolutions: {resolutions}")

    best_res = pick_best_resolution(resolutions, target=ARCHCODE_REGION["resolution"])
    print(f"  Selected: {best_res}bp (closest to ARCHCODE {ARCHCODE_REGION['resolution']}bp)")

    # Step 2: Extract HBB region
    print("\n--- Step 2: Extract HBB locus ---")
    hbb_matrix, hbb_meta = extract_region(
        MCOOL_PATH,
        best_res,
        ARCHCODE_REGION["chrom"],
        ARCHCODE_REGION["start"],
        ARCHCODE_REGION["end"],
        label="HBB_ARCHCODE_window",
    )

    # Save HBB matrix (include window size for non-default configs)
    hbb_npy_path = DATA_DIR / f"HBB_K562_HiC{size_tag}_{best_res}bp.npy"
    np.save(hbb_npy_path, hbb_matrix)
    print(f"\n  Saved: {hbb_npy_path.name}")

    # Also extract extended HBB for context
    print("\n--- Step 2b: Extract extended HBB (60kb) ---")
    hbb_ext_matrix, hbb_ext_meta = extract_region(
        MCOOL_PATH,
        best_res,
        HBB_EXTENDED["chrom"],
        HBB_EXTENDED["start"],
        HBB_EXTENDED["end"],
        label="HBB_extended",
    )
    hbb_ext_npy = DATA_DIR / f"HBB_K562_HiC_extended_{best_res}bp.npy"
    np.save(hbb_ext_npy, hbb_ext_matrix)
    print(f"  Saved: {hbb_ext_npy.name}")

    # Step 3: Extract SOX2 region (for future cross-locus)
    print("\n--- Step 3: Extract SOX2 locus (future cross-locus) ---")
    try:
        sox2_matrix, sox2_meta = extract_region(
            MCOOL_PATH,
            best_res,
            SOX2_REGION["chrom"],
            SOX2_REGION["start"],
            SOX2_REGION["end"],
            label="SOX2_region",
        )
        sox2_npy = DATA_DIR / f"SOX2_K562_HiC_{best_res}bp.npy"
        np.save(sox2_npy, sox2_matrix)
        print(f"  Saved: {sox2_npy.name}")
    except Exception as e:
        print(f"  WARNING: SOX2 extraction failed: {e}")
        sox2_meta = {"error": str(e)}

    # Step 4: Filter ChIP-seq peaks for HBB
    print("\n--- Step 4: Filter ChIP-seq peaks (HBB region) ---")
    ctcf_gz = DATA_DIR / "K562_CTCF_peaks.bed.gz"
    med1_gz = DATA_DIR / "K562_MED1_peaks.bed.gz"

    n_ctcf = filter_chipseq_peaks(
        ctcf_gz,
        HBB_EXTENDED["chrom"],
        HBB_EXTENDED["start"],
        HBB_EXTENDED["end"],
        DATA_DIR / "K562_CTCF_HBB.bed",
    )
    print(f"  CTCF peaks in HBB region: {n_ctcf}")

    n_med1 = filter_chipseq_peaks(
        med1_gz,
        HBB_EXTENDED["chrom"],
        HBB_EXTENDED["start"],
        HBB_EXTENDED["end"],
        DATA_DIR / "K562_MED1_HBB.bed",
    )
    print(f"  MED1 peaks in HBB region: {n_med1}")

    # Step 5: Save combined metadata
    print("\n--- Step 5: Save metadata ---")
    all_metadata = {
        "extraction_tool": f"cooler {cooler.__version__}",
        "mcool_file": MCOOL_PATH.name,
        "mcool_size_gb": round(file_size_gb, 2),
        "available_resolutions": resolutions,
        "selected_resolution": best_res,
        "regions": {
            "hbb_archcode": hbb_meta,
            "hbb_extended": hbb_ext_meta,
            "sox2": sox2_meta,
        },
        "chipseq": {
            "ctcf_peaks_hbb": n_ctcf,
            "med1_peaks_hbb": n_med1,
        },
    }

    meta_path = DATA_DIR / "HBB_K562_HiC_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(all_metadata, f, indent=2)
    print(f"  Saved: {meta_path.name}")

    # Summary
    print("\n" + "=" * 60)
    print("  Extraction Complete")
    print("=" * 60)
    print(f"\n  HBB matrix:      {hbb_npy_path.name} ({hbb_matrix.shape})")
    print(f"  HBB extended:    {hbb_ext_npy.name} ({hbb_ext_matrix.shape})")
    print(f"  CTCF peaks:      {n_ctcf} in HBB region")
    print(f"  MED1 peaks:      {n_med1} in HBB region")
    print(f"  Metadata:        {meta_path.name}")
    print(f"\n  Next: python scripts/correlate_hic_archcode.py")


if __name__ == "__main__":
    main()
