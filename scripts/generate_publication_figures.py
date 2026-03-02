#!/usr/bin/env python3
"""
ARCHCODE Publication Figures — Master Generation Script.

Generates all 6 publication-quality figures for the bioRxiv preprint.
Output: figures/fig{N}_{name}.pdf + .png (300 DPI)

Usage:
    python scripts/generate_publication_figures.py

Dependencies: matplotlib, seaborn, pandas, numpy, scipy, sklearn
"""

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch
from scipy import stats
from sklearn.metrics import roc_curve, auc

warnings.filterwarnings("ignore", category=FutureWarning)

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
CONFIG = ROOT / "config" / "locus"

ATLAS_CAT = RESULTS / "HBB_Unified_Atlas_95kb.csv"
ATLAS_POS = RESULTS / "HBB_Unified_Atlas_95kb_POSITION_ONLY.csv"
CONTROL_JSON = RESULTS / "position_only_control_experiment.json"

FIGURES.mkdir(parents=True, exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────
# Publication-quality defaults (Nature/Cell style)
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 10,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.05,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.5,
    "ytick.major.width": 0.5,
    "lines.linewidth": 1.0,
    "pdf.fonttype": 42,  # TrueType for editability
    "ps.fonttype": 42,
})

# Color palette
C_PATH = "#C0392B"   # pathogenic red
C_BEN = "#2980B9"    # benign blue
C_PEARL = "#E74C3C"  # pearl highlight
C_GRAY = "#95A5A6"   # neutral gray
C_DARK = "#2C3E50"   # text dark

# Category sort order (by mean LSSIM, most disrupted first)
CAT_ORDER = [
    "nonsense", "frameshift", "splice_acceptor", "splice_donor",
    "splice_region", "promoter", "missense", "5_prime_UTR",
    "other", "3_prime_UTR", "intronic", "synonymous",
]

MM_TO_INCH = 1 / 25.4  # conversion factor


def save_fig(fig, name):
    """Save figure as both PDF and PNG."""
    pdf_path = FIGURES / f"{name}.pdf"
    png_path = FIGURES / f"{name}.png"
    fig.savefig(str(pdf_path), format="pdf", facecolor="white")
    fig.savefig(str(png_path), format="png", facecolor="white")
    print(f"  Saved: {pdf_path.name} + {png_path.name}")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════
