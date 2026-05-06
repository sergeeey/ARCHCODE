# G4-3 Hypothesis Roadmap — Cancer Vulnerability via G4-Clearance Deficit

**Priority:** P0 (Clinical Ready)  
**Score:** 9.0/10  
**Created:** 2026-04-26  
**Status:** Literature review complete, ready for computational validation

---

## Core Hypothesis

**Чувствительность опухоли к G4-лигандам определяется фазовым переходом:**

```python
Λ = G4-load / helicase-capacity

# При Λ > Λ_critical → replication catastrophe
```

---

## Key Evidence from Literature (2024-2026)

### 1. CX-5461 Clinical Data EXISTS ✅

**Source:** Phase I CCTG IND.231 trial (Nature Communications 2022)

**Key Facts:**
- **40 patients** enrolled (10 dose levels: 50-650 mg/m²)
- **Recommended Phase II dose:** 475 mg/m² days 1,8,15 every 4 weeks
- **Response rate:** 14% (primarily BRCA1/2, PALB2-deficient tumors)
- **Dose-limiting toxicity:** Phototoxicity
- **Resistance mechanism:** PALB2/BRCA2 reversion mutations on progression
- **FDA status:** Fast Track Designation

**Critical for hypothesis:**
- ✅ Patient cohort с measured responses exists
- ✅ BRCA1/2 status documented (DNA repair capacity proxy)
- ❌ G4-load НЕ был измерен в пациентах
- ❌ BLM/WRN/FANCJ expression НЕ был использован для stratification

**Retrospective analysis feasible:** YES (if patient samples available)

---

### 2. G4-Load Quantification Methods Ready ✅

**Available Technologies:**

| Method | Coverage | Resolution | Throughput | Status |
|--------|----------|------------|------------|--------|
| **G4-seq** | >700K sites | 100-500 bp | High | Established 2021 |
| **G4-ChIP-seq** | Genome-wide | ~200 bp | Medium | BG4 antibody ready |
| **ssG4-seq** | Strand-specific | ~100 bp | High | **NEW 2025** |
| **EndoQuad DB** | Validated sites | Exact loci | Database | Public access |

**Computational proxy (fast alternative):**
```python
# G4Hunter score (sequence-based)
# PQS prediction algorithms
# No wet-lab needed for initial Λ-index calculation
```

---

### 3. Helicase Expression = Stratification Biomarker ✅

**WRN Helicase:**
- **>90% MSI cancers WRN-dependent** (Cancer Discovery 2021, 2024)
- **TA-repeat expansions** validated as sensitivity indicator
- **WRN inhibitors** in development (synthetic lethal approach)
- **Patient stratification ready:** MSI status + WRN expression

**BLM Helicase:**
- **Overexpressed** in gliomas, multiple myeloma
- **High BLM = poor outcomes** in myeloma
- **Replication stress signature** enrichment
- **TP53 status** modulates response

**FANCJ Helicase:**
- **Interacts with BLM** (protein stability)
- **Role in G4-resolution** established
- Less clinical data than WRN/BLM

**Therapeutic Index Formula:**
```python
Λ = G4-load / (α·WRN + β·BLM + γ·FANCJ + δ·HR_capacity + ε·TOP)

# Where:
# α, β, γ = helicase weights (to be fitted)
# HR_capacity = BRCA1/2, PALB2, RAD51 status
# TOP = topoisomerase activity proxy
```

---

## Validation Roadmap

### Phase 1: Computational Validation (Week 1-2) 🚀

**Goal:** Prove Λ-index predicts CX-5461 response better than baseline

**Data Sources:**
- CX-5461 trial patient data (if accessible via publication supplements)
- TCGA/ICGC cancer genomics (for G4-load + helicase expression)
- DepMap (for WRN/BLM dependency scores)
- EndoQuad database (validated G4 sites)

**Baseline Models:**
```python
# Model 1: MYC expression only (G4-load proxy)
# Model 2: BRCA status only (HR capacity)
# Model 3: Dose only

# Hypothesis model:
# Λ-index = f(G4-load, WRN, BLM, FANCJ, HR, TOP)
```

**Metrics:**
- AUC(Λ-index) vs AUC(baseline)
- Stratification into sensitive/resistant cohorts
- Correlation Λ vs progression-free survival

**Kill Criteria:**
- AUC(Λ) ≤ AUC(MYC) — G4-load alone sufficient
- AUC(Λ) ≤ AUC(BRCA) — HR status alone sufficient
- No dose-response correlation with Λ

**Success Criteria:**
- AUC(Λ) > 0.75
- Λ_high patients show 2×+ response rate vs Λ_low
- Independent validation on 2+ cancer types

**Tools:**
- Python: pandas, scikit-learn, lifelines (survival)
- R: TCGAbiolinks (for TCGA data)
- G4Hunter (for sequence-based G4 prediction)

