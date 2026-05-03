# Paper 3 Autonomous Status

**Date:** 2026-05-03  
**Mode:** Evidence-first feasibility pass  
**Verdict:** Promising direction, not ready for manuscript claims

## Executive Verdict

| Item | Rating |
|---|---:|
| Scientific direction | 8.5/10 |
| Current local evidence outside HBB | 5.5/10 |
| Execution readiness after this pass | 7.0/10 |
| Submit-ready Paper 3 claim | No |

The strongest idea remains:

> mechanism-stratified population-guided falsification / triage for regulatory structural variant predictions.

The strongest warning from this pass:

> current non-HBB atlas evidence is not yet a clean regulatory expansion. BCL11A has a compact pilot cohort, but those rows are broad `other` category and map to coding/splice HGVS annotations in local ClinVar files.

## Files Produced

| File | Purpose |
|---|---|
| `docs/PAPER3_MECHANISM_STRATIFIED_FALSIFICATION_PLAN.md` | Frozen design, guardrails, baselines, kill criteria |
| `scripts/paper3_feasibility_matrix.py` | Rebuilds atlas readiness matrix without gnomAD calls |
| `results/PAPER3_FEASIBILITY_MATRIX_20260503.csv` | Machine-readable feasibility matrix |
| `results/PAPER3_FEASIBILITY_MATRIX_20260503.md` | Reviewer-readable feasibility matrix |
| `results/paper3_bcl11a_erythroid_bottom5_20260503.csv` | Strict BCL11A pilot query output |
| `results/paper3_bcl11a_erythroid_bottom5_20260503.json` | Strict BCL11A query summary |
| `results/paper3_bcl11a_erythroid_bottom5_not_observed_20260503.csv` | Opt-in not-observed BCL11A output |
| `results/paper3_bcl11a_erythroid_bottom5_not_observed_20260503.json` | Opt-in not-observed BCL11A summary |
| `results/PAPER3_BCL11A_SOURCE_AUDIT_20260503.csv` | Local source/category audit of BCL11A bottom-5% rows |
| `results/PAPER3_BCL11A_SOURCE_AUDIT_20260503.md` | Source audit summary |
| `results/paper3_bcl11a_primary_regulatory_not_observed_20260503.csv` | Opt-in gnomAD output for source-audited primary BCL11A subset |
| `results/paper3_bcl11a_primary_regulatory_not_observed_20260503.json` | Summary for source-audited primary BCL11A subset |
| `results/PAPER3_BCL11A_BASELINE_AUDIT_20260503.md` | Category/position baseline audit for the BCL11A pilot |
| `results/PAPER3_BCL11A_POSITION_MATCHED_CONTROLS_20260503.csv` | Position-matched BCL11A control cohort |
| `results/PAPER3_BCL11A_POSITION_MATCHED_CONTROLS_20260503.md` | Position control cohort summary |
| `results/paper3_bcl11a_position_controls_not_observed_20260503.csv` | Opt-in gnomAD output for position controls |
| `results/paper3_bcl11a_position_controls_not_observed_20260503.json` | Summary for position controls |
| `results/PAPER3_ALL_ATLAS_QUICK_SCAN_20260503.csv` | Quick scan of all local Unified Atlas files for queryable low-LSSIM cohorts |
| `results/PAPER3_CFTR_REGULATORY_SCREEN_20260503.md` | CFTR regulatory candidate/control cohort definition |
| `results/PAPER3_CFTR_REGULATORY_CANDIDATES_20260503.csv` | CFTR low-LSSIM regulatory candidate cohort |
| `results/PAPER3_CFTR_POSITION_CONTROLS_20260503.csv` | CFTR position-matched control cohort |
| `results/paper3_cftr_regulatory_candidates_20260503.csv` | gnomAD output for CFTR low-LSSIM candidates |
| `results/paper3_cftr_position_controls_20260503.csv` | gnomAD output for CFTR position controls |
| `results/PAPER3_CFTR_POPULATION_SCREEN_COMPARISON_20260503.md` | CFTR candidate vs control comparison |

