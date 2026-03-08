# VALIDATION_EXECUTION_2026-03-06_HBB_SENSITIVITY

## Task

Exploratory sensitivity analysis for HBB VUS enrichment vs `top_k` threshold.

## Implemented

- Added script:
  - `scripts/analyze_hbb_vus_sensitivity.py`
- Behavior:
  - Reads `results/HBB_Unified_Atlas_95kb.csv`.
  - Selects `ARCHCODE_Verdict == VUS`.
  - Ranks by lowest `ARCHCODE_LSSIM`.
  - Computes one-sided hypergeometric enrichment p-value for `k in {5,10,15,20,25}`.
  - Writes artifact:
    - `results/hbb_vus_sensitivity_2026-03-06.json`

## Verified

- `python scripts/analyze_hbb_vus_sensitivity.py --date 2026-03-06` -> PASS
- Produced:
  - `results/hbb_vus_sensitivity_2026-03-06.json`
- Observed:
  - `k=5` -> `p=0.34237892`
  - `k=10` -> `p=0.08717949`
  - `k=15` -> `p=0.01309524`
  - `k=20` -> `p=0.0005698`
  - `k=25` -> `p=0.0`

- `python scripts/secret_scan.py` -> `Secret scan PASSED.`

## UNVERIFIED

- No new clinical utility claim was validated.
- No orthogonal biological confirmation was added.

## Risks

- Sensitivity to `top_k` indicates threshold dependence; this is exploratory and must not overwrite strict decision artifact.
- Post-hoc threshold selection can inflate apparent significance if used as primary decision gate.

## Decision Boundary

- Strict decision source remains:
  - `results/hbb_vus_validation_report_2026-03-06.json` (`go_no_go=NO_GO`).
- This sensitivity output is informational only and does not change claim level.

## Verdict

`READY` (exploratory analysis artifact generated); strict HBB VUS decision remains `NO_GO`.
