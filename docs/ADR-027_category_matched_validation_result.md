# ADR-027: Category-Matched Validation Result — 73bp Cluster WEAK (PARTIAL Validity)

**Date:** 2026-05-08  
**Status:** ACCEPTED  
**Context:** GO/NO-GO GATE 1 (Day 3, 14-day plan)  
**Decision Maker:** Sergey Boyko  

---

## Context

ADR-026 identified HIGH category leakage risk in 73bp HBB promoter cluster:
- 15/20 pearls (75%) = promoter category
- 68.2% of zone = promoter category
- Fisher p=8.5e-25, permutation p=0.0 → но возможна категориальная артефактность

**Hypothesis to test:**
> Category-matched permutation: If enrichment survives category matching, it's positional (not categorical artifact).

**Test protocol:**
Sample random variants matching pearl category distribution (75% promoter, 15% missense, 5% splice_acceptor, 5% frameshift), count how many fall in 73bp zone. Compare to observed (15 pearls in zone).

---

## Problem Discovered

**CRITICAL DATA LIMITATION:**

```
HBB ClinVar dataset (N=1103):
- Promoter category: 15 pearl variants, 0 non-pearl variants
- Missense category: 3 pearl variants, 122 non-pearl variants
- Frameshift category: 1 pearl variant, 98 non-pearl variants
- Splice_acceptor category: 1 pearl variant, sufficient controls
```

**Implication:**
Category-matched test CANNOT sample random promoter variants (pool size = 0). Test can only validate 5/20 pearls (non-promoter categories).

---

## Test Result

**Category-Matched Permutation (10,000 iterations, seed=42):**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Observed in zone | 15/20 pearls | All 15 are promoter category |
| Expected (category-matched) | 0.00 ± 0.00 | Only 5 non-promoter pearls tested, none in zone |
| p-value | 0.0000 | Meaningless comparison (apples vs oranges) |
| Test validity | **PARTIAL** | 15/20 pearls (75%) SKIPPED |
| Insufficient categories | promoter (15 pearls, 0 controls) | — |

**Warning:**
```
Category-matched test is PARTIAL: 1 categories have insufficient controls. 
15/20 pearls skipped. Test valid for remaining 5 pearls only.
```

---

## Interpretation

### What p=0.0 Does NOT Mean

❌ **"Enrichment is positional"** — FALSE  
The p-value compares:
- Numerator: 15 pearls in zone (includes 15 promoter pearls)
- Denominator: 0.00 mean (excludes all promoter pearls)

This is **not a valid comparison**. We're asking: "Do promoter pearls enrich in promoter zone more than random promoter variants?" — but we have ZERO random promoter variants to test against.

### What the Result Actually Means

✅ **"73bp cluster enrichment CANNOT be validated via category matching"**

The test successfully validated 5/20 pearls (non-promoter categories):
- 3 missense pearls: NOT in zone (expected)
- 1 frameshift pearl: NOT in zone (expected)
- 1 splice_acceptor pearl: NOT in zone (expected)

For these 5 pearls, category-matched test passes (no false positives).

**BUT:** The core hypothesis ("73bp promoter cluster") involves 15 promoter pearls, which are UNTESTABLE with this method.

---

## Verdict

**Status:** WEAK  
**Confidence:** LOW  
**Reason:**

> Category-matched test PARTIAL: p-value = 0.0000, but test covers only subset of pearls. Dominant pearl category (promoter) has no non-pearl controls. 73bp promoter cluster enrichment CANNOT be validated via category matching.

---

## Decision

### What We Know (VERIFIED)

1. **Positional enrichment exists** (Fisher p=8.5e-25, permutation p=0.0) [VERIFIED]
2. **Category leakage is HIGH** (75% pearls = promoter, 68% zone = promoter) [VERIFIED]
3. **Category-matched validation is IMPOSSIBLE** for promoter pearls (no controls) [VERIFIED]

### What We Do NOT Know

❓ Is the enrichment driven by:
- (A) Category membership alone (promoter variants cluster in promoter region)?
- (B) Positional signal beyond category (specific 73bp hotspot within promoter)?
- (C) Both?

**Category-matched test was designed to answer this — but dataset lacks the controls needed.**

### Pivot Decision (GO/NO-GO GATE 1)

**Original plan:**
- PASS → proceed with 73bp cluster as validated discovery
- WEAK → proceed with caveats
- FAIL → pivot to ISM scan (no positional claim)

