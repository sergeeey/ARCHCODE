#!/usr/bin/env python3
"""Three Correct Falsification Tests for ARCHCODE"""
import json, numpy as np, pandas as pd, warnings
from pathlib import Path
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore")

RESULTS_DIR = Path("D:/ДНК/results")
K_BASE, ALPHA, GAMMA, BG_OCC = 0.002, 0.92, 0.8, 0.1

CAT_EFF = {"nonsense":0.1,"frameshift":0.15,"splice_donor":0.2,"splice_acceptor":0.2,
    "splice_region":0.5,"missense":0.4,"promoter":0.3,"5_prime_UTR":0.6,
    "3_prime_UTR":0.7,"intronic":0.8,"synonymous":0.9,"other":0.5}

CFG = {"start":5210000,"end":5240000,"res":600,"nb":50,
    "enh":[{"p":5227000,"o":0.85},{"p":5225500,"o":0.75},{"p":5230000,"o":0.70},
           {"p":5233000,"o":0.65},{"p":5220000,"o":0.50}],
    "ctcf":[5212000,5218000,5224000,5228000,5232000,5236000]}

class SRng:
    def __init__(s, seed): s.r = np.random.RandomState(seed % (2**31))
    def random(s): return s.r.random()

def build_occ(nb, enhs, ss, res, seed):
    rng = SRng(seed); L = np.zeros(nb)
    for i in range(nb):
        gp = ss + i*res; o = BG_OCC + rng.random()*0.05
        for e in enhs:
            d = abs(gp - e["p"]) / res
            if d < 5: o += e["o"] * np.exp(-0.5*d*d)
        L[i] = min(1.0, o)
    return L

def apply_var(L, vb, es):
    m = L.copy()
    if vb >= 0:
        for i in range(len(L)):
            d = abs(i-vb)
            if d < 3: m[i] = L[i] * (es + (1-es)*(d/3))
    return m

def cmat(nb, occ, cb):
    M = np.zeros((nb,nb))
    for i in range(nb):
        for j in range(i+1, nb):
            df = (j-i)**(-1.0); of = np.sqrt(occ[i]*occ[j])
            pf = 1.0
            for c in cb:
                if i < c < j: pf *= 0.15
            kf = 1 - K_BASE*(1-ALPHA*max(0.001,of)**GAMMA)
            v = df*of*pf*kf; M[i,j]=v; M[j,i]=v
    return M

def jnorm(r, m):
    mx = max(r.max(), m.max())
    return (r/mx, m/mx) if mx > 0 else (r, m)

def calc_ssim(a, b):
    fa,fb = a.flatten(), b.flatten()
    ma,mb = fa.mean(), fb.mean()
    sa2 = np.mean((fa-ma)**2); sb2 = np.mean((fb-mb)**2)
    sab = np.mean((fa-ma)*(fb-mb))
    return ((2*ma*mb+1e-4)*(2*sab+9e-4))/((ma**2+mb**2+1e-4)*(sa2+sb2+9e-4))

def arch_ssim(vp, cat, cfg, ctcf=None):
    s,res,nb = cfg["start"],cfg["res"],cfg["nb"]
    if ctcf is None: ctcf = cfg["ctcf"]
    vb = int((vp-s)/res)
    cb = [int((p-s)/res) for p in ctcf]; cb = [b for b in cb if 0<=b<nb]
    es = CAT_EFF.get(cat, 0.5)
    L = build_occ(nb, cfg["enh"], s, res, seed=vp)
    mo = apply_var(L, vb, es)
    rc = cb
    mc = [b for b in cb if vb<0 or abs(b-vb)>2] if ("splice" in cat or "promoter" in cat) else cb
    rm = cmat(nb, L, rc); mm = cmat(nb, mo, mc)
    rn, mn = jnorm(rm, mm)
    return calc_ssim(rn, mn)

