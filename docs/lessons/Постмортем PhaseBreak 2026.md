---
tags:
  - lessons
  - postmortem
  - phasebreak
  - lppls
  - finance
created: '2026-04-12'
project: PhaseBreak 2026
---
# Постмортем PhaseBreak 2026

**Проект:** Cross-domain phase transition detection через LPPLS (Log-Periodic Power Law Singularity)
**Период:** 2026-03-28 — 2026-04-08 (~2 сессии, 10 часов)
**Статус:** QUALIFIED SUCCESS. 4/5 gates passed. Paper ready, awaiting endorsement.

## Что это

Детекция пузырей и критических переходов через уравнение Sornette. 5 доменов: finance, commodities, housing, geology, fraud. Multi-window confidence, HMM-gated ensemble, forward validation. 268 тестов, FastAPI + React dashboard.

## Результат

- Finance: precision 78%, recall 64%
- Forward validation (unseen 2024): 100% precision, 33% recall
- Cross-domain universality: KS p > 0.05 (cannot reject, n=4-13)
- Live predictions locked: TSLA tc=2 Aug, NVDA tc=20 Sep 2026

## Положительные уроки

1. **От нуля до paper за 2 сессии** — baseline проверен сразу, проект летит
2. **5 Gate criteria заранее** — 4/5 passed, 1 честно помечен NO
3. **Forward validation на unseen данных** — locked predictions ДО результата
4. **Честные лимитации** — crash recall 23%, meme stocks = immutable blind spot
5. **Nikkei postmortem** — пропущен на 0.006 quality points, root cause + 4 fixes
6. **Red team аудит** — metric leakage + hardcoded mocks найдены до публикации
7. **Ablation по компонентам** — вклад каждого слоя оценён отдельно

## Отрицательные уроки

8. **Cross-domain universality на n=4-13** — нулевая мощность KS теста
9. **2 из 5 доменов декоративные** — fraud (synthetic), geology (no ground truth)
10. **AI Council = complexity без accuracy gain** — 75% не лучше baseline
11. **arXiv endorsement снова блокирует** — publication target не решён заранее

up:: [[Каталог проектов — 7 постмортемов]]
