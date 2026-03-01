#!/usr/bin/env python3
"""
Download Hi-C contact matrices for ARCHCODE loci via Juicer Tools streaming.

ПОЧЕМУ Juicer Tools (Java) а не hic-straw (Python):
hic-straw 1.3.1 требует C++ компиляцию (MSVC на Windows),
а pure-Python straw 0.0.6 не поддерживает .hic v9 (ENCODE).
Juicer Tools 2.20 работает через Java 17 и стримит данные
с S3 через HTTP range requests — не нужно скачивать 30 GB файлы.

Usage:
    python scripts/download_hic_regions.py --locus tp53
    python scripts/download_hic_regions.py --locus tp53 --resolution 5000
    python scripts/download_hic_regions.py --all
    python scripts/download_hic_regions.py --correlate tp53
"""

import argparse
import subprocess
import tempfile
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

# ============================================================================
# Hi-C source registry
# ============================================================================

HIC_SOURCES: dict[str, dict] = {
    "tp53": {
        "gene": "TP53",
        "cell_type": "K562",
        "url": "https://encode-public.s3.amazonaws.com/2022/05/15/e6fd8021-6548-4cf8-88bb-151103cb066e/ENCFF725EXS.hic",
        "experiment": "ENCSR479XDG",
        "chr_prefix": "chr",
        "assembly": "GRCh38",
        "source": "ENCODE_K562_intact_HiC",
    },
    "tp53_mcf7": {
        "gene": "TP53",
        "cell_type": "MCF7",
        "url": "https://encode-public.s3.amazonaws.com/2022/02/14/cad3402e-8bd5-4d22-b4b2-0b22cbb2aa09/ENCFF776XCM.hic",
        "experiment": "ENCSR660LPJ",
        "chr_prefix": "chr",
        "assembly": "GRCh38",
        "source": "ENCODE_MCF7_intact_HiC",
    },
    "brca1": {
        "gene": "BRCA1",
        "cell_type": "MCF7",
        "url": "https://encode-public.s3.amazonaws.com/2022/02/14/cad3402e-8bd5-4d22-b4b2-0b22cbb2aa09/ENCFF776XCM.hic",
        "experiment": "ENCSR660LPJ",
        "chr_prefix": "chr",
        "assembly": "GRCh38",
        "source": "ENCODE_MCF7_intact_HiC",
    },
    "mlh1": {
        "gene": "MLH1",
        "cell_type": "HCT116",
        "url": "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/c51bc383-04e0-40cf-a72f-589524efd8f7/4DNFIXB4O92R.hic",
        "experiment": "4DNESOE1RAS4",
        "chr_prefix": "",
        "assembly": "GRCh38",
        "source": "4DN_HCT116_HiC",
    },
    "ldlr": {
        "gene": "LDLR",
        "cell_type": "HepG2",
        "url": "https://encode-public.s3.amazonaws.com/2021/10/28/3736d9dc-38a6-48c6-9f4a-955b4a225b33/ENCFF020DPP.hic",
        "experiment": "ENCSR194SRI",
        "chr_prefix": "chr",
        "assembly": "GRCh38",
        "source": "ENCODE_HepG2_insitu_HiC",
    },
    "scn5a": {
        "gene": "SCN5A",
        "cell_type": "iPSC-CM",
        "url": "https://4dn-open-data-public.s3.amazonaws.com/fourfront-webprod/wfoutput/0c91cbc4-536e-4eb0-b33b-d4b50bee47df/4DNFIGN9FJ6R.hic",
        "experiment": "4DNESIQ6IPCO",
        "chr_prefix": "",
        "assembly": "GRCh38",
        "source": "4DN_iPSCCM_HiC",
    },
}

# ============================================================================
# Locus config loader
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
JUICER_JAR = PROJECT_ROOT / "tools" / "juicer_tools.jar"

LOCUS_ALIASES: dict[str, str] = {
    "30kb": "hbb_30kb_v2.json",
    "95kb": "hbb_95kb_subTAD.json",
    "cftr": "cftr_317kb.json",
    "tp53": "tp53_300kb.json",
}


def load_locus_config(locus: str) -> dict:
    """Load locus config JSON."""
    filename = LOCUS_ALIASES.get(locus, f"{locus}.json")
    config_path = PROJECT_ROOT / "config" / "locus" / filename
    if not config_path.exists():
        # Try with _300kb, _317kb suffixes
        for f in (PROJECT_ROOT / "config" / "locus").glob(f"{locus}*.json"):
            config_path = f
            break
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found for {locus}")
    with open(config_path) as f:
        return json.load(f)


