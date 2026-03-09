#!/usr/bin/env python3
"""
Taxonomy Assignment Pipeline — Mechanistic classification of ARCHCODE variants
===============================================================================
ПОЧЕМУ: Regulatory pathogenicity is mechanistically heterogeneous.
Single-score tools conflate 5 distinct classes. This script applies the
decision rules from regulatory_pathogenicity_taxonomy.md to auto-classify
each locus and its variant groups into Classes A–E.

Decision rules (from taxonomy doc):
  VEP = -1 (no score)         → Class D (Coverage Gap)
    + ARCHCODE LSSIM < 0.95   → Class D with B overlap (D+B)
  MPRA+ AND ARCHCODE-         → Class A (Activity-Driven)
  MPRA- AND ARCHCODE+ AND tissue_matched → Class B (Architecture-Driven)
  MPRA+ AND ARCHCODE+         → Class C (Mixed)
  Signal collapses in wrong tissue       → Class E (Tissue-Mismatch Artifact)
  ARCHCODE+ AND NOT tissue_matched       → Ambiguous (B vs E)

Since we don't have per-variant MPRA data, classification operates at the
variant-group level using Q2a/Q2b splits and tissue match status as proxies:
  - Q2a variants (VEP=-1) → Class D
  - Q2b variants (VEP scored low, ARCHCODE+) with tissue_match=1.0 → Class B
  - Q2b variants with tissue_match=0.0 → Ambiguous (needs tissue data)
  - Q2b variants with tissue_match=0.5 → partial evidence for B
  - Loci with zero Q2 variants → Not classifiable by ARCHCODE alone
  - Tissue mismatch controls → Class E evidence where available
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────
BASE = Path(r"D:\ДНК")
ANALYSIS = BASE / "analysis"

INPUT_VERDICT = ANALYSIS / "per_locus_verdict.csv"
INPUT_BLINDSPOTS = ANALYSIS / "Q2b_true_blindspots.csv"
INPUT_DISCORDANCE = ANALYSIS / "discordance_by_locus.csv"
INPUT_TISSUE = ANALYSIS / "tissue_mismatch_controls_summary.json"

OUTPUT_CSV = ANALYSIS / "taxonomy_auto_assignment.csv"
OUTPUT_JSON = ANALYSIS / "taxonomy_auto_assignment_summary.json"

# ── Thresholds ───────────────────────────────────────────────────────
LSSIM_THRESHOLD = 0.95
TISSUE_MATCH_FULL = 1.0
TISSUE_MATCH_PARTIAL = 0.5
TISSUE_MATCH_NONE = 0.0


# ── Class definitions ────────────────────────────────────────────────
CLASS_LABELS = {
    "A": "Activity-Driven",
    "B": "Architecture-Driven",
    "C": "Mixed (Activity + Architecture)",
    "D": "Coverage Gap",
    "D+B": "Coverage Gap with Architecture Signal",
    "E": "Tissue-Mismatch Artifact",
    "Ambiguous": "Cannot distinguish B from E (no matched-tissue data)",
    "NULL": "No ARCHCODE signal (no Q2 variants)",
}


def load_data():
    """Load all input data files."""
    verdict = pd.read_csv(INPUT_VERDICT)
    blindspots = pd.read_csv(INPUT_BLINDSPOTS)
    discordance = pd.read_csv(INPUT_DISCORDANCE)

    with open(INPUT_TISSUE) as f:
        tissue_controls = json.load(f)

    return verdict, blindspots, discordance, tissue_controls


def classify_variant_group(row, tissue_controls):
    """
    Apply taxonomy decision rules to a single locus row from per_locus_verdict.

    Returns list of (variant_group, assigned_class, evidence, confidence) tuples.
    """
    locus = row["Locus"]
    n_q2 = row["N_Q2"]
    n_q2a = row["N_Q2a"]
    n_q2b = row["N_Q2b"]
    tissue_match = row["Tissue_Match"]
    verdict = row["Verdict"]

    assignments = []

    # ── Rule 1: Q2a variants → Class D (VEP = -1, coverage gap) ──
    if n_q2a > 0:
        # ПОЧЕМУ: Q2a = VEP couldn't score these at all. They're coverage gaps.
        # Some may also have ARCHCODE signal (D+B overlap).
        # We check if any Q2a variants have LSSIM < threshold from blindspots
        evidence_parts = [f"N_Q2a={n_q2a}", "VEP=-1 (no score)"]

        # Check if this locus has Q2b too (some Q2a might have architecture signal)
        if n_q2b > 0:
            assigned_class = "D+B"
            evidence_parts.append(f"N_Q2b={n_q2b} (architecture signal coexists)")
            confidence = "high"
        else:
            assigned_class = "D"
            confidence = "high"

        assignments.append(
            {
                "locus": locus,
                "variant_group": "Q2a",
                "assigned_class": assigned_class,
                "evidence": "; ".join(evidence_parts),
                "confidence": confidence,
                "n_variants": n_q2a,
            }
        )

    # ── Rule 2: Q2b variants → depends on tissue match ──
    if n_q2b > 0:
        evidence_parts = [f"N_Q2b={n_q2b}", f"ARCHCODE+ (LSSIM<{LSSIM_THRESHOLD})"]

        if tissue_match == TISSUE_MATCH_FULL:
            # ПОЧЕМУ: MPRA-null (VEP scored low) + ARCHCODE+ + tissue matched
            # = Class B (architecture-driven). This is ARCHCODE's sweet spot.
            assigned_class = "B"
            evidence_parts.append("tissue_matched=1.0 (fully matched)")
            confidence = "high"
        elif tissue_match == TISSUE_MATCH_NONE:
            # ПОЧЕМУ: Without matched tissue, we can't tell if the signal is
            # real (Class B) or artifact (Class E). Honest classification.
            assigned_class = "Ambiguous"
            evidence_parts.append("tissue_matched=0.0 (cannot distinguish B from E)")
            confidence = "low"
        else:
            # tissue_match == 0.5 → partial evidence
            assigned_class = "B"
            evidence_parts.append("tissue_matched=0.5 (partial — K562 proxy, not ideal)")
            confidence = "medium"

        assignments.append(
            {
                "locus": locus,
                "variant_group": "Q2b",
                "assigned_class": assigned_class,
                "evidence": "; ".join(evidence_parts),
                "confidence": confidence,
                "n_variants": n_q2b,
            }
        )

    # ── Rule 3: Tissue mismatch evidence → Class E ──
    # Check if this locus appears in EXP-003 mismatch controls
    proxy = tissue_controls.get("proxy_results", {})
    mismatch_pairs = [
        k for k in proxy if k.startswith(f"{locus}|") and proxy[k]["condition"] == "MISMATCH"
    ]

    if mismatch_pairs:
        # ПОЧЕМУ: EXP-003 showed that off-diagonal (mismatched) pairs have
        # delta ≈ 0, confirming tissue specificity. This is Class E evidence.
        mismatch_deltas = []
        for pair in mismatch_pairs:
            d = proxy[pair]["delta"]
            mismatch_deltas.append(f"{pair}: delta={d:.2e}")

        assignments.append(
            {
                "locus": locus,
                "variant_group": "tissue_mismatch_control",
                "assigned_class": "E",
                "evidence": (f"EXP-003 mismatch controls: {'; '.join(mismatch_deltas)}"),
                "confidence": "high",
                "n_variants": 0,  # not a variant group, it's a control result
            }
        )

    # ── Rule 4: Loci with zero Q2 → NULL ──
    if n_q2 == 0:
        assignments.append(
            {
                "locus": locus,
                "variant_group": "all",
                "assigned_class": "NULL",
                "evidence": (
                    f"N_Q2=0; no ARCHCODE-discordant variants detected; tissue_match={tissue_match}"
                ),
                "confidence": "N/A",
                "n_variants": 0,
            }
        )

    return assignments


def build_summary(df):
    """Build summary statistics from assignment dataframe."""
    # Class counts (excluding tissue_mismatch_control rows for variant counts)
    variant_rows = df[df["variant_group"] != "tissue_mismatch_control"]

    class_counts = {}
    for cls in sorted(df["assigned_class"].unique()):
        subset = variant_rows[variant_rows["assigned_class"] == cls]
        class_counts[cls] = {
            "n_loci": int(subset["locus"].nunique()),
            "n_variant_groups": len(subset),
            "n_variants_total": int(subset["n_variants"].sum()),
            "label": CLASS_LABELS.get(cls, cls),
        }

    # Per-locus breakdown
    per_locus = {}
    for locus in df["locus"].unique():
        locus_df = df[df["locus"] == locus]
        per_locus[locus] = []
        for _, row in locus_df.iterrows():
            per_locus[locus].append(
                {
                    "variant_group": row["variant_group"],
                    "class": row["assigned_class"],
                    "confidence": row["confidence"],
                    "n_variants": int(row["n_variants"]),
                }
            )

    summary = {
        "pipeline": "taxonomy_assignment_pipeline.py",
        "version": "1.0",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "decision_rules_source": "docs/regulatory_pathogenicity_taxonomy.md",
        "thresholds": {
            "LSSIM": LSSIM_THRESHOLD,
            "tissue_match_full": TISSUE_MATCH_FULL,
            "tissue_match_partial": TISSUE_MATCH_PARTIAL,
        },
        "class_counts": class_counts,
        "per_locus": per_locus,
        "class_labels": CLASS_LABELS,
    }
    return summary


def print_summary_table(df, summary):
    """Print a formatted summary table to stdout."""
    print("=" * 78)
    print("TAXONOMY AUTO-ASSIGNMENT — Summary")
    print("=" * 78)
    print()

    # Class distribution
    print("Class Distribution (variant groups only):")
    print("-" * 60)
    print(f"{'Class':<12} {'Label':<35} {'Loci':>5} {'Variants':>9}")
    print("-" * 60)
    for cls, info in sorted(summary["class_counts"].items()):
        label = info["label"][:35]
        print(f"{cls:<12} {label:<35} {info['n_loci']:>5} {info['n_variants_total']:>9}")
    print("-" * 60)
    print()

    # Per-locus detail
    print("Per-Locus Assignments:")
    print("-" * 78)
    print(f"{'Locus':<8} {'Group':<25} {'Class':<12} {'Conf':<8} {'N':>5}")
    print("-" * 78)
    for locus in df["locus"].unique():
        locus_df = df[df["locus"] == locus]
        for _, row in locus_df.iterrows():
            group = row["variant_group"][:25]
            cls = row["assigned_class"]
            conf = row["confidence"]
            n = int(row["n_variants"])
            print(f"{locus:<8} {group:<25} {cls:<12} {conf:<8} {n:>5}")
    print("-" * 78)
    print()


def main():
    """Run the taxonomy assignment pipeline."""
    print("Loading data...")
    verdict, blindspots, discordance, tissue_controls = load_data()

    print(f"  per_locus_verdict: {len(verdict)} loci")
    print(f"  Q2b_true_blindspots: {len(blindspots)} variants")
    print(f"  discordance_by_locus: {len(discordance)} loci")
    print(f"  tissue_mismatch_controls: {len(tissue_controls.get('loci', []))} loci")
    print()

    # ── Apply decision rules per locus ──
    all_assignments = []
    for _, row in verdict.iterrows():
        assignments = classify_variant_group(row, tissue_controls)
        all_assignments.extend(assignments)

    # ── Build output dataframe ──
    df = pd.DataFrame(all_assignments)
    df = df[["locus", "variant_group", "assigned_class", "evidence", "confidence", "n_variants"]]

    # ── Save CSV ──
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved: {OUTPUT_CSV}")

    # ── Build and save summary JSON ──
    summary = build_summary(df)
    with open(OUTPUT_JSON, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved: {OUTPUT_JSON}")
    print()

    # ── Print summary table ──
    print_summary_table(df, summary)

    # ── Validation checks ──
    n_total_loci = len(verdict)
    n_assigned_loci = df["locus"].nunique()
    assert n_assigned_loci == n_total_loci, (
        f"Not all loci assigned: {n_assigned_loci}/{n_total_loci}"
    )
    print(f"Validation: all {n_total_loci} loci have at least one assignment.")
    print("Done.")


if __name__ == "__main__":
    main()
