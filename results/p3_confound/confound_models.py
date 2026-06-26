#!/usr/bin/env python
"""
Etap 3 — Regulatory-confound test (kill criteria K1, K2).

Q (K2): does LSSIM add predictive value for the LABEL beyond consequence category?
        Model B: label ~ category    vs    Model C: label ~ category + LSSIM
Q (K1): is LSSIM itself just a deterministic function of category + CTCF distance?
        LSSIM ~ category + dist_to_CTCF   ->   R^2 near 1 means structural-annotation
        proxy, not independent 3D information.

READ-ONLY on canonical atlas. Seed fixed (passed in, not Date.now()).
Evidence marker: [VERIFIED-INLINE] descriptive computation on the project's own
ClinVar-derived atlas. NOT real-world pathogenicity validation.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "HBB_Unified_Atlas_95kb.csv"
CTCF = ROOT.parent / "data" / "hbb_ctcf_sites_literature.json"
OUT = Path(__file__).resolve().parent / "CONFOUND_STATS.json"
RNG = 20260605

df = pd.read_csv(ATLAS).dropna(subset=["ARCHCODE_LSSIM"])
df["is_path"] = df["Label"].str.lower().eq("pathogenic").astype(int)

ctcf_pos = np.array([s["position_absolute"] for s in json.loads(CTCF.read_text())["ctcf_sites"]])
df["dist_ctcf"] = df["Position_GRCh38"].apply(lambda p: float(np.min(np.abs(ctcf_pos - p))))

res = {"n": int(len(df)), "n_path": int(df["is_path"].sum()),
       "seed": RNG, "ctcf_sites_used": int(len(ctcf_pos)), "models": {}}


def cv_auc(X, y):
    """5-fold stratified CV AUC for logistic regression. Robust to separation."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RNG)
    p = cross_val_predict(
        LogisticRegression(max_iter=2000, C=1.0), X, y, cv=skf, method="predict_proba"
    )[:, 1]
    return float(roc_auc_score(y, p))


cat_dummies = pd.get_dummies(df["Category"], prefix="cat").astype(float)
y = df["is_path"].to_numpy()

res["models"]["A_label~LSSIM"] = {"cv_auc": cv_auc(df[["ARCHCODE_LSSIM"]].to_numpy(), y)}
res["models"]["B_label~category"] = {"cv_auc": cv_auc(cat_dummies.to_numpy(), y)}
XC = np.hstack([cat_dummies.to_numpy(), df[["ARCHCODE_LSSIM"]].to_numpy()])
res["models"]["C_label~category+LSSIM"] = {"cv_auc": cv_auc(XC, y)}

res["K2_verdict"] = (
    "LSSIM adds NOTHING over category"
    if res["models"]["C_label~category+LSSIM"]["cv_auc"]
    <= res["models"]["B_label~category"]["cv_auc"] + 0.01
    else "LSSIM adds residual value over category"
)

Xk = np.hstack([cat_dummies.to_numpy(), df[["dist_ctcf"]].to_numpy()])
lin = LinearRegression().fit(Xk, df["ARCHCODE_LSSIM"].to_numpy())
r2_full = lin.score(Xk, df["ARCHCODE_LSSIM"].to_numpy())
lin_cat = LinearRegression().fit(cat_dummies.to_numpy(), df["ARCHCODE_LSSIM"].to_numpy())
r2_cat = lin_cat.score(cat_dummies.to_numpy(), df["ARCHCODE_LSSIM"].to_numpy())
res["K1_LSSIM_explained"] = {
    "r2_category_only": round(float(r2_cat), 4),
    "r2_category_plus_ctcf_dist": round(float(r2_full), 4),
    "verdict": ("LSSIM is ~fully determined by category (deterministic proxy)"
                if r2_cat > 0.9 else "category alone does not explain LSSIM"),
}

intr = df[df["Category"] == "intronic"]
if len(intr) > 10 and intr["dist_ctcf"].nunique() > 1:
    rho = intr["ARCHCODE_LSSIM"].corr(intr["dist_ctcf"], method="spearman")
    res["within_intronic_lssim_vs_ctcfdist_spearman"] = round(float(rho), 4)

OUT.write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
