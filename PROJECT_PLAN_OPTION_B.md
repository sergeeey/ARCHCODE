# Project Plan: Option B — Real ClinVar Data Integration
## ARCHCODE Manuscript Upgrade from Synthetic to Real Clinical Data

**Decision Date:** 2026-02-04
**Timeline:** 1-2 weeks
**Status:** PLANNING → EXECUTION
**Lead:** Sergey Boyko + Claude Sonnet 4.5

---

## 🎯 Objective

Replace synthetic HBB variant dataset with real ClinVar pathogenic variants to enable:
1. **Clinical validation** of "Loop That Stayed" computational signature
2. **Real AI comparison** (SpliceAI/CADD instead of mock AlphaGenome)
3. **Publishable discovery** backed by clinical evidence
4. **Strong preprint** → journal submission track

---

## 📊 Current vs Target State

| Aspect | Current (Synthetic) | Target (Real) |
|--------|---------------------|---------------|
| **Dataset** | 366 generated variants | ~1,500-3,000 ClinVar pathogenic |
| **VCV IDs** | Sequential mock (VCV000000001) | Real ClinVar accessions |
| **Baseline** | AlphaGenome (random generator) | SpliceAI + CADD scores |
| **Validation** | Computational only | Clinical literature evidence |
| **Discovery** | Artifact (synthetic clustering) | Real if pattern exists |
| **Publication** | Framework demo | Clinical discovery |

---

## 📅 Timeline (14 Days)

### **Week 1: Data & Simulation**

**Day 1-2: Data Acquisition**
- [ ] Download ClinVar HBB variants (API/FTP)
- [ ] Process and categorize (~1,500-3,000 variants)
- [ ] Verify data quality

**Day 3-5: ARCHCODE Simulation**
- [ ] Run simulations on all real variants (batch processing)
- [ ] Calculate SSIM for each variant
- [ ] Generate contact matrices for top candidates
- [ ] Checkpoint: ~50% variants simulated

**Day 6-7: Complete Simulation + QC**
- [ ] Finish remaining simulations
- [ ] Quality control: outlier detection
- [ ] Generate summary statistics

---

### **Week 2: Analysis & Writing**

**Day 8-9: Real Predictor Integration**
- [ ] Download SpliceAI scores (precomputed or API)
- [ ] Extract CADD scores from ClinVar
- [ ] Merge with ARCHCODE results

**Day 10-11: Discovery Analysis**
- [ ] Search for real "Loop That Stayed" pattern
- [ ] Statistical validation (clustering, p-values)
- [ ] Cross-reference with literature (HbVar, PubMed)
- [ ] Identify clinical case reports

**Day 12-13: Manuscript Revision**
- [ ] Update Methods (real data sources)
- [ ] Rewrite Results (real discovery or null result)
- [ ] Update Discussion (clinical implications)
- [ ] Fix all Sabaté 2025 → 2024

**Day 14: Final Review & Submission**
- [ ] Regenerate figures with real data
- [ ] Create supplementary tables
- [ ] Generate PDF
- [ ] Submit to bioRxiv

---

## 🔧 Technical Implementation

### Phase 1: Data Acquisition Scripts

**Created:**
- ✅ `scripts/download_clinvar_hbb.ts` — ClinVar API download
- ✅ `scripts/process_clinvar_hbb.ts` — Data processing & categorization

**To Create:**
- [ ] `scripts/simulate_real_variants.ts` — Batch ARCHCODE simulation
- [ ] `scripts/integrate_spliceai.ts` — SpliceAI score integration
- [ ] `scripts/analyze_real_patterns.ts` — Discovery analysis

---

### Phase 2: ARCHCODE Batch Simulation

**Challenge:** ~2,000 variants × 30s/variant = ~16 hours compute time

**Solution: Parallel Processing**
```typescript
// Batch configuration
const BATCH_SIZE = 50;  // Process 50 variants at a time
const PARALLEL_WORKERS = 4;  // 4 simultaneous simulations

// Estimated time: 16 hours / 4 workers = 4 hours
```

**Checkpoint System:**
```json
{
  "checkpoint": {
    "processed_variants": 500,
    "remaining": 1500,
    "timestamp": "2026-02-06T10:30:00Z",
    "resume_from": "VCV000123456"
  }
}
```

---

### Phase 3: Real Predictor Integration

#### SpliceAI Scores

