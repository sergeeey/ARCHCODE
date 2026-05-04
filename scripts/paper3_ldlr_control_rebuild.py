#!/usr/bin/env python
"""Attempt a strict LDLR control rebuild for the Paper 3 gate.

Pre-specified control rule:
- same configured LDLR promoter/upstream regulatory window
- queryable SNV
- benign or likely benign
- outside the LDLR queryable bottom 5% by ARCHCODE_LSSIM
- primary controls additionally require promoter/5_prime_UTR mechanism and
  exact Kircher overlap

The script does not query gnomAD.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CONFIG = ROOT / "config" / "locus" / "ldlr_300kb.json"

IN_AUDIT = RESULTS / "PAPER3_LDLR_DESIGN_AUDIT_20260503.csv"
OUT_OPTIONS = RESULTS / "PAPER3_LDLR_CONTROL_REBUILD_OPTIONS_20260503.csv"
OUT_CONTROLS = RESULTS / "PAPER3_LDLR_STRICT_CONTROL_REBUILD_20260503.csv"
OUT_MD = RESULTS / "PAPER3_LDLR_CONTROL_REBUILD_DECISION_20260503.md"


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def truthy(value: Any) -> bool:
    return norm(value).lower() in {"true", "1", "yes", "y"}


def parse_peak_interval(note: str) -> tuple[int, int] | None:
    match = re.search(r"Peak_[^,]*,\s*(\d+)-(\d+)", note)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2))
    return min(start, end), max(start, end)


def load_ldlr_promoter_windows() -> list[dict[str, Any]]:
    if not CONFIG.exists():
        return []
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    windows: list[dict[str, Any]] = []
    for item in (data.get("features") or {}).get("enhancers", []):
        name = norm(item.get("name"))
        note = norm(item.get("note"))
        if "LDLR_promoter" not in name and "LDLR_upstream" not in name:
            continue
        interval = parse_peak_interval(note)
        if not interval:
            pos = int(item["position"])
            interval = (pos - 1000, pos + 1000)
        windows.append(
            {
                "window_name": name,
                "window_source": norm(item.get("source")),
                "window_start": interval[0],
                "window_end": interval[1],
                "window_note": note,
            }
        )
    return windows


def annotate_window(row: pd.Series, windows: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        pos = int(row["Position_GRCh38"])
    except Exception:
        return {
            "same_promoter_upstream_window": False,
            "matched_window_name": "",
            "matched_window_start": "",
            "matched_window_end": "",
            "distance_to_window_bp": "",
        }

    containing = [
        item for item in windows if int(item["window_start"]) <= pos <= int(item["window_end"])
    ]
    if containing:
        best = min(containing, key=lambda item: int(item["window_end"]) - int(item["window_start"]))
        return {
            "same_promoter_upstream_window": True,
            "matched_window_name": best["window_name"],
            "matched_window_start": best["window_start"],
            "matched_window_end": best["window_end"],
            "distance_to_window_bp": 0,
        }

    if not windows:
        return {
            "same_promoter_upstream_window": False,
            "matched_window_name": "",
            "matched_window_start": "",
            "matched_window_end": "",
            "distance_to_window_bp": "",
        }
    best = min(
        windows,
        key=lambda item: min(
            abs(pos - int(item["window_start"])),
            abs(pos - int(item["window_end"])),
        ),
    )
    distance = min(abs(pos - int(best["window_start"])), abs(pos - int(best["window_end"])))
    return {
        "same_promoter_upstream_window": False,
        "matched_window_name": best["window_name"],
        "matched_window_start": best["window_start"],
        "matched_window_end": best["window_end"],
        "distance_to_window_bp": distance,
    }


def classify_option(row: pd.Series) -> tuple[str, str, str]:
    same_window = truthy(row.get("same_promoter_upstream_window"))
    queryable = truthy(row.get("is_queryable_snv"))
    benign = norm(row.get("clinvar_bucket")) == "benign_or_likely_benign"
    nonbottom = not truthy(row.get("ldlr_bottom5"))
    same_mechanism = norm(row.get("mechanism_subclass")) == "promoter_or_5_prime_UTR"
    exact_kircher = truthy(row.get("kircher_exact_match"))

    if not queryable or not benign:
        return "not_control_eligible", "REJECT", "Not a queryable benign SNV."
    if not same_window:
        return "outside_promoter_upstream_window", "REJECT", "Outside the pre-specified LDLR promoter/upstream windows."
    if same_mechanism and exact_kircher and nonbottom:
        return "strict_same_window_same_mechanism_nonbottom", "ACCEPT_STRICT", "Primary control rule satisfied."
    if same_mechanism and exact_kircher and not nonbottom:
        return (
            "same_window_same_mechanism_but_low_lssim",
            "REJECT_LOW_LSSIM_CONFOUNDED",
            "Same-window promoter control-like row is also in the LDLR bottom 5%.",
        )
    if nonbottom:
        return (
            "same_window_relaxed_nonbottom_different_mechanism",
            "RELAXED_ONLY_DIFFERENT_MECHANISM",
            "Same-window non-bottom benign row exists, but mechanism/Kircher matching fails.",
        )
    return (
        "same_window_relaxed_but_low_lssim",
        "REJECT_LOW_LSSIM_CONFOUNDED",
        "Same-window benign row exists, but it is also in the LDLR bottom 5%.",
    )


def table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def rows_table(df: pd.DataFrame, cols: list[str], limit: int = 25) -> list[str]:
    if df.empty:
        return ["No rows."]
    rows = []
    for _, row in df.head(limit).iterrows():
        rows.append([norm(row.get(col)) for col in cols])
    return table(rows, cols)


def write_report(options: pd.DataFrame, strict_controls: pd.DataFrame) -> None:
    same_window = options[options["same_promoter_upstream_window"].map(truthy)]
    same_window_benign = same_window[same_window["clinvar_bucket"].eq("benign_or_likely_benign")]
    accepted = options[options["control_rebuild_gate_status"].eq("ACCEPT_STRICT")]
    relaxed_nonbottom = options[
        options["control_rebuild_gate_status"].eq("RELAXED_ONLY_DIFFERENT_MECHANISM")
    ]
    same_mechanism_low = options[
        options["control_rebuild_option_class"].eq("same_window_same_mechanism_but_low_lssim")
    ]
    decision = "STOP_LDLR_AS_CLEAN_POSITIVE_GATE" if strict_controls.empty else "CONTINUE_TO_DRY_RUN_ONLY"

    lines = [
        "# Paper 3 LDLR Control Rebuild Decision",
        "",
        "Date: 2026-05-03",
        "",
        "Bounded local control rebuild only. No gnomAD query was run.",
        "",
        "## Executive Verdict",
        "",
        f"- Decision: **{decision}**",
        "- Can LDLR serve as the second clean regulatory-positive locus now? **NO / NOT YET**",
        f"- Accepted strict controls: `{len(accepted)}`",
        f"- Frozen strict controls written: `{len(strict_controls)}`",
        "- Main blocker: no benign queryable row satisfies same promoter/upstream window, promoter/5_prime_UTR mechanism, exact Kircher overlap, and non-bottom LSSIM simultaneously.",
        "- Next required action: stop LDLR as the current clean positive gate and move to HBG1 atlas/config import or another complete regulatory source import.",
        "",
        "## Pre-Specified Control Rule",
        "",
        "- Same configured LDLR promoter/upstream H3K27ac window from `config/locus/ldlr_300kb.json`.",
        "- Queryable SNV.",
        "- Benign or Likely benign local source semantics.",
        "- Outside LDLR queryable bottom 5% by `ARCHCODE_LSSIM`.",
        "- Primary control additionally requires promoter/5_prime_UTR mechanism and exact Kircher overlap.",
        "",
        "## Control Rebuild Counts",
        "",
    ]
    class_counts = options["control_rebuild_option_class"].value_counts().to_dict()
    lines.extend(
        table(
            [
                ["same-window total rows", len(same_window)],
                ["same-window benign/queryable rows", len(same_window_benign)],
                ["strict accepted controls", len(accepted)],
                ["same-mechanism but low-LSSIM controls", len(same_mechanism_low)],
                ["relaxed non-bottom different-mechanism rows", len(relaxed_nonbottom)],
                ["outside-window benign options", class_counts.get("outside_promoter_upstream_window", 0)],
            ],
            ["Metric", "Value"],
        )
    )
    lines.extend(
        [
            "",
            "## Same-Mechanism Low-LSSIM Rows",
            "",
            "These rows look mechanism-matched, but fail as controls because they are also in the low-LSSIM tail.",
            "",
        ]
    )
    lines.extend(
        rows_table(
            same_mechanism_low,
            [
                "ClinVar_ID",
                "Position_GRCh38",
                "Ref",
                "Alt",
                "HGVS_c",
                "ARCHCODE_LSSIM",
                "ldlr_bottom5",
                "kircher_value",
                "control_rebuild_gate_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Relaxed Non-Bottom Rows",
            "",
            "These rows are same-window and non-bottom, but they are not promoter/5_prime_UTR exact-Kircher controls. They are not accepted for the clean gate.",
            "",
        ]
    )
    lines.extend(
        rows_table(
            relaxed_nonbottom,
            [
                "ClinVar_ID",
                "Position_GRCh38",
                "Ref",
                "Alt",
                "HGVS_c",
                "Category",
                "mechanism_subclass",
                "ARCHCODE_LSSIM",
                "control_rebuild_gate_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Dry-Run / Live Gate",
            "",
            "- LDLR strict dry-run: **NOT RUN** because strict controls are empty.",
            "- Live gnomAD: **NOT RUN**.",
            "",
            "## Allowed Claim",
            "",
            "LDLR remains source-rich and biologically relevant, but the strict control rebuild fails; it should not be used as the second clean regulatory-positive Paper 3 locus from current local artifacts.",
            "",
            "## Not Allowed",
            "",
            "- \"LDLR validates ARCHCODE\"",
            "- \"multi-locus confirmed\"",
            "- \"Paper 3 ready\"",
            "- \"not found proves constraint\"",
            "- \"ARCHCODE beats VEP/CADD\"",
            "",
            "## Decision",
            "",
            f"**{decision}**",
            "",
            "Move to HBG1 atlas/config import or another complete regulatory source import before any further live population gate.",
            "",
            "## Reproducibility",
            "",
            "```powershell",
            "python scripts\\paper3_ldlr_control_rebuild.py",
            "```",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not IN_AUDIT.exists():
        raise FileNotFoundError(f"Missing LDLR design audit: {IN_AUDIT}")
    df = pd.read_csv(IN_AUDIT)
    windows = load_ldlr_promoter_windows()
    annotations = [annotate_window(row, windows) for _, row in df.iterrows()]
    df = pd.concat([df, pd.DataFrame(annotations)], axis=1)

    option_rows = []
    for _, row in df.iterrows():
        option_class, status, note = classify_option(row)
        option_rows.append(
            {
                "control_rebuild_option_class": option_class,
                "control_rebuild_gate_status": status,
                "control_rebuild_note": note,
            }
        )
    df = pd.concat([df, pd.DataFrame(option_rows)], axis=1)
    options = df[
        df["is_queryable_snv"].map(truthy)
        & df["clinvar_bucket"].eq("benign_or_likely_benign")
    ].copy()
    strict_controls = options[options["control_rebuild_gate_status"].eq("ACCEPT_STRICT")].copy()

    options.to_csv(OUT_OPTIONS, index=False)
    strict_controls.to_csv(OUT_CONTROLS, index=False)
    write_report(options, strict_controls)

    print(f"Wrote {OUT_OPTIONS.relative_to(ROOT)} ({len(options)} rows)")
    print(f"Wrote {OUT_CONTROLS.relative_to(ROOT)} ({len(strict_controls)} rows)")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
