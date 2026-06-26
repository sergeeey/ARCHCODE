#!/usr/bin/env python
"""
GATA1 Frozen Gate — full matched-test pipeline (read-only).

Etap 5 frozen gate steps (p0_governance/RULES.md):
  1. Source audit
  2. Coordinate sanity
  3. Category baseline
  4. Position baseline
  5. Regulatory baseline (distance to CTCF/enhancer, where available)
  6. Full model comparison (A: LSSIM, B: category, C: category+LSSIM,
                           D: category+pos, E: category+pos+LSSIM)

Kill criterion K3 (governance): a locus that fails the gate is NOT promoted
to positive evidence.

Evidence marker: [VERIFIED-INLINE] on GATA1_Unified_Atlas_300kb.csv
(ClinVar-derived, real data, NOT synthetic).
DESCRIPTIVE claim only — NOT real-world pathogenicity validation.
"""
import json, re
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "GATA1_Unified_Atlas_300kb.csv"
CTCF_META = ROOT.parent / "data" / "hbb_ctcf_sites_literature.json"   # GATA1 CTCF JSON absent; note in audit
OUT = Path(__file__).resolve().parent / "GATA1_GATE_STATS.json"
RNG = 20260605

df = pd.read_csv(ATLAS)
df = df.dropna(subset=["ARCHCODE_LSSIM"])
df["is_path"] = df["Label"].str.lower().eq("pathogenic").astype(int)

# ── 1. SOURCE AUDIT ──────────────────────────────────────────────────────────
gata1_ctcf_json = ROOT.parent / "data" / "hbb_ctcf_sites_literature.json"
# check what CTCF data exists for GATA1 (may not have a dedicated file)
gata1_ctcf_exists = (ROOT.parent / "data" / "encode_cache").exists()

source_audit = {
    "atlas_file": str(ATLAS.name),
    "rows": int(len(df)),
    "n_pathogenic": int(df["is_path"].sum()),
    "n_benign": int((df["is_path"]==0).sum()),
    "ClinVar_source": "NCBI ClinVar via data/gata1_variants.csv",
    "atlas_date": "2026-03-05 (UNIFIED_ATLAS_SUMMARY_GATA1_300kb.json)",
    "effect_sources": df["Effect_Source"].unique().tolist(),
    "CTCF_source": "ENCODE_K562 (from UNIFIED_ATLAS_SUMMARY_GATA1_300kb.json)",
    "tissue_concern": "CRITICAL: K562 is a leukemic myelogenous cell line. "
                      "GATA1 is primarily an erythroid/megakaryocyte TF. "
                      "K562 CTCF landscape != HUDEP-2/K562-erythroid. "
                      "This invalidates CTCF-barrier simulation for tissue-specific claims.",
    "enhancer_source": "ENCODE_K562_H3K27ac (same tissue mismatch concern)",
    "thresholds_calibrated": False,
    "audit_verdict": "TISSUE_MISMATCH — K562 ≠ erythroid for GATA1 analysis",
}

# ── 2. COORDINATE SANITY ─────────────────────────────────────────────────────
pos = df["Position_GRCh38"]
coord_sanity = {
    "build": "GRCh38",
    "expected_chrom": "chrX",
    "expected_region": "chrX:48640425-48940425 (300kb simulation window)",
    "GATA1_gene_body_GRCh38": "chrX:48786606-48794270",
    "observed_pos_min": int(pos.min()),
    "observed_pos_max": int(pos.max()),
    "observed_range_bp": int(pos.max() - pos.min()),
    "verdict": ("WARNING: all 183 variants cluster in {:.0f}bp — essentially all coding/splice. "
                "No spread across regulatory landscape. "
                "A structural 3D metric cannot differentiate variants at the same position.").format(
                    pos.max() - pos.min()),
}

# ── 3. CATEGORY BASELINE ─────────────────────────────────────────────────────
cat_dummies = pd.get_dummies(df["Category"], prefix="cat").astype(float)
y = df["is_path"].to_numpy()

