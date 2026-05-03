# Data Provenance Audit — PyPop HBB Paper

**Audit Date:** 2026-05-03  
**Manuscript:** pypop_paper_HumanMutation_SUBMIT_CLEAN.docx  
**Purpose:** Trace all numerical claims to authoritative sources

---

## Audit Scope

Every number, percentage, and allele frequency in the manuscript must be traceable to:
1. **Primary data file** (CSV/JSON)
2. **Public database** (gnomAD v4)
3. **Literature citation**

No invented, estimated, or "rounded for clarity" values permitted.

---

## Critical Numbers Audit

### 1. Sample Sizes

| Claim (Manuscript) | Source | File | Status |
|-------------------|--------|------|--------|
| **15 HBB promoter variants** | HBB_Unified_Atlas.csv filtered for Category=promoter + Pearl=true | `gnomad_populations_pearls.csv` (17 total - 2 missense) | ✅ VERIFIED |
| **12 variants successfully queried** | gnomAD query success count | Count of non-QUERY_FAILED rows in CSV | ✅ VERIFIED (12/15 = 80%) |
| **3 variants not found** | gnomAD query failures | Count of QUERY_FAILED rows (VCV000869288, VCV000869290, VCV000801184) | ✅ VERIFIED (3/15 = 20%) |
| **807,162 individuals** | gnomAD v4 total cohort | gnomAD documentation (exome + genome) | ✅ VERIFIED |

### 2. Allele Frequencies (VCV000015471 — EAS-enriched)

| Claim | Source | File/Line | Status |
|-------|--------|-----------|--------|
| **AF_EAS = 0.000648** | gnomAD v4 genome (AC=24, AN=37,034) | `gnomad_coverage_check.json` line 6 | ✅ VERIFIED |
| **AC = 24** | gnomAD v4 genome re-query | `gnomad_coverage_check.json` line 5 | ✅ VERIFIED |
| **AN = 37,034** | gnomAD v4 genome re-query | `gnomad_coverage_check.json` line 4 | ✅ VERIFIED |
| **~OLD~ 0.000193** | Superseded preliminary query | `gnomad_populations_pearls.csv` row 5 (DEPRECATED) | ⚠️ STALE (not in manuscript ✅) |

**Calculation check:**  
24 / 37,034 = 0.0006480531... ≈ 0.000648 ✅ MATCHES

### 3. Allele Frequencies (VCV000015466 — EAS-enriched)

| Claim | Source | File/Line | Status |
|-------|--------|-----------|--------|
| **AF_EAS = 0.000464** | gnomAD v4 exome (AC=17, AN=36,610) | `gnomad_coverage_check.json` line 14 | ✅ VERIFIED |
| **AC = 17** | gnomAD v4 exome | `gnomad_populations_summary.json` (max_af_per_population.EAS matches) | ✅ VERIFIED |
| **AN = 36,610** | gnomAD v4 exome | `gnomad_coverage_check.json` line 12 | ✅ VERIFIED |

**Calculation check:**  
17 / 36,610 = 0.0004643540... ≈ 0.000464 ✅ MATCHES

### 4. Cross-Population Summary

| Claim | Source | File/Line | Status |
|-------|--------|-----------|--------|
| **5 strong evidence** (absent in all 5 populations) | Cross-population analysis | `gnomad_populations_summary.json` line 7 | ✅ VERIFIED |
| **7 weak evidence** (absent in ≥3 populations) | Cross-population analysis | `gnomad_populations_summary.json` line 8 | ✅ VERIFIED |
| **0 false pearls** (AF ≥1% in any population) | Cross-population analysis | `gnomad_populations_summary.json` line 9 | ✅ VERIFIED |
| **41.7% strong evidence** | 5/12 × 100% | Calculated from strong_evidence_n / total_pearls_queried | ✅ VERIFIED |

**Calculation check:**  
5 / 12 = 0.4166... ≈ 41.7% ✅ MATCHES

### 5. VEP/CADD Comparison

| Claim | Source | File | Status |
|-------|--------|------|--------|
| **12/12 successfully queried variants classified as MODIFIER** | VEP annotations in HBB_Unified_Atlas.csv matched by ClinVar_ID | Count where VEP_Impact = MODIFIER among successfully queried promoter variants | ✅ VERIFIED |
| **12/12 successfully queried variants with CADD < 20** | CADD scores in HBB_Unified_Atlas.csv matched by ClinVar_ID | Count where CADD_Phred < 20 among successfully queried promoter variants | ✅ VERIFIED |

**Verification result:** 12 successful gnomAD rows matched 12 HBB atlas rows by ClinVar_ID; all 12 have `VEP_Impact = MODIFIER` and all 12 have `CADD_Phred < 20`.

### 6. Population-Specific Enrichment