---

### Phase 2: Cross-Cancer Validation (Week 3-4)

**Goal:** Prove Λ-index generalizes beyond BRCA-deficient tumors

**Cancer Types to Test:**
1. **Colorectal (MSI-high)** — WRN dependency proven
2. **Gliomas** — BLM overexpression documented
3. **Multiple myeloma** — BLM therapeutic target
4. **Breast (BRCA-WT)** — test beyond original cohort
5. **Ovarian** — G4-stabilizers tested here

**Hypothesis:**
- MSI cancers: high Λ due to low WRN
- MYC-amplified: high Λ due to high G4-load
- BRCA-deficient: high Λ due to low HR capacity
- **Synergy:** highest Λ when multiple deficiencies combine

**Validation:**
- DepMap drug sensitivity screens (if CX-5461 or similar tested)
- Published case reports of G4-stabilizer responses
- Cell line panels with matched genomics

---

### Phase 3: Mechanism Validation (Month 2-3)

**Goal:** Prove Λ > Λ_crit creates replication catastrophe

**In Silico:**
```python
# Queueing model: M/M/k queue
# λ = G4 fork stalling rate
# μ = helicase clearance rate
# k = number of active helicases

# Predicted: waiting time ~ 1/(1 - λ/μk)
# At λ/μk → 1: catastrophic queue buildup
```

**Experimental (if resources available):**
- Isogenic cell lines: WRN+/+ vs WRN-/-
- Dose CX-5461, measure:
  - γH2AX foci (replication stress)
  - 53BP1 foci (DNA damage)
  - Cell cycle arrest
  - Survival (colony formation)

**Prediction:**
- WRN-/- cells show non-linear dose-response (phase transition)
- WRN+/+ cells show linear/saturating response

---

### Phase 4: Clinical Translation (Month 4-6)

**If Phase 1-2 SUCCESS:**

**Retrospective Analysis:**
- Contact CCTG IND.231 trial investigators
- Request: patient tumor samples, genomic data, response outcomes
- Calculate Λ-index retrospectively
- Publish: "Λ-index stratifies CX-5461 response in Phase I trial"

**Prospective Validation:**
- Partner with ongoing G4-stabilizer trials
- Add Λ-index as exploratory biomarker
- Real-time patient stratification

**Regulatory Path:**
- Companion diagnostic development (if validated)
- FDA submission for patient selection biomarker

---

## Data Availability Assessment

### ✅ Immediately Available (Public)

1. **TCGA/ICGC genomics:**
   - RNA-seq (WRN, BLM, FANCJ, MYC expression)
   - Copy number (gene amplifications)
   - Mutation status (BRCA1/2, PALB2, TP53)
   - MSI status

2. **DepMap:**
   - Gene dependency scores (CRISPR/RNAi)
   - Drug sensitivity (limited G4-stabilizers)
   - Cell line features

3. **EndoQuad database:**
   - 700K+ validated G4 sites
   - Genomic coordinates
   - Cell-type-specific data

4. **Literature:**
   - CX-5461 trial summary statistics (Nature Comm 2022)
   - WRN/MSI dependency (Cancer Discovery 2021, 2024)
   - BLM expression in cancers (multiple papers)

### ❓ Restricted Access (Need Collaboration)

1. **CX-5461 patient-level data:**
   - Individual responses
   - Genomic profiles
   - Tumor samples for G4-ChIP-seq

2. **Unpublished trial data:**
   - Other G4-stabilizer trials
   - Combination therapy results

3. **Proprietary cell line screens:**
   - Pharma company drug sensitivity data

---

## Resource Requirements

### Minimal (Computational Only) — Week 1-2

**Personnel:** 1 computational biologist
**Compute:** Standard laptop + cloud (AWS/GCP for TCGA download)
**Cost:** <$500 (compute time)
**Time:** 2-4 weeks

**Deliverable:** Proof-of-concept manuscript draft

### Full Validation — Month 1-3

**Personnel:**
- 1 computational biologist
- 1 bioinformatician (TCGA/DepMap wrangling)
- 1 statistician (survival analysis, clinical trial design)

**Compute:** Medium (multi-cancer datasets, parameter sweeps)
**Cost:** ~$2-5K (compute + data access fees)
**Time:** 2-3 months

**Deliverable:** Multi-cancer validation paper

### Experimental Validation — Month 3-6

**Personnel:** Add wet-lab collaborator
**Materials:** Cell lines, CX-5461, assays
**Cost:** ~$20-50K (typical academic lab budget)
**Time:** 3-6 months

**Deliverable:** Mechanism paper + clinical trial proposal

---

## Kill Criteria (Pre-Registered)