def cv_auc(X, y, seed=RNG):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    p = cross_val_predict(
        LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs"),
        X, y, cv=skf, method="predict_proba"
    )[:, 1]
    return float(roc_auc_score(y, p))

def cliffs_delta(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return None
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return float((gt - lt) / (len(a) * len(b)))

def boot_ci(x, n=3000, alpha=0.05, seed=RNG):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float)
    if len(x) < 2:
        return [None, None]
    idx = rng.integers(0, len(x), size=(n, len(x)))
    stat = np.mean(x[idx], axis=1)
    return [round(float(np.quantile(stat, alpha/2)), 6),
            round(float(np.quantile(stat, 1-alpha/2)), 6)]

cat_baseline_auc = cv_auc(cat_dummies.to_numpy(), y)

# ── 4. WITHIN-CATEGORY MATCHED TEST ─────────────────────────────────────────
within_cat = []
for cat, g in df.groupby("Category"):
    lp = g.loc[g["is_path"]==1, "ARCHCODE_LSSIM"].to_numpy()
    lb = g.loc[g["is_path"]==0, "ARCHCODE_LSSIM"].to_numpy()
    testable = bool(len(lp) >= 3 and len(lb) >= 3)
    rec = {
        "category": cat,
        "n_total": int(len(g)),
        "n_path": int(len(lp)),
        "n_benign": int(len(lb)),
        "mean_lssim_path": round(float(np.mean(lp)), 6) if len(lp) else None,
        "mean_lssim_benign": round(float(np.mean(lb)), 6) if len(lb) else None,
        "delta_lssim_path_minus_benign": round(float(np.mean(lp)-np.mean(lb)), 6) if (len(lp) and len(lb)) else None,
        "expected_direction": "negative (path < benign, since severe = low LSSIM)",
        "boot95_path": boot_ci(lp) if len(lp)>=2 else [None,None],
        "boot95_benign": boot_ci(lb) if len(lb)>=2 else [None,None],
        "testable": testable,
        "mannwhitney_p": None,
        "cliffs_delta": None,
        "within_cat_auc": None,
    }
    if testable:
        try:
            _, p = stats.mannwhitneyu(lp, lb, alternative="two-sided")
            rec["mannwhitney_p"] = float(p)
        except ValueError:
            pass
        rec["cliffs_delta"] = cliffs_delta(lp, lb)
        # AUC: score = 1-LSSIM, higher = more pathogenic-like
        sp, sn = 1-lp, 1-lb
        U, _ = stats.mannwhitneyu(sp, sn, alternative="two-sided")
        rec["within_cat_auc"] = float(U / (len(sp)*len(sn)))
    within_cat.append(rec)

# ── 5. POSITION BASELINE ─────────────────────────────────────────────────────
df["pos_norm"] = (df["Position_GRCh38"] - df["Position_GRCh38"].mean()) / (df["Position_GRCh38"].std() + 1e-9)
pos_baseline_auc = cv_auc(df[["pos_norm"]].to_numpy(), y)

# ── 6. FULL MODEL COMPARISON ─────────────────────────────────────────────────
Xa = df[["ARCHCODE_LSSIM"]].to_numpy()
Xb = cat_dummies.to_numpy()
Xc = np.hstack([cat_dummies.to_numpy(), df[["ARCHCODE_LSSIM"]].to_numpy()])
Xd = np.hstack([cat_dummies.to_numpy(), df[["pos_norm"]].to_numpy()])
Xe = np.hstack([cat_dummies.to_numpy(), df[["pos_norm"]].to_numpy(), df[["ARCHCODE_LSSIM"]].to_numpy()])

models = {
    "A_label~LSSIM":                  cv_auc(Xa, y),
    "B_label~category":               cv_auc(Xb, y),
    "C_label~category+LSSIM":         cv_auc(Xc, y),
    "D_label~category+pos":           cv_auc(Xd, y),
    "E_label~category+pos+LSSIM":     cv_auc(Xe, y),
}