# ====================== TEST 1 ======================
def test1(atlas, nperms=30):
    print("\n"+"="*70+"\nTEST 1: CORRECT CTCF SHUFFLE\n"+"="*70)
    cfg = CFG; rc = cfg["ctcf"]; ls,le = cfg["start"],cfg["end"]
    pa = atlas[atlas["Label"]=="Pathogenic"]
    be = atlas[atlas["Label"]=="Benign"].sample(n=min(353,750), random_state=42)
    smp = pd.concat([pa,be]).reset_index(drop=True)
    y = (smp["Label"]=="Pathogenic").astype(int).values
    print(f"Balanced: {len(smp)} ({y.sum()} path, {len(y)-y.sum()} ben)")

    print("Sanity check...")
    rs = np.array([arch_ssim(r["Position_GRCh38"],r["Category"],cfg) for _,r in smp.iterrows()])
    az = smp["ARCHCODE_SSIM"].values
    co = np.corrcoef(rs, az)[0,1]
    rauc = roc_auc_score(y, 1-rs)
    print(f"  Port corr: r={co:.4f}, Port AUC: {rauc:.4f}, Atlas AUC: {roc_auc_score(y,1-az):.4f}")

    np.random.seed(42); rd = np.diff(sorted(rc))
    sa = []
    for p in range(nperms):
        if (p+1)%5==0: print(f"  Perm {p+1}/{nperms}...")
        nc = len(rc); pos = [ls+1000]
        for _ in range(nc-1):
            d = np.random.choice(rd)+np.random.normal(0,np.random.choice(rd)*0.1)
            d = max(500,d); np3 = pos[-1]+d
            if np3 > le-1000: break
            pos.append(np3)
        while len(pos)<nc: pos.append(np.random.randint(ls+1000,le-1000))
        sc = sorted(pos[:nc])
        ps = np.array([arch_ssim(r["Position_GRCh38"],r["Category"],cfg,ctcf=sc) for _,r in smp.iterrows()])
        try: sa.append(roc_auc_score(y, 1-ps))
        except: sa.append(0.5)

    sa = np.array(sa); df = abs(rauc-sa.mean())
    if sa.std()>0: ts,pv = stats.ttest_1samp(sa, rauc)
    else: ts,pv = 0,1.0
    print(f"\nReal AUC: {rauc:.4f}")
    print(f"Shuffled: {sa.mean():.4f} +/- {sa.std():.4f} [{sa.min():.4f}-{sa.max():.4f}]")
    print(f"Delta: {df:.4f}, t={ts:.3f}, p={pv:.6f}")
    if df<0.02: v=f"EXPECTED -- AUC preserved (d={df:.4f}). Category-driven."
    elif df<0.05: v=f"INCONCLUSIVE -- small delta ({df:.4f})"
    else: v=f"SURPRISING -- CTCF matters (d={df:.4f})"
    print(f"Verdict: {v}")
    return {"real_auc":round(float(rauc),4),"shuf_mean":round(float(sa.mean()),4),
            "shuf_std":round(float(sa.std()),4),"delta":round(float(df),4),
            "corr":round(float(co),4),"verdict":v}

# ====================== TEST 2 ======================
def test2(atlas):
    print("\n"+"="*70+"\nTEST 2: NON-CIRCULAR BASELINE\n"+"="*70)
    cfg = CFG; y = (atlas["Label"]=="Pathogenic").astype(int).values
    ep = [e["p"] for e in cfg["enh"]]; cp = cfg["ctcf"]
    fe = (1-atlas["Category"].map(CAT_EFF).fillna(0.5).values).reshape(-1,1)
    fd = np.log1p(atlas["Position_GRCh38"].apply(lambda p: min(abs(p-e) for e in ep)).values).reshape(-1,1)
    fc = np.log1p(atlas["Position_GRCh38"].apply(lambda p: min(abs(p-c) for c in cp)).values).reshape(-1,1)
    arch = 1-atlas["ARCHCODE_SSIM"].values
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    sc = StandardScaler(); R = {}

    aa = roc_auc_score(y, fe.ravel()); print(f"Category only:      AUC={aa:.4f}"); R["cat"]={"auc":round(aa,4)}

    yp = cross_val_predict(LogisticRegression(random_state=42,max_iter=1000),sc.fit_transform(fd),y,cv=cv,method="predict_proba")[:,1]
    ab = roc_auc_score(y,yp); print(f"Distance only (LR): AUC={ab:.4f}"); R["dist"]={"auc":round(ab,4)}

    yp = cross_val_predict(LogisticRegression(random_state=42,max_iter=1000),sc.fit_transform(np.hstack([fe,fd])),y,cv=cv,method="predict_proba")[:,1]
    ac = roc_auc_score(y,yp); print(f"Cat+dist (LR):      AUC={ac:.4f}"); R["cat_dist"]={"auc":round(ac,4)}

    yp = cross_val_predict(RandomForestClassifier(n_estimators=100,max_depth=5,random_state=42),sc.fit_transform(np.hstack([fe,fd,fc])),y,cv=cv,method="predict_proba")[:,1]
    ad = roc_auc_score(y,yp); print(f"RF (no CADD/VEP):   AUC={ad:.4f}"); R["rf"]={"auc":round(ad,4)}

    ar = roc_auc_score(y, arch); print(f"ARCHCODE SSIM:      AUC={ar:.4f}"); R["archcode"]={"auc":round(ar,4)}
    best = max(r["auc"] for k,r in R.items() if k!="archcode")
    if best>=0.95: v=f"FAIL -- simple={best:.4f}>=0.95"
    elif best>=0.90: v=f"INCONCLUSIVE -- simple={best:.4f}"
    else: v=f"PASS -- all<0.90 (best={best:.4f})"
    print(f"Verdict: {v}"); R["verdict"]=v; R["best"]=round(best,4)
    return R

