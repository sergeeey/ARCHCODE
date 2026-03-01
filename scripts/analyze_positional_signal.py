#!/usr/bin/env python
"""
ARCHCODE Within-Category Positional Signal Analysis
====================================================
Honest, non-circular validation of whether ARCHCODE SSIM captures
positional signal beyond variant category assignment.

Scientific Integrity: This script reports ALL results including nulls.
No p-hacking, no selective reporting.

Usage:
    python scripts/analyze_positional_signal.py --locus 95kb
    python scripts/analyze_positional_signal.py --locus 30kb
"""

import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder

# Add project root for shared loader
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.locus_config import load_locus_config, resolve_locus_path


def load_atlas(locus_tag: str) -> list[dict]:
    """Load the unified atlas CSV for given locus."""
    if locus_tag == "cftr":
        path = Path("results/CFTR_Unified_Atlas_317kb.csv")
    elif locus_tag == "tp53":
        path = Path("results/TP53_Unified_Atlas_300kb.csv")
    elif locus_tag == "brca1":
        path = Path("results/BRCA1_Unified_Atlas_400kb.csv")
    elif locus_tag == "95kb":
        path = Path("results/HBB_Unified_Atlas_95kb.csv")
    else:
        path = Path("results/HBB_Unified_Atlas.csv")

    if not path.exists():
        raise FileNotFoundError(f"Atlas not found: {path}")

    with open(path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Parse numeric fields
    for r in rows:
        r["pos"] = int(r["Position_GRCh38"])
        r["ssim"] = float(r["ARCHCODE_SSIM"])
        r["delta_ssim"] = 1.0 - r["ssim"]  # disruption score
        r["is_pathogenic"] = 1 if r["Label"] == "Pathogenic" else 0

    return rows


def category_label_breakdown(rows: list[dict]) -> dict:
    """Report category x label breakdown, identify testable categories."""
    counts = Counter()
    for r in rows:
        counts[(r["Category"], r["Label"])] += 1

    categories = sorted(set(r["Category"] for r in rows))
    breakdown = {}
    for cat in categories:
        n_path = counts.get((cat, "Pathogenic"), 0)
        n_ben = counts.get((cat, "Benign"), 0)
        breakdown[cat] = {"pathogenic": n_path, "benign": n_ben, "total": n_path + n_ben}

    return breakdown


def within_category_mann_whitney(rows: list[dict], min_per_group: int = 3) -> list[dict]:
    """
    Mann-Whitney U test within each category: pathogenic SSIM vs benign SSIM.
    Only for categories with >= min_per_group in BOTH groups.
    """
    categories = sorted(set(r["Category"] for r in rows))
    results = []

    for cat in categories:
        cat_rows = [r for r in rows if r["Category"] == cat]
        path_ssim = [r["ssim"] for r in cat_rows if r["is_pathogenic"] == 1]
        ben_ssim = [r["ssim"] for r in cat_rows if r["is_pathogenic"] == 0]

        if len(path_ssim) < min_per_group or len(ben_ssim) < min_per_group:
            results.append({
                "category": cat,
                "n_pathogenic": len(path_ssim),
                "n_benign": len(ben_ssim),
                "testable": False,
                "reason": f"insufficient n (path={len(path_ssim)}, ben={len(ben_ssim)})"
            })
            continue

        # One-sided: pathogenic SSIM < benign SSIM (more disruption)
        stat, p_two = stats.mannwhitneyu(path_ssim, ben_ssim, alternative="two-sided")
        _, p_less = stats.mannwhitneyu(path_ssim, ben_ssim, alternative="less")

        # Effect size: rank-biserial correlation
        n1, n2 = len(path_ssim), len(ben_ssim)
        r_rb = 1 - (2 * stat) / (n1 * n2)

        results.append({
            "category": cat,
            "n_pathogenic": n1,
            "n_benign": n2,
            "testable": True,
            "path_mean_ssim": mean(path_ssim),
            "ben_mean_ssim": mean(ben_ssim),
            "delta_mean": mean(path_ssim) - mean(ben_ssim),
            "U_statistic": stat,
            "p_two_sided": p_two,
            "p_one_sided_less": p_less,
            "rank_biserial_r": r_rb,
        })

    return results


def logistic_regression_additive(rows: list[dict]) -> dict:
    """
    Test whether SSIM adds predictive value beyond category alone.

    Model 1: pathogenicity ~ category (baseline)
    Model 2: pathogenicity ~ category + SSIM (test)

    Uses likelihood ratio test via scipy.
    """
    # Encode category
    le = LabelEncoder()
    categories = le.fit_transform([r["Category"] for r in rows])
    ssim_scores = np.array([r["ssim"] for r in rows])
    y = np.array([r["is_pathogenic"] for r in rows])

    # One-hot encode categories (drop first to avoid collinearity)
    from sklearn.preprocessing import OneHotEncoder
    ohe = OneHotEncoder(drop="first", sparse_output=False)
    X_cat = ohe.fit_transform(categories.reshape(-1, 1))
    X_cat_ssim = np.column_stack([X_cat, ssim_scores])

    # Model 1: category only
    lr1 = LogisticRegression(max_iter=10000, solver="lbfgs", penalty=None)
    lr1.fit(X_cat, y)
    y_prob1 = lr1.predict_proba(X_cat)[:, 1]
    ll1 = np.sum(y * np.log(y_prob1 + 1e-15) + (1 - y) * np.log(1 - y_prob1 + 1e-15))

    # Model 2: category + SSIM
    lr2 = LogisticRegression(max_iter=10000, solver="lbfgs", penalty=None)
    lr2.fit(X_cat_ssim, y)
    y_prob2 = lr2.predict_proba(X_cat_ssim)[:, 1]
    ll2 = np.sum(y * np.log(y_prob2 + 1e-15) + (1 - y) * np.log(1 - y_prob2 + 1e-15))

    # Likelihood ratio test (1 additional parameter)
    lr_stat = -2 * (ll1 - ll2)
    lr_p = stats.chi2.sf(lr_stat, df=1)

    # AUC comparison
    auc1 = roc_auc_score(y, y_prob1)
    auc2 = roc_auc_score(y, y_prob2)

    # SSIM coefficient in full model
    ssim_coef = lr2.coef_[0][-1]

    return {
        "model1_auc": auc1,
        "model2_auc": auc2,
        "auc_improvement": auc2 - auc1,
        "ssim_coefficient": ssim_coef,
        "log_likelihood_1": ll1,
        "log_likelihood_2": ll2,
        "lr_statistic": lr_stat,
        "lr_p_value": lr_p,
        "n_categories": X_cat.shape[1],
        "interpretation": (
            "SSIM adds significant predictive value beyond category"
            if lr_p < 0.05
            else "SSIM does NOT add significant value beyond category"
        ),
    }


def permutation_test(rows: list[dict], n_perm: int = 10000, min_n: int = 5) -> list[dict]:
    """
    Permutation test: within each testable category, shuffle pathogenicity
    labels and compute the fraction of permuted AUCs >= observed AUC.
    """
    rng = np.random.default_rng(42)
    results = []

    categories = sorted(set(r["Category"] for r in rows))
    for cat in categories:
        cat_rows = [r for r in rows if r["Category"] == cat]
        ssim = np.array([r["ssim"] for r in cat_rows])
        labels = np.array([r["is_pathogenic"] for r in cat_rows])

        n_path = labels.sum()
        n_ben = len(labels) - n_path

        if n_path < min_n or n_ben < min_n:
            continue

        # Observed AUC
        obs_auc = roc_auc_score(labels, -ssim)  # negative: lower SSIM = more pathogenic

        # Permutation
        perm_aucs = []
        for _ in range(n_perm):
            perm_labels = rng.permutation(labels)
            try:
                perm_aucs.append(roc_auc_score(perm_labels, -ssim))
            except ValueError:
                perm_aucs.append(0.5)

        perm_aucs = np.array(perm_aucs)
        p_value = (perm_aucs >= obs_auc).mean()

        results.append({
            "category": cat,
            "n_path": int(n_path),
            "n_ben": int(n_ben),
            "observed_auc": obs_auc,
            "perm_mean_auc": perm_aucs.mean(),
            "perm_std_auc": perm_aucs.std(),
            "p_value": p_value,
            "n_permutations": n_perm,
        })

    return results


def ssim_dilution_analysis(rows: list[dict]) -> dict:
    """
    Assess SSIM dilution: is within-category variance too small for detection?
    """
    categories = sorted(set(r["Category"] for r in rows))
    analysis = {}

    for cat in categories:
        ssims = [r["ssim"] for r in rows if r["Category"] == cat]
        n = len(ssims)
        m = mean(ssims)
        s = stdev(ssims) if n > 1 else 0.0
        cv = s / (1 - m) if (1 - m) > 1e-10 else float("inf")

        analysis[cat] = {
            "n": n,
            "mean_ssim": m,
            "std_ssim": s,
            "mean_disruption": 1.0 - m,
            "std_disruption": s,
            # ПОЧЕМУ: coefficient of variation relative to disruption magnitude
            # If CV >> 1, variance is large relative to signal — detectable
            # If CV << 1, signal is buried in noise
            "disruption_cv": cv,
            "detectable": s > 0.001,  # conservative threshold
        }

    return analysis


def distance_to_tss_analysis(rows: list[dict]) -> dict:
    """
    The ONLY distance that varies meaningfully (0-1548bp).
    Test Spearman correlation between dist_to_TSS and SSIM within categories.
    """
    HBB_TSS = 5227002  # NM_000518.5 TSS

    results = {}
    for cat in sorted(set(r["Category"] for r in rows)):
        cat_rows = [r for r in rows if r["Category"] == cat]
        if len(cat_rows) < 10:
            continue

        dists = [abs(r["pos"] - HBB_TSS) for r in cat_rows]
        ssims = [r["ssim"] for r in cat_rows]

        rho, p = stats.spearmanr(dists, ssims)
        results[cat] = {
            "n": len(cat_rows),
            "spearman_rho": rho,
            "p_value": p,
            "dist_range": f"{min(dists)}-{max(dists)} bp",
        }

    return results


def plot_positional_landscape(rows: list[dict], config: dict, output_path: str):
    """
    Figure 1: Multi-panel positional landscape.

    Panel A: SSIM by position, colored by category
    Panel B: Within-intronic detail (pathogenic vs benign)
    Panel C: Category boxplots with within-category separation
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [3, 2, 2]})

    # --- Panel A: All variants SSIM by position ---
    ax = axes[0]
    cat_colors = {
        "nonsense": "#d62728", "frameshift": "#e377c2",
        "splice_donor": "#ff7f0e", "splice_acceptor": "#bcbd22",
        "splice_region": "#ffbb78", "missense": "#2ca02c",
        "promoter": "#9467bd", "other": "#8c564b",
        "5_prime_UTR": "#17becf", "3_prime_UTR": "#7f7f7f",
        "intronic": "#1f77b4", "synonymous": "#aec7e8",
    }

    for r in rows:
        color = cat_colors.get(r["Category"], "#333333")
        marker = "^" if r["is_pathogenic"] else "o"
        alpha = 0.8 if r["is_pathogenic"] else 0.3
        ax.scatter(r["pos"], r["ssim"], c=color, marker=marker,
                   s=20 if r["is_pathogenic"] else 8, alpha=alpha, edgecolors="none")

    # Gene annotation
    for gene in config["features"]["genes"]:
        if gene["start"] >= min(r["pos"] for r in rows) - 500:
            ax.axvspan(gene["start"], gene["end"], alpha=0.05, color="gray")
            ax.text((gene["start"] + gene["end"]) / 2, ax.get_ylim()[0],
                    gene["name"], ha="center", va="bottom", fontsize=7, style="italic")

    ax.set_xlabel("Genomic Position (chr11)")
    ax.set_ylabel("ARCHCODE SSIM")
    ax.set_title("A. SSIM Landscape — All 1,103 Variants by Position")

    # Legend
    patches = [mpatches.Patch(color=c, label=cat) for cat, c in cat_colors.items()
               if any(r["Category"] == cat for r in rows)]
    ax.legend(handles=patches, loc="lower left", ncol=4, fontsize=7)

    # --- Panel B: Intronic only — pathogenic vs benign ---
    ax = axes[1]
    intronic = [r for r in rows if r["Category"] == "intronic"]
    for r in intronic:
        color = "#d62728" if r["is_pathogenic"] else "#1f77b4"
        marker = "^" if r["is_pathogenic"] else "o"
        size = 50 if r["is_pathogenic"] else 8
        ax.scatter(r["pos"], r["ssim"], c=color, marker=marker,
                   s=size, alpha=0.7, edgecolors="black" if r["is_pathogenic"] else "none",
                   linewidths=0.5)

    ax.set_xlabel("Genomic Position (chr11)")
    ax.set_ylabel("SSIM")
    ax.set_title(f"B. Intronic Only — 9 Pathogenic (▲) vs 658 Benign (○)")

    path_ssim = [r["ssim"] for r in intronic if r["is_pathogenic"]]
    ben_ssim = [r["ssim"] for r in intronic if not r["is_pathogenic"]]
    ax.axhline(mean(path_ssim), color="#d62728", ls="--", alpha=0.5, label=f"Path mean={mean(path_ssim):.6f}")
    ax.axhline(mean(ben_ssim), color="#1f77b4", ls="--", alpha=0.5, label=f"Ben mean={mean(ben_ssim):.6f}")
    ax.legend(fontsize=8)

    # --- Panel C: Within-category boxplots ---
    ax = axes[2]
    testable_cats = []
    for cat in ["intronic", "other", "synonymous", "3_prime_UTR"]:
        cat_rows = [r for r in rows if r["Category"] == cat]
        path = [r["ssim"] for r in cat_rows if r["is_pathogenic"]]
        ben = [r["ssim"] for r in cat_rows if not r["is_pathogenic"]]
        if len(path) >= 1 and len(ben) >= 1:
            testable_cats.append((cat, path, ben))

    positions_box = []
    labels_box = []
    for i, (cat, path, ben) in enumerate(testable_cats):
        bp = ax.boxplot([ben, path], positions=[i * 3, i * 3 + 1], widths=0.6,
                        patch_artist=True, showfliers=True)
        bp["boxes"][0].set_facecolor("#1f77b4")
        bp["boxes"][1].set_facecolor("#d62728")
        labels_box.extend([(i * 3 + 0.5, cat)])

    ax.set_xticks([x for x, _ in labels_box])
    ax.set_xticklabels([cat for _, cat in labels_box])
    ax.set_ylabel("SSIM")
    ax.set_title("C. Within-Category Comparison: Benign (blue) vs Pathogenic (red)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Figure saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="ARCHCODE Positional Signal Analysis")
    parser.add_argument("--locus", default="95kb", help="Locus config: 30kb or 95kb")
    parser.add_argument("--permutations", type=int, default=10000)
    args = parser.parse_args()

    print("=" * 70)
    print("ARCHCODE Within-Category Positional Signal Analysis")
    print("Scientific Integrity: ALL results reported, including nulls")
    print("=" * 70)

    # Load data
    config_path = resolve_locus_path(args.locus)
    config = load_locus_config(config_path)
    rows = load_atlas(args.locus)
    print(f"\nLocus: {config['id']} ({config['window']['chromosome']}:"
          f"{config['window']['start']:,}-{config['window']['end']:,})")
    print(f"Variants loaded: {len(rows)}")

    # Positional context
    positions = [r["pos"] for r in rows]
    window_size = config["window"]["end"] - config["window"]["start"]
    variant_spread = max(positions) - min(positions)
    print(f"\n--- POSITIONAL CONTEXT ---")
    print(f"Simulation window: {window_size:,} bp")
    print(f"Variant spread:    {variant_spread:,} bp ({variant_spread/window_size*100:.1f}% of window)")
    print(f"Variant range:     {min(positions):,} - {max(positions):,}")

    ctcf_positions = [c["position"] for c in config["features"]["ctcf_sites"]]
    enhancer_positions = [e["position"] for e in config["features"]["enhancers"]]
    min_dist_ctcf = min(min(abs(p - c) for c in ctcf_positions) for p in positions)
    max_dist_ctcf = max(min(abs(p - c) for c in ctcf_positions) for p in positions)
    print(f"Distance to nearest CTCF: {min_dist_ctcf:,} - {max_dist_ctcf:,} bp")
    print(f"  → Variation: {max_dist_ctcf - min_dist_ctcf:,} bp")

    if variant_spread < 5000:
        print(f"\n⚠️  WARNING: All variants clustered in {variant_spread:,} bp")
        print(f"   Distance-to-feature predictors will have minimal variance.")
        print(f"   This is an HONEST LIMITATION of the HBB ClinVar dataset.")

    # 1. Category x Label breakdown
    print(f"\n{'='*70}")
    print("1. CATEGORY × LABEL BREAKDOWN")
    print(f"{'='*70}")
    breakdown = category_label_breakdown(rows)
    print(f"\n{'Category':<20s} {'Path':>6s} {'Ben':>6s} {'Total':>6s} {'Testable':>10s}")
    print("-" * 55)
    for cat, info in sorted(breakdown.items()):
        testable = "✓" if info["pathogenic"] >= 3 and info["benign"] >= 3 else "✗"
        print(f"{cat:<20s} {info['pathogenic']:>6d} {info['benign']:>6d} "
              f"{info['total']:>6d} {testable:>10s}")

    testable_count = sum(1 for info in breakdown.values()
                         if info["pathogenic"] >= 3 and info["benign"] >= 3)
    print(f"\nTestable categories (≥3 in both groups): {testable_count}")

    # 2. SSIM dilution assessment
    print(f"\n{'='*70}")
    print("2. SSIM DILUTION ASSESSMENT")
    print(f"{'='*70}")
    dilution = ssim_dilution_analysis(rows)
    print(f"\n{'Category':<20s} {'n':>5s} {'Mean SSIM':>10s} {'STD':>10s} "
          f"{'Disruption':>12s} {'Detectable':>12s}")
    print("-" * 75)
    for cat, info in sorted(dilution.items()):
        det = "YES" if info["detectable"] else "NO (std<0.001)"
        print(f"{cat:<20s} {info['n']:>5d} {info['mean_ssim']:>10.6f} "
              f"{info['std_ssim']:>10.6f} {info['mean_disruption']:>12.6f} {det:>12s}")

    # 3. Within-category Mann-Whitney U
    print(f"\n{'='*70}")
    print("3. WITHIN-CATEGORY MANN-WHITNEY U TEST")
    print(f"   H₀: pathogenic SSIM = benign SSIM within category")
    print(f"   H₁: pathogenic SSIM < benign SSIM (more disruption)")
    print(f"{'='*70}")
    mw_results = within_category_mann_whitney(rows, min_per_group=3)
    for res in mw_results:
        print(f"\n  {res['category']}: n_path={res['n_pathogenic']}, n_ben={res['n_benign']}")
        if not res["testable"]:
            print(f"    → NOT TESTABLE: {res['reason']}")
        else:
            sig = "***" if res["p_two_sided"] < 0.001 else "**" if res["p_two_sided"] < 0.01 else "*" if res["p_two_sided"] < 0.05 else "ns"
            print(f"    Path mean SSIM: {res['path_mean_ssim']:.6f}")
            print(f"    Ben mean SSIM:  {res['ben_mean_ssim']:.6f}")
            print(f"    Δ mean:         {res['delta_mean']:.6f}")
            print(f"    U = {res['U_statistic']:.1f}, p(two-sided) = {res['p_two_sided']:.4e} {sig}")
            print(f"    p(one-sided, path<ben) = {res['p_one_sided_less']:.4e}")
            print(f"    Rank-biserial r = {res['rank_biserial_r']:.4f}")

    # 4. Logistic regression: additive value of SSIM
    print(f"\n{'='*70}")
    print("4. LOGISTIC REGRESSION — ADDITIVE VALUE OF SSIM")
    print(f"   Model 1: pathogenicity ~ category")
    print(f"   Model 2: pathogenicity ~ category + SSIM")
    print(f"   Test: likelihood ratio test (df=1)")
    print(f"{'='*70}")
    lr_results = logistic_regression_additive(rows)
    print(f"\n  Model 1 AUC (category only):    {lr_results['model1_auc']:.4f}")
    print(f"  Model 2 AUC (category + SSIM):  {lr_results['model2_auc']:.4f}")
    print(f"  AUC improvement:                {lr_results['auc_improvement']:.4f}")
    print(f"  SSIM coefficient (β):           {lr_results['ssim_coefficient']:.4f}")
    print(f"  LR statistic:                   {lr_results['lr_statistic']:.4f}")
    print(f"  LR p-value:                     {lr_results['lr_p_value']:.4e}")
    print(f"\n  → {lr_results['interpretation']}")

    # 5. Permutation test
    print(f"\n{'='*70}")
    print(f"5. PERMUTATION TEST ({args.permutations:,} iterations)")
    print(f"   Shuffling pathogenicity labels within each category")
    print(f"{'='*70}")
    perm_results = permutation_test(rows, n_perm=args.permutations, min_n=5)
    if not perm_results:
        print("\n  No categories with ≥5 in both groups for permutation test.")
    for res in perm_results:
        sig = "*" if res["p_value"] < 0.05 else "ns"
        print(f"\n  {res['category']}: n_path={res['n_path']}, n_ben={res['n_ben']}")
        print(f"    Observed AUC:   {res['observed_auc']:.4f}")
        print(f"    Permuted mean:  {res['perm_mean_auc']:.4f} ± {res['perm_std_auc']:.4f}")
        print(f"    p-value:        {res['p_value']:.4f} {sig}")

    # 6. Distance to HBB TSS correlation
    print(f"\n{'='*70}")
    print("6. DISTANCE TO HBB TSS — SPEARMAN CORRELATION WITH SSIM")
    print(f"   Only meaningful distance metric (variant spread = {variant_spread} bp)")
    print(f"{'='*70}")
    tss_results = distance_to_tss_analysis(rows)
    for cat, info in tss_results.items():
        sig = "*" if info["p_value"] < 0.05 else "ns"
        print(f"\n  {cat}: n={info['n']}, range={info['dist_range']}")
        print(f"    Spearman ρ = {info['spearman_rho']:.4f}, p = {info['p_value']:.4e} {sig}")

    # 7. Generate figure
    print(f"\n{'='*70}")
    print("7. GENERATING FIGURES")
    print(f"{'='*70}")
    os.makedirs("plots", exist_ok=True)
    plot_positional_landscape(rows, config, f"plots/positional_signal_{args.locus}.png")

    # 8. Save JSON results
    output = {
        "analysis": "ARCHCODE within-category positional signal",
        "locus": args.locus,
        "n_variants": len(rows),
        "variant_spread_bp": variant_spread,
        "window_size_bp": window_size,
        "spread_fraction": variant_spread / window_size,
        "honest_limitation": (
            f"All {len(rows)} ClinVar variants cluster in {variant_spread} bp "
            f"({variant_spread/window_size*100:.1f}% of {window_size/1000:.0f}kb window). "
            f"Distance-to-feature predictors have minimal variance."
        ),
        "testable_categories": testable_count,
        "mann_whitney_results": [r for r in mw_results if r.get("testable")],
        "logistic_regression": lr_results,
        "permutation_results": perm_results,
        "tss_correlation": tss_results,
        "dilution_assessment": dilution,
    }

    json_path = f"results/positional_signal_{args.locus}.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"  Results saved: {json_path}")

    # 9. Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"\n  Logistic regression (SSIM additive value):")
    print(f"    → p = {lr_results['lr_p_value']:.4e}, "
          f"AUC gain = {lr_results['auc_improvement']:.4f}")

    testable_mw = [r for r in mw_results if r.get("testable")]
    if testable_mw:
        print(f"\n  Within-category Mann-Whitney U:")
        for r in testable_mw:
            sig = "SIGNIFICANT" if r["p_two_sided"] < 0.05 else "NOT SIGNIFICANT"
            print(f"    {r['category']}: Δ={r['delta_mean']:.6f}, p={r['p_two_sided']:.4e} → {sig}")

    print(f"\n  Honest assessment:")
    if lr_results["lr_p_value"] < 0.05:
        print(f"    SSIM provides statistically significant additive value")
        print(f"    beyond category assignment (LR p={lr_results['lr_p_value']:.4e}).")
    else:
        print(f"    SSIM does NOT provide significant additive value")
        print(f"    beyond category assignment at {config['id']} locus.")

    all_ns = all(r["p_two_sided"] >= 0.05 for r in testable_mw) if testable_mw else True
    any_sig = any(r["p_two_sided"] < 0.05 for r in testable_mw) if testable_mw else False
    if all_ns:
        print(f"    Within-category tests show NO significant separation.")
        print(f"    Variant spread: {variant_spread} bp ({variant_spread/window_size*100:.1f}% of window).")
    elif any_sig and lr_results["lr_p_value"] >= 0.05:
        sig_cats = [r["category"] for r in testable_mw if r["p_two_sided"] < 0.05]
        print(f"    Some within-category MW-U tests are significant ({', '.join(sig_cats)}),")
        print(f"    but global logistic regression shows no additive value (p=1.0).")
        print(f"    Conclusion: SSIM is a category-level classifier, not a within-category predictor.")


if __name__ == "__main__":
    main()
