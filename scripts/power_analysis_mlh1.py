#!/usr/bin/env python3
"""
MLH1 Post-hoc Power Analysis
============================

Computes the sample size required for MLH1 AlphaGenome CAGE pathogenic-vs-benign
comparison to survive the Bonferroni-corrected threshold (α=0.007 for 7 tests).

Referenced from manuscript v2.18 (Methods Section 2.5, ADR-036).

Observed data (results/alphagenome_batch_cage_9loci.json):
- n_pathogenic = 15, n_benign = 15
- mean_path = 1.195, mean_ben = 0.324 (ratio 3.7×)
- Mann-Whitney U = 168.0, p = 0.0225

Output: n_per_group ≈ 84, n_total ≈ 167 (5.6× current).
"""

import numpy as np
from scipy import stats


def mlh1_power_analysis():
    # Observed MLH1 statistics
    n_path = 15
    n_ben = 15
    p_observed = 0.0225

    N_total = n_path + n_ben

    # Step 1: Recover Z-score from p-value (two-tailed)
    z_observed = stats.norm.isf(p_observed / 2)

    # Step 2: Effect size estimation
    # Cohen's r = Z / sqrt(N)  (rank-biserial / Cohen convention)
    r_effect = z_observed / np.sqrt(N_total)

    # Cohen's d equivalent for normal-approximation Mann-Whitney
    d_observed = z_observed * np.sqrt(2 / N_total)

    # Step 3: Power analysis for Bonferroni target
    alpha_target = 0.007  # 0.05 / 7 tests
    power_target = 0.80

    z_alpha = stats.norm.isf(alpha_target / 2)
    z_beta = stats.norm.isf(1 - power_target)

    # Z-test approximation (two-sample, equal groups)
    n_per_group_z = 2 * ((z_alpha + z_beta) / d_observed) ** 2

    # Mann-Whitney correction: ARE = 0.864 vs t-test (for normal data)
    # Conservative: divide by ARE to inflate required N
    n_per_group_mw = n_per_group_z / 0.864
    n_total_mw = 2 * n_per_group_mw

    increase_factor = n_total_mw / N_total

    return {
        "observed": {
            "n_path": n_path,
            "n_ben": n_ben,
            "N_total": N_total,
            "p_value": p_observed,
            "z_score": float(z_observed),
            "effect_size_r": float(r_effect),
            "cohens_d": float(d_observed),
        },
        "target": {
            "alpha": alpha_target,
            "power": power_target,
            "z_alpha": float(z_alpha),
            "z_beta": float(z_beta),
        },
        "required": {
            "n_per_group_ztest": float(n_per_group_z),
            "n_per_group_mw": float(n_per_group_mw),
            "n_total_mw": float(n_total_mw),
            "increase_factor": float(increase_factor),
        },
    }


if __name__ == "__main__":
    result = mlh1_power_analysis()

    print("=" * 60)
    print("MLH1 Post-hoc Power Analysis (Bonferroni α=0.007)")
    print("=" * 60)

    o = result["observed"]
    print(f"\nObserved (current cohort):")
    print(f"  N total = {o['N_total']} ({o['n_path']} path + {o['n_ben']} ben)")
    print(f"  Mann-Whitney p = {o['p_value']:.4f}")
    print(f"  Recovered Z = {o['z_score']:.3f}")
    print(f"  Effect size r = {o['effect_size_r']:.3f} (medium)")
    print(f"  Cohen's d ≈ {o['cohens_d']:.3f}")

    t = result["target"]
    print(f"\nTarget:")
    print(f"  α = {t['alpha']} (Bonferroni 7 tests)")
    print(f"  Power = {t['power']}")
    print(f"  z_α = {t['z_alpha']:.3f}")
    print(f"  z_β = {t['z_beta']:.3f}")

    r = result["required"]
    print(f"\nRequired (Mann-Whitney, ARE=0.864):")
    print(f"  n per group ≈ {r['n_per_group_mw']:.0f}")
    print(f"  N total ≈ {r['n_total_mw']:.0f}")
    print(f"  Increase factor: {r['increase_factor']:.1f}×")
    print()
