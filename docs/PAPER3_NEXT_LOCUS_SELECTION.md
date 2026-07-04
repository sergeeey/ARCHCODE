# Paper 3 Next Locus Selection

**Date:** 2026-05-03  
**Status:** Decision note, not a results claim

## Selected locus

`LDLR`

## Why this is the next locus

LDLR is the most usable next candidate because:

- it already has a full local atlas;
- a strict candidate subset is now frozen;
- candidate and control-space manifests already exist;
- it has supporting local artifacts for positional, Hi-C, and TDA context;
- it avoids reusing HBB as the only anchor and avoids forcing BCL11A into an unsafe positive claim.

## What is frozen already

- candidate-side strict subset: 17 rows
- control-space strict subset: 50 rows

These are frozen for design purposes only.

## What is not done yet

- the control-space is **not yet** a manuscript-grade matched-control set
- no live gnomAD query has been run against the frozen LDLR subset
- no Paper 3 claim should be written from this locus yet

## Next step

1. Audit the 50-row LDLR control-space subset.
2. If it can be cleaned, convert it to a true matched-control set.
3. Only then run live gnomAD queries with `scripts/population_filter.py`.

## Kill criteria

Stop if:

- the control side cannot be separated from coding-dominant noise,
- the candidate/control split collapses into the same mechanism category,
- or the live query would depend on unfrozen ad hoc filtering.

