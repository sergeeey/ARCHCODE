#!/usr/bin/env python
"""Create a source-audited BCL11A candidate subset for Paper 3 planning."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "BCL11A_Unified_Atlas_bcl11a_erythroid.csv"
CONFIG = ROOT / "config" / "locus" / "bcl11a_erythroid_95kb.json"
OUT = ROOT / "results" / "PAPER3_BCL11A_SOURCE_AUDIT_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_BCL11A_SOURCE_AUDIT_20260503.md"


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


def nearest_feature(position: int, features: list[dict]) -> tuple[str, int]:
    distances = [
        (feature.get("name", "unknown"), abs(position - int(feature["position"])))
        for feature in features
        if "position" in feature
    ]
    if not distances:
        return "NA", -1
    return min(distances, key=lambda item: item[1])


def main() -> None:
    atlas = pd.read_csv(ATLAS)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    enhancer_features = config.get("features", {}).get("enhancers", [])

    q05 = atlas["ARCHCODE_LSSIM"].quantile(0.05)
    cohort = atlas[atlas["ARCHCODE_LSSIM"] <= q05].copy()

    rows = []
    for _, row in cohort.iterrows():
        position = int(row["Position_GRCh38"])
        feature_name, feature_distance = nearest_feature(position, enhancer_features)
        subclass = classify_hgvs(row.get("HGVS_c"))
        is_snv = (
            len(str(row.get("Ref", ""))) == 1
            and len(str(row.get("Alt", ""))) == 1
            and str(row.get("Ref", "")) in "ACGT"
            and str(row.get("Alt", "")) in "ACGT"
            and str(row.get("Ref", "")) != str(row.get("Alt", ""))
        )
        include_primary = (
            is_snv
            and
            subclass in {"splice_region_or_intronic", "utr_or_transcript_flank"}
            and feature_distance <= 1000
        )
        rows.append(
            {
                "ClinVar_ID": row["ClinVar_ID"],
                "Position_GRCh38": position,
                "Ref": row["Ref"],
                "Alt": row["Alt"],
                "HGVS_c": row.get("HGVS_c", ""),
                "ClinVar_Significance": row.get("ClinVar_Significance", ""),
                "atlas_category": row.get("Category", ""),
                "mechanism_subclass": subclass,
                "ARCHCODE_LSSIM": row["ARCHCODE_LSSIM"],
                "nearest_config_feature": feature_name,
                "distance_to_nearest_feature_bp": feature_distance,
                "include_primary_paper3": include_primary,
                "exclusion_reason": ""
                if include_primary
                else "not a clean regulatory/enhancer subset under local HGVS/config audit",
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)

    include_count = int(out["include_primary_paper3"].sum())
    subclass_counts = out["mechanism_subclass"].value_counts().to_dict()
    md = [
        "# Paper 3 BCL11A Source Audit",
        "",
        "Generated from local atlas and locus config only.",
        "",
        f"- Input atlas: `{ATLAS.relative_to(ROOT)}`",
        f"- Locus config: `{CONFIG.relative_to(ROOT)}`",
        f"- Bottom-5% LSSIM threshold: `{q05:.4f}`",
        f"- Audited rows: `{len(out)}`",
        f"- Rows allowed for primary Paper 3 regulatory cohort: `{include_count}`",
        "",
        "## Mechanism Subclass Counts",
        "",
        "| subclass | count |",
        "|---|---:|",
    ]
    for key, value in subclass_counts.items():
        md.append(f"| {key} | {value} |")

    md.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit is intentionally conservative. Rows are only allowed into the primary Paper 3 regulatory cohort if local HGVS/config evidence supports a promoter-proximal splice/UTR/flank interpretation within 1 kb of a configured feature.",
            "",
            "Rows excluded here can still be used in secondary/boundary analyses, but not as clean regulatory-positive evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
