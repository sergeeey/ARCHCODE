"""
Generate taxonomy figures for the Mechanistic Taxonomy paper.

Figures:
  1. Taxonomy map (2D schematic)
  2. ARCHCODE examples by class (5-panel)
  3. Tool-to-mechanism comparison matrix (heatmap)

Usage:
  python scripts/plot_taxonomy_figures.py

Output:
  figures/taxonomy/fig_taxonomy_map.pdf
  figures/taxonomy/fig_archcode_examples.pdf
  figures/taxonomy/fig_tool_matrix.pdf
"""

import json
import pathlib

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
OUTDIR = ROOT / "figures" / "taxonomy"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Publication style
plt.rcParams.update(
    {
        "font.size": 9,
        "font.family": "sans-serif",
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.1,
    }
)

# Color palette for classes
CLASS_COLORS = {
    "A": "#4393C3",  # blue — activity
    "B": "#E66101",  # orange — architecture
    "C": "#7B3294",  # purple — mixed
    "D": "#999999",  # gray — coverage gap
    "E": "#D73027",  # red — tissue mismatch
}


def figure1_taxonomy_map():
    """Figure 1: Mechanistic taxonomy map as a 2D schematic."""
    fig, ax = plt.subplots(1, 1, figsize=(7, 6))

    # Axes
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel("Sequence / Activity Signal →", fontsize=11, fontweight="bold")
    ax.set_ylabel("Architecture / Contact Signal →", fontsize=11, fontweight="bold")
    ax.set_title(
        "Mechanistic Taxonomy of Regulatory Pathogenicity", fontsize=12, fontweight="bold", pad=15
    )

    # Class zones as rectangles
    zones = {
        "A": {
            "xy": (0.55, 0.0),
            "w": 0.55,
            "h": 0.45,
            "label": "Class A\nActivity-Driven",
            "sublabel": "MPRA+, VEP+\nARCHCODE−",
        },
        "B": {
            "xy": (0.0, 0.55),
            "w": 0.5,
            "h": 0.55,
            "label": "Class B\nArchitecture-Driven",
            "sublabel": "ARCHCODE+, VEP−\nMPRA− (plasmid blind)",
        },
        "C": {
            "xy": (0.55, 0.55),
            "w": 0.55,
            "h": 0.55,
            "label": "Class C\nMixed",
            "sublabel": "Both axes +\nDual-readout needed",
        },
        "D": {
            "xy": (0.0, 0.0),
            "w": 0.5,
            "h": 0.45,
            "label": "Class D\nCoverage Gap",
            "sublabel": "VEP = no score\nARCHCODE partial",
        },
    }

    for cls, z in zones.items():
        rect = mpatches.FancyBboxPatch(
            z["xy"],
            z["w"],
            z["h"],
            boxstyle="round,pad=0.02",
            facecolor=CLASS_COLORS[cls],
            alpha=0.2,
            edgecolor=CLASS_COLORS[cls],
            linewidth=2,
        )
        ax.add_patch(rect)
        cx = z["xy"][0] + z["w"] / 2
        cy = z["xy"][1] + z["h"] / 2
        ax.text(
            cx,
            cy + 0.07,
            z["label"],
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=CLASS_COLORS[cls],
        )
        ax.text(
            cx,
            cy - 0.08,
            z["sublabel"],
            ha="center",
            va="center",
            fontsize=7.5,
            color="#333333",
            style="italic",
        )

    # Class E overlay (tissue mismatch) as hatched zone over B
    e_rect = mpatches.FancyBboxPatch(
        (0.02, 0.57),
        0.46,
        0.2,
        boxstyle="round,pad=0.01",
        facecolor="none",
        edgecolor=CLASS_COLORS["E"],
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(e_rect)
    ax.text(
        0.25,
        0.67,
        "Class E: Tissue-Mismatch\nArtifact Zone",
        ha="center",
        va="center",
        fontsize=7.5,
        color=CLASS_COLORS["E"],
        fontweight="bold",
        style="italic",
    )

    # Example annotations
    examples = [
        {"x": 0.15, "y": 0.85, "text": "HBB Q2b\n(25 var)", "cls": "B"},
        {"x": 0.82, "y": 0.2, "text": "HBB Q3\n(75 var)", "cls": "A"},
        {"x": 0.75, "y": 0.75, "text": "HBB Q1\n(270 var)", "cls": "C"},
        {"x": 0.2, "y": 0.2, "text": "TERT Q2a\n(34 var)", "cls": "D"},
        {"x": 0.35, "y": 0.62, "text": "SCN5A/GJB2", "cls": "E"},
    ]
    for ex in examples:
        ax.plot(
            ex["x"],
            ex["y"],
            "o",
            color=CLASS_COLORS[ex["cls"]],
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=0.5,
            zorder=5,
        )
        ax.annotate(
            ex["text"],
            (ex["x"], ex["y"]),
            textcoords="offset points",
            xytext=(12, -5),
            fontsize=7,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8, edgecolor="#ccc"),
        )

    # Divider lines
    ax.axhline(0.5, color="#aaa", linewidth=0.5, linestyle=":")
    ax.axvline(0.5, color="#aaa", linewidth=0.5, linestyle=":")

    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xticklabels(["Absent", "Partial", "Strong"])
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["Absent", "Partial", "Strong"])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out = OUTDIR / "fig_taxonomy_map.pdf"
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  Saved: {out}")


