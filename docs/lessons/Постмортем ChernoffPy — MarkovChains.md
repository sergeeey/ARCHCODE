---
tags:
  - lessons
  - postmortem
  - chernoffpy
  - math
  - finance
created: '2026-04-12'
updated: '2026-04-13'
project: ChernoffPy
---
# Постмортем ChernoffPy / MarkovChains

**Проект:** ChernoffPy v0.2.0 — pricing финансовых деривативов через Chernoff operator splitting с certified error bounds. PyPI-пакет.
**Статус:** Released, но с known architectural issue (Heston CFL instability).
**Стек:** Python 3.11+, NumPy, SciPy, PyTorch (GPU). 563 тестов (после аудита 12 апреля), CI/CD, MkDocs.

## Что это

Математическая библиотека: European, barrier, double-barrier, American, Heston, Bates option pricing + certified error bounds. Базируется на формулах произведения Чернова — связь с работами Ремизова (МГУ/ВШЭ).

## Положительные уроки

1. **Единственный зарелизенный проект из 27** — PyPI 0.2.0, CI/CD, MkDocs, release guide
2. **Verification Reset** — формализованный trust layer для 16 claims (VERIFIED/RETRACTED/INFERRED)
3. **18 фаз с отдельными ТЗ** — инкрементальная разработка с Spec_Index.md навигацией
4. **563 теста** — correctness определяется тестами, не документацией
5. **Minimal scope = единственный release** — 34 модуля, не 157 как Reflexio
6. **VeriFind интеграция** — deployed в production (Truth Gate + Certified Intervals)

## Отрицательные уроки

7. **Heston CFL instability** — architectural issue замаскированный как "плохой параметр в тесте". CFL ratio 16.13 при target 0.5. Fix n_steps 50->200 = костыль. Нужен CFL warning в API.
8. **Multi-agent аудит провалил 3/4 kill criteria** — 40% false positives, 0 unique critical bugs vs baseline, человек обязателен. Для 34 модулей baseline (pytest) дешевле.
9. **"Fail loud" не полностью реализован** — Heston молча diverges до 1e123 без предупреждения.
10. **Нет arXiv paper** — library без paper = ограниченный академический impact
11. **10+ TZ файлов** — документация фрагментирована

## Уникальные практики (переносимые)

- Verification Reset ledger для disputed claims
- Phased specs + Spec_Index navigation
- Certified error bounds как differentiator
- Minimal scope as success factor

up:: [[Каталог всех проектов 2026]]