**Actual result:** WEAK (but closer to FAIL for promoter hypothesis)

**Action:** Pivot to **ISM (In Silico Mutagenesis) promoter scan** (Day 8-10)

**Rationale:**
- We cannot claim "73bp positional enrichment" without category-matched validation
- BUT we can claim "AlphaGenome identifies HBB regulatory hotspots" (hotspot = high ISM sensitivity, not positional clustering)
- ISM does NOT require positional enrichment hypothesis — it discovers functional sites via perturbation

---

## ISM Scan Strategy (Pivot Path)

**Hypothesis shift:**
- ❌ OLD: "Pearls cluster in 73bp promoter zone"
- ✅ NEW: "AlphaGenome ISM identifies regulatory-critical positions in HBB promoter"

**Method:**
1. Scan HBB promoter (-200 to TSS) with AlphaGenome ISM (perturb each position A→T, C→G, etc.)
2. Measure CAGE disruption magnitude per position
3. Identify top 10 ISM-sensitive positions (hotspots)
4. Check: Do ClinVar pathogenic variants overlap ISM hotspots?

**Success criteria:**
- Overlap enrichment (Fisher exact test on ISM hotspots vs ClinVar pathogenic)
- NO positional clustering claim (avoid category leakage)
- Claim: "AlphaGenome ISM predicts regulatory impact, validated by ClinVar overlap"

**Honest limitation:**
Still category-confounded (promoter ISM tested on promoter variants), BUT weaker claim:
- ISM = functional perturbation (not positional enrichment)
- Hotspot = high sensitivity (not spatial clustering)

---

## Lessons Learned

### For Future Validations

1. **Check control availability BEFORE designing test**
   - Category-matched test requires balanced controls
   - HBB dataset: promoter variants are ALL pathogenic (evolutionary constraint?)
   - Should have checked `df.groupby('Category')['Pearl'].value_counts()` first

2. **Partial validity ≠ weak evidence**
   - test_validity="PARTIAL" with 75% data skipped → test is NOT APPLICABLE
   - Don't interpret p-value when validity compromised

3. **Category leakage has no statistical fix**
   - If category = biology (promoter variants ARE promoter-localized), no permutation can disentangle
   - Solution: change hypothesis (ISM hotspot vs positional cluster)

### Code Improvement

Added to `validate_73bp_cluster.py`:
- `test_validity` field: "VALID" / "PARTIAL" / "INVALID"
- `insufficient_categories` tracking
- Early return in `generate_verdict()` when validity != "VALID"
- Honest warning message in output

---

## Impact on 14-Day Plan

**Gate 1 Result:** WEAK (partial validity)

**Downstream changes:**

| Day | Original Task | Updated Task (Post-Gate 1) |
|-----|---------------|---------------------------|
| 8-10 | ISM scan OR mechanism analysis | **ISM scan** (no "OR") |
| 11 | Forum post (73bp cluster) | Forum post (ISM hotspot + honest null on 73bp) |
| 13 | ag-falsifier (with 73bp case study) | ag-falsifier (with ISM case study) |
| 14 | 14-day report (73bp validated or not) | 14-day report (category leakage lesson + ISM pivot) |

**Gate 2 (Day 7):** Still relevant — concordance benchmark proceeds regardless of 73bp result.

---

## Artifacts

**Code:**
- `scripts/validate_73bp_cluster.py` (updated with test_validity logic)

**Results:**
- `results/validate_73bp_cluster.json` (test_validity="PARTIAL", warning included)

**Documentation:**
- ADR-026: Original hypothesis + category leakage disclosure
- ADR-027: Category-matched validation result (this document)

---

## Honest Conclusion

**73bp HBB promoter cluster:**
- Positional enrichment: TRUE (Fisher p=8.5e-25)
- Category leakage: HIGH (75% promoter pearls, 68% promoter zone)
- Category-matched validation: IMPOSSIBLE (no non-pearl promoter controls)
- **Final status:** UNVALIDATED (cannot disentangle category from position)

**This is honest null result #5** (after within-category AUC, Bayesian opt, dual-DL, router Class B).

**Next step:** ISM promoter scan (Day 8-10) — functional hotspot discovery, not positional clustering claim.

---

**Version:** 1.0  
**Last Updated:** 2026-05-08  
**Next Review:** After ISM scan (Day 10)
