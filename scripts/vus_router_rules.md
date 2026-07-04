# VUS Decision Router — Rules (FROZEN BEFORE ANALYSIS)

**Date:** 2026-04-15
**Purpose:** Classify VUS by mechanism using VEP × ARCHCODE 2×2 matrix
**Data:** Unified Atlas CSVs (frozen snapshot)

## Axes

### Axis X: VEP Signal
- **VEP_HIGH**: VEP_Impact in {HIGH, MODERATE} OR VEP_Score > 0.5
- **VEP_LOW**: VEP_Impact in {LOW, MODIFIER} AND VEP_Score <= 0.5
- **VEP_NULL**: VEP_Score = -1 (VEP cannot annotate)

### Axis Y: ARCHCODE Structural Signal
- **ARCH_HIGH**: LSSIM < per-locus threshold (from ADR-017)
- **ARCH_LOW**: LSSIM >= per-locus threshold

### Per-locus thresholds (ADR-017)
- HBB: 0.977
- TERT: 0.968
- TP53: 0.982
- MLH1: 0.972
- BRCA1: 0.985
- CFTR: 0.989
- PTEN: 0.989
- LDLR: 0.996
- GJB2: N/A (no threshold works)
- SCN5A: N/A (tissue mismatch)

## Quadrant → Class mapping

| | ARCH_HIGH (LSSIM < threshold) | ARCH_LOW (LSSIM >= threshold) |
|---|---|---|
| **VEP_HIGH** | Class C (Mixed) | Class A (Activity-only) |
| **VEP_LOW** | **Class B (Architecture — BLIND SPOT)** | Unclassified (no signal) |
| **VEP_NULL** | Class D (Coverage gap) | Unclassified |

## Metrics to compute
1. **Coverage**: % VUS assigned to any class (A, B, C, D) vs unclassified
2. **New interpretations**: count in Class B (VEP blind, ARCHCODE sees)
3. **Enrichment**: enhancer distance in Class B vs rest
4. **Within-category control**: LSSIM difference within same VEP category, matched enhancer distance

## Kill criteria
- Class B empty or < 5 VUS → router adds nothing
- Within-category LSSIM test p > 0.05 → router = category proxy
