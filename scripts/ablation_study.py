"""
EXP-001: Epigenome-only vs Epigenome+3D Ablation Study
=======================================================
Compares 4 models on the same 30,318-variant dataset:
  M1: Nearest-gene only (distance to TSS)
  M2: Epigenome-only (distance to nearest H3K27ac enhancer + CTCF proximity)
  M3: Epigenome + simplified 3D (enhancer distance + CTCF count between)
  M4: ARCHCODE full (LSSIM from loop extrusion simulation)

Metric: AUC for P/LP vs B/LB separation, overall and within enhancer-proximal zone.
If M2 ≈ M4, the 3D simulation overhead is unjustified.

Usage: python scripts/ablation_study.py
"""

import json
import os

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve

# ── Load locus configs for enhancer/CTCF/TSS positions ───────

LOCUS_CONFIGS = {
    "HBB": "config/locus/hbb_95kb_subTAD.json",
    "BRCA1": "config/locus/brca1_400kb.json",
    "TP53": "config/locus/tp53_300kb.json",
    "TERT": "config/locus/tert_300kb.json",
    "MLH1": "config/locus/mlh1_300kb.json",
    "CFTR": "config/locus/cftr_317kb.json",
    "SCN5A": "config/locus/scn5a_400kb.json",
    "GJB2": "config/locus/gjb2_300kb.json",
    "LDLR": "config/locus/ldlr_300kb.json",
}

ATLAS_FILES = {
    "HBB": "results/HBB_Unified_Atlas.csv",
    "BRCA1": "results/BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "results/TP53_Unified_Atlas_300kb.csv",
    "TERT": "results/TERT_Unified_Atlas_300kb.csv",
    "MLH1": "results/MLH1_Unified_Atlas_300kb.csv",
    "CFTR": "results/CFTR_Unified_Atlas_317kb.csv",
    "SCN5A": "results/SCN5A_Unified_Atlas_400kb.csv",
    "GJB2": "results/GJB2_Unified_Atlas_300kb.csv",
    "LDLR": "results/LDLR_Unified_Atlas_300kb.csv",
}


def load_config(locus):
    with open(LOCUS_CONFIGS[locus]) as f:
        cfg = json.load(f)
    enhancers = [e["position"] for e in cfg["features"]["enhancers"]]
    ctcf_sites = [c["position"] for c in cfg["features"]["ctcf_sites"]]
    # TSS = first enhancer with "TSS" or "promoter" in name, or first enhancer
    tss = enhancers[0]
    for e in cfg["features"]["enhancers"]:
        if "TSS" in e.get("name", "") or "promoter" in e.get("name", "").lower():
            tss = e["position"]
            break
    return enhancers, ctcf_sites, tss


def compute_features(df, enhancers, ctcf_sites, tss):
    """Compute ablation features for each variant."""
    positions = df["Position_GRCh38"].values

    # M1: Distance to TSS (log-transformed, inverted: closer = higher score)
    dist_tss = np.abs(positions - tss).astype(float)
    dist_tss[dist_tss == 0] = 1  # avoid log(0)
    m1_score = 1.0 / np.log10(dist_tss + 1)

    # M2: Distance to nearest enhancer (epigenome-only)
    dist_enh = np.array([min(abs(p - e) for e in enhancers) for p in positions]).astype(float)
    dist_enh[dist_enh == 0] = 1
    m2_enh = 1.0 / np.log10(dist_enh + 1)

    # Also add CTCF proximity component
    dist_ctcf = np.array([min(abs(p - c) for c in ctcf_sites) for p in positions]).astype(float)
    dist_ctcf[dist_ctcf == 0] = 1
    m2_ctcf = 1.0 / np.log10(dist_ctcf + 1)

    # M2 combined: enhancer proximity (weighted 0.7) + CTCF proximity (weighted 0.3)
    m2_score = 0.7 * m2_enh + 0.3 * m2_ctcf

    # M3: Epigenome + simplified 3D (enhancer distance + N CTCF barriers between)
    n_ctcf_between = np.zeros(len(positions))
    for i, pos in enumerate(positions):
        nearest_enh = min(enhancers, key=lambda e: abs(pos - e))
        lo, hi = min(pos, nearest_enh), max(pos, nearest_enh)
        n_ctcf_between[i] = sum(1 for c in ctcf_sites if lo < c < hi)

    # More barriers between variant and enhancer = more insulation = less disruption
    barrier_penalty = 1.0 / (1.0 + n_ctcf_between)
    m3_score = m2_enh * barrier_penalty

    # M4: ARCHCODE LSSIM (inverted: lower LSSIM = higher disruption score)
    lssim = df["ARCHCODE_LSSIM"].values.astype(float)
    m4_score = 1.0 - lssim

    return m1_score, m2_score, m3_score, m4_score


def safe_auc(y_true, y_score):
    """Compute AUC, return NaN if only one class present."""
    if len(set(y_true)) < 2:
        return np.nan
    try:
        return roc_auc_score(y_true, y_score)
    except ValueError:
        return np.nan


