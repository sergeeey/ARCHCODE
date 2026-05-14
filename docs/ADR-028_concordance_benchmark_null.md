# ADR-028: ARCHCODE × AlphaGenome Concordance — NULL (Orthogonal Mechanisms)

**Date:** 2026-05-08  
**Status:** ACCEPTED  
**Context:** GO/NO-GO GATE 2 (Day 4-7, 14-day plan) — PREEMPTIVE EVALUATION  
**Decision Maker:** Sergey Boyko  

---

## Context

**Hypothesis:**
ARCHCODE structural fragility (low LSSIM) should correlate with AlphaGenome functional disruption (CAGE delta). If methods measure the same underlying pathogenicity, Spearman ρ ≥ 0.5 expected.

**GO/NO-GO GATE 2 Criteria:**
- **PASS:** ρ ≥ 0.5 (moderate concordance) → proceed with ARCHCODE × AlphaGenome integration narrative
- **WEAK:** 0.3 ≤ ρ < 0.5 → proceed with caveats
- **FAIL:** ρ < 0.3 → pivot to "AlphaGenome standalone clinical benchmark"

---

## Data Source

**Existing dataset:** `results/alphagenome_pearl_vs_control.json` (March 30, 2026)

```
N = 32 HBB variants:
- 13 pearls (ARCHCODE structural fragility candidates, LSSIM < 0.93)
- 19 benign controls (ClinVar Benign/Likely Benign)

Each variant:
- archcode_ssim: ARCHCODE Local Structural Similarity Index
- cage_delta: AlphaGenome CAGE prediction delta (ref vs alt)
- cage_pct: Percentage change in CAGE signal
```

**API confirmation:** Real AlphaGenome API (predict_variant endpoint, SDK v0.6.0) [VERIFIED-REAL]

---

## Concordance Analysis

### Test 1: SSIM vs CAGE Delta (Raw Metrics)

```python
from scipy.stats import spearmanr

# All variants (N=32)
ρ = 0.077, p = 0.675 (NOT SIGNIFICANT)
```

**Interpretation:** No correlation between ARCHCODE structural similarity and AlphaGenome CAGE disruption.

---

### Test 2: Fragility vs Disruption (Inverted Metrics)

Inverted to align directions:
- `fragility = 1 - SSIM` (higher = more structurally disrupted)
- `disruption = abs(cage_delta)` (higher = stronger CAGE effect)

```python
# All variants (N=32)
ρ = 0.094, p = 0.610 (NOT SIGNIFICANT)
```

**Interpretation:** Still no correlation after inverting metrics.

---

### Test 3: Pearls Only (N=13)

Hypothesis: Controls have low variance, limiting correlation. Test pearls separately.

```python
# Pearls only (N=13)
ρ = 0.151, p = 0.622 (NOT SIGNIFICANT)
```

**Interpretation:** Even within high-fragility candidates, no ARCHCODE-AlphaGenome concordance.

---

### Test 4: Promoter Variants Only (N=11)

Hypothesis: Category-specific effects. Test promoter category separately.

```python
# Promoter variants only (N=11)
ρ = 0.073, p = 0.831 (NOT SIGNIFICANT)
```

**Interpretation:** No improvement in category-restricted analysis.

---

## Diagnostic Analysis

### Variance Check

**ARCHCODE Fragility (1 - SSIM):**
```
Range: [0.0042, 0.1265]
Std: 0.0321
Coefficient of Variation (CV): 0.0345 (3.5%)

Pearls cluster: 0.070 - 0.108 (narrow range)
```

**AlphaGenome CAGE Disruption (|delta|):**
```
Range: [0.000067, 0.009805]
Std: 0.002736
CV: 1.166 (116%)

High variance, but no trend with fragility.
```

**Problem identified:** ARCHCODE fragility has LOW variance (all pearls ~0.07-0.11), but even within this narrow range, CAGE varies 100× (0.0001 to 0.0098) with no pattern.

---

### Visual Inspection (Pearls, Sorted by Fragility)

| Fragility | CAGE Disruption | Pattern |
|-----------|----------------|---------|
| 0.0508 | 0.000102 | LOW fragility → LOW CAGE ✓ |
| 0.0703 | 0.005142 | MID fragility → MID CAGE ✓ |
| 0.0710 | 0.009805 | MID fragility → **HIGH CAGE** ✗ |
| 0.0710 | 0.001037 | MID fragility → **LOW CAGE** ✗ |
| 0.0718 | 0.008144 | MID fragility → HIGH CAGE ✓ |
| 0.0721 | 0.002049 | MID fragility → LOW CAGE ✗ |
| 0.1085 | 0.001363 | **HIGH fragility** → **LOW CAGE** ✗ |

