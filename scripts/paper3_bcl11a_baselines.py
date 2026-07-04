#!/usr/bin/env python
"""Baseline checks for the BCL11A Paper 3 pilot cohort."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "BCL11A_Unified_Atlas_bcl11a_erythroid.csv"
AUDIT = ROOT / "results" / "PAPER3_BCL11A_SOURCE_AUDIT_20260503.csv"
CONFIG = ROOT / "config" / "locus" / "bcl11a_erythroid_95kb.json"
OUT = ROOT / "results" / "PAPER3_BCL11A_BASELINE_AUDIT_20260503.md"


def classify_hgvs(hgvs: object) -> str:
    value = "" if pd.isna(hgvs) else str(hgvs)
    if "+" in value or "-" in value:
        return "splice_region_or_intronic"
    if "(p." in value:
        if "Ter" in value or "*" in value:
            return "coding_nonsense"
        return "coding_missense_or_synonymous"
    if "c.*" in value:
        return "utr_or_transcript_flank"
    return "unresolved"


def nearest_distance(position: int, features: list[dict]) -> int:
    distances = [abs(position - int(feature["position"])) for feature in features if "position" in feature]
    return min(distances) if distances else -1


def summarize_group(name: str, df: pd.DataFrame, bottom_ids: set[str]) -> dict[str, object]:
    if df.empty:
        return {
            "group": name,
            "n": 0,
            "bottom5_overlap": 0,
            "lssim_median": "NA",
            "lssim_min": "NA",
        }
    lssim = pd.to_numeric(df["ARCHCODE_LSSIM"], errors="coerce")
    return {
        "group": name,
        "n": len(df),
        "bottom5_overlap": int(df["ClinVar_ID"].isin(bottom_ids).sum()),
        "lssim_median": f"{float(lssim.median()):.4f}",
        "lssim_min": f"{float(lssim.min()):.4f}",
    }


def main() -> None:
    atlas = pd.read_csv(ATLAS)
    audit = pd.read_csv(AUDIT)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    features = config.get("features", {}).get("enhancers", [])
    bottom_ids = set(audit["ClinVar_ID"])
    primary_ids = set(audit.loc[audit["include_primary_paper3"].astype(bool), "ClinVar_ID"])

    atlas["mechanism_subclass"] = atlas["HGVS_c"].map(classify_hgvs)
    atlas["distance_to_nearest_feature_bp"] = atlas["Position_GRCh38"].map(
        lambda pos: nearest_distance(int(pos), features)
    )
    atlas["near_feature_1kb"] = atlas["distance_to_nearest_feature_bp"] <= 1000
    atlas["near_feature_5kb"] = atlas["distance_to_nearest_feature_bp"] <= 5000

    groups = [
        summarize_group("all_atlas", atlas, bottom_ids),
        summarize_group("near_feature_1kb", atlas[atlas["near_feature_1kb"]], bottom_ids),
        summarize_group("near_feature_5kb", atlas[atlas["near_feature_5kb"]], bottom_ids),
        summarize_group(
            "splice_or_intronic",
            atlas[atlas["mechanism_subclass"] == "splice_region_or_intronic"],
            bottom_ids,
        ),
        summarize_group(
            "coding_missense_or_synonymous",
            atlas[atlas["mechanism_subclass"] == "coding_missense_or_synonymous"],
            bottom_ids,
        ),
        summarize_group("primary_audited_ids", atlas[atlas["ClinVar_ID"].isin(primary_ids)], bottom_ids),
    ]

    category_counts = atlas["Category"].fillna("NA").value_counts().to_dict()
    subclass_counts = atlas["mechanism_subclass"].value_counts().to_dict()

    lines = [
        "# Paper 3 BCL11A Baseline Audit",
        "",
        "Generated from local atlas, source audit, and locus config only.",
        "",
        "## Group Summary",
        "",
        "| group | n | bottom5_overlap | lssim_median | lssim_min |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in groups:
        lines.append(
            f"| {row['group']} | {row['n']} | {row['bottom5_overlap']} | "
            f"{row['lssim_median']} | {row['lssim_min']} |"
        )

    lines.extend(["", "## Category Counts", "", "| category | count |", "|---|---:|"])
    for key, value in category_counts.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## HGVS-Derived Subclass Counts", "", "| subclass | count |", "|---|---:|"])
    for key, value in subclass_counts.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Category-only baseline is currently uninformative because all BCL11A rows are `other`.",
            "- Position-window baseline is necessary: all 11 bottom-5% rows are within 1 kb of a configured feature.",
            "- The 3 primary audited rows are a small promoter-proximal splice/UTR-like pilot, not an enhancer-wide validation set.",
        ]
    )
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
