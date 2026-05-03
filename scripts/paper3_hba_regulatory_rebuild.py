#!/usr/bin/env python
"""Rebuild a conservative Paper 3 HBA regulatory cohort gate.

This script uses existing local HBA/HBA1 source artifacts only. It does not
recover new alleles or query gnomAD. The primary gate is intentionally strict:
queryable, non-synthetic, regulatory-subclass SNVs must also fall in the
bottom 5 percent of the HBA queryable source locus by ARCHCODE_LSSIM.
"""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"
CONFIG = ROOT / "config" / "locus"
SCRIPTS = ROOT / "scripts"

SOURCE_ATLAS = RESULTS / "PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv"
CONFIGS = [
    CONFIG / "hba1_90kb_focused.json",
    CONFIG / "hba1_300kb.json",
]

OUT_CANDIDATES = RESULTS / "PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_HBA_POSITION_CONTROLS_20260503.csv"
OUT_REPORT = RESULTS / "PAPER3_HBA_REGULATORY_REBUILD_20260503.md"

SAFE_BASES = {"A", "C", "G", "T"}
SYNTHETIC_MARKERS = ("synthetic", "mock", "demo")
CODING_SUBCLASSES = {
    "coding_missense",
    "coding_nonsense",
    "coding_synonymous",
    "coding_frameshift",
    "coding_other",
}
REGULATORY_SUBCLASSES = {
    "promoter_or_5_prime_UTR",
    "5_prime_UTR",
    "intronic",
    "splice_region",
    "enhancer_like",
    "3_prime_UTR",
}


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def lower_blob(row: dict[str, Any], columns: list[str]) -> str:
    return " ".join(norm(row.get(col)) for col in columns).lower()


def is_synthetic_row(row: dict[str, Any]) -> bool:
    blob = lower_blob(
        row,
        [
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
        ],
    )
    return any(marker in blob for marker in SYNTHETIC_MARKERS)


def is_queryable_snv(row: dict[str, Any]) -> bool:
    ref = norm(row.get("Ref") or row.get("ref")).upper()
    alt = norm(row.get("Alt") or row.get("alt")).upper()
    return len(ref) == 1 and len(alt) == 1 and ref in SAFE_BASES and alt in SAFE_BASES and ref != alt


def classify_mechanism(row: dict[str, Any]) -> str:
    category = norm(row.get("Category") or row.get("category")).lower()
    hgvs_c = norm(row.get("HGVS_c") or row.get("hgvs_c"))
    hgvs_p = norm(row.get("HGVS_p") or row.get("hgvs_p"))
    blob = f"{category} {hgvs_c} {hgvs_p}".lower()

    if "frameshift" in blob or "fs" in hgvs_p.lower():
        return "coding_frameshift"
    if "nonsense" in blob or "ter" in hgvs_p.lower() or "*" in hgvs_p:
        return "coding_nonsense"
    if "missense" in blob or (hgvs_p and "=" not in hgvs_p):
        return "coding_missense"
    if "synonymous" in blob or "=" in hgvs_p:
        return "coding_synonymous"
    if re.search(r"c\.-\d+", hgvs_c):
        return "promoter_or_5_prime_UTR"
    if re.search(r"c\.\*\d+", hgvs_c):
        return "3_prime_UTR"
    splice_match = re.search(r"c\.\d+([+-])(\d+)", hgvs_c)
    if category == "splice":
        return "splice_region"
    if splice_match:
        offset = int(splice_match.group(2))
        return "splice_region" if offset <= 2 else "intronic"
    if category == "intronic":
        return "intronic"
    if any(token in category for token in ["promoter", "utr", "regulatory"]):
        return "promoter_or_5_prime_UTR"
    if any(token in category for token in ["enhancer", "cre", "dhs"]):
        return "enhancer_like"
    if category in {"other", ""}:
        return "other_unresolved"
    return "coding_other"


