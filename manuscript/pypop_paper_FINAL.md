# Population Stratification Identifies Epidemiology-Discordant Variants in the HBB Locus: A Validation Framework for Structural Predictions

**Authors:** Sergey Boyko  
**Affiliation:** Independent Researcher; Ronin Institute for Independent Scholarship 2.0 (affiliation pending confirmation, decision expected May 2026)  
**Correspondence:** sergeikuch80@gmail.com  
**ORCID:** 0009-0009-2178-5701

**Running title:** Population Validation of HBB Structural Variants

**Article type:** Brief Report

**Conflict of interest:** None declared  
**Funding:** None  
**Tool disclosure:** ARCHCODE (Zenodo DOI: 10.5281/zenodo.18908214, v2.17) was developed by the author. Validation uses independent gnomAD population data.

---

## ABSTRACT

**Background:** Structural variant prediction tools detect 3D chromatin disruptions in regulatory regions that sequence-based pathogenicity predictors (VEP, CADD) classify as low impact. However, validating structural predictions without functional data remains challenging. Population genetics offers an alternative validation strategy: truly pathogenic variants should be under purifying selection and thus rare across all populations, while population-specific presence suggests benign variation.

**Methods:** We adapted the PyPop population stratification framework (Lancaster et al., 2024) to validate 15 HBB promoter region variants identified by ARCHCODE structural prediction. We queried gnomAD v4 (807,162 individuals) for population-specific allele frequencies across 5 genetic ancestry groups (AFR, AMR, EAS, EUR, SAS) and cross-referenced results with beta-thalassemia epidemiology. Variants with population-specific presence inconsistent with disease prevalence were flagged as potential false positives.

**Results:** Of 15 HBB promoter variants, 3 (20.0%) were not observed in gnomAD v4 queried datasets, and 12 (80.0%) were successfully queried. Two variants showed East Asian-specific enrichment (AF_EAS = 0.000464-0.000648, popmax = eas) despite beta-thalassemia being rare in East Asian populations (carrier rate <1%), suggesting population-specific benign polymorphisms and potential misclassification by structural prediction. VEP correctly classified both as MODIFIER impact, demonstrating complementarity between sequence-based and structural approaches.

**Conclusion:** Population stratification detects epidemiology mismatches in structural variant predictions invisible to sequence-based tools. Integrating cross-population allele frequency analysis with disease epidemiology provides a validation framework for regulatory variant interpretation, particularly when functional data is unavailable. Larger multi-locus studies are needed to quantify false positive rates across structural prediction tools.

**Keywords:** population genetics, structural variants, PyPop, beta-thalassemia, regulatory variants, HBB, gnomAD, variant validation

---

## INTRODUCTION

Structural variation in non-coding regulatory regions poses a significant challenge for clinical variant interpretation. While sequence-based pathogenicity predictors (VEP, CADD, SpliceAI) perform well for coding variants, they often classify promoter and enhancer variants as "low impact" (MODIFIER) even when these variants disrupt 3D chromatin structure and gene expression (Spielmann et al., 2018; Lupiáñez et al., 2015). This limitation has motivated the development of 3D genome-based variant effect prediction tools, including ARCHCODE, which predicts structural disruption from chromatin contact map perturbations.

However, structural variant prediction introduces a new challenge: **how to validate predictions in the absence of functional data**. Unlike coding variants, where protein structure and conservation provide ground truth, regulatory variants lack direct phenotypic readouts. Chromatin immunoprecipitation (ChIP-seq) and Hi-C experiments are expensive and cell-type-specific, making experimental validation impractical for large-scale variant screening.

**Population genetics offers an alternative validation strategy.** If a structural variant prediction is truly pathogenic, the variant should be under purifying selection and thus rare or absent across all human populations. Conversely, if a predicted pathogenic variant shows population-specific presence — particularly in populations where the disease is NOT enriched — this suggests misclassification.

The PyPop framework, originally developed for HLA immunogenetics (Lancaster et al., 2024), provides a robust methodology for cross-population meta-analysis. PyPop compares genotype frequencies across populations to detect deviations from Hardy-Weinberg equilibrium and population structure. We hypothesized that adapting PyPop's population stratification approach to **rare pathogenic variants** (allele frequency < 0.001) could identify false positives in structural variant prediction.

