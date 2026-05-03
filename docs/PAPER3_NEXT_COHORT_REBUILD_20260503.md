# Paper 3 Next Cohort Rebuild

Date: 2026-05-03

## Decision

The next Paper 3 step is to rebuild a clean regulatory candidate cohort rather than expand the current mixed-mechanism screen.

## What the current search showed

- BCL11A is a useful cautionary pilot, but it does not separate from position-matched controls.
- CFTR behaves as a boundary / negative locus, not a second positive locus.
- LDLR is a frozen candidate/control pair, but it is still a design-level screen rather than a clean second regulatory-positive locus.
- HBB remains the anchor and should not be used as independent second-locus evidence.

## Best next rebuild target

**HBA1/HBA2**

Why:

- the downloaded local data contains real erythroid regulatory evidence;
- HBA1 MANGO-overlap rows are now queryable after allele recovery;
- HBA1 is the closest current path to a second locus that is biologically regulatory and not just a control-like boundary locus;
- the remaining blocker is the regulatory subclass, not the availability of any local signal at all.

## Current blocker

The current HBA1 build is still not clean regulatory-only:

- the low-LSSIM candidates are currently annotated as coding / nonsense / missense in the local table;
- this means the cohort is usable as pilot evidence, but not as a manuscript-grade second positive regulatory locus yet.

## Required rebuild

1. Recover or import noncoding HBA2 / HBA regulatory variants inside the MANGO anchors.
2. Keep candidate and control strata separate.
3. Freeze a position-matched control set before any live gnomAD query.
4. Run dry-run first, then live query only if the cohort remains non-empty after source audit.

## Stop rules

- Do not pool HBA1 with BCL11A, CFTR, or LDLR into one multi-locus claim.
- Do not write a Paper 3 manuscript claim until one second locus survives a position-matched control check.
- Do not expand to more loci before the HBA rebuild is complete.

## Output expectation

The next useful artifact is a clean HBA1/HBA2 candidate-control rebuild note, not a manuscript section.
