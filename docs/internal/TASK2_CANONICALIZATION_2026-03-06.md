# TASK2_CANONICALIZATION_2026-03-06

## Task

Canonicalize Task 2 ("Loop That Stayed") evidence to a single claim-safe source of truth and prevent legacy overclaim.

## Implemented

- Added canonical Task2 status artifact:
  - `results/task2_canonical_status_2026-03-06.json`
- Marked legacy high-claim artifact as deprecated for claims:
  - `results/vus_batch_analysis_loop_that_stayed.json` (kept for traceability, not claim authority)
- Updated public-facing references to point to canonical/reconciled artifacts:
  - `manuscript/ACKNOWLEDGMENTS.md`
  - `results/LOOP_THAT_STAYED_INDEX.md`
  - `results/LOOP_THAT_STAYED_EXECUTIVE_SUMMARY.md`

## Verified

- Canonical claim levels are explicitly fixed:
  - `loop_that_stayed_as_pathogenic_class = UNVERIFIED`
  - `discordance_between_structure_and_sequence_predictors = SUPPORTED`
  - `clinical_reclassification_of_vus = UNVERIFIED`
- Legacy artifact remains available but no longer serves as primary evidence source for publication claims.

## UNVERIFIED

- Mechanistic causality and clinical reclassification remain unverified without orthogonal experiments.

## Risks

- Historical HTML/manuscript derivatives may still contain stale text until regenerated.
- If future edits reintroduce legacy artifact as primary source, overclaim risk returns.

## Verdict

- `READY_WITH_LIMITS` for documentation integrity.
- Scientific claim state remains `NEEDS_FIXES` as previously recorded.
