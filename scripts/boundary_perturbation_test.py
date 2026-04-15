"""
Boundary Perturbation Test
===========================
Tests: do CTCF boundary perturbations produce structural signals
that cannot be explained by simple baselines?

Hypothesis: variants at CTCF boundary positions produce disproportionately
large 3D perturbations that are specific to real architecture (not shuffled).

Verdict:
- PASS: boundary ΔSSIM >> non-boundary (p<0.05, d>0.5) AND signal dies on shuffled
- FAIL: boundary ≈ non-boundary OR signal survives shuffled
"""

import json
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import time

print("=" * 70)
print("BOUNDARY PERTURBATION TEST")
print("=" * 70)

# ============================================================
# CONSTANTS — exact TypeScript formula
# ============================================================

K_BASE = 0.002
DEFAULT_ALPHA = 0.92
DEFAULT_GAMMA = 0.8
BACKGROUND_OCCUPANCY = 0.1
CTCF_INSULATION = 0.15


def build_matrix(occupancy, ctcf_bins, n_bins):
    """Vectorized contact matrix — exact TypeScript formula."""
    dist_factor = np.zeros((n_bins, n_bins))
    for i in range(n_bins):
        for j in range(i+1, n_bins):
            dist_factor[i,j] = (j-i) ** (-1.0)
            dist_factor[j,i] = dist_factor[i,j]
    
    occ_factor = np.sqrt(np.outer(occupancy, occupancy))
    
    perm = np.ones((n_bins, n_bins))
    for ctcf in ctcf_bins:
        mask = (np.arange(n_bins)[:, None] < ctcf) & (np.arange(n_bins)[None, :] > ctcf)
        perm[mask] *= CTCF_INSULATION
    
    kramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * np.power(np.maximum(0.001, occ_factor), DEFAULT_GAMMA))
    return dist_factor * occ_factor * perm * kramer


def compute_ssim(ref_matrix, mut_matrix):
    """Global SSIM between two matrices."""
    flat_r = ref_matrix.flatten()
    flat_m = mut_matrix.flatten()
    mu_r, mu_m = flat_r.mean(), flat_m.mean()
    sig_r2, sig_m2 = flat_r.var(), flat_m.var()
    sig_rm = ((flat_r - mu_r) * (flat_m - mu_m)).mean()
    return ((2*mu_r*mu_m + 0.0001) * (2*sig_rm + 0.0009)) / \
           ((mu_r**2 + mu_m**2 + 0.0001) * (sig_r2 + sig_m2 + 0.0009))


def build_landscape(config, seed=42):
    """Build MED1 occupancy landscape from config."""
    rng = np.random.default_rng(seed)
    n_bins = config["window"]["n_bins"]
    window_start = config["window"]["start"]
    resolution = config["window"]["resolution_bp"]
    
    enhancers = [(e["position"], e["occupancy"]) for e in config["features"].get("enhancers", [])]
    
    landscape = np.zeros(n_bins)
    for i in range(n_bins):
        pos = window_start + i * resolution
        occ = BACKGROUND_OCCUPANCY + rng.random() * 0.05
        for enh_pos, enh_occ in enhancers:
            dist = abs(pos - enh_pos) / resolution
            if dist < 5:
                occ += enh_occ * np.exp(-0.5 * dist * dist)
        landscape[i] = min(1.0, occ)
    
    return landscape, window_start, resolution, n_bins


