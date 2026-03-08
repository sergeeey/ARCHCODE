#!/usr/bin/env python3
"""
LSSIM vs distance to nearest enhancer.

Hypothesis: variants closer to an enhancer show stronger structural effect (lower LSSIM).
Inputs: locus config(s) with features.enhancers[].position, atlas CSV with Position_GRCh38, ARCHCODE_LSSIM.
Output: results/lssim_enhancer_distance_report.json, optional scatter plot for HBB.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
RESULTS_DIR = PROJECT_ROOT / "results"
CONFIG_DIR = PROJECT_ROOT / "config" / "locus"

try:
    from scipy.stats import spearmanr
except ImportError:
    spearmanr = None


def load_locus_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_enhancer_positions(config: dict[str, Any]) -> list[int]:
    """Extract enhancer positions from config. Supports config['features']['enhancers'] or config['enhancers']."""
    enhancers = (config.get("features") or {}).get("enhancers") or config.get("enhancers") or []
    positions = []
    for e in enhancers:
        if isinstance(e, dict) and "position" in e:
            try:
                positions.append(int(e["position"]))
            except (TypeError, ValueError):
                pass
        elif isinstance(e, (int, float)):
            positions.append(int(e))
    return positions


def resolve_baseline_atlas(locus: str) -> Path | None:
    """Resolve canonical atlas path for locus (e.g. HBB -> HBB_Unified_Atlas_95kb.csv)."""
    candidates = sorted(RESULTS_DIR.glob(f"{locus}_Unified_Atlas_*.csv"))
    if not candidates:
        return None
    excluded = ("INVERTED", "POSITION_ONLY", "RANDOM", "UNIFORM_MEDIUM")
    filtered = [p for p in candidates if not any(tok in p.name for tok in excluded)]
    if not filtered:
        filtered = candidates
    canonical = [p for p in filtered if re.match(r"^[0-9]+kb\.csv$", p.name.split("_Unified_Atlas_", 1)[1])]
    pool = canonical if canonical else filtered
    return sorted(pool, key=lambda x: (len(x.name), x.name))[0] if pool else None


def compute_distances_and_lssim(
    atlas_path: Path, enhancer_positions: list[int]
) -> tuple[list[float], list[float], list[int]]:
    """Return (distances, LSSIMs, positions) for each variant in atlas."""
    distances: list[float] = []
    lssims: list[float] = []
    positions: list[int] = []
    if not enhancer_positions:
        return distances, lssims, positions

    with atlas_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                pos = int(row.get("Position_GRCh38") or 0)
            except (ValueError, TypeError):
                continue
            raw_lssim = row.get("ARCHCODE_LSSIM")
            if raw_lssim is None or raw_lssim == "":
                continue
            try:
                lssim = float(raw_lssim)
            except (ValueError, TypeError):
                continue
            min_dist = min(abs(pos - e) for e in enhancer_positions)
            distances.append(float(min_dist))
            lssims.append(lssim)
            positions.append(pos)
    return distances, lssims, positions


def run_locus(locus_id: str, config_path: Path, atlas_path: Path, config_id: str | None = None) -> dict[str, Any]:
    """Compute Spearman(distance, LSSIM) for one locus."""
    config = load_locus_config(config_path)
    enhancers = get_enhancer_positions(config)
    if not enhancers:
        return {"locus": locus_id, "config": config_id or config_path.stem, "error": "No enhancer positions", "n": 0}
    dist, lssim, pos = compute_distances_and_lssim(atlas_path, enhancers)
    if len(dist) < 3:
        return {"locus": locus_id, "config": config_id or config_path.stem, "n": len(dist), "error": "Too few variants"}
    out = {"locus": locus_id, "config": config_id or config_path.stem, "n": len(dist), "n_enhancers": len(enhancers)}
    if spearmanr:
        r, p = spearmanr(dist, lssim)
        out["spearman_rho"] = round(float(r), 6)
        out["spearman_p"] = round(float(p), 6)
    else:
        out["spearman_rho"] = None
        out["spearman_p"] = None
        out["note"] = "scipy not available"
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="LSSIM vs distance to nearest enhancer")
    parser.add_argument(
        "--locus",
        default="95kb",
        help="Locus config alias (default: 95kb = HBB 95kb). Use --all-loci to run all configs with enhancers.",
    )
    parser.add_argument(
        "--all-loci",
        action="store_true",
        help="Run for all locus configs that have enhancers and a matching atlas.",
    )
    parser.add_argument("-o", "--output", type=Path, default=RESULTS_DIR / "lssim_enhancer_distance_report.json")
    parser.add_argument("--plot", action="store_true", help="Write scatter plot for HBB to results/lssim_enhancer_distance_hbb.png")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "hypothesis": "Variants closer to enhancer show lower LSSIM (stronger structural effect).",
        "loci": [],
    }

    if args.all_loci:
        config_files = sorted(CONFIG_DIR.glob("*.json"))
        for cfg_path in config_files:
            stem = cfg_path.stem
            locus_name = stem.split("_")[0].upper()
            if stem.startswith("mouse"):
                locus_name = "MOUSE_HBB"
            config = load_locus_config(cfg_path)
            if not get_enhancer_positions(config):
                continue
            atlas_path = resolve_baseline_atlas(locus_name)
            if not atlas_path or not atlas_path.exists():
                continue
            result = run_locus(locus_name, cfg_path, atlas_path, config_id=stem)
            report["loci"].append(result)
    else:
        # Single locus: resolve config via alias (e.g. 95kb -> hbb_95kb_subTAD.json)
        try:
            from scripts.lib import locus_config as lc
            config_path = lc.resolve_locus_path(args.locus)
        except (ImportError, FileNotFoundError):
            alias = {"95kb": "hbb_95kb_subTAD.json", "30kb": "hbb_30kb_v2.json"}.get(args.locus)
            config_path = CONFIG_DIR / (alias or args.locus if args.locus.endswith(".json") else f"{args.locus}.json")
            if not config_path.exists():
                raise SystemExit(f"Locus config not found: {args.locus}")
        locus_name = config_path.stem.split("_")[0].upper()
        if config_path.stem.startswith("mouse"):
            locus_name = "MOUSE_HBB"
        atlas_path = resolve_baseline_atlas(locus_name)
        if not atlas_path or not atlas_path.exists():
            raise SystemExit(f"Atlas not found for locus {locus_name}")
        result = run_locus(locus_name, config_path, atlas_path)
        report["loci"].append(result)

        if args.plot and result.get("n", 0) >= 3 and "error" not in result:
            config = load_locus_config(config_path)
            enhancers = get_enhancer_positions(config)
            dist, lssim, _ = compute_distances_and_lssim(atlas_path, enhancers)
            try:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.scatter(dist, lssim, alpha=0.5, s=8)
                ax.set_xlabel("Distance to nearest enhancer (bp)")
                ax.set_ylabel("ARCHCODE LSSIM")
                ax.set_title(f"LSSIM vs enhancer distance — {locus_name}\nSpearman ρ = {result.get('spearman_rho', 'N/A')}, p = {result.get('spearman_p', 'N/A')}")
                fig.tight_layout()
                plot_path = RESULTS_DIR / "lssim_enhancer_distance_hbb.png"
                plot_path.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(plot_path, dpi=150)
                plt.close(fig)
                print(f"Plot saved: {plot_path}")
            except ImportError:
                print("matplotlib not available; skipping plot.")

    out_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(f"Report: {out_path}")
    for r in report["loci"]:
        if "error" in r:
            print(f"  {r['locus']}: {r['error']}")
        else:
            print(f"  {r['locus']}: n={r['n']}, Spearman ρ={r.get('spearman_rho')}, p={r.get('spearman_p')}")


if __name__ == "__main__":
    main()
