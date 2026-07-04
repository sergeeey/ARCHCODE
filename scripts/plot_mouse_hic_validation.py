#!/usr/bin/env python3
"""
Figure 13: Mouse Hi-C Validation of ARCHCODE WT Contact Matrix

Compares experimental G1E-ER4 Hi-C contact matrix with ARCHCODE-predicted
WT contact matrix for mouse beta-globin locus (chr7:103,788,000-103,918,000).

Panel A: Experimental Hi-C heatmap
Panel B: ARCHCODE WT prediction heatmap
Panel C: Pearson correlation by genomic distance
Panel D: Scatter plot (Hi-C vs ARCHCODE)
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy import stats

PROJECT = Path(__file__).parent.parent
HIC_JSON = PROJECT / "results" / "mouse_hic_beta_globin.json"
CROSS_JSON = PROJECT / "results" / "cross_species_hbb_comparison.json"
OUT_PDF = PROJECT / "figures" / "fig13_mouse_hic_validation.pdf"
OUT_PNG = PROJECT / "figures" / "fig13_mouse_hic_validation.png"

# Load Hi-C data
with open(HIC_JSON) as f:
    hic_data = json.load(f)

hic_matrix = np.array(hic_data["matrix"])
n = hic_matrix.shape[0]
print(f"Hi-C matrix: {n}x{n}")

# Load ARCHCODE WT mouse matrix from cross-species results
with open(CROSS_JSON) as f:
    cross_data = json.load(f)

# The cross-species comparison has mouseWT matrix
# If not available, we'll generate it
if "mouseWTMatrix" in cross_data:
    archcode_matrix = np.array(cross_data["mouseWTMatrix"])
else:
    print("WARNING: mouseWTMatrix not in cross_species results.")
    print("Run cross_species_comparison.ts first to generate it.")
    print("For now, using placeholder analysis...")
    archcode_matrix = None

# ---- Analysis ----

if archcode_matrix is not None and archcode_matrix.shape == hic_matrix.shape:
    n = hic_matrix.shape[0]

    # Distance-dependent correlation
    max_dist = n // 2
    distances = []
    correlations = []

    for d in range(1, max_dist):
        hic_diag = np.diag(hic_matrix, d)
        arch_diag = np.diag(archcode_matrix, d)
        mask = (hic_diag > 0) & (arch_diag > 0)
        if mask.sum() > 5:
            r, _ = stats.pearsonr(hic_diag[mask], arch_diag[mask])
            distances.append(d)
            correlations.append(r)

    # Overall correlation (upper triangle)
    triu_idx = np.triu_indices(n, k=1)
    hic_flat = hic_matrix[triu_idx]
    arch_flat = archcode_matrix[triu_idx]
    mask = (hic_flat > 0) & (arch_flat > 0)
    overall_r, overall_p = stats.pearsonr(hic_flat[mask], arch_flat[mask])

    print(f"Overall Pearson r = {overall_r:.3f} (p = {overall_p:.2e})")
    print(f"Distance-dependent: min r = {min(correlations):.3f}, max r = {max(correlations):.3f}")
else:
    # Generate comparison with Hi-C alone
    print("Generating Hi-C analysis (without ARCHCODE comparison)")
    overall_r = None

# ---- Figure ----

fig = plt.figure(figsize=(16, 14))

# Panel A: Hi-C heatmap
ax1 = fig.add_subplot(2, 2, 1)
im1 = ax1.imshow(np.log1p(hic_matrix), cmap="YlOrRd", aspect="equal",
                  interpolation="nearest")
ax1.set_title(f"A. Experimental Hi-C (G1E-ER4)\n{hic_data['region']}", fontsize=12)
ax1.set_xlabel("Genomic position (bins)")
ax1.set_ylabel("Genomic position (bins)")
plt.colorbar(im1, ax=ax1, label="log(contact freq + 1)", shrink=0.8)

# Mark key features
config_path = PROJECT / "config" / "locus" / "mouse_hbb_130kb.json"
with open(config_path) as f:
    cfg = json.load(f)

win_start = cfg["window"]["start"]
win_end = cfg["window"]["end"]
res = (win_end - win_start) / n

# CTCF positions as bin indices
for ctcf in cfg["features"]["ctcf_sites"]:
    bin_idx = int((ctcf["position"] - win_start) / res)
    if 0 <= bin_idx < n:
        ax1.axhline(bin_idx, color="cyan", alpha=0.3, linewidth=0.5)
        ax1.axvline(bin_idx, color="cyan", alpha=0.3, linewidth=0.5)

if archcode_matrix is not None and archcode_matrix.shape == hic_matrix.shape:
    # Panel B: ARCHCODE heatmap
    ax2 = fig.add_subplot(2, 2, 2)
    im2 = ax2.imshow(archcode_matrix, cmap="YlOrRd", aspect="equal",
                      interpolation="nearest")
    ax2.set_title("B. ARCHCODE WT Prediction (Mouse Hbb)", fontsize=12)
    ax2.set_xlabel("Genomic position (bins)")
    ax2.set_ylabel("Genomic position (bins)")
    plt.colorbar(im2, ax=ax2, label="Contact probability", shrink=0.8)

    for ctcf in cfg["features"]["ctcf_sites"]:
        bin_idx = int((ctcf["position"] - win_start) / res)
        if 0 <= bin_idx < n:
            ax2.axhline(bin_idx, color="cyan", alpha=0.3, linewidth=0.5)
            ax2.axvline(bin_idx, color="cyan", alpha=0.3, linewidth=0.5)

    # Panel C: Distance-dependent correlation
    ax3 = fig.add_subplot(2, 2, 3)
    dist_kb = [d * res / 1000 for d in distances]
    ax3.plot(dist_kb, correlations, "b-", linewidth=1.5, alpha=0.7)
    ax3.axhline(0, color="gray", linestyle="--", alpha=0.3)
    ax3.set_xlabel("Genomic distance (kb)", fontsize=11)
    ax3.set_ylabel("Pearson r", fontsize=11)
    ax3.set_title(f"C. Distance-Dependent Correlation\n(Overall r = {overall_r:.3f})", fontsize=12)
    ax3.set_ylim(-0.3, 1.0)
    ax3.grid(True, alpha=0.2)

    # Panel D: Scatter
    ax4 = fig.add_subplot(2, 2, 4)
    # Subsample for scatter (too many points)
    n_sample = min(5000, mask.sum())
    idx = np.random.choice(np.where(mask)[0], n_sample, replace=False)
    ax4.scatter(hic_flat[idx], arch_flat[idx], s=2, alpha=0.3, c="steelblue")
    ax4.set_xlabel("Hi-C contact frequency", fontsize=11)
    ax4.set_ylabel("ARCHCODE contact probability", fontsize=11)
    ax4.set_title(f"D. Hi-C vs ARCHCODE (r = {overall_r:.3f}, n = {mask.sum():,})", fontsize=12)

    # Fit line
    z = np.polyfit(hic_flat[mask], arch_flat[mask], 1)
    p_fit = np.poly1d(z)
    x_range = np.linspace(hic_flat[mask].min(), hic_flat[mask].max(), 100)
    ax4.plot(x_range, p_fit(x_range), "r--", linewidth=1.5, alpha=0.7)
else:
    # Just show Hi-C analysis
    ax2 = fig.add_subplot(2, 2, 2)
    # Contact probability vs distance (P(s) curve)
    dists = []
    probs = []
    for d in range(1, n):
        diag = np.diag(hic_matrix, d)
        if diag.size > 0:
            dists.append(d * res / 1000)
            probs.append(np.nanmean(diag))
    ax2.loglog(dists, probs, "b-", linewidth=1.5)
    ax2.set_xlabel("Genomic distance (kb)", fontsize=11)
    ax2.set_ylabel("Mean contact frequency", fontsize=11)
    ax2.set_title("B. Contact Probability P(s) Curve", fontsize=12)
    ax2.grid(True, alpha=0.2)

    # Panel C: Hi-C slice at LCR
    ax3 = fig.add_subplot(2, 2, 3)
    lcr_bin = int((103870566 - win_start) / res)  # HS3/4 strongest enhancer
    if 0 <= lcr_bin < n:
        ax3.plot(range(n), hic_matrix[lcr_bin, :], "r-", linewidth=1)
        ax3.set_xlabel("Genomic position (bins)", fontsize=11)
        ax3.set_ylabel("Contact frequency", fontsize=11)
        ax3.set_title("C. Hi-C Contacts from LCR HS3/4", fontsize=12)
        # Mark genes
        for gene in cfg["features"]["genes"]:
            gene_bin = int((gene["start"] - win_start) / res)
            if 0 <= gene_bin < n:
                ax3.axvline(gene_bin, color="green", alpha=0.5, linewidth=1, linestyle="--")
                ax3.text(gene_bin, ax3.get_ylim()[1] * 0.9, gene["name"], fontsize=7,
                        rotation=90, va="top")

    # Panel D: TAD-like structure
    ax4 = fig.add_subplot(2, 2, 4)
    # Insulation score approximation
    window = max(3, n // 20)
    insulation = np.zeros(n)
    for i in range(window, n - window):
        submat = hic_matrix[i-window:i, i:i+window]
        insulation[i] = np.nanmean(submat)
    pos_kb = np.arange(n) * res / 1000
    ax4.plot(pos_kb, insulation, "k-", linewidth=1)
    ax4.set_xlabel("Position relative to start (kb)", fontsize=11)
    ax4.set_ylabel("Insulation score (a.u.)", fontsize=11)
    ax4.set_title("D. Insulation Score Profile", fontsize=12)
    for ctcf in cfg["features"]["ctcf_sites"]:
        ctcf_kb = (ctcf["position"] - win_start) / 1000
        ax4.axvline(ctcf_kb, color="blue", alpha=0.5, linewidth=1, linestyle="--")
        ax4.text(ctcf_kb, ax4.get_ylim()[1] * 0.95, ctcf["name"], fontsize=7,
                rotation=90, va="top", color="blue")

plt.tight_layout()
fig.savefig(OUT_PDF, dpi=300, bbox_inches="tight")
fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print(f"\nSaved: {OUT_PDF}")
print(f"Saved: {OUT_PNG}")
plt.close()
