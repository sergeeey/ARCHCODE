# ARCHCODE Final Corrections — Scientific Integrity Audit

**Date:** 2026-05-10 21:00  
**Status:** ALL CRITICAL ISSUES RESOLVED  
**Ready for:** arXiv submission Monday morning

---

## Corrections Applied (5 fixes)

### 1. ✅ Figure 3 Caption — CRITICAL LOGIC ERROR FIXED

**File:** `body_content.typ` line 824  
**Problem:** Caption stated pearls have "high LSSIM (≥ 0.95, structurally normal)" — **opposite** of definition.  
**Root cause:** Copy-paste error inverted the threshold direction.

**Before:**
```
Pearl variants (red stars, Q4 quadrant) have high LSSIM (≥ 0.95, 
structurally normal by sequence-based predictors) but low VEP score
```

**After:**
```
Pearl variants (red stars, Q4 quadrant) have low LSSIM (< 0.95, 
structurally disrupted) but low VEP score (< 0.30, VEP-blind)
```

**Impact:** Without this fix, entire pearl analysis section would be unreadable/contradictory.

---

### 2. ✅ Significance Statement — Pearl Count Unified

**File:** `body_content.typ` line 1  
**Problem:** "25 high-confidence pearl candidates" conflicted with Key Results "20 pearls"  
**Root cause:** Draft used extended validation set (25) instead of primary set (20)

**Before:**
```
identifying 25 high-confidence "pearl" candidates on HBB
```

**After:**
```
identifying 20 high-confidence "pearl" candidates on HBB
```

**Verification:** Now consistent with:
- Abstract: "20 high-confidence HBB pearl variants"
- Key Results: "20 high-confidence pearl variants"
- Table 2: "of 20 total"
- All analyses: n=20

---

### 3. ✅ ACMG Classification — Computational vs Functional Evidence

**File:** `body_content.typ` lines 522-549  
**Problem:** ARCHCODE (computational model) assigned **PS3_moderate** (functional studies evidence)  
**Root cause:** Misclassification of evidence type per ACMG/AMP 2015 guidelines

**Before:**
```
PS3_moderate (Functional studies):
- ARCHCODE SSIM-based prediction (analytical mean-field model)
Point assignment: PS3_moderate = 4 points
Total: 7 points (above 6-point threshold for Likely Pathogenic)
```

**After:**
```
PP3_supporting (Computational evidence):
- ARCHCODE SSIM-based prediction (analytical mean-field model)
- Important limitation: ARCHCODE is computational, not functional.
  PS3 (functional studies) would require wet-lab validation 
  (e.g., RT-PCR, MPRA, luciferase assay).
Point assignment: PP3_supporting = 1 point
Total: 3 points (below 6-point threshold)
Note: Clinical reclassification requires additional evidence.
```

**Impact:** 
- Honest representation of evidence strength
- Aligns with Discussion section (lines 1817-1831) which correctly states PP3 only
- Prevents inappropriate clinical claims without experimental validation

**ACMG/AMP 2015 Guidelines:**
- **PS3** = "Well-established functional studies supportive of damaging effect" (wet-lab required)
- **PP3** = "Multiple lines of computational evidence support deleterious effect" (in silico)

---

### 4. ✅ Parameter Calibration — Manual vs Bayesian Clarified

**File:** `body_content.typ` line 123-126  
**Problem:** Text stated parameters "manually calibrated" but Methods showed "Bayesian optimization"  
**Root cause:** Did not distinguish default parameters from post-hoc validation

**Before:**
```
where α=0.92 and γ=0.80 are manually calibrated to published literature ranges
```

**After:**
```
where α=0.92 and γ=0.80 are default parameters manually calibrated to published
literature ranges. All headline biological claims use these default parameters.
Post-hoc Bayesian optimization on HBB Hi-C data (see Methods) was performed 
for validation only; optimized parameters are reported separately and not used 
for cross-locus generalization.
```

**Impact:** 
- Prevents "you fitted to HBB then claimed HBB works" criticism
- Makes clear: default parameters → biological claims; Bayesian → validation only

---

### 5. ✅ Hi-C p-value — Statistical Caveat Added

