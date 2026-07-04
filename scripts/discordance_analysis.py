#!/usr/bin/env python3
"""
ARCHCODE Discordance Analysis — ARCHCODE vs Sequence-Based Predictors
=====================================================================
Builds 2×2 discordance matrix (ARCHCODE_HIGH/LOW × SEQ_HIGH/LOW),
analyzes Q2 structural blind spots, tissue specificity, and NMI.

ПОЧЕМУ: Доказательство что ARCHCODE и VEP/CADD захватывают разные
механистические оси патогенности. Q2 = enhancer-proximity variants
невидимые для sequence-based tools.
"""

import json
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import normalized_mutual_info_score

# ── Configuration ──────────────────────────────────────────────────

BASE = Path(r"D:\ДНК")
RESULTS = BASE / "results"
CONFIG = BASE / "config" / "locus"
OUTPUT = BASE / "analysis"
OUTPUT.mkdir(exist_ok=True)

# ПОЧЕМУ: LSSIM < 0.95 = структурное нарушение (established threshold from paper)
LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20

# Atlas file mapping (9 core loci)
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

# Config file mapping
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

# Tissue match score: 1=matched, 0.5=partial, 0=mismatched
# ПОЧЕМУ: K562 is erythroid leukemia; HBB is the most tissue-matched.
# Others range from partial (ubiquitous genes) to full mismatch.
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


# ── Step 0: Load and merge all data ───────────────────────────────


def load_locus_config(locus: str) -> dict:
    """Load enhancer and CTCF positions from config JSON."""
    path = CONFIG / LOCUS_CONFIG[locus]
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)

    enhancers = [e["position"] for e in cfg["features"]["enhancers"]]
    ctcf_sites = [c["position"] for c in cfg["features"]["ctcf_sites"]]
    return {"enhancers": enhancers, "ctcf_sites": ctcf_sites}


def compute_min_distance(positions: pd.Series, targets: list[int]) -> pd.Series:
    """Compute minimum distance from each position to nearest target."""
    if not targets:
        return pd.Series(np.nan, index=positions.index)
    targets_arr = np.array(targets)
    return positions.apply(lambda p: int(np.min(np.abs(targets_arr - p))))


def load_all_data() -> pd.DataFrame:
    """Load all 9 loci into a single DataFrame with computed distances."""
    frames = []
    for locus, fname in LOCUS_ATLAS.items():
        path = RESULTS / fname
        if not path.exists():
            print(f"WARNING: {path} not found, skipping {locus}")
            continue

        df = pd.read_csv(path)
        df["Locus"] = locus
        df["Tissue_Match"] = TISSUE_MATCH[locus]

        # Compute enhancer and CTCF distances
        cfg = load_locus_config(locus)
        df["Dist_Enhancer"] = compute_min_distance(df["Position_GRCh38"], cfg["enhancers"])
        df["Dist_CTCF"] = compute_min_distance(df["Position_GRCh38"], cfg["ctcf_sites"])

        frames.append(df)
        print(
            f"  {locus}: {len(df)} variants, "
            f"{len(cfg['enhancers'])} enhancers, "
            f"{len(cfg['ctcf_sites'])} CTCF sites"
        )

    combined = pd.concat(frames, ignore_index=True)
    print(f"\nTotal: {len(combined)} variants across {len(frames)} loci")
    return combined


# ── Step 1: Build 2×2 Discordance Matrix ──────────────────────────


