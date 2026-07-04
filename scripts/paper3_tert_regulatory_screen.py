#!/usr/bin/env python
"""Build a conservative Paper 3 TERT regulatory dry-run cohort.

This script freezes a small TERT candidate/control pair from local atlas rows
only. It adds exact Kircher MPRA-style source overlap where available, but does
not query gnomAD and does not resolve germline/somatic semantics.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "TERT_Unified_Atlas_300kb.csv"
KIRCHER = ROOT / "data" / "kircher_TERT_GRCh38.tsv"
OUT_CANDIDATES = ROOT / "results" / "PAPER3_TERT_REGULATORY_CANDIDATES_20260503.csv"
OUT_CONTROLS = ROOT / "results" / "PAPER3_TERT_POSITION_CONTROLS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_TERT_REGULATORY_SCREEN_20260503.md"

REGULATORY_SUBCLASSES = {
    "promoter_or_5_prime_UTR",
    "5_prime_UTR",
    "3_prime_UTR",
    "intronic",
    "splice_region",
    "enhancer_like",
}
SYNTHETIC_MARKERS = ("synthetic", "mock", "demo")


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def is_snv(row: pd.Series) -> bool:
    ref = norm(row.get("Ref")).upper()
    alt = norm(row.get("Alt")).upper()
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT" and ref != alt


def is_synthetic(row: pd.Series) -> bool:
    blob = " ".join(
        norm(row.get(col))
        for col in [
            "ClinVar_ID",
            "Source",
            "Label",
            "Category",
            "ClinVar_Significance",
            "HGVS_c",
        ]
    ).lower()
    return any(marker in blob for marker in SYNTHETIC_MARKERS)


def classify_mechanism(row: pd.Series) -> str:
    category = norm(row.get("Category")).lower()
    hgvs_c = norm(row.get("HGVS_c")).lower()
    hgvs_p = norm(row.get("HGVS_p")).lower()
    blob = f"{category} {hgvs_c} {hgvs_p}"

    if any(token in blob for token in ["missense", "nonsense", "frameshift", "synonymous", "inframe"]):
        if "synonymous" in blob or "=" in hgvs_p:
            return "coding_synonymous"
        if "nonsense" in blob or "ter" in hgvs_p or "*" in hgvs_p:
            return "coding_nonsense"
        if "frameshift" in blob or "fs" in hgvs_p:
            return "coding_frameshift"
        return "coding_missense"
    if "5_prime_utr" in category or "promoter" in category or "c.-" in hgvs_c:
        return "promoter_or_5_prime_UTR"
    if "3_prime_utr" in category or "c.*" in hgvs_c:
        return "3_prime_UTR"
    if "splice" in category:
        return "splice_region"
    if "intronic" in category or "+" in hgvs_c or "-" in hgvs_c:
        return "intronic"
    if "enhancer" in category or "cre" in category or "dhs" in category:
        return "enhancer_like"
    return "other_unresolved"


def add_kircher_overlap(df: pd.DataFrame) -> pd.DataFrame:
    if not KIRCHER.exists():
        df["kircher_exact_match"] = False
        df["kircher_value"] = pd.NA
        df["kircher_p_value"] = pd.NA
        return df

    kircher = pd.read_csv(KIRCHER, sep="\t")
    kircher = kircher.rename(
        columns={
            "Position": "Position_GRCh38",
            "Value": "kircher_value",
            "P-Value": "kircher_p_value",
        }
    )
    kircher["Position_GRCh38"] = kircher["Position_GRCh38"].astype(int)
    for col in ["Ref", "Alt"]:
        kircher[col] = kircher[col].astype(str)
        df[col] = df[col].astype(str)
    merged = df.merge(
        kircher[
            [
                "Position_GRCh38",
                "Ref",
                "Alt",
                "Tags",
                "DNA",
                "RNA",
                "kircher_value",
                "kircher_p_value",
            ]
        ],
        on=["Position_GRCh38", "Ref", "Alt"],
        how="left",
    )
    merged["kircher_exact_match"] = merged["kircher_value"].notna()
    return merged


def select_controls(candidates: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    selected = []
    used: set[str] = set()
    for _, candidate in candidates.iterrows():
        choices = pool[
            (~pool["tert_low_lssim_candidate"])
            & (~pool["ClinVar_ID"].isin(used))
            & (pool["ClinVar_ID"] != candidate["ClinVar_ID"])
        ].copy()
        if choices.empty:
            continue
        choices["same_mechanism"] = choices["mechanism_subclass"] == candidate["mechanism_subclass"]
        choices["same_category"] = choices["Category"] == candidate["Category"]
        choices["same_kircher_overlap"] = choices["kircher_exact_match"] == candidate["kircher_exact_match"]
        choices["position_distance"] = (
            choices["Position_GRCh38"].astype(int) - int(candidate["Position_GRCh38"])
        ).abs()
        choices["lssim_delta"] = (
            choices["ARCHCODE_LSSIM"].astype(float) - float(candidate["ARCHCODE_LSSIM"])
        ).abs()
        chosen = choices.sort_values(
            [
                "same_mechanism",
                "same_category",
                "same_kircher_overlap",
                "position_distance",
                "lssim_delta",
            ],
            ascending=[False, False, False, True, True],
        ).iloc[0]
        used.add(str(chosen["ClinVar_ID"]))
        selected.append(chosen)
    controls = pd.DataFrame(selected)
    if len(controls):
        controls = controls.drop(
            columns=[
                "same_mechanism",
                "same_category",
                "same_kircher_overlap",
                "position_distance",
                "lssim_delta",
            ],
            errors="ignore",
        )
    return controls


def main() -> None:
    if not ATLAS.exists():
        raise FileNotFoundError(f"Missing TERT atlas: {ATLAS}")

    df = pd.read_csv(ATLAS)
    df["is_queryable_snv_rechecked"] = df.apply(is_snv, axis=1)
    df["is_synthetic_or_demo"] = df.apply(is_synthetic, axis=1)
    df["mechanism_subclass"] = df.apply(classify_mechanism, axis=1)
    df["is_regulatory_subclass"] = df["mechanism_subclass"].isin(REGULATORY_SUBCLASSES)

    df = add_kircher_overlap(df)
    usable = df[df["is_queryable_snv_rechecked"] & ~df["is_synthetic_or_demo"]].copy()
    q05 = float(usable["ARCHCODE_LSSIM"].quantile(0.05))
    usable["tert_locus_bottom5_threshold"] = q05
    usable["tert_low_lssim_candidate"] = usable["is_regulatory_subclass"] & (
        usable["ARCHCODE_LSSIM"] <= q05
    )

    regulatory_pool = usable[usable["is_regulatory_subclass"]].copy()
    candidates = regulatory_pool[regulatory_pool["tert_low_lssim_candidate"]].copy()
    controls = select_controls(candidates, regulatory_pool).copy()
    if len(controls):
        controls["tert_position_control"] = True
    else:
        controls = regulatory_pool.head(0).copy()
        controls["tert_position_control"] = pd.Series(dtype=bool)

    output_columns = [
        "ClinVar_ID",
        "Position_GRCh38",
        "Ref",
        "Alt",
        "HGVS_c",
        "HGVS_p",
        "Category",
        "ClinVar_Significance",
        "Source",
        "Label",
        "ARCHCODE_LSSIM",
        "mechanism_subclass",
        "kircher_exact_match",
        "kircher_value",
        "kircher_p_value",
        "Tags",
        "DNA",
        "RNA",
        "is_queryable_snv_rechecked",
        "is_synthetic_or_demo",
        "is_regulatory_subclass",
        "tert_locus_bottom5_threshold",
        "tert_low_lssim_candidate",
    ]
    candidates[[col for col in output_columns if col in candidates.columns]].to_csv(
        OUT_CANDIDATES, index=False
    )
    control_columns = [col for col in output_columns if col in controls.columns]
    if "tert_position_control" in controls.columns:
        control_columns.append("tert_position_control")
    controls[control_columns].to_csv(OUT_CONTROLS, index=False)

    lines = [
        "# Paper 3 TERT Regulatory Screen",
        "",
        "Date: 2026-05-03",
        "",
        "This is a source/dry-run cohort artifact, not a manuscript result.",
        "",
        f"- Input atlas: `{ATLAS.relative_to(ROOT)}`",
        f"- Kircher source table: `{KIRCHER.relative_to(ROOT)}`",
        f"- Queryable non-synthetic SNVs: `{len(usable)}`",
        f"- Queryable regulatory-subclass SNVs: `{len(regulatory_pool)}`",
        f"- Whole-locus bottom-5% LSSIM threshold: `{q05:.6g}`",
        f"- Low-LSSIM regulatory candidates: `{len(candidates)}`",
        f"- Selected position controls: `{len(controls)}`",
        f"- Candidate rows with exact Kircher overlap: `{int(candidates['kircher_exact_match'].sum())}`",
        "",
        "## Candidate Mechanism Counts",
        "",
        "| mechanism_subclass | n |",
        "|---|---:|",
    ]
    for key, value in candidates["mechanism_subclass"].value_counts().to_dict().items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Dry-Run Commands",
            "",
            "Candidate dry-run:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_TERT_REGULATORY_CANDIDATES_20260503.csv --chrom 5 --cohort-column tert_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name TERT --out paper3_tert_candidates_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "Control dry-run:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_TERT_POSITION_CONTROLS_20260503.csv --chrom 5 --cohort-column tert_position_control --cohort-op equals --cohort-value true --locus-name TERT_position_controls --out paper3_tert_position_controls_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "## Gate Caveat",
            "",
            "Do not run live gnomAD from this artifact alone. TERT promoter/5_prime_UTR rows need a separate germline/somatic/source semantics audit before population interpretation.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CANDIDATES}")
    print(f"Wrote {OUT_CONTROLS}")
    print(f"Wrote {OUT_MD}")
    print(f"Candidates: {len(candidates)}")
    print(f"Controls: {len(controls)}")


if __name__ == "__main__":
    main()
