#!/usr/bin/env python
"""Inventory local GATA1 source rows for the Paper 3 next-locus gate.

The goal is not to build a live-query cohort. This script checks whether the
local GATA1 atlas/source files can support queryable regulatory candidates and
matched controls after recovering SNV alleles from HGVS where possible.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"
CONFIG = ROOT / "config" / "locus" / "gata1_300kb.json"

ATLAS = RESULTS / "GATA1_Unified_Atlas_300kb.csv"
SOURCE = DATA / "clinvar_gata1_variants.csv"
ALT_SOURCE = DATA / "gata1_variants.csv"

OUT_ATLAS = RESULTS / "PAPER3_GATA1_SOURCE_INVENTORY_20260503.csv"
OUT_MD = RESULTS / "PAPER3_GATA1_SOURCE_INVENTORY_20260503.md"

BASES = {"A", "C", "G", "T"}
SYNTHETIC_MARKERS = ("synthetic", "mock", "demo")


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def recover_ref_alt(row: pd.Series) -> tuple[str, str, str]:
    ref = norm(row.get("Ref") or row.get("ref")).upper()
    alt = norm(row.get("Alt") or row.get("alt")).upper()
    if ref in BASES and alt in BASES and ref != alt:
        return ref, alt, "existing_ref_alt"

    blob = " ".join(
        norm(row.get(col))
        for col in [
            "HGVS_c",
            "hgvs_c",
            "title",
            "ClinVar_ID",
            "clinvar_id",
        ]
    )
    match = re.search(r"c\.[^,\s()]*?([ACGT])>([ACGT])", blob)
    if match and match.group(1) != match.group(2):
        return match.group(1), match.group(2), "recovered_from_hgvs_plus_strand_assumption"
    return ref, alt, "not_recovered"


def classify_mechanism(row: pd.Series) -> str:
    category = norm(row.get("Category") or row.get("category")).lower()
    hgvs_c = norm(row.get("HGVS_c") or row.get("hgvs_c") or row.get("title")).lower()
    hgvs_p = norm(row.get("HGVS_p") or row.get("hgvs_p")).lower()
    blob = f"{category} {hgvs_c} {hgvs_p}"

    if "frameshift" in blob or "fs" in hgvs_p:
        return "coding_frameshift"
    if "nonsense" in blob or "ter" in hgvs_p or "*" in hgvs_p:
        return "coding_nonsense"
    if "missense" in blob:
        return "coding_missense"
    if "synonymous" in blob or hgvs_p.endswith("=") or re.search(r"p\.[a-z0-9]+=", hgvs_p):
        return "coding_synonymous"

    # GATA1 c.-19-1/c.-19-2 are splice-acceptor-adjacent, not promoter rows.
    splice_like = re.search(r"c\.(?:-\d+|\d+)([+-])(\d+)", hgvs_c)
    if "splice" in category or (splice_like and int(splice_like.group(2)) <= 2):
        return "splice_region"
    if splice_like:
        return "intronic"
    if "intronic" in category or "intron" in category:
        return "intronic"
    if re.search(r"c\.-\d+[acgt]>[acgt]", hgvs_c):
        return "promoter_or_5_prime_UTR"
    if "utr" in category or "promoter" in category:
        return "promoter_or_5_prime_UTR"
    if "enhancer" in category or "cre" in category or "dhs" in category:
        return "enhancer_like"
    return "other_unresolved"


def is_synthetic(row: pd.Series) -> bool:
    blob = " ".join(
        norm(row.get(col))
        for col in [
            "ClinVar_ID",
            "clinvar_id",
            "Source",
            "source",
            "Label",
            "label",
            "ClinVar_Significance",
            "clinical_significance",
            "Category",
            "category",
            "HGVS_c",
            "hgvs_c",
            "title",
        ]
    ).lower()
    return any(marker in blob for marker in SYNTHETIC_MARKERS)


def load_features() -> list[dict[str, Any]]:
    if not CONFIG.exists():
        return []
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    features: list[dict[str, Any]] = []
    for feature_type, rows in (data.get("features") or {}).items():
        if not isinstance(rows, list):
            continue
        for item in rows:
            if feature_type == "genes":
                start = int(item["start"])
                end = int(item["end"])
                pos = (start + end) // 2
            else:
                pos = int(item["position"])
                start = pos
                end = pos
            features.append(
                {
                    "feature_type": feature_type,
                    "name": item.get("name", feature_type),
                    "position": pos,
                    "start": start,
                    "end": end,
                }
            )
    return features


def nearest_feature(pos: int, features: list[dict[str, Any]]) -> dict[str, Any]:
    if not features:
        return {
            "nearest_feature_type": "",
            "nearest_feature_name": "",
            "nearest_feature_distance_bp": "",
        }

    def distance(item: dict[str, Any]) -> int:
        start = int(item["start"])
        end = int(item["end"])
        if start <= pos <= end:
            return 0
        return min(abs(pos - start), abs(pos - end), abs(pos - int(item["position"])))

    best = min(features, key=distance)
    return {
        "nearest_feature_type": best["feature_type"],
        "nearest_feature_name": best["name"],
        "nearest_feature_distance_bp": distance(best),
    }


def normalize_atlas() -> pd.DataFrame:
    if not ATLAS.exists():
        raise FileNotFoundError(f"Missing GATA1 atlas: {ATLAS}")
    atlas = pd.read_csv(ATLAS)

    if SOURCE.exists():
        source = pd.read_csv(SOURCE)
        source = source.rename(
            columns={
                "accession": "ClinVar_ID",
                "title": "source_title",
                "review_status": "source_review_status",
                "clinical_significance": "source_clinical_significance",
            }
        )
        atlas = atlas.merge(
            source[
                [
                    "ClinVar_ID",
                    "source_title",
                    "source_review_status",
                    "source_clinical_significance",
                ]
            ],
            on="ClinVar_ID",
            how="left",
        )

    if ALT_SOURCE.exists():
        alt = pd.read_csv(ALT_SOURCE)
        alt = alt.rename(
            columns={
                "clinvar_id": "ClinVar_ID",
                "ref": "alt_source_ref",
                "alt": "alt_source_alt",
                "hgvs_c": "alt_source_hgvs_c",
                "hgvs_p": "alt_source_hgvs_p",
            }
        )
        atlas = atlas.merge(
            alt[
                [
                    "ClinVar_ID",
                    "alt_source_ref",
                    "alt_source_alt",
                    "alt_source_hgvs_c",
                    "alt_source_hgvs_p",
                ]
            ],
            on="ClinVar_ID",
            how="left",
        )
    return atlas


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def write_report(df: pd.DataFrame) -> None:
    queryable = df[df["is_queryable_snv_recovered"]].copy()
    regulatory = queryable[queryable["mechanism_subclass"].isin({"promoter_or_5_prime_UTR", "enhancer_like"})]
    splice_intronic = queryable[queryable["mechanism_subclass"].isin({"splice_region", "intronic"})]
    coding = queryable[queryable["mechanism_subclass"].str.startswith("coding_")]
    bottom5 = queryable[queryable["gata1_bottom5_recovered"]].copy()
    primary_candidates = df[df["gata1_primary_regulatory_candidate"]].copy()
    potential_controls = df[df["gata1_potential_position_control"]].copy()

    source_rows = 0
    if SOURCE.exists():
        source_rows = len(pd.read_csv(SOURCE))

    lines = [
        "# Paper 3 GATA1 Source Inventory",
        "",
        "Date: 2026-05-03",
        "",
        "Local-source inventory only. No gnomAD query was run.",
        "",
        "## Executive Verdict",
        "",
        "- Decision: **STOP_LOCAL_POSITIVE_GATE / REBUILD_REF_ALT_ONLY**",
        "- Can GATA1 serve as the second regulatory-positive locus from current local rows? **NO / NOT YET**",
        f"- Queryable SNVs after HGVS allele recovery: `{len(queryable)}`",
        f"- Primary promoter/enhancer-like regulatory candidates: `{len(primary_candidates)}`",
        f"- Primary controls selected: `{len(potential_controls) if len(primary_candidates) else 0}`",
        "- Main blocker: local GATA1 rows are mostly coding or splice/intronic disease variants; Ref/Alt can be recovered for many SNVs, but that does not create a clean noncoding regulatory-positive cohort.",
        "- Next required action: import a true GATA1 regulatory source set or switch to a documented regulatory locus with queryable noncoding SNVs and matched controls.",
        "",
        "## Inventory Counts",
        "",
    ]
    lines.extend(
        table(
            [
                ["atlas rows", len(df)],
                ["source rows", source_rows],
                ["queryable SNVs after recovery", len(queryable)],
                ["promoter/enhancer-like queryable rows", len(regulatory)],
                ["splice/intronic queryable rows", len(splice_intronic)],
                ["coding queryable rows", len(coding)],
                ["bottom 5% queryable rows", len(bottom5)],
                ["primary regulatory candidates", len(primary_candidates)],
            ],
            ["Metric", "Value"],
        )
    )
    lines.extend(
        [
            "",
            "## Bottom-5 Mechanism Composition",
            "",
        ]
    )
    if bottom5.empty:
        lines.append("No bottom-5 queryable rows after allele recovery.")
    else:
        rows = []
        for mechanism, count in bottom5["mechanism_subclass"].value_counts().items():
            rows.append([mechanism, int(count)])
        lines.extend(table(rows, ["mechanism_subclass", "bottom5 rows"]))

    lines.extend(
        [
            "",
            "## Regulatory-Like Rows After Recovery",
            "",
        ]
    )
    if regulatory.empty:
        lines.append("No promoter/enhancer-like queryable rows were recovered from the current local GATA1 source set.")
    else:
        rows = []
        for _, row in regulatory.iterrows():
            rows.append(
                [
                    norm(row.get("ClinVar_ID")),
                    norm(row.get("Position_GRCh38")),
                    f"{norm(row.get('Ref_recovered'))}>{norm(row.get('Alt_recovered'))}",
                    norm(row.get("HGVS_c")),
                    norm(row.get("ClinVar_Significance")),
                    norm(row.get("ARCHCODE_LSSIM")),
                    norm(row.get("mechanism_subclass")),
                ]
            )
        lines.extend(
            table(
                rows,
                [
                    "ClinVar_ID",
                    "pos",
                    "allele",
                    "HGVS_c",
                    "ClinVar",
                    "ARCHCODE_LSSIM",
                    "mechanism_subclass",
                ],
            )
        )

    lines.extend(
        [
            "",
            "## Dry-Run / Live Gate",
            "",
            "- `population_filter.py` dry-run: **SKIPPED** because primary regulatory candidates are empty.",
            "- Live gnomAD: **NOT RUN**.",
            "",
            "## Allowed Claim",
            "",
            "GATA1 local rows show recoverable SNV queryability, but current local sources do not support a clean regulatory-positive Paper 3 cohort.",
            "",
            "## Not Allowed",
            "",
            "- \"GATA1 validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_gata1_source_inventory.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = normalize_atlas()
    recovered = df.apply(recover_ref_alt, axis=1, result_type="expand")
    recovered.columns = ["Ref_recovered", "Alt_recovered", "allele_recovery_status"]
    df = pd.concat([df, recovered], axis=1)
    df["is_queryable_snv_recovered"] = df.apply(
        lambda row: norm(row["Ref_recovered"]).upper() in BASES
        and norm(row["Alt_recovered"]).upper() in BASES
        and norm(row["Ref_recovered"]).upper() != norm(row["Alt_recovered"]).upper(),
        axis=1,
    )
    df["mechanism_subclass"] = df.apply(classify_mechanism, axis=1)
    df["is_synthetic_or_demo"] = df.apply(is_synthetic, axis=1)

    queryable = df[df["is_queryable_snv_recovered"] & ~df["is_synthetic_or_demo"]].copy()
    if len(queryable):
        q05 = float(queryable["ARCHCODE_LSSIM"].astype(float).quantile(0.05))
    else:
        q05 = math.nan
    df["gata1_lssim_q05_recovered"] = q05
    df["gata1_bottom5_recovered"] = df["is_queryable_snv_recovered"] & (
        df["ARCHCODE_LSSIM"].astype(float) <= q05 if not math.isnan(q05) else False
    )
    df["gata1_primary_regulatory_candidate"] = (
        df["gata1_bottom5_recovered"]
        & df["mechanism_subclass"].isin({"promoter_or_5_prime_UTR", "enhancer_like"})
        & df["is_queryable_snv_recovered"]
        & ~df["is_synthetic_or_demo"]
    )
    df["gata1_potential_position_control"] = (
        df["mechanism_subclass"].isin({"promoter_or_5_prime_UTR", "enhancer_like"})
        & df["is_queryable_snv_recovered"]
        & ~df["gata1_bottom5_recovered"]
        & ~df["is_synthetic_or_demo"]
    )

    features = load_features()
    nearest_rows = []
    for _, row in df.iterrows():
        try:
            pos = int(row["Position_GRCh38"])
            nearest_rows.append(nearest_feature(pos, features))
        except Exception:
            nearest_rows.append(
                {
                    "nearest_feature_type": "",
                    "nearest_feature_name": "",
                    "nearest_feature_distance_bp": "",
                }
            )
    df = pd.concat([df, pd.DataFrame(nearest_rows)], axis=1)

    df.to_csv(OUT_ATLAS, index=False)
    write_report(df)
    print(f"Wrote {OUT_ATLAS.relative_to(ROOT)} ({len(df)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
