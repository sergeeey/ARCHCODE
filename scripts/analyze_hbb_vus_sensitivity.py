#!/usr/bin/env python3
"""
Sensitivity analysis for HBB VUS enrichment across multiple top-k thresholds.

This script is exploratory-only and does not modify strict decision artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def is_pearl_like(row: dict[str, str]) -> bool:
    pearl = (row.get("Pearl") or "").strip().lower() == "true"
    discord = (row.get("Discordance") or "").strip().lower()
    return pearl or discord in {"vep_only", "archcode_only"}


def hypergeom_tail(k: int, n: int, k_total: int, n_total: int) -> float:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="HBB VUS sensitivity analysis by top-k thresholds.")
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--atlas", default="results/HBB_Unified_Atlas_95kb.csv")
    parser.add_argument("--ks", default="5,10,15,20,25")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    atlas_path = PROJECT_ROOT / args.atlas
    out_path = (
        PROJECT_ROOT / args.output
        if args.output
        else RESULTS_DIR / f"hbb_vus_sensitivity_{args.date}.json"
    )
    ks = [int(x.strip()) for x in args.ks.split(",") if x.strip()]

    rows: list[dict[str, str]] = []
    with atlas_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("ARCHCODE_Verdict") or "").strip() == "VUS":
                rows.append(row)

    rows_sorted = sorted(rows, key=lambda r: float(r.get("ARCHCODE_LSSIM") or 1.0))
    n_vus = len(rows_sorted)
    pearl_flags = [is_pearl_like(r) for r in rows_sorted]
    total_pearl = sum(1 for x in pearl_flags if x)
    bg_rate = (total_pearl / n_vus) if n_vus else 0.0

    results = []
    for k_raw in ks:
        k = min(max(k_raw, 1), n_vus) if n_vus else 0
        topk_pearl = sum(1 for x in pearl_flags[:k]) if k else 0
        topk_rate = (topk_pearl / k) if k else 0.0
        fold = (topk_rate / bg_rate) if bg_rate > 0 else None
        pval = hypergeom_tail(topk_pearl, k, total_pearl, n_vus) if k else 1.0
        results.append(
            {
                "top_k": k,
                "topk_pearl_like": topk_pearl,
                "topk_rate": round(topk_rate, 6),
                "background_rate": round(bg_rate, 6),
                "enrichment_fold": round(fold, 6) if fold is not None else None,
                "enrichment_pvalue_one_sided_hypergeom": round(pval, 8),
                "passes_strict_gate_p_le_0_01": pval <= 0.01,
            }
        )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": "HBB_VUS_SENSITIVITY",
        "claim_level": "EXPLORATORY",
        "provenance": {"type": "COMPUTATIONAL_DERIVED", "source": str(atlas_path.relative_to(PROJECT_ROOT)).replace("\\", "/")},
        "n_hbb_vus": n_vus,
        "total_pearl_like": total_pearl,
        "background_rate": round(bg_rate, 6),
        "sensitivity_by_top_k": results,
        "note": "Sensitivity analysis only; strict Go/No-Go decision remains in hbb_vus_validation_report_2026-03-06.json.",
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")

    print(f"Saved: {out_path}")
    for row in results:
        print(
            f"k={row['top_k']}: pearl={row['topk_pearl_like']}, "
            f"fold={row['enrichment_fold']}, p={row['enrichment_pvalue_one_sided_hypergeom']}"
        )


if __name__ == "__main__":
    main()