**KILL Phase 1 if:**
- AUC(Λ-index) ≤ 0.65 (no better than random + small effect)
- AUC(Λ) ≤ AUC(BRCA status alone)
- No correlation with dose-response (Λ irrelevant to mechanism)
- Effect disappears in cross-validation

**KILL Phase 2 if:**
- Λ-index fails in >2 independent cancer types
- MSI cancers don't show predicted WRN-driven high Λ
- MYC-amplified cancers don't show G4-load-driven high Λ

**KILL Phase 3 if:**
- Queueing model predicts linear, not threshold response
- Isogenic WRN+/- cells show same Λ sensitivity

**SUCCESS if:**
- AUC(Λ) > 0.75 across ≥3 cancer types
- Stratification into high/low Λ shows ≥2× response rate difference
- Mechanism validated in vitro
- Retrospective CX-5461 analysis confirms prediction

---

## Next Immediate Steps (This Week)

### Step 1: TCGA Data Download (Day 1) ✅ READY

```python
# Script: scripts/g4_tcga_download.py

import TCGAbiolinks

# Target cancers:
cancers = ['BRCA', 'COAD', 'GBM', 'OV', 'MM']

for cancer in cancers:
    # RNA-seq: WRN, BLM, FANCJ, MYC
    # Clinical: survival, response
    # Mutation: BRCA1/2, PALB2, TP53
    # MSI status
```

### Step 2: G4-Load Calculation (Day 2-3)

```python
# Use G4Hunter or PQS prediction
# Input: cancer genome sequences
# Output: G4-load score per sample

# Alternative: use EndoQuad validated sites
# Count G4 density in high-expression regions (MYC, rDNA)
```

### Step 3: Helicase Capacity Index (Day 4)

```python
# Helicase_capacity = 
#   α * WRN_expr + 
#   β * BLM_expr + 
#   γ * FANCJ_expr +
#   δ * HR_status  # BRCA1/2, PALB2, RAD51

# Fit α, β, γ, δ from DepMap dependency data
```

### Step 4: Baseline Model Comparison (Day 5-7)

```python
# Train models on DepMap or published sensitivity
# Test on held-out cancer types
# Plot ROC curves
# Report AUC + 95% CI
```

**Checkpoint:** If AUC(Λ) > 0.70 → proceed to Phase 2  
If AUC(Λ) < 0.65 → KILL or pivot to mechanism-only paper

---

## Publications Strategy

### Scenario A: Strong Validation (AUC > 0.75)

**Paper 1 (Month 2):** "Λ-index stratifies G4-stabilizer sensitivity across cancers"
- **Target:** Nature Communications, Cell Reports
- **Impact:** Patient stratification tool
- **Wet-lab required:** No (computational only)

**Paper 2 (Month 4):** "Retrospective validation in CX-5461 Phase I trial"
- **Target:** JAMA Oncology, JCO Precision Oncology
- **Impact:** Clinical biomarker
- **Requires:** Trial investigator collaboration

**Paper 3 (Month 6):** "Queueing theory model of G4-replication catastrophe"
- **Target:** PNAS, PLoS Computational Biology
- **Impact:** Mechanistic understanding
- **Wet-lab required:** Minimal (isogenic validation)

### Scenario B: Modest Validation (AUC 0.65-0.75)

**Paper 1:** "G4-load and helicase capacity partially predict drug sensitivity"
- **Target:** Scientific Reports, Cancers
- **Frame:** Contribution to multi-biomarker panel

### Scenario C: Negative Result (AUC < 0.65)

**Paper:** "Why G4-load alone is insufficient: the role of context"
- **Target:** eLife, PLoS ONE
- **Frame:** Falsification, lessons for biomarker development
- **Value:** Save others from pursuing dead end

---

## Integration with ATR Framework

**Connection to ATR-T3 (Catenation Percolation):**
- G4-structures create topological barriers
- Unresolved G4s increase catenation at replication forks
- Λ-index may correlate with catenation stress

**Connection to ATR-ALGORITHM:**
- G4-clearance as active process (like TOP2 annealing)
- Helicase = molecular motor resolving topological trap
- Phase transition when motor capacity exceeded

**New Layer Proposal:**
```
ATR LAYER 7: MOLECULAR STRESS THRESHOLDS
  ├─ G4-clearance overload (Λ-index)
  ├─ Topoisomerase saturation
  └─ Repair capacity thresholds
```

---

## Confidence Assessment

| Aspect | Confidence | Basis |
|--------|------------|-------|
| CX-5461 data exists | **HIGH (0.95)** | Published Phase I trial |
| G4-load measurable | **HIGH (0.90)** | G4-seq, G4-ChIP-seq established |
| Helicase expression measurable | **HIGH (0.95)** | TCGA RNA-seq available |
| Λ-index > baseline | **MEDIUM (0.70)** | Requires validation |
| Clinical translation feasible | **MEDIUM (0.65)** | Depends on retrospective access |
| Mechanism correct | **MEDIUM-HIGH (0.75)** | Queueing theory well-established |

