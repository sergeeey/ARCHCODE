# Infrastructure Readiness Checklist — FASTQ Download Tonight

**Date:** 2026-02-05 16:10
**Status:** 🟡 Partially Ready (SRA Toolkit needs installation)

---

## ✅ What's Ready

### Disk Space

- **Available:** 155 GB on D: drive
- **Required:** ~50 GB (FASTQ 30GB + BAM 15GB + temp 5GB)
- **Status:** ✅ **SUFFICIENT** (3× headroom)

### Directory Structure

```
D:\ДНК\fastq_data\
├── raw\           ✅ Created (empty, ready)
├── aligned\       ✅ Created (empty, ready)
└── junctions\     ✅ Created (empty, ready)

D:\ДНК\reference\
└── hg38\          ✅ Created (empty, ready)
```

### Reference Genome

- **chr11.fa.gz:** ✅ Present (41 MB)
  - Location: `D:\ДНК\ДНК Образцы СКАЧЕННЫЙ\chr11.fa.gz`
  - Sufficient for HBB locus analysis (chr11:5.2-5.25 Mb)
- **Full hg38:** ⚠️ Optional (not required for targeted analysis)

### Existing Data

- **Hi-C data:** ✅ GSE160422 (extracted)
- **RNA-seq CPM:** ✅ GSE160420 (6 samples analyzed)
- **ChIP-seq BigWig:** ✅ GSE131055 (CTCF, H3K27ac available)
- **Reference:** ✅ chr11.fa.gz (GRCh38)

---

## ⚠️ What Needs Installation

### SRA Toolkit (CRITICAL for FASTQ download)

**Status:** ❌ Not installed (conda failed: PackagesNotFoundError)
**Attempted:** `conda install -c bioconda sra-tools` → package not available for win-64

**Installation required:** Pre-built Windows binaries (manual download)

**Instructions:** See `INSTALL_SRA_TOOLKIT_WINDOWS.md`
**Tonight:** Download ZIP (5 min) → Unzip → Add to PATH → Test

**Quick install (tonight, 5-10 minutes):**

```bash
# 1. Download (browser or wget)
https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-win64.zip

# 2. Unzip to D:\ДНК\tools\

# 3. Add to PATH
export PATH=$PATH:D:/ДНК/tools/sratoolkit.3.X.X-win64/bin

# 4. Test
fastq-dump --version
```

**Alternative:** Use WSL if available (conda install works in Linux)

---

### STAR Aligner (Needed tomorrow for alignment)

**Status:** ⚠️ Unknown (needs checking)

**Check command:**

```bash
STAR --version
```

**If not installed:**

```bash
# Via conda (may fail on work network)
conda install -c bioconda star

# Or download binaries
https://github.com/alexdobin/STAR/releases
```

**Note:** Can be installed tomorrow morning while FASTQ downloads complete

---

### Python Dependencies (For splice analysis)

**Required packages:**

- pandas ✅ (already used)
- numpy ✅ (already used)
- scipy ✅ (for correlation)
- matplotlib ✅ (for figures)

**Check:**

```bash
python -c "import pandas, numpy, scipy, matplotlib; print('All dependencies OK')"
```

**Status:** ✅ Likely already installed (used in previous scripts)

---

## 🎯 Tonight's Workflow (Assuming SRA Toolkit Installed)

### Step 1: Install SRA Toolkit (5-10 minutes)

```bash
# Follow INSTALL_SRA_TOOLKIT_WINDOWS.md
fastq-dump --version  # Verify
```

### Step 2: Navigate to Target Directory

```bash
cd D:\ДНК\fastq_data\raw
pwd  # Verify: /d/ДНК/fastq_data/raw
```

### Step 3: Start Download (4-6 hours, leave overnight)

```bash
# Download 3 samples in parallel
fastq-dump --split-files --gzip SRR12837671 &  # WT rep1
fastq-dump --split-files --gzip SRR12837674 &  # D3 (-36% HBB)
fastq-dump --split-files --gzip SRR12837675 &  # A2 (+28% HBB)

# Check progress (every 30 min)
ls -lh
du -sh .
```

**Expected completion:** 4-6 hours (by 1-3 AM if started at 21:00)

### Step 4: Verify Download (Tomorrow morning)

```bash
cd D:\ДНК\fastq_data\raw

# Check file sizes
ls -lh *.fastq.gz

# Expected:
# SRR12837671_1.fastq.gz  ~5 GB
# SRR12837671_2.fastq.gz  ~5 GB
# SRR12837674_1.fastq.gz  ~5 GB
# SRR12837674_2.fastq.gz  ~5 GB
# SRR12837675_1.fastq.gz  ~5 GB
# SRR12837675_2.fastq.gz  ~5 GB
# Total: ~30 GB

# Count reads (should be ~30-50 million per sample)
zcat SRR12837671_1.fastq.gz | wc -l  # Divide by 4 = read count
```

---

## 📋 Pre-Download Checklist

Run this tonight before starting download:

