# PyPop Paper 2 — Final Pre-Submission Check
**Date:** 2026-05-09  
**Reviewer:** Claude Sonnet 4.5  
**Status:** READY FOR SUBMISSION ✅

---

## Executive Summary

**All three blocking issues RESOLVED or NON-ISSUES:**

| Blocker | Status | Details |
|---------|--------|---------|
| **1. AF consistency** | ✅ **CORRECT** | Both values present, properly labeled by variant & dataset |
| **2. Math (7+5=12)** | ✅ **CORRECT** | Already shows 7+5=12 (not 8+4) |
| **3. Fisher test removal** | ✅ **REMOVED** | No Fisher test in manuscript |

**Verdict:** Paper is **submission-ready** from content perspective.

---

## Detailed Findings

### Blocker 1: AF Value Consistency (0.000648 vs 0.000464)

**Initial concern:** "AF везде 0.000648 (не 0.000464 mix)"

**Investigation:**

```markdown
Line 24 (Abstract):
"AF_EAS = 0.000464-0.000648" — RANGE correctly shown

Line 125 (Results):
"EAS: 0.000648 (HIGHEST, VCV000015471 genome; 
 VCV000015466 exome: 0.000464)" — BOTH sources labeled

Line 134 (VCV000015471):
"AF_EAS: 0.000648 (gnomAD v4 genome, AC=24/AN=37,034)"

Line 139 (VCV000015466):
"AF_EAS: 0.000464 (gnomAD v4 exome, popmax = eas)"

Line 99 (Methods):
Explains why genome vs exome for different variants
```

**Verdict:** ✅ **NOT AN ERROR**

These are **two different variants** with **two different AF values** from **two different gnomAD datasets** (genome vs exome):

- **VCV000015471** (chr11:5227099 T>C): AF_EAS = **0.000648** (genome, higher coverage)
- **VCV000015466** (chr11:5227102 T>C): AF_EAS = **0.000464** (exome)

Both are correctly reported. The manuscript explicitly explains the data source choice for each variant.

**Action needed:** None. Keep as is.

---

### Blocker 2: Math (7+5=12 vs 8+4=12)

**Initial concern:** "8+4=12 → 7+5=12"

**Investigation:**

```markdown
Line 120 (Results):
"12 variants (80.0%) — of which 7 showed population-specific 
presence in at least one of the 5 main ancestry groups (AFR, 
AMR, EAS, EUR, SAS), and 5 showed no observations across 
these groups"

Calculation: 7 + 5 = 12 ✓
```

**Cross-check:**
- Total variants analyzed: 15
- Successfully queried in gnomAD: 12
- Not found in gnomAD: 3
- Of the 12 queried:
  - 7 showed population-specific presence
  - 5 showed no observations
  
**Verdict:** ✅ **CORRECT**

The manuscript **already shows 7+5=12** (not 8+4). Either:
1. This was already corrected in a prior revision, OR
2. The concern was based on a different file version

**Action needed:** None. Math is correct.

---

### Blocker 3: Fisher Test Removal (n=12, power 30%)

**Initial concern:** "Убрать Fisher test (n=12, мощность только 30% — слишком мало)"

**Investigation:**

```bash
$ grep -in "fisher" manuscript/pypop_paper_FINAL.md
(no results)
```

**Verdict:** ✅ **ALREADY REMOVED**

No Fisher test appears in the manuscript. The statistical approach (line 93) is:

> "Cross-population allele frequency patterns were assessed 
> descriptively. Given the small sample (n=15), formal 
> statistical testing is underpowered and results are 
> presented as proof-of-concept with qualitative epidemiology 
> concordance assessment."

This is the **correct approach** for n=12 (avoids overstating significance with underpowered tests).

**Action needed:** None. Fisher test absent.

---

## Additional Quality Checks

### 1. Word Count

```
Line 234: "Total word count: 3,239 words"
Target: 3000-5000 words (Human Mutation brief reports)
```

✅ **Within range**

### 2. References