## Feasibility Matrix Summary

| Locus | Role | Key Finding | Status |
|---|---|---|---|
| HBB | Paper 2 anchor | Current `Pearl=True` dry-run starts with missense/splice/frameshift, not a clean promoter-only cohort | Use only as audited Paper 2 anchor |
| HBA1 | candidate positive | 111 rows, 0 queryable SNVs under current Ref/Alt fields (`.`/`.`); VEP/CADD unavailable | Needs subset rebuild |
| BCL11A erythroid | candidate positive | 11 bottom-5% LSSIM SNVs; all category `other`; local HGVS includes coding/splice labels | Best pilot, but source/category blocker remains |
| GATA1 | candidate positive | 183 rows, 0 queryable SNVs under current Ref/Alt fields; low tail mostly missense/nonsense | Needs subset rebuild |
| CFTR | mechanism boundary | 177 bottom-5% dry-run variants; too large for first run; context/tissue caveat | Boundary/control, not headline |
| BRCA1 | coding control | 542 bottom-5% dry-run variants; many coding/other rows | Control stratum only |
| TP53 | coding control | small regulatory bottom-5% count in matrix, but VEP/CADD unavailable | Control stratum after source audit |

## BCL11A Pilot Result

Command cohort:

```powershell
python scripts\population_filter.py --atlas results\BCL11A_Unified_Atlas_bcl11a_erythroid.csv --chrom 2 --cohort-column ARCHCODE_LSSIM --cohort-op less_equal --cohort-value 0.9791 --locus-name BCL11A_erythroid --out paper3_bcl11a_erythroid_bottom5_20260503 --rate-limit 2.0
```

Strict result:

| Source | Count | Interpretation |
|---|---:|---|
| `QUERY_FAILED` | 11 | Technical/query status, not biological absence |

Opt-in not-observed run:

```powershell
python scripts\population_filter.py --atlas results\BCL11A_Unified_Atlas_bcl11a_erythroid.csv --chrom 2 --cohort-column ARCHCODE_LSSIM --cohort-op less_equal --cohort-value 0.9791 --locus-name BCL11A_erythroid --out paper3_bcl11a_erythroid_bottom5_not_observed_20260503 --rate-limit 2.0 --treat-not-found-as-absent
```

| Source | Count | Interpretation |
|---|---:|---|
| `gnomAD_v4_not_observed_graphql` | 10 | Not observed under opt-in GraphQL interpretation; requires coordinate/build sanity check |
| `QUERY_FAILED` | 1 | Rate-limit/retry failure; not interpretable |

Do not write "10/11 absent" in a manuscript yet. The accurate phrase is:

> In an exploratory BCL11A bottom-5% LSSIM pilot, 10/11 variants returned gnomAD GraphQL `Variant not found` responses under an opt-in not-observed interpretation, while 1/11 remained a query failure; this requires coordinate/build and category audit before biological interpretation.

## Source Audit Notes

Local evidence:

- `data/clinvar_bcl11a_variants.csv` contains the pilot IDs.
- `results/BCL11A_Unified_Atlas_bcl11a_erythroid.csv` marks them as `Category=other`.
- HGVS labels include `c.55+1G>A`, `c.55C>T (p.Pro19Ser)`, and `c.28C>T (p.Gln10Ter)`.

This means the full BCL11A bottom-5% cohort is not a clean enhancer/regulatory cohort. A conservative source audit allows only 3/11 rows into a primary promoter-proximal splice/UTR-like subset:

| Subset | Count |
|---|---:|
| splice_region_or_intronic | 3 |
| coding_missense_or_synonymous | 7 |
| coding_nonsense | 1 |

Primary subset gnomAD opt-in result:

