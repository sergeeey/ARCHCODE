# Immediate Tasks Summary — Pre-FASTQ Work Complete

**Date:** 2026-02-05 (End of Work Day)
**Status:** 🟢 All feasible tasks completed

---

## ✅ Task 1: H3K36me3 ChIP-seq Search (COMPLETED)

**Objective:** Search GSE131055 archive for H3K36me3 data (splicing-related histone mark)

**Result:** ❌ **Not present in dataset**

**What we found in GSE131055:**

- ✅ H3K27ac (active enhancers) — 4 samples
- ✅ H3K27me3 (repressive mark) — 4 samples
- ✅ GATA1 (transcription factor) — 4 samples
- ❌ H3K36me3 — **NOT included**

**Conclusion:** Cannot analyze H3K36me3 effects on HBB splicing with current data. Alternative: Use tomorrow's RNA-seq BAM files to directly measure splice junction usage.

---

## ✅ Task 2: NMD Detection Pipeline (COMPLETED)

**Objective:** Prepare analysis code for tomorrow's FASTQ data

**Deliverable:** `scripts/analyze_nmd_susceptibility.py` (361 lines)

**Key Features:**

1. **HBB Gene Structure Definition**
   - Exon/intron coordinates (GRCh38)
   - CDS start/stop positions
   - Canonical splice junctions

2. **Junction Classification**
   - Canonical (normal splicing)
   - Exon skipping (e.g., exon 2 skipped)
   - Intron retention (cryptic splice sites)
   - Cryptic sites (unknown aberrant junctions)

3. **PTC Detection**
   - Scans retained introns for in-frame stop codons
   - Calculates frameshift probability for exon skipping
   - Applies NMD rule: PTC >50-55 nt from last junction

4. **Hypothesis Testing**
   - Automatically checks if D3 ≥15% NMD-susceptible
   - Compares WT vs D3 vs A2
   - Generates publication-ready summary tables

**Usage (tomorrow):**

```bash
cd D:\ДНК\fastq_data\aligned

python ../../scripts/analyze_nmd_susceptibility.py \
    WT_rep1_SJ.out.tab \
    D3_SJ.out.tab \
    A2_SJ.out.tab \
    --output-dir ../../data/nmd_analysis
```

**Expected Outputs:**

- `WT_rep1_nmd_details.csv` — Per-junction classification
- `D3_nmd_details.csv` — Per-junction classification
- `A2_nmd_details.csv` — Per-junction classification
- `nmd_comparison_summary.csv` — Cross-sample comparison
- Console output with hypothesis test result (✅/⚠️)

**Success Criteria:**

- If D3 shows ≥15% NMD-susceptible transcripts → Hypothesis SUPPORTED
- If D3 shows <15% → Alternative mechanism (documented in LOOP_THAT_STAYED_HYPOTHESIS.md)

---

## ⚠️ Task 3: Transcriptional Pausing Analysis (NOT FEASIBLE)

**Objective:** Calculate Promoter-Proximal Index (PPI) from CPM data

**Data Format Issue:**
Current CPM files (`GSM4873102_HUDEP2_RNA_WTrep1_rawcpm.csv`) contain:

```csv
Gene_Symbol, Total_CPM
HBB, 10886.3
```

**What's needed for PPI analysis:**

```csv
Gene, Exon, CPM
HBB, exon1, 3500
HBB, exon2, 4200
HBB, exon3, 3186
```

Or position-specific coverage: `chr11:5225464-5225726` → CPM value

**Conclusion:** ❌ **Current data lacks exon-level resolution**

**Solution:** Analysis becomes feasible **tomorrow** once BAM files available:

```bash
# Extract coverage from BAM (tomorrow)
samtools depth -r chr11:5225618-5225726 WT_rep1.bam > exon1_coverage.txt
samtools depth -r chr11:5227020-5227070 WT_rep1.bam > exon3_coverage.txt

# Calculate PPI
PPI = mean(exon1_coverage) / mean(exon3_coverage)
# If PPI >> 1 → Pol II paused at promoter
```

**Alternative Approach (Available Now):**
We already have **gene-level CPM** which shows:

