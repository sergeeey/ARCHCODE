#!/usr/bin/env python3
"""
ADR-026: 73bp HBB Cluster Validation

Strict independent validation of hypothesis:
HBB pearl variants are enriched in promoter zone chr11:5227099-5227172 (73bp).

Protocol:
1. Load all HBB variants
2. Extract pearl variants
3. Define fixed zone
4. Calculate enrichment
5. Fisher exact test
6. Permutation test (10,000 samples)
7. Negative controls (random windows, shuffled labels, category-matched)
8. Seed sensitivity (seeds: 1, 7, 21, 42, 100)
9. Verdict: PASS / WEAK / FAIL
10. Check for circularity, selection bias, category leakage

Critical: Honest null result if hypothesis fails.
"""

import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from typing import Dict, Any, List
import json
from pathlib import Path

# Configuration
DATA_PATH = Path("D:/ДНК/results/HBB_Unified_Atlas.csv")
OUTPUT_PATH = Path("D:/ДНК/results/validate_73bp_cluster.json")
ADR_PATH = Path("D:/ДНК/docs/ADR-026_73bp_cluster_validation.md")

# Fixed zone (pre-registered)
ZONE_START = 5227099
ZONE_END = 5227172
ZONE_SIZE = ZONE_END - ZONE_START + 1  # 74bp (73 intervals)

# Test parameters
N_PERMUTATIONS = 10000
SEEDS = [1, 7, 21, 42, 100]
ALPHA = 0.01  # Stringent threshold (p < 0.01)


def load_data() -> pd.DataFrame:
    """Load HBB variant data."""
    df = pd.read_csv(DATA_PATH)
    print(f"✓ Loaded {len(df)} HBB variants from {DATA_PATH.name}")
    return df


def extract_pearls(df: pd.DataFrame) -> pd.DataFrame:
    """Extract pearl variants (Pearl == True)."""
    pearls = df[df["Pearl"] == True].copy()
    print(f"✓ Found {len(pearls)} pearl variants ({len(pearls)/len(df)*100:.1f}% of total)")
    return pearls


def count_in_zone(df: pd.DataFrame, start: int, end: int) -> int:
    """Count variants in genomic zone."""
    in_zone = df[(df["Position_GRCh38"] >= start) & (df["Position_GRCh38"] <= end)]
    return len(in_zone)


def fisher_test(
    pearls_in_zone: int, pearls_total: int, all_in_zone: int, all_total: int
) -> Dict[str, Any]:
    """
    Fisher exact test for enrichment.

    Contingency table:
                In Zone   Outside Zone
    Pearls         a           b          (a+b = pearls_total)
    Non-Pearls     c           d          (c+d = non_pearls_total)
    """
    a = pearls_in_zone
    b = pearls_total - pearls_in_zone
    c = all_in_zone - pearls_in_zone  # Non-pearls in zone
    d = (all_total - pearls_total) - c  # Non-pearls outside zone

    oddsratio, pvalue = fisher_exact([[a, b], [c, d]], alternative="greater")

    return {
        "contingency_table": {
            "pearls_in_zone": a,
            "pearls_outside_zone": b,
            "non_pearls_in_zone": c,
            "non_pearls_outside_zone": d,
        },
        "odds_ratio": float(oddsratio),
        "p_value": float(pvalue),
    }


def permutation_test(
    df: pd.DataFrame, pearls: pd.DataFrame, zone_start: int, zone_end: int, n_perms: int, seed: int
) -> Dict[str, Any]:
    """
    Permutation test: randomly sample N variants (N = number of pearls),
    count how many fall in zone, compute p-value.
    """
    np.random.seed(seed)

    n_pearls = len(pearls)
    observed_in_zone = count_in_zone(pearls, zone_start, zone_end)

    # Generate null distribution
    null_counts = []
    positions = df["Position_GRCh38"].values

    for _ in range(n_perms):
        random_sample = np.random.choice(positions, size=n_pearls, replace=False)
        count = np.sum((random_sample >= zone_start) & (random_sample <= zone_end))
        null_counts.append(count)

    null_counts = np.array(null_counts)
    p_value = np.sum(null_counts >= observed_in_zone) / n_perms

    return {
        "observed_in_zone": int(observed_in_zone),
        "expected_mean": float(null_counts.mean()),
        "expected_std": float(null_counts.std()),
        "p_value": float(p_value),
        "n_permutations": n_perms,
        "seed": seed,
    }


