# Active Context — ARCHCODE

**Last Updated:** 2026-02-28
**Branch:** main
**Last Commit:** 0ec16ad (fix(integrity): remove all fabricated claims and add honest disclaimers)
**GitHub:** https://github.com/sergeeey/ARCHCODE

---

## Текущий статус проекта

**Фаза:** Real Data Pipeline COMPLETE → Pre-Publication Cleanup

Проект прошёл через несколько фаз:

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes (FALSIFICATION_REPORT.md)
3. ✅ Phase 4-6: Real Hi-C validation (r=+0.16, не значимо)
4. ✅ Phase A: Documentation + hypothesis "The Loop That Stayed"
5. ✅ **Phase B: Real Data Replacement (AlphaGenome → VEP)** ← ЗАВЕРШЕНО 2026-02-28

---

## Что сделано в Phase B (Real Data Pipeline)

### Шаг 1: ClinVar Download (✅)

- 431 real HBB variants via NCBI E-utilities API (esearch + esummary)
- 353 с ref/alt alleles → `data/hbb_real_variants.csv`
- Фикс: переписан парсер `download_clinvar_hbb.ts` под реальный формат API

### Шаг 2: Sequence Predictions (✅)

- **SpliceAI** — недоступен (pysam не компилируется на Windows, Broad Institute API таймаут из KZ)
- **Pivot → Ensembl VEP v113** REST API (batch mode, 200 вариантов/запрос)
- 353 предсказания с SIFT scores → `data/hbb_vep_results.csv`
- Скрипт: `scripts/run_vep_predictions.py`

### Шаг 3: ARCHCODE Simulation (✅)

- Analytical mean-field approach (НЕ стохастический Monte Carlo)
- Формула: C(i,j) = distance_decay × occupancy × ctcf_permeability × kramer
- Пороги калиброваны: <0.85 PATHOGENIC, 0.85-0.92 LP, 0.92-0.96 VUS, 0.96-0.99 LB, ≥0.99 B
- Скрипт: `scripts/generate-real-atlas.ts`

### Шаг 4: Results (✅)

- **161/353 (45.6%)** ARCHCODE pathogenic
- **20 pearl variants** (VEP blind, ARCHCODE detects): 15 promoter, 3 missense, 1 frameshift, 1 splice_acceptor
- Категориальная стратификация биологически корректна:
  - nonsense: SSIM=0.8753 (100% pathogenic)
  - frameshift: SSIM=0.8919 (100% pathogenic)
  - synonymous: SSIM=0.9989 (0% pathogenic)
- Файлы: `results/HBB_Clinical_Atlas_REAL.csv`, `results/REAL_ATLAS_SUMMARY.json`

### Шаг 5: Manuscript Update (✅)

- Обновлены ВСЕ 8 файлов рукописи:
  - ABSTRACT.md, METHODS.md, RESULTS.md, DISCUSSION.md
  - INTRODUCTION.md, REFERENCES.md, SUPPLEMENTARY_TABLE_S1.md
  - FULL_MANUSCRIPT.md (полная пересборка, 1162 строки)
- AlphaGenome → VEP/sequence-based predictors
- Fake VCV IDs → real ClinVar IDs
- R²=0.89 "fitted to FRAP" → honest "calibrated from literature"
- Added Jaganathan et al. 2019 (SpliceAI, Cell) — DOI verified

---

## Ключевые результаты (всё вместе)

### Hi-C Validation

- r=+0.16 (KR normalized, p=0.30) — **не значимо**, честно задокументировано

### Real Clinical Atlas

- 353 real ClinVar variants, 12 categories
- 20 pearl variants (VEP-blind, ARCHCODE-detected)
- Primary pearl class: promoter variants (SSIM≈0.928, VEP=0.20)

### Гипотеза "The Loop That Stayed"

- Теоретический фреймворк, НЕ подтверждённое открытие
- Нужна экспериментальная валидация (RT-PCR, Capture Hi-C)

---

## Незавершённые задачи (приоритет)

### 🔴 Критические (блокируют публикацию)

1. **Коммит и push всех изменений** — много unstaged файлов
2. **FASTQ download + splice junction analysis** (если нужна для рукописи)
   - SRA: SRR12837671 (WT), SRR12837674 (D3), SRR12837675 (A2)
3. **Publication-quality фигуры** — contact matrices, SSIM distribution, pearl highlight

### 🟡 Важные

4. Валидация на Sox2 и Pcdh loci (multi-locus)
5. Перепроверить FULL_MANUSCRIPT.md на inline цитирования (нумерация сдвинулась в REFERENCES.md)
6. Проверить рукопись на consistency (числа между секциями)

### 🟢 Можно отложить

7. Web deployment (GitHub Pages / Vercel)
8. Parameter optimization (grid/Bayesian search)
9. SpliceAI retry (если API станет доступен)

---

## Тех. стек

- **Engine:** TypeScript (Vite + React + Three.js)
- **Validation:** Python (cooler, Ensembl VEP)
- **Analysis:** Analytical mean-field simulation
- **State:** Zustand
- **Tests:** Vitest (seed=42)
- **Config:** config/default.json

---

## Ключевые файлы (новые/обновлённые)

```
scripts/download_clinvar_hbb.ts       ← ClinVar download (fixed parser)
scripts/process_clinvar_hbb.ts        ← ClinVar processing + CSV export
scripts/run_vep_predictions.py        ← Ensembl VEP batch predictions
scripts/generate-real-atlas.ts        ← Real atlas generator (analytical)
data/hbb_real_variants.csv            ← 353 real variants input
data/hbb_vep_results.csv              ← VEP predictions output
results/HBB_Clinical_Atlas_REAL.csv   ← Final real atlas
results/REAL_ATLAS_SUMMARY.json       ← Summary with pearl list
manuscript/                           ← ALL sections updated (no AlphaGenome)
```

---

## Guardrails (из CLAUDE.md)

- ✅ Все DOI проверены (Jaganathan 2019, McLaren 2016, Sabaté 2024)
- ✅ AlphaGenome удалён из всех рукописных файлов (кроме "NOT USED" transparency table)
- ✅ Fake VCV IDs удалены (0 matches в manuscript/)
- ✅ R²=0.89 заменён на honest "calibrated from literature"
- ✅ "Fitted to FRAP" → "calibrated parameter"
- ❌ Sabaté 2025 (Nature Genetics) — НЕ СУЩЕСТВУЕТ

---

## Для следующей сессии

1. Прочитай этот файл
2. Проверь `git log --oneline -5`
3. Спроси: "Продолжаем [задачу] или новая цель?"
4. Приоритет: коммит, фигуры, consistency check
