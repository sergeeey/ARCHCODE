#!/usr/bin/env python3
"""
VEP Batch Scoring for All Non-HBB Loci

Queries Ensembl VEP REST API for 8 loci (MLH1, CFTR, TP53, BRCA1, LDLR, SCN5A, TERT, GJB2),
computes VEP_Score using the same formula as HBB, re-derives Pearl/Discordance columns.

Uses the same CONSEQUENCE_SCORES and SIFT formula from run_vep_predictions.py.

Usage:
  python scripts/vep_batch_scoring.py --locus MLH1      # single locus
  python scripts/vep_batch_scoring.py --all              # all 8 loci
  python scripts/vep_batch_scoring.py --all --dry-run    # show counts only
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import argparse
import sys
from pathlib import Path

# --- Reuse from run_vep_predictions.py ---

VEP_API_URL = "https://rest.ensembl.org/vep/homo_sapiens/region"
VEP_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
BATCH_SIZE = 200
REQUEST_DELAY = 0.5  # 500ms between batches (Ensembl allows 15 req/s)

CONSEQUENCE_SCORES = {
    "transcript_ablation": 0.99,
    "splice_acceptor_variant": 0.95,
    "splice_donor_variant": 0.95,
    "stop_gained": 0.90,
    "frameshift_variant": 0.90,
    "stop_lost": 0.85,
    "start_lost": 0.85,
    "transcript_amplification": 0.80,
    "inframe_insertion": 0.60,
    "inframe_deletion": 0.60,
    "missense_variant": 0.50,
    "protein_altering_variant": 0.50,
    "splice_region_variant": 0.50,
    "splice_donor_5th_base_variant": 0.40,
    "splice_donor_region_variant": 0.35,
    "splice_polypyrimidine_tract_variant": 0.30,
    "incomplete_terminal_codon_variant": 0.30,
    "start_retained_variant": 0.15,
    "stop_retained_variant": 0.15,
    "synonymous_variant": 0.05,
    "coding_sequence_variant": 0.20,
    "mature_miRNA_variant": 0.25,
    "5_prime_UTR_variant": 0.20,
    "3_prime_UTR_variant": 0.15,
    "non_coding_transcript_exon_variant": 0.15,
    "intron_variant": 0.10,
    "NMD_transcript_variant": 0.10,
    "non_coding_transcript_variant": 0.10,
    "upstream_gene_variant": 0.15,
    "downstream_gene_variant": 0.10,
    "TFBS_ablation": 0.40,
    "TFBS_amplification": 0.25,
    "TF_binding_site_variant": 0.20,
    "regulatory_region_ablation": 0.35,
    "regulatory_region_amplification": 0.20,
    "feature_elongation": 0.10,
    "regulatory_region_variant": 0.15,
    "feature_truncation": 0.10,
    "intergenic_variant": 0.05,
}

# --- Locus configuration ---

LOCUS_CONFIG = {
    "MLH1":  {"chr": "3",  "gene": "MLH1",  "atlas": "results/MLH1_Unified_Atlas_300kb.csv"},
    "CFTR":  {"chr": "7",  "gene": "CFTR",  "atlas": "results/CFTR_Unified_Atlas_317kb.csv"},
    "TP53":  {"chr": "17", "gene": "TP53",  "atlas": "results/TP53_Unified_Atlas_300kb.csv"},
    "BRCA1": {"chr": "17", "gene": "BRCA1", "atlas": "results/BRCA1_Unified_Atlas_400kb.csv"},
    "LDLR":  {"chr": "19", "gene": "LDLR",  "atlas": "results/LDLR_Unified_Atlas_300kb.csv"},
    "SCN5A": {"chr": "3",  "gene": "SCN5A", "atlas": "results/SCN5A_Unified_Atlas_400kb.csv"},
    "TERT":  {"chr": "5",  "gene": "TERT",  "atlas": "results/TERT_Unified_Atlas_300kb.csv"},
    "GJB2":  {"chr": "13", "gene": "GJB2",  "atlas": "results/GJB2_Unified_Atlas_300kb.csv"},
}

VALID_BASES = {"A", "C", "G", "T"}


def is_queryable_snv(ref: str, alt: str) -> bool:
    """Check if variant is a clean SNV queryable via VEP region endpoint."""
    return (
        isinstance(ref, str) and isinstance(alt, str)
        and len(ref) == 1 and len(alt) == 1
        and ref in VALID_BASES and alt in VALID_BASES
    )


def run_vep_batch(variants: list[str], retries: int = 3) -> list[dict]:
    """Query Ensembl VEP API with a batch of variants."""
    data = {"variants": variants, "SIFT": "b"}
    for attempt in range(retries):
        try:
            r = requests.post(VEP_API_URL, headers=VEP_HEADERS, json=data, timeout=120)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 5))
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    VEP API error {r.status_code}: {r.text[:200]}")
                time.sleep(2)
        except Exception as e:
            print(f"    Request error (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(3)
    return []


def parse_vep_result(result: dict, gene_symbol: str) -> dict:
    """Parse VEP result, filtering transcripts for the target gene."""
    transcript_consequences = result.get("transcript_consequences", [])

    # ПОЧЕМУ: фильтр по gene_symbol — чтобы брать аннотацию именно для целевого гена,
    # а не соседнего (напр. EPM2AIP1 рядом с MLH1)
    gene_csqs = [
        tc for tc in transcript_consequences
        if tc.get("gene_symbol") == gene_symbol
    ]
    if not gene_csqs:
        gene_csqs = transcript_consequences

    if not gene_csqs:
        return {
            "most_severe_consequence": result.get("most_severe_consequence", "unknown"),
            "vep_score": CONSEQUENCE_SCORES.get(
                result.get("most_severe_consequence", ""), 0.1
            ),
            "sift_score": np.nan,
            "sift_prediction": "",
            "impact": "MODIFIER",
        }

    # Find most severe consequence across gene transcripts
    best_tc = None
    best_severity = -1
    for tc in gene_csqs:
        for term in tc.get("consequence_terms", []):
            severity = CONSEQUENCE_SCORES.get(term, 0.1)
            if severity > best_severity:
                best_severity = severity
                best_tc = tc

    if best_tc is None:
        best_tc = gene_csqs[0]

    sift_score = best_tc.get("sift_score", np.nan)
    sift_prediction = best_tc.get("sift_prediction", "")
    most_severe = result.get("most_severe_consequence", "unknown")
    vep_score = best_severity

    # SIFT refinement for missense (same formula as HBB pipeline)
    if most_severe == "missense_variant" and not np.isnan(sift_score):
        vep_score = 0.4 + 0.5 * (1 - sift_score)

    return {
        "most_severe_consequence": most_severe,
        "vep_score": round(vep_score, 4),
        "sift_score": round(sift_score, 4) if not np.isnan(sift_score) else np.nan,
        "sift_prediction": sift_prediction,
        "impact": best_tc.get("impact", "MODIFIER"),
    }


def interpret_vep_score(score: float) -> str:
    """VEP score → human-readable interpretation."""
    if np.isnan(score) or score < 0:
        return "N/A"
    if score >= 0.8:
        return "Very High Impact"
    elif score >= 0.5:
        return "High Impact"
    elif score >= 0.2:
        return "Moderate Impact"
    else:
        return "Low Impact"


def compute_pearl(vep_score: float, lssim: float) -> bool:
    """Pearl = VEP says benign (< 0.30) BUT ARCHCODE detects structural disruption (< 0.95)."""
    return (
        not np.isnan(vep_score)
        and vep_score >= 0
        and vep_score < 0.30
        and not np.isnan(lssim)
        and lssim < 0.95
    )


def compute_discordance(vep_score: float, verdict: str) -> str:
    """Compute discordance category between VEP and ARCHCODE verdict."""
    if np.isnan(vep_score) or vep_score < 0:
        return "NO_VEP"

    pathogenic_verdicts = {"PATHOGENIC", "LIKELY_PATHOGENIC"}
    benign_verdicts = {"BENIGN", "LIKELY_BENIGN"}
    verdict_upper = str(verdict).upper()

    if vep_score >= 0.5 and verdict_upper in benign_verdicts:
        return "VEP_ONLY"
    elif vep_score < 0.5 and verdict_upper in pathogenic_verdicts:
        return "ARCHCODE_ONLY"
    else:
        return "AGREEMENT"


def generate_mechanism_insight(
    vep_score: float, lssim: float, ssim: float, is_pearl: bool, discordance: str
) -> str:
    """Generate mechanism insight text for the atlas."""
    if is_pearl:
        return (
            f"PEARL: VEP-invisible (score={vep_score:.2f}) but structurally disruptive "
            f"(LSSIM={lssim:.3f}). Potential enhancer-mediated pathogenicity."
        )
    if discordance == "NO_VEP":
        return (
            f"Structural-only assessment (LSSIM={lssim:.3f}, global SSIM={ssim:.3f}). "
            f"VEP not available for this variant type."
        )
    if discordance == "VEP_ONLY":
        return (
            f"VEP detects sequence impact (score={vep_score:.2f}) but structure appears "
            f"intact (LSSIM={lssim:.3f}). Possible compensatory mechanism."
        )
    if discordance == "ARCHCODE_ONLY":
        return (
            f"VEP benign (score={vep_score:.2f}) but structural disruption detected "
            f"(LSSIM={lssim:.3f}). Enhancer/loop-mediated effect."
        )
    return "Convergent evidence from structural and sequence analysis."


def process_locus(locus_name: str, project_root: Path, dry_run: bool = False) -> dict:
    """Process a single locus: query VEP, update atlas CSV, return stats."""
    cfg = LOCUS_CONFIG[locus_name]
    atlas_path = project_root / cfg["atlas"]
    chrom = cfg["chr"]
    gene = cfg["gene"]
    checkpoint_path = project_root / "results" / f".vep_checkpoint_{locus_name}.json"

    print(f"\n{'='*60}")
    print(f"Processing {locus_name} (chr{chrom}, gene={gene})")
    print(f"Atlas: {atlas_path}")

    df = pd.read_csv(atlas_path)
    n_total = len(df)
    print(f"Total variants: {n_total}")

    # Identify queryable SNVs that still need VEP
    needs_vep = df["VEP_Score"].apply(lambda x: x == -1 or (isinstance(x, float) and np.isnan(x)))
    queryable = df.apply(
        lambda r: is_queryable_snv(str(r["Ref"]), str(r["Alt"])),
        axis=1,
    )
    to_query_mask = needs_vep & queryable
    to_query_idx = df.index[to_query_mask].tolist()
    n_query = len(to_query_idx)
    n_skip = needs_vep.sum() - n_query

    print(f"Queryable SNVs needing VEP: {n_query}")
    print(f"Non-queryable (indels/CNV, keep VEP=-1): {n_skip}")

    if dry_run:
        return {
            "locus": locus_name,
            "total": n_total,
            "queryable_snvs": n_query,
            "non_queryable": int(n_skip),
            "batches": (n_query + BATCH_SIZE - 1) // BATCH_SIZE,
        }

    if n_query == 0:
        print("Nothing to query — all SNVs already scored or non-queryable.")
        return _compute_locus_stats(df, locus_name)

    # Load checkpoint if exists (resume support)
    scored_positions = {}
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            scored_positions = json.load(f)
        print(f"Resuming: {len(scored_positions)} variants already scored from checkpoint")

    # Build VEP queries
    total_batches = (n_query + BATCH_SIZE - 1) // BATCH_SIZE
    batch_num = 0

    for batch_start in range(0, n_query, BATCH_SIZE):
        batch_num += 1
        batch_indices = to_query_idx[batch_start : batch_start + BATCH_SIZE]

        # Skip already-scored variants (from checkpoint)
        vep_inputs = []
        batch_rows = []
        for idx in batch_indices:
            row = df.loc[idx]
            pos = int(row["Position_GRCh38"])
            ref = str(row["Ref"])
            alt = str(row["Alt"])
            pos_key = f"{pos}_{ref}_{alt}"

            if pos_key in scored_positions:
                # Apply from checkpoint
                cached = scored_positions[pos_key]
                df.at[idx, "VEP_Consequence"] = cached["consequence"]
                df.at[idx, "VEP_Score"] = cached["score"]
                df.at[idx, "VEP_Impact"] = cached["impact"]
                df.at[idx, "SIFT_Score"] = cached.get("sift_score", -1)
                df.at[idx, "SIFT_Prediction"] = cached.get("sift_prediction", "")
                df.at[idx, "VEP_Interpretation"] = cached.get("interpretation", "")
                continue

            vep_input = f"{chrom} {pos} . {ref} {alt} . . ."
            vep_inputs.append(vep_input)
            batch_rows.append((idx, pos, ref, alt))

        if not vep_inputs:
            print(f"  Batch {batch_num}/{total_batches}: all from checkpoint, skipping API")
            continue

        print(f"  Batch {batch_num}/{total_batches}: {len(vep_inputs)} variants to API...")
        vep_results = run_vep_batch(vep_inputs)

        # Build result map by position
        result_map = {}
        for vr in vep_results:
            rkey = f"{vr.get('start', 0)}"
            # Handle multiple results at same position (different alleles)
            allele = vr.get("allele_string", "").split("/")[-1] if "/" in vr.get("allele_string", "") else ""
            result_map[f"{rkey}_{allele}"] = vr
            result_map[rkey] = vr  # fallback without allele

        # Apply results
        for idx, pos, ref, alt in batch_rows:
            pos_key = f"{pos}_{ref}_{alt}"
            # Try exact match first (pos + alt allele), then position-only
            vr = result_map.get(f"{pos}_{alt}") or result_map.get(str(pos))

            if vr:
                parsed = parse_vep_result(vr, gene)
                df.at[idx, "VEP_Consequence"] = parsed["most_severe_consequence"]
                df.at[idx, "VEP_Score"] = parsed["vep_score"]
                df.at[idx, "VEP_Impact"] = parsed["impact"]
                df.at[idx, "SIFT_Score"] = (
                    parsed["sift_score"] if not np.isnan(parsed["sift_score"]) else -1
                )
                df.at[idx, "SIFT_Prediction"] = parsed["sift_prediction"]
                df.at[idx, "VEP_Interpretation"] = interpret_vep_score(parsed["vep_score"])

                # Save to checkpoint
                scored_positions[pos_key] = {
                    "consequence": parsed["most_severe_consequence"],
                    "score": parsed["vep_score"],
                    "impact": parsed["impact"],
                    "sift_score": parsed["sift_score"] if not np.isnan(parsed["sift_score"]) else -1,
                    "sift_prediction": parsed["sift_prediction"],
                    "interpretation": interpret_vep_score(parsed["vep_score"]),
                }
            else:
                # VEP returned no result for this variant
                df.at[idx, "VEP_Score"] = -1
                df.at[idx, "VEP_Consequence"] = ""
                df.at[idx, "VEP_Impact"] = ""
                df.at[idx, "VEP_Interpretation"] = ""

        # Save checkpoint after each batch
        with open(checkpoint_path, "w") as f:
            json.dump(scored_positions, f)

        time.sleep(REQUEST_DELAY)

    # Recompute Pearl and Discordance for ALL rows
    print(f"Recomputing Pearl/Discordance for {n_total} variants...")
    for idx in df.index:
        vep_score = df.at[idx, "VEP_Score"]
        lssim = df.at[idx, "ARCHCODE_LSSIM"]
        ssim = df.at[idx, "ARCHCODE_SSIM"]
        verdict = df.at[idx, "ARCHCODE_Verdict"]

        vep_f = float(vep_score) if not pd.isna(vep_score) else np.nan
        lssim_f = float(lssim) if not pd.isna(lssim) else np.nan
        ssim_f = float(ssim) if not pd.isna(ssim) else np.nan

        is_pearl = compute_pearl(vep_f, lssim_f)
        discordance = compute_discordance(vep_f, str(verdict))
        insight = generate_mechanism_insight(vep_f, lssim_f, ssim_f, is_pearl, discordance)

        df.at[idx, "Pearl"] = is_pearl
        df.at[idx, "Discordance"] = discordance
        df.at[idx, "Mechanism_Insight"] = insight

    # Convert Pearl to lowercase string to match HBB format (true/false not True/False)
    df["Pearl"] = df["Pearl"].apply(lambda x: str(x).lower() if isinstance(x, bool) else str(x).lower())

    # Save updated atlas
    df.to_csv(atlas_path, index=False)
    print(f"Saved updated atlas: {atlas_path}")

    # Clean up checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"Cleaned up checkpoint file")

    stats = _compute_locus_stats(df, locus_name)
    _print_locus_summary(stats)
    return stats


def _compute_locus_stats(df: pd.DataFrame, locus_name: str) -> dict:
    """Compute summary statistics for a locus."""
    vep_scored = df[df["VEP_Score"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)]
    vep_unscored = df[df["VEP_Score"].apply(lambda x: x == -1 or (isinstance(x, float) and np.isnan(x)))]
    pearls = df[df["Pearl"].apply(lambda x: str(x).lower() == "true")]

    scores = vep_scored["VEP_Score"].astype(float)
    stats = {
        "locus": locus_name,
        "total_variants": len(df),
        "vep_scored": len(vep_scored),
        "vep_unscored": len(vep_unscored),
        "vep_score_mean": round(float(scores.mean()), 4) if len(scores) > 0 else None,
        "vep_score_median": round(float(scores.median()), 4) if len(scores) > 0 else None,
        "vep_score_q25": round(float(scores.quantile(0.25)), 4) if len(scores) > 0 else None,
        "vep_score_q75": round(float(scores.quantile(0.75)), 4) if len(scores) > 0 else None,
        "pearl_count": len(pearls),
        "pearl_variants": pearls["ClinVar_ID"].tolist() if len(pearls) > 0 else [],
        "discordance": {
            cat: int(count)
            for cat, count in df["Discordance"].value_counts().items()
        },
        "consequence_breakdown": {
            cat: int(count)
            for cat, count in vep_scored["VEP_Consequence"].value_counts().head(10).items()
        },
    }
    return stats


def _print_locus_summary(stats: dict):
    """Print human-readable summary for a locus."""
    print(f"\n--- {stats['locus']} Summary ---")
    print(f"VEP scored: {stats['vep_scored']} / {stats['total_variants']}")
    print(f"VEP unscored: {stats['vep_unscored']}")
    if stats["vep_score_mean"] is not None:
        print(f"VEP score: mean={stats['vep_score_mean']}, median={stats['vep_score_median']}")
    print(f"Pearl variants: {stats['pearl_count']}")
    if stats["pearl_count"] > 0:
        for pid in stats["pearl_variants"][:10]:
            print(f"  - {pid}")
        if stats["pearl_count"] > 10:
            print(f"  ... and {stats['pearl_count'] - 10} more")
    print(f"Discordance: {stats['discordance']}")


def main():
    parser = argparse.ArgumentParser(
        description="VEP batch scoring for non-HBB loci"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--locus", type=str, choices=list(LOCUS_CONFIG.keys()),
                       help="Single locus to process")
    group.add_argument("--all", action="store_true",
                       help="Process all 8 loci")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show variant counts without querying API")

    args = parser.parse_args()
    project_root = Path(__file__).parent.parent

    loci = [args.locus] if args.locus else list(LOCUS_CONFIG.keys())

    all_stats = {}
    for locus in loci:
        stats = process_locus(locus, project_root, dry_run=args.dry_run)
        all_stats[locus] = stats

    # Write summary JSON
    if not args.dry_run:
        summary_path = project_root / "results" / "vep_multilocus_summary.json"
        with open(summary_path, "w") as f:
            json.dump(all_stats, f, indent=2)
        print(f"\n{'='*60}")
        print(f"Summary saved: {summary_path}")

    # Final overview
    print(f"\n{'='*60}")
    print("OVERVIEW")
    print(f"{'='*60}")
    total_pearls = 0
    for locus, stats in all_stats.items():
        pearl_count = stats.get("pearl_count", 0)
        total_pearls += pearl_count
        scored = stats.get("vep_scored", stats.get("queryable_snvs", "?"))
        total = stats.get("total_variants", stats.get("total", "?"))
        pearl_str = f" *** {pearl_count} PEARLS ***" if pearl_count > 0 else ""
        print(f"  {locus:6s}: {scored}/{total} scored{pearl_str}")

    if not args.dry_run:
        print(f"\nTotal new pearls across 8 loci: {total_pearls}")
        if total_pearls > 0:
            print(">>> Pearl variants found! Manuscript update recommended (v2.10)")


if __name__ == "__main__":
    main()
