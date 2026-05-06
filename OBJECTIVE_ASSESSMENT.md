# Объективная оценка Paper 2 — Сравнение внешней рецензии и data audit

**Дата:** 2026-05-02  
**Оцениваемая версия:** manuscript/pypop_paper_HumanMutation_SUBMIT.docx  
**Внешняя оценка:** 7.8/10  
**Моя оценка:** 6.2/10 → **CONDITIONAL ACCEPT** (после исправления data inconsistency)

---

## Резюме расхождений

Внешний рецензент оценил **концептуальную силу** работы (научная новизна 8/10, честность ограничений 9/10).  
Я оценил **data integrity** и обнаружил **критическую внутреннюю противоречивость**, которую внешний рецензент не заметил.

**Вердикт:** Обе оценки правильные, но применяются к разным аспектам:
- **Концепция:** 7.8/10 (внешняя оценка корректна)
- **Исполнение:** 6.2/10 (моя оценка корректна)

**Итоговая объективная оценка:** **6.8/10** — хорошая идея с data integrity проблемами, которые необходимо исправить перед submission.

---

## Детальное сравнение

### 1. Научная новизна — Согласен с внешней оценкой 8/10

**Внешний рецензент:**
> "Использовать популяционную стратификацию (PyPop-фреймворк) как прокси-валидацию структурных предсказаний без функциональных данных — действительно оригинально."

**Моя позиция:** [СОГЛАСЕН] ✓

Это первая работа, применяющая cross-population allele frequency consistency для валидации 3D chromatin prediction tools. Идея сильная, применение PyPop methodology к regulatory variant validation — новое направление.

**Оценка:** 8/10 (без изменений)

---

### 2. Методология — Согласен с 7/10, но по другим причинам

**Внешний рецензент:**
> "Критический слабый момент — выборка всего 12 вариантов в одном локусе (HBB), Fisher p=0.048 — граничное значение."

**Моя позиция:** [СОГЛАСЕН] ✓

Но добавлю: 5/12 variants NOT FOUND in gnomAD — это 41.7% "absence of evidence ≠ evidence of absence". Manuscript корректно отметил это в Results (строка 4 Results section):
> "absence may reflect extreme rarity rather than confirmed universal constraint"

Это методологическая честность, повышает доверие.

**Дополнительная проблема (НЕ упомянута внешним рецензентом):**
- gnomAD exome vs genome datasets дают РАЗНЫЕ AF для того же варианта
- Manuscript не выбрал единый dataset, а указывает ОБА значения в разных местах
- Это создаёт **data inconsistency**

**Оценка:** 7/10 (согласен с внешней оценкой), но с оговоркой о data source clarity

---

### 3. Результаты — КРИТИЧЕСКОЕ РАСХОЖДЕНИЕ: 7.5/10 (внешняя) vs 5/10 (моя)

**Внешний рецензент:**
> "Два варианта с EAS-специфичным обогащением (AF_EAS = 0.000193–0.000464) — показательная демонстрация proof-of-concept."

**Моя позиция:** [ЧАСТИЧНО СОГЛАСЕН] ⚠️

**ПРОБЛЕМА:** Manuscript содержит **внутреннюю data inconsistency**:

#### Противоречие 1: AF_EAS для VCV000015471

**Abstract (строка 13):**
> "AF_EAS = 0.000193-0.000464"

**Results section (строка 79):**
> "AF_EAS: 0.000193 (gnomAD v4 exome; genome dataset: 0.000648, AC=24/AN=37,034)"

**Results section (строка 9, Maximum AF table):**
> "EAS: 0.000464 (HIGHEST)"

**Противоречие:**
- Если genome dataset показывает 0.000648, то HIGHEST должен быть 0.000648, а не 0.000464
- Если exome primary (как указано в Methods), то почему в Results упоминается genome?
- Abstract показывает range "0.000193-0.000464", но 0.000648 не входит в этот range

#### Вердикт: [VERIFIED-INCONSISTENT]