def category_matched_permutation(
    df: pd.DataFrame,
    pearls: pd.DataFrame,
    zone_start: int,
    zone_end: int,
    n_perms: int,
    seed: int,
) -> Dict[str, Any]:
    """
    Category-matched permutation test.

    Null hypothesis: Random variants FROM THE SAME CATEGORY as pearls.

    This controls for category leakage. If pearls = 75% promoter, we sample
    random variants where 75% are also promoter category.

    Example: If 15/20 pearls are promoter, sample 15 random promoter variants
    + 5 random from other categories matching pearl distribution.

    Critical difference from standard permutation:
    - Standard permutation: random from ALL variants (category-blind)
    - Category-matched: random within SAME category distribution (category-aware)
    """
    np.random.seed(seed)

    # Get pearl category distribution
    pearl_categories = pearls["Category"].value_counts().to_dict()

    observed_in_zone = count_in_zone(pearls, zone_start, zone_end)

    null_counts = []

    # Track categories with insufficient controls
    insufficient_categories = {}

    for iteration in range(n_perms):
        # Sample variants matching pearl category distribution
        sampled_variants = []

        for category, count in pearl_categories.items():
            # Get all variants of this category (excluding pearls themselves)
            category_pool = df[(df["Category"] == category) & (df["Pearl"] == False)]

            if len(category_pool) == 0:
                # CRITICAL: No non-pearl variants of this category exist
                # Cannot perform category-matched sampling for this category
                # Skip this category (reduces sample size)
                if category not in insufficient_categories:
                    insufficient_categories[category] = {
                        "pearl_count": count,
                        "available_controls": 0,
                        "action": "SKIPPED (no controls available)",
                    }
                continue  # Skip this category entirely

            elif len(category_pool) < count:
                # If not enough variants, sample with replacement
                if category not in insufficient_categories:
                    insufficient_categories[category] = {
                        "pearl_count": count,
                        "available_controls": len(category_pool),
                        "action": "sampled with replacement",
                    }
                sample = category_pool.sample(n=count, replace=True, random_state=seed + iteration)
            else:
                sample = category_pool.sample(n=count, replace=False, random_state=seed + iteration)

            sampled_variants.append(sample)

        # Combine samples
        sampled_df = pd.concat(sampled_variants, ignore_index=True)

        # Count in zone
        count = count_in_zone(sampled_df, zone_start, zone_end)
        null_counts.append(count)

    null_counts = np.array(null_counts)

    # Check if we have valid permutations
    if len(null_counts) == 0:
        return {
            "observed_in_zone": int(observed_in_zone),
            "expected_mean_category_matched": None,
            "expected_std_category_matched": None,
            "p_value": None,
            "n_permutations": n_perms,
            "seed": seed,
            "pearl_category_distribution": {str(k): int(v) for k, v in pearl_categories.items()},
            "insufficient_categories": insufficient_categories
            if len(insufficient_categories) > 0
            else None,
            "test_validity": "INVALID",
            "warning": "INVALID: No category-matched controls available. All pearl categories lack non-pearl variants.",
            "interpretation": "INVALID: insufficient category-matched controls",
        }

    p_value = np.sum(null_counts >= observed_in_zone) / n_perms

    # Calculate test validity based on skipped categories
    total_pearls = sum(pearl_categories.values())
    skipped_pearls = sum(
        v["pearl_count"] for v in insufficient_categories.values() if v["available_controls"] == 0
    )

    if skipped_pearls == 0:
        test_validity = "VALID"
        warning = None
    elif skipped_pearls < total_pearls:
        test_validity = "PARTIAL"
        warning = (
            f"Category-matched test is PARTIAL: {len(insufficient_categories)} categories have "
            f"insufficient controls. {skipped_pearls}/{total_pearls} pearls skipped. "
            f"Test valid for remaining {total_pearls - skipped_pearls} pearls only."
        )
    else:
        test_validity = "INVALID"
        warning = "INVALID: All pearls belong to categories with no non-pearl controls."

    return {
        "observed_in_zone": int(observed_in_zone),
        "expected_mean_category_matched": float(null_counts.mean()),
        "expected_std_category_matched": float(null_counts.std()),
        "p_value": float(p_value),
        "n_permutations": n_perms,
        "seed": seed,
        "pearl_category_distribution": {str(k): int(v) for k, v in pearl_categories.items()},
        "insufficient_categories": insufficient_categories
        if len(insufficient_categories) > 0
        else None,
        "test_validity": test_validity,
        "warning": warning,
        "interpretation": (
            "PASS: enrichment is positional (not category artifact)"
            if p_value < 0.01
            else "FAIL: enrichment is categorical (not positional)"
            if p_value >= 0.05
            else "WEAK"
        ),
    }


