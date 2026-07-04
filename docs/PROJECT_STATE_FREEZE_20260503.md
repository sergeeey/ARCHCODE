# ARCHCODE Project State Freeze

**Date:** 2026-05-03  
**Scope:** State/source-of-truth freeze, not new scientific analysis  
**Verdict:** `READY` for Paper 2 package handling; repository cleanup still needed before broad commit

## Current Canonical State

| File/Folder | Category | Reason | Action |
|---|---|---|---|
| `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx` | Paper 2 canonical | Clean manuscript exists; docx scan confirms `Sergey Boyko`, `Brief Report`, `0.000648`, no `0.000193` | Use for Human Mutation upload |
| `manuscript/cover_letter_HumanMutation.docx` | Paper 2 canonical | Cover letter exists; docx scan confirms aligned author/affiliation and no deprecated AF | Use for Human Mutation upload |
| `SUBMISSION_FINAL_CHECKLIST.md` | Paper 2 canonical checklist | States READY; documents stale CSV warning and updated coverage source | Commit with Paper 2 package |
| `DATA_PROVENANCE_AUDIT.md` | Paper 2 canonical audit | Documents `0.000648`, stale `0.000193`, VEP/CADD 12/12 verification | Commit with Paper 2 package |
| `COVER_LETTER_ADDENDUM.md` | Paper 2 support | Contains provenance/addendum wording for cover letter | Keep with Paper 2 package |
| `REVIEWER_RISK_REGISTER.md` | Paper 2 support | Reviewer-response preparation; not a submission upload file by itself | Commit as support doc |
| `results/README_DATA_NOTES.md` | Paper 2 canonical data note | Explains supplementary data, stale CSV, and authoritative coverage JSON | Commit with supplementary data |
| `results/HBB_Unified_Atlas.csv` | Paper 2 supplementary | Source atlas for HBB annotations; 1103 rows verified locally | Commit only if intended current atlas state is accepted |
| `results/gnomad_populations_pearls.csv` | Paper 2 supplementary with warning | Contains 17 rows; includes stale preliminary `0.000193` context documented elsewhere | Include only with `README_DATA_NOTES.md` caveat |
| `results/gnomad_coverage_check.json` | Paper 2 numerical source of truth | Confirms `VCV000015471 AF_EAS=0.000648053...` and `VCV000015466 AF_EAS=0.000464354...` | Commit with Paper 2 package |
| `scripts/population_filter.py` | Shared tooling | Generic CLI exists; now always writes JSON summary and has explicit not-observed opt-in | Commit as separate tooling change or with Paper 3 tooling |
| `.agents/skills/*/SKILL.md` | Infrastructure fix | Added required YAML frontmatter to 4 local skills | Commit as infra cleanup |
| `docs/PAPER3_*`, `results/PAPER3_*`, `results/paper3_*`, `scripts/paper3_*` | Paper 3 research artifacts | Useful exploratory evidence; not part of Paper 2 submission | Commit separately from Paper 2 or archive until Paper 3 branch |
| `manuscript/pypop_paper_HumanMutation_SUBMIT*.docx` backups | Legacy/backups | Older manuscript versions and timestamped backups | Archive later; do not use as source of truth |
| `manuscript/pypop_paper_FINAL.md`, `manuscript/SUBMISSION_CHECKLIST_MAY4.md`, `manuscript/abstract_content.typ` | Legacy/modified | Existing modified files predate this freeze; not canonical for Paper 2 package | Needs human decision before commit |
| `.claude/memory/*` | Agent memory | Modified/untracked state files; not submission evidence | Needs human decision |
| `results/MULTI_LOCUS_ANALYSIS.md`, `results/PURIFYING_SELECTION_RESULTS.md`, `results/PEARL_VALIDATION_SUMMARY.md` | Legacy research claims | Older reports contain stronger validation/confirmed framing | Archive or mark legacy; do not cite as current source |
| `results/brca1_*`, `results/cftr_pypop_pilot_20260503.csv`, `results/sfi_*`, `results/contact_matrices/` | Generated/research artifacts | Not Paper 2 canonical; may be large or pilot-only | Ignore/generated or Paper 3 branch decision |
| `scripts/gnomad_*`, `scripts/query_brca1_populations.py`, `scripts/test_*` | Experimental tooling | Multiple query/test variants; not canonical Paper 2 path | Archive later unless actively used |
| `C:\Users\serge\.codex\config.toml` | Global Codex config | `fred` already disabled; `taskmaster` still enabled; outside workspace | Not changed; human decision if disabling global MCP |

