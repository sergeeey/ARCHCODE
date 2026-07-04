# Paper 3 Loci Triage

**Date:** 2026-05-03  
**Status:** Internal triage note, not a results claim

## Summary

The current local atlas files do **not** yet contain a second clean regulatory positive locus for Paper 3.

## Evidence

### HBA1

- Queryable MANGO overlap exists.
- Low-LSSIM candidates are few.
- Current candidate categories are `nonsense` and `missense`, not clean regulatory-only rows.
- Conclusion: HBA1 is queryable, but not a clean second positive locus in the current local annotation.

### BCL11A erythroid

- Queryable bottom-5% cohort exists.
- Source audit retains only a small subset for primary use.
- The retained rows still map to broad `other` labels and coding/splice HGVS annotations.
- Conclusion: BCL11A remains the best immediate pilot, but it is not yet a clean regulatory-only positive locus.

### GATA1

- Current local atlas does not yet provide a clean queryable regulatory SNV subset.
- Conclusion: not ready for the next positive-locus claim.

### CFTR

- Useful as a boundary/negative locus.
- Not a second positive locus.

### BRCA1 and TP53

- Useful as controls only.
- Do not pool them with regulatory positives.

## Decision

There is still no second positive locus that survives source audit and position-matched control logic.

## Practical next step

1. Keep BCL11A as the immediate pilot if a stricter source audit is possible.
2. Otherwise, import a new locus with known regulatory pathogenic SNVs and enough matched controls.
3. Do not expand the Paper 3 claim yet.

