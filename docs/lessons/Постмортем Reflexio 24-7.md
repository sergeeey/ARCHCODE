---
tags:
  - lessons
  - postmortem
  - reflexio
  - product
created: '2026-04-12'
project: Reflexio 24/7
---
# Постмортем Reflexio 24/7

**Проект:** Цифровая память — 24/7 запись речи с телефона, транскрипция, обогащение, дайджест
**Период:** ~2026-01 — ongoing (v0.5.2-beta, live production)
**Статус:** BETA. 157 .py файлов, 697 тестов, 5000+ events, VPS deployment.

## Что это

Телефон записывает речь 24/7. Система транскрибирует (faster-whisper), определяет кто говорит (speaker verification), обогащает (эмоции, темы, задачи через LLM), хранит как structured events. Вечерний дайджест с инсайтами. "О чём я говорил с Маратом в январе?" — находит, суммирует, показывает паттерны.

## Положительные уроки

1. **Incident Ledger** — формализованный реестр: signature + root_cause + guardrail + regression_test
2. **Memory Contract** — ownership model + quality states (trusted/uncertain/garbage/quarantined)
3. **Dogfooding** — автор = пользователь, 5000+ events. Радикально другой feedback loop
4. **Одна honest metric** — trusted_fraction 15.8% (цель >= 0.5)
5. **LLM cascade** — Gemini -> Claude Haiku -> GPT-4o-mini с circuit breakers
6. **Full Audit pipeline** — 7 шагов, воспроизводимый

## Отрицательные уроки

7. **54 markdown файла** — documentation sprawl
8. **tmp/debug в корне** — 6+ db файлов, screenshots, wav в корне проекта
9. **fix:feat > 3:1** — tech debt растёт быстрее чем гасится
10. **Scope creep** — от "запись -> дайджест" до social graph + balance wheel + voice intent
11. **trusted_fraction 15.8%** — 84% данных ненадёжны

up:: [[Каталог проектов — 7 постмортемов]]
