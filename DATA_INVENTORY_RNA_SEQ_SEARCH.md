# Data Inventory: RNA-seq Search for Aberrant Splicing Analysis

**Date:** 2026-02-05
**Objective:** Find RNA-seq data to validate "Loop That Stayed" hypothesis functionally (splicing level)
**Status:** ❌ No RNA-seq data currently available — ChIP-seq and Hi-C only

---

## Current Data Inventory

### ✅ What We HAVE

**1. Hi-C Data (GSE160422)**
- **Files:** GSE160422_RAW.tar (multiple archives, 31 GB total)
- **Content:** Capture Hi-C .hic files for HUDEP2 cells
- **Samples:** GSM4873116 (WT), GSM4873118 (A2), etc.
- **Status:** ✅ Already used for validation (GSM4873116 extracted)
- **Use case:** Chromatin architecture validation (completed)

**2. ChIP-seq Data (GSE131055)**
- **Files:** GSE131055_RAW.tar (4.4 GB) + unpacked in DNK OBRAZCI/ (31 GB)
- **Content:** BigWig files (.bw format)
- **Targets:**
  - CTCF (GSM3762801-3762804) — 4 replicates (CD34 D0/D12)
  - H3K27ac (GSM3762805-3762806, 3762815-3762816) — active enhancers
  - H3K27me3 (GSM3762807-3762808) — repressive mark
  - GATA1 (GSM3762809-3762810, 3762813, 3762817) — erythroid TF
  - Input controls
- **Cell types:** CD34+ progenitors (D0, D12), HUDEP2 (D3), SNP235
- **Status:** ⚠️ Unpacked but not used yet (pyBigWig installation failed previously)
- **Use case:** CTCF site validation, enhancer mapping (potential)

**3. Reference Genome**
- **File:** chr11.fa.gz (41 MB)
- **Content:** Chromosome 11 sequence (GRCh38)
- **Status:** ✅ Available
- **Use case:** Reference for alignment, splice site annotation

---

### ❌ What We NEED (Missing)

**RNA-seq Data for Aberrant Splicing Analysis**

**Required format (any of):**
1. **FASTQ files** (raw reads) — need alignment + splice junction calling
2. **BAM files** (aligned reads) — need splice junction calling
3. **Splice junction files** (pre-computed) — ready for analysis
4. **Gene expression matrix** with isoform counts — can infer splicing

**Ideal dataset characteristics:**
- **Cell type:** HUDEP2 erythroid progenitors (matches Hi-C data)
- **Condition:** Wild-type (no perturbations)
- **Locus:** Covers chr11:5,200,000-5,250,000 (HBB region)
- **Depth:** >30M reads for robust splice junction detection
- **Replicates:** ≥2 biological replicates

**What we're looking for:**
- Canonical splice junctions (expected HBB exon-exon boundaries)
- Aberrant junctions:
  - Exon skipping (e.g., exon 1 missing)
  - Intron retention (e.g., intron 1 retained in mRNA)
  - Cryptic splice sites (non-canonical donor/acceptor usage)
- Junction read counts (quantification)

---

## Search Strategy: Finding RNA-seq Data

### Option 1: Search GEO for HUDEP2 RNA-seq

**Hypothesis:** Same research group that generated GSE160422 (Hi-C) and GSE131055 (ChIP-seq) likely generated RNA-seq.

**Search query:**
```
HUDEP2 AND RNA-seq AND (erythroid OR globin OR differentiation)
```

**Promising accessions to check:**
- GSE131055 (check if it has RNA-seq in addition to ChIP-seq)
- SuperSeries containing GSE160422
- Liang et al. 2021 (authors of GSM4873116) — check Supplementary Data

**Action:** Use GEO DataSets web search or NCBI Entrez

---

### Option 2: Extract from Published Supplements

**Paper:** Liang et al. 2021 (source of GSM4873116 Hi-C data)

