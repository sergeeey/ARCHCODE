---
tags:
  - project-card
  - archcode
  - research
  - genomics
  - negative-result
created: '2026-04-12'
updated: '2026-04-16'
status: negative-result
---
# ARCHCODE

**Одно предложение:** 3D-хроматиновая симуляция петлевой экструзии для анализа геномных вариантов. Центральная гипотеза (предсказание патогенности) провалена. Выжившая роль после аудита 2026-05-05: domain-specific negative-result case study + benchmark suite для 3D-genome claims, не второй Skeptic.
**Статус:** Negative Result / Domain Benchmark. Все broad predictor claims убиты; часть узких гипотез остаётся preliminary.
**Стек:** TypeScript (движки), Python (анализ), 49 locus configs, ClinVar, AlphaGenome API
**Где:** D:\ДНК
**GitHub:** github.com/sergeeey/ARCHCODE
**Preprint:** Research Square rs-9090074 (DOI: 10.21203/rs.3.rs-9090074/v1)
**Zenodo:** v2.17 (DOI: 10.5281/zenodo.18908214)
**Длительность:** 5 месяцев (ноябрь 2025 - апрель 2026), 299 коммитов

## Обновление 2026-05-05

Текущая честная оценка проекта: **6.5/10**.

Важно: ARCHCODE не нужно позиционировать как общий продукт для scientific integrity / falsification. Эта ниша уже занята [[Карточка — Nobel Premia Boiko]] и Skeptic Engine. ARCHCODE лучше держать как:

- доменный case study: как strong 3D-genome predictor claim collapsed under falsification;
- reusable benchmark suite для 3D-genome / regulatory-variant models;
- источник уроков, из которых вырос Skeptic / Nobel Premia / AI Research Integrity Checklist.

См. [[ARCHCODE — актуальный контекст 2026-05-05]].

## Что убито (6 claims)

| Claim | Дата | Причина |
|-------|------|---------|
| AUC=0.977 как предсказание | 7 апреля | Category baseline=0.98 без физики |
| Router Class B (27 VUS) | 15 апреля | Matched-control p=0.996 |
| H-01 P(s) exponent shift | 15 апреля | 0/3 within-category значимых |
| H-14 sensitivity map | 15 апреля | rho=0.72-0.81 с occupancy (floor compression) |
| Cross-locus transfer | Апрель | 0% sensitivity на 8/9 локусах |
| Pearl claim | 16 апреля | Unmatched test, untestable (0 benign promoter в HBB) |

## Что выжило

| Компонент | Ценность |
|-----------|----------|
| Validation suite (30 тестов) | 8/10 — domain-specific benchmark для 3D-genome моделей |
| Falsification methodology | 9/10 как урок/методология, но главный горизонтальный бренд = Skeptic / Nobel Premia |
| Taxonomy Class A-E | 5/10 — концептуальная рамка слепых зон |
| Hi-C корреляция (r=0.28-0.59) | 6/10 — модель воспроизводит структуру |
| Кодовая база (49/49 тестов) | 7/10 — working software |
| 17 уроков | 8/10 — чеклист для AI-assisted science |

## Корневая причина провала

effectStrength = f(category) на входе модели. LSSIM на выходе = эхо входной категории. Физика (петлевая экструзия, CTCF, Kramer) добавляет около 0 сверх occupancy landscape. Sensitivity map повторяет входные данные (rho=0.72-0.81 на non-floor бинах).

## Главные уроки

1. Проверяй baseline в первый день (сэкономило бы 4 месяца)
2. AUC более 0.95 на биоданных = почти всегда confound
3. AI усиливает confirmation bias (phantom ref, MPRA hallucination, mock без пометки)
4. Effort не равно evidence (299 коммитов не заменяют 1 matched-control)
5. Self-falsification до рецензии = лучшая стратегия

## Мост к Nobel Premia Boiko

Работа над ARCHCODE научила выявлять category confounds, тестировать baselines, делать matched-control. Эти навыки из fraud detection в финансах (VeriFind) + опыт самофальсификации в геномике привели к созданию Nobel Premia Boiko — инструмента для обнаружения статистических артефактов в научных данных.

## Варианты закрытия

- A: Negative result paper (PLOS ONE, F1000Research)
- B: Domain benchmark / methods paper для 3D-genome model claims
- C: Архивировать (DOI есть, preprint есть)

## Связи

- [[Карточка — Nobel Premia Boiko]] — falsification methodology перенесена
- [[ARCHCODE — актуальный контекст 2026-05-05]] — текущая стратегия и разведение со Skeptic
- [[Карточка — VeriFind 2026]] — fraud detection опыт
- [[10 уроков ARCHCODE — MOC]] — 17 детальных уроков
- [[Каталог всех проектов 2026]]

up:: [[Каталог всех проектов 2026]]
