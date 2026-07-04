# ADR-034: GENE_MASK_LFC Scorer — Deferred to Local Research Package

**Date:** 2026-05-09  
**Status:** DEFERRED  
**Context:** TIER 0 execution — zero-cost improvements  
**Decision:** Defer GENE_MASK_LFC to future work (requires alphagenome_research package)

---

## Context

**Original plan:** Re-score existing HBB predictions with GENE_MASK_LFC scorer (DeepMind official recommendation for gene expression).

**Expected:** Zero-cost improvement (same data, better scoring algorithm).

---

## Investigation Results

### Discovery #1: Two Separate Packages

AlphaGenome ecosystem has **two distinct packages:**

1. **`alphagenome` (Commercial SDK)** — Currently installed ✅
   - Purpose: API client for DeepMind hosted service
   - Function: `client.predict_variant()`
   - Outputs: Mean aggregates (CAGE delta, contact map delta)
   - Scoring: Built-in (DIFF_MEAN equivalent)
   - Hardware: None (cloud API)

2. **`alphagenome_research` (Research Package)** — NOT installed ❌
   - Purpose: Local model inference + advanced scoring
   - Location: https://github.com/google-deepmind/alphagenome_research
   - Scorers: `gene_mask_lfc`, `contact_map`, `splice_junction`, etc.
   - Requirements:
     - Model weights (Kaggle/HuggingFace, ~50GB)
     - H100 GPU (inference)
     - Dependencies: jax, dm-haiku, chex, tensorflow

---

### Discovery #2: Current Predictions Use DIFF_MEAN

**Existing HBB predictions** (`alphagenome_pearl_vs_control.json`):
```json
{
  "cage_delta": -0.008611000142991543,
  "cage_pct": -35.58752913299049
}
```

**Scoring method:** DIFF_MEAN
```python
cage_delta = mean(alt_cage) - mean(ref_cage)
cage_pct = (cage_delta / mean(ref_cage)) * 100
```

**GENE_MASK_LFC would require:**
```python
# Full track data (not just means)
ref_cage_track = [0.024, 0.025, 0.023, ...]  # NOT stored
alt_cage_track = [0.016, 0.018, 0.015, ...]  # NOT stored

# Gene mask (which positions = HBB gene body)
gene_mask = [False, False, True, True, ...]  # NOT available via API

# Log-fold-change at gene-masked positions
lfc = log2((alt_cage[gene_mask] + 1) / (ref_cage[gene_mask] + 1))
score = mean(lfc)
```

**Conclusion:** Cannot re-score existing predictions. Requires **re-prediction** with full track data.

---

## Decision

**DEFER to future work** for the following reasons:

### Blocker #1: Hardware Requirements
- Requires H100 GPU (~$2-3/hour cloud cost OR $30K+ hardware)
- Current setup: CPU-only laptop (NVIDIA RTX 5070 Ti = 4GB VRAM, insufficient)

### Blocker #2: Model Weights Not Downloaded
- Weights: ~50GB download from Kaggle/HuggingFace
- Requires accepting non-commercial research license
- Not needed for API-based workflow

### Blocker #3: Re-Prediction Cost
- Cannot re-score existing predictions (no full track data)
- Would require new API calls: N=32 variants × full tracks ≈ $50-100 USD
- Not zero-cost as originally planned

### Blocker #4: Marginal Benefit
- Current DIFF_MEAN scoring already shows strong signal:
  - HBB: p=2.77e-4, Cohen's d=-1.53 (large effect)
  - TERT hotspots: +33-53% CAGE increase
  - Mechanism specificity: 7/7 loci consistent
- GENE_MASK_LFC **may** improve signal, but existing results already publication-ready

---

## Alternative: Document Current Method

**Instead of re-scoring**, transparently document current scoring method in publications:

