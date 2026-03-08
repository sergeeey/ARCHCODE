# 📋 RNA-seq Analysis Plan — Updated

**Date:** 2026-03-06  
**Status:** FASTQ Ready, Reference Needed

---

## ✅已完成 (Done)

| Component | Status | Location |
|-----------|--------|----------|
| **FASTQ files** | ✅ READY | `fastq_data/raw/` (12.4 GB) |
| **Sample ID** | ✅ VERIFIED | WT, B6 (del), A2 (inv) |
| **Pipeline scripts** | ✅ CREATED | `scripts/rnaseq_*.py` |
| **Documentation** | ✅ UPDATED | `fastq_data/README.md` |

---

## ⚠️ Требуется (Required)

### 1. Reference Genome Setup

**Status:** ❌ NOT READY

**Location:** `reference/hg38/` — EMPTY

**What's needed:**
- Human genome FASTA (hg38/GRCh38) — ~3 GB
- Gene annotation GTF — ~1 GB
- STAR index — ~30 GB

**Time:** 1-2 hours (download) + 30-60 min (STAR index)

**Instructions:** `reference/SETUP_REFERENCE.md`

---

### 2. Software Installation

| Tool | Status | Install |
|------|--------|---------|
| **STAR** | ❓ Unknown | `conda install -c bioconda star` |
| **FastQC** | ❓ Unknown | `conda install -c bioconda fastqc` |
| **Python 3.9+** | ✅ Ready | Already installed |

---

## 🚀 Options

### Option A: Full Setup (Recommended for publication)

**Steps:**
1. Download reference genome (1-2 hours)
2. Generate STAR index (30-60 min)
3. Install STAR + FastQC (10 min)
4. Run pipeline (2-3 hours)

**Total time:** 4-6 hours

**Benefit:** Full splice junction analysis, publication-grade results

---

### Option B: Quick Analysis (Exploratory)

**Use existing alignment (if available):**

If you already have BAM files from another analysis:

```bash
# Copy existing BAM files
cp /path/to/existing/*.bam fastq_data/aligned/

# Extract junctions from BAM
# (script needed: extract_junctions_from_bam.py)

# Run splice analysis directly
python scripts/analyze_splice_junctions.py
```

**Time:** 30 min

**Benefit:** Fast results, no reference setup needed

---

### Option C: External Service

**Use Galaxy Web Platform:**

1. Upload FASTQ to https://usegalaxy.org/
2. Run "RNA-seq alignment with STAR"
3. Download junctions file
4. Run local analysis: `python scripts/analyze_splice_junctions.py`

**Time:** 2-3 hours (upload + processing)

**Benefit:** No local setup, free

---

## 📊 Current Pipeline Status

```
┌─────────────────────────────────────────────────────────────┐
│  RNA-seq Pipeline Status                                    │
├─────────────────────────────────────────────────────────────┤
│  Step 1: FastQC           ⏸️  WAITING (FastQC needed)       │
│  Step 2: STAR Alignment   ⏸️  WAITING (Reference needed)    │
│  Step 3: Splice Analysis  ✅ READY (Script created)         │
│                                                             │
│  FASTQ:           ✅ SRR12935486 (WT)                       │
│                   ✅ SRR12935488 (B6 del)                   │
│                   ✅ SRR12935490 (A2 inv)                   │
│                                                             │
│  Reference:       ❌ NOT READY                              │
│  STAR Index:      ❌ NOT READY                              │
│  Software:        ❓ UNKNOWN                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recommendation

### Tonight (2026-03-06):

**If you have time (4-6 hours):**
1. Download reference genome
2. Start STAR index generation (runs overnight)
3. Tomorrow: Run pipeline

**If no time:**
1. Skip tonight
2. Tomorrow: Setup reference
3. Run pipeline

---

## 📅 Tomorrow (2026-03-07)

**Morning:**
- Setup reference genome (1-2 hours)
- Generate STAR index (30-60 min)

**Afternoon:**
- Run RNA-seq pipeline (2-3 hours)
- Review results
- Update manuscript if validated

---

## 📞 Alternative: Use Existing Data

**If you already have:**
- BAM files from previous analysis
- Or access to Galaxy/other platform

**Then:**
- Skip reference setup
- Extract junctions from existing data
- Run splice analysis directly

**Question:** Do you have existing RNA-seq alignment data for these samples?

---

## 📊 Expected Results (Hypothesis)

| Sample | Modification | Expected Aberrant % |
|--------|--------------|---------------------|
| WT (SRR12935486) | Intact | <5% |
| B6 (SRR12935488) | Deletion | 15-30% |
| A2 (SRR12935490) | Inversion | <10% |

**If validated:** Manuscript upgrade from EXPLORATORY → SUPPORTED

---

**Next action:** Choose option (A, B, or C) and proceed.
