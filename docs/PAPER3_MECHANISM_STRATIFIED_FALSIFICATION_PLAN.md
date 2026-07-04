# Paper 3 Mechanism-Stratified Falsification Plan

**Status:** Draft execution plan, not a manuscript result  
**Date:** 2026-05-03  
**Working title:** LSSIM as a Mechanism-Specific Marker of Regulatory Variant Disruption: A Population-Guided Multi-Locus Falsification Framework

## Scope

Paper 3 should not claim that ARCHCODE is a universal pathogenicity predictor. The target claim is narrower:

> LSSIM may provide a mechanism-specific structural signal for regulatory/chromatin-context variants, and population allele frequency can serve as an orthogonal falsification or triage layer.

Use the terms **falsification**, **triage**, **orthogonal epidemiological context**, and **candidate epidemiology-discordant classification**. Avoid **validation**, **proves pathogenicity**, and **misclassification** unless a specific external truth set supports the statement.

## Lessons Carried Forward

The prior ARCHCODE work exposed a central risk: an apparently high metric can be a category artifact if promoter, enhancer, splice, missense, frameshift, and synonymous variants are pooled. Paper 3 therefore freezes mechanism strata before any new gnomAD interpretation.

Paper 2 is the proof-of-concept anchor. It is not enough for a general method claim.

## Frozen Strata

| Stratum | Purpose | Loci | Interpretation Rule |
|---|---|---|---|
| Regulatory positive candidates | Test whether low LSSIM enriches for population contradictions in regulatory contexts | HBB, BCL11A erythroid, HBA1/HBA2, GATA1 | Analyze separately by locus and regulatory subset |
| Mechanism boundary | Test where signal should weaken or become tissue/context dependent | CFTR | Interpret as boundary evidence, not failure/success alone |
| Coding-dominant controls | Estimate whether the signal is merely a category/position artifact | BRCA1, TP53, ATM if available | Keep separate from regulatory strata; do not pool into one headline metric |

## Candidate Selection Rules

Primary candidate cohort for the first reproducible run:

1. Use only rows from local Unified Atlas CSVs.
2. Exclude rows explicitly marked `SYNTHETIC`, `MOCK`, or `DEMO` in source/significance fields.
3. Use SNVs first. Indels can be a secondary analysis if gnomAD query handling is audited.
4. Within each locus, define the low-LSSIM cohort as the bottom 5% by `ARCHCODE_LSSIM`.
5. Keep regulatory-category and coding-category rows separate.
6. For broad `other` categories, perform a source audit before labeling them enhancer/regulatory.

Secondary boundary cohort:

1. SNV.
2. Non-synthetic.
3. Regulatory-category row.
4. `ARCHCODE_LSSIM < 0.99`.

These rules are feasibility defaults. They become pre-frozen only after this plan is committed before live gnomAD runs.

## Required Baselines

Every Paper 3 result needs at least these baselines:

| Baseline | Why It Exists |
|---|---|
| Category-only baseline | Tests whether LSSIM adds anything beyond promoter/splice/coding labels |
| Position/window baseline | Tests whether signal is just distance from locus or local ClinVar density |
| VEP/CADD/SpliceAI where available | Frames ARCHCODE as complementary, not superior by assumption |
| Coding-dominant controls | Tests mechanism specificity instead of universal prediction |

Do not report a single pooled AUC across mixed mechanisms as the main result.

## Population Interpretation Rules

Population AF can falsify or flag a claim; it does not prove pathogenicity.

Use:

- "not observed in gnomAD v4 under this query"
- "population-level contradiction"
- "candidate population-specific benign polymorphism"
- "requires functional or clinical follow-up"

Avoid:

- "confirmed universal constraint"
- "validated pathogenic"
- "gnomAD absence proves disease causality"

## Minimum Reproducible Artifacts

| Artifact | Purpose |
|---|---|
| `results/PAPER3_FEASIBILITY_MATRIX_20260503.csv` | Atlas readiness and candidate counts |
| `results/PAPER3_FEASIBILITY_MATRIX_20260503.md` | Reviewer-readable feasibility summary |
| `scripts/paper3_feasibility_matrix.py` | Rebuilds the feasibility matrix |
| `scripts/population_filter.py` outputs | Live gnomAD query evidence for frozen cohorts |
| `docs/PAPER3_MECHANISM_STRATIFIED_FALSIFICATION_PLAN.md` | Frozen design and guardrails |

## First Execution Order

1. Run the feasibility matrix from current atlas files.
2. Source-audit BCL11A erythroid rows because current category labels are broad.
3. Run dry-run cohorts for HBB and BCL11A before any live gnomAD calls.
4. If dry-run cohorts are non-empty and source-audited, run live gnomAD queries with `scripts/population_filter.py`.
5. Only then compute population contradiction rates by stratum.

## Kill Criteria

Stop or reframe the Paper 3 claim if any of these occur:

- Low-LSSIM regulatory cohorts are empty outside HBB after source audit.
- Category-only or position-only baseline matches LSSIM performance.
- The signal appears only when synthetic rows are included.
- The effect requires pooling unrelated mechanisms into one metric.
- gnomAD query failures or stale files cannot be separated from true absence.

## Rating

Current idea rating: **8.5/10** as a scientific direction.

Reason: the framing is strong and fixes the main ARCHCODE failure mode, but current local evidence outside HBB is not yet enough for a 9+/10 execution rating. The next improvement is not more writing; it is a frozen, source-audited multi-locus run with category and position baselines.

## Next 30 Minutes

1. Generate the feasibility matrix.
2. Inspect whether BCL11A/HBA1/GATA1 have real non-synthetic low-LSSIM regulatory SNV cohorts.
3. Record blockers before live gnomAD queries.
