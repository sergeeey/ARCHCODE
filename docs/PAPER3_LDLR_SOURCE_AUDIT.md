# Paper 3 LDLR Source Audit

**Date:** 2026-05-03  
**Status:** Internal audit note, not a results claim

## Conclusion

`LDLR` is a usable import candidate, but the current local atlas still does **not** provide a clean regulatory-only positive subset.

## What the local files show

- The LDLR atlas exists and is well populated.
- The top visible candidate rows include many coding or upstream/5'UTR-like annotations.
- Existing LDLR artifacts show mixed mechanism behavior rather than a frozen clean regulatory cohort.
- Position and TDA artifacts exist, but they do not by themselves establish a clean second positive locus.

## Implication

LDLR can be imported as a candidate locus, but only after a stricter subset definition.

That stricter subset should:

- isolate regulatory/proximal non-coding rows,
- exclude coding-dominant rows,
- and define matched controls before any live gnomAD query.

## Decision

- Do **not** yet call LDLR the second positive locus.
- Do **not** run live gnomAD against the unfrozen full atlas.
- Use LDLR only as an import candidate pending subset freeze.

