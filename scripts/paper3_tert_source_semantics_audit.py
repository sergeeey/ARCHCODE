#!/usr/bin/env python
"""Audit TERT candidate/control source semantics before any live query.

The audit is local-source only. It uses the frozen Paper 3 TERT dry-run
candidate/control CSVs and does not query gnomAD or external services.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

IN_CANDIDATES = RESULTS / "PAPER3_TERT_REGULATORY_CANDIDATES_20260503.csv"
IN_CONTROLS = RESULTS / "PAPER3_TERT_POSITION_CONTROLS_20260503.csv"

OUT_MD = RESULTS / "PAPER3_TERT_SOURCE_SEMANTICS_AUDIT_20260503.md"
OUT_CANDIDATES = RESULTS / "PAPER3_TERT_AUDITED_CANDIDATES_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_TERT_AUDITED_CONTROLS_20260503.csv"

SAFE_BASES = {"A", "C", "G", "T"}


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def as_bool(value: Any) -> bool:
    return norm(value).lower() in {"true", "1", "yes", "y"}


def is_queryable_snv(row: pd.Series) -> bool:
    ref = norm(row.get("Ref")).upper()
    alt = norm(row.get("Alt")).upper()
    return len(ref) == 1 and len(alt) == 1 and ref in SAFE_BASES and alt in SAFE_BASES and ref != alt


def is_promoter_or_5utr(row: pd.Series) -> bool:
    category = norm(row.get("Category")).lower()
    mechanism = norm(row.get("mechanism_subclass")).lower()
    hgvs_c = norm(row.get("HGVS_c")).lower()
    return (
        "promoter" in category
        or "5_prime_utr" in category
        or "5'utr" in category
        or "promoter" in mechanism
        or "5_prime_utr" in mechanism
        or "c.-" in hgvs_c
    )


def is_splice_or_intronic(row: pd.Series) -> bool:
    category = norm(row.get("Category")).lower()
    mechanism = norm(row.get("mechanism_subclass")).lower()
    hgvs_c = norm(row.get("HGVS_c")).lower()
    return (
        "splice" in category
        or "intronic" in category
        or "splice" in mechanism
        or "intronic" in mechanism
        or "+" in hgvs_c
    )


def clinvar_semantics(row: pd.Series) -> str:
    significance = norm(row.get("ClinVar_Significance")).lower()
    if "conflicting" in significance:
        return "conflicting_pathogenicity"
    if "pathogenic" in significance:
        return "pathogenic_or_likely_pathogenic"
    if "benign" in significance:
        return "benign_or_likely_benign"
    return "unresolved_clinvar_semantics"


def kircher_direction(row: pd.Series) -> str:
    if not as_bool(row.get("kircher_exact_match")):
        return "no_exact_kircher_overlap"
    try:
        value = float(row.get("kircher_value"))
    except Exception:
        return "exact_kircher_overlap_value_missing"
    if value >= 0.5:
        return "positive_kircher_effect_score"
    if value <= -0.2:
        return "negative_kircher_effect_score"
    return "near_zero_kircher_effect_score"


def audit_candidate(row: pd.Series) -> dict[str, Any]:
    promoter = is_promoter_or_5utr(row)
    splice_intronic = is_splice_or_intronic(row)
    exact_kircher = as_bool(row.get("kircher_exact_match"))
    semantics = clinvar_semantics(row)
    queryable = is_queryable_snv(row)

    if not queryable:
        flag = "queryability_blocker"
        reason = "exclude_ref_alt_not_queryable_snv"
        local_interpretation = "not_assessable_queryability_blocker"
        note = "Ref/Alt are not valid single-nucleotide alleles."
    elif not promoter:
        flag = "not_primary_regulatory_promoter_5utr"
        reason = "exclude_not_promoter_or_5_prime_UTR"
        local_interpretation = "not_primary_promoter_5utr_regulatory"
        note = "Row is splice/intronic or coding-adjacent, not a primary TERT promoter/5_prime_UTR row."
    elif not exact_kircher:
        flag = "missing_exact_kircher_overlap"
        reason = "exclude_missing_exact_kircher_source_overlap"
        local_interpretation = "promoter_5utr_without_exact_source_overlap"
        note = "Row lacks exact local Kircher source overlap."
    elif semantics in {"pathogenic_or_likely_pathogenic", "conflicting_pathogenicity"}:
        flag = "source_semantics_ambiguous_possible_cancer_context"
        reason = "exclude_until_germline_vs_somatic_source_semantics_resolved"
        local_interpretation = "promoter_5utr_candidate_like_but_cancer_somatic_ambiguous"
        note = (
            "Promoter/5_prime_UTR row is candidate-like but ClinVar semantics are "
            "pathogenic/conflicting in TERT, where cancer and somatic contexts can be mixed."
        )
    elif semantics == "benign_or_likely_benign":
        flag = "benign_control_like_not_positive_candidate"
        reason = "exclude_from_positive_candidate_set_benign_control_like"
        local_interpretation = "promoter_5utr_benign_germline_compatible_control_like"
        note = "Promoter/5_prime_UTR exact-overlap row is useful as control-like source context, not positive evidence."
    else:
        flag = "unresolved_source_semantics"
        reason = "exclude_unresolved_source_semantics"
        local_interpretation = "unresolved_local_germline_semantics"
        note = "Local source semantics are not specific enough for a live candidate gate."

    return {
        "is_queryable_snv_audit": queryable,
        "is_promoter_or_5_prime_UTR_audit": promoter,
        "is_splice_or_intronic_audit": splice_intronic,
        "exact_kircher_overlap_audit": exact_kircher,
        "kircher_effect_direction": kircher_direction(row),
        "clinvar_semantics_audit": semantics,
        "local_germline_regulatory_interpretation": local_interpretation,
        "source_semantics_flag": flag,
        "mechanism_match_quality": "candidate_row_not_control",
        "exclude_before_live": True,
        "exclude_before_live_reason": reason,
        "live_gate_include": False,
        "audit_note": note,
    }


def audit_control(row: pd.Series, candidate_gate_nonempty: bool) -> dict[str, Any]:
    promoter = is_promoter_or_5utr(row)
    splice_intronic = is_splice_or_intronic(row)
    exact_kircher = as_bool(row.get("kircher_exact_match"))
    semantics = clinvar_semantics(row)
    queryable = is_queryable_snv(row)

    if not queryable:
        quality = "control_queryability_blocker"
        reason = "exclude_ref_alt_not_queryable_snv"
        conditional_usable = False
        local_interpretation = "not_assessable_queryability_blocker"
        note = "Ref/Alt are not valid single-nucleotide alleles."
    elif promoter and exact_kircher and semantics == "benign_or_likely_benign":
        quality = "good_for_rebuilt_promoter_5utr_benign_control"
        reason = "hold_until_candidate_set_is_rebuilt"
        conditional_usable = True
        local_interpretation = "promoter_5utr_benign_germline_compatible_control_like"
        note = "Mechanism-matched promoter/5_prime_UTR benign control-like row with exact Kircher overlap."
    elif splice_intronic and semantics == "benign_or_likely_benign":
        quality = "partial_for_excluded_splice_rows_only"
        reason = "exclude_if_primary_promoter_5utr_candidate_set_is_used"
        conditional_usable = False
        local_interpretation = "not_primary_promoter_5utr_regulatory"
        note = "Only matches excluded splice-region rows; lacks exact Kircher promoter source overlap."
    elif semantics in {"pathogenic_or_likely_pathogenic", "conflicting_pathogenicity"}:
        quality = "poor_control_pathogenic_or_ambiguous"
        reason = "exclude_pathogenic_or_ambiguous_control_semantics"
        conditional_usable = False
        local_interpretation = "intronic_or_splice_pathogenic_control_not_clean"
        note = "Pathogenic/intronic row is not a clean position control for promoter/5_prime_UTR candidates."
    else:
        quality = "unresolved_control_semantics"
        reason = "exclude_unresolved_control_semantics"
        conditional_usable = False
        local_interpretation = "unresolved_local_germline_semantics"
        note = "Local source semantics are not specific enough for a live control gate."

    include = bool(candidate_gate_nonempty and conditional_usable)
    return {
        "is_queryable_snv_audit": queryable,
        "is_promoter_or_5_prime_UTR_audit": promoter,
        "is_splice_or_intronic_audit": splice_intronic,
        "exact_kircher_overlap_audit": exact_kircher,
        "kircher_effect_direction": kircher_direction(row),
        "clinvar_semantics_audit": semantics,
        "local_germline_regulatory_interpretation": local_interpretation,
        "source_semantics_flag": quality,
        "mechanism_match_quality": quality,
        "exclude_before_live": not include,
        "exclude_before_live_reason": "" if include else reason,
        "live_gate_include": include,
        "audit_note": note,
    }


def audited_frame(df: pd.DataFrame, group: str, candidate_gate_nonempty: bool = False) -> pd.DataFrame:
    audit_rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        if group == "candidate":
            audit = audit_candidate(row)
        else:
            audit = audit_control(row, candidate_gate_nonempty)
        audit["audit_group"] = group
        audit_rows.append(audit)
    audit_df = pd.DataFrame(audit_rows)
    return pd.concat([df.reset_index(drop=True), audit_df], axis=1)


def count_true(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns:
        return 0
    return int(df[col].map(as_bool).sum())


def markdown_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def row_action_table(df: pd.DataFrame, limit: int | None = None) -> list[str]:
    view = df if limit is None else df.head(limit)
    rows = []
    for _, row in view.iterrows():
        rows.append(
            [
                norm(row.get("ClinVar_ID")),
                norm(row.get("Position_GRCh38")),
                f"{norm(row.get('Ref'))}>{norm(row.get('Alt'))}",
                norm(row.get("Category")),
                norm(row.get("ClinVar_Significance")),
                norm(row.get("kircher_exact_match")),
                norm(row.get("local_germline_regulatory_interpretation")),
                norm(row.get("source_semantics_flag")),
                norm(row.get("exclude_before_live_reason")),
            ]
        )
    return markdown_table(
        rows,
        [
            "ClinVar_ID",
            "pos",
            "allele",
            "category",
            "ClinVar",
            "Kircher exact",
            "local source interpretation",
            "audit flag",
            "pre-live action",
        ],
    )


def subset_table(df: pd.DataFrame, interpretation: str) -> list[str]:
    subset = df[df["local_germline_regulatory_interpretation"].eq(interpretation)]
    if subset.empty:
        return ["No rows in this subset."]
    rows = []
    for _, row in subset.iterrows():
        rows.append(
            [
                norm(row.get("audit_group")),
                norm(row.get("ClinVar_ID")),
                norm(row.get("Position_GRCh38")),
                f"{norm(row.get('Ref'))}>{norm(row.get('Alt'))}",
                norm(row.get("HGVS_c")),
                norm(row.get("ClinVar_Significance")),
                norm(row.get("kircher_value")),
                norm(row.get("exclude_before_live_reason")),
            ]
        )
    return markdown_table(
        rows,
        ["group", "ClinVar_ID", "pos", "allele", "HGVS_c", "ClinVar", "Kircher value", "pre-live action"],
    )


def write_report(candidates: pd.DataFrame, controls: pd.DataFrame) -> None:
    combined = pd.concat([candidates, controls], ignore_index=True)
    candidate_live = int(candidates["live_gate_include"].sum())
    control_live = int(controls["live_gate_include"].sum())
    candidate_promoter = int(candidates["is_promoter_or_5_prime_UTR_audit"].sum())
    control_promoter = int(controls["is_promoter_or_5_prime_UTR_audit"].sum())
    candidate_kircher = int(candidates["exact_kircher_overlap_audit"].sum())
    control_kircher = int(controls["exact_kircher_overlap_audit"].sum())
    candidate_ambiguous = int(
        candidates["source_semantics_flag"].eq("source_semantics_ambiguous_possible_cancer_context").sum()
    )
    candidate_control_like = int(
        candidates["source_semantics_flag"].eq("benign_control_like_not_positive_candidate").sum()
    )
    control_good = int(
        controls["mechanism_match_quality"].eq("good_for_rebuilt_promoter_5utr_benign_control").sum()
    )

    decision = "REBUILD"
    if candidate_live and control_live:
        decision = "CONTINUE_TO_STRICT_LIVE"
    elif candidate_ambiguous >= len(candidates) // 2 and control_good == 0:
        decision = "STOP"

    lines = [
        "# Paper 3 TERT Source-Semantics Audit",
        "",
        "Date: 2026-05-03",
        "",
        "This is a local source-semantics audit before any live gnomAD query. No live population query was run.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{decision}**",
        "- Can TERT be interpreted as a regulatory-positive candidate locus now? **NOT YET**",
        "- Why: the local TERT cohort contains real promoter/5_prime_UTR rows with exact Kircher overlap, but the candidate-like pathogenic/conflicting promoter rows need germline-versus-somatic source resolution before live population interpretation.",
        "- Main blocker: after pre-live exclusions, clean positive candidates are `0`; control-like promoter rows remain useful only after candidate rebuild.",
        "- Next required action: rebuild a smaller TERT promoter/5_prime_UTR cohort from source rows whose germline/cancer/somatic semantics are explicitly auditable, or switch to another regulatory locus with cleaner noncoding source provenance.",
        "",
        "## Audit Counts",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                [
                    "Candidates",
                    len(candidates),
                    candidate_promoter,
                    candidate_kircher,
                    candidate_ambiguous,
                    candidate_control_like,
                    candidate_live,
                    "current candidate set is not live-ready",
                ],
                [
                    "Controls",
                    len(controls),
                    control_promoter,
                    control_kircher,
                    0,
                    control_good,
                    control_live,
                    "3 controls are useful for a rebuilt promoter/5_prime_UTR design, but not without candidates",
                ],
            ],
            [
                "Group",
                "n",
                "promoter/5_prime_UTR",
                "exact Kircher overlap",
                "source-ambiguous candidate-like",
                "benign/control-like",
                "live_gate_include",
                "interpretation",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Germline / Cancer Semantics",
            "",
            "- Local rows do not encode a definitive germline-versus-somatic flag.",
            "- Benign/Likely benign promoter/5_prime_UTR rows are treated as germline-compatible control-like source context, not positive candidate evidence.",
            "- Pathogenic or conflicting TERT promoter/5_prime_UTR rows are treated as cancer/somatic/cancer-predisposition ambiguous until their original source semantics are checked.",
            "- Splice-region or intronic rows are not accepted as primary promoter/5_prime_UTR regulatory-positive candidates in this gate.",
            "",
            "### Locally Germline-Compatible Promoter/5_prime_UTR Rows",
            "",
            "These rows are not definitive germline truth-set rows; they are benign/Likely benign promoter/5_prime_UTR rows with exact local Kircher overlap and are therefore control-like source context.",
            "",
        ]
    )
    lines.extend(
        subset_table(
            combined,
            "promoter_5utr_benign_germline_compatible_control_like",
        )
    )
    lines.extend(
        [
            "",
            "### Cancer/Somatic/Cancer-Predisposition Ambiguous Rows",
            "",
            "These are the candidate-like promoter/5_prime_UTR rows that must be excluded before live population screening unless the original source semantics are resolved.",
            "",
        ]
    )
    lines.extend(
        subset_table(
            combined,
            "promoter_5utr_candidate_like_but_cancer_somatic_ambiguous",
        )
    )
    lines.extend(
        [
            "",
            "## Exact Kircher / Source Overlap",
            "",
            f"- Candidates with exact Kircher overlap: `{candidate_kircher}/{len(candidates)}`.",
            f"- Controls with exact Kircher overlap: `{control_kircher}/{len(controls)}`.",
            "- Candidate/control exact-overlap rows are not the same variants, but both groups draw from the same local Kircher source family for the promoter/5_prime_UTR subset.",
            "- Source overlap is incomplete for splice/intronic rows, so those rows should not be mixed into a promoter/5_prime_UTR live gate.",
            "",
            "## Controls Mechanism Matching",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            [
                [
                    "promoter/5_prime_UTR benign exact-Kircher controls",
                    control_good,
                    "good mechanism match for a rebuilt promoter/5_prime_UTR candidate set",
                ],
                [
                    "splice-region benign controls",
                    int(controls["mechanism_match_quality"].eq("partial_for_excluded_splice_rows_only").sum()),
                    "partial match only if splice candidates are kept, which this audit excludes",
                ],
                [
                    "pathogenic/intronic controls",
                    int(controls["mechanism_match_quality"].eq("poor_control_pathogenic_or_ambiguous").sum()),
                    "poor controls for a promoter/5_prime_UTR regulatory cohort",
                ],
            ],
            ["Control subset", "n", "interpretation"],
        )
    )
    lines.extend(
        [
            "",
            "## Rows To Exclude Before Live Gate",
            "",
            "### Candidates",
            "",
        ]
    )
    lines.extend(row_action_table(candidates))
    lines.extend(["", "### Controls", ""])
    lines.extend(row_action_table(controls))
    lines.extend(
        [
            "",
            "## Allowed Claim",
            "",
            "TERT remains a plausible source-rebuild target because local rows include promoter/5_prime_UTR exact Kircher overlap, but the current 8-row TERT candidate/control gate is not clean enough for live gnomAD interpretation.",
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
            "Do not run live gnomAD for the current TERT 8-candidate / 8-control set. Rebuild or externally audit source semantics first.",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_tert_source_semantics_audit.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not IN_CANDIDATES.exists():
        raise FileNotFoundError(f"Missing candidate input: {IN_CANDIDATES}")
    if not IN_CONTROLS.exists():
        raise FileNotFoundError(f"Missing control input: {IN_CONTROLS}")

    candidates = pd.read_csv(IN_CANDIDATES)
    controls = pd.read_csv(IN_CONTROLS)
    audited_candidates = audited_frame(candidates, "candidate")
    candidate_gate_nonempty = bool(audited_candidates["live_gate_include"].sum())
    audited_controls = audited_frame(controls, "control", candidate_gate_nonempty)

    audited_candidates.to_csv(OUT_CANDIDATES, index=False)
    audited_controls.to_csv(OUT_CONTROLS, index=False)
    write_report(audited_candidates, audited_controls)

    print(f"Wrote {OUT_CANDIDATES.relative_to(ROOT)} ({len(audited_candidates)} rows)")
    print(f"Wrote {OUT_CONTROLS.relative_to(ROOT)} ({len(audited_controls)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
