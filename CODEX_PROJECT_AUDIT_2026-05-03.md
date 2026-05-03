# CODEX Project Audit

**Date:** 2026-05-03  
**Workspace:** `D:\ДНК`  
**Scope:** Stabilization, source-of-truth freeze, Paper 2 consistency check, no submission, no commit.

## Executive Verdict

`READY` for Paper 2 package handling after final human portal metadata check.  
`NEEDS_FIXES` for repository hygiene before broad commit or Paper 3 continuation.

The main issue is not scientific collapse. The main issue is state management: many legacy/generated files exist beside current canonical files.

## Canonical State

| Area | Current Source of Truth | Status |
|---|---|---|
| Project canon | `PROJECT_CANON.md` | PASS |
| State freeze | `PROJECT_STATE_FREEZE_2026-05-03.md` and `docs/PROJECT_STATE_FREEZE_20260503.md` | Created |
| Paper 2 manuscript | `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx` | PASS |
| Paper 2 cover letter | `manuscript/cover_letter_HumanMutation.docx` | PASS |
| Paper 2 provenance | `DATA_PROVENANCE_AUDIT.md`, `results/README_DATA_NOTES.md`, `results/gnomad_coverage_check.json` | PASS |
| Paper 3 | `docs/PAPER3_*`, `results/PAPER3_*`, `scripts/paper3_*` | Exploratory, not canonical submission package |

## Paper 1 Status

Research Square public page was checked on 2026-05-03:

- DOI: `10.21203/rs.3.rs-9090074/v1`
- Title: `Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots`
- Author shown: `Sergey V. Boyko`
- Status shown: `Posted`
- Version shown: `Version 1`

Local version labels conflict:

| File | Version Claim | Status |
|---|---|---|
| `PROJECT_CANON.md` | `v2.17` public research release | Canonical local policy |
| `docs/STATUS_DASHBOARD.md` | `v2.18` reframed | Needs reconciliation |
| `docs/PROJECT_UPDATE_2026-04-29.md` | `v5.0` spectral validation edition | Needs reconciliation |

## Paper 2 Status

File inventory passed. All required files exist:

- `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx`
- `manuscript/cover_letter_HumanMutation.docx`
- `SUBMISSION_FINAL_CHECKLIST.md`
- `COVER_LETTER_ADDENDUM.md`
- `DATA_PROVENANCE_AUDIT.md`
- `REVIEWER_RISK_REGISTER.md`
- `results/HBB_Unified_Atlas.csv`
- `results/gnomad_populations_pearls.csv`
- `results/gnomad_coverage_check.json`
- `scripts/population_filter.py`
- `results/README_DATA_NOTES.md`

Consistency scan:

| Check | Result | Evidence |
|---|---|---|
| Manuscript author | PASS | `Sergey Boyko=1`, `Sergey Kucherenko=0` in clean docx scan |
| Cover letter author | PASS | `Sergey Boyko=1`, `Sergey Kucherenko=0` in cover docx scan |
| Article type | PASS | `Brief Report=1`, `Short Report=0` in clean docx scan |
| Deprecated AF | PASS | `0.000193=0` in manuscript and cover letter docx scans |
| Corrected AF | PASS | `0.000648=3` in manuscript, `0.000648=2` in cover letter |
| Ronin wording | PASS | `application submitted; decision pending=1`; `affiliation pending confirmation=0` |
| Strong cover phrase | PASS | `misclassifications invisible=0` |
| VEP/CADD successful rows | PASS | 12 gnomAD-success rows matched to atlas; 12/12 `VEP_Impact=MODIFIER`; 12/12 `CADD_Phred < 20` |

## Git State

`git status --short` shows a dirty tree with modified and many untracked files. This is expected for the current work, but unsafe for broad commit.

Recommended categories:

| Category | Files |
|---|---|
| Safe to commit now | Paper 2 canonical docs, clean manuscript/cover letter, data notes, coverage JSON, `.agents/skills/*/SKILL.md`, audit/freeze docs |
| Commit separately | `scripts/population_filter.py`, Paper 3 docs/results/scripts |
| Archive later | old manuscript backups, legacy reports with strong validation language |
| Do not mass commit | `results/contact_matrices/`, pilot outputs, unrelated research folders |
| Human decision | `.claude/memory/*`, `.claude/skills/*`, global `C:\Users\serge\.codex\config.toml` |

## Agent/Skills Status

Four local project skills now have valid YAML frontmatter:

- `.agents/skills/implementer/SKILL.md`
- `.agents/skills/planner/SKILL.md`
- `.agents/skills/reviewer/SKILL.md`
- `.agents/skills/security-check/SKILL.md`

Global MCP config was inspected but not edited because it is outside the workspace:

- `fred` is already disabled.
- `taskmaster` remains enabled and is a human decision.

## Tests Run

| Command | Result |
|---|---|
| `npm run validate:project-canon` | `PROJECT CANON PASSED.` |
| `npm run validate:results-contracts` | `RESULTS CONTRACT PASSED.` |
| `npm run security:secrets` | `Secret scan PASSED.` |
| `npm test -- --run` | PASS: 6 test files, 49 tests |

## Blockers

No Paper 2 internal-consistency blocker found.

Repository-level blocker before broad commit:

- The working tree contains many unrelated/generated/untracked files. Do not use `git add .`.

## Warnings

- `results/gnomad_populations_pearls.csv` contains stale preliminary AF context; use only with `results/README_DATA_NOTES.md`.
- Paper 1 release labels are inconsistent across local docs.
- Paper 3 HBA1/BCL11A/CFTR artifacts are exploratory; do not frame them as completed validation.
- `taskmaster` MCP remains enabled globally.

## Safe to Commit

Suggested first commit scope:

- `.agents/skills/implementer/SKILL.md`
- `.agents/skills/planner/SKILL.md`
- `.agents/skills/reviewer/SKILL.md`
- `.agents/skills/security-check/SKILL.md`
- `PROJECT_STATE_FREEZE_2026-05-03.md`
- `docs/PROJECT_STATE_FREEZE_20260503.md`
- `CODEX_PROJECT_AUDIT_2026-05-03.md`
- `SUBMISSION_FINAL_CHECKLIST.md`
- `COVER_LETTER_ADDENDUM.md`
- `DATA_PROVENANCE_AUDIT.md`
- `REVIEWER_RISK_REGISTER.md`
- `results/README_DATA_NOTES.md`
- `results/gnomad_coverage_check.json`
- `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx`
- `manuscript/cover_letter_HumanMutation.docx`

## Do Not Commit

Do not include in the first stabilization commit:

- `results/contact_matrices/`
- all `PAPER3_*` / `paper3_*` outputs unless making a separate Paper 3 research commit
- old manuscript backups
- unrelated `stress_biology/` and `topology_control/` trees
- global Codex config

## Next 30 Minutes

1. Make a targeted Paper 2 + infra commit from the safe list.
2. Create a separate Paper 3 branch or commit for exploratory HBA1/BCL11A/CFTR work.
3. Decide whether to reconcile `v2.17`, `v2.18`, and `v5.0` labels now or defer.
4. Decide whether to disable `taskmaster` in global Codex config.

## Next 7 Days

1. Reconcile Paper 1 public/local versioning.
2. Prepare a Research Square update plan only after the version conflict is resolved.
3. Keep Paper 3 as mechanism-stratified falsification, not generic multi-locus expansion.
4. Freeze selection rules before adding more loci.

## Suggested Commit Message

```text
Freeze ARCHCODE project state and Paper 2 submission package
```

