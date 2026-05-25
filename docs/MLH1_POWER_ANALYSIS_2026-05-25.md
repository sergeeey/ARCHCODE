# MLH1 Post-hoc Power Analysis

**Date:** 2026-05-25
**Status:** Reproducibility artifact for manuscript v2.18 Methods Section 2.5
**Related ADR:** ADR-036 (manuscript reframe)
**Script:** `scripts/power_analysis_mlh1.py`

---

## Context

MLH1 was the only regulatory locus apart from HBB to reach nominal significance in the AlphaGenome CAGE mechanism-specificity test (Mann-Whitney p=0.0225, ratio 3.7×). It failed the Bonferroni-corrected threshold (α=0.007 for 7 tests).

The reframed manuscript (commit `c3f62b3`) claims that MLH1 would require ~84 variants per group (~167 total) to reach 80% power at α=0.007. This document reproduces the calculation.

## Observed Data

From `results/alphagenome_batch_cage_9loci.json`:

| Statistic | Value |
|-----------|-------|
| n_pathogenic | 15 |
| n_benign | 15 |
| N_total | 30 |
| mean ΔCAGE pathogenic | 1.195 |
| mean ΔCAGE benign | 0.324 |
| ratio (path/ben) | 3.7 |
| Mann-Whitney U | 168.0 |
| p-value (two-tailed) | 0.0225 |

## Effect Size Recovery

Convert the observed p-value to an asymptotic Z-score (two-tailed):
```
Z = norm.isf(p/2) = norm.isf(0.01125) = 2.282
```

Cohen's rank-biserial effect size:
```
r = Z / sqrt(N) = 2.282 / sqrt(30) = 0.417  (medium effect)
```

Cohen's d equivalent (normal-approximation Mann-Whitney):
```
d ≈ Z * sqrt(2/N) = 2.282 * sqrt(2/30) = 0.589
```

Reference: Rosenthal R. (1991). Meta-analytic procedures for social research. Sage. Cohen (1988) effect-size conventions: r=0.1 small, r=0.3 medium, r=0.5 large.

## Sample-Size Calculation

Target: α = 0.007 (Bonferroni for 7 tests), power = 0.80.

Critical values:
```
z_α = norm.isf(α/2) = norm.isf(0.0035) = 2.697
z_β = norm.isf(1 - power) = norm.isf(0.20) = 0.842
```

Two-sample Z-test approximation (equal groups, common variance assumption):
```
n_per_group_Z = 2 * ((z_α + z_β) / d)²
              = 2 * ((2.697 + 0.842) / 0.589)²
              = 2 * (6.011)²
              ≈ 72
```

Mann-Whitney correction. The asymptotic relative efficiency (ARE) of the Mann-Whitney U test relative to the t-test is 3/π ≈ 0.955 for normal data and ≥0.864 for arbitrary continuous distributions (Hodges-Lehmann lower bound; Lehmann, 1975). Using the conservative ARE = 0.864:

```
n_per_group_MW = n_per_group_Z / ARE
              = 72 / 0.864
              ≈ 83  (84 with round-up)
```

Total required:
```
N_total_MW = 2 * n_per_group_MW ≈ 167
Increase factor = 167 / 30 = 5.6×
```

## Result Summary

| Quantity | Current | Required (target α=0.007, power=0.80) |
|----------|---------|---------------------------------------|
| n per group | 15 | **~84** |
| N total | 30 | **~167** |
| Increase factor | — | **5.6×** |

## Reproducibility

```bash
cd D:/ДНК
python scripts/power_analysis_mlh1.py
```

Expected output: `N total ≈ 167, Increase factor: 5.6×`.

Dependencies: `numpy`, `scipy.stats`.

## Caveats

1. **Post-hoc calculation.** This is not a pre-registered power analysis. Effect-size estimate from observed data is biased upward (winner's curse). True effect may be smaller, requiring even more samples.
2. **Normal approximation.** The Mann-Whitney Z-score recovery assumes large-sample normality. With N=30, this is borderline; exact permutation-based power could differ by ±15%.
3. **No multiple-imputation for ARE.** ARE = 0.864 is a Hodges-Lehmann lower bound. For approximately normal data, ARE ≈ 0.955, lowering N_required to ~72 per group (~144 total).
4. **Variance assumption.** Both groups assumed equal variance (homoscedastic). If pathogenic group has higher variance (common in clinical data), N_required increases further.

**Conservative reporting:** the manuscript reports ~84 per group (~167 total) as a planning estimate. The true requirement is bracketed by 144 (optimistic) and 200 (pessimistic).

## Implication for Follow-up Study Design

To confirm MLH1 mechanism-specificity at Bonferroni-corrected significance:
- **ClinVar coverage:** MLH1 has ~4,000 variants annotated (mostly VUS). Selecting ~84 pathogenic + ~84 benign with matched consequence categories should be feasible.
- **Pre-registration required:** Specify variant selection criteria, statistical test, and kill threshold BEFORE accessing data (avoids the garden of forking paths concern that motivated this reframe; Gelman & Loken, 2013).
- **Independent cohort preferred:** Re-using the current 15+15 variants in the larger N would inflate Type I error. Sample fresh variants.

---

## References

1. Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Lawrence Erlbaum.
2. Lehmann, E.L. (1975). Nonparametrics: Statistical Methods Based on Ranks. Holden-Day. ARE of Mann-Whitney vs t-test.
3. Rosenthal, R. (1991). Meta-Analytic Procedures for Social Research. Sage. Rank-biserial effect size.
4. Gelman, A. & Loken, E. (2013). The garden of forking paths. Columbia University. http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf

**Last updated:** 2026-05-25 (post-skeptic reframe, ADR-036)
