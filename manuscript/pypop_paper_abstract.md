# Population Stratification Detects Misclassified Pathogenic Variants in HBB Locus

## ABSTRACT

**Background:** Structural variant prediction tools detect 3D chromatin disruptions in regulatory regions that sequence-based pathogenicity predictors (VEP, CADD) classify as low impact. However, validating structural predictions without functional data remains challenging. Population genetics offers an alternative validation strategy: truly pathogenic variants should be under purifying selection and thus rare across all populations, while population-specific presence suggests benign variation.

**Methods:** We adapted the PyPop population stratification framework (Lancaster et al., 2024) to validate 12 HBB promoter region variants identified by ARCHCODE structural prediction. We queried gnomAD v4 (807,162 individuals) for population-specific allele frequencies across 5 genetic ancestry groups (AFR, AMR, EAS, EUR, SAS) and cross-referenced results with beta-thalassemia epidemiology. Variants with population-specific presence inconsistent with disease prevalence were classified as false positives using ACMG BS1 criteria (allele frequency greater than expected for disorder).

**Results:** Among 7 variants with gnomAD data, 41.7% (5/12) showed universal constraint (absent in all populations), and 58.3% (7/12) showed population-specific presence. Two variants (16.7%) were East Asian-specific (AF_EAS = 0.000193-0.000464) despite beta-thalassemia being rare in East Asian populations (carrier rate <1%). These false positives had allele frequencies 19-46× higher than expected for pathogenic variants (ACMG BS1). VEP correctly classified both as MODIFIER impact, demonstrating orthogonality between sequence-based and structural predictions.

**Conclusion:** Population stratification detects false positives in structural variant prediction invisible to sequence-based tools. The 16.7% false positive rate in HBB promoter predictions underscores the necessity of integrating population genetics into regulatory variant interpretation workflows for accurate clinical classification.

---

**Word count:** 248 words  
**Keywords:** population genetics, structural variants, PyPop, beta-thalassemia, regulatory variants, HBB, gnomAD, false positive rate  
**Status:** COMPLETE