# ── Main ──────────────────────────────────────────────────────


def main():
    print("=" * 70)
    print("EXP-001: Ablation Study — What Does 3D Add?")
    print("=" * 70)

    all_results = []
    all_data = []  # for combined analysis

    for locus, atlas_path in ATLAS_FILES.items():
        if not os.path.exists(atlas_path):
            print(f"  SKIP {locus}: {atlas_path} not found")
            continue

        df = pd.read_csv(atlas_path)

        # Binary label: P/LP = 1, B/LB = 0
        plp = df["ClinVar_Significance"].str.contains("athogenic", na=False)
        blb = df["ClinVar_Significance"].str.contains("enign", na=False)
        mask = plp | blb
        df_labeled = df[mask].copy()
        df_labeled["label"] = plp[mask].astype(int)

        if len(df_labeled) < 10 or df_labeled["label"].nunique() < 2:
            print(f"  SKIP {locus}: insufficient labeled data ({len(df_labeled)} rows)")
            continue

        # Drop rows with NaN LSSIM
        df_labeled = df_labeled.dropna(subset=["ARCHCODE_LSSIM", "Position_GRCh38"])

        enhancers, ctcf_sites, tss = load_config(locus)
        m1, m2, m3, m4 = compute_features(df_labeled, enhancers, ctcf_sites, tss)
        y = df_labeled["label"].values

        # Overall AUC
        auc_m1 = safe_auc(y, m1)
        auc_m2 = safe_auc(y, m2)
        auc_m3 = safe_auc(y, m3)
        auc_m4 = safe_auc(y, m4)

        # Enhancer-proximal subset (≤5 kb from nearest enhancer)
        positions = df_labeled["Position_GRCh38"].values
        dist_enh = np.array([min(abs(p - e) for e in enhancers) for p in positions])
        enh_mask = dist_enh <= 5000

        auc_m1_ep = safe_auc(y[enh_mask], m1[enh_mask]) if enh_mask.sum() > 10 else np.nan
        auc_m2_ep = safe_auc(y[enh_mask], m2[enh_mask]) if enh_mask.sum() > 10 else np.nan
        auc_m3_ep = safe_auc(y[enh_mask], m3[enh_mask]) if enh_mask.sum() > 10 else np.nan
        auc_m4_ep = safe_auc(y[enh_mask], m4[enh_mask]) if enh_mask.sum() > 10 else np.nan

        result = {
            "locus": locus,
            "n_total": len(df_labeled),
            "n_pathogenic": int(y.sum()),
            "n_benign": int((1 - y).sum()),
            "n_enh_proximal": int(enh_mask.sum()),
            "auc_m1_nearest_gene": round(auc_m1, 4) if not np.isnan(auc_m1) else None,
            "auc_m2_epigenome_only": round(auc_m2, 4) if not np.isnan(auc_m2) else None,
            "auc_m3_epigenome_3d": round(auc_m3, 4) if not np.isnan(auc_m3) else None,
            "auc_m4_archcode": round(auc_m4, 4) if not np.isnan(auc_m4) else None,
            "auc_m1_enh_proximal": round(auc_m1_ep, 4) if not np.isnan(auc_m1_ep) else None,
            "auc_m2_enh_proximal": round(auc_m2_ep, 4) if not np.isnan(auc_m2_ep) else None,
            "auc_m3_enh_proximal": round(auc_m3_ep, 4) if not np.isnan(auc_m3_ep) else None,
            "auc_m4_enh_proximal": round(auc_m4_ep, 4) if not np.isnan(auc_m4_ep) else None,
        }
        all_results.append(result)

        # Store for combined analysis
        df_labeled = df_labeled.copy()
        df_labeled["locus"] = locus
        df_labeled["m1"] = m1
        df_labeled["m2"] = m2
        df_labeled["m3"] = m3
        df_labeled["m4"] = m4
        df_labeled["dist_enh"] = dist_enh
        all_data.append(df_labeled)

        print(f"\n  {locus} (n={len(df_labeled)}, P/LP={int(y.sum())}, B/LB={int((1 - y).sum())})")
        print(
            f"    Overall:          M1={auc_m1:.3f}  M2={auc_m2:.3f}  M3={auc_m3:.3f}  M4={auc_m4:.3f}"
        )
        if not np.isnan(auc_m4_ep):
            print(
                f"    Enh-proximal({int(enh_mask.sum())}): M1={auc_m1_ep:.3f}  M2={auc_m2_ep:.3f}  M3={auc_m3_ep:.3f}  M4={auc_m4_ep:.3f}"
            )
        else:
            print(f"    Enh-proximal: insufficient data (n={int(enh_mask.sum())})")

    # ── Combined cross-locus analysis ────────────────────────
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        y_all = combined["label"].values
        enh_mask_all = combined["dist_enh"].values <= 5000

        print("\n" + "=" * 70)
        print("=== Combined Cross-Locus Analysis ===")
        print(
            f"Total: {len(combined)} variants ({int(y_all.sum())} P/LP, {int((1 - y_all).sum())} B/LB)"
        )

        for name, scores in [
            ("M1:Nearest-gene", combined["m1"].values),
            ("M2:Epigenome-only", combined["m2"].values),
            ("M3:Epigenome+3D", combined["m3"].values),
            ("M4:ARCHCODE", combined["m4"].values),
        ]:
            auc_all = safe_auc(y_all, scores)
            auc_ep = (
                safe_auc(y_all[enh_mask_all], scores[enh_mask_all])
                if enh_mask_all.sum() > 10
                else np.nan
            )
            ep_str = f"{auc_ep:.4f}" if not np.isnan(auc_ep) else "N/A"
            print(f"  {name:25s}  Overall AUC={auc_all:.4f}  Enh-proximal AUC={ep_str}")

    # ── Save results ─────────────────────────────────────────
    os.makedirs("analysis", exist_ok=True)

    results_df = pd.DataFrame(all_results)
    results_df.to_csv("analysis/ablation_study_results.csv", index=False)
    print(f"\nSaved: analysis/ablation_study_results.csv ({len(all_results)} loci)")

    summary = {
        "experiment": "EXP-001: Ablation Study",
        "date": "2026-03-09",
        "n_loci": len(all_results),
        "n_variants_total": int(sum(r["n_total"] for r in all_results)),
        "models": {
            "M1": "Nearest-gene (1/log10(dist_TSS))",
            "M2": "Epigenome-only (0.7×enhancer_proximity + 0.3×CTCF_proximity)",
            "M3": "Epigenome+3D (enhancer_proximity × barrier_penalty)",
            "M4": "ARCHCODE (1 - LSSIM)",
        },
        "per_locus": all_results,
    }

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        y_all = combined["label"].values
        enh_mask_all = combined["dist_enh"].values <= 5000
        summary["combined"] = {
            "n_total": len(combined),
            "n_enh_proximal": int(enh_mask_all.sum()),
            "auc_m1_overall": round(safe_auc(y_all, combined["m1"].values), 4),
            "auc_m2_overall": round(safe_auc(y_all, combined["m2"].values), 4),
            "auc_m3_overall": round(safe_auc(y_all, combined["m3"].values), 4),
            "auc_m4_overall": round(safe_auc(y_all, combined["m4"].values), 4),
        }

    with open("analysis/ablation_study_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Saved: analysis/ablation_study_summary.json")

    # ── Figure ───────────────────────────────────────────────
    try:
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Panel A: Per-locus AUC comparison
        ax = axes[0]
        loci = [r["locus"] for r in all_results]
        x = np.arange(len(loci))
        w = 0.2
        for i, (key, label, color) in enumerate(
            [
                ("auc_m1_nearest_gene", "M1: Nearest-gene", "#9E9E9E"),
                ("auc_m2_epigenome_only", "M2: Epigenome-only", "#FF9800"),
                ("auc_m3_epigenome_3d", "M3: Epigenome+3D", "#2196F3"),
                ("auc_m4_archcode", "M4: ARCHCODE", "#E53935"),
            ]
        ):
            vals = [r[key] if r[key] is not None else 0.5 for r in all_results]
            ax.bar(x + (i - 1.5) * w, vals, w, label=label, color=color, alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(loci, rotation=45, ha="right")
        ax.set_ylabel("AUC (P/LP vs B/LB)")
        ax.set_title("A. Per-Locus AUC: 4-Model Ablation", fontweight="bold")
        ax.axhline(0.5, color="gray", linewidth=0.5, linestyle="--", label="Random")
        ax.legend(fontsize=8, loc="lower right")
        ax.set_ylim(0.3, 1.05)

        # Panel B: Combined ROC curves
        ax = axes[1]
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            y_all = combined["label"].values

            for scores, label, color, ls in [
                (combined["m1"].values, "M1: Nearest-gene", "#9E9E9E", "--"),
                (combined["m2"].values, "M2: Epigenome-only", "#FF9800", "--"),
                (combined["m3"].values, "M3: Epigenome+3D", "#2196F3", "-."),
                (combined["m4"].values, "M4: ARCHCODE", "#E53935", "-"),
            ]:
                fpr, tpr, _ = roc_curve(y_all, scores)
                auc_val = safe_auc(y_all, scores)
                ax.plot(
                    fpr,
                    tpr,
                    color=color,
                    linestyle=ls,
                    linewidth=2,
                    label=f"{label} (AUC={auc_val:.3f})",
                )

            ax.plot([0, 1], [0, 1], "k--", linewidth=0.5)
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            ax.set_title("B. Combined ROC (All 9 Loci)", fontweight="bold")
            ax.legend(fontsize=9)

        plt.tight_layout()
        plt.savefig("figures/fig_ablation_study.pdf", bbox_inches="tight", dpi=300)
        plt.savefig("figures/fig_ablation_study.png", bbox_inches="tight", dpi=200)
        plt.close()
        print("Saved: figures/fig_ablation_study.pdf + .png")
    except ImportError:
        print("matplotlib not available — skipping figure")


if __name__ == "__main__":
    main()
