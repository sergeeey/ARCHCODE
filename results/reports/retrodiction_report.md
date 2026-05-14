# ARCHCODE Retrodiction Suite — Results

**Date:** 2026-05-14 19:37:53
**Tests:** 1/4 passed
**Assertions:** 4/4 passed

---

## Summary

| Test | Status | Assertions | Details |
|------|--------|------------|---------|
| RETRO-01: HBB 73bp Cluster Regulatory | ✅ PASS | 4/4 |  |
| RETRO-02: MLH1 Promoter Regulatory | ❌ FAIL | 0/0 |  (Error: No validation results found for MLH1) |
| RETRO-03: TERT Hotspots Gain-of-Function | ❌ FAIL | 0/0 |  (Error: TERT hotspot variants not found in database) |
| RETRO-04: GJB2 Coding NULL (Orthogonal) | ❌ FAIL | 0/0 |  (Error: No validation results found for GJB2) |

---

## Detailed Results

### RETRO-01: HBB 73bp Cluster Regulatory

**Status:** ✅ PASS

**Metrics:**
- `alphagenome_p_value`: 0.000270
- `archcode_p_value`: 0.210000
- `spearman_rho`: 0.069000
- `alphagenome_p`: 0.000270
- `archcode_p`: 0.210000
- `classification`: WEAK-ORTHOGONAL
- `locus`: HBB

**Assertions:**
1. ✅ **AlphaGenome detects regulatory variants (p < 0.05)**
   - Mann-Whitney p-value: 0.000270 (threshold: 0.05)
   - Metric: `alphagenome_p_value` = 0.000270
2. ✅ **ARCHCODE weak on category-selected dataset (p > 0.05)**
   - Mann-Whitney p-value: 0.210000 (expected >0.05 due to category selection bias)
   - Metric: `archcode_p_value` = 0.210000
3. ✅ **Low correlation confirms orthogonality (|ρ| < 0.3)**
   - Spearman ρ: 0.069 (WEAK-ORTHOGONAL classification)
   - Metric: `spearman_rho` = 0.069000
4. ✅ **Classification = WEAK-ORTHOGONAL (one method strong)**
   - Classification: WEAK-ORTHOGONAL (AlphaGenome strong, ARCHCODE weak)

---

### RETRO-02: MLH1 Promoter Regulatory

**Status:** ❌ FAIL

**Error:** No validation results found for MLH1

### RETRO-03: TERT Hotspots Gain-of-Function

**Status:** ❌ FAIL

**Error:** TERT hotspot variants not found in database

### RETRO-04: GJB2 Coding NULL (Orthogonal)

**Status:** ❌ FAIL

**Error:** No validation results found for GJB2
