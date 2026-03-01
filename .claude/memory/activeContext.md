# Active Context — ARCHCODE

**Last Updated:** 2026-03-01 (session 11, 4-step plan complete: classify_hgvs fix + BRCA1 + 5kb Hi-C + manuscript v2.1)
**Branch:** main
**Last Commit:** 5a7ea6c (pending — manuscript and pipeline updates not yet committed)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment. Manuscript v2.1 ready.

---

## Текущий статус проекта

**Фаза:** v2.1 — Multi-locus expansion COMPLETE (4 loci done, manuscript updated)

### 4-Locus Summary Table

| Метрика           | HBB (95kb)     | CFTR (317kb)     | TP53 (300kb)     | BRCA1 (400kb)    |
| ----------------- | -------------- | ---------------- | ---------------- | ---------------- |
| ClinVar variants  | 1,103          | 3,349            | 2,795            | 10,682           |
| P/LP + B/LB       | 353 + 750      | 1,756 + 1,593    | 1,646 + 1,149    | 7,062 + 3,620    |
| Variant spread    | 2.1 kb (2.2%)  | 201.5 kb (63.6%) | 109.9 kb (36.6%) | 103.6 kb (25.9%) |
| SSIM range        | 0.8753–0.9989  | 0.9948–1.0000    | 0.9983–1.0000    | 0.9982–1.0000    |
| LR ΔAUC           | -0.001 (p=1.0) | +0.008 (p=1.0)   | +0.023 (p=0.65)  | -0.000 (p=1.0)   |
| K562 Hi-C r       | 0.53 / 0.59    | —                | 0.29             | 0.53             |
| MCF7 Hi-C r       | —              | —                | 0.28             | 0.50             |
| TDA ρ (SSIM↔W_H1) | -0.96          | -1.00            | -0.85            | NaN              |
| Pearl variants    | 20             | 0                | 0                | 0                |

**Key findings:**

- Within-category null confirmed on ALL 4 loci (LR p > 0.6) — ARCHCODE is definitively a category-level classifier
- Matrix-size dilution monotonically reduces SSIM sensitivity (50×50 → 400×400)
- Hi-C correlation locus-dependent: best for HBB/BRCA1 (r~0.53), lowest for TP53 (r~0.29)
- classify_hgvs() fix resolved >90% of "other" variants via cDNA indel length modulo 3

### ✅ Session 11 Completed Steps

1. ✅ **classify_hgvs() fix** — Added `_cdna_indel_length()`, rewrote classify_hgvs() to detect frameshift/inframe from cDNA notation. TP53 "other" 709→53, CFTR "other" 603→54.
2. ✅ **BRCA1 implementation** — Config (13 CTCF, 9 enhancers), 10,682 ClinVar variants, pipeline, within-category (ΔAUC=-0.0002), Hi-C (K562 r=0.53, MCF7 r=0.50), TDA
3. ✅ **5kb Hi-C test** — TP53 r improved 0.29→0.42 at 5kb; KR normalization unavailable in ENCODE intact Hi-C
4. ✅ **Manuscript v2.1 update** — ~15 edits: TP53+BRCA1 Results sections, multi-locus Table 6, abstract/significance/discussion/methods/data availability updates

---