def load_features() -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    for path in CONFIGS:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        config_id = data.get("id", path.stem)
        for feature_type, rows in (data.get("features") or {}).items():
            if not isinstance(rows, list):
                continue
            for item in rows:
                if feature_type == "genes":
                    start = int(item["start"])
                    end = int(item["end"])
                    position = (start + end) // 2
                else:
                    position = int(item["position"])
                    start = position
                    end = position
                features.append(
                    {
                        "config_id": config_id,
                        "feature_type": feature_type,
                        "name": item.get("name", feature_type),
                        "position": position,
                        "start": start,
                        "end": end,
                    }
                )
    return features


def nearest_feature(pos: int, features: list[dict[str, Any]]) -> dict[str, Any]:
    if not features:
        return {
            "nearest_config": "",
            "nearest_feature_type": "",
            "nearest_feature_name": "",
            "nearest_feature_distance_bp": "",
        }
    best = min(
        features,
        key=lambda item: 0
        if int(item["start"]) <= pos <= int(item["end"])
        else min(abs(pos - int(item["start"])), abs(pos - int(item["end"])), abs(pos - int(item["position"]))),
    )
    if int(best["start"]) <= pos <= int(best["end"]):
        distance = 0
    else:
        distance = min(
            abs(pos - int(best["start"])),
            abs(pos - int(best["end"])),
            abs(pos - int(best["position"])),
        )
    return {
        "nearest_config": best["config_id"],
        "nearest_feature_type": best["feature_type"],
        "nearest_feature_name": best["name"],
        "nearest_feature_distance_bp": distance,
    }


def has_columns(path: Path, required: list[str]) -> tuple[bool, list[str]]:
    if path.suffix.lower() != ".csv" or not path.exists():
        return False, required
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
    missing = [col for col in required if col not in header]
    return len(missing) == 0, missing


def csv_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, reader.fieldnames or []


def inventory_hba_files() -> list[dict[str, Any]]:
    files: list[Path] = []
    for base in [RESULTS, DATA, CONFIG, SCRIPTS]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            name = path.name.lower()
            if not path.is_file() or path.suffix.lower() == ".pyc":
                continue
            if "hba" not in name and "hba1" not in name and "hba2" not in name:
                continue
            files.append(path)

    inventory = []
    for path in sorted(files):
        exists = path.exists()
        rows_n = 0
        queryable = 0
        regulatory = 0
        synthetic = 0
        status = "not_tabular"
        if path.suffix.lower() == ".csv":
            try:
                rows, columns = csv_rows(path)
                rows_n = len(rows)
                queryable = sum(1 for row in rows if is_queryable_snv(row))
                regulatory = sum(
                    1
                    for row in rows
                    if is_queryable_snv(row)
                    and classify_mechanism(row) in REGULATORY_SUBCLASSES
                    and not is_synthetic_row(row)
                )
                synthetic = sum(1 for row in rows if is_synthetic_row(row))
                required = ["Position_GRCh38", "Ref", "Alt", "HGVS_c", "Category", "Source", "ARCHCODE_LSSIM"]
                _, missing = has_columns(path, required)
                if synthetic and synthetic == rows_n:
                    status = "synthetic_or_mutagenesis_only"
                elif missing:
                    status = "missing " + ",".join(missing)
                elif queryable == 0:
                    status = "not_queryable_ref_alt"
                else:
                    status = "candidate_space_available" if regulatory else "queryable_coding_only"
            except Exception as exc:  # pragma: no cover - defensive report path
                status = f"read_error {exc}"
        elif path.suffix.lower() == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                feature_keys = sorted((data.get("features") or {}).keys())
                if feature_keys:
                    status = "features " + ",".join(feature_keys)
                else:
                    status = "json_no_locus_features"
            except Exception as exc:  # pragma: no cover - defensive report path
                status = f"json_error {exc}"
        elif path.suffix.lower() == ".txt":
            try:
                rows_n = len(path.read_text(encoding="utf-8").splitlines())
                status = "text_positions_only"
            except Exception as exc:  # pragma: no cover - defensive report path
                status = f"text_error {exc}"
        elif path.suffix.lower() == ".py":
            status = "script"
        inventory.append(
            {
                "File": str(path.relative_to(ROOT)),
                "Exists": exists,
                "Rows": rows_n,
                "Queryable SNVs": queryable,
                "Regulatory candidates": regulatory,
                "Synthetic risk": synthetic,
                "Status": status,
            }
        )
    return inventory


