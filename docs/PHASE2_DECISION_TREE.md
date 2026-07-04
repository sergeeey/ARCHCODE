# Phase 2 Decision Tree — Autonomous Research Mode

**Status:** Awaiting Phase 1 results (REAL Nucleotide Transformer)  
**ETA:** 2026-05-08 (running now)

---

## Decision Tree (4 исхода)

```
                    REAL NT Results
                          |
        +-----------------+-----------------+
        |                                   |
    p < 0.05                            p >= 0.05
    (significant)                       (NOT significant)
        |                                   |
        |                                   |
   +----+----+                         NULL RESULT
   |         |                              |
AUC>0.60  AUC≤0.60                   → PIVOT: Pathway 3
   |         |                           (Computational
STRONG   MARGINAL                        Closed-Loop)
   |         |
   |    +----|----+
   |    |         |
   |  within   category
   |  -cat OK   artifact
   |    |         |
   |    v         v
   | EXPAND    DOCUMENT
   |  Phase2    as honest
   |           null
   v
EXPAND
Phase2
```

---

## Outcome 1: STRONG (p<0.05 + AUC>0.60 + within-category OK)

**Interpretation:** Foundation model learned embeddings improve discrimination  
**Confidence:** HIGH  
**Action:** Expand to full dataset

### Phase 2.1: Full HBB (1,103 variants)
```bash
python scripts/nucleotide_transformer_full_hbb.py
```

**Tasks:**
- [ ] Load all HBB variants (not just 27 pearls)
- [ ] Compute embeddings for all (ETA ~2 hours on CPU, ~20 min on Colab GPU)
- [ ] Within-category AUC per category (missense, promoter, frameshift, splice)
- [ ] Compare to categorical baseline (Table)

**Success criteria:**
- Within-category median AUC > 0.55 (improvement over 0.52 baseline)
- At least 2/4 categories show p<0.05

### Phase 2.2: Cross-locus validation (BRCA1, TP53)

**If HBB successful:**
```bash
python scripts/nucleotide_transformer_cross_locus.py --loci BRCA1,TP53
```

**Tasks:**
- [ ] BRCA1 (10,682 variants): pathogenic vs benign, 23+23 sample
- [ ] TP53 (2,794 variants): pathogenic vs benign, 23+23 sample
- [ ] Cross-locus transfer: train on HBB, test on BRCA1/TP53

**Success criteria:**
- At least 1/2 loci replicate HBB signal (p<0.05)

### Phase 2.3: Integration into ARCHCODE pipeline

**If cross-locus successful:**
- [ ] Replace `effectStrength` dictionary with learned embeddings
- [ ] Update `ContactMatrixSimulator.ts` to call Python embedding service
- [ ] Re-run 30-test validation suite
- [ ] Update manuscript: Results section, ADR

**Manuscript changes:**
- New subsection: "Learned embeddings vs hand-crafted features"
- Figure: within-category AUC heatmap (9 loci × 4 categories)
- Table: MOCK vs categorical vs REAL comparison

---

## Outcome 2: MARGINAL (p<0.05 but AUC≤0.60 or category artifact)

**Interpretation:** Statistical significance, but weak effect or confounded  
**Confidence:** MEDIUM  
**Action:** Document as honest null + inspect high-delta variants

### Tasks:
- [ ] Run falsification checks (matched control, skeptic triggers)
- [ ] Identify variants with highest embedding delta
- [ ] Manual inspection: are high-delta variants biologically interesting?
- [ ] ADR: "Nucleotide Transformer shows marginal improvement, insufficient for integration"

### Pivot options:
- Try different embedding strategy (CLS token instead of mean pooling)
- Try different model (DNABERT-2, Enformer)
- Proceed to Pathway 3 (Computational Closed-Loop)

---

## Outcome 3: NULL RESULT (p≥0.05)

**Interpretation:** Foundation model embeddings не лучше edit distance  
**Confidence:** HIGH (honest null)  
**Action:** Document + PIVOT to Pathway 3

