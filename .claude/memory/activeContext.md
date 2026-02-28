# Active Context — ARCHCODE

**Last Updated:** 2026-02-28 (session 3, post-K562 correlation)
**Branch:** main
**Last Commit:** pending (K562 Hi-C correlation results)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment

---

## Текущий статус проекта

**Фаза:** v2.0 — K562 Hi-C correlation DONE, threshold recalibration next

### ✅ K562 Hi-C Correlation Results (MILESTONE)

| Метрика      | GM12878 (v1.0) | K562 30kb   | K562 95kb   |
| ------------ | -------------- | ----------- | ----------- |
| Pearson r    | 0.16 (ns)      | **0.530\*** | **0.588\*** |
| Spearman ρ   | —              | **0.680\*** | **0.409\*** |
| p-value      | 0.30           | 2.19e-82    | <1e-300     |
| n datapoints | 12             | 1,124       | 11,649      |

- **r(95kb) > r(30kb)** как предсказано — реальные CTCF-якоря улучшают корреляцию
- 95kb Pearson выше, Spearman ниже (sparse элементы зашумляют ранги при 159x159)
- mcool: 4DNFI18UHVRO.mcool (7.5 GB), resolution 1000bp, KR-balanced

**Hi-C extraction details:**

- 30kb: 30x30 matrix, 717/900 non-zero, 1 CTCF peak in region
- 95kb: 95x95 matrix, 5559/9025 non-zero, 5 CTCF peaks in region

### ✅ Locus Config Externalization (session 3)

- `config/locus/hbb_30kb_v2.json` + `hbb_95kb_subTAD.json`
- TS + Python loaders, `--locus 30kb|95kb` в 3 скриптах
- 30kb backward compat: byte-identical CSV
- 95kb: 159x159, 0 structural pathogenic (thresholds uncalibrated)

---

## Все фазы

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes
3. ✅ Phase 4-6: Real Hi-C validation GM12878 (r=+0.16, p=0.30)
4. ✅ Phase A-H: Documentation, ROC, bioRxiv submission
5. ✅ Phase I: Unified pipeline (AUC 1.000 → 0.9766)
6. ✅ Locus config externalization (30kb + 95kb)
7. ✅ **K562 Hi-C correlation** (r=0.53/0.59, p<1e-82)
8. 🔄 **95kb threshold recalibration + manuscript update**

---

## Ключевые файлы v2.0

| Файл                                     | Назначение                        |
| ---------------------------------------- | --------------------------------- |
| `config/locus/hbb_30kb_v2.json`          | 30kb config (MODEL_PARAMETER)     |
| `config/locus/hbb_95kb_subTAD.json`      | 95kb config (ENCODE CTCF)         |
| `src/domain/config/locus-config.ts`      | TS loader + LocusConfig interface |
| `scripts/lib/locus_config.py`            | Python mirror loader              |
| `scripts/generate-unified-atlas.ts`      | Main pipeline (`--locus`)         |
| `scripts/extract_k562_hbb.py`            | Extract HBB from K562 mcool       |
| `scripts/correlate_hic_archcode.py`      | K562 vs ARCHCODE correlation      |
| `results/hic_correlation_k562.json`      | **NEW** 30kb: r=0.530, p=2.19e-82 |
| `results/hic_correlation_k562_95kb.json` | **NEW** 95kb: r=0.588, p<1e-300   |

---

## v2.0 Research Roadmap (оставшиеся действия)

1. ~~Унифицировать пайплайн~~ ✅
2. ~~Externalize locus config~~ ✅
3. ~~K562 Hi-C correlation~~ ✅ (r=0.53/0.59)
4. **95kb threshold recalibration** — SSIM thresholds для 159x159
5. **Обновить манускрипт** с K562 результатами (r=0.53→0.59 vs GM12878 r=0.16)
6. **Bayesian fit** HBB → SOX2 через Optuna GPSampler
7. **CFTR локус** — config + 4,200 ClinVar variants
8. **TDA proof-of-concept** — ripser + persim

---

## Для следующей сессии

1. **Рекалибровка thresholds** для 159x159: эмпирическое определение SSIM cutoffs
2. **Манускрипт**: добавить K562 результаты (Table, Figure)
3. Проверь: получен ли DOI от bioRxiv?
4. Bayesian fit: Optuna GPSampler для 3 параметров (K_BASE, alpha, gamma)
