"""
gnomAD Constraint × Taxonomy Class Analysis

Correlates gene constraint (LOEUF, pLI) with Class B enrichment
across 9 ARCHCODE loci.

Data source: gnomAD v4 GraphQL API (fetched 2026-03-09) [VERIFIED]
"""

import json
import numpy as np
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# gnomAD v4 constraint data — fetched via API [VERIFIED]
constraint_data = {
    "HBB": {"pLI": 7.42e-10, "LOEUF": 1.964, "oe_lof": 1.800, "oe_mis_upper": 0.963},
    "BRCA1": {"pLI": 1.55e-34, "LOEUF": 0.885, "oe_lof": 0.766, "oe_mis_upper": 0.898},
    "TP53": {"pLI": 0.998, "LOEUF": 0.449, "oe_lof": 0.277, "oe_mis_upper": 0.933},
    "TERT": {"pLI": 0.002, "LOEUF": 0.593, "oe_lof": 0.457, "oe_mis_upper": 0.817},
    "MLH1": {"pLI": 0.001, "LOEUF": 0.639, "oe_lof": 0.480, "oe_mis_upper": 0.952},
    "CFTR": {"pLI": 2.38e-39, "LOEUF": 1.152, "oe_lof": 0.988, "oe_mis_upper": 1.125},
    "SCN5A": {"pLI": 1.000, "LOEUF": 0.372, "oe_lof": 0.295, "oe_mis_upper": 0.773},
    "GJB2": {"pLI": 3.60e-15, "LOEUF": 1.965, "oe_lof": 1.780, "oe_mis_upper": 1.026},
    "LDLR": {"pLI": 1.25e-30, "LOEUF": 1.091, "oe_lof": 0.921, "oe_mis_upper": 1.000},
}

# Taxonomy data from taxonomy_auto_assignment_summary.json
taxonomy_data = {
    "HBB": {"Q2b": 25, "Q2a": 0, "Q2_total": 25, "tissue_match": 1.0, "class_B": 25},
    "BRCA1": {"Q2b": 26, "Q2a": 53, "Q2_total": 79, "tissue_match": 0.5, "class_B": 26},
    "TP53": {"Q2b": 2, "Q2a": 2, "Q2_total": 4, "tissue_match": 0.5, "class_B": 2},
    "TERT": {"Q2b": 1, "Q2a": 34, "Q2_total": 35, "tissue_match": 0.5, "class_B": 1},
    "MLH1": {"Q2b": 0, "Q2a": 72, "Q2_total": 72, "tissue_match": 0.0, "class_B": 0},
    "CFTR": {"Q2b": 0, "Q2a": 36, "Q2_total": 36, "tissue_match": 0.0, "class_B": 0},
    "SCN5A": {"Q2b": 0, "Q2a": 0, "Q2_total": 0, "tissue_match": 0.0, "class_B": 0},
    "GJB2": {"Q2b": 0, "Q2a": 0, "Q2_total": 0, "tissue_match": 0.0, "class_B": 0},
    "LDLR": {"Q2b": 0, "Q2a": 10, "Q2_total": 10, "tissue_match": 0.0, "class_B": 0},
}

# Total variants per locus (from cross_locus_atlas_comparison.json)
total_variants = {
    "HBB": 1103,
    "BRCA1": 7219,
    "TP53": 1978,
    "TERT": 2089,
    "MLH1": 2580,
    "CFTR": 2594,
    "SCN5A": 2202,
    "GJB2": 379,
    "LDLR": 2345,
}

genes = list(constraint_data.keys())

# Build arrays
loeuf = np.array([constraint_data[g]["LOEUF"] for g in genes])
pli = np.array([constraint_data[g]["pLI"] for g in genes])
q2b = np.array([taxonomy_data[g]["Q2b"] for g in genes])
q2_total = np.array([taxonomy_data[g]["Q2_total"] for g in genes])
tissue = np.array([taxonomy_data[g]["tissue_match"] for g in genes])
class_b = np.array([taxonomy_data[g]["class_B"] for g in genes])
n_total = np.array([total_variants[g] for g in genes])
class_b_rate = class_b / n_total  # Class B fraction

