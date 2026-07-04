#!/usr/bin/env python
"""Build a small HBG1 ARCHCODE source atlas for the Paper 3 gate.

This is a local source-to-ARCHCODE bridge. It uses Kircher HBG1 MPRA rows to
build a small effect/control input for the generic atlas runner, then rewrites
the output with source semantics suitable for Paper 3 review.

No gnomAD query is run here.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from paper3_hbg1_import_feasibility import annotate_source, load_config


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESULTS = ROOT / "results"

SOURCE = DATA / "kircher_HBG1_GRCh38.tsv"
GENERIC_INPUT = DATA / "hbg1_variants.csv"
RAW_ATLAS = RESULTS / "HBG1_Unified_Atlas_hbg1.csv"
RAW_SUMMARY = RESULTS / "UNIFIED_ATLAS_SUMMARY_hbg1.json"
CONTACT_DIR = RESULTS / "contact_matrices" / "HBG1"

OUT_INPUT = RESULTS / "PAPER3_HBG1_ARCHCODE_RUNNER_INPUT_20260503.csv"
OUT_ATLAS = RESULTS / "PAPER3_HBG1_ARCHCODE_SOURCE_ATLAS_20260503.csv"
OUT_CANDIDATES = RESULTS / "PAPER3_HBG1_ARCHCODE_CANDIDATES_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_HBG1_ARCHCODE_CONTROLS_20260503.csv"
OUT_MD = RESULTS / "PAPER3_HBG1_ARCHCODE_RUNNER_GATE_20260503.md"

N_PER_GROUP = 8


def norm(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def stable_id(group: str, row: pd.Series) -> str:
    return (
        f"KIRCHER_HBG1_{group.upper()}_"
        f"{int(row['Position'])}_{norm(row['Ref']).upper()}_{norm(row['Alt']).upper()}"
    )


def select_source_rows(annotated: pd.DataFrame) -> pd.DataFrame:
    candidates = annotated[annotated["hbg1_source_candidate"]].copy()
    controls = annotated[annotated["hbg1_source_control"]].copy()
    if candidates.empty:
        raise ValueError("No HBG1 source candidates available.")
    if controls.empty:
        raise ValueError("No HBG1 source controls available.")

    candidates["abs_mpra_value"] = candidates["Value"].astype(float).abs()
    candidates = candidates.sort_values(
        ["P-Value", "abs_mpra_value", "Position", "Ref", "Alt"],
        ascending=[True, False, True, True, True],
    ).head(N_PER_GROUP)

    controls = controls.copy()
    controls["abs_mpra_value"] = controls["Value"].astype(float).abs()
    selected_controls = []
    used: set[tuple[int, str, str]] = set()
    for _, candidate in candidates.iterrows():
        cand_dist = float(candidate["distance_to_hbg1_tss_bp"])
        available = controls[
            ~controls.apply(
                lambda row: (int(row["Position"]), norm(row["Ref"]), norm(row["Alt"])) in used,
                axis=1,
            )
        ].copy()
        if available.empty:
            break
        available["distance_delta_to_candidate"] = (
            available["distance_to_hbg1_tss_bp"].astype(float) - cand_dist
        ).abs()
        best = available.sort_values(
            ["distance_delta_to_candidate", "abs_mpra_value", "P-Value", "Position", "Ref", "Alt"],
            ascending=[True, True, False, True, True, True],
        ).iloc[0]
        used.add((int(best["Position"]), norm(best["Ref"]), norm(best["Alt"])))
        selected_controls.append(best)

    controls = pd.DataFrame(selected_controls).head(len(candidates))
    candidates["hbg1_source_group"] = "candidate"
    controls["hbg1_source_group"] = "control"
    selected = pd.concat([candidates, controls], ignore_index=True)
    selected["hbg1_source_group_rank"] = selected.groupby("hbg1_source_group").cumcount() + 1
    return selected


def build_runner_input(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in selected.iterrows():
        group = norm(row["hbg1_source_group"])
        label = "MPRA_Effect" if group == "candidate" else "MPRA_NearZero"
        clinical = "Kircher_MPRA_strong_effect" if group == "candidate" else "Kircher_MPRA_near_zero_control"
        rows.append(
            {
                "clinvar_id": stable_id(group, row),
                "chr": int(row["Chromosome"]),
                "position": int(row["Position"]),
                "ref": norm(row["Ref"]).upper(),
                "alt": norm(row["Alt"]).upper(),
                "category": "promoter",
                "hgvs_c": f"NC_000011.10:g.{int(row['Position'])}{norm(row['Ref']).upper()}>{norm(row['Alt']).upper()}",
                "hgvs_p": "",
                "clinical_significance": clinical,
                "label": label,
                "hbg1_source_group": group,
                "mpra_value": float(row["Value"]),
                "mpra_p_value": float(row["P-Value"]),
                "distance_to_hbg1_tss_bp": int(row["distance_to_hbg1_tss_bp"]),
                "nearest_feature_name": norm(row["nearest_feature_name"]),
                "paper3_label_note": (
                    "MPRA source-effect label for ARCHCODE runner; not a ClinVar disease label."
                ),
            }
        )
    return pd.DataFrame(rows)


def write_generic_input(runner_input: pd.DataFrame) -> None:
    if GENERIC_INPUT.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing temporary runner input: {GENERIC_INPUT}"
        )
    cols = [
        "clinvar_id",
        "chr",
        "position",
        "ref",
        "alt",
        "category",
        "hgvs_c",
        "hgvs_p",
        "clinical_significance",
        "label",
    ]
    runner_input[cols].to_csv(GENERIC_INPUT, index=False)


def run_archcode() -> None:
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise FileNotFoundError("npx executable was not found on PATH.")
    cmd = [npx, "tsx", "scripts/generate-unified-atlas.ts", "--locus", "hbg1"]
    completed = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    if not RAW_ATLAS.exists():
        raise FileNotFoundError(f"Expected atlas was not produced: {RAW_ATLAS}")


def cleanup_intermediate() -> None:
    if GENERIC_INPUT.exists():
        GENERIC_INPUT.unlink()
    if CONTACT_DIR.exists():
        resolved = CONTACT_DIR.resolve()
        allowed_parent = (RESULTS / "contact_matrices").resolve()
        if allowed_parent not in resolved.parents:
            raise RuntimeError(f"Refusing to remove unexpected path: {resolved}")
        shutil.rmtree(resolved)


def build_source_atlas(runner_input: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(RAW_ATLAS)
    merged = raw.merge(
        runner_input,
        left_on="ClinVar_ID",
        right_on="clinvar_id",
        how="left",
        validate="one_to_one",
    )
    if merged["hbg1_source_group"].isna().any():
        missing = merged[merged["hbg1_source_group"].isna()]["ClinVar_ID"].tolist()
        raise ValueError(f"ARCHCODE output rows missing source metadata: {missing}")

    q05 = float(merged["ARCHCODE_LSSIM"].astype(float).quantile(0.05))
    merged["hbg1_archcode_lssim_q05_runner"] = q05
    merged["hbg1_archcode_bottom5_in_runner"] = merged["ARCHCODE_LSSIM"].astype(float) <= q05
    merged["hbg1_archcode_candidate"] = (
        merged["hbg1_source_group"].eq("candidate")
        & merged["hbg1_archcode_bottom5_in_runner"]
    )
    merged["hbg1_archcode_control"] = (
        merged["hbg1_source_group"].eq("control")
        & ~merged["hbg1_archcode_bottom5_in_runner"]
    )
    merged["paper3_gate_status"] = "SOURCE_EFFECT_NOT_BOTTOM5"
    merged.loc[merged["hbg1_archcode_candidate"], "paper3_gate_status"] = "PRIMARY_LSSIM_SOURCE_CANDIDATE"
    merged.loc[merged["hbg1_archcode_control"], "paper3_gate_status"] = "POSITION_MATCHED_SOURCE_CONTROL"
    merged["paper3_semantics_note"] = (
        "Kircher MPRA source-effect row with ARCHCODE LSSIM; not ClinVar disease evidence."
    )

    candidates = merged[merged["hbg1_archcode_candidate"]].copy()
    controls = merged[merged["hbg1_archcode_control"]].copy()
    return merged, candidates, controls


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def write_report(source_atlas: pd.DataFrame, candidates: pd.DataFrame, controls: pd.DataFrame) -> None:
    bottom5 = source_atlas[source_atlas["hbg1_archcode_bottom5_in_runner"]]
    bottom5_effect = bottom5[bottom5["hbg1_source_group"].eq("candidate")]
    bottom5_control = bottom5[bottom5["hbg1_source_group"].eq("control")]
    if len(candidates) >= 3 and len(controls) >= 3:
        decision = "DRY_RUN_ONLY_SOURCE_SEMANTICS_REVIEW"
        verdict = "NOT YET"
        blocker = "HBG1 source rows now have ARCHCODE LSSIM and controls, but MPRA source-effect semantics are not germline disease semantics."
    elif len(candidates) and len(controls):
        decision = "REBUILD_ARCHCODE_SELECTION"
        verdict = "NOT YET"
        blocker = "ARCHCODE bottom-5% source candidate count is too small for a clean Paper 3 live gate."
    elif len(controls):
        decision = "STOP_NO_PRIMARY_ARCHCODE_CANDIDATES"
        verdict = "NO"
        blocker = "0 MPRA effect rows fall inside the ARCHCODE bottom-5% source-runner tail; the bottom-5% row is not a candidate."
    else:
        decision = "STOP_EMPTY_ARCHCODE_GATE"
        verdict = "NO"
        blocker = "ARCHCODE candidate/control gate is empty after source-atlas generation."

    rows = [
        ["source rows in runner", len(source_atlas)],
        ["MPRA effect rows", int(source_atlas["hbg1_source_group"].eq("candidate").sum())],
        ["MPRA near-zero controls", int(source_atlas["hbg1_source_group"].eq("control").sum())],
        ["ARCHCODE bottom-5% threshold", round(float(source_atlas["hbg1_archcode_lssim_q05_runner"].iloc[0]), 4)],
        ["bottom-5% MPRA effect rows", len(bottom5_effect)],
        ["bottom-5% near-zero control rows", len(bottom5_control)],
        ["primary LSSIM candidates", len(candidates)],
        ["position/source controls", len(controls)],
        ["raw ARCHCODE atlas", RAW_ATLAS.relative_to(ROOT)],
        ["raw ARCHCODE summary", RAW_SUMMARY.relative_to(ROOT)],
    ]
    lines = [
        "# Paper 3 HBG1 ARCHCODE Runner Gate",
        "",
        "Date: 2026-05-03",
        "",
        "Local source-to-ARCHCODE gate only. No live gnomAD query was run.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{decision}**",
        f"- Can HBG1 serve as the second regulatory-positive locus now? **{verdict}**",
        f"- Main blocker: {blocker}",
        "- Next required action: review source semantics and decide whether a source-effect MPRA cohort is acceptable before any strict live gate.",
        "",
        "## Counts",
        "",
    ]
    lines.extend(table(rows, ["Metric", "Value"]))
    lines.extend(
        [
            "",
            "## Candidate vs Controls",
            "",
            "| Group | n | source semantics | ARCHCODE rule | live eligible |",
            "|---|---:|---|---|---|",
            f"| Candidates | {len(candidates)} | Kircher MPRA effect rows | bottom 5% inside 16-row HBG1 source runner | NO |",
            f"| Controls | {len(controls)} | Kircher MPRA near-zero rows | not bottom 5%, position/source matched | NO |",
            "",
            "## Dry-Run Result",
            "",
            "| Group | local dry-run status | reason |",
            "|---|---|---|",
            f"| Candidates | BLOCKED_ZERO_ROWS | `{len(candidates)}` candidate rows after ARCHCODE gate |",
            f"| Controls | PREVIEW-ONLY eligible | `{len(controls)}` control rows after ARCHCODE gate |",
            "",
            "## Dry-Run Commands",
            "",
            "Candidate dry-run:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_HBG1_ARCHCODE_CANDIDATES_20260503.csv --chrom 11 --cohort-column hbg1_archcode_candidate --cohort-op equals --cohort-value true --locus-name HBG1_archcode_candidates --out paper3_hbg1_archcode_candidates_dryrun_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "Control dry-run:",
            "",
            "```powershell",
            "python scripts\\population_filter.py --atlas results\\PAPER3_HBG1_ARCHCODE_CONTROLS_20260503.csv --chrom 11 --cohort-column hbg1_archcode_control --cohort-op equals --cohort-value true --locus-name HBG1_archcode_controls --out paper3_hbg1_archcode_controls_dryrun_20260503 --rate-limit 3.0 --dry-run",
            "```",
            "",
            "## Allowed Claim",
            "",
            "HBG1 now has a small local Kircher MPRA source-effect cohort with ARCHCODE LSSIM values and matched near-zero source controls, but it remains a source-semantics review target rather than a population-positive Paper 3 locus.",
            "",
            "## Not Allowed",
            "",
            "- \"HBG1 validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_hbg1_archcode_runner.py",
            "```",
            "",
            "The runner invokes:",
            "",
            "```powershell",
            "npx tsx scripts\\generate-unified-atlas.ts --locus hbg1",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing HBG1 source table: {SOURCE}")
    source = pd.read_csv(SOURCE, sep="\t")
    annotated = annotate_source(source, load_config())
    selected = select_source_rows(annotated)
    runner_input = build_runner_input(selected)
    OUT_INPUT.parent.mkdir(parents=True, exist_ok=True)
    runner_input.to_csv(OUT_INPUT, index=False)

    try:
        write_generic_input(runner_input)
        run_archcode()
    finally:
        cleanup_intermediate()

    source_atlas, candidates, controls = build_source_atlas(runner_input)
    source_atlas.to_csv(OUT_ATLAS, index=False)
    candidates.to_csv(OUT_CANDIDATES, index=False)
    controls.to_csv(OUT_CONTROLS, index=False)
    write_report(source_atlas, candidates, controls)

    print(f"Wrote {OUT_INPUT.relative_to(ROOT)} ({len(runner_input)} rows)")
    print(f"Wrote {OUT_ATLAS.relative_to(ROOT)} ({len(source_atlas)} rows)")
    print(f"Wrote {OUT_CANDIDATES.relative_to(ROOT)} ({len(candidates)} rows)")
    print(f"Wrote {OUT_CONTROLS.relative_to(ROOT)} ({len(controls)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
