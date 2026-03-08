# VALIDATION_EXECUTION_2026-03-06_TASK5

## Task

Task 5: VUS Stratification (reproducible summary with explicit rules, provenance, and anti-overclaim gates)

Primary claim source (canonicalized):
- `results/task5_canonical_status_2026-03-06.json`

## Implemented

- Added reproducible builder:
  - `scripts/build_task5_vus_summary.py`
- Builder behavior:
  - Reads `results/within_category_analysis.json`.
  - Reads `results/vus_validation_report.json` (if present) for variant-level rationale sample.
  - Uses baseline atlas files for loci present in within-category analysis.
  - Excludes ablation/control atlas variants (`INVERTED`, `POSITION_ONLY`, `RANDOM`, `UNIFORM_MEDIUM`).
  - Applies explicit stratification rules and writes dated Task 5 summary.
- Generated artifact:
  - `results/task5_vus_stratification_summary_2026-03-06.json`

## Verified

- Recomputed within-category metrics:
  - `python scripts/within_category_analysis.py`
  - Output confirmed:
    - `results/within_category_analysis.json`
    - supplementary table updated at desktop path (script default behavior)

- Built Task 5 summary:
  - `python scripts/build_task5_vus_summary.py --date 2026-03-06`
  - Output:
    - `results/task5_vus_stratification_summary_2026-03-06.json`
  - Key observed fields:
    - `vus_total_in_windows=219`
    - `candidates_total=219`
    - `pearl_like_total=49`
    - `mean_within_category_auc_across_loci=0.482278`
    - `claim_level.clinical_reclassification=UNVERIFIED`
    - per-variant rationale sample present with provenance tags.

- Regression safety:
  - `npm test -- src/__tests__/regression/gold-standard.test.ts` → PASS
  - `npm run test:coverage` → PASS
    - Coverage gate remains satisfied: statements `64.81`, branches `55.00`, functions `67.90`, lines `64.68`

## UNVERIFIED

- Clinical reclassification from Task 5 metrics remains unverified.
- Causal mechanism assignment remains exploratory without orthogonal functional experiments.

## Risks

- `within_category_analysis.py` writes supplementary table to a machine-specific path; this is operationally brittle for CI portability.
- Counts are definition-sensitive; the summary explicitly binds definitions in `stratification_rules` to prevent silent metric drift.

## Verdict

`READY` for Task 5 at validation-protocol level (reproducible computational stratification summary with strict anti-overclaim boundaries).