**Potential sources:**
1. **Supplementary Data Files**
   - Splice junction tables (pre-computed)
   - Gene expression matrices (TPM, FPKM)
   - Differential isoform usage
2. **Data Availability Statement**
   - May list additional GEO accessions
   - May provide direct download links
3. **Methods Section**
   - RNA-seq experimental design details
   - Analysis pipeline (can reproduce if data available)

**Action:** Download paper PDF, check Supplements

---

### Option 3: Public Splice Junction Databases

**Resources:**
1. **ENCODE CSHL Long RNA-seq**
   - Cell types: K562, GM12878 (not HUDEP2, but related)
   - Format: BAM files with splice junctions annotated
   - URL: https://www.encodeproject.org/

2. **GTEx (Genotype-Tissue Expression)**
   - Tissue: Whole blood (contains erythroid cells)
   - Format: Expression + splice junction quantification
   - URL: https://gtexportal.org/

3. **TCGA (Cancer Genome Atlas)**
   - Tissue: Leukemia samples (may include erythroid)
   - Format: BAM + processed junction files
   - URL: https://portal.gdc.cancer.gov/

**Limitation:** These are NOT HUDEP2-specific, may have different splicing patterns.

**Action:** Download K562 or whole blood RNA-seq as proxy

---

### Option 4: In Silico Splice Prediction

**If no experimental data available, predict computationally:**

**Tools:**
1. **SpliceAI** (deep learning splice predictor)
   - Input: Genomic sequence + variant position
   - Output: Δ splice score (cryptic site activation probability)
   - Can predict aberrant splicing WITHOUT RNA-seq data

2. **MaxEntScan**
   - Input: Splice site sequences (donor/acceptor)
   - Output: Splice strength score
   - Can compare WT vs variant strength

3. **Human Splicing Finder**
   - Input: Sequence surrounding variant
   - Output: ESE/ESS (enhancer/silencer) predictions
   - Identifies regulatory motifs

**Workflow:**
1. Extract HBB gene sequence (chr11:5,225,464-5,227,079)
2. Annotate canonical splice sites (exon 1-2-3 boundaries)
3. Run SpliceAI to predict cryptic sites
4. Calculate expected % aberrant splicing based on scores

**Limitation:** Computational predictions, not experimental validation.

**Advantage:** Can proceed immediately without waiting for data.

---

## Recommended Action Plan

### Plan A: Search + Download RNA-seq (if exists)

**Timeline:** 1-2 days

**Steps:**
1. Search GEO for HUDEP2 RNA-seq (query above)
2. If found: Download FASTQ or BAM files
3. Align (if FASTQ) using STAR aligner
4. Call splice junctions using STAR or LeafCutter
5. Quantify aberrant splicing at HBB locus

**Success criteria:** Find ≥1 HUDEP2 RNA-seq dataset with >30M reads

**If successful:** Proceed to splice junction analysis (Phase C experimental validation)

---

### Plan B: Use Proxy Data (K562 or GTEx)

**Timeline:** 1 day

**Steps:**
1. Download K562 RNA-seq from ENCODE (closest erythroid cell line)
2. Extract HBB locus reads (chr11:5.2-5.25 Mb)
3. Call splice junctions
4. Document as "proxy validation" (not HUDEP2-specific)

**Limitation:** K562 is leukemia cell line, may have different splicing patterns than HUDEP2.

**Justification:** Better than no data, can establish methodology.

---

### Plan C: In Silico Prediction (Immediate)

**Timeline:** <1 day

**Steps:**
1. Install SpliceAI (`pip install spliceai`)
2. Extract HBB sequence from chr11.fa.gz
3. Predict splice sites for WT sequence
4. Calculate expected aberrant splicing %
5. Document as "computational hypothesis pending experimental validation"

**Advantage:** Can proceed immediately, establishes testable hypothesis.

**Limitation:** Not experimental data (violates CLAUDE.md preference for real data).

**Acceptable if:** Clearly labeled as "in silico prediction" in manuscript.

---