def assign_quadrants(df: pd.DataFrame) -> pd.DataFrame:
    """Assign each variant to a discordance quadrant."""
    # ARCHCODE axis: structural disruption
    df["ARCHCODE_HIGH"] = df["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD

    # Sequence axis: VEP primary, CADD where available
    vep_high = df["VEP_Score"] >= VEP_THRESHOLD

    has_cadd = "CADD_Phred" in df.columns
    if has_cadd:
        cadd_vals = pd.to_numeric(df["CADD_Phred"], errors="coerce")
        cadd_high = cadd_vals >= CADD_THRESHOLD
        # SEQ_HIGH if VEP high OR CADD high (where CADD exists)
        df["SEQ_HIGH"] = vep_high | (cadd_high.fillna(False))
    else:
        df["SEQ_HIGH"] = vep_high

    # Quadrant assignment
    conditions = [
        (df["ARCHCODE_HIGH"]) & (df["SEQ_HIGH"]),
        (df["ARCHCODE_HIGH"]) & (~df["SEQ_HIGH"]),
        (~df["ARCHCODE_HIGH"]) & (df["SEQ_HIGH"]),
        (~df["ARCHCODE_HIGH"]) & (~df["SEQ_HIGH"]),
    ]
    labels = [
        "Q1: Concordant Pathogenic",
        "Q2: Structural Blind Spot",
        "Q3: Sequence Channel",
        "Q4: Concordant Benign",
    ]
    df["Quadrant"] = np.select(conditions, labels, default="Unknown")
    df["Q"] = np.select(conditions, ["Q1", "Q2", "Q3", "Q4"], default="?")
    return df


def quadrant_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-quadrant statistics."""
    # Normalize ClinVar significance
    df["Is_Pathogenic"] = df["ClinVar_Significance"].str.lower().str.contains(
        "pathogenic", na=False
    ) & ~df["ClinVar_Significance"].str.lower().str.contains("benign", na=False)
    df["Is_Benign"] = df["ClinVar_Significance"].str.lower().str.contains("benign", na=False) & ~df[
        "ClinVar_Significance"
    ].str.lower().str.contains("pathogenic", na=False)

    rows = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        sub = df[df["Q"] == q]
        n = len(sub)
        n_path = sub["Is_Pathogenic"].sum()
        n_ben = sub["Is_Benign"].sum()
        precision = n_path / n if n > 0 else 0
        pct = n / len(df) * 100

        # Top-3 functional categories
        top_cats = sub["Category"].value_counts().head(3)
        top_cats_str = ", ".join(f"{cat}({cnt})" for cat, cnt in top_cats.items())

        # Mean enhancer distance
        mean_enh = sub["Dist_Enhancer"].mean() if "Dist_Enhancer" in sub else np.nan

        rows.append(
            {
                "Quadrant": q,
                "N_Total": n,
                "N_Pathogenic": int(n_path),
                "N_Benign": int(n_ben),
                "Precision": round(precision, 4),
                "Pct_Dataset": round(pct, 2),
                "Mean_Enhancer_Dist": round(mean_enh, 0) if not np.isnan(mean_enh) else "N/A",
                "Top3_Categories": top_cats_str,
            }
        )

    return pd.DataFrame(rows)


# ── Step 2: Q2 Analysis (Structural Blind Spots) ──────────────────


def analyze_q2(df: pd.DataFrame) -> pd.DataFrame:
    """Deep analysis of Q2 (ARCHCODE_HIGH + SEQ_LOW) variants."""
    q2 = df[df["Q"] == "Q2"].copy()
    q3 = df[df["Q"] == "Q3"].copy()
    q4 = df[df["Q"] == "Q4"].copy()

    print(f"\n{'=' * 60}")
    print(f"Q2 STRUCTURAL BLIND SPOTS: {len(q2)} variants")
    print(f"{'=' * 60}")

    # a) Distribution by locus
    print("\nBy locus:")
    locus_dist = q2["Locus"].value_counts()
    for loc, cnt in locus_dist.items():
        total_loc = len(df[df["Locus"] == loc])
        print(f"  {loc}: {cnt} ({cnt / total_loc * 100:.1f}% of locus)")

    # b) Functional category distribution
    print("\nBy category:")
    cat_dist = q2["Category"].value_counts()
    for cat, cnt in cat_dist.items():
        print(f"  {cat}: {cnt}")

    # c) Enhancer distance: Q2 vs Q3
    if len(q2) > 0 and len(q3) > 0:
        q2_enh = q2["Dist_Enhancer"].dropna()
        q3_enh = q3["Dist_Enhancer"].dropna()
        q4_enh = q4["Dist_Enhancer"].dropna()

        if len(q2_enh) > 0 and len(q3_enh) > 0:
            u_stat_23, p_23 = stats.mannwhitneyu(q2_enh, q3_enh, alternative="less")
            print(f"\nEnhancer distance Q2 vs Q3:")
            print(f"  Q2 mean: {q2_enh.mean():.0f} bp, median: {q2_enh.median():.0f} bp")
            print(f"  Q3 mean: {q3_enh.mean():.0f} bp, median: {q3_enh.median():.0f} bp")
            print(f"  Mann-Whitney U (Q2 < Q3): U={u_stat_23:.0f}, p={p_23:.2e}")

        if len(q2_enh) > 0 and len(q4_enh) > 0:
            u_stat_24, p_24 = stats.mannwhitneyu(q2_enh, q4_enh, alternative="less")
            print(f"\nEnhancer distance Q2 vs Q4:")
            print(f"  Q4 mean: {q4_enh.mean():.0f} bp, median: {q4_enh.median():.0f} bp")
            print(f"  Mann-Whitney U (Q2 < Q4): U={u_stat_24:.0f}, p={p_24:.2e}")

    # d) CTCF distance
    if len(q2) > 0 and len(q3) > 0:
        q2_ctcf = q2["Dist_CTCF"].dropna()
        q3_ctcf = q3["Dist_CTCF"].dropna()
        if len(q2_ctcf) > 0 and len(q3_ctcf) > 0:
            u_ctcf, p_ctcf = stats.mannwhitneyu(q2_ctcf, q3_ctcf)
            print(f"\nCTCF distance Q2 vs Q3:")
            print(f"  Q2 mean: {q2_ctcf.mean():.0f} bp")
            print(f"  Q3 mean: {q3_ctcf.mean():.0f} bp")
            print(f"  Mann-Whitney U: U={u_ctcf:.0f}, p={p_ctcf:.2e}")

    # e) Pearl overlap
    if "Pearl" in q2.columns:
        pearl_q2 = q2["Pearl"].astype(str).str.lower().isin(["true", "yes", "1"]).sum()
        print(f"\nPearl overlap: {pearl_q2}/{len(q2)} Q2 variants are pearls")

    # f) ClinVar breakdown
    n_path_q2 = q2["Is_Pathogenic"].sum()
    n_ben_q2 = q2["Is_Benign"].sum()
    n_vus_q2 = len(q2) - n_path_q2 - n_ben_q2
    print(f"\nClinVar breakdown: P={n_path_q2}, B={n_ben_q2}, VUS/other={n_vus_q2}")

    q2.to_csv(OUTPUT / "Q2_structural_blindspots.csv", index=False)
    print(f"\nSaved: {OUTPUT / 'Q2_structural_blindspots.csv'}")
    return q2


# ── Step 3: Q3 Analysis (Sequence Channel) ────────────────────────


def analyze_q3(df: pd.DataFrame):
    """Analysis of Q3 (ARCHCODE_LOW + SEQ_HIGH) variants."""
    q2 = df[df["Q"] == "Q2"]
    q3 = df[df["Q"] == "Q3"]

    print(f"\n{'=' * 60}")
    print(f"Q3 SEQUENCE CHANNEL: {len(q3)} variants")
    print(f"{'=' * 60}")

    # Dominant categories
    print("\nBy category:")
    cat_dist = q3["Category"].value_counts()
    for cat, cnt in cat_dist.items():
        print(f"  {cat}: {cnt}")

    # Enhancer distance comparison
    if len(q2) > 0 and len(q3) > 0:
        q2_enh = q2["Dist_Enhancer"].dropna()
        q3_enh = q3["Dist_Enhancer"].dropna()
        if len(q2_enh) > 0 and len(q3_enh) > 0:
            t_stat, p_val = stats.ttest_ind(q3_enh, q2_enh, alternative="greater")
            print(f"\nEnhancer distance t-test (Q3 > Q2):")
            print(f"  Q3 mean: {q3_enh.mean():.0f} bp")
            print(f"  Q2 mean: {q2_enh.mean():.0f} bp")
            print(f"  t={t_stat:.3f}, p={p_val:.2e}")

    # CTCF distance comparison
    if len(q2) > 0 and len(q3) > 0:
        q2_ctcf = q2["Dist_CTCF"].dropna()
        q3_ctcf = q3["Dist_CTCF"].dropna()
        if len(q2_ctcf) > 0 and len(q3_ctcf) > 0:
            t_ctcf, p_ctcf = stats.ttest_ind(q3_ctcf, q2_ctcf, alternative="less")
            print(f"\nCTCF distance t-test (Q3 < Q2):")
            print(f"  Q3 mean: {q3_ctcf.mean():.0f} bp")
            print(f"  Q2 mean: {q2_ctcf.mean():.0f} bp")
            print(f"  t={t_ctcf:.3f}, p={p_ctcf:.2e}")

    # % in coding exons (proxy: missense + nonsense + frameshift)
    coding_cats = {"missense", "nonsense", "frameshift", "splice_donor", "splice_acceptor"}
    q2_coding = q2["Category"].isin(coding_cats).mean() * 100
    q3_coding = q3["Category"].isin(coding_cats).mean() * 100
    print(f"\n% coding-region variants: Q2={q2_coding:.1f}%, Q3={q3_coding:.1f}%")


# ── Step 4: Tissue Specificity of Discordance ─────────────────────


def tissue_specificity(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze Q2 proportion by locus and correlate with tissue match."""
    rows = []
    for locus in LOCUS_ATLAS:
        sub = df[df["Locus"] == locus]
        if len(sub) == 0:
            continue
        n_q2 = (sub["Q"] == "Q2").sum()
        n_q3 = (sub["Q"] == "Q3").sum()
        n_total = len(sub)
        q2_ratio = n_q2 / n_total if n_total > 0 else 0
        rows.append(
            {
                "Locus": locus,
                "N_Total": n_total,
                "N_Q2": n_q2,
                "N_Q3": n_q3,
                "Q2_Ratio": round(q2_ratio, 4),
                "Tissue_Match": TISSUE_MATCH[locus],
            }
        )

    result = pd.DataFrame(rows)

    # Spearman correlation
    if len(result) >= 3:
        rho, p_val = stats.spearmanr(result["Q2_Ratio"], result["Tissue_Match"])
        print(f"\n{'=' * 60}")
        print(f"TISSUE SPECIFICITY")
        print(f"{'=' * 60}")
        print(f"Spearman r (Q2_Ratio vs Tissue_Match): {rho:.3f}, p={p_val:.4f}")
        print(result.to_string(index=False))

    result.to_csv(OUTPUT / "discordance_by_locus.csv", index=False)
    return result


# ── Step 5: NMI Validation ─────────────────────────────────────────


def nmi_validation(df: pd.DataFrame) -> dict:
    """Compute Normalized Mutual Information between all metric pairs."""
    print(f"\n{'=' * 60}")
    print(f"NMI VALIDATION")
    print(f"{'=' * 60}")

    # Binary features
    lssim_bin = (df["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD).astype(int)
    vep_bin = (df["VEP_Score"] >= VEP_THRESHOLD).astype(int)
    clinvar_bin = df["Is_Pathogenic"].astype(int)

    results = {}

    # LSSIM vs VEP
    mask_vep = lssim_bin.notna() & vep_bin.notna()
    nmi_lv = normalized_mutual_info_score(lssim_bin[mask_vep], vep_bin[mask_vep])
    results["ARCHCODE_vs_VEP"] = round(nmi_lv, 4)
    print(f"NMI(ARCHCODE, VEP) = {nmi_lv:.4f}  (paper: 0.101)")

    # LSSIM vs CADD (where available)
    if "CADD_Phred" in df.columns:
        cadd_vals = pd.to_numeric(df["CADD_Phred"], errors="coerce")
        cadd_bin = (cadd_vals >= CADD_THRESHOLD).astype(int)
        mask_cadd = lssim_bin.notna() & cadd_bin.notna()
        if mask_cadd.sum() > 100:
            nmi_lc = normalized_mutual_info_score(lssim_bin[mask_cadd], cadd_bin[mask_cadd])
            results["ARCHCODE_vs_CADD"] = round(nmi_lc, 4)
            print(f"NMI(ARCHCODE, CADD) = {nmi_lc:.4f}  (paper: 0.024)")

            # VEP vs CADD
            mask_vc = vep_bin.notna() & cadd_bin.notna()
            if mask_vc.sum() > 100:
                nmi_vc = normalized_mutual_info_score(vep_bin[mask_vc], cadd_bin[mask_vc])
                results["VEP_vs_CADD"] = round(nmi_vc, 4)
                print(f"NMI(VEP, CADD) = {nmi_vc:.4f}  (paper: 0.231)")

    # LSSIM vs ClinVar
    mask_cv = lssim_bin.notna() & clinvar_bin.notna()
    nmi_lcv = normalized_mutual_info_score(lssim_bin[mask_cv], clinvar_bin[mask_cv])
    results["ARCHCODE_vs_ClinVar"] = round(nmi_lcv, 4)
    print(f"NMI(ARCHCODE, ClinVar) = {nmi_lcv:.4f}")

    # VEP vs ClinVar
    nmi_vcv = normalized_mutual_info_score(vep_bin[mask_cv], clinvar_bin[mask_cv])
    results["VEP_vs_ClinVar"] = round(nmi_vcv, 4)
    print(f"NMI(VEP, ClinVar) = {nmi_vcv:.4f}")

    return results


# ── Step 6: Figures ────────────────────────────────────────────────


def plot_discordance_scatter(df: pd.DataFrame):
    """Figure 1: 2×2 discordance scatter plot."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Color by ClinVar
    colors = []
    for _, row in df.iterrows():
        if row["Is_Pathogenic"]:
            colors.append("#d62728")  # red
        elif row["Is_Benign"]:
            colors.append("#1f77b4")  # blue
        else:
            colors.append("#999999")  # grey (VUS)

    vep_scores = df["VEP_Score"].fillna(0)
    lssim_scores = df["ARCHCODE_LSSIM"].fillna(1)

    ax.scatter(vep_scores, lssim_scores, c=colors, alpha=0.3, s=8, rasterized=True)

    # Quadrant lines
    ax.axhline(y=LSSIM_THRESHOLD, color="black", linestyle="--", linewidth=1, alpha=0.7)
    ax.axvline(x=VEP_THRESHOLD, color="black", linestyle="--", linewidth=1, alpha=0.7)

    # Quadrant labels with counts
    for q_label, x_pos, y_pos in [
        ("Q1", 0.75, 0.90),
        ("Q2", 0.25, 0.90),
        ("Q3", 0.75, 0.98),
        ("Q4", 0.25, 0.98),
    ]:
        n = (df["Q"] == q_label).sum()
        ax.text(
            x_pos,
            y_pos,
            f"{q_label}\nn={n}",
            transform=ax.transAxes,
            fontsize=11,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
        )

    # Highlight Q2 region
    ax.axhspan(
        ymin=ax.get_ylim()[0],
        ymax=LSSIM_THRESHOLD,
        xmin=0,
        xmax=VEP_THRESHOLD / ax.get_xlim()[1] if ax.get_xlim()[1] > 0 else 0.5,
        alpha=0.05,
        color="orange",
    )

    ax.set_xlabel("VEP Score", fontsize=12)
    ax.set_ylabel("ARCHCODE LSSIM", fontsize=12)
    ax.set_title(
        "Discordance Matrix: ARCHCODE vs VEP\n(30,325 ClinVar variants across 9 loci)", fontsize=13
    )
    ax.invert_yaxis()  # Lower LSSIM = more disruption → top

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor="#d62728", label="Pathogenic"),
        mpatches.Patch(facecolor="#1f77b4", label="Benign"),
        mpatches.Patch(facecolor="#999999", label="VUS/Other"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=10)

    plt.tight_layout()
    fig.savefig(OUTPUT / "fig1_discordance_scatter.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT / "fig1_discordance_scatter.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: fig1_discordance_scatter.png/pdf")


def plot_enhancer_distance(df: pd.DataFrame):
    """Figure 2: Enhancer distance by quadrant (violin + box)."""
    fig, ax = plt.subplots(figsize=(8, 6))

    data_by_q = []
    labels = []
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        vals = df[df["Q"] == q]["Dist_Enhancer"].dropna()
        if len(vals) > 0:
            data_by_q.append(np.log10(vals + 1))
            labels.append(f"{q}\n(n={len(vals)})")
        else:
            data_by_q.append(np.array([]))
            labels.append(f"{q}\n(n=0)")

    parts = ax.violinplot(
        [d for d in data_by_q if len(d) > 0],
        positions=[i + 1 for i, d in enumerate(data_by_q) if len(d) > 0],
        showmeans=True,
        showmedians=True,
    )

    ax.set_xticks(range(1, 5))
    ax.set_xticklabels(labels)
    ax.set_ylabel("log10(Distance to Nearest Enhancer + 1)", fontsize=11)
    ax.set_title("Enhancer Proximity by Discordance Quadrant", fontsize=13)

    # Statistical brackets
    q2_vals = df[df["Q"] == "Q2"]["Dist_Enhancer"].dropna()
    q3_vals = df[df["Q"] == "Q3"]["Dist_Enhancer"].dropna()
    if len(q2_vals) > 0 and len(q3_vals) > 0:
        _, p_23 = stats.mannwhitneyu(q2_vals, q3_vals, alternative="less")
        p_str = f"p={p_23:.2e}" if p_23 < 0.05 else f"p={p_23:.2f} (ns)"
        y_max = max(np.log10(q2_vals + 1).max(), np.log10(q3_vals + 1).max())
        ax.plot(
            [2, 2, 3, 3],
            [y_max + 0.2, y_max + 0.3, y_max + 0.3, y_max + 0.2],
            color="black",
            linewidth=1,
        )
        ax.text(2.5, y_max + 0.35, p_str, ha="center", fontsize=9)

    plt.tight_layout()
    fig.savefig(OUTPUT / "fig2_enhancer_distance.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT / "fig2_enhancer_distance.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: fig2_enhancer_distance.png/pdf")


def plot_locus_q2(locus_df: pd.DataFrame):
    """Figure 3: Q2 proportion by locus, colored by tissue match."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort by Q2_Ratio descending
    locus_df = locus_df.sort_values("Q2_Ratio", ascending=False)

    colors = []
    for tm in locus_df["Tissue_Match"]:
        if tm >= 0.8:
            colors.append("#2ca02c")  # green
        elif tm >= 0.3:
            colors.append("#ff7f0e")  # orange
        else:
            colors.append("#d62728")  # red

    bars = ax.bar(locus_df["Locus"], locus_df["Q2_Ratio"] * 100, color=colors, edgecolor="black")

    # Add count labels on bars
    for bar, n_q2 in zip(bars, locus_df["N_Q2"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f"n={n_q2}",
            ha="center",
            fontsize=9,
        )

    ax.set_ylabel("% Q2 (Structural Blind Spot) Variants", fontsize=11)
    ax.set_title("Tissue Specificity of Structural Blind Spots", fontsize=13)

    legend_elements = [
        mpatches.Patch(facecolor="#2ca02c", label="Tissue-matched"),
        mpatches.Patch(facecolor="#ff7f0e", label="Partial match"),
        mpatches.Patch(facecolor="#d62728", label="Tissue-mismatched"),
    ]
    ax.legend(handles=legend_elements, fontsize=10)

    plt.tight_layout()
    fig.savefig(OUTPUT / "fig3_locus_Q2.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT / "fig3_locus_Q2.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: fig3_locus_Q2.png/pdf")


def plot_nmi_heatmap(nmi_results: dict):
    """Figure 4: NMI heatmap."""
    # Build 4×4 matrix: ARCHCODE, VEP, CADD, ClinVar
    labels = ["ARCHCODE", "VEP", "CADD", "ClinVar"]
    matrix = np.ones((4, 4))  # diagonal = 1
    matrix[np.diag_indices(4)] = 1.0

    # Fill from results
    pair_map = {
        (0, 1): "ARCHCODE_vs_VEP",
        (0, 2): "ARCHCODE_vs_CADD",
        (1, 2): "VEP_vs_CADD",
        (0, 3): "ARCHCODE_vs_ClinVar",
        (1, 3): "VEP_vs_ClinVar",
    }
    for (i, j), key in pair_map.items():
        val = nmi_results.get(key, np.nan)
        if not np.isnan(val) if isinstance(val, float) else val is not None:
            matrix[i, j] = val
            matrix[j, i] = val
        else:
            matrix[i, j] = np.nan
            matrix[j, i] = np.nan

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=0.3)

    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_yticklabels(labels, fontsize=11)

    # Annotate values
    for i in range(4):
        for j in range(4):
            val = matrix[i, j]
            if not np.isnan(val):
                color = "white" if val > 0.15 else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.3f}",
                    ha="center",
                    va="center",
                    fontsize=12,
                    fontweight="bold",
                    color=color,
                )
            else:
                ax.text(j, i, "N/A", ha="center", va="center", fontsize=10, color="gray")

    ax.set_title(
        "Normalized Mutual Information\n(Low NMI = orthogonal information axes)", fontsize=13
    )
    plt.colorbar(im, ax=ax, label="NMI", shrink=0.8)

    plt.tight_layout()
    fig.savefig(OUTPUT / "fig4_NMI_heatmap.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUTPUT / "fig4_NMI_heatmap.pdf", bbox_inches="tight")
    plt.close()
    print(f"Saved: fig4_NMI_heatmap.png/pdf")


# ── Step 7: Report ─────────────────────────────────────────────────


def generate_report(
    df: pd.DataFrame,
    matrix_df: pd.DataFrame,
    locus_df: pd.DataFrame,
    nmi_results: dict,
):
    """Generate the final discordance report."""
    q2 = df[df["Q"] == "Q2"]
    q3 = df[df["Q"] == "Q3"]

    # Key tests
    q2_enh = q2["Dist_Enhancer"].dropna()
    q3_enh = q3["Dist_Enhancer"].dropna()
    _, p_enh_23 = (
        stats.mannwhitneyu(q2_enh, q3_enh, alternative="less")
        if len(q2_enh) > 0 and len(q3_enh) > 0
        else (0, 1)
    )

    rho_tissue, p_tissue = (
        stats.spearmanr(locus_df["Q2_Ratio"], locus_df["Tissue_Match"])
        if len(locus_df) >= 3
        else (0, 1)
    )

    # Hypothesis B verdict
    go_criteria = [
        p_enh_23 < 0.01,
        rho_tissue > 0.3 and p_tissue < 0.1,
        len(q2) > 50,
    ]
    verdict = "GO" if sum(go_criteria) >= 2 else "NO-GO"

    # NMI match check
    nmi_match = []
    if "ARCHCODE_vs_VEP" in nmi_results:
        diff = abs(nmi_results["ARCHCODE_vs_VEP"] - 0.101)
        nmi_match.append(
            f"ARCHCODE vs VEP: {nmi_results['ARCHCODE_vs_VEP']:.4f} (paper: 0.101, diff: {diff:.4f})"
        )
    if "ARCHCODE_vs_CADD" in nmi_results:
        diff = abs(nmi_results["ARCHCODE_vs_CADD"] - 0.024)
        nmi_match.append(
            f"ARCHCODE vs CADD: {nmi_results['ARCHCODE_vs_CADD']:.4f} (paper: 0.024, diff: {diff:.4f})"
        )
    if "VEP_vs_CADD" in nmi_results:
        diff = abs(nmi_results["VEP_vs_CADD"] - 0.231)
        nmi_match.append(
            f"VEP vs CADD: {nmi_results['VEP_vs_CADD']:.4f} (paper: 0.231, diff: {diff:.4f})"
        )

    report = f"""# ARCHCODE Discordance Analysis Report
## Date: 2026-03-09

## Key Finding

{"ARCHCODE captures a mechanistically distinct axis of pathogenicity: enhancer-proximal structural disruption invisible to VEP/CADD." if verdict == "GO" else "Insufficient evidence for distinct structural axis — Q2 variants do not show significant enhancer proximity enrichment."}

## 2×2 Matrix Results

Thresholds: LSSIM < {LSSIM_THRESHOLD} (structural), VEP >= {VEP_THRESHOLD} or CADD >= {CADD_THRESHOLD} (sequence)

{matrix_df.to_csv(index=False)}

Total variants: {len(df)}

## Q2 Structural Blind Spots

- **N total:** {len(q2)}
- **N pathogenic:** {int(q2["Is_Pathogenic"].sum())}
- **N benign:** {int(q2["Is_Benign"].sum())}
- **Mean enhancer distance:** {q2_enh.mean():.0f} bp (Q3: {q3_enh.mean():.0f} bp)
- **Mann-Whitney U (Q2 < Q3):** p={p_enh_23:.2e}
- **Dominant loci:** {", ".join(q2["Locus"].value_counts().head(3).index.tolist())}
- **Dominant categories:** {", ".join(q2["Category"].value_counts().head(3).index.tolist())}
- **Pearl overlap:** {q2["Pearl"].astype(str).str.lower().isin(["true", "yes", "1"]).sum()}/{len(q2)}

## Q3 Sequence Channel

- **N total:** {len(q3)}
- **Dominant categories:** {", ".join(q3["Category"].value_counts().head(3).index.tolist())}
- **Mean enhancer distance:** {q3_enh.mean():.0f} bp (vs Q2: {q2_enh.mean():.0f} bp)

## Tissue Specificity

{locus_df.to_csv(index=False)}

- **Spearman r (Q2_Ratio vs Tissue_Match):** {rho_tissue:.3f}
- **p-value:** {p_tissue:.4f}

## NMI Validation

{chr(10).join("- " + m for m in nmi_match) if nmi_match else "- CADD data not available for all loci"}

Full NMI results:
{json.dumps(nmi_results, indent=2)}

## Hypothesis B Status

**{verdict}**

Criteria met:
1. Enhancer proximity Q2 < Q3: {"PASS" if p_enh_23 < 0.01 else "FAIL"} (p={p_enh_23:.2e})
2. Tissue specificity correlation: {"PASS" if rho_tissue > 0.3 and p_tissue < 0.1 else "FAIL"} (rho={rho_tissue:.3f}, p={p_tissue:.4f})
3. Sufficient Q2 variants: {"PASS" if len(q2) > 50 else "FAIL"} (n={len(q2)})

## Next Steps

{"1. Integrate Q2 list into manuscript as Table N (Structural Blind Spots)" if verdict == "GO" else "1. Re-examine LSSIM threshold — try 0.90 instead of 0.95"}
{"2. Build per-locus Q2 case studies (HBB pearls as anchor)" if verdict == "GO" else "2. Check if tissue-matched loci alone show significance"}
{"3. Submit discordance figure to bioRxiv revision" if verdict == "GO" else "3. Consider restricting analysis to tissue-matched loci only"}
"""

    report_path = OUTPUT / "DISCORDANCE_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSaved: {report_path}")


# ── Main ───────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("ARCHCODE DISCORDANCE ANALYSIS")
    print("=" * 60)

    # Step 0: Load data
    print("\n[Step 0] Loading data...")
    df = load_all_data()

    # Step 1: Build 2×2 matrix
    print("\n[Step 1] Building 2×2 discordance matrix...")
    df = assign_quadrants(df)
    matrix_df = quadrant_stats(df)
    print(matrix_df.to_string(index=False))
    matrix_df.to_csv(OUTPUT / "discordance_2x2_matrix.csv", index=False)

    # Step 2: Q2 analysis
    print("\n[Step 2] Analyzing Q2 (Structural Blind Spots)...")
    q2 = analyze_q2(df)

    # Step 3: Q3 analysis
    print("\n[Step 3] Analyzing Q3 (Sequence Channel)...")
    analyze_q3(df)

    # Step 4: Tissue specificity
    print("\n[Step 4] Tissue specificity of discordance...")
    locus_df = tissue_specificity(df)

    # Step 5: NMI validation
    print("\n[Step 5] NMI validation...")
    nmi_results = nmi_validation(df)

    # Step 6: Figures
    print("\n[Step 6] Creating figures...")
    plot_discordance_scatter(df)
    plot_enhancer_distance(df)
    plot_locus_q2(locus_df)
    plot_nmi_heatmap(nmi_results)

    # Step 7: Report
    print("\n[Step 7] Generating report...")
    generate_report(df, matrix_df, locus_df, nmi_results)

    # Final: list all created files
    print(f"\n{'=' * 60}")
    print("CREATED FILES:")
    print(f"{'=' * 60}")
    for f in sorted(OUTPUT.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:45s} {size_kb:8.1f} KB")


if __name__ == "__main__":
    main()
