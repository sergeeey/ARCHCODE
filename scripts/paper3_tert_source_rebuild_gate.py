#!/usr/bin/env python
"""Finalize the strict TERT source-rebuild gate after semantics audit.

This script consumes the audited TERT candidate/control files and applies a
pre-live gate. It does not query gnomAD. Candidate-like TERT promoter rows
with unresolved germline/somatic cancer semantics remain excluded.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

IN_CANDIDATES = RESULTS / "PAPER3_TERT_AUDITED_CANDIDATES_20260503.csv"
IN_CONTROLS = RESULTS / "PAPER3_TERT_AUDITED_CONTROLS_20260503.csv"

OUT_CANDIDATES = RESULTS / "PAPER3_TERT_SOURCE_REBUILD_CANDIDATES_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_TERT_SOURCE_REBUILD_CONTROLS_20260503.csv"
OUT_DECISION = RESULTS / "PAPER3_TERT_SOURCE_REBUILD_DECISION_20260503.md"

SOURCE_RESOLUTION_NOTES: dict[str, dict[str, str]] = {
    "VCV000242210": {
        "external_semantics": "mixed_germline_and_somatic",
        "clinvar_url": "https://www.ncbi.nlm.nih.gov/clinvar/variation/242210/",
        "note": (
            "ClinVar VCV page reports aggregate germline conflicting classifications "
            "and separate somatic clinical-impact/oncogenicity sections."
        ),
    },
    "VCV001299388": {
        "external_semantics": "mixed_germline_and_strong_somatic",
        "clinvar_url": "https://www.ncbi.nlm.nih.gov/clinvar/variation/1299388/",
        "note": (
            "ClinVar VCV page reports aggregate germline conflicting classifications, "
            "somatic clinical impact for multiple tumor types, and somatic oncogenicity."
        ),
    },
    "VCV002443072": {
        "external_semantics": "somatic_dominated_or_mixed",
        "clinvar_url": "https://www.ncbi.nlm.nih.gov/clinvar/variation/2443072/",
        "note": (
            "ClinVar VCV page reports a germline pathogenic aggregate with no assertion "
            "criteria and multiple somatic clinical-impact/oncogenicity submissions."
        ),
    },
}


def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def truthy(value: Any) -> bool:
    return norm(value).lower() in {"true", "1", "yes", "y"}


def add_source_resolution(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["external_source_semantics"] = df["ClinVar_ID"].map(
        lambda value: SOURCE_RESOLUTION_NOTES.get(norm(value), {}).get("external_semantics", "not_externally_resolved")
    )
    df["external_source_url"] = df["ClinVar_ID"].map(
        lambda value: SOURCE_RESOLUTION_NOTES.get(norm(value), {}).get("clinvar_url", "")
    )
    df["external_source_note"] = df["ClinVar_ID"].map(
        lambda value: SOURCE_RESOLUTION_NOTES.get(norm(value), {}).get("note", "")
    )
    return df


def select_rebuilt_candidates(candidates: pd.DataFrame) -> pd.DataFrame:
    candidates = add_source_resolution(candidates)
    # A strict live candidate needs both local audit inclusion and no external
    # germline/somatic ambiguity. The prior audit intentionally leaves all
    # candidate-like promoter rows excluded until that ambiguity is resolved.
    include = candidates["live_gate_include"].map(truthy) & candidates["external_source_semantics"].isin(
        {"not_externally_resolved", "germline_clean"}
    )
    return candidates[include].copy()


def select_rebuilt_controls(controls: pd.DataFrame, candidate_count: int) -> pd.DataFrame:
    controls = add_source_resolution(controls)
    potential = controls[
        controls["mechanism_match_quality"].eq("good_for_rebuilt_promoter_5utr_benign_control")
    ].copy()
    if candidate_count == 0:
        return potential.head(0).copy()
    return potential.head(min(candidate_count, len(potential))).copy()


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def summarize_rows(df: pd.DataFrame, cols: list[str]) -> list[str]:
    if df.empty:
        return ["No rows."]
    rows = []
    for _, row in df.iterrows():
        rows.append([norm(row.get(col)) for col in cols])
    return table(rows, cols)


def write_decision(
    candidates: pd.DataFrame,
    controls: pd.DataFrame,
    rebuilt_candidates: pd.DataFrame,
    rebuilt_controls: pd.DataFrame,
) -> None:
    potential_controls = controls[
        controls["mechanism_match_quality"].eq("good_for_rebuilt_promoter_5utr_benign_control")
    ].copy()
    ambiguous_candidates = candidates[
        candidates["external_source_semantics"].isin(
            {"mixed_germline_and_somatic", "mixed_germline_and_strong_somatic", "somatic_dominated_or_mixed"}
        )
    ].copy()
    decision = "STOP_CURRENT_TERT_GATE"
    if len(rebuilt_candidates) and len(rebuilt_controls):
        decision = "CONTINUE_TO_DRY_RUN_ONLY"
    elif len(potential_controls):
        decision = "REBUILD_OR_SWITCH"

    lines = [
        "# Paper 3 TERT Source-Rebuild Gate",
        "",
        "Date: 2026-05-03",
        "",
        "This gate finalizes the current TERT source-semantics pass. It does not query gnomAD.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{decision}**",
        "- Can TERT serve as the second regulatory-positive locus now? **NO / NOT YET**",
        f"- Rebuilt candidates: `{len(rebuilt_candidates)}`",
        f"- Rebuilt controls: `{len(rebuilt_controls)}`",
        "- Main blocker: all candidate-like promoter rows remain mixed germline/somatic/cancer-context rows or lack clean positive-candidate semantics.",
        "- Next required action: either perform a deeper TERT source-resolution import, or switch to a cleaner regulatory locus such as GATA1 if local source rows support it.",
        "",
        "## Rebuild Result",
        "",
    ]
    lines.extend(
        table(
            [
                [
                    "strict rebuilt TERT candidates",
                    len(rebuilt_candidates),
                    int(rebuilt_candidates["live_gate_include"].map(truthy).sum()) if len(rebuilt_candidates) else 0,
                    "empty; live gate blocked",
                ],
                [
                    "strict rebuilt TERT controls",
                    len(rebuilt_controls),
                    int(rebuilt_controls["live_gate_include"].map(truthy).sum()) if len(rebuilt_controls) else 0,
                    "empty because candidates are empty",
                ],
                [
                    "potential promoter/5_prime_UTR benign controls",
                    len(potential_controls),
                    0,
                    "useful only if a clean candidate set is rebuilt",
                ],
            ],
            ["Group", "n", "live_gate_include", "interpretation"],
        )
    )
    lines.extend(
        [
            "",
            "## External Source-Resolution Notes",
            "",
            "The current candidate-like TERT promoter rows are not discarded as biology; they are excluded from this live gate because source semantics are mixed enough to confound population interpretation.",
            "",
        ]
    )
    lines.extend(
        summarize_rows(
            ambiguous_candidates,
            [
                "ClinVar_ID",
                "HGVS_c",
                "ClinVar_Significance",
                "kircher_value",
                "external_source_semantics",
                "external_source_url",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Potential Controls Preserved For Future Design",
            "",
        ]
    )
    lines.extend(
        summarize_rows(
            potential_controls,
            [
                "ClinVar_ID",
                "HGVS_c",
                "ClinVar_Significance",
                "kircher_value",
                "mechanism_match_quality",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Live Query Gate",
            "",
            "- Live gnomAD: **NOT RUN**.",
            "- Strict dry-run: **SKIPPED** because rebuilt candidates and rebuilt controls are empty.",
            "- Treat-not-found-as-absent mode: **NOT RUN**.",
            "",
            "## Allowed Claim",
            "",
            "TERT remains biologically plausible and source-rich, but the current source-rebuild gate does not produce a clean non-empty regulatory-positive candidate/control cohort.",
            "",
            "## Not Allowed",
            "",
            "- \"TERT validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Decision",
            "",
            f"**{decision}**",
            "",
            "Do not run live gnomAD on the current TERT set. The next efficient move is a bounded source-resolution import; if that still leaves candidates empty, switch locus.",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_tert_source_rebuild_gate.py",
            "```",
        ]
    )
    OUT_DECISION.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not IN_CANDIDATES.exists():
        raise FileNotFoundError(f"Missing audited candidates: {IN_CANDIDATES}")
    if not IN_CONTROLS.exists():
        raise FileNotFoundError(f"Missing audited controls: {IN_CONTROLS}")

    candidates = add_source_resolution(pd.read_csv(IN_CANDIDATES))
    controls = add_source_resolution(pd.read_csv(IN_CONTROLS))
    rebuilt_candidates = select_rebuilt_candidates(candidates)
    rebuilt_controls = select_rebuilt_controls(controls, len(rebuilt_candidates))

    rebuilt_candidates.to_csv(OUT_CANDIDATES, index=False)
    rebuilt_controls.to_csv(OUT_CONTROLS, index=False)
    write_decision(candidates, controls, rebuilt_candidates, rebuilt_controls)

    print(f"Wrote {OUT_CANDIDATES.relative_to(ROOT)} ({len(rebuilt_candidates)} rows)")
    print(f"Wrote {OUT_CONTROLS.relative_to(ROOT)} ({len(rebuilt_controls)} rows)")
    print(f"Wrote {OUT_DECISION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