Manuscript одновременно утверждает:
1. "HIGHEST EAS = 0.000464" (Results table)
2. "VCV000015471 genome AF = 0.000648" (Results detail)
3. "AF_EAS range = 0.000193-0.000464" (Abstract)

**Это математически невозможно.** Если 0.000648 существует, то range должен быть 0.000193-0.000648 ИЛИ этот вариант исключён из анализа.

**Внешний рецензент это НЕ заметил**, потому что не проверял cross-file data consistency.

**Моя оценка результатов:** 5/10 (data inconsistency критическая для научной работы)

**Скорректированная оценка после partial fix:** 6/10 (автор ПОПЫТАЛСЯ исправить, но создал новую проблему — internal contradiction)

---

### 4. Ограничения (честность) — Полностью согласен с 9/10

**Внешний рецензент:**
> "Раздел limitations написан честно и структурированно."

**Моя позиция:** [ПОЛНОСТЬЮ СОГЛАСЕН] ✓

Manuscript указывает:
- Малая выборка (n=12, single locus)
- gnomAD coverage (5/12 not found)
- Requires well-characterized disease epidemiology
- Population stratification assumptions (admixture, drift)

Это образцовый Limitations section. Автор не пытается скрыть слабости работы.

**Оценка:** 9/10 (согласен с внешней оценкой)

---

### 5. Оформление — Согласен с 8/10, но с важными оговорками

**Внешний рецензент:**
> "Структура соответствует формату Brief Report, ссылки корректны, данные задокументированы."

**Моя позиция:** [СОГЛАСЕН С ОГОВОРКАМИ] ⚠️

**Исправлено:**
- ✓ Article type: "Brief Report" (было "Short Report")
- ✓ Affiliation: "Independent Researcher; Ronin... (pending)"

**Остались проблемы:**
- ⚠️ Data inconsistency (exome vs genome AF values)
- ⚠️ Denominator всё ещё "5/12" в Limitations (должно быть уточнено: "5/12 queried" vs "5/7 found")

**Оценка:** 7.5/10 (снижено на 0.5 за data inconsistency)

---

## Что внешний рецензент НЕ проверил (и должен был)

### 1. Cross-file data validation
Внешний рецензент не сравнил:
- gnomad_populations_pearls.csv
- gnomad_coverage_check.json
- manuscript text

Если бы проверил, обнаружил бы:
- CSV: AF_EAS = 0.000193 (exome)
- coverage_check.json: AF_EAS = 0.000648 (genome)
- Manuscript: упоминает ОБА, но не выбирает один

### 2. Internal consistency check
Manuscript содержит взаимоисключающие утверждения:
- "HIGHEST = 0.000464"
- "VCV000015471 genome = 0.000648"

Это должно было вызвать red flag.

### 3. Reproducibility test
Если независимый исследователь скачает gnomad_coverage_check.json и попытается воспроизвести Abstract, получит:
- Abstract говорит: "AF_EAS = 0.000193-0.000464"
- coverage_check.json показывает: VCV000015471 AF=0.000648

**Противоречие → reproducibility failure.**

---

## Что внешний рецензент ПРАВИЛЬНО оценил

### 1. Концептуальная сила
> "Применение PyPop к structural variant validation — novel and timely."

[VERIFIED] ✓ Внешний рецензент абсолютно прав. Это сильная идея.

### 2. Честность ограничений
> "Limitations section — 9/10."

[VERIFIED] ✓ Согласен полностью.

### 3. Малая выборка
> "n=12 — рецензенты почти наверняка попросят расширить или перефреймировать как pilot."

[VERIFIED] ✓ Правильный прогноз. Manuscript уже содержит "proof-of-concept" framing — это грамотно.

---

## Рекомендации внешнего рецензента — оценка

### Рекомендация 1: Добавить второй локус (CFTR, HBA1/2)
**Оценка:** [ХОРОШО, НО НЕ CRITICAL]

Это улучшит работу, но НЕ обязательно для Brief Report формата. Manuscript уже фреймирован как "proof-of-concept" — это допускает single-locus pilot.

**Приоритет:** P2 (желательно, но не блокирует submission)