### Plan D: Acknowledge as Future Work (Recommended)

**Timeline:** N/A (documentation only)

**Steps:**
1. Add to manuscript Discussion:
   - "Functional validation via RNA-seq aberrant splicing analysis is pending"
   - "Experimental design: HUDEP2 RNA-seq, splice junction calling, quantification"
   - "Expected outcome: If 'Loop That Stayed' hypothesis correct, expect 10-30% aberrant splicing"
2. Add to Phase C roadmap:
   - "Experimental RNA-seq generation (if data unavailable)"
   - "RT-PCR validation of predicted splice junctions"

**Rationale:** We just completed Hi-C validation (r=0.16, modest). Adding RNA-seq analysis now would be premature without first improving Hi-C correlation through parameter optimization (Phase C goals).

**Advantage:** Honest about limitations, focuses effort on improving structural model first.

---

## Decision Matrix

| Plan | Data Type | Timeline | Cost | CLAUDE.md Compliant | Recommended? |
|------|-----------|----------|------|---------------------|--------------|
| **A: Search RNA-seq** | Experimental (if exists) | 1-2 days | Free | ✅ Yes (real data) | ✅ If found |
| **B: K562 proxy** | Experimental (proxy) | 1 day | Free | ⚠️ Partial (not HUDEP2) | ⚠️ If Plan A fails |
| **C: In silico** | Computational | <1 day | Free | ⚠️ No (synthetic) | ❌ Only if labeled |
| **D: Future work** | N/A (proposal) | N/A | N/A | ✅ Yes (honest) | ✅ **RECOMMENDED** |

---

## Recommendation

### Short-term (Now): **Plan A + D Combined**

**Immediate (1-2 days):**
1. ✅ Search GEO for HUDEP2 RNA-seq (Plan A)
2. ✅ If found → Download and analyze
3. ✅ If NOT found → Document as Phase C future work (Plan D)

**Rationale:**
- Quick search (1-2 days) is low-cost, high-reward if data exists
- If data doesn't exist, acknowledge honestly rather than using synthetic/proxy data
- Aligns with CLAUDE.md "real data first" principle

### Medium-term (Phase C): Experimental Generation

**If no public data exists:**
1. **Collaborate with HUDEP2 lab** to generate RNA-seq
2. **RT-PCR validation** of predicted splice junctions (cheaper than whole transcriptome)
3. **Minigene assays** to test splicing in controlled system

**Budget:** $15-30K for RNA-seq + validation experiments

---

## Next Steps (User Decision)

**Choose one:**

**Option 1:** "Proceed with Plan A (search GEO for RNA-seq)"
- I'll search GEO systematically for HUDEP2 RNA-seq datasets
- If found: download and analyze
- If not found: document as future work

**Option 2:** "Proceed with Plan B (use K562 proxy data)"
- Download ENCODE K562 RNA-seq
- Analyze HBB splicing (with caveat: not HUDEP2)
- Document limitations in manuscript

**Option 3:** "Skip RNA-seq for now (Plan D)"
- Focus on Phase C (Hi-C model improvement first)
- Document RNA-seq validation as future work in manuscript
- Wait for better Hi-C correlation (r≥0.5) before adding splicing layer

**Option 4:** "In silico prediction (Plan C)"
- Run SpliceAI computationally
- Document as hypothesis, not validation
- Mark clearly as "pending experimental confirmation"

---

**My recommendation:** **Option 1 (Plan A search) → fallback to Option 3 (Plan D) if not found.**

**Reasoning:**
1. We just finished Hi-C validation showing r=0.16 (modest)
2. Adding RNA-seq now is "stacking hypotheses" before validating the first layer
3. Better to improve Hi-C model (Phase C) → THEN add splicing layer
4. Quick GEO search is worth trying, but if data unavailable, honest acknowledgment > synthetic workaround

---

*Data Inventory Report*
*Created: 2026-02-05*
*Status: Awaiting user decision on RNA-seq analysis strategy*
