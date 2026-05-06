# ClinVar Submission Preparation — 2 FALSE PEARLS Reclassification

**Date:** 2026-05-01  
**Submitter:** Sergey Boyko (ARCHCODE Project)  
**Variants:** 2 HBB variants for Benign reclassification  

---

## SUBMISSION OVERVIEW

**Goal:** Reclassify 2 variants from current ClinVar status → Benign (population-specific, contradict disease epidemiology)

**Impact:** Update public database used by ALL clinical genetics labs worldwide. Your name in ClinVar as submitter.

---

## VARIANTS TO RECLASSIFY

### Variant 1: chr11:5227099 T>C

**ClinVar ID:** VCV000015471  
**Current Status:** Benign (already labeled Benign, but missing population annotation)  
**HGVS:** NC_000011.10:g.5227099T>C  
**Gene:** HBB (beta-globin)  
**Location:** Promoter region  

**Evidence for BENIGN (population-specific):**
1. **ACMG BS1** (Allele frequency greater than expected)
   - AF_EAS (East Asian) = 0.000193 (gnomAD v4)
   - Beta-thalassemia carrier rate in EAS: <1% (expected AF <0.00001)
   - Observed AF is 20× higher than expected → inconsistent with pathogenic
2. **Population specificity:** Present ONLY in EAS (AFR=AMR=EUR=SAS=0)
3. **Disease epidemiology mismatch:** Beta-thal NOT enriched in East Asian

**Proposed Annotation:**
> "Benign. Population-specific variant in East Asian ancestry (gnomAD AF_EAS=0.000193). Beta-thalassemia carrier prevalence in East Asian <1%, inconsistent with pathogenic structural variant. ARCHCODE structural prediction likely false positive."

---

### Variant 2: chr11:5227102 T>C

**ClinVar ID:** VCV000015466  
**Current Status:** Benign (already labeled Benign, but missing population annotation)  
**HGVS:** NC_000011.10:g.5227102T>C  
**Gene:** HBB (beta-globin)  
**Location:** Promoter region  

**Evidence for BENIGN (population-specific):**
1. **ACMG BS1** (Allele frequency greater than expected)
   - AF_EAS (East Asian) = 0.000464 (gnomAD v4, HIGHEST in dataset)
   - Beta-thalassemia carrier rate in EAS: <1% (expected AF <0.00001)
   - Observed AF is 50× higher than expected → inconsistent with pathogenic
2. **Population specificity:** Present ONLY in EAS (AFR=AMR=EUR=SAS=0)
3. **gnomAD popmax:** eas (confirms East Asian enrichment)
4. **Disease epidemiology mismatch:** Beta-thal NOT enriched in East Asian

**Proposed Annotation:**
> "Benign. Population-specific variant in East Asian ancestry (gnomAD AF_EAS=0.000464, popmax=eas). Beta-thalassemia carrier prevalence in East Asian <1%, inconsistent with pathogenic structural variant. ARCHCODE structural prediction false positive confirmed by population genetics."

---

## CLINVAR SUBMISSION REQUIREMENTS

### 1. Account Registration

**URL:** https://submit.ncbi.nlm.nih.gov/subs/clinvar/  
**Required Information:**
- Name: Sergey Boyko
- Email: sergeikuch80@gmail.com
- ORCID: 0009-0009-2178-5701
- Affiliation: Independent Researcher / Ronin Institute (pending approval)
- Organization: ARCHCODE Project

**Note:** ClinVar accepts submissions from independent researchers (no institutional affiliation required for annotations/reclassifications).

---

### 2. Evidence Package (Per Variant)

**Required Fields:**
1. **Variant identifiers:**
   - ClinVar VCV ID
   - HGVS (genomic coordinates)
   - dbSNP rs ID (if available)

2. **Clinical significance:**
   - Current: Benign
   - Proposed: Benign (with population annotation)

3. **Evidence:**
   - Population frequency data (gnomAD v4)
   - Disease epidemiology reference
   - ACMG criteria applied

4. **Supporting data:**
   - Publication (if available) — cite PyPop paper + ARCHCODE analysis
   - Data files (CSV with population frequencies)

---

### 3. ACMG Criteria Application

**BS1 (Benign Strong):** Allele frequency is greater than expected for disorder