## Files Safe To Submit

| Role | File |
|---|---|
| Main manuscript | `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx` |
| Cover letter | `manuscript/cover_letter_HumanMutation.docx` |
| Data notes | `results/README_DATA_NOTES.md` |
| HBB atlas | `results/HBB_Unified_Atlas.csv` |
| gnomAD population CSV | `results/gnomad_populations_pearls.csv` with stale-value caveat |
| Coverage check | `results/gnomad_coverage_check.json` |
| Reproducibility script | `scripts/population_filter.py` |

## Files Safe To Commit Now

Recommended as a **Paper 2 + infra freeze commit**:

- `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx`
- `manuscript/cover_letter_HumanMutation.docx`
- `SUBMISSION_FINAL_CHECKLIST.md`
- `COVER_LETTER_ADDENDUM.md`
- `DATA_PROVENANCE_AUDIT.md`
- `REVIEWER_RISK_REGISTER.md`
- `results/README_DATA_NOTES.md`
- `results/gnomad_coverage_check.json`
- `.agents/skills/implementer/SKILL.md`
- `.agents/skills/planner/SKILL.md`
- `.agents/skills/reviewer/SKILL.md`
- `.agents/skills/security-check/SKILL.md`

Commit separately or hold for Paper 3 branch:

- `scripts/population_filter.py`
- `docs/PAPER3_*`
- `results/PAPER3_*`
- `results/paper3_*`
- `scripts/paper3_*`

Do **not** mass-commit all untracked files.

## Blockers

None identified for Paper 2 package upload after final human portal metadata check.

## Warnings

- `results/gnomad_populations_pearls.csv` contains a superseded preliminary AF value (`0.000193`) and must only be used with `results/README_DATA_NOTES.md`.
- The manuscript title/running title still uses "Validation Framework"/"Population Validation" language. This is canonical as of this freeze, but it remains a reviewer-tone risk.
- `REVIEWER_RISK_REGISTER.md` is support material, not a source of truth for manuscript claims.
- `taskmaster` MCP remains enabled in global config outside the project; not changed in this pass.
- Many legacy reports contain strong terms like "confirmed" or "validated"; do not use them as current source of truth without re-audit.

## Verification Evidence

| Check | Result | Evidence |
|---|---|---|
| Skill frontmatter | PASS | 4 local `.agents/skills/*/SKILL.md` files now start with YAML frontmatter |
| Paper 2 file inventory | PASS | All canonical manuscript/checklist/audit/data/script files exist |
| Clean manuscript author/type | PASS | docx scan: `Sergey Boyko=1`, `Brief Report=1`, `Sergey Kucherenko=0`, `Short Report=0` |
| Clean manuscript AF | PASS | docx scan: `0.000193=0`, `0.000648=3` |
| Cover letter AF | PASS | docx scan: `0.000193=0`, `0.000648=2` |
| Coverage JSON | PASS | `VCV000015471 AF_EAS=0.000648053...`; `VCV000015466 AF_EAS=0.000464354...` |
| Secret scan | PASS | `python scripts/secret_scan.py` |
| Test suite | PASS | `npm test -- --run`: 6 test files, 49 tests passed |

## Next 30 Minutes

1. Create a Paper 2-only commit from the safe-to-commit list.
2. Create a separate Paper 3 research branch/commit for `PAPER3_*` and `paper3_*` artifacts.
3. Archive or quarantine older reports with over-strong "validated/confirmed" language.
4. Decide whether to edit global `C:\Users\serge\.codex\config.toml` to disable `taskmaster`.
