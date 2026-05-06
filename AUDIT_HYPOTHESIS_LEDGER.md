# AUDIT HYPOTHESIS LEDGER

Date: 2026-05-05
Status vocabulary requested: `ACTIVE`, `SUPPORTED_PRELIMINARY`, `NOT_YET`, `REBUILD`, `STOP`, `NEGATIVE`, `BLOCKED`, `DEPRECATED`, `UNKNOWN`.

## Ledger Rules

- `SUPPORTED_PRELIMINARY` means reproducible local evidence exists, but not enough for `validated`, `confirmed`, or clinical/publication-grade proof.
- `NEGATIVE` means current evidence argues against the hypothesis.
- `STOP` means do not promote or continue without redesign.
- `REBUILD` means the idea may be useful, but the current design/evidence chain must be reconstructed before more claims.
- `NOT_YET` means plausible but not adequately tested.
- `UNKNOWN` means insufficient evidence was inspected in this pass.

## Main Hypotheses

| ID | Hypothesis | Status | Evidence | Notes |
|---|---|---|---|---|
| H01 | ARCHCODE is a general pathogenicity predictor across loci | STOP | `README.md`; `PROJECT_CANON.md`; `validation_suite/results/master_results.json` | Public canon already rejects this framing. Simple baselines and within-category tests undermine broad predictor claims. |
| H02 | HBB high AUC demonstrates independent structural prediction power | NEGATIVE | `results/publication_claim_matrix_2026-03-30.json` P02 and P09; `validation_suite/results/master_results.json` | HBB AUC is supported as a metric, but ablation says category mapping drives it. Claim must be framed as catalog characterization, not independent predictor power. |
| H03 | HBB Class B / pearl set is a computationally defined structural blind-spot candidate set | SUPPORTED_PRELIMINARY | `README.md`; `results/publication_claim_matrix_2026-03-30.json` P03, P06, P07, P08, P10 | Supported as computational candidate/hypothesis set. Not experimentally validated and not clinical reclassification evidence. |
| H04 | HBB pearls are experimentally confirmed pathogenic architecture variants | STOP | `CLAUDE.md`; `README.md` limitations; `docs/VALIDATION.md` | No allele-specific Capture Hi-C / RT-qPCR / functional assay evidence inspected. Must not claim confirmed pathogenicity. |
| H05 | MPRA validates HBB pearl mechanism | NEGATIVE | `results/publication_claim_matrix_2026-03-30.json` P08 | Current structured MPRA artifact is globally null; positive MPRA wording is overclaim unless backed by a newer promoted artifact. |
| H06 | AlphaGenome real API provides auxiliary support for HBB promoter hotspot | SUPPORTED_PRELIMINARY | `results/publication_claim_matrix_2026-03-30.json` P06, P07 | Real API outputs are claimed, but promoter cluster/pseudoreplication and training overlap caveats block independent-confirmation language. |
| H07 | AlphaGenome proves independent orthogonal validation | OVERCLAIM/STOP | `README.md` caveats; `results/publication_claim_matrix_2026-03-30.json` P06/P07 | Same K562/4DN domain caveat; use as auxiliary, not definitive validation. |
| H08 | TP53 within-category signal is a real surviving signal island | SUPPORTED_PRELIMINARY | `validation_suite/results/within_category_tp53.json`; `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md`; `results/tp53_splice_region_deep_dive.json` | TP53 has 4/4 categories surviving FDR in suite artifact. Splice-region AUC approx 0.691, but RF baseline stronger in deep dive. |
| H09 | TP53 splice-region signal uniquely proves ARCHCODE physics advantage | REBUILD | `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` | Signal exists, but RF baseline AUC 0.825 in inspected evidence beats SSIM/LSSIM. Needs matched design and external replication. |
| H10 | Simple baselines are weaker than ARCHCODE across the atlas | NEGATIVE | `validation_suite/results/master_results.json` | RF/logistic/severity baselines beat or match SSIM on most loci; GJB2 simple baseline FAIL. |
| H11 | CTCF architecture specificity is proven by shuffle controls | NEGATIVE/REBUILD | `validation_suite/results/master_results.json` | HBB CTCF shuffle verdict FAIL; many shuffled AUCs equal real AUC. Need better interpretation of what shuffle implementation actually tests. |
| H12 | Cross-locus threshold transfer is robust | NEGATIVE | `README.md`; validation suite README/master results | Public README says cross-locus transfer fails. Do not promote universal threshold. |
| H13 | Tissue specificity gradient is a domain-of-applicability observation | SUPPORTED_PRELIMINARY | `results/publication_claim_matrix_2026-03-30.json` P04; `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md` | Supported with caveat. Not causal proof. |
| H14 | SCN5A cardiac context improves over K562 mismatch | SUPPORTED_PRELIMINARY/REBUILD | `docs/HYPOTHESIS_INVENTORY_EVIDENCE.md`; `analysis/scn5a_cardiac_comparison.json` | Full cardiac atlas is recorded, but config warns thresholds require recalibration. Publication-grade claim needs recalibration gate. |
| H15 | BCL11A/Casgevy bridge establishes second public-canonical Class B locus | STOP | `docs/BCL11A_CASGEVY_BRIDGE.md`; `PROJECT_CANON.md` | Current BCL11A is technical bridge only; public canon should not promote it. |
| H16 | Paper3 HBA1/HBG1/LDLR/TERT/GATA1/CFTR exploratory gates are completed validations | REBUILD | `docs/PAPER3_*`; `results/PAPER3_*`; dirty untracked outputs | Many artifacts exist, but this pass did not reconstruct full lineage. Keep exploratory until frozen cohort, controls, and rerun evidence are documented. |
| H17 | Population stratification can flag false positives / epidemiology-discordant HBB calls | SUPPORTED_PRELIMINARY | `REVIEWER_RISK_REGISTER.md`; `DATA_PROVENANCE_AUDIT.md`; modified `results/gnomad_populations_pearls.csv` | Proof-of-concept only; small n and dirty-tree result modifications require caution. |
| H18 | gnomAD not-found / not-observed variants prove universal constraint | STOP | `CLAUDE.md`; `REVIEWER_RISK_REGISTER.md` | Absence is not universal proof. Must state as descriptive or consistent-with only. |
| H19 | Synthetic variant scans can support mechanistic intuition | ACTIVE | `CLAUDE.md`; `manuscript/taxonomy_paper/body_content.typ` search hits | Allowed only if clearly watermarked and excluded from real-data validation. |
| H20 | Synthetic scans can be used as real biological validation | STOP | `CLAUDE.md` | Violates no invisible synthetic data rule. |
| H21 | Parameters alpha/gamma are fitted to FRAP data | DEPRECATED/STOP | `CLAUDE.md`; `README.md` limitation wording | Project policy says use manually calibrated / literature ranges unless fitting artifacts exist. |
| H22 | ARCHCODE engine and validation suite are valuable as falsification infrastructure | SUPPORTED_PRELIMINARY | `README.md`; `validation_suite/README.md`; passed `npm test -- --run` | Strongest surviving project value: reproducible stress-testing and claim governance. |
| H23 | Paper2 PyPop-style HBB population manuscript is internally consistent | UNKNOWN/SUPPORTED_PRELIMINARY | `CODEX_PROJECT_AUDIT_2026-05-03.md`; current modified manuscript files | Earlier audit says no blocker, but current dirty manuscript/data files were not re-reviewed in this pass. |
| H24 | Spectral collapse pilot is ready as a claim-bearing result | UNKNOWN/REBUILD | branch name; modified `results/spectral_sprint_log.md`; untracked spectral reports | Not enough lineage inspected. Keep as pilot until gates and artifacts are mapped. |

