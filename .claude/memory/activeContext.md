# Active Context — ARCHCODE

**Last Updated:** 2026-03-01 (session 4, post-positional signal analysis)
**Branch:** main
**Last Commit:** de84f7a (within-category positional signal — honest null)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment

---

## Текущий статус проекта

**Фаза:** v2.0 — Within-category analysis DONE (null result), CFTR next

### ✅ K562 Hi-C Correlation Results (MILESTONE)

| Метрика      | GM12878 (v1.0) | K562 30kb   | K562 95kb   |
| ------------ | -------------- | ----------- | ----------- |
| Pearson r    | 0.16 (ns)      | **0.530\*** | **0.588\*** |
| Spearman ρ   | —              | **0.680\*** | **0.409\*** |
| p-value      | 0.30           | 2.19e-82    | <1e-300     |
| n datapoints | 12             | 1,124       | 11,649      |

### ✅ Within-Category Positional Signal (HONEST NULL — session 4)

**Ключевой результат:** SSIM НЕ добавляет predictive value поверх категории на HBB.

| Тест                                | Результат     | p-value |
| ----------------------------------- | ------------- | ------- |
| Logistic regression (SSIM additive) | ΔAUC = -0.001 | 1.0     |
| Mann-Whitney intronic (9 vs 658)    | Δ = 0.000008  | 0.69    |
| Mann-Whitney other (12 vs 7)        | Δ = -0.0009   | 0.058   |
| Mann-Whitney synonymous (3 vs 83)   | Δ = -0.00006  | 0.22    |
| Permutation other (n=19)            | AUC = 0.77    | 0.032\* |

**Причина null:** Все 1,103 ClinVar варианта кластеризованы в 2.1 kb из 95 kb окна (2.2%). Distance-to-CTCF/LCR не варьируется (20-23 kb ≈ константа). Within-category positional diversity = 0.

**Модель IS positionally sensitive:** Distance-to-TSS коррелирует с SSIM (intronic ρ=0.80, splice_donor ρ=0.92) — но одинаково для path и benign.

**Вывод:** AUC=0.977 = category-level structural model, не independent positional prediction. Для доказательства positional signal нужен CFTR (~4200 вариантов в 317 kb TAD).

### ✅ Manuscript updated with K562 (session 4)

- 14 правок: Abstract → Discussion → Supplementary
- r=0.16 → K562 trajectory (0.16→0.53→0.59)
- Commit: de4ac71, pushed

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
9. ✅ **Within-category positional signal** → honest null (de84f7a)
10. 🔄 **CFTR locus — real positional signal test**

---

## Ключевые файлы v2.0

| Файл                                   | Назначение                         |
| -------------------------------------- | ---------------------------------- |
| `config/locus/hbb_30kb_v2.json`        | 30kb config (MODEL_PARAMETER)      |
| `config/locus/hbb_95kb_subTAD.json`    | 95kb config (ENCODE CTCF)          |
| `src/domain/config/locus-config.ts`    | TS loader + LocusConfig interface  |
| `scripts/lib/locus_config.py`          | Python mirror loader               |
| `scripts/generate-unified-atlas.ts`    | Main pipeline (`--locus`)          |
| `scripts/analyze_positional_signal.py` | **NEW** Within-category analysis   |
| `scripts/correlate_hic_archcode.py`    | K562 vs ARCHCODE correlation       |
| `results/positional_signal_95kb.json`  | **NEW** Honest null result         |
| `docs/RESEARCH_POSITIONAL_SIGNAL.md`   | **NEW** 30-paper literature review |
| `plots/positional_signal_95kb.png`     | **NEW** 3-panel diagnostic figure  |

---

## v2.0 Research Roadmap (оставшиеся действия)

1. ~~Унифицировать пайплайн~~ ✅
2. ~~Externalize locus config~~ ✅
3. ~~K562 Hi-C correlation~~ ✅ (r=0.53/0.59)
4. ~~Manuscript K562 update~~ ✅ (14 edits)
5. ~~Within-category analysis~~ ✅ (honest null)
6. **CFTR локус** — config + ~4,200 ClinVar variants (NEXT PRIORITY)
   - Варианты распределены по всему 317kb TAD
   - Реальный тест positional signal
7. **95kb threshold recalibration** — SSIM thresholds для 159x159
8. **Bayesian fit** HBB → CFTR через Optuna GPSampler
9. **Manuscript update** — добавить within-category null + reframe AUC
10. **TDA proof-of-concept** — ripser + persim

---

## Для следующей сессии

1. **CFTR locus config** — CTCF sites из ENCODE, enhancers из литературы
2. **CFTR ClinVar download** — ~4200 variants via E-utilities
3. **Manuscript**: добавить within-category null result в Discussion
4. Проверь: получен ли DOI от bioRxiv?
5. Обновить ссылку: Sabaté 2024 bioRxiv → Nature Genetics 2025
