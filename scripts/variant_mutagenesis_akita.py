#!/usr/bin/env python3
"""
Variant-level Akita mutagenesis benchmark for ARCHCODE pearl variants.

ПОЧЕМУ этот скрипт:
AlphaGenome predict_variant() дал null result (ΔSSIM ~49× < ARCHCODE, r=0.06 ns).
Akita — второй независимый DL бенчмарк с тем же 2048bp resolution.
Если Akita тоже даёт null → два DL models подтверждают: ARCHCODE имеет
уникальную variant-level sensitivity на 2048bp resolution.

ПОЧЕМУ ref/alt mutagenesis: Akita не имеет predict_variant() API.
Вместо этого: предсказываем ref sequence → мутируем → предсказываем alt sequence →
считаем ΔSSIM(ref_map, alt_map).

Usage:
    python scripts/variant_mutagenesis_akita.py
    python scripts/variant_mutagenesis_akita.py --locus 95kb --atlas results/HBB_Unified_Atlas_95kb.csv
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

PROJECT_ROOT = Path(__file__).parent.parent

# Reuse constants from benchmark_akita
AKITA_SEQ_LENGTH = 1_048_576
AKITA_OUTPUT_SIZE = 448
AKITA_DIAG_OFFSET = 2
AKITA_RESOLUTION = 2048
AKITA_TARGETS = {
    "HFF": 0,
    "H1-hESC": 1,
    "GM12878": 2,
    "IMR-90": 3,
    "HCT-116": 4,
}


def load_pearl_variants(csv_path: str) -> list[dict]:
    """Load pearl variants from unified atlas CSV."""
    pearls = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Pearl", "").lower() == "true":
                pearls.append({
                    "clinvar_id": row["ClinVar_ID"],
                    "position": int(row["Position_GRCh38"]),
                    "ref": row["Ref"],
                    "alt": row["Alt"],
                    "category": row.get("Category", ""),
                    "archcode_ssim": float(row["ARCHCODE_SSIM"]),
                    "archcode_lssim": float(row.get("ARCHCODE_LSSIM", row["ARCHCODE_SSIM"])),
                    "vep_score": float(row.get("VEP_Score", 0)),
                    "hgvs_c": row.get("HGVS_c", ""),
                })
    return pearls


def compute_ssim_2d(ref_map: np.ndarray, alt_map: np.ndarray) -> float:
    """Compute SSIM between two 2D contact maps."""
    from skimage.metrics import structural_similarity
    data_range = max(ref_map.max() - ref_map.min(), alt_map.max() - alt_map.min())
    if data_range < 1e-12:
        return 1.0
    return float(structural_similarity(ref_map, alt_map, data_range=data_range))


def fetch_sequence(chrom: str, start: int, end: int) -> str:
    """Fetch reference sequence from Ensembl REST API (with caching)."""
    import urllib.request

    cache_dir = PROJECT_ROOT / "data" / "reference_sequences"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{chrom}_{start}_{end}.txt"

    if cache_path.exists():
        seq = cache_path.read_text().strip()
        if len(seq) == end - start:
            return seq

    chrom_num = chrom.replace("chr", "")
    url = f"https://rest.ensembl.org/sequence/region/human/{chrom_num}:{start}..{end - 1}:1"
    headers = {"Content-Type": "text/plain"}

    print(f"  Fetching {chrom}:{start}-{end} from Ensembl...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        seq = response.read().decode("utf-8").strip()

    if len(seq) != end - start:
        raise RuntimeError(f"Ensembl returned {len(seq)} bp, expected {end - start}")

    cache_path.write_text(seq)
    return seq


def upper_tri_to_2d(ut_vector: np.ndarray, n: int = 448, offset: int = 2) -> np.ndarray:
    """Reconstruct 2D symmetric matrix from upper triangle vector."""
    mat = np.zeros((n, n))
    triu_idx = np.triu_indices(n, k=offset)
    mat[triu_idx] = ut_vector
    mat += mat.T
    return mat


def load_akita_model():
    """Load Akita model from local weights."""
    sys.path.insert(0, str(PROJECT_ROOT / "external" / "basenji"))
    from basenji import seqnn

    params_path = PROJECT_ROOT / "data" / "models" / "akita" / "params.json"
    weights_path = PROJECT_ROOT / "data" / "models" / "akita" / "model_best.h5"

    with open(params_path) as f:
        params = json.load(f)

    print("  Building Akita model...")
    model = seqnn.SeqNN(params["model"])
    model.restore(str(weights_path))
    print(f"  Model loaded: {model.model.output_shape}")
    return model


def predict_and_extract(
    model,
    sequence: str,
    target_idx: int,
    interval_start: int,
    window_start: int,
    window_end: int,
) -> np.ndarray:
    """
    Predict contact map and extract locus window.

    Returns: extracted window in linear scale (exp of log₂(O/E)).
    """
    sys.path.insert(0, str(PROJECT_ROOT / "external" / "basenji"))
    from basenji import dna_io

    seq_1hot = dna_io.dna_1hot(sequence)
    pred = model.model.predict(seq_1hot[np.newaxis], verbose=0)
    ut_vector = pred[0, :, target_idx]
    full_map = upper_tri_to_2d(ut_vector)

    # Extract locus window
    bin_start = max(0, (window_start - interval_start) // AKITA_RESOLUTION)
    bin_end = min(full_map.shape[0], (window_end - interval_start) // AKITA_RESOLUTION)
    window = full_map[bin_start:bin_end, bin_start:bin_end]

    # ПОЧЕМУ exp: Akita output в log-scale, SSIM работает в linear scale
    return np.exp(window)


def mutate_sequence(ref_seq: str, variant_pos: int, seq_start: int, ref: str, alt: str) -> str:
    """
    Create alternate sequence by substituting variant.

    ПОЧЕМУ простая замена: для SNVs и коротких indels — прямая замена подстроки.
    Длина может измениться (indels), но Akita принимает фиксированные 1Mb.
    Для коротких indels разница < 50bp на 1Mb — пренебрежимо мало.
    """
    offset = variant_pos - seq_start
    if offset < 0 or offset >= len(ref_seq):
        raise ValueError(f"Variant position {variant_pos} outside sequence [{seq_start}, {seq_start + len(ref_seq)})")

    # Verify ref allele matches
    actual_ref = ref_seq[offset:offset + len(ref)]
    if actual_ref.upper() != ref.upper():
        print(f"    WARNING: ref mismatch at {variant_pos}: expected {ref}, got {actual_ref}")

    alt_seq = ref_seq[:offset] + alt + ref_seq[offset + len(ref):]

    # ПОЧЕМУ trim/pad: indels change sequence length, but Akita needs exactly 1Mb.
    # Trim or pad to maintain 1Mb input.
    if len(alt_seq) > AKITA_SEQ_LENGTH:
        alt_seq = alt_seq[:AKITA_SEQ_LENGTH]
    elif len(alt_seq) < AKITA_SEQ_LENGTH:
        # Pad with N at the end (won't affect central region)
        alt_seq = alt_seq + "N" * (AKITA_SEQ_LENGTH - len(alt_seq))

    return alt_seq


def compute_correlations(results: list[dict]) -> dict:
    """Compute correlation between ARCHCODE and Akita perturbation signals."""
    from scipy.stats import pearsonr, spearmanr

    valid = [r for r in results if r.get("akita_status") == "success"
             and r.get("akita_delta_ssim") is not None]

    if len(valid) < 3:
        return {
            "error": f"insufficient valid variants ({len(valid)})",
            "n_valid": len(valid),
            "n_total": len(results),
        }

    archcode_deltas = np.array([1.0 - r["archcode_ssim"] for r in valid])
    akita_deltas = np.array([r["akita_delta_ssim"] for r in valid])

    if np.std(akita_deltas) < 1e-12:
        return {
            "warning": "zero variance in Akita deltas — model does not detect variant-level signal at 2048bp resolution",
            "akita_delta_mean": float(np.mean(akita_deltas)),
            "akita_delta_std": float(np.std(akita_deltas)),
            "archcode_delta_mean": float(np.mean(archcode_deltas)),
            "archcode_delta_std": float(np.std(archcode_deltas)),
            "n_valid": len(valid),
        }

    r, p_r = pearsonr(archcode_deltas, akita_deltas)
    rho, p_rho = spearmanr(archcode_deltas, akita_deltas)

    return {
        "pearson_r": float(r),
        "pearson_p": float(p_r),
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "n_valid": len(valid),
        "n_total": len(results),
        "n_skipped": sum(1 for r in results if "skipped" in r.get("akita_status", "")),
        "n_errors": sum(1 for r in results if r.get("akita_status", "").startswith("error")),
        "archcode_delta_range": [float(archcode_deltas.min()), float(archcode_deltas.max())],
        "akita_delta_range": [float(akita_deltas.min()), float(akita_deltas.max())],
        "archcode_delta_mean": float(np.mean(archcode_deltas)),
        "akita_delta_mean": float(np.mean(akita_deltas)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Variant-level Akita mutagenesis benchmark"
    )
    parser.add_argument(
        "--atlas", default="results/HBB_Unified_Atlas_95kb.csv",
        help="Path to unified atlas CSV with Pearl column (default: 95kb)",
    )
    parser.add_argument("--locus", default="95kb", help="Locus alias (default: 95kb)")
    parser.add_argument(
        "--cell-type", default="GM12878",
        help="Cell type for contact maps (default: GM12878)",
    )
    parser.add_argument(
        "--output",
        help="Output JSON path (default: results/variant_mutagenesis_akita_hbb.json)",
    )
    args = parser.parse_args()

    target_idx = AKITA_TARGETS.get(args.cell_type)
    if target_idx is None:
        print(f"ERROR: Unknown cell type: {args.cell_type}")
        sys.exit(1)

    print("=" * 70)
    print("ARCHCODE Variant-Level Akita Mutagenesis Benchmark")
    print("=" * 70)

    # Step 1: Load locus config
    print(f"\n--- Step 1: Load locus config ({args.locus}) ---")
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from lib.locus_config import resolve_locus_path, load_locus_config
    config = load_locus_config(resolve_locus_path(args.locus))
    window = config["window"]
    chrom = window["chromosome"]
    start = window["start"]
    end = window["end"]
    print(f"  {chrom}:{start}-{end}")

    # Step 2: Load pearl variants
    atlas_path = PROJECT_ROOT / args.atlas
    print(f"\n--- Step 2: Load pearl variants ({atlas_path.name}) ---")
    pearls = load_pearl_variants(str(atlas_path))
    print(f"  Found {len(pearls)} pearl variants")
    if not pearls:
        print("  ERROR: No pearl variants found.")
        sys.exit(1)

    # Step 3: Load model
    print(f"\n--- Step 3: Load Akita model ---")
    model = load_akita_model()

    # Step 4: Fetch reference sequence (cached)
    print(f"\n--- Step 4: Fetch reference 1Mb sequence ---")
    center = (start + end) // 2
    seq_start = center - AKITA_SEQ_LENGTH // 2
    seq_end = center + AKITA_SEQ_LENGTH // 2
    ref_sequence = fetch_sequence(chrom, seq_start, seq_end)
    print(f"  Reference: {len(ref_sequence)} bp ({chrom}:{seq_start}-{seq_end})")

    # Step 5: Predict reference contact map (once — reuse for all variants)
    print(f"\n--- Step 5: Reference prediction ---")
    t0 = time.time()
    ref_map = predict_and_extract(
        model, ref_sequence, target_idx, seq_start, start, end
    )
    print(f"  Ref map shape: {ref_map.shape}, time: {time.time() - t0:.1f}s")

    # Step 6: Variant mutagenesis
    print(f"\n--- Step 6: Variant mutagenesis ({len(pearls)} variants) ---")
    results = []
    valid_bases = set("ACGTN")

    for i, pearl in enumerate(pearls):
        pos = pearl["position"]
        ref = pearl["ref"]
        alt = pearl["alt"]

        # Skip complex variants
        if len(ref) > 50 or len(alt) > 50:
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: "
                  f"complex variant ({len(ref)}bp→{len(alt)}bp)")
            results.append({**pearl, "akita_status": "skipped_complex", "akita_delta_ssim": None})
            continue

        # Skip IUPAC ambiguity codes
        if not all(b in valid_bases for b in ref.upper()) or not all(b in valid_bases for b in alt.upper()):
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: IUPAC ({ref}>{alt})")
            results.append({**pearl, "akita_status": "skipped_iupac", "akita_delta_ssim": None})
            continue

        # Check variant is within 1Mb window
        if pos < seq_start or pos >= seq_end:
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: outside 1Mb window")
            results.append({**pearl, "akita_status": "skipped_outside", "akita_delta_ssim": None})
            continue

        print(f"  [{i+1}/{len(pearls)}] {pearl['clinvar_id']} "
              f"{chrom}:{pos} {ref}>{alt} (ARCHCODE SSIM={pearl['archcode_ssim']:.4f})")

        try:
            # Create alternate sequence
            alt_sequence = mutate_sequence(ref_sequence, pos, seq_start, ref, alt)

            # Predict alternate contact map
            t0 = time.time()
            alt_map = predict_and_extract(
                model, alt_sequence, target_idx, seq_start, start, end
            )
            pred_time = time.time() - t0

            # Compute ΔSSIM
            akita_ssim = compute_ssim_2d(ref_map, alt_map)
            akita_delta = 1.0 - akita_ssim

            print(f"    Akita SSIM(ref,alt) = {akita_ssim:.6f}, Δ = {akita_delta:.6f} "
                  f"({pred_time:.1f}s)")
            print(f"    ARCHCODE SSIM = {pearl['archcode_ssim']:.4f}, "
                  f"Δ = {1.0 - pearl['archcode_ssim']:.4f}")

            results.append({
                **pearl,
                "akita_status": "success",
                "akita_ssim": float(akita_ssim),
                "akita_delta_ssim": float(akita_delta),
                "akita_map_bins": int(ref_map.shape[0]),
                "akita_resolution_bp": AKITA_RESOLUTION,
                "akita_cell_type": args.cell_type,
                "akita_prediction_time_sec": round(pred_time, 1),
            })

        except Exception as e:
            print(f"    ERROR: {type(e).__name__}: {e}")
            results.append({
                **pearl,
                "akita_status": f"error_{type(e).__name__}",
                "akita_delta_ssim": None,
            })

    # Step 7: Correlation analysis
    print(f"\n--- Step 7: Correlation analysis ---")
    correlations = compute_correlations(results)

    if "error" in correlations:
        print(f"  {correlations['error']}")
    elif "warning" in correlations:
        print(f"  WARNING: {correlations['warning']}")
    else:
        print(f"  Pearson r  = {correlations['pearson_r']:.4f} (p = {correlations['pearson_p']:.4e})")
        print(f"  Spearman ρ = {correlations['spearman_rho']:.4f} (p = {correlations['spearman_p']:.4e})")
        print(f"  Valid variants: {correlations['n_valid']}/{correlations['n_total']}")

    # Step 8: Save results
    output_path = Path(args.output) if args.output else PROJECT_ROOT / "results" / "variant_mutagenesis_akita_hbb.json"

    output = {
        "analysis": "variant_level_akita_mutagenesis",
        "locus": args.locus,
        "locus_id": config.get("id"),
        "atlas_csv": str(atlas_path.name),
        "window": {
            "chromosome": chrom,
            "start": start,
            "end": end,
        },
        "parameters": {
            "cell_type": args.cell_type,
            "target_index": target_idx,
            "framework": "basenji",
            "model_file": "model_best.h5",
            "reference": "Fudenberg et al. 2020, Nature Methods",
        },
        "summary": {
            "total_pearls": len(pearls),
            "successful": sum(1 for r in results if r.get("akita_status") == "success"),
            "skipped_complex": sum(1 for r in results if r.get("akita_status") == "skipped_complex"),
            "skipped_iupac": sum(1 for r in results if r.get("akita_status") == "skipped_iupac"),
            "skipped_outside": sum(1 for r in results if r.get("akita_status") == "skipped_outside"),
            "errors": sum(1 for r in results if r.get("akita_status", "").startswith("error")),
        },
        "correlations": correlations,
        "variants": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\n  Results saved: {output_path}")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Pearl variants:   {len(pearls)}")
    print(f"  Successfully run: {output['summary']['successful']}")
    if "pearson_r" in correlations:
        print(f"  Pearson r:        {correlations['pearson_r']:.4f}")
        print(f"  Spearman ρ:       {correlations['spearman_rho']:.4f}")
    elif "warning" in correlations:
        print(f"  Result:           {correlations['warning']}")
    valid = [r for r in results if r.get("akita_status") == "success"]
    if valid:
        deltas = [r["akita_delta_ssim"] for r in valid]
        print(f"  Akita ΔSSIM:      mean={np.mean(deltas):.6f}, range=[{min(deltas):.6f}, {max(deltas):.6f}]")
        arch_deltas = [1.0 - r["archcode_ssim"] for r in valid]
        print(f"  ARCHCODE Δ:       mean={np.mean(arch_deltas):.6f}, range=[{min(arch_deltas):.6f}, {max(arch_deltas):.6f}]")
        if np.mean(arch_deltas) > 0:
            ratio = np.mean(arch_deltas) / max(np.mean(deltas), 1e-12)
            print(f"  ARCHCODE/Akita:   ~{ratio:.0f}× difference")
    print()


if __name__ == "__main__":
    main()
