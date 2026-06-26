#!/usr/bin/env python3
"""
Step +1 analysis: apply gnomAD gene constraint filter to existing ClinVar results.
Reads clinvar_results.json (Step 0), adds HI gene annotation, computes new metrics.

Step +1 rule:
  DISRUPTED + HI gene (pLI>=0.9 or LOEUF<=0.35) within ±500kb → PATHOGENIC prediction
  DISRUPTED + no HI gene                                          → BENIGN prediction
  INTACT                                                          → BENIGN prediction
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from archcode_sv import find_hi_genes, load_gene_constraint

CLINVAR_IN = "experiments/exp_archcode_sv/clinvar_results.json"
RESULTS_OUT = "experiments/exp_archcode_sv/clinvar_step1_results.json"


def apply_step1(sv: dict, constraint: dict, genes: list[dict]) -> dict:
    """Add Step +1 verdict to an already-scored SV dict."""
    sv = dict(sv)
    step0_verdict = sv["verdict"]
    if step0_verdict == "DISRUPTED":
        hi = find_hi_genes(sv["chrom"], sv["start"], sv["end"], constraint, genes)
        sv["step1_verdict"] = "DISRUPTED_WITH_HI_GENE" if hi else "DISRUPTED_NO_HI_GENE"
        sv["hi_genes"] = hi
    else:
        sv["step1_verdict"] = "INTACT"
        sv["hi_genes"] = []
    return sv


def compute_metrics(svs: list[dict]) -> dict:
    """
    Compute TP/FN/FP/TN for Step +1 classification.
    Positive prediction: DISRUPTED_WITH_HI_GENE
    Negative prediction: DISRUPTED_NO_HI_GENE or INTACT
    """
    tp = fn = fp = tn = 0
    for sv in svs:
        is_path = sv["pathogenic"]
        pred_path = sv["step1_verdict"] == "DISRUPTED_WITH_HI_GENE"
        if is_path and pred_path:
            tp += 1
        elif is_path and not pred_path:
            fn += 1
        elif not is_path and pred_path:
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
    print(f"gnomAD: {len(constraint)} genes  |  GENCODE: {len(genes)} protein-coding on chr2/7/17")

    all_svs = data["pathogenic_svs"] + data["benign_svs"]
    annotated = [apply_step1(sv, constraint, genes) for sv in all_svs]

    # Step 0 metrics (original)
    m0 = data["metrics"]

    # Step +1 metrics
    m1 = compute_metrics(annotated)

    print("\n=== Step 0 (ARCHCODE-SV boundary disruption only) ===")
    print(f"TP={m0['TP']}  FN={m0['FN']}  FP={m0['FP']}  TN={m0['TN']}")
    print(
        f"Recall={m0['recall']:.3f}  Precision={m0.get('precision', m0.get('precision',0)):.3f}  FPR={m0['FPR']:.3f}"
    )

    print("\n=== Step +1 (+ gnomAD gene constraint filter) ===")
    print(f"TP={m1['TP']}  FN={m1['FN']}  FP={m1['FP']}  TN={m1['TN']}")
    print(f"Recall={m1['recall']:.3f}  Precision={m1['precision']:.3f}  FPR={m1['FPR']:.3f}")

    print("\n=== Delta ===")
    print(f"FPR: {m0['FPR']:.3f} → {m1['FPR']:.3f}  (Δ={m1['FPR']-m0['FPR']:+.3f})")
    print(f"Recall: {m0['recall']:.3f} → {m1['recall']:.3f}  (Δ={m1['recall']-m0['recall']:+.3f})")
    print(f"Precision: {m0.get('precision', m0.get('precision', 0)):.3f} → {m1['precision']:.3f}")

    # Per-SV breakdown of interesting cases
    print("\n=== FPs rescued by Step +1 (benign, was DISRUPTED → now DISRUPTED_NO_HI_GENE) ===")
    rescued = [
        s
        for s in annotated
        if not s["pathogenic"]
        and s["verdict"] == "DISRUPTED"
        and s["step1_verdict"] == "DISRUPTED_NO_HI_GENE"
    ]
    for s in rescued[:8]:
        print(f"  {s['chrom']}:{s['start']}-{s['end']}  ratio={s['ratio']}  no HI genes")

    print("\n=== FPs still wrong (benign, DISRUPTED_WITH_HI_GENE) ===")
    still_fp = [
        s
        for s in annotated
        if not s["pathogenic"] and s["step1_verdict"] == "DISRUPTED_WITH_HI_GENE"
    ]
    for s in still_fp:
        print(f"  {s['chrom']}:{s['start']}-{s['end']}  hi_genes={s['hi_genes'][:3]}")

    print("\n=== New FNs introduced (pathogenic, verdict → non-DISRUPTED_WITH_HI_GENE) ===")
    new_fn = [
        s for s in annotated if s["pathogenic"] and s["step1_verdict"] != "DISRUPTED_WITH_HI_GENE"
    ]
    for s in new_fn:
        print(
            f"  {s['chrom']}:{s['start']}-{s['end']}  step0={s['verdict']}  step1={s['step1_verdict']}  hi_genes={s['hi_genes'][:3]}"
        )

    # Save results
    out = {
        "source": data["source"],
        "filter": data["filter"],
        "evidence": "[VERIFIED-REAL] ClinVar + ENCODE CTCF K562 hg38 + gnomAD v2.1.1 + GENCODE v47",
        "step0_metrics": m0,
        "step1_metrics": m1,
        "svs": annotated,
    }
    with open(RESULTS_OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_OUT}")


if __name__ == "__main__":
    main()
