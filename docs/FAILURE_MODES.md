# Failure Modes Review (ARCHCODE)

**Canon Tier:** Technical Full-Scope  
**Release-facing:** No  
**Last Updated:** 2026-04-04

This file maps current failure modes to detection mechanisms and actual coverage.

| Failure mode | Description | Detection | Status | Evidence |
|--------------|-------------|-----------|--------|----------|
| Claim/version drift | Public and technical surfaces disagree on counts, wording, or release version | `scripts/validate_project_canon.py` + publication-integrity workflow | Implemented | `PROJECT_CANON.md`, `.github/workflows/publication-integrity.yml` |
| Results claim drift | Promoted release claims drift from tracked result artifacts | `scripts/validate_results_contracts.py` | Implemented | `docs/RESULTS_CONTRACT.md`, `results/publication_claim_matrix_2026-03-30.json` |
| Manuscript number/reference drift | DOI, table, and overclaim mismatches in manuscript text | `scripts/verify_manuscript.py` | Implemented | `scripts/verify_manuscript.py` |
| Mock/synthetic disclosure drift | Development-only or synthetic outputs appear publication-ready | `check_redflags.py` + policy docs | Partially automated | `CLAUDE.md`, `check_redflags.py` |
| Silent validation failure | Validation appears to pass without the expected artifacts or context | Results contract + canon validator + manual scientific review | Partial | `docs/VALIDATION.md`, `results/` |
| Secret regression | Secrets accidentally committed or documented | `scripts/secret_scan.py` + CI | Implemented | `scripts/secret_scan.py`, `security-gates.yml` |
| Score inversion / regression | Metric directionality or core engine behavior flips | Unit tests + gold-standard regression tests | Implemented | `src/__tests__/`, `test:gold` |
| Distribution shift / tissue mismatch over-interpretation | Cross-locus or cross-tissue results are promoted beyond their scope | Manual scientific review + applicability rules + canon validator | Partial | `docs/ARCHCODE_applicability_rules.md`, `PROJECT_CANON.md` |
| Performance regression | Large-genome or high-resolution runs become too slow or unstable | Manual observation | Needs automation | `KNOWN_ISSUES.md` |

## Current Gaps

- Performance baselines are not yet automated.
- Tissue-mismatch overinterpretation still depends on scientific review, not only CI.
- Some broader technical results remain sensitive to threshold and context choices even when honestly labeled.