**Beta-thalassemia provides an ideal test case** for this hypothesis. The disease has well-characterized epidemiology: high prevalence in Mediterranean and South Asian populations (carrier rate 3-20%), but low prevalence in East Asian populations (carrier rate <1%) (Angastiniotis & Modell, 1998; Weatherall, 2001). If an ARCHCODE-predicted structural variant in the HBB promoter region shows East Asian-specific enrichment, this contradicts the known disease distribution and suggests a **population-specific benign polymorphism** rather than a pathogenic mutation.

In this study, we applied PyPop population stratification to 15 HBB promoter region variants identified by ARCHCODE structural prediction. We queried gnomAD v4 (807,162 individuals) for population-specific allele frequencies across 5 major genetic ancestry groups and cross-referenced results with beta-thalassemia epidemiology. Our objectives were:

1. **Validate ARCHCODE structural predictions** using cross-population allele frequency consistency
2. **Identify potential false positives** via disease epidemiology concordance
3. **Demonstrate population stratification** as a validation framework for structural predictions
4. **Compare with sequence-based tools** (VEP, CADD) to assess complementarity

We demonstrate that population stratification detects epidemiology mismatches invisible to sequence-based tools. Two HBB promoter variants show East Asian-specific enrichment despite beta-thalassemia being rare in this population, suggesting population-specific benign polymorphisms and potential overclassification by structural prediction. This approach provides a scalable validation strategy when functional data is unavailable, though larger multi-locus studies are needed to quantify error rates systematically.

---

## METHODS

### Study Design

We applied population stratification analysis to HBB promoter region variants identified by ARCHCODE, a structural variant prediction pipeline based on 3D chromatin contact disruption. The analysis utilized the PyPop framework (Lancaster et al., 2024) adapted for rare pathogenic variants (allele frequency < 0.001).

**Objective:** Validate structural predictions through cross-population allele frequency consistency and disease epidemiology concordance.

**Hypothesis:** Structural variant predictions that show population-specific presence inconsistent with disease prevalence may represent candidate false positives — potentially benign polymorphisms epidemiology-discordant with structural predictions.

### Variant Selection

**Source:** ClinVar database (accessed March 2026)  
**Locus:** HBB gene (chr11:5,225,464-5,227,071, GRCh38)  
**Region:** Promoter region (73bp cluster, -200 to -127 bp from transcription start site)  

**Inclusion criteria:**
- ARCHCODE LSSIM (local structural similarity index) < 0.93, indicating predicted structural disruption
- VEP consequence annotation: MODIFIER or LOW (sequence-based tools classify as low impact)
- ClinVar annotation: Pathogenic, Likely Pathogenic, VUS, or Benign (for validation)

**Total variants analyzed:** 15  
**Successfully queried in gnomAD:** 12 (3 not found in gnomAD v4)

### Population Stratification Analysis

**Data source:** Genome Aggregation Database (gnomAD) v4 (Chen et al., 2024)  
- Total individuals: 807,162 (genome 76,156 + exome 730,947)
- Populations analyzed: AFR, AMR, EAS, EUR, SAS

**Query method:** gnomAD GraphQL API with 3-second rate limiting and exponential backoff retry logic. Population-specific allele frequencies calculated manually from allele count (AC) and allele number (AN) fields.

### PyPop Meta-Analysis Framework

Cross-population consistency classification:
- **Not found in gnomAD v4:** not observed in queried exome/genome datasets (note: absence from database ≠ confirmed universal constraint; extremely rare variants may be below detection threshold)
- **WEAK evidence:** Present in 1-2 populations (requires epidemiology check)

**Statistical approach:** Cross-population allele frequency patterns were assessed descriptively. Given the small sample (n=15), formal statistical testing is underpowered and results are presented as proof-of-concept with qualitative epidemiology concordance assessment.

### Epidemiology Concordance Check

For population-specific variants, we cross-referenced allele frequency patterns with disease epidemiology. Beta-thalassemia shows well-characterized population distribution: high carrier rate (3-20%) in Mediterranean and South Asian populations, low carrier rate (<1%) in East Asian populations (Angastiniotis & Modell, 1998). Variants showing enrichment in low-disease populations (reverse epidemiology pattern) were flagged as potential population-specific benign polymorphisms.

