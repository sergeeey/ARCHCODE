# Active Context — ARCHCODE

**Last Updated:** 2026-02-27
**Branch:** main
**Last Commit:** bbf71e4 (chore: sync all local changes to GitHub)
**GitHub:** https://github.com/sergeeey/ARCHCODE

---

## Текущий статус проекта

**Фаза:** Post-Validation → Real Data Replacement (AlphaGenome → SpliceAI)

Проект прошёл через несколько фаз:

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes (FALSIFICATION_REPORT.md)
3. ✅ Phase 4-6: Real Hi-C validation (r=+0.16, не значимо)
4. ✅ Phase A: Documentation + hypothesis "The Loop That Stayed"
5. 🟡 **Текущая:** Замена mock AlphaGenome → реальные SpliceAI данные

---

## Ключевые результаты (что уже сделано)

### Hi-C Validation (реальные данные)

- Извлечены Hi-C данные HUDEP-2 (GSM4873116) для HBB locus
- V1 (гипотетические CTCF): r=+0.16 (KR normalized, p=0.30)
- V2 (литературные CTCF): r=+0.05 (KR normalized, p=0.76)
- **Оба не значимы** — честно задокументировано

### CTCF Validation

- 6/6 сайтов совпали с литературой (100% concordance)
- Механистическая основа валидна, структурная корреляция слабая

### Гипотеза "The Loop That Stayed"

- HBB promoter ↔ 3'HS1 loop (22 kb) регулирует сплайсинг
- Разрушение петли (D3 deletion) → -36% экспрессия HBB
- Инверсия (A2) → +28% экспрессия HBB
- Предсказание: D3 покажет 15-30% аберрантного сплайсинга

### RNA-seq анализ (GSE160420)

- Данные Himadewi et al. 2021, eLife
- CPM: WT=10,886 | D3=6,947 (-36%) | A2=13,978 (+28%)
- Нужна splice junction analysis (FASTQ → STAR → SJ.out.tab)

---

## Незавершённые задачи (приоритет)

### 🔴 Критические (блокируют публикацию)

1. **Замена AlphaGenome → SpliceAI** (REAL_DATA_REPLACEMENT_PLAN.md)
   - Установить SpliceAI, скачать ClinVar VCF + hg38.fa
   - Прогнать 366 HBB вариантов
   - Обновить manuscript (10 файлов)

2. **FASTQ download + splice junction analysis**
   - SRA: SRR12837671 (WT), SRR12837674 (D3), SRR12837675 (A2)
   - Скрипт готов: `scripts/analyze_nmd_susceptibility.py`
   - Нужно: скачать FASTQ (~30 GB), выровнять STAR, проанализировать

### 🟡 Важные

3. Обновить manuscript FULL_MANUSCRIPT.md с реальными данными
4. Сгенерировать publication-quality фигуры
5. Валидация на Sox2 и Pcdh loci (Hi-C)

### 🟢 Можно отложить

6. Web deployment (GitHub Pages / Vercel)
7. Live AlphaGenome integration (когда API выйдет)
8. Parameter optimization (grid/Bayesian search)

---

## Архитектурные решения (ADR-009, ADR-010)

- **ADR-009:** Pivot от mock к Hi-C + RNA-seq валидации
- **ADR-010:** CLAUDE.md Falsification-First Protocol (обязательно)
- **ADR-003:** Mock AlphaGenome только для UI dev, НЕ для публикации

---

## Тех. стек

- **Engine:** TypeScript (Vite + React + Three.js)
- **Validation:** Python (cooler, SpliceAI, STAR)
- **State:** Zustand
- **Tests:** Vitest (seed=42)
- **Config:** config/default.json (единый источник параметров)

---

## Файловая структура (ключевые)

```
src/engines/LoopExtrusionEngine.ts    ← основной движок
src/engines/MultiCohesinEngine.ts     ← ансамбль 20 когезинов
src/services/AlphaGenomeService.ts    ← MOCK (помечен как synthetic)
src/validation/alphagenome.ts         ← валидация
config/default.json                   ← параметры (α, γ, velocity)
manuscript/                           ← все секции рукописи
data/samples/                         ← JSON сэмплы
results/                              ← результаты симуляций
scripts/                              ← Python/TS скрипты
```

---

## Guardrails (из CLAUDE.md)

- ❌ Никаких фантомных ссылок (все DOI проверять)
- ❌ Никаких скрытых синтетических данных (MOCK\_ prefix)
- ❌ Никаких "fitted" параметров без fitting code
- ❌ Никаких post-hoc claims как pre-registered
- ✅ Sabaté 2024 (bioRxiv) — реальная ссылка
- ❌ Sabaté 2025 (Nature Genetics) — НЕ СУЩЕСТВУЕТ

---

## Данные на диске (НЕ в git)

| Путь                       | Размер | Содержимое                |
| -------------------------- | ------ | ------------------------- |
| `fastq_data/`              | 13 GB  | SRA downloads (частичные) |
| `ДНК Образцы СКАЧЕННЫЙ/`   | 88 GB  | Downloaded DNA samples    |
| `data/temp_hudep2_wt.cool` | 67 MB  | Hi-C cooler file          |

Всё тяжёлое исключено из git через `.gitignore`.

---

## Для следующей сессии

1. Прочитай этот файл
2. Проверь `git log --oneline -5` на свежие коммиты
3. Спроси: "Продолжаем [задачу] или новая цель?"
4. Основные планы: REAL_DATA_REPLACEMENT_PLAN.md
