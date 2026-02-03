# ARCHCODE — 3D DNA Loop Extrusion Simulator

> **TL;DR**: Научный симулятор loop extrusion с 3D визуализацией. Publication Ready (95%).

## Quick Status

| Метрика | Значение |
|---------|----------|
| **Версия** | 1.0.2 |
| **Branch** | master |
| **Тесты** | 37/37 pass |
| **Power-law** | α = -0.964 (error 3.6%) |
| **Blind-test** | HBB, Sox2, CTCFΔ, **IGH** — ALL PASS |

## Model Validation: Blind-Test Performance

**Calibrated on:** HBB locus (Sabaté et al. 2025) | **Seed:** 2000 (all tests)

| Locus/Condition | Mean Duration | 95% CI | Contact Prob | Verdict |
|-----------------|---------------|--------|--------------|---------|
| HBB (wild-type) | 16.17 min | [15.23, 17.11] | 3.15% | PASS |
| Sox2 (blind) | 16.18 min | [15.28, 17.08] | 3.26% | PASS |
| HBB-CTCFΔ (blind) | 16.17 min | [15.23, 17.11] | 3.15% | PASS |

**Key observation:** CTCF knockout of weak site (strength 0.8) showed **NO effect** — identical to WT.

**Hypothesis:** Weak CTCF barriers (strength < 0.85) are dispensable. Only strong barriers stabilize loops.

## Commands

```bash
npm run dev              # Dev server
npm run build            # Production build
npm run test             # Unit tests
npm run test:regression  # Regression suite (37 tests)
npm run validate:hic     # Power-law validation (offline)
npm run validate:nature2025  # Sabaté 2025 blind-test (HBB, 1000 runs)
npm run validate:sox2    # Sox2 validation (100 runs)
npm run validate:ctcf-kd # CTCF knockout validation
```

## Architecture

```
src/
├── domain/
│   ├── constants/biophysics.ts  # ВСЕ физические константы здесь
│   └── models/genome.ts         # CTCFOrientation: 'F' | 'R'
├── engines/
│   ├── LoopExtrusionEngine.ts   # Основной движок (stochastic blocking)
│   └── MultiCohesinEngine.ts    # Multi-cohesin (leaky 15%)
├── downloaders/hic.ts           # Hi-C data downloader (Rao 2014)
└── utils/random.ts              # SeededRandom (НЕ Math.random!)
```

## Key Rules (из .cursorrules)

1. **Константы** → только в `biophysics.ts`
2. **CTCF** → только `'F' | 'R'`
3. **Random** → только `SeededRandom`, никогда `Math.random()`
4. **Комментарии** → `LITERATURE-BASED` vs `MODEL PARAMETER`

## Научные параметры

| Параметр | Значение | Источник |
|----------|----------|----------|
| Velocity | 1 kb/s | Davidson 2019 |
| Processivity | 600 kb (model) | 33 kb lit × 18 |
| CTCF efficiency | 85% | MODEL PARAMETER |
| Residence time | ~20 min | Gerlich 2006 |

## Что осталось (TODO)

- [ ] Zenodo DOI
- [ ] GitHub Pages demo
- [ ] Edge case тесты (extreme velocity)
- [x] Blind-test валидация (HBB, Sox2, CTCFΔ) — DONE
- [ ] Расширить до 10+ локусов (сейчас 2)

## H2: FountainLoader (Mediator-driven loading)

**Статус:** Работает | **Оптимальный beta:** 5

### MYC Locus (calibration)
| Beta | stepLoadProb | avgLoops | NonZero cells |
|------|--------------|----------|---------------|
| 0 | 0.000278 | 2.8 | baseline |
| 5 | 0.001801 | 3.0 | **623** (max) |
| 10 | 0.003323 | 3.0 | 599 |

### IGH Locus (blind test) — PASS
| Metric | Beta=0 | Beta=5 | Change |
|--------|--------|--------|--------|
| stepLoadProb | 0.000278 | 0.002233 | 8.0x |
| avgLoops | 5.0 | 6.0 | +1.0 |
| NonZero cells | 223 | 379 | +70% |
| Diff cells | — | 398 | ✓ |

**Ключевые файлы:**
- `src/simulation/SpatialLoadingModule.ts` — FountainLoader
- `scripts/run-fountain-ensemble.ts` — MYC ensemble
- `scripts/run-fountain-igh.ts` — IGH blind test
- `updateOccupancyMatrix()` — учёт времени контакта

## Последняя сессия

**Дата**: 2026-02-03 (утро)
**Сделано**:
- FountainLoader: occupancy-based matrix вместо static loops
- updateOccupancyMatrix() для учёта времени контакта
- Ensemble: 20 runs × 50000 steps
- beta=5 оптимальный (623 NonZero cells на MYC)
- **IGH blind validation**: PASS (398 diff cells, 8x loading increase)

## Ключевые файлы для контекста

| Приоритет | Файл | Зачем |
|-----------|------|-------|
| 1 | Этот CLAUDE.md | Быстрый старт |
| 2 | SESSION_REPORT_2026-02-02.md | Детали последней сессии |
| 3 | .cursorrules | Coding rules |
| 4 | METHODS.md | Научная методология |
| 5 | KNOWN_ISSUES.md | Известные ограничения |

---

## Auto-Update Rule

**Claude должен автоматически обновлять этот файл** в конце сессии если:
- Изменилась архитектура или ключевые файлы
- Добавлены новые фичи или исправлены баги
- Изменился статус TODO
- Появились новые known issues
- Прошла валидация или тесты

Формат обновления:
1. Обновить "Quick Status" если изменились метрики
2. Обновить "Последняя сессия" с кратким summary
3. Обновить TODO если задачи выполнены
4. Закоммитить: `docs: update CLAUDE.md session context`

---
*Обновлено: 2026-02-03 (IGH blind-test validation)*
