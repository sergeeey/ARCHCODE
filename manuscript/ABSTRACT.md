# ARCHCODE: 3D Chromatin Loop Extrusion Simulation Reveals Structural Pathogenicity Invisible to Sequence-Based Predictors in β-Globin Variants

**Sergey V. Boyko**

---

## Abstract

**Background:** Sequence-based predictors capture coding and canonical splice effects, but are
not designed to explicitly model 3D chromatin topology. ARCHCODE is a physics-informed
loop-extrusion simulation framework intended as an orthogonal, hypothesis-generating layer for
structural variant interpretation.

**Methods:** We analyzed ClinVar HBB variants with ARCHCODE structural metrics and compared outputs
with sequence-based predictors under a strict validation protocol (`VALIDATION_PROTOCOL.md`).
Claims were constrained by canonical governance artifacts and explicit evidence tiers
(`SUPPORTED`, `EXPLORATORY`, `UNVERIFIED`).

**Results:** Current validated outputs support three bounded findings: (1) reproducible
model-discordance observations between structural and sequence-based signals (Task 2, supported at
observation level), (2) weak-CTCF isolated behavior supported in-model only (Task 3,
`SUPPORTED_IN_MODEL`), and (3) tissue-context input-feature alignment support in Task 4
(`SUPPORTED_WITH_LIMITS`). For Task 5, computational VUS stratification signal is reproducible but
clinical reclassification remains `UNVERIFIED` (HBB strict report: `NO_GO`). For Task 1, the
current 1Mb benchmark setup does not support the strong Pearson-correlation target and remains
`EXPLORATORY`.

**Conclusions:** ARCHCODE currently supports constrained, non-clinical use: reproducible
computational stratification and prioritization for follow-up experiments. It does not yet support
publication-grade causal certainty or clinical reclassification claims without orthogonal
experimental validation.

**Limitations:**

- Hi-C validation showed weak, non-significant correlation (r = 0.16)
- Analytical mean-field model; not full stochastic simulation
- Kramer kinetics parameters (α, γ) are manually calibrated, not fitted to experimental data
- VEP used instead of SpliceAI (API unreachable during study period)
- Pearl variants require experimental validation before clinical use
- No experimental RNA or protein data confirming predicted effects

**Keywords:** β-thalassemia, HBB, chromatin loops, loop extrusion, cohesin, SSIM, structural
pathogenicity predictor, VEP, regulatory variants, promoter variants, pearl variants,
variant interpretation, mean-field simulation

**Word Count:** ~480 words

---

## Significance Statement

ARCHCODE provides a reproducible computational framework for structural, physics-informed
variant prioritization that complements sequence-based tools. Under strict claim governance, the
supported scope is model-discordance analysis, in-model barrier behavior checks, and
tissue-context alignment diagnostics. Causal and clinical claims remain explicitly blocked until
orthogonal experimental validation.

**Word Count:** ~110 words

---

## Main Findings (for graphical abstract)

1. **Claim governance is canonicalized** across Task1–Task5 with explicit allowed/blocked conclusions.
2. **Task2 supports model-discordance observation**, but pathogenic-class causality remains `UNVERIFIED`.
3. **Task3 weak-CTCF result is `SUPPORTED_IN_MODEL`**, not externally validated biology.
4. **Task4 supports tissue-context input alignment** with causal/clinical extrapolation blocked.
5. **Task5 supports computational stratification only**; clinical reclassification remains `UNVERIFIED` (`NO_GO`).

---

## Data Transparency Declaration

| Data source                  | Status                | Notes                                      |
| ---------------------------- | --------------------- | ------------------------------------------ |
| ClinVar HBB variants (n=353) | REAL                  | NCBI E-utilities API, April 2026           |
| Ensembl VEP v113 SIFT scores | REAL                  | Standard Ensembl REST API                  |
| ARCHCODE SSIM scores         | COMPUTATIONAL         | Analytical simulation; not experimental    |
| Hi-C/benchmark status        | MIXED / CONTEXT-BOUND | Task1 remains exploratory in current setup |
| SpliceAI predictions         | NOT AVAILABLE         | API unreachable; replaced by VEP           |
| AlphaGenome predictions      | NOT USED              | Synthetic mock data; excluded entirely     |
| Kramer parameters (α, γ)     | MANUALLY CALIBRATED   | Literature ranges; not fitted to data      |

---

_Manuscript prepared for bioRxiv preprint submission_
_Date: 2026-03-06_
_Correspondence: sergeikuch80@gmail.com_
