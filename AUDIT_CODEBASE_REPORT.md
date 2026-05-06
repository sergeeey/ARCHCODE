# AUDIT CODEBASE REPORT

Date: 2026-05-05

## Executive Verdict

`NEEDS_FIXES` for repository hygiene and full reproducibility.

`READY_WITH_LIMITS` for the current governance/test baseline: project canon, results contract, secret scan, and unit/regression tests passed in this audit session.

## What Was Checked

| Area | Evidence |
|---|---|
| Package metadata | `package.json`, `pyproject.toml` read |
| Top-level docs | `README.md`, `REPRODUCE.md`, `PROJECT_CANON.md`, `CLAUDE.md`, `AGENTS.md` read |
| Existing audits | `CODEX_PROJECT_AUDIT_2026-05-03.md`, `REVIEWER_RISK_REGISTER.md` read |
| Validation contracts | `VALIDATION_PROTOCOL.md`, `docs/RESULTS_CONTRACT.md`, `docs/VALIDATION.md`, `docs/FAILURE_MODES.md` read |
| Hypothesis evidence doc | `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` read |
| Validation suite artifacts | `validation_suite/results/master_results.json`, `validation_suite/results/within_category_tp53.json` read |
| Tests | `npm test -- --run` passed |

## Main Entrypoints

| Entrypoint | Role | Status |
|---|---|---|
| `src/main.tsx` | React app entry | Not deeply audited |
| `src/engines/LoopExtrusionEngine.ts` | Core loop-extrusion engine | Covered by passing unit tests; not line-reviewed in this pass |
| `src/engines/contactMatrix.ts` | Contact-map utilities | Covered by passing tests; not line-reviewed |
| `scripts/generate-unified-atlas.ts` | Main atlas generation | High risk: modified in dirty tree |
| `scripts/validate_project_canon.py` | Canon gate | Executed and passed |
| `scripts/validate_results_contracts.py` | Results contract gate | Executed and passed |
| `scripts/secret_scan.py` | Secret scan | Executed and passed |
| `validation_suite/run_tests.py` | Falsification suite runner | Existing outputs inspected; not rerun |
| `tools/run_pipeline.py` | Pipeline helper | Not audited in this pass |

## Test Evidence

Command:

```text
npm test -- --run
```

Observed outcome:

```text
Test Files: 6 passed
Tests: 49 passed
```

Limitations:

- Full build was not run.
- Coverage gate was not run.
- Python analysis tests were not comprehensively run.
- Full validation suite was not rerun; only existing artifacts were inspected.

## Code Quality Risks

| Risk | Evidence | Severity |
|---|---|---|
| Dirty source/result coupling | `scripts/generate-unified-atlas.ts`, `results/HBB_Unified_Atlas.csv`, and `results/UNIFIED_ATLAS_SUMMARY.json` modified together | HIGH |
| Many scripts without a single pipeline manifest | Large `scripts/` directory with multiple historical pipelines | HIGH |
| Scientific claims depend on generated CSV/JSON naming conventions | `results/*Unified_Atlas*`, `analysis/*`, `validation_suite/results/*` | HIGH |
| Validation suite is not integrated into the standard `npm test` gate | Separate Python suite and artifacts | MEDIUM |
| Log-heavy tests | Unit tests pass but emit large stdout/stderr | LOW/MEDIUM |
| Local `.env` exists | Secret scan passed, but local secret-bearing file exists | MEDIUM |
| Line-ending churn warnings | Git warned LF will be replaced by CRLF for several modified files | LOW/MEDIUM |

## Architecture Strengths

1. Clear governance layer exists: `CLAUDE.md`, `PROJECT_CANON.md`, `docs/RESULTS_CONTRACT.md`.
2. Machine-checkable gates exist for canon and claim matrix drift.
3. Unit/regression test suite is fast and currently green.
4. Validation suite is designed around falsification rather than confirmation.
5. Results claim matrix maps public claims to artifacts and caveats.

## Architecture Weaknesses

1. Artifact sprawl makes current truth hard to identify without canon routing.
2. Many results are untracked, which weakens reproducibility claims.
3. Some technical/manuscript surfaces still use language stronger than the current public canon.
4. The project mixes app, simulation engine, manuscript, exploratory research, and raw/generated data in one repository.
5. Several important checks are manual or not run in this pass: `check_redflags.py`, `verify_manuscript.py`, full validation suite, checksums.

## Contract Change Risks

| Contract | Risk |
|---|---|
| CSV atlas columns | Any change in `scripts/generate-unified-atlas.ts` can invalidate scripts expecting columns such as `ClinVar_ID`, `ARCHCODE_LSSIM`, `VEP_Score`, `CADD_Phred`, `Category` |
| Result summary JSON | Numeric claim matrix may drift if summaries change without updating `publication_claim_matrix` |
| Locus config semantics | Thresholds and cell-type annotations can change biological interpretation |
| Validation suite labels | PASS/FAIL/WARNING semantics must remain aligned with claim language |

## Recommended Codebase Gates Before Any Scientific Claim Update

1. `npm run build`
2. `npm test -- --run`
3. `npm run test:coverage`
4. `npm run validate:project-canon`
5. `npm run validate:results-contracts`
6. `python check_redflags.py`
7. `python scripts/verify_manuscript.py`
8. `python -m validation_suite run --all`
9. `sha256sum -c checksums.sha256` or Windows equivalent
10. A clean `git status --short` except explicitly intended files

## Verdict

The codebase has real engineering substance and unusually mature integrity gates, but the current working tree is not publication-clean. The biggest codebase risk is not failing tests; it is that data/result/manuscript changes can become coupled without a single frozen lineage manifest.