# ====================== TEST 3 ======================
def test3(atlas):
    print("\n"+"="*70+"\nTEST 3: PEARL FALSIFICATION\n"+"="*70)
    cfg = CFG; ep = [e["p"] for e in cfg["enh"]]
    pearls = atlas[(atlas["VEP_Score"]<0.3)&(atlas["Label"]=="Pathogenic")&(atlas["ARCHCODE_SSIM"]<0.95)]
    vib = atlas[(atlas["VEP_Score"]<0.3)&(atlas["Label"]=="Benign")]
    print(f"Pearls: {len(pearls)} ({pearls['Position_GRCh38'].nunique()} unique)")
    print(f"  Cats: {dict(pearls['Category'].value_counts())}")
    print(f"VEP-invis benign: {len(vib)}")
    print(f"  Cats: {dict(vib['Category'].value_counts())}")

    # A: distance among VEP<0.3
    print("\n--- A: Distance among VEP<0.3 ---")
    vi = atlas[atlas["VEP_Score"]<0.3].copy()
    ya = (vi["Label"]=="Pathogenic").astype(int).values
    da = vi["Position_GRCh38"].apply(lambda p: min(abs(p-e) for e in ep)).values
    if len(np.unique(ya))<2: ra={"verdict":"NO_DATA"}
    else:
        aa = roc_auc_score(ya,-da); pd2=da[ya==1]; bd=da[ya==0]
        u,up = stats.mannwhitneyu(pd2,bd,alternative="two-sided")
        print(f"  AUC={aa:.4f}, path_med={np.median(pd2):.0f}, ben_med={np.median(bd):.0f}, p={up:.6f}")
        va = "FAIL" if aa>=0.80 else "PASS"
        ra = {"auc":round(aa,4),"n_p":int(ya.sum()),"n_b":int(len(ya)-ya.sum()),
              "p_med":round(float(np.median(pd2))),"b_med":round(float(np.median(bd))),
              "mw_p":round(float(up),6),"verdict":va}
    print(f"  Verdict: {ra.get('verdict')}")

    # B: category overlap
    print("\n--- B: Category overlap ---")
    pc=set(pearls["Category"].unique()); bc=set(vib["Category"].unique()); sh=pc&bc
    vb="PASS" if sh else "FAIL"
    rb = {"pearl":list(pc),"benign":list(bc),"shared":list(sh),"verdict":vb}
    print(f"  Shared: {sh} => {vb}")

    # C: within shared categories
    print("\n--- C: Within shared categories ---")
    if sh:
        pool = atlas[(atlas["VEP_Score"]<0.3)&(atlas["Category"].isin(sh))].copy()
        yc = (pool["Label"]=="Pathogenic").astype(int).values
        if len(np.unique(yc))>1 and len(pool)>=10:
            sc2=pool["ARCHCODE_SSIM"].values
            dc=pool["Position_GRCh38"].apply(lambda p: min(abs(p-e) for e in ep)).values
            as2=roc_auc_score(yc,1-sc2); ad2=roc_auc_score(yc,-dc)
            adv=as2-ad2
            print(f"  n={len(pool)}, ARCH={as2:.4f}, dist={ad2:.4f}, adv={adv:+.4f}")
            if adv>0.05: vc=f"PASS -- ARCHCODE +{adv:.3f}"
            elif ad2>=as2: vc="FAIL -- distance >= ARCHCODE"
            else: vc="INCONCLUSIVE"
            rc={"n":len(pool),"arch":round(as2,4),"dist":round(ad2,4),"adv":round(float(adv),4),"verdict":vc}
        else: print(f"  Insufficient"); rc={"verdict":"INSUFFICIENT_DATA"}
    else: rc={"verdict":"NO_SHARED"}
    print(f"  Verdict: {rc.get('verdict')}")
    return {"n_pearls":len(pearls),"a":ra,"b":rb,"c":rc}

if __name__ == "__main__":
    print("="*70+"\nCORRECT FALSIFICATION TESTS\n"+"="*70)
    atlas = pd.read_csv(RESULTS_DIR / "HBB_Combined_Atlas.csv")
    print(f"Loaded {len(atlas)} variants")
    r1=test1(atlas,30); r2=test2(atlas); r3=test3(atlas)
    res={"t1":r1,"t2":r2,"t3":r3}
    print("\n"+"="*70+"\nFINAL SUMMARY\n"+"="*70)
    print(f"T1 CTCF:    {r1['verdict']}")
    print(f"T2 Base:    {r2['verdict']}")
    print(f"T3A Dist:   {r3['a'].get('verdict')}")
    print(f"T3B Cats:   {r3['b']['verdict']}")
    print(f"T3C Within: {r3['c'].get('verdict')}")
    fails=sum(1 for x in [r1['verdict'],r2['verdict'],
              r3['a'].get('verdict',"")] if str(x).startswith("FAIL"))
    ov = "REJECT" if fails>=2 else ("CAUTION" if fails==1 else "CONDITIONAL PASS")
    print(f"\nOVERALL: {ov}"); res["overall"]=ov
    with open(RESULTS_DIR/"correct_falsification_results.json","w") as f: json.dump(res,f,indent=2)
    print("Saved.")
