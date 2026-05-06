#!/usr/bin/env python
"""Build CFTR low-LSSIM regulatory candidates and position-matched controls."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "CFTR_Unified_Atlas_317kb.csv"
CONFIG = ROOT / "config" / "locus" / "cftr_317kb.json"
OUT_CANDIDATES = ROOT / "results" / "PAPER3_CFTR_REGULATORY_CANDIDATES_20260503.csv"
OUT_CONTROLS = ROOT / "results" / "PAPER3_CFTR_POSITION_CONTROLS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_CFTR_REGULATORY_SCREEN_20260503.md"


REGULATORY_CATEGORIES = {"5_prime_UTR", "3_prime_UTR", "intronic", "splice", "splice_region", "other"}


def is_snv(row: pd.Series) -> bool:
    ref = str(row.get("Ref", ""))
    alt = str(row.get("Alt", ""))
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT" and ref != alt


def nearest_feature(position: int, features: list[dict]) -> tuple[str, int]:
    distances = [
        (feature.get("name", "unknown"), abs(position - int(feature["position"])))
        for feature in features
        if "position" in feature
    ]
    return min(distances, key=lambda item: item[1]) if distances else ("NA", -1)


def classify_hgvs(hgvs: object) -> str:
    value = "" if pd.isna(hgvs) else str(hgvs)
    if "c.-" in value:
        return "5_prime_utr_or_promoter"
    if "c.*" in value:
        return "3_prime_utr_or_flank"
    if "+" in value or "-" in value:
        return "splice_region_or_intronic"
    if "g." in value and "(CFTR)" not in value:
        return "genomic_other"
    if "(p." in value:
        return "coding"
    return "unresolved"


def main() -> None:
    atlas = pd.read_csv(ATLAS)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    features = config.get("features", {}).get("enhancers", [])

    atlas["is_snv"] = atlas.apply(is_snv, axis=1)
    nearest = atlas["Position_GRCh38"].map(lambda pos: nearest_feature(int(pos), features))
    atlas["nearest_config_feature"] = nearest.map(lambda item: item[0])
    atlas["distance_to_nearest_feature_bp"] = nearest.map(lambda item: item[1])
    atlas["mechanism_subclass"] = atlas["HGVS_c"].map(classify_hgvs)

    q05 = atlas["ARCHCODE_LSSIM"].quantile(0.05)
    regulatory = atlas["Category"].isin(REGULATORY_CATEGORIES)
    near_feature = atlas["distance_to_nearest_feature_bp"] <= 1500
    non_synthetic = ~(
        atlas.get("Source", pd.Series("", index=atlas.index))
        .fillna("")
        .astype(str)
        .str.contains("SYNTHETIC|MOCK|DEMO", case=False, regex=True)
    )

    atlas["cftr_primary_candidate"] = (
        atlas["is_snv"]
        & non_synthetic
        & regulatory
        & near_feature
        & (atlas["ARCHCODE_LSSIM"] <= q05)
    )
    atlas["cftr_position_control_pool"] = (
        atlas["is_snv"] & non_synthetic & regulatory & near_feature & ~atlas["cftr_primary_candidate"]
    )

    candidates = atlas[atlas["cftr_primary_candidate"]].copy()
    controls = atlas[atlas["cftr_position_control_pool"]].copy()
    controls = controls.sort_values(
        ["nearest_config_feature", "distance_to_nearest_feature_bp", "ARCHCODE_LSSIM"],
        ascending=[True, True, False],
    ).head(max(len(candidates), 1))

    candidates.to_csv(OUT_CANDIDATES, index=False)
    controls.to_csv(OUT_CONTROLS, index=False)

    lines = [
        "# Paper 3 CFTR Regulatory Screen",
        "",
        "Generated from local CFTR atlas and locus config only.",
        "",
        f"- Input atlas: `{ATLAS.relative_to(ROOT)}`",
        f"- Locus config: `{CONFIG.relative_to(ROOT)}`",
        f"- Bottom-5% LSSIM threshold: `{q05:.4f}`",
        f"- Primary low-LSSIM regulatory candidates: `{len(candidates)}`",
        f"- Position control pool within 1.5 kb of configured features: `{int(atlas['cftr_position_control_pool'].sum())}`",
        f"- Position controls selected for pilot: `{len(controls)}`",
        "",
        "## Candidate Subclasses",
        "",
        "| subclass | count |",
        "|---|---:|",
    ]
    for key, value in candidates["mechanism_subclass"].value_counts().to_dict().items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Control Subclasses",
            "",
            "| subclass | count |",
            "|---|---:|",
        ]
    )
    for key, value in controls["mechanism_subclass"].value_counts().to_dict().items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Interpretation Guardrail",
            "",
            "CFTR is a mechanism-boundary candidate because the local config notes K562 tissue mismatch and literature-derived enhancer occupancy. Passing this screen would identify a useful regulatory test locus, not a final validation result.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CANDIDATES}")
    print(f"Wrote {OUT_CONTROLS}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