**Option A: Precomputed (Recommended)**
```bash
# Download SpliceAI precomputed scores for HBB region
wget https://spliceailookup-api.broadinstitute.org/spliceai/scores/chr11:5225464-5227079
```

**Option B: API (Rate Limited)**
```typescript
// Max 1 request/second
const spliceaiScore = await fetchSpliceAI(hgvs);
await sleep(1000);
```

#### CADD Scores

**From ClinVar:**
```typescript
// Already included in ClinVar variant records
const caddScore = variant.cadd_phred_score;
```

---

### Phase 4: Discovery Analysis

**Statistical Test for "Loop That Stayed" Pattern:**

```typescript
// 1. Filter splice_region variants
const spliceRegion = variants.filter(v => v.category === 'splice_region');

// 2. Calculate SSIM distribution
const ssimDistribution = spliceRegion.map(v => v.archcode_ssim);

// 3. Identify outliers (high SSIM + pathogenic)
const loopConstrained = spliceRegion.filter(v =>
    v.archcode_ssim > 0.50 &&  // Goldilocks zone
    v.archcode_ssim < 0.60 &&
    v.clinical_significance === 'Pathogenic' &&
    v.spliceai_score < 0.5  // Low sequence-based prediction
);

// 4. Statistical significance
const pValue = calculateClusteringPValue(loopConstrained);

// 5. Clinical validation
for (const variant of loopConstrained) {
    const literature = await searchPubMed(variant.vcv_id);
    const hbvar = await queryHbVar(variant.hgvs_c);
    // Document case reports, functional studies
}
```

---

## 📋 Data Sources (Approved per CLAUDE.md)

### Primary Data
- ✅ **ClinVar** — NCBI ClinVar FTP/API (current release)
- ✅ **SpliceAI** — Illumina SpliceAI Lookup (precomputed scores)
- ✅ **CADD** — Combined Annotation Dependent Depletion (from ClinVar)

### Validation Databases
- ✅ **HbVar** — http://globin.bx.psu.edu/hbvar/ (beta-globin variants)
- ✅ **PubMed** — Literature evidence via E-utilities API
- ✅ **gnomAD** — Population frequency (v4.0)

### Reference Data
- ✅ **Sabaté et al. 2024** (bioRxiv) — Loop duration 6-19 min
- ✅ **Davidson et al. 2019** — Cohesin extrusion speed
- ✅ **Treisman et al. 1982** — IVS-II-1 discovery (β-thalassemia)

---

## 🎲 Possible Outcomes

### Outcome A: Pattern Confirmed (Best Case)
**Discovery:** Real splice_region variants cluster at SSIM 0.50-0.60

**Evidence:**
- n ≥ 5 variants with SSIM clustering (SD < 0.01)
- All pathogenic with literature evidence
- Low SpliceAI/CADD scores (blind spot confirmed)
- Clinical case reports documenting β-thalassemia

**Manuscript:** "Discovery of Loop-Constrained Pathogenic Variants in HBB"

**Impact:** High (potential Nature Genetics / AJHG)

---

### Outcome B: Pattern Absent (Null Result)
**Finding:** No significant clustering in real data

**Explanation:** Synthetic dataset artifact due to:
- Deterministic position generation
- Uniform CTCF anchor spacing assumption
- Oversimplified loop model

**Manuscript:** "ARCHCODE: A Physics-Based Framework for Variant Interpretation"

**Impact:** Medium (methods paper, Bioinformatics / NAR)

---

### Outcome C: Weaker Pattern (Middle Ground)
**Finding:** Some evidence but low sample size (n=2-3)

**Interpretation:** Suggestive but requires validation

**Manuscript:** "Computational Evidence for Loop-Constrained Splice Variants (Pilot Study)"

**Impact:** Medium (bioRxiv → follow-up with wet-lab)

---

## 🚨 Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| **No pattern found** | Medium | Pivot to framework paper (Outcome B) |
| **Compute time overrun** | Low | Parallel processing + checkpoints |
| **SpliceAI API limits** | Medium | Use precomputed scores |
| **Scooping risk** | Low | Fast execution (2 weeks max) |
| **Data quality issues** | Low | ClinVar gold standard dataset |

---

## 📊 Success Metrics

### Technical Milestones
- [ ] Downloaded ≥1,500 real ClinVar variants
- [ ] Simulated ≥95% variants successfully
- [ ] Integrated SpliceAI + CADD for ≥90% variants
- [ ] Identified statistical pattern (p < 0.05) OR documented null result

