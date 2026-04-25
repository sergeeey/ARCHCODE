---
tags:
  - project-card
  - reflexio
  - product
created: '2026-04-12'
updated: '2026-04-13'
---
# Reflexio 24/7

**Одно предложение:** Цифровая память — 24/7 запись речи с телефона, транскрипция, обогащение, structured events, дайджест.
**Статус:** Beta (v0.5.2, live VPS)
**Стек:** Python 3.11, FastAPI, faster-whisper, Ollama/Gemini/Claude/GPT cascade, SQLite, Android Kotlin
**Где:** D:\24 na 7
**GitHub:** github.com/sergeeey/24-na-7
**Тесты:** 1,035 passed, 1 failed

## Актуальные метрики (12 апреля 2026, из prod)

- **trusted_fraction: 75.6%** (target >70% — ДОСТИГНУТ)
- Транскрипций: 20,709 total
- Episodes: 2,940 closed
- Day threads: 5,388 (5,169 trusted)
- Long threads: 4,924 (1,975 active)
- Thread coverage: 40.5% (target >50% — NOT YET)

## Scope (текущий, включая drift)

Core: запись -> транскрипция -> обогащение -> structured events -> дайджест
Добавлено: speaker verification, social graph, balance wheel, emotion calibration
Experimental: voice intent (за флагом)
Архив: OSINT KDS, billing заготовки (stripe/freemium)

## v1.0 осталось

1. Thread coverage > 50%
2. Fix 1 failing test
3. Soak 7 days
4. Tag v1.0.0

## Связи

- Anokhin TFS <- PhaseBreak
- CogniML -> memory infrastructure
- Incident Ledger -> уникальная практика
- WhatsApp Analyzer -> PII masking patterns

up:: [[Каталог всех проектов 2026]]