```bash
# 1. SRA Toolkit installed
fastq-dump --version
# Expected: fastq-dump : 3.X.X

# 2. Target directory exists and is writable
cd D:\ДНК\fastq_data\raw && touch test.txt && rm test.txt
# No errors = OK

# 3. Disk space sufficient
df -h D:\ДНК
# Available should be >50 GB

# 4. Internet connection stable
ping -c 5 ftp-trace.ncbi.nlm.nih.gov
# All packets received = OK

# 5. Command ready in clipboard
# Copy-paste from FASTQ_DOWNLOAD_PLAN_EVENING.md
```

---

## 🚨 Troubleshooting Guide

### "fastq-dump: command not found"

**Solution:** Install SRA Toolkit (see INSTALL_SRA_TOOLKIT_WINDOWS.md)

### "Failed to resolve hostname"

**Solution:** Check internet connection, retry after 5 min

### "Insufficient disk space"

**Check:**

```bash
df -h D:\ДНК
# Need: 50+ GB free
# Have: 155 GB ✅
```

### "Permission denied"

**Solution:**

```bash
# Check write permissions
cd D:\ДНК\fastq_data\raw
touch test.txt  # Should succeed
```

### Very slow download (<1 MB/s)

**Solutions:**

1. Use `fasterq-dump` instead (2-3× faster)
2. Switch to Aspera (10× faster, requires Aspera Connect)
3. Download during off-peak hours (midnight-6am)

### Download interrupted

**Resume download:**

```bash
# SRA Toolkit automatically resumes incomplete downloads
fastq-dump --split-files --gzip SRR12837671  # Will continue from last chunk
```

---

## ⏰ Estimated Timeline

**Tonight:**

- 19:00-19:10 — Install SRA Toolkit
- 19:10-19:15 — Run pre-download checklist
- 19:15-19:20 — Start downloads (3 parallel jobs)
- 19:20-23:00 — Monitor progress (optional, can leave unattended)
- 23:00+ — Leave overnight

**Tomorrow morning (09:00):**

- Check downloads complete (~30 GB total)
- Verify file integrity (read counts, gzip test)
- Install STAR aligner (if needed)
- Start STAR alignment (~12 hours, leave running during day)

**Tomorrow evening (21:00):**

- Check alignments complete
- Extract splice junctions (30 min)
- Run analysis (30 min)
- **Results ready!**

---

## 📊 Expected Outputs (Tomorrow)

### FASTQ Files (Raw)

```
D:\ДНК\fastq_data\raw\
├── SRR12837671_1.fastq.gz  (WT rep1 forward, ~5 GB)
├── SRR12837671_2.fastq.gz  (WT rep1 reverse, ~5 GB)
├── SRR12837674_1.fastq.gz  (D3 forward, ~5 GB)
├── SRR12837674_2.fastq.gz  (D3 reverse, ~5 GB)
├── SRR12837675_1.fastq.gz  (A2 forward, ~5 GB)
└── SRR12837675_2.fastq.gz  (A2 reverse, ~5 GB)
```

### BAM Files (Aligned, tomorrow evening)

```
D:\ДНК\fastq_data\aligned\
├── WT_rep1_Aligned.sortedByCoord.out.bam  (~3 GB)
├── WT_rep1_SJ.out.tab                      (~5 MB) ← SPLICE JUNCTIONS
├── D3_Aligned.sortedByCoord.out.bam        (~3 GB)
├── D3_SJ.out.tab                           (~5 MB) ← KEY FILE
├── A2_Aligned.sortedByCoord.out.bam        (~3 GB)
└── A2_SJ.out.tab                           (~5 MB) ← KEY FILE
```

### Analysis Results (Tomorrow evening)

```
D:\ДНК\fastq_data\junctions\
├── WT_rep1_HBB_junctions.txt
├── D3_HBB_junctions.txt
├── A2_HBB_junctions.txt
└── HBB_aberrant_splicing_results.csv  ← FINAL RESULT
```

---

## ✅ Readiness Summary

| Component        | Status           | Action Required                |
| ---------------- | ---------------- | ------------------------------ |
| **Disk Space**   | ✅ 155 GB free   | None                           |
| **Directories**  | ✅ Created       | None                           |
| **Reference**    | ✅ chr11.fa.gz   | None                           |
| **SRA Toolkit**  | ❌ Not installed | **Install tonight (5-10 min)** |
| **STAR Aligner** | ⚠️ Unknown       | Install tomorrow if needed     |
| **Python deps**  | ✅ Likely OK     | Verify tomorrow                |

**Overall Status:** 🟡 **75% Ready** (only SRA Toolkit missing)

**Critical Path:** Install SRA Toolkit → Start download → Leave overnight → Success

---

## 🎯 Success Criteria

**Tonight:** FASTQ download started successfully (no errors in first 10 min)
**Tomorrow AM:** All 6 FASTQ files present (~30 GB total)
**Tomorrow PM:** Splice junction analysis complete, aberrant % calculated

**If all criteria met:** Functional validation complete! 🎉

---

_Infrastructure Readiness Checklist_
_Created: 2026-02-05 16:10_
_Status: Ready except SRA Toolkit (install tonight)_