### ADR Entry:
```markdown
## ADR-XXX: Nucleotide Transformer null result (2026-05-08)

**Context:** Tested InstaDeepAI NT v2-100m on HBB 27 pearls vs 27 benign

**Result:**
- MOCK (edit distance): AUC=0.482, p=0.648
- REAL (learned embeddings): AUC=X.XXX, p=X.XXX
- Delta AUC: +X.XXX (not significant)

**Decision:** Foundation model does NOT improve within-category discrimination

**Reasoning:**
- Nucleotide Transformer trained on genome-wide tasks (promoter prediction, enhancer identification)
- Regulatory variant discrimination требует более специфичного training signal
- 256bp window может быть too short for context (NT trained on 6kb)

**Next:** Pivot to Pathway 3 (Computational Closed-Loop)
```

---

## Outcome 4: VALIDATION THEATER (skeptic triggers fired)

**Interpretation:** Suspicious результаты требуют дополнительной проверки  
**Confidence:** LOW  
**Action:** Deep dive + additional controls

### Skeptic Triggers:
- AUC > 0.95 + p < 0.001 (слишком perfect)
- Round numbers (AUC = 1.000)
- Within-category всё significant (zero failures)

### Additional checks:
- [ ] Data leakage test: пересечение pearls и benign training data?
- [ ] Sequence similarity: pearls vs benign edit distance distribution
- [ ] Manual review: инспектировать top 5 highest-delta variants
- [ ] Independent validation: другой seed (seed=123 instead of 42)

---

## Pathway 3: Computational Closed-Loop (альтернатива если NT fails)

**Concept:** Ginkgo-style closed-loop, но без wet-lab

### Architecture:
```
ARCHCODE (detect pearls)
    ↓
AlphaGenome ISM (in-silico validation)
    ↓
Claude Opus (hypothesis generation)
    ↓
New pearl cluster / mechanism
    ↓
ARCHCODE (test new hypothesis)
    ↓ (loop)
```

### Phase 3.1: Setup
```bash
python scripts/computational_closed_loop.py \
  --locus HBB \
  --initial-pearls results/hbb_pearls.csv \
  --iterations 3
```

**Tasks:**
- [ ] ARCHCODE → 27 pearls
- [ ] AlphaGenome ISM → CAGE/ATAC delta for each
- [ ] Claude API → interpret results, generate next hypothesis
- [ ] ARCHCODE → test hypothesis on nearby variants

**Success criteria:**
- At least 1 new pearl discovered per iteration
- Hypothesis refinement: iteration 3 more specific than iteration 1

### Phase 3.2: Metrics
- Discovery rate: new pearls / iteration
- Hypothesis quality: specificity, testability
- Cycle time: hours per iteration (vs weeks manual)

---

## Timeline (optimistic)

| Phase | Task | Duration | ETA |
|-------|------|----------|-----|
| 1.1 | REAL NT pilot (47 variants) | 5 min | 2026-05-08 now |
| 1.2 | Falsification checks | 5 min | +10 min |
| 1.3 | Decision (which outcome?) | 2 min | +12 min |
| **IF STRONG:** |
| 2.1 | Full HBB (1,103 variants) | 2 hours CPU | +2h 12min |
| 2.2 | Cross-locus (BRCA1, TP53) | 4 hours CPU | +6h 12min |
| 2.3 | Integration + validation | 1 day | +1d 6h |
| **IF NULL:** |
| 3.1 | Pivot to Pathway 3 setup | 2 hours | +2h 12min |
| 3.2 | First closed-loop iteration | 30 min | +2h 42min |

---

## Rollback Plan

**If Phase 2 breaks ARCHCODE:**
- Commit before integration: `git tag pre-embedding-integration`
- If validation suite fails → `git reset --hard pre-embedding-integration`
- Keep categorical as default, embeddings as optional flag

---

**Last updated:** 2026-05-08 (awaiting Phase 1 results)  
**Next update:** After REAL NT completes (~5 min)
