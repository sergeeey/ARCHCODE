#!/usr/bin/env python3
"""
Build strict HBB VUS validation report with predeclared Go/No-Go criteria.

Inputs:
  - results/HBB_Unified_Atlas_95kb.csv
  - results/within_category_analysis.json
  - results/vus_validation_report.json (optional, for rationale sample only)

Output:
  - results/hbb_vus_validation_report_<date>.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def is_pearl_like(row: dict[str, str]) -> bool:
    pearl = (row.get("Pearl") or "").strip().lower() == "true"
    discord = (row.get("Discordance") or "").strip().lower()
    return pearl or discord in {"vep_only", "archcode_only"}


def hypergeom_tail(k: int, n: int, k_total: int, n_total: int) -> float:
    """
    One-sided enrichment p-value P[X >= k] for Hypergeometric distribution.
    X ~ Hypergeom(N=n_total, K=k_total, n=n)
    """
    max_x = min(n, k_total)
    if n_total <= 0 or n <= 0 or k_total < 0 or k < 0:
        return 1.0
    if k > max_x:
        return 0.0

    denom = math.comb(n_total, n)
    if denom == 0:
        return 1.0

    p = 0.0
    for x in range(k, max_x + 1):
        if 0 <= (n - x) <= (n_total - k_total):
            p += (math.comb(k_total, x) * math.comb(n_total - k_total, n - x)) / denom
    return min(max(p, 0.0), 1.0)


def get_hbb_within_category_stats(within_json: dict[str, Any]) -> dict[str, Any]:
    for locus in within_json.get("loci", []):
        if str(locus.get("locus", "")).upper() == "HBB":
            categories = locus.get("categories", [])
            valid = [c for c in categories if c.get("within_category_auc") is not None]
            return {
                "overall_auc": locus.get("overall_auc"),
                "mean_within_category_auc": locus.get("mean_within_category_auc"),
                "n_categories_with_auc": locus.get("n_categories_with_auc"),
                "valid_categories": [
                    {
                        "category": c.get("category"),
                        "within_category_auc": c.get("within_category_auc"),
                        "n_pathogenic": c.get("n_pathogenic"),
                        "n_benign": c.get("n_benign"),
                    }
                    for c in valid
                ],
            }
    return {
        "overall_auc": None,
        "mean_within_category_auc": None,
        "n_categories_with_auc": 0,
        "valid_categories": [],
    }


def extract_rationale_sample(vus_report: dict[str, Any] | None, max_items: int = 5) -> list[dict[str, Any]]:
    if not isinstance(vus_report, dict):
        return []
    out: list[dict[str, Any]] = []
    for row in vus_report.get("variants", [])[:max_items]:
        out.append(
            {
                "clinvar_id": row.get("clinvar_id"),
                "category": row.get("category"),
                "archcode_verdict": ((row.get("archcode") or {}).get("verdict")),
                "alphagenome_prediction": ((row.get("alphagenome") or {}).get("prediction")),
                "interpretation": row.get("interpretation"),
                "provenance_tag": "COMPUTATIONAL_HYPOTHESIS_LEVEL",
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Build strict HBB VUS validation report")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--atlas", default="results/HBB_Unified_Atlas_95kb.csv")
    parser.add_argument("--within-json", default="results/within_category_analysis.json")
    parser.add_argument("--vus-report", default="results/vus_validation_report.json")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    atlas_path = PROJECT_ROOT / args.atlas
    within_path = PROJECT_ROOT / args.within_json
    vus_path = PROJECT_ROOT / args.vus_report

    within_json = load_json(within_path)
    vus_json = load_json(vus_path) if vus_path.exists() else None

    rows: list[dict[str, str]] = []
    with atlas_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("ARCHCODE_Verdict") or "").strip() == "VUS":
                rows.append(row)

    rows_sorted = sorted(
        rows,
        key=lambda r: float(r.get("ARCHCODE_LSSIM") or 1.0),
    )
    n_vus = len(rows_sorted)
    k = min(max(args.top_k, 1), n_vus) if n_vus else 0

    pearl_flags = [is_pearl_like(r) for r in rows_sorted]
    total_pearl = sum(1 for x in pearl_flags if x)
    topk_pearl = sum(1 for x in pearl_flags[:k] if x) if k else 0

    bg_rate = (total_pearl / n_vus) if n_vus else 0.0
    topk_rate = (topk_pearl / k) if k else 0.0
    fold = (topk_rate / bg_rate) if bg_rate > 0 else None
    p_value = hypergeom_tail(topk_pearl, k, total_pearl, n_vus) if n_vus and k else 1.0

    hbb_within = get_hbb_within_category_stats(within_json)
    mean_within_auc = hbb_within.get("mean_within_category_auc")
    n_within = int(hbb_within.get("n_categories_with_auc") or 0)

    # Predeclared criteria for a strict Go/No-Go decision.
    c1 = 20 <= n_vus <= 60
    c2 = isinstance(mean_within_auc, (int, float)) and float(mean_within_auc) >= 0.60 and n_within >= 3
    c3 = (fold is not None) and (fold >= 1.25) and (p_value <= 0.05)
    go = c1 and c2 and c3

    output_path = (
        PROJECT_ROOT / args.output
        if args.output
        else RESULTS_DIR / f"hbb_vus_validation_report_{args.date}.json"
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": "HBB_VUS_STRICT_VALIDATION",
        "hypothesis": {
            "h0": "ARCHCODE does not provide useful ranking signal among HBB VUS beyond category structure.",
            "h1": "ARCHCODE provides reproducible ranking signal among HBB VUS suitable for prioritization of follow-up assays.",
        },
        "claim_level": {
            "ranking_signal_hbb_vus": "SUPPORTED" if go else "EXPLORATORY",
            "clinical_reclassification": "UNVERIFIED",
            "causal_mechanism_assignment": "EXPLORATORY",
        },
        "provenance": {
            "type": "COMPUTATIONAL_DERIVED",
            "sources": [
                str(atlas_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                str(within_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                str(vus_path.relative_to(PROJECT_ROOT)).replace("\\", "/") if vus_path.exists() else "MISSING:results/vus_validation_report.json",
            ],
        },
        "predeclared_criteria": {
            "criterion_1_sample_size": "20 <= N_HBB_VUS <= 60",
            "criterion_2_within_category": "mean_within_category_auc(HBB) >= 0.60 and n_categories_with_auc >= 3",
            "criterion_3_topk_enrichment": "topK pearl-like enrichment fold >= 1.25 and one-sided hypergeom p <= 0.05",
        },
        "metrics": {
            "n_hbb_vus": n_vus,
            "top_k": k,
            "topk_pearl_like": topk_pearl,
            "total_pearl_like": total_pearl,
            "topk_pearl_like_rate": round(topk_rate, 6),
            "background_pearl_like_rate": round(bg_rate, 6),
            "enrichment_fold": round(fold, 6) if fold is not None else None,
            "enrichment_pvalue_one_sided_hypergeom": round(p_value, 8),
            "hbb_overall_auc": hbb_within.get("overall_auc"),
            "hbb_mean_within_category_auc": mean_within_auc,
            "hbb_n_categories_with_auc": n_within,
        },
        "criteria_results": {
            "criterion_1_sample_size_pass": c1,
            "criterion_2_within_category_pass": c2,
            "criterion_3_topk_enrichment_pass": c3,
        },
        "go_no_go": "GO" if go else "NO_GO",
        "no_go_reason": None
        if go
        else "At least one predeclared criterion failed; keep claim at EXPLORATORY and do not escalate to clinical utility claims.",
        "top_k_variants_by_lowest_lssim": [
            {
                "clinvar_id": r.get("ClinVar_ID"),
                "position_grch38": r.get("Position_GRCh38"),
                "category": r.get("Category"),
                "archcode_lssim": float(r.get("ARCHCODE_LSSIM") or 1.0),
                "discordance": r.get("Discordance"),
                "pearl_like": is_pearl_like(r),
            }
            for r in rows_sorted[:k]
        ],
        "hbb_within_category_details": hbb_within,
        "variant_rationale_sample": extract_rationale_sample(vus_json, max_items=5),
        "allowed_claims": [
            "Strict HBB VUS ranking diagnostics were computed with predeclared criteria.",
            "Go/No-Go decision is reproducible from local artifacts.",
            "Interpretation remains computational and hypothesis-level without wet-lab confirmation.",
        ],
        "blocked_claims": [
            "Clinical reclassification based on this report alone.",
            "Causal disease mechanism assignment without orthogonal experimental evidence.",
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
        fh.write("\n")

    print(f"HBB VUS validation report written: {output_path}")
    print(
        f"Go/No-Go: {report['go_no_go']} | N={n_vus} | top{k}={topk_pearl}/{k if k else 0} | p={report['metrics']['enrichment_pvalue_one_sided_hypergeom']}"
    )


if __name__ == "__main__":
    main()
