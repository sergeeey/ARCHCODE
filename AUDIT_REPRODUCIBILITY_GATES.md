# AUDIT REPRODUCIBILITY GATES

Date: 2026-05-05

## Gates Run In This Audit Session

| Gate | Command | Outcome | Evidence |
|---|---|---|---|
| Git branch | `git branch --show-current` | PASS | `experiment/spectral-collapse-pilot` |
| Git status | `git status --short` | PASS with dirty tree | Modified and untracked files observed |
| Git diff stat | `git diff --stat` | PASS | 14 tracked files changed before audit docs |
| Project canon | `npm run validate:project-canon` | PASS | `PROJECT CANON PASSED.` |
| Results contract | `npm run validate:results-contracts` | PASS | `RESULTS CONTRACT PASSED.` |
| Secret scan | `npm run security:secrets` | PASS | `Secret scan PASSED.` |
| Unit/regression tests | `npm test -- --run` | PASS | 6 test files, 49 tests |

## Gates Not Run Yet

| Gate | Command | Risk if skipped |
|---|---|---|
| Build | `npm run build` | TypeScript or Vite production breakage can be missed |
| Coverage | `npm run test:coverage` | Regression coverage threshold not verified |
| Full validation suite rerun | `python -m validation_suite run --all` | Existing artifacts may be stale |
| Validation suite report | `python -m validation_suite report` | Human-readable falsification report not refreshed |
| Manuscript verifier | `python scripts/verify_manuscript.py` | Manuscript drift not checked |
| Red flags | `python check_redflags.py` | Overclaim/reference/synthetic wording drift not checked |
| Checksums | `sha256sum -c checksums.sha256` or Windows equivalent | Data integrity not verified |
| Python security | `npm run security:python` | Python security issues not checked |
| Dependency audit | `npm run security:deps` | npm dependency risk not checked |
| Full data lineage reruns | multiple scripts in `REPRODUCE.md` | Claims may rely on stale/generated artifacts |

## Minimum Release Gate

Source: `docs/RESULTS_CONTRACT.md`.

For release-facing edits, green status requires:

```text
python scripts/verify_manuscript.py
python scripts/validate_results_contracts.py
python check_redflags.py
python scripts/secret_scan.py
npm test
```

Current audit status:

| Required release gate | Current status |
|---|---|
| `python scripts/verify_manuscript.py` | NOT RUN |
| `python scripts/validate_results_contracts.py` | PASS via `npm run validate:results-contracts` |
| `python check_redflags.py` | NOT RUN |
| `python scripts/secret_scan.py` | PASS via `npm run security:secrets` |
| `npm test` | PASS via `npm test -- --run` |

Release gate is therefore `INCOMPLETE`, not ready.

## Claim-Promotion Gate

Before promoting any claim from technical/exploratory to public:

1. Add or identify structured artifact under `results/`.
2. Add artifact to `results/publication_canonical_index_*.json`.
3. Add field-level mapping to `results/publication_claim_matrix_*.json`.
4. Run `npm run validate:results-contracts`.
5. Run `python check_redflags.py`.
6. Run manuscript verifier if manuscript text changes.
7. Record commit hash and command output in the claim evidence note.

## Data Gate

Before treating result files as reproducible:

1. Cleanly classify files as raw, processed, generated, or exploratory.
2. Do not modify raw data.
3. Pair every generated artifact with the exact command and source input list.
4. Regenerate checksums for intended tracked artifacts only.
5. Keep `not_found` and `not_observed` interpretations descriptive.

## Current Reproducibility Verdict

`PARTIAL`.

The engineering smoke gates are green, but full scientific reproducibility is not established in this pass. The repo cannot honestly be called fully reproducible until the validation suite, manuscript verifier, red-flag scan, checksums, and dirty-tree review are complete.

