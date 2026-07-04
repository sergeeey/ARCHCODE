#!/usr/bin/env python3
"""
Build FOXP3 Treg-matched locus config from Marson lab GEO data.

H3K27ac: GSM9177365 (Human Treg rest, Donor 1) — GSE286472
CTCF:    GSM9161596 (Human Tconv rest, Donor 1) — GSE305063

Paper: Umhoefer et al., Immunity 59(1):129-144, 2026
DOI: 10.1016/j.immuni.2025.10.020
"""

import gzip
import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT / "config" / "locus"

# FOXP3 window (same as K562 baseline for comparability)
CHROM = "chrX"
WIN_START = 49107618
WIN_END = 49407618
RESOLUTION = 1000
N_BINS = (WIN_END - WIN_START) // RESOLUTION  # 300

MAX_ENHANCERS = 15
MAX_CTCF = 10


def parse_bed_region(bed_gz_path: Path, chrom: str, start: int, end: int) -> list[dict]:
    """Parse gzipped BED file, extract peaks in region, sort by signal (col5) desc."""
    peaks = []
    with gzip.open(bed_gz_path, "rt") as f:
        for line in f:
            fields = line.strip().split("\t")
            if len(fields) < 5:
                continue
            p_chrom = fields[0]
            p_start = int(fields[1])
            p_end = int(fields[2])
            p_name = fields[3]
            p_signal = int(fields[4])

            if p_chrom != chrom or p_end < start or p_start > end:
                continue

            peaks.append(
                {
                    "chrom": p_chrom,
                    "start": p_start,
                    "end": p_end,
                    "name": p_name,
                    "signal": p_signal,
                    "center": (p_start + p_end) // 2,
                }
            )

    return sorted(peaks, key=lambda p: p["signal"], reverse=True)


def signal_to_occupancy(signal: float, max_signal: float) -> float:
    """Convert signal to occupancy [0.1, 0.95]."""
    if max_signal <= 0:
        return 0.3
    ratio = signal / max_signal
    return round(max(0.1, min(0.95, 0.1 + 0.85 * ratio)), 2)


def main():
    h3k27ac_path = PROJECT / "data" / "treg" / "GSM9177365_H3K27ac_Treg_rest.bed.gz"
    ctcf_path = PROJECT / "data" / "treg" / "GSM9161596_CTCF_Tconv_rest.bed.gz"

    print("Parsing H3K27ac peaks (Treg rest, Donor 1)...")
    h3k27ac_peaks = parse_bed_region(h3k27ac_path, CHROM, WIN_START, WIN_END)
    print(f"  {len(h3k27ac_peaks)} peaks in FOXP3 window")

    print("Parsing CTCF peaks (Tconv rest, Donor 1)...")
    ctcf_peaks = parse_bed_region(ctcf_path, CHROM, WIN_START, WIN_END)
    print(f"  {len(ctcf_peaks)} peaks in FOXP3 window")

    # Build enhancers (top N by signal)
    enhancers = []
    if h3k27ac_peaks:
        max_sig = h3k27ac_peaks[0]["signal"]
        for peak in h3k27ac_peaks[:MAX_ENHANCERS]:
            occ = signal_to_occupancy(peak["signal"], max_sig)
            enhancers.append(
                {
                    "position": peak["center"],
                    "occupancy": occ,
                    "name": f"H3K27ac_Treg_{peak['name']}",
                    "source": "GEO_GSM9177365_Treg_H3K27ac",
                    "note": (
                        f"H3K27ac peak at {peak['start']}-{peak['end']}, "
                        f"signal={peak['signal']}. "
                        f"Umhoefer et al. Immunity 2026, DOI:10.1016/j.immuni.2025.10.020"
                    ),
                }
            )

    # Build CTCF sites (top N by signal)
    ctcf_sites = []
    for i, peak in enumerate(ctcf_peaks[:MAX_CTCF]):
        # WHY: BED files from this dataset don't have strand info (col6 = "."),
        # so we use "unknown" orientation. ARCHCODE handles this with default barrier logic.
        ctcf_sites.append(
            {
                "position": peak["center"],
                "orientation": "unknown",
                "signal": peak["signal"],
                "name": f"CTCF_Tconv_{peak['name']}",
                "source": "GEO_GSM9161596_Tconv_CTCF",
                "note": (
                    f"Peak at {peak['start']}-{peak['end']}, signal={peak['signal']}. "
                    f"Umhoefer et al. Immunity 2026, DOI:10.1016/j.immuni.2025.10.020"
                ),
            }
        )

    # Reuse genes from K562 config (same window)
    k562_config_path = CONFIG_DIR / "foxp3_300kb.json"
    with open(k562_config_path) as f:
        k562_config = json.load(f)
    genes = k562_config["features"]["genes"]

    config = {
        "id": "foxp3_treg_300kb",
        "name": "FOXP3 300kb (Treg H3K27ac + Tconv CTCF, Marson lab 2026)",
        "description": (
            "300kb window centered on FOXP3 (chrX:49107618-49407618, GRCh38). "
            "CTCF sites from human resting Tconv ChIP-seq (GSM9161596, Donor 1, MACS3 peaks). "
            "Enhancers from human resting Treg H3K27ac ChIP-seq (GSM9177365, Donor 1, MACS3 peaks). "
            "Data from Umhoefer et al., Immunity 59(1):129-144, 2026. "
            "DOI: 10.1016/j.immuni.2025.10.020. "
            "GEO SuperSeries: GSE286473."
        ),
        "genome_assembly": "GRCh38",
        "organism": "Homo sapiens",
        "cell_type": "Treg (H3K27ac) + Tconv (CTCF)",
        "target_gene": "FOXP3",
        "window": {
            "chromosome": CHROM,
            "start": WIN_START,
            "end": WIN_END,
            "resolution_bp": RESOLUTION,
            "n_bins": N_BINS,
        },
        "features": {
            "enhancers": enhancers,
            "ctcf_sites": ctcf_sites,
            "genes": genes,
        },
        "thresholds": None,
        "_data_sources": {
            "h3k27ac": {
                "geo_accession": "GSM9177365",
                "series": "GSE286472",
                "cell_type": "Human Treg rest, Donor 1",
                "peak_caller": "MACS3",
            },
            "ctcf": {
                "geo_accession": "GSM9161596",
                "series": "GSE305063",
                "cell_type": "Human Tconv rest, Donor 1",
                "peak_caller": "MACS3",
            },
            "paper": {
                "authors": "Umhoefer JM et al.",
                "title": "FOXP3 expression depends on cell-type-specific cis-regulatory elements",
                "journal": "Immunity",
                "year": 2026,
                "doi": "10.1016/j.immuni.2025.10.020",
                "pmid": "41237776",
            },
        },
    }

    out_path = CONFIG_DIR / "foxp3_treg_300kb.json"
    with open(out_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\nSaved: {out_path}")
    print(f"  CTCF sites: {len(ctcf_sites)}")
    print(f"  Enhancers: {len(enhancers)}")
    print(f"  Genes: {len(genes)}")


if __name__ == "__main__":
    main()
