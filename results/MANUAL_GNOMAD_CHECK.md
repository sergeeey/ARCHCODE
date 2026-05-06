# Manual gnomAD Browser Check — 15 Sample Pearls

**Цель:** Проверить вручную через gnomAD browser, т.к. API не работает (100% timeouts).

**Время:** ~15 минут (1 мин на вариант)

---

## Инструкции

Для каждого варианта:

1. **Открой URL** в браузере
2. **Дождись загрузки** (~5-10 сек)
3. **Проверь статус:**
   - ❌ "Variant not found" → запиши "NOT_IN_GNOMAD"
   - ✅ Данные отображаются → запиши AC и AF
4. **Запиши результат** в таблицу ниже

---

## Варианты для проверки (15 простых SNVs)

| # | ClinVar ID | Position | Ref | Alt | gnomAD v4 URL | AC | AF | Status |
|---|------------|----------|-----|-----|---------------|----|----|--------|
| 1 | VCV003766487 | 5226598 | G | T | [Check](https://gnomad.broadinstitute.org/variant/11-5226598-G-T?dataset=gnomad_r4) | | | |
| 2 | VCV000801186 | 5226598 | G | C | [Check](https://gnomad.broadinstitute.org/variant/11-5226598-G-C?dataset=gnomad_r4) | | | |
| 3 | VCV002664746 | 5226613 | G | C | [Check](https://gnomad.broadinstitute.org/variant/11-5226613-G-C?dataset=gnomad_r4) | | | |
| 4 | VCV000811500 | 5226613 | G | T | [Check](https://gnomad.broadinstitute.org/variant/11-5226613-G-T?dataset=gnomad_r4) | | | |
| 5 | VCV000618675 | 5226643 | C | G | [Check](https://gnomad.broadinstitute.org/variant/11-5226643-C-G?dataset=gnomad_r4) | | | |
| 6 | VCV000015471 | 5227099 | T | C | [Check](https://gnomad.broadinstitute.org/variant/11-5227099-T-C?dataset=gnomad_r4) | | | |
| 7 | VCV000015470 | 5227099 | T | G | [Check](https://gnomad.broadinstitute.org/variant/11-5227099-T-G?dataset=gnomad_r4) | | | |
| 8 | VCV000869288 | 5227100 | T | G | [Check](https://gnomad.broadinstitute.org/variant/11-5227100-T-G?dataset=gnomad_r4) | | | |
| 9 | VCV000869290 | 5227101 | A | G | [Check](https://gnomad.broadinstitute.org/variant/11-5227101-A-G?dataset=gnomad_r4) | | | |
| 10 | VCV000015466 | 5227102 | T | C | [Check](https://gnomad.broadinstitute.org/variant/11-5227102-T-C?dataset=gnomad_r4) | | | |
| 11 | VCV000801184 | 5227142 | G | A | [Check](https://gnomad.broadinstitute.org/variant/11-5227142-G-A?dataset=gnomad_r4) | | | |
| 12 | VCV002506212 | 5227157 | G | T | [Check](https://gnomad.broadinstitute.org/variant/11-5227157-G-T?dataset=gnomad_r4) | | | |
| 13 | VCV000036284 | 5227157 | G | A | [Check](https://gnomad.broadinstitute.org/variant/11-5227157-G-A?dataset=gnomad_r4) | | | |
| 14 | VCV000036287 | 5227158 | G | A | [Check](https://gnomad.broadinstitute.org/variant/11-5227158-G-A?dataset=gnomad_r4) | | | |
| 15 | VCV000036285 | 5227158 | G | T | [Check](https://gnomad.broadinstitute.org/variant/11-5227158-G-T?dataset=gnomad_r4) | | | |

---

## Что искать на странице gnomAD

**Если вариант найден:**
```
Population: gnomAD v4.1
├─ Allele Count (AC): [число]
├─ Allele Number (AN): [число]
└─ Allele Frequency (AF): [десятичное число]
```

**Если вариант НЕ найден:**
```
"Variant not found in gnomAD v4"
```

---

## Пример заполнения

| AC | AF | Status |
|----|----|--------|
| 5 | 0.000033 | ULTRA_RARE |
| 0 | N/A | ABSENT |
| — | — | NOT_IN_GNOMAD |

---

## Интерпретация результатов

| AC | AF | Интерпретация |
|----|----|----|
| **0** | N/A | **Отсутствует** в популяции (purifying selection) |
| **1-5** | <0.00004 | **Ultra-rare** (очень сильное давление отбора) |
| **6-50** | 0.00004-0.0003 | **Rare** (сильное давление отбора) |
| **>50** | >0.0003 | **Polymorphic** (нейтральный или балансирующий отбор) |
| **N/A** | N/A | **Не в базе** (может быть недавняя мутация или ошибка координат) |

---

## После завершения проверки

Сохрани заполненную таблицу и мы пересчитаем:

1. **% pearls absent** (AC=0)
2. **% pearls ultra-rare** (AC=1-5, AF<0.00004)
3. **Mean AF** для присутствующих вариантов

Это даст нам **ground truth validation** для claims о purifying selection.

---

**Estimated time:** 15 минут (1 мин/вариант × 15 вариантов)
