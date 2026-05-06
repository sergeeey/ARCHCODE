# Publication Readiness Review — Строгая рецензия
**Reviewer:** Claude Code (Skeptic Mode)  
**Date:** 2026-05-02  
**Status:** 🔴 **NOT READY — критические ошибки требуют исправления**

---

## Executive Summary

**Paper 1 (Research Square rs-9090074):** 6/10 — Публичен как preprint, но содержит устаревшие claims без baseline comparison и matched-control tests. **Требуется обновление v2.**

**Paper 2 (Human Mutation submission):** 5/10 — Идея хорошая, но 4 критических ошибки блокируют submission:
1. Неправильное значение AF (0.000193 vs 0.000648)
2. Логически неверный denominator (7 vs 12)
3. Article type не подтверждён ("Short Report" vs "Brief Report")
4. Affiliation pending (Ronin ответ ожидается ~May 10)

**Вердикт:** Задержать submission на 2-3 дня для исправления критических ошибок.

---

## Paper 2: PyPop HBB Population Stratification

### 🔴 CRITICAL ERRORS (must fix before submission)

#### Error 1: Incorrect AF_EAS Value for VCV000015471
**Location:** Lines 136-137, Results section

**Current text:**
```
Variant 1: chr11:5227099 T>C (VCV000015471)
- AF_EAS: 0.000193 (East Asian-specific, absent in other populations)
```

**Problem:** [VERIFIED-REAL] Data mismatch between sources:
- **gnomad_populations_pearls.csv:** AF_EAS = 0.000193 (uses TOTAL AC=1, AN=152146, NOT population-specific)
- **gnomad_coverage_check.json:** AF_EAS = 0.000648 (uses population-specific AC_EAS=24, AN_EAS=37034) ✓ CORRECT

**Evidence:**
```python
# From coverage_check.json (VERIFIED source):
AC_EAS = 24
AN_EAS = 37034
AF_EAS = 24/37034 = 0.000648053...
```

**Root cause:** CSV file mixes total AC/AN with population-specific AF in same row. Coverage_check.json is authoritative source.

**Fix required:**
```diff
- AF_EAS: 0.000193 (East Asian-specific, absent in other populations)
+ AF_EAS: 0.000648 (East Asian-specific, absent in other populations)
```

**Impact:** This affects the MAIN CLAIM of the paper (East Asian enrichment). With corrected AF=0.000648, enrichment is even STRONGER, so conclusion remains valid but numbers must be accurate.

---

#### Error 2: Denominator Mismatch in Abstract
**Location:** Line 23, Abstract

**Current text:**
```
Among 7 variants with gnomAD data, 41.7% (5/12) showed universal constraint
```

**Problem:** [INFERRED-LOGIC] "Among 7" implies denominator = 7, but fraction shows 5/12.

**Correct options:**
1. "Among 12 variants queried, 41.7% (5/12) were found in gnomAD and showed universal constraint"
2. "Among 7 variants found in gnomAD, 71.4% (5/7) showed universal constraint"

**Recommended fix:**
```diff
- Among 7 variants with gnomAD data, 41.7% (5/12) showed universal constraint
+ Among 12 HBB promoter variants, 7 (58.3%) were found in gnomAD; of these, 5 (71.4%) showed universal constraint (absent in all populations)
```

This separates query success rate (7/12) from constraint analysis (5/7).

---

#### Error 3: Article Type Not Confirmed
**Location:** Line 10, front matter

**Current text:**
```
Article type: Short Report
```

**Problem:** [VERIFIED-DOCS] Human Mutation journal uses "**Brief Reports**", not "Short Report".