def negative_control_random_windows(
    df: pd.DataFrame, pearls: pd.DataFrame, window_size: int, n_windows: int, seed: int
) -> Dict[str, Any]:
    """
    Negative control: test N random windows of same size as target zone.
    If hypothesis is specific to promoter zone, random windows should NOT show enrichment.
    """
    np.random.seed(seed)

    min_pos = df["Position_GRCh38"].min()
    max_pos = df["Position_GRCh38"].max()

    p_values = []

    for i in range(n_windows):
        # Random window start
        window_start = np.random.randint(min_pos, max_pos - window_size + 1)
        window_end = window_start + window_size - 1

        pearls_in = count_in_zone(pearls, window_start, window_end)
        all_in = count_in_zone(df, window_start, window_end)

        if all_in > 0:
            # Fisher test for this random window
            a = pearls_in
            b = len(pearls) - pearls_in
            c = all_in - pearls_in
            d = (len(df) - len(pearls)) - c

            _, p = fisher_exact([[a, b], [c, d]], alternative="greater")
            p_values.append(p)

    p_values = np.array(p_values)

    # How many random windows show p < 0.05?
    false_positive_rate = np.sum(p_values < 0.05) / len(p_values)

    return {
        "n_windows_tested": n_windows,
        "false_positive_rate_p005": float(false_positive_rate),
        "min_p_value": float(p_values.min()) if len(p_values) > 0 else None,
        "median_p_value": float(np.median(p_values)) if len(p_values) > 0 else None,
    }


def negative_control_shuffled_labels(
    df: pd.DataFrame,
    pearls: pd.DataFrame,
    zone_start: int,
    zone_end: int,
    n_shuffles: int,
    seed: int,
) -> Dict[str, Any]:
    """
    Negative control: shuffle Pearl labels, test enrichment in same zone.
    If positional enrichment is real, shuffled labels should NOT show enrichment.
    """
    np.random.seed(seed)

    p_values = []

    for i in range(n_shuffles):
        # Shuffle Pearl column
        df_shuffled = df.copy()
        df_shuffled["Pearl"] = np.random.permutation(df_shuffled["Pearl"].values)

        pearls_shuffled = df_shuffled[df_shuffled["Pearl"] == True]

        pearls_in = count_in_zone(pearls_shuffled, zone_start, zone_end)
        all_in = count_in_zone(df, zone_start, zone_end)

        a = pearls_in
        b = len(pearls_shuffled) - pearls_in
        c = all_in - pearls_in
        d = (len(df) - len(pearls_shuffled)) - c

        _, p = fisher_exact([[a, b], [c, d]], alternative="greater")
        p_values.append(p)

    p_values = np.array(p_values)

    false_positive_rate = np.sum(p_values < 0.05) / len(p_values)

    return {
        "n_shuffles": n_shuffles,
        "false_positive_rate_p005": float(false_positive_rate),
        "median_p_value": float(np.median(p_values)),
    }


