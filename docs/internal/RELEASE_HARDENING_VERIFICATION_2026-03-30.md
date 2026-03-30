# RELEASE_HARDENING_VERIFICATION_2026-03-30

Scope: publication-integrity hardening added after the `52b3bba` integrity-fix commit.

## Implemented

- Added [publication-integrity.yml](D:/ДНК/.github/workflows/publication-integrity.yml)
  - New dedicated GitHub Actions workflow for release-facing integrity gates.
  - Runs manuscript verification, results-contract validation, red-flag scan, secret scan, and unit tests.
- Added [validate_results_contracts.py](D:/ДНК/scripts/validate_results_contracts.py)
  - New machine-checkable validator for release-facing result contracts.
  - Enforces file existence, required JSON structure, and numeric consistency for promoted publication claims.
- Added [RESULTS_CONTRACT.md](D:/ДНК/docs/RESULTS_CONTRACT.md)
  - Documents the required structure for canonical publication evidence and claim matrices.
- Added [publication_canonical_index_2026-03-30.json](D:/ДНК/results/publication_canonical_index_2026-03-30.json)
  - New release-facing canonical evidence index for promoted README/manuscript claims.
- Added [publication_claim_matrix_2026-03-30.json](D:/ДНК/results/publication_claim_matrix_2026-03-30.json)
  - New promoted-claims registry with explicit evidence mappings and caveats.
- Updated [package.json](D:/ДНК/package.json)
  - Added `npm run validate:results-contracts`.
- Updated [README.md](D:/ДНК/README.md)
  - Removed unsupported positive MPRA wording.
  - Aligned public MPRA text with the current structured artifact (`results/mpra_crossvalidation_summary.json`), which supports a null global cross-validation result.
- Updated [README_results.md](D:/ДНК/results/README_results.md)
  - Pointed results-manifest governance to the new 2026-03-30 publication index and claim matrix while retaining legacy task-governance references.

## Verified

### Local working tree verification

- Command: `python scripts/validate_results_contracts.py`
  - Result: `RESULTS CONTRACT PASSED.`
- Command: `npm run validate:results-contracts`
  - Result: `RESULTS CONTRACT PASSED.`
- Command: `python scripts/verify_manuscript.py`
  - Result: all three modules passed; final status `ALL CHECKS PASSED`.
- Command: `python check_redflags.py`
  - Result: `RED FLAGS: НЕ ОБНАРУЖЕНЫ`.
- Command: `python scripts/secret_scan.py`
  - Result: `Secret scan PASSED.`
- Command: `npm test`
  - Result: `5 passed` test files, `44 passed` tests.
- Command: `npm run build`
  - Result: build succeeded; output emitted to [dist](D:/ДНК/dist).

### Clean worktree reproduction

- Command: `git worktree add --detach .codex-cleanroom 52b3bba849596ebb841d4d02a30ab98c299d86f7`
  - Result: clean detached worktree created from committed `HEAD`.
- Command: `npm ci` in `.codex-cleanroom`
  - Result: install completed; `found 0 vulnerabilities`.
- Command: `python scripts/verify_manuscript.py` in `.codex-cleanroom`
  - Result: passed.
- Command: `python scripts/secret_scan.py` in `.codex-cleanroom`
  - Result: passed.
- Command: `python check_redflags.py` in `.codex-cleanroom`
  - Result: passed.
- Command: `npm test` in `.codex-cleanroom`
  - Result: `44 passed`.
- Command: `git worktree remove --force .codex-cleanroom`
  - Result: temporary clean worktree removed.

## Notes

- The clean worktree reproduction above validates committed baseline `52b3bba`.
- The new publication-hardening files in this session are not committed yet; they were verified in the current working tree, not in the detached clean worktree.
- Unrelated modified/untracked user files outside the hardening scope were not touched.

## Verdict

`READY`
