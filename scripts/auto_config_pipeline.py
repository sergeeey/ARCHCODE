#!/usr/bin/env python3
"""
ARCHCODE Auto-Config Pipeline

Generates locus configuration JSON for any human gene using ENCODE API data.

Input: gene symbol + cell type (default K562)
Output: config/locus/<gene>_<size>kb.json

Steps:
  1. Get gene coordinates from Ensembl REST API
  2. Define window (gene center ± padding, default 150kb each side = 300kb)
  3. Query ENCODE for CTCF ChIP-seq narrowPeak (IDR preferred)
  4. Query ENCODE for H3K27ac ChIP-seq narrowPeak
  5. Download and parse BED files, extract peaks in window
  6. Get genes in window from Ensembl
  7. Generate config JSON

Usage:
  python scripts/auto_config_pipeline.py MYC
  python scripts/auto_config_pipeline.py MYC --cell-type HepG2 --padding 200000
  python scripts/auto_config_pipeline.py HBA1 --cell-type K562

Dependencies: requests
"""

import argparse
import json
import gzip
import io
import sys
import time
from pathlib import Path
from typing import Optional

import requests

PROJECT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT / "config" / "locus"

# ============================================================================
# Ensembl REST API
# ============================================================================

ENSEMBL_REST = "https://rest.ensembl.org"