### Manuscript Quality
- [ ] All DOIs resolve (no 404)
- [ ] Real ClinVar VCV IDs (verified)
- [ ] Clinical literature evidence (≥3 case reports for key variants)
- [ ] Passes CLAUDE.md integrity checks

### Publication Readiness
- [ ] Manuscript ready for bioRxiv (Day 14)
- [ ] Supplementary files complete
- [ ] GitHub repository updated
- [ ] Data availability compliant

---

## 🔄 Daily Stand-up Format

**Every morning (5 minutes):**
1. Yesterday: What did we complete?
2. Today: What will we work on?
3. Blockers: Any issues?

**Example:**
```
Day 3 Stand-up:
- Yesterday: Downloaded 2,137 ClinVar variants, processed categories
- Today: Start ARCHCODE batch simulation (target: 500 variants)
- Blockers: None
```

---

## 📁 File Structure (Updated)

```
ARCHCODE/
├── data/
│   ├── clinvar_hbb_raw.json          # Downloaded ClinVar data
│   ├── clinvar_hbb_processed.json    # Categorized variants
│   └── spliceai_scores.json          # SpliceAI predictions
├── results/
│   ├── HBB_Clinical_Atlas_REAL.csv   # Final dataset (replaces synthetic)
│   ├── simulation_checkpoints/       # Batch processing checkpoints
│   └── discovery_analysis.json       # Pattern detection results
├── scripts/
│   ├── download_clinvar_hbb.ts       # ✅ Created
│   ├── process_clinvar_hbb.ts        # ✅ Created
│   ├── simulate_real_variants.ts     # 🔨 To create
│   ├── integrate_spliceai.ts         # 🔨 To create
│   └── analyze_real_patterns.ts      # 🔨 To create
└── PROJECT_PLAN_OPTION_B.md          # This file
```

---

## 💬 Communication Protocol

**Progress Updates:**
- Daily stand-up notes in this file (append to bottom)
- Git commits with descriptive messages
- Mark checkpoints with tags: `git tag checkpoint-day3`

**Decision Points:**
- Day 7: Review simulation progress → continue or pivot?
- Day 11: Pattern found? → choose manuscript angle
- Day 13: Final go/no-go for bioRxiv submission

---

## 🎓 Learning Outcomes (Regardless of Result)

### Technical Skills
- ✅ ClinVar API integration
- ✅ Large-scale biophysical simulation
- ✅ Statistical pattern detection
- ✅ Multi-source data integration

### Scientific Process
- ✅ Falsification-first methodology
- ✅ Real data vs synthetic comparison
- ✅ Null result acceptance
- ✅ Transparent reporting (CLAUDE.md compliance)

### Project Management
- ✅ 2-week sprint execution
- ✅ Checkpoint-based progress tracking
- ✅ Risk mitigation strategies

---

## 🚀 Next Immediate Actions

**TODAY (Day 0):**
1. ✅ Create PROJECT_PLAN_OPTION_B.md
2. ✅ Create download_clinvar_hbb.ts
3. ✅ Create process_clinvar_hbb.ts
4. [ ] Commit to git: `git add . && git commit -m "plan: Option B real data pipeline"`
5. [ ] Review plan with user
6. [ ] BEGIN Day 1 execution

**DAY 1 (Tomorrow):**
```bash
# Morning
npx tsx scripts/download_clinvar_hbb.ts

# Afternoon
npx tsx scripts/process_clinvar_hbb.ts

# Evening
Review data quality, prepare simulation script
```

---

## 📝 Notes & Decisions

**2026-02-04 19:15** — Decision: Option B selected (real ClinVar data)
- Rationale: Stronger publication, clinical validation possible
- Trade-off: 1-2 weeks delay vs immediate synthetic demo
- Confidence: 80% (realistic timeline, CLAUDE.md guardrails in place)

**Next Decision Point:** Day 7 (simulation progress review)

---

**Project Lead:** Sergey Boyko
**AI Assistant:** Claude Sonnet 4.5 (CLAUDE.md compliant)
**Start Date:** 2026-02-05 (planned)
**Target Submission:** 2026-02-18 (bioRxiv)

---

*"Real data beats synthetic data, but shipping beats perfection."*
— Adapted from Reid Hoffman
