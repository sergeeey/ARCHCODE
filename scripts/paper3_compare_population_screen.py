#!/usr/bin/env python
"""Compare Paper 3 candidate and position-control gnomAD outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def load(path: str, group: str) -> pd.DataFrame:
    df = pd.read_csv(ROOT / path)
    df["group"] = group
    for col in ["gnomAD_AF", "AF_AFR", "AF_AMR", "AF_EAS", "AF_EUR", "AF_SAS"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def summarize(df: pd.DataFrame) -> dict[str, object]:
    success = df[df["gnomAD_source"].astype(str).str.contains("gnomAD_v4", na=False)]
    failed = df[df["gnomAD_source"] == "QUERY_FAILED"]
    if success.empty:
        return {
            "n": len(df),
            "success": 0,
            "query_failed": len(failed),
            "not_observed": 0,
            "af_zero_all_5_pops": 0,
            "af_ge_1pct": 0,
            "af_ge_0_1pct": 0,
            "median_af_success": "NA",
            "max_af_success": "NA",
        }
    af = success["gnomAD_AF"].fillna(0.0)
    pop_cols = ["AF_AFR", "AF_AMR", "AF_EAS", "AF_EUR", "AF_SAS"]
    af_zero_all_5 = int((success[pop_cols].fillna(0.0) == 0.0).all(axis=1).sum())
    return {
        "n": len(df),
        "success": len(success),
        "query_failed": len(failed),
        "not_observed": int((success["gnomAD_source"] == "gnomAD_v4_not_observed_graphql").sum()),
        "af_zero_all_5_pops": af_zero_all_5,
        "af_ge_1pct": int((af >= 0.01).sum()),
        "af_ge_0_1pct": int((af >= 0.001).sum()),
        "median_af_success": f"{float(af.median()):.6g}",
        "max_af_success": f"{float(af.max()):.6g}",
    }


def write_report(name: str, candidate: pd.DataFrame, control: pd.DataFrame, out: Path) -> None:
    candidate_summary = summarize(candidate)
    control_summary = summarize(control)
    columns = [
        "n",
        "success",
        "query_failed",
        "not_observed",
        "af_zero_all_5_pops",
        "af_ge_1pct",
        "af_ge_0_1pct",
        "median_af_success",
        "max_af_success",
    ]
    lines = [
        f"# Paper 3 {name} Population Screen Comparison",
        "",
        "This compares low-LSSIM candidates against position-matched controls. It is a screening artifact, not a manuscript claim.",
        "",
        "| group | " + " | ".join(columns) + " |",
        "|---|" + "|".join(["---:"] * len(columns)) + "|",
        "| low_lssim_candidates | "
        + " | ".join(str(candidate_summary[col]) for col in columns)
        + " |",
        "| position_controls | " + " | ".join(str(control_summary[col]) for col in columns) + " |",
        "",
        "## Interpretation",
        "",
    ]
    cand_high = int(candidate_summary["af_ge_1pct"])
    ctrl_high = int(control_summary["af_ge_1pct"])
    cand_zero = int(candidate_summary["af_zero_all_5_pops"])
    ctrl_zero = int(control_summary["af_zero_all_5_pops"])
    if cand_high > ctrl_high:
        lines.append(
            "Low-LSSIM candidates have more common-population observations than controls. "
            "This argues against using this locus as a positive regulatory constraint example without re-framing."
        )
    elif cand_zero > ctrl_zero and cand_high == 0 and ctrl_high == 0:
        lines.append(
            "Low-LSSIM candidates show stronger all-population zero-AF constraint than controls, "
            "with no common variants in either group. This is a candidate positive screen, "
            "but it remains limited by cohort size and source/category audit."
        )
    elif cand_high < ctrl_high:
        lines.append(
            "Low-LSSIM candidates have fewer common-population observations than controls. "
            "This is a candidate positive signal, subject to query-failure and source audits."
        )
    else:
        lines.append(
            "Low-LSSIM candidates do not separate from position controls on the common-variant screen."
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


def main() -> None:
    cftr_candidates = load("results/paper3_cftr_regulatory_candidates_20260503.csv", "low_lssim")
    cftr_controls = load("results/paper3_cftr_position_controls_20260503.csv", "position_controls")
    write_report(
        "CFTR",
        cftr_candidates,
        cftr_controls,
        ROOT / "results" / "PAPER3_CFTR_POPULATION_SCREEN_COMPARISON_20260503.md",
    )

    hba1_candidates = load("results/paper3_hba1_mango_candidates_20260503.csv", "low_lssim")
    hba1_controls = load("results/paper3_hba1_mango_controls_20260503.csv", "position_controls")
    write_report(
        "HBA1 MANGO",
        hba1_candidates,
        hba1_controls,
        ROOT / "results" / "PAPER3_HBA1_MANGO_POPULATION_SCREEN_COMPARISON_20260503.md",
    )


if __name__ == "__main__":
    main()
