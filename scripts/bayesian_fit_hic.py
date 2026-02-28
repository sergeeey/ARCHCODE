#!/usr/bin/env python3
"""
Bayesian optimization of ARCHCODE kinetics parameters (α, γ, K_BASE).

ПОЧЕМУ Optuna GPSampler: 3 параметра в непрерывном пространстве — GP
(Gaussian Process) sampler оптимален для малого числа параметров с дорогой
objective. 200 trials × ~0.5s = ~2 min. Это post-hoc fit на HBB K562 Hi-C,
не cross-locus validation.

Objective: maximize Pearson r (ARCHCODE WT matrix vs K562 Hi-C).
Search space:
  alpha   ∈ [0.5, 1.0]  — MED1 sensitivity
  gamma   ∈ [0.3, 1.5]  — nonlinearity exponent
  k_base  ∈ [0.0005, 0.01] log-scale — unloading probability

Usage:
  python scripts/bayesian_fit_hic.py [--n-trials 200] [--scale both|30kb|95kb]
"""

import sys
import json
import math
import argparse
import time
from pathlib import Path

import numpy as np
from scipy import stats, ndimage

import optuna
from optuna.samplers import GPSampler

# Suppress Optuna INFO logs (trial-by-trial noise)
optuna.logging.set_verbosity(optuna.logging.WARNING)

# === Paths ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "reference"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = PROJECT_ROOT / "plots"

sys.path.insert(0, str(Path(__file__).parent))
from lib.locus_config import resolve_locus_path, load_locus_config


# === Core functions (from correlate_hic_archcode.py, parameterized) ===

