#!/usr/bin/env python
"""Build BCL11A position-matched controls for the Paper 3 pilot."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "BCL11A_Unified_Atlas_bcl11a_erythroid.csv"
AUDIT = ROOT / "results" / "PAPER3_BCL11A_SOURCE_AUDIT_20260503.csv"
CONFIG = ROOT / "config" / "locus" / "bcl11a_erythroid_95kb.json"
OUT = ROOT / "results" / "PAPER3_BCL11A_POSITION_MATCHED_CONTROLS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_BCL11A_POSITION_MATCHED_CONTROLS_20260503.md"


def nearest_feature(position: int, features: list[dict]) -> tuple[str, int]:
    distances = [
        (feature.get("name", "unknown"), abs(position - int(feature["position"])))
        for feature in features
        if "position" in feature
    ]
    return min(distances, key=lambda item: item[1]) if distances else ("NA", -1)


def main() -> None:
    atlas = pd.read_csv(ATLAS)
    audit = pd.read_csv(AUDIT)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    features = config.get("features", {}).get("enhancers", [])
    bottom_ids = set(audit["ClinVar_ID"])

    nearest = atlas["Position_GRCh38"].map(lambda pos: nearest_feature(int(pos), features))
    atlas["nearest_config_feature"] = nearest.map(lambda item: item[0])
    atlas["distance_to_nearest_feature_bp"] = nearest.map(lambda item: item[1])
    atlas["near_feature_1kb"] = atlas["distance_to_nearest_feature_bp"] <= 1000
    snv = atlas.apply(
        lambda row: (
            len(str(row.get("Ref", ""))) == 1
            and len(str(row.get("Alt", ""))) == 1
            and str(row.get("Ref", "")) in "ACGT"
            and str(row.get("Alt", "")) in "ACGT"
            and str(row.get("Ref", "")) != str(row.get("Alt", ""))
        ),
        axis=1,
    )
    atlas["position_control"] = snv & atlas["near_feature_1kb"] & ~atlas["ClinVar_ID"].isin(bottom_ids)

    controls = atlas[atlas["position_control"]].copy()
    controls.to_csv(OUT, index=False)

    lines = [
        "# Paper 3 BCL11A Position-Matched Controls",
        "",
        "Generated from local BCL11A atlas and locus config only.",
        "",
        f"- Near-feature rows within 1 kb: `{int(atlas['near_feature_1kb'].sum())}`",
        f"- Bottom-5% rows excluded: `{len(bottom_ids)}`",
        f"- Position-matched controls: `{len(controls)}`",
        "",
        "These controls test whether the pilot signal is simply caused by proximity to the configured BCL11A promoter/enhancer feature.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
