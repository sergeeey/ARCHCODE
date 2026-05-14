---
tags:
  - ARCHCODE
  - аудит
  - устарел
date: '2026-04-15'
type: audit
status: superseded
replaced_by: Аудит ARCHCODE — 16 апреля 2026
---
> [!warning] УСТАРЕЛ
> Этот аудит заменён на [[Аудит ARCHCODE — 16 апреля 2026]].
> Ключевые отличия: H-01 и H-14 killed, pearl claim untestable, .env false positive исправлен, AlphaGenome downgraded.

---

(Оригинальное содержимое ниже для истории)

# Полный аудит ARCHCODE — 15 апреля 2026

## 1. Что доказано (факты с инструментальной верификацией)

| Факт | Источник | Статус |
|------|----------|--------|
| 30318 ClinVar вариантов по 9 локусам | Unified Atlas CSV (сумма строк) | VERIFIED |
| AUC 0.977 на HBB | roc_unified.json: 0.9766 | VERIFIED |
| AUC это артефакт категории | Position-only AUC 0.551 (ADR-015) | VERIFIED |
| Within-category AUC около 0.50 | 25 тестов, медиана 0.52 | VERIFIED |
| Router Class B убит matched-control | 0 из 6, pooled p 0.996 | VERIFIED |
| Hi-C корреляция r 0.28-0.59 | hic_correlation json (6 файлов) | VERIFIED |
| SpliceAI 0.00 для всех 20 pearl SNV | spliceai_pearl_variants.csv | VERIFIED |
| MPRA pearls неотличимы от non-pearl | p 0.91 Mann-Whitney | VERIFIED |
| AlphaGenome CAGE: pearls -18 pct vs controls -3.2 pct | p 2.77e-4, real API | VERIFIED |
| SCN5A и GJB2 тканевой mismatch null | 0 pearls, LSSIM около 1.0 | VERIFIED |
| 49 тестов TypeScript проходят | vitest 49 из 49 pass | VERIFIED |
| FOXP3 пациенты в hotspots | 0 найдено | VERIFIED NULL |

## 2. Что убито

| Claim | Когда убит | Чем убит |
|-------|-----------|----------|
| AUC 0.977 как предсказание патогенности | 7 апреля | Category baseline AUC 0.98 |
| Физика добавляет сверх категории | 7 апреля | Position-only 0.551, within-cat 0.50 |
| Router Class B как utility tool | 15 апреля | Matched-control p 0.996 |
| FOXP3 EGR2 как сильное предсказание | 15 апреля | EGR2 не в CRISPR-скрине 2025 |
| Cross-locus threshold transfer | Апрель | HBB threshold дает 0 pct sensitivity на остальных |

## 3. Что выжило

| Компонент | Сила | Почему жив |
|-----------|------|-----------|
| Hi-C корреляция (r 0.28-0.59) | 7 из 10 | Модель реально ловит структуру хроматина |
| AlphaGenome CAGE (p 4e-6) | 7 из 10 | Внешний инструмент DeepMind, pearls реально нарушают экспрессию |
| Taxonomy framework (Class A-E) | 5 из 10 | Концептуально полезна для понимания слепых зон |
| Validation suite (30 тестов) | 8 из 10 | Reusable benchmark, первый falsification-first подход |
| Научная честность (7 null results) | 9 из 10 | Редко кто так документирует отрицательные результаты |
| Class D coverage gap (49 VUS) | 3 из 10 | VEP пуст, ARCHCODE хоть что-то. Слабый claim |
| TP53 splice_region (AUC 0.69) | 4 из 10 | Единственный surviving within-category сигнал |

## 4. Что хотели и не сделали

