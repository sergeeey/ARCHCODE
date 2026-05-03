# SUBMISSION FINAL CHECKLIST — Human Mutation Brief Report

**Paper:** Population Stratification Identifies Epidemiology-Discordant Variants in the HBB Locus: A Validation Framework for Structural Predictions  
**Target Journal:** Human Mutation (Brief Reports, 3000-5000 words)  
**Submission Date:** May 2026  
**Status:** ✅ INTERNALLY CONSISTENT — READY FOR SUBMISSION

---

## Manuscript Files

| File | Path | Size | Status | Notes |
|------|------|------|--------|-------|
| **Main manuscript** | `manuscript/pypop_paper_HumanMutation_SUBMIT_CLEAN.docx` | 44KB | ✅ FINAL | Post-integrity-audit version |
| **Backup (original)** | `manuscript/pypop_paper_HumanMutation_SUBMIT_BACKUP_20260503_023430.docx` | 44KB | ℹ️ ARCHIVE | Pre-fix version |
| **Cover letter** | `manuscript/cover_letter_HumanMutation.docx` | 38KB | ✅ FINAL | Softened claims; includes data provenance note |
| **Repository data notes** | `results/README_DATA_NOTES.md` | - | ✅ FINAL | Explains authoritative AF sources and stale CSV value |

---

## Data Files (Deposited in GitHub + Zenodo)

| File | Path | Purpose | Status |
|------|------|---------|--------|
| **Primary data** | `results/gnomad_populations_pearls.csv` | 17 variants × 20 populations | ⚠️ TRANSPARENT PROVENANCE | Contains one superseded preliminary AF value; see README |
| **Summary JSON** | `results/gnomad_populations_summary.json` | Cross-population analysis | ✅ CURRENT |
| **Coverage check** | `results/gnomad_coverage_check.json` | VCV000015471 & VCV000015466 re-query | ✅ CURRENT (May 2) |
| **Query script** | `scripts/population_filter.py` | Reproducible generic gnomAD query CLI | ✅ CURRENT |
| **Full atlas** | `results/HBB_Unified_Atlas.csv` | Complete HBB variants (reference) | ✅ CURRENT |
| **Data notes** | `results/README_DATA_NOTES.md` | Reviewer-facing provenance note | ✅ CURRENT |

**⚠️ CSV Deprecation Note:**  
`gnomad_populations_pearls.csv` (May 1) contains preliminary query results with **stale AF value** for VCV000015471 (0.000193). Two variants were re-queried with extended coverage on May 2 (`gnomad_coverage_check.json`), yielding updated AF (0.000648). **Manuscript uses updated values** from coverage_check.json.

**Resolution:** Cover letter and `results/README_DATA_NOTES.md` now document this provenance.

---

## Manuscript Metadata

| Field | Value |
|-------|-------|
| **Title** | Population Stratification Identifies Epidemiology-Discordant Variants in the HBB Locus: A Validation Framework for Structural Predictions |
| **Article Type** | Brief Report |
| **Word Count** | 3,239 words (target: 3000-5000) ✅ |
| **Keywords** | population genetics, structural variants, PyPop, beta-thalassemia, regulatory variants, HBB, gnomAD, variant validation |
| **Running Title** | Population Validation of HBB Structural Variants |

---

## Author Information

| Field | Value |
|-------|-------|
| **Author** | Sergey Boyko |
| **ORCID** | 0009-0009-2178-5701 |
| **Email** | sergeikuch80@gmail.com |
| **Affiliation** | Independent Researcher; Ronin Institute for Independent Scholarship 2.0 (application submitted; decision pending) |
| **Corresponding** | Yes |

---

## Required Sections (All Present ✅)

- [x] Abstract (248 words)
- [x] Introduction
- [x] Methods
- [x] Results
- [x] Discussion
- [x] References (Lancaster et al., 2024 cited)
- [x] Data Availability (GitHub + Zenodo DOI)
- [x] Acknowledgments (PyPop developers, gnomAD)
- [x] Conflict of Interest (None declared)
- [x] Funding (None; ARCHCODE disclosed)

---

## Integrity Audit Results

