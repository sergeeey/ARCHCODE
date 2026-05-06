# AUDIT PROJECT CONTEXT MAP

Date: 2026-05-05
Workspace: `D:\ДНК`
Branch: `experiment/spectral-collapse-pilot`
Audit depth self-rating at start: `6/10`

## Scope

This document maps the current ARCHCODE repository context for a scientific-integrity audit. It does not change scientific results, raw data, manuscripts, README claims, or production code.

## Phase 0 Repository Snapshot

Commands already run:

| Command | Outcome |
|---|---|
| `git branch --show-current` | `experiment/spectral-collapse-pilot` |
| `git log --oneline -20` | PASS; top commit `4fcb51f fix(paper3): handle empty population gates` |
| `git status --short` | Dirty tree observed |
| `git diff --stat` | 14 tracked files changed before this audit-doc generation |

Current dirty tree status before audit files:

- Modified tracked files include `.claude/memory/*`, `.claude/skills/*`, `manuscript/abstract_content.typ`, `manuscript/pypop_paper_FINAL.md`, `results/HBB_Unified_Atlas.csv`, `results/UNIFIED_ATLAS_SUMMARY.json`, `results/gnomad_populations_pearls.csv`, `results/spectral_sprint_log.md`, `scripts/generate-unified-atlas.ts`, and `src/domain/config/locus-config.ts`.
- Many untracked files exist under root, `docs/`, `manuscript/`, `results/`, `scripts/`, `stress_biology/`, and `topology_control/`.
- This state is not safe for broad staging. Do not use `git add .`.

## Mandatory Governance Files

| File | Role | Audit status |
|---|---|---|
| `AGENTS.md` | Codex execution protocol; approval gate and Implemented/Verified separation | READ |
| `CLAUDE.md` | Scientific Integrity Protocol; falsification-first; no phantom references; no invisible synthetic data | READ |
| `PROJECT_CANON.md` | Public / technical / legacy layer model and current claim policy | READ |
| `README.md` | Public canonical project narrative | READ |
| `REPRODUCE.md` | Reproducibility commands and expected artifacts | READ |
| `VALIDATION_PROTOCOL.md` | Claim levels and evidence contract | READ |
| `docs/RESULTS_CONTRACT.md` | Machine-checkable release claim contract | READ |
| `docs/VALIDATION.md` | Validation wording rules | READ |
| `docs/FAILURE_MODES.md` | Known failure modes and detection coverage | READ |
| `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` | Existing evidence map for TP53 and SCN5A | READ |

## Layer Model

Source: `PROJECT_CANON.md`.

| Layer | Intended use | Main files |
|---|---|---|
| Public Canonical | Narrow release-facing narrative | `README.md`, `submission_metadata.json`, selected `docs/`, selected manuscript surfaces |
| Technical Full-Scope | Broader research and exploratory analyses | `docs/VALIDATION.md`, `docs/FAILURE_MODES.md`, `manuscript/taxonomy_paper/*`, many `results/*.json` |
| Legacy | Provenance only; not current truth by default | `archive/legacy/*`, old audits, old reports |

Audit implication: a statement may be true as a technical or legacy artifact but invalid as a public claim.

## Codebase Map

| Area | Paths | Role | Risk |
|---|---|---|---|
| TypeScript engine | `src/engines/`, `src/domain/`, `src/simulation/` | Loop extrusion, contact maps, domain models | Metric directionality and parameter semantics must stay stable |
| React UI | `src/pages/`, `src/main.tsx`, `src/index.css` | Simulator frontend | Lower scientific risk, but can mislead if labels overclaim |
| TS pipelines | `scripts/*.ts` | Atlas generation, validation, simulation runners | High: changes can alter CSV/JSON schema and claims |
| Python analysis | `scripts/*.py`, `analysis/scripts/`, `tools/` | ROC, baselines, overlays, population analysis | High: claims often derive here |
| Validation suite | `validation_suite/` | Falsification battery | High value; must remain reproducible |
| Config | `config/`, `config/locus/` | Locus windows, thresholds, features | High: threshold/cell-context drift risk |
| Data | `data/`, `reference/`, `fastq_data/`, `stress_biology/data/` | Raw and processed biological inputs | Do not delete or silently rewrite |
| Results | `results/`, `analysis/`, `figures/`, `plots/` | Generated artifacts and evidence | High drift risk due many untracked generated files |
| Manuscripts/docs | `manuscript/`, `docs/`, root reports | Claims and narrative | Highest overclaim risk |

## Key Source-of-Truth Artifacts

| Claim domain | Source of truth |
|---|---|
| Release claim matrix | `results/publication_claim_matrix_2026-03-30.json` |
| Release evidence index | `results/publication_canonical_index_2026-03-30.json` |
| Canon validator | `scripts/validate_project_canon.py` |
| Results contract validator | `scripts/validate_results_contracts.py` |
| Secret scan | `scripts/secret_scan.py` |
| Unit/regression tests | `src/__tests__/` |
| Falsification suite artifacts | `validation_suite/results/*.json` |
| TP53 evidence inventory | `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` |

## Verified Gates So Far

| Gate | Command | Outcome |
|---|---|---|
| Project canon | `npm run validate:project-canon` | PASS: `PROJECT CANON PASSED.` |
| Results contract | `npm run validate:results-contracts` | PASS: `RESULTS CONTRACT PASSED.` |
| Secret hygiene | `npm run security:secrets` | PASS: `Secret scan PASSED.` |
| Unit/regression tests | `npm test -- --run` | PASS: 6 test files, 49 tests |

## Not Yet Verified

| Gate | Status |
|---|---|
| Full build | NOT RUN |
| Coverage gate | NOT RUN |
| Full validation suite rerun | NOT RUN; only existing `validation_suite/results/master_results.json` inspected |
| Manuscript verifier | NOT RUN in this pass |
| Red-flag scanner | NOT RUN in this pass |
| Checksums | NOT RUN |
| External DOI/API verification | NOT RUN |

## Breaking-Change Risks

| Risk | Evidence |
|---|---|
| Result schema/data drift | `results/HBB_Unified_Atlas.csv`, `results/UNIFIED_ATLAS_SUMMARY.json`, and `scripts/generate-unified-atlas.ts` modified in dirty tree |
| Public/technical claim drift | README is cautious, but searches found stronger validation/confirmation language in technical/manuscript files |
| Generated artifact sprawl | Many untracked `results/*`, `PAPER3_*`, backups, PDFs, and contact matrices |
| Raw/processed boundary unclear | `data/`, `results/`, `analysis/`, and `stress_biology/` all contain biologically meaningful artifacts |
| Canon version confusion | Existing audit `CODEX_PROJECT_AUDIT_2026-05-03.md` records local version-label conflict (`v2.17`, `v2.18`, `v5.0`) |

## Context Verdict

The repository has unusually strong claim-governance infrastructure, but it is in a dirty, artifact-heavy state. Current public canon is more cautious than several broader technical/manuscript surfaces. The next scientific-risk unit is not a code bug; it is preserving the chain:

`hypothesis -> data -> script -> result -> claim -> status`.

