#!/usr/bin/env python
"""Recover Ref/Alt alleles for the full local HBA atlas.

The existing HBA atlas contains HBA1/HBA2-window ClinVar rows with missing
Ref/Alt values. This script uses local HGVS_c substitutions plus the UCSC hg38
sequence API to rebuild queryable SNV fields without modifying the source atlas.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "HBA1_Unified_Atlas_300kb.csv"
CONFIG = ROOT / "config" / "locus" / "hba1_300kb.json"
OUT = ROOT / "results" / "PAPER3_HBA_FULL_QUERYABLE_ATLAS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_HBA_FULL_QUERYABLE_ATLAS_20260503.md"

HGVS_SNV = re.compile(r"c\.(?:[-*]?\d+(?:[+-]\d+)?)([ACGT])>([ACGT])")
UCSC_URL = "https://api.genome.ucsc.edu/getData/sequence"


def parse_hgvs_snv(value: object) -> tuple[str | None, str | None]:
    if pd.isna(value):
        return None, None
    match = HGVS_SNV.search(str(value))
    if not match:
        return None, None
    return match.group(1), match.group(2)


def ucsc_ref_base(chrom: str, pos_1based: int) -> str:
    response = requests.get(
        UCSC_URL,
        params={
            "genome": "hg38",
            "chrom": chrom,
            "start": pos_1based - 1,
            "end": pos_1based,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["dna"].upper()


def load_genes() -> list[dict[str, Any]]:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    genes = []
    for item in (data.get("features") or {}).get("genes", []):
        genes.append(
            {
                "name": item["name"],
                "start": int(item["start"]),
                "end": int(item["end"]),
            }
        )
    return genes


def nearest_gene(pos: int, genes: list[dict[str, Any]]) -> tuple[str, int]:
    if not genes:
        return "", -1
    best = min(
        genes,
        key=lambda gene: 0
        if gene["start"] <= pos <= gene["end"]
        else min(abs(pos - gene["start"]), abs(pos - gene["end"])),
    )
    if best["start"] <= pos <= best["end"]:
        return best["name"], 0
    return best["name"], min(abs(pos - best["start"]), abs(pos - best["end"]))


def main() -> None:
    if not ATLAS.exists():
        raise FileNotFoundError(f"Missing source atlas: {ATLAS}")
    if not CONFIG.exists():
        raise FileNotFoundError(f"Missing source config: {CONFIG}")

    df = pd.read_csv(ATLAS)
    genes = load_genes()
    ref_cache: dict[int, str] = {}
    rows: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        pos = int(row["Position_GRCh38"])
        hgvs_ref, hgvs_alt = parse_hgvs_snv(row.get("HGVS_c"))
        if pos not in ref_cache:
            ref_cache[pos] = ucsc_ref_base("chr16", pos)
            time.sleep(0.05)
        ucsc_ref = ref_cache[pos]
        recovered = (
            hgvs_ref is not None
            and hgvs_alt is not None
            and ucsc_ref == hgvs_ref
            and hgvs_ref != hgvs_alt
        )
        gene, gene_distance = nearest_gene(pos, genes)
        out = row.to_dict()
        out["Ref"] = hgvs_ref if recovered else row.get("Ref")
        out["Alt"] = hgvs_alt if recovered else row.get("Alt")
        out["UCSC_hg38_ref"] = ucsc_ref
        out["HGVS_ref"] = hgvs_ref
        out["HGVS_alt"] = hgvs_alt
        out["allele_recovery_status"] = (
            "RECOVERED_UCSC_HGVS_MATCH"
            if recovered
            else "NOT_RECOVERED_HGVS_OR_REF_MISMATCH"
        )
        out["allele_recovery_source"] = "UCSC_hg38_sequence_api_plus_HGVS_c"
        out["is_queryable_snv"] = recovered
        out["nearest_gene"] = gene
        out["nearest_gene_distance_bp"] = gene_distance
        out["source_atlas"] = str(ATLAS.relative_to(ROOT))
        rows.append(out)

    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False)

    recovered_n = int(result["is_queryable_snv"].sum())
    hba2_rows = int((result["nearest_gene"] == "HBA2").sum())
    hba2_queryable = int(
        ((result["nearest_gene"] == "HBA2") & result["is_queryable_snv"].astype(bool)).sum()
    )
    category_counts = (
        result[result["is_queryable_snv"].astype(bool)]["Category"]
        .value_counts(dropna=False)
        .to_dict()
    )

    lines = [
        "# Paper 3 HBA Full Queryable Atlas",
        "",
        "This file is derived from the local HBA 300kb atlas and does not modify the source atlas.",
        "",
        f"- Input atlas: `{ATLAS.relative_to(ROOT)}`",
        f"- Locus config: `{CONFIG.relative_to(ROOT)}`",
        f"- Rows in source atlas: `{len(result)}`",
        f"- Queryable SNVs recovered: `{recovered_n}`",
        f"- HBA2-position rows by nearest gene: `{hba2_rows}`",
        f"- Queryable HBA2-position SNVs: `{hba2_queryable}`",
        f"- Recovery source: UCSC hg38 sequence API + local `HGVS_c` substitution",
        "",
        "## Queryable Category Counts",
        "",
        "| Category | n |",
        "|---|---:|",
    ]
    for category, count in category_counts.items():
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "This is a queryability/provenance table. It is not population evidence and does not establish a regulatory-positive locus.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_MD}")
    print(f"Queryable SNVs recovered: {recovered_n}")
    print(f"Queryable HBA2-position SNVs: {hba2_queryable}")


if __name__ == "__main__":
    main()
