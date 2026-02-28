# ARCHCODE Validation Contract

This contract defines minimum integrity and validation rules for simulation outputs.

## Gate 0: Scientific Integrity

1. Do not claim parameter fitting to datasets that are not present in the repository.
2. Do not cite non-existent papers.
3. Parameters without direct experimental fit must be labeled as `MODEL PARAMETER` or `EXPLORATORY`.
4. Publication-facing text must use: `estimated from literature ranges` when direct fit artifacts are absent.

## Data Provenance Rules

1. Validation artifacts must state the data source explicitly (`experimental`, `mock`, or `synthetic`).
2. Mock or synthetic outputs are allowed for development only.
3. Any publication claim must be backed by experimental provenance and reproducible scripts.

## Decision Matrix

| Scenario                             | Source            | Allowed for dev | Allowed for publication |
| ------------------------------------ | ----------------- | --------------- | ----------------------- |
| Quick local simulation               | Synthetic/mock    | Yes             | No                      |
| Hi-C validation script               | Experimental Hi-C | Yes             | Yes                     |
| Missing experimental source metadata | Unknown           | Yes (temporary) | No                      |

## Required Evidence for Publication

1. A reproducible command that generates the reported result.
2. A tracked artifact in `results/` with source metadata.
3. Consistent wording in docs: no `fitted to FRAP data` claims unless raw FRAP data exists in-repo.
