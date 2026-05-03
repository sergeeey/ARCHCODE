# ARCHCODE Project State Freeze

**Date:** 2026-05-03  
**Scope:** State/source-of-truth freeze, not new scientific analysis  
**Detailed working note:** `docs/PROJECT_STATE_FREEZE_20260503.md`

## Executive State

ARCHCODE is scientifically active, but the repository state is mixed. Paper 2 has a coherent submission package. Paper 1 is publicly posted on Research Square. Paper 3 has useful exploratory artifacts, but they are not ready to become a submission package or a single commit without curation.

Do not run `git add .`.

## Canonical Paper 1 Files

| File/Source | Status | Action |
|---|---|---|
| Research Square DOI `10.21203/rs.3.rs-9090074/v1` | Public status verified as `Posted`, Version 1 | Treat as current public Paper 1 surface |
| `PROJECT_CANON.md` | Canonical local release policy; says public research release `v2.17` | Keep as source of truth until explicitly updated |
| `docs/STATUS_DASHBOARD.md` | Conflicts with canon by saying `v2.18` reframed | Needs human decision before treating as canonical |
| `docs/PROJECT_UPDATE_2026-04-29.md` | Conflicts by saying `v5.0` spectral validation edition | Treat as project update / legacy status until reconciled |

## Canonical Paper 2 Files

| Role | File | Status |
|---|---|---|
| Main manuscript | `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx` | Canonical |
| Cover letter | `manuscript/cover_letter_HumanMutation.docx` | Canonical |
| Final checklist | `SUBMISSION_FINAL_CHECKLIST.md` | Canonical support |
| Data provenance audit | `DATA_PROVENANCE_AUDIT.md` | Canonical support |
| Reviewer risk register | `REVIEWER_RISK_REGISTER.md` | Support only, not source of truth |
| Cover letter addendum | `COVER_LETTER_ADDENDUM.md` | Support |
| Data notes | `results/README_DATA_NOTES.md` | Required with supplementary data |
| Atlas | `results/HBB_Unified_Atlas.csv` | Supplementary data |
| gnomAD population output | `results/gnomad_populations_pearls.csv` | Supplementary with stale-value caveat |
| Coverage check | `results/gnomad_coverage_check.json` | Numerical source for AF correction |
| Reproducibility script | `scripts/population_filter.py` | Tooling source |

## Canonical Spectral Validation State

| Source | Claim | Status |
|---|---|---|
| `PROJECT_CANON.md` | Public release `v2.17`; non-HBB material exploratory unless confirmed | Canonical |
| `docs/STATUS_DASHBOARD.md` | Public release `v2.18` reframed | Needs reconciliation |
| `docs/PROJECT_UPDATE_2026-04-29.md` | Version `v5.0` spectral validation edition | Needs reconciliation |

Until these are reconciled, the safe public statement is: Paper 1 is posted on Research Square as Version 1; local release/version labels are inconsistent and should not be promoted without a canon update.

## Stale / Legacy Files

| File/Folder | Category | Action |
|---|---|---|
| `manuscript/pypop_paper_HumanMutation_SUBMIT*.docx` backups | Legacy backups | Archive later |
| `manuscript/pypop_paper_FINAL.md` | Legacy/modified | Human decision |
| `manuscript/SUBMISSION_CHECKLIST_MAY4.md` | Legacy/modified | Human decision |
| `results/MULTI_LOCUS_ANALYSIS.md` | Legacy research claim | Do not cite without re-audit |
| `results/PURIFYING_SELECTION_RESULTS.md` | Legacy research claim | Do not cite without re-audit |
| `results/PEARL_VALIDATION_SUMMARY.md` | Legacy research claim | Do not cite without re-audit |

## Generated / Research Artifacts

| Pattern | Status | Action |
|---|---|---|
| `docs/PAPER3_*` | Paper 3 exploratory | Commit separately or hold |
| `results/PAPER3_*` | Paper 3 exploratory | Commit separately or hold |
| `results/paper3_*` | Paper 3 exploratory | Commit separately or hold |
| `scripts/paper3_*` | Paper 3 tooling | Commit separately or hold |
| `results/contact_matrices/` | Generated output | Do not include in broad commit |
| `stress_biology/`, `topology_control/` | Separate research areas | Human decision |

## Git State Policy

| Category | Files |
|---|---|
| Commit now | Paper 2 canonical package, `results/README_DATA_NOTES.md`, `results/gnomad_coverage_check.json`, `.agents/skills/*/SKILL.md`, this freeze/audit |
| Commit separately | `scripts/population_filter.py`, Paper 3 docs/results/scripts |
| Archive later | old manuscript backups, legacy strong-claim reports |
| Ignore/generated | contact matrices and generated result folders unless intentionally published |
| Human decision | `.claude/memory/*`, `.claude/skills/*`, global Codex MCP config |

## Current Blockers

No Paper 2 package blocker was found in this freeze pass. Final portal metadata still requires human verification before upload.

## Current Warnings

- `results/gnomad_populations_pearls.csv` contains stale preliminary AF context and must travel with `results/README_DATA_NOTES.md`.
- Version labels conflict: `v2.17` vs `v2.18` vs `v5.0`.
- `taskmaster` remains enabled in global Codex config outside this workspace and was not changed.
- Paper 3 artifacts are exploratory and should not be represented as a clean second regulatory-locus result yet.