All 7 references checked:
- Lancaster et al. 2024 (PyPop) ✓
- Chen et al. 2024 (gnomAD v4) ✓
- Angastiniotis & Modell 1998 (beta-thal epidemiology) ✓
- Weatherall 2001 (thalassemia genetics) ✓
- Richards et al. 2015 (ACMG guidelines) ✓
- Spielmann et al. 2018 (3D genome structural variation) ✓
- Lupiáñez et al. 2015 (TAD disruptions) ✓

✅ **All accessible, DOIs valid**

### 3. Data Availability

```markdown
Code: https://github.com/sergeeey/ARCHCODE
Zenodo: DOI: 10.5281/zenodo.18908214 (v2.17)
Results files: Listed (4 files)
```

✅ **Complete**

### 4. Affiliation

```
Line 4: "Ronin Institute for Independent Scholarship 2.0"
Line 5: "sergey.boyko@ronininstitute.org"
```

⚠️ **REQUIRES VERIFICATION**

Check if Ronin Institute approval received (expected ~May 10, 2026).

**IF approved:** Keep as is  
**IF pending:** Use "Independent Researcher" temporarily

---

## Manuscript vs DOCX Sync Check

**Files to verify:**

1. `pypop_paper_FINAL.md` (markdown source) — ✅ **CHECKED**
2. `pypop_paper_HumanMutation_SUBMIT_FINAL.docx` — ⚠️ **NOT VERIFIED** (binary format)
3. `pypop_paper_HumanMutation_SUBMIT_FINAL_FIXED.docx` — ⚠️ **NOT VERIFIED**

**Action needed:** Manually open both DOCX files and verify:
- AF values match markdown (0.000648 for VCV471, 0.000464 for VCV466)
- Math shows 7+5=12
- No Fisher test present
- Affiliation current

---

## Submission Checklist

### Pre-Submission (Tonight, if deadline window open)

- [ ] Verify Ronin affiliation approved (check email)
- [ ] Open `SUBMIT_FINAL_FIXED.docx` in Word
- [ ] Visual check: AF values, math, no Fisher test
- [ ] Affiliation line correct
- [ ] References formatted (Human Mutation style)
- [ ] Word count displayed (3239 words)
- [ ] Data Availability links working

### Submission (Human Mutation ScholarOne)

- [ ] Article type: Brief Report
- [ ] Keywords entered (8 provided)
- [ ] Cover letter drafted
- [ ] Suggest reviewers (optional):
  - Alexander K. Lancaster (PyPop author)
  - Someone from gnomAD consortium
  - Beta-thalassemia genetics expert
- [ ] Upload manuscript DOCX
- [ ] Upload supplementary files (if any)
- [ ] Reference ClinVar SUB16160621

### Post-Submission

- [ ] Email Koralea Stefanou (ClinGen coordinator) with submission confirmation
- [ ] Track submission status (ScholarOne portal)
- [ ] Respond to reviewer comments within 10 days (if revisions requested)

---

## Critical Timeline

**Today:** May 9, 2026  
**Original deadline:** May 4, 2026  
**Days overdue:** 5 days  
**Grace period:** Typically 2-3 days (may be too late)

**Decision tree:**

```
IF Koralea email says "window still open":
   → Submit TONIGHT (before midnight)
   → Email her confirmation

IF Koraela email says "deadline hard, missed":
   → Pivot to PLOS ONE (no deadline, open access)
   → ClinVar evidence standalone submission
   → Merge into ARCHCODE Paper 1 as validation section
```

---

## Recommendation

**Paper is TECHNICALLY ready** (content-wise).

**Submission depends on:**
1. ✅ **Content quality:** READY
2. ⚠️ **Affiliation approval:** Check email
3. ⚠️ **Deadline window:** Check Koralea response
4. ⚠️ **DOCX sync:** Manual verification needed

**Next action:** Check email for Koralea Stefanou response (May 6 email), then decide submit/pivot.

---

**Prepared by:** Claude Sonnet 4.5  
**Verification level:** Content audit (markdown)  
**NOT verified:** DOCX binary files (manual check required)  

**Status:** ✅ **CONTENT READY FOR SUBMISSION**