**Overall Confidence in Hypothesis:** **0.76** (from EXTENDED_HYPOTHESES.md)

**Confidence in Feasibility:** **0.85** (data available, methods ready)

---

## Risk Assessment

### Technical Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| CX-5461 patient data inaccessible | Medium | Use DepMap as alternative |
| G4-load prediction inaccurate | Low | Multiple methods (G4Hunter, EndoQuad) |
| TCGA sample size insufficient | Low | >10K patients across cancer types |
| Λ-index overfits to BRCA | Medium | Test on MSI, MYC-amp, glioma |

### Strategic Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Scooped by pharma company | Low-Medium | Publish computational first |
| Negative result kills project | Medium | Pre-register, publish negative |
| No clinical partner interest | Medium | Strong computational proof → interest |

---

## Success Metrics (Pre-Defined)

**Minimal Success (publishable negative):**
- ✓ Completed analysis on ≥3 cancer types
- ✓ Rigorous baseline comparisons
- ✓ Documented kill criteria met

**Moderate Success (specialized journal):**
- ✓ AUC(Λ) = 0.65-0.75
- ✓ Works in ≥1 cancer type robustly
- ✓ Mechanism partially validated

**Strong Success (high-impact journal):**
- ✓ AUC(Λ) > 0.75
- ✓ Works across ≥3 cancer types
- ✓ Retrospective CX-5461 validation
- ✓ Mechanism confirmed in vitro

**Exceptional Success (clinical impact):**
- ✓ All "Strong Success" criteria
- ✓ Prospective trial collaboration
- ✓ Companion diagnostic development
- ✓ FDA biomarker qualification interest

---

## Timeline Summary

```
Week 1:    TCGA download + G4-load calculation
Week 2:    Baseline models + Λ-index fitting
Week 3-4:  Cross-cancer validation
Month 2:   Paper 1 draft (if AUC > 0.70)
Month 3:   Mechanism validation (queueing + in silico)
Month 4:   Retrospective CX-5461 analysis (if collaboration)
Month 6:   Paper 2 submission (clinical validation)
```

**Critical Path Decision Point:** End of Week 2
- If AUC(Λ) > 0.70 → full speed ahead
- If AUC(Λ) = 0.65-0.70 → continue cautiously
- If AUC(Λ) < 0.65 → KILL or pivot to mechanism-only

---

**Status:** READY TO START (pending T2 results for resource allocation)

**Recommendation:** Begin Week 1 work immediately if T2 KILL or marginal

---

## Sources

**Clinical Data:**
- [CX-5461 Phase I Trial Results (Nature Communications 2022)](https://www.nature.com/articles/s41467-022-31199-2)
- [CX-5461 BRCA1/2 Deficiency Study (Nature Communications 2017)](https://www.nature.com/articles/ncomms14432)
- [G-quadruplex ligand CX-5461 Review (Journal of Translational Medicine 2025)](https://translational-medicine.biomedcentral.com/articles/10.1186/s12967-025-06473-8)

**G4 Quantification:**
- [Direct genome-wide G4 identification (Nature Communications 2021)](https://www.nature.com/articles/s41467-021-26312-w)
- [G4-ChIP-seq Protocol (Nature Protocols 2017)](https://www.nature.com/articles/nprot.2017.150)
- [ssG4-seq Strand-Specific Mapping (Nature Communications 2025)](https://www.nature.com/articles/s41467-025-66895-2)
- [EndoQuad Database (Nucleic Acids Research)](https://academic.oup.com/nar/article/52/D1/D72/7334091)
- [G4 Mapping Methods Review (RSC Chemical Biology 2024)](https://pubs.rsc.org/en/content/articlehtml/2024/cb/d4cb00023d)

**Helicase Stratification:**
- [WRN Synthetic Lethality in MSI Cancer (Cancer Discovery 2021)](https://aacrjournals.org/cancerdiscovery/article/11/8/1923/666232/Werner-Helicase-Is-a-Synthetic-Lethal)
- [Novel WRN Inhibitors Target MSI Tumors (Cancer Discovery 2024)](https://aacrjournals.org/cancerdiscovery/article/14/8/1457/746511/Novel-WRN-Helicase-Inhibitors-Selectively-Target)
- [BLM in Multiple Myeloma (Frontiers Immunology 2022)](https://www.frontiersin.org/journals/immunology/articles/10.3389/fimmu.2022.983181/full)
- [BLM in Gliomas (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10175545/)
- [DNA Repair Helicases Review (NAR Cancer 2024)](https://academic.oup.com/narcancer/article/7/4/zcaf034/8276621)