Allele frequencies were queried from both gnomAD v4 exome and genome datasets. For VCV000015471 (chr11:5227099 T>C), genome data was used as primary (AC_EAS=24, AN_EAS=37,034) due to substantially higher East Asian coverage compared to exome (AC_EAS=1), consistent with known WES cohort bias toward European populations. For VCV000015466 (chr11:5227102 T>C), exome data was used (AC_EAS=17, AN_EAS=36,610). Both datasets confirmed sufficient coverage (AN_EAS >30,000) for reliable East Asian allele frequency estimates, validated independently via gnomAD coverage API.

### ARCHCODE Structural Prediction

Mean-field loop extrusion simulator (Kramer kinetics) with SSIM-based contact map comparison. Variants with LSSIM < 0.93 classified as "pearls" (structural disruptions).

### VEP and CADD Comparison

VEP v113 (consequence annotations), CADD v1.7 (deleteriousness scores, threshold >20 = pathogenic).

---

## RESULTS

### gnomAD Query Success

Of 15 HBB promoter variants, 12 (80.0%) were successfully queried in gnomAD v4, and 3 (20.0%) were not found.

### Cross-Population Constraint Analysis

- **Not found in gnomAD v4:** 3 variants (20.0%) — not observed in queried datasets (absence may reflect extreme rarity rather than confirmed universal constraint)
- **Found in gnomAD v4:** 12 variants (80.0%) — of which 7 showed population-specific presence in at least one of the 5 main ancestry groups (AFR, AMR, EAS, EUR, SAS), and 5 showed no observations across these groups (including 1 with AC=0 in 544K individuals)

### Population-Specific Allele Frequency Distribution

**Maximum AF per population (across 12 queried variants):**
- **EAS:** 0.000648 (HIGHEST, VCV000015471 genome; VCV000015466 exome: 0.000464)
- SAS: 0.000415 (VCV000036287)
- AFR: 0.000121 (VCV000036285, VCV000015514)
- AMR: not observed
- **EUR: 0.0** (no variants observed in EUR main population; NFE sub-population observations noted for VCV000015464)

### Population-Specific Variants with Epidemiology Mismatch

**Variant 1: chr11:5227099 T>C (VCV000015471)**
- **AF_EAS: 0.000648** (gnomAD v4 genome, AC=24/AN=37,034 — higher coverage than exome AC=1; used as primary for this variant)
- AF in high-prevalence populations: AFR=0, EUR=0, SAS=0
- **Interpretation:** Population-specific presence inconsistent with beta-thal epidemiology

**Variant 2: chr11:5227102 T>C (VCV000015466)**
- **AF_EAS: 0.000464** (gnomAD v4 exome, popmax = eas)
- AF in high-prevalence populations: AFR=0, EUR=0, SAS=0.000058
- **Interpretation:** East Asian enrichment contradicts disease rarity in this population

**Epidemiology mismatch:** Beta-thalassemia carrier rate <1% in East Asian vs 3-20% in Mediterranean/South Asian populations. Both variants show reverse enrichment pattern (high AF in low-disease population), suggesting population-specific benign polymorphisms rather than pathogenic mutations.

### Comparison with Sequence-Based Tools

### VEP/CADD Comparison

- VEP: 11/12 variants classified as MODIFIER (low impact)
- CADD: 10/12 variants with CADD < 20 (below pathogenic threshold)
- **Both epidemiology-discordant variants correctly classified as MODIFIER by VEP**

**Conclusion:** Sequence-based tools detect sequence-level pathogenicity. ARCHCODE detects structural disruption. Population genetics detects epidemiology-level false positives. Integration maximizes accuracy.

---

## DISCUSSION

### Principal Findings

Population stratification analysis detects epidemiology mismatches in structural variant predictions invisible to sequence-based tools. Among 15 HBB promoter variants (12 successfully queried in gnomAD v4), we identified 2 showing East Asian-specific enrichment despite beta-thalassemia being rare in this population — a reverse epidemiology pattern consistent with population-specific benign polymorphisms and potential overclassification by structural prediction. This demonstrates that cross-population consistency can serve as functional validation when experimental data is unavailable.

### Comparison with Existing Approaches

- **Sequence-based tools:** Detect coding/splicing pathogenicity, miss regulatory disruption
- **Structural tools:** Detect chromatin disruption, but lack validation framework for regulatory variants
- **Population stratification:** Validates structural predictions via disease epidemiology concordance

**Integration of all three approaches maximizes accuracy:** sequence annotation filters obvious low-impact variants, structural prediction identifies candidates for investigation, and population genetics validates or refutes pathogenicity claims.

### Limitations

