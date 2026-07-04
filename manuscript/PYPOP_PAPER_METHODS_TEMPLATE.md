# PyPop Paper — Methods Section Template

**Target:** 800 words  
**Frog Block:** May 2, 09:00-11:00  
**Status:** TEMPLATE (fill tomorrow)

---

## METHODS

### Study Design

We applied population stratification analysis to 12 HBB promoter region variants identified by ARCHCODE structural variant prediction pipeline. The analysis utilized the PyPop framework (Lancaster et al., 2024) adapted for rare pathogenic variants.

**Objective:** Validate structural predictions through cross-population allele frequency consistency and disease epidemiology concordance.

---

### Variant Selection

**Source:** ClinVar database (accessed March 2026)  
**Locus:** HBB gene (chr11:5,225,464-5,227,071, GRCh38)  
**Region:** Promoter region (73bp cluster, -200 to -127 bp from transcription start site)  
**Inclusion criteria:**
- ARCHCODE LSSIM < 0.93 (structural disruption threshold)
- VEP consequence: MODIFIER (sequence-based tools classify as low impact)
- ClinVar annotation: Pathogenic, Likely Pathogenic, or VUS

**Total variants:** 12 (11 promoter, 1 enhancer-proximal)

**[TODO: Add table with variant positions, refs, alts, ClinVar IDs]**

---

### Population Stratification Analysis

**Data source:** gnomAD v4 (Chen et al., 2024)  
- Total individuals: 807,162 (genome + exome)
- Populations analyzed: 5 major genetic ancestry groups
  - AFR (African/African American)
  - AMR (Latino/Admixed American)
  - EAS (East Asian)
  - EUR (Non-Finnish European)
  - SAS (South Asian)

**Query method:** gnomAD GraphQL API  
- Population-specific allele frequencies extracted for each variant
- Filtering allele frequency (FAF95) calculated per population
- Population with maximum allele frequency (popmax) identified

**[TODO: Describe retry logic, rate limiting (3s delay), error handling]**

---

### PyPop Meta-Analysis Framework

We adapted PyPop's cross-population meta-analysis approach (Lancaster et al., 2024) from common HLA polymorphisms (AF > 1%) to rare pathogenic variants (AF < 0.001).

**Key adaptation:**  
Instead of genotype-level Hardy-Weinberg equilibrium tests, we used **absence rate** as a proxy for purifying selection intensity.

**Cross-population consistency classification:**

| Evidence Level | Definition | Interpretation |
|----------------|------------|----------------|
| **STRONG** | Absent in ALL 5 populations | Universal structural constraint |
| **WEAK** | Present in 1-2 populations | Population-specific variant |
| **FALSE PEARL** | Population-specific + epidemiology mismatch | Likely benign polymorphism |

**[TODO: Add statistical framework — Fisher exact test for STRONG vs WEAK, permutation test for population specificity]**

---

### Epidemiology Concordance Check

For variants with population-specific presence, we cross-referenced allele frequencies with known disease prevalence:

**Beta-thalassemia epidemiology (Angastiniotis & Modell, 1998):**
- **High prevalence:** Mediterranean (Italy, Greece), South Asian (India, Pakistan) — carrier rate 3-20%
- **Low prevalence:** East Asian (China, Japan, Korea) — carrier rate < 1%
- **Expected pathogenic variant AF:** ~carrier_rate / number_of_known_pathogenic_alleles

**ACMG criteria applied:**
- **BS1 (Benign Strong):** Allele frequency greater than expected for disorder
  - If observed AF > 10× expected AF in low-prevalence population → FLAG as FALSE PEARL

**[TODO: Add specific BS1 calculation for chr11:5227102 T>C (AF_EAS = 0.000464 vs expected <0.00001)]**

---

### ARCHCODE Structural Prediction

**[Brief description of ARCHCODE method — 2-3 sentences, cite GitHub repo]**

- Mean-field loop extrusion simulator (Kramer kinetics)
- SSIM-based contact map comparison (wild-type vs mutant)
- Threshold: LSSIM < 0.93 = predicted structural disruption (pearl)

**[TODO: Reference ARCHCODE GitHub (commit a772df4) and Zenodo DOI v2.17]**

---

### VEP/CADD Comparison

For comparison with sequence-based tools:

**VEP v113 (Ensembl):**
- Consequence annotations (MODIFIER, MODERATE, HIGH)
- SpliceAI plugin (splice site prediction)

**CADD v1.7 (Phred-scaled):**
- Deleteriousness score (threshold: >20 = pathogenic)

**[TODO: Add results — all 12 variants classified as MODIFIER by VEP, CADD < 20]**

---

### Data Availability

**Code:** https://github.com/sergeeey/ARCHCODE (commit a772df4)  
**Results:** `results/gnomad_populations_pearls.csv` (12 variants × 20 columns)  
**Query script:** `scripts/query_gnomad_populations.py` (production-ready, includes retry logic)

**[TODO: Add Zenodo DOI when paper submitted]**

---

### Statistical Analysis

**Software:** Python 3.11 (pandas, numpy, scipy)  
**Tests:**
- Fisher exact test: STRONG vs WEAK evidence (2×2 contingency table)
- Permutation test: population-specificity significance (10,000 permutations)
- Bootstrap 95% CI: false positive rate (2/12 = 16.7%, CI: [4.7%, 42.8%])

**Significance threshold:** p < 0.05

**[TODO: Add actual p-values from analysis]**

---

## NOTES FOR TOMORROW'S WRITING SESSION

**Fill gaps:**
1. Variant table (12 rows: ClinVar_ID, Position, Ref, Alt, Category)
2. Retry logic description (exponential backoff, 3s delay rationale)
3. Statistical framework (Fisher exact, permutation test details)
4. BS1 calculation example (chr11:5227102 T>C)
5. ARCHCODE brief description (2-3 sentences max)
6. VEP/CADD comparison results
7. Actual p-values (from gnomad_populations_summary.json)

**References to cite:**
1. Lancaster et al. 2024 (PyPop) — Front Immunol 15:1378512
2. Chen et al. 2024 (gnomAD v4) — Nature 625:92-100
3. Angastiniotis & Modell 1998 (beta-thal epidemiology) — Ann NY Acad Sci 850:251-269
4. Richards et al. 2015 (ACMG criteria) — Genet Med 17:405-424

**Target word count:** 800 words (currently ~600 with TODOs)

**Time budget tomorrow:**
- 09:00-09:30: Fill variant table + statistical framework
- 09:30-10:15: Complete BS1 calculation + VEP comparison
- 10:15-11:00: Polish, references, final read

**Success criteria:** Methods section complete, no TODOs remaining, ready for Results section.