# ============================================================================
# Juicer Tools wrapper
# ============================================================================

def juicer_dump(url: str, chr_name: str, resolution: int, normalization: str = "NONE") -> str:
    """Run juicer_tools dump and return output file path."""
    if not JUICER_JAR.exists():
        raise FileNotFoundError(
            f"Juicer Tools not found at {JUICER_JAR}. "
            f"Download: curl -L -o tools/juicer_tools.jar "
            f"https://github.com/aidenlab/Juicebox/releases/download/v2.20.00/juicer_tools.2.20.00.jar"
        )

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
        outpath = f.name

    cmd = [
        "java", "-jar", str(JUICER_JAR),
        "dump", "observed", normalization,
        url,
        chr_name, chr_name,
        "BP", str(resolution),
        outpath,
    ]

    print(f"  Running: juicer_tools dump {normalization} {chr_name} BP {resolution}")
    print(f"  URL: {url[:80]}...")

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=600
    )

    if result.returncode != 0:
        stderr = result.stderr
        if "Unknown chromosome" in stderr or "Invalid chromosome" in stderr:
            raise ValueError(f"Chromosome {chr_name} not found in .hic file")
        raise RuntimeError(f"Juicer dump failed (exit {result.returncode}): {stderr[:200]}")

    return outpath


def parse_sparse_to_matrix(
    filepath: str,
    window_start: int,
    window_end: int,
    resolution: int,
) -> np.ndarray:
    """Parse Juicer sparse output and extract region as dense matrix."""
    n_bins = (window_end - window_start) // resolution

    # ПОЧЕМУ фильтруем: juicer_tools dump без range выгружает всю хромосому.
    # Мы берём только записи в нашем окне и строим плотную матрицу.
    matrix = np.zeros((n_bins, n_bins), dtype=np.float64)

    total_records = 0
    in_window = 0

    with open(filepath) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue
            pos1, pos2, value = int(parts[0]), int(parts[1]), float(parts[2])
            total_records += 1

            if pos1 < window_start or pos1 >= window_end:
                continue
            if pos2 < window_start or pos2 >= window_end:
                continue

            i = (pos1 - window_start) // resolution
            j = (pos2 - window_start) // resolution

            if 0 <= i < n_bins and 0 <= j < n_bins:
                matrix[i, j] = value
                matrix[j, i] = value  # symmetric
                in_window += 1

    print(f"  Total records: {total_records:,}, in window: {in_window:,}")
    print(f"  Matrix: {n_bins}x{n_bins}, non-zero: {np.count_nonzero(matrix):,}")
    print(f"  Value range: {matrix.min():.1f} - {matrix.max():.1f}")

    return matrix


def vc_sqrt_normalize(matrix: np.ndarray) -> np.ndarray:
    """Apply VC_SQRT normalization (vanilla coverage square root)."""
    # ПОЧЕМУ VC_SQRT: KR нормализация не всегда доступна в .hic файлах.
    # VC_SQRT — стандартная альтернатива: делим каждый элемент на
    # sqrt(row_sum * col_sum). Устраняет coverage bias.
    row_sums = matrix.sum(axis=1)
    row_sums[row_sums == 0] = 1  # avoid division by zero
    sqrt_sums = np.sqrt(row_sums)

    norm = np.outer(sqrt_sums, sqrt_sums)
    norm[norm == 0] = 1

    return matrix / norm


# ============================================================================
# Main download function
# ============================================================================

