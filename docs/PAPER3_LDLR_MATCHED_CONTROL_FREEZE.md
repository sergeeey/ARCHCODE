# Paper 3 LDLR Matched-Control Freeze

**Date:** 2026-05-03  
**Status:** Strict freeze note, not a results claim

## Frozen files

- `results/PAPER3_LDLR_STRICT_SUBSET_CANDIDATES_20260503.csv`
- `results/PAPER3_LDLR_MATCHED_CONTROLS_20260503.csv`

## Candidate side

Frozen candidate rule:

- locus: `LDLR`
- category: `5_prime_UTR` or `upstream_gene_variant`
- non-synthetic
- `ARCHCODE_LSSIM < 0.99`
- `Pearl == false`

Frozen candidate count:

- `17` rows

## Matched-control side

Frozen matched-control rule:

- locus: `LDLR`
- nearby same-locus control-space window
- category: `synonymous` or `intronic`
- `VEP_Consequence` in `synonymous_variant`, `intron_variant`, or `splice_donor_region_variant`
- `ARCHCODE_LSSIM >= 0.996`
- `Pearl == false`

Frozen matched-control count:

- `24` rows

## Why this is acceptable

The control side is now cleaner than the original broad search space because it excludes the obvious coding-dominant VEP noise while remaining within the same locus and nearby context.

## What this freeze means

This freeze is sufficient to:

- stop ad hoc reshaping of the LDLR control set,
- define a stable candidate/control pair for the next Paper 3 gate,
- and justify a single future live gnomAD query pass.

It is **not** sufficient to claim a validated second regulatory locus yet.

## Next gate

Run `scripts/population_filter.py` only after the current frozen candidate/control pair is reviewed against the dry-run criteria in the Paper 3 design note.

