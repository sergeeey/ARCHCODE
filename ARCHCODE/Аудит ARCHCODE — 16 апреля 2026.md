---
tags:
  - ARCHCODE
  - аудит
  - финальный
  - negative-result
date: '2026-04-16'
type: audit
replaces: Аудит ARCHCODE — 15 апреля 2026
---
# Финальный аудит ARCHCODE — 16 апреля 2026

Обновляет и заменяет аудит от 15 апреля. Все данные перепроверены.

## 1. Что доказано

| Факт | Источник | Статус |
|------|----------|--------|
| 30318 ClinVar вариантов по 9 локусам | Unified Atlas CSV | VERIFIED |
| AUC=0.977 на HBB | roc_unified.json | VERIFIED |
| AUC = артефакт категории | Position-only AUC=0.551, baseline=0.98 | VERIFIED |
| Within-category AUC около 0.50 | 25 тестов, медиана 0.52 | VERIFIED |
| Router Class B убит matched-control | 0/6, pooled p=0.996 | VERIFIED |
| H-01 P(s) exponent: 0/3 within-category | h01_ps_exponent_results.json | VERIFIED |
| H-14 sensitivity map = occupancy | rho=0.72 BCL11A, 0.81 HBB (occ более 0.15) | VERIFIED |
| Pearl claim untestable | 0 benign promoter variants в HBB | VERIFIED |
| Hi-C корреляция r=0.28-0.59 | hic_correlation json (6 файлов) | VERIFIED |
| SpliceAI=0.00 для всех 20 pearl SNV | spliceai_pearl_variants.csv | VERIFIED |
| MPRA pearls неотличимы от non-pearl | p=0.91 Mann-Whitney | VERIFIED |
| AlphaGenome CAGE unmatched | 11/12 pearls в 73bp кластере, effective n=2-3 | VERIFIED |
| SCN5A и GJB2 тканевой mismatch null | 0 pearls, LSSIM около 1.0 | VERIFIED |
| 49 тестов TypeScript проходят | vitest 49/49 pass | VERIFIED |

## 2. Что убито (6 claims)

| Claim | Дата | Причина |
|-------|------|---------|
| AUC как предсказание патогенности | 7 апреля | Category baseline=0.98 |
| Физика добавляет сверх категории | 7 апреля | Position-only=0.551, within-cat=0.50 |
| Router Class B (27 VUS) | 15 апреля | Matched-control p=0.996 |
| H-01 P(s) exponent shift | 15 апреля | 0/3 within-category значимых |
| H-14 sensitivity map | 15 апреля | rho=0.72-0.81 с occupancy (floor compression) |
| Pearl = доказанный класс | 16 апреля | Unmatched, untestable, псевдорепликации |

## 3. Что выжило

| Компонент | Сила | Почему |
|-----------|------|--------|
| Validation suite (30 тестов) | 8/10 | Первый reusable benchmark для 3D-genome моделей |
| Falsification methodology | 9/10 | 7+ null results, 24 ADR, integrity protocol |
| Taxonomy Class A-E | 5/10 | Концептуальная рамка для слепых зон |
| Hi-C корреляция | 6/10 | Модель воспроизводит структуру (но не предсказывает) |
| Кодовая база | 7/10 | 49/49 тестов, 3 движка, 49 конфигов |
| 17 уроков | 8/10 | Чеклист для AI-assisted science |

## 4. Исправления к аудиту от 15 апреля

| Пункт | Было (15 апреля) | Стало (16 апреля) |
|-------|-------------------|-------------------|
| AlphaGenome CAGE | 7/10, "живо" | UNTESTABLE, unmatched, pseudo-replicated |
| H-01, H-14 | Не проверены | KILLED (оба) |
| Region-level pivot | NEXT | KILLED (sensitivity=occupancy) |
| .env в git | CRITICAL | FALSE POSITIVE (проверено git log -S, .env никогда не коммитился) |
| Class D (49 VUS) | 3/10, "слабо живо" | Не проверялось matched-control, статус неизвестен |
| TP53 splice_region | 4/10 | Не перепроверялось, может быть last surviving false positive |

## 5. Состояние кода

| Компонент | Оценка |
|-----------|--------|
| TypeScript engines | 9/10 |
| Config files (49) | 8/10 |
| Validation suite | 7/10 (30 тестов: 9 PASS, 9 WARNING, 12 FAIL) |
| Python layer | 3/10 (stub) |
| Scripts | 5/10 (140+ файлов, 7 активных) |
| CI/CD | 9/10 |
| validate_project_canon.py | FAILS (README не соответствует старому канону) |

## 6. Безопасность

.env с API ключами НЕ закоммичен в git (проверено git log -S с реальными значениями ключей). Аудит-агент от 15 апреля дал false positive. Ключи в безопасности, .gitignore работает.

## 7. Endorser статус

| Контакт | Статус |
|---------|--------|
| Nora (UCSF) | Жива, follow-up 21 апреля |
| Fudenberg (USC) | Правильный email найден, не отправлен |
| Paulsen (Oslo) | NEW, реферал, не отправлен |
| Polovnikov (Skoltech) | NEW, реферал, не отправлен |
| Giorgetti, Hansen | NO REPLY 14+ дней |
| Mirny | NO REPLY 13+ дней |
| Goloborodko | DECLINED |

## 8. Финальная формулировка

ARCHCODE — negative result project. Центральная гипотеза (3D-структура хроматина предсказывает патогенность вариантов) провалена на всех уровнях: variant-level, region-level, cross-locus. Модель повторяет входные данные (category -> effectStrength -> LSSIM). Физика добавляет около 0.

Выжившая ценность: validation suite (30 тестов), falsification methodology (24 ADR, 7+ nulls), taxonomy framework (Class A-E), 17 уроков для AI-assisted science.

Мост к Nobel Premia Boiko: навыки выявления confounds и self-falsification перенесены на детекцию фальсификаций в научных данных.

---

Аудит: Claude Code (Opus 4.6), 16 апреля 2026. Все числа из файлов репозитория.
