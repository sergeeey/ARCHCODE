#!/usr/bin/env python3
"""
Low-Hanging Fruits Analysis — trust amplifiers for ARCHCODE v4
===============================================================
Computes 5 analyses in one script:
  D: Enhancer proximity odds ratios (500bp, 1kb thresholds)
  E: Threshold sensitivity (LSSIM 0.94/0.95/0.96)
  F: Leave-one-locus-out summary
  G: Q2a sub-classification
  H: Q2b composite ranking (top-10)
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

# ── Config (reused from discordance_v2_split.py) ─────────────────

BASE = Path(r"D:\ДНК")
RESULTS = BASE / "results"
CONFIG = BASE / "config" / "locus"
OUTPUT = BASE / "analysis"
OUTPUT.mkdir(exist_ok=True)

VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20

LOCUS_ATLAS = {
    "HBB": "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
    "TERT": "TERT_Unified_Atlas_300kb.csv",
    "GJB2": "GJB2_Unified_Atlas_300kb.csv",
}

LOCUS_CONFIG = {
    "HBB": "hbb_95kb_subTAD.json",
    "BRCA1": "brca1_400kb.json",
    "TP53": "tp53_300kb.json",
    "CFTR": "cftr_317kb.json",
    "MLH1": "mlh1_300kb.json",
    "LDLR": "ldlr_300kb.json",
    "SCN5A": "scn5a_400kb.json",
    "TERT": "tert_300kb.json",
    "GJB2": "gjb2_300kb.json",
}

TISSUE_MATCH = {
    "HBB": 1.0,
    "BRCA1": 0.5,
    "TP53": 0.5,
    "CFTR": 0.0,
    "MLH1": 0.5,
    "LDLR": 0.0,
    "SCN5A": 0.0,
    "TERT": 0.5,
    "GJB2": 0.0,
}


def load_locus_config(locus: str) -> dict:
    path = CONFIG / LOCUS_CONFIG[locus]
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {
        "enhancers": [e["position"] for e in cfg["features"]["enhancers"]],
        "ctcf_sites": [c["position"] for c in cfg["features"]["ctcf_sites"]],
    }


def compute_min_distance(positions: pd.Series, targets: list[int]) -> pd.Series:
    if not targets:
        return pd.Series(np.nan, index=positions.index)
    targets_arr = np.array(targets)
    return positions.apply(lambda p: int(np.min(np.abs(targets_arr - p))))


def load_all_data(lssim_threshold: float = 0.95) -> pd.DataFrame:
    frames = []
    for locus, fname in LOCUS_ATLAS.items():
        path = RESULTS / fname
        if not path.exists():
            continue
        df = pd.read_csv(path)
        df["Locus"] = locus
        df["Tissue_Match"] = TISSUE_MATCH[locus]
        cfg = load_locus_config(locus)
        df["Dist_Enhancer"] = compute_min_distance(df["Position_GRCh38"], cfg["enhancers"])
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)

    combined["ARCHCODE_HIGH"] = combined["ARCHCODE_LSSIM"] < lssim_threshold

    vep_high = combined["VEP_Score"] >= VEP_THRESHOLD
    cadd_vals = pd.to_numeric(combined.get("CADD_Phred", pd.Series(dtype=float)), errors="coerce")
    combined["SEQ_HIGH"] = vep_high | (cadd_vals >= CADD_THRESHOLD).fillna(False)

    conditions = [
        (combined["ARCHCODE_HIGH"]) & (combined["SEQ_HIGH"]),
        (combined["ARCHCODE_HIGH"]) & (~combined["SEQ_HIGH"]),
        (~combined["ARCHCODE_HIGH"]) & (combined["SEQ_HIGH"]),
        (~combined["ARCHCODE_HIGH"]) & (~combined["SEQ_HIGH"]),
    ]
    combined["Q"] = np.select(conditions, ["Q1", "Q2", "Q3", "Q4"], default="?")

    # Q2 subtype
    is_q2 = combined["Q"] == "Q2"
    vep_missing = combined["VEP_Score"] == -1
    combined["Q_sub"] = combined["Q"]
    combined.loc[is_q2 & vep_missing, "Q_sub"] = "Q2a"
    combined.loc[is_q2 & ~vep_missing, "Q_sub"] = "Q2b"

    return combined


# ══════════════════════════════════════════════════════════════════
# Task D: Enhancer proximity odds ratios
# ══════════════════════════════════════════════════════════════════


def task_d_proximity_odds(df: pd.DataFrame) -> dict:
    """Compute fraction and odds ratio of Q2b vs Q3 within distance thresholds."""
    q2b = df[df["Q_sub"] == "Q2b"]
    q3 = df[df["Q"] == "Q3"]

    results = {}
    for threshold in [500, 1000, 2000, 5000]:
        q2b_within = (q2b["Dist_Enhancer"] <= threshold).sum()
        q2b_total = len(q2b)
        q3_within = (q3["Dist_Enhancer"] <= threshold).sum()
        q3_total = len(q3)

        q2b_frac = q2b_within / q2b_total if q2b_total else 0
        q3_frac = q3_within / q3_total if q3_total else 0

        # 2x2 contingency: [within, outside] x [Q2b, Q3]
        table = np.array([[q2b_within, q3_within], [q2b_total - q2b_within, q3_total - q3_within]])
        or_val, p_val = stats.fisher_exact(table, alternative="greater")

        results[f"{threshold}bp"] = {
            "Q2b_within": int(q2b_within),
            "Q2b_total": int(q2b_total),
            "Q2b_fraction": round(q2b_frac, 3),
            "Q3_within": int(q3_within),
            "Q3_total": int(q3_total),
            "Q3_fraction": round(q3_frac, 3),
            "odds_ratio": round(or_val, 2),
            "fisher_p": f"{p_val:.2e}",
        }

    print("\n=== Task D: Enhancer Proximity Odds Ratios ===")
    for k, v in results.items():
        print(
            f"  {k}: Q2b {v['Q2b_fraction']:.1%} vs Q3 {v['Q3_fraction']:.1%}, "
            f"OR={v['odds_ratio']}, p={v['fisher_p']}"
        )

    return results


# ══════════════════════════════════════════════════════════════════
# Task E: Threshold sensitivity
# ══════════════════════════════════════════════════════════════════


def task_e_threshold_sensitivity() -> list[dict]:
    """How Q2b count and enhancer enrichment change with LSSIM threshold."""
    results = []
    for thresh in [0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98]:
        df = load_all_data(lssim_threshold=thresh)
        q2b = df[df["Q_sub"] == "Q2b"]
        q3 = df[df["Q"] == "Q3"]

        n_q2b = len(q2b)
        mean_dist_q2b = q2b["Dist_Enhancer"].mean() if n_q2b > 0 else np.nan
        mean_dist_q3 = q3["Dist_Enhancer"].mean() if len(q3) > 0 else np.nan

        # Mann-Whitney if enough data
        if n_q2b >= 3 and len(q3) >= 3:
            _, p = stats.mannwhitneyu(
                q2b["Dist_Enhancer"].dropna(), q3["Dist_Enhancer"].dropna(), alternative="less"
            )
        else:
            p = np.nan

        # Fraction within 1kb
        frac_1kb = (q2b["Dist_Enhancer"] <= 1000).mean() if n_q2b > 0 else np.nan

        # HBB-only Q2b
        n_hbb_q2b = len(q2b[q2b["Locus"] == "HBB"])

        results.append(
            {
                "LSSIM_threshold": thresh,
                "N_Q2b": n_q2b,
                "N_Q2b_HBB": n_hbb_q2b,
                "Mean_dist_Q2b_bp": round(mean_dist_q2b, 0)
                if not np.isnan(mean_dist_q2b)
                else None,
                "Mean_dist_Q3_bp": round(mean_dist_q3, 0) if not np.isnan(mean_dist_q3) else None,
                "Frac_Q2b_within_1kb": round(frac_1kb, 3) if not np.isnan(frac_1kb) else None,
                "MW_p_value": f"{p:.2e}" if not np.isnan(p) else "N/A",
            }
        )

    print("\n=== Task E: Threshold Sensitivity ===")
    for r in results:
        print(
            f"  LSSIM<{r['LSSIM_threshold']}: Q2b={r['N_Q2b']} (HBB={r['N_Q2b_HBB']}), "
            f"mean_dist={r['Mean_dist_Q2b_bp']}bp, within_1kb={r['Frac_Q2b_within_1kb']}, "
            f"p={r['MW_p_value']}"
        )

    return results


# ══════════════════════════════════════════════════════════════════
# Task F: Leave-one-locus-out
# ══════════════════════════════════════════════════════════════════


def task_f_leave_one_out(df: pd.DataFrame) -> list[dict]:
    """Summary statistics with each locus excluded."""
    results = []
    loci = list(LOCUS_ATLAS.keys())

    # Full dataset
    q2b_all = df[df["Q_sub"] == "Q2b"]
    q3_all = df[df["Q"] == "Q3"]
    _, p_all = stats.mannwhitneyu(
        q2b_all["Dist_Enhancer"].dropna(), q3_all["Dist_Enhancer"].dropna(), alternative="less"
    )
    results.append(
        {
            "Config": "All 9 loci",
            "N_total": len(df),
            "N_Q2b": len(q2b_all),
            "Mean_Q2b_dist": round(q2b_all["Dist_Enhancer"].mean(), 0),
            "Mean_Q3_dist": round(q3_all["Dist_Enhancer"].mean(), 0),
            "MW_p": f"{p_all:.2e}",
            "Enrichment_fold": round(
                q3_all["Dist_Enhancer"].mean() / q2b_all["Dist_Enhancer"].mean(), 1
            ),
        }
    )

    # HBB alone
    for single in ["HBB", "TERT"]:
        sub = df[df["Locus"] == single]
        q2b_s = sub[sub["Q_sub"] == "Q2b"]
        q3_s = sub[sub["Q"] == "Q3"]
        if len(q2b_s) >= 3 and len(q3_s) >= 3:
            _, p_s = stats.mannwhitneyu(
                q2b_s["Dist_Enhancer"].dropna(), q3_s["Dist_Enhancer"].dropna(), alternative="less"
            )
        else:
            p_s = np.nan
        results.append(
            {
                "Config": f"{single} only",
                "N_total": len(sub),
                "N_Q2b": len(q2b_s),
                "Mean_Q2b_dist": round(q2b_s["Dist_Enhancer"].mean(), 0) if len(q2b_s) else None,
                "Mean_Q3_dist": round(q3_s["Dist_Enhancer"].mean(), 0) if len(q3_s) else None,
                "MW_p": f"{p_s:.2e}" if not np.isnan(p_s) else "N/A",
                "Enrichment_fold": round(
                    q3_s["Dist_Enhancer"].mean() / q2b_s["Dist_Enhancer"].mean(), 1
                )
                if len(q2b_s) > 0 and q2b_s["Dist_Enhancer"].mean() > 0
                else None,
            }
        )

    # Exclude HBB
    sub_no_hbb = df[df["Locus"] != "HBB"]
    q2b_nh = sub_no_hbb[sub_no_hbb["Q_sub"] == "Q2b"]
    q3_nh = sub_no_hbb[sub_no_hbb["Q"] == "Q3"]
    if len(q2b_nh) >= 3 and len(q3_nh) >= 3:
        _, p_nh = stats.mannwhitneyu(
            q2b_nh["Dist_Enhancer"].dropna(), q3_nh["Dist_Enhancer"].dropna(), alternative="less"
        )
    else:
        p_nh = np.nan
    results.append(
        {
            "Config": "Exclude HBB",
            "N_total": len(sub_no_hbb),
            "N_Q2b": len(q2b_nh),
            "Mean_Q2b_dist": round(q2b_nh["Dist_Enhancer"].mean(), 0) if len(q2b_nh) else None,
            "Mean_Q3_dist": round(q3_nh["Dist_Enhancer"].mean(), 0) if len(q3_nh) else None,
            "MW_p": f"{p_nh:.2e}" if not np.isnan(p_nh) else "N/A",
            "Enrichment_fold": round(
                q3_nh["Dist_Enhancer"].mean() / q2b_nh["Dist_Enhancer"].mean(), 1
            )
            if len(q2b_nh) > 0 and q2b_nh["Dist_Enhancer"].mean() > 0
            else None,
        }
    )

    # Tissue-matched only (>=0.5)
    sub_matched = df[df["Tissue_Match"] >= 0.5]
    q2b_m = sub_matched[sub_matched["Q_sub"] == "Q2b"]
    q3_m = sub_matched[sub_matched["Q"] == "Q3"]
    if len(q2b_m) >= 3 and len(q3_m) >= 3:
        _, p_m = stats.mannwhitneyu(
            q2b_m["Dist_Enhancer"].dropna(), q3_m["Dist_Enhancer"].dropna(), alternative="less"
        )
    else:
        p_m = np.nan
    results.append(
        {
            "Config": "Tissue-matched only (≥0.5)",
            "N_total": len(sub_matched),
            "N_Q2b": len(q2b_m),
            "Mean_Q2b_dist": round(q2b_m["Dist_Enhancer"].mean(), 0) if len(q2b_m) else None,
            "Mean_Q3_dist": round(q3_m["Dist_Enhancer"].mean(), 0) if len(q3_m) else None,
            "MW_p": f"{p_m:.2e}" if not np.isnan(p_m) else "N/A",
            "Enrichment_fold": round(
                q3_m["Dist_Enhancer"].mean() / q2b_m["Dist_Enhancer"].mean(), 1
            )
            if len(q2b_m) > 0 and q2b_m["Dist_Enhancer"].mean() > 0
            else None,
        }
    )

    # Null controls only (tissue=0)
    sub_null = df[df["Tissue_Match"] == 0.0]
    q2b_n = sub_null[sub_null["Q_sub"] == "Q2b"]
    results.append(
        {
            "Config": "Null controls only (0.0)",
            "N_total": len(sub_null),
            "N_Q2b": len(q2b_n),
            "Mean_Q2b_dist": None,
            "Mean_Q3_dist": None,
            "MW_p": "N/A",
            "Enrichment_fold": None,
        }
    )

    print("\n=== Task F: Leave-One-Locus-Out ===")
    for r in results:
        print(
            f"  {r['Config']:30s} N={r['N_total']:>6}, Q2b={r['N_Q2b']:>3}, "
            f"fold={r['Enrichment_fold']}, p={r['MW_p']}"
        )

    return results


# ══════════════════════════════════════════════════════════════════
# Task G: Q2a sub-classification
# ══════════════════════════════════════════════════════════════════


def task_g_q2a_subclass(df: pd.DataFrame) -> dict:
    """Classify Q2a variants by WHY VEP couldn't score them."""
    q2a = df[df["Q_sub"] == "Q2a"].copy()

    # Sub-classify by VEP_Consequence (why VEP = -1)
    def classify_gap(row):
        cons = str(row.get("VEP_Consequence", "")).lower()
        cat = str(row.get("Category", "")).lower()

        if "frameshift" in cat:
            return "noncoding_frameshift"
        elif any(x in cons for x in ["intergenic", "downstream", "upstream"]):
            return "intergenic_unscored"
        elif cons in ["", "nan", "-1", "none", "other_variant (from_category)"]:
            return "annotation_missing"
        elif "coding_sequence" in cons or "synonymous" in cons:
            return "coding_consequence_gap"
        elif "splice" in cons:
            return "splice_model_gap"
        else:
            return "other_gap"

    q2a["Gap_Type"] = q2a.apply(classify_gap, axis=1)

    summary = (
        q2a.groupby("Gap_Type")
        .agg(
            N=("Gap_Type", "size"),
            N_Pathogenic=(
                "ClinVar_Significance",
                lambda x: x.str.lower().str.contains("pathogenic", na=False).sum(),
            ),
            Mean_LSSIM=("ARCHCODE_LSSIM", "mean"),
            Mean_Enhancer_Dist=("Dist_Enhancer", "mean"),
        )
        .reset_index()
    )
    summary = summary.sort_values("N", ascending=False)

    # Per-locus Q2a breakdown
    locus_breakdown = q2a.groupby(["Locus", "Gap_Type"]).size().unstack(fill_value=0)

    result = {
        "total_q2a": len(q2a),
        "gap_types": summary.to_dict(orient="records"),
        "per_locus": {locus: row.to_dict() for locus, row in locus_breakdown.iterrows()},
    }

    print("\n=== Task G: Q2a Sub-Classification ===")
    print(f"  Total Q2a: {len(q2a)}")
    for _, row in summary.iterrows():
        print(
            f"  {row['Gap_Type']:30s}: N={row['N']:>4}, "
            f"path={row['N_Pathogenic']:>4}, "
            f"LSSIM={row['Mean_LSSIM']:.3f}, "
            f"dist={row['Mean_Enhancer_Dist']:.0f}bp"
        )

    return result


