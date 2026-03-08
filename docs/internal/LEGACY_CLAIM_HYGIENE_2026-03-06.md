# Legacy Claim Hygiene (2026-03-06)

This note defines publication-safe handling of legacy narrative artifacts in `manuscript/`,
`results/`, and `docs/internal/`.

## Canonical Sources of Truth

- `results/publication_claim_matrix_2026-03-06.json`
- `results/validation_canonical_index_2026-03-06.json`
- task-level canonical files (`task2_canonical_status_2026-03-06.json`, etc.)

## Rule

If any legacy file contains stronger wording than canonical claim gates, canonical artifacts take precedence.

## Legacy Files Explicitly Marked as Non-Canonical

- `manuscript/DISCUSSION.md`
- `results/LOOP_THAT_STAYED_EXECUTIVE_SUMMARY.md`
- `results/LOOP_THAT_STAYED_INDEX.md`
- `results/alphagenome_forum_post.md`
- `results/loop_that_stayed_comparative_table.md`
- `results/SCIENTIFIC_ABSTRACT.md`
- `results/VALIDATION_summary_Sabate2025.md`
- `results/blind_test_validation_2025.md`
- `results/README_results.md`

## Allowed Usage

- Historical traceability
- Hypothesis generation
- Internal experiment planning

## Blocked Usage

- Clinical reclassification claims
- Causal disease-mechanism proof claims
- External-validation claims beyond canonical verification
