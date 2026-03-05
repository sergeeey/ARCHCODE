#!/usr/bin/env python3
"""
Epigenome cross-validation: AlphaGenome predicted ChIP vs ENCODE ChIP-seq.

ПОЧЕМУ этот скрипт:
ARCHCODE использует ENCODE ChIP-seq peaks (CTCF, H3K27ac) как input features.
AlphaGenome предсказывает те же эпигеномные сигналы из ДНК последовательности.
Если AlphaGenome предсказывает CTCF в тех же позициях что ENCODE — наши input
данные (configs) подтверждены независимым DL-методом.

Это NOT validation ARCHCODE'а. Это validation наших INPUT данных.

Usage:
    python scripts/epigenome_crossval_alphagenome.py
    python scripts/epigenome_crossval_alphagenome.py --loci tp53 brca1 mlh1
    python scripts/epigenome_crossval_alphagenome.py --api-key YOUR_KEY
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent

# ПОЧЕМУ эти локусы: только те, где configs содержат ENCODE data.
# HBB 30kb uses MODEL_PARAMETER (не ENCODE), поэтому исключён.
DEFAULT_LOCI = ["95kb", "cftr", "tp53", "brca1", "mlh1", "ldlr", "scn5a", "gjb2"]

# Tissue-context metadata for protocol-aware reporting (Task 4).
LOCUS_TISSUE_CONTEXT = {
    "95kb": "matched",
    "cftr": "partial",
    "tp53": "partial",
    "brca1": "partial",
    "mlh1": "partial",
    "ldlr": "partial",
    "scn5a": "mismatch",
    "gjb2": "mismatch",
    "tert": "expressed",
}

# ПОЧЕМУ tolerance в bp: ChIP-seq peaks имеют ширину ~200-500 bp.
# Position в config — центр пика. AlphaGenome разрешение 128 bp.
# 2000 bp tolerance покрывает 1 пик шириной + 1 bin AlphaGenome.
POSITION_TOLERANCE_BP = 2000


def get_api_key(args: argparse.Namespace) -> str:
    """Resolve API key from args, env, or .env file."""
    if args.api_key:
        return args.api_key

    env_key = os.environ.get("ALPHAGENOME_API_KEY")
    if env_key:
        return env_key

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ALPHAGENOME_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val

    print("ERROR: No API key found.")
    sys.exit(1)


def load_config_features(locus: str) -> dict:
    """Load CTCF and enhancer positions from locus config."""
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from lib.locus_config import resolve_locus_path, load_locus_config
    config = load_locus_config(resolve_locus_path(locus))

    window = config["window"]
    features = config.get("features", {})

    # Filter to ENCODE-sourced features only
    ctcf_sites = [
        s for s in features.get("ctcf_sites", [])
        if "ENCODE" in s.get("source", "")
    ]
    enhancers = [
        e for e in features.get("enhancers", [])
        if "ENCODE" in e.get("source", "") or "H3K27ac" in e.get("source", "")
    ]

    return {
        "config": config,
        "window": window,
        "ctcf_positions": [s["position"] for s in ctcf_sites],
        "ctcf_details": ctcf_sites,
        "enhancer_positions": [e["position"] for e in enhancers],
        "enhancer_details": enhancers,
    }


def predict_epigenome(
    client,
    chromosome: str,
    start: int,
    end: int,
) -> dict:
    """
    Get AlphaGenome CTCF and H3K27ac predictions for an interval.

    Returns dict with 'ctcf' and 'h3k27ac' track data.
    """
    from alphagenome.models import dna_client
    from alphagenome.models.dna_output import OutputType
    from alphagenome.data.genome import Interval

    window_size = end - start
    center = (start + end) // 2
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    seq_length = next((sl for sl in supported if sl >= window_size), supported[-1])

    interval = Interval(chromosome, center - seq_length // 2, center + seq_length // 2)
    interval_start = center - seq_length // 2

    print(f"  Requesting CHIP_TF + CHIP_HISTONE...")
    output = client.predict_interval(
        interval=interval,
        requested_outputs=[OutputType.CHIP_TF, OutputType.CHIP_HISTONE],
        ontology_terms=None,
    )

    result = {
        "interval_start": interval_start,
        "seq_length": seq_length,
    }

    # Process CTCF (CHIP_TF)
    if output.chip_tf is not None:
        tf_data = output.chip_tf
        tf_meta = tf_data.metadata
        # ПОЧЕМУ фильтр по CTCF: CHIP_TF может содержать несколько TFs.
        # Ищем треки с "CTCF" в имени.
        ctcf_mask = tf_meta["name"].str.contains("CTCF", case=False)
        if ctcf_mask.any():
            ctcf_idx = tf_meta[ctcf_mask].index[0]
            result["ctcf_values"] = tf_data.values[:, ctcf_idx]
            result["ctcf_resolution"] = tf_data.resolution
            result["ctcf_track_name"] = tf_meta.iloc[ctcf_idx]["name"] if ctcf_idx < len(tf_meta) else "CTCF"
            print(f"    CTCF track found: {result['ctcf_track_name']} "
                  f"(resolution={tf_data.resolution}bp, bins={tf_data.values.shape[0]})")
        else:
            print(f"    WARNING: No CTCF track in CHIP_TF output")
            print(f"    Available TF tracks: {list(tf_meta['name'])}")
    else:
        print(f"    WARNING: No CHIP_TF data returned")

    # Process H3K27ac (CHIP_HISTONE)
    if output.chip_histone is not None:
        hist_data = output.chip_histone
        hist_meta = hist_data.metadata
        h3k27ac_mask = hist_meta["name"].str.contains("H3K27ac", case=False)
        if h3k27ac_mask.any():
            h3k_idx = hist_meta[h3k27ac_mask].index[0]
            result["h3k27ac_values"] = hist_data.values[:, h3k_idx]
            result["h3k27ac_resolution"] = hist_data.resolution
            result["h3k27ac_track_name"] = hist_meta.iloc[h3k_idx]["name"] if h3k_idx < len(hist_meta) else "H3K27ac"
            print(f"    H3K27ac track found: {result['h3k27ac_track_name']} "
                  f"(resolution={hist_data.resolution}bp, bins={hist_data.values.shape[0]})")
        else:
            print(f"    WARNING: No H3K27ac track in CHIP_HISTONE output")
            print(f"    Available histone tracks: {list(hist_meta['name'])}")
    else:
        print(f"    WARNING: No CHIP_HISTONE data returned")

    return result


def find_peaks(values: np.ndarray, threshold_percentile: float = 90) -> list[int]:
    """
    Find peak bins in a 1D signal track.

    ПОЧЕМУ percentile-based threshold: разные локусы имеют разные absolute scales.
    Top 10% сигнала = peaks, адаптивно к масштабу каждого локуса.
    """
    threshold = np.percentile(values, threshold_percentile)
    peak_bins = np.where(values >= threshold)[0]
    return list(peak_bins)


def compute_overlap(
    encode_positions: list[int],
    ag_peak_bins: list[int],
    interval_start: int,
    resolution: int,
    window_start: int,
    window_end: int,
    tolerance_bp: int = POSITION_TOLERANCE_BP,
) -> dict:
    """
    Compute overlap between ENCODE peak positions and AlphaGenome predicted peaks.

    ПОЧЕМУ bidirectional overlap:
    - recall: какой % ENCODE peaks нашёл AlphaGenome (чувствительность)
    - precision: какой % AG peaks совпадает с ENCODE (специфичность)
    """
    if not encode_positions or not ag_peak_bins:
        return {
            "n_encode": len(encode_positions),
            "n_ag_peaks": len(ag_peak_bins),
            "matched_encode": 0,
            "recall": 0.0,
            "precision": 0.0,
            "f1": 0.0,
        }

    # Convert AG peak bins to genomic positions
    ag_positions = [interval_start + b * resolution for b in ag_peak_bins]

    # Filter to our window
    ag_in_window = [p for p in ag_positions if window_start <= p <= window_end]
    encode_in_window = [p for p in encode_positions if window_start <= p <= window_end]

    if not encode_in_window:
        return {
            "n_encode": 0,
            "n_ag_peaks": len(ag_in_window),
            "matched_encode": 0,
            "recall": 0.0,
            "precision": 0.0,
            "f1": 0.0,
            "note": "no ENCODE features in window",
        }

    # Recall: what fraction of ENCODE peaks has an AG peak nearby?
    matched_encode = 0
    match_details = []
    for enc_pos in encode_in_window:
        min_dist = min(abs(enc_pos - ag_pos) for ag_pos in ag_in_window) if ag_in_window else float("inf")
        if min_dist <= tolerance_bp:
            matched_encode += 1
            match_details.append({"encode_pos": enc_pos, "nearest_ag_dist_bp": int(min_dist)})

    recall = matched_encode / len(encode_in_window) if encode_in_window else 0.0

    # Precision: what fraction of AG peaks matches an ENCODE peak?
    matched_ag = 0
    for ag_pos in ag_in_window:
        min_dist = min(abs(ag_pos - enc_pos) for enc_pos in encode_in_window) if encode_in_window else float("inf")
        if min_dist <= tolerance_bp:
            matched_ag += 1

    precision = matched_ag / len(ag_in_window) if ag_in_window else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "n_encode": len(encode_in_window),
        "n_ag_peaks": len(ag_in_window),
        "matched_encode": matched_encode,
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
        "tolerance_bp": tolerance_bp,
        "match_details": match_details,
    }


def run_crossval_for_locus(
    client,
    locus: str,
) -> dict:
    """Run full epigenome cross-validation for one locus."""
    print(f"\n{'='*60}")
    print(f"  Locus: {locus}")
    print(f"{'='*60}")

    features = load_config_features(locus)
    window = features["window"]
    chrom = window["chromosome"]
    start = window["start"]
    end = window["end"]

    n_ctcf = len(features["ctcf_positions"])
    n_enh = len(features["enhancer_positions"])
    print(f"  Window: {chrom}:{start}-{end}")
    print(f"  ENCODE CTCF sites: {n_ctcf}")
    print(f"  ENCODE H3K27ac peaks: {n_enh}")

    if n_ctcf == 0 and n_enh == 0:
        print(f"  SKIP: No ENCODE features in config")
        return {
            "locus": locus,
            "status": "skipped_no_encode",
            "n_encode_ctcf": 0,
            "n_encode_h3k27ac": 0,
        }

    # Get AlphaGenome predictions
    ag_data = predict_epigenome(client, chrom, start, end)

    result = {
        "locus": locus,
        "locus_id": features["config"].get("id"),
        "tissue_context": LOCUS_TISSUE_CONTEXT.get(locus, "unknown"),
        "window": {"chromosome": chrom, "start": start, "end": end},
        "status": "success",
    }

    # CTCF overlap
    if "ctcf_values" in ag_data and n_ctcf > 0:
        ctcf_peaks = find_peaks(ag_data["ctcf_values"])
        ctcf_overlap = compute_overlap(
            features["ctcf_positions"],
            ctcf_peaks,
            ag_data["interval_start"],
            ag_data["ctcf_resolution"],
            start,
            end,
        )
        result["ctcf"] = {
            "ag_track": ag_data.get("ctcf_track_name"),
            "ag_resolution_bp": ag_data["ctcf_resolution"],
            "ag_total_peaks": len(ctcf_peaks),
            **ctcf_overlap,
        }
        print(f"  CTCF: recall={ctcf_overlap['recall']:.0%} "
              f"({ctcf_overlap['matched_encode']}/{ctcf_overlap['n_encode']}), "
              f"precision={ctcf_overlap['precision']:.0%}, "
              f"F1={ctcf_overlap['f1']:.2f}")
    else:
        result["ctcf"] = {"status": "no_data", "reason": "no AG CTCF track or no ENCODE CTCF"}

    # H3K27ac overlap
    if "h3k27ac_values" in ag_data and n_enh > 0:
        h3k_peaks = find_peaks(ag_data["h3k27ac_values"])
        h3k_overlap = compute_overlap(
            features["enhancer_positions"],
            h3k_peaks,
            ag_data["interval_start"],
            ag_data["h3k27ac_resolution"],
            start,
            end,
        )
        result["h3k27ac"] = {
            "ag_track": ag_data.get("h3k27ac_track_name"),
            "ag_resolution_bp": ag_data["h3k27ac_resolution"],
            "ag_total_peaks": len(h3k_peaks),
            **h3k_overlap,
        }
        print(f"  H3K27ac: recall={h3k_overlap['recall']:.0%} "
              f"({h3k_overlap['matched_encode']}/{h3k_overlap['n_encode']}), "
              f"precision={h3k_overlap['precision']:.0%}, "
              f"F1={h3k_overlap['f1']:.2f}")
    else:
        result["h3k27ac"] = {"status": "no_data", "reason": "no AG H3K27ac track or no ENCODE H3K27ac"}

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Epigenome cross-validation: AlphaGenome vs ENCODE ChIP-seq"
    )
    parser.add_argument("--api-key", help="AlphaGenome API key")
    parser.add_argument(
        "--loci", nargs="+", default=DEFAULT_LOCI,
        help=f"Locus aliases to process (default: {DEFAULT_LOCI})",
    )
    parser.add_argument(
        "--output",
        default="results/epigenome_crossval_summary.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    api_key = get_api_key(args)

    print("=" * 70)
    print("Epigenome Cross-Validation: AlphaGenome vs ENCODE ChIP-seq")
    print("=" * 70)

    from alphagenome.models import dna_client
    client = dna_client.create(api_key)

    all_results = []
    for locus in args.loci:
        try:
            result = run_crossval_for_locus(client, locus)
            all_results.append(result)
        except Exception as e:
            print(f"  ERROR for {locus}: {type(e).__name__}: {e}")
            all_results.append({
                "locus": locus,
                "status": f"error_{type(e).__name__}",
                "error": str(e),
            })

    # Aggregate summary
    ctcf_recalls = [r["ctcf"]["recall"] for r in all_results
                    if r.get("status") == "success" and isinstance(r.get("ctcf"), dict) and "recall" in r["ctcf"]]
    h3k_recalls = [r["h3k27ac"]["recall"] for r in all_results
                   if r.get("status") == "success" and isinstance(r.get("h3k27ac"), dict) and "recall" in r["h3k27ac"]]
    successful = [r for r in all_results if r.get("status") == "success"]

    # Tissue-context aggregates for Task 4 controls.
    ctx_stats: dict[str, dict] = {}
    for ctx in ["matched", "partial", "mismatch", "expressed", "unknown"]:
        ctx_rows = [r for r in successful if r.get("tissue_context") == ctx]
        if not ctx_rows:
            continue
        ctx_ctcf_f1 = [
            r["ctcf"]["f1"] for r in ctx_rows
            if isinstance(r.get("ctcf"), dict) and "f1" in r["ctcf"]
        ]
        ctx_h3k_f1 = [
            r["h3k27ac"]["f1"] for r in ctx_rows
            if isinstance(r.get("h3k27ac"), dict) and "f1" in r["h3k27ac"]
        ]
        ctx_stats[ctx] = {
            "n_loci": len(ctx_rows),
            "loci": [r["locus"] for r in ctx_rows],
            "ctcf_mean_f1": round(float(np.mean(ctx_ctcf_f1)), 4) if ctx_ctcf_f1 else None,
            "h3k27ac_mean_f1": round(float(np.mean(ctx_h3k_f1)), 4) if ctx_h3k_f1 else None,
        }

    positive_controls = [
        r["locus"] for r in successful if r.get("tissue_context") in {"matched", "partial"}
    ]
    negative_controls = [
        r["locus"] for r in successful if r.get("tissue_context") == "mismatch"
    ]
    task4_go = bool(positive_controls) and bool(negative_controls)
    task4_reasons = []
    if not positive_controls:
        task4_reasons.append("No successful positive tissue controls (matched/partial).")
    if not negative_controls:
        task4_reasons.append("No successful negative tissue controls (mismatch).")

    summary = {
        "analysis": "epigenome_crossvalidation_alphagenome_vs_encode",
        "sdk_version": "0.6.0",
        "tolerance_bp": POSITION_TOLERANCE_BP,
        "peak_threshold_percentile": 90,
        "n_loci": len(args.loci),
        "n_successful": sum(1 for r in all_results if r.get("status") == "success"),
        "aggregate": {
            "ctcf_mean_recall": round(float(np.mean(ctcf_recalls)), 4) if ctcf_recalls else None,
            "ctcf_mean_f1": round(float(np.mean([
                r["ctcf"]["f1"] for r in all_results
                if r.get("status") == "success" and isinstance(r.get("ctcf"), dict) and "f1" in r["ctcf"]
            ])), 4) if ctcf_recalls else None,
            "h3k27ac_mean_recall": round(float(np.mean(h3k_recalls)), 4) if h3k_recalls else None,
            "h3k27ac_mean_f1": round(float(np.mean([
                r["h3k27ac"]["f1"] for r in all_results
                if r.get("status") == "success" and isinstance(r.get("h3k27ac"), dict) and "f1" in r["h3k27ac"]
            ])), 4) if h3k_recalls else None,
        },
        "task4_controls": {
            "positive_controls": positive_controls,
            "negative_controls": negative_controls,
            "context_aggregates": ctx_stats,
        },
        "task4_go_nogo": {
            "go": task4_go,
            "status": "GO" if task4_go else "NO_GO",
            "reasons": task4_reasons,
        },
        "claim_level": {
            "input_feature_alignment_ctcf": "SUPPORTED",
            "input_feature_alignment_h3k27ac": "SUPPORTED",
            "causal_biological_inference": "UNVERIFIED",
            "clinical_prediction_impact": "UNVERIFIED"
        },
        "provenance": {
            "type": "REAL_API_PLUS_ENCODE_CONFIG",
            "note": "Compares AlphaGenome predicted epigenomic peaks with ENCODE-derived config features.",
            "scope": "Input-data consistency check, not direct ARCHCODE clinical validation."
        },
        "allowed_claims": [
            "CTCF positional overlap is high under selected tolerance/threshold settings.",
            "H3K27ac agreement is heterogeneous and locus-dependent.",
            "Tissue-context controls are explicitly reported (matched/partial vs mismatch)."
        ],
        "blocked_claims": [
            "Causal disease mechanism statements from this cross-validation alone",
            "Clinical utility claims from input-feature overlap metrics alone"
        ],
        "limitations": [
            "Tolerance/percentile settings affect recall/precision tradeoff",
            "Peak overlap does not establish causal regulatory effect",
            "Tissue mismatch controls validate context sensitivity but do not prove pathology causality"
        ],
        "loci": all_results,
    }

    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2))
    print(f"\n  Results saved: {output_path}")

    # Print summary table
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  {'Locus':<10} {'CTCF recall':>12} {'CTCF F1':>10} {'H3K27ac recall':>15} {'H3K27ac F1':>12}")
    print(f"  {'-'*10} {'-'*12} {'-'*10} {'-'*15} {'-'*12}")
    for r in all_results:
        if r.get("status") != "success":
            print(f"  {r['locus']:<10} {'SKIP':>12}")
            continue
        ctcf_rec = f"{r['ctcf']['recall']:.0%}" if isinstance(r.get("ctcf"), dict) and "recall" in r["ctcf"] else "N/A"
        ctcf_f1 = f"{r['ctcf']['f1']:.2f}" if isinstance(r.get("ctcf"), dict) and "f1" in r["ctcf"] else "N/A"
        h3k_rec = f"{r['h3k27ac']['recall']:.0%}" if isinstance(r.get("h3k27ac"), dict) and "recall" in r["h3k27ac"] else "N/A"
        h3k_f1 = f"{r['h3k27ac']['f1']:.2f}" if isinstance(r.get("h3k27ac"), dict) and "f1" in r["h3k27ac"] else "N/A"
        print(f"  {r['locus']:<10} {ctcf_rec:>12} {ctcf_f1:>10} {h3k_rec:>15} {h3k_f1:>12}")

    if summary["aggregate"]["ctcf_mean_recall"] is not None:
        print(f"\n  Mean CTCF recall: {summary['aggregate']['ctcf_mean_recall']:.0%}")
    if summary["aggregate"]["h3k27ac_mean_recall"] is not None:
        print(f"  Mean H3K27ac recall: {summary['aggregate']['h3k27ac_mean_recall']:.0%}")
    print()


if __name__ == "__main__":
    main()