# Figure 1: SSIM Distribution by Category (violin + strip)
# ══════════════════════════════════════════════════════════════════════
def figure1_ssim_violin():
    print("\n[Fig 1] SSIM Distribution by Category...")
    df = pd.read_csv(ATLAS_CAT)

    # Filter to categories present and sort
    cats_present = [c for c in CAT_ORDER if c in df["Category"].unique()]
    df_plot = df[df["Category"].isin(cats_present)].copy()
    df_plot["Category"] = pd.Categorical(df_plot["Category"], categories=cats_present, ordered=True)

    fig, ax = plt.subplots(figsize=(184 * MM_TO_INCH, 100 * MM_TO_INCH))

    # Violin plot split by Label
    sns.violinplot(
        data=df_plot, x="Category", y="ARCHCODE_LSSIM", hue="Label",
        split=True, inner=None, linewidth=0.5, saturation=0.8,
        palette={"Pathogenic": C_PATH, "Benign": C_BEN},
        ax=ax, density_norm="width", cut=0,
    )

    # Strip plot for individual points
    sns.stripplot(
        data=df_plot, x="Category", y="ARCHCODE_LSSIM", hue="Label",
        dodge=True, size=1.5, alpha=0.4, jitter=0.15,
        palette={"Pathogenic": C_PATH, "Benign": C_BEN},
        ax=ax, legend=False,
    )

    # Pearl overlay (diamonds)
    pearls = df_plot[df_plot["Pearl"] == True]
    if len(pearls) > 0:
        for cat_name in pearls["Category"].unique():
            cat_idx = cats_present.index(cat_name)
            cat_pearls = pearls[pearls["Category"] == cat_name]
            ax.scatter(
                [cat_idx] * len(cat_pearls), cat_pearls["ARCHCODE_LSSIM"],
                marker="D", s=25, c=C_PEARL, edgecolors="black",
                linewidths=0.5, zorder=10, label="_nolegend_",
            )

    # Threshold lines
    ax.axhline(y=0.85, color=C_PATH, linewidth=0.6, linestyle="--", alpha=0.5)
    ax.axhline(y=0.95, color=C_GRAY, linewidth=0.6, linestyle=":", alpha=0.5)
    ax.text(len(cats_present) - 0.5, 0.847, "PATHOGENIC", fontsize=5.5,
            color=C_PATH, alpha=0.7, ha="right", va="top")
    ax.text(len(cats_present) - 0.5, 0.953, "VUS/LB", fontsize=5.5,
            color=C_GRAY, alpha=0.7, ha="right", va="bottom")

    # Category counts
    for i, cat in enumerate(cats_present):
        n = len(df_plot[df_plot["Category"] == cat])
        ax.text(i, ax.get_ylim()[0] + 0.005, f"n={n}", fontsize=5.5,
                ha="center", va="bottom", color=C_DARK, alpha=0.6)

    ax.set_xlabel("")
    ax.set_ylabel("ARCHCODE LSSIM")
    ax.set_title("Figure 1. LSSIM Distribution Across Variant Categories (HBB, n=1,103)",
                 fontweight="bold", pad=8)
    ax.set_xticklabels([c.replace("_", "\n") for c in cats_present], rotation=0)

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    # Add pearl marker to legend
    from matplotlib.lines import Line2D
    pearl_handle = Line2D([0], [0], marker="D", color="w", markerfacecolor=C_PEARL,
                          markeredgecolor="black", markersize=5, label="Pearl variant")
    ax.legend(handles=handles[:2] + [pearl_handle],
              labels=["Pathogenic", "Benign", "Pearl variant"],
              loc="lower left", framealpha=0.9, edgecolor="#D1D5DB")

    ax.set_ylim(0.70, 1.005)
    ax.grid(axis="y", alpha=0.15, linewidth=0.3)
    fig.tight_layout()
    save_fig(fig, "fig1_ssim_violin")


# ══════════════════════════════════════════════════════════════════════
# Figure 2: ROC Curve — Categorical vs Position-Only
# ══════════════════════════════════════════════════════════════════════
def figure2_roc_curves():
    print("\n[Fig 2] ROC Curves...")
    df_cat = pd.read_csv(ATLAS_CAT)
    df_pos = pd.read_csv(ATLAS_POS)

    # Binary labels: Pathogenic=1, Benign=0
    y_true_cat = (df_cat["Label"] == "Pathogenic").astype(int)
    y_true_pos = (df_pos["Label"] == "Pathogenic").astype(int)

    # LSSIM is inverse — lower = more pathogenic, so negate for ROC
    scores_cat = -df_cat["ARCHCODE_LSSIM"]
    scores_pos = -df_pos["ARCHCODE_LSSIM"]

    fpr_cat, tpr_cat, thresh_cat = roc_curve(y_true_cat, scores_cat)
    fpr_pos, tpr_pos, thresh_pos = roc_curve(y_true_pos, scores_pos)
    auc_cat = auc(fpr_cat, tpr_cat)
    auc_pos = auc(fpr_pos, tpr_pos)

    # Youden index for categorical
    youden = tpr_cat - fpr_cat
    opt_idx = np.argmax(youden)

    fig, ax = plt.subplots(figsize=(89 * MM_TO_INCH, 89 * MM_TO_INCH))

    # ROC curves
    ax.plot(fpr_cat, tpr_cat, color=C_BEN, linewidth=1.5,
            label=f"Categorical model (AUC = {auc_cat:.3f})")
    ax.plot(fpr_pos, tpr_pos, color=C_GRAY, linewidth=1.2, linestyle="--",
            label=f"Position-only control (AUC = {auc_pos:.3f})")
    ax.plot([0, 1], [0, 1], color="#BDC3C7", linewidth=0.6, linestyle=":")

    # Youden optimal point
    ax.scatter(fpr_cat[opt_idx], tpr_cat[opt_idx], s=40, color=C_PATH,
               zorder=5, marker="o", edgecolors="black", linewidths=0.5)
    ax.annotate(
        f"Youden optimal\nSens={tpr_cat[opt_idx]:.3f}\nSpec={1-fpr_cat[opt_idx]:.3f}",
        xy=(fpr_cat[opt_idx], tpr_cat[opt_idx]),
        xytext=(fpr_cat[opt_idx] + 0.15, tpr_cat[opt_idx] - 0.15),
        fontsize=6, color=C_DARK,
        arrowprops=dict(arrowstyle="->", color=C_DARK, lw=0.6),
    )

    ax.set_xlabel("False Positive Rate (1 − Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title("Figure 2. ROC: Categorical vs Position-Only",
                 fontweight="bold", pad=8)
    ax.legend(loc="lower right", framealpha=0.9, edgecolor="#D1D5DB")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")
    ax.grid(alpha=0.15, linewidth=0.3)

    # Inset: within-category AUC bar chart
    with open(CONTROL_JSON) as f:
        ctrl = json.load(f)

    within_cats = list(ctrl["categorical"]["within_category"].keys())
    cat_aucs = [ctrl["categorical"]["within_category"][c]["auc"] for c in within_cats]
    pos_aucs = [ctrl["position_only"]["within_category"][c]["auc"] for c in within_cats]

    ax_inset = fig.add_axes([0.22, 0.35, 0.35, 0.30])
    x = np.arange(len(within_cats))
    w = 0.35
    ax_inset.bar(x - w/2, cat_aucs, w, color=C_BEN, alpha=0.8, label="Categorical")
    ax_inset.bar(x + w/2, pos_aucs, w, color=C_GRAY, alpha=0.8, label="Position-only")
    ax_inset.axhline(y=0.5, color="#BDC3C7", linewidth=0.5, linestyle=":")
    ax_inset.set_xticks(x)
    ax_inset.set_xticklabels([c.replace("_", "\n") for c in within_cats], fontsize=5)
    ax_inset.set_ylabel("Within-cat AUC", fontsize=6)
    ax_inset.set_title("Within-category AUC", fontsize=6.5, fontweight="bold")
    ax_inset.tick_params(labelsize=5)
    ax_inset.set_ylim(0, 1.0)
    ax_inset.legend(fontsize=4.5, loc="upper right")

    fig.tight_layout()
    save_fig(fig, "fig2_roc_curves")