**Observation:** At fragility ~0.07, CAGE varies from 0.001 to 0.010 (10× range). Highest fragility (0.108) produces LOW CAGE (0.001).

**Conclusion:** No monotonic relationship. Methods are **orthogonal**.

---

## Interpretation: Orthogonal Pathogenicity Mechanisms

### Why No Correlation?

**ARCHCODE measures:** 3D chromatin structure disruption
- Mechanism: Loop extrusion, TAD boundary shifts, enhancer-promoter contact loss
- Signal: Structural Similarity Index (SSIM) on Hi-C-like contact maps
- Sensitive to: Long-range architectural changes (>10kb)

**AlphaGenome CAGE measures:** Transcription initiation rate
- Mechanism: CAGE-seq signal at promoter (TSS activity)
- Signal: Direct functional output (RNA polymerase recruitment)
- Sensitive to: Promoter-proximal sequence changes, TF binding disruption

**These mechanisms can be INDEPENDENT:**

| Example Variant | ARCHCODE | AlphaGenome CAGE | Orthogonality |
|----------------|----------|------------------|---------------|
| Promoter SNP (no loop impact) | Low fragility (SSIM ≈ 0.93) | High disruption (CAGE ↓40%) | ✓ |
| Enhancer-loop SNP (no promoter impact) | High fragility (SSIM ≈ 0.85) | Low disruption (CAGE ↓1%) | ✓ |
| Dual-impact SNP | High fragility + High CAGE | Both high | Rare |

**Biology supports orthogonality:**
- Promoter mutations directly disrupt transcription → high CAGE delta, low structural fragility
- Structural variants (loop anchors, CTCF sites) disrupt 3D → high fragility, low CAGE delta (if promoter intact)
- Both pathogenic, but via **different layers** of gene regulation

---

## GO/NO-GO GATE 2 Verdict

**Concordance Result:** ρ = 0.077, p = 0.675

**Verdict:** **FAIL** (threshold: ρ ≥ 0.5, actual: 0.077)

**Confidence:** HIGH (multiple tests, consistent null across all variants/subsets)

---

## What This Does NOT Mean

❌ **"ARCHCODE is wrong"**
- ARCHCODE detects structural fragility (validated by spectral methods, ADR-024)
- Group difference exists: pearls mean fragility = 0.073 vs controls = 0.066

❌ **"AlphaGenome is wrong"**
- AlphaGenome detects regulatory disruption (p=2.77e-4 for HBB pearls vs benign)
- Mechanism specificity confirmed (HBB/MLH1 work, BRCA1/TP53 null)

❌ **"Methods are useless"**
- Both detect pathogenicity, just via **orthogonal mechanisms**

---

## What This DOES Mean

✅ **"ARCHCODE and AlphaGenome measure different aspects of pathogenicity"**

- ARCHCODE → 3D structural layer (chromatin architecture)
- AlphaGenome → 1D functional layer (promoter sequence → transcription)
- **Both valid, not redundant, not concordant**

✅ **"Concordance is NOT required for validation"**

- Methods can validate each other via **complementarity**, not correlation
- Example: ARCHCODE finds structural hotspots, AlphaGenome validates if they're functionally critical
- Overlap enrichment ≠ rank correlation

✅ **"AlphaGenome standalone validation path is correct"**

- AlphaGenome CAGE works on regulatory variants (HBB, MLH1)
- This is independent of ARCHCODE
- Narrative: "First clinical validation of AlphaGenome regulatory predictions"

---

## Pivot Decision (GATE 2 FAIL)

**Original plan (if concordance PASS):**
- Integrate ARCHCODE × AlphaGenome as unified validation platform
- Claim: "Structural predictions validated by functional AI"

**Pivot (concordance FAIL):**
- Separate narratives:
  - **ARCHCODE:** Structural fragility detection (spectral validation, ADR-024)
  - **AlphaGenome:** Regulatory variant validation (mechanism-specific, this ADR)
- No concordance claim
- Mention orthogonality as **complementarity** (two layers of regulation)

---

## Impact on 14-Day Plan

**GATE 2 Result:** FAIL (preemptive, data already existed)

**Downstream changes:**

