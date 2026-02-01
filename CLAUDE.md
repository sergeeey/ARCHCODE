# ARCHCODE — 3D DNA Loop Extrusion Simulator

> **TL;DR**: Научный симулятор loop extrusion с 3D визуализацией. Publication Ready (95%).

## Quick Status

| Метрика | Значение |
|---------|----------|
| **Версия** | 1.0.2 |
| **Branch** | master |
| **Тесты** | 37/37 pass |
| **Валидация** | Power-law α = -0.964 (error 3.6%) |
| **Hi-C данные** | Rao 2014, 8054 loops |

## Commands

```bash
npm run dev          # Dev server
npm run build        # Production build
npm run test         # Unit tests
npm run test:regression  # Regression suite (37 tests)
npm run validate:hic     # Power-law validation (offline)
npm run validate:hic:download  # Real Hi-C validation
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
- [ ] Расширить валидацию до 10+ локусов

## Последняя сессия

**Дата**: 2026-02-02
**Сделано**:
- HaluGate верификация METHODS.md
- Исправлена ошибка citation (Ganji → Davidson)
- Добавлен stochastic blocking
- Hi-C downloader создан
- Power-law валидация пройдена

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
*Обновлено: 2026-02-02*
