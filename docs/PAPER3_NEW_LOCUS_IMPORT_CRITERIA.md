# Paper 3 New Locus Import Criteria

**Date:** 2026-05-03  
**Status:** Design note, not a results claim

## Why this note exists

The current local atlas files do not yet contain a second clean regulatory positive locus for Paper 3. Existing candidates are either:

- queryable but coding-dominant,
- source-audited but still mixed with broad `other` labels,
- or useful only as boundary / control loci.

If Paper 3 is extended beyond the current local atlas, the next locus must be imported under frozen criteria, not ad hoc enthusiasm.

## Minimum import requirements

1. The locus must have known or strongly suspected regulatory SNVs.
2. The imported atlas must contain a non-empty regulatory-only or promoter/enhancer-oriented subset.
3. Low-LSSIM candidates must be queryable without coordinate ambiguity.
4. Position-matched controls must exist in the same locus.
5. The locus must not collapse to a coding-only category after source audit.
6. The locus must be separable from the HBB anchor without reusing HBB as a proxy.
7. The locus must survive category-only and position-only baselines before any claim is written.

## Candidate import shortlist

These loci already exist as configuration surfaces in the repository and are plausible import candidates, but none is yet promoted here as the second positive locus:

- `SHH`
- `SCN5A`
- `FOXP3`
- `LDLR`
- `GATA1`
- `BCL11A` after stricter source audit

## Import decision rule

Import a new locus only if it can be treated as a frozen positive candidate with:

- source-audited regulatory SNVs,
- matched controls,
- a mechanism-specific rationale,
- and no need to pool unrelated mechanisms to obtain a signal.

## Do not do

- Do not import a locus just because its atlas is large.
- Do not import a locus if the low-LSSIM cohort is still coding-dominant.
- Do not promote a boundary locus as a positive locus.
- Do not treat gnomAD not-observed responses as proof of universal constraint.

## Next action

Either:

1. tighten BCL11A further, or
2. import one locus from the shortlist and freeze it before any live gnomAD query.