# ══════════════════════════════════════════════════════════════════════
# Figure 3: Pearl Variant Quadrant Plot
# ══════════════════════════════════════════════════════════════════════
def figure3_pearl_quadrant():
    print("\n[Fig 3] Pearl Quadrant Plot...")
    df = pd.read_csv(ATLAS_CAT)

    VEP_THRESH = 0.30
    LSSIM_THRESH = 0.95

    fig, ax = plt.subplots(figsize=(89 * MM_TO_INCH, 89 * MM_TO_INCH))

    # Quadrant shading
    xlim = (0.70, 1.005)
    ylim = (-0.02, 1.02)
    # Q1: VEP high, LSSIM high (concordant benign) — light green
    ax.axvspan(LSSIM_THRESH, xlim[1], ymin=(VEP_THRESH - ylim[0])/(ylim[1]-ylim[0]),
               ymax=1.0, alpha=0.04, color="#27AE60")
    # Q2: VEP high, LSSIM low (VEP-only pathogenic) — light blue
    ax.axvspan(xlim[0], LSSIM_THRESH, ymin=(VEP_THRESH - ylim[0])/(ylim[1]-ylim[0]),
               ymax=1.0, alpha=0.04, color="#2980B9")
    # Q3: VEP low, LSSIM low (concordant pathogenic) — light red
    ax.axvspan(xlim[0], LSSIM_THRESH, ymin=0,
               ymax=(VEP_THRESH - ylim[0])/(ylim[1]-ylim[0]),
               alpha=0.04, color="#E74C3C")
    # Q4: VEP low, LSSIM high — PEARL ZONE — gold
    ax.axvspan(LSSIM_THRESH, xlim[1], ymin=0,
               ymax=(VEP_THRESH - ylim[0])/(ylim[1]-ylim[0]),
               alpha=0.06, color="#F39C12")

    # Threshold lines
    ax.axvline(x=LSSIM_THRESH, color=C_GRAY, linewidth=0.7, linestyle="--", alpha=0.6)
    ax.axhline(y=VEP_THRESH, color=C_GRAY, linewidth=0.7, linestyle="--", alpha=0.6)

    # Category colors
    cat_colors = {
        "nonsense": "#2563EB", "frameshift": "#7C3AED", "splice_donor": "#0891B2",
        "splice_acceptor": "#0891B2", "missense": "#6B7280", "splice_region": "#059669",
        "promoter": "#D97706", "3_prime_UTR": "#9CA3AF", "5_prime_UTR": "#9CA3AF",
        "intronic": "#D1D5DB", "synonymous": "#E5E7EB", "other": "#9CA3AF",
    }

    # Non-pearl variants
    non_pearls = df[df["Pearl"] != True]
    for cat in non_pearls["Category"].unique():
        sub = non_pearls[non_pearls["Category"] == cat]
        ax.scatter(sub["ARCHCODE_LSSIM"], sub["VEP_Score"],
                   s=12, alpha=0.5, c=cat_colors.get(cat, "#9CA3AF"),
                   edgecolors="white", linewidths=0.2, zorder=2,
                   label=cat.replace("_", " "))

    # Pearl variants — stars with red edge
    pearls = df[df["Pearl"] == True]
    if len(pearls) > 0:
        ax.scatter(pearls["ARCHCODE_LSSIM"], pearls["VEP_Score"],
                   s=50, marker="*", c=C_PEARL, edgecolors="#991B1B",
                   linewidths=0.5, zorder=10, label=f"Pearl (n={len(pearls)})")

    # Quadrant counts
    q1 = len(df[(df["VEP_Score"] >= VEP_THRESH) & (df["ARCHCODE_LSSIM"] >= LSSIM_THRESH)])
    q2 = len(df[(df["VEP_Score"] >= VEP_THRESH) & (df["ARCHCODE_LSSIM"] < LSSIM_THRESH)])
    q3 = len(df[(df["VEP_Score"] < VEP_THRESH) & (df["ARCHCODE_LSSIM"] < LSSIM_THRESH)])
    q4 = len(df[(df["VEP_Score"] < VEP_THRESH) & (df["ARCHCODE_LSSIM"] >= LSSIM_THRESH)])

    # Quadrant labels
    qfont = dict(fontsize=6.5, fontweight="bold", alpha=0.6, ha="center")
    ax.text(0.975, 0.85, f"Q1: Concordant\nbenign (n={q1})", color="#27AE60", **qfont)
    ax.text(0.825, 0.85, f"Q2: VEP-only\npathogenic (n={q2})", color="#2980B9", **qfont)
    ax.text(0.825, 0.08, f"Q3: Concordant\npathogenic (n={q3})", color="#E74C3C", **qfont)
    ax.text(0.975, 0.08, f"Q4: PEARL zone\n(n={q4})", color="#F39C12", **qfont)

    ax.set_xlabel("ARCHCODE LSSIM")
    ax.set_ylabel("VEP Score")
    ax.set_title("Figure 3. Pearl Variant Identification (HBB)",
                 fontweight="bold", pad=8)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(alpha=0.12, linewidth=0.3)

    # Compact legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper left", fontsize=5, ncol=2,
              framealpha=0.9, edgecolor="#D1D5DB", columnspacing=0.8,
              handletextpad=0.3, borderpad=0.4)

    fig.tight_layout()
    save_fig(fig, "fig3_pearl_quadrant")


