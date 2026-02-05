# RNA-seq Preliminary Analysis: GSE160420 HUDEP2 Cells

**Date:** 2026-02-05
**Status:** Processed gene expression data analyzed — splice junction data requires FASTQ download

---

## Downloaded Data

**Source:** GSE160420 (HUDEP2 RNA-seq, loop engineering study)

**Files:** 6 CSV files with CPM (counts per million) gene expression

**Format:** Gene-level quantification, NOT splice junction information

**Size:** 1.3 MB total (processed data)

---

## HBB Gene Expression Results

| Sample | Clone | Type | HBB CPM | vs WT Avg | Observation |
|--------|-------|------|---------|-----------|-------------|
| **GSM4873102** | WT rep1 | Control | 11,538 | Baseline | High expression (erythroid) |
| **GSM4873103** | WT rep2 | Control | 10,234 | Baseline | High expression (erythroid) |
| **WT Average** | — | — | **10,886** | — | **Baseline reference** |
| **GSM4873104** | B6 | 3'HS1 deletion | 10,468 | -4% | Similar to WT |
| **GSM4873105** | D3 | 3'HS1 deletion | 6,947 | **-36%** ⚠️ | **Significantly reduced** |
| **GSM4873106** | A2 | 3'HS1 inversion | 13,978 | **+28%** ⚠️ | **Significantly elevated** |
| **GSM4873107** | G3 | 3'HS1 inversion | 8,767 | -19% | Moderately reduced |

---

## Key Observations

### 1. Wild-Type Baseline

**WT Average: 10,886 CPM**
- High HBB expression confirms erythroid identity (beta-globin major transcript)
- Good replicate agreement (11,538 vs 10,234, ~11% CV acceptable for RNA-seq)
- HBBP1 (pseudogene) also detected: 8.14 CPM (100× lower than HBB, expected)

### 2. 3'HS1 Deletion Clones (B6, D3)

**B6:** 10,468 CPM (-4% vs WT) — minimal change
**D3:** 6,947 CPM (-36% vs WT) — **major reduction**

**Interpretation:**
- D3 shows substantial loss of HBB expression
- Could indicate:
  - ❓ Aberrant splicing → nonsense-mediated decay
  - ❓ Transcriptional downregulation
  - ❓ mRNA instability
- **Cannot distinguish mechanisms without splice junction data**

**Clone variation:** B6 vs D3 both have same 3'HS1 deletion, but different expression
- Suggests clonal heterogeneity or off-target effects
- D3 may have additional perturbations beyond 3'HS1 deletion

### 3. 3'HS1 Inversion Clones (A2, G3)

**A2:** 13,978 CPM (+28% vs WT) — **elevated expression**
**G3:** 8,767 CPM (-19% vs WT) — moderate reduction

**Interpretation:**
- A2 shows INCREASED HBB expression (unexpected!)
- Possible mechanisms:
  - ❓ Enhanced transcription (inversion creates new enhancer interaction?)
  - ❓ Increased mRNA stability
  - ❓ Compensatory upregulation
- **Counterintuitive:** Loop disruption leading to MORE expression, not less

**Clone variation:** A2 vs G3 diverge dramatically (14K vs 8.7K CPM)
- Again suggests clonal effects

---

## Limitations of Gene-Level Data

### What We CAN Conclude

✅ **Functional impact detected:** 3'HS1 modifications alter HBB expression
✅ **Clone-specific effects:** Different clones with same edit show different outcomes
✅ **Directional variation:** Both increases (A2: +28%) and decreases (D3: -36%) observed

### What We CANNOT Conclude

❌ **Aberrant splicing mechanism:** Gene counts don't distinguish spliced vs unspliced
❌ **Splice junction usage:** No information on exon skipping, intron retention, cryptic sites
❌ **Isoform composition:** Can't tell if HBB isoforms change (though HBB has simple 3-exon structure)
❌ **Correlation with Hi-C loops:** Need splice-specific data to test "Loop That Stayed" hypothesis

---

## Why Splice Junction Data Is Critical