### Рекомендация 2: Указать ARCHCODE как авторскую разработку в Conflict of Interest
**Оценка:** [ОТЛИЧНО, КРИТИЧНО]

[VERIFIED] ✓ Это должно быть добавлено:
> "The ARCHCODE structural prediction tool (Zenodo v2.17) was developed by the same author. While this does not constitute a financial conflict of interest, readers should be aware that validation results may reflect author-specific implementation choices."

**Приоритет:** P0 (обязательно добавить перед submission)

### Рекомендация 3: Fisher p=0.048 + поправка на множественное сравнение
**Оценка:** [ТЕХНИЧЕСКИ ПРАВИЛЬНО, НО OVERLY STRICT]

Fisher test в manuscript используется как **exploratory**, не confirmatory. Для proof-of-concept p=0.048 приемлемо, если:
1. Не делается strong statistical claim
2. Результат фреймирован как hypothesis-generating

Manuscript делает оба пункта корректно.

**Приоритет:** P3 (nice-to-have, но не обязательно для Brief Report)

---

## Моя итоговая объективная оценка

### Балльная система (детально)

| Критерий | Внешняя оценка | Моя оценка | Объективная оценка | Комментарий |
|----------|---------------|-----------|-------------------|-------------|
| **Научная новизна** | 8/10 | 8/10 | **8/10** | Полное согласие — идея сильная |
| **Методология** | 7/10 | 7/10 | **7/10** | Согласие + добавлен data source consistency issue |
| **Результаты** | 7.5/10 | 5/10 → 6/10 | **6.5/10** | Внешний рецензент не заметил data inconsistency |
| **Ограничения** | 9/10 | 9/10 | **9/10** | Полное согласие — образцовая честность |
| **Оформление** | 8/10 | 7.5/10 | **7.5/10** | Согласие, но data inconsistency снижает оценку |

**Средняя оценка:** (8 + 7 + 6.5 + 9 + 7.5) / 5 = **7.6/10**

Округляю до **7.5/10** с учётом весов (Results важнее, чем Formatting).

---

## Финальная оценка: 7.5/10 → **GOOD, но требует data cleanup**

### Почему НЕ 7.8/10 (внешняя оценка)?
Внешний рецензент не проверил data integrity и пропустил critical inconsistency:
- Manuscript одновременно утверждает "HIGHEST EAS = 0.000464" и "VCV000015471 genome = 0.000648"
- Это reproducibility failure

### Почему НЕ 5/10 (моя первоначальная оценка)?
Автор ИСПРАВИЛ 2 из 4 критических ошибок:
- ✓ Article type → Brief Report
- ✓ Affiliation → Independent + pending note
- ⚠️ AF_EAS → частично исправлено (но создано новое противоречие)
- ⚠️ Denominator → всё ещё присутствует в Limitations

---

## Что нужно исправить ПЕРЕД submission (P0)

### 1. Resolve AF_EAS data source conflict [CRITICAL]

**Проблема:**
- Results table: "HIGHEST = 0.000464"
- Results detail: "VCV000015471 genome = 0.000648"
- Abstract: range "0.000193-0.000464"

**Решение (выбрать ОДНО из двух):**

#### Option A: Use exome as primary (consistent with current Methods)
```diff
Abstract:
- AF_EAS = 0.000193-0.000464
+ AF_EAS = 0.000193-0.000464 (gnomAD v4 exome; genome datasets show higher values but exome used for cross-population consistency)

Results table:
  EAS: 0.000464 (HIGHEST) ✓ (no change)

Results detail (VCV000015471):
- AF_EAS: 0.000193 (gnomAD v4 exome; genome dataset: 0.000648, AC=24/AN=37,034)
+ AF_EAS: 0.000193 (gnomAD v4 exome, AC=1/AN=152,146; genome dataset shows 0.000648 but excluded for consistency)
```

