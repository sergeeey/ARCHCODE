#!/usr/bin/env python
"""Audit LDLR/HBG1 as next Paper 3 regulatory-locus designs.

This is a local-source design gate. It does not query gnomAD. LDLR has a
local ARCHCODE atlas plus Kircher source overlap; HBG1 currently has Kircher
source rows only and no local ARCHCODE atlas/config gate.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"
CONFIG = ROOT / "config" / "locus"

LDLR_ATLAS = RESULTS / "LDLR_Unified_Atlas_300kb.csv"
LDLR_K562_ATLAS = RESULTS / "LDLR_Unified_Atlas_300kb_K562.csv"
LDLR_KIRCHER = DATA / "kircher_LDLR_GRCh38.tsv"
HBG1_KIRCHER = DATA / "kircher_HBG1_GRCh38.tsv"
HBG1_ATLAS = RESULTS / "HBG1_Unified_Atlas_300kb.csv"
HBG1_CONFIG = CONFIG / "hbg1_300kb.json"

OUT_LDLR = RESULTS / "PAPER3_LDLR_DESIGN_AUDIT_20260503.csv"
OUT_LDLR_CANDIDATES = RESULTS / "PAPER3_LDLR_REBUILD_CANDIDATES_20260503.csv"
OUT_LDLR_CONTROLS = RESULTS / "PAPER3_LDLR_REBUILD_CONTROLS_20260503.csv"
OUT_LDLR_CONTROL_OPTIONS = RESULTS / "PAPER3_LDLR_CONTROL_OPTIONS_20260503.csv"
OUT_HBG1 = RESULTS / "PAPER3_HBG1_SOURCE_ONLY_AUDIT_20260503.csv"
OUT_MD = RESULTS / "PAPER3_LDLR_HBG1_DESIGN_DECISION_20260503.md"

BASES = {"A", "C", "G", "T"}
SYNTHETIC_MARKERS = ("synthetic", "mock", "demo")


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def is_snv(ref: Any, alt: Any) -> bool:
    ref_s = norm(ref).upper()
    alt_s = norm(alt).upper()
    return len(ref_s) == 1 and len(alt_s) == 1 and ref_s in BASES and alt_s in BASES and ref_s != alt_s


def is_synthetic(row: pd.Series) -> bool:
    blob = " ".join(
        norm(row.get(col))
        for col in [
            "ClinVar_ID",
            "Source",
            "Label",
            "ClinVar_Significance",
            "Category",
            "HGVS_c",
            "HGVS_p",
        ]
    ).lower()
    return any(marker in blob for marker in SYNTHETIC_MARKERS)


def classify_mechanism(row: pd.Series) -> str:
    category = norm(row.get("Category")).lower()
    hgvs_c = norm(row.get("HGVS_c")).lower()
    hgvs_p = norm(row.get("HGVS_p")).lower()
    blob = f"{category} {hgvs_c} {hgvs_p}"

    if "5_prime_utr" in category or "c.-" in hgvs_c:
        return "promoter_or_5_prime_UTR"
    if "3_prime_utr" in category or "c.*" in hgvs_c:
        return "3_prime_UTR"
    if "splice" in category:
        return "splice_region"
    if "intronic" in category or "+" in hgvs_c or "-" in hgvs_c:
        return "intronic"
    if "frameshift" in blob or "fs" in hgvs_p:
        return "coding_frameshift"
    if "nonsense" in blob or "ter" in hgvs_p or "*" in hgvs_p:
        return "coding_nonsense"
    if "missense" in blob or (hgvs_p and "=" not in hgvs_p):
        return "coding_missense"
    if "synonymous" in blob or "=" in hgvs_p:
        return "coding_synonymous"
    return "other_unresolved"


def clinvar_bucket(value: Any) -> str:
    text = norm(value).lower()
    if "conflicting" in text:
        return "conflicting"
    if "pathogenic" in text:
        return "pathogenic_or_likely_pathogenic"
    if "benign" in text:
        return "benign_or_likely_benign"
    if "uncertain" in text:
        return "vus"
    return "unresolved"


def add_kircher(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    df = df.copy()
    if not path.exists():
        df["kircher_exact_match"] = False
        df["kircher_value"] = pd.NA
        df["kircher_p_value"] = pd.NA
        return df
    kircher = pd.read_csv(path, sep="\t").rename(
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
        kircher[["Position_GRCh38", "Ref", "Alt", "Tags", "DNA", "RNA", "kircher_value", "kircher_p_value"]],
        on=["Position_GRCh38", "Ref", "Alt"],
        how="left",
    )
    merged["kircher_exact_match"] = merged["kircher_value"].notna()
    return merged


def load_ldlr() -> pd.DataFrame:
    if not LDLR_ATLAS.exists():
        raise FileNotFoundError(f"Missing LDLR atlas: {LDLR_ATLAS}")
    df = pd.read_csv(LDLR_ATLAS)
    df["locus"] = "LDLR"
    df["is_queryable_snv"] = df.apply(lambda row: is_snv(row.get("Ref"), row.get("Alt")), axis=1)
    df["is_synthetic_or_demo"] = df.apply(is_synthetic, axis=1)
    df["mechanism_subclass"] = df.apply(classify_mechanism, axis=1)
    df["clinvar_bucket"] = df["ClinVar_Significance"].map(clinvar_bucket)
    df = add_kircher(df, LDLR_KIRCHER)

    usable = df[df["is_queryable_snv"] & ~df["is_synthetic_or_demo"]].copy()
    q05 = float(usable["ARCHCODE_LSSIM"].astype(float).quantile(0.05)) if len(usable) else math.nan
    df["ldlr_lssim_q05"] = q05
    df["ldlr_bottom5"] = df["is_queryable_snv"] & (df["ARCHCODE_LSSIM"].astype(float) <= q05)
    df["ldlr_primary_candidate"] = (
        df["is_queryable_snv"]
        & df["mechanism_subclass"].eq("promoter_or_5_prime_UTR")
        & df["clinvar_bucket"].eq("pathogenic_or_likely_pathogenic")
        & df["kircher_exact_match"]
        & ~df["is_synthetic_or_demo"]
    )
    df["ldlr_conflicting_candidate_like"] = (
        df["is_queryable_snv"]
        & df["mechanism_subclass"].eq("promoter_or_5_prime_UTR")
        & df["clinvar_bucket"].eq("conflicting")
        & df["kircher_exact_match"]
        & ~df["is_synthetic_or_demo"]
    )
    df["ldlr_strict_mechanism_control"] = (
        df["is_queryable_snv"]
        & df["mechanism_subclass"].eq("promoter_or_5_prime_UTR")
        & df["clinvar_bucket"].eq("benign_or_likely_benign")
        & df["kircher_exact_match"]
        & ~df["ldlr_bottom5"]
        & ~df["is_synthetic_or_demo"]
    )
    df["ldlr_control_like_but_low_lssim"] = (
        df["is_queryable_snv"]
        & df["mechanism_subclass"].eq("promoter_or_5_prime_UTR")
        & df["clinvar_bucket"].eq("benign_or_likely_benign")
        & df["kircher_exact_match"]
        & df["ldlr_bottom5"]
        & ~df["is_synthetic_or_demo"]
    )
    return df


def build_ldlr_cands_controls(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidates = df[df["ldlr_primary_candidate"]].copy()
    candidates = candidates.sort_values(["ARCHCODE_LSSIM", "Position_GRCh38"], ascending=[True, True]).head(20)
    controls = df[df["ldlr_strict_mechanism_control"]].copy()
    controls = controls.sort_values(["ARCHCODE_LSSIM", "Position_GRCh38"], ascending=[False, True]).head(
        min(20, len(candidates))
    )

    # Freeze live gate flags, but keep them false if the control side is empty
    # or too small to support a meaningful mechanism-matched comparison.
    candidates["ldlr_rebuild_candidate"] = len(candidates) > 0 and len(controls) >= 3
    controls["ldlr_rebuild_control"] = len(candidates) > 0 and len(controls) >= 3
    return candidates, controls


def build_ldlr_control_options(df: pd.DataFrame) -> pd.DataFrame:
    options = df[
        df["is_queryable_snv"]
        & ~df["is_synthetic_or_demo"]
        & df["clinvar_bucket"].eq("benign_or_likely_benign")
    ].copy()
    if options.empty:
        options["control_option_class"] = pd.Series(dtype=str)
        options["control_gate_status"] = pd.Series(dtype=str)
        options["control_option_note"] = pd.Series(dtype=str)
        return options

    def classify(row: pd.Series) -> str:
        mechanism = norm(row.get("mechanism_subclass"))
        exact = bool(row.get("kircher_exact_match"))
        bottom = bool(row.get("ldlr_bottom5"))
        if mechanism == "promoter_or_5_prime_UTR" and exact and not bottom:
            return "strict_same_mechanism_nonbottom"
        if mechanism == "promoter_or_5_prime_UTR" and exact and bottom:
            return "same_mechanism_but_low_lssim"
        if mechanism == "3_prime_UTR":
            return "noncoding_3utr_benign"
        if mechanism == "coding_synonymous":
            return "coding_synonymous_benign"
        return "other_benign"

    def gate_status(option_class: str) -> str:
        if option_class == "strict_same_mechanism_nonbottom":
            return "ACCEPT_STRICT"
        if option_class == "same_mechanism_but_low_lssim":
            return "REJECT_AS_CONTROL_LOW_LSSIM_CONFOUNDED"
        if option_class == "noncoding_3utr_benign":
            return "RELAXED_ONLY_DIFFERENT_UTR_MECHANISM"
        if option_class == "coding_synonymous_benign":
            return "RELAXED_ONLY_CODING_CONTROL"
        return "REJECT_UNMATCHED"

    def note(option_class: str) -> str:
        notes = {
            "strict_same_mechanism_nonbottom": "Same promoter/5_prime_UTR mechanism, exact Kircher overlap, and outside LDLR bottom 5%.",
            "same_mechanism_but_low_lssim": "Same promoter/5_prime_UTR mechanism, but also low-LSSIM; cannot test candidate-vs-position-control separation.",
            "noncoding_3utr_benign": "Noncoding and benign, but 3_prime_UTR rather than promoter/5_prime_UTR.",
            "coding_synonymous_benign": "Queryable benign coding control; not a regulatory mechanism match.",
            "other_benign": "Benign row without sufficient mechanism match.",
        }
        return notes.get(option_class, "")

    options["control_option_class"] = options.apply(classify, axis=1)
    options["control_gate_status"] = options["control_option_class"].map(gate_status)
    options["control_option_note"] = options["control_option_class"].map(note)
    return options.sort_values(
        ["control_gate_status", "mechanism_subclass", "ARCHCODE_LSSIM", "Position_GRCh38"],
        ascending=[True, True, True, True],
    )


def audit_hbg1() -> pd.DataFrame:
    if not HBG1_KIRCHER.exists():
        return pd.DataFrame(
            [
                {
                    "source_file": str(HBG1_KIRCHER.relative_to(ROOT)),
                    "source_exists": False,
                    "rows": 0,
                    "queryable_snvs": 0,
                    "positive_effect_rows": 0,
                    "negative_effect_rows": 0,
                    "has_archcode_atlas": HBG1_ATLAS.exists(),
                    "has_locus_config": HBG1_CONFIG.exists(),
                    "decision": "MISSING_SOURCE",
                }
            ]
        )
    df = pd.read_csv(HBG1_KIRCHER, sep="\t")
    df["is_queryable_snv"] = df.apply(lambda row: is_snv(row.get("Ref"), row.get("Alt")), axis=1)
    df["effect_bucket"] = df["Value"].astype(float).map(
        lambda value: "positive_effect" if value >= 0.5 else "negative_effect" if value <= -0.5 else "near_zero"
    )
    summary = pd.DataFrame(
        [
            {
                "source_file": str(HBG1_KIRCHER.relative_to(ROOT)),
                "source_exists": True,
                "rows": len(df),
                "queryable_snvs": int(df["is_queryable_snv"].sum()),
                "positions": int(df["Position"].nunique()),
                "positive_effect_rows": int(df["effect_bucket"].eq("positive_effect").sum()),
                "negative_effect_rows": int(df["effect_bucket"].eq("negative_effect").sum()),
                "has_archcode_atlas": HBG1_ATLAS.exists(),
                "has_locus_config": HBG1_CONFIG.exists(),
                "decision": "IMPORT_ARCHCODE_ATLAS",
            }
        ]
    )
    return summary


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def row_table(df: pd.DataFrame, cols: list[str], limit: int = 20) -> list[str]:
    if df.empty:
        return ["No rows."]
    rows = []
    for _, row in df.head(limit).iterrows():
        rows.append([norm(row.get(col)) for col in cols])
    return table(rows, cols)


def write_report(
    ldlr: pd.DataFrame,
    cands: pd.DataFrame,
    controls: pd.DataFrame,
    control_options: pd.DataFrame,
    hbg1: pd.DataFrame,
) -> None:
    queryable = ldlr[ldlr["is_queryable_snv"]]
    promoter = queryable[queryable["mechanism_subclass"].eq("promoter_or_5_prime_UTR")]
    primary = ldlr[ldlr["ldlr_primary_candidate"]]
    conflict = ldlr[ldlr["ldlr_conflicting_candidate_like"]]
    strict_controls = ldlr[ldlr["ldlr_strict_mechanism_control"]]
    low_lssim_controls = ldlr[ldlr["ldlr_control_like_but_low_lssim"]]
    option_counts = (
        control_options["control_option_class"].value_counts().to_dict() if len(control_options) else {}
    )
    old_control_file = RESULTS / "PAPER3_LDLR_MATCHED_CONTROLS_20260503.csv"
    old_live_audit = RESULTS / "PAPER3_LDLR_LIVE_AUDIT_20260503.md"

    if len(cands) and len(controls) >= 3:
        ldlr_decision = "CONTINUE_TO_DRY_RUN_ONLY"
    elif len(primary):
        ldlr_decision = "REBUILD_CONTROLS_BEFORE_DRY_RUN"
    else:
        ldlr_decision = "STOP_NO_CANDIDATES"

    hbg1_decision = norm(hbg1.iloc[0]["decision"]) if len(hbg1) else "MISSING_SOURCE"
    if ldlr_decision == "CONTINUE_TO_DRY_RUN_ONLY":
        overall = "LDLR_DRY_RUN_CANDIDATE"
    elif hbg1_decision == "IMPORT_ARCHCODE_ATLAS":
        overall = "LDLR_CONTROL_REBUILD_OR_HBG1_IMPORT"
    else:
        overall = "REBUILD_EXTERNAL_SOURCE"

    lines = [
        "# Paper 3 LDLR / HBG1 Design Audit",
        "",
        "Date: 2026-05-03",
        "",
        "Local source-design audit only. No gnomAD query was run.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{overall}**",
        f"- LDLR: **{ldlr_decision}**",
        f"- HBG1: **{hbg1_decision}**",
        "- Can either serve as the second regulatory-positive locus now? **NOT YET**",
        "- Why: LDLR has cleaner germline disease/source semantics and many promoter/5_prime_UTR candidate-like rows, but strict same-mechanism non-bottom controls are too limited; HBG1 has useful MPRA-like source rows but no local ARCHCODE atlas/config gate.",
        "- Next required action: rebuild LDLR controls before dry-run, or import HBG1 ARCHCODE atlas/config before any population gate.",
        "",
        "## LDLR Source Counts",
        "",
    ]
    lines.extend(
        table(
            [
                ["atlas rows", len(ldlr)],
                ["queryable SNVs", len(queryable)],
                ["promoter/5_prime_UTR queryable rows", len(promoter)],
                ["primary P/LP promoter exact-Kircher candidates", len(primary)],
                ["conflicting promoter exact-Kircher candidate-like rows", len(conflict)],
                ["strict same-mechanism benign non-bottom controls", len(strict_controls)],
                ["benign promoter exact-Kircher rows inside bottom5", len(low_lssim_controls)],
                ["relaxed 3_prime_UTR benign options", option_counts.get("noncoding_3utr_benign", 0)],
                ["relaxed coding synonymous benign options", option_counts.get("coding_synonymous_benign", 0)],
                ["frozen rebuild candidates", len(cands)],
                ["frozen rebuild controls", len(controls)],
            ],
            ["Metric", "Value"],
        )
    )
    lines.extend(
        [
            "",
            "## LDLR Candidate Semantics",
            "",
            "LDLR promoter/5_prime_UTR P/LP rows are more interpretable than TERT promoter rows because the local disease context is familial hypercholesterolemia rather than mixed tumor/somatic interpretation. This is still not enough for a live or manuscript claim without mechanism-matched controls.",
            "",
            "### Frozen Candidate Rows",
            "",
        ]
    )
    lines.extend(
        row_table(
            cands,
            [
                "ClinVar_ID",
                "Position_GRCh38",
                "Ref",
                "Alt",
                "HGVS_c",
                "ClinVar_Significance",
                "ARCHCODE_LSSIM",
                "kircher_value",
                "ldlr_rebuild_candidate",
            ],
        )
    )
    lines.extend(
        [
            "",
            "### Strict Same-Mechanism Controls",
            "",
        ]
    )
    lines.extend(
        row_table(
            controls,
            [
                "ClinVar_ID",
                "Position_GRCh38",
                "Ref",
                "Alt",
                "HGVS_c",
                "ClinVar_Significance",
                "ARCHCODE_LSSIM",
                "kircher_value",
                "ldlr_rebuild_control",
            ],
        )
    )
    lines.extend(
        [
            "",
            "### Control Option Classes",
            "",
        ]
    )
    if len(control_options):
        rows = []
        for option_class, count in control_options["control_option_class"].value_counts().items():
            subset = control_options[control_options["control_option_class"].eq(option_class)]
            rows.append(
                [
                    option_class,
                    int(count),
                    norm(subset.iloc[0].get("control_gate_status")),
                    norm(subset.iloc[0].get("control_option_note")),
                ]
            )
        lines.extend(table(rows, ["option_class", "n", "gate_status", "note"]))
    else:
        lines.append("No benign queryable control options.")
    lines.extend(
        [
            "",
            "## Old LDLR Artifacts Are Not Positive Evidence",
            "",
            f"- Old matched-control file exists: `{old_control_file.exists()}`.",
            f"- Old live audit exists: `{old_live_audit.exists()}`.",
            "- The old controls were not strict promoter/5_prime_UTR mechanism matches, and the prior live audit had query failures. Those artifacts remain design-level only.",
            "",
            "## HBG1 Source-Only Audit",
            "",
        ]
    )
    lines.extend(
        table(
            [[col, norm(hbg1.iloc[0].get(col))] for col in hbg1.columns],
            ["Metric", "Value"],
        )
    )
    lines.extend(
        [
            "",
            "## Dry-Run / Live Gate",
            "",
            "- LDLR strict dry-run: **NOT RUN** because same-mechanism controls are not sufficient for the frozen gate.",
            "- HBG1 strict dry-run: **NOT RUN** because no local ARCHCODE atlas/config gate exists.",
            "- Live gnomAD: **NOT RUN**.",
            "",
            "## Allowed Claim",
            "",
            "LDLR is the current best local source-rich design candidate, but it needs a stricter control rebuild before any dry-run/live population screen. HBG1 is a plausible import target, not a current local cohort.",
            "",
            "## Not Allowed",
            "",
            "- \"LDLR validates ARCHCODE\"",
            "- \"HBG1 validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Decision",
            "",
            f"**{overall}**",
            "",
            "Do not run live gnomAD. The next narrow task is an LDLR control rebuild; if strict controls remain sparse, import HBG1 or another regulatory locus with a complete ARCHCODE atlas/config.",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_ldlr_hbg1_design_audit.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ldlr = load_ldlr()
    cands, controls = build_ldlr_cands_controls(ldlr)
    control_options = build_ldlr_control_options(ldlr)
    hbg1 = audit_hbg1()

    ldlr.to_csv(OUT_LDLR, index=False)
    cands.to_csv(OUT_LDLR_CANDIDATES, index=False)
    controls.to_csv(OUT_LDLR_CONTROLS, index=False)
    control_options.to_csv(OUT_LDLR_CONTROL_OPTIONS, index=False)
    hbg1.to_csv(OUT_HBG1, index=False)
    write_report(ldlr, cands, controls, control_options, hbg1)

    print(f"Wrote {OUT_LDLR.relative_to(ROOT)} ({len(ldlr)} rows)")
    print(f"Wrote {OUT_LDLR_CANDIDATES.relative_to(ROOT)} ({len(cands)} rows)")
    print(f"Wrote {OUT_LDLR_CONTROLS.relative_to(ROOT)} ({len(controls)} rows)")
    print(f"Wrote {OUT_LDLR_CONTROL_OPTIONS.relative_to(ROOT)} ({len(control_options)} rows)")
    print(f"Wrote {OUT_HBG1.relative_to(ROOT)} ({len(hbg1)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
