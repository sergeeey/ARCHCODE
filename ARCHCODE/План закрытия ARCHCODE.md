---
tags:
  - ARCHCODE
  - план
  - закрытие
  - negative-result
date: '2026-04-16'
type: action-plan
status: active
---
# План закрытия ARCHCODE

## Статус: проект закрывается как negative result

Решение принято 16 апреля 2026 после финального аудита (Tracy Reset + код-аудит).
Все 6 гипотез убиты. Модель = category engine, не physics-based predictor.

---

## Проблема: публикации содержат устаревшие claims

| Документ | Что написано | Реальность |
|----------|-------------|------------|
| Research Square preprint | AUC=0.977 как результат | Category artifact (baseline=0.98) |
| Research Square | Pearl variants как открытие | Untestable (unmatched, pseudo-replicated) |
| Research Square | Complementary layer for interpretation | Не добавляет ценности сверх category+position |
| Manuscript | p=4e-6 без caveat | 11/12 pearls в 73bp кластере, effective n=2-3 |
| Manuscript | ARCHCODE detects structural disruption | Sensitivity map = occupancy (rho=0.72-0.81) |
| Zenodo v2.17 | Код без falsification results | H-01, H-14, matched-control kills не включены |

### P-value конфликт (решён)

- Mann-Whitney (pearl vs benign CAGE): p = 8.32e-06 (в manuscript округлено до 4e-6)
- Welch t-test (те же данные): p = 4.33e-04
- В Obsidian archcode-publication-campaign: p = 2.8e-4 (вероятно другой тест/подвыборка)
- Правильное значение для Mann-Whitney: 8.32e-06
- НО: effective n = 2-3 (11/12 в одном 73bp кластере), сравнение unmatched

---

## План действий

### P0: Обновить Research Square (v2)

- Добавить falsification results в manuscript
- Переписать abstract: AUC caveat, matched-control FAIL, pearl untestable
- Переписать conclusions: negative result framing
- Загрузить новую версию на RS (rs-9090074)
- Оценка: 2-3 часа

### P0: Обновить Zenodo (v2.18)

- Добавить H-01, H-14, matched-control результаты
- Обновить README с финальным статусом
- Загрузить на Zenodo (новая версия, DOI сохраняется)
- Оценка: 1 час

### P1: Финальный коммит

- Пометить проект как closed: negative result
- Включить все результаты сессии 15-16 апреля
- Обновить activeContext как финальный

### P1: Решить по endorsers

- Nora follow-up 21 апреля: стоит ли продолжать если проект closed?
- Вариант: честно написать что проект = negative result, endorsement для negative result paper
- Или: отменить endorsement request

### P2: Negative Result Paper (опционально)

- Переписать как methods paper: validation suite = центральный продукт
- Target: PLOS ONE, F1000Research, или Bioinformatics Application Note
- Или: оставить preprint на RS как есть (после обновления)

---

## Мост к Nobel Premia Boiko

Нарратив для Nobel Premia Boiko about/intro:

Работая над геномным проектом ARCHCODE, столкнулся с проблемой: AUC=0.977 оказался артефактом категориальной переменной. Тривиальный baseline без физики давал 0.98. Пять месяцев работы на ложном фундаменте.

Стал задаваться вопросом: сколько таких артефактов в опубликованных статьях? Имея опыт fraud detection в финансах (VeriFind), применил те же подходы к научным данным.

Результат: Nobel Premia Boiko — инструмент для обнаружения статистических артефактов в omics datasets.

---

## Что выжило (финальный список)

| Компонент | Ценность | Действие |
|-----------|----------|----------|
| Validation suite (30 тестов) | 8/10 | Сохранить, можно выпустить отдельно |
| Falsification methodology | 9/10 | Описать в negative result paper |
| Taxonomy Class A-E | 5/10 | Концептуальная рамка, оставить в manuscript |
| Hi-C корреляция (r=0.28-0.59) | 6/10 | Техническая валидация, не claim |
| 17 уроков | 8/10 | Перенесены в Obsidian lessons |
| Кодовая база (49/49 тестов) | 7/10 | Архив на GitHub |

---

## Таймлайн

- Сегодня-завтра: финальный коммит + Obsidian обновлён
- Эта неделя: обновить manuscript body (частично сделано 15 апреля)
- До 21 апреля: решить по Nora/endorsers
- До конца апреля: загрузить RS v2 + Zenodo v2.18
- Май: решить по negative result paper

---

Создано: 16 апреля 2026
Статус: активный план