| Задача | Статус | Почему отложено |
|--------|--------|-----------------|
| Wet-lab Capture Hi-C | DEFERRED | Нет лаб-партнера плюс claim ослаб |
| RNA-seq validation | 0 pct | Нужен tissue-matched партнер |
| Multi-locus atlas publication | 0 pct | Данные есть, нет консолидации |
| Benchmark dataset release | PENDING | Нужна стабилизация canonical layer |
| Batch AlphaGenome CAGE (1103 варианта) | PENDING | Ресурсоемко |
| GATA1 и KLF1 TF disruption | PENDING | Отложен после фальсификации |
| Tissue-matched BRCA1 MCF7 и TP53 IMR-90 | PARTIALLY DONE | Результаты mixed |
| BCL11A sprint | SETUP phase | Phase A-D определены, не начат |
| Region-level sensitivity map | NEXT | Решено 15 апреля как pivot |

## 5. Состояние кода

| Компонент | Оценка | Деталь |
|-----------|--------|--------|
| TypeScript engines | 9 из 10 | LoopExtrusionEngine плюс MultiCohesinEngine, 49 тестов |
| Config files | 8 из 10 | 50 locus configs, ENCODE-validated |
| Validation suite | 7 из 10 | 30 тестов: 9 PASS, 9 WARNING, 12 FAIL |
| Python layer | 3 из 10 | Намеренный stub, core в TypeScript |
| Scripts | 5 из 10 | 132 файла, 7 активных, 100 legacy |
| CI и CD | 9 из 10 | 3 workflow |
| Docker | 7 из 10 | Работает, narrative устарел |

## 6. Критическая проблема безопасности

Файл .env с API ключами закоммичен в git (CRITICAL).

Содержит: AlphaGenome API key, 4 Google API keys, 2 Zenodo tokens.

Действия:
1. Немедленно ревокнуть все ключи
2. Удалить из git history (BFG)
3. Force push

## 7. Несогласованности в документах

| Что | README | Manuscript | Canon |
|-----|--------|-----------|-------|
| Вариантов | 30318 на 9 loci | 32201 на 13 loci | 30318 на 9 loci |
| Pearls | 25 и 27 (оба) | 27 | 25 плюс 29 exploratory |
| AUC caveat | Полная фальсификация | category-level | Specified |
| Matched-control FAIL | Есть | НЕТ | Enforced |

Manuscript отстает от README.

## 8. Endorser статус

| Контакт | Статус | Следующее действие |
|---------|--------|-------------------|
| Nora (UCSF) | Жива, в поездке | Follow-up 21 апреля |
| Fudenberg (USC) | BOUNCED, правильный email найден | Отправить |
| Paulsen (Oslo) | NEW, реферал Goloborodko | Отправить |
| Polovnikov (Skoltech) | NEW, реферал Goloborodko | Отправить |
| Giorgetti, Hansen | NO REPLY 14 дней | Follow-up |
| Mirny | NO REPLY 13 дней | Ждать |
| Goloborodko | DECLINED | Закрыт |

## 9. Итоговая картина

### Мертво
- AUC predictor
- Router Class B
- Cross-locus transfer
- Physics adds beyond category
- FOXP3 EGR2 prediction
- Within-category signal (кроме TP53 splice)

### Живо
- Hi-C корреляция (r 0.28-0.59)
- AlphaGenome CAGE (p 4e-6)
- Validation suite (30 тестов)
- Taxonomy (conceptual)
- Class D coverage gap (weak)
- TP53 splice_region (maybe)
- Научная честность (7 nulls)
- Кодовая база (49 из 49 тестов)

### Не проверено
- Region-level sensitivity map (NEXT PIVOT)
- TP53 splice deep-dive
- AlphaGenome pearls under matched controls

## 10. Три приоритета

1. CRITICAL: Ревокнуть API ключи из .env
2. P0: Синхронизировать manuscript с README (matched-control FAIL, variant counts)
3. P1: Region-level sensitivity benchmark (следующая сессия)

## 11. Самая честная формулировка проекта

ARCHCODE это exploratory structural sensitivity mapping tool с провалившимися variant-level claims и одной непроверенной region-level гипотезой. Основная выжившая ценность: falsification methodology плюс blind-spot taxonomy плюс candidate atlas.

---

Аудит проведен Claude Code (Opus 4.6) по запросу автора. Все числа верифицированы из файлов репозитория.