| Claim | Source | File | Status |
|-------|--------|------|--------|
| **2 variants with East Asian enrichment** | VCV000015471 (AF_EAS=0.000648) + VCV000015466 (AF_EAS=0.000464) | Both AF_EAS > 0.0001 while other populations ≈0 | ✅ VERIFIED |
| **EUR = 0% for both** | Population stratification data | `gnomad_populations_pearls.csv` AF_EUR column | ✅ VERIFIED |

---

## Data File Timeline

| File | Created | Purpose | Authoritative? |
|------|---------|---------|----------------|
| `HBB_Unified_Atlas.csv` | 2026-04-29 | Full HBB variant catalog | Reference only |
| `gnomad_populations_pearls.csv` | **2026-05-01 22:50** | Initial query (17 variants) | ⚠️ STALE for VCV000015471 |
| `gnomad_populations_summary.json` | 2026-05-01 22:50 | Cross-population summary | ✅ CURRENT |
| `gnomad_coverage_check.json` | **2026-05-02 11:35** | Re-query with extended coverage (2 variants) | ✅ **AUTHORITATIVE** |

**Hierarchy:**  
1. **coverage_check.json** (May 2) — most recent, extended coverage
2. **populations_summary.json** (May 1) — derived from CSV
3. **populations_pearls.csv** (May 1) — preliminary, one stale value

**Manuscript sources:**  
- VCV000015471, VCV000015466 AF values: coverage_check.json ✅
- Cross-population counts (5/7/0): populations_summary.json ✅
- Other variants: populations_pearls.csv ✅

---

## Verification Commands

### Count promoter variants in CSV

```bash
awk -F',' 'NR>1 && $5=="promoter"' results/gnomad_populations_pearls.csv | wc -l
# Expected: 15
```

### Count successful queries

```bash
awk -F',' 'NR>1 && $5=="promoter" && $17!="QUERY_FAILED"' results/gnomad_populations_pearls.csv | wc -l
# Expected: 12
```

### Count QUERY_FAILED

```bash
awk -F',' 'NR>1 && $5=="promoter" && $17=="QUERY_FAILED"' results/gnomad_populations_pearls.csv | wc -l
# Expected: 3
```

### Verify VCV000015471 AF calculation

```python
import json
with open('results/gnomad_coverage_check.json') as f:
    data = json.load(f)
    
vcv471 = data[0]
assert vcv471['vcv'] == 'VCV000015471'
assert vcv471['ac_eas'] == 24
assert vcv471['an_eas'] == 37034
calculated_af = 24 / 37034
assert abs(calculated_af - 0.000648) < 0.000001
print(f"✅ VCV000015471 AF verified: {calculated_af:.6f}")
```

### Verify VCV000015466 AF calculation

```python
vcv466 = data[1]
assert vcv466['vcv'] == 'VCV000015466'
assert vcv466['ac_eas'] == 17
assert vcv466['an_eas'] == 36610
calculated_af = 17 / 36610
assert abs(calculated_af - 0.000464) < 0.000001
print(f"✅ VCV000015466 AF verified: {calculated_af:.6f}")
```

---

## Discrepancies Found

### 1. VCV000015471 AF Mismatch (RESOLVED)

**Issue:**  
- CSV (May 1): AF_EAS = 0.000193 (AC=1, AN=152,146)
- coverage_check (May 2): AF_EAS = 0.000648 (AC=24, AN=37,034)

**Resolution:**  
✅ Manuscript uses coverage_check.json value (0.000648)  
✅ CSV not updated but deprecated value NOT cited in manuscript  
✅ Data Availability section lists both files with timestamps

**Risk:** LOW — manuscript is internally consistent, uses authoritative source

### 2. 15 vs 17 Variants (RESOLVED)

**Issue:**  
- CSV contains 17 total variants (15 promoter + 2 missense)
- Manuscript focuses on 15 promoter variants

**Resolution:**  
✅ Manuscript correctly excludes 2 missense variants (above LSSIM threshold)  
✅ Data Availability explicitly states: "15 variants, 2 above LSSIM threshold"

**Risk:** NONE — scientifically justified exclusion, transparently documented

---

## Audit Verdict

**Status:** ✅ **PASS — All critical numbers verified**

**Confidence:**  
- ✅ AF values traceable to gnomAD via coverage_check.json
- ✅ Counts verified against CSV row counts
- ✅ Percentages calculated correctly (41.7% = 5/12)
- ✅ No phantom numbers detected
- ✅ No rounding errors detected

**Remaining verification:** None identified for the numerical claims audited here.

**Recommendation:**  
Proceed with submission package upload after the final human portal metadata check. The only remaining warning is transparent provenance handling for the superseded preliminary CSV value, now documented in the cover letter and `results/README_DATA_NOTES.md`.

---

*Audit completed: 2026-05-03 02:45*  
*Auditor: Data integrity verification agent*  
*Methodology: Source-to-claim tracing*
