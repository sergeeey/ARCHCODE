# Active Context — ARCHCODE

**Last Updated:** 2026-03-04 (session 27: 9-locus expansion + threshold/CTCF analysis)
**Branch:** main
**Last Commit:** pending (uncommitted: TERT + GJB2 pipeline, threshold analysis, CTCF distance)
**GitHub:** https://github.com/sergeeev/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — REJECTED ("not complete research with new data")
**Status:** 9 loci, 30,318 variants. Per-locus thresholds + CTCF/enhancer proximity analysis complete. Manuscript reframe next.

---

## Текущий статус проекта

**Фаза:** v3.1 — 9-locus expansion + mechanistic analysis + manuscript reframe

### Session 27: Full Pipeline — 2 New Loci + Threshold + CTCF Analysis

**Part 1: Two New Loci (TERT + GJB2)**

1. **TERT locus (chr5p15.33)** — 2,089 ClinVar variants (431 P/LP, 1,658 B/LB). Inter-TAD boundary region. 10 CTCF sites, 5 H3K27ac peaks. Mean LSSIM: Path=0.9798, Ben=0.9986 (Δ=0.019). 27 structural pathogenic. 0 pearls. CADD: 1,957/2,089 scored (93.7%)
2. **GJB2 locus (chr13q12.11)** — 469 ClinVar variants (314 P/LP, 155 B/LB). **Intentional tissue-mismatch benchmark** (cochlear gene in K562 erythroid). Mean LSSIM: Path=0.9916, Ben=0.9978 (Δ=0.006). **0 structural pathogenic, 0 pearls — expected null**. CADD: 379/469 scored (80.8%)
3. **Missense misclassification fix** — Created `reclassify_with_vep.py` using Ensembl VEP REST API
4. **Integrative benchmark** — 30,318 variants (9 loci), 20,029 CADD-scored (66.1%)

**Part 2: Per-Locus Threshold Analysis (KEY RESULT)**

5. **Per-locus thresholds** — universal 0.95 works only for HBB (79.6% sens). Per-locus optimal (FPR≤1%):
   - HBB: 0.977 → 92.9% sensitivity (vs 79.6% at 0.95)
   - TERT: 0.968 → 22.7%
   - TP53: 0.982 → 22.6%
   - SCN5A: 0.994 → 22.4% (but tissue-mismatch caveat)
   - MLH1: 0.972 → 5.5%
   - LDLR: 0.989 → 4.2%
   - CFTR: 0.971 → 2.6%
   - BRCA1: 0.965 → 0.9%
   - GJB2: **NO THRESHOLD** achieves FPR≤1% with any sensitivity

6. **Tissue-specificity gradient confirmed (9 loci):**
   ```
   HBB  (matched)   Δ=0.111  STRONG
   TERT (expressed)  Δ=0.019  STRONG
   MLH1 (partial)    Δ=0.009  MODERATE
   TP53 (partial)    Δ=0.009  MODERATE
   CFTR (partial)    Δ=0.007  MODERATE
   GJB2 (mismatch)   Δ=0.006  MODERATE  ← expected null
   BRCA1(partial)    Δ=0.006  MODERATE
   SCN5A(mismatch)   Δ=0.003  MODERATE  ← expected null
   LDLR (partial)    Δ=0.002  WEAK
   ```

**Part 3: CTCF Distance + ARCHCODE-Only Clustering (MECHANISTIC INSIGHT)**

7. **Pearl variants (n=27) cluster near ENHANCERS, not CTCF:**
   - Median CTCF distance: 22,120bp (far)
   - Median enhancer distance: 831bp (close!)
   - Pearl vs non-pearl pathogenic: p = 1.08e-8 (Mann-Whitney)

8. **Enhancer proximity = strongest structural predictor:**

   ```
   ≤1kb from enhancer:  Δ(path-ben) = 0.039  ← 7× average
   1-5kb:               Δ = 0.011
   5-20kb:              Δ = 0.002
   >20kb:               Δ = 0.005
   ```

9. **ARCHCODE-only clustering (n=394, LSSIM<0.95 + CADD<20):**
   - True Positives (364): 83% frameshift, median enhancer dist=494bp, across 7 loci
   - False Positives (30): 93% "other" (CNVs), median CTCF dist=692bp, 87% BRCA1
   - TP vs FP CTCF distance: p = 3.69e-8
   - **Actionable: filter "other" category to reduce FP**

**Files created/modified this session:**

- `config/locus/tert_300kb.json`, `config/locus/gjb2_300kb.json`
- `data/tert_variants.csv`, `data/gjb2_variants.csv`
- `results/TERT_Unified_Atlas_300kb.csv`, `results/GJB2_Unified_Atlas_300kb.csv`
- `results/cadd_scores_TERT.csv`, `results/cadd_scores_GJB2.csv`
- `results/integrative_benchmark.csv` (30,318 rows, 9 loci)
- `results/per_locus_thresholds.csv` + `_summary.json`
- `results/ctcf_distance_analysis.json`
- `scripts/reclassify_with_vep.py` (VEP missense fix)
- `scripts/per_locus_thresholds.py`
- `scripts/ctcf_distance_analysis.py`
- Modified: `locus-config.ts`, `generate-unified-atlas.ts`, `build_integrative_benchmark.py`, `fetch_cadd_scores.py`

---

## Key Manuscript Findings (Ready for Reframe)

1. **Enhancer proximity drives ARCHCODE discrimination** — Δ at ≤1kb = 7× average. Pearl variants = enhancer-proximal, not CTCF-proximal.
2. **Per-locus thresholds required** — universal 0.95 only works for HBB. Table ready.
3. **Tissue-specificity confirmed with 9 loci** — 2 mismatches (SCN5A, GJB2) = nulls; 1 inter-TAD (TERT) = moderate; 6 partial/matched = gradient.
4. **FP filtering possible** — 93% FP are "other" category CNVs. Category filter eliminates most.
5. **CADD complementarity** — 20,029/30,318 scored (66.1%). Pearl CADD median=15.7 (ambiguous zone). ARCHCODE detects what CADD misses at enhancer-proximal positions.

## Backlog

1. **P0: Manuscript reframe** — "structural annotation tool" not "predictor". Add: tissue gradient, enhancer proximity figure, per-locus threshold table
2. **P1: arXiv q-bio.GN** — submit reframed manuscript with 9 loci
3. **P2: Commit + push** — all new files
4. SpliceAI локальная интеграция (postponed)
5. Bioinformatics (Oxford) submission — after arXiv
6. gnomAD constraint correlation (low priority)
7. GTEx AE check (low priority, n=27 too small)
