#!/usr/bin/env python3
"""
Multimodal AlphaGenome validation: RNA_SEQ + ATAC for pearl and benign variants.

ПОЧЕМУ этот скрипт:
Contact maps (2048bp resolution) дают null на variant-level (ΔSSIM < 10⁻⁴).
Но RNA_SEQ и ATAC предсказываются AlphaGenome с разрешением **1bp** —
в 2048× выше. При 1bp resolution каждый SNV = ровно 1 bin.
Гипотеза: ортогональные модальности могут показать signal, невидимый
в contact maps. Если delta > noise → functional validation pearl variants.
Если delta ≈ noise → ещё одно evidence что DL модели не видят SNVs.

ПОЧЕМУ control group (v2):
Pearl variants дают mean max_delta=28 (RNA) и 5.7 (ATAC). Но без контроля
неясно, специфичен ли этот сигнал. --variant-mode benign загружает Label==Benign
non-pearl variants и прогоняет тот же pipeline. --compare сравнивает группы
через Mann-Whitney U (non-parametric, не требует нормальности).

ПОЧЕМУ cross-locus (v3):
Для локусов без pearls (BRCA1, SCN5A) используем --variant-mode pathogenic
для ClinVar Pathogenic variants. Сравнение pathogenic vs benign — внешняя
ground truth от ClinVar вместо ARCHCODE-internal pearl detection.

Usage:
    python scripts/multimodal_alphagenome.py                              # HBB pearl (default)
    python scripts/multimodal_alphagenome.py --variant-mode benign --sample-size 23 --seed 42
    python scripts/multimodal_alphagenome.py --variant-mode pathogenic --locus brca1 --atlas results/BRCA1_Unified_Atlas_400kb.csv --sample-size 23
    python scripts/multimodal_alphagenome.py --compare --locus brca1      # load both JSONs for locus
    python scripts/multimodal_alphagenome.py --api-key YOUR_KEY
    python scripts/multimodal_alphagenome.py --cell-line MCF7 --ontology-term EFO:0001203
"""

import argparse
import csv
import json
import os
import random
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


