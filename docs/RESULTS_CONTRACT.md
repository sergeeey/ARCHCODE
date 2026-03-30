# Results Contract

Machine-checkable contract for release-facing ARCHCODE result artifacts.

## Goal

Promote only claims that satisfy all three requirements:

1. Structured artifact exists in `results/`
2. Artifact path is listed in a canonical publication index
3. Claim text is mapped to explicit field-level evidence in a publication claim matrix

If one of these is missing, the claim stays `UNVERIFIED` for release purposes even if it appears in prose.

## Canonical Release Files

- `results/publication_canonical_index_2026-03-30.json`
- `results/publication_claim_matrix_2026-03-30.json`
- `scripts/validate_results_contracts.py`

Legacy governance files remain in force for older task-specific content:

- `results/publication_claim_matrix_2026-03-06.json`
- `results/validation_canonical_index_2026-03-06.json`

## Required Top-Level Fields

### Publication Canonical Index

Required keys:

- `generated_at_utc`
- `scope`
- `release_surface`
- `governance`
- `source_of_truth`
- `note`

`governance` must include:

- `legacy_claim_governance`
- `results_contract_doc`
- `validator`

`source_of_truth` must enumerate release-facing evidence groups such as:

- atlas scale
- ROC / thresholds
- concordance / complementarity
- Hi-C validation
- AlphaGenome validation
- MPRA cross-validation
- ablation
- conservation / population data

### Publication Claim Matrix

Required keys:

- `generated_at_utc`
- `scope`
- `governance_source`
- `claims`
- `summary`

Each claim entry must include:

- `id`
- `surface`
- `claim_text`
- `status`
- `evidence`
- `evidence_values`
- `required_wording`
- `caveats`

## Enforcement

Run:

```bash
python scripts/validate_results_contracts.py
```

The validator fails closed on:

- missing files
- invalid JSON
- missing required keys
- missing evidence paths
- numeric drift between promoted claim values and source artifacts

## Release Rule

For release-facing edits, green status requires all of:

```bash
python scripts/verify_manuscript.py
python scripts/validate_results_contracts.py
python check_redflags.py
python scripts/secret_scan.py
npm test
```

This contract does not replace scientific judgment. It enforces that public claims remain anchored to tracked artifacts and cannot silently drift from them.
