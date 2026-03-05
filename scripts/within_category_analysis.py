"""Within-category AUC analysis for ARCHCODE.

Addresses category leakage concern: is ARCHCODE discrimination driven by
LOF vs non-LOF category distribution, or does it work WITHIN categories?

Outputs: JSON summary + Supplementary Table S3
"""

import argparse
import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.metrics import roc_auc_score

RESULTS_DIR = Path("D:/ДНК/results")
OUTPUT_JSON = RESULTS_DIR / "within_category_analysis.json"
DEFAULT_OUTPUT_TABLE = RESULTS_DIR / "TABLE_S3_within_category.txt"

# All atlas files
ATLAS_FILES = {
    "HBB": RESULTS_DIR / "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    "CFTR": RESULTS_DIR / "CFTR_Unified_Atlas_317kb.csv",
    "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
    "MLH1": RESULTS_DIR / "MLH1_Unified_Atlas_300kb.csv",
    "LDLR": RESULTS_DIR / "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": RESULTS_DIR / "SCN5A_Unified_Atlas_400kb.csv",
    "TERT": RESULTS_DIR / "TERT_Unified_Atlas_300kb.csv",
    "GJB2": RESULTS_DIR / "GJB2_Unified_Atlas_300kb.csv",
}


def load_atlas(path):
    df = pd.read_csv(path)
    # Standardize label
    df["binary_label"] = df["Label"].map({"Pathogenic": 1, "Benign": 0})
    df = df.dropna(subset=["binary_label", "ARCHCODE_LSSIM"])
    df["binary_label"] = df["binary_label"].astype(int)
    return df


def compute_category_stats(df, locus_name):
    results = []
    categories = df["Category"].dropna().unique()

    for cat in sorted(categories):
        sub = df[df["Category"] == cat]
        n_path = (sub["binary_label"] == 1).sum()
        n_ben = (sub["binary_label"] == 0).sum()
        n_total = len(sub)

        mean_lssim_path = sub.loc[sub["binary_label"] == 1, "ARCHCODE_LSSIM"].mean()
        mean_lssim_ben = sub.loc[sub["binary_label"] == 0, "ARCHCODE_LSSIM"].mean()
        delta = mean_lssim_ben - mean_lssim_path if pd.notna(mean_lssim_ben) and pd.notna(mean_lssim_path) else None

        # AUC only if both classes present and n >= 5
        auc = None
        if n_path >= 3 and n_ben >= 3:
            try:
                # For LSSIM, lower = more pathogenic, so use 1-LSSIM as score
                auc = roc_auc_score(sub["binary_label"], 1 - sub["ARCHCODE_LSSIM"])
                auc = round(auc, 4)
            except ValueError:
                pass

        results.append({
            "locus": locus_name,
            "category": cat,
            "n_total": int(n_total),
            "n_pathogenic": int(n_path),
            "n_benign": int(n_ben),
            "mean_lssim_pathogenic": round(float(mean_lssim_path), 6) if pd.notna(mean_lssim_path) else None,
            "mean_lssim_benign": round(float(mean_lssim_ben), 6) if pd.notna(mean_lssim_ben) else None,
            "delta_lssim": round(float(delta), 6) if delta is not None else None,
            "within_category_auc": auc,
        })

    return results


