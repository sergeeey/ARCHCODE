---
tags:
  - project-card
  - verifind
  - product
  - finance
created: '2026-04-12'
updated: '2026-04-13'
---
# VeriFind / APE 2026

**Одно предложение:** Financial decision support — LLM генерирует код (не числа), Truth Boundary Gate, multi-agent debate, paper trading.
**Статус:** Production (paper trading $1000)
**Стек:** Python 3.11, FastAPI, LangGraph, TimescaleDB, Neo4j, Redis, Next.js 14, Docker (9 containers)
**Где:** E:\VeriFind - 2026
**Тесты:** 983

## ChernoffPy интеграция (VERIFIED)

ChernoffPy уже встроен в VeriFind в 3 местах:
- **Truth Gate** (bs_validator.py) — независимая перепроверка option prices
- **Conformal Predictor** (certified_bounds.py) — proven interval bounds вместо naive heuristic
- **PhaseBreak adapter** — MarketRegime detection

Проблема: bs_validator использует hardcoded defaults (S=100, K=100). Нужно извлекать из VEE context.

## Результат

- Directional accuracy: 55.5% (14d), 57.2% (30d) — честно для финансов
- Golden Set: 5/20 (25%) pass rate
- Live paper trading: $1000

## Связи

- [[Карточка — ChernoffPy]] -> Truth Gate + Certified Intervals (deployed)
- [[Карточка — PhaseBreak 2026]] -> MarketRegime adapter (deployed)
- [[ChernoffPy — применения и стратегия]] -> validation companion tool

up:: [[Каталог всех проектов 2026]]