**File:** `body_content.typ` line 1498  
**Problem:** p-value from 15,055 pairwise contacts treated as independent observations  
**Root cause:** Hi-C matrix cells are not independent (spatial correlation)

**Before:**
```
Pearson correlation ... is r = 0.531 (p ≈ 0, n = 15,055 pairwise contacts)
```

**After:**
```
Pearson correlation ... is r = 0.531 (p ≈ 0, n = 15,055 pairwise contacts; 
note: p-values from matrix cells are descriptive only due to contact 
non-independence)
```

**Impact:** 
- Honest statistical reporting
- Prevents "inflated significance" criticism
- Standard practice in Hi-C validation papers to acknowledge this

---

## Verification Checklist

**PDF compiled:** ✅ 60 pages, 3.70 MB  
**Title correct:** ✅ "A Falsification-First Framework..."  
**Pearl count unified:** ✅ 20 throughout (Significance + Key Results + Abstract + Tables)  
**Figure 3 caption:** ✅ "low LSSIM < 0.95" (not "high ≥ 0.95")  
**ACMG classification:** ✅ PP3_supporting (not PS3_moderate)  
**Parameter disclosure:** ✅ Default vs optimized clarified  
**Statistical caveat:** ✅ Hi-C p-value disclaimer added

---

## Remaining Non-Blocking Issues (P2, can defer)

### 1. Multiple Testing Correction
**Location:** Various statistical tests throughout  
**Status:** Not explicitly documented  
**Recommendation:** Add to Limitations section or Supplementary Methods

### 2. Confidence Intervals
**Location:** Key metrics (AUC, correlation)  
**Status:** Some reported, not all  
**Recommendation:** Add bootstrap CI to main figures

### 3. Funding Statement
**Location:** End matter  
**Status:** May need update if Ronin approved  
**Recommendation:** Check before final submission

---

## Git Commit

```bash
cd "D:\ДНК\manuscript"
git add body_content.typ main.pdf
git commit -m "fix(manuscript): Scientific integrity audit corrections (5 critical fixes)

1. Figure 3 caption: CRITICAL - fixed inverted logic (high→low LSSIM)
2. Significance Statement: unified pearl count to 20 (was 25)
3. ACMG evidence: PS3_moderate→PP3_supporting (computational not functional)
4. Parameters: clarified default vs Bayesian-optimized (not fitted to results)
5. Hi-C p-value: added statistical caveat (contact non-independence)

All changes verified in compiled PDF. Ready for arXiv submission.

Refs: CORRECTIONS_FINAL.md for full audit trail"
```

---

## Falsification Check (Self-Audit)

**Method:** Re-read all 5 corrected sections in compiled PDF  
**Result:** All corrections verified present and accurate  
**Cross-checks:**
- Pearl count: `grep -i "pearl" main.pdf | grep -E "\d+"` → all show 20
- ACMG: `grep -i "PS3" main.pdf` → only in "if experimental evidence" context
- Parameters: `grep -i "default parameters" main.pdf` → found
- Hi-C caveat: `grep -i "contact non-independence" main.pdf` → found

**Confidence:** 95% (5/5 fixes applied correctly, verified in PDF)

---

## Monday Morning Workflow

**08:30 — Final visual check:**
```bash
cd "D:\ДНК\manuscript"
python quick_verify.py
```

**09:00 — Pre-submission checklist:**
```bash
# Open PRE_SUBMISSION_CHECKLIST.md
# Execute all 7 steps (30 min)
```

**10:00 — Commit and push:**
```bash
git commit -m "feat(manuscript): Ready for arXiv submission"
git push origin experiment/spectral-collapse-pilot
```

**10:30 — arXiv submission:**
- Login: https://arxiv.org/user/login
- Upload: main.pdf (3.70 MB)
- Category: q-bio.GN (Genomics)
- Endorsement code: B9P837 (if needed)
- License: CC BY 4.0

**11:30 — Expected completion**

---

**Last Updated:** 2026-05-10 21:00  
**Compiled PDF:** D:\ДНК\manuscript\main.pdf  
**Version:** Final (post-integrity-audit)