def category_leakage_check(
    df: pd.DataFrame, pearls: pd.DataFrame, zone_start: int, zone_end: int
) -> Dict[str, Any]:
    """
    Check if enrichment is driven by Category distribution.
    If pearls = promoter category AND zone = promoter region → circular logic.
    """
    # Categories in zone vs outside
    df_zone = df[(df["Position_GRCh38"] >= zone_start) & (df["Position_GRCh38"] <= zone_end)]
    df_outside = df[(df["Position_GRCh38"] < zone_start) | (df["Position_GRCh38"] > zone_end)]

    zone_categories = df_zone["Category"].value_counts(normalize=True).to_dict()
    outside_categories = df_outside["Category"].value_counts(normalize=True).to_dict()

    # Pearl category distribution
    pearl_categories = pearls["Category"].value_counts(normalize=True).to_dict()

    # Check if pearls are dominated by a category that's overrepresented in zone
    dominant_pearl_cat = pearls["Category"].mode().values[0] if len(pearls) > 0 else None
    dominant_pearl_frac = pearl_categories.get(dominant_pearl_cat, 0)

    zone_frac = zone_categories.get(dominant_pearl_cat, 0)
    outside_frac = outside_categories.get(dominant_pearl_cat, 0)

    leakage_risk = "HIGH" if (dominant_pearl_frac > 0.5 and zone_frac > 2 * outside_frac) else "LOW"

    return {
        "dominant_pearl_category": str(dominant_pearl_cat),
        "dominant_pearl_fraction": float(dominant_pearl_frac),
        "zone_fraction_of_dominant": float(zone_frac),
        "outside_fraction_of_dominant": float(outside_frac),
        "leakage_risk": leakage_risk,
        "zone_category_distribution": {str(k): float(v) for k, v in zone_categories.items()},
        "pearl_category_distribution": {str(k): float(v) for k, v in pearl_categories.items()},
    }


def seed_sensitivity_test(
    df: pd.DataFrame, pearls: pd.DataFrame, zone_start: int, zone_end: int, seeds: List[int]
) -> Dict[str, Any]:
    """
    Test multiple random seeds for permutation test.
    If result is seed-dependent → unstable, cannot trust.
    """
    results = []

    for seed in seeds:
        perm_result = permutation_test(df, pearls, zone_start, zone_end, N_PERMUTATIONS, seed)
        results.append({"seed": seed, "p_value": perm_result["p_value"]})

    p_values = [r["p_value"] for r in results]
    p_range = max(p_values) - min(p_values)

    # If p-value range crosses significance threshold → unstable
    crosses_threshold = min(p_values) < ALPHA < max(p_values)

    stability = "STABLE" if p_range < 0.01 and not crosses_threshold else "UNSTABLE"

    return {
        "seeds_tested": seeds,
        "p_values": p_values,
        "p_value_range": float(p_range),
        "stability": stability,
        "crosses_threshold": crosses_threshold,
    }