def get_ctcf_bins(config):
    """Get CTCF bin indices from config."""
    window_start = config["window"]["start"]
    resolution = config["window"]["resolution_bp"]
    n_bins = config["window"]["n_bins"]
    
    ctcf_sites = config["features"].get("ctcf_sites", [])
    bins = []
    for c in ctcf_sites:
        b = int((c["position"] - window_start) // resolution)
        if 0 <= b < n_bins:
            bins.append({"bin": b, "position": c["position"], "name": c.get("name", "")})
    return bins


def perturb_boundary(ctcf_bins, landscape, perturbation_type):
    """Apply a specific perturbation to CTCF configuration."""
    perturbed_bins = [c["bin"] for c in ctcf_bins]
    
    if perturbation_type == "delete_one":
        # Delete the strongest CTCF site
        if ctcf_bins:
            # Remove the first (typically strongest) CTCF
            perturbed_bins = [c["bin"] for c in ctcf_bins[1:]]
    
    elif perturbation_type == "weaken_all":
        # Weaken all CTCF by 50% — simulate by removing half randomly
        np.random.seed(42)
        n_remove = max(1, len(perturbed_bins) // 2)
        to_remove = set(np.random.choice(perturbed_bins, size=n_remove, replace=False))
        perturbed_bins = [b for b in perturbed_bins if b not in to_remove]
    
    elif perturbation_type == "shift_all":
        # Shift all CTCF by 1 bin (600bp)
        perturbed_bins = [b + 1 for b in perturbed_bins if b + 1 < len(landscape)]
    
    elif perturbation_type == "flip_half":
        # Flip orientation doesn't affect insulation in our model,
        # so this tests whether orientation matters — it shouldn't
        pass  # No change expected
    
    elif perturbation_type == "random_reposition":
        # Randomly reposition CTCF sites
        n_bins = len(landscape)
        n_ctcf = len(ctcf_bins)
        perturbed_bins = list(np.random.choice(range(1, n_bins-1), size=min(n_ctcf, n_bins-2), replace=False))
    
    return perturbed_bins


# ============================================================
# LOAD CONFIGS
# ============================================================

config_dir = Path("D:/ДНК/config/locus")
config_files = list(config_dir.glob("hbb*.json"))
print(f"\nFound {len(config_files)} HBB configs")

all_results = []

for config_file in config_files:
    print(f"\n{'=' * 70}")
    print(f"Testing: {config_file.name}")
    print(f"{'=' * 70}")
    
    with open(config_file) as f:
        config = json.load(f)
    
    n_bins = config["window"]["n_bins"]
    resolution = config["window"]["resolution_bp"]
    window_start = config["window"]["start"]
    ctcf_bins = get_ctcf_bins(config)
    
    print(f"  Window: {n_bins} bins × {resolution}bp = {n_bins*resolution//1000}kb")
    print(f"  CTCF sites: {len(ctcf_bins)}")
    
    if len(ctcf_bins) < 2:
        print(f"  ⚠️  Too few CTCF sites, skipping")
        continue
    
    # Build landscape
    landscape, ws, res, nb = build_landscape(config, seed=42)
    
    # REF matrix (real CTCF)
    ref_ctcf = [c["bin"] for c in ctcf_bins]
    ref_matrix = build_matrix(landscape, ref_ctcf, nb)
    ref_max = ref_matrix.max()
    if ref_max > 0:
        ref_matrix /= ref_max
    
    # ============================================================
    # Test 1: Boundary perturbations (real architecture)
    # ============================================================
    
    perturbation_types = ["delete_one", "weaken_all", "shift_all", "random_reposition"]
    boundary_deltas = {}
    
    for pert in perturbation_types:
        perturbed_bins = perturb_boundary(ctcf_bins, landscape, pert)
        
        if len(perturbed_bins) == 0:
            boundary_deltas[pert] = 0.0
            continue
        
        mut_matrix = build_matrix(landscape, perturbed_bins, nb)
        mut_max = mut_matrix.max()
        if mut_max > 0:
            mut_matrix /= mut_max
        
        ssim = compute_ssim(ref_matrix, mut_matrix)
        delta = 1.0 - ssim
        boundary_deltas[pert] = delta
        
        print(f"  {pert:<20} ΔSSIM = {delta:.6f}  (SSIM = {ssim:.6f})")
    
    # ============================================================
    # Test 2: Non-boundary control (random bin perturbations)
    # ============================================================
    
    n_controls = 100
    control_deltas = []
    np.random.seed(42)
    
    for _ in range(n_controls):
        # Random single-bin occupancy perturbation
        perturbed_occ = landscape.copy()
        bin_idx = np.random.randint(1, nb-1)
        perturbed_occ[bin_idx] *= 0.5  # 50% reduction
        
        ctrl_matrix = build_matrix(perturbed_occ, ref_ctcf, nb)
        ctrl_max = ctrl_matrix.max()
        if ctrl_max > 0:
            ctrl_matrix /= ctrl_max
        
        ssim = compute_ssim(ref_matrix, ctrl_matrix)
        control_deltas.append(1.0 - ssim)
    
    control_deltas = np.array(control_deltas)
    print(f"\n  Non-boundary control (n={n_controls}):")
    print(f"    Mean ΔSSIM = {control_deltas.mean():.6f} ± {control_deltas.std():.6f}")
    print(f"    Range = [{control_deltas.min():.6f}, {control_deltas.max():.6f}]")
    
    # ============================================================
    # Test 3: Shuffled architecture specificity
    # ============================================================
    
    # Shuffle CTCF positions, apply same perturbations
    real_ctcf_positions = sorted([c["position"] for c in ctcf_bins])
    real_distances = np.diff(real_ctcf_positions)
    
    # Generate one shuffled config
    np.random.seed(123)
    n_ctcf = len(ctcf_bins)
    shuffled_positions = [window_start + 500]
    for _ in range(n_ctcf - 1):
        d = np.random.choice(real_distances) + np.random.normal(0, 200)
        d = max(500, d)
        new_pos = shuffled_positions[-1] + d
        if new_pos > window_start + nb * res - 500:
            break
        shuffled_positions.append(new_pos)
    while len(shuffled_positions) < n_ctcf:
        shuffled_positions.append(np.random.randint(window_start + 500, window_start + nb * res - 500))
    shuffled_positions = sorted(shuffled_positions[:n_ctcf])
    shuffled_ctcf_bins = [int((p - window_start) // res) for p in shuffled_positions]
    
    # REF shuffled matrix
    shuf_ref_matrix = build_matrix(landscape, shuffled_ctcf_bins, nb)
    shuf_ref_max = shuf_ref_matrix.max()
    if shuf_ref_max > 0:
        shuf_ref_matrix /= shuf_ref_max
    
    # Delete one shuffled CTCF
    shuf_perturbed = shuffled_ctcf_bins[1:] if len(shuffled_ctcf_bins) > 1 else []
    if shuf_perturbed:
        shuf_mut_matrix = build_matrix(landscape, shuf_perturbed, nb)
        shuf_mut_max = shuf_mut_matrix.max()
        if shuf_mut_max > 0:
            shuf_mut_matrix /= shuf_mut_max
        shuffled_delta = 1.0 - compute_ssim(shuf_ref_matrix, shuf_mut_matrix)
    else:
        shuffled_delta = 0.0
    
    print(f"\n  Shuffled architecture (delete_one):")
    print(f"    ΔSSIM = {shuffled_delta:.6f}")
    
    # ============================================================
    # Verdict
    # ============================================================
    
    # Compare boundary vs control
    delete_delta = boundary_deltas.get("delete_one", 0)
    
    # Mann-Whitney: is delete_one delta significantly > control distribution?
    control_with_perturbation = np.concatenate([control_deltas, [delete_delta]])
    labels = np.concatenate([np.zeros(n_controls), np.ones(1)])
    
    # t-test: delete_one delta vs control mean
    if control_deltas.std() > 0:
        t_stat = (delete_delta - control_deltas.mean()) / (control_deltas.std() / np.sqrt(n_controls))
        # One-sided p-value approximation
        p_val = 1 - stats.norm.cdf(t_stat)
    else:
        t_stat = 0
        p_val = 1.0
    
    # Cohen's d
    pooled_std = control_deltas.std()
    cohens_d = (delete_delta - control_deltas.mean()) / pooled_std if pooled_std > 0 else 0
    
    # Specificity test: is real architecture delta > shuffled delta?
    specificity = delete_delta > shuffled_delta
    
    verdict = "PASS" if (p_val < 0.05 and cohens_d > 0.5 and specificity) else \
              "WARNING" if (p_val < 0.05 or cohens_d > 0.5) else "FAIL"
    
    result = {
        "config": config_file.name,
        "n_ctcf": len(ctcf_bins),
        "boundary_deltas": {k: float(v) for k, v in boundary_deltas.items()},
        "control_mean_delta": float(control_deltas.mean()),
        "control_std_delta": float(control_deltas.std()),
        "shuffled_delta": float(shuffled_delta),
        "t_stat": float(t_stat),
        "p_value": float(p_val),
        "cohens_d": float(cohens_d),
        "specificity": bool(specificity),
        "verdict": verdict,
    }
    
    all_results.append(result)
    print(f"\n  Verdict: {verdict}")
    print(f"  t = {t_stat:.2f}, p = {p_val:.6f}, d = {cohens_d:.2f}")
    print(f"  Real > Shuffled: {specificity}")

# ============================================================
# SAVE
# ============================================================

out_dir = Path("D:/ДНК/validation_suite/results")
out_dir.mkdir(exist_ok=True)

with open(out_dir / "boundary_perturbation_test.json", "w") as f:
    json.dump({"results": all_results}, f, indent=2)

# Summary CSV
csv_rows = []
for r in all_results:
    csv_rows.append({
        "config": r["config"],
        "n_ctcf": r["n_ctcf"],
        "delete_one_delta": r["boundary_deltas"].get("delete_one", 0),
        "weaken_all_delta": r["boundary_deltas"].get("weaken_all", 0),
        "shift_all_delta": r["boundary_deltas"].get("shift_all", 0),
        "random_delta": r["boundary_deltas"].get("random_reposition", 0),
        "control_mean": r["control_mean_delta"],
        "control_std": r["control_std_delta"],
        "shuffled_delta": r["shuffled_delta"],
        "t_stat": r["t_stat"],
        "p_value": r["p_value"],
        "cohens_d": r["cohens_d"],
        "specificity": r["specificity"],
        "verdict": r["verdict"],
    })
pd.DataFrame(csv_rows).to_csv(out_dir / "boundary_perturbation_summary.csv", index=False)

# ============================================================
# OVERALL VERDICT
# ============================================================

print(f"\n{'=' * 70}")
print("OVERALL VERDICT")
print(f"{'=' * 70}")

pass_count = sum(1 for r in all_results if r["verdict"] == "PASS")
warn_count = sum(1 for r in all_results if r["verdict"] == "WARNING")
fail_count = sum(1 for r in all_results if r["verdict"] == "FAIL")

for r in all_results:
    print(f"  {r['config']:<30} {r['verdict']:<10} "
          f"ΔSSIM={r['boundary_deltas'].get('delete_one', 0):.6f} "
          f"(control={r['control_mean_delta']:.6f}, shuffled={r['shuffled_delta']:.6f})")

print(f"\n  PASS: {pass_count}, WARNING: {warn_count}, FAIL: {fail_count}")

if pass_count > fail_count:
    overall = "PASS"
    overall_detail = f"Boundary perturbations are detectable and specific to real architecture in {pass_count}/{len(all_results)} configs."
else:
    overall = "FAIL"
    overall_detail = f"Boundary perturbations are not reliably distinguishable from non-boundary perturbations."

print(f"\n  Overall: {overall}")
print(f"  {overall_detail}")
