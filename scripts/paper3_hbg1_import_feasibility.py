#!/usr/bin/env python
"""Assess HBG1 as a source-only import target for Paper 3.

This script reads the local Kircher HBG1 source table and the existing HBB
95kb sub-TAD config. It proposes source-only MPRA candidate/control rows, but
does not create an ARCHCODE atlas and does not query gnomAD.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"
CONFIG = ROOT / "config" / "locus" / "hbb_95kb_subTAD.json"
GENERATOR = ROOT / "scripts" / "generate-unified-atlas.ts"
LOCUS_CONFIG_TS = ROOT / "src" / "domain" / "config" / "locus-config.ts"
HBG1_VARIANTS_CSV = DATA / "hbg1_variants.csv"
HBG1_ATLAS_CSV = RESULTS / "HBG1_Unified_Atlas_hbg1.csv"

SOURCE = DATA / "kircher_HBG1_GRCh38.tsv"
OUT_ALL = RESULTS / "PAPER3_HBG1_IMPORT_SOURCE_TABLE_20260503.csv"
OUT_CANDIDATES = RESULTS / "PAPER3_HBG1_SOURCE_ONLY_CANDIDATES_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_HBG1_SOURCE_ONLY_CONTROLS_20260503.csv"
OUT_MD = RESULTS / "PAPER3_HBG1_IMPORT_FEASIBILITY_20260503.md"

BASES = {"A", "C", "G", "T"}


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def is_snv(row: pd.Series) -> bool:
    ref = norm(row.get("Ref")).upper()
    alt = norm(row.get("Alt")).upper()
    return len(ref) == 1 and len(alt) == 1 and ref in BASES and alt in BASES and ref != alt


def load_config() -> dict[str, Any]:
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def find_gene(config: dict[str, Any], gene_name: str) -> dict[str, Any]:
    for gene in (config.get("features") or {}).get("genes", []):
        if norm(gene.get("name")).upper() == gene_name.upper():
            return gene
    return {}


def nearest_feature(position: int, config: dict[str, Any]) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    for feature_type, rows in (config.get("features") or {}).items():
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
                    "name": norm(item.get("name")),
                    "start": start,
                    "end": end,
                    "position": pos,
                }
            )
    if not features:
        return {
            "nearest_feature_type": "",
            "nearest_feature_name": "",
            "nearest_feature_distance_bp": "",
        }

    def distance(item: dict[str, Any]) -> int:
        start = int(item["start"])
        end = int(item["end"])
        if start <= position <= end:
            return 0
        return min(abs(position - start), abs(position - end), abs(position - int(item["position"])))

    best = min(features, key=distance)
    return {
        "nearest_feature_type": best["feature_type"],
        "nearest_feature_name": best["name"],
        "nearest_feature_distance_bp": distance(best),
    }


def annotate_source(df: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    df = df.copy()
    hbg1 = find_gene(config, "HBG1")
    window = config.get("window") or {}
    hbg1_start = int(hbg1["start"]) if hbg1 else math.nan
    hbg1_end = int(hbg1["end"]) if hbg1 else math.nan
    hbg1_strand = norm(hbg1.get("strand")) if hbg1 else ""
    hbg1_tss = hbg1_end if hbg1_strand == "-" else hbg1_start
    window_start = int(window.get("start", -1))
    window_end = int(window.get("end", -1))

    df["is_queryable_snv"] = df.apply(is_snv, axis=1)
    df["hbg1_config_source"] = CONFIG.name if config else ""
    df["inside_hbb_95kb_config_window"] = df["Position"].astype(int).between(window_start, window_end)
    df["inside_hbg1_gene_body"] = df["Position"].astype(int).between(hbg1_start, hbg1_end)
    df["distance_to_hbg1_tss_bp"] = (df["Position"].astype(int) - int(hbg1_tss)).abs() if hbg1 else pd.NA
    if hbg1_strand == "-":
        df["hbg1_promoter_side"] = df["Position"].astype(int).map(
            lambda pos: "promoter_side" if pos >= int(hbg1_tss) else "gene_body_side"
        )
    else:
        df["hbg1_promoter_side"] = df["Position"].astype(int).map(
            lambda pos: "promoter_side" if pos <= int(hbg1_tss) else "gene_body_side"
        )
    nearest = [nearest_feature(int(row["Position"]), config) for _, row in df.iterrows()]
    df = pd.concat([df, pd.DataFrame(nearest)], axis=1)

    df["mpra_effect_class"] = df["Value"].astype(float).map(
        lambda value: "strong_positive"
        if value >= 0.5
        else "strong_negative"
        if value <= -0.5
        else "near_zero"
        if abs(value) <= 0.05
        else "intermediate"
    )
    df["hbg1_source_candidate"] = (
        df["is_queryable_snv"]
        & df["inside_hbb_95kb_config_window"]
        & df["hbg1_promoter_side"].eq("promoter_side")
        & df["mpra_effect_class"].isin({"strong_positive", "strong_negative"})
        & (df["P-Value"].astype(float) <= 0.05)
    )
    df["hbg1_source_control"] = (
        df["is_queryable_snv"]
        & df["inside_hbb_95kb_config_window"]
        & df["hbg1_promoter_side"].eq("promoter_side")
        & df["mpra_effect_class"].eq("near_zero")
        & (df["P-Value"].astype(float) >= 0.5)
    )
    df["paper3_gate_status"] = "SOURCE_ONLY_NO_ARCHCODE_LSSIM"
    return df


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def rows_table(df: pd.DataFrame, cols: list[str], limit: int = 20) -> list[str]:
    if df.empty:
        return ["No rows."]
    rows = []
    for _, row in df.head(limit).iterrows():
        rows.append([norm(row.get(col)) for col in cols])
    return table(rows, cols)


def write_report(df: pd.DataFrame, candidates: pd.DataFrame, controls: pd.DataFrame, config: dict[str, Any]) -> None:
    hbg1 = find_gene(config, "HBG1")
    generator_text = GENERATOR.read_text(encoding="utf-8") if GENERATOR.exists() else ""
    config_text = LOCUS_CONFIG_TS.read_text(encoding="utf-8") if LOCUS_CONFIG_TS.exists() else ""
    generator_supports_hbg1 = "LOCUS_ARG === \"hbg1\"" in generator_text
    config_alias_supports_hbg1 = "hbg1:" in config_text or "\"hbg1\"" in config_text
    decision = "IMPORT_ARCHCODE_ATLAS_BEFORE_DRY_RUN"
    lines = [
        "# Paper 3 HBG1 Import Feasibility",
        "",
        "Date: 2026-05-03",
        "",
        "Source-only import feasibility. No ARCHCODE atlas was generated and no gnomAD query was run.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{decision}**",
        "- Can HBG1 serve as the second regulatory-positive locus now? **NOT YET**",
        f"- Source-only candidate rows: `{len(candidates)}`",
        f"- Source-only control rows: `{len(controls)}`",
        "- Main blocker: HBG1 has queryable MPRA-like source rows inside the HBB 95kb sub-TAD config, but no HBG1 ARCHCODE atlas/LSSIM values have been generated for these source variants.",
        "- Next required action: generate or import an HBG1/HBB-subTAD ARCHCODE atlas for the Kircher HBG1 rows, then rerun candidate/control selection and dry-run gate.",
        "",
        "## Config Coverage",
        "",
    ]
    lines.extend(
        table(
            [
                ["config", CONFIG.name if config else "MISSING"],
                ["config window", f"{(config.get('window') or {}).get('chromosome')}:{(config.get('window') or {}).get('start')}-{(config.get('window') or {}).get('end')}" if config else ""],
                ["HBG1 gene in config", bool(hbg1)],
                ["HBG1 interval", f"{hbg1.get('start')}-{hbg1.get('end')} ({hbg1.get('strand')})" if hbg1 else ""],
            ["source rows", len(df)],
            ["queryable SNVs", int(df["is_queryable_snv"].sum())],
            ["inside config window", int(df["inside_hbb_95kb_config_window"].sum())],
            ["promoter-side rows", int(df["hbg1_promoter_side"].eq("promoter_side").sum())],
            ],
            ["Metric", "Value"],
        )
    )
    lines.extend(
        [
            "",
            "## Source Effect Counts",
            "",
        ]
    )
    rows = []
    for effect_class, count in df["mpra_effect_class"].value_counts().items():
        rows.append([effect_class, int(count)])
    lines.extend(table(rows, ["mpra_effect_class", "rows"]))
    lines.extend(
        [
            "",
            "## Local Runner Readiness",
            "",
        ]
    )
    lines.extend(
        table(
            [
                ["generate-unified-atlas supports `--locus hbg1`", generator_supports_hbg1],
                ["locus-config alias supports `hbg1`", config_alias_supports_hbg1],
                ["data/hbg1_variants.csv exists", HBG1_VARIANTS_CSV.exists()],
                ["HBG1 atlas output exists", HBG1_ATLAS_CSV.exists()],
            ],
            ["Check", "Status"],
        )
    )
    lines.extend(
        [
            "",
            "Runner blocker: the current generic atlas path is not wired for HBG1. The next implementation step is a targeted HBG1 atlas runner/import, not population screening.",
        ]
    )
    lines.extend(
        [
            "",
            "## Source-Only Candidate Rows",
            "",
        ]
    )
    lines.extend(
        rows_table(
            candidates.sort_values(["P-Value", "Value"], ascending=[True, True]),
            ["Chromosome", "Position", "Ref", "Alt", "Value", "P-Value", "distance_to_hbg1_tss_bp", "nearest_feature_name"],
        )
    )
    lines.extend(["", "## Source-Only Control Rows", ""])
    lines.extend(
        rows_table(
            controls.sort_values(["distance_to_hbg1_tss_bp", "P-Value"], ascending=[True, False]),
            ["Chromosome", "Position", "Ref", "Alt", "Value", "P-Value", "distance_to_hbg1_tss_bp", "nearest_feature_name"],
        )
    )
    lines.extend(
        [
            "",
            "## Dry-Run / Live Gate",
            "",
            "- `population_filter.py` dry-run: **NOT RUN** because HBG1 source rows do not yet have ARCHCODE_LSSIM and frozen candidate/control gate columns.",
            "- Live gnomAD: **NOT RUN**.",
            "",
            "## Allowed Claim",
            "",
            "HBG1 is the best current source-import target because local MPRA-like rows provide non-empty candidate/control source pools inside the HBB 95kb sub-TAD config, but it is not a Paper 3 population cohort until ARCHCODE atlas values are generated.",
            "",
            "## Not Allowed",
            "",
            "- \"HBG1 validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Decision",
            "",
            f"**{decision}**",
            "",
            "Proceed only to an HBG1 ARCHCODE atlas/config import step. Do not run population screening from source-only rows.",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_hbg1_import_feasibility.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing HBG1 source table: {SOURCE}")
    source = pd.read_csv(SOURCE, sep="\t")
    config = load_config()
    annotated = annotate_source(source, config)
    candidates = annotated[annotated["hbg1_source_candidate"]].copy()
    controls = annotated[annotated["hbg1_source_control"]].copy()

    annotated.to_csv(OUT_ALL, index=False)
    candidates.to_csv(OUT_CANDIDATES, index=False)
    controls.to_csv(OUT_CONTROLS, index=False)
    write_report(annotated, candidates, controls, config)

    print(f"Wrote {OUT_ALL.relative_to(ROOT)} ({len(annotated)} rows)")
    print(f"Wrote {OUT_CANDIDATES.relative_to(ROOT)} ({len(candidates)} rows)")
    print(f"Wrote {OUT_CONTROLS.relative_to(ROOT)} ({len(controls)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
