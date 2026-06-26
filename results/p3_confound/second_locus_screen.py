#!/usr/bin/env python
"""
Etap 5 pre-gate — second-locus degeneracy screen (READ-ONLY).

WHY: HBB and BCL11A both failed because their category x label matrix is degenerate
(benign ~all one category, severe categories have 0 benign) -> a matched-category test
is impossible. Before spending effort simulating any candidate locus, screen whether
its ClinVar data can EVER support a non-circular matched test.

Pass condition: >=1 consequence category with >=3 pathogenic AND >=3 benign.
This is the 'category baseline' step of the frozen gate (p0_governance/RULES.md).

Evidence: [VERIFIED-INLINE] on real ClinVar-derived CSVs. Descriptive screen only.
"""
import json
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
OUT = Path(__file__).resolve().parent / "SECOND_LOCUS_SCREEN.json"
CANDIDATES = {"GATA1": "gata1_variants.csv", "HBA1": "hba1_variants.csv"}

PATH_KEYS = ("pathogenic",)
BEN_KEYS = ("benign",)


def norm_label(s):
    s = str(s).lower()
    if "pathogenic" in s and "benign" not in s:
        return "pathogenic"
    if "benign" in s and "pathogenic" not in s:
        return "benign"
    return "other"


report = {"screen": "second-locus matched-test feasibility", "min_per_class": 3, "loci": []}
for locus, fname in CANDIDATES.items():
    p = DATA / fname
    if not p.exists():
        report["loci"].append({"locus": locus, "status": "FILE_MISSING"})
        continue
    df = pd.read_csv(p)
    lab_col = "label" if "label" in df.columns else "clinical_significance"
    df["_lab"] = df[lab_col].apply(norm_label)
    rec = {"locus": locus, "file": fname, "n": int(len(df)),
           "n_path": int((df["_lab"] == "pathogenic").sum()),
           "n_benign": int((df["_lab"] == "benign").sum()),
           "categories": [], "testable_categories": [], "verdict": ""}
    if "category" in df.columns:
        for cat, g in df.groupby("category"):
            np_, nb_ = int((g["_lab"] == "pathogenic").sum()), int((g["_lab"] == "benign").sum())
            rec["categories"].append({"category": str(cat), "n_path": np_, "n_benign": nb_})
            if np_ >= 3 and nb_ >= 3:
                rec["testable_categories"].append(str(cat))
        rec["verdict"] = ("PASS — matched test feasible" if rec["testable_categories"]
                          else "FAIL — degenerate (same wall as HBB/BCL11A)")
    else:
        rec["verdict"] = "NO_CATEGORY_COLUMN — needs consequence annotation first"
    report["loci"].append(rec)

OUT.write_text(json.dumps(report, indent=2))
for l in report["loci"]:
    print(f"{l['locus']:6s} n={l.get('n','?')} path={l.get('n_path','?')} ben={l.get('n_benign','?')} "
          f"-> {l.get('verdict','?')}  testable={l.get('testable_categories', [])}")
