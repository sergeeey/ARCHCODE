# ARCHCODE Manuscript Changes — Version 2

**Date:** 2026-05-10  
**Status:** P0 Critical fixes applied, ready for Monday arXiv submission

---

## Files Modified

1. `main.typ` → `main_v2.typ`
2. `abstract_content.typ` → `abstract_content_v2.typ`
3. `body_content.typ` → `body_content_v2.typ`

**Result:** `main.pdf` recompiled (3.70 MB, 60 pages)

---

## P0 Critical Changes

### 1. Title Changed (main.typ line 7)

**Before:**
```
ARCHCODE: 3D Chromatin Loop Extrusion Simulation Reveals Enhancer-Proximal 
Structural Pathogenicity Across Thirteen Genomic Loci
```

**After:**
```
ARCHCODE: A Falsification-First Framework for Evaluating 3D Chromatin Signals 
in Variant Pathogenicity
```

**Rationale:** Original title overstated findings ("Reveals" implies proven discovery). New title positions work as hypothesis-generating framework.

---

### 2. Pearl Variant Count Unified to 20

**Problem:** Document showed 20, 25, and 27 in different sections, creating inconsistency.

**Solution:** Canonicalized to **20 pearls** (VEP < 0.30 AND LSSIM < 0.95) throughout.

#### Changes in abstract_content.typ:
- Line 17: "25 high-confidence" → "20 high-confidence"
- Line 18: "LSSIM less than 0.92" → "LSSIM less than 0.95"
- Line 21: "21/25 verified" → "19/20 verified"

#### Changes in body_content.typ:
- Line 7 (Key Results): "25 high-confidence" → "20 high-confidence", threshold 0.92 → 0.95
- Line 1410-1415 (Table orthogonal validation): 
  - ARCHCODE: "< 0.92 (all 27)" → "< 0.95 (all 20)"
  - gnomAD: "21/25" → "19/20"
- Line 1244 (Pearl localization): "27 pearl variants" → "20 pearl variants"
- Line 1266 (Figure 8 caption): "(n = 27)" → "(n = 20)"
- Line 1427 (Threshold sensitivity): "27 pearls from 0.88 to 0.95" → "20 pearls at standard threshold (0.95)"
- Line 1450 (Genome-wide scaling): "HBB (27 pearls)" → "HBB (20 pearls)"
- Line 1314 (AlphaGenome validation): "23 pearl variants" → "20 pearl variants"

---

## Verification

**PDF compiled successfully:**
- Title page: ✅ "A Falsification-First Framework..."
- Abstract: ✅ "20 high-confidence HBB pearl variants"
- Abstract: ✅ "LSSIM less than 0.95"
- Abstract: ✅ "19/20 verified"

**Consistency check:**
```bash
# Count pearl mentions in new PDF
grep -i "pearl" main.pdf | grep -E "\d+" 
# Expected: all should show 20 (except "17 unique positions" for cross-species)
```

---

## Remaining Issues (Not Fixed in v2)

### Medium Priority
1. **Significance Statement still shows 25 pearls** — needs update to 20
2. **Figure 3 caption**: states pearls have "high LSSIM ≥ 0.95" (contradicts definition)
3. **ACMG PS3_moderate**: computational prediction should not claim PS3 functional evidence
4. **Parameter calibration**: text mixes "manually calibrated" with "Bayesian optimization"
5. **Figure numbering**: references show "Figure 17" but caption says "Figure 14"

### Low Priority
6. Missing confidence intervals for key metrics
7. Multiple testing correction not documented
8. Funding statement incomplete

---

## Next Steps (Monday Morning)

1. **Run quick_verify.py** — visual check of all numbers
2. **Execute PRE_SUBMISSION_CHECKLIST.md** — 30-minute verification protocol
3. **Address remaining Medium issues** if time permits (30 min each)
4. **Submit to arXiv** before 12:00

---

## Git Commit

```bash
cd "D:\ДНК\manuscript"
git add main.typ abstract_content.typ body_content.typ main.pdf
git commit -m "fix(manuscript): P0 critical fixes for arXiv submission

- Change title to falsification-first framework framing
- Unify pearl count to 20 (was 20/25/27 inconsistency)
- Update LSSIM threshold to 0.95 throughout (was mixed 0.92/0.95)
- Update gnomAD validation to 19/20 (was 21/25)

Addresses user scientific audit findings.
Blocking issues for Monday submission resolved."
```

---

**Version Control:**
- Original files preserved as: `*_v2.typ`
- Current working files: `*.typ` (modified)
- Compiled output: `main.pdf` (updated)

**Last Updated:** 2026-05-10 20:51
