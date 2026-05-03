# Spectral Collapse Final Decision

**Date:** 2026-05-03  
**Branch:** `experiment/spectral-collapse-pilot`

## Verdict

**Stop here for now.** The HBB pilot is real, but the mechanism-level interpretation is not yet robust enough to promote.

## Evidence

- Baseline HBB separation is strong:
  - `SFI p = 0.00020453214097175136`
  - `spectral_gap p = 6.67538766891713e-05`
- Threshold and window perturbations preserve separation.
- Coverage/downsampling controls erase separation:
  - `coverage_keep_0.75 p = 0.6726091804237861`
  - `coverage_keep_0.50 p = 0.5757390449173081`
- Null controls do not support a stable mechanism claim:
  - `degree_preserving_null p = 0.9000257225381322`
  - `weight_shuffled_null p = 0.08881163592817248`

## Decision

- **Continue as a paper claim:** no
- **Continue as an exploratory branch:** yes, only if a later matched-control design removes the coverage sensitivity

## Practical Meaning

The pilot is sufficient to justify the line of work, but not sufficient to claim a validated spectral-collapse mechanism.