# ══════════════════════════════════════════════════════════════════════
# Figure 4: Hi-C Validation Bar Chart
# ══════════════════════════════════════════════════════════════════════
def figure4_hic_validation():
    print("\n[Fig 4] Hi-C Validation...")

    # Collect Hi-C correlation data from JSON files
    hic_data = []

    # HBB 30kb
    with open(RESULTS / "hic_correlation_k562.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "HBB\n30 kb", "r": d["primary_result"]["pearson_r"],
            "n": d["primary_result"]["n_valid"], "cell": "K562",
        })

    # HBB 95kb
    with open(RESULTS / "hic_correlation_k562_95kb.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "HBB\n95 kb", "r": d["primary_result"]["pearson_r"],
            "n": d["primary_result"]["n_valid"], "cell": "K562",
        })

    # BRCA1 K562
    with open(RESULTS / "hic_correlation_brca1.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "BRCA1\nK562", "r": d["K562"]["r"],
            "n": d["K562"]["n_pairs"], "cell": "K562",
        })

    # BRCA1 MCF7
    hic_data.append({
        "locus": "BRCA1\nMCF7", "r": d["MCF7"]["r"],
        "n": d["MCF7"]["n_pairs"], "cell": "MCF7",
    })

    # MLH1
    with open(RESULTS / "hic_correlation_mlh1.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "MLH1", "r": d["pearson_r"],
            "n": d["n_valid_pairs"], "cell": "K562",
        })

    # LDLR
    with open(RESULTS / "hic_correlation_ldlr.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "LDLR", "r": d["pearson_r"],
            "n": d["n_valid_pairs"], "cell": "HepG2",
        })

    # TP53 K562
    with open(RESULTS / "hic_correlation_tp53.json") as f:
        d = json.load(f)
        hic_data.append({
            "locus": "TP53\nK562", "r": d["K562"]["r"],
            "n": d["K562"]["n_pairs"], "cell": "K562",
        })

    # TP53 MCF7
    hic_data.append({
        "locus": "TP53\nMCF7", "r": d["MCF7"]["r"],
        "n": d["MCF7"]["n_pairs"], "cell": "MCF7",
    })

    df_hic = pd.DataFrame(hic_data)
    df_hic = df_hic.sort_values("r", ascending=False).reset_index(drop=True)

    # Cell type → color mapping
    cell_colors = {"K562": "#C0392B", "MCF7": "#8E44AD", "HepG2": "#27AE60"}

    fig, ax = plt.subplots(figsize=(184 * MM_TO_INCH, 80 * MM_TO_INCH))

    bars = ax.bar(
        range(len(df_hic)), df_hic["r"],
        color=[cell_colors[c] for c in df_hic["cell"]],
        edgecolor="white", linewidth=0.5, width=0.7,
    )

    # Annotations: r value + n pairs
    for i, row in df_hic.iterrows():
        ax.text(i, row["r"] + 0.015, f"r={row['r']:.2f}",
                ha="center", va="bottom", fontsize=6.5, fontweight="bold")
        ax.text(i, row["r"] / 2, f"n={row['n']:,}",
                ha="center", va="center", fontsize=5.5, color="white",
                fontweight="bold", alpha=0.9)

    ax.set_xticks(range(len(df_hic)))
    ax.set_xticklabels(df_hic["locus"], fontsize=7)
    ax.set_ylabel("Pearson r (ARCHCODE vs Hi-C)")
    ax.set_title("Figure 4. Hi-C Validation Across Loci and Cell Types",
                 fontweight="bold", pad=8)
    ax.set_ylim(0, 0.72)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.grid(axis="y", alpha=0.15, linewidth=0.3)

    # Legend for cell types
    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=v, label=k) for k, v in cell_colors.items()]
    ax.legend(handles=legend_handles, loc="upper right", framealpha=0.9,
              edgecolor="#D1D5DB", title="Cell type", title_fontsize=7)

    # p-value note
    ax.text(0.01, 0.97, "All p < 1e-82 (Pearson)", transform=ax.transAxes,
            fontsize=6, color=C_GRAY, va="top")

    fig.tight_layout()
    save_fig(fig, "fig4_hic_validation")


