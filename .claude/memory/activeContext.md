# Active Context — ARCHCODE

**Last Updated:** 2026-03-01 (session 8, manuscript CFTR + Bayesian update — 17 edits)
**Branch:** main
**Last Commit:** 5a7ea6c (chore: reference data, research docs, ADRs, scripts)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment

---

## Текущий статус проекта

**Фаза:** v2.0 — CFTR locus implemented, Bayesian fit completed

### ✅ Bayesian Optimization Result (MILESTONE — honest null #2)

| Метрика | Baseline | Best (200 trials)    | Δ       |
| ------- | -------- | -------------------- | ------- |
| alpha   | 0.92     | 0.50 (lower bound)   | —       |
| gamma   | 0.80     | 0.30 (lower bound)   | —       |
| k_base  | 0.002    | 0.0005 (lower bound) | —       |
| r_30kb  | 0.5299   | 0.5300               | +0.0001 |
| r_95kb  | 0.5876   | 0.5877               | +0.0001 |

**Key insight:** All 3 best params hit lower bounds → optimizer minimizes the Kramer kinetics term entirely. k_base importance = 90% (fANOVA). Hi-C correlation is **architecture-driven** (distance decay, MED1 landscape, CTCF barriers), NOT kinetics-driven. Kinetics params serve a different role: variant pathogenicity classification via SSIM perturbation. **Decision: KEEP original params.** Grid-search estimates confirmed near-optimal.

### ✅ CFTR Locus — Within-Category Results (MILESTONE)

| Метрика                  | HBB (95kb)     | CFTR (317kb)         |
| ------------------------ | -------------- | -------------------- |
| ClinVar variants         | 1,103          | 3,349                |
| P/LP + B/LB              | 353 + 750      | 1,756 + 1,593        |
| Variant spread           | 2.1 kb (2.2%)  | 201.5 kb (63.6%)     |
| Bins occupied            | 2-3 / 159      | 93 / 317             |
| SSIM range               | 0.9910–1.0000  | 0.9948–1.0000        |
| Logistic regression ΔAUC | -0.001 (p=1.0) | +0.007 (p=1.0)       |
| MW-U synonymous          | p=0.22 ns      | **p=6.1e-6** \*\*\*  |
| MW-U intronic            | p=0.69 ns      | p=0.13 ns            |
| MW-U "other"             | p=0.058 ns     | **p=1.6e-16** \*\*\* |

**Key insight:** synonymous category shows statistically significant but practically negligible (Δ=7e-6 SSIM units) within-category signal at CFTR. Global logistic regression p=1.0 → SSIM is a **category-level classifier**, not a within-category positional predictor. Consistent across both loci.

**SSIM dilution at 317x317:** Matrix size reduces SSIM sensitivity. All SSIM > 0.9948. Need threshold recalibration for large matrices.

### ✅ K562 Hi-C Correlation Results

| Метрика   | GM12878 (v1.0) | K562 30kb   | K562 95kb   |
| --------- | -------------- | ----------- | ----------- |
| Pearson r | 0.16 (ns)      | **0.530\*** | **0.588\*** |
| p-value   | 0.30           | 2.19e-82    | <1e-300     |

---

## Все фазы

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes
3. ✅ Phase 4-6: Real Hi-C validation GM12878 (r=+0.16, p=0.30)
4. ✅ Phase A-H: Documentation, ROC, bioRxiv submission
5. ✅ Phase I: Unified pipeline (AUC 1.000 → 0.9766)
6. ✅ Locus config externalization (30kb + 95kb)
7. ✅ K562 Hi-C correlation (r=0.53/0.59, p<1e-82)
8. ✅ Manuscript K562 update (14 edits, de4ac71)
9. ✅ Within-category HBB → honest null (de84f7a)
10. ✅ Manuscript within-category update (8 edits, aa0f677)
11. ✅ **CFTR locus — config, pipeline, within-category test**
12. ✅ **Bayesian fit (Optuna)** — Δr=0.0001, confirmed near-optimal, honest null
13. ✅ **Manuscript CFTR + Bayesian update** — 17 edits, ~1400→1527 lines

---

## Ключевые файлы

| Файл                                   | Назначение                                             |
| -------------------------------------- | ------------------------------------------------------ |
| `config/locus/cftr_317kb.json`         | CFTR 317kb config (ENCODE CTCF + literature enhancers) |
| `config/locus/hbb_30kb_v2.json`        | 30kb config (MODEL_PARAMETER)                          |
| `config/locus/hbb_95kb_subTAD.json`    | 95kb config (ENCODE CTCF)                              |
| `scripts/download_clinvar_cftr.py`     | CFTR ClinVar download (P/LP + B/LB)                    |
| `scripts/generate-unified-atlas.ts`    | Main pipeline (`--locus cftr\|30kb\|95kb`)             |
| `scripts/analyze_positional_signal.py` | Within-category analysis (supports cftr)               |
| `data/cftr_variants.csv`               | 3,349 CFTR variants                                    |
| `results/CFTR_Unified_Atlas_317kb.csv` | CFTR atlas output                                      |
| `results/positional_signal_cftr.json`  | CFTR within-category result                            |
| `results/positional_signal_95kb.json`  | HBB honest null result                                 |
| `scripts/bayesian_fit_hic.py`          | Optuna Bayesian optimization (α, γ, K_BASE)            |
| `results/bayesian_fit_hic.json`        | Bayesian fit result (honest null — Δr=0.0001)          |

---

## v2.0 Research Roadmap (оставшиеся действия)

1. ~~Унифицировать пайплайн~~ ✅
2. ~~Externalize locus config~~ ✅
3. ~~K562 Hi-C correlation~~ ✅ (r=0.53/0.59)
4. ~~Manuscript K562 update~~ ✅
5. ~~Within-category HBB~~ ✅ (honest null)
6. ~~Manuscript within-category update~~ ✅
7. ~~CFTR locus~~ ✅ (3,349 variants, within-category: LR p=1.0)
8. **317kb threshold recalibration** — SSIM thresholds для 317x317
9. ~~Manuscript CFTR + Bayesian update~~ ✅ (17 edits applied)
10. ~~Bayesian fit~~ ✅ (Δr=0.0001, params confirmed, honest null)
11. **TDA proof-of-concept** — ripser + persim

---

## Для следующей сессии

1. ~~Manuscript update~~ ✅ (17 edits, session 8)
2. **317kb threshold recalibration** — current 30kb thresholds are diluted at 317x317
3. Проверь: получен ли DOI от bioRxiv?
4. Обновить ссылку: Sabaté 2024 bioRxiv → Nature Genetics 2025
5. bioRxiv revision: загрузить обновлённый манускрипт (с CFTR + Bayesian)
6. Consider category classification improvement — classify_hgvs() misses missense/frameshift for CFTR (no protein_change from API)
7. **TDA proof-of-concept** — ripser + persim (топологический анализ)
