#!/usr/bin/env python3
"""
TERT Validation as Second Locus
================================
Reproduces HBB-like metrics for TERT:
  - Q1/Q2/Q3/Q4 distribution
  - Q2 precision
  - Enhancer distance Q2 vs Q3 (Mann-Whitney)
  - Pearl count (LSSIM < 0.95, CADD < 20, VEP < 0.5)
  - GO/NO-GO: Q2 enhancer distance < Q3, p < 0.01
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(r"D:\ДНК")
RESULTS = BASE / "results"
CONFIG = BASE / "config" / "locus"
OUTPUT = BASE / "analysis"

LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20


def load_tert():
    atlas = pd.read_csv(RESULTS / "TERT_Unified_Atlas_300kb.csv")
    cadd = pd.read_csv(RESULTS / "cadd_scores_TERT.csv")

    # Merge CADD scores (atlas already has CADD_Phred column but may have -1)
    # Use cadd file for more complete data
    cadd_map = cadd.set_index("ClinVar_ID")["CADD_Phred"].to_dict()
    atlas["CADD_Phred_file"] = atlas["ClinVar_ID"].map(cadd_map)
    # Prefer file CADD over atlas CADD where available and valid
    atlas_cadd = pd.to_numeric(atlas["CADD_Phred"], errors="coerce")
    file_cadd = pd.to_numeric(atlas["CADD_Phred_file"], errors="coerce")
    atlas["CADD_final"] = file_cadd.where(file_cadd.notna(), atlas_cadd)

    # Load config for enhancer/CTCF positions
    with open(CONFIG / "tert_300kb.json", encoding="utf-8") as f:
        cfg = json.load(f)
    enhancers = [e["position"] for e in cfg["features"]["enhancers"]]
    ctcf_sites = [c["position"] for c in cfg["features"]["ctcf_sites"]]

    # Compute distances
    enh_arr = np.array(enhancers)
    ctcf_arr = np.array(ctcf_sites)
    atlas["Dist_Enhancer"] = atlas["Position_GRCh38"].apply(
        lambda p: int(np.min(np.abs(enh_arr - p)))
    )
    atlas["Dist_CTCF"] = atlas["Position_GRCh38"].apply(lambda p: int(np.min(np.abs(ctcf_arr - p))))

    # Derived columns
    atlas["Is_Pathogenic"] = atlas["ClinVar_Significance"].str.lower().str.contains(
        "pathogenic", na=False
    ) & ~atlas["ClinVar_Significance"].str.lower().str.contains("benign", na=False)
    atlas["Is_Benign"] = atlas["ClinVar_Significance"].str.lower().str.contains(
        "benign", na=False
    ) & ~atlas["ClinVar_Significance"].str.lower().str.contains("pathogenic", na=False)

    # Quadrant assignment
    atlas["ARCHCODE_HIGH"] = atlas["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD
    vep_high = atlas["VEP_Score"] >= VEP_THRESHOLD
    cadd_high = (atlas["CADD_final"] >= CADD_THRESHOLD).fillna(False)
    atlas["SEQ_HIGH"] = vep_high | cadd_high

    conditions = [
        (atlas["ARCHCODE_HIGH"]) & (atlas["SEQ_HIGH"]),
        (atlas["ARCHCODE_HIGH"]) & (~atlas["SEQ_HIGH"]),
        (~atlas["ARCHCODE_HIGH"]) & (atlas["SEQ_HIGH"]),
        (~atlas["ARCHCODE_HIGH"]) & (~atlas["SEQ_HIGH"]),
    ]
    atlas["Q"] = np.select(conditions, ["Q1", "Q2", "Q3", "Q4"], default="?")

    return atlas


def analyze(df):
    print("=" * 60)
    print("TERT VALIDATION AS SECOND LOCUS")
    print("=" * 60)
    print(f"Total TERT variants: {len(df)}")
    print()

    # Q distribution
    print("--- Q1/Q2/Q3/Q4 Distribution ---")
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        sub = df[df["Q"] == q]
        n_path = sub["Is_Pathogenic"].sum()
        n_ben = sub["Is_Benign"].sum()
        precision = n_path / len(sub) if len(sub) > 0 else 0
        mean_enh = sub["Dist_Enhancer"].mean() if len(sub) > 0 else float("nan")
        print(
            f"  {q}: N={len(sub):4d}, Path={n_path:3d}, Ben={n_ben:3d}, "
            f"Precision={precision:.3f}, MeanEnhDist={mean_enh:.0f}bp"
        )

    q2 = df[df["Q"] == "Q2"]
    q3 = df[df["Q"] == "Q3"]

    # Q2 precision
    q2_precision = q2["Is_Pathogenic"].mean() if len(q2) > 0 else 0
    print(f"\nQ2 Precision (pathogenic fraction): {q2_precision:.3f} (N={len(q2)})")

    # Q2 vs Q3 enhancer distance
    q2_enh = q2["Dist_Enhancer"].dropna()
    q3_enh = q3["Dist_Enhancer"].dropna()

    if len(q2_enh) > 0 and len(q3_enh) > 0:
        u, p_mw = stats.mannwhitneyu(q2_enh, q3_enh, alternative="less")
        print(f"\nEnhancer Distance Q2 vs Q3:")
        print(f"  Q2 mean: {q2_enh.mean():.0f} bp (median: {q2_enh.median():.0f})")
        print(f"  Q3 mean: {q3_enh.mean():.0f} bp (median: {q3_enh.median():.0f})")
        print(f"  Mann-Whitney U={u:.0f}, p={p_mw:.2e} (one-sided: Q2 < Q3)")
        print(f"  Ratio Q3/Q2: {q3_enh.mean() / q2_enh.mean():.1f}x")
    else:
        p_mw = 1.0
        print(f"\nInsufficient data for Q2 vs Q3 comparison (Q2={len(q2_enh)}, Q3={len(q3_enh)})")

    # Pearls: LSSIM < 0.95 AND CADD < 20 AND VEP < 0.5
    # (variants where sequence tools miss but ARCHCODE catches)
    pearl_mask = (
        (df["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD)
        & ((df["CADD_final"] < CADD_THRESHOLD) | df["CADD_final"].isna())
        & (df["VEP_Score"] < VEP_THRESHOLD)
    )
    pearls = df[pearl_mask]
    n_pearls = len(pearls)
    n_pearls_path = pearls["Is_Pathogenic"].sum()

    print(f"\nPearls (LSSIM < 0.95, CADD < 20, VEP < 0.5):")
    print(f"  N total: {n_pearls}")
    print(f"  N pathogenic: {n_pearls_path}")
    if n_pearls > 0:
        print(f"  Mean LSSIM: {pearls['ARCHCODE_LSSIM'].mean():.4f}")
        print(f"  Mean enhancer dist: {pearls['Dist_Enhancer'].mean():.0f} bp")
        cats = pearls["Category"].value_counts()
        print(f"  Categories: {', '.join(f'{c}({n})' for c, n in cats.head(5).items())}")

    # Q2a/Q2b split
    q2a = q2[q2["VEP_Score"] == -1.0]
    q2b = q2[(q2["VEP_Score"] >= 0) & (q2["VEP_Score"] < VEP_THRESHOLD)]
    print(f"\nQ2 Split:")
    print(f"  Q2a (VEP coverage gap): {len(q2a)}")
    print(f"  Q2b (true blind spots): {len(q2b)}")

    if len(q2b) > 0:
        q2b_enh = q2b["Dist_Enhancer"].dropna()
        if len(q2b_enh) > 0 and len(q3_enh) > 0:
            u2b, p2b = stats.mannwhitneyu(q2b_enh, q3_enh, alternative="less")
            print(f"  Q2b mean enhancer dist: {q2b_enh.mean():.0f} bp")
            print(f"  Q2b vs Q3: U={u2b:.0f}, p={p2b:.2e}")

    # GO/NO-GO
    print(f"\n{'=' * 60}")
    print("GO / NO-GO ASSESSMENT")
    print(f"{'=' * 60}")

    go_criteria = []

    # Criterion 1: p < 0.01
    c1 = p_mw < 0.01
    go_criteria.append(c1)
    print(f"  1. Q2 enhancer dist < Q3 (p < 0.01): {'PASS' if c1 else 'FAIL'} (p={p_mw:.2e})")

    # Criterion 2: N_Q2 > 20
    c2 = len(q2) > 20
    go_criteria.append(c2)
    print(f"  2. N_Q2 > 20: {'PASS' if c2 else 'FAIL'} (N_Q2={len(q2)})")

    # Criterion 3: Q2 precision > 0.5
    c3 = q2_precision > 0.5
    go_criteria.append(c3)
    print(f"  3. Q2 precision > 0.5: {'PASS' if c3 else 'FAIL'} (precision={q2_precision:.3f})")

    # Criterion 4: pearls exist
    c4 = n_pearls > 0
    go_criteria.append(c4)
    print(f"  4. Pearls > 0: {'PASS' if c4 else 'FAIL'} (N={n_pearls})")

    if all(go_criteria):
        verdict = "GO — TERT = SECONDARY LOCUS"
    elif c1 and c2:
        verdict = "CONDITIONAL GO — TERT = secondary locus (some criteria marginal)"
    else:
        verdict = "NO-GO — TERT = EXPLORATORY (HBB primary only)"
    print(f"\n  VERDICT: {verdict}")

    return {
        "p_mw": p_mw,
        "n_q2": len(q2),
        "q2_precision": q2_precision,
        "n_pearls": n_pearls,
        "verdict": verdict,
        "q2": q2,
        "q3": q3,
        "pearls": pearls,
    }


def save_validation(df, results):
    # Save full TERT validation table
    out_cols = [
        "ClinVar_ID",
        "Position_GRCh38",
        "Ref",
        "Alt",
        "HGVS_c",
        "HGVS_p",
        "Category",
        "ClinVar_Significance",
        "ARCHCODE_LSSIM",
        "VEP_Score",
        "CADD_final",
        "Dist_Enhancer",
        "Dist_CTCF",
        "Is_Pathogenic",
        "Is_Benign",
        "ARCHCODE_HIGH",
        "SEQ_HIGH",
        "Q",
    ]
    existing = [c for c in out_cols if c in df.columns]
    out = df[existing].copy()
    out = out.rename(columns={"CADD_final": "CADD_Phred"})
    out.to_csv(OUTPUT / "TERT_validation.csv", index=False)
    print(f"\nSaved: {OUTPUT / 'TERT_validation.csv'} ({len(out)} rows)")

    # Summary JSON
    summary = {
        "locus": "TERT",
        "n_total": len(df),
        "n_q1": int((df["Q"] == "Q1").sum()),
        "n_q2": int((df["Q"] == "Q2").sum()),
        "n_q3": int((df["Q"] == "Q3").sum()),
        "n_q4": int((df["Q"] == "Q4").sum()),
        "q2_precision": round(results["q2_precision"], 4),
        "q2_mean_enhancer_dist": round(results["q2"]["Dist_Enhancer"].mean(), 0),
        "q3_mean_enhancer_dist": round(results["q3"]["Dist_Enhancer"].mean(), 0),
        "p_mannwhitney_q2_lt_q3": float(f"{results['p_mw']:.4e}"),
        "n_pearls": results["n_pearls"],
        "verdict": results["verdict"],
    }
    with open(OUTPUT / "TERT_validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved: {OUTPUT / 'TERT_validation_summary.json'}")


def main():
    df = load_tert()
    results = analyze(df)
    save_validation(df, results)


if __name__ == "__main__":
    main()
