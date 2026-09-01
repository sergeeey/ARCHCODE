# Active Context — ARCHCODE Project

**Last Updated:** 2026-09-01
**Current Branch:** experiment/spectral-collapse-pilot
**Session Focus:** ⏸️ **PROJECT STILL PAUSED.** No ARCHCODE code/manuscript work resumed. 2026-08-29 session was exploratory/archival (see below), not a resumption. Do NOT raise new ARCHCODE work unprompted.
**Reality source:** session 2026-08-30 (ATR Phase 1 ЗАВЕРШЕНА — kill switch сработал, фреймворк WEAK)

## 🎯 Session 2026-09-01 (часть 3): D1 переспрошен на GTEx v10 — вердикт устоял, pearl нет

**Коммит `5374e63`.** Проверялось ОДНО возражение: не держался ли KILL для D1 на объёме
данных. GTEx v10 даёт 1 841 906 значимых пар против 458 161 в v8 (в 4.02 раза); после
отбора — 218 495 пар и 11 359 вариантов против 87 198 и 4 934.

`run_analysis.py` прогнан **без единой правки**, только другой `--features`. Предсказание
(«вердикт не изменится, ΔAUC < 0.02») записано ДО прогона и устояло:

| | v8 (заморожено `0f8cbb4`) | v10 |
|---|---|---|
| позитивный / негативный контроль | 0.8725 / +0.0006 PASS | 0.8704 / +0.0002 PASS |
| **ΔAUC первичный** | **+0.0004** | **−0.0007** |
| вердикт | KILL | **KILL** |

Знак ΔAUC перевернулся вокруг нуля — величина колеблется около него, а не лежит чуть выше.

**Что НЕ воспроизвелось — pearl-число 0.5063** (`~/.claude/rules/pearl_registry/INDEX.md`,
статус переписан на `weakened`):
- устояло: R² 0.6727→**0.6734**, наклон −0.8212→**−0.8175**, Spearman −0.790→**−0.792**
- НЕ устояло: **AUC остатка контакта 0.5063 → 0.5383** (расстояние от случайности ×6)

Детерминированная половина («контакт на 67% есть функция расстояния») — свойство Hi-C,
подтверждено. Формулировка «канал ПУСТ» была свойством **пары** (Hi-C × разреженный набор
меток v8). Канал не пуст, он слабый. Дешёвая проверка «AUC остатка ≈ 0.5» перестала быть
валидным прокси — она зависит от плотности меток; проверять надо сам ΔAUC.

Это **третий раз за двое суток**, когда число из этого проекта меняет статус: сперва 0.88
(фальсифицировано свипом окна), затем 0.5063 (подтверждено артефактом против двух
оспариваний), теперь 0.5063 же — ослаблено бо́льшим набором данных, а не оспариванием.

**Явная оговорка, записанная в `decision_v10_replication.md`:** TSS из GENCODE v26
(аннотация под v8), eGenes из v10; пересечение 11 897/12 428 (**95.7%**), теряется 531 ген.
Это не чистая репликация. Открыто: V10-A (согласованный GENCODE), V10-B (чем отличаются
потерянные 531).

**D1 остаётся ЗАКРЫТЫМ.** Прогон проверял прежний вердикт, а не переоткрывал гипотезу.

## 🎯 Session 2026-09-01 (часть 2): R7+R6 — загадка 14.2% ЗАКРЫТА разложением
[summarized] **R7 SUCCESS — замкнутая форма выведена и проверена.** При аддитивном шуме, N→∞:
[summarized] **Отклонение существует УЖЕ при N=∞ и БОЛЬШЕ наблюдаемого: 39.5% против 14.2%.**
[summarized] **R6 REJECT — единицы Гувера метрику НЕ чинят.** Разброс растёт ВЕЗДЕ: базовая
[summarized] **НО побочный продукт R6 закрывает исходный вопрос — разложение ТОЧНОЕ (ошибка 0.0007):**
[summarized] ```

наблюдаемое = аналитика (−39.5%, N=∞) × остаток симуляции (+41.9%)
0.986/0.950/0.972/0.846 = 0.9824/0.9361/0.8091/0.5942 × 1.003/1.015/1.202/1.424
```

Два эффекта **противоположного знака**, каждый БОЛЬШЕ исходной загадки, почти гасящие
друг друга. 14.2% — то, что не догасилось. Ровно то «взаимное погашение», которое
`decision_r3.md` вывел из смены знаков — здесь измерено.

**Немонотонность объяснена без третьего механизма:** обе компоненты СТРОГО монотонны
(одна убывает, другая растёт), произведение — нет. Проба роя `Q1-debugger` предсказала
это дословно. `decision_r2.md` называл возврат при CV=1.0 «независимым указанием на
другой механизм» — **это было неверно**, и на этом стоял приоритет R3.

⚠️ Оговорка: вывод сделан для АДДИТИВНОГО шума. Для мультипликативного сводится к
`H_ε = H_λ`, то есть отношение ровно 1 — но это **[INFERRED]**, численно не проверялось.

**→ R9 (единственное непонятое):** разложить +41.9% на конечное N / порог / шаги
аналитически, тем же способом. R8: персистить per-seed значения.

Артефакты: `analytic_r7.{py,json}`, `run_r6.py`, `result_r6.json`, `decision_r6_r7.md`.

