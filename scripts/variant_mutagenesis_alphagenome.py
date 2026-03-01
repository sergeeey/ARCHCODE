#!/usr/bin/env python3
"""
Variant-level AlphaGenome mutagenesis benchmark for ARCHCODE pearl variants.

ПОЧЕМУ этот скрипт:
ARCHCODE structural benchmark (benchmark_alphagenome.py) сравнивает wild-type contact maps.
Но не проверяет, видит ли AlphaGenome те же variant perturbations что и ARCHCODE.
Этот скрипт закрывает Limitation #10: для каждого pearl variant вызываем
predict_variant() → получаем WT и MUT contact maps → считаем ΔSSIM.
Если ARCHCODE ΔSSIM и AlphaGenome ΔSSIM коррелируют → independent validation.

Usage:
    python scripts/variant_mutagenesis_alphagenome.py
    python scripts/variant_mutagenesis_alphagenome.py --locus 95kb --atlas results/HBB_Unified_Atlas_95kb.csv
    python scripts/variant_mutagenesis_alphagenome.py --api-key YOUR_KEY --batch-size 5
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent


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
    print("  Provide via: --api-key KEY or ALPHAGENOME_API_KEY env var")
    sys.exit(1)


def load_pearl_variants(csv_path: str) -> list[dict]:
    """
    Load pearl variants from unified atlas CSV.

    ПОЧЕМУ pearl variants: это варианты где VEP (sequence-based) говорит 'benign'
    (score < 0.30), а ARCHCODE (structure-based) говорит 'disruptive' (SSIM < 0.95).
    Они представляют наибольший интерес: если AlphaGenome тоже видит структурное
    нарушение → это triple validation (ARCHCODE + AlphaGenome vs VEP).
    """
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
    """
    Compute SSIM between two 2D contact maps.

    ПОЧЕМУ SSIM а не просто корреляция: SSIM учитывает luminance, contrast
    и structure — три компонента восприятия. Для contact maps это означает:
    сохранились ли паттерны TAD/loop (structure), уровень контактов (luminance),
    и контраст между TAD и inter-TAD (contrast).
    """
    from skimage.metrics import structural_similarity
    # ПОЧЕМУ data_range=auto: обе карты могут быть на разных шкалах
    # после distance normalization. SSIM нормализует внутренне.
    data_range = max(ref_map.max() - ref_map.min(), alt_map.max() - alt_map.min())
    if data_range < 1e-12:
        return 1.0  # identical zero maps
    return float(structural_similarity(ref_map, alt_map, data_range=data_range))


def run_variant_mutagenesis(
    api_key: str,
    pearls: list[dict],
    chromosome: str,
    window_start: int,
    window_end: int,
    cell_line: str = "GM12878",
    batch_size: int = 5,
    batch_delay: float = 5.0,
) -> list[dict]:
    """
    Run AlphaGenome predict_variant() for each pearl variant.

    ПОЧЕМУ predict_variant а не predict_interval с edited sequence:
    predict_variant() — нативный SDK метод, оптимизированный для mutagenesis.
    Он гарантирует идентичный контекст (interval) для ref и alt,
    и возвращает VariantOutput с обоими contact maps в одном вызове.
    """
    from alphagenome.models import dna_client
    from alphagenome.models.dna_output import OutputType
    from alphagenome.data.genome import Variant, Interval

    print(f"  Creating AlphaGenome client...")
    model = dna_client.create(api_key)

    # ПОЧЕМУ выбор sequence length: берём ближайший >= window_size
    window_size = window_end - window_start
    center = (window_start + window_end) // 2
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    seq_length = next((sl for sl in supported if sl >= window_size), supported[-1])

    interval = Interval(chromosome, center - seq_length // 2, center + seq_length // 2)
    ag_interval_start = center - seq_length // 2

    print(f"  Interval: {interval} (seq_length={seq_length})")
    print(f"  Cell line: {cell_line}")
    print(f"  Variants to process: {len(pearls)}")

    results = []
    for i, pearl in enumerate(pearls):
        pos = pearl["position"]
        ref = pearl["ref"]
        alt = pearl["alt"]

        # ПОЧЕМУ skip multi-allelic: AlphaGenome Variant expects simple SNV/indel.
        # Complex structural variants or multi-allelic entries need special handling.
        if len(ref) > 50 or len(alt) > 50:
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: "
                  f"complex variant ({len(ref)}bp→{len(alt)}bp)")
            results.append({
                **pearl,
                "ag_status": "skipped_complex",
                "ag_delta_ssim": None,
            })
            continue

        # ПОЧЕМУ skip IUPAC ambiguity codes: AlphaGenome accepts only ACGTN.
        # ClinVar sometimes has Y (C/T), R (A/G), etc.
        valid_bases = set("ACGTN")
        if not all(b in valid_bases for b in ref.upper()) or not all(b in valid_bases for b in alt.upper()):
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: "
                  f"IUPAC ambiguity code ({ref}>{alt})")
            results.append({
                **pearl,
                "ag_status": "skipped_iupac",
                "ag_delta_ssim": None,
            })
            continue

        print(f"  [{i+1}/{len(pearls)}] {pearl['clinvar_id']} "
              f"{chromosome}:{pos} {ref}>{alt} (ARCHCODE SSIM={pearl['archcode_ssim']:.4f})")

        try:
            variant = Variant(chromosome, pos, ref, alt)
            output = model.predict_variant(
                interval=interval,
                variant=variant,
                requested_outputs=[OutputType.CONTACT_MAPS],
                ontology_terms=None,
            )

            # Extract contact maps for target cell line
            ref_contacts = output.reference.contact_maps
            alt_contacts = output.alternate.contact_maps

            if ref_contacts is None or alt_contacts is None:
                print(f"    WARNING: No contact maps returned")
                results.append({
                    **pearl,
                    "ag_status": "no_contact_maps",
                    "ag_delta_ssim": None,
                    "ag_ref_ssim_self": None,
                })
                continue

            # Find cell line track index
            meta_df = ref_contacts.metadata
            matches = meta_df[meta_df["biosample_name"] == cell_line]
            if matches.empty:
                # Fallback: first Hi-C track
                hic_tracks = meta_df[meta_df["Assay title"].str.contains("Hi-C", case=False)]
                if not hic_tracks.empty:
                    track_idx = hic_tracks.index[0]
                    used_cell = hic_tracks.iloc[0]["biosample_name"]
                    print(f"    WARNING: {cell_line} not found, using {used_cell}")
                else:
                    track_idx = 0
                    used_cell = meta_df.iloc[0]["biosample_name"]
                    print(f"    WARNING: No Hi-C tracks, using first track: {used_cell}")
            else:
                track_idx = matches.index[0]
                used_cell = cell_line

            ref_map = ref_contacts.values[:, :, track_idx]
            alt_map = alt_contacts.values[:, :, track_idx]
            ag_resolution = ref_contacts.resolution

            # Extract our window from the full maps
            bin_start = max(0, (window_start - ag_interval_start) // ag_resolution)
            bin_end = min(ref_map.shape[0], (window_end - ag_interval_start) // ag_resolution)

            ref_window = ref_map[bin_start:bin_end, bin_start:bin_end]
            alt_window = alt_map[bin_start:bin_end, bin_start:bin_end]

            # ПОЧЕМУ exp(): AlphaGenome contact maps в log-scale (O/E).
            # SSIM работает с линейными значениями.
            ref_linear = np.exp(ref_window)
            alt_linear = np.exp(alt_window)

            # Compute ΔSSIM
            ag_ssim = compute_ssim_2d(ref_linear, alt_linear)

            # ПОЧЕМУ delta = 1 - SSIM: ARCHCODE SSIM уже показывает близость к WT.
            # ag_ssim тоже: 1.0 = идентично, <1.0 = различие.
            # Delta = amount of disruption.
            ag_delta = 1.0 - ag_ssim

            print(f"    AG SSIM(ref,alt) = {ag_ssim:.6f}, Δ = {ag_delta:.6f}")
            print(f"    ARCHCODE SSIM = {pearl['archcode_ssim']:.4f}, "
                  f"Δ = {1.0 - pearl['archcode_ssim']:.4f}")

            results.append({
                **pearl,
                "ag_status": "success",
                "ag_ssim": float(ag_ssim),
                "ag_delta_ssim": float(ag_delta),
                "ag_contact_map_bins": int(bin_end - bin_start),
                "ag_resolution_bp": int(ag_resolution),
                "ag_cell_line_used": used_cell,
            })

        except Exception as e:
            print(f"    ERROR: {type(e).__name__}: {e}")
            results.append({
                **pearl,
                "ag_status": f"error_{type(e).__name__}",
                "ag_delta_ssim": None,
                "ag_ref_ssim_self": None,
            })

        # Rate limiting between batches
        if (i + 1) % batch_size == 0 and i + 1 < len(pearls):
            print(f"  --- Batch pause ({batch_delay}s) ---")
            time.sleep(batch_delay)

    return results


def compute_correlations(results: list[dict]) -> dict:
    """
    Compute correlation between ARCHCODE and AlphaGenome perturbation signals.

    ПОЧЕМУ два вектора Δ:
    - archcode_delta = 1 - ARCHCODE_SSIM (structural disruption по нашей модели)
    - ag_delta = 1 - AG_SSIM(ref, alt)  (structural disruption по DL модели)
    Если оба вектора коррелируют → обе модели видят те же variants как disruptive.
    """
    from scipy.stats import pearsonr, spearmanr

    # Filter successful results with valid deltas
    valid = [r for r in results if r.get("ag_status") == "success"
             and r.get("ag_delta_ssim") is not None]

    if len(valid) < 3:
        return {
            "error": f"insufficient valid variants ({len(valid)})",
            "n_valid": len(valid),
            "n_total": len(results),
        }

    archcode_deltas = np.array([1.0 - r["archcode_ssim"] for r in valid])
    ag_deltas = np.array([r["ag_delta_ssim"] for r in valid])

    # Check for zero variance (all AlphaGenome deltas identical)
    if np.std(ag_deltas) < 1e-12:
        return {
            "warning": "zero variance in AlphaGenome deltas — model may not detect variant-level signal at this resolution",
            "ag_delta_mean": float(np.mean(ag_deltas)),
            "ag_delta_std": float(np.std(ag_deltas)),
            "archcode_delta_mean": float(np.mean(archcode_deltas)),
            "archcode_delta_std": float(np.std(archcode_deltas)),
            "n_valid": len(valid),
        }

    r, p_r = pearsonr(archcode_deltas, ag_deltas)
    rho, p_rho = spearmanr(archcode_deltas, ag_deltas)

    return {
        "pearson_r": float(r),
        "pearson_p": float(p_r),
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "n_valid": len(valid),
        "n_total": len(results),
        "n_skipped": sum(1 for r in results if r.get("ag_status") == "skipped_complex"),
        "n_errors": sum(1 for r in results if r.get("ag_status", "").startswith("error")),
        "archcode_delta_range": [float(archcode_deltas.min()), float(archcode_deltas.max())],
        "ag_delta_range": [float(ag_deltas.min()), float(ag_deltas.max())],
        "archcode_delta_mean": float(np.mean(archcode_deltas)),
        "ag_delta_mean": float(np.mean(ag_deltas)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Variant-level AlphaGenome mutagenesis benchmark"
    )
    parser.add_argument(
        "--atlas",
        default="results/HBB_Unified_Atlas_95kb.csv",
        help="Path to unified atlas CSV with Pearl column (default: 95kb)",
    )
    parser.add_argument("--locus", default="95kb", help="Locus alias (default: 95kb)")
    parser.add_argument("--api-key", help="AlphaGenome API key")
    parser.add_argument(
        "--cell-line", default="GM12878",
        help="Cell line for contact maps (default: GM12878)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=5,
        help="Variants per batch before rate-limit pause (default: 5)",
    )
    parser.add_argument(
        "--batch-delay", type=float, default=5.0,
        help="Seconds to wait between batches (default: 5.0)",
    )
    parser.add_argument(
        "--output",
        help="Output JSON path (default: results/variant_mutagenesis_alphagenome_hbb.json)",
    )
    args = parser.parse_args()

    api_key = get_api_key(args)

    print("=" * 70)
    print("ARCHCODE Variant-Level AlphaGenome Mutagenesis Benchmark")
    print("=" * 70)

    # Step 1: Load locus config for genomic coordinates
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
        print("  ERROR: No pearl variants found. Check CSV Pearl column.")
        sys.exit(1)

    # Step 3: Run variant mutagenesis
    print(f"\n--- Step 3: AlphaGenome variant mutagenesis ---")
    results = run_variant_mutagenesis(
        api_key=api_key,
        pearls=pearls,
        chromosome=chrom,
        window_start=start,
        window_end=end,
        cell_line=args.cell_line,
        batch_size=args.batch_size,
        batch_delay=args.batch_delay,
    )

    # Step 4: Compute correlations
    print(f"\n--- Step 4: Correlation analysis ---")
    correlations = compute_correlations(results)

    if "error" in correlations:
        print(f"  {correlations['error']}")
    elif "warning" in correlations:
        print(f"  WARNING: {correlations['warning']}")
    else:
        print(f"  Pearson r  = {correlations['pearson_r']:.4f} (p = {correlations['pearson_p']:.4e})")
        print(f"  Spearman ρ = {correlations['spearman_rho']:.4f} (p = {correlations['spearman_p']:.4e})")
        print(f"  Valid variants: {correlations['n_valid']}/{correlations['n_total']}")

    # Step 5: Save results
    output_path = Path(args.output) if args.output else PROJECT_ROOT / "results" / "variant_mutagenesis_alphagenome_hbb.json"

    output = {
        "analysis": "variant_level_alphagenome_mutagenesis",
        "locus": args.locus,
        "locus_id": config.get("id"),
        "atlas_csv": str(atlas_path.name),
        "window": {
            "chromosome": chrom,
            "start": start,
            "end": end,
        },
        "parameters": {
            "cell_line": args.cell_line,
            "batch_size": args.batch_size,
            "sdk_version": "0.6.0",
        },
        "summary": {
            "total_pearls": len(pearls),
            "successful": sum(1 for r in results if r.get("ag_status") == "success"),
            "skipped_complex": sum(1 for r in results if r.get("ag_status") == "skipped_complex"),
            "errors": sum(1 for r in results if r.get("ag_status", "").startswith("error")),
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
    print()


if __name__ == "__main__":
    main()
