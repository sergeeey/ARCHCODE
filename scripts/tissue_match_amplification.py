"""
Tissue-Match Amplification Analysis

Compares tissue-matched vs K562-only ARCHCODE results for multiple loci.
Produces systematic table showing amplification effect.

Output:
  - analysis/tissue_match_amplification.json
  - figures/taxonomy/fig_tissue_match_amplification.pdf/png
"""

import json
import logging
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent


def load_atlas(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize label column
    if "Label" in df.columns:
        df["label"] = df["Label"].map({"Pathogenic": "P", "Benign": "B"})
    elif "ClinVar_Significance" in df.columns:
        df["label"] = df["ClinVar_Significance"].apply(
            lambda x: "P" if "athogenic" in str(x) else "B" if "enign" in str(x) else "?"
        )
    return df


def compute_metrics(df: pd.DataFrame, lssim_col: str = "ARCHCODE_LSSIM") -> dict:
    if lssim_col not in df.columns:
        return {"error": f"Column {lssim_col} not found"}

    path_df = df[df["label"] == "P"]
    ben_df = df[df["label"] == "B"]

    path_mean = path_df[lssim_col].mean() if len(path_df) > 0 else None
    ben_mean = ben_df[lssim_col].mean() if len(ben_df) > 0 else None
    delta = path_mean - ben_mean if path_mean is not None and ben_mean is not None else None

    # Structural calls: LSSIM < 0.95 for pathogenic
    struct_calls = int((path_df[lssim_col] < 0.95).sum()) if len(path_df) > 0 else 0

    # Q2 variants: LSSIM < 0.95 across all
    q2_total = int((df[lssim_col] < 0.95).sum())

    return {
        "n_total": len(df),
        "n_path": len(path_df),
        "n_ben": len(ben_df),
        "mean_lssim_path": round(path_mean, 6) if path_mean else None,
        "mean_lssim_ben": round(ben_mean, 6) if ben_mean else None,
        "delta_pb": round(delta, 6) if delta else None,
        "structural_calls": struct_calls,
        "q2_variants": q2_total,
    }


def main():
    comparisons = []

    # === HBB: K562 IS tissue-matched (erythroid), no K562-only baseline exists ===
    # HBB is the reference — included for context only
    hbb_path = ROOT / "results" / "HBB_Unified_Atlas_95kb.csv"
    if hbb_path.exists():
        hbb = load_atlas(hbb_path)
        hbb_metrics = compute_metrics(hbb)
        comparisons.append(
            {
                "locus": "HBB",
                "tissue_matched": "K562 (erythroid = matched)",
                "k562_only": "N/A (K562 IS tissue-matched)",
                "matched_metrics": hbb_metrics,
                "k562_metrics": None,
                "amplification": None,
                "note": "Reference locus. K562 erythroid is the correct tissue for HBB.",
            }
        )
        log.info(
            f"HBB: delta={hbb_metrics['delta_pb']}, struct_calls={hbb_metrics['structural_calls']}"
        )

    # === SCN5A: K562 vs Cardiac ===
    scn5a_k562 = ROOT / "results" / "SCN5A_Unified_Atlas_400kb.csv"
    scn5a_cardiac = ROOT / "results" / "SCN5A_Unified_Atlas_250kb.csv"
    if scn5a_k562.exists() and scn5a_cardiac.exists():
        k562_df = load_atlas(scn5a_k562)
        cardiac_df = load_atlas(scn5a_cardiac)
        k562_m = compute_metrics(k562_df)
        cardiac_m = compute_metrics(cardiac_df)
        amp_delta = (
            cardiac_m["delta_pb"] / k562_m["delta_pb"]
            if k562_m["delta_pb"] and k562_m["delta_pb"] != 0
            else None
        )
        amp_struct = (
            cardiac_m["structural_calls"] / k562_m["structural_calls"]
            if k562_m["structural_calls"] > 0
            else None
        )
        comparisons.append(
            {
                "locus": "SCN5A",
                "tissue_matched": "Cardiac (ENCSR000NPF + ENCSR713SXF)",
                "k562_only": "K562 (erythroid, mismatched)",
                "matched_metrics": cardiac_m,
                "k562_metrics": k562_m,
                "amplification": {
                    "delta_ratio": round(amp_delta, 2) if amp_delta else None,
                    "struct_ratio": round(amp_struct, 2) if amp_struct else None,
                },
                "note": "Class E→B partial conversion confirmed.",
            }
        )
        log.info(
            f"SCN5A: K562 delta={k562_m['delta_pb']}, cardiac delta={cardiac_m['delta_pb']}, "
            f"amp={amp_delta:.2f}x"
            if amp_delta
            else "SCN5A: amp=N/A"
        )

    # === LDLR: HepG2 (tissue-matched) vs K562 ===
    ldlr_matched = ROOT / "results" / "LDLR_Unified_Atlas_300kb.csv"
    ldlr_k562 = ROOT / "results" / "LDLR_Unified_Atlas_300kb_K562.csv"
    if ldlr_matched.exists() and ldlr_k562.exists():
        matched_df = load_atlas(ldlr_matched)
        k562_df = load_atlas(ldlr_k562)
        matched_m = compute_metrics(matched_df)
        k562_m = compute_metrics(k562_df)
        amp_delta = (
            matched_m["delta_pb"] / k562_m["delta_pb"]
            if k562_m["delta_pb"] and k562_m["delta_pb"] != 0
            else None
        )
        amp_struct = (
            matched_m["structural_calls"] / k562_m["structural_calls"]
            if k562_m["structural_calls"] > 0
            else None
        )
        comparisons.append(
            {
                "locus": "LDLR",
                "tissue_matched": "HepG2 (liver, ENCFF012ADZ + ENCFF205OKL)",
                "k562_only": "K562 (erythroid, mismatched)",
                "matched_metrics": matched_m,
                "k562_metrics": k562_m,
                "amplification": {
                    "delta_ratio": round(amp_delta, 2) if amp_delta else None,
                    "struct_ratio": round(amp_struct, 2) if amp_struct else None,
                },
                "note": "LDLR is primarily expressed in hepatocytes (SREBP regulation).",
            }
        )
        log.info(
            f"LDLR: HepG2 delta={matched_m['delta_pb']}, K562 delta={k562_m['delta_pb']}, "
            f"amp={amp_delta:.2f}x"
            if amp_delta
            else "LDLR: amp=N/A"
        )

    # === BRCA1: MCF7 (tissue-matched) vs K562 ===
    brca1_matched = ROOT / "results" / "BRCA1_Unified_Atlas_400kb.csv"
    brca1_k562 = ROOT / "results" / "BRCA1_Unified_Atlas_400kb_K562.csv"
    if brca1_matched.exists() and brca1_k562.exists():
        matched_df = load_atlas(brca1_matched)
        k562_df = load_atlas(brca1_k562)
        matched_m = compute_metrics(matched_df)
        k562_m = compute_metrics(k562_df)
        amp_delta = (
            matched_m["delta_pb"] / k562_m["delta_pb"]
            if k562_m["delta_pb"] and k562_m["delta_pb"] != 0
            else None
        )
        amp_struct = (
            matched_m["structural_calls"] / k562_m["structural_calls"]
            if k562_m["structural_calls"] > 0
            else None
        )
        comparisons.append(
            {
                "locus": "BRCA1",
                "tissue_matched": "MCF7 (breast, ENCFF340KSH + ENCFF163JHE)",
                "k562_only": "K562 (erythroid, mismatched)",
                "matched_metrics": matched_m,
                "k562_metrics": k562_m,
                "amplification": {
                    "delta_ratio": round(amp_delta, 2) if amp_delta else None,
                    "struct_ratio": round(amp_struct, 2) if amp_struct else None,
                },
                "note": "BRCA1 is expressed in breast tissue; MCF7 is breast cancer cell line.",
            }
        )
        log.info(
            f"BRCA1: MCF7 delta={matched_m['delta_pb']}, K562 delta={k562_m['delta_pb']}, "
            f"amp={amp_delta:.2f}x"
            if amp_delta
            else "BRCA1: amp=N/A"
        )

    # === Summary ===
    result = {
        "analysis": "tissue_match_amplification",
        "description": "Systematic comparison of tissue-matched vs K562-only ARCHCODE results",
        "comparisons": comparisons,
    }

    out_json = ROOT / "analysis" / "tissue_match_amplification.json"
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    log.info(f"JSON saved: {out_json}")

    # === Figure ===
    loci_with_comparison = [c for c in comparisons if c["k562_metrics"] is not None]

    if len(loci_with_comparison) >= 2:
        fig, axes = plt.subplots(1, 3, figsize=(14, 5))

        locus_names = [c["locus"] for c in loci_with_comparison]
        x = np.arange(len(locus_names))
        w = 0.35

        # Panel A: Delta P-B
        matched_deltas = [abs(c["matched_metrics"]["delta_pb"] or 0) for c in loci_with_comparison]
        k562_deltas = [abs(c["k562_metrics"]["delta_pb"] or 0) for c in loci_with_comparison]
        axes[0].bar(
            x - w / 2, matched_deltas, w, label="Tissue-matched", color="#2ca02c", alpha=0.8
        )
        axes[0].bar(x + w / 2, k562_deltas, w, label="K562-only", color="#d62728", alpha=0.8)
        axes[0].set_ylabel("|Δ LSSIM| (P − B)")
        axes[0].set_title("A. Pathogenic–Benign Separation")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(locus_names)
        axes[0].legend(fontsize=8)

        # Panel B: Structural calls
        matched_struct = [c["matched_metrics"]["structural_calls"] for c in loci_with_comparison]
        k562_struct = [c["k562_metrics"]["structural_calls"] for c in loci_with_comparison]
        axes[1].bar(
            x - w / 2, matched_struct, w, label="Tissue-matched", color="#2ca02c", alpha=0.8
        )
        axes[1].bar(x + w / 2, k562_struct, w, label="K562-only", color="#d62728", alpha=0.8)
        axes[1].set_ylabel("Structural calls (LSSIM < 0.95)")
        axes[1].set_title("B. Structural Variant Calls")
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(locus_names)
        axes[1].legend(fontsize=8)

        # Panel C: Amplification ratios
        amp_deltas = [c["amplification"]["delta_ratio"] or 0 for c in loci_with_comparison]
        amp_structs = [c["amplification"]["struct_ratio"] or 0 for c in loci_with_comparison]
        axes[2].bar(x - w / 2, amp_deltas, w, label="Delta ratio", color="#1f77b4", alpha=0.8)
        axes[2].bar(x + w / 2, amp_structs, w, label="Struct ratio", color="#ff7f0e", alpha=0.8)
        axes[2].axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="No change")
        axes[2].set_ylabel("Amplification ratio (matched / K562)")
        axes[2].set_title("C. Tissue-Match Amplification")
        axes[2].set_xticks(x)
        axes[2].set_xticklabels(locus_names)
        axes[2].legend(fontsize=8)

        plt.tight_layout()
        fig_pdf = ROOT / "figures" / "taxonomy" / "fig_tissue_match_amplification.pdf"
        fig_png = ROOT / "figures" / "taxonomy" / "fig_tissue_match_amplification.png"
        plt.savefig(fig_pdf, bbox_inches="tight")
        plt.savefig(fig_png, dpi=150, bbox_inches="tight")
        plt.close()
        log.info(f"Figure saved: {fig_pdf}")

    # Print summary table
    print("\n" + "=" * 70)
    print("TISSUE-MATCH AMPLIFICATION — SUMMARY")
    print("=" * 70)
    for c in comparisons:
        print(f"\n  {c['locus']}:")
        m = c["matched_metrics"]
        print(
            f"    Tissue-matched: delta={m['delta_pb']}, struct_calls={m['structural_calls']}, Q2={m['q2_variants']}"
        )
        if c["k562_metrics"]:
            k = c["k562_metrics"]
            print(
                f"    K562-only:      delta={k['delta_pb']}, struct_calls={k['structural_calls']}, Q2={k['q2_variants']}"
            )
            if c["amplification"]:
                a = c["amplification"]
                print(f"    Amplification:  delta {a['delta_ratio']}x, struct {a['struct_ratio']}x")
        else:
            print(f"    K562-only:      N/A ({c['note']})")
    print("=" * 70)


if __name__ == "__main__":
    main()
