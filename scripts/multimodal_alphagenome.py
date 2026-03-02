#!/usr/bin/env python3
"""
Multimodal AlphaGenome validation: RNA_SEQ + ATAC for pearl variants.

ПОЧЕМУ этот скрипт:
Contact maps (2048bp resolution) дают null на variant-level (ΔSSIM < 10⁻⁴).
Но RNA_SEQ и ATAC предсказываются AlphaGenome с разрешением **1bp** —
в 2048× выше. При 1bp resolution каждый SNV = ровно 1 bin.
Гипотеза: ортогональные модальности могут показать signal, невидимый
в contact maps. Если delta > noise → functional validation pearl variants.
Если delta ≈ noise → ещё одно evidence что DL модели не видят SNVs.

Usage:
    python scripts/multimodal_alphagenome.py
    python scripts/multimodal_alphagenome.py --api-key YOUR_KEY
    python scripts/multimodal_alphagenome.py --cell-line GM12878
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

# ПОЧЕМУ K562: это эритроидная линия, экспрессирующая гемоглобин.
# Для HBB locus — наиболее релевантный клеточный контекст.
DEFAULT_CELL_LINE = "K562"
DEFAULT_ONTOLOGY = "EFO:0002067"  # K562 ontology term

# ПОЧЕМУ ±500bp: для signal concentration ratio — проверяем
# локализован ли delta вокруг варианта (реальный) или рассеян (шум).
VARIANT_WINDOW_BP = 500


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
    """Load pearl variants from unified atlas CSV, skipping IUPAC codes."""
    valid_bases = set("ACGTN")
    pearls = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Pearl", "").lower() != "true":
                continue

            ref = row["Ref"]
            alt = row["Alt"]

            # ПОЧЕМУ skip IUPAC: AlphaGenome Variant accepts only ACGTN
            if not all(b in valid_bases for b in ref.upper()):
                continue
            if not all(b in valid_bases for b in alt.upper()):
                continue

            pearls.append({
                "clinvar_id": row["ClinVar_ID"],
                "position": int(row["Position_GRCh38"]),
                "ref": ref,
                "alt": alt,
                "category": row.get("Category", ""),
                "archcode_ssim": float(row["ARCHCODE_SSIM"]),
                "archcode_lssim": float(row.get("ARCHCODE_LSSIM", row["ARCHCODE_SSIM"])),
                "vep_score": float(row.get("VEP_Score", 0)),
                "hgvs_c": row.get("HGVS_c", ""),
                "variant_type": "SNV" if len(ref) == 1 and len(alt) == 1 else "indel",
            })
    return pearls


def compute_track_metrics(
    ref_values: np.ndarray,
    alt_values: np.ndarray,
    variant_bin: int,
    locus_start_bin: int,
    locus_end_bin: int,
) -> dict:
    """
    Compute delta metrics between ref and alt for a single track.

    ПОЧЕМУ несколько метрик: max_delta показывает наибольший эффект,
    mean_delta — средний, cosine — общее сохранение формы,
    delta_at_variant — прямое влияние на позицию варианта,
    signal_concentration — локализован ли эффект вокруг варианта.
    """
    # Locus window extraction
    ref_w = ref_values[locus_start_bin:locus_end_bin]
    alt_w = alt_values[locus_start_bin:locus_end_bin]
    delta = np.abs(ref_w - alt_w)

    # Cosine similarity
    dot = np.dot(ref_w, alt_w)
    norms = np.linalg.norm(ref_w) * np.linalg.norm(alt_w)
    cosine = float(dot / norms) if norms > 1e-12 else 1.0

    # Delta at variant position
    delta_at_var = float(np.abs(ref_values[variant_bin] - alt_values[variant_bin]))

    # Signal concentration: mean delta in ±500bp around variant vs elsewhere
    var_local_start = max(locus_start_bin, variant_bin - VARIANT_WINDOW_BP)
    var_local_end = min(locus_end_bin, variant_bin + VARIANT_WINDOW_BP)
    local_delta = delta[var_local_start - locus_start_bin:var_local_end - locus_start_bin]

    mean_local = float(np.mean(local_delta)) if len(local_delta) > 0 else 0.0
    mean_global = float(np.mean(delta)) if len(delta) > 0 else 0.0

    # ПОЧЕМУ ratio: если signal_concentration > 1 → delta сконцентрирован
    # вокруг варианта (локальный эффект). Если ≈ 1 → равномерный шум.
    concentration = mean_local / mean_global if mean_global > 1e-12 else 0.0

    return {
        "max_abs_delta": float(delta.max()),
        "mean_abs_delta": float(delta.mean()),
        "cosine_similarity": cosine,
        "delta_at_variant_bin": delta_at_var,
        "n_bins_above_1e4": int((delta > 1e-4).sum()),
        "n_bins_above_1e3": int((delta > 1e-3).sum()),
        "signal_concentration_ratio": round(concentration, 4),
        "locus_bins": int(locus_end_bin - locus_start_bin),
    }


def run_multimodal_analysis(
    api_key: str,
    pearls: list[dict],
    chromosome: str,
    window_start: int,
    window_end: int,
    cell_line: str,
    ontology_term: str,
    batch_size: int = 5,
    batch_delay: float = 3.0,
) -> list[dict]:
    """Run predict_variant with RNA_SEQ + ATAC for each pearl variant."""
    from alphagenome.models import dna_client
    from alphagenome.models.dna_output import OutputType
    from alphagenome.data.genome import Variant, Interval

    print(f"  Creating AlphaGenome client...")
    model = dna_client.create(api_key)

    # ПОЧЕМУ 131072: ближайший поддерживаемый размер >= 95kb window
    center = (window_start + window_end) // 2
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    seq_length = next((sl for sl in supported if sl >= (window_end - window_start)), supported[-1])
    interval_start = center - seq_length // 2
    interval = Interval(chromosome, interval_start, interval_start + seq_length)

    locus_start_bin = window_start - interval_start
    locus_end_bin = window_end - interval_start

    print(f"  Interval: {interval} (seq_length={seq_length})")
    print(f"  Cell line: {cell_line} ({ontology_term})")
    print(f"  Locus window bins: {locus_start_bin}-{locus_end_bin} ({locus_end_bin - locus_start_bin} bins)")
    print(f"  Variants to process: {len(pearls)}")

    results = []
    for i, pearl in enumerate(pearls):
        pos = pearl["position"]
        ref = pearl["ref"]
        alt = pearl["alt"]
        variant_bin = pos - interval_start

        # Skip very large indels (>50bp each allele)
        if len(ref) > 50 or len(alt) > 50:
            print(f"  [{i+1}/{len(pearls)}] SKIP {pearl['clinvar_id']}: "
                  f"complex variant ({len(ref)}bp>{len(alt)}bp)")
            results.append({**pearl, "status": "skipped_complex"})
            continue

        print(f"  [{i+1}/{len(pearls)}] {pearl['clinvar_id']} "
              f"{chromosome}:{pos} {ref}>{alt} ({pearl['variant_type']}, "
              f"ARCHCODE SSIM={pearl['archcode_ssim']:.4f})")

        try:
            variant = Variant(chromosome, pos, ref, alt)
            output = model.predict_variant(
                interval=interval,
                variant=variant,
                requested_outputs=[OutputType.RNA_SEQ, OutputType.ATAC],
                ontology_terms=[ontology_term],
            )

            result = {**pearl, "status": "success"}

            # RNA_SEQ metrics
            if output.reference.rna_seq is not None:
                ref_rna = output.reference.rna_seq
                alt_rna = output.alternate.rna_seq
                meta = ref_rna.metadata

                # ПОЧЕМУ unstranded: strand='.' объединяет + и - strands.
                # Для общего анализа это наиболее robust signal.
                unstranded = meta[meta["strand"] == "."]
                polya = unstranded[unstranded["name"].str.contains("polyA", case=False)]

                if not polya.empty:
                    tidx = polya.index[0]
                    track_name = meta.iloc[tidx]["name"]
                else:
                    tidx = 0
                    track_name = meta.iloc[0]["name"]

                rna_metrics = compute_track_metrics(
                    ref_rna.values[:, tidx],
                    alt_rna.values[:, tidx],
                    variant_bin, locus_start_bin, locus_end_bin,
                )
                result["rna_seq"] = {
                    "track": track_name,
                    "resolution_bp": ref_rna.resolution,
                    **rna_metrics,
                }
                print(f"    RNA_SEQ: max_delta={rna_metrics['max_abs_delta']:.4f}, "
                      f"at_variant={rna_metrics['delta_at_variant_bin']:.4f}, "
                      f"concentration={rna_metrics['signal_concentration_ratio']:.2f}")
            else:
                result["rna_seq"] = {"status": "no_data"}

            # ATAC metrics
            if output.reference.atac is not None:
                ref_atac = output.reference.atac
                alt_atac = output.alternate.atac

                atac_metrics = compute_track_metrics(
                    ref_atac.values[:, 0],
                    alt_atac.values[:, 0],
                    variant_bin, locus_start_bin, locus_end_bin,
                )
                result["atac"] = {
                    "track": ref_atac.metadata.iloc[0]["name"],
                    "resolution_bp": ref_atac.resolution,
                    **atac_metrics,
                }
                print(f"    ATAC:    max_delta={atac_metrics['max_abs_delta']:.4f}, "
                      f"at_variant={atac_metrics['delta_at_variant_bin']:.4f}, "
                      f"concentration={atac_metrics['signal_concentration_ratio']:.2f}")
            else:
                result["atac"] = {"status": "no_data"}

            results.append(result)

        except Exception as e:
            print(f"    ERROR: {type(e).__name__}: {e}")
            results.append({**pearl, "status": f"error_{type(e).__name__}"})

        # Rate limiting
        if (i + 1) % batch_size == 0 and i + 1 < len(pearls):
            print(f"  --- Batch pause ({batch_delay}s) ---")
            time.sleep(batch_delay)

    return results


def compute_correlations(results: list[dict]) -> dict:
    """
    Compute correlations between ARCHCODE perturbation and multimodal deltas.

    ПОЧЕМУ Spearman: rank correlation устойчива к outliers и не требует
    линейности. Если ARCHCODE и AG ранжируют варианты одинаково → agreement.
    """
    from scipy.stats import spearmanr, pearsonr

    valid = [r for r in results if r.get("status") == "success"]
    if len(valid) < 3:
        return {"error": f"insufficient valid variants ({len(valid)})"}

    archcode_deltas = np.array([1.0 - r["archcode_ssim"] for r in valid])

    correlations = {"n_valid": len(valid), "n_total": len(results)}

    for modality in ["rna_seq", "atac"]:
        mod_data = [r.get(modality, {}) for r in valid]
        if all("max_abs_delta" in m for m in mod_data):
            max_deltas = np.array([m["max_abs_delta"] for m in mod_data])
            mean_deltas = np.array([m["mean_abs_delta"] for m in mod_data])
            var_deltas = np.array([m["delta_at_variant_bin"] for m in mod_data])

            # ПОЧЕМУ три корреляции: max, mean и at_variant ловят разные аспекты
            for metric_name, metric_vals in [
                ("max_delta", max_deltas),
                ("mean_delta", mean_deltas),
                ("variant_delta", var_deltas),
            ]:
                if np.std(metric_vals) < 1e-12:
                    correlations[f"{modality}_{metric_name}_spearman"] = {
                        "warning": "zero variance",
                        "mean": float(np.mean(metric_vals)),
                    }
                    continue
                rho, p_rho = spearmanr(archcode_deltas, metric_vals)
                r, p_r = pearsonr(archcode_deltas, metric_vals)
                correlations[f"{modality}_{metric_name}_spearman"] = {
                    "rho": round(float(rho), 4),
                    "p": round(float(p_rho), 4),
                }
                correlations[f"{modality}_{metric_name}_pearson"] = {
                    "r": round(float(r), 4),
                    "p": round(float(p_r), 4),
                }

            # Summary stats for this modality
            correlations[f"{modality}_summary"] = {
                "max_delta_range": [float(max_deltas.min()), float(max_deltas.max())],
                "max_delta_mean": round(float(np.mean(max_deltas)), 6),
                "mean_delta_mean": round(float(np.mean(mean_deltas)), 6),
                "variant_delta_mean": round(float(np.mean(var_deltas)), 6),
            }

    return correlations


def main():
    parser = argparse.ArgumentParser(
        description="Multimodal AlphaGenome validation: RNA_SEQ + ATAC"
    )
    parser.add_argument(
        "--atlas", default="results/HBB_Unified_Atlas_95kb.csv",
        help="Path to unified atlas CSV (default: 95kb)",
    )
    parser.add_argument("--locus", default="95kb", help="Locus alias")
    parser.add_argument("--api-key", help="AlphaGenome API key")
    parser.add_argument(
        "--cell-line", default=DEFAULT_CELL_LINE,
        help=f"Cell line (default: {DEFAULT_CELL_LINE})",
    )
    parser.add_argument(
        "--ontology-term", default=DEFAULT_ONTOLOGY,
        help=f"Ontology term for cell line (default: {DEFAULT_ONTOLOGY})",
    )
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--batch-delay", type=float, default=3.0)
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()

    api_key = get_api_key(args)

    print("=" * 70)
    print("ARCHCODE Multimodal AlphaGenome Validation (RNA_SEQ + ATAC)")
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
    n_snv = sum(1 for p in pearls if p["variant_type"] == "SNV")
    n_indel = sum(1 for p in pearls if p["variant_type"] == "indel")
    print(f"  Found {len(pearls)} usable pearls ({n_snv} SNV, {n_indel} indel)")
    if not pearls:
        print("  ERROR: No pearl variants found.")
        sys.exit(1)

    # Step 3: Run multimodal analysis
    print(f"\n--- Step 3: Multimodal predict_variant ---")
    results = run_multimodal_analysis(
        api_key=api_key,
        pearls=pearls,
        chromosome=chrom,
        window_start=start,
        window_end=end,
        cell_line=args.cell_line,
        ontology_term=args.ontology_term,
        batch_size=args.batch_size,
        batch_delay=args.batch_delay,
    )

    # Step 4: Correlations
    print(f"\n--- Step 4: Correlation analysis ---")
    correlations = compute_correlations(results)

    if "error" in correlations:
        print(f"  {correlations['error']}")
    else:
        for modality in ["rna_seq", "atac"]:
            key = f"{modality}_max_delta_spearman"
            if key in correlations and "rho" in correlations[key]:
                c = correlations[key]
                print(f"  {modality.upper()} max_delta ~ ARCHCODE: "
                      f"ρ={c['rho']:.4f} (p={c['p']:.4f})")

    # Step 5: Save results
    output_path = (
        Path(args.output) if args.output
        else PROJECT_ROOT / "results" / "multimodal_alphagenome_hbb.json"
    )

    successful = [r for r in results if r.get("status") == "success"]

    # Summary statistics
    summary_stats = {}
    for modality in ["rna_seq", "atac"]:
        mod_vals = [r[modality] for r in successful if modality in r and "max_abs_delta" in r.get(modality, {})]
        if mod_vals:
            summary_stats[modality] = {
                "mean_max_delta": round(float(np.mean([m["max_abs_delta"] for m in mod_vals])), 6),
                "mean_mean_delta": round(float(np.mean([m["mean_abs_delta"] for m in mod_vals])), 8),
                "mean_variant_delta": round(float(np.mean([m["delta_at_variant_bin"] for m in mod_vals])), 6),
                "mean_cosine": round(float(np.mean([m["cosine_similarity"] for m in mod_vals])), 10),
                "mean_concentration": round(float(np.mean([m["signal_concentration_ratio"] for m in mod_vals])), 4),
            }

    output = {
        "analysis": "multimodal_alphagenome_validation",
        "description": "RNA_SEQ + ATAC predict_variant for pearl variants at 1bp resolution",
        "locus": args.locus,
        "locus_id": config.get("id"),
        "window": {"chromosome": chrom, "start": start, "end": end},
        "parameters": {
            "cell_line": args.cell_line,
            "ontology_term": args.ontology_term,
            "output_types": ["RNA_SEQ", "ATAC"],
            "resolution_bp": 1,
            "variant_window_bp": VARIANT_WINDOW_BP,
            "sdk_version": "0.6.0",
        },
        "counts": {
            "total_pearls": len(pearls),
            "successful": len(successful),
            "snv": sum(1 for r in successful if r.get("variant_type") == "SNV"),
            "indel": sum(1 for r in successful if r.get("variant_type") == "indel"),
            "skipped": sum(1 for r in results if r.get("status", "").startswith("skipped")),
            "errors": sum(1 for r in results if r.get("status", "").startswith("error")),
        },
        "summary": summary_stats,
        "correlations": correlations,
        "variants": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2))
    print(f"\n  Results saved: {output_path}")

    # Print summary table
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Variants processed: {len(successful)}/{len(pearls)}")

    for mod_name, mod_label in [("rna_seq", "RNA_SEQ"), ("atac", "ATAC")]:
        if mod_name in summary_stats:
            s = summary_stats[mod_name]
            print(f"\n  {mod_label} (1bp resolution, {args.cell_line}):")
            print(f"    Mean max_delta:     {s['mean_max_delta']:.6f}")
            print(f"    Mean delta@variant: {s['mean_variant_delta']:.6f}")
            print(f"    Mean cosine:        {s['mean_cosine']:.10f}")
            print(f"    Mean concentration: {s['mean_concentration']:.4f}")

    # Comparison with contact maps
    print(f"\n  Context: Contact maps ΔSSIM < 10⁻⁴ (null)")
    if "rna_seq" in summary_stats:
        rna_max = summary_stats["rna_seq"]["mean_max_delta"]
        print(f"  RNA_SEQ mean_max_delta = {rna_max:.4f} → "
              f"{'DETECTABLE signal' if rna_max > 0.01 else 'near-null'}")
    if "atac" in summary_stats:
        atac_max = summary_stats["atac"]["mean_max_delta"]
        print(f"  ATAC mean_max_delta = {atac_max:.4f} → "
              f"{'DETECTABLE signal' if atac_max > 0.01 else 'near-null'}")
    print()


if __name__ == "__main__":
    main()
