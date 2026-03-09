"""
ARCHCODE HDAC Inhibitor Sweep — Publication Figure
===================================================
3-panel figure:
  A) 2D heatmap for HBB (enhancer boost × CTCF retention → ΔSSIM)
  B) Bar chart: enhancer-only vs CTCF-only vs combined effect, all 9 loci
  C) Pharmacological landscape: BET vs HDAC-i comparison across loci

Usage: python scripts/plot_hdac_sweep.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import os

# ── Load data ─────────────────────────────────────────────────

hdac_df = pd.read_csv("analysis/hdac_sweep_multilocus.csv")
with open("analysis/hdac_sweep_multilocus_summary.json") as f:
    hdac_summary = json.load(f)

bet_path = "analysis/bet_sweep_multilocus.csv"
bet_df = pd.read_csv(bet_path) if os.path.exists(bet_path) else None

# ── Figure setup ──────────────────────────────────────────────

fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.30)

# ── Panel A: 2D Heatmap for HBB ──────────────────────────────

ax_a = fig.add_subplot(gs[0, 0])

hbb = hdac_df[hdac_df["Locus"] == "HBB"]
boosts = sorted(hbb["Enhancer_Boost"].unique())
retentions = sorted(hbb["CTCF_Retention"].unique(), reverse=True)

heatmap_data = np.zeros((len(retentions), len(boosts)))
for i, ret in enumerate(retentions):
    for j, bst in enumerate(boosts):
        row = hbb[(hbb["Enhancer_Boost"] == bst) & (hbb["CTCF_Retention"] == ret)]
        if len(row) > 0:
            heatmap_data[i, j] = row["Delta_SSIM"].values[0]

im = ax_a.imshow(
    heatmap_data,
    cmap="RdYlBu_r",
    aspect="auto",
    vmin=heatmap_data.min() * 0.95,
    vmax=heatmap_data.max() * 1.05,
)
ax_a.set_xticks(range(len(boosts)))
ax_a.set_xticklabels([f"{b}×" for b in boosts])
ax_a.set_yticks(range(len(retentions)))
ax_a.set_yticklabels([f"{int(r * 100)}%" for r in retentions])
ax_a.set_xlabel("Enhancer Boost (H3K27ac↑)", fontsize=11)
ax_a.set_ylabel("CTCF Retention", fontsize=11)
ax_a.set_title("A. HBB: HDAC-i 2D Parameter Space", fontsize=12, fontweight="bold")

# Annotate cells
for i in range(len(retentions)):
    for j in range(len(boosts)):
        val = heatmap_data[i, j]
        color = "white" if val > (heatmap_data.max() + heatmap_data.min()) / 2 else "black"
        ax_a.text(j, i, f"{val:.4f}", ha="center", va="center", fontsize=8, color=color)

cb = plt.colorbar(im, ax=ax_a, shrink=0.8)
cb.set_label("ΔSSIM (structural disruption)", fontsize=9)

# Mark baseline
ax_a.plot(
    0,
    0,
    "s",
    markersize=14,
    markeredgecolor="lime",
    markerfacecolor="none",
    markeredgewidth=2,
    label="Baseline",
)
ax_a.legend(loc="lower right", fontsize=8)

# ── Panel B: Decomposition bar chart ─────────────────────────

ax_b = fig.add_subplot(gs[0, 1])

loci_order = ["HBB", "TERT", "MLH1", "LDLR", "TP53", "BRCA1", "CFTR", "SCN5A", "GJB2"]
per_locus = hdac_summary["per_locus"]

enh_changes = []
ctcf_changes = []
combined_changes = []
colors_tissue = []

tissue_colors = {"matched": "#2196F3", "partial": "#FF9800", "mismatch": "#9E9E9E"}

for locus in loci_order:
    data = per_locus[locus]
    enh_changes.append(data["enhancer_only_change_pct"])
    ctcf_changes.append(data["ctcf_only_change_pct"])
    combined_changes.append(data["combined_max_change_pct"])
    colors_tissue.append(tissue_colors[data["tissue_match"]])

x = np.arange(len(loci_order))
width = 0.25

bars1 = ax_b.bar(
    x - width, enh_changes, width, label="Enhancer 2× only", color="#E53935", alpha=0.8
)
bars2 = ax_b.bar(x, ctcf_changes, width, label="CTCF 25% only", color="#1E88E5", alpha=0.8)
bars3 = ax_b.bar(
    x + width, combined_changes, width, label="Combined max", color="#7B1FA2", alpha=0.8
)

ax_b.axhline(y=0, color="black", linewidth=0.5, linestyle="-")
ax_b.set_xticks(x)
ax_b.set_xticklabels(loci_order, rotation=45, ha="right", fontsize=9)
ax_b.set_ylabel("Change in ΔSSIM (%)", fontsize=11)
ax_b.set_title("B. HDAC-i Effect Decomposition", fontsize=12, fontweight="bold")
ax_b.legend(fontsize=8, loc="lower left")

# Add tissue match color strip
for i, c in enumerate(colors_tissue):
    ax_b.plot(i, ax_b.get_ylim()[1] * 0.95, "s", color=c, markersize=8)

# ── Panel C: BET vs HDAC-i pharmacological landscape ─────────

ax_c = fig.add_subplot(gs[1, :])

if bet_df is not None:
    bet_loss = {}
    for locus in loci_order:
        locus_bet = bet_df[bet_df["Locus"] == locus]
        base = locus_bet[locus_bet["BET_Inhibition_Pct"] == 0]["Delta_SSIM"].values
        full = locus_bet[locus_bet["BET_Inhibition_Pct"] == 100]["Delta_SSIM"].values
        if len(base) > 0 and len(full) > 0 and base[0] > 0:
            bet_loss[locus] = -round((1 - full[0] / base[0]) * 100)
        else:
            bet_loss[locus] = 0

    x = np.arange(len(loci_order))
    width = 0.35

    bet_vals = [bet_loss.get(l, 0) for l in loci_order]
    hdac_vals = [per_locus[l]["combined_max_change_pct"] for l in loci_order]

    bars_bet = ax_c.bar(
        x - width / 2,
        bet_vals,
        width,
        label="BET inhibitor (100%)",
        color="#FF5722",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.5,
    )
    bars_hdac = ax_c.bar(
        x + width / 2,
        hdac_vals,
        width,
        label="HDAC inhibitor (max)",
        color="#4CAF50",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.5,
    )

    ax_c.axhline(y=0, color="black", linewidth=1, linestyle="-")
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(loci_order, fontsize=11)
    ax_c.set_ylabel("Change in Structural Discrimination (%)", fontsize=11)
    ax_c.set_title(
        "C. Pharmacological Landscape: BET vs HDAC Inhibitors", fontsize=12, fontweight="bold"
    )
    ax_c.legend(fontsize=10, loc="upper right")

    # Annotations
    for i, locus in enumerate(loci_order):
        tm = per_locus[locus]["tissue_match"]
        ax_c.annotate(
            tm,
            (i, min(bet_vals[i], hdac_vals[i]) - 5),
            ha="center",
            fontsize=7,
            fontstyle="italic",
            color="gray",
        )

    # Key insight box
    ax_c.text(
        0.02,
        0.05,
        "HBB: only locus where HDAC-i enhances discrimination (+5%)\n"
        "BET universally suppresses; HDAC-i suppresses most loci\n"
        "Dominant axis: enhancer boost (not CTCF weakening)",
        transform=ax_c.transAxes,
        fontsize=8,
        verticalalignment="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8),
    )

plt.suptitle(
    "ARCHCODE: HDAC Inhibitor Structural Perturbation Across Nine Loci",
    fontsize=14,
    fontweight="bold",
    y=0.98,
)

# ── Save ──────────────────────────────────────────────────────

os.makedirs("figures", exist_ok=True)
plt.savefig("figures/fig_hdac_sweep.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figures/fig_hdac_sweep.png", bbox_inches="tight", dpi=200)
plt.close()
print("Saved: figures/fig_hdac_sweep.pdf + .png")
