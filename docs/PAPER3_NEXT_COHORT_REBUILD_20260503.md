# Paper 3 Next Cohort Rebuild

Date: 2026-05-03

## Current Decision

Paper 3 remains in feasibility and cohort-gate mode. The next useful work is a source-clean regulatory cohort rebuild, not manuscript writing and not broad expansion to many loci.

## Locus Status

| Locus | Current status | Gate implication |
|---|---|---|
| HBB | Paper 2 proof-of-concept anchor | Do not count as independent second-locus evidence. |
| BCL11A | Not usable as the second clean positive locus now: full bottom-5% cohort is mixed coding/splice, source audit retained only 3 promoter-proximal candidates, and position controls showed the same not-observed pattern. | Keep as cautionary pilot with source/category and position-confound limits. |
| CFTR | Boundary/negative case: low-LSSIM regulatory candidates did not behave like a clean regulatory-constraint example against controls. | Use only as mechanism-boundary evidence, not as a positive locus. |
| HBA1/HBA2 | **NOT YET**: full local HBA source recovery produced 108 queryable SNVs and 23 regulatory-subclass rows, but 0 primary low-LSSIM regulatory candidates and 0 selected position controls under the whole-locus bottom-5% rule. HBA2-position rows exist, but no HBA2-named local source table was found. | Stop live gnomAD for current HBA gate; rebuild source cohort first. |

## Exact HBA Blocker

The local HBA low-LSSIM tail is coding/nonsense/missense. Queryable regulatory-subclass rows exist, including HBA2-position rows in the full atlas, but they sit outside the whole-locus bottom 5% and outside the secondary `LSSIM < 0.99` boundary.

Evidence:

- `results/PAPER3_HBA_REGULATORY_REBUILD_20260503.md`
- `results/PAPER3_HBA_FULL_QUERYABLE_ATLAS_20260503.csv`
- `results/PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv`
- `results/PAPER3_HBA_POSITION_CONTROLS_20260503.csv`
- `results/PAPER3_HBA_COHORT_DECISION_20260503.md`

## Current Best Next Locus Or Design

Best next design: rebuild HBA/HBA2 with a real noncoding regulatory source set before considering another live population screen.

Minimum requirements:

- HBA2 or alpha-globin regulatory source rows with `Position_GRCh38`, `Ref`, `Alt`, `HGVS` or equivalent local source evidence.
- Clear subclass labels: promoter, 5_prime_UTR, intronic, splice_region, enhancer-like, and coding separated.
- Non-synthetic source audit.
- Primary low-LSSIM denominator frozen before live gnomAD.
- Position-matched controls selected before live gnomAD.

If HBA/HBA2 source rebuild cannot produce non-empty candidates and controls, the next design should import a different known regulatory locus with queryable noncoding SNVs and enough local controls. Do not reuse BCL11A or CFTR as positive evidence under the current artifacts.

## Next 30 Minutes

1. Decide whether to keep HBA as the immediate rebuild target or switch to a new imported regulatory locus.
2. If staying with HBA, locate or create a source-audited HBA2/noncoding HBA input table with explicit Ref/Alt provenance.
3. Add a zero-row guard to `population_filter.py` only if future gates need graceful dry-run behavior for empty selected-control files.

## Next 7 Days

1. Build a source-audited HBA/HBA2 noncoding regulatory table from accepted local or documented external source files.
2. Recover and sanity-check Ref/Alt against GRCh38 before gnomAD.
3. Freeze primary candidates and position controls before live query.
4. Run strict dry-run first; run live gnomAD only if candidates and controls are non-empty, <=20 rows each, and coordinate sanity checks pass.
5. Keep Paper 3 claims limited to cohort-gate evidence until a second locus separates from position controls.