**All 10 critical checks PASSED:**
✅ Deprecated AF (0.000193) removed  
✅ Correct AF (0.000648) present  
✅ PyPop framework usage clarified (methodology-inspired, not software)  
✅ No universal constraint overclaim  
✅ No LSSIM pathogenicity overclaim  
✅ No clinical misclassification claims  
✅ Variant counts consistent (15 total, 12 found, 3 not found)  
✅ Ronin affiliation worded carefully  
✅ ARCHCODE authorship disclosed  
✅ VEP/CADD counts verified against HBB atlas (12/12 MODIFIER; 12/12 CADD <20 among successfully queried variants)  
✅ Formatting preserved (bold/italic intact)

---

## Key Fixes Applied (May 3, 02:34)

| Para | Fix | Reason |
|------|-----|--------|
| 3 | "affiliation pending confirmation" → "application submitted; decision pending" | Avoid premature claim |
| 14 | "PyPop framework" → "PyPop's population stratification approach" | Software not executed |
| 23 | "The PyPop framework" → "PyPop, a population stratification framework" | Clarify inspiration vs usage |
| 34 | "utilized the PyPop framework" → "adapted the PyPop population stratification methodology" | No software claim |

---

## Submission Checklist for Wiley ScholarOne

### Pre-Upload

- [x] Manuscript in .docx format (not .doc)
- [x] Cover letter prepared
- [x] Cover letter updated with CSV deprecation note
- [x] All authors approved final version
- [x] ORCID linked
- [x] No copyright violations
- [x] All figures/tables cited in text
- [x] References formatted per journal style

### Upload Order (ScholarOne)

1. Cover letter (.docx)
2. Main manuscript (.docx) — `pypop_paper_HumanMutation_SUBMIT_CLEAN.docx`
3. Data files (optional upload, or GitHub/Zenodo link in manuscript)
   - `gnomad_populations_pearls.csv`
   - `gnomad_populations_summary.json`
   - `gnomad_coverage_check.json`
   - `README_DATA_NOTES.md`
   - `population_filter.py`

### Article Type Selection

- **Select:** Brief Report
- **NOT:** Full Article, Review, Letter

### Suggested Reviewers (Optional)

**Include if asked:**
1. Alexander K. Lancaster (PyPop author) — alex.lancaster@ronininstitute.org
2. Elphège Nora (3D chromatin, UCSF) — elphege.nora@ucsf.edu
3. Geoff Fudenberg (chromatin structure, USC) — gfudenbe@usc.edu

**Exclude:**
- None (no conflicts)

---

## Post-Submission Actions

### If Accepted

- [ ] Add DOI to Zenodo record (v2.18 update)
- [ ] Update GitHub README with publication link
- [ ] Update ORCID with publication
- [ ] Notify PyPop developers (courtesy, cited their work)

### If Minor Revisions

- [ ] Address reviewer comments
- [ ] Update Data Availability if files requested
- [ ] Re-run integrity checklist before resubmission

### If Major Revisions / Rejection

- [ ] Consider pivot:
  - Option A: Submit to *Genetic Epidemiology* (population genetics focus)
  - Option B: Submit to *European Journal of Human Genetics* (clinical genetics)
  - Option C: Expand to multi-locus and resubmit to *AJHG* (comprehensive study)

---

## Final Pre-Flight Check

- [x] Word count within range (3,239 / 3000-5000) ✅
- [x] No "FIXME", "TODO", "XXX" in manuscript
- [x] All references cited in text
- [x] All figures/tables cited (N/A — no figures)
- [x] Conflict of Interest declared
- [x] Funding declared (None + ARCHCODE disclosure)
- [x] Data Availability complete
- [x] ORCID correct
- [x] Email correct
- [x] No plagiarism (original work)
- [x] No self-plagiarism (first submission of this PyPop analysis)

---

**Status:** ✅ **READY FOR SUBMISSION**  
**Remaining Blockers:** None identified in this pass.  
**Remaining Warnings:** `gnomad_populations_pearls.csv` contains one superseded preliminary AF value, documented in cover letter and `results/README_DATA_NOTES.md`.

**Estimated submission time:** 15 minutes (ScholarOne upload + metadata)

---

*Checklist created: 2026-05-03 02:40*  
*Audit version: Post-integrity-fix*  
*Manuscript version: pypop_paper_HumanMutation_SUBMIT_CLEAN.docx*