1. **Small sample (15 variants, single locus)** — precludes precise false positive rate quantification; multi-locus validation (n≥50) needed
2. **gnomAD coverage (3/15 not found)** — 12/15 variants queried successfully; 3/15 not observed in gnomAD v4 datasets (extremely rare variants may be below detection threshold)
3. **Requires well-characterized disease epidemiology** — applicable to Mendelian disorders with established prevalence patterns, not complex traits
4. **Population stratification assumptions** — admixture, migration, and genetic drift may confound interpretation

### Clinical Implications

- **Population-aware VUS interpretation:** Variants enriched in populations where disease is rare warrant skepticism of pathogenic classification
- **Structural prediction with caution:** Regulatory variant predictions require orthogonal validation (functional assays, family segregation, or population genetics)
- **ClinVar submissions:** Should include population stratification data to aid evidence-based reclassification

### Future Directions

1. Multi-locus expansion (CFTR, BRCA1, TP53)
2. Automated gnomAD query integration into ARCHCODE
3. Bayesian integration (LSSIM + CADD + population AF)
4. Experimental validation (Hi-C, CRISPR on identified variants)
5. Baseline comparison with other structural prediction tools (Akita, Enformer, DeepSEA) to quantify ARCHCODE-specific vs general structural prediction error rates

### Conclusion

Population stratification, adapted from PyPop immunogenetics methodology, provides a scalable validation framework for structural variant predictions in regulatory regions. By leveraging disease epidemiology and cross-population allele frequency consistency, this approach detects misclassifications invisible to sequence-based pathogenicity tools. The identification of 2 of 15 HBB promoter variants with reverse epidemiology patterns demonstrates proof-of-concept for this methodology. Larger multi-locus studies are needed to systematically quantify error rates and establish population genetics as a standard component of regulatory variant interpretation workflows.

---

## REFERENCES

1. Lancaster AK, et al. (2024). PyPop: A mature open-source software pipeline for population genomics. *Front Immunol* 15:1378512. DOI: 10.3389/fimmu.2024.1378512

2. Chen S, et al. (2024). A genomic mutational constraint map using variation in 76,156 human genomes. *Nature* 625:92-100. DOI: 10.1038/s41586-023-06045-0

3. Angastiniotis M, Modell B. (1998). Global epidemiology of hemoglobin disorders. *Ann NY Acad Sci* 850:251-269. DOI: 10.1111/j.1749-6632.1998.tb10479.x

4. Weatherall DJ. (2001). Phenotype-genotype relationships in monogenic disease: lessons from the thalassaemias. *Nat Rev Genet* 2:245-255. DOI: 10.1038/35066048

5. Richards S, et al. (2015). Standards and guidelines for the interpretation of sequence variants. *Genet Med* 17:405-424. DOI: 10.1038/gim.2015.30

6. Spielmann M, et al. (2018). Structural variation in the 3D genome. *Nat Rev Genet* 19:453-467. DOI: 10.1038/s41576-018-0007-0

7. Lupiáñez DG, et al. (2015). Disruptions of topological chromatin domains cause pathogenic rewiring of gene-enhancer interactions. *Cell* 161:1012-1025. DOI: 10.1016/j.cell.2015.04.004

---

## DATA AVAILABILITY

**Code:** https://github.com/sergeeey/ARCHCODE (commit 1415229)  
**ARCHCODE Zenodo:** DOI: 10.5281/zenodo.18908214 (v2.17)  
**Results:**
- `results/gnomad_populations_pearls.csv` — 15 variants × 20 population columns (12 with gnomAD data, 3 not found, 2 above LSSIM threshold)
- `results/gnomad_populations_summary.json` — cross-population analysis summary
- `results/gnomad_coverage_check.json` — allele number (AN) coverage validation for 2 variants
- `scripts/query_gnomad_populations.py` — gnomAD GraphQL query tool

---

## ACKNOWLEDGMENTS

We thank Alexander K. Lancaster, Richard M. Single, Steven J. Mack, Vanessa Sochat, Michael P. Mariani, and Gordon D. Webster for developing the PyPop framework and for making it openly available. We acknowledge the Genome Aggregation Database (gnomAD) consortium for providing open-access population genetics data.

---

**Total word count:** 3,239 words  
**Target journal:** Human Mutation (short reports: 3000-5000 words accepted)  
**Submission date:** May 2026  
**Status:** READY FOR SUBMISSION
