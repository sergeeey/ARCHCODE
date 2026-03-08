# 📊 Galaxy RNA-seq Progress Tracker

**Start Time:** _____________  
**Expected Finish:** _____________ (+3-4 hours)

---

## 📋 Progress Checklist

### Phase 1: Setup (5-10 min)

- [ ] Открыть https://usegalaxy.org/
- [ ] Click "Login or Register"
- [ ] Click "Register"
- [ ] Заполнить форму (email, username, password)
- [ ] Подтвердить email
- [ ] ✅ Login successful

**Time started:** _____:_____  
**Time finished:** _____:_____

---

### Phase 2: FASTQ Upload (30-60 min)

**Files to upload (6 total):**

| File | Size | Status | Time |
|------|------|--------|------|
| SRR12935486_1.fastq.gz | 1.95 GB | ⏳ Pending | _____:_____ |
| SRR12935486_2.fastq.gz | 1.84 GB | ⏳ Pending | _____:_____ |
| SRR12935488_1.fastq.gz | 1.87 GB | ⏳ Pending | _____:_____ |
| SRR12935488_2.fastq.gz | 2.08 GB | ⏳ Pending | _____:_____ |
| SRR12935490_1.fastq.gz | 1.87 GB | ⏳ Pending | _____:_____ |
| SRR12935490_2.fastq.gz | 2.73 GB | ⏳ Pending | _____:_____ |

**Upload method:**
- [ ] Web browser (Upload Data button)
- [ ] FTP (ftp.usegalaxy.org)

**All files uploaded:** _____:_____

---

### Phase 3: STAR Alignment (1-2 hours per sample)

#### Sample 1: WT (SRR12935486)

- [ ] Open "STAR on data" tool
- [ ] Select R1: SRR12935486_1.fastq.gz
- [ ] Select R2: SRR12935486_2.fastq.gz
- [ ] Reference: Human (GRCh38)
- [ ] Click "Run"
- [ ] ⏳ Running...
- [ ] ✅ Complete

**Started:** _____:_____  
**Finished:** _____:_____

---

#### Sample 2: B6 Deletion (SRR12935488)

- [ ] Open "STAR on data" tool
- [ ] Select R1: SRR12935488_1.fastq.gz
- [ ] Select R2: SRR12935488_2.fastq.gz
- [ ] Reference: Human (GRCh38)
- [ ] Click "Run"
- [ ] ⏳ Running...
- [ ] ✅ Complete

**Started:** _____:_____  
**Finished:** _____:_____

---

#### Sample 3: A2 Inversion (SRR12935490)

- [ ] Open "STAR on data" tool
- [ ] Select R1: SRR12935490_1.fastq.gz
- [ ] Select R2: SRR12935490_2.fastq.gz
- [ ] Reference: Human (GRCh38)
- [ ] Click "Run"
- [ ] ⏳ Running...
- [ ] ✅ Complete

**Started:** _____:_____  
**Finished:** _____:_____

---

### Phase 4: Extract Junctions (10-15 min)

#### For each sample:

**WT Junctions:**
- [ ] Tools → Search "regtools"
- [ ] Select "regtools junctions extract"
- [ ] Input: WT BAM file
- [ ] Run
- [ ] Download → Save as `WT_junctions.tab`

**B6 Junctions:**
- [ ] Tools → Search "regtools"
- [ ] Select "regtools junctions extract"
- [ ] Input: B6 BAM file
- [ ] Run
- [ ] Download → Save as `B6_junctions.tab`

**A2 Junctions:**
- [ ] Tools → Search "regtools"
- [ ] Select "regtools junctions extract"
- [ ] Input: A2 BAM file
- [ ] Run
- [ ] Download → Save as `A2_junctions.tab`

**All junctions downloaded:** _____:_____

---

### Phase 5: Local Analysis (1-2 min)

- [ ] Verify files:
  ```bash
  dir D:\ДНК\fastq_data\junctions\*.tab
  ```
- [ ] Run analysis:
  ```bash
  cd D:\ДНК
  python scripts\analyze_splice_junctions.py
  ```
- [ ] Open report:
  ```
  D:\ДНК\fastq_data\results\splice_analysis_report.md
  ```

**Analysis complete:** _____:_____

---

## 📊 Results Summary

### Expected vs Observed

| Sample | Expected Aberrant % | Observed % | Status |
|--------|---------------------|------------|--------|
| WT | <5% | _____% | ⏳ Pending |
| B6 (deletion) | 15-30% | _____% | ⏳ Pending |
| A2 (inversion) | <10% | _____% | ⏳ Pending |

---

## 🎯 Final Verdict

**Hypothesis Test:**

- [ ] ✅ **VALIDATED** — B6 shows 15-30% aberrant splicing
- [ ] ⚠️  **PARTIAL** — Some samples match, others don't
- [ ] ❌ **NOT SUPPORTED** — Results don't match predictions

**Next Steps:**

- [ ] Update manuscript with validation results
- [ ] Submit to bioRxiv
- [ ] Prepare for experimental follow-up

---

## 📝 Notes

**Issues encountered:**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

**Observations:**
```
_______________________________________________________
_______________________________________________________
_______________________________________________________
```

---

**Total Time:** _____ hours _____ minutes

**Status:** ⏳ In Progress / ✅ Complete / ❌ Failed
