"""
Apply per-locus calibrated thresholds to locus config JSONs.

Reads computed thresholds from results/per_locus_thresholds_summary.json
and writes them into the corresponding config/locus/*.json files.

This fixes Blocker B2 from PR Gate review: universal threshold (0.95)
fails on BRCA1 (0.7% FPs). Per-locus calibration at FPR ≤ 1% is mandatory.
"""

import json
from pathlib import Path

PROJECT = Path(__file__).parent.parent

LOCUS_TO_CONFIG = {
    "HBB": "hbb_95kb_subTAD.json",
    "CFTR": "cftr_317kb.json",
    "TP53": "tp53_300kb.json",
    "BRCA1": "brca1_400kb.json",
    "MLH1": "mlh1_300kb.json",
    "LDLR": "ldlr_300kb.json",
    "SCN5A": "scn5a_400kb.json",
    "TERT": "tert_300kb.json",
    "GJB2": "gjb2_300kb.json",
}


def compute_thresholds(entry: dict) -> dict | None:
    """Convert per-locus stats into SSIM threshold config."""
    opt = entry.get("opt_threshold")
    if opt is None:
        return None

    # Use calibrated optimal threshold as the VUS boundary
    # Scale other thresholds proportionally from HBB reference
    # HBB reference: pathogenic=0.85, likely_path=0.92, vus=0.96, likely_ben=0.99
    # Calibrated VUS boundary = opt_threshold (FPR ≤ 1%)
    vus_boundary = round(opt, 4)

    # Pathogenic and LP boundaries scale with signal strength
    delta = entry.get("delta_mean", 0.01)
    if delta < 0.005:
        # Weak signal locus — compress thresholds
        pathogenic = round(vus_boundary - 0.03, 4)
        likely_path = round(vus_boundary - 0.01, 4)
    elif delta < 0.02:
        # Moderate signal
        pathogenic = round(vus_boundary - 0.06, 4)
        likely_path = round(vus_boundary - 0.03, 4)
    else:
        # Strong signal (HBB-like)
        pathogenic = round(vus_boundary - 0.12, 4)
        likely_path = round(vus_boundary - 0.05, 4)

    # Likely benign is always above VUS boundary
    likely_ben = round(min(vus_boundary + 0.02, 0.999), 4)

    return {
        "ssim_pathogenic": pathogenic,
        "ssim_likely_pathogenic": likely_path,
        "ssim_vus": vus_boundary,
        "ssim_likely_benign": likely_ben,
        "note": f"Calibrated at FPR ≤ 1% (opt_threshold={opt:.4f}, sensitivity={entry['opt_sens']:.1%}, tissue={entry['tissue']})"
    }


def main():
    thresholds_path = PROJECT / "results" / "per_locus_thresholds_summary.json"
    with open(thresholds_path) as f:
        all_thresholds = json.load(f)

    updated = 0
    for entry in all_thresholds:
        locus = entry["locus"]
        config_name = LOCUS_TO_CONFIG.get(locus)
        if not config_name:
            continue

        config_path = PROJECT / "config" / "locus" / config_name
        if not config_path.exists():
            print(f"  SKIP {locus}: config not found at {config_path}")
            continue

        thresholds = compute_thresholds(entry)
        if thresholds is None:
            print(f"  SKIP {locus}: no optimal threshold computed")
            continue

        with open(config_path) as f:
            config = json.load(f)

        config["thresholds"] = thresholds

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

        print(f"  OK {locus}: {config_name} → threshold={thresholds['ssim_vus']}"
              f" (FPR≤1%, sens={entry['opt_sens']:.1%})")
        updated += 1

    print(f"\nUpdated {updated} locus configs with per-locus thresholds.")


if __name__ == "__main__":
    main()
