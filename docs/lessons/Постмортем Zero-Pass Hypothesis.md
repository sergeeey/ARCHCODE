---
tags:
  - lessons
  - postmortem
  - zero-pass
  - plasma-turbulence
created: '2026-04-12'
project: Zero-Pass Hypothesis
---
# Постмортем Zero-Pass Hypothesis

**Проект:** Топологическое замыкание для сжимаемой плазменной турбулентности (compressible MHD)
**Период:** 2026-04-11 20:41 — 2026-04-12 01:30 (5 часов)
**Статус:** KILLED. Гипотеза опровергнута тремя способами.

## Что это

Вопрос: может ли *топология* когерентных структур (числа Бетти, Euler characteristic, persistence) лучше предсказывать межмасштабный перенос энергии в плазменной турбулентности, чем стандартные локальные инварианты (Q, R, div u)?

Pipeline: 2D pseudo-spectral MHD solver -> coarse-graining -> TDA features -> ML models -> kill criteria.

## Результат

- Phase 1: TDA дала -25 pp vs baseline (хуже, не лучше)
- Phase 1b: Tensorial alignment +0.15 pp (ниже порога 2 pp)
- Phase 2: SINDy closure — OOD R2 отрицательный (хуже чем среднее)
- Placebo: shuffle TDA within div(u) bins = Delta 0.000

## Положительные уроки

1. **Kill criteria за 5 часов** — от идеи до verdict. Hard kill: Delta < 3 pp. Результат: -24.75 pp
2. **Три уровня фальсификации** — TDA, alignment, SINDy. Три смерти = железобетонный negative
3. **Placebo control встроен** — shuffle within bins. Именно то чего не было в ARCHCODE
4. **Strong baseline убивает рано** — M2 (95.2%) убил гипотезу до placebo
5. **Папка "Не подтвердились"** — mindset: гипотезы проверяются, не доказываются

## Отрицательные уроки

6. **64x64 grid слишком мал** — M_s <= 0.35, TDA может не иметь структур на малой сетке
7. **OOD тест узкий** — Roberts vs stochastic, нужен разный Mach/plasma beta/solver
8. **Нет внешних данных** — CATS/TURB-MHD перечислены но не использованы
9. **Paper не написан** — clean negative result публикуем, но deliverable не создан

up:: [[Каталог проектов — 7 постмортемов]]
