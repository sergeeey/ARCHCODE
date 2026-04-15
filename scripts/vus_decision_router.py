"""
VUS Decision Router — 2×2 VEP × ARCHCODE matrix
Rules frozen in vus_router_rules.md BEFORE this analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
import json
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

RESULTS = Path("D:/ДНК/results")
OUT = Path("D:/ДНК/results")

# Per-locus LSSIM thresholds (ADR-017, FPR <= 1%)
THRESHOLDS = {
    "HBB": 0.977,
    "TERT": 0.968,
    "TP53": 0.982,
    "MLH1": 0.972,
    "BRCA1": 0.985,
    "CFTR": 0.989,
    "PTEN": 0.989,
    "LDLR": 0.996,
}

# Atlas files per locus (primary configs only)
ATLAS_FILES = {
    "HBB": "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "TERT": "TERT_Unified_Atlas_300kb.csv",
    "PTEN": "PTEN_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
}


def load_all_variants():
    """Load all variants from Unified Atlas files."""
    frames = []
    for locus, fname in ATLAS_FILES.items():
        path = RESULTS / fname
        if not path.exists():
            print(f"  SKIP {locus}: {fname} not found")
            continue
        df = pd.read_csv(path)
        df["Locus"] = locus
        df["LSSIM_Threshold"] = THRESHOLDS.get(locus, np.nan)
        frames.append(df)
        print(f"  {locus}: {len(df)} variants loaded")
    return pd.concat(frames, ignore_index=True)


def classify_vep(row):
    """Classify VEP signal: HIGH, LOW, or NULL."""
    vep_score = row.get("VEP_Score", -1)
    vep_impact = str(row.get("VEP_Impact", "")).upper()

    if vep_score == -1 or vep_impact == "" or vep_impact == "NAN":
        return "VEP_NULL"
    if vep_impact in ("HIGH", "MODERATE") or (
        isinstance(vep_score, (int, float)) and vep_score > 0.5
    ):
        return "VEP_HIGH"
    return "VEP_LOW"


def classify_arch(row):
    """Classify ARCHCODE signal: HIGH or LOW."""
    lssim = row.get("ARCHCODE_LSSIM", 1.0)
    threshold = row.get("LSSIM_Threshold", 0.95)
    if pd.isna(lssim) or pd.isna(threshold):
        return "ARCH_LOW"
    return "ARCH_HIGH" if lssim < threshold else "ARCH_LOW"


def assign_class(vep_class, arch_class):
    """Map quadrant to taxonomy class."""
    if arch_class == "ARCH_HIGH":
        if vep_class == "VEP_HIGH":
            return "C_mixed"
        elif vep_class == "VEP_LOW":
            return "B_architecture"
        else:  # VEP_NULL
            return "D_coverage_gap"
    else:  # ARCH_LOW
        if vep_class == "VEP_HIGH":
            return "A_activity"
        else:
            return "Unclassified"


def main():
    print("=" * 60)
    print("VUS DECISION ROUTER")
    print("=" * 60)

    # Step 1: Load all variants
    print("\n[1] Loading variants from Unified Atlas files...")
    df = load_all_variants()
    print(f"\n  TOTAL: {len(df)} variants across {df['Locus'].nunique()} loci")

    # Step 2: Filter to VUS only
    vus_keywords = ["uncertain", "vus", "conflicting"]
    df["is_vus"] = (
        df["ClinVar_Significance"]
        .fillna("")
        .str.lower()
        .apply(lambda s: any(kw in s for kw in vus_keywords))
    )
    vus = df[df["is_vus"]].copy()
    print(f"\n[2] VUS variants: {len(vus)}")
    print(f"    Per locus: {vus['Locus'].value_counts().to_dict()}")

    # Also keep ALL variants for within-category control
    all_variants = df.copy()

    # Step 3: Classify
    print("\n[3] Classifying VUS through router...")
    vus["VEP_Class"] = vus.apply(classify_vep, axis=1)
    vus["ARCH_Class"] = vus.apply(classify_arch, axis=1)
    vus["Router_Class"] = vus.apply(lambda r: assign_class(r["VEP_Class"], r["ARCH_Class"]), axis=1)

    # 2×2 matrix counts
    matrix = pd.crosstab(vus["VEP_Class"], vus["ARCH_Class"], margins=True)
    print("\n  2×2 Matrix (VEP rows × ARCHCODE cols):")
    print(matrix.to_string())

    # Class distribution
    class_counts = vus["Router_Class"].value_counts()
    print("\n  Router Class distribution:")
    for cls, n in class_counts.items():
        pct = 100 * n / len(vus)
        print(f"    {cls}: {n} ({pct:.1f}%)")

    # Step 4: Metrics
    print("\n[4] Computing metrics...")

    classified = vus[vus["Router_Class"] != "Unclassified"]
    coverage = 100 * len(classified) / len(vus) if len(vus) > 0 else 0
    print(f"  Coverage: {len(classified)}/{len(vus)} = {coverage:.1f}%")

    n_class_b = len(vus[vus["Router_Class"] == "B_architecture"])
    print(f"  New interpretations (Class B — VEP blind, ARCHCODE sees): {n_class_b}")

    n_class_d = len(vus[vus["Router_Class"] == "D_coverage_gap"])
    print(f"  Coverage gap (Class D — VEP NULL, ARCHCODE sees): {n_class_d}")

    # Per-locus Class B breakdown
    if n_class_b > 0:
        class_b = vus[vus["Router_Class"] == "B_architecture"]
        print(f"\n  Class B per locus:")
        for locus, count in class_b["Locus"].value_counts().items():
            print(f"    {locus}: {count}")

        # Category distribution within Class B
        print(f"\n  Class B by VEP consequence:")
        for cat, count in class_b["Category"].value_counts().head(10).items():
            print(f"    {cat}: {count}")

    # Step 5: Within-category control (THE KILL TEST)
    print("\n[5] Within-category control (kill test)...")
    print("    Testing: within same VEP category, does LSSIM differ between")
    print("    Class B VUS vs non-Class-B VUS?")

    # Classify ALL variants (not just VUS) for control
    all_variants["VEP_Class"] = all_variants.apply(classify_vep, axis=1)
    all_variants["ARCH_Class"] = all_variants.apply(classify_arch, axis=1)
    all_variants["Router_Class"] = all_variants.apply(
        lambda r: assign_class(r["VEP_Class"], r["ARCH_Class"]), axis=1
    )

    # Within VEP_LOW variants: compare Class B vs non-Class-B
    vep_low_all = all_variants[all_variants["VEP_Class"] == "VEP_LOW"].copy()
    print(f"\n    Total VEP_LOW variants (all ClinSig): {len(vep_low_all)}")

    # Group by Category and test
    categories_tested = 0
    categories_significant = 0
    category_results = []

    for cat in vep_low_all["Category"].dropna().unique():
        cat_df = vep_low_all[vep_low_all["Category"] == cat]
        class_b_lssim = cat_df[cat_df["ARCH_Class"] == "ARCH_HIGH"]["ARCHCODE_LSSIM"].dropna()
        non_b_lssim = cat_df[cat_df["ARCH_Class"] == "ARCH_LOW"]["ARCHCODE_LSSIM"].dropna()

        if len(class_b_lssim) >= 3 and len(non_b_lssim) >= 3:
            u_stat, p_val = stats.mannwhitneyu(class_b_lssim, non_b_lssim, alternative="less")
            categories_tested += 1
            sig = p_val < 0.05
            if sig:
                categories_significant += 1
            category_results.append(
                {
                    "category": cat,
                    "n_arch_high": len(class_b_lssim),
                    "n_arch_low": len(non_b_lssim),
                    "median_high": float(class_b_lssim.median()),
                    "median_low": float(non_b_lssim.median()),
                    "U": float(u_stat),
                    "p": float(p_val),
                    "significant": bool(sig),
                }
            )
            status = "***SIG***" if sig else "ns"
            print(
                f"    {cat}: n={len(class_b_lssim)}vs{len(non_b_lssim)}, "
                f"median={class_b_lssim.median():.4f} vs {non_b_lssim.median():.4f}, "
                f"p={p_val:.2e} {status}"
            )

    print(f"\n    Within-category tests: {categories_significant}/{categories_tested} significant")

    # IMPORTANT: This is tautological! ARCH_HIGH is defined as LSSIM < threshold,
    # so of course ARCH_HIGH has lower LSSIM. The REAL test is:
    # Among VUS with VEP_LOW, do Class B VUS have lower LSSIM than NON-VUS with same category?
    print("\n[5b] NON-TAUTOLOGICAL control:")
    print("     Among VEP_LOW variants of same category,")
    print("     do VUS have different LSSIM than known benign?")

    vep_low_vus = vus[vus["VEP_Class"] == "VEP_LOW"].copy()
    vep_low_benign = all_variants[
        (all_variants["VEP_Class"] == "VEP_LOW") & (all_variants["Label"] == "Benign")
    ].copy()

    real_results = []
    for cat in vep_low_vus["Category"].dropna().unique():
        vus_lssim = vep_low_vus[vep_low_vus["Category"] == cat]["ARCHCODE_LSSIM"].dropna()
        ben_lssim = vep_low_benign[vep_low_benign["Category"] == cat]["ARCHCODE_LSSIM"].dropna()

        if len(vus_lssim) >= 3 and len(ben_lssim) >= 3:
            u_stat, p_val = stats.mannwhitneyu(vus_lssim, ben_lssim, alternative="two-sided")
            sig = p_val < 0.05
            real_results.append(
                {
                    "category": cat,
                    "n_vus": len(vus_lssim),
                    "n_benign": len(ben_lssim),
                    "median_vus": float(vus_lssim.median()),
                    "median_benign": float(ben_lssim.median()),
                    "U": float(u_stat),
                    "p": float(p_val),
                    "significant": bool(sig),
                }
            )
            status = "***SIG***" if sig else "ns"
            print(
                f"    {cat}: VUS(n={len(vus_lssim)}, med={vus_lssim.median():.4f}) vs "
                f"Benign(n={len(ben_lssim)}, med={ben_lssim.median():.4f}), "
                f"p={p_val:.2e} {status}"
            )

    real_sig = sum(1 for r in real_results if r["significant"])
    print(f"\n    Non-tautological tests: {real_sig}/{len(real_results)} significant")

    # Step 6: Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)

    if n_class_b < 5:
        print("  FAIL: Class B has < 5 VUS. Router adds nothing.")
        verdict = "FAIL_EMPTY"
    elif real_sig == 0 and len(real_results) > 0:
        print("  FAIL: No within-category significance.")
        print("  Router = category proxy, not structural tool.")
        verdict = "FAIL_CATEGORY_PROXY"
    elif real_sig > 0:
        print(f"  PASS: {real_sig}/{len(real_results)} within-category tests significant.")
        print("  Router provides structural discrimination beyond category.")
        verdict = "PASS"
    else:
        print("  INCONCLUSIVE: Not enough data for within-category tests.")
        verdict = "INCONCLUSIVE"

    # Step 7: Save results
    results = {
        "date": "2026-04-15",
        "total_variants": len(df),
        "total_vus": len(vus),
        "coverage_pct": round(coverage, 1),
        "class_counts": {k: int(v) for k, v in class_counts.items()},
        "n_class_b": n_class_b,
        "n_class_d": n_class_d,
        "within_category_results": category_results,
        "non_tautological_results": real_results,
        "verdict": verdict,
    }
    out_json = OUT / "vus_router_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to {out_json}")

    # Step 8: Figure
    print("\n[8] Generating figure...")
    make_figure(vus, results)
    print("  Done.")

    return results


def make_figure(vus, results):
    """Generate 2×2 heatmap figure."""
    # Count per quadrant
    quadrant_data = {
        ("VEP_HIGH", "ARCH_HIGH"): 0,
        ("VEP_HIGH", "ARCH_LOW"): 0,
        ("VEP_LOW", "ARCH_HIGH"): 0,
        ("VEP_LOW", "ARCH_LOW"): 0,
        ("VEP_NULL", "ARCH_HIGH"): 0,
        ("VEP_NULL", "ARCH_LOW"): 0,
    }
    for _, row in vus.iterrows():
        key = (row["VEP_Class"], row["ARCH_Class"])
        if key in quadrant_data:
            quadrant_data[key] += 1

    # Build 3×2 matrix (VEP_HIGH, VEP_LOW, VEP_NULL) × (ARCH_HIGH, ARCH_LOW)
    matrix = np.array(
        [
            [quadrant_data[("VEP_HIGH", "ARCH_HIGH")], quadrant_data[("VEP_HIGH", "ARCH_LOW")]],
            [quadrant_data[("VEP_LOW", "ARCH_HIGH")], quadrant_data[("VEP_LOW", "ARCH_LOW")]],
            [quadrant_data[("VEP_NULL", "ARCH_HIGH")], quadrant_data[("VEP_NULL", "ARCH_LOW")]],
        ]
    )

    class_labels = np.array(
        [
            ["C: Mixed\n(both detect)", "A: Activity\n(VEP only)"],
            ["B: Architecture\n(BLIND SPOT)", "Unclassified\n(no signal)"],
            ["D: Coverage gap\n(VEP can't score)", "Unclassified\n(no signal)"],
        ]
    )

    colors = np.array(
        [
            ["#FFD700", "#90EE90"],  # C=gold, A=green
            ["#FF6B6B", "#E0E0E0"],  # B=red (blind spot!), Unclassified=gray
            ["#FFA500", "#E0E0E0"],  # D=orange, Unclassified=gray
        ]
    )

    fig, ax = plt.subplots(1, 1, figsize=(10, 7))

    for i in range(3):
        for j in range(2):
            rect = mpatches.FancyBboxPatch(
                (j, 2 - i),
                1,
                1,
                boxstyle="round,pad=0.02",
                facecolor=colors[i][j],
                edgecolor="black",
                linewidth=1.5,
            )
            ax.add_patch(rect)
            # Number
            ax.text(
                j + 0.5,
                2 - i + 0.65,
                str(matrix[i][j]),
                ha="center",
                va="center",
                fontsize=28,
                fontweight="bold",
            )
            # Class label
            ax.text(j + 0.5, 2 - i + 0.3, class_labels[i][j], ha="center", va="center", fontsize=10)

    ax.set_xlim(0, 2)
    ax.set_ylim(0, 3)
    ax.set_xticks([0.5, 1.5])
    ax.set_xticklabels(["ARCHCODE\nStructural Signal", "ARCHCODE\nNo Signal"], fontsize=12)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(
        ["VEP NULL\n(can't score)", "VEP LOW\n(MODIFIER)", "VEP HIGH\n(impact)"], fontsize=12
    )
    ax.set_title(
        f"VUS Decision Router — {results['total_vus']} variants across {len(ATLAS_FILES)} loci",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )

    # Add verdict
    verdict_text = f"Coverage: {results['coverage_pct']:.0f}%  |  Class B (blind spot): {results['n_class_b']}  |  Verdict: {results['verdict']}"
    ax.text(
        1.0,
        -0.15,
        verdict_text,
        ha="center",
        va="center",
        fontsize=10,
        style="italic",
        transform=ax.transAxes,
    )

    ax.set_aspect("equal")
    plt.tight_layout()

    fig.savefig(OUT / "fig_vus_router.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / "fig_vus_router.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig_vus_router.png/pdf")


if __name__ == "__main__":
    main()