def get_gene_info(symbol: str) -> dict:
    """Get gene coordinates from Ensembl."""
    url = f"{ENSEMBL_REST}/lookup/symbol/homo_sapiens/{symbol}"
    resp = requests.get(url, headers={"Content-Type": "application/json"}, timeout=30)
    if resp.status_code == 400:
        # Try case-insensitive search
        url2 = f"{ENSEMBL_REST}/lookup/symbol/homo_sapiens/{symbol.upper()}"
        resp = requests.get(url2, headers={"Content-Type": "application/json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {
        "symbol": data["display_name"],
        "ensembl_id": data["id"],
        "chromosome": f"chr{data['seq_region_name']}",
        "start": data["start"],
        "end": data["end"],
        "strand": "+" if data["strand"] == 1 else "-",
        "biotype": data["biotype"],
        "description": data.get("description", ""),
    }


def get_genes_in_region(chrom: str, start: int, end: int) -> list[dict]:
    """Get all protein-coding genes in a region from Ensembl."""
    region = f"{chrom.replace('chr', '')}:{start}-{end}"
    url = f"{ENSEMBL_REST}/overlap/region/homo_sapiens/{region}?feature=gene;content-type=application/json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    genes = []
    for g in resp.json():
        if g.get("biotype") == "protein_coding":
            name = g.get("external_name") or g.get("gene_id", g.get("id", "unknown"))
            genes.append({
                "name": name,
                "start": g["start"],
                "end": g["end"],
                "strand": "+" if g["strand"] == 1 else "-",
            })
    return sorted(genes, key=lambda g: g["start"])


# ============================================================================
# ENCODE API
# ============================================================================

ENCODE_API = "https://www.encodeproject.org"

# Known ENCODE file accessions for common cell types (verified, GRCh38)
# Format: {cell_type: {"ctcf": {"accession": ..., "href": ...}, "h3k27ac": {...}}}
KNOWN_ENCODE_FILES = {
    "K562": {
        "ctcf": {
            "accession": "ENCFF736NYC",
            "href": "/files/ENCFF736NYC/@@download/ENCFF736NYC.bed.gz",
            "output_type": "optimal IDR thresholded peaks",
            "experiment": "ENCSR000DWE",
        },
        "h3k27ac": {
            "accession": "ENCFF864OSZ",
            "href": "/files/ENCFF864OSZ/@@download/ENCFF864OSZ.bed.gz",
            "output_type": "replicated peaks",
            "experiment": "ENCSR000AKP",
        },
    },
    "HepG2": {
        "ctcf": {
            "accession": "ENCFF473IZV",
            "href": "/files/ENCFF473IZV/@@download/ENCFF473IZV.bed.gz",
            "output_type": "optimal IDR thresholded peaks",
            "experiment": "ENCSR000BMN",
        },
        "h3k27ac": {
            "accession": "ENCFF882PRP",
            "href": "/files/ENCFF882PRP/@@download/ENCFF882PRP.bed.gz",
            "output_type": "replicated peaks",
            "experiment": "ENCSR000AMO",
        },
    },
    "MCF-7": {
        "ctcf": {
            "accession": "ENCFF237QEK",
            "href": "/files/ENCFF237QEK/@@download/ENCFF237QEK.bed.gz",
            "output_type": "optimal IDR thresholded peaks",
            "experiment": "ENCSR000BNS",
        },
        "h3k27ac": {
            "accession": "ENCFF366PML",
            "href": "/files/ENCFF366PML/@@download/ENCFF366PML.bed.gz",
            "output_type": "replicated peaks",
            "experiment": "ENCSR000AOB",
        },
    },
}


def get_encode_files(cell_type: str, assembly: str = "GRCh38") -> dict:
    """Get CTCF and H3K27ac file info for a cell type.
    Uses cache for known cell types, falls back to ENCODE API search."""

    if cell_type in KNOWN_ENCODE_FILES:
        print(f"   Using cached ENCODE files for {cell_type}")
        return KNOWN_ENCODE_FILES[cell_type]

    # Fallback: search ENCODE API
    print(f"   Searching ENCODE API for {cell_type}...")
    result = {}

    for target, assay_key in [("CTCF", "ctcf"), ("H3K27ac", "h3k27ac")]:
        assay = "TF ChIP-seq" if target == "CTCF" else "Histone ChIP-seq"
        # Search for experiments
        params = {
            "type": "Experiment",
            "assay_title": assay,
            "target.label": target,
            "biosample_ontology.term_name": cell_type,
            "status": "released",
            "format": "json",
            "limit": 5,
        }
        try:
            resp = requests.get(
                f"{ENCODE_API}/search/",
                params=params,
                headers={"Accept": "application/json"},
                timeout=30,
            )
            if resp.status_code == 200:
                experiments = resp.json().get("@graph", [])
                if experiments:
                    exp_acc = experiments[0]["accession"]
                    # Get files from experiment
                    exp_resp = requests.get(
                        f"{ENCODE_API}/experiments/{exp_acc}/?format=json",
                        timeout=30,
                    )
                    if exp_resp.status_code == 200:
                        exp_data = exp_resp.json()
                        for f in exp_data.get("files", []):
                            if isinstance(f, str):
                                continue
                            if f.get("assembly") != assembly:
                                continue
                            if f.get("status") != "released":
                                continue
                            out = f.get("output_type", "")
                            if "peak" not in out.lower():
                                continue
                            result[assay_key] = {
                                "accession": f.get("accession", ""),
                                "href": f.get("href", ""),
                                "output_type": out,
                                "experiment": exp_acc,
                            }
                            break
        except Exception as e:
            print(f"   WARNING: ENCODE search failed for {target}: {e}")

    return result


# ============================================================================
# BED file parsing
# ============================================================================


def download_and_parse_bed(href: str, chrom: str, start: int, end: int) -> list[dict]:
    """Download a BED/narrowPeak file and extract peaks in region."""
    url = f"{ENCODE_API}{href}" if href.startswith("/") else href
    print(f"  Downloading: {url}")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    content = resp.content
    # Handle gzip
    if href.endswith(".gz") or content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)

    peaks = []
    for line in content.decode("utf-8", errors="replace").strip().split("\n"):
        if line.startswith("#") or line.startswith("track"):
            continue
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        p_chrom = fields[0]
        p_start = int(fields[1])
        p_end = int(fields[2])

        if p_chrom != chrom:
            continue
        if p_end < start or p_start > end:
            continue

        peak = {
            "chrom": p_chrom,
            "start": p_start,
            "end": p_end,
            "name": fields[3] if len(fields) > 3 else ".",
            "score": int(fields[4]) if len(fields) > 4 else 0,
            "strand": fields[5] if len(fields) > 5 else ".",
            "signal": float(fields[6]) if len(fields) > 6 else 0.0,
            "pvalue": float(fields[7]) if len(fields) > 7 else -1,
            "qvalue": float(fields[8]) if len(fields) > 8 else -1,
            "peak_offset": int(fields[9]) if len(fields) > 9 else -1,
        }
        peak["center"] = p_start + peak["peak_offset"] if peak["peak_offset"] >= 0 else (p_start + p_end) // 2
        peaks.append(peak)

    return sorted(peaks, key=lambda p: p["signal"], reverse=True)