def generate_verdict(
    fisher_p: float,
    perm_p: float,
    cat_matched_p: float,
    cat_matched_validity: str,
    cat_matched_warning: str,
    stability: str,
    leakage_risk: str,
    negative_controls: Dict,
) -> Dict[str, str]:
    """
    Generate final verdict: PASS / WEAK / FAIL.

    Updated with category-matched control (CRITICAL for ADR-027).

    Verdict logic (priority order):
    0. Category-matched test validity check (INVALID/PARTIAL → cannot validate)
    1. Category-matched FAIL (p >= 0.05) → FAIL (enrichment is categorical, not positional)
    2. Category-matched WEAK (0.01 <= p < 0.05) → WEAK (signal exists but weak after category matching)
    3. All tests PASS (incl. cat-matched p < 0.01) → PASS
    4. Otherwise → WEAK or FAIL

    PASS: All tests pass including category-matched p < 0.01 AND validity="VALID"
    WEAK: Category-matched p < 0.05 but >= 0.01, OR other issues, OR validity="PARTIAL"
    FAIL: Category-matched p >= 0.05 (enrichment is purely categorical) OR validity="INVALID"
    """
    # Check negative controls
    random_windows_clean = negative_controls["random_windows"]["false_positive_rate_p005"] < 0.10
    shuffled_labels_clean = negative_controls["shuffled_labels"]["false_positive_rate_p005"] < 0.10

    # PRIORITY 0: Check test validity FIRST (before p-value)
    if cat_matched_validity == "INVALID":
        verdict = "FAIL"
        confidence = "NONE"
        reason = (
            f"Category-matched test INVALID: {cat_matched_warning}. "
            f"Cannot validate positional enrichment hypothesis. "
            f"This is a fundamental data limitation, not a statistical failure."
        )
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reason": reason,
        }

    elif cat_matched_validity == "PARTIAL":
        verdict = "WEAK"
        confidence = "LOW"
        reason = (
            f"Category-matched test PARTIAL: {cat_matched_warning}. "
            f"p-value = {cat_matched_p:.4f}, but test covers only subset of pearls. "
            f"Dominant pearl category (promoter) has no non-pearl controls. "
            f"73bp promoter cluster enrichment CANNOT be validated via category matching."
        )
        return {
            "verdict": verdict,
            "confidence": confidence,
            "reason": reason,
        }

    # PRIORITY 1: Category-matched control (most important test, only if validity="VALID")
    if cat_matched_p >= 0.05:
        verdict = "FAIL"
        confidence = "NONE"
        reason = (
            f"Category-matched control FAILED (p={cat_matched_p:.4f}). "
            f"Enrichment is purely categorical, NOT positional. "
            f"Promoter pearls do NOT enrich in 73bp zone more than random promoter variants. "
            f"This is honest null result #5 (after within-category, Bayesian opt, dual-DL, router)."
        )

    elif cat_matched_p >= 0.01:
        verdict = "WEAK"
        confidence = "LOW"
        reason = (
            f"Category-matched control MARGINAL (p={cat_matched_p:.4f}). "
            f"Signal exists but weak after accounting for category distribution. "
            f"Enrichment is partially positional, but category artifact not fully ruled out."
        )

    # PRIORITY 2: All tests pass (including category-matched)
    elif (
        fisher_p < ALPHA
        and perm_p < ALPHA
        and cat_matched_p < ALPHA
        and stability == "STABLE"
        and leakage_risk == "LOW"
        and random_windows_clean
        and shuffled_labels_clean
    ):
        verdict = "PASS"
        confidence = "HIGH"
        reason = (
            f"All tests PASS: Fisher (p={fisher_p:.6f}), "
            f"Permutation (p={perm_p:.6f}), Category-matched (p={cat_matched_p:.6f}). "
            f"Enrichment is POSITIONAL, not category artifact. "
            f"Stable across seeds, clean negative controls."
        )

    # PRIORITY 3: Partial pass (category-matched OK but other issues)
    elif fisher_p < 0.05 and perm_p < 0.05 and cat_matched_p < 0.01:
        if leakage_risk == "HIGH":
            verdict = "WEAK"
            confidence = "MEDIUM"
            reason = (
                f"Category-matched passed (p={cat_matched_p:.4f}), but leakage risk HIGH. "
                f"Enrichment is positional, but requires cautious interpretation."
            )
        elif stability == "UNSTABLE":
            verdict = "WEAK"
            confidence = "LOW"
            reason = "Category-matched passed, but result is seed-dependent (unstable)"
        elif not random_windows_clean or not shuffled_labels_clean:
            verdict = "WEAK"
            confidence = "LOW"
            reason = "Category-matched passed, but negative controls show false positives"
        else:
            verdict = "WEAK"
            confidence = "MEDIUM"
            reason = "Significant at p < 0.05 but below stringent threshold (p < 0.01)"

    else:
        verdict = "FAIL"
        confidence = "NONE"
        reason = f"Not significant (Fisher p={fisher_p:.4f}, Permutation p={perm_p:.4f})"

    return {"verdict": verdict, "confidence": confidence, "reason": reason}


