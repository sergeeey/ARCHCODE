# Paper 3 Frozen Cohort Design

**Date:** 2026-05-03  
**Status:** Design note, not a results claim

## Objective

Find a second genuine regulatory positive locus for Paper 3 where low-LSSIM candidates separate from position-matched controls after source audit.

The target is **not** a universal predictor claim. The target is:

> a mechanism-stratified population-guided falsification / triage framework with at least two audited regulatory positive loci.

## Frozen strata

### Positive anchor

- `HBB`

Use as the anchor only. Do not reinterpret HBB as multi-locus proof.

### Candidate positive loci

- `BCL11A_erythroid`
- `HBA1`
- `HBA2` if the atlas can be separated cleanly
- `GATA1`

These loci are only acceptable as positive Paper 3 evidence after source audit confirms a regulatory subset that is not dominated by coding, nonsense, or broad `other` labels.

### Boundary / negative loci

- `CFTR`

Use as a mechanism boundary or negative control. Do not promote it as a second positive locus unless a new source audit changes the classification.

### Coding-dominant controls

- `BRCA1`
- `TP53`
- `ATM` if a clean control cohort exists

These are controls only. Do not pool them with regulatory positives.

## Frozen candidate rules

1. Use only non-synthetic rows from local atlas files.
2. Freeze mechanism strata before any live gnomAD query.
3. Keep regulatory and coding rows separate.
4. Require a source audit before a locus can be called regulatory-positive.
5. Require position-matched controls for every positive locus.
6. Do not report pooled AUC across mixed mechanisms as the main result.
7. Treat gnomAD absence as a triage signal, not proof of universal constraint.

## Minimum positive-locus standard

A locus can enter the positive set only if all of the following hold:

- queryable cohort is non-empty after source audit
- low-LSSIM tail is not dominated by coding or nonsense HGVS labels
- position-matched controls are available
- the low-LSSIM cohort differs from controls under the frozen interpretation rule
- the result survives a baseline check against category-only and position-only models

## Kill criteria

Stop treating a locus as a positive candidate if:

- the cohort becomes empty after source audit
- the apparent signal is explained by coding/category labels
- the controls behave the same way as the candidates
- the result only appears when synthetic or mock rows are included
- gnomAD query failures cannot be separated from true not-observed outcomes

## Recommended next move

1. Rebuild the HBA1/HBA2 and GATA1 regulatory subsets if possible.
2. Re-run the source audit on BCL11A with stricter regulatory-only rules.
3. Keep CFTR as boundary evidence.
4. Keep BRCA1 and TP53 as controls.
5. Promote only one new locus at a time.

## Practical decision rule

If no candidate locus survives the source audit, the Paper 3 claim should remain:

> direction strong, second positive locus not yet found.

