#!/usr/bin/env python3
"""
Pearl-like VUS enrichment by locus and by consequence (Category).

Hypothesis: among 641 pearl-like VUS there is enrichment in tissue-relevant loci
and/or in regulatory classes (promoter, intron, UTR). Uses Fisher exact and chi-squared.
Outputs: results/pearl_enrichment_report.json, results/pearl_enrichment_report.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

try:
    from scipy.stats import chi2_contingency, fisher_exact
except ImportError:
    chi2_contingency = None
    fisher_exact = None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def resolve_baseline_atlas_for_locus(locus: str) -> Path | None:
    candidates = sorted(RESULTS_DIR.glob(f"{locus}_Unified_Atlas_*.csv"))
    if not candidates:
        return None
    excluded_tokens = ("INVERTED", "POSITION_ONLY", "RANDOM", "UNIFORM_MEDIUM")
    filtered = [p for p in candidates if not any(tok in p.name for tok in excluded_tokens)]
    if not filtered:
        filtered = candidates
    canonical = [p for p in filtered if re.match(r"^[0-9]+kb\.csv$", p.name.split("_Unified_Atlas_", 1)[1])]
    pool = canonical if canonical else filtered
    return sorted(pool, key=lambda x: (len(x.name), x.name))[0] if pool else None


def locus_enrichment(vus_summary: dict[str, Any]) -> dict[str, Any]:
    """Build locus × (pearl_like yes/no) and run global chi2 + selected Fisher (locus vs rest)."""
    per_locus = vus_summary.get("per_locus") or vus_summary.get("per_locus_counts")
    if not per_locus:
        return {"error": "No per_locus in vus_reclassification_summary"}

    # Use "gene" or "locus" key
    rows = []
    for item in per_locus:
        locus = item.get("locus") or item.get("gene")
        in_window = int(item.get("in_window") or item.get("vus") or 0)
        pearl = int(item.get("pearl_like") or 0)
        if locus and in_window is not None and pearl is not None:
            rows.append({"locus": locus, "pearl_like": pearl, "not_pearl_like": in_window - pearl})

    if not rows:
        return {"error": "No locus rows"}

    # Contingency table: each row = locus, cols = [pearl_like, not_pearl_like]
    table = [[r["pearl_like"], r["not_pearl_like"]] for r in rows]

    out = {
        "locus_table": [{"locus": r["locus"], "pearl_like": r["pearl_like"], "not_pearl_like": r["not_pearl_like"]} for r in rows],
        "global_chi2": None,
        "fisher_locus_vs_rest": [],
    }

    if chi2_contingency and table:
        try:
            chi2, p, dof, expected = chi2_contingency(table)
            out["global_chi2"] = {"chi2": round(float(chi2), 6), "p_value": round(float(p), 6), "df": int(dof)}
        except Exception as e:
            out["global_chi2"] = {"error": str(e)}

    if fisher_exact:
        for r in rows:
            locus = r["locus"]
            a, b = r["pearl_like"], r["not_pearl_like"]
            rest_pearl = sum(x["pearl_like"] for x in rows if x["locus"] != locus)
            rest_not = sum(x["not_pearl_like"] for x in rows if x["locus"] != locus)
            try:
                odds, p = fisher_exact([[a, b], [rest_pearl, rest_not]])
                out["fisher_locus_vs_rest"].append({
                    "locus": locus,
                    "odds_ratio": round(float(odds), 4),
                    "p_value": round(float(p), 6),
                })
            except Exception as e:
                out["fisher_locus_vs_rest"].append({"locus": locus, "error": str(e)})

    return out


def consequence_enrichment(results_dir: Path, loci: list[str]) -> dict[str, Any]:
    """From atlases, collect VUS rows with Category and pearl_like; then Category × pearl enrichment."""
    category_pearl: dict[str, int] = {}
    category_not_pearl: dict[str, int] = {}

    for locus in loci:
        path = resolve_baseline_atlas_for_locus(locus)
        if not path or not path.exists():
            continue
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                verdict = (row.get("ARCHCODE_Verdict") or "").strip()
                if verdict != "VUS":
                    continue
                cat = (row.get("Category") or "").strip() or "unknown"
                discord = (row.get("Discordance") or "").strip().lower()
                pearl = (row.get("Pearl") or "").strip().lower() == "true" or discord in {"vep_only", "archcode_only"}
                if pearl:
                    category_pearl[cat] = category_pearl.get(cat, 0) + 1
                else:
                    category_not_pearl[cat] = category_not_pearl.get(cat, 0) + 1

    # Merge rare categories into "other" (e.g. < 10 total)
    min_count = 10
    all_cats = set(category_pearl.keys()) | set(category_not_pearl.keys())
    other_pearl = 0
    other_not = 0
    for c in list(all_cats):
        total = category_pearl.get(c, 0) + category_not_pearl.get(c, 0)
        if total < min_count:
            other_pearl += category_pearl.get(c, 0)
            other_not += category_not_pearl.get(c, 0)
            all_cats.discard(c)
            if c in category_pearl:
                del category_pearl[c]
            if c in category_not_pearl:
                del category_not_pearl[c]
    if other_pearl or other_not:
        category_pearl["other"] = category_pearl.get("other", 0) + other_pearl
        category_not_pearl["other"] = category_not_pearl.get("other", 0) + other_not
        all_cats.add("other")

    rows = []
    for cat in sorted(all_cats):
        p = category_pearl.get(cat, 0)
        n = category_not_pearl.get(cat, 0)
        rows.append({"category": cat, "pearl_like": p, "not_pearl_like": n})

    table = [[r["pearl_like"], r["not_pearl_like"]] for r in rows]
    out = {
        "category_table": rows,
        "contingency_chi2": None,
    }
    if chi2_contingency and table:
        try:
            chi2, p, dof, expected = chi2_contingency(table)
            out["contingency_chi2"] = {"chi2": round(float(chi2), 6), "p_value": round(float(p), 6), "df": int(dof)}
        except Exception as e:
            out["contingency_chi2"] = {"error": str(e)}
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Pearl-like VUS enrichment by locus and consequence")
    parser.add_argument(
        "--vus-summary",
        type=Path,
        default=RESULTS_DIR / "vus_reclassification_summary.json",
        help="Path to vus_reclassification_summary.json",
    )
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    parser.add_argument("-o", "--output-json", type=Path, default=RESULTS_DIR / "pearl_enrichment_report.json")
    parser.add_argument("--output-md", type=Path, default=RESULTS_DIR / "pearl_enrichment_report.md")
    args = parser.parse_args()

    if not args.vus_summary.is_file():
        raise SystemExit(f"VUS summary not found: {args.vus_summary}")

    vus = load_json(args.vus_summary)
    loci = [item.get("locus") or item.get("gene") for item in (vus.get("per_locus") or vus.get("per_locus_counts") or [])]
    loci = [x for x in loci if x]

    locus_out = locus_enrichment(vus)
    consequence_out = consequence_enrichment(args.results_dir, loci)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "Pearl-like VUS enrichment by locus and by consequence (Category)",
        "sources": {
            "vus_summary": str(args.vus_summary.resolve()),
            "atlases": "results/*_Unified_Atlas_*.csv (canonical)",
        },
        "locus_enrichment": locus_out,
        "consequence_enrichment": consequence_out,
        "interpretation": "Exploratory. Use for Limitations/Exploratory only; no strong claims without validation.",
    }

    out_json = args.output_json if args.output_json.is_absolute() else PROJECT_ROOT / args.output_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(f"JSON report: {out_json}")

    # Markdown report
    md_lines = [
        "# Pearl-like VUS enrichment (exploratory)",
        "",
        "**Hypothesis:** Among pearl-like VUS there is enrichment by locus and/or by consequence (regulatory classes).",
        "",
        "## Locus enrichment",
        "",
    ]
    if "locus_table" in locus_out:
        md_lines.append("| Locus | Pearl-like | Not pearl-like |")
        md_lines.append("|------|-----------|----------------|")
        for r in locus_out["locus_table"]:
            md_lines.append(f"| {r['locus']} | {r['pearl_like']} | {r['not_pearl_like']} |")
        md_lines.append("")
    if locus_out.get("global_chi2") and "p_value" in locus_out["global_chi2"]:
        g = locus_out["global_chi2"]
        md_lines.append(f"Global χ²: χ²={g['chi2']}, p={g['p_value']}.")
        md_lines.append("")
    if locus_out.get("fisher_locus_vs_rest"):
        md_lines.append("Fisher exact (locus vs rest):")
        for f in locus_out["fisher_locus_vs_rest"][:5]:
            if "p_value" in f:
                md_lines.append(f"- {f['locus']}: OR={f['odds_ratio']}, p={f['p_value']}")
        md_lines.append("")

    md_lines.append("## Consequence (Category) enrichment")
    md_lines.append("")
    if consequence_out.get("category_table"):
        md_lines.append("| Category | Pearl-like | Not pearl-like |")
        md_lines.append("|----------|-----------|----------------|")
        for r in consequence_out["category_table"]:
            md_lines.append(f"| {r['category']} | {r['pearl_like']} | {r['not_pearl_like']} |")
        md_lines.append("")
    if consequence_out.get("contingency_chi2") and "p_value" in (consequence_out["contingency_chi2"] or {}):
        c = consequence_out["contingency_chi2"]
        md_lines.append(f"χ² (Category × pearl): χ²={c['chi2']}, p={c['p_value']}.")
        md_lines.append("")

    md_lines.extend([
        "## Limitations",
        "",
        "- Exploratory only; no causal claims.",
        "- Category and locus definitions depend on atlas and summary sources.",
        "- Use wording for manuscript Limitations/Exploratory section only.",
        "",
    ])
    out_md = args.output_md if args.output_md.is_absolute() else PROJECT_ROOT / args.output_md
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        f.write("\n")
    print(f"MD report: {out_md}")


if __name__ == "__main__":
    main()
