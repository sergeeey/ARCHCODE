---
tags:
  - project-card
  - chernoffpy
  - library
  - math
  - finance
created: '2026-04-12'
updated: '2026-04-13'
---
# ChernoffPy

**Одно предложение:** Option pricing через Chernoff operator splitting с certified error bounds — единственный зарелизенный PyPI пакет.
**Статус:** Released v0.2.0, PR 1 с двумя коммитами (CFL guard + price_to_tolerance)
**Стек:** Python 3.11, NumPy, SciPy, Numba (optional), CuPy (optional GPU), MkDocs
**Где:** E:\MarkovChains\ChernoffPy
**GitHub:** github.com/sergeeey/MarkovChains
**Тесты:** 569 passed, 0 failed, 4 skipped

## Сессия 13 апреля — два ключевых коммита

### 1. CFL Guard (ab8e560)
- До: молчаливый взрыв при недостаточном n_steps
- После: ValueError с рекомендацией min n_steps плюс min_n_steps() API
- Fail loud работает

### 2. price_to_tolerance() (8c53597) — КЛЮЧЕВАЯ ФИЧА
- Было: "вот цена и вот оценка ошибки" (пользователь сам думает)
- Стало: "задай tolerance, библиотека сама дойдёт до нужной точности"
- Adaptive: pilot run -> estimate B -> compute n -> refine (до 3 раундов)
- Работает для European и Barrier DST
- Bound стал механизмом управления расчётом, а не просто информацией

### Что это значит
Превращает rare feature (certified bounds) в real use case (adaptive certified pricing). Это "smart stopping rule" из неочевидных применений — теперь реализован.

## Оставшиеся ограничения

- MAX_LMIX_SUBSTEPS=8 — эмпирика (MEDIUM)
- Domain truncation error: grid L=8 даёт floor около 3.8e-3, нужен L=12 для 1e-3 (MEDIUM)
- Stress matrix: 17 cases, не полный sweep (LOW)

## Production readiness: 8.5/10

- CFL guard: fail loud работает
- price_to_tolerance: adaptive computation
- 569 тестов зелёные
- Remaining: spatial accuracy warning, full stress matrix

## VeriFind интеграция (VERIFIED, deployed)

- Truth Gate (bs_validator.py) — перепроверка option prices
- Conformal Predictor (certified_bounds.py) — proven interval bounds
- PhaseBreak adapter — MarketRegime detection

## Roadmap

1. Merge PR 1 -> tag v0.2.1
2. arXiv paper draft (неделя 2 месячного плана)
3. Написать Ремизову
4. Spatial accuracy warning
5. CI stress matrix

## Связи

- [[ChernoffPy — применения и стратегия]]
- [[Карточка — VeriFind 2026]] — deployed integration
- [[Карточка — HeatPrice 2026]] — API обёртка (frozen)
- Ремизов (МГУ ВШЭ) — потенциальный co-author

up:: [[Каталог всех проектов 2026]]