```markdown
### CAGE Variant Scoring (Methods)

AlphaGenome CAGE predictions were scored using mean difference method:

$$\Delta \text{CAGE} = \overline{\text{CAGE}_{\text{alt}}} - \overline{\text{CAGE}_{\text{ref}}}$$

where $\overline{\text{CAGE}}$ denotes the mean CAGE signal across the predicted interval.

**Note:** DeepMind recommends GENE_MASK_LFC (gene-masked log-fold-change) for 
enhanced gene-level scoring [1]. This requires the alphagenome_research package 
and was not used in this study due to hardware constraints.

[1] https://github.com/google-deepmind/alphagenome_research
```

---

## Future Work: When to Revisit

**Revisit GENE_MASK_LFC if:**

1. **Hardware access** — H100 GPU available (cloud or institutional)
2. **Stronger signal needed** — Current p=2.77e-4 insufficient for publication
3. **Cross-locus expansion** — Testing ≥5 regulatory loci (justify infrastructure investment)
4. **Local research package installed** — For other reasons (e.g., custom track predictions)

**Priority:** LOW (current results strong enough for preliminary publication)

---

## Impact on 30-Day Plan

**Original TIER 0:**
- ~~P0-A: Re-score HBB with GENE_MASK_LFC (60 min, $0)~~ → **DEFERRED**

**Updated TIER 0:**
- ✅ P0-B: Commit manuscript changes (10 min, $0) → **COMPLETE**
- ✅ P0-C: Create evidence pack (50 min, $0) → **COMPLETE**
- 🔴 P0-D: Document current scoring method (20 min, $0) → **NEW**

**TIER 1 (unchanged):**
- MLH1 variant-level predictions (RNA_SEQ) — 3 days, $10
- MLH1 SPLICE_JUNCTION test — 2 days, $10

**Budget:** $20 USD (unchanged, GENE_MASK_LFC was $0 anyway)

**Score trajectory:** 9.0 → 9.3/10 (skip 9.1 intermediate step)

---

## Lessons Learned

### Lesson 1: API vs Research Package Distinction
DeepMind publishes **two separate packages** for the same model:
- API client (commercial, easy, limited)
- Research package (open, complex, full-featured)

Always check which package a feature belongs to before planning.

### Lesson 2: Zero-Cost != Zero-Effort
"Re-score existing predictions" sounded zero-cost, but:
- Requires full track data (not stored)
- Requires H100 GPU (not available)
- Actual cost: $50-100 USD (re-prediction) + $2-3/hour (GPU)

Verify data requirements before committing to "zero-cost" improvements.

### Lesson 3: Strong Results Don't Need Optimization
Current results:
- p=2.77e-4 (highly significant)
- Cohen's d=-1.53 (large effect)
- 7/7 loci mechanism specificity

GENE_MASK_LFC **may** improve to p=1e-6 or d=-1.7, but:
- Marginal scientific gain
- High technical cost
- Not required for publication

**Optimization trap:** Don't gold-plate results that are already publication-ready.

---

## Recommendation

**ACCEPT current DIFF_MEAN scoring** as sufficient for preliminary publication.

**DOCUMENT method transparently** in Methods section (see Alternative above).

**DEFER GENE_MASK_LFC** to future work (post-publication improvement if needed).

**PROCEED to TIER 1** — MLH1 variant-level strengthening ($10 USD, higher ROI).

---

## Updated Immediate Actions (Today)

~~P0-A: Re-score HBB with GENE_MASK_LFC~~ → **SKIP**

**New P0-D: Document Current Scoring Method** (20 min, $0)
```markdown
1. Update forum_post_alphagenome_validation.md (Methods section)
2. Update ARCHCODE_ALPHAGENOME_MECHANISM_SPECIFICITY_BRIEF.md (scoring note)
3. Create future_work.md (GENE_MASK_LFC listed as enhancement)
```

---

**Version:** 1.0  
**Date:** 2026-05-09  
**Next Review:** After publication (if reviewers request stronger scoring method)

---

_"Zero-cost improvements that require H100 GPU are not zero-cost."_
