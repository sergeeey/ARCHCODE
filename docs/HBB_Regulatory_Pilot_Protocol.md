# HBB Regulatory Variant Evidence Audit — Pilot Protocol

**Date:** 2026-05-10  
**Status:** READY FOR EXECUTION  
**Timeline:** 2 weeks  
**Kill criterion:** <10% novel conflicts → pivot

---

## Objective

Test falsification hypothesis:
> **H-AUDIT:** AI/annotation-based pathogenicity claims for regulatory variants become substantially less reliable after ancestry-aware population-frequency filtering and category-matched functional controls.

---

## Pilot Cohort

**File:** `docs/HBB_Regulatory_Pilot_50_Enhanced.csv`

**Composition:**
- **Total variants:** 50
- **Categories:**
  - Promoter: 15 (30%)
  - Splice donor: 22 (44%)
  - Splice acceptor: 3 (6%)
  - Splice region: 9 (18%)
  - 5'UTR: 1 (2%)
- **All labeled:** Pathogenic/Likely Pathogenic в ClinVar
- **Pearl variants:** 16/50 (32%)
- **Mean ARCHCODE LSSIM:** 0.9257 (range: 0.9004–0.9806)

---

## Data Collection (5 Evidence Layers)

### Layer 1: ClinVar Clinical Label ✅
**Status:** Already collected  
**Source:** HBB_Unified_Atlas.csv  
**Fields:**
- ClinVar_ID
- ClinVar_Significance
- Label (Pathogenic/Benign)

### Layer 2: Population Allele Frequency ⏳
**Status:** TO DO  
**Source:** gnomAD v4.1  
**API:** https://gnomad.broadinstitute.org/api  
**Fields required:**
- gnomAD_AF_Global (all populations)
- gnomAD_AF_AFR (African/African American)
- gnomAD_AF_EUR (European non-Finnish)
- gnomAD_AF_EAS (East Asian)
- gnomAD_AF_SAS (South Asian)
- gnomAD_Homozygote_Count

**Expected disease prevalence for beta-thalassemia:**
- Severe form: ~1:100,000 (carrier: ~1:200)
- Expected AF threshold: <0.005 (0.5%)

**Red flag threshold:** AF > 0.001 (0.1%) for claimed severe pathogenic variant

### Layer 3: Functional Category ✅
**Status:** Already collected  
**Source:** VEP annotation  
**Fields:**
- Category (promoter, splice_donor, etc.)
- VEP_Consequence
- VEP_Score

### Layer 4: Regulatory Evidence ⏳
**Status:** PARTIAL (need to query AlphaGenome API)  
**Source:** AlphaGenome `predict_variant` endpoint  
**Fields required:**
- CAGE_ref (reference CAGE-seq signal)
- CAGE_alt (alternate allele CAGE-seq signal)
- CAGE_delta (alt - ref)
- CAGE_effect_size (fold change)

**Interpretation:**
- Strong disruption: |CAGE_delta| > 0.15 OR fold-change > 2×
- Moderate: 0.05 < |CAGE_delta| < 0.15
- Weak: |CAGE_delta| < 0.05

### Layer 5: 3D Chromatin Signal ✅
**Status:** Already collected  
**Source:** ARCHCODE simulation  
**Fields:**
- ARCHCODE_LSSIM (local structural similarity)
- Pearl (VEP-blind structural disruption)

---

## Evidence Conflict Detection

### Conflict Type 1: Population-Frequency Contradiction
**Criteria:**
```
IF variant.label == "Pathogenic" 
   AND variant.category in ["promoter", "5'UTR", "splice_region"]
   AND variant.gnomAD_AF > 0.001  # 0.1% = 100× expected for severe disease
   AND variant.homozygote_count > 0
THEN flag as "POP_FREQ_CONFLICT"
```

### Conflict Type 2: Weak Regulatory Signal
**Criteria:**
```
IF variant.label == "Pathogenic"
   AND variant.category in ["promoter", "5'UTR"]
   AND |variant.CAGE_delta| < 0.05
   AND variant.ARCHCODE_LSSIM > 0.95  # minimal 3D disruption
THEN flag as "WEAK_REGULATORY_SIGNAL"
```

### Conflict Type 3: Category Artifact
**Criteria:**
```
IF variant.category == "promoter"
   AND variant.CADD < 15
   AND variant.Pearl == False
   AND matched_benign_promoters have similar LSSIM
THEN flag as "CATEGORY_ARTIFACT"
```

### Conflict Type 4: Known ClinVar Dispute
**Criteria:**
```
IF variant has conflicting interpretations in ClinVar submitter data
   OR variant appears in ClinVar "conflicting interpretations" list
THEN flag as "KNOWN_CLINVAR_CONFLICT"
```

---

## Execution Steps

### Week 1: Data Collection

**Day 1-2: Population AF**
```python
# Query gnomAD for all 50 variants
for variant in pilot_cohort:
    chr, pos, ref, alt = parse_variant(variant)
    af_data = gnomad_api.query(chr, pos, ref, alt)
    variant.gnomAD_AF = af_data
```

**Day 3-4: AlphaGenome CAGE**
```python
# Query AlphaGenome for regulatory variants
for variant in pilot_cohort.filter(category=['promoter', '5_prime_UTR']):
    cage_data = alphagenome.predict_variant(
        chr=variant.chr,
        pos=variant.pos,
        ref=variant.ref,
        alt=variant.alt
    )
    variant.CAGE_effect = cage_data
```

**Day 5: ClinVar Review Check**
- Manually check each variant's ClinVar page
- Record: submitter conflicts, review status, literature citations
- Flag: already documented conflicts

### Week 2: Analysis