def download_hic_region(
    locus: str,
    resolution: int | None = None,
    hic_source: str | None = None,
) -> Path:
    """Download Hi-C for a locus and save as numpy matrix."""
    config = load_locus_config(locus)
    window = config["window"]
    chr_num = window["chromosome"].replace("chr", "")
    w_start = window["start"]
    w_end = window["end"]

    if resolution is None:
        resolution = window.get("resolution_bp", 1000)

    # Select Hi-C source
    source_key = hic_source or locus
    if source_key not in HIC_SOURCES:
        # Try locus name as gene name (case-insensitive match)
        for k, v in HIC_SOURCES.items():
            if v["gene"].lower() == locus.lower():
                source_key = k
                break
        else:
            available = ", ".join(HIC_SOURCES.keys())
            raise ValueError(f"No Hi-C source for '{source_key}'. Available: {available}")

    source = HIC_SOURCES[source_key]
    gene = source["gene"]
    cell = source["cell_type"]
    url = source["url"]
    chr_prefix = source["chr_prefix"]
    chr_name = f"{chr_prefix}{chr_num}"

    output_dir = PROJECT_ROOT / "data" / "reference"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{gene}_{cell}_HiC_{resolution}bp.npy"
    meta_path = output_dir / f"{gene}_{cell}_HiC_{resolution}bp_meta.json"

    print(f"\n{'='*60}")
    print(f"Downloading Hi-C: {gene} from {cell}")
    print(f"{'='*60}")
    print(f"  Region: {window['chromosome']}:{w_start:,}-{w_end:,} ({(w_end-w_start)//1000}kb)")
    print(f"  Resolution: {resolution} bp")
    print(f"  Source: {source['source']} ({source['experiment']})")
    print(f"  Chromosome in .hic: {chr_name}")
    print()

    # Try KR first, fall back to NONE + VC_SQRT
    normalization = "KR"
    try:
        print(f"  Trying KR normalization...")
        dump_path = juicer_dump(url, chr_name, resolution, "KR")
        lines = sum(1 for _ in open(dump_path))
        if lines == 0:
            raise ValueError("KR returned empty output")
        print(f"  KR normalization: {lines:,} records")
        used_norm = "KR"
    except (ValueError, RuntimeError):
        print(f"  KR not available, using NONE + VC_SQRT normalization")
        dump_path = juicer_dump(url, chr_name, resolution, "NONE")
        lines = sum(1 for _ in open(dump_path))
        if lines == 0:
            raise RuntimeError(f"No data at resolution {resolution}bp for {chr_name}")
        print(f"  NONE normalization: {lines:,} records")
        used_norm = "NONE_VCSQRT"

    # Parse and extract region
    print(f"\n  Extracting window {w_start:,}-{w_end:,}...")
    matrix = parse_sparse_to_matrix(dump_path, w_start, w_end, resolution)

    if used_norm == "NONE_VCSQRT":
        print(f"  Applying VC_SQRT normalization...")
        matrix = vc_sqrt_normalize(matrix)

    # Clean up temp file
    Path(dump_path).unlink(missing_ok=True)

    # Save
    np.save(output_path, matrix)
    print(f"\n  Saved: {output_path}")
    print(f"  Shape: {matrix.shape}")

    # Save metadata
    meta = {
        "gene": gene,
        "cell_type": cell,
        "experiment": source["experiment"],
        "source": source["source"],
        "assembly": source["assembly"],
        "region": f"{window['chromosome']}:{w_start}-{w_end}",
        "resolution_bp": resolution,
        "matrix_shape": list(matrix.shape),
        "normalization": used_norm,
        "nonzero_fraction": float(np.count_nonzero(matrix)) / matrix.size,
        "value_range": [float(matrix.min()), float(matrix.max())],
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Metadata: {meta_path}")

    return output_path


# ============================================================================
# Correlation with ARCHCODE
# ============================================================================

def correlate_with_archcode(locus: str, resolution: int | None = None):
    """Compute Pearson r between Hi-C and ARCHCODE WT matrix."""
    from scipy import stats

    config = load_locus_config(locus)
    window = config["window"]
    if resolution is None:
        resolution = window.get("resolution_bp", 1000)

    source_key = locus
    if source_key not in HIC_SOURCES:
        print(f"No Hi-C source for {locus}")
        return

    source = HIC_SOURCES[source_key]
    gene = source["gene"]
    cell = source["cell_type"]

    hic_path = PROJECT_ROOT / "data" / "reference" / f"{gene}_{cell}_HiC_{resolution}bp.npy"
    if not hic_path.exists():
        print(f"Hi-C matrix not found: {hic_path}")
        print(f"Run: python scripts/download_hic_regions.py --locus {locus}")
        return

    hic = np.load(hic_path)
    n = hic.shape[0]

    # Build ARCHCODE WT contact matrix
    # ПОЧЕМУ дублируем: analytical formula из generate-unified-atlas.ts
    # C(i,j) = |i-j|^(-1) * sqrt(occ_i * occ_j) * Π(ctcf_perm)
    # Config already loaded above, use it directly

    features = config.get("features", {})
    enhancers = features.get("enhancers", [])
    ctcf_sites = features.get("ctcf_sites", [])
    w_start = window["start"]
    res = resolution

    # Occupancy landscape
    occ = np.full(n, 0.01)
    for enh in enhancers:
        bin_idx = (enh["position"] - w_start) // res
        if 0 <= bin_idx < n:
            occ[bin_idx] = max(occ[bin_idx], enh["occupancy"])

    # CTCF bins
    ctcf_bins = []
    for c in ctcf_sites:
        b = (c["position"] - w_start) // res
        if 0 <= b < n:
            ctcf_bins.append(b)

    # Build WT matrix
    alpha, gamma, k_base = 0.92, 0.80, 0.002
    archcode = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            dist = abs(i - j)
            if dist == 0:
                archcode[i, j] = 1.0
                archcode[j, i] = 1.0
                continue

            contact = (1.0 / dist) * np.sqrt(occ[i] * occ[j])

            # CTCF barrier
            perm = 1.0
            for cb in ctcf_bins:
                if cb > i and cb < j:
                    perm *= 0.15
            contact *= perm

            # Kramer kinetics
            avg_occ = (occ[i] + occ[j]) / 2.0
            p_unload = k_base * (1.0 - alpha * (avg_occ ** gamma))
            contact *= (1.0 - p_unload)

            archcode[i, j] = contact
            archcode[j, i] = contact

    # Correlate upper triangle (excluding diagonal)
    mask = np.triu_indices(n, k=1)
    hic_vals = hic[mask]
    arch_vals = archcode[mask]

    # Filter out zeros in both
    valid = (hic_vals > 0) & (arch_vals > 0)
    hic_valid = hic_vals[valid]
    arch_valid = arch_vals[valid]

    if len(hic_valid) < 10:
        print(f"Too few valid pairs: {len(hic_valid)}")
        return

    r, p = stats.pearsonr(hic_valid, arch_valid)

    print(f"\n{'='*60}")
    print(f"Hi-C vs ARCHCODE Correlation: {gene} ({cell})")
    print(f"{'='*60}")
    print(f"  Region: {window['chromosome']}:{w_start:,}-{window['end']:,}")
    print(f"  Resolution: {resolution} bp, Matrix: {n}x{n}")
    print(f"  Valid pairs: {len(hic_valid):,} / {len(hic_vals):,}")
    print(f"  Pearson r = {r:.4f}")
    print(f"  p-value   = {p:.2e}")
    print()

    # Save result
    result = {
        "gene": gene,
        "cell_type": cell,
        "region": f"{window['chromosome']}:{w_start}-{window['end']}",
        "resolution_bp": resolution,
        "pearson_r": float(r),
        "p_value": float(p),
        "n_valid_pairs": int(len(hic_valid)),
        "n_total_pairs": int(len(hic_vals)),
    }
    result_path = PROJECT_ROOT / "results" / f"hic_correlation_{locus}.json"
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Result saved: {result_path}")

    return r, p


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Download Hi-C regions for ARCHCODE loci")
    parser.add_argument("--locus", help="Locus to download (e.g., tp53, mlh1)")
    parser.add_argument("--resolution", type=int, help="Resolution in bp (default: from config)")
    parser.add_argument("--all", action="store_true", help="Download all available loci")
    parser.add_argument("--correlate", help="Compute correlation for a locus")
    parser.add_argument("--list", action="store_true", help="List available Hi-C sources")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable Hi-C sources:")
        print(f"{'Key':<15} {'Gene':<8} {'Cell':<10} {'Source':<30} {'Experiment'}")
        print("-" * 80)
        for key, src in HIC_SOURCES.items():
            print(f"{key:<15} {src['gene']:<8} {src['cell_type']:<10} {src['source']:<30} {src['experiment']}")
        return

    if args.correlate:
        correlate_with_archcode(args.correlate, args.resolution)
        return

    if args.all:
        for locus_key in HIC_SOURCES:
            # Skip aliases (tp53_mcf7 shares URL with brca1)
            if "_" in locus_key:
                continue
            try:
                download_hic_region(locus_key, args.resolution)
            except Exception as e:
                print(f"  ERROR: {e}")
        return

    if args.locus:
        download_hic_region(args.locus, args.resolution)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