# Print summary table
print("=" * 90)
print(
    f"{'Gene':<8} {'LOEUF':>7} {'pLI':>8} {'Q2b':>5} {'Q2tot':>6} {'B_rate':>8} {'Tissue':>7} {'Constraint':>12}"
)
print("-" * 90)
for g in genes:
    loeuf_cat = "UNCONSTRAINED" if constraint_data[g]["LOEUF"] > 0.6 else "CONSTRAINED"
    print(
        f"{g:<8} {constraint_data[g]['LOEUF']:>7.3f} {constraint_data[g]['pLI']:>8.3f} "
        f"{taxonomy_data[g]['Q2b']:>5d} {taxonomy_data[g]['Q2_total']:>6d} "
        f"{class_b[genes.index(g)] / n_total[genes.index(g)]:>8.4f} "
        f"{taxonomy_data[g]['tissue_match']:>7.1f} {loeuf_cat:>12}"
    )

# Correlations
print("\n" + "=" * 60)
print("CORRELATIONS")
print("=" * 60)

# 1. LOEUF vs Q2b count
r_loeuf_q2b, p_loeuf_q2b = stats.spearmanr(loeuf, q2b)
print(f"\nLOEUF vs Q2b count:    Spearman rho = {r_loeuf_q2b:.3f}, p = {p_loeuf_q2b:.4f}")

# 2. LOEUF vs Class B rate
r_loeuf_brate, p_loeuf_brate = stats.spearmanr(loeuf, class_b_rate)
print(f"LOEUF vs Class B rate: Spearman rho = {r_loeuf_brate:.3f}, p = {p_loeuf_brate:.4f}")

# 3. pLI vs Q2b
r_pli_q2b, p_pli_q2b = stats.spearmanr(pli, q2b)
print(f"pLI vs Q2b count:      Spearman rho = {r_pli_q2b:.3f}, p = {p_pli_q2b:.4f}")

# 4. Tissue match vs Q2b (for reference)
r_tissue_q2b, p_tissue_q2b = stats.spearmanr(tissue, q2b)
print(f"Tissue match vs Q2b:   Spearman rho = {r_tissue_q2b:.3f}, p = {p_tissue_q2b:.4f}")

# 5. LOEUF vs Q2b, controlling for tissue (partial correlation proxy)
# Split by tissue match
matched = [g for g in genes if taxonomy_data[g]["tissue_match"] >= 0.5]
unmatched = [g for g in genes if taxonomy_data[g]["tissue_match"] < 0.5]
print(f"\nMatched loci (tissue >= 0.5): {matched}")
print(f"Unmatched loci (tissue = 0): {unmatched}")

if len(matched) >= 3:
    loeuf_m = [constraint_data[g]["LOEUF"] for g in matched]
    q2b_m = [taxonomy_data[g]["Q2b"] for g in matched]
    r_m, p_m = stats.spearmanr(loeuf_m, q2b_m)
    print(f"LOEUF vs Q2b (matched only, N={len(matched)}): rho = {r_m:.3f}, p = {p_m:.4f}")

# Key insight
print("\n" + "=" * 60)
print("KEY INSIGHT")
print("=" * 60)
constrained = [g for g in genes if constraint_data[g]["LOEUF"] <= 0.6]
unconstrained = [g for g in genes if constraint_data[g]["LOEUF"] > 0.6]
q2b_constrained = sum(taxonomy_data[g]["Q2b"] for g in constrained)
q2b_unconstrained = sum(taxonomy_data[g]["Q2b"] for g in unconstrained)
print(f"\nConstrained genes (LOEUF ≤ 0.6): {constrained}")
print(f"  Total Q2b: {q2b_constrained}")
print(f"\nUnconstrained genes (LOEUF > 0.6): {unconstrained}")
print(f"  Total Q2b: {q2b_unconstrained}")

# Confound check
print(f"\nCONFOUND CHECK:")
print(
    f"Constrained genes tissue match:   {[taxonomy_data[g]['tissue_match'] for g in constrained]}"
)
print(
    f"Unconstrained genes tissue match: {[taxonomy_data[g]['tissue_match'] for g in unconstrained]}"
)

# Figure
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Panel A: LOEUF vs Q2b
ax = axes[0]
colors = ["#e74c3c" if taxonomy_data[g]["tissue_match"] >= 0.5 else "#95a5a6" for g in genes]
ax.scatter(loeuf, q2b, c=colors, s=100, zorder=5, edgecolors="black", linewidths=0.5)
for i, g in enumerate(genes):
    offset = (0.05, 1) if g != "BRCA1" else (0.05, -3)
    ax.annotate(
        g, (loeuf[i], q2b[i]), textcoords="offset points", xytext=offset, fontsize=8, ha="left"
    )