# ══════════════════════════════════════════════════════════════════════
# Figure 5: Multi-Locus Summary Heatmap
# ══════════════════════════════════════════════════════════════════════
def figure5_multilocus_summary():
    print("\n[Fig 5] Multi-Locus Summary...")

    loci_info = [
        ("HBB",   "UNIFIED_ATLAS_SUMMARY_95kb.json",           "alphagenome_benchmark_95kb.json",   "hic_correlation_k562_95kb.json"),
        ("CFTR",  "UNIFIED_ATLAS_SUMMARY_CFTR_317kb.json",     "alphagenome_benchmark_cftr.json",   None),
        ("TP53",  "UNIFIED_ATLAS_SUMMARY_TP53_300kb.json",     "alphagenome_benchmark_tp53.json",   "hic_correlation_tp53.json"),
        ("BRCA1", "UNIFIED_ATLAS_SUMMARY_BRCA1_400kb.json",    "alphagenome_benchmark_brca1.json",  "hic_correlation_brca1.json"),
        ("MLH1",  "UNIFIED_ATLAS_SUMMARY_MLH1_300kb.json",     "alphagenome_benchmark_mlh1.json",   "hic_correlation_mlh1.json"),
        ("LDLR",  "UNIFIED_ATLAS_SUMMARY_LDLR_300kb.json",     "alphagenome_benchmark_ldlr.json",   "hic_correlation_ldlr.json"),
        ("SCN5A", "UNIFIED_ATLAS_SUMMARY_SCN5A_400kb.json",    "alphagenome_benchmark_scn5a.json",  None),
    ]

    rows = []
    for gene, atlas_f, ag_f, hic_f in loci_info:
        with open(RESULTS / atlas_f) as f:
            atlas = json.load(f)
        with open(RESULTS / ag_f) as f:
            ag = json.load(f)

        st = atlas["statistics"]
        n_variants = st["total_variants"]
        mean_lssim_path = st.get("mean_lssim_pathogenic", np.nan)
        mean_lssim_ben = st.get("mean_lssim_benign", np.nan)
        if mean_lssim_path is None:
            mean_lssim_path = np.nan
        if mean_lssim_ben is None:
            mean_lssim_ben = np.nan
        delta_lssim = mean_lssim_ben - mean_lssim_path if not (np.isnan(mean_lssim_path) or np.isnan(mean_lssim_ben)) else 0
        pearls = st.get("pearls", 0)

        # AG rho (Spearman, O/E — archcode_vs_alphagenome)
        ag_rho = ag["correlations"].get("archcode_vs_alphagenome", {}).get("spearman_rho", np.nan)

        # Hi-C r
        hic_r = np.nan
        if hic_f:
            with open(RESULTS / hic_f) as f:
                hic_d = json.load(f)
            if "primary_result" in hic_d:
                hic_r = hic_d["primary_result"]["pearson_r"]
            elif "K562" in hic_d:
                hic_r = hic_d["K562"]["r"]
            elif "pearson_r" in hic_d:
                hic_r = hic_d["pearson_r"]

        rows.append({
            "Gene": gene,
            "n": n_variants,
            "ΔLSSIM\n(B−P)": delta_lssim,
            "Hi-C r": hic_r,
            "AG ρ": ag_rho,
            "Pearls": pearls,
        })

    df = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(184 * MM_TO_INCH, 90 * MM_TO_INCH))
    ax.axis("off")

    # Create table
    col_labels = ["Gene", "ClinVar\nvariants", "ΔLSSIM\n(Ben−Path)", "Hi-C\nPearson r",
                  "AG\nSpearman ρ", "Pearl\nvariants"]

    delta_col = "ΔLSSIM\n(B−P)"
    cell_text = []
    cell_colors_grid = []
    for _, row in df.iterrows():
        hic_val_r = row["Hi-C r"]
        ag_val_r = row["AG ρ"]
        delta_r = row[delta_col]
        hic_val = f"{hic_val_r:.2f}" if not np.isnan(hic_val_r) else "—"
        ag_val = f"{ag_val_r:.2f}" if not np.isnan(ag_val_r) else "—"
        delta_val = f"{delta_r:.4f}" if delta_r != 0 else "—"
        n_val = row["n"]

        cell_text.append([
            row["Gene"],
            f"{n_val:,}",
            delta_val,
            hic_val,
            ag_val,
            str(row["Pearls"]),
        ])

        # Color coding for ΔLSSIM
        d = delta_r
        if d > 0.05:
            delta_c = "#FADBD8"  # strong separation → light red background
        elif d > 0.01:
            delta_c = "#FEF9E7"  # moderate
        else:
            delta_c = "#F2F3F4"  # minimal

        # Color coding for Hi-C r
        h = row["Hi-C r"]
        if np.isnan(h):
            hic_c = "#F2F3F4"
        elif h >= 0.5:
            hic_c = "#D5F5E3"
        elif h >= 0.3:
            hic_c = "#FEF9E7"
        else:
            hic_c = "#FADBD8"

        cell_colors_grid.append(["white", "white", delta_c, hic_c, "white", "white"])

    table = ax.table(
        cellText=cell_text, colLabels=col_labels,
        cellColours=cell_colors_grid,
        colColours=["#D6EAF8"] * len(col_labels),
        loc="center", cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.6)

    # Bold header
    for j in range(len(col_labels)):
        table[0, j].set_text_props(fontweight="bold")
    # Bold gene names
    for i in range(len(df)):
        table[i + 1, 0].set_text_props(fontweight="bold")
        # Highlight HBB row
        if df.iloc[i]["Gene"] == "HBB":
            for j in range(len(col_labels)):
                if cell_colors_grid[i][j] == "white":
                    table[i + 1, j].set_facecolor("#EBF5FB")
        # Gray out SCN5A (negative control)
        if df.iloc[i]["Gene"] == "SCN5A":
            for j in range(len(col_labels)):
                table[i + 1, j].set_text_props(color="#95A5A6")
                table[i + 1, j].set_facecolor("#F8F9F9")

    ax.set_title("Figure 5. Multi-Locus Summary: ARCHCODE Validation Across 7 Genomic Loci",
                 fontweight="bold", pad=15, fontsize=10)

    # Footnotes
    ax.text(0.5, -0.05,
            "Green cells: Hi-C r ≥ 0.50; Yellow: r ≥ 0.30; Red background: ΔLSSIM > 0.05.\n"
            "SCN5A = negative control (K562 cell-type mismatch). AG = AlphaGenome SDK v0.6.0.\n"
            "ΔLSSIM = mean benign LSSIM − mean pathogenic LSSIM (higher = better separation).",
            transform=ax.transAxes, fontsize=6, color=C_GRAY, ha="center", va="top")

    fig.tight_layout()
    save_fig(fig, "fig5_multilocus_summary")


