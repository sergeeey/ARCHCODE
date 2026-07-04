# Paper 3 Imported Locus Selection — LDLR

**Date:** 2026-05-03  
**Status:** Design note, not a results claim

## Selection

`LDLR` is selected as the next import candidate for Paper 3.

## Why LDLR

LDLR is the best available local candidate because:

- it already has a full local atlas;
- the atlas summary shows a non-empty regulatory tail;
- there are existing LDLR-specific supporting artifacts in the repo;
- it is not being used as a control locus;
- it can be frozen before any live gnomAD query.

## Local evidence available now

- `results/UNIFIED_ATLAS_SUMMARY_LDLR_300kb.json`
- `results/positional_signal_ldlr.json`
- `results/tda_proof_of_concept_ldlr.json`
- `results/hic_correlation_ldlr.json`
- `results/LDLR_vus_candidates.csv`
- `results/LDLR_Unified_Atlas_300kb.csv`

## What this does not mean

- It does **not** mean LDLR is already validated as the second positive locus.
- It does **not** mean a manuscript claim should be written now.
- It does **not** mean gnomAD should be queried before the locus is frozen.

## Freeze conditions before live query

1. Source-audit the LDLR regulatory subset.
2. Freeze the candidate / control split.
3. Keep category-only and position-only baselines separate.
4. Run live gnomAD queries only after the frozen cohort is written down.

## Practical role

LDLR is the current import candidate for the next Paper 3 step because it has the strongest existing local support without reusing HBB or forcing a mixed-mechanism BCL11A pilot into a positive claim.

