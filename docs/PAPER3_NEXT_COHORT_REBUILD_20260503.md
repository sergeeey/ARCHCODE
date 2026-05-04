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
| TERT | **REBUILD_OR_SWITCH**: source-semantics audit retained useful promoter/5_prime_UTR Kircher overlap, but strict source rebuild produced 0 clean live-gate candidates and 0 controls. Candidate-like promoter rows remain mixed germline/somatic/cancer-context rows. | Do not run live gnomAD on current TERT set; either perform bounded source-resolution import or switch locus. |
| GATA1 | **STOP_LOCAL_POSITIVE_GATE / REBUILD_REF_ALT_ONLY**: HGVS allele recovery produces 182 queryable SNVs, but current local rows have 0 promoter/enhancer-like queryable rows and 0 primary regulatory candidates; bottom-5 recovered rows are coding missense/nonsense. | Do not run live gnomAD on current GATA1 set; only revisit with a true regulatory source import. |

## Exact HBA Blocker

The local HBA low-LSSIM tail is coding/nonsense/missense. Queryable regulatory-subclass rows exist, including HBA2-position rows in the full atlas, but they sit outside the whole-locus bottom 5% and outside the secondary `LSSIM < 0.99` boundary.

Evidence:

- `results/PAPER3_HBA_REGULATORY_REBUILD_20260503.md`
- `results/PAPER3_HBA_FULL_QUERYABLE_ATLAS_20260503.csv`
- `results/PAPER3_HBA_REGULATORY_CANDIDATES_20260503.csv`
- `results/PAPER3_HBA_POSITION_CONTROLS_20260503.csv`
- `results/PAPER3_HBA_COHORT_DECISION_20260503.md`

## Current Best Next Locus Or Design

TERT was the best local dry-run target after HBA, but it is now blocked for the current live gate.

Evidence:

- `results/PAPER3_NEXT_LOCUS_SCOUT_20260503.md`
- `results/PAPER3_TERT_REGULATORY_SCREEN_20260503.md`
- `results/PAPER3_TERT_COHORT_DECISION_20260503.md`
- `results/PAPER3_TERT_SOURCE_SEMANTICS_AUDIT_20260503.md`
- `results/PAPER3_TERT_SOURCE_REBUILD_DECISION_20260503.md`

TERT had a non-empty low-LSSIM regulatory candidate cohort and non-empty controls in local dry-run. After source-semantics audit, the strict rebuilt live-gate cohort is empty. The useful remaining assets are 3 benign promoter/5_prime_UTR exact-Kircher controls and 3 candidate-like promoter rows that need source-resolution before population interpretation.

Best immediate design: switch to a **new or re-imported documented regulatory locus** rather than trying to rescue the current local GATA1/TERT/HBA gates indefinitely.

Local GATA1 is no longer the best next live-gate target because the source inventory recovered queryable alleles but no promoter/enhancer-like regulatory candidates.

Possible next designs:

1. Import a true GATA1 regulatory source set, then rerun the same source/cohort gate.
2. Rebuild TERT only if external source-resolution can separate germline regulatory rows from somatic/cancer-only rows.
3. Consider LDLR/HBG1 only as fresh source-audited designs, not as positive evidence from existing mixed artifacts.

Minimum requirements:

- TERT, GATA1, HBA2, or another regulatory source table with `Position_GRCh38`, `Ref`, `Alt`, `HGVS` or equivalent local source evidence.
- Clear subclass labels: promoter, 5_prime_UTR, intronic, splice_region, enhancer-like, and coding separated.
- Non-synthetic source audit.
- Germline/somatic/cancer-context source semantics resolved before live population interpretation.
- Primary low-LSSIM denominator frozen before live gnomAD.
- Position-matched controls selected before live gnomAD.

If TERT source-resolution, HBA/HBA2 source rebuild, and local GATA1 source rows cannot produce non-empty candidates and controls, the next design should import a different known regulatory locus with queryable noncoding SNVs and enough local controls. Do not reuse BCL11A, CFTR, or current local GATA1/TERT artifacts as positive evidence.

## Next 30 Minutes

1. Choose between a true regulatory source import and a fresh LDLR/HBG1 design audit.
2. For TERT rescue, list the exact missing source-resolution fields needed to separate germline regulatory rows from somatic/cancer-only rows.
3. Do not run live gnomAD until a non-empty strict candidate/control set passes dry-run.

## Next 7 Days

1. Import or build one source-audited regulatory locus table with queryable noncoding SNVs and matched controls.
2. Keep HBA/HBA2, TERT, and GATA1 as rebuild-only paths unless their source tables materially change.
3. For any selected locus, recover and sanity-check Ref/Alt against GRCh38 before gnomAD.
4. Freeze primary candidates and position controls before live query.
5. Run strict dry-run first; run live gnomAD only if candidates and controls are non-empty, <=20 rows each, and coordinate sanity checks pass.
6. Keep Paper 3 claims limited to cohort-gate evidence until a second locus separates from position controls.