## Все фазы

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes
3. ✅ Phase 4-6: Real Hi-C validation GM12878 (r=+0.16, p=0.30)
4. ✅ Phase A-H: Documentation, ROC, bioRxiv submission
5. ✅ Phase I: Unified pipeline (AUC 1.000 → 0.9766)
6. ✅ Locus config externalization (30kb + 95kb)
7. ✅ K562 Hi-C correlation (r=0.53/0.59, p<1e-82)
8. ✅ Manuscript K562 update (14 edits)
9. ✅ Within-category HBB → honest null
10. ✅ Manuscript within-category update (8 edits)
11. ✅ CFTR locus — config, pipeline, within-category test
12. ✅ Bayesian fit (Optuna) — Δr=0.0001, confirmed near-optimal
13. ✅ Manuscript CFTR + Bayesian update — 17 edits
14. ✅ TDA proof-of-concept — ripser on HBB+CFTR+TP53
15. ✅ Multi-locus candidate research — 25 ACMG genes screened
16. ✅ TP53 locus — config, ClinVar, pipeline, within-category, TDA
17. ✅ **classify_hgvs() fix — frameshift detection from cDNA notation**
18. ✅ **BRCA1 locus — config, ClinVar, pipeline, Hi-C (K562+MCF7), TDA**
19. ✅ **5kb Hi-C test for TP53**
20. ✅ **Manuscript v2.1 — 4-locus update (1,765 lines)**

---

## Ключевые файлы

| Файл                                    | Назначение                                              |
| --------------------------------------- | ------------------------------------------------------- |
| `config/locus/brca1_400kb.json`         | BRCA1 400kb config (K562+MCF7 CTCF, MCF7 H3K27ac)       |
| `config/locus/tp53_300kb.json`          | TP53 300kb config (ENCODE K562 CTCF + H3K27ac)          |
| `config/locus/cftr_317kb.json`          | CFTR 317kb config                                       |
| `config/locus/hbb_30kb_v2.json`         | HBB 30kb config                                         |
| `config/locus/hbb_95kb_subTAD.json`     | HBB 95kb config                                         |
| `scripts/download_clinvar_generic.py`   | Generic ClinVar downloader (--gene TP53/BRCA1/etc.)     |
| `scripts/generate-unified-atlas.ts`     | Main pipeline (`--locus brca1\|tp53\|cftr\|30kb\|95kb`) |
| `scripts/analyze_positional_signal.py`  | Within-category analysis (all loci)                     |
| `scripts/tda_proof_of_concept.py`       | TDA analysis (all loci)                                 |
| `scripts/download_hic_regions.py`       | Hi-C download + correlation                             |
| `data/brca1_variants.csv`               | 10,682 BRCA1 variants                                   |
| `data/tp53_variants.csv`                | 2,795 TP53 variants                                     |
| `results/BRCA1_Unified_Atlas_400kb.csv` | BRCA1 atlas output                                      |
| `results/positional_signal_brca1.json`  | BRCA1 within-category result                            |
| `results/hic_correlation_brca1.json`    | BRCA1 Hi-C: K562 r=0.53, MCF7 r=0.50                    |
| `results/hic_correlation_tp53.json`     | TP53 Hi-C: K562 r=0.29, MCF7 r=0.28                     |
| `manuscript/FULL_MANUSCRIPT.md`         | Manuscript v2.1 (1,765 lines, 4-locus)                  |

---

## v2.1 Research Roadmap — Remaining

1. ~~TP53~~ ✅
2. ~~BRCA1~~ ✅ (10,682 variants, LR p=1.0, Hi-C r=0.50-0.53)
3. **MLH1** — Tier 1 (4,314 variants, HCT116 Hi-C, chr3) — next candidate
4. **LDLR** — Tier 1 (3,721 variants, HepG2 Hi-C, chr19)
5. **SCN5A** — Tier 1 (2,333 variants, iPSC-CM Hi-C, chr3)
6. **Threshold recalibration** — SSIM thresholds for large matrices (>200×200)
7. **bioRxiv revision** — upload updated manuscript with 4-locus data
8. **Git commit** — all changes from session 11

---

## Для следующей сессии

1. **Git commit** — commit all session 11 changes (classify_hgvs fix, BRCA1, manuscript v2.1)
2. **bioRxiv revision** — upload updated manuscript with 4-locus data
3. Проверь: получен ли DOI от bioRxiv?
4. **MLH1 implementation** — same workflow (config, ClinVar, pipeline, Hi-C, TDA)
5. Consider: threshold recalibration for large matrices
6. Consider: resolution-adaptive SSIM normalization
