#!/usr/bin/env python3
"""
Step +2 analysis: TAD-aware gene constraint filter on ClinVar SVs.

Algorithm (two-tier):
  Tier 1 (body overlap): SV directly deletes gene with pLI>=0.9 OR LOEUF<=0.80
  Tier 2 (+-200kb, no CTCF barrier): pLI>=0.9 OR LOEUF<=0.35

CTCF barrier check: if a strong CTCF site (score>=50) lies between the SV edge
and the gene, the gene is in a different TAD -> excluded.

Results [VERIFIED-REAL] ClinVar n=50: Recall=0.68, Precision=0.895, FPR=0.08
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from archcode_sv import (
    find_hi_genes_step2,
    load_ctcf_strong,
    load_gene_constraint,
)

CLINVAR_IN = "experiments/exp_archcode_sv/clinvar_results.json"
RESULTS_OUT = "experiments/exp_archcode_sv/clinvar_step2_results.json"


def apply_step2(sv: dict, constraint: dict, genes: list[dict], strong_ctcf: dict) -> dict:
    sv = dict(sv)
    if sv["verdict"] == "DISRUPTED":
        hi = find_hi_genes_step2(
            sv["chrom"], sv["start"], sv["end"], constraint, genes, strong_ctcf
        )
        sv["step2_verdict"] = "DISRUPTED_WITH_HI_GENE" if hi else "DISRUPTED_NO_HI_GENE"
        sv["hi_genes_step2"] = hi
    else:
        sv["step2_verdict"] = "INTACT"
        sv["hi_genes_step2"] = []
    return sv


def compute_metrics(svs: list[dict], verdict_key: str = "step2_verdict") -> dict:
    tp = fn = fp = tn = 0
    for sv in svs:
        pred = sv[verdict_key] == "DISRUPTED_WITH_HI_GENE"
        if sv["pathogenic"] and pred:
            tp += 1
        elif sv["pathogenic"] and not pred:
            fn += 1
        elif not sv["pathogenic"] and pred:
            fp += 1
        else:
            tn += 1
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    return {
        "TP": tp,
        "FN": fn,
        "FP": fp,
        "TN": tn,
        "recall": round(recall, 3),
        "precision": round(precision, 3),
        "FPR": round(fpr, 3),
    }


REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    os.chdir(REPO_ROOT)

    with open(CLINVAR_IN) as f:
        data = json.load(f)

    constraint, genes = load_gene_constraint()
    strong_ctcf = load_ctcf_strong()
    print(
        f"gnomAD: {len(constraint)} genes | GENCODE: {len(genes)} genes | Strong CTCF: {sum(len(v) for v in strong_ctcf.values())}"
    )

    all_svs = data["pathogenic_svs"] + data["benign_svs"]
    annotated = [apply_step2(sv, constraint, genes, strong_ctcf) for sv in all_svs]

    m0 = data["metrics"]
    m2 = compute_metrics(annotated)

    print("\n=== Step 0 (boundary disruption only) ===")
    print(f"TP={m0['TP']}  FN={m0['FN']}  FP={m0['FP']}  TN={m0['TN']}")
    print(f"Recall={m0['recall']:.3f}  FPR={m0['FPR']:.3f}")

    print("\n=== Step +2 (TAD-aware gene constraint) ===")
    print(f"TP={m2['TP']}  FN={m2['FN']}  FP={m2['FP']}  TN={m2['TN']}")
    print(f"Recall={m2['recall']:.3f}  Precision={m2['precision']:.3f}  FPR={m2['FPR']:.3f}")

    goal_met = m2["FPR"] <= 0.15 and m2["recall"] >= 0.65
    print(f"\nGOAL (FPR<=15% AND Recall>=65%): {'ACHIEVED' if goal_met else 'NOT MET'}")

    print("\n=== Remaining FPs ===")
    for sv in annotated:
        if not sv["pathogenic"] and sv["step2_verdict"] == "DISRUPTED_WITH_HI_GENE":
            print(f"  {sv['chrom']}:{sv['start']}-{sv['end']}  hi={sv['hi_genes_step2'][:3]}")

    print("\n=== FN-DISRUPTED (pathogenic, DISRUPTED but no qualifying HI genes) ===")
    for sv in annotated:
        if (
            sv["pathogenic"]
            and sv["verdict"] == "DISRUPTED"
            and sv["step2_verdict"] != "DISRUPTED_WITH_HI_GENE"
        ):
            print(f"  {sv['chrom']}:{sv['start']}-{sv['end']}  ratio={sv['ratio']:.3f}")

    out = {
        "source": data["source"],
        "filter": data["filter"],
        "evidence": "[VERIFIED-REAL] ClinVar + ENCODE CTCF K562 hg38 + gnomAD v2.1.1 + GENCODE v47",
        "algorithm": {
            "tier1": "body_overlap: pLI>=0.9 OR LOEUF<=0.80",
            "tier2": "window 200kb, no strong CTCF barrier (score>=50): pLI>=0.9 OR LOEUF<=0.35",
        },
        "step0_metrics": m0,
        "step2_metrics": m2,
        "svs": annotated,
    }
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_OUT}")


if __name__ == "__main__":
    main()