def overall_auc(df):
    if df["binary_label"].nunique() < 2:
        return None
    try:
        return round(roc_auc_score(df["binary_label"], 1 - df["ARCHCODE_LSSIM"]), 4)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Within-category AUC analysis for ARCHCODE.")
    parser.add_argument("--output-json", default=str(OUTPUT_JSON))
    parser.add_argument("--output-table", default=str(DEFAULT_OUTPUT_TABLE))
    args = parser.parse_args()

    output_json_path = Path(args.output_json)
    output_table_path = Path(args.output_table)

    all_results = []
    locus_summaries = []

    for locus, path in ATLAS_FILES.items():
        if not path.exists():
            print(f"SKIP: {locus} — file not found")
            continue

        df = load_atlas(path)
        n_path = (df["binary_label"] == 1).sum()
        n_ben = (df["binary_label"] == 0).sum()

        full_auc = overall_auc(df)
        cat_results = compute_category_stats(df, locus)
        all_results.extend(cat_results)

        # Categories with valid within-category AUC
        valid_aucs = [r for r in cat_results if r["within_category_auc"] is not None]
        mean_within_auc = np.mean([r["within_category_auc"] for r in valid_aucs]) if valid_aucs else None

        locus_summaries.append({
            "locus": locus,
            "n_variants": len(df),
            "n_pathogenic": int(n_path),
            "n_benign": int(n_ben),
            "overall_auc": full_auc,
            "n_categories_with_auc": len(valid_aucs),
            "mean_within_category_auc": round(float(mean_within_auc), 4) if mean_within_auc else None,
            "categories": cat_results,
        })

        print(f"\n{locus}: n={len(df)} (P={n_path}, B={n_ben}), Overall AUC={full_auc}")
        for r in cat_results:
            auc_str = f"AUC={r['within_category_auc']}" if r['within_category_auc'] else "AUC=n/a"
            delta_str = f"Δ={r['delta_lssim']:.4f}" if r['delta_lssim'] is not None else "Δ=n/a"
            print(f"  {r['category']:25s}  P={r['n_pathogenic']:4d}  B={r['n_benign']:4d}  {delta_str}  {auc_str}")

    # Save JSON
    output = {
        "analysis": "within_category_auc",
        "purpose": "Address category leakage concern: does ARCHCODE discriminate WITHIN variant categories?",
        "method": "Per-category ROC AUC using 1-LSSIM as score, minimum 3 per class",
        "loci": locus_summaries,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nJSON saved: {output_json_path}")

    # Generate Supplementary Table S3
    lines = [
        "SUPPLEMENTARY TABLE S3 — Within-Category ARCHCODE Discrimination",
        "=" * 70,
        "",
        "Purpose: Address whether ARCHCODE AUC is driven by variant category",
        "(LOF vs non-LOF) rather than positional structural prediction.",
        "",
        "Method: ROC AUC computed separately for each variant category where",
        "both pathogenic (n >= 3) and benign (n >= 3) variants exist.",
        "Score: 1 - LSSIM (higher = more structurally disrupted).",
        "",
        f"{'Locus':<8} {'Category':<25} {'N_P':>5} {'N_B':>5} {'Delta_LSSIM':>12} {'AUC':>8}",
        "-" * 70,
    ]

    for locus_sum in locus_summaries:
        locus = locus_sum["locus"]
        # Overall row
        lines.append(f"{locus:<8} {'ALL (overall)':25s} {locus_sum['n_pathogenic']:5d} {locus_sum['n_benign']:5d} {'':>12} {locus_sum['overall_auc'] or 'n/a':>8}")
        for r in locus_sum["categories"]:
            delta_str = f"{r['delta_lssim']:.6f}" if r['delta_lssim'] is not None else "n/a"
            auc_str = f"{r['within_category_auc']:.4f}" if r['within_category_auc'] is not None else "n/a"
            lines.append(f"{'':8s} {r['category']:<25} {r['n_pathogenic']:5d} {r['n_benign']:5d} {delta_str:>12} {auc_str:>8}")
        lines.append("")

    # Summary
    all_valid = [r for r in all_results if r["within_category_auc"] is not None]
    if all_valid:
        aucs = [r["within_category_auc"] for r in all_valid]
        lines.append("-" * 70)
        lines.append(f"Categories with computable AUC: {len(all_valid)}")
        lines.append(f"Mean within-category AUC: {np.mean(aucs):.4f}")
        lines.append(f"Median within-category AUC: {np.median(aucs):.4f}")
        lines.append(f"Range: {min(aucs):.4f} - {max(aucs):.4f}")
        lines.append("")
        lines.append("INTERPRETATION: If mean within-category AUC is substantially")
        lines.append("above 0.50, ARCHCODE discriminates WITHIN categories, not just")
        lines.append("between them. Category leakage alone cannot explain the signal.")

    table_text = "\n".join(lines) + "\n"

    output_table_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_table_path, "w", encoding="utf-8") as f:
        f.write(table_text)
    print(f"Table saved: {output_table_path}")


if __name__ == "__main__":
    main()