# ============================================================================
# Config generation
# ============================================================================


def signal_to_occupancy(signal: float, max_signal: float) -> float:
    """Convert H3K27ac signal to occupancy [0.1, 0.95]."""
    if max_signal <= 0:
        return 0.3
    ratio = signal / max_signal
    return round(max(0.1, min(0.95, 0.1 + 0.85 * ratio)), 2)


def generate_config(
    gene_symbol: str,
    cell_type: str,
    padding: int,
    resolution_bp: int,
    assembly: str = "GRCh38",
    max_enhancers: int = 15,
    max_ctcf: int = 10,
) -> dict:
    """Generate a locus config for a gene."""

    print(f"\n{'='*60}")
    print(f"Generating config for {gene_symbol} ({cell_type})")
    print(f"{'='*60}")

    # Step 1: Gene info
    print(f"\n1. Getting gene info from Ensembl...")
    gene = get_gene_info(gene_symbol)
    print(f"   {gene['symbol']} ({gene['ensembl_id']}): {gene['chromosome']}:{gene['start']}-{gene['end']} ({gene['strand']})")

    # Step 2: Define window
    gene_center = (gene["start"] + gene["end"]) // 2
    win_start = gene_center - padding
    win_end = gene_center + padding
    window_size_kb = (win_end - win_start) // 1000
    n_bins = (win_end - win_start) // resolution_bp

    print(f"\n2. Window: {gene['chromosome']}:{win_start}-{win_end} ({window_size_kb}kb, {n_bins} bins @ {resolution_bp}bp)")

    # Step 3: Get genes in region
    print(f"\n3. Getting genes in region...")
    genes_in_region = get_genes_in_region(gene["chromosome"], win_start, win_end)
    print(f"   Found {len(genes_in_region)} protein-coding genes")
    for g in genes_in_region:
        print(f"   - {g['name']}: {g['start']}-{g['end']} ({g['strand']})")
    time.sleep(0.3)  # rate limit

    # Step 4-5: Get ENCODE CTCF + H3K27ac
    print(f"\n4. Getting ENCODE ChIP-seq data ({cell_type})...")
    encode_files = get_encode_files(cell_type, assembly)

    ctcf_file = encode_files.get("ctcf")
    h3k27ac_file = encode_files.get("h3k27ac")

    if not ctcf_file:
        print("   ERROR: No CTCF ChIP-seq found!")
        sys.exit(1)

    print(f"   CTCF: {ctcf_file['accession']} ({ctcf_file.get('output_type', '')})")
    ctcf_peaks = download_and_parse_bed(
        ctcf_file["href"], gene["chromosome"], win_start, win_end
    )
    print(f"   {len(ctcf_peaks)} CTCF peaks in region")
    time.sleep(0.3)

    if h3k27ac_file:
        print(f"   H3K27ac: {h3k27ac_file['accession']} ({h3k27ac_file.get('output_type', '')})")
        h3k27ac_peaks = download_and_parse_bed(
            h3k27ac_file["href"], gene["chromosome"], win_start, win_end
        )
        print(f"   {len(h3k27ac_peaks)} H3K27ac peaks in region")
    else:
        print("   WARNING: No H3K27ac ChIP-seq found! Using CTCF-only config.")
        h3k27ac_peaks = []

    # Step 6: Build config
    print(f"\n6. Building config...")

    # CTCF sites: top N by signal
    ctcf_sites = []
    for i, peak in enumerate(ctcf_peaks[:max_ctcf]):
        # Determine orientation from strand if available, otherwise alternate
        orientation = peak["strand"] if peak["strand"] in ["+", "-"] else ("+" if i % 2 == 0 else "-")
        ctcf_sites.append({
            "position": peak["center"],
            "orientation": orientation,
            "signal": round(peak["signal"], 1),
            "name": f"CTCF_{i+1}_{peak['name']}",
            "source": f"ENCODE_{cell_type}_CTCF",
            "encode_accession": ctcf_file.get("accession", ""),
            "note": f"Peak at {peak['start']}-{peak['end']}, signal={peak['signal']:.1f}, {peak.get('output_type', 'narrowPeak')}",
        })

    # Enhancers: top N H3K27ac peaks by signal
    enhancers = []
    if h3k27ac_peaks:
        max_sig = h3k27ac_peaks[0]["signal"]
        for peak in h3k27ac_peaks[:max_enhancers]:
            occ = signal_to_occupancy(peak["signal"], max_sig)
            enhancers.append({
                "position": peak["center"],
                "occupancy": occ,
                "name": f"H3K27ac_{peak['name']}",
                "source": f"ENCODE_{cell_type}_H3K27ac",
                "encode_accession": h3k27ac_file.get("accession", ""),
                "note": f"H3K27ac peak at {peak['start']}-{peak['end']}, signal={peak['signal']:.1f}",
            })

    # Genes
    config_genes = []
    for g in genes_in_region:
        config_genes.append({
            "name": g["name"],
            "start": g["start"],
            "end": g["end"],
            "strand": g["strand"],
        })

    config_id = f"{gene_symbol.lower()}_{window_size_kb}kb"
    config = {
        "id": config_id,
        "name": f"{gene_symbol} {window_size_kb}kb (ENCODE {cell_type} CTCF + H3K27ac)",
        "description": (
            f"{window_size_kb}kb window centered on {gene_symbol} "
            f"({gene['chromosome']}:{win_start}-{win_end}, {assembly}). "
            f"CTCF sites from ENCODE {cell_type} ChIP-seq "
            f"({ctcf_file.get('accession', 'N/A')}, {ctcf_file.get('output_type', 'narrowPeak')}). "
            f"Enhancers from ENCODE {cell_type} H3K27ac ChIP-seq "
            f"({h3k27ac_file.get('accession', 'N/A') if h3k27ac_file else 'N/A'}). "
            f"Auto-generated by auto_config_pipeline.py."
        ),
        "genome_assembly": assembly,
        "organism": "Homo sapiens",
        "cell_type": cell_type,
        "target_gene": gene_symbol,
        "window": {
            "chromosome": gene["chromosome"],
            "start": win_start,
            "end": win_end,
            "resolution_bp": resolution_bp,
            "n_bins": n_bins,
        },
        "features": {
            "enhancers": enhancers,
            "ctcf_sites": ctcf_sites,
            "genes": config_genes,
        },
        "thresholds": None,
        "_auto_generated": True,
        "_pipeline_version": "1.0",
        "_encode_ctcf_experiment": ctcf_file.get("dataset", ctcf_file.get("accession", "")),
        "_encode_h3k27ac_experiment": h3k27ac_file.get("dataset", h3k27ac_file.get("accession", "")) if h3k27ac_file else None,
    }

    # Save
    out_path = CONFIG_DIR / f"{config_id}.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n   Saved: {out_path}")
    print(f"   CTCF sites: {len(ctcf_sites)}")
    print(f"   Enhancers: {len(enhancers)}")
    print(f"   Genes: {len(config_genes)}")

    return config


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="ARCHCODE Auto-Config Pipeline")
    parser.add_argument("gene", help="Gene symbol (e.g., MYC, HBA1, FGFR3)")
    parser.add_argument("--cell-type", default="K562", help="ENCODE cell type (default: K562)")
    parser.add_argument("--padding", type=int, default=150000, help="Padding around gene center in bp (default: 150000)")
    parser.add_argument("--resolution", type=int, default=1000, help="Bin resolution in bp (default: 1000)")
    parser.add_argument("--assembly", default="GRCh38", help="Genome assembly (default: GRCh38)")
    parser.add_argument("--max-enhancers", type=int, default=15, help="Max enhancer peaks (default: 15)")
    parser.add_argument("--max-ctcf", type=int, default=10, help="Max CTCF sites (default: 10)")

    args = parser.parse_args()

    config = generate_config(
        gene_symbol=args.gene,
        cell_type=args.cell_type,
        padding=args.padding,
        resolution_bp=args.resolution,
        assembly=args.assembly,
        max_enhancers=args.max_enhancers,
        max_ctcf=args.max_ctcf,
    )

    print(f"\nConfig generated successfully: {config['id']}")
    print(f"Window: {config['window']['chromosome']}:{config['window']['start']}-{config['window']['end']}")


if __name__ == "__main__":
    main()