def load_variants(
    csv_path: str,
    mode: str = "pearl",
    sample_size: int | None = None,
    seed: int = 42,
) -> list[dict]:
    """
    Load variants from unified atlas CSV, skipping IUPAC codes.

    ПОЧЕМУ три режима:
    - mode="pearl" → Pearl==true (ARCHCODE-only detections, HBB specific)
    - mode="benign" → Label==Benign AND Pearl!=true (control group)
    - mode="pathogenic" → Label==Pathogenic (ClinVar ground truth, for cross-locus)
    Benign and pathogenic variants are randomly sampled for fair comparison.
    """
    valid_bases = set("ACGTN")
    variants = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # ПОЧЕМУ разные фильтры: pearl = наши ARCHCODE-only detections,
            # benign = ClinVar Benign (контрольная группа),
            # pathogenic = ClinVar Pathogenic (для локусов без pearls)
            if mode == "pearl":
                if row.get("Pearl", "").lower() != "true":
                    continue
            elif mode == "benign":
                if row.get("Label", "") != "Benign":
                    continue
                if row.get("Pearl", "").lower() == "true":
                    continue
            elif mode == "pathogenic":
                if row.get("Label", "") != "Pathogenic":
                    continue
            else:
                raise ValueError(f"Unknown variant mode: {mode}")

            ref = row["Ref"]
            alt = row["Alt"]

            # ПОЧЕМУ skip IUPAC: AlphaGenome Variant accepts only ACGTN
            if not all(b in valid_bases for b in ref.upper()):
                continue
            if not all(b in valid_bases for b in alt.upper()):
                continue

            variants.append({
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

    # ПОЧЕМУ random sample: fair comparison требует одинакового n.
    # seed фиксирован для воспроизводимости.
    if mode in ("benign", "pathogenic") and sample_size is not None and len(variants) > sample_size:
        rng = random.Random(seed)
        variants = rng.sample(variants, sample_size)

    return variants


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
    variants: list[dict],
    chromosome: str,
    window_start: int,
    window_end: int,
    cell_line: str,
    ontology_term: str,
    batch_size: int = 5,
    batch_delay: float = 3.0,
) -> list[dict]:
    """Run predict_variant with RNA_SEQ + ATAC for each variant."""
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
    print(f"  Variants to process: {len(variants)}")

    results = []
    for i, pearl in enumerate(variants):
        pos = pearl["position"]
        ref = pearl["ref"]
        alt = pearl["alt"]
        variant_bin = pos - interval_start

        # Skip very large indels (>50bp each allele)
        if len(ref) > 50 or len(alt) > 50:
            print(f"  [{i+1}/{len(variants)}] SKIP {pearl['clinvar_id']}: "
                  f"complex variant ({len(ref)}bp>{len(alt)}bp)")
            results.append({**pearl, "status": "skipped_complex"})
            continue

        print(f"  [{i+1}/{len(variants)}] {pearl['clinvar_id']} "
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
        if (i + 1) % batch_size == 0 and i + 1 < len(variants):
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


def run_comparison(
    pearl_json_path: Path,
    benign_json_path: Path,
    output_path: Path,
) -> dict:
    """
    Compare pearl vs benign multimodal results using Mann-Whitney U test.

    ПОЧЕМУ Mann-Whitney U: non-parametric тест, не требует нормальности.
    Наши данные — малые выборки (n=23), скошенные (indels >> SNVs).
    Rank-biserial r = effect size: 1 − 2U/(n1×n2).
    """
    from scipy.stats import mannwhitneyu

    pearl_data = json.loads(pearl_json_path.read_text())
    benign_data = json.loads(benign_json_path.read_text())

    pearl_variants = [v for v in pearl_data["variants"] if v.get("status") == "success"]
    benign_variants = [v for v in benign_data["variants"] if v.get("status") == "success"]

    n1, n2 = len(pearl_variants), len(benign_variants)
    print(f"  Pearl variants (success): {n1}")
    print(f"  Benign variants (success): {n2}")

    # Verify no overlap
    pearl_ids = {v["clinvar_id"] for v in pearl_variants}
    benign_ids = {v["clinvar_id"] for v in benign_variants}
    overlap = pearl_ids & benign_ids
    if overlap:
        print(f"  WARNING: {len(overlap)} overlapping variants: {overlap}")

    metrics = ["max_abs_delta", "mean_abs_delta", "cosine_similarity",
               "delta_at_variant_bin", "signal_concentration_ratio"]
    modalities = ["rna_seq", "atac"]

    comparison_results = {
        "analysis": "pearl_vs_benign_multimodal_comparison",
        "pearl_json": str(pearl_json_path),
        "benign_json": str(benign_json_path),
        "n_pearl": n1,
        "n_benign": n2,
        "overlap_count": len(overlap),
        "tests": {},
    }

    print(f"\n  {'Modality':<10} {'Metric':<30} {'Pearl mean':>12} {'Benign mean':>12} {'U':>8} {'p-value':>10} {'Effect r':>10}")
    print(f"  {'-'*92}")

    for modality in modalities:
        for metric in metrics:
            pearl_vals = []
            benign_vals = []

            for v in pearl_variants:
                mod_data = v.get(modality, {})
                if metric in mod_data:
                    pearl_vals.append(mod_data[metric])

            for v in benign_variants:
                mod_data = v.get(modality, {})
                if metric in mod_data:
                    benign_vals.append(mod_data[metric])

            if len(pearl_vals) < 3 or len(benign_vals) < 3:
                continue

            pearl_arr = np.array(pearl_vals)
            benign_arr = np.array(benign_vals)

            try:
                U, p = mannwhitneyu(pearl_arr, benign_arr, alternative="two-sided")
                # ПОЧЕМУ rank-biserial: стандартный effect size для Mann-Whitney.
                # r = 1 → полное разделение групп, r = 0 → перекрытие.
                r_effect = 1.0 - (2.0 * U) / (len(pearl_arr) * len(benign_arr))
            except ValueError:
                U, p, r_effect = float("nan"), float("nan"), float("nan")

            key = f"{modality}_{metric}"
            comparison_results["tests"][key] = {
                "pearl_mean": round(float(pearl_arr.mean()), 6),
                "pearl_median": round(float(np.median(pearl_arr)), 6),
                "pearl_std": round(float(pearl_arr.std()), 6),
                "benign_mean": round(float(benign_arr.mean()), 6),
                "benign_median": round(float(np.median(benign_arr)), 6),
                "benign_std": round(float(benign_arr.std()), 6),
                "mann_whitney_U": round(float(U), 2),
                "p_value": round(float(p), 6),
                "rank_biserial_r": round(float(r_effect), 4),
                "significant_005": bool(p < 0.05),
                "n_pearl": len(pearl_arr),
                "n_benign": len(benign_arr),
            }

            sig = "*" if p < 0.05 else " "
            print(f"  {modality:<10} {metric:<30} {pearl_arr.mean():>12.4f} {benign_arr.mean():>12.4f} "
                  f"{U:>8.0f} {p:>10.4f} {r_effect:>9.4f} {sig}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(comparison_results, indent=2))
    print(f"\n  Comparison saved: {output_path}")

    # Count significant results
    sig_count = sum(1 for t in comparison_results["tests"].values() if t.get("significant_005"))
    total_tests = len(comparison_results["tests"])
    print(f"  Significant tests (p<0.05): {sig_count}/{total_tests}")

    return comparison_results


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
    parser.add_argument(
        "--variant-mode", choices=["pearl", "benign", "pathogenic"], default="pearl",
        help="Variant selection mode: pearl (default), benign control, or pathogenic (ClinVar)",
    )
    parser.add_argument(
        "--sample-size", type=int, default=None,
        help="Sample size for benign mode (default: match pearl count)",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument(
        "--compare", action="store_true",
        help="Skip API, load pearl+benign JSONs, compute Mann-Whitney U comparison",
    )
    args = parser.parse_args()

    # ПОЧЕМУ --compare отдельно: не тратит API calls, просто загружает
    # два уже готовых JSON и считает статистику.
    if args.compare:
        # ПОЧЕМУ locus-aware paths: для HBB — pearl vs benign,
        # для других локусов (BRCA1, SCN5A) — pathogenic vs benign.
        locus = args.locus.lower().replace("_400kb", "").replace("_95kb", "")

        if locus in ("95kb", "hbb"):
            # Legacy HBB paths (backward compatible)
            group_a_path = PROJECT_ROOT / "results" / "multimodal_alphagenome_hbb.json"
            group_b_path = PROJECT_ROOT / "results" / "multimodal_alphagenome_hbb_benign_control.json"
            comparison_path = PROJECT_ROOT / "results" / "multimodal_pearl_vs_benign_comparison.json"
            label = "Pearl vs Benign"
        else:
            group_a_path = PROJECT_ROOT / "results" / f"multimodal_alphagenome_{locus}_pathogenic.json"
            group_b_path = PROJECT_ROOT / "results" / f"multimodal_alphagenome_{locus}_benign.json"
            comparison_path = PROJECT_ROOT / "results" / f"multimodal_{locus}_path_vs_benign_comparison.json"
            label = "Pathogenic vs Benign"

        print("=" * 70)
        print(f"ARCHCODE {label} Multimodal Comparison — {locus.upper()} (Mann-Whitney U)")
        print("=" * 70)

        if not group_a_path.exists():
            print(f"  ERROR: Group A results not found: {group_a_path}")
            sys.exit(1)
        if not group_b_path.exists():
            print(f"  ERROR: Group B results not found: {group_b_path}")
            sys.exit(1)

        run_comparison(group_a_path, group_b_path, comparison_path)
        return

    api_key = get_api_key(args)

    variant_mode = args.variant_mode
    print("=" * 70)
    print(f"ARCHCODE Multimodal AlphaGenome Validation (RNA_SEQ + ATAC) — {variant_mode}")
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

    # Step 2: Load variants (pearl or benign)
    atlas_path = PROJECT_ROOT / args.atlas

    # ПОЧЕМУ default sample_size = None для pearl: pearls и так мало (~23),
    # не нужно семплировать. Для benign/pathogenic — если не указан, 23 (как HBB baseline).
    sample_size = args.sample_size
    if variant_mode in ("benign", "pathogenic") and sample_size is None:
        sample_size = 23
        print(f"  Default sample size: {sample_size}")

    print(f"\n--- Step 2: Load {variant_mode} variants ({atlas_path.name}) ---")
    variants = load_variants(
        str(atlas_path), mode=variant_mode, sample_size=sample_size, seed=args.seed,
    )
    n_snv = sum(1 for p in variants if p["variant_type"] == "SNV")
    n_indel = sum(1 for p in variants if p["variant_type"] == "indel")
    print(f"  Found {len(variants)} usable {variant_mode} variants ({n_snv} SNV, {n_indel} indel)")
    if variant_mode in ("benign", "pathogenic"):
        print(f"  Seed: {args.seed}, sample_size: {sample_size}")
    if not variants:
        print(f"  ERROR: No {variant_mode} variants found.")
        sys.exit(1)

    # Step 3: Run multimodal analysis
    print(f"\n--- Step 3: Multimodal predict_variant ---")
    results = run_multimodal_analysis(
        api_key=api_key,
        variants=variants,
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
    # ПОЧЕМУ dynamic naming: locus-aware paths. HBB pearl/benign — legacy paths
    # для backward compatibility. Другие локусы — {locus}_{mode}.json.
    locus_tag = args.locus.lower().replace("_400kb", "").replace("_95kb", "")
    if args.output:
        output_path = Path(args.output)
    elif locus_tag in ("95kb", "hbb"):
        if variant_mode == "benign":
            output_path = PROJECT_ROOT / "results" / "multimodal_alphagenome_hbb_benign_control.json"
        else:
            output_path = PROJECT_ROOT / "results" / "multimodal_alphagenome_hbb.json"
    else:
        output_path = PROJECT_ROOT / "results" / f"multimodal_alphagenome_{locus_tag}_{variant_mode}.json"

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
        "description": f"RNA_SEQ + ATAC predict_variant for {variant_mode} variants at 1bp resolution",
        "variant_mode": variant_mode,
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
            "variant_mode": variant_mode,
            "sample_size": sample_size if variant_mode in ("benign", "pathogenic") else None,
            "seed": args.seed if variant_mode in ("benign", "pathogenic") else None,
        },
        "counts": {
            "total_variants": len(variants),
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
    print(f"  Variants processed: {len(successful)}/{len(variants)} ({variant_mode})")

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
