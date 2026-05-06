# AUDIT NEXT 30 DAYS PLAN

Date: 2026-05-05

## Goal

Move ARCHCODE from "strong integrity-aware research repo with dirty state" to "scientifically clean, reproducible, publishable-with-caveats project."

## Week 1: Freeze And Verify

| Day | Task | Output | Verification |
|---|---|---|---|
| 1 | Categorize dirty tree into user edits, generated results, docs, backups, exploratory Paper3, raw data | `DIRTY_TREE_CLASSIFICATION.md` | `git status --short` |
| 1 | Run missing release gates | `GATE_RUN_2026-05-xx.md` | command outputs |
| 2 | Rerun `python check_redflags.py` and manuscript verifier | redflag/manuscript report | PASS or issue list |
| 2 | Reconcile version labels | updated canon note or TODO | `rg "v2\\.17|v2\\.18|v5\\.0"` |
| 3 | Decide whether modified HBB atlas and summary are intended | lineage note | diff review |
| 4 | Rerun full validation suite or document blocker | refreshed `validation_suite/results/master_results.json` or `BLOCKED` note | command output |
| 5 | Create exact claim-drift issue list | `CLAIM_DRIFT_TODO.md` | file/line refs |

## Week 2: Claim Matrix Hardening

| Task | Output | Verification |
|---|---|---|
| Update or freeze publication claim matrix after dirty results decision | new or confirmed `publication_claim_matrix` | `npm run validate:results-contracts` |
| Add status markers to Paper3 docs | docs remain technical/exploratory | `npm run validate:project-canon` |
| Add population-screen caveat boilerplate | no universal-constraint language | `rg "universal|constraint|not_found|not_observed"` |
| Add AlphaGenome caveat boilerplate | no independent-proof wording | redflag scan |
| Downgrade MPRA-positive wording | MPRA remains null unless new structured artifact exists | claim matrix consistency |

## Week 3: Reproducibility And Data Lineage

| Task | Output | Verification |
|---|---|---|
| Create `DATA_LINEAGE_MANIFEST.md` | input -> script -> output matrix | manual review |
| Add schema checks for key CSVs | script or documented check | command output |
| Add Windows checksum instructions | reproducible checksum gate | successful checksum run |
| Add validation suite to npm scripts | easier standard gate | `npm run validation:suite` |
| Document API-key-dependent scripts | no hidden dependency surprises | docs review |

## Week 4: Scientific Publishability Decision

| Task | Output | Verification |
|---|---|---|
| Decide publication target for falsification-first framework | scope memo | human decision |
| Decide whether HBB pearl paper remains computational/hypothesis-only | scope memo | claim matrix |
| Decide TP53 follow-up design | preregistered internal plan | timestamped commit before run |
| Decide Paper3 freeze criteria | cohort/control/gate template | checklist |
| Prepare external collaboration packet for wet-lab validation | non-overclaiming one-pager | reviewer pass |

## Hypotheses To Advance

| Hypothesis | Next action |
|---|---|
| HBB pearl candidate set | Seek experimental validation; keep computational-only |
| TP53 within-category signal | Rebuild with matched RF/position baselines and external replication target |
| SCN5A cardiac tissue context | Recalibrate thresholds before publication-grade comparison |
| Falsification infrastructure | Package validation suite as the primary contribution |

## Hypotheses To Stop Or Downgrade

| Hypothesis | Action |
|---|---|
| General pathogenicity predictor | Stop permanently in public claims |
| HBB AUC as proof of physics | Always pair with ablation caveat |
| MPRA positive validation | Downgrade to null |
| gnomAD absence as constraint | Downgrade to descriptive |
| BCL11A as public second locus | Keep technical bridge only |

## First Three Fixes

1. Run the incomplete release gate suite and save outputs.
2. Classify dirty tree before any commit.
3. Build `CLAIM_DRIFT_TODO.md` with exact file/line references for strong wording.

## 30-Day Success Criteria

- Clean or intentionally categorized git state.
- All public claims map to claim matrix.
- All technical claims have status markers.
- Full validation suite rerun or explicitly blocked with reason.
- No `validated/confirmed/proved` language without corresponding evidence class.
- No synthetic or gnomAD absence overclaim.
- One primary publishable story selected: falsification infrastructure, not broad predictor performance.

## Project Score

| Dimension | Score |
|---|---:|
| Scientific honesty infrastructure | 8/10 |
| Engineering test baseline | 7/10 |
| Current reproducibility cleanliness | 5/10 |
| Data-lineage clarity | 5/10 |
| Claim discipline in public canon | 7/10 |
| Claim discipline across all docs/manuscripts/results | 4/10 |
| Biological validation strength | 4/10 |
| Publishability if framed as broad predictor | 2/10 |
| Publishability if framed as falsification/discovery framework | 7/10 |

Overall current score: `6.5/10`.