# ══════════════════════════════════════════════════════════════════════
# Figure 6: Contact Map Comparison (WT vs Mutant vs Differential)
# ══════════════════════════════════════════════════════════════════════
def figure6_contact_maps():
    """
    Python reimplementation of the analytical contact formula from
    src/engines/contactMatrix.ts — generates WT, mutant, and differential
    contact maps for the HBB 30kb locus (50×50 matrix for clean visualization).
    """
    print("\n[Fig 6] Contact Maps...")

    with open(CONFIG / "hbb_30kb_v2.json") as f:
        cfg = json.load(f)

    w = cfg["window"]
    start, end, res = w["start"], w["end"], w["resolution_bp"]
    n_bins = w["n_bins"]
    bg = 0.1

    enhancers = cfg["features"]["enhancers"]
    ctcf_sites = cfg["features"]["ctcf_sites"]

    def make_contact_matrix(enhancers_list, ctcf_list, mutation_bin=None,
                            effect_strength=0.0):
        """Analytical contact matrix: C(i,j) = decay × sqrt(occ_i×occ_j) × ctcf_perm."""
        # Build occupancy landscape
        occ = np.ones(n_bins) * 0.3  # baseline occupancy
        for enh in enhancers_list:
            enh_bin = int((enh["position"] - start) / res)
            if 0 <= enh_bin < n_bins:
                spread = max(1, int(2000 / res))  # ~2kb spread
                for b in range(max(0, enh_bin - spread), min(n_bins, enh_bin + spread + 1)):
                    dist = abs(b - enh_bin)
                    occ[b] = max(occ[b], enh["occupancy"] * np.exp(-dist * 0.5))

        # Apply mutation: reduce occupancy around mutation site
        if mutation_bin is not None and 0 <= mutation_bin < n_bins:
            spread = max(1, int(1500 / res))
            for b in range(max(0, mutation_bin - spread), min(n_bins, mutation_bin + spread + 1)):
                dist = abs(b - mutation_bin)
                reduction = effect_strength * np.exp(-dist * 0.3)
                occ[b] = max(0.05, occ[b] * (1 - reduction))

        # Build CTCF barrier map
        ctcf_bins = []
        for site in ctcf_list:
            b = int((site["position"] - start) / res)
            if 0 <= b < n_bins:
                ctcf_bins.append(b)

        ctcf_perm = 0.15  # default permeability

        # Generate contact matrix
        mat = np.zeros((n_bins, n_bins))
        for i in range(n_bins):
            mat[i, i] = 1.0
            for j in range(i + 1, n_bins):
                distance = j - i
                decay = 1.0 / (distance + 1)

                # Occupancy geometric mean
                occ_factor = np.sqrt(occ[i] * occ[j])

                # CTCF barrier penalty: multiply by permeability for each
                # CTCF site between i and j
                barrier = 1.0
                for cb in ctcf_bins:
                    if i < cb < j:
                        barrier *= ctcf_perm

                contact = bg * decay * occ_factor * barrier
                mat[i, j] = contact
                mat[j, i] = contact

        # Normalize to [0, 1]
        if mat.max() > 0:
            mat = mat / mat.max()
        return mat

    # WT matrix
    mat_wt = make_contact_matrix(enhancers, ctcf_sites)

    # Mutant: nonsense at codon 39 (HBB:c.118C>T, most common β⁰)
    # Position ~5227118 → bin (5227118 - 5210000) / 600 ≈ 28
    mutation_bin = int((5227118 - start) / res)
    mat_mut = make_contact_matrix(enhancers, ctcf_sites,
                                  mutation_bin=mutation_bin, effect_strength=0.8)

    # Differential
    mat_diff = mat_wt - mat_mut

    fig, axes = plt.subplots(1, 3, figsize=(184 * MM_TO_INCH, 65 * MM_TO_INCH))

    # Genomic coordinate labels (in kb)
    extent = [start/1e3, end/1e3, end/1e3, start/1e3]

    # Panel A: WT
    im_wt = axes[0].imshow(mat_wt, cmap="Reds", vmin=0, vmax=1, extent=extent, aspect="equal")
    axes[0].set_title("A. Wild-type", fontweight="bold", fontsize=8)

    # Panel B: Mutant
    im_mut = axes[1].imshow(mat_mut, cmap="Reds", vmin=0, vmax=1, extent=extent, aspect="equal")
    axes[1].set_title("B. Cd39 (C→T) nonsense", fontweight="bold", fontsize=8)

    # Panel C: Differential
    vmax_diff = max(abs(mat_diff.min()), abs(mat_diff.max()))
    if vmax_diff == 0:
        vmax_diff = 0.01
    im_diff = axes[2].imshow(mat_diff, cmap="RdBu_r", vmin=-vmax_diff, vmax=vmax_diff,
                             extent=extent, aspect="equal")
    axes[2].set_title("C. Differential (WT − Mut)", fontweight="bold", fontsize=8)

    # Shared formatting
    for ax_i in axes:
        ax_i.set_xlabel("Position (kb)", fontsize=7)
        ax_i.set_ylabel("Position (kb)", fontsize=7)
        ax_i.tick_params(labelsize=6)
        # Mark mutation position
        mut_pos_kb = (start + mutation_bin * res) / 1e3
        ax_i.axvline(x=mut_pos_kb, color="black", linewidth=0.4, linestyle=":", alpha=0.5)
        ax_i.axhline(y=mut_pos_kb, color="black", linewidth=0.4, linestyle=":", alpha=0.5)

    # Colorbars
    fig.colorbar(im_wt, ax=axes[0], fraction=0.046, pad=0.04, label="Contact\nprobability")
    fig.colorbar(im_mut, ax=axes[1], fraction=0.046, pad=0.04, label="Contact\nprobability")
    fig.colorbar(im_diff, ax=axes[2], fraction=0.046, pad=0.04, label="ΔContact")

    fig.suptitle("Figure 6. ARCHCODE Predicted Contact Maps — HBB 30 kb (50×50, 600 bp resolution)",
                 fontweight="bold", fontsize=9, y=1.02)
    fig.tight_layout()
    save_fig(fig, "fig6_contact_maps")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("ARCHCODE Publication Figures — Generation")
    print("=" * 60)

    figure1_ssim_violin()
    figure2_roc_curves()
    figure3_pearl_quadrant()
    figure4_hic_validation()
    figure5_multilocus_summary()
    figure6_contact_maps()

    print("\n" + "=" * 60)
    generated = list(FIGURES.glob("fig*_*.p*"))
    print(f"Generated {len(generated)} files in {FIGURES}/")
    for f in sorted(generated):
        print(f"  {f.name} ({f.stat().st_size / 1024:.0f} KB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
