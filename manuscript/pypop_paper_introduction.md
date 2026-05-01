# Population Stratification Detects Misclassified Pathogenic Variants in HBB Locus

## INTRODUCTION

Structural variation in non-coding regulatory regions poses a significant challenge for clinical variant interpretation. While sequence-based pathogenicity predictors (VEP, CADD, SpliceAI) perform well for coding variants, they often classify promoter and enhancer variants as "low impact" (MODIFIER) even when these variants disrupt 3D chromatin structure and gene expression (Spielmann et al., 2018; Lupiáñez et al., 2015). This limitation has motivated the development of 3D genome-based variant effect prediction tools, including ARCHCODE, which predicts structural disruption from chromatin contact map perturbations.

However, structural variant prediction introduces a new challenge: **how to validate predictions in the absence of functional data**. Unlike coding variants, where protein structure and conservation provide ground truth, regulatory variants lack direct phenotypic readouts. Chromatin immunoprecipitation (ChIP-seq) and Hi-C experiments are expensive and cell-type-specific, making experimental validation impractical for large-scale variant screening.

**Population genetics offers an alternative validation strategy.** If a structural variant prediction is truly pathogenic, the variant should be under purifying selection and thus rare or absent across all human populations. Conversely, if a predicted pathogenic variant shows population-specific presence — particularly in populations where the disease is NOT enriched — this suggests misclassification.

The PyPop framework, originally developed for HLA immunogenetics (Lancaster et al., 2024), provides a robust methodology for cross-population meta-analysis. PyPop compares genotype frequencies across populations to detect deviations from Hardy-Weinberg equilibrium and population structure. We hypothesized that adapting PyPop's population stratification approach to **rare pathogenic variants** (allele frequency < 0.001) could identify false positives in structural variant prediction.

**Beta-thalassemia provides an ideal test case** for this hypothesis. The disease has well-characterized epidemiology: high prevalence in Mediterranean and South Asian populations (carrier rate 3-20%), but low prevalence in East Asian populations (carrier rate <1%) (Angastiniotis & Modell, 1998; Weatherall, 2001). If an ARCHCODE-predicted structural variant in the HBB promoter region shows East Asian-specific enrichment, this contradicts the known disease distribution and suggests a **population-specific benign polymorphism** rather than a pathogenic mutation.

In this study, we applied PyPop population stratification to 12 HBB promoter region variants identified by ARCHCODE structural prediction. We queried gnomAD v4 (807,162 individuals) for population-specific allele frequencies across 5 major genetic ancestry groups and cross-referenced results with beta-thalassemia epidemiology. Our objectives were:

1. **Validate ARCHCODE structural predictions** using cross-population allele frequency consistency
2. **Identify false positives** via disease epidemiology concordance (ACMG BS1 criteria)
3. **Estimate false positive rate** for structural variant prediction in regulatory regions
4. **Compare with sequence-based tools** (VEP, CADD) to assess complementarity

We demonstrate that **16.7% (2/12) of ARCHCODE HBB promoter predictions are false positives** — East Asian-specific benign polymorphisms that sequence-based tools correctly classify as low impact but structural tools misclassify as pathogenic. This false positive rate is invisible without population stratification analysis, highlighting the necessity of integrating population genetics into structural variant interpretation workflows.

---

**Word count:** 467 words  
**Status:** COMPLETE