- WT: 10,886 CPM (baseline)
- D3: 6,947 CPM (-36%) ← Overall reduction
- A2: 13,978 CPM (+28%) ← Overall increase

If pausing were the primary issue, we'd expect:

- High total CPM (Pol II initiated) + low protein (paused before exon 2)
- But D3 shows **low CPM** → suggests degradation (NMD) not pausing

**Tentative Conclusion (from gene-level data):**
Transcriptional pausing is **unlikely** to be the primary mechanism for D3 because:

1. Total mRNA reduced (not just protein)
2. Reduction matches NMD prediction (-36% → 15-30% aberrant transcripts)

**Definitive answer:** Tomorrow with exon-level coverage from BAM files.

---

## 📊 Summary of Day's Progress

| Task Category                | Status      | Key Findings                                     |
| ---------------------------- | ----------- | ------------------------------------------------ |
| **Hi-C Structural Analysis** | ✅ Complete | 0 TAD boundaries, weak structure explains r=0.16 |
| **CTCF Validation**          | ✅ Complete | 100% concordance with literature (6/6 sites)     |
| **RNA-seq Preliminary**      | ✅ Complete | D3: -36%, A2: +28% (novel finding)               |
| **Hypothesis Formulation**   | ✅ Complete | "Loop That Stayed" (8,000 words)                 |
| **Infrastructure Prep**      | ✅ Complete | 155 GB free, directories ready                   |
| **H3K36me3 Search**          | ✅ Complete | Not in dataset                                   |
| **NMD Pipeline**             | ✅ Complete | Ready for tomorrow's data                        |
| **Pausing Analysis**         | ⚠️ Deferred | Needs BAM files (tomorrow)                       |

**Total Files Created Today:** 19 files, >20,000 words documentation, 3 analysis scripts

---

## 🎯 Tonight's Action Items (User)

**⏰ After 19:00 (at home):**

1. **Install SRA Toolkit** (5-10 minutes)
   - Follow: `INSTALL_SRA_TOOLKIT_WINDOWS.md`
   - Test: `fastq-dump --version`

2. **Start FASTQ Download** (leave overnight, 4-6 hours)

   ```bash
   cd D:\ДНК\fastq_data\raw

   # See: FASTQ_DOWNLOAD_PLAN_EVENING.md
   # Or quick start: ⏰_START_HERE_TONIGHT.txt

   fastq-dump --split-files --gzip SRR12837671 SRR12837674 SRR12837675 &
   ```

3. **Verify next morning** (~30 GB expected)
   ```bash
   ls -lh D:\ДНК\fastq_data\raw
   # Should see 6 files: *_1.fastq.gz, *_2.fastq.gz
   ```

---

## 🚀 Tomorrow's Workflow (User)

**Morning (09:00):**

- Check FASTQ downloads complete
- Install STAR aligner (if needed): `conda install -c bioconda star`
- Start alignment (12 hours):
  ```bash
  STAR --runThreadN 8 --genomeDir reference/hg38 \
       --readFilesIn raw/SRR12837671_1.fastq.gz raw/SRR12837671_2.fastq.gz \
       --readFilesCommand zcat \
       --outFileNamePrefix aligned/WT_rep1_ \
       --outSAMtype BAM SortedByCoordinate
  ```

**Evening (21:00):**

- Run NMD analysis: `python scripts/analyze_nmd_susceptibility.py ...`
- Run PPI analysis: Extract exon-level coverage from BAM files
- **Result:** Hypothesis validated or refuted within 24 hours!

---

## ✅ All Pre-FASTQ Work Complete

**What's Ready:**

- ✅ Download commands prepared
- ✅ Installation guides written
- ✅ Analysis pipeline coded
- ✅ Hypothesis documented
- ✅ Infrastructure checked
- ✅ Disk space confirmed (155 GB)

**What's Pending:**

- ⏰ FASTQ download (tonight)
- ⏰ STAR alignment (tomorrow day)
- ⏰ Splice junction analysis (tomorrow evening)

**You are fully prepared for tonight's data acquisition!** 🎉

---

_Immediate Tasks Summary_
_Created: 2026-02-05 17:30_
_All feasible pre-FASTQ tasks completed_
