#!/usr/bin/env python3
"""Robustness of the category-matched conclusion to binning scheme (reviewer response).
Leave-one-category-out + coarse 3-group binning. Source: benchmark_phylop_subset.csv (23,038)."""
import pandas as pd, numpy as np
from scipy.stats import rankdata
d = pd.read_csv("D:/ДНК/results/benchmark_phylop_subset.csv")
def auc(y,s):
    y=np.asarray(y); s=np.asarray(s,float); npos=int(y.sum()); nn=len(y)-npos
    if npos==0 or nn==0: return np.nan,0
    r=rankdata(s); return (r[y==1].sum()-npos*(npos+1)/2)/(npos*nn), npos*nn
def marg(y,s): return auc(y,s)[0]
def strat(y,s,cat):
    num=den=0.0
    for c in np.unique(cat):
        m=cat==c; a,p=auc(y[m],s[m])
        if p>0 and not np.isnan(a): num+=a*p; den+=p
    return num/den if den else np.nan
def orient(y,s,cat): return s if marg(y,s)>=0.5 else -s
# LOCO for ARCHCODE_LSSIM
vals=[]
for drop in d["Category"].unique():
    sub=d[d["Category"]!=drop]; y=sub["y"].values; c=sub["Category"].values
    vals.append(strat(y,orient(y,sub["ARCHCODE_LSSIM"].values,c),c))
print(f"LOCO ARCHCODE_LSSIM within-cat range: {min(vals):.3f}-{max(vals):.3f} (all<0.55: {all(v<0.55 for v in vals)})")
# coarse 3-group
coarse={'nonsense':'trunc','frameshift':'trunc','splice_donor':'trunc','splice_acceptor':'trunc',
        'missense':'subst','synonymous':'subst','inframe_deletion':'subst','inframe_indel':'subst',
        'intronic':'nonc','promoter':'nonc','3_prime_UTR':'nonc','5_prime_UTR':'nonc','splice_region':'nonc','other':'nonc'}
d["coarse"]=d["Category"].map(coarse)
for col in ["ARCHCODE_LSSIM","ARCHCODE_SSIM","phylop","CADD_Phred"]:
    g=d.dropna(subset=[col]); y=g["y"].values; c=g["coarse"].values
    print(f"coarse within-group {col}: {strat(y,orient(y,g[col].values,c),c):.3f}")
