#!/usr/bin/env python3
"""Unsupervised positive control: phyloP100way conservation vs ARCHCODE, category-matched.
Fetches UCSC phyloP per locus (chunked), computes marginal + within-category stratified AUC."""

import json, time, sys
from pathlib import Path
import numpy as np, pandas as pd, requests
from scipy.stats import rankdata

ROOT = Path("D:/ДНК")
OUT = ROOT / "results" / "phylop_control.json"
CHROM = {
    "BRCA1": "chr17",
    "CFTR": "chr7",
    "GJB2": "chr13",
    "HBB": "chr11",
    "LDLR": "chr19",
    "MLH1": "chr3",
    "SCN5A": "chr3",
    "TERT": "chr5",
    "TP53": "chr17",
}
URL = "https://api.genome.ucsc.edu/getData/track"


def fetch_phylop(chrom, lo, hi, chunk=50000):
    pp = {}
    p = lo
    while p < hi:
        end = min(p + chunk, hi)
        for attempt in range(3):
            try:
                r = requests.get(
                    URL,
                    params={
                        "genome": "hg38",
                        "track": "phyloP100way",
                        "chrom": chrom,
                        "start": p,
                        "end": end,
                    },
                    timeout=90,
                )
                d = r.json()
                for it in d.get("phyloP100way", []):
                    pp[it["end"]] = it["value"]  # UCSC end == 1-based pos
                break
            except Exception as e:
                if attempt == 2:
                    print(f"    fail {chrom}:{p}-{end}: {e}")
                time.sleep(2)
        p = end
        time.sleep(0.2)
    return pp


def auc(y, s):
    y = np.asarray(y)
    s = np.asarray(s, float)
    np_ = int(y.sum())
    nn = len(y) - np_
    if np_ == 0 or nn == 0:
        return np.nan, 0
    r = rankdata(s)
    return (r[y == 1].sum() - np_ * (np_ + 1) / 2) / (np_ * nn), np_ * nn


def marg(y, s):
    return auc(y, s)[0]


def strat(y, s, cat):
    num = den = 0.0
    for c in np.unique(cat):
        m = cat == c
        a, p = auc(y[m], s[m])
        if p > 0 and not np.isnan(a):
            num += a * p
            den += p
    return num / den if den else np.nan


def orient(y, s, cat):
    return s if marg(y, s) >= 0.5 else -s


df = pd.read_csv(ROOT / "results" / "integrative_benchmark.csv")
sig = df["ClinVar_Significance"].fillna("NaN")
P = {
    "Pathogenic",
    "Likely pathogenic",
    "Pathogenic/Likely pathogenic",
    "Pathogenic/Likely pathogenic; other",
    "Pathogenic; drug response",
    "Pathogenic; other",
}
B = {"Benign", "Benign/Likely benign", "Likely benign"}
df["y"] = np.where(sig.isin(P), 1, np.where(sig.isin(B), 0, -1))
d = df[df["y"] >= 0].copy()

# fetch phyloP per locus over 2.5-97.5 pct window
d["phylop"] = np.nan
for loc, g in d.groupby("Locus"):
    lo = int(np.percentile(g["Position"], 2.5))
    hi = int(np.percentile(g["Position"], 97.5)) + 1
    print(f"{loc}: {CHROM[loc]}:{lo:,}-{hi:,} ({hi - lo:,}bp)...", flush=True)
    pp = fetch_phylop(CHROM[loc], lo - 1, hi)
    idx = g.index
    d.loc[idx, "phylop"] = g["Position"].map(lambda p: pp.get(int(p), np.nan)).values
    cov = d.loc[idx, "phylop"].notna().mean()
    print(f"    coverage {cov * 100:.0f}% of {len(g)} variants", flush=True)

dd = d.dropna(subset=["phylop"]).copy()
y = dd["y"].values
cat = dd["Category"].values
print(f"\nphyloP assigned to {len(dd)}/{len(d)} variants")
s = orient(y, dd["phylop"].values, cat)
res = {
    "n": len(dd),
    "phylop_marginal": round(marg(y, s), 3),
    "phylop_within_category": round(strat(y, s, cat), 3),
}
# ARCHCODE + CADD on SAME phyloP-covered subset for fair comparison
for col in ["ARCHCODE_LSSIM", "ARCHCODE_SSIM", "CADD_Phred"]:
    sub = dd.dropna(subset=[col])
    yy = sub["y"].values
    cc = sub["Category"].values
    ss = orient(yy, sub[col].values, cc)
    res[f"{col}_marginal"] = round(marg(yy, ss), 3)
    res[f"{col}_within_category"] = round(strat(yy, ss, cc), 3)
    res[f"{col}_n"] = len(sub)
OUT.write_text(json.dumps(res, indent=2))
print("\n=== RESULT (same phyloP-covered subset) ===")
for k, v in res.items():
    print(f"  {k}: {v}")
print(f"\nSaved: {OUT}")
