#!/usr/bin/env python
"""Build a conservative Paper 3 feasibility matrix from existing atlas files.

This script does not query gnomAD and does not make validation claims. It
summarizes local atlas readiness for a mechanism-stratified falsification plan.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


REGULATORY_CATEGORIES = {
    "promoter",
    "intronic",
    "splice",
    "splice_region",
    "5_prime_utr",
    "3_prime_utr",
    "other",
}

CODING_CATEGORIES = {
    "missense",
    "synonymous",
    "frameshift",
    "nonsense",
    "inframe_deletion",
    "inframe_insertion",
}


@dataclass(frozen=True)
class LocusSpec:
    locus: str
    atlas: str
    chrom: str
    role: str
    mechanism_group: str
    primary_use: str
    source_caveat: str


LOCI = [
    LocusSpec(
        locus="HBB",
        atlas="HBB_Unified_Atlas.csv",
        chrom="11",
        role="positive_proof_of_concept",
        mechanism_group="promoter/regulatory",
        primary_use="carry forward as Paper 2 anchor; do not re-use as only evidence",
        source_caveat="Paper 2 package already audited separately",
    ),
    LocusSpec(
        locus="HBA1",
        atlas="HBA1_Unified_Atlas_300kb.csv",
        chrom="16",
        role="candidate_positive_regulatory",
        mechanism_group="alpha-globin regulatory/coding mix",
        primary_use="feasibility only until regulatory subset is frozen",
        source_caveat="VEP/CADD mostly unavailable in current atlas",
    ),
    LocusSpec(
        locus="BCL11A_erythroid",
        atlas="BCL11A_Unified_Atlas_bcl11a_erythroid.csv",
        chrom="2",
        role="candidate_positive_regulatory",
        mechanism_group="erythroid enhancer/regulatory",
        primary_use="best next positive locus if source rows are non-synthetic",
        source_caveat="category is broad 'other'; needs source audit before claims",
    ),
    LocusSpec(
        locus="GATA1",
        atlas="GATA1_Unified_Atlas_300kb.csv",
        chrom="X",
        role="candidate_positive_regulatory",
        mechanism_group="erythroid regulator/coding mix",
        primary_use="secondary positive locus; not enough current low-LSSIM signal alone",
        source_caveat="VEP/CADD mostly unavailable in current atlas",
    ),
    LocusSpec(
        locus="CFTR",
        atlas="CFTR_Unified_Atlas_317kb.csv",
        chrom="7",
        role="mechanism_boundary",
        mechanism_group="mixed regulatory/coding, tissue-sensitive",
        primary_use="boundary test, not primary positive evidence",
        source_caveat="tissue/context mismatch risk; no CADD column in current atlas",
    ),
    LocusSpec(
        locus="BRCA1",
        atlas="BRCA1_Unified_Atlas_brca1.csv",
        chrom="17",
        role="negative_coding_control",
        mechanism_group="coding-dominant control",
        primary_use="negative/control stratum only",
        source_caveat="VEP/CADD mostly unavailable in current atlas",
    ),
    LocusSpec(
        locus="TP53",
        atlas="TP53_Unified_Atlas_tp53.csv",
        chrom="17",
        role="negative_coding_control",
        mechanism_group="coding-dominant/dosage-sensitive control",
        primary_use="control stratum; interpret separately from BRCA1",
        source_caveat="VEP/CADD mostly unavailable in current atlas",
    ),
]


def pct(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.4f}"


def safe_quantile(series: pd.Series, q: float) -> float:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return math.nan
    return float(numeric.quantile(q))


def normalize_category(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def is_snv(row: pd.Series) -> bool:
    ref = str(row.get("Ref", ""))
    alt = str(row.get("Alt", ""))
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT" and ref != alt


def count_present(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return 0
    series = df[column]
    if column == "CADD_Phred":
        numeric = pd.to_numeric(series, errors="coerce")
        return int(numeric.notna().sum() - (numeric == -1).sum())
    return int(series.notna().sum())


def summarize_locus(spec: LocusSpec) -> dict[str, object]:
    path = RESULTS / spec.atlas
    if not path.exists():
        return {
            "locus": spec.locus,
            "atlas": spec.atlas,
            "exists": False,
            "status": "MISSING",
            "note": "atlas file not found",
        }

    df = pd.read_csv(path)
    categories = df.get("Category", pd.Series(dtype=object)).map(normalize_category)
    source = df.get("Source", pd.Series(dtype=object)).fillna("").astype(str)
    significance = df.get("ClinVar_Significance", pd.Series(dtype=object)).fillna("").astype(str)
    lssim = pd.to_numeric(df.get("ARCHCODE_LSSIM"), errors="coerce")
    snv_mask = df.apply(is_snv, axis=1)
    regulatory_mask = categories.isin(REGULATORY_CATEGORIES)
    coding_mask = categories.isin(CODING_CATEGORIES)
    synthetic_mask = (
        source.str.contains("SYNTHETIC|MOCK|DEMO", case=False, regex=True)
        | significance.str.contains("SYNTHETIC|MOCK|DEMO", case=False, regex=True)
    )
    non_synthetic_mask = ~synthetic_mask

    q05 = safe_quantile(lssim, 0.05)
    q10 = safe_quantile(lssim, 0.10)
    bottom_5_mask = lssim <= q05 if not math.isnan(q05) else pd.Series(False, index=df.index)
    abs_099_mask = lssim < 0.99
    abs_095_mask = lssim < 0.95

    candidate_primary_mask = snv_mask & non_synthetic_mask & regulatory_mask & bottom_5_mask
    candidate_boundary_mask = snv_mask & non_synthetic_mask & regulatory_mask & abs_099_mask

    pearl_count = 0
    if "Pearl" in df.columns:
        pearl_count = int(df["Pearl"].fillna(False).astype(bool).sum())

    status = "READY_FOR_DRY_RUN"
    warnings: list[str] = []
    if int(non_synthetic_mask.sum()) == 0:
        status = "EXCLUDE_PRIMARY"
        warnings.append("all rows appear synthetic/mock/demo")
    if spec.role.startswith("candidate_positive") and int(candidate_primary_mask.sum()) == 0:
        status = "NEEDS_SUBSET_AUDIT"
        warnings.append("no non-synthetic regulatory SNVs in bottom 5% LSSIM")
    if count_present(df, "VEP_Impact") == 0:
        warnings.append("VEP unavailable")
    if count_present(df, "CADD_Phred") == 0:
        warnings.append("CADD unavailable")
    if categories.nunique(dropna=True) == 1 and "other" in set(categories):
        warnings.append("category field is broad 'other'")

    return {
        "locus": spec.locus,
        "atlas": spec.atlas,
        "exists": True,
        "chrom": spec.chrom,
        "role": spec.role,
        "mechanism_group": spec.mechanism_group,
        "primary_use": spec.primary_use,
        "total_rows": len(df),
        "snv_rows": int(snv_mask.sum()),
        "non_synthetic_rows": int(non_synthetic_mask.sum()),
        "synthetic_flagged_rows": int(synthetic_mask.sum()),
        "regulatory_category_rows": int(regulatory_mask.sum()),
        "coding_category_rows": int(coding_mask.sum()),
        "pearl_true_rows": pearl_count,
        "lssim_min": pct(safe_quantile(lssim, 0.0)),
        "lssim_q05": pct(q05),
        "lssim_q10": pct(q10),
        "lssim_median": pct(safe_quantile(lssim, 0.5)),
        "low_lssim_lt_0_99_rows": int(abs_099_mask.sum()),
        "low_lssim_lt_0_95_rows": int(abs_095_mask.sum()),
        "candidate_primary_bottom5_regulatory_snv_rows": int(candidate_primary_mask.sum()),
        "candidate_boundary_lt099_regulatory_snv_rows": int(candidate_boundary_mask.sum()),
        "vep_present_rows": count_present(df, "VEP_Impact"),
        "cadd_present_rows": count_present(df, "CADD_Phred"),
        "status": status,
        "source_caveat": spec.source_caveat,
        "warnings": "; ".join(warnings) if warnings else "none",
    }


def write_markdown(rows: list[dict[str, object]], path: Path) -> None:
    columns = [
        "locus",
        "role",
        "total_rows",
        "snv_rows",
        "regulatory_category_rows",
        "pearl_true_rows",
        "lssim_min",
        "lssim_q05",
        "candidate_primary_bottom5_regulatory_snv_rows",
        "candidate_boundary_lt099_regulatory_snv_rows",
        "vep_present_rows",
        "cadd_present_rows",
        "status",
        "warnings",
    ]
    lines = [
        "# Paper 3 Feasibility Matrix",
        "",
        "Generated from local atlas files only. This is a feasibility artifact, not a results claim.",
        "",
        "|" + "|".join(columns) + "|",
        "|" + "|".join(["---"] * len(columns)) + "|",
    ]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(col, "")) for col in columns) + "|")

    lines.extend(
        [
            "",
            "## Interpretation Guardrails",
            "",
            "- `candidate_primary_bottom5_regulatory_snv_rows` is a dry-run cohort size for planning.",
            "- It must not be reported as validation evidence until gnomAD queries are run and audited.",
            "- Broad `other` categories require source review before being treated as enhancer/regulatory.",
            "- Synthetic/mock/demo rows are excluded from primary Paper 3 evidence.",
            "- Absence from gnomAD is a triage signal, not proof of universal constraint.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = [summarize_locus(spec) for spec in LOCI]
    csv_path = RESULTS / "PAPER3_FEASIBILITY_MATRIX_20260503.csv"
    md_path = RESULTS / "PAPER3_FEASIBILITY_MATRIX_20260503.md"

    fieldnames = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    write_markdown(rows, md_path)
    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