## 🔬 Session 2026-09-01: R3 — все три кандидата убиты, вопрос оказался некорректным
[summarized] Пре-регистрация `5a9e6e6`. **Исходный R3 (тяжесть хвоста при конечном N) опровергнут ДО
[summarized] **Позитивный контроль прошёл первым:** базовая конфигурация дала ровно **14.2%** при
[summarized] **Снятие КАЖДОГО фактора делает разброс БОЛЬШЕ:**
[summarized] | Сняли | Разброс | Было |
[summarized] Ни один не роняет ниже порога 5% → **сработал заранее записанный KILL всей тройки**.
[summarized] **Структура важнее вердикта:** базовая конфигурация — САМАЯ устойчивая из восьми, любое
[summarized] **Вывод сильнее ожидаемого: вопрос «почему отношение ≠ 1» ПОСТАВЛЕН НЕКОРРЕКТНО.**

При CV ≥ 1 величина не инвариантна ни к одному из трёх произвольных допущений, ни одно
из которых не правильнее других. Отклонение существует, но его знак и величина задаются
выбором допущений, а не механизмом. Тот же класс, что D1 («контакт = функция расстояния»)
и `capacity_ratio` в самом H1.

⚠️ **Отступление от пре-регистрации, названо явно:** вторичный тест требовал ≥3σ,
реализация проверила только НАПРАВЛЕНИЕ. Возврат при CV=1.0 воспроизводится в обеих
половинах (против оценок роя 0.9σ и 1.5–1.9σ), но 3σ не проверено — σ не восстановима
из артефакта, `breakeven()` возвращает медианы, а не значения по seed. Статус не повышен.

⚠️ **Граница метода:** при гамме и CV=2.0 точки безубыточности НЕТ вообще — кривая не
пересекает 1.0 в пределах сетки. Метрика не определена в части пространства параметров.

Персистировано 64 кривые — те, что `run_r2.py` выбрасывал.

**→ R7 (дешевле и логически первее R6):** посчитать отношение аналитически при N = ∞
через индекс Гувера `H(s) = 2Φ(s/2) − 1`. R8: персистить per-seed значения, иначе любой
будущий σ-тест невозможен.

Артефакты: `{claim_r3,decision_r3}.md`, `run_r3.py`, `result_r3.json`, `r3_log.txt`.

## ❌ Session 2026-08-30 (часть 8): R2 — H_A убита, и допуск решил исход
[summarized] Пре-регистрация `3374774`. Объясняли остаток из R1: почему `noise_breakeven / CV_pop`
[summarized] **H_A:** ошибка локального арма мультипликативна, то есть сцеплена с нагрузкой органеллы,
[summarized] | CV | мультипликативный | аддитивный |

| **разброс** | **27.0%** | **14.2%** |

**KILL: 14.2% против допуска 10%.** Расцепление уменьшило эффект почти вдвое
(сцепление отвечает за ≈47%), но не убрало. Механизм назван верно, но он не единственный.

⚠️ **ДОПУСК РЕШИЛ ИСХОД — прямое следствие урока R1.** При «факторе 2» из `claim_r1.md`
оба варианта прошли бы (27% и 14.2% укладываются в двукратный запас), вердикт был бы
SUCCESS, а объяснение — ложным. Порог 10% поставлен УЖЕ объясняемого эффекта (27%)
именно по итогам `decision_r1.md`. **Первый случай за сессию, когда исправленная
методика изменила ВЕРДИКТ, а не добавила оговорку.**

Вторичное предсказание: мультипликативный монотонен (1.003→0.980→0.884→0.732), аддитивный
НЕТ (0.986→0.950→0.972→0.846) — независимое указание, что остаток порождается другим
механизмом, а не ослабленной версией того же.

**→ R3 (открыт, высокий приоритет):** тяжесть хвоста логнормали как таковая — конечное N,
несколько органелл доминируют в Σ max(0, λ−mean). Единственный кандидат, объясняющий
немонотонность.

Артефакты: `{claim_r2,decision_r2}.md`, `run_r2.py`, `result_r2.json`. `[VERIFIED-SYNTHETIC]`.

## ✅ Session 2026-08-30 (часть 7): R1 выполнен — вторичный защищаем, первичный был слабым тестом
[summarized] Пре-регистрация `98b95cc` заморожена до `run_r1.py`.
[summarized] **ЗАКАЗАННАЯ ЧАСТЬ ВЫПОЛНЕНА — SUCCESS и он защищаем.** Параметры зафиксированы до
[summarized] | Величина | Значение |
[summarized] Обе причины, по которым первый прогон был понижен до INCONCLUSIVE, сняты.


⚠️ **Довесок, который я добавил сверх заказа, оказался слабым тестом.** Первичный вопрос
(«шум безубыточности = CV популяции») прошёл 4 из 4 — отношения 1.003 / 0.980 / 0.884 /
0.732. Но проверка после прогона показала: соотношение **в значительной мере
аналитическое**. У локального арма ошибка задана шумом сенсора, у ядерного —
гетерогенностью популяции; безубыточность там, где они равны. Проверено сменой порога
(10/20/40), N (50) и нагрузки (15) — отношение остаётся 0.73–1.00 везде.
**Допуск «фактор 2» против структурного ожидания ≈1 провалить было невозможно.**

**ЭТО ТРЕТИЙ ЗА СЕССИЮ КРИТЕРИЙ, КОТОРЫЙ НЕ МОГ БЫТЬ ПРОВАЛЕН** — после исходного H1
(A-005) и незафиксированного `capacity_ratio` в `claim.md`. Разница: здесь дефект
нашёлся в том же прогоне, а не через четыре месяца. Паттерн устойчивый, стоит внести
в `patterns.md` как `[AVOID]`.