**Gene expression (CPM) measures:**
- Total mRNA abundance (all isoforms combined)
- Includes properly spliced + aberrantly spliced transcripts

**Splice junction data measures:**
- Reads spanning exon-exon boundaries
- Can quantify:
  - Canonical junction usage (exon 1→2, exon 2→3)
  - Aberrant junctions (exon 1→3 skipping, intron retention)
  - Cryptic splice sites

**Example:**
If D3 has 36% reduced HBB expression, possible scenarios:
1. **Scenario A:** 36% transcriptional reduction, normal splicing
   - No aberrant splicing, just less mRNA
2. **Scenario B:** Normal transcription, 36% aberrantly spliced → degraded
   - This would support "Loop That Stayed" (splicing defect)
3. **Scenario C:** Mix of both

**We cannot distinguish these without junction-level data.**

---

## Next Steps: Decision Point

### Option 1: Download FASTQ and Call Splice Junctions (Recommended)

**Action:**
1. Access SRA Run Selector: https://www.ncbi.nlm.nih.gov/Traces/study/?acc=SRP290306
2. Download FASTQ for WT + D3 + A2 (prioritize clones with biggest expression changes)
3. Align with STAR (splice-aware aligner)
4. Extract SJ.out.tab (splice junction file)
5. Quantify canonical vs aberrant junctions at HBB locus

**Timeline:** 1-2 days (download + alignment)

**Size:** ~20-30 GB total (or ~10 GB if just WT, D3, A2)

**Advantage:** Direct splice junction quantification

**Deliverable:** Aberrant splicing % for each clone

---

### Option 2: Infer from Gene Expression (Quick but Limited)

**Analysis:**
Use existing CPM data to calculate differential expression and infer functional impact (already done above).

**Limitations:**
- Cannot prove aberrant splicing mechanism
- Can only say "expression changed" not "why"

**Manuscript framing:**
- "Loop disruption correlates with altered HBB expression (r=?, p=?)"
- "Splice junction analysis required to confirm aberrant splicing hypothesis"
- Document as preliminary finding, full validation pending

---

### Option 3: Check Published Paper for Splice Data

**Action:**
1. Find the publication associated with GSE160420 (likely Liang et al. 2021)
2. Check Supplementary Data for splice junction tables
3. If available, use published data directly

**Advantage:** No download or compute needed

**Risk:** May not be published or may not include splice-specific analysis

---

### Option 4: Correlation with Hi-C (Exploratory)

**Analysis:**
Despite lacking splice data, test if HBB expression change correlates with Hi-C loop disruption:

| Clone | Hi-C Loop Status | HBB Expression Change | Loop-Expression Correlation? |
|-------|------------------|-----------------------|------------------------------|
| WT | Intact loops | Baseline (10,886 CPM) | — |
| B6 | Deleted 3'HS1 | -4% (minimal) | Weak |
| D3 | Deleted 3'HS1 | -36% (major) | Strong |
| A2 | Inverted 3'HS1 | +28% (elevated!) | **Opposite direction?** |
| G3 | Inverted 3'HS1 | -19% (moderate) | Moderate |

**Hypothesis:**
If loop disruption → functional impact, expect correlation between:
- Hi-C loop change (from GSE160422, already have)
- HBB expression change (from GSE160420, just obtained)

**Problem:**
- Clonal heterogeneity (B6≠D3, A2≠G3) complicates interpretation
- Need Hi-C data for D3 and G3 (only have WT, B6, A2 from GSE160422)

**Partial test possible:**
- WT vs B6 vs A2 (all have matching Hi-C)
- Calculate correlation (n=3, limited power)

---

## Recommended Action Plan

### Immediate (Today)

✅ **Download gene expression data** — DONE
✅ **Extract HBB expression** — DONE
✅ **Identify D3 (-36%) and A2 (+28%) as interesting clones** — DONE

### Short-term (Tomorrow)

**Task:** Search for published paper + check for splice junction data in Supplementary Materials