def feature_config_summary() -> dict[str, bool]:
    keys: set[str] = set()
    for path in CONFIGS:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            keys.update((data.get("features") or {}).keys())
    lower_keys = {key.lower() for key in keys}
    return {
        "promoter": any("promoter" in key for key in lower_keys),
        "enhancer": any("enhancer" in key for key in lower_keys),
        "CRE": any("cre" in key for key in lower_keys),
        "DHS": any("dhs" in key for key in lower_keys),
        "CTCF": any("ctcf" in key for key in lower_keys),
        "TAD": any("tad" in key for key in lower_keys),
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    lines = ["|" + "|".join(columns) + "|", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        values = [str(row.get(col, "")).replace("\n", " ") for col in columns]
        lines.append("|" + "|".join(values) + "|")
    return lines


def select_position_controls(candidates: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    selected = []
    used: set[str] = set()
    if candidates.empty:
        return pool.head(0).copy()

    for _, candidate in candidates.iterrows():
        choices = pool[
            (~pool["ClinVar_ID"].isin(used))
            & (pool["ClinVar_ID"] != candidate["ClinVar_ID"])
            & (~pool["primary_low_lssim_candidate"])
        ].copy()
        if choices.empty:
            continue
        choices["same_subclass"] = choices["mechanism_subclass"] == candidate["mechanism_subclass"]
        choices["same_feature"] = choices["nearest_feature_name"] == candidate["nearest_feature_name"]
        choices["position_distance"] = (
            choices["Position_GRCh38"].astype(int) - int(candidate["Position_GRCh38"])
        ).abs()
        choices["feature_distance_delta"] = (
            choices["nearest_feature_distance_bp"].astype(int)
            - int(candidate["nearest_feature_distance_bp"])
        ).abs()
        choices["lssim_delta"] = (
            choices["ARCHCODE_LSSIM"].astype(float) - float(candidate["ARCHCODE_LSSIM"])
        ).abs()
        chosen = choices.sort_values(
            ["same_subclass", "same_feature", "feature_distance_delta", "position_distance", "lssim_delta"],
            ascending=[False, False, True, True, True],
        ).iloc[0]
        used.add(str(chosen["ClinVar_ID"]))
        selected.append(chosen.drop(labels=[c for c in ["same_subclass", "same_feature", "position_distance", "feature_distance_delta", "lssim_delta"] if c in chosen.index]))
    return pd.DataFrame(selected)


def main() -> None:
    if not SOURCE_ATLAS.exists():
        raise FileNotFoundError(f"Required HBA queryable source atlas not found: {SOURCE_ATLAS}")

    df = pd.read_csv(SOURCE_ATLAS)
    features = load_features()

    df["is_synthetic_or_demo"] = df.apply(lambda row: is_synthetic_row(row.to_dict()), axis=1)
    df["is_queryable_snv_rechecked"] = df.apply(lambda row: is_queryable_snv(row.to_dict()), axis=1)
    df["mechanism_subclass"] = df.apply(lambda row: classify_mechanism(row.to_dict()), axis=1)
    df["is_coding_subclass"] = df["mechanism_subclass"].isin(CODING_SUBCLASSES)
    df["is_regulatory_subclass"] = df["mechanism_subclass"].isin(REGULATORY_SUBCLASSES)

    feature_rows = [nearest_feature(int(pos), features) for pos in df["Position_GRCh38"]]
    feature_df = pd.DataFrame(feature_rows)
    df = pd.concat([df, feature_df], axis=1)

    usable = df[(~df["is_synthetic_or_demo"]) & (df["is_queryable_snv_rechecked"])].copy()
    locus_q05 = float(usable["ARCHCODE_LSSIM"].quantile(0.05))
    regulatory = usable[usable["is_regulatory_subclass"]].copy()
    regulatory_q05 = float(regulatory["ARCHCODE_LSSIM"].quantile(0.05)) if len(regulatory) else float("nan")

    usable["locus_bottom5_lssim_threshold"] = locus_q05
    usable["primary_low_lssim_candidate"] = usable["is_regulatory_subclass"] & (
        usable["ARCHCODE_LSSIM"] <= locus_q05
    )
    usable["secondary_lssim_lt_0_99_candidate"] = usable["is_regulatory_subclass"] & (
        usable["ARCHCODE_LSSIM"] < 0.99
    )
    usable["exploratory_regulatory_subset_bottom5"] = False
    if len(regulatory):
        usable.loc[
            usable["is_regulatory_subclass"] & (usable["ARCHCODE_LSSIM"] <= regulatory_q05),
            "exploratory_regulatory_subset_bottom5",
        ] = True
    usable["candidate_gate_status"] = "not_regulatory_subclass"
    usable.loc[usable["is_regulatory_subclass"], "candidate_gate_status"] = "regulatory_not_locus_bottom5"
    usable.loc[usable["primary_low_lssim_candidate"], "candidate_gate_status"] = "primary_gate_candidate"
    usable.loc[usable["secondary_lssim_lt_0_99_candidate"], "candidate_gate_status"] = (
        usable.loc[usable["secondary_lssim_lt_0_99_candidate"], "candidate_gate_status"]
        + ";secondary_lssim_lt_0_99"
    )

    candidate_space = usable[usable["is_regulatory_subclass"]].copy()
    primary_candidates = candidate_space[candidate_space["primary_low_lssim_candidate"]].copy()
    controls = select_position_controls(primary_candidates, candidate_space).copy()
    if len(controls):
        controls["selected_position_control"] = True
    else:
        controls = candidate_space.head(0).copy()
        controls["selected_position_control"] = pd.Series(dtype=bool)

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
        "ARCHCODE_LSSIM",
        "mechanism_subclass",
        "nearest_config",
        "nearest_feature_type",
        "nearest_feature_name",
        "nearest_feature_distance_bp",
        "anchor_start",
        "anchor_end",
        "other_anchor",
        "count",
        "pvalue",
        "is_synthetic_or_demo",
        "is_queryable_snv_rechecked",
        "is_regulatory_subclass",
        "locus_bottom5_lssim_threshold",
        "primary_low_lssim_candidate",
        "secondary_lssim_lt_0_99_candidate",
        "exploratory_regulatory_subset_bottom5",
        "candidate_gate_status",
    ]
    present_candidate_columns = [col for col in output_columns if col in candidate_space.columns]
    candidate_space[present_candidate_columns].to_csv(OUT_CANDIDATES, index=False)

    control_columns = [col for col in output_columns if col in controls.columns]
    if "selected_position_control" in controls.columns:
        control_columns.append("selected_position_control")
    controls[control_columns].to_csv(OUT_CONTROLS, index=False)

    bottom5_rows = usable[usable["ARCHCODE_LSSIM"] <= locus_q05].copy()
    config_summary = feature_config_summary()
    inventory = inventory_hba_files()

    report: list[str] = [
        "# Paper 3 HBA Regulatory Rebuild",
        "",
        "Date: 2026-05-03",
        "",
        "This is a gate artifact, not a manuscript result.",
        "",
        "## Source Inventory",
        "",
        *markdown_table(
            inventory,
            [
                "File",
                "Exists",
                "Rows",
                "Queryable SNVs",
                "Regulatory candidates",
                "Synthetic risk",
                "Status",
            ],
        ),
        "",
        "## Config Feature Audit",
        "",
        "| Feature | Present in local HBA configs |",
        "|---|---:|",
    ]
    for key in ["promoter", "enhancer", "CRE", "DHS", "CTCF", "TAD"]:
        report.append(f"| {key} | {str(config_summary[key])} |")

    report.extend(
        [
            "",
            "## Rebuild Inputs",
            "",
            f"- Primary queryable source atlas: `{SOURCE_ATLAS.relative_to(ROOT)}`",
            "- HBA2-specific source rows found locally: `0`",
            f"- Queryable non-synthetic source rows: `{len(usable)}`",
            f"- Queryable regulatory-subclass source rows: `{len(candidate_space)}`",
            f"- Whole-locus bottom-5% LSSIM threshold: `{locus_q05:.6g}`",
            f"- Regulatory-subset exploratory bottom-5% threshold: `{regulatory_q05:.6g}`",
            "",
            "## Whole-Locus Bottom-5% Rows",
            "",
            "| ClinVar_ID | Position_GRCh38 | Ref | Alt | HGVS_c | Category | mechanism_subclass | ARCHCODE_LSSIM |",
            "|---|---:|---|---|---|---|---|---:|",
        ]
    )
    for _, row in bottom5_rows.sort_values("ARCHCODE_LSSIM").iterrows():
        report.append(
            "| {ClinVar_ID} | {Position_GRCh38} | {Ref} | {Alt} | {HGVS_c} | {Category} | {mechanism_subclass} | {ARCHCODE_LSSIM:.4f} |".format(
                **row.to_dict()
            )
        )

    report.extend(
        [
            "",
            "## Candidate Gate",
            "",
            "| Gate | n | Interpretation |",
            "|---|---:|---|",
            f"| regulatory candidate space | {len(candidate_space)} | Queryable non-synthetic regulatory-subclass rows exist. |",
            f"| primary low-LSSIM regulatory candidates | {int(usable['primary_low_lssim_candidate'].sum())} | Requires regulatory subclass and whole-locus bottom 5% LSSIM. |",
            f"| secondary regulatory LSSIM < 0.99 | {int(usable['secondary_lssim_lt_0_99_candidate'].sum())} | Boundary-only gate; not primary. |",
            f"| exploratory regulatory-subset bottom 5% | {int(usable['exploratory_regulatory_subset_bottom5'].sum())} | Not used for the primary Paper 3 gate because it changes the denominator post hoc. |",
            f"| selected position controls | {len(controls)} | Controls are selected only after primary candidates exist. |",
            "",
            "## Dry-Run Commands",
            "",
            "Candidate dry-run gate:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv --chrom 16 --cohort-column primary_low_lssim_candidate --cohort-op equals --cohort-value true --locus-name HBA --out paper3_hba_candidates_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "Control dry-run gate:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_HBA_POSITION_CONTROLS_20260503.csv --chrom 16 --cohort-column selected_position_control --cohort-op equals --cohort-value true --locus-name HBA_position_controls --out paper3_hba_position_controls_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "## Gate Result",
            "",
            "The current local HBA queryable source does not produce a primary low-LSSIM regulatory cohort. The low-LSSIM tail is coding/nonsense/missense, while queryable regulatory-subclass rows sit outside the primary bottom-5% and outside the secondary `LSSIM < 0.99` boundary.",
        ]
    )

    OUT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_CANDIDATES}")
    print(f"Wrote {OUT_CONTROLS}")
    print(f"Wrote {OUT_REPORT}")
    print(f"Primary candidates: {int(usable['primary_low_lssim_candidate'].sum())}")
    print(f"Selected controls: {len(controls)}")


if __name__ == "__main__":
    main()