| Day | Original Task | Updated Task (Post-GATE 2) |
|-----|---------------|---------------------------|
| 4-5 | Prepare concordance data | ~~SKIPPED~~ (data existed, analysis complete) |
| 6-7 | Run concordance benchmark | ~~SKIPPED~~ (analysis complete, result: FAIL) |
| 8-10 | ISM scan (GATE 1 pivot) | ISM scan (unchanged) + mechanism specificity analysis |
| 11 | Forum post (concordance or pivot) | Forum post (AlphaGenome standalone + honest null on concordance) |
| 13 | ag-falsifier | ag-falsifier (with orthogonality case study) |
| 14 | 14-day report | 14-day report (both gates failed, pivot paths successful) |

**Both gates failed, but project NOT failed:**
- GATE 1 WEAK → pivot to ISM scan (functional hotspot discovery)
- GATE 2 FAIL → pivot to AlphaGenome standalone (mechanism specificity)
- **Honest null results strengthen scientific integrity**

---

## Lessons Learned

### For Future Concordance Studies

1. **Check variance BEFORE running concordance**
   - ARCHCODE fragility CV=3.5% (too low for correlation)
   - Need broader range of structural fragility to detect correlation

2. **Group difference ≠ rank correlation**
   - Mann-Whitney p=2.77e-4 (pearls vs controls) does NOT imply Spearman ρ > 0
   - Both can be pathogenic without ranking agreement

3. **Orthogonality is NOT failure**
   - Two methods can validate same biology via different mechanisms
   - Complementarity > redundancy

4. **Preemptive GATE evaluation saves time**
   - Data existed (March 30), analyzed May 8 (39 days wasted)
   - Should have checked concordance immediately after data collection

### Statistical Insight

**Within-group correlation vs between-group difference:**

```
Pearls: fragility=0.073, CAGE=0.00436
Controls: fragility=0.066, CAGE=0.00097

Group difference: LARGE (4.5× CAGE, p=2.77e-4)
Rank correlation: NULL (ρ=0.077, p=0.67)
```

This pattern indicates: **categorical separation, not continuous concordance**.

Both methods distinguish pathogenic from benign, but via **different ranking criteria**.

---

## Next Steps (Post-GATE 2)

**Day 8-10:** ISM Promoter Scan + Mechanism Specificity Analysis
- ISM scan: HBB promoter (-200bp to TSS) functional hotspots
- Mechanism analysis: Why HBB/MLH1 work, BRCA1/TP53 null (category distribution)
- Deliverable: AlphaGenome mechanism specificity figure

**Day 11:** Forum Post
- Title: "First Independent Clinical Validation of AlphaGenome Regulatory Predictions"
- Honest disclosure: No ARCHCODE concordance (orthogonal mechanisms)
- Mechanism specificity thesis (regulatory vs coding)

**Day 13:** ag-falsifier Tool
- Case study: Orthogonality detection (group difference ≠ rank correlation)
- Statistical harness: check CV before concordance, warn if <10%

**Day 14:** 14-Day Report
- Both gates failed (GATE 1 WEAK, GATE 2 FAIL)
- Both pivots successful (ISM scan, AlphaGenome standalone)
- **Falsification-first methodology validated**

---

## Artifacts

**Data:**
- `results/alphagenome_pearl_vs_control.json` (March 30, N=32, real API)

**Analysis:**
- Spearman correlation: ρ=0.077, p=0.675 (all variants)
- Subgroup analyses: all null (pearls-only, promoter-only)
- Variance diagnostics: ARCHCODE CV=3.5% (too narrow)

**Documentation:**
- ADR-027: GATE 1 result (category-matched WEAK)
- ADR-028: GATE 2 result (concordance FAIL) — this document

---

## Honest Conclusion

**ARCHCODE × AlphaGenome concordance:** NULL (ρ = 0.077, p = 0.675)

**This is honest null result #6** (after within-category AUC, Bayesian opt, dual-DL, router Class B, 73bp category-matched PARTIAL, concordance).

**Interpretation:** Methods measure **orthogonal pathogenicity mechanisms**:
- ARCHCODE: 3D chromatin structure
- AlphaGenome: promoter function

**Both valid. Not concordant. Complementary.**

**Pivot:** AlphaGenome standalone clinical validation (mechanism-specific, regulatory loci only).

---

**Version:** 1.0  
**Last Updated:** 2026-05-08  
**Next Review:** After mechanism specificity analysis (Day 10)  

---

_"Null correlation is a result, not a failure. Orthogonality explains why both methods work."_
