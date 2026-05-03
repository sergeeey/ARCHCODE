# Spectral Collapse Pilot

**Date:** 2026-05-03  
**Branch:** `experiment/spectral-collapse-pilot`  
**Status:** exploratory branch note, not a manuscript claim

## Question

Does the spectral-gap style collapse metric separate HBB pearls from matched benign controls on already persisted contact matrices?

## Pilot Set

- Source matrices: `results/contact_matrices/30KB`
- Subset: HBB pilot from `scripts/spectral_fragility_batch.py`
- Cohort size: 45 pairs
- Pearls: 20
- Benign matched controls: 25
- Matrix size: `50x50`

## Results

| Metric | Pearls | Benign controls | Effect |
|---|---:|---:|---:|
| `SFI` mean | 0.3222 | 0.1171 | Cohen's d = 1.31 |
| `spectral_gap_disruption` mean | 0.000555 | 0.000111 | Cohen's d = 1.42 |
| `eigenvalue_shifts_mean` mean | 0.009997 | 0.000566 | Cohen's d = 6.73 |
| `eigenvector_angles_mean` mean | 0.4271 | 0.2400 | Cohen's d = 1.07 |

Statistical tests:

| Metric | Mann-Whitney p |
|---|---:|
| `SFI` | 2.045e-4 |
| `spectral_gap_disruption` | 6.675e-5 |
| `eigenvalue_shifts_mean` | 1.188e-8 |
| `eigenvector_angles_mean` | 2.676e-4 |

## Interpretation

The pilot shows a clear HBB separation on the spectral metrics already implemented in the repo. This is consistent with the earlier HBB spectral validation and supports using spectral gap collapse as a follow-up analysis.

This does **not** establish a new locus-level claim by itself. It is still an HBB-local pilot on pre-existing matrices.

## Negative-Control Context

Existing full-locus outputs are not contradictory:

- `results/sfi_brca1_all.csv` stays near background on `SFI` and spectral gap metrics.
- `results/sfi_tp53_all.csv` shows a weaker, broader signal than HBB.

That pattern is consistent with HBB being the strong positive anchor and BRCA1 acting as a near-null control.

## Next Step

If the goal is a clean spectral-collapse hypothesis, the next useful move is a matched-control pilot on a locus that already has persisted contact matrices and a clear negative control, not a new global sweep.

