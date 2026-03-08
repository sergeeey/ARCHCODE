# Legacy JSON Claim Hygiene (2026-03-06)

Scope: high-risk legacy JSON artifacts with clinical-style wording.

## Canonical Sources

- `results/publication_claim_matrix_2026-03-06.json`
- `results/validation_canonical_index_2026-03-06.json`
- `results/task2_canonical_status_2026-03-06.json`

## Updated Legacy JSON Files

- `results/individual_reports/VCV000000026_analysis.json`
- `results/individual_reports/VCV000000302_analysis.json`
- `results/individual_reports/VCV000000327_analysis.json`
- `results/vus_batch_analysis_loop_that_stayed.json`
- `results/vus_validation_report.json`

## Applied Guardrails

- Added top-level `canonical_governance` blocks.
- Marked files as `legacy_non_canonical_for_claims` or `deprecated_for_claims`.
- Explicitly blocked standalone clinical reclassification usage (`BLOCKED_UNVERIFIED`).
- Linked each file to canonical source-of-truth artifacts.

## Interpretation Rule

Legacy JSON files are allowed for historical traceability and hypothesis generation only.
Any publication, causal, or clinical claim must be derived from canonical validation artifacts.
