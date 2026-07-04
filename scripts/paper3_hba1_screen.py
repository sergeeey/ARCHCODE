#!/usr/bin/env python
"""Build HBA1 MANGO low-LSSIM candidates and matched controls."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "results" / "PAPER3_HBA1_MANGO_QUERYABLE_ATLAS_20260503.csv"
OUT_CANDIDATES = ROOT / "results" / "PAPER3_HBA1_MANGO_CANDIDATES_20260503.csv"
OUT_CONTROLS = ROOT / "results" / "PAPER3_HBA1_MANGO_CONTROLS_20260503.csv"
OUT_MD = ROOT / "results" / "PAPER3_HBA1_MANGO_SCREEN_20260503.md"


def main() -> None:
    df = pd.read_csv(ATLAS)
    df = df[df["is_queryable_snv"].astype(bool)].copy()
    q05 = df["ARCHCODE_LSSIM"].quantile(0.05)
    df["hba1_low_lssim_candidate"] = df["ARCHCODE_LSSIM"] <= q05
    df["hba1_control_pool"] = ~df["hba1_low_lssim_candidate"]

    candidates = df[df["hba1_low_lssim_candidate"]].copy()
    # Match by same MANGO anchor first, then closest LSSIM above the low tail.
    control_rows = []
    used_ids = set()
    for _, candidate in candidates.iterrows():
        pool = df[
            (df["hba1_control_pool"])
            & (df["anchor_start"] == candidate["anchor_start"])
            & (~df["ClinVar_ID"].isin(used_ids))
        ].copy()
        if pool.empty:
            pool = df[df["hba1_control_pool"] & (~df["ClinVar_ID"].isin(used_ids))].copy()
        if pool.empty:
            continue
        pool["lssim_distance"] = (pool["ARCHCODE_LSSIM"] - candidate["ARCHCODE_LSSIM"]).abs()
        chosen = pool.sort_values(["lssim_distance", "Position_GRCh38"]).iloc[0]
        used_ids.add(chosen["ClinVar_ID"])
        control_rows.append(chosen)

    controls = pd.DataFrame(control_rows)
    candidates.to_csv(OUT_CANDIDATES, index=False)
    controls.to_csv(OUT_CONTROLS, index=False)

    lines = [
        "# Paper 3 HBA1 MANGO Screen",
        "",
        "HBA1 queryable alleles were recovered from UCSC hg38 sequence plus local HGVS_c substitutions.",
        "",
        f"- Queryable MANGO-overlap SNVs: `{len(df)}`",
        f"- Bottom-5% LSSIM threshold: `{q05:.4f}`",
        f"- Low-LSSIM candidates: `{len(candidates)}`",
        f"- Matched controls selected: `{len(controls)}`",
        "",
        "## Candidate Category Counts",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for key, value in candidates["Category"].value_counts().to_dict().items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Control Category Counts", "", "| category | count |", "|---|---:|"])
    for key, value in controls["Category"].value_counts().to_dict().items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "## Guardrail",
            "",
            "This is MANGO-anchored and queryable, but not a clean regulatory-only cohort because the low-LSSIM candidates are coding/nonsense in the current local annotation.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_CANDIDATES}")
    print(f"Wrote {OUT_CONTROLS}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