**Что содержательного осталось (→ R2):** отношение систематически МЕНЬШЕ 1 и убывает с
CV (1.003 → 0.732), тогда как чистая структура дала бы 1.0 везде. Реально, не объяснено,
не пре-регистрировано — наблюдение, не результат.

Артефакты: `h1_redox_controller/{claim_r1,decision_r1}.md`, `run_r1.py`, `result_r1.json`.
`[VERIFIED-SYNTHETIC]`, ни один параметр не из биологии, приоритет CoRR Аллена.

## 🧪 Session 2026-08-30 (часть 6): H1 прогнан по новому критерию — INCONCLUSIVE
[summarized] Пре-регистрация `274bbb8` заморожена ДО написания модели. Решающий тест при **τ_ratio = 1**
[summarized] **Результат: `advantage_excess = 4.52` при пороге SUCCESS ≥ 1.20.** Все три контроля
[summarized] **Но вердикт понижен до INCONCLUSIVE** — сработали три триггера скептика (первый
[summarized] 1. **Величина целиком задана `capacity_ratio`**, который claim.md не зафиксировал:

   excess идёт от 1.008 (ρ=0.5, KILL — мощности не хватает всем) до 313 (ρ=1.2).
   Порог держится на ρ ∈ [0.8, 1.2], но 4.52 — следствие выбора ρ = 1.0.
2. **Нужен сенсор точнее, чем разброс популяции.** Точка безразличия — шум CV ≈ 0.5,
   ровно равный гетерогенности. Дальше адресность ХУЖЕ равномерности (8176 событий
   против 3344). Это ограничение на CoRR, а не подтверждение.

⚠️ **Нашёл и исправил ошибку в СВОЕЙ проверке робастности:** первая версия нормировала
на нулевую модель, испорченную тем же шумом, и эффект выглядел независимым от точности
сенсора. Абсолютные числа показали обратное. **Второй за сессию случай одного класса**
(первый — «0.5 = случайно» в decision_v3.md): база, испорченная самим воздействием.
**Правило: робастность проверять на АБСОЛЮТНЫХ величинах, не на отношениях к базе,
которую манипуляция задевает.**

Артефакты: `h1_redox_controller/{claim,decision}.md`, `specificity_model.py`, `result.json`.
Приоритет CoRR Аллена указан во всех. `[VERIFIED-SYNTHETIC]` — о реальных митохондриях
не говорит ничего.

**Следующий шаг (решение человека):** R1 — новая пре-регистрация с зафиксированными
`capacity_ratio` и границей шума, повторный прогон (~час). Превратит INCONCLUSIVE в
защищаемый вердикт.

## 📚 Session 2026-08-30 (часть 5): H1 — это CoRR-гипотеза Аллена, механизм не тот
[summarized] Поиск литературы по предусловиям A-005. **Оба предусловия отработаны, результат меняет H1.**
[summarized] **П2 ЗАКРЫТО — но не так, как ожидалось. H1 оказалась переоткрытием CoRR-гипотезы**
[summarized] ⚠️ **У Аллена механизм — НЕ задержка.** Это со-локация сенсора и гена: отклик на
[summarized] **П1 ЗАКРЫТО. τ_real ≈ 2–5, а НЕ 100 — ошибка в 20–50 раз.**
[summarized] Ключевая величина найдена со ВТОРОЙ попытки: **0.422 кодон/с**, Wakigawa et al. 2023,

⚠️ **Урок поиска:** первая итерация (обзорные запросы «mitoribosome elongation rate»)
дала «признанный пробел в знаниях» — это было верно **про обзоры**, но не про
литературу. Вторая итерация искала **по МЕТОДУ** (retapamulin run-off, mitoribosome
profiling) и нашла за один запрос. **Отсутствие в обзоре ≠ отсутствие измерения.**

**Контринтуитивный факт:** митохондриальная трансляция **в 10–16 раз МЕДЛЕННЕЕ**
цитозольной (0.42 против 4.3–6.8 аа/с). Митохондриальный маршрут экономит на сплайсинге
(7–14 мин) и экспорте (5–40 мин) — и возвращает это с лихвой на медленной трансляции:
MT-ND1 (318 аа) 13 мин в митохондрии против 0.8–1.2 мин в цитозоле → τ_real 2.4–4.8;
MT-CO1 (513 аа) 20 мин → τ_real 1.5–3.0.

**Оба вывода сошлись независимо:** скорость даёт фактор 2–5, а не 100, значит она НЕ
может быть причиной сохранения митохондриального генома — механизм именно тот, что
у Аллена. **H1 вышла из `BLOCKED_DATA`, оба предусловия выполнены.**

**Артефакты:** `h1_redox_controller/{novelty_check,source_register,null_model.py}`.
Числа помечены `[VERIFIED-DOCS]`, НЕ `[VERIFIED-REAL]` — получены из вторичных обзорных
источников через поиск, первичные статьи построчно не читались.

⚠️ **Приоритет обязателен:** любой документ по H1 обязан ссылаться на CoRR Аллена.

## 🔧 Session 2026-08-30 (часть 4): H1 починен — критерий не мог быть провален
[summarized] Три скилла (`/macro-locality` → `/gate-check` → `/harvest`) независимо сошлись на одном:
[summarized] **Дефект H1 замерен** (`experiments/h1_redox_controller/null_model.py`, симуляция БЕЗ

недостижимым.** Плюс кривая насыщается при колене τ_ratio ≈ 8 — число 100 неинформативно.

**Критерий заменён — `AMENDMENTS.md` A-005** (основание: Amendment Protocol, «техническая
ошибка»). Новый стоит на `advantage_excess = advantage_model / advantage_null` при одних
и тех же параметрах. [VERIFIED] подстановка самой нулевой модели даёт excess = **1.0000**
при τ_ratio 2/8/100 — то есть **KILL-зона достижима**, чего старый критерий не позволял.

**Два блокирующих предусловия, H1 в состоянии `BLOCKED_DATA`:**
- **П1:** `τ_real` — цитируемое значение, а не назначенное. Сейчас **[UNKNOWN]**, ни одной
  ссылки в репозитории. «4 дня до результата» недействительны.
- **П2:** механизм, **отличимый от арифметики задержки**. Сейчас в спецификации нет
  ничего, кроме «локальное быстрее». Если П2 выполнить не удаётся — **H1 не гипотеза,
  а определение**, и это самостоятельный публикуемый вывод.

Также: `cost_ratio` (стоимость содержания отдельного генома) в метрике отсутствовала
как понятие — без неё «локальное лучше» бесплатный обед. Добавлена в новый критерий.

**Топ-актив харвеста (18/20) — приём «арм-потолок»**, и это дыра в самом стеке: в
`falsification-ladder.md` есть позитивный и негативный контроли, но **потолка нет**.
Записано в pearl-реестр, impact 9, next_check 2026-10-15.

## 🛑 Session 2026-08-30 (часть 3): ATR Phase 1 ЗАВЕРШЕНА — kill switch сработал
[summarized] Решение пользователя: **засчитать переформулированную D1**. Зафиксировано как
[summarized] **Ни один критерий, порог или формула не изменены.** `KILL_CRITERIA.md` остался LOCKED,
[summarized] **Сработала ветка `T2 KILL AND D1 KILL` → ATR framework WEAK.**
[summarized] | Гипотеза | Статус | Причина |
[summarized] **⚠️ Две честные проблемы, записанные, а не сглаженные:**

1. **Буквальный критерий KILL для D1 НЕ срабатывает** — требует `AUC(spectral) <=
   AUC(baseline)`, факт 0.8742 > 0.8738. У исходных критериев **нет серой зоны**,
   промежуток `0 < ΔAUC < 0.10` не определён, результат попал ровно в эту дыру. Это
   дефект пре-регистрации 2026-04-25. То же в `UNIFIED_FRAMEWORK.md` (там формулировка
   «не лучше nearest-gene» тоже не срабатывает на +0.0017).
2. **Записанная D1 не запускалась** намеренно — её эстиманд закрыт дважды.

KILL стоит на **Meta-Level Kill Switch 3 «Baseline Dominance»** (собственное правило
фреймворка, срабатывает буквально), пороге переформулированной пре-регистрации
(`ΔAUC < 0.02`, взят у DNA-Ladder) и нулевом Δprecision@1. Планка **поднята, не опущена**.

**Создано:** `NEGATIVE_RESULT.md` для T2 и D1 — протокол их требует, я успел поставить
галочку «записано» до того, как они существовали, проверил и написал.

**НЕ покрыто вердиктом:** каузальная цепочка `ΔG → ΔL → Δλ → Δ(экспрессия)` не
проверялась — вопрос D1 был предиктивным по построению. Единственное направление внутри
ATR, не являющееся повтором; требует данных о возмущениях (CRISPRi), а не нового признака.

**Осталось человеку:** решение о публикации negative result (ветка предписывает
«Publish negative result»; методология сильная, результат отрицательный).

## 🧬 Session 2026-08-30 (часть 2): D1 spectral — данные скачаны, прогон выполнен, KILL
[summarized] **Scope-тест (`d1_spectral_3d/scope_test.md`) → REDIRECT**, затем D1 запущен в
[summarized] **Данные (публичные, без ключей, без оплаты):** Hi-C GM12878 4DN `4DNFINPH7UOD` — НЕ

**Результат: KILL.** ΔAUC +0.0004, CI [−0.0006, +0.0013], 0/1000 бутстрапов выше порога
0.02. Δprecision@1 внутри варианта = ровно 0. Оба контроля пройдены (позитивный:
расстояние одно AUC 0.8725; негативный: перемешанные метки ΔAUC +0.0006).

**Главное — причина, а не сам ноль:** расстояние 0.8725 → +cCRE 0.8738 → **+контакт
0.8738 (−0.0000)** → +спектр 0.8742. **Сырой контакт Hi-C не добавляет над расстоянием
ничего.** Значит «усиленный baseline» оказался тем же самым, что закрыт дважды, и это по
факту третье подтверждение — но впервые с измеренной причиной: канал контакта пуст.

**[VERIFIED] Поправка к собственной пре-регистрации:** заявленные 37.2% пар на пустом
бине Hi-C — артефакт смещённой выборки (первые 40 вариантов chr1 = плохо покрытое начало
хромосомы). По геному 6.6%. На вердикт не влияет, запись исправлена явно.

**Вторичное предсказание опровергнуто со сменой знака:** +0.0007 (нижний терциль) против
−0.0148 (верхний), ожидался рост.

⚠️ **Открытый вопрос к человеку:** `KILL_CRITERIA.md:126` требует `T2 KILL AND D1 KILL` →
остановить все топологические гипотезы. T2 убита трижды, эта D1 убита — но она
ПЕРЕФОРМУЛИРОВАННАЯ, а записанная в файле версия не запускалась (и по scope-тесту не
должна). Засчитывать ли более сильную версию — решение автора фреймворка.

## 🧪 Session 2026-08-30: T2 (topology_control) — три локальных правила убиты, гипотеза исчерпана
[summarized] ⚠️ **Это НЕ возобновление ARCHCODE.** Работа шла в `topology_control/` (ATR Framework) —
[summarized] **Вердикт T2:** гипотеза «TOP2 распутывает ДНК по локальному геометрическому правилу»
[summarized] | Вариант | Правило | Медиана `advantage_score` (30 seed) | Коммит |
[summarized] **Почему это информативный NULL, а не пустой:** потолок оракула устойчив в трёх
[summarized] **Три технических дефекта, из-за которых эксперимент физически не мог проверить свою

гипотезу** (`AMENDMENTS.md`): A-002 `create_linked_rings` никогда не создавала
зацеплений (все прогоны v1 от апреля 2026 информационно пусты) · A-003 срывы passage
различались между армами втрое и двигали метрику сильнее правила (после починки вердикт
v2 сменился INCONCLUSIVE → KILL) · A-001 метрика инвертирована в трёх местах.
Плюс ускорение >90 мин → 8.1 с, эквивалентность доказана 16 тестами.

**[VERIFIED] Ретроактивная поправка, применена к `decision_v3.md`:** базовая линия
согласия с оракулом — **0.368** (замерено на арме `random`), а не 0.5. v3 сообщал
«0.400 (0.5 = случайно)», из чего читалось «хуже случайного»; на деле слегка лучше.
Вердикты не меняются, но строка была бы унаследована третьим отчётом. Ошибка типа 3 по
`research-methodology.md` — результат верен при неозвученном условии, само условие не
проверялось.

**Следующий шаг и его блокировка:** по `KILL_CRITERIA.md` при T2 KILL → pivot на **D1
(spectral 3D)**. ⚠️ **Перед D1 обязателен scope-тест.** Близкий эстиманд закрыт дважды
независимо: ARCHCODE 2026-04-15 (RF на distance+category = 0.9921) и DNA-Ladder
2026-07-20 (holdout ΔAUC = −0.007). Без scope-теста D1 будет третьей проверкой того же.

**Kill switch НЕ сработал:** требует `T2 KILL AND D1 KILL`, а D1 никогда не запускался
(`experiments/d1_spectral_3d/` существует, но ПУСТА — 0 файлов, вне git; проверено 2026-08-30). ATR-фреймворк не опровергнут.

## 🗂️ Session 2026-08-29: DNA-Ladder sibling audit + NotebookLM mining + 3-item verification
[summarized] - **[VERIFIED, this session]** **DNA-Ladder audit** (`sergeeey/-DNA-Ladder-`, sibling project born

  (actually run), 0 secrets in git history (grepped), 2 minor hygiene issues found (Windows long-path
  checkout failure — reproduced; stale `C:\Users\sboi\` cross-machine path in CLAUDE.md — read
  directly). TE/Alu-3D track paused at wet-lab boundary — `GO_A1_READY_PACK_v1.md` read directly:
  ready but `date_signed: null` (machine-enforced NO-GO), B0 reporter-path recommended first,
  RADIL_mm3 off-target still open. SE/LLPS track fully closed (7 convergent REJECTs on
  missing-heritability-via-SE, read from `null_results/META_missing_heritability_2026-07-10.md`,
  positive control validated pipeline at Cliff's delta +0.609). Full audit content in prior turns;
  not re-summarized here.
- **NotebookLM access recovered** (auth had expired; `nlm login` re-auth via existing Chrome session
  worked without manual browser interaction — worth noting for future sessions).
- **Mined 5 DNA-related notebooks** (215+ sources: ДНК РЕСТРАКТ 2, ДНК 2026 рестракт, ДНК ARCHCODE
  3D-Генома, Продвижение проекта ДНК, GenomicsGPU) after user scoped down from "all 115 notebooks"
  via AskUserQuestion (most notebooks are unrelated to DNA — Брак, bedtime stories, Ray Dalio, etc).
  Large trove of ARCHCODE historical findings surfaced — mostly ALREADY KNOWN incidents (Sabaté
  phantom ref, mock AlphaGenome, circular AUC=0.977, MPRA hallucination) independently
  cross-confirmed, not new. Also surfaced a previously-unknown parked idea: **GenomicsGPU**
  (GPU-accelerated RNA-seq quantification tool, kallisto/salmon competitor) — planning-only,
  never started, no repo/folder exists anywhere.

[summarized] - **3-item verification round (user explicitly asked to re-check before trusting):**

## 🔍 Session 2026-07-05 (part 3): Harvest/Capture sweep
[summarized] - 2026-07-05: harvest scan (7 questions) + capture routing done. 2 reusable patterns captured →

  captured → `~/.claude/memory/_auto/patterns.md`: [REPEAT][HIGH] portable integrity-protocol
  (CLAUDE.md + integrity-checker, "вынести во все research-репо"); [REPEAT] self-correcting companion
  preprint (rs-9090074 → rs-10254695, honest: reputational payoff not yet measured). ALSO: the
  "skill run without checking its assumption" [AVOID] pattern RECURRED (harvest asked 7 Qs on a project
  Claude ran all session) → incremented to [×2] in patterns.md; at [×3] → fix the harvest skill itself.
- 2026-07-08 (DOI-live wrap-up + PAUSE): rs-10254695 LIVE (DOI 10.21203/rs.3.rs-10254695/v1, Prescreening
  passed ~2 days). Commits this session:
  · `f4c8ca6` (D:/ДНК `feature/readme-link-new-preprint`, pushed) — README callout DOI fix
  · `da9e072` (same branch, pushed) — CITATION.cff + README Preprint/Citation now cite rs-10254695
    (were citing a NEVER-published arXiv paper — stale). Done via `git worktree` (hook kept re-dirtying
    activeContext, blocking checkout).
  · `ac96ad2`, `635f51c` (~/.claude `fix/quality-v13`, LOCAL only — that repo has NO git remote) —
    harvest-capture `--auto` fix; [REPEAT] "disclose AI in every submission"; integrity/self-correction patterns
  · `705fb59` (D:/ДНК) — PAUSE record
  DECISIONS (final): NO v2, NO editorial note now — AI-disclosure DEFERRED to the NEXT paper (rule saved in
  patterns.md + Obsidian). Declarations text (Competing Interests + Funding + Use of AI) staged in manuscript
  source `category_confound_paper.md` §8, UNCOMMITTED. dotfiles `~/.claude` has NO remote → memory commits
  stay local (safe, by design — user confirmed).
  OPEN (user-side, optional, non-blocking): merge PR `feature/readme-link-new-preprint` → main (gh auth broken
  here) to make DOI callout + "Cite this repository" button live on the public repo. **PROJECT PAUSED.**

## 📦 Session 2026-07-05 (part 2): GitHub showcase audit — repo README/description/topics
[summarized] **What was done (after preprint submission, same session):**

  the working branch (63,153/13 loci on main vs 26,225/9 loci locally), no mention of rs-10254695, topics
  field is completely empty (`[]`).
- **Executed (approved, "option A" only):** added a one-line pointer in `main`'s README (right after the
  existing AUC-caveat callout) linking to rs-10254695 (status Prescreening) and to the
  `backup/snapshot-20260706` branch with the reproducible code. Done via proper workflow — repo has a
  branch-protection hook blocking direct commits to `main` (requires `feature/` prefix branch + PR).
  Commit `19aeb56` on branch `feature/readme-link-new-preprint`, pushed to origin.
- **🔴 PR NOT YET MERGED — user needs to do this manually:**
  https://github.com/sergeeey/ARCHCODE/pull/new/feature/readme-link-new-preprint
  (gh CLI auth is broken in this environment — 401 Bad credentials — cannot merge via API)
- **NOT done (parked, user only approved option A):** repo description update, 12 topics, and the fuller
  README merge (options B/C in the audit). Exact recommended description text + topics list are in
  `docs/GITHUB_SHOWCASE_AUDIT.md` sections 5-6 — ready to paste via GitHub web UI "About" gear icon
  whenever user wants, no session needed for that (2-minute manual task).
- Minor hygiene note: during branch-switching this session, ~49 unrelated tracked files showed as
  "modified" on `main` (residue from earlier orphan-branch operations) — did NOT touch/commit any of
  them, only ever staged README.md explicitly. Harmless but worth a `git checkout main -- .` cleanup
  in a future session if it recurs.

---

## ✅ Session 2026-07-05 (part 1): Preprint SUBMITTED — Research Square rs-10254695, status Prescreening
[summarized] **What happened:** User submitted the category-confound paper as a new, separate Research Square preprint.

  stale `main`). Re-verify this link before citing it anywhere else (e.g. cover letters, correspondence).
- Also caught and declined: a marketing-email link to **SCIRP (Scientific Research Publishing)** —
  confirmed via search this is a well-known predatory publisher (Cabells 2021, Norwegian Index rating 0).
  Do not let user submit there under any circumstance if this resurfaces.

**User signal (still valid — user is stepping away from ARCHCODE after this):** two years on one project,
low sense of payoff, moving attention to other projects (GeoScan mentioned once, then reverted back to
ARCHCODE same session — mild confusion/fatigue, resolved by asking directly). Do NOT push new ARCHCODE
hypotheses or re-open old discovery threads (pearls, ATPH, QEC-MWPM) unprompted in future sessions.

**🔴 NEXT (when user returns, in priority order):**
1. Check Research Square dashboard for rs-10254695 — did it pass Prescreening? Is DOI assigned?
2. Once DOI live: add an editorial note/comment on the OLD preprint rs-9090074 linking to the new DOI,
   framed as self-correction/companion (rs-9090074's own Limitations already flagged category-driven AUC —
   this is not a retraction, just don't skip this step or the two preprints look contradictory in isolation).
3. Optional, not urgent: journal submission (check current APC/fee before committing to any venue — do not
   quote remembered numbers, they drift).
4. If the user does NOT bring up ARCHCODE next session, do not raise it either — respect the wind-down.

---

## 📄 Session 2026-07-06 (historical — superseded by submission above): Paper flattened + off-site backup
[summarized] **What was done:**

  matched-control p=0.996". Decision: do NOT withdraw/kill it — new paper is a companion/self-correction,
  not a refutation of fabricated data. No fabrication ever occurred.
- `manuscript/category_confound_paper.md` is now the SOLE authoritative source (v2). Section scaffolding
  moved to `manuscript/_archive_category_confound_sections/` (deprecated, historical only).
- Off-site backup: `backup/snapshot-20260706` pushed to GitHub (orphan branch, no big-file history issue).
- Pre-submission checklist updated in paper.md: most items DONE (integrity, refs, skeptic, reviewer,
  robustness, backup). Remaining: post to Research Square (free, no affiliation gate — user's own login
  required), link old↔new preprints via editorial note, format to typst template.

**User signal (important, read before next session):** user explicitly said they will submit this preprint,
then STEP AWAY from ARCHCODE ("на этом успокоюсь... перейду на другой проект... два года мучаюсь, не
ощутил результата"). Two years on one project, low sense of payoff. Do NOT push new ARCHCODE hypotheses
or re-open old discovery threads (pearls, ATPH, QEC-MWPM) unprompted next session — respect the wind-down.
If they return, lead with "post the preprint" as the one remaining action, not new science.

**🔴 NEXT (when user returns):**
1. User posts to Research Square (their login, ~20 min) — I cannot do this step.
2. After posted: add editorial note on rs-9090074 linking to new DOI (self-correction, not error).
3. Optional: journal submission later (Bioinformatics non-OA track is free-to-author; check current fees
   before committing — do not quote remembered numbers).

## 🔬 Session 2026-06-28: Discovery Audit — 4 Converging Lines [VERIFIED]
[summarized] **What was done:**

**✅ RESOLVED (2026-07-04): AlphaGenome rescue-or-kill test → KILL**
- Existing promoter ISM scan re-analyzed as neg control: −43% was peak of contiguous 6bp element (5227097-5227102),
  2 non-pearls in it equally disruptive (−24 to −28%). Fisher OR=14.5 but MW p=0.31 (pearls bimodal).
- New distal test (real ClinVar SNVs): pearl 5226613 CAGE −0.04% vs 10 controls −0.45%, MW p=0.70. No signal.
- Results: `results/distal_pearl_cage_test.json`, scratchpad `distal_pearl_cage_test.py`

**✅ PIVOT EXECUTED (2026-07-04): negative-result paper DRAFTED + verified + skeptic-hardened.**
Category-confound methods paper, systematic across 9 loci. Files: `manuscript/category_confound_*.md`
(paper.md = assembled draft) + `results/fig_category_confound.png`/stats + `analysis/fig_category_confound.py`
+ `analysis/phylop_control.py`. Commits 3762f4c → d089b09 → e62af65.
- Core: ARCHCODE marginal 0.754→within 0.430 (LSSIM), 0.783→0.507 (SSIM); category-only 0.827; 7/8 loci collapse.
- TWO positive controls SURVIVE: CADD (supervised) 0.989→0.991, phyloP (unsupervised) 0.790→0.894.
- Verified: integrity-checker CLEAR, 10 refs confirmed, skeptic 3 attacks addressed (Simpson tested+rejected; Attack 2 closed by phyloP).

**Science + figure DONE (commit 69fb031):** Fig v2 shows 5 methods — both ARCHCODE metrics collapse,
CADD+phyloP survive. Paper draft complete, verified, skeptic-hardened, figure matches text.
**🔴 NEXT (production, not science):** (1) Decide relationship to LIVE preprint rs-9090074 (positive ARCHCODE
claim) — erratum/companion. (2) Venue (NAR GAB / Bioinformatics) + format to template + cover letter + 24h cooling-off.
(3) Optional: verify remaining DOIs resolve.
- Parked: ATPH, QEC-MWPM `[CANDIDATE]`. Old ARCHCODE discovery claim = FALSIFIED (block above).

## 🔧 Session 2026-06-25: Manuscript Fixed for Submission (commit 703e398)

**What was done:**
- paper-critic + integrity-checker ran pre-submission review → found 2 FATAL, 4 MAJOR issues
- FATAL 1 resolved: switched body from `body_content.typ` → `taxonomy_paper/body_content.typ`
- FATAL 2 resolved: fixed headline stats — d=−1.53→−2.1, fold 5.4→5.5, Bonferroni α=0.007/7→α=0.008/6
- Variant count standardized: 30,318→26,225 (6 occurrences in taxonomy body)
- Competitor comparison table added to Introduction (svMIL/POSTRE/Daly/AlphaGenome vs ARCHCODE)
- PDF compiled: manuscript/main.pdf (2.7 MB)

**Current state:** manuscript coherent — abstract (CAGE/Simpson's Paradox) matches body (taxonomy + CAGE validation)
**Next:** write cover letter → submit to Bioinformatics Advances

---













## 🗂️ Key Documents

**Manuscript:**
- `manuscript/manuscript_v2_full.md` (77K, May 18) — biology-first framing
- `manuscript/manuscript_v2_full.docx` (36 KB) — submission-ready

**Validation Reports:**
- `docs/CODE_AUDIT_HARDENING_2026-05-25.md` — P0 audit complete
- `docs/CONSILIENCE_ASSESSMENT_2026-05-18.md` — H2 AlphaGenome 6/10 score
- `docs/ADR-029_MLH1_mechanism_specificity.md` — cross-locus validation PASS
- `docs/ADR-030_TERT_sampling_bias_solved.md` — hotspots validated
- `docs/ADR-033_Forensic_Audit_Summary.md` — data integrity 5/5 PASS

**Published:**
- Research Square: rs-9090074 — LIVE, DOI: 10.21203/rs.3.rs-9090074/v1
- Zenodo: v2.17 DOI — https://zenodo.org/records/18908214

---



















## ⚠️ Critical Constraints (CORRECTED)

**DO NOT:**
- ❌ Max Imakaev follow-up — REFUSED May 20, path closed
- ❌ Ronin Discord check — affiliation already works on Research Square
- ❌ Wait for arXiv endorsement — <10% probability, paused
- ❌ Submit to Nature Genetics/AJHG — <5% acceptance with N=1 robust
- ❌ "7/7" claim anywhere — manuscript reframed (commit c3f62b3)
- ❌ Promise clinical predictor — README discloses "Discovery Engine, not Predictor"

**DO:**
- ✅ Push 7 unpushed commits (public state stale)
- ✅ Verify bioRxiv appeal sent (response expected May 28)
- ✅ Target Bioinformatics Advances (40-50% with HBB framing)
- ✅ Use Research Square DOI as primary citation
- ✅ Disclose limitations honestly (N=1 robust, garden of forking paths, Gelman & Loken)

---



















## 🧭 Success Criteria (CORRECTED)

**Today (25 min):**
- ✅ 7 commits pushed to GitHub
- ✅ bioRxiv appeal status confirmed (sent or just-sent)
- ✅ APC funding source identified

**This week (5-7h):**
- ✅ AlphaGenome training overlap verified (kills #1 reviewer attack)
- ✅ Outreach updated with HBB framing + RS DOI
- ✅ Bioinformatics Advances submission prep started
- ✅ bioRxiv appeal response received (May 28 expected)

**This month (Jun 25):**
- ✅ Bioinformatics Advances submitted with HBB pilot framing
- ✅ Research Square v2 updated with HBB reframe (if appeal rejected, this becomes primary)
- ✅ Decision: continue ARCHCODE polish OR pivot to next project (ChernoffPy / GeoScan)

---



















## 📖 Context for Next Session
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...

- Research Square LIVE since May 18 ✅
- bioRxiv rejected May 21 (3rd attempt) → appeal drafted
- Max Imakaev REFUSED May 20 (arXiv path closed)
- Bioinformatics Advances = next target

**Decision tree branches:**
- IF appeal accepted (May 28) → bioRxiv preprint with HBB reframe
- IF appeal rejected → Research Square stays primary, focus Bioinformatics Advances
- IF no APC funding → MDPI/PeerJ alternatives (fee waivers)

**Next immediate action:** `git push` (5 min) → verify appeal sent (5 min) → APC funding check (15 min)

**Blocker:** None external. All internal/operational.

**Critical question:** Was bioRxiv appeal email sent May 21, or only drafted?

---

**Last Session Duration:** ~6 hours (P0 audit cleanup + skeptic + reframe + power + trust repair + reality sync)  
**Next Session Goal:** Push + bioRxiv appeal verification + Bioinformatics Advances prep

## Auto-commit log
- [2026-09-01 17:37] `5374e63`: D1 v10: KILL воспроизведён на 2.5x данных, pearl-число — нет
- [2026-09-01 15:11] `7b26ec8`: memory: R7+R6 -- 14.2% closes as product of a -39.5% analytic artifact and a +41.9% simulation term
- [2026-09-01 15:10] `b4829ca`: H1 R7+R6: the 14.2% puzzle closes as a product of two opposing effects
- [2026-09-01 15:04] `f9ede03`: memory: R3 done -- all three candidates killed, the question itself was ill-posed
- [2026-09-01 15:04] `0650d6c`: H1 R3: all three candidates KILLED -- and the question turns out to be ill-posed
- [2026-09-01 14:39] `5a9e6e6`: prereg(H1 R3): original R3 refuted before launch, redefined as a factorial ablation
- [2026-09-01 08:38] `02d3a79`: revert: un-track another session's work-in-progress files
- [2026-09-01 08:37] `37a24b6`: records: verify before correcting -- one accusation was false, three were true
- [2026-08-30 21:14] `dacc760`: H1 R2: KILL for H_A -- coupling explains about half, and the tolerance decided it
- [2026-08-30 21:07] `3374774`: prereg(H1 R2): tolerance set NARROWER than the effect being explained
- [2026-08-30 21:04] `5add1c7`: memory: R1 done -- secondary defensible, primary was a weak test (3rd such criterion this session)
- [2026-08-30 21:04] `bba0b9f`: H1 R1: secondary PROMOTE-worthy, primary was a weak test -- and I say so
- [2026-08-30 20:57] `98b95cc`: prereg(H1 R1): parameters pinned, and the primary question is one I cannot predict
- [2026-08-30 20:49] `13cf549`: memory: H1 run INCONCLUSIVE -- threshold met but magnitude is parameter-driven
- [2026-08-30 20:49] `07da1f3`: H1: INCONCLUSIVE -- threshold passed at 4.52, but the magnitude is parameter-driven
- [2026-08-30 20:43] `274bbb8`: prereg(H1): frozen before the model is written
- [2026-08-30 20:34] `a8a98fe`: memory: tau_real found (2-5, not 100); H1 unblocked, both preconditions met
- [2026-08-30 20:33] `3cbb5bc`: H1 P1 CLOSED: tau_real is 2-5, not 100 -- mitochondrial translation is 10-16x SLOWER
- [2026-08-30 20:26] `05c2c06`: H1: fix header self-contradiction (it still claimed no criterion changed), memory updated
- [2026-08-30 20:25] `f528111`: H1 literature search: P2 closed, P1 blocked on one unmeasured number
- [2026-08-30 20:18] `93b2e44`: A-005: H1 criterion replaced -- the old one could not be failed

[summarized] - [2026-08-30 20:09] `4de00f0`: memory: ATR Phase 1 concluded, framework WEAK, H1 is the only live direction
[summarized] - [2026-07-04 21:59] `e62af65`: feat(paper): add unsupervised phyloP positive control — closes skeptic Attack 2