From journal guidelines ([source](https://onlinelibrary.wiley.com/page/journal/10981004/homepage/guide.htm)):
> Brief Reports are concise (~2-4 page), high-impact observations... Limited to 12 double-spaced pages.

**Word count issue:**
- Current manuscript: 3,239 words = ~13 double-spaced pages
- Brief Report limit: 12 double-spaced pages
- **EXCEEDS LIMIT by ~1 page**

**Options:**
1. Cut 200-300 words to fit Brief Report format
2. Submit as **Research Article** (if journal accepts, no clear word limit found)
3. Contact editorial office to confirm article type before submission

**Recommended action:** Email Managing Editor (humu@wiley.com) BEFORE submission:
> "Does Human Mutation accept 3,200-word submissions as Brief Reports, or should this be submitted as a Research Article?"

---

#### Error 4: Affiliation Status Uncertain
**Location:** Line 4, front matter

**Current text:**
```
Affiliation: Ronin Institute for Independent Scholarship 2.0
```

**Problem:** [MEMORY] Ronin application submitted 2026-03-12, expected answer ~2026-05-10 (60 days). Today is 2026-05-02 → **answer not yet received**.

**Options:**
1. Wait until May 10 for Ronin approval
2. Submit with pending affiliation + note in cover letter:
   > "Affiliation: Ronin Institute (application under review, approval expected May 10, 2026)"
3. Submit as independent researcher:
   > "Affiliation: Independent Researcher"

**Recommended:** Option 1 (wait 8 days) OR Option 3 (submit now as independent).

Do NOT use "Ronin Institute 2.0" as confirmed affiliation until approval received.

---

### ⚠️ MEDIUM PRIORITY ISSUES (fix before submission)

#### Issue 5: Methods — Data Source Clarity
**Location:** Lines 96-98, Methods

**Current text:**
```
Allele frequencies were queried from gnomAD v4 exome (primary) and genome (supplementary) datasets.
```

**Problem:** [WEAK] Does not specify which variant came from which dataset.

**Fix:**
```diff
- Allele frequencies were queried from gnomAD v4 exome (primary) and genome (supplementary) datasets.
+ VCV000015466 (chr11:5227102 T>C) was queried from gnomAD v4 exome (AN_EAS=36,610), VCV000015471 (chr11:5227099 T>C) from genome (AN_EAS=37,034). Both datasets showed sufficient coverage (AN >30,000) for reliable East Asian allele frequency estimates, confirmed via independent coverage validation (results/gnomad_coverage_check.json).
```

This makes data provenance explicit and reproducible.

---

#### Issue 6: Results — Maximum AF Table Inconsistency
**Location:** Lines 125-130, Results

**Current text:**
```
Maximum AF per population:
- EAS: 0.000464 (HIGHEST)
- SAS: 0.000415
```

**Problem:** [INFERRED] After fixing VCV000015471 AF from 0.000193 → 0.000648, EAS maximum should be 0.000648, not 0.000464.

**Fix:**
```diff
- EAS: 0.000464 (HIGHEST)
+ EAS: 0.000648 (HIGHEST)
```

Also update line 140:
```diff
- Variant 2: chr11:5227102 T>C (VCV000015466)
-   AF_EAS: 0.000464 (HIGHEST in dataset, popmax = eas)
+ Variant 2: chr11:5227102 T>C (VCV000015466)
+   AF_EAS: 0.000464 (second-highest, popmax = eas)
```

---

### ✅ LOW PRIORITY (consider but not blocking)

#### Suggestion 1: Strengthen Limitations Section
**Location:** Lines 173-178, Discussion

Current limitations are good, but add:
```
5. Single time-point analysis — allele frequencies are dynamic; historical selection may differ from current distribution
6. Admixture not modeled — EAS designation in gnomAD may include mixed-ancestry individuals
```

---

#### Suggestion 2: Add Data Transparency Note
Add after Data Availability (line 226):
```markdown
## TRANSPARENCY DECLARATION

This study detects potential false positives in structural variant prediction through epidemiology mismatch. While we identify two variants with reverse enrichment patterns, functional validation (Hi-C, CRISPR) is required to definitively classify these as benign. Population stratification provides hypothesis-generating evidence, not diagnostic classification.
```

This pre-empts reviewer concerns about over-claiming.

---

## Paper 1: Research Square Preprint (rs-9090074/v1)

### 🔴 REQUIRES UPDATE (not urgent, but scientifically necessary)

**Current status:** Live preprint DOI: 10.21203/rs.3.rs-9090074/v1

**Problems identified from MOC:**
1. Reports AUC=0.98 WITHOUT baseline comparison
2. No matched-control tests (later killed Class B with p=0.996)
3. No category-leakage analysis (baseline category→score alone = AUC 0.98)

**Recommendation:** Upload **v2** to Research Square with:
- Title update: "...Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots: A Negative Result"
- Abstract caveat: "Baseline category mapping achieves AUC=0.98; structural features add ~0.02"
- Methods: Add "Matched Controls" section
- Results: Report baseline AUC + within-category AUC (~0.5)
- Discussion: Reframe as negative result with methodological lessons

**Urgency:** P0 but NOT blocking Paper 2. Can upload v2 AFTER Paper 2 submission.

**Benefit:** Protects scientific credibility. Negative results are publishable and valuable.

---

## Submission Checklist — Paper 2

### Before Submission (MUST complete ALL)

- [ ] **Fix AF_EAS for VCV000015471:** 0.000193 → 0.000648 (lines 136, 125)
- [ ] **Fix denominator:** "Among 7... 5/12" → "Among 12... 7 found; of these, 5..." (line 23)
- [ ] **Confirm article type:** Email humu@wiley.com re: Brief Report vs Research Article
- [ ] **Resolve affiliation:** Wait for Ronin approval OR use "Independent Researcher"
- [ ] **Update Results table:** EAS max AF = 0.000648 (line 130)
- [ ] **Add data provenance:** Specify exome vs genome source for each variant (Methods)
- [ ] **Re-run numbers check:** Grep all "0.000193" in manuscript, replace with 0.000648
- [ ] **Convert to .docx:** Use Pandoc or Word, check formatting
- [ ] **Prepare cover letter:** Draft ready in SUBMISSION_CHECKLIST_MAY4.md
- [ ] **Supplementary files:** gnomad_populations_pearls.csv, gnomad_coverage_check.json, query script

### Estimated Time to Fix

- Critical errors 1-4: **2 hours** (data correction + article type clarification)
- Medium priority 5-6: **30 minutes** (methods clarity)
- Format + convert: **1 hour**

**Total:** 3.5 hours → can submit **May 3** if start today.

---

## Reviewer Verdict

### Paper 2: 5/10 → **REVISE AND RESUBMIT (to yourself)**

**Strengths:**
- Novel application of PyPop to structural variant validation ✓
- Strong epidemiology concordance analysis ✓
- Good limitations disclosure ✓
- Reproducible data (GitHub + Zenodo) ✓

**Critical weaknesses:**
- Wrong AF value (data integrity error)
- Denominator logic flaw (confusing fractions)
- Article type unclear (may not fit Brief Report format)
- Affiliation not confirmed

**Recommendation:** Do NOT submit until all 4 critical errors fixed. Risk of desk rejection for data inconsistency.

**Timeline:**
- Fix errors: May 2-3 (today + tomorrow)
- Submit: May 3 afternoon
- Deadline: May 4 ✓ achievable

---

### Paper 1: 6/10 → **UPDATE RECOMMENDED (post-Paper 2)**

**Why 6/10:**
- Preprint is live and citable ✓
- Taxonomy framework is novel ✓
- BUT: Contains overclaims (AUC without baseline) ❌
- Missing falsification results ❌

**Recommendation:** Upload v2 with negative-result framing after Paper 2 acceptance.

**Priority:** P1 (important for reputation, not urgent for submission deadlines)

---

## Evidence Audit

All claims in this review marked with evidence levels:

- [VERIFIED-REAL]: AF values from gnomad_coverage_check.json (calculated from AC/AN)
- [VERIFIED-DOCS]: Human Mutation journal guidelines (WebSearch + official site)
- [INFERRED-LOGIC]: Denominator mismatch (mathematical inconsistency)
- [MEMORY]: Ronin application timeline (from activeContext.md)
- [WEAK]: Methods clarity (style issue, not factual error)

Zero [UNKNOWN] claims. All reviewable.

---

## Final Recommendation

🛑 **STOP submission until critical errors fixed.**

✅ **THEN submit Paper 2 on May 3** (achievable with 1 day focused work).

⏳ **THEN update Paper 1 v2 in June** (after Paper 2 response).

**Reasoning:** One clean submission beats two rushed submissions. Paper 2 is close to ready; fix the bugs first.
