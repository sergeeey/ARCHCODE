#!/usr/bin/env python3
"""
validate_results_contracts.py

Machine-checkable validation for release-facing ARCHCODE result contracts.

This script validates:
1. Canonical publication evidence index structure
2. Publication claim matrix structure
3. Existence of every referenced evidence artifact
4. Numeric consistency for promoted README/publication claims
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[1]

INDEX_PATH = Path("results/publication_canonical_index_2026-03-30.json")
CLAIM_MATRIX_PATH = Path("results/publication_claim_matrix_2026-03-30.json")


def load_json(rel_path: str | Path) -> Any:
    path = REPO_ROOT / rel_path
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def rel_exists(rel_path: str) -> None:
    path = REPO_ROOT / rel_path
    require(path.exists(), f"Missing referenced artifact: {rel_path}")


def approx(actual: float, expected: float, tol: float = 1e-4) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=tol)


def validate_index(index_data: dict[str, Any]) -> None:
    required_keys = {
        "generated_at_utc",
        "scope",
        "release_surface",
        "governance",
        "source_of_truth",
        "note",
    }
    require(required_keys.issubset(index_data), "Publication canonical index is missing required keys")
    require(isinstance(index_data["release_surface"], list) and index_data["release_surface"], "release_surface must be a non-empty list")

    governance = index_data["governance"]
    require(isinstance(governance, dict), "governance must be an object")
    for key in ("legacy_claim_governance", "results_contract_doc", "validator"):
        require(key in governance, f"governance missing key: {key}")

    for rel_path in governance["legacy_claim_governance"]:
        rel_exists(rel_path)
    rel_exists(governance["results_contract_doc"])
    rel_exists(governance["validator"])

    required_sources = {
        "atlas_scale",
        "hbb_roc",
        "archcode_vs_cadd",
        "per_locus_thresholds",
        "hic_validation",
        "alphagenome_real_api",
        "mpra_crossvalidation",
        "ablation",
        "conservation",
    }
    require(required_sources.issubset(index_data["source_of_truth"]), "source_of_truth missing one or more required source groups")
    for group, paths in index_data["source_of_truth"].items():
        require(isinstance(paths, list) and paths, f"source_of_truth[{group}] must be a non-empty list")
        for rel_path in paths:
            rel_exists(rel_path)


def validate_claim_matrix(matrix_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    required_keys = {
        "generated_at_utc",
        "scope",
        "governance_source",
        "claims",
        "summary",
    }
    require(required_keys.issubset(matrix_data), "Publication claim matrix is missing required keys")
    rel_exists(matrix_data["governance_source"])
    require(isinstance(matrix_data["claims"], list) and matrix_data["claims"], "claims must be a non-empty list")

    claims_by_id: dict[str, dict[str, Any]] = {}
    for claim in matrix_data["claims"]:
        for key in ("id", "surface", "claim_text", "status", "evidence", "evidence_values", "required_wording", "caveats"):
            require(key in claim, f"Claim missing key: {key}")
        require(claim["id"] not in claims_by_id, f"Duplicate claim id: {claim['id']}")
        require(isinstance(claim["evidence"], list) and claim["evidence"], f"{claim['id']} must reference at least one evidence artifact")
        for rel_path in claim["evidence"]:
            rel_exists(rel_path)
        claims_by_id[claim["id"]] = claim

    summary = matrix_data["summary"]
    require(summary["total_claims"] == len(matrix_data["claims"]), "summary.total_claims does not match actual claim count")
    return claims_by_id


def check_p01(claim: dict[str, Any]) -> None:
    benchmark = load_json("results/integrative_benchmark_summary.json")
    thresholds = load_json("results/per_locus_thresholds_summary.json")
    require(benchmark["total_variants"] == claim["evidence_values"]["total_variants"], "P01 total_variants mismatch")
    require(len(benchmark["per_locus"]) == claim["evidence_values"]["primary_loci"], "P01 primary_loci mismatch from integrative summary")
    require(len(thresholds) == claim["evidence_values"]["primary_loci"], "P01 primary_loci mismatch from threshold summary")


def check_p02(claim: dict[str, Any]) -> None:
    roc = load_json("results/roc_unified.json")["roc"]
    values = claim["evidence_values"]
    require(approx(roc["auc"], values["auc"]), "P02 auc mismatch")
    require(approx(roc["youden_optimal_ssim_threshold"], values["youden_threshold"]), "P02 threshold mismatch")
    require(approx(roc["youden_sensitivity"], values["sensitivity"]), "P02 sensitivity mismatch")
    require(approx(roc["youden_specificity"], values["specificity"]), "P02 specificity mismatch")


def check_p03(claim: dict[str, Any]) -> None:
    benchmark = load_json("results/integrative_benchmark_summary.json")
    values = claim["evidence_values"]
    require(benchmark["total_pearls"] == values["total_pearls"], "P03 total_pearls mismatch")
    require(benchmark["concordance"]["archcode_only"] == values["archcode_only"], "P03 archcode_only mismatch")
    require(benchmark["concordance"]["cadd_only"] == values["cadd_only"], "P03 cadd_only mismatch")
    require(approx(benchmark["pearl_cadd_median"], values["pearl_cadd_median"]), "P03 pearl_cadd_median mismatch")


def check_p04(claim: dict[str, Any]) -> None:
    thresholds = {entry["locus"]: entry for entry in load_json("results/per_locus_thresholds_summary.json")}
    values = claim["evidence_values"]
    require(approx(thresholds["HBB"]["delta_mean"], values["hbb_delta_lssim"]), "P04 HBB delta mismatch")
    require(approx(thresholds["TERT"]["delta_mean"], values["tert_delta_lssim"]), "P04 TERT delta mismatch")
    require(approx(thresholds["SCN5A"]["delta_mean"], values["scn5a_delta_lssim"]), "P04 SCN5A delta mismatch")
    require(approx(thresholds["GJB2"]["delta_mean"], values["gjb2_delta_lssim"]), "P04 GJB2 delta mismatch")
    require(thresholds["HBB"]["tissue"] == "matched", "P04 HBB tissue label drift")
    require(thresholds["SCN5A"]["tissue"] == "mismatch", "P04 SCN5A tissue label drift")
    require(thresholds["GJB2"]["tissue"] == "mismatch", "P04 GJB2 tissue label drift")


def check_p05(claim: dict[str, Any]) -> None:
    hbb30 = load_json("results/hic_correlation_k562.json")["primary_result"]["pearson_r"]
    hbb95 = load_json("results/hic_correlation_k562_95kb.json")["primary_result"]["pearson_r"]
    brca1 = load_json("results/hic_correlation_brca1.json")
    mlh1 = load_json("results/hic_correlation_mlh1.json")
    tp53 = load_json("results/hic_correlation_tp53.json")
    ldlr = load_json("results/hic_correlation_ldlr.json")["pearson_r"]
    observed = [
        hbb30,
        hbb95,
        brca1["K562"]["r"],
        brca1["MCF7"]["r"],
        mlh1["pearson_r"],
        tp53["K562"]["r"],
        tp53["MCF7"]["r"],
        ldlr,
    ]
    values = claim["evidence_values"]
    require(approx(min(observed), values["pearson_r_min"]), "P05 pearson_r_min mismatch")
    require(approx(max(observed), values["pearson_r_max"]), "P05 pearson_r_max mismatch")
    require(approx(mlh1["pearson_r"], values["mlh1_k562_r"]), "P05 MLH1 mismatch")
    require(approx(hbb95, values["hbb_95kb_r"]), "P05 HBB 95kb mismatch")
    require(approx(brca1["K562"]["r"], values["brca1_k562_r"]), "P05 BRCA1 K562 mismatch")


def check_p06(claim: dict[str, Any]) -> None:
    three_way = load_json("results/alphagenome_3way_comparison.json")
    values = claim["evidence_values"]
    require(approx(three_way["mean_cage_pct"]["pearl"], values["pearl_mean_cage_pct"]), "P06 pearl mean mismatch")
    require(approx(three_way["mean_cage_pct"]["pathogenic"], values["pathogenic_mean_cage_pct"]), "P06 pathogenic mean mismatch")
    require(approx(three_way["mean_cage_pct"]["benign"], values["benign_mean_cage_pct"]), "P06 benign mean mismatch")
    require(three_way["n"]["pearl"] == values["n_pearl"], "P06 n_pearl mismatch")
    require(three_way["n"]["pathogenic"] == values["n_pathogenic"], "P06 n_pathogenic mismatch")
    require(three_way["n"]["benign"] == values["n_benign"], "P06 n_benign mismatch")


def check_p07(claim: dict[str, Any]) -> None:
    ism = load_json("results/alphagenome_ism_promoter.json")["results"]
    pearl_rows = [row for row in ism if row["is_pearl"]]
    peak = min(pearl_rows, key=lambda row: row["max_cage_pct"])
    values = claim["evidence_values"]
    require(peak["pos"] == values["peak_position"], "P07 peak position mismatch")
    require(approx(peak["max_cage_pct"], values["peak_cage_pct"]), "P07 peak CAGE mismatch")


def check_p08(claim: dict[str, Any]) -> None:
    mpra = load_json("results/mpra_crossvalidation_summary.json")
    values = claim["evidence_values"]
    require(approx(mpra["allele_pearson_r"], values["allele_pearson_r"]), "P08 allele_pearson_r mismatch")
    require(approx(mpra["allele_pearson_p"], values["allele_pearson_p"]), "P08 allele_pearson_p mismatch")
    require(approx(mpra["position_pearson_r"], values["position_pearson_r"]), "P08 position_pearson_r mismatch")
    require(approx(mpra["mpra_pearl_vs_nonpearl_p"], values["pearl_vs_nonpearl_p"]), "P08 pearl_vs_nonpearl_p mismatch")
    require(mpra["allele_specific_matches"] == values["allele_specific_matches"], "P08 allele_specific_matches mismatch")


def check_p09(claim: dict[str, Any]) -> None:
    ablation = load_json("results/ablation_effectstrength.json")
    modes = {entry["mode"]: entry for entry in ablation["modes"]}
    values = claim["evidence_values"]
    require(approx(modes["categorical"]["auc"], values["categorical_auc"]), "P09 categorical_auc mismatch")
    require(approx(modes["position-only"]["auc"], values["position_only_auc"]), "P09 position_only_auc mismatch")
    require(approx(modes["random"]["auc"], values["random_auc"]), "P09 random_auc mismatch")


def check_p10(claim: dict[str, Any]) -> None:
    conservation = load_json("results/conservation_pearl_analysis.json")
    gnomad = load_json("results/gnomad_pearl_af_summary.json")
    values = claim["evidence_values"]
    require(approx(conservation["fold_enrichment"], values["phyloP_fold_enrichment"]), "P10 phyloP enrichment mismatch")
    require(approx(conservation["pearl_positions"]["phyloP_mean"], values["pearl_phyloP_mean"]), "P10 pearl_phyloP_mean mismatch")
    require(approx(conservation["background"]["phyloP_mean"], values["background_phyloP_mean"]), "P10 background_phyloP_mean mismatch")
    require(approx(gnomad["af_distribution"]["pct_absent"], values["gnomad_pct_absent"]), "P10 gnomAD pct_absent mismatch")
    require(approx(gnomad["af_distribution"]["pct_ultra_rare_or_absent"], values["gnomad_pct_absent_or_ultra_rare"]), "P10 gnomAD pct_absent_or_ultra_rare mismatch")


CLAIM_CHECKS: dict[str, Callable[[dict[str, Any]], None]] = {
    "P01": check_p01,
    "P02": check_p02,
    "P03": check_p03,
    "P04": check_p04,
    "P05": check_p05,
    "P06": check_p06,
    "P07": check_p07,
    "P08": check_p08,
    "P09": check_p09,
    "P10": check_p10,
}


def main() -> int:
    try:
        index_data = load_json(INDEX_PATH)
        matrix_data = load_json(CLAIM_MATRIX_PATH)
        validate_index(index_data)
        claims_by_id = validate_claim_matrix(matrix_data)
        for claim_id, checker in CLAIM_CHECKS.items():
            require(claim_id in claims_by_id, f"Claim matrix missing required promoted claim: {claim_id}")
            checker(claims_by_id[claim_id])
    except AssertionError as exc:
        print(f"RESULTS CONTRACT FAILED: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - fail closed for integrity tooling
        print(f"RESULTS CONTRACT ERROR: {exc}")
        return 1

    print("RESULTS CONTRACT PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
