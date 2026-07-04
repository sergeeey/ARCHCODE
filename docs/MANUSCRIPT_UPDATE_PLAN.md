# Manuscript Update Plan — Discovery Engine Positioning

**Date:** 2026-03-06  
**Goal:** Update manuscript to reflect "Discovery Engine" positioning (not "Prediction Tool")

---

## ✅ Safe Changes (Non-Destructive)

These changes **enhance** existing text without removing critical information:

### 1. Abstract — Opening Sentence

**Current (prediction-focused):**
> "Sequence-based variant effect predictors (VEP) evaluate pathogenicity through protein-coding impact..."

**Proposed (discovery-focused):**
> "We discovered a systematic structural blind spot in sequence-based variant interpretation: 27 'pearl' variants invisible to VEP, SpliceAI, and CADD, yet detectable through 3D chromatin simulation."

**Impact:** ✅ Adds discovery narrative, doesn't remove existing content

---

### 2. Abstract — Methods Section

**Current:**
> "We retrieved 353 clinically classified HBB variants from ClinVar..."

**Proposed:**
> "We applied ARCHCODE, a physics-based discovery engine, to 353 clinically classified HBB variants from ClinVar..."

**Impact:** ✅ Clarifies ARCHCODE's role as discovery tool

---

### 3. Abstract — Results Section

**Current:**
> "Across nine loci — HBB (1,103), CFTR (3,349)... ARCHCODE processed 30,318 ClinVar variants..."

**Proposed:**
> "Across nine loci, ARCHCODE **discovered** 27 'pearl' variants on HBB — VEP-blind (score < 0.30), SpliceAI-blind (0.00), CADD-ambiguous (median 15.7), yet structurally disruptive (LSSIM < 0.92)."

**Impact:** ✅ Highlights key finding, not just processing stats

---

### 4. Abstract — Conclusions

**Current:**
> "ARCHCODE's analytical mean-field approach to loop extrusion simulation identifies enhancer-proximal structural pathogenic signal..."

**Proposed:**
> "ARCHCODE **reveals** a dimension of pathogenicity **invisible to sequence-based tools**: enhancer-proximal structural disruption. The 27 HBB pearl variants represent candidates for experimental prioritization. We propose structural simulation as a **complementary, hypothesis-generating layer**, not a replacement for sequence-based prediction."

**Impact:** ✅ Clarifies complementary role, avoids overclaiming

---

### 5. Introduction — New Paragraph

**Add after existing intro:**

> "**ARCHCODE is a Discovery Engine, not a Prediction Tool.** This distinction is critical: prediction tools compete on accuracy (AUC, F1), while discovery engines create new categories by revealing previously invisible mechanisms. ARCHCODE does not aim to outperform VEP or CADD at their tasks; instead, it detects variants that operate through structural mechanisms fundamentally outside their scope."

**Impact:** ✅ Explicit positioning statement

---

## ⚠️ Changes Requiring Review

These changes modify existing claims — **review before applying**:

### 1. ROC/AUC Emphasis

**Current:**
> "ROC analysis yielded AUC = 0.977 (Pathogenic mean SSIM = 0.927; Benign mean SSIM = 0.996)."

**Proposed:**
> "ROC analysis characterized category-distribution differences (AUC = 0.977); however, the primary finding is the discovery of 27 pearl variants in the ARCHCODE-only quadrant (Q2), invisible to sequence-based methods."

**Rationale:** AUC is secondary; pearls are primary.

**Requires review:** ✅ Yes — check with author

---

### 2. Clinical Utility Claims

**Current:**
> "Per-locus threshold calibration demonstrates that universal thresholds are locus-specific..."

**Proposed:**
> "Per-locus threshold calibration enables **hypothesis prioritization** for experimental validation. Clinical utility requires orthogonal validation and is not claimed in this study."

**Rationale:** Avoids overclaiming clinical readiness.

**Requires review:** ✅ Yes — check with author

---

## 📋 Implementation Checklist

- [ ] **Abstract** — Update opening sentence (discovery-focused)
- [ ] **Abstract** — Add "27 pearl variants" to results
- [ ] **Abstract** — Clarify complementary role in conclusions
- [ ] **Introduction** — Add Discovery Engine paragraph
- [ ] **Results** — De-emphasize AUC, emphasize pearls
- [ ] **Discussion** — Add limitations about clinical utility
- [ ] **Review** — Confirm all changes with author

---

## 🚀 Safe to Apply Now

The following files can be updated **without risk**:

1. `manuscript/ABSTRACT.md` — Add discovery narrative
2. `manuscript/INTRODUCTION.md` — Add Discovery Engine paragraph
3. `manuscript/DISCUSSION.md` — Add limitations section

**Files requiring author review:**
1. `manuscript/FULL_MANUSCRIPT.md` — Main manuscript (comprehensive changes)
2. `manuscript/RESULTS.md` — AUC emphasis changes

---

## 📞 Next Steps

1. ✅ Apply safe changes (abstract, intro, discussion)
2. ⏳ Wait for author review on Results changes
3. ⏳ Submit to bioRxiv after review

---

**Status:** Ready to implement safe changes. Awaiting confirmation for Results changes.
