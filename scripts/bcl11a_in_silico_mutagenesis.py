#!/usr/bin/env python3
"""
BCL11A In Silico Saturation Mutagenesis — SYNTHETIC VARIANTS

Generates synthetic SNVs across the BCL11A erythroid enhancer complex
(DHS +55/+58/+62) to predict structural vulnerability hotspots.

The DHS +58 site is the Casgevy (exagamglogene autotemcel) CRISPR target.
If ARCHCODE identifies this site as a structural hotspot, it validates
the method's ability to predict gene therapy targets.

ALL VARIANTS ARE SYNTHETIC — NOT FROM CLINVAR.

Data sources:
  Enhancer positions: Bauer et al., Science 2013; Canver et al., Nature 2015
  CTCF: ENCODE K562 (ENCFF736NYC)
  Casgevy: FDA approval 2023, Application 761163
"""

import csv
import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT / "config" / "locus" / "bcl11a_erythroid_95kb.json"
OUTPUT_PATH = PROJECT / "data" / "SYNTHETIC_bcl11a_erythroid_mutagenesis.csv"

# BCL11A gene and enhancer coordinates (hg38)
BCL11A_TSS = 60554467  # minus strand
BCL11A_GENE = {"start": 60450520, "end": 60554467}
WIN_START = 60455000
WIN_END = 60555000

# DHS enhancer regions (estimated from TSS distance, ±500bp)
# VERIFIED coordinates from Bauer 2013, Canver 2015, Frangoul 2021
DHS_REGIONS = [
    {"name": "DHS_h55", "center": 60498362, "start": 60498101, "end": 60498623, "occupancy": 0.7},
    {
        "name": "DHS_h58_CASGEVY",
        "center": 60495193,
        "start": 60495079,
        "end": 60495691,
        "occupancy": 0.95,
        # Casgevy sgRNA target: chr2:60495263-60495283 (GATA1 motif at 60495264-60495269)
    },
    {"name": "DHS_h62", "center": 60491066, "start": 60490852, "end": 60491280, "occupancy": 0.6},
]

# CTCF sites from ENCODE K562
CTCF_SITES = [
    {"name": "CTCF_1", "start": 60458500, "end": 60459200},
    {"name": "CTCF_2", "start": 60480600, "end": 60481400},
    {"name": "CTCF_3", "start": 60530700, "end": 60531400},
    {"name": "CTCF_4", "start": 60540500, "end": 60541200},
]

# Promoter region
PROMOTER = {"name": "BCL11A_promoter", "start": 60553500, "end": 60555000}


def classify_position(pos: int) -> tuple[str, str]:
    for dhs in DHS_REGIONS:
        if dhs["start"] <= pos <= dhs["end"]:
            return "enhancer", dhs["name"]
    for ctcf in CTCF_SITES:
        if ctcf["start"] <= pos <= ctcf["end"]:
            return "ctcf_site", ctcf["name"]
    if PROMOTER["start"] <= pos <= PROMOTER["end"]:
        return "promoter", PROMOTER["name"]
    return "intergenic", "background"


def main():
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    variants: list[dict] = []
    vid = 0

    # 1. Dense sampling in DHS enhancer regions (every 50bp)
    for dhs in DHS_REGIONS:
        pos = dhs["start"]
        while pos <= dhs["end"]:
            vid += 1
            region, annotation = classify_position(pos)
            variants.append(
                {
                    "clinvar_id": f"SYNTH_DHS_{vid:04d}",
                    "chr": "2",
                    "position": pos,
                    "ref": "A",
                    "alt": "G",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chr2:g.{pos}A>G",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Pathogenic",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
            pos += 50

    # 2. Dense sampling in CTCF sites (every 50bp)
    for ctcf in CTCF_SITES:
        pos = ctcf["start"]
        while pos <= ctcf["end"]:
            vid += 1
            region, annotation = classify_position(pos)
            variants.append(
                {
                    "clinvar_id": f"SYNTH_CTCF_{vid:04d}",
                    "chr": "2",
                    "position": pos,
                    "ref": "C",
                    "alt": "T",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chr2:g.{pos}C>T",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Pathogenic",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
            pos += 50

    # 3. Promoter region (every 50bp)
    pos = PROMOTER["start"]
    while pos <= PROMOTER["end"]:
        vid += 1
        region, annotation = classify_position(pos)
        variants.append(
            {
                "clinvar_id": f"SYNTH_PROM_{vid:04d}",
                "chr": "2",
                "position": pos,
                "ref": "G",
                "alt": "A",
                "category": "other",
                "hgvs_c": f"SYNTHETIC:chr2:g.{pos}G>A",
                "hgvs_p": "",
                "clinical_significance": "SYNTHETIC",
                "label": "Pathogenic",
                "region_type": region,
                "region_annotation": annotation,
                "data_type": "SYNTHETIC",
            }
        )
        pos += 50

    # 4. Background (every 500bp, excluding peaks)
    pos = WIN_START
    while pos <= WIN_END:
        region, annotation = classify_position(pos)
        if region == "intergenic":
            vid += 1
            variants.append(
                {
                    "clinvar_id": f"SYNTH_BG_{vid:04d}",
                    "chr": "2",
                    "position": pos,
                    "ref": "T",
                    "alt": "C",
                    "category": "other",
                    "hgvs_c": f"SYNTHETIC:chr2:g.{pos}T>C",
                    "hgvs_p": "",
                    "clinical_significance": "SYNTHETIC",
                    "label": "Benign",
                    "region_type": region,
                    "region_annotation": annotation,
                    "data_type": "SYNTHETIC",
                }
            )
        pos += 500

    variants.sort(key=lambda v: v["position"])

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
        f.write("# SYNTHETIC BASELINE — NOT REAL CLINVAR DATA\n")
        f.write("# BCL11A erythroid enhancer in silico mutagenesis\n")
        f.write("# DHS +58 = Casgevy CRISPR target (Vertex/CRISPR Therapeutics)\n")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants)

    from collections import Counter

    regions = Counter(v["region_type"] for v in variants)
    print(f"Generated {len(variants)} synthetic variants → {OUTPUT_PATH}")
    print(f"  By region: {dict(regions)}")
    for dhs in DHS_REGIONS:
        n = sum(1 for v in variants if v["region_annotation"] == dhs["name"])
        print(f"  {dhs['name']}: {n} SNVs")


if __name__ == "__main__":
    main()
