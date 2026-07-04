#!/usr/bin/env python
"""Scout local Paper 3 next-locus candidates without population queries.

The scout is deliberately conservative. It reads local atlas/source files,
checks queryability and regulatory low-LSSIM availability, and writes a gate
table. It does not call gnomAD and does not make manuscript-level claims.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data"

OUT_CSV = RESULTS / "PAPER3_NEXT_LOCUS_SCOUT_20260503.csv"
OUT_MD = RESULTS / "PAPER3_NEXT_LOCUS_SCOUT_20260503.md"

REGULATORY_SUBCLASSES = {
    "promoter_or_5_prime_UTR",
    "5_prime_UTR",
    "3_prime_UTR",
    "intronic",
    "splice_region",
    "enhancer_like",
}
CODING_MARKERS = ("missense", "nonsense", "frameshift", "synonymous", "inframe")
SYNTHETIC_MARKERS = ("synthetic", "mock", "demo")


@dataclass(frozen=True)
class ScoutSpec:
    locus: str
    role: str
    atlas: str | None = None
    source: str | None = None
    prior_status: str = ""
    note: str = ""


SPECS = [
    ScoutSpec(
        locus="HBA_full",
        role="candidate_positive_regulatory",
        atlas="PAPER3_HBA_FULL_QUERYABLE_ATLAS_20260503.csv",
        prior_status="STOP_current_gate",
        note="Full HBA gate already failed: regulatory rows do not enter whole-locus bottom 5%.",
    ),
    ScoutSpec(
        locus="GATA1",
        role="candidate_positive_regulatory",
        atlas="GATA1_Unified_Atlas_300kb.csv",
        source="clinvar_gata1_variants.csv",
        note="Erythroid regulator; needs queryability and source/category audit.",
    ),
    ScoutSpec(
        locus="LDLR",
        role="candidate_regulatory_or_design",
        atlas="LDLR_Unified_Atlas_300kb.csv",
        source="kircher_LDLR_GRCh38.tsv",
        prior_status="DESIGN_LEVEL_ONLY",
        note="Has prior design/live artifacts; not a clean regulatory-positive locus yet.",
    ),
    ScoutSpec(
        locus="LDLR_K562",
        role="candidate_regulatory_or_design",
        atlas="LDLR_Unified_Atlas_300kb_K562.csv",
        source="kircher_LDLR_GRCh38.tsv",
        prior_status="DESIGN_LEVEL_ONLY",
        note="Cell-context variant of LDLR; same source-audit caveat.",
    ),
    ScoutSpec(
        locus="TERT",
        role="candidate_regulatory_import",
        atlas="TERT_Unified_Atlas_300kb.csv",
        source="kircher_TERT_GRCh38.tsv",
        note="Promoter biology is plausible, but germline/somatic semantics need source audit.",
    ),
    ScoutSpec(
        locus="TERT_SKNS",
        role="candidate_regulatory_import",
        atlas="TERT_Unified_Atlas_300kb_SKNS.csv",
        source="kircher_TERT_GRCh38.tsv",
        note="Alternative cell context; same source semantics caveat.",
    ),
    ScoutSpec(
        locus="HBG1_source_only",
        role="candidate_external_import",
        source="kircher_HBG1_GRCh38.tsv",
        note="Source-only MPRA-style table; needs ARCHCODE atlas/config before Paper 3 gate.",
    ),
    ScoutSpec(
        locus="BCL11A_erythroid",
        role="known_blocked_pilot",
        atlas="BCL11A_Unified_Atlas_bcl11a_erythroid.csv",
        prior_status="STOP_control_confound",
        note="Prior source/control audit showed position controls share the same query pattern.",
    ),
    ScoutSpec(
        locus="CFTR",
        role="mechanism_boundary",
        atlas="CFTR_Unified_Atlas_317kb.csv",
        prior_status="BOUNDARY_ONLY",
        note="Prior candidate/control comparison behaved as a boundary or negative locus.",
    ),
]


def norm(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return math.nan


def is_snv(row: pd.Series | dict[str, Any]) -> bool:
    ref = norm(row.get("Ref") or row.get("ref")).upper()
    alt = norm(row.get("Alt") or row.get("alt")).upper()
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT" and ref != alt


def is_synthetic(row: pd.Series | dict[str, Any]) -> bool:
    blob = " ".join(
        norm(row.get(col))
        for col in [
            "ClinVar_ID",
            "clinvar_id",
            "Source",
            "source",
            "Label",
            "label",
            "Category",
            "category",
            "ClinVar_Significance",
            "clinical_significance",
            "HGVS_c",
            "hgvs_c",
        ]
    ).lower()
    return any(marker in blob for marker in SYNTHETIC_MARKERS)


def classify_mechanism(row: pd.Series | dict[str, Any]) -> str:
    category = norm(row.get("Category") or row.get("category")).lower()
    hgvs_c = norm(row.get("HGVS_c") or row.get("hgvs_c")).lower()
    hgvs_p = norm(row.get("HGVS_p") or row.get("hgvs_p")).lower()
    blob = f"{category} {hgvs_c} {hgvs_p}"

    if any(marker in blob for marker in CODING_MARKERS) or "ter" in hgvs_p or "*" in hgvs_p:
        if "synonymous" in blob or "=" in hgvs_p:
            return "coding_synonymous"
        if "nonsense" in blob or "ter" in hgvs_p or "*" in hgvs_p:
            return "coding_nonsense"
        if "frameshift" in blob or "fs" in hgvs_p:
            return "coding_frameshift"
        return "coding_missense"
    if "promoter" in category or "5_prime_utr" in category or "5'utr" in category or "c.-" in hgvs_c:
        return "promoter_or_5_prime_UTR"
    if "3_prime_utr" in category or "3'utr" in category or "c.*" in hgvs_c:
        return "3_prime_UTR"
    if "enhancer" in category or "cre" in category or "dhs" in category:
        return "enhancer_like"
    if "splice" in category:
        return "splice_region"
    if "intronic" in category or "intron" in category:
        return "intronic"
    if "+" in hgvs_c or "-" in hgvs_c:
        return "intronic"
    return "other_unresolved"


def count_source_rows(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "source_exists": False,
            "source_rows": 0,
            "source_queryable_snvs": 0,
            "source_status": "MISSING",
        }
    if path.suffix.lower() == ".tsv":
        df = pd.read_csv(path, sep="\t")
    else:
        df = pd.read_csv(path)
    return {
        "source_exists": True,
        "source_rows": len(df),
        "source_queryable_snvs": int(df.apply(is_snv, axis=1).sum()) if len(df) else 0,
        "source_status": "SOURCE_ONLY" if "ARCHCODE_LSSIM" not in df.columns else "HAS_LSSIM",
    }


def choose_verdict(
    spec: ScoutSpec,
    atlas_exists: bool,
    queryable_snvs: int,
    regulatory_snvs: int,
    bottom5_regulatory_snvs: int,
    controls_possible: int,
    synthetic_risk: int,
    source_status: str,
) -> str:
    if spec.prior_status.startswith("STOP"):
        return spec.prior_status
    if spec.prior_status == "BOUNDARY_ONLY":
        return "BOUNDARY_ONLY"
    if spec.prior_status == "DESIGN_LEVEL_ONLY":
        return "REBUILD_SOURCE"
    if not atlas_exists:
        return "IMPORT_ARCHCODE_ATLAS" if source_status != "MISSING" else "MISSING_LOCAL_SOURCE"
    if synthetic_risk and queryable_snvs == 0:
        return "STOP_SYNTHETIC_OR_NOT_QUERYABLE"
    if queryable_snvs == 0:
        return "REBUILD_REF_ALT"
    if regulatory_snvs == 0:
        return "REBUILD_REGULATORY_SOURCE"
    if bottom5_regulatory_snvs == 0:
        return "REBUILD_SOURCE"
    if bottom5_regulatory_snvs > 20:
        return "TOO_MANY_FOR_SAFE_LIVE"
    if controls_possible < bottom5_regulatory_snvs:
        return "REBUILD_CONTROLS"
    return "TRY_NEXT_DRY_RUN"


def summarize_atlas(spec: ScoutSpec) -> dict[str, Any]:
    atlas_path = RESULTS / spec.atlas if spec.atlas else None
    source_info = count_source_rows(DATA / spec.source) if spec.source else {
        "source_exists": False,
        "source_rows": 0,
        "source_queryable_snvs": 0,
        "source_status": "",
    }
    row: dict[str, Any] = {
        "locus": spec.locus,
        "role": spec.role,
        "atlas": spec.atlas or "",
        "source": spec.source or "",
        **source_info,
        "note": spec.note,
    }

    if atlas_path is None or not atlas_path.exists():
        row.update(
            {
                "atlas_exists": False,
                "total_rows": 0,
                "queryable_snvs": 0,
                "regulatory_snvs": 0,
                "bottom5_regulatory_snvs": 0,
                "controls_possible": 0,
                "synthetic_risk_rows": 0,
                "lssim_q05": "NA",
            }
        )
        row["verdict"] = choose_verdict(spec, False, 0, 0, 0, 0, 0, row["source_status"])
        return row

    df = pd.read_csv(atlas_path)
    if "ARCHCODE_LSSIM" not in df.columns:
        row.update(
            {
                "atlas_exists": True,
                "total_rows": len(df),
                "queryable_snvs": int(df.apply(is_snv, axis=1).sum()) if len(df) else 0,
                "regulatory_snvs": 0,
                "bottom5_regulatory_snvs": 0,
                "controls_possible": 0,
                "synthetic_risk_rows": int(df.apply(is_synthetic, axis=1).sum()) if len(df) else 0,
                "lssim_q05": "NA",
            }
        )
        row["verdict"] = "IMPORT_ARCHCODE_ATLAS"
        return row

    df["is_queryable_snv"] = df.apply(is_snv, axis=1)
    df["is_synthetic"] = df.apply(is_synthetic, axis=1)
    df["mechanism_subclass"] = df.apply(classify_mechanism, axis=1)
    df["is_regulatory"] = df["mechanism_subclass"].isin(REGULATORY_SUBCLASSES)
    usable = df[df["is_queryable_snv"] & ~df["is_synthetic"]].copy()
    lssim = pd.to_numeric(usable["ARCHCODE_LSSIM"], errors="coerce").dropna()
    q05 = float(lssim.quantile(0.05)) if len(lssim) else math.nan
    usable["lssim_numeric"] = pd.to_numeric(usable["ARCHCODE_LSSIM"], errors="coerce")
    bottom5 = usable["lssim_numeric"] <= q05 if not math.isnan(q05) else pd.Series(False, index=usable.index)
    regulatory = usable["is_regulatory"]
    bottom5_reg = bottom5 & regulatory
    controls = regulatory & ~bottom5

    queryable_snvs = int(len(usable))
    regulatory_snvs = int(regulatory.sum())
    bottom5_regulatory_snvs = int(bottom5_reg.sum())
    controls_possible = int(controls.sum())
    synthetic_risk = int(df["is_synthetic"].sum())

    row.update(
        {
            "atlas_exists": True,
            "total_rows": len(df),
            "queryable_snvs": queryable_snvs,
            "regulatory_snvs": regulatory_snvs,
            "bottom5_regulatory_snvs": bottom5_regulatory_snvs,
            "controls_possible": controls_possible,
            "synthetic_risk_rows": synthetic_risk,
            "lssim_q05": f"{q05:.6g}" if not math.isnan(q05) else "NA",
        }
    )
    row["verdict"] = choose_verdict(
        spec,
        True,
        queryable_snvs,
        regulatory_snvs,
        bottom5_regulatory_snvs,
        controls_possible,
        synthetic_risk,
        row["source_status"],
    )
    return row


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "locus",
        "role",
        "atlas",
        "source",
        "atlas_exists",
        "source_exists",
        "source_status",
        "total_rows",
        "source_rows",
        "queryable_snvs",
        "source_queryable_snvs",
        "regulatory_snvs",
        "bottom5_regulatory_snvs",
        "controls_possible",
        "synthetic_risk_rows",
        "lssim_q05",
        "verdict",
        "note",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Paper 3 Next Locus Scout",
        "",
        "Date: 2026-05-03",
        "",
        "Local-source scout only. No gnomAD queries were run.",
        "",
        "## Summary",
        "",
        "| locus | queryable SNVs | regulatory SNVs | bottom5 regulatory SNVs | controls possible | verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {locus} | {queryable_snvs} | {regulatory_snvs} | {bottom5_regulatory_snvs} | {controls_possible} | {verdict} |".format(
                **row
            )
        )

    try_next = [row for row in rows if row["verdict"] == "TRY_NEXT_DRY_RUN"]
    rebuild = [row for row in rows if row["verdict"] in {"REBUILD_SOURCE", "REBUILD_REF_ALT", "REBUILD_REGULATORY_SOURCE", "IMPORT_ARCHCODE_ATLAS"}]
    boundary = [row for row in rows if row["verdict"] == "BOUNDARY_ONLY"]
    stopped = [row for row in rows if str(row["verdict"]).startswith("STOP")]

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- TRY_NEXT_DRY_RUN loci: `{', '.join(row['locus'] for row in try_next) or 'none'}`",
            f"- Rebuild/import candidates: `{', '.join(row['locus'] for row in rebuild) or 'none'}`",
            f"- Boundary-only loci: `{', '.join(row['locus'] for row in boundary) or 'none'}`",
            f"- Stopped/blocked loci: `{', '.join(row['locus'] for row in stopped) or 'none'}`",
            "",
            "## Recommended Next Step",
            "",
        ]
    )
    if try_next:
        chosen = try_next[0]
        lines.append(
            f"Run a source audit and dry-run gate for `{chosen['locus']}` before any live gnomAD query."
        )
    elif rebuild:
        chosen = rebuild[0]
        lines.append(
            f"No local locus is ready for live query. The least-bad next step is rebuilding/importing `{chosen['locus']}` source evidence."
        )
    else:
        lines.append("No local next-locus candidate is ready; import a new source-audited regulatory locus.")

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            "- Do not pool loci into one headline result.",
            "- Do not treat queryability as evidence of regulatory constraint.",
            "- Do not run live gnomAD unless candidate and control cohorts are non-empty and <=20 rows each.",
            "- Prior blocked loci remain blocked unless their source/control gate is rebuilt.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = [summarize_atlas(spec) for spec in SPECS]
    write_csv(rows)
    write_markdown(rows)
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_MD}")
    for row in rows:
        print(
            f"{row['locus']}: {row['verdict']} "
            f"(queryable={row['queryable_snvs']}, regulatory={row['regulatory_snvs']}, "
            f"bottom5_reg={row['bottom5_regulatory_snvs']}, controls={row['controls_possible']})"
        )


if __name__ == "__main__":
    main()
