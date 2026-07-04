#!/usr/bin/env python3
"""
FOXP3 In Silico Saturation Mutagenesis — SYNTHETIC VARIANTS

Generates synthetic SNVs across the FOXP3 60kb regulatory window to predict
which positions are structurally sensitive to mutation via ARCHCODE.

ALL VARIANTS ARE SYNTHETIC — NOT FROM CLINVAR.
Output file is prefixed SYNTHETIC_ per project integrity protocol.

Regions:
  - Enhancer peaks (H3K27ac Treg): every 50bp within peak boundaries
  - CTCF sites (Tconv): every 50bp within peak boundaries
  - Background: every 200bp across remaining 60kb window

Data sources:
  H3K27ac: GSM9177365 (Human Treg rest, Donor 1) — GSE286472
  CTCF:    GSM9161596 (Human Tconv rest, Donor 1) — GSE305063
  Paper:   Umhoefer et al., Immunity 59(1):129-144, 2026
  DOI:     10.1016/j.immuni.2025.10.020
"""

import csv
import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT / "config" / "locus" / "foxp3_treg_60kb_hires.json"
OUTPUT_PATH = PROJECT / "data" / "SYNTHETIC_foxp3_enhancer_mutagenesis.csv"

WIN_START = 49235000
WIN_END = 49295000

# Enhancer peak boundaries (from Treg H3K27ac BED file)
ENHANCER_PEAKS = [
    {"name": "H3K27ac_peak_33965", "start": 49235416, "end": 49235850, "signal": 469},
    {"name": "H3K27ac_peak_33970", "start": 49259433, "end": 49260161, "signal": 266},
    {"name": "H3K27ac_peak_33972", "start": 49260861, "end": 49261907, "signal": 358},
    {"name": "H3K27ac_peak_33973", "start": 49262058, "end": 49267604, "signal": 357},
    {"name": "H3K27ac_peak_33974", "start": 49268681, "end": 49269113, "signal": 212},
    {"name": "H3K27ac_peak_33975", "start": 49269288, "end": 49270838, "signal": 1965},
    {"name": "H3K27ac_peak_33977", "start": 49271456, "end": 49280515, "signal": 2294},
]

# CTCF peak boundaries (from Tconv CTCF BED file)
CTCF_PEAKS = [
    {"name": "CTCF_peak_57780", "start": 49273177, "end": 49273723, "signal": 972},
    {"name": "CTCF_peak_57781", "start": 49291670, "end": 49292376, "signal": 2595},
]

# FOXP3 gene boundaries (for annotation)
FOXP3_GENE = {"start": 49250436, "end": 49264800}


def classify_position(pos: int) -> tuple[str, str]:
    """Classify a genomic position into region type and annotation."""
    for peak in CTCF_PEAKS:
        if peak["start"] <= pos <= peak["end"]:
            return "ctcf_site", peak["name"]
    for peak in ENHANCER_PEAKS:
        if peak["start"] <= pos <= peak["end"]:
            return "enhancer", peak["name"]
    if FOXP3_GENE["start"] <= pos <= FOXP3_GENE["end"]:
        return "gene_body", "FOXP3"
    return "intergenic", "background"


def main():
    # Load config to verify window
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    assert config["window"]["start"] == WIN_START
    assert config["window"]["end"] == WIN_END

    variants: list[dict] = []
    variant_id = 0

    # 1. Dense sampling in enhancer peaks (every 50bp)
    for peak in ENHANCER_PEAKS:
        pos = peak["start"]
        while pos <= peak["end"]:
            variant_id += 1
            region, annotation = classify_position(pos)
            variants.append(
                {
                    "clinvar_id": f"SYNTH_ENH_{variant_id:04d}",
                    "chr": "X",
                    "position": pos,
                    "ref": "A",
                    "alt": "G",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chrX:g.{pos}A>G",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Pathogenic",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
            pos += 50

    # 2. Dense sampling in CTCF peaks (every 50bp)
    for peak in CTCF_PEAKS:
        pos = peak["start"]
        while pos <= peak["end"]:
            variant_id += 1
            region, annotation = classify_position(pos)
            variants.append(
                {
                    "clinvar_id": f"SYNTH_CTCF_{variant_id:04d}",
                    "chr": "X",
                    "position": pos,
                    "ref": "C",
                    "alt": "T",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chrX:g.{pos}C>T",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Pathogenic",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
            pos += 50

    # 3. Background sampling (every 500bp across entire window, excluding peaks)
    pos = WIN_START
    while pos <= WIN_END:
        region, annotation = classify_position(pos)
        if region == "intergenic" or region == "gene_body":
            variant_id += 1
            variants.append(
                {
                    "clinvar_id": f"SYNTH_BG_{variant_id:04d}",
                    "chr": "X",
                    "position": pos,
                    "ref": "G",
                    "alt": "A",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chrX:g.{pos}G>A",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Benign",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
        pos += 500

    # Sort by position
    variants.sort(key=lambda v: v["position"])

    # Write CSV (compatible with generic locus loader, minus extra columns)
    fieldnames = [
        "clinvar_id",
        "chr",
        "position",
        "ref",
        "alt",
        "category",
        "hgvs_c",
        "hgvs_p",
        "clinical_significance",
        "label",
        "region_type",
        "region_annotation",
        "data_type",
    ]
    with open(OUTPUT_PATH, "w", newline="") as f:
        # WHY: Header comment for synthetic data watermark
        f.write("# SYNTHETIC BASELINE — NOT REAL CLINVAR DATA\n")
        f.write(
            "# Generated by foxp3_in_silico_mutagenesis.py for ARCHCODE structural sensitivity mapping\n"
        )
        f.write(f"# Source: Umhoefer et al., Immunity 2026, DOI:10.1016/j.immuni.2025.10.020\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants)

    # Summary
    from collections import Counter

    regions = Counter(v["region_type"] for v in variants)
    labels = Counter(v["label"] for v in variants)
    print(f"Generated {len(variants)} synthetic variants → {OUTPUT_PATH}")
    print(f"  By region: {dict(regions)}")
    print(f"  By label:  {dict(labels)}")
    print(f"  Enhancer SNVs: {sum(1 for v in variants if v['region_type'] == 'enhancer')}")
    print(f"  CTCF SNVs:     {sum(1 for v in variants if v['region_type'] == 'ctcf_site')}")
    print(
        f"  Background:    {sum(1 for v in variants if v['region_type'] in ('intergenic', 'gene_body'))}"
    )


if __name__ == "__main__":
    main()
