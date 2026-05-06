# AUDIT CLAIMS AND EVIDENCE

Date: 2026-05-05
Claim status vocabulary requested: `SUPPORTED`, `PRELIMINARY`, `OVERCLAIM`, `UNSUPPORTED`, `NEEDS_VERIFICATION`.

## Evidence Rules

- `SUPPORTED`: mapped to a local artifact and passed governance checks in this audit.
- `PRELIMINARY`: local evidence exists, but caveats or missing external validation prevent stronger wording.
- `OVERCLAIM`: wording exceeds evidence or violates project canon.
- `UNSUPPORTED`: no inspected evidence supports the claim.
- `NEEDS_VERIFICATION`: plausible, but not verified in this pass.

## Verified Governance Claims

| Claim | Status | Evidence |
|---|---|---|
| Project canon currently passes | SUPPORTED | `npm run validate:project-canon` -> `PROJECT CANON PASSED.` |
| Results contract currently passes | SUPPORTED | `npm run validate:results-contracts` -> `RESULTS CONTRACT PASSED.` |
| Secret scan currently passes | SUPPORTED | `npm run security:secrets` -> `Secret scan PASSED.` |
| TS unit/regression tests pass | SUPPORTED | `npm test -- --run` -> 6 test files, 49 tests |
| Repository is dirty | SUPPORTED | `git status --short` |

## Public Claim Matrix Summary

Source: `results/publication_claim_matrix_2026-03-30.json`.

| ID | Claim summary | Audit classification | Caveat |
|---|---|---|---|
| P01 | 30,318 variants across 9 primary loci | SUPPORTED | Excludes later exploratory scaling |
| P02 | HBB AUC 0.977 / threshold / sensitivity / specificity | SUPPORTED | HBB-specific; not universal threshold or mechanism proof |
| P03 | 27 HBB pearls / 54 Class B / CADD complementarity | PRELIMINARY | Candidate set; not clinical reclassification |
| P04 | Tissue-specificity gradient | PRELIMINARY | Applicability statement, not causal biology |
| P05 | Hi-C correlations 0.28-0.59 | PRELIMINARY | Benchmark is locus/cell-context limited |
| P06 | AlphaGenome CAGE disruption stronger for pearls | PRELIMINARY | Real API claimed, but promoter cluster and training overlap caveats |
| P07 | AlphaGenome ISM hotspot at HBB promoter | PRELIMINARY | Local promoter sensitivity, not clinical validation |
| P08 | MPRA cross-validation is globally null | SUPPORTED | Null result must not be reworded as positive MPRA validation |
| P09 | Ablation shows category encoding drives HBB AUC | SUPPORTED | Must accompany high-AUC claims |
| P10 | Conservation/gnomAD descriptive support | PRELIMINARY | gnomAD absence is not universal constraint proof |

## Falsification Claims

| Claim | Status | Evidence | Required wording |
|---|---|---|---|
| Broad pathogenicity prediction fails | SUPPORTED | `README.md`; `PROJECT_CANON.md`; `validation_suite/results/master_results.json` | "Not a pathogenicity predictor" |
| HBB AUC is category-driven | SUPPORTED | P09; `results/ablation_effectstrength.json`; README | "catalog/category effect", not independent physics |
| Simple baselines often beat SSIM | SUPPORTED | `validation_suite/results/master_results.json` | "baselines match or beat on most loci" |
| Within-category signal is generally weak | SUPPORTED | `validation_suite/results/master_results.json` | "near chance for most loci" |
| TP53 has a surviving within-category signal | PRELIMINARY | `validation_suite/results/within_category_tp53.json`; `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` | "surviving signal island; needs matched baseline/external replication" |
| HBB CTCF-specific architecture is proven by shuffle | OVERCLAIM | HBB `ctcf_shuffle` verdict FAIL in master results | Do not claim; redesign control |

## Claim Drift Hotspots

| Surface | Drift risk | Evidence |
|---|---|---|
| `manuscript/taxonomy_paper/body_content.typ` | Strong "validated/confirmed" style language around taxonomy, AlphaGenome, BCL11A, external cases | Search hits in earlier audit pass |
| `docs/ARCHCODE_experiment_backlog.md` | Several experiments marked completed with strong AUC/validation language | Search hits in earlier audit pass |
| `results/ARCHCODE_VS_VEP_CADD.md` | Contains strong "ARCHCODE correct, VEP wrong" style conclusion | Search hit |
| Paper3 files | Many exploratory outputs may read as completed gates | Untracked `docs/PAPER3_*`, `results/PAPER3_*`, `scripts/paper3_*` |
| Paper2 manuscript/results | Dirty tree includes manuscript and population-result changes | `git status --short` |

## Overclaims To Block

| Overclaim | Reason |
|---|---|
| "ARCHCODE is validated as a clinical pathogenicity predictor" | Violates public canon and validation evidence |
| "HBB AUC proves 3D physics adds independent predictive value" | Category ablation undermines this |
| "MPRA validates HBB pearl variants" | Promoted artifact is null |
| "AlphaGenome independently confirms pearl pathogenicity" | Auxiliary model, promoter cluster, possible training/domain overlap |
| "not_found/not_observed proves universal constraint" | Explicitly forbidden by `CLAUDE.md` and reviewer risk register |
| "BCL11A is second public-canonical Class B locus" | Current bridge docs explicitly block public promotion |
| "parameters fitted to FRAP" | Deprecated unless fitting artifacts exist |
| "synthetic saturation scan is real biological validation" | Violates synthetic data policy |

## Publishability Assessment

| Component | Publishability | Reason |
|---|---|---|
| Falsification-first engineering framework | HIGH | Strong, honest, reproducible framing; current tests pass |
| ARCHCODE as discovery engine | MODERATE/HIGH | Useful if framed narrowly with caveats |
| HBB pearl candidate narrative | MODERATE | Interesting but computational; needs experimental validation |
| TP53 signal island | MODERATE | Needs stronger baseline and external replication |
| General predictor claim | LOW/STOP | Refuted by current evidence |
| Paper3 multi-locus extension | LOW/MODERATE | Exploratory; needs frozen cohort/control design and clean lineage |
| Clinical reclassification claims | STOP | Not supported |

## Scientific Value Assessment

The strongest scientific value is not "ARCHCODE predicts pathogenicity." The strongest value is a documented case study and tooling stack showing how a plausible 3D-genome predictor claim collapses under falsification while leaving narrower, testable mechanistic hypotheses.

Project score for scientific honesty infrastructure: `8/10`.
Project score for current publication cleanliness: `5/10`.
Project score for broad biological validation: `4/10`.
Overall current project score: `6.5/10`.