class SeededRandom:
    """Mulberry32 PRNG — matches SeededRandom from src/utils/random.ts."""

    def __init__(self, seed: int):
        self._state = seed & 0xFFFFFFFF

    def random(self) -> float:
        self._state = (self._state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self._state
        t = self._imul(t ^ (t >> 15), t | 1)
        t = (t ^ (t + self._imul(t ^ (t >> 7), t | 61))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    @staticmethod
    def _imul(a: int, b: int) -> int:
        a, b = a & 0xFFFFFFFF, b & 0xFFFFFFFF
        return (a * b) & 0xFFFFFFFF


def generate_wt_matrix(
    config: dict,
    alpha: float,
    gamma: float,
    k_base: float,
    seed: int = 0,
) -> np.ndarray:
    """Generate ARCHCODE WT contact matrix with given kinetics parameters.

    ПОЧЕМУ параметризация: correlate_hic_archcode.py использует глобальные
    константы. Для Optuna нам нужно вызывать функцию с разными α, γ, K_BASE
    на каждом trial — поэтому параметры передаются явно.
    """
    w = config["window"]
    n_bins = w["n_bins"]
    sim_start = w["start"]
    resolution = w["resolution_bp"]
    enhancers = config["features"]["enhancers"]
    ctcf_sites = config["features"]["ctcf_sites"]

    background_occ = 0.1
    rng = SeededRandom(seed)

    # Build MED1 occupancy landscape
    base_landscape = []
    for i in range(n_bins):
        genomic_pos = sim_start + i * resolution
        occ = background_occ + rng.random() * 0.05

        for enh in enhancers:
            dist = abs(genomic_pos - enh["position"]) / resolution
            if dist < 5:
                occ += enh["occupancy"] * math.exp(-0.5 * dist * dist)

        base_landscape.append(min(1.0, occ))

    # CTCF barrier bins
    ctcf_bins = [
        math.floor((c["position"] - sim_start) / resolution)
        for c in ctcf_sites
    ]
    ctcf_bins = [b for b in ctcf_bins if 0 <= b < n_bins]

    # Analytical contact map
    matrix = np.zeros((n_bins, n_bins))

    for i in range(n_bins):
        for j in range(i + 1, n_bins):
            dist = j - i
            dist_factor = dist ** (-1.0)

            occ_factor = math.sqrt(base_landscape[i] * base_landscape[j])

            perm = 1.0
            for ctcf in ctcf_bins:
                if ctcf > i and ctcf < j:
                    perm *= 0.15

            kramer = 1 - k_base * (
                1 - alpha * max(0.001, occ_factor) ** gamma
            )

            val = dist_factor * occ_factor * perm * kramer
            matrix[i, j] = val
            matrix[j, i] = val

    max_val = matrix.max()
    if max_val > 0:
        matrix /= max_val

    return matrix


def resize_matrix(matrix: np.ndarray, target_size: int) -> np.ndarray:
    """Resize matrix via bilinear interpolation to match ARCHCODE dimensions."""
    current_size = matrix.shape[0]
    if current_size == target_size:
        return matrix

    zoom_factor = target_size / current_size
    resized = ndimage.zoom(matrix, zoom_factor, order=1)

    if resized.shape[0] != target_size:
        result = np.zeros((target_size, target_size))
        n = min(target_size, resized.shape[0])
        result[:n, :n] = resized[:n, :n]
        resized = result

    resized = (resized + resized.T) / 2.0
    return resized


def flatten_upper_triangle(matrix: np.ndarray, k_min: int = 2) -> np.ndarray:
    """Extract upper triangle excluding near-diagonal (k < k_min)."""
    n = matrix.shape[0]
    values = []
    for i in range(n):
        for j in range(i + k_min, n):
            values.append(matrix[i, j])
    return np.array(values)


def pearson_r(archcode: np.ndarray, hic: np.ndarray, k_min: int = 2) -> float:
    """Compute Pearson r between flattened upper triangles."""
    arch_flat = flatten_upper_triangle(archcode, k_min)
    hic_flat = flatten_upper_triangle(hic, k_min)

    mask = (hic_flat > 0) & np.isfinite(hic_flat) & np.isfinite(arch_flat)
    arch_valid = arch_flat[mask]
    hic_valid = hic_flat[mask]

    if len(arch_valid) < 10:
        return 0.0

    r, _ = stats.pearsonr(arch_valid, hic_valid)
    return float(r)


# === Main ===

def parse_args():
    parser = argparse.ArgumentParser(
        description="Bayesian optimization of ARCHCODE kinetics (α, γ, K_BASE)"
    )
    parser.add_argument(
        "--n-trials", type=int, default=200,
        help="Number of Optuna trials (default: 200)"
    )
    parser.add_argument(
        "--scale", choices=["both", "30kb", "95kb"], default="both",
        help="Which Hi-C scale to optimize (default: both)"
    )
    parser.add_argument(
        "--n-startup", type=int, default=20,
        help="Number of random startup trials before GP kicks in (default: 20)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("  ARCHCODE: Bayesian Parameter Optimization (Optuna)")
    print("=" * 60)
    print(f"  Trials: {args.n_trials}")
    print(f"  Scale:  {args.scale}")
    print(f"  Sampler: GPSampler (n_startup={args.n_startup})")

    # --- Load locus configs ---
    config_30kb = load_locus_config(resolve_locus_path("30kb"))
    config_95kb = load_locus_config(resolve_locus_path("95kb"))
    print(f"\n  30kb config: {config_30kb['id']} ({config_30kb['window']['n_bins']}x{config_30kb['window']['n_bins']})")
    print(f"  95kb config: {config_95kb['id']} ({config_95kb['window']['n_bins']}x{config_95kb['window']['n_bins']})")

    # --- Load & cache Hi-C matrices ---
    print("\n--- Loading Hi-C matrices ---")

    hic_30kb_path = DATA_DIR / "HBB_K562_HiC_1000bp.npy"
    hic_95kb_path = DATA_DIR / "HBB_K562_HiC_95kb_1000bp.npy"

    hic_30kb_raw = np.load(hic_30kb_path)
    hic_95kb_raw = np.load(hic_95kb_path)
    print(f"  30kb Hi-C: {hic_30kb_raw.shape} from {hic_30kb_path.name}")
    print(f"  95kb Hi-C: {hic_95kb_raw.shape} from {hic_95kb_path.name}")

    # Resize to match ARCHCODE bins (cached — done once)
    n_bins_30 = config_30kb["window"]["n_bins"]
    n_bins_95 = config_95kb["window"]["n_bins"]

    hic_30kb = resize_matrix(hic_30kb_raw, n_bins_30)
    hic_95kb = resize_matrix(hic_95kb_raw, n_bins_95)

    # Normalize to [0, 1]
    hic_30kb = hic_30kb / hic_30kb.max() if hic_30kb.max() > 0 else hic_30kb
    hic_95kb = hic_95kb / hic_95kb.max() if hic_95kb.max() > 0 else hic_95kb

    print(f"  30kb resized: {hic_30kb.shape}, range [{hic_30kb.min():.4f}, {hic_30kb.max():.4f}]")
    print(f"  95kb resized: {hic_95kb.shape}, range [{hic_95kb.min():.4f}, {hic_95kb.max():.4f}]")

    # --- Baseline ---
    baseline_alpha = 0.92
    baseline_gamma = 0.80
    baseline_k_base = 0.002

    r_30kb_baseline = pearson_r(
        generate_wt_matrix(config_30kb, baseline_alpha, baseline_gamma, baseline_k_base),
        hic_30kb,
    )
    r_95kb_baseline = pearson_r(
        generate_wt_matrix(config_95kb, baseline_alpha, baseline_gamma, baseline_k_base),
        hic_95kb,
    )

    print(f"\n--- Baseline (α={baseline_alpha}, γ={baseline_gamma}, K={baseline_k_base}) ---")
    print(f"  r_30kb = {r_30kb_baseline:.4f}")
    print(f"  r_95kb = {r_95kb_baseline:.4f}")
    print(f"  r_mean = {(r_30kb_baseline + r_95kb_baseline) / 2:.4f}")

    # --- Objective function ---
    def objective(trial: optuna.Trial) -> float:
        alpha = trial.suggest_float("alpha", 0.5, 1.0)
        gamma = trial.suggest_float("gamma", 0.3, 1.5)
        # ПОЧЕМУ log=True: k_base варьируется на 2 порядка (0.0005–0.01),
        # log-scale обеспечивает равномерный sampling в мультипликативном пространстве
        k_base = trial.suggest_float("k_base", 0.0005, 0.01, log=True)

        if args.scale in ("both", "30kb"):
            arch_30 = generate_wt_matrix(config_30kb, alpha, gamma, k_base)
            r_30 = pearson_r(arch_30, hic_30kb)
        else:
            r_30 = 0.0

        if args.scale in ("both", "95kb"):
            arch_95 = generate_wt_matrix(config_95kb, alpha, gamma, k_base)
            r_95 = pearson_r(arch_95, hic_95kb)
        else:
            r_95 = 0.0

        if args.scale == "both":
            return (r_30 + r_95) / 2
        elif args.scale == "30kb":
            return r_30
        else:
            return r_95

    # --- Run optimization ---
    print(f"\n--- Running Optuna ({args.n_trials} trials) ---")
    t0 = time.time()

    study = optuna.create_study(
        direction="maximize",
        sampler=GPSampler(n_startup_trials=args.n_startup),
        study_name="archcode_hic_fit",
    )
    study.optimize(objective, n_trials=args.n_trials, show_progress_bar=True)

    elapsed = time.time() - t0
    print(f"  Completed in {elapsed:.1f}s ({elapsed / args.n_trials:.2f}s/trial)")

    # --- Best result ---
    best = study.best_trial
    best_alpha = best.params["alpha"]
    best_gamma = best.params["gamma"]
    best_k_base = best.params["k_base"]

    # Recompute individual correlations for best params
    r_30kb_best = pearson_r(
        generate_wt_matrix(config_30kb, best_alpha, best_gamma, best_k_base),
        hic_30kb,
    )
    r_95kb_best = pearson_r(
        generate_wt_matrix(config_95kb, best_alpha, best_gamma, best_k_base),
        hic_95kb,
    )

    print(f"\n{'=' * 60}")
    print(f"  BEST TRIAL (#{best.number}):")
    print(f"    alpha  = {best_alpha:.4f}  (was {baseline_alpha})")
    print(f"    gamma  = {best_gamma:.4f}  (was {baseline_gamma})")
    print(f"    k_base = {best_k_base:.6f}  (was {baseline_k_base})")
    print(f"")
    print(f"    r_30kb = {r_30kb_best:.4f}  (was {r_30kb_baseline:.4f}, Δ={r_30kb_best - r_30kb_baseline:+.4f})")
    print(f"    r_95kb = {r_95kb_best:.4f}  (was {r_95kb_baseline:.4f}, Δ={r_95kb_best - r_95kb_baseline:+.4f})")
    print(f"    r_mean = {(r_30kb_best + r_95kb_best) / 2:.4f}")
    print(f"{'=' * 60}")

    # --- Parameter importance ---
    try:
        importance = optuna.importance.get_param_importances(study)
        print(f"\n--- Parameter Importance ---")
        for param, imp in importance.items():
            print(f"  {param}: {imp:.4f}")
    except Exception:
        importance = {}
        print("\n  (Parameter importance unavailable)")

    # --- Top 10 trials ---
    sorted_trials = sorted(study.trials, key=lambda t: t.value if t.value is not None else -999, reverse=True)
    top_10 = []
    for t in sorted_trials[:10]:
        top_10.append({
            "trial": t.number,
            "value": round(t.value, 6) if t.value is not None else None,
            "alpha": round(t.params["alpha"], 4),
            "gamma": round(t.params["gamma"], 4),
            "k_base": round(t.params["k_base"], 6),
        })

    # --- Save JSON ---
    RESULTS_DIR.mkdir(exist_ok=True)

    delta_30 = r_30kb_best - r_30kb_baseline
    delta_95 = r_95kb_best - r_95kb_baseline

    output = {
        "study_name": "archcode_hic_fit",
        "n_trials": args.n_trials,
        "scale": args.scale,
        "sampler": "GPSampler",
        "n_startup_trials": args.n_startup,
        "elapsed_seconds": round(elapsed, 1),
        "baseline": {
            "alpha": baseline_alpha,
            "gamma": baseline_gamma,
            "k_base": baseline_k_base,
            "r_30kb": round(r_30kb_baseline, 4),
            "r_95kb": round(r_95kb_baseline, 4),
            "r_mean": round((r_30kb_baseline + r_95kb_baseline) / 2, 4),
        },
        "best": {
            "alpha": round(best_alpha, 4),
            "gamma": round(best_gamma, 4),
            "k_base": round(best_k_base, 6),
            "r_30kb": round(r_30kb_best, 4),
            "r_95kb": round(r_95kb_best, 4),
            "r_mean": round((r_30kb_best + r_95kb_best) / 2, 4),
        },
        "improvement": {
            "delta_r_30kb": round(delta_30, 4),
            "delta_r_95kb": round(delta_95, 4),
            "delta_r_mean": round((delta_30 + delta_95) / 2, 4),
        },
        "search_space": {
            "alpha": {"min": 0.5, "max": 1.0, "log": False},
            "gamma": {"min": 0.3, "max": 1.5, "log": False},
            "k_base": {"min": 0.0005, "max": 0.01, "log": True},
        },
        "top_10_trials": top_10,
        "parameter_importance": {k: round(v, 4) for k, v in importance.items()},
        "scientific_note": (
            "Post-hoc optimization on HBB K562 Hi-C. "
            "Cross-locus validation requires Hi-C from CFTR-expressing cells."
        ),
    }

    output_path = RESULTS_DIR / "bayesian_fit_hic.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved: {output_path}")

    # --- Diagnostic plots ---
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        PLOTS_DIR.mkdir(exist_ok=True)

        # 1. Optimization history
        fig, ax = plt.subplots(figsize=(10, 5))
        values = [t.value for t in study.trials if t.value is not None]
        ax.scatter(range(len(values)), values, s=8, alpha=0.5, label="Trial value")
        # Running best
        running_best = []
        best_so_far = -999
        for v in values:
            best_so_far = max(best_so_far, v)
            running_best.append(best_so_far)
        ax.plot(running_best, color="red", linewidth=2, label="Best so far")
        ax.axhline(y=(r_30kb_baseline + r_95kb_baseline) / 2, color="gray",
                    linestyle="--", label=f"Baseline (r={((r_30kb_baseline + r_95kb_baseline) / 2):.4f})")
        ax.set_xlabel("Trial")
        ax.set_ylabel("Pearson r (objective)")
        ax.set_title("Optuna Optimization History")
        ax.legend()
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "bayesian_fit_history.png", dpi=150)
        plt.close(fig)
        print(f"  Plot saved: plots/bayesian_fit_history.png")

        # 2. Slice plots — marginal effect of each parameter
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        for ax_i, param in enumerate(["alpha", "gamma", "k_base"]):
            param_vals = [t.params[param] for t in study.trials if t.value is not None]
            obj_vals = [t.value for t in study.trials if t.value is not None]
            axes[ax_i].scatter(param_vals, obj_vals, s=8, alpha=0.5)
            axes[ax_i].axvline(x=best.params[param], color="red", linestyle="--", alpha=0.7)
            axes[ax_i].set_xlabel(param)
            axes[ax_i].set_ylabel("r (objective)")
            axes[ax_i].set_title(f"Slice: {param}")
            if param == "k_base":
                axes[ax_i].set_xscale("log")
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "bayesian_fit_slices.png", dpi=150)
        plt.close(fig)
        print(f"  Plot saved: plots/bayesian_fit_slices.png")

        # 3. Contour plots (pairwise)
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        pairs = [("alpha", "gamma"), ("alpha", "k_base"), ("gamma", "k_base")]
        for ax_i, (p1, p2) in enumerate(pairs):
            x = [t.params[p1] for t in study.trials if t.value is not None]
            y = [t.params[p2] for t in study.trials if t.value is not None]
            c = [t.value for t in study.trials if t.value is not None]
            sc = axes[ax_i].scatter(x, y, c=c, s=10, alpha=0.6, cmap="viridis")
            axes[ax_i].scatter([best.params[p1]], [best.params[p2]],
                               marker="*", s=200, c="red", edgecolors="black", zorder=5)
            axes[ax_i].set_xlabel(p1)
            axes[ax_i].set_ylabel(p2)
            axes[ax_i].set_title(f"{p1} vs {p2}")
            if p2 == "k_base":
                axes[ax_i].set_yscale("log")
            if p1 == "k_base":
                axes[ax_i].set_xscale("log")
            plt.colorbar(sc, ax=axes[ax_i], label="r")
        fig.tight_layout()
        fig.savefig(PLOTS_DIR / "bayesian_fit_contours.png", dpi=150)
        plt.close(fig)
        print(f"  Plot saved: plots/bayesian_fit_contours.png")

        # 4. Parameter importance bar chart
        if importance:
            fig, ax = plt.subplots(figsize=(6, 4))
            params = list(importance.keys())
            imps = list(importance.values())
            ax.barh(params, imps, color=["#2196F3", "#4CAF50", "#FF9800"][:len(params)])
            ax.set_xlabel("Importance")
            ax.set_title("Parameter Importance (fANOVA)")
            fig.tight_layout()
            fig.savefig(PLOTS_DIR / "bayesian_fit_importance.png", dpi=150)
            plt.close(fig)
            print(f"  Plot saved: plots/bayesian_fit_importance.png")

    except ImportError:
        print("  matplotlib not available — skipping plots")
    except Exception as e:
        print(f"  Plot generation failed: {e}")

    # --- Summary ---
    significant = (delta_30 > 0.02) or (delta_95 > 0.02)
    print(f"\n{'=' * 60}")
    if significant:
        print("  RECOMMENDATION: Update biophysics.ts with optimized parameters")
        print(f"  Δr_30kb={delta_30:+.4f}, Δr_95kb={delta_95:+.4f}")
    else:
        print("  RECOMMENDATION: Keep original parameters (improvement < 0.02)")
        print("  Bayesian search confirms grid-search estimate is near-optimal.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