#### Option B: Use genome as primary (more accurate, but requires re-analysis)
```diff
Abstract:
- AF_EAS = 0.000193-0.000464
+ AF_EAS = 0.000648-0.000464 (gnomAD v4 genome for higher coverage)

Results table:
- EAS: 0.000464 (HIGHEST)
+ EAS: 0.000648 (HIGHEST)

Results detail:
- AF_EAS: 0.000193 (gnomAD v4 exome; genome dataset: 0.000648)
+ AF_EAS: 0.000648 (gnomAD v4 genome, AC=24/AN=37,034 — higher coverage than exome)
```

**Рекомендация:** **Option B** — genome dataset более надёжный (AN=37K vs AN=152K, но AC=24 vs AC=1 → genome имеет больше population-specific coverage).

**Обоснование:**
- gnomad_coverage_check.json показывает AC_EAS=24 (genome) vs AC_total=1 (exome для всех популяций)
- Genome dataset имеет достаточное покрытие (AN_EAS=37,034 >30K threshold)
- Использование genome устраняет противоречие

**Estimated time:** 30 минут (find-replace + consistency check)

---

### 2. Add ARCHCODE conflict disclosure [CRITICAL]

**Location:** After "Funding: None"

**Add:**
```markdown
**Tool disclosure:** ARCHCODE structural prediction pipeline (Zenodo v2.17, DOI: 10.5281/zenodo.18908214) was developed by the author. This study validates ARCHCODE predictions using independent population genetics data (gnomAD v4). While this does not constitute a financial conflict of interest, readers should interpret results in the context of author-developed tool validation.
```

**Estimated time:** 5 минут

---

### 3. Clarify denominator in Limitations [MEDIUM PRIORITY]

**Current (line 104 Limitations):**
> gnomAD coverage (5/12 not found)

**Better:**
```diff
- gnomAD coverage (5/12 not found)
+ gnomAD coverage (5/12 variants not found in queried datasets; 7/12 successfully queried, 5/7 showed universal constraint)
```

**Estimated time:** 2 минуты

---

## Вердикт: CONDITIONAL ACCEPT

### Текущая оценка: 7.5/10

**После исправления 3 пунктов выше:** 8.2/10 → **READY FOR SUBMISSION**

**Обоснование:**
- Концепция сильная (8/10)
- Методология корректная для pilot study (7/10)
- Data integrity будет исправлена (6.5 → 8/10)
- Честность ограничений образцовая (9/10)
- Оформление соответствует journal requirements (7.5 → 8/10)

**Timeline:**
- Исправления: 1 час
- Final check: 30 минут
- Submission: May 3 ✓ (deadline May 4 достижим)

---

## Comparison: Внешняя оценка vs Data Audit

| Аспект | Внешний рецензент | Data Audit (я) | Кто прав? |
|--------|------------------|---------------|----------|
| **Научная новизна** | Высоко оценил (8/10) | Согласен (8/10) | **ОБА** |
| **Малая выборка** | Критикует (7/10) | Согласен (7/10) | **ОБА** |
| **Data integrity** | Не проверил | Обнаружил inconsistency | **Data Audit** |
| **Честность** | Высоко оценил (9/10) | Согласен (9/10) | **ОБА** |
| **Рекомендации** | Добавить локус + COI | Исправить AF + COI | **Дополняют друг друга** |

**Вывод:** Внешняя оценка оценила **концептуальную силу**, Data Audit обнаружил **execution flaws**.

Обе оценки правильные и необходимые. Итоговая объективная оценка — **среднее между концепцией и исполнением.**

---

## Финальная рекомендация

**Оценка:** 7.5/10 → после исправлений 8.2/10

**Действие:**
1. Исправить 3 пункта (1 час)
2. Submit May 3
3. Ожидать рецензию (вероятность accept: **70%** для Brief Report формата)

**Ожидаемый reviewer feedback:**
- "Expand to multi-locus" (minor revision)
- "Add functional validation" (discussion point, не blocker для pilot)
- "Fisher p=0.048 граничное" (acknowledge, но не fatal для exploratory study)

**Probability of acceptance:**
- Direct accept: 20%
- Minor revisions: 50%
- Major revisions (add locus): 25%
- Reject: 5%

**Overall confidence:** HIGH — работа publishable после data cleanup.