def main():
    """Run full validation protocol."""
    print("=" * 70)
    print("ADR-026: 73bp HBB Cluster Validation")
    print("=" * 70)
    print()

    # Step 1: Load data
    df = load_data()

    # Step 2: Extract pearls
    pearls = extract_pearls(df)

    # Step 3: Fixed zone
    print(f"✓ Fixed zone: chr11:{ZONE_START}-{ZONE_END} ({ZONE_SIZE}bp)")
    print()

    # Step 4: Calculate enrichment
    pearls_in_zone = count_in_zone(pearls, ZONE_START, ZONE_END)
    all_in_zone = count_in_zone(df, ZONE_START, ZONE_END)

    enrichment_pct = (pearls_in_zone / len(pearls)) * 100 if len(pearls) > 0 else 0

    print(f"Observed:")
    print(f"  Total HBB variants in zone: {all_in_zone}/{len(df)}")
    print(f"  Total pearls in zone: {pearls_in_zone}/{len(pearls)} ({enrichment_pct:.1f}%)")
    print()

    # Step 5: Fisher exact test
    print("Running Fisher exact test...")
    fisher_result = fisher_test(pearls_in_zone, len(pearls), all_in_zone, len(df))
    print(f"  Odds ratio: {fisher_result['odds_ratio']:.2f}")
    print(f"  p-value: {fisher_result['p_value']:.6f}")
    print()

    # Step 6: Permutation test (seed 42 for primary)
    print(f"Running permutation test ({N_PERMUTATIONS} samples, seed=42)...")
    perm_result = permutation_test(df, pearls, ZONE_START, ZONE_END, N_PERMUTATIONS, seed=42)
    print(f"  Observed in zone: {perm_result['observed_in_zone']}")
    print(
        f"  Expected (mean ± std): {perm_result['expected_mean']:.2f} ± {perm_result['expected_std']:.2f}"
    )
    print(f"  p-value: {perm_result['p_value']:.6f}")
    print()

    # Step 6b: Category-matched permutation test (CRITICAL for category leakage)
    print(f"Running category-matched permutation test ({N_PERMUTATIONS} samples, seed=42)...")
    cat_matched_result = category_matched_permutation(
        df, pearls, ZONE_START, ZONE_END, N_PERMUTATIONS, seed=42
    )
    print(f"  Observed in zone: {cat_matched_result['observed_in_zone']}")
    print(
        f"  Expected (category-matched): {cat_matched_result['expected_mean_category_matched']:.2f} ± {cat_matched_result['expected_std_category_matched']:.2f}"
    )
    print(f"  p-value: {cat_matched_result['p_value']:.6f}")
    print(f"  Pearl categories: {cat_matched_result['pearl_category_distribution']}")
    print(f"  Interpretation: {cat_matched_result['interpretation']}")
    print()

    # Step 7a: Negative control - random windows
    print("Negative control: random windows (100 samples)...")
    neg_random = negative_control_random_windows(df, pearls, ZONE_SIZE, 100, seed=42)
    print(f"  False positive rate (p<0.05): {neg_random['false_positive_rate_p005']:.2%}")
    print(f"  Median p-value: {neg_random['median_p_value']:.4f}")
    print()

    # Step 7b: Negative control - shuffled labels
    print("Negative control: shuffled labels (100 shuffles)...")
    neg_shuffled = negative_control_shuffled_labels(df, pearls, ZONE_START, ZONE_END, 100, seed=42)
    print(f"  False positive rate (p<0.05): {neg_shuffled['false_positive_rate_p005']:.2%}")
    print(f"  Median p-value: {neg_shuffled['median_p_value']:.4f}")
    print()

    # Step 7c: Category leakage check
    print("Category leakage check...")
    leakage = category_leakage_check(df, pearls, ZONE_START, ZONE_END)
    print(
        f"  Dominant pearl category: {leakage['dominant_pearl_category']} ({leakage['dominant_pearl_fraction']:.1%})"
    )
    print(f"  Zone fraction: {leakage['zone_fraction_of_dominant']:.1%}")
    print(f"  Outside fraction: {leakage['outside_fraction_of_dominant']:.1%}")
    print(f"  Leakage risk: {leakage['leakage_risk']}")
    print()

    # Step 8: Seed sensitivity
    print(f"Seed sensitivity test ({len(SEEDS)} seeds)...")
    sensitivity = seed_sensitivity_test(df, pearls, ZONE_START, ZONE_END, SEEDS)
    print(f"  p-value range: {sensitivity['p_value_range']:.6f}")
    print(f"  Stability: {sensitivity['stability']}")
    print(f"  Crosses threshold: {sensitivity['crosses_threshold']}")
    print()

    # Step 9: Generate verdict (updated with category-matched control)
    negative_controls = {"random_windows": neg_random, "shuffled_labels": neg_shuffled}

    verdict_result = generate_verdict(
        fisher_result["p_value"],
        perm_result["p_value"],
        cat_matched_result["p_value"],  # CRITICAL: category-matched control
        cat_matched_result["test_validity"],  # NEW: check validity before p-value
        cat_matched_result.get("warning", ""),  # NEW: include warning message
        sensitivity["stability"],
        leakage["leakage_risk"],
        negative_controls,
    )

    # Step 10: Save results
    output = {
        "metadata": {
            "hypothesis": "HBB pearl variants enriched in promoter zone chr11:5227099-5227172",
            "zone": {
                "chromosome": "chr11",
                "start": ZONE_START,
                "end": ZONE_END,
                "size_bp": ZONE_SIZE,
            },
            "data_source": str(DATA_PATH),
            "n_variants_total": len(df),
            "n_pearls_total": len(pearls),
        },
        "observed": {
            "variants_in_zone": all_in_zone,
            "pearls_in_zone": pearls_in_zone,
            "enrichment_percent": float(enrichment_pct),
        },
        "fisher_exact_test": fisher_result,
        "permutation_test": perm_result,
        "category_matched_permutation": cat_matched_result,  # ADR-027 critical test
        "negative_controls": negative_controls,
        "category_leakage": leakage,
        "seed_sensitivity": sensitivity,
        "verdict": verdict_result,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print(f"Status: {verdict_result['verdict']}")
    print(f"Confidence: {verdict_result['confidence']}")
    print(f"Reason: {verdict_result['reason']}")
    print()
    print(f"✓ Results saved: {OUTPUT_PATH}")
    print()

    # Print pearls in zone for manual inspection
    if pearls_in_zone > 0:
        print("Pearls in zone:")
        pearls_zone = pearls[
            (pearls["Position_GRCh38"] >= ZONE_START) & (pearls["Position_GRCh38"] <= ZONE_END)
        ]
        print(
            pearls_zone[["ClinVar_ID", "Position_GRCh38", "HGVS_c", "Category"]].to_string(
                index=False
            )
        )
        print()

    return output


if __name__ == "__main__":
    result = main()
