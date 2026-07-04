# Paper 3 LDLR Strict Subset Freeze

**Date:** 2026-05-03  
**Status:** Strict freeze note, not a results claim

## Frozen files

- `results/PAPER3_LDLR_STRICT_SUBSET_CANDIDATES_20260503.csv`
- `results/PAPER3_LDLR_STRICT_SUBSET_CONTROL_SPACE_20260503.csv`

## Candidate freeze

Frozen candidate rule:

- locus: `LDLR`
- category: `5_prime_UTR` or `upstream_gene_variant`
- non-synthetic
- `ARCHCODE_LSSIM < 0.99`
- `Pearl == false`

Frozen candidate count:

- `17` rows

## Control freeze status

Control search space rule:

- locus: `LDLR`
- nearby window in the same 300 kb atlas region
- category: `synonymous` or `intronic`
- `Pearl == false`

Control search-space count:

- `50` rows

## Important caution

The control side is a search space, not yet a manuscript-grade matched-control set.

Reason:

- the nearby LDLR annotation layer still contains consequence noise, including rows where the category label and VEP consequence are not biologically clean enough for immediate promotion.

## What this freeze means

This freeze is sufficient to:

- stop ad hoc candidate reshaping,
- keep the LDLR candidate side stable,
- and define a concrete next audit step.

It is **not** sufficient to claim a second positive locus or to run live gnomAD as if the locus were already frozen for publication.

## Next step

1. Audit the 50-row control search space.
2. If the control side can be cleaned, convert it into a true matched-control set.
3. Only then consider live gnomAD queries.