## Living Hypotheses

| Hypothesis | Why still alive |
|---|---|
| H03 HBB pearl candidate set | Multiple computational and auxiliary artifacts exist; no experimental proof, but hypothesis generation is defensible. |
| H08 TP53 within-category island | Validation suite artifact supports a surviving within-category signal; needs stronger baseline/external checks. |
| H13 tissue-specificity gradient | Supported as applicability statement, not causal proof. |
| H14 SCN5A cardiac comparison | Interesting but needs threshold recalibration. |
| H22 falsification infrastructure | Strongest project-level contribution. |

## Closed or Blocked Hypotheses

| Hypothesis | Reason |
|---|---|
| General pathogenicity predictor | Refuted by project canon and falsification artifacts. |
| HBB AUC as independent physics proof | Category ablation undercuts this. |
| MPRA positive validation | Current promoted matrix says MPRA is null. |
| gnomAD absence as universal constraint | Explicitly forbidden by governance. |
| Fitted FRAP parameters | Deprecated unless fitting code/data exists. |
| BCL11A as second public-canonical Class B locus | Current docs explicitly block this promotion. |

## Highest Self-Deception Risks

1. Treating computationally selected classes as independently validated biology.
2. Treating high AUC as mechanistic insight despite category leakage.
3. Treating auxiliary AlphaGenome support as external wet-lab validation.
4. Treating not-found/not-observed as universal biological constraint.
5. Letting technical/legacy artifacts leak into public canon.

