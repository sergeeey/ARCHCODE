#!/usr/bin/env python
"""
HUDEP-2 real Hi-C HBB retest — full frozen gate (read-only).

Design rationale:
  The residual-signal hypothesis failed on all analytical maps. The ONLY data in this
  repo with the correct erythroid tissue is data/hudep2_wt_hic_hbb_locus_normalized.npy
  (GSM4873116, HUDEP-2 WT capture Hi-C, KR-balanced, 5kb resolution).

  However, at 5kb resolution the ENTIRE HBB gene and all 1103 variants fall in a
  single bin (bin 5 of the 10-bin window chr11:5200000-5250000). This makes
  per-variant LSSIM computation meaningless at this resolution — every variant
  gets exactly the same real Hi-C submatrix.

  What IS possible:
    1. Resolution verdict: are per-variant tests possible at 5kb? (answer: no)
    2. Reference validation: does the analytical wt contact map correlate with HUDEP-2?
    3. Structural comparison: SSIM(analytical, hudep2) at locus level
    4. The hybrid LSSIM test: for each variant, compute LSSIM(hudep2_perturbed, hudep2_wt)
       where perturbation is the same CATEGORICAL_EFFECTS model applied TO the real map.
       This isolates whether the real tissue landscape changes the within-category signal.
    5. Within-category matched test on hybrid LSSIM (if meaningful variation exists).

Evidence marker: [VERIFIED-INLINE] on real HUDEP-2 capture Hi-C + ClinVar-derived atlas.
DESCRIPTIVE claim only.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from scipy.signal import correlate2d
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "HBB_Unified_Atlas_95kb.csv"
HUDEP2_RAW = ROOT.parent / "data" / "hudep2_wt_hic_hbb_locus.npy"
HUDEP2_NORM = ROOT.parent / "data" / "hudep2_wt_hic_hbb_locus_normalized.npy"
ANALYTIC_NORM = ROOT.parent / "data" / "archcode_hbb_simulation_normalized.npy"
ANALYTIC_RAW_JSON = ROOT.parent / "data" / "archcode_hbb_simulation_matrix.json"
OUT = Path(__file__).resolve().parent / "HUDEP2_HBB_GATE_STATS.json"
RNG = 20260605

# ── LOAD MATRICES ─────────────────────────────────────────────────────────────
h_norm = np.load(HUDEP2_NORM)     # 10×10, KR-balanced HUDEP-2
a_norm = np.load(ANALYTIC_NORM)   # 10×10, analytical simulation, same window
h_raw  = np.load(HUDEP2_RAW)      # 10×10, raw counts

# Load analytical unnormalized
with open(ANALYTIC_RAW_JSON) as f:
    a_json = json.load(f)
a_raw = np.array(a_json["matrix"])   # 10×10

WIN_START = 5200000
WIN_END   = 5250000
RES_HIC   = 5000
N_BINS    = 10

# ── 1. RESOLUTION VERDICT ─────────────────────────────────────────────────────
df = pd.read_csv(ATLAS)
df = df.dropna(subset=["ARCHCODE_LSSIM"])
df["is_path"] = df["Label"].str.lower().eq("pathogenic").astype(int)
df["hic_bin"] = np.clip(((df["Position_GRCh38"] - WIN_START) // RES_HIC).astype(int), 0, N_BINS - 1)
in_win = df[(df["Position_GRCh38"] >= WIN_START) & (df["Position_GRCh38"] < WIN_END)]
unique_bins_used = int(in_win["hic_bin"].nunique())
all_same_bin = (unique_bins_used == 1)

res_verdict = {
    "n_variants_in_window": int(len(in_win)),
    "n_variants_total": int(len(df)),
    "unique_hic_bins_used": unique_bins_used,
    "all_in_single_bin": bool(all_same_bin),
    "implication": (
        "CRITICAL: All 1103 HBB variants fall in bin 5 (5225000-5230000) at 5kb resolution. "
        "No positional discrimination is possible at 5kb. Per-variant LSSIM from the real Hi-C "
        "position context is NOT computable — every variant has the same local Hi-C submatrix."
        if all_same_bin else
        "Variants spread across multiple bins — per-variant test is meaningful."
    ),
}

# ── 2. REFERENCE VALIDATION: analytical vs HUDEP-2 ───────────────────────────
def flat_upper(m):
    idx = np.triu_indices(m.shape[0], k=1)
    return m[idx]

h_flat = flat_upper(h_norm)
a_flat = flat_upper(a_norm)

pearson_r, pearson_p = stats.pearsonr(h_flat, a_flat)
spearman_r, spearman_p = stats.spearmanr(h_flat, a_flat)

# SSIM between the two 10×10 matrices
def ssim_2d(a, b):
    fa, fb = a.flatten(), b.flatten()
    mu_a, mu_b = fa.mean(), fb.mean()
    sa2 = fa.var()
    sb2 = fb.var()
    sab = ((fa - mu_a) * (fb - mu_b)).mean()
    c1, c2 = 1e-4, 9e-4
    return float(((2*mu_a*mu_b + c1) * (2*sab + c2)) / ((mu_a**2 + mu_b**2 + c1) * (sa2 + sb2 + c2)))

ref_ssim = ssim_2d(h_norm, a_norm)
ref_validation = {
    "pearson_r_analytic_vs_hudep2": round(float(pearson_r), 4),
    "pearson_p": float(pearson_p),
    "spearman_r_analytic_vs_hudep2": round(float(spearman_r), 4),
    "spearman_p": float(spearman_p),
    "ssim_analytic_vs_hudep2": round(ref_ssim, 4),
    "interpretation": (
        "HIGH: analytical model resembles HUDEP-2 (positive control)"
        if pearson_r > 0.8 else
        "MODERATE: partial similarity"
        if pearson_r > 0.5 else
        "LOW: analytical model does NOT resemble HUDEP-2 — another failure mode"
    ),
}

# ── 3. HYBRID LSSIM TEST ──────────────────────────────────────────────────────
# For each variant, apply the same CATEGORICAL_EFFECTS perturbation to the real
# HUDEP-2 map and compute LSSIM(hudep2_perturbed, hudep2_wt).
# The reference is now real; the mutant is the real map with the variant's
# category-derived occupancy reduction applied at the variant's 5kb bin.

CATEGORICAL_EFFECTS = {
    "nonsense": 0.1, "frameshift": 0.15, "splice_donor": 0.2, "splice_acceptor": 0.2,
    "splice_region": 0.5, "missense": 0.4, "promoter": 0.3,
    "5_prime_UTR": 0.6, "3_prime_UTR": 0.7, "intronic": 0.8, "synonymous": 0.9, "other": 0.5,
}

def hybrid_lssim(ref_matrix, variant_bin, effect_strength):
    """Compute LSSIM(ref, perturbed_ref) at 5kb scale.
    Perturbation: reduce all contacts involving variant_bin by effect_strength
    (same occupancy-reduction logic as TypeScript, applied to real Hi-C).
    """
    mut = ref_matrix.copy()
    for i in range(mut.shape[0]):
        dist = abs(i - variant_bin)
        if dist < 3:
            reduction = effect_strength + (1 - effect_strength) * (dist / 3)
            mut[variant_bin, i] *= reduction
            mut[i, variant_bin] *= reduction
    return ssim_2d(ref_matrix, mut)

# Use KR-balanced (normalized) HUDEP-2 as reference
ref = h_norm
lssim_hybrid = []
for _, row in df.iterrows():
    cat = str(row["Category"]).lower()
    es = CATEGORICAL_EFFECTS.get(cat, 0.5)
    vbin = int(row["hic_bin"])
    lssim_hybrid.append(hybrid_lssim(ref, vbin, es))

df["LSSIM_hybrid"] = lssim_hybrid

# ── 4. WITHIN-CATEGORY ANALYSIS ON HYBRID LSSIM ──────────────────────────────
def cliffs_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if not len(a) or not len(b):
        return None
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return float((gt - lt) / (len(a) * len(b)))

def cv_auc(X, y, seed=RNG):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    p = cross_val_predict(
        LogisticRegression(max_iter=2000, C=1.0), np.atleast_2d(X).T if X.ndim==1 else X,
        y, cv=skf, method="predict_proba"
    )[:, 1]
    return float(roc_auc_score(y, p))

within_cat_hybrid = []
for cat, g in df.groupby("Category"):
    lp = g.loc[g["is_path"]==1, "LSSIM_hybrid"].to_numpy()
    lb = g.loc[g["is_path"]==0, "LSSIM_hybrid"].to_numpy()
    testable = bool(len(lp)>=3 and len(lb)>=3)
    rec = {
        "category": cat,
        "n_path": int(len(lp)), "n_benign": int(len(lb)),
        "mean_hybrid_path": round(float(np.mean(lp)),6) if len(lp) else None,
        "mean_hybrid_benign": round(float(np.mean(lb)),6) if len(lb) else None,
        "delta": round(float(np.mean(lp)-np.mean(lb)),6) if (len(lp) and len(lb)) else None,
        "testable": testable,
        "within_cat_auc": None, "mannwhitney_p": None, "cliffs_delta": None,
        "unique_hybrid_values_path": int(len(np.unique(lp))),
        "unique_hybrid_values_benign": int(len(np.unique(lb))),
    }
    if testable:
        try:
            _, p = stats.mannwhitneyu(lp, lb, alternative="two-sided")
            rec["mannwhitney_p"] = float(p)
        except Exception:
            pass
        rec["cliffs_delta"] = cliffs_d(lp, lb)
        U, _ = stats.mannwhitneyu(1-lp, 1-lb, alternative="two-sided")
        rec["within_cat_auc"] = float(U / (len(lp)*len(lb)))
    within_cat_hybrid.append(rec)

# ── 5. MODEL COMPARISON (hybrid LSSIM) ───────────────────────────────────────
cat_dummies = pd.get_dummies(df["Category"], prefix="cat").astype(float)
y = df["is_path"].to_numpy()

A_auc = cv_auc(df[["LSSIM_hybrid"]].to_numpy(), y)
B_auc = cv_auc(cat_dummies.to_numpy(), y)
C_auc = cv_auc(np.hstack([cat_dummies.to_numpy(), df[["LSSIM_hybrid"]].to_numpy()]), y)
models_hybrid = {"A_label~hybrid_LSSIM": A_auc, "B_label~category": B_auc,
                 "C_label~category+hybrid_LSSIM": C_auc}

# also check unique hybrid LSSIM values globally
n_unique = int(df["LSSIM_hybrid"].nunique())
unique_per_cat = {cat: int(df[df["Category"]==cat]["LSSIM_hybrid"].nunique())
                  for cat in df["Category"].unique()}

# ── 6. VERDICT ────────────────────────────────────────────────────────────────
# Collect testable within-cat results
testable = [c for c in within_cat_hybrid if c["testable"]]
best_auc = max((c["within_cat_auc"] for c in testable if c["within_cat_auc"] is not None), default=0)
k2_fires = C_auc <= B_auc + 0.01

# Check if hybrid LSSIM has any discriminating variation within categories
max_unique = max((c["unique_hybrid_values_path"] + c["unique_hybrid_values_benign"]
                  for c in testable), default=0)
variation_exists = max_unique > 2  # more than 2 distinct values total in a testable category

if not variation_exists:
    verdict = "HUDEP2_FAILS_SAME_BIN"
elif k2_fires and best_auc < 0.60:
    verdict = "HUDEP2_FAILS_PROXY_ONLY"
elif best_auc >= 0.70:
    verdict = "HUDEP2_RESCUES_SIGNAL"
elif best_auc >= 0.60:
    verdict = "HUDEP2_WEAK_SIGNAL"
else:
    verdict = "HUDEP2_FAILS_PROXY_ONLY"

out = {
    "locus": "HBB",
    "date": "2026-06-05",
    "data_source": "GSM4873116 WT-HUDEP2 capture Hi-C, KR-balanced, 5kb, chr11:5200000-5250000",
    "resolution_verdict": res_verdict,
    "reference_validation": ref_validation,
    "hybrid_lssim": {
        "description": "LSSIM(real HUDEP2, HUDEP2_perturbed_by_CATEGORICAL_EFFECTS)",
        "n_unique_values_global": n_unique,
        "n_unique_per_category": unique_per_cat,
        "note": (
            "If all variants in same Hi-C bin AND same category have same effectStrength, "
            "the hybrid LSSIM is IDENTICAL for all of them. Unique value count reveals this."
        ),
    },
    "model_comparison_hybrid": {k: round(v, 4) for k, v in models_hybrid.items()},
    "within_category_hybrid": within_cat_hybrid,
    "k2_fires_hybrid": bool(k2_fires),
    "best_within_cat_auc": round(float(best_auc), 4),
    "gate_verdict": verdict,
}

OUT.write_text(json.dumps(out, indent=2))

print(f"\n{'='*60}")
print(f"HUDEP-2 HBB GATE VERDICT: {verdict}")
print(f"{'='*60}")
print(f"\n[1] Resolution: all {res_verdict['n_variants_in_window']} variants in {res_verdict['unique_hic_bins_used']} bin(s)")
print(f"[2] Reference validation (analytic vs HUDEP-2):")
print(f"    Pearson r = {ref_validation['pearson_r_analytic_vs_hudep2']:.4f} (p={ref_validation['pearson_p']:.2e})")
print(f"    Spearman r = {ref_validation['spearman_r_analytic_vs_hudep2']:.4f}")
print(f"    SSIM(analytic, hudep2) = {ref_validation['ssim_analytic_vs_hudep2']:.4f}")
print(f"    -> {ref_validation['interpretation']}")
print(f"\n[3] Hybrid LSSIM unique values per category:")
for cat, n in unique_per_cat.items():
    marker = "CONSTANT" if n == 1 else f"{n} values"
    print(f"    {cat:15s} → {marker}")
print(f"\n[4] Models (hybrid LSSIM):")
for k, v in models_hybrid.items():
    print(f"    {k:45s} = {v:.4f}")
print(f"    K2 fires: {k2_fires}")
print(f"\n[5] Within-category matched test (hybrid LSSIM):")
for c in testable:
    print(f"    [{c['category']:12s}] AUC={c['within_cat_auc']:.4f} MW_p={c['mannwhitney_p']:.3g} cliff={c['cliffs_delta']:.3f}")