def figure2_archcode_examples():
    """Figure 2: ARCHCODE examples by class (5-panel)."""
    # Load data
    q2b = pd.read_csv(ANALYSIS / "Q2b_true_blindspots.csv")
    matrix = pd.read_csv(ANALYSIS / "discordance_2x2_matrix.csv")

    with open(ANALYSIS / "TERT_validation_summary.json") as f:
        tert = json.load(f)
    with open(ANALYSIS / "tissue_mismatch_controls_summary.json") as f:
        mismatch = json.load(f)
    with open(ANALYSIS / "ablation_study_summary.json") as f:
        ablation = json.load(f)

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    fig.suptitle(
        "ARCHCODE Evidence for Each Mechanistic Class", fontsize=13, fontweight="bold", y=0.98
    )

    # --- Panel A: Activity-Driven (Q3 bar) ---
    ax = axes[0, 0]
    quadrants = matrix["Quadrant"].tolist()
    counts = matrix["N_Total"].astype(int).tolist()
    colors = ["#7B3294", "#E66101", "#4393C3", "#999999"]  # Q1=C, Q2=B, Q3=A, Q4=D
    ax.bar(quadrants, counts, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_ylabel("N variants")
    ax.set_title("A. Discordance Quadrants", fontweight="bold", color=CLASS_COLORS["A"])
    ax.set_yscale("log")
    for i, (q, c) in enumerate(zip(quadrants, counts)):
        ax.text(i, c * 1.2, str(c), ha="center", va="bottom", fontsize=8, fontweight="bold")
    # Highlight Q3
    ax.annotate(
        "Class A\n(Activity)",
        xy=(2, counts[2]),
        xytext=(2.5, counts[2] * 0.3),
        fontsize=7,
        fontweight="bold",
        color=CLASS_COLORS["A"],
        arrowprops=dict(arrowstyle="->", color=CLASS_COLORS["A"]),
    )

    # --- Panel B: Architecture-Driven (Q2b enhancer proximity) ---
    ax = axes[0, 1]
    q2b_hbb = q2b[q2b["Locus"] == "HBB"]
    ax.hist(
        q2b_hbb["Enhancer_Dist_bp"],
        bins=15,
        color=CLASS_COLORS["B"],
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
    )
    ax.axvline(434, color="red", linestyle="--", linewidth=1.2, label="Mean = 434 bp")
    ax.set_xlabel("Enhancer distance (bp)")
    ax.set_ylabel("N variants")
    ax.set_title("B. Architecture-Driven (HBB Q2b)", fontweight="bold", color=CLASS_COLORS["B"])
    ax.legend(fontsize=7)
    ax.text(
        0.95,
        0.9,
        f"n = {len(q2b_hbb)}\np = 2.51e-31",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="#ccc"),
    )

    # --- Panel C: Mixed (Q1 scatter concept) ---
    ax = axes[0, 2]
    q1_n = int(matrix.loc[matrix["Quadrant"] == "Q1", "N_Total"].values[0])
    q2_n = int(matrix.loc[matrix["Quadrant"] == "Q2", "N_Total"].values[0])
    q3_n = int(matrix.loc[matrix["Quadrant"] == "Q3", "N_Total"].values[0])
    q4_n = int(matrix.loc[matrix["Quadrant"] == "Q4", "N_Total"].values[0])

    # Conceptual scatter of quadrants
    sizes = np.array([q1_n, q2_n, q3_n, q4_n])
    sizes_scaled = np.sqrt(sizes) * 3
    x_pos = [0.3, 0.3, 0.7, 0.7]  # VEP low, low, high, high
    y_pos = [0.7, 0.7, 0.3, 0.3]  # ARCH low, low, high, high
    # Actually: Q1=VEP+/ARCH+, Q2=VEP-/ARCH+, Q3=VEP+/ARCH-, Q4=VEP-/ARCH-
    x_pos = [0.75, 0.25, 0.75, 0.25]
    y_pos = [0.75, 0.75, 0.25, 0.25]
    q_colors = [CLASS_COLORS["C"], CLASS_COLORS["B"], CLASS_COLORS["A"], CLASS_COLORS["D"]]
    q_labels = [f"Q1\n{q1_n}", f"Q2\n{q2_n}", f"Q3\n{q3_n}", f"Q4\n{q4_n}"]
    ax.scatter(
        x_pos,
        y_pos,
        s=sizes_scaled,
        c=q_colors,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
        zorder=5,
    )
    for x, y, lbl in zip(x_pos, y_pos, q_labels):
        ax.text(x, y - 0.12, lbl, ha="center", va="top", fontsize=8, fontweight="bold")
    ax.set_xlabel("VEP Score →")
    ax.set_ylabel("ARCHCODE Disruption →")
    ax.set_title("C. Quadrant Map (class overlay)", fontweight="bold", color=CLASS_COLORS["C"])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axhline(0.5, color="#aaa", linewidth=0.5, linestyle=":")
    ax.axvline(0.5, color="#aaa", linewidth=0.5, linestyle=":")

    # --- Panel D: Coverage Gap (TERT ablation) ---
    ax = axes[1, 0]
    # Find TERT in ablation
    tert_ablation = None
    for loc_data in ablation["per_locus"]:
        if loc_data["locus"] == "TERT":
            tert_ablation = loc_data
            break
    if tert_ablation:
        models = ["M1\nNearest-gene", "M2\nEpigenome", "M3\nEpi+3D", "M4\nARCHCODE"]
        aucs = [
            tert_ablation["auc_m1_nearest_gene"],
            tert_ablation["auc_m2_epigenome_only"],
            tert_ablation["auc_m3_epigenome_3d"],
            tert_ablation["auc_m4_archcode"],
        ]
        bar_colors = [CLASS_COLORS["D"]] * 3 + [CLASS_COLORS["B"]]
        ax.bar(models, aucs, color=bar_colors, edgecolor="black", linewidth=0.5)
        ax.axhline(0.5, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_ylabel("AUC")
        ax.set_ylim(0.3, 1.0)
        for i, v in enumerate(aucs):
            ax.text(
                i, v + 0.02, f"{v:.3f}", ha="center", va="bottom", fontsize=8, fontweight="bold"
            )
    ax.set_title("D. Coverage Gap (TERT ablation)", fontweight="bold", color=CLASS_COLORS["D"])
    ax.text(
        0.95,
        0.05,
        f"Q2a: {tert.get('n_q2', 'N/A')}\nQ2b: 1",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="#ccc"),
    )

    # --- Panel E: Tissue-Mismatch (heatmap) ---
    ax = axes[1, 1]
    loci_order = ["HBB", "LDLR", "TP53"]
    mat = np.zeros((3, 3))
    for i, lv in enumerate(loci_order):
        for j, le in enumerate(loci_order):
            key = f"{lv}|{le}"
            if key in mismatch["proxy_results"]:
                mat[i, j] = mismatch["proxy_results"][key]["delta"]
    sns.heatmap(
        mat,
        ax=ax,
        annot=True,
        fmt=".4f",
        cmap="RdYlGn",
        xticklabels=loci_order,
        yticklabels=loci_order,
        center=0,
        linewidths=0.5,
        cbar_kws={"shrink": 0.7, "label": "Δ proxy"},
    )
    ax.set_xlabel("Enhancer config")
    ax.set_ylabel("Variant locus")
    ax.set_title("E. Tissue-Mismatch (EXP-003)", fontweight="bold", color=CLASS_COLORS["E"])

    # --- Panel F: Legend / Summary ---
    ax = axes[1, 2]
    ax.axis("off")
    legend_text = (
        "Summary of Mechanistic Classes\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "A  Activity-Driven   (VEP+, ARCHCODE−)\n"
        "B  Architecture-Driven (VEP−, ARCHCODE+)\n"
        "C  Mixed             (both +)\n"
        "D  Coverage Gap      (VEP = no score)\n"
        "E  Tissue Mismatch   (signal collapse)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Total variants: 30,318\n"
        f"Q2b (Class B): 54\n"
        f"Q2a (Class D): 207\n"
        f"Loci: 9 (3 tissue-matched)"
    )
    ax.text(
        0.1,
        0.95,
        legend_text,
        transform=ax.transAxes,
        fontsize=9,
        va="top",
        ha="left",
        family="monospace",
        bbox=dict(facecolor="#f9f9f9", edgecolor="#ccc", boxstyle="round,pad=0.5"),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    out = OUTDIR / "fig_archcode_examples.pdf"
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  Saved: {out}")


def figure3_tool_matrix():
    """Figure 3: Tool-to-mechanism comparison matrix (heatmap)."""
    # Define the matrix
    tools = [
        "VEP",
        "CADD",
        "Seq models\n(Enformer/Sei)",
        "MPRA /\nSTARR-seq",
        "CRISPRi/a",
        "ARCHCODE",
        "Hi-C /\nCapture-C",
        "Conservation\n(PhyloP)",
    ]
    classes = [
        "A: Activity",
        "B: Architecture",
        "C: Mixed",
        "D: Coverage\nGap",
        "E: Tissue\nMismatch",
    ]

    # Score: 3=gold standard, 2=good, 1=partial, 0=blind, -1=artifact, nan=N/A
    data = np.array(
        [
            [1, 0, 1, 0, np.nan],  # VEP
            [3, 0, 1, 1, np.nan],  # CADD
            [3, 0, 1, 1, 0.5],  # Seq models
            [3, 0, 1, 0, 0.5],  # MPRA
            [2, 1, 2, 0, 0.5],  # CRISPRi
            [0, 3, 1, 2, -1],  # ARCHCODE
            [0, 3, 2, 0, 0.5],  # Hi-C
            [2, 1, 2, 1, np.nan],  # Conservation
        ]
    )

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    # Custom colormap: red(0) -> yellow(1) -> light green(2) -> dark green(3)
    from matplotlib.colors import LinearSegmentedColormap

    colors_list = ["#D73027", "#FDAE61", "#A6D96A", "#1A9850"]
    cmap = LinearSegmentedColormap.from_list("tool_matrix", colors_list, N=256)

    # Mask NaN
    masked = np.ma.masked_invalid(data)

    im = ax.imshow(masked, cmap=cmap, vmin=-1, vmax=3, aspect="auto")

    # Annotations
    labels_map = {
        3: "+++",
        2: "++",
        1: "+",
        0: "BLIND",
        -1: "ARTIFACT",
        0.5: "cell\ndep.",
    }
    for i in range(len(tools)):
        for j in range(len(classes)):
            val = data[i, j]
            if np.isnan(val):
                txt = "N/A"
                color = "#999"
            elif val == -1:
                txt = "ARTIFACT"
                color = "white"
            elif val == 0:
                txt = "BLIND"
                color = "white"
            elif val == 0.5:
                txt = "cell\ndep."
                color = "black"
            else:
                txt = labels_map.get(val, str(val))
                color = "black" if val >= 1.5 else "black"
            ax.text(
                j,
                i,
                txt,
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold" if val in [0, -1, 3] else "normal",
                color=color,
            )

    # Highlight ARCHCODE row
    ax.add_patch(
        mpatches.Rectangle(
            (-0.5, 5 - 0.5),
            len(classes),
            1,
            fill=False,
            edgecolor=CLASS_COLORS["B"],
            linewidth=2.5,
            linestyle="-",
        )
    )

    # Highlight Architecture column
    ax.add_patch(
        mpatches.Rectangle(
            (1 - 0.5, -0.5),
            1,
            len(tools),
            fill=False,
            edgecolor=CLASS_COLORS["B"],
            linewidth=2,
            linestyle="--",
        )
    )

    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(tools)))
    ax.set_yticklabels(tools, fontsize=9)

    ax.set_title("Tool-to-Mechanism Coverage Matrix", fontsize=12, fontweight="bold", pad=10)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_ticks([-1, 0, 1, 2, 3])
    cbar.set_ticklabels(["Artifact", "Blind", "Partial", "Good", "Gold\nStandard"])
    cbar.ax.tick_params(labelsize=8)

    # Annotation boxes
    ax.text(
        1,
        len(tools) + 0.3,
        "← Systematic blind spot for\n    sequence-based tools",
        fontsize=7.5,
        color=CLASS_COLORS["B"],
        fontweight="bold",
        ha="center",
    )

    fig.tight_layout()
    out = OUTDIR / "fig_tool_matrix.pdf"
    fig.savefig(out)
    fig.savefig(out.with_suffix(".png"))
    plt.close(fig)
    print(f"  Saved: {out}")


if __name__ == "__main__":
    print("Generating taxonomy figures...")
    print()
    print("Figure 1: Taxonomy Map")
    figure1_taxonomy_map()
    print()
    print("Figure 2: ARCHCODE Examples by Class")
    figure2_archcode_examples()
    print()
    print("Figure 3: Tool-Mechanism Matrix")
    figure3_tool_matrix()
    print()
    print("Done! All figures saved to figures/taxonomy/")