| Source | Count | Interpretation |
|---|---:|---|
| `gnomAD_v4_not_observed_graphql` | 3 | Not observed under opt-in GraphQL interpretation; requires coordinate/build sanity check before manuscript use |
| `QUERY_FAILED` | 0 | No retry failures in this 3-variant run |

Accurate allowed phrase:

> After local source audit, 3 promoter-proximal BCL11A splice/UTR-like candidates were retained for a primary pilot; all 3 returned gnomAD GraphQL `Variant not found` responses under an opt-in not-observed interpretation. This is pilot evidence requiring coordinate/build sanity checks, not a validation claim.

## Baseline Audit Result

| Baseline | Local Result | Consequence |
|---|---|---|
| Category-only | All 182 BCL11A rows are `Category=other` | Category baseline is uninformative in current atlas |
| Position-window | 11/11 bottom-5% rows are within 1 kb of a configured feature | Position baseline is a real confounder and must be included |
| HGVS subclass | 7/11 coding missense/synonymous, 3/11 splice/intronic, 1/11 nonsense | Full 11-row set must not be called regulatory |
| Primary audited subset | 3/3 retained rows overlap bottom-5% and are promoter-proximal splice/UTR-like | Usable only as a small pilot |
| Position-matched controls | 6/6 controls also returned `gnomAD_v4_not_observed_graphql` in opt-in mode | BCL11A pilot does not currently distinguish LSSIM from position/query behavior |

This is the most important negative result from the autonomous pass. BCL11A is still useful, but not as a clean second positive proof yet.

## Required Next Step

Do not expand to 10 loci yet. First close this blocker:

1. Coordinate/build sanity-check both BCL11A primary candidates and position controls.
2. Build clean regulatory-only candidate sets for HBA1/GATA1 or mark them unsuitable.
3. Find a second positive locus where low-LSSIM candidates separate from position-matched controls.
4. Only then run CFTR/BRCA1/TP53 controls.

The all-atlas quick scan found many apparent low-LSSIM cohorts, but several are not safe as Paper 3 positives because they are broad `other` category, synthetic/mutagenesis-adjacent, or coding-dominant controls. The next locus must be selected by mechanism/source audit, not by largest candidate count.

## CFTR Follow-Up Screen

CFTR was tested as the next real regulatory/mechanism-boundary locus because the local config contains promoter/5'UTR and literature CRE/DHS features.

| Group | n | gnomAD successes | query failures | not observed | AF >= 1% | max AF |
|---|---:|---:|---:|---:|---:|---:|
| low-LSSIM regulatory candidates | 26 | 15 | 11 | 3 | 3 | 0.111533 |
| position-matched controls | 26 | 15 | 11 | 7 | 0 | 0.00000658 |

Interpretation:

> CFTR does separate from position controls, but in the opposite direction expected for a positive regulatory constraint example. Low-LSSIM promoter/5'UTR candidates include common population variants, while position controls are mostly rare/not observed. CFTR is therefore a useful boundary/negative locus, not the second positive locus.

Current answer to the Paper 3 search:

> A second true positive regulatory locus has not yet been found in the current local atlas files.

## Claims Allowed Today

Allowed:

- Paper 3 direction is strong.
- Current feasibility scan identified BCL11A as the best immediate pilot.
- Current BCL11A pilot is promising but blocked by category/coordinate audit.
- HBA1 and GATA1 current atlases are not ready for gnomAD SNV queries.

Not allowed:

- "Multi-locus validation confirmed."
- "BCL11A proves regulatory generalization."
- "10/11 absent proves constraint."
- "ARCHCODE beats VEP/CADD."
- "Paper 3 is ready."

## Next 30 Minutes

Best next implementation task:

> Do not use BCL11A or CFTR as the second positive claim yet. Rebuild a real enhancer/promoter regulatory subset for HBA/BCL11A/GATA1, or import a locus with known regulatory pathogenic SNVs and enough position-matched controls.

Until a second positive locus survives a position-matched control, Paper 3 should stay in feasibility mode.