**Steps:**
1. Search PubMed: "GSE160420" OR "GSE160425" OR "Liang HUDEP2 3'HS1"
2. Download paper PDF
3. Check Supplementary Tables for splice junction data
4. If found → extract and analyze
5. If NOT found → proceed to FASTQ download

---

### Medium-term (Next Week)

**Task:** Download FASTQ for selected samples and perform splice junction analysis

**Priority samples:**
1. **WT rep1** (GSM4873102) — baseline
2. **D3** (GSM4873105) — biggest reduction (-36%)
3. **A2** (GSM4873106) — biggest increase (+28%)

**Analysis pipeline:**
1. STAR alignment → BAM + SJ.out.tab
2. Extract HBB locus reads (chr11:5,225,464-5,227,079)
3. Quantify canonical junctions:
   - Exon 1→2: chr11:5,225,726→5,226,405
   - Exon 2→3: chr11:5,226,626→5,227,079
4. Quantify aberrant junctions (any non-canonical)
5. Calculate aberrant splicing %:
   ```
   aberrant % = aberrant_reads / (canonical_reads + aberrant_reads)
   ```
6. Compare WT vs D3 vs A2

**Expected outcome:**
- **If "Loop That Stayed" correct:** D3 shows high aberrant splicing (15-30%)
- **If alternative mechanism:** D3 shows normal splicing, just lower total counts

---

## Preliminary Hypothesis

### Based on Expression Data Only

**Observation:** Loop engineering (deletion/inversion of 3'HS1) causes bidirectional HBB expression changes:
- Deletion clone D3: -36% (major reduction)
- Inversion clone A2: +28% (major elevation)

**Possible mechanisms:**

**For D3 reduction (-36%):**
1. **Aberrant splicing → NMD (nonsense-mediated decay)** ⭐ Supports "Loop That Stayed"
2. Transcriptional downregulation (enhancer-promoter loop disrupted)
3. mRNA instability (3'HS1 affects RNA processing)

**For A2 elevation (+28%):**
1. **Compensatory upregulation** (inversion disrupts negative regulatory loop?)
2. New enhancer interaction (inversion creates novel contact)
3. mRNA stabilization (inverted 3'HS1 acts as stabilizing element)

**Critical test:** Splice junction analysis will distinguish scenario 1 (aberrant splicing) from scenarios 2-3 (transcriptional/stability).

---

## Correlation Potential (Once Junction Data Available)

**If we obtain splice junction data, we can test:**

**Hypothesis:** Loop disruption (Hi-C) correlates with aberrant splicing (RNA-seq)

**Data integration:**
| Clone | Hi-C SSIM Change | HBB Expression Change | Aberrant Splicing % (TBD) |
|-------|------------------|----------------------|---------------------------|
| WT | 0 (baseline) | 0% | ? (baseline) |
| B6 | ? (have Hi-C) | -4% | ? |
| D3 | ? (no Hi-C) | -36% | ? |
| A2 | ? (have Hi-C) | +28% | ? |
| G3 | ? (no Hi-C) | -19% | ? |

**Problem:** Incomplete matrix (missing Hi-C for D3, G3)

**Solution:**
- Focus on WT, B6, A2 (have both Hi-C and RNA-seq)
- Download Hi-C for D3, G3 if available (check GSE160422 for additional samples)

---

## Conclusion

**What we learned today:**
✅ HUDEP2 RNA-seq data exists and is downloadable
✅ HBB gene expression varies substantially across loop-engineered clones (-36% to +28%)
✅ Functional impact of loop disruption is detectable at gene level

**What we still need:**
❌ Splice junction data to test aberrant splicing hypothesis
❌ Complete Hi-C coverage for all RNA-seq clones (D3, G3)
❌ Quantitative correlation analysis (loop disruption vs splicing defects)

**Next decision:**
- Download FASTQ for splice junction analysis? (1-2 days work)
- OR check published paper first for existing splice data? (1 hour search)

**Recommendation:** Check published paper first (quick), then download FASTQ if splice data not available.

---

*RNA-seq Preliminary Analysis*
*Created: 2026-02-05*
*Gene expression analyzed — splice junction analysis pending FASTQ download*