ax.set_xlabel("LOEUF (gnomAD v4)", fontsize=11)
ax.set_ylabel("Q2b variants (Class B)", fontsize=11)
ax.set_title(
    f"Gene Constraint vs Architecture-Driven Variants\n"
    f"Spearman ρ = {r_loeuf_q2b:.3f}, p = {p_loeuf_q2b:.3f}",
    fontsize=11,
)
ax.axhline(y=0, color="gray", linestyle="--", alpha=0.3)

# Legend
from matplotlib.lines import Line2D

legend_elements = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="#e74c3c",
        markersize=10,
        label="Tissue-matched (≥0.5)",
    ),
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="#95a5a6",
        markersize=10,
        label="Tissue-mismatched (0.0)",
    ),
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

# Panel B: Constraint category barplot
ax = axes[1]
categories = ["Constrained\n(LOEUF ≤ 0.6)", "Unconstrained\n(LOEUF > 0.6)"]
q2b_vals = [q2b_constrained, q2b_unconstrained]
bar_colors = ["#3498db", "#e67e22"]
bars = ax.bar(categories, q2b_vals, color=bar_colors, edgecolor="black", linewidth=0.5)
ax.set_ylabel("Total Q2b variants (Class B)", fontsize=11)
ax.set_title("Class B Variants by Gene Constraint Category", fontsize=11)
for bar, val in zip(bars, q2b_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        str(val),
        ha="center",
        fontsize=12,
        fontweight="bold",
    )

# Annotation
n_c = len(constrained)
n_u = len(unconstrained)
ax.text(
    0.5, 0.85, f"N = {n_c} genes", transform=ax.transAxes, ha="center", fontsize=9, color="#3498db"
)
ax.text(
    0.5,
    0.78,
    f"vs N = {n_u} genes",
    transform=ax.transAxes,
    ha="center",
    fontsize=9,
    color="#e67e22",
)

plt.tight_layout()
plt.savefig("figures/taxonomy/fig_gnomad_constraint.pdf", dpi=300, bbox_inches="tight")
plt.savefig("figures/taxonomy/fig_gnomad_constraint.png", dpi=150, bbox_inches="tight")
print(f"\nFigure saved: figures/taxonomy/fig_gnomad_constraint.pdf/png")

# Save summary JSON
summary = {
    "analysis": "gnomAD_constraint_vs_taxonomy_class",
    "date": "2026-03-09",
    "source": "gnomAD v4 GraphQL API [VERIFIED]",
    "n_genes": 9,
    "correlations": {
        "LOEUF_vs_Q2b": {"spearman_rho": round(r_loeuf_q2b, 3), "p": round(p_loeuf_q2b, 4)},
        "LOEUF_vs_ClassB_rate": {
            "spearman_rho": round(r_loeuf_brate, 3),
            "p": round(p_loeuf_brate, 4),
        },
        "pLI_vs_Q2b": {"spearman_rho": round(r_pli_q2b, 3), "p": round(p_pli_q2b, 4)},
        "tissue_vs_Q2b": {"spearman_rho": round(r_tissue_q2b, 3), "p": round(p_tissue_q2b, 4)},
    },
    "constraint_by_gene": {
        g: {
            "LOEUF": constraint_data[g]["LOEUF"],
            "pLI": constraint_data[g]["pLI"],
            "Q2b": taxonomy_data[g]["Q2b"],
            "class_B_rate": round(taxonomy_data[g]["class_B"] / total_variants[g], 5),
            "tissue_match": taxonomy_data[g]["tissue_match"],
            "constraint_category": "constrained"
            if constraint_data[g]["LOEUF"] <= 0.6
            else "unconstrained",
        }
        for g in genes
    },
    "summary": {
        "constrained_genes": constrained,
        "constrained_Q2b_total": q2b_constrained,
        "unconstrained_genes": unconstrained,
        "unconstrained_Q2b_total": q2b_unconstrained,
    },
    "interpretation": "placeholder",
}

with open("analysis/gnomad_constraint_taxonomy.json", "w") as f:
    json.dump(summary, f, indent=2)
print("Summary saved: analysis/gnomad_constraint_taxonomy.json")
