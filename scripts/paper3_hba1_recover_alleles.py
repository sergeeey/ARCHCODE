#!/usr/bin/env python
"""Recover HBA1 Ref/Alt alleles for MANGO-anchored variants.

Ref bases are fetched from UCSC hg38 sequence API and checked against the
single-nucleotide HGVS_c substitution. This creates a queryable planning table;
it does not modify the original atlas.
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import pandas as pd
import requests


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "HBA1_Unified_Atlas_300kb.csv"
OVERLAP = ROOT / "results" / "PAPER3_HBA1_MANGO_VARIANT_OVERLAP_20260503.csv"
OUT = ROOT / "results" / "PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.md"

HGVS_SNV = re.compile(r"c\.(?:[-*]?\d+(?:[+-]\d+)?)([ACGT])>([ACGT])")
UCSC_URL = "https://api.genome.ucsc.edu/getData/sequence"


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


def parse_hgvs_snv(value: object) -> tuple[str | None, str | None]:
    if pd.isna(value):
        return None, None
    match = HGVS_SNV.search(str(value))
    if not match:
        return None, None
    return match.group(1), match.group(2)


def main() -> None:
    atlas = pd.read_csv(ATLAS)
    overlap = pd.read_csv(OVERLAP)

    # Keep one MANGO evidence row per variant, preferring the lowest p-value.
    evidence = (
        overlap.sort_values(["id", "pvalue", "count"], ascending=[True, True, False])
        .drop_duplicates("id")
        .rename(columns={"id": "ClinVar_ID"})
    )
    merged = atlas.merge(
        evidence[
            [
                "ClinVar_ID",
                "anchor_start",
                "anchor_end",
                "other_anchor",
                "count",
                "pvalue",
            ]
        ],
        on="ClinVar_ID",
        how="inner",
    )

    rows = []
    ref_cache: dict[int, str] = {}
    for _, row in merged.iterrows():
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
        rows.append(out)

    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False)

    recovered_n = int(result["is_queryable_snv"].sum())
    lines = [
        "# Paper 3 HBA1 MANGO Queryable Atlas",
        "",
        "This file is derived from local HBA1 atlas rows that overlap HUDEP2 H3K27ac MANGO interaction anchors.",
        "",
        f"- Input atlas: `{ATLAS.relative_to(ROOT)}`",
        f"- MANGO overlap: `{OVERLAP.relative_to(ROOT)}`",
        f"- Rows with MANGO evidence: `{len(result)}`",
        f"- Queryable SNVs recovered: `{recovered_n}`",
        f"- Recovery source: UCSC hg38 sequence API + local `HGVS_c` substitution",
        "",
        "Rows with `allele_recovery_status=RECOVERED_UCSC_HGVS_MATCH` passed a reference-base sanity check.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
