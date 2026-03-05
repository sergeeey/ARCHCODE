#!/usr/bin/env python3
"""
Build reproducible Task 5 VUS stratification summary.

Inputs:
  - results/within_category_analysis.json
  - results/vus_validation_report.json (optional)
  - results/*_Unified_Atlas_*.csv

Output:
  - results/task5_vus_stratification_summary_<date>.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_baseline_atlas_for_locus(locus: str) -> Path | None:
    candidates = sorted(RESULTS_DIR.glob(f"{locus}_Unified_Atlas_*.csv"))
    if not candidates:
        return None

    # Prefer canonical baseline files and exclude ablation/control variants.
    excluded_tokens = ("INVERTED", "POSITION_ONLY", "RANDOM", "UNIFORM_MEDIUM")
    filtered = [p for p in candidates if not any(tok in p.name for tok in excluded_tokens)]
    if not filtered:
        filtered = candidates

    canonical = []
    for p in filtered:
        suffix = p.name.split("_Unified_Atlas_", 1)[1]
        if re.match(r"^[0-9]+kb\.csv$", suffix):
            canonical.append(p)
    pool = canonical if canonical else filtered
    return sorted(pool, key=lambda x: (len(x.name), x.name))[0]


def collect_atlas_counts(loci: list[str]) -> dict[str, Any]:
    atlas_paths: list[Path] = []
    for locus in loci:
        p = resolve_baseline_atlas_for_locus(locus)
        if p is not None:
            atlas_paths.append(p)

    vus_total = 0
    candidate_total = 0
    pearl_like_total = 0
    per_locus: list[dict[str, Any]] = []

    for path in atlas_paths:
        locus = path.name.split("_Unified_Atlas_")[0]
        n_rows = 0
        n_vus = 0
        n_candidates = 0
        n_pearl = 0

        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                n_rows += 1
                verdict = (row.get("ARCHCODE_Verdict") or "").strip()
                discord = (row.get("Discordance") or "").strip().lower()

                is_candidate_vus = verdict == "VUS"
                is_pearl_like = (
                    (row.get("Pearl") or "").strip().lower() == "true"
                    or discord in {"vep_only", "archcode_only"}
                )

                if is_candidate_vus:
                    n_vus += 1
                    n_candidates += 1
                    if is_pearl_like:
                        n_pearl += 1

        vus_total += n_vus
        candidate_total += n_candidates
        pearl_like_total += n_pearl
        per_locus.append(
            {
                "locus": locus,
                "n_rows": n_rows,
                "vus": n_vus,
                "candidates": n_candidates,
                "pearl_like": n_pearl,
            }
        )

    pearl_fraction = (pearl_like_total / vus_total) if vus_total else 0.0
    return {
        "atlas_files": [str(p.relative_to(PROJECT_ROOT)).replace("\\", "/") for p in atlas_paths],
        "vus_total_in_windows": vus_total,
        "candidates_total": candidate_total,
        "pearl_like_total": pearl_like_total,
        "pearl_like_fraction_of_vus": round(pearl_fraction, 6),
        "per_locus_counts": per_locus,
    }


def compute_within_category_stats(within_json: dict[str, Any]) -> dict[str, Any]:
    loci = within_json.get("loci", [])
    means: list[float] = []
    low_within: list[str] = []

    for locus in loci:
        overall = locus.get("overall_auc")
        within_mean = locus.get("mean_within_category_auc")
        name = locus.get("locus", "UNKNOWN")
        if isinstance(within_mean, (int, float)):
            means.append(float(within_mean))
        if isinstance(overall, (int, float)) and isinstance(within_mean, (int, float)):
            if overall >= 0.7 and within_mean < 0.55:
                low_within.append(name)

    return {
        "mean_within_category_auc_across_loci": round(mean(means), 6) if means else None,
        "loci_with_high_overall_but_low_within_category": low_within,
    }


def extract_variant_rationale(vus_report: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(vus_report, dict):
        return []
    variants = vus_report.get("variants", [])
    sample: list[dict[str, Any]] = []
    for item in variants[:10]:
        sample.append(
            {
                "clinvar_id": item.get("clinvar_id"),
                "category": item.get("category"),
                "archcode_verdict": ((item.get("archcode") or {}).get("verdict")),
                "alphagenome_prediction": ((item.get("alphagenome") or {}).get("prediction")),
                "interpretation": item.get("interpretation"),
                "provenance_tag": "COMPUTATIONAL_HYPOTHESIS_LEVEL",
            }
        )
    return sample


def main() -> None:
    parser = argparse.ArgumentParser(description="Build reproducible Task 5 VUS stratification summary")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--within-json", default="results/within_category_analysis.json")
    parser.add_argument("--vus-report", default="results/vus_validation_report.json")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    within_path = PROJECT_ROOT / args.within_json
    within_json = load_json(within_path)
    within_loci = [str(x.get("locus")) for x in within_json.get("loci", []) if x.get("locus")]

    vus_path = PROJECT_ROOT / args.vus_report
    vus_json = load_json(vus_path) if vus_path.exists() else None

    counts = collect_atlas_counts(within_loci)
    within_stats = compute_within_category_stats(within_json)
    rationale_sample = extract_variant_rationale(vus_json)

    output_path = (
        PROJECT_ROOT / args.output
        if args.output
        else RESULTS_DIR / f"task5_vus_stratification_summary_{args.date}.json"
    )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": "Task5_VUS_Stratification",
        "claim_level": {
            "vus_stratification_signal": "SUPPORTED",
            "clinical_reclassification": "UNVERIFIED",
            "causal_mechanism_assignment": "EXPLORATORY",
        },
        "provenance": {
            "type": "COMPUTATIONAL_DERIVED",
            "sources": [
                str(within_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                str(vus_path.relative_to(PROJECT_ROOT)).replace("\\", "/") if vus_path.exists() else "MISSING:vus_validation_report.json",
                "results/*_Unified_Atlas_*.csv",
            ],
        },
        "stratification_rules": [
            "Candidate VUS = ARCHCODE_Verdict == 'VUS' in locus atlas rows.",
            "Pearl-like VUS = Candidate VUS with Pearl == true OR Discordance in {VEP_ONLY, ARCHCODE_ONLY}.",
            "Within-category discrimination metric = ROC AUC(1-LSSIM) with minimum 3 pathogenic and 3 benign variants per category.",
            "Clinical reclassification is blocked without orthogonal experimental validation.",
        ],
        **counts,
        **within_stats,
        "variant_rationale_sample": rationale_sample,
        "interpretation": "Computational stratification signal exists, but within-category separability is modest in several loci; findings remain hypothesis-generating pending functional validation.",
        "allowed_claims": [
            "Computational stratification signal is present in this data slice.",
            "Within-category discrimination is limited in multiple loci and constrains overinterpretation.",
            "Variant-level rationale is available as hypothesis-level computational evidence.",
        ],
        "blocked_claims": [
            "Clinical reclassification from these metrics alone",
            "Disease-causal mechanism assignment without orthogonal experiments",
        ],
        "limitations": [
            "No direct wet-lab validation in this artifact",
            "Category structure and class imbalance can influence global metrics",
            "Variant rationale sample is computational and non-causal by itself",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")

    print(f"Task 5 summary written: {output_path}")
    print(
        f"VUS={summary['vus_total_in_windows']} | candidates={summary['candidates_total']} | pearl_like={summary['pearl_like_total']}"
    )


if __name__ == "__main__":
    main()
