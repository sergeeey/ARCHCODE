#!/usr/bin/env python
"""
A2 — Generality of the category-lookup property across loci/diseases.

Scans results/ for every locus that has the full 5-mode ablation set
({LOCUS}_Unified_Atlas_*.csv: categorical + POSITION_ONLY + UNIFORM_MEDIUM +
INVERTED + RANDOM) and computes the transfer-function diagnostics per locus:
  - categorical global AUC
  - mirror gap |AUC_cat - (1 - AUC_inverted)|
  - position-random gap |AUC_pos - AUC_random|

Tests the hypothesis: the mirror (directional category lookup) is universal across
unrelated disease genes, not specific to erythroid loci. HBB taken from the
precomputed ablation_effectstrength.json.

Evidence: [VERIFIED-INLINE], real ClinVar atlases via the project's own engine.
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]  # results/
OUT = Path(__file__).resolve().parent / "MULTILOCUS_GENERALITY.json"

SUFFIX = {
    "categorical": "",
    "position-only": "_POSITION_ONLY",
    "uniform-medium": "_UNIFORM_MEDIUM",
    "inverted": "_INVERTED",
    "random": "_RANDOM",
}

DISEASE = {
    "HBB": "β-thalassemia",
    "GATA1": "anemia/leukemia",
    "HBA1": "α-thalassemia",
    "BCL11A": "HbF/intellectual disability",
    "GJB2": "deafness",
    "LDLR": "hypercholesterolemia",
    "PTEN": "cancer/PHTS",
    "SCN5A": "cardiac arrhythmia",
    "TERT": "cancer/telomere",
}


def auc_mw(p, b):
    if len(p) == 0 or len(b) == 0:
        return np.nan
    u, _ = mannwhitneyu(-np.asarray(p, float), -np.asarray(b, float), alternative="two-sided")
    return float(u / (len(p) * len(b)))


def global_auc(csv):
    d = pd.read_csv(csv).dropna(subset=["ARCHCODE_LSSIM"])
    d["p"] = d["Label"].str.lower().str.startswith("patho")
    return auc_mw(d[d.p].ARCHCODE_LSSIM, d[~d.p].ARCHCODE_LSSIM), int(d.p.sum()), int((~d.p).sum())


# discover loci with a categorical atlas + all 4 ablations
loci = {}
for cat_csv in sorted(ROOT.glob("*_Unified_Atlas_*.csv")):
    m = re.match(r"([A-Z0-9]+)_Unified_Atlas_(\d+kb)(_[A-Z_]+)?\.csv", cat_csv.name)
    if not m:
        continue
    locus, window, suf = m.group(1), m.group(2), m.group(3)
    if suf:  # only seed from the categorical (no suffix) file
        continue
    base = ROOT / f"{locus}_Unified_Atlas_{window}"
    if all((Path(str(base) + s + ".csv").exists()) for s in SUFFIX.values()):
        loci[locus] = base

result = {
    "experiment": "A2 — multi-locus generality of category-lookup property",
    "evidence": "[VERIFIED-INLINE] real ClinVar atlases, project engine, 5-mode ablation",
    "loci": {},
}

# HBB from precomputed
hbb = json.load(open(ROOT / "ablation_effectstrength.json"))
hm = {x["mode"]: x["auc"] for x in hbb["modes"]}
result["loci"]["HBB"] = {
    "disease": DISEASE["HBB"],
    "n_path": hbb["n_pathogenic"],
    "n_benign": hbb["n_benign"],
    "categorical_auc": hm["categorical"],
    "inverted_auc": hm["inverted"],
    "mirror_gap": round(abs(hm["categorical"] - (1 - hm["inverted"])), 4),
    "position_random_gap": round(abs(hm["position-only"] - hm["random"]), 4),
    "source": "ablation_effectstrength.json (precomputed)",
}

for locus, base in loci.items():
    aucs = {}
    npb = None
    for mode, suf in SUFFIX.items():
        a, np_, nb_ = global_auc(Path(str(base) + suf + ".csv"))
        aucs[mode] = a
        npb = (np_, nb_)
    result["loci"][locus] = {
        "disease": DISEASE.get(locus, "?"),
        "n_path": npb[0],
        "n_benign": npb[1],
        "categorical_auc": round(aucs["categorical"], 4),
        "inverted_auc": round(aucs["inverted"], 4),
        "mirror_gap": round(abs(aucs["categorical"] - (1 - aucs["inverted"])), 4),
        "position_random_gap": round(abs(aucs["position-only"] - aucs["random"]), 4),
    }

# summary
gaps = [v["mirror_gap"] for v in result["loci"].values()]
result["summary"] = {
    "n_loci": len(result["loci"]),
    "loci_list": sorted(result["loci"].keys()),
    "mirror_gap_max": round(max(gaps), 4),
    "mirror_gap_mean": round(float(np.mean(gaps)), 4),
    "all_mirror_below_0.10": bool(all(g < 0.10 for g in gaps)),
    "verdict": (
        "CATEGORY-LOOKUP PROPERTY IS LOCUS-GENERAL across diseases"
        if all(g < 0.10 for g in gaps)
        else "MIXED — inspect per-locus"
    ),
}

OUT.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
print("\nSaved:", OUT)