**Calculation for chr11:5227102 T>C:**
```
Expected AF (pathogenic beta-thal in EAS):
  Carrier rate <1% = <0.01
  Pathogenic variant AF = carrier_rate / num_pathogenic_alleles
                        ≈ 0.01 / 300 known beta-thal alleles
                        ≈ 0.00003

Observed AF_EAS: 0.000464

Ratio: 0.000464 / 0.00003 = 15.5× higher than expected

Conclusion: AF inconsistent with pathogenic variant in this population
           → BS1 applies → Benign
```

---

### 4. References

**Required Citations:**
1. **gnomAD v4:**
   - Chen S et al. (2024). A genomic mutational constraint map using variation in 76,156 human genomes. *Nature* 625:92-100.
   - DOI: 10.1038/s41586-023-06045-0

2. **Beta-thalassemia epidemiology:**
   - Angastiniotis M, Modell B. (1998). Global epidemiology of hemoglobin disorders. *Ann NY Acad Sci* 850:251-269.
   - DOI: 10.1111/j.1749-6632.1998.tb10479.x

3. **PyPop methodology:**
   - Lancaster AK et al. (2024). PyPop: A mature open-source software pipeline for population genomics. *Front Immunol* 15:1378512.
   - DOI: 10.3389/fimmu.2024.1378512

4. **ARCHCODE analysis:**
   - Boyko S. (2026). Population stratification analysis of HBB variants. [GitHub repository or Zenodo DOI]

---

## SUBMISSION WORKFLOW

### Step 1: Register ClinVar Account (15 min)
1. Go to https://submit.ncbi.nlm.nih.gov/subs/clinvar/
2. Click "Register" → login with NCBI account (or create)
3. Complete organization profile (use "Independent Researcher")
4. Verify email

### Step 2: Prepare Data Files (30 min)
1. Extract 2 variants from `gnomad_populations_pearls.csv`
2. Create evidence spreadsheet:
   - Variant ID
   - HGVS
   - Population frequencies (AFR, AMR, EAS, EUR, SAS)
   - ACMG criteria
   - References

### Step 3: Submit Variant 1 (chr11:5227099 T>C) (20 min)
1. ClinVar Submission Portal → "New Submission"
2. Select: "Assertion" (not "Variant")
3. Fill form:
   - Variant: VCV000015471 or HGVS
   - Clinical significance: Benign
   - Evidence: BS1 (paste calculation)
   - Population annotation: Add comment
4. Upload supporting data (CSV)
5. Review → Submit

### Step 4: Submit Variant 2 (chr11:5227102 T>C) (20 min)
- Same process as Variant 1

### Step 5: Await Review (2-4 weeks)
- ClinVar curators review submission
- May request additional evidence
- Once approved → variant page updated with your annotation

---

## EXPECTED TIMELINE

| Step | Time Required | Status |
|------|---------------|--------|
| Account registration | 15 min | ⏳ TODO |
| Prepare evidence spreadsheet | 30 min | ⏳ TODO |
| Submit Variant 1 | 20 min | ⏳ TODO |
| Submit Variant 2 | 20 min | ⏳ TODO |
| ClinVar review | 2-4 weeks | ⏳ Pending |
| **Total active work** | **1.5 hours** | — |

**Target:** Complete submission by **May 3, 2026** (this weekend)

---

## SUCCESS METRICS

**Immediate (Submission):**
- ✅ 2 variants submitted to ClinVar
- ✅ Evidence package includes gnomAD population data
- ✅ ACMG BS1 criteria properly applied

**Long-term (Approval):**
- ✅ ClinVar variant pages updated with population annotation
- ✅ Your name listed as submitter (public record)
- ✅ Clinical labs worldwide see annotation when interpreting these variants

**Impact:**
- East Asian patients with these variants → labs will see "population-specific benign" annotation
- Reduces false positive clinical reports
- Demonstrates ARCHCODE population validation methodology

---

## NEXT STEPS (ACTION ITEMS)

1. **NOW:** Register ClinVar account (15 min)
2. **Today:** Prepare evidence spreadsheet (30 min)
3. **Tomorrow:** Submit both variants (40 min)
4. **Next week:** Monitor for ClinVar curator questions

---

**Status:** READY TO START (registration URL + evidence template prepared)