# ══════════════════════════════════════════════════════════════════
# Task H: Q2b composite ranking
# ══════════════════════════════════════════════════════════════════


def task_h_q2b_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """Rank Q2b variants by composite priority score."""
    q2b = df[df["Q_sub"] == "Q2b"].copy()

    # Composite score components (all 0-1, higher = higher priority):
    # 1. Structural disruption: lower LSSIM = more disrupted = higher priority
    q2b["score_disruption"] = 1.0 - q2b["ARCHCODE_LSSIM"]

    # 2. Enhancer proximity: closer = higher priority (log-scaled)
    max_dist = q2b["Dist_Enhancer"].max()
    q2b["score_proximity"] = 1.0 - (np.log1p(q2b["Dist_Enhancer"]) / np.log1p(max_dist))

    # 3. Tissue match: 1.0 > 0.5 > 0.0
    q2b["score_tissue"] = q2b["Tissue_Match"]

    # 4. ClinVar pathogenicity: P/LP = 1.0, VUS = 0.5, B/LB = 0.0
    def clinvar_score(sig):
        sig = str(sig).lower()
        if "pathogenic" in sig and "benign" not in sig:
            return 1.0
        elif "benign" in sig and "pathogenic" not in sig:
            return 0.0
        else:
            return 0.5

    q2b["score_clinvar"] = q2b["ClinVar_Significance"].apply(clinvar_score)

    # 5. PCHi-C support (binary: HBB = 1, others = 0 for now)
    q2b["score_pchic"] = (q2b["Locus"] == "HBB").astype(float)

    # Composite: weighted sum
    q2b["Priority_Score"] = (
        0.30 * q2b["score_disruption"]
        + 0.25 * q2b["score_proximity"]
        + 0.20 * q2b["score_tissue"]
        + 0.15 * q2b["score_clinvar"]
        + 0.10 * q2b["score_pchic"]
    )

    q2b = q2b.sort_values("Priority_Score", ascending=False)

    # Top 10
    top10 = q2b.head(10)[
        [
            "ClinVar_ID",
            "Locus",
            "Position_GRCh38",
            "Category",
            "ARCHCODE_LSSIM",
            "VEP_Score",
            "Dist_Enhancer",
            "ClinVar_Significance",
            "Priority_Score",
        ]
    ].copy()
    top10["Priority_Score"] = top10["Priority_Score"].round(3)
    top10["ARCHCODE_LSSIM"] = top10["ARCHCODE_LSSIM"].round(4)

    print("\n=== Task H: Q2b Composite Ranking (Top 10) ===")
    for i, (_, row) in enumerate(top10.iterrows(), 1):
        print(
            f"  #{i}: {row['ClinVar_ID']} ({row['Locus']}) "
            f"LSSIM={row['ARCHCODE_LSSIM']}, dist={row['Dist_Enhancer']}bp, "
            f"score={row['Priority_Score']}"
        )

    return top10


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Loading data (LSSIM threshold = 0.95)...")
    df = load_all_data(lssim_threshold=0.95)
    print(f"Total: {len(df)} variants")

    # Task D
    odds_results = task_d_proximity_odds(df)

    # Task E
    sensitivity_results = task_e_threshold_sensitivity()

    # Task F
    loo_results = task_f_leave_one_out(df)

    # Task G
    q2a_results = task_g_q2a_subclass(df)

    # Task H
    top10 = task_h_q2b_ranking(df)

    # ── Save outputs ─────────────────────────────────────────────
    with open(OUTPUT / "enhancer_proximity_odds.json", "w") as f:
        json.dump(odds_results, f, indent=2)

    pd.DataFrame(sensitivity_results).to_csv(OUTPUT / "threshold_sensitivity.csv", index=False)

    pd.DataFrame(loo_results).to_csv(OUTPUT / "leave_one_locus_out.csv", index=False)

    with open(OUTPUT / "q2a_subclassification.json", "w") as f:
        json.dump(q2a_results, f, indent=2, default=str)

    top10.to_csv(OUTPUT / "q2b_top10_ranked.csv", index=False)

    print("\n=== All outputs saved to analysis/ ===")
    print("  enhancer_proximity_odds.json")
    print("  threshold_sensitivity.csv")
    print("  leave_one_locus_out.csv")
    print("  q2a_subclassification.json")
    print("  q2b_top10_ranked.csv")