# K2: does LSSIM add over category?
k2_fires = models["C_label~category+LSSIM"] <= models["B_label~category"] + 0.01
# K2b: does LSSIM add over category+pos?
k2b_fires = models["E_label~category+pos+LSSIM"] <= models["D_label~category+pos"] + 0.01

# K1: regression of LSSIM ~ category
from sklearn.linear_model import LinearRegression
lr_cat = LinearRegression().fit(Xb, df["ARCHCODE_LSSIM"].to_numpy())
r2_cat = float(lr_cat.score(Xb, df["ARCHCODE_LSSIM"].to_numpy()))
lr_catpos = LinearRegression().fit(Xd, df["ARCHCODE_LSSIM"].to_numpy())
r2_catpos = float(lr_catpos.score(Xd, df["ARCHCODE_LSSIM"].to_numpy()))

# ── VERDICT ───────────────────────────────────────────────────────────────────
testable_within = [c for c in within_cat if c["testable"]]
missense_cat = next((c for c in within_cat if c["category"] == "missense"), {})
wrong_direction = (missense_cat.get("delta_lssim_path_minus_benign") or 0) > 0  # path LSSIM > benign = wrong

if k2_fires and k2b_fires:
    gate_verdict = "FAIL_PROXY_ONLY"
elif not testable_within:
    gate_verdict = "FAIL_INSUFFICIENT_DATA"
elif wrong_direction:
    gate_verdict = "FAIL_WRONG_DIRECTION"
else:
    best_auc = max(c["within_cat_auc"] for c in testable_within if c["within_cat_auc"])
    if best_auc >= 0.70:
        gate_verdict = "PASS_RESIDUAL_SIGNAL"
    elif best_auc >= 0.60:
        gate_verdict = "WEAK_RESIDUAL_SIGNAL"
    else:
        gate_verdict = "FAIL_PROXY_ONLY"

out = {
    "locus": "GATA1",
    "date": "2026-06-05",
    "source_audit": source_audit,
    "coordinate_sanity": coord_sanity,
    "category_baseline_cv_auc": round(cat_baseline_auc, 4),
    "position_baseline_cv_auc": round(pos_baseline_auc, 4),
    "within_category_matched": within_cat,
    "model_comparison": {k: round(v, 4) for k, v in models.items()},
    "K1_LSSIM_r2_from_category": round(r2_cat, 4),
    "K1_LSSIM_r2_from_category_plus_pos": round(r2_catpos, 4),
    "K2_fires": bool(k2_fires),
    "K2b_fires": bool(k2b_fires),
    "missense_wrong_direction": bool(wrong_direction),
    "gate_verdict": gate_verdict,
}

OUT.write_text(json.dumps(out, indent=2))

print(f"GATE VERDICT: {gate_verdict}")
print()
print(f"Source audit: {source_audit['audit_verdict']}")
print(f"Coord sanity: range={coord_sanity['observed_range_bp']}bp (expected 300,000bp)")
print()
print(f"Models (5-fold CV AUC):")
for k,v in models.items():
    print(f"  {k:45s} = {v:.4f}")
print(f"\nK1 (LSSIM ~ category R2)  = {r2_cat:.4f}")
print(f"K2 fires (LSSIM adds nothing over category): {k2_fires}")
print()
print("Within-category matched test:")
for c in testable_within:
    d = c.get("delta_lssim_path_minus_benign")
    direction = "WRONG_DIR" if (d and d > 0) else "correct_dir"
    print(f"  [{c['category']:12s}] n={c['n_total']:3d} p={c['n_path']:3d} b={c['n_benign']:3d} "
          f"delta={d} AUC={c['within_cat_auc']:.4f} MW_p={c['mannwhitney_p']:.3g} cliff={c['cliffs_delta']:.3f} {direction}")