**Day 1-2: Conflict Scoring**
```python
for variant in pilot_cohort:
    conflicts = []
    
    # Check each conflict type
    if check_pop_freq_conflict(variant):
        conflicts.append("POP_FREQ_CONFLICT")
    
    if check_weak_regulatory(variant):
        conflicts.append("WEAK_REGULATORY_SIGNAL")
    
    if check_category_artifact(variant):
        conflicts.append("CATEGORY_ARTIFACT")
    
    if check_clinvar_dispute(variant):
        conflicts.append("KNOWN_CLINVAR_CONFLICT")
    
    variant.conflict_types = conflicts
    variant.conflict_score = len(conflicts)
```

**Day 3-4: Manual Review**
- For each flagged conflict:
  - Check literature (PubMed)
  - Check clinical databases (HGMD, ClinGen)
  - Check population genetics (founder effects, selection)
  - Classify: **NOVEL** vs **ALREADY_KNOWN** vs **FALSE_POSITIVE**

**Day 5: Report**
- Count: novel conflicts / total conflicts
- Precision: real issues / flagged conflicts
- Document: case studies (3-5 strongest)

---

## Success Criteria

| Metric | Target | Kill if |
|--------|--------|---------|
| **Novel conflicts** | ≥5 out of 50 (≥10%) | <5 (0 novel) |
| **Precision** | ≥40% flagged = real | <20% precision |
| **Clinical interest** | ≥1 lab says "we'd use this" | 0 interest |
| **OS4LS fit** | Audit tools = stated priority | Not in scope |

---

## Output Deliverables

### 1. Evidence Conflict Table
**File:** `HBB_Regulatory_Evidence_Conflicts.csv`

**Columns:**
- ClinVar_ID
- Category
- HGVS_c
- ClinVar_Label
- gnomAD_AF
- CAGE_Effect
- ARCHCODE_LSSIM
- Conflict_Type (comma-separated)
- Conflict_Score (0-4)
- Novel (TRUE/FALSE)
- Literature_Support (PMID if exists)
- Audit_Verdict (CONFIRMED | REFUTED | UNCERTAIN)

### 2. Case Studies (3-5 strongest)
**File:** `HBB_Regulatory_Case_Studies.md`

**Format for each:**
```markdown
## Case 1: [ClinVar_ID] — [Conflict Type]

**Variant:** chr11:pos ref>alt ([HGVS])
**ClinVar Label:** Pathogenic
**Category:** promoter

**Evidence Conflict:**
- gnomAD AF: 0.0023 (230× expected for severe disease)
- Homozygotes: 3 (if truly severe, should be 0)
- CAGE effect: Δ = -0.02 (minimal disruption)
- ARCHCODE LSSIM: 0.95 (normal structure)

**Literature Check:**
- PubMed: 0 results for this variant + beta-thalassemia
- HGMD: Listed as "DM" (disease-causing mutation) but no phenotype details
- ClinGen: No expert panel review

**Alternative Explanations:**
1. Carrier state (mild or asymptomatic)
2. Population-specific modifier genes
3. Classification error (older submission)

**Audit Verdict:** UNCERTAIN — requires clinical phenotype data

**Status:** NOVEL (not in ClinVar submitter conflicts)
```

### 3. Summary Report
**File:** `HBB_Regulatory_Pilot_Report.md`

**Sections:**
1. Executive Summary
2. Methods
3. Results
   - Conflict detection rates
   - Novel vs known conflicts
   - Precision/recall
4. Case Studies
5. Discussion
6. Next Steps / Kill Decision

---

## Decision Tree (After 2 Weeks)

```
IF novel_conflicts ≥ 5:
    → GO: Draft grant proposal + expand to 200 variants
    
ELIF novel_conflicts = 1-4:
    → PIVOT: Narrow scope to "HBB promoter sanity check" niche tool
    
ELIF novel_conflicts = 0:
    → FREEZE: Publish ARCHCODE null result, switch to PyPop Paper 2
    
IF precision < 20%:
    → ABANDON: Too many false positives, tool not usable
```

---

## Resources

**Data Sources:**
- ClinVar: https://www.ncbi.nlm.nih.gov/clinvar/
- gnomAD: https://gnomad.broadinstitute.org/
- AlphaGenome: https://alphagenome.com/ (or local predictions)
- ARCHCODE: `results/HBB_Unified_Atlas.csv`

**Tools:**
- Python pandas for data manipulation
- requests/aiohttp for API calls
- matplotlib for visualizations

**Timeline:**
- Start: Monday 2026-05-12
- Data collection complete: Friday 2026-05-16
- Analysis complete: Friday 2026-05-23
- GO/PIVOT/FREEZE decision: Monday 2026-05-26

---

## Contact

**Clinical Lab Outreach (parallel task):**

Email template:
```
Subject: Open-source variant evidence audit toolkit — feedback request

Dear [Lab Director / ClinGen VCEP Chair],

We are developing an open-source toolkit for automated variant 
evidence contradiction flagging (population AF vs pathogenicity claims).

Pilot: 50 HBB regulatory variants, multi-layer evidence audit.

Would your lab use automated population-frequency + functional-evidence 
conflict detection in your workflow?

Context: ACMG PM2/BS1 checks, but automated + reproducible.

2-minute feedback survey: [link]

Thank you,
[Signature]
```

**Target labs:**
1. ClinGen HBB/Hemoglobinopathy VCEP
2. GeneDx clinical lab
3. Invitae clinical lab

---

**Status:** READY TO EXECUTE  
**Next action:** Query gnomAD for 50 variants (Day 1)  
**Kill criterion checkpoint:** Day 14 (count novel conflicts)
