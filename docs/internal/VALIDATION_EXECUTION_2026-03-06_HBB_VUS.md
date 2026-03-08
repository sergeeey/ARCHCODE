# VALIDATION_EXECUTION_2026-03-06_HBB_VUS

## Task

HBB-focused strict VUS validation with predeclared Go/No-Go criteria and portable artifact generation.

Top-level canonical index (primary governance source):
- `results/validation_canonical_index_2026-03-06.json`

## Implemented

- Updated portability in:
  - `scripts/within_category_analysis.py`
  - Added CLI args `--output-json`, `--output-table`.
  - Replaced machine-specific default table path with repo-local default:
    - `results/TABLE_S3_within_category.txt`

- Added strict HBB report builder:
  - `scripts/build_hbb_vus_validation_report.py`
  - Inputs:
    - `results/HBB_Unified_Atlas_95kb.csv`
    - `results/within_category_analysis.json`
    - `results/vus_validation_report.json` (optional rationale sample)
  - Output:
    - `results/hbb_vus_validation_report_2026-03-06.json`
  - Adds explicit:
    - H0/H1
    - predeclared criteria
    - one-sided hypergeometric enrichment p-value
    - Go/No-Go decision and reason
    - blocked claims / allowed claims

## Verified

- Recomputed within-category metrics:
  - `python scripts/within_category_analysis.py`
  - Produced:
    - `results/within_category_analysis.json`
    - `results/TABLE_S3_within_category.txt`

- Rebuilt Task 5 summary:
  - `python scripts/build_task5_vus_summary.py --date 2026-03-06`
  - Produced:
    - `results/task5_vus_stratification_summary_2026-03-06.json`
  - Observed:
    - `VUS=219`
    - `candidates=219`
    - `pearl_like=49`

- Built strict HBB VUS report:
  - `python scripts/build_hbb_vus_validation_report.py --date 2026-03-06`
  - Produced:
    - `results/hbb_vus_validation_report_2026-03-06.json`
  - Observed:
    - `Go/No-Go: NO_GO`
    - `N=28`
    - `top10=10/10`
    - `p=0.08717949`

- Regression and coverage safety:
  - `npm test -- src/__tests__/regression/gold-standard.test.ts` -> PASS
    - HBB Pearson `0.888`
    - Sox2 Pearson `0.662`
    - Pcdh Pearson `0.668`
  - `npm run test:coverage` -> PASS
    - Statements `64.81`
    - Branches `55.00`
    - Functions `67.90`
    - Lines `64.68`

- Secret hygiene:
  - `python scripts/secret_scan.py` -> `Secret scan PASSED.`

## UNVERIFIED

- Clinical utility/reclassification claims remain unverified.
- Causal mechanism assignment remains exploratory without orthogonal wet-lab evidence.

## Risks

- Go/No-Go depends on chosen `top_k` (default 10); this is now explicit but still a design choice.
- Pearl-like definition (`Pearl == true` OR discordance in `{VEP_ONLY, ARCHCODE_ONLY}`) may require tightening for publication context.
- HBB NO_GO result should block escalation to stronger claims unless criteria are revised in advance and rerun.

## Verdict

`READY` (engineering/validation infrastructure), with scientific decision `NO_GO` for HBB VUS utility under current predeclared thresholds.
