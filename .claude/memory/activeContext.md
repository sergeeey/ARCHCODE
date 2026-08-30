# Active Context — ARCHCODE Project

**Last Updated:** 2026-08-30
**Current Branch:** experiment/spectral-collapse-pilot
**Session Focus:** ⏸️ **PROJECT STILL PAUSED.** No ARCHCODE code/manuscript work resumed. 2026-08-29 session was exploratory/archival (see below), not a resumption. Do NOT raise new ARCHCODE work unprompted.
**Reality source:** session 2026-08-30 (ATR Phase 1 ЗАВЕРШЕНА — kill switch сработал, фреймворк WEAK)

## 🧪 Session 2026-08-30 (часть 6): H1 прогнан по новому критерию — INCONCLUSIVE

Пре-регистрация `274bbb8` заморожена ДО написания модели. Решающий тест при **τ_ratio = 1**
(задержек нет вообще), армы отличаются только распределением ОДИНАКОВОГО бюджета:
local — пропорционально своей нагрузке, nuclear — равномерно, null — то же при CV = 0.

**Результат: `advantage_excess = 4.52` при пороге SUCCESS ≥ 1.20.** Все три контроля
пройдены: калибровка при CV=0 даёт ровно 1.0000, бюджеты равны, негативный контроль
(перемешать нагрузки после распределения) обрушает эффект до 0.7355. Вторичное
предсказание подтверждено: excess растёт с гетерогенностью 2.65 → 4.52 → 7.28 → 9.23.

**Но вердикт понижен до INCONCLUSIVE** — сработали три триггера скептика (первый
ненулевой результат за сессию, превышение порога в 3.8 раза, чисто синтетика), и
проверка нашла две области применимости, которых НЕ было в пре-регистрации:

1. **Величина целиком задана `capacity_ratio`**, который claim.md не зафиксировал:
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

Поиск литературы по предусловиям A-005. **Оба предусловия отработаны, результат меняет H1.**

**П2 ЗАКРЫТО — но не так, как ожидалось. H1 оказалась переоткрытием CoRR-гипотезы**
(Co-location for Redox Regulation, John F. Allen, 1993). Источники проверены HTTP:
Allen 2015 PNAS `10.1073/pnas.1500012112` (277 цит.), Allen 2003 Phil Trans R Soc B
`10.1098/rstb.2002.1191` (265), Allen 2017 J Theor Biol PMID `28408315`. Найдены
поиском по формулировке самой H1, БЕЗ имени Аллена — совпадение не подгонялось.

⚠️ **У Аллена механизм — НЕ задержка.** Это со-локация сенсора и гена: отклик на
редокс-состояние КОНКРЕТНОЙ органеллы. В клетке сотни митохондрий с разными
состояниями, ядерный контроллер действует по среднему **даже при нулевой задержке**.
Специфичность на органеллу не сводится к арифметике задержки — это и есть механизм,
которого требовало П2. Но значит **исходная формулировка H1 через задержку описывала
не тот механизм.** Решающий тест ставится при τ_ratio = 1, где преимущества по скорости
нет вообще; KILL, если преимущество исчезает при устранении гетерогенности.

**П1 ЗАКРЫТО. τ_real ≈ 2–5, а НЕ 100 — ошибка в 20–50 раз.**

Ключевая величина найдена со ВТОРОЙ попытки: **0.422 кодон/с**, Wakigawa et al. 2023,
DOI `10.1101/2023.07.19.549812` (Molecular Cell 2025), ретапамулиновый run-off,
in organello. Прямая цитата подписи к рис. 2C.

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

Три скилла (`/macro-locality` → `/gate-check` → `/harvest`) независимо сошлись на одном:
**comparator ни разу не разбирался на составляющие** — ни в T2 (не было потолка), ни в
трёх итерациях D1 (baseline не раскладывали), ни в H1 (нулевой модели не строили).

**Дефект H1 замерен** (`experiments/h1_redox_controller/null_model.py`, симуляция БЕЗ
биологии): порог SUCCESS (>1.5) перекрывается уже при τ_ratio = 1.5, при τ_ratio = 100
нулевая модель даёт **11.01** — в 7 раз выше порога. Условие KILL требует τ_ratio < 1.5,
но гипотеза существует только при τ_ratio ≫ 1. **Посылка гипотезы делала её опровержение
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

Решение пользователя: **засчитать переформулированную D1**. Зафиксировано как
`AMENDMENTS.md` **A-004** — по собственному Amendment Protocol файла, потому что
засчитывание другого теста против записанного критерия есть интерпретация.

**Ни один критерий, порог или формула не изменены.** `KILL_CRITERIA.md` остался LOCKED,
дописаны три блока «ИСХОД», и это сказано в шапке.

**Сработала ветка `T2 KILL AND D1 KILL` → ATR framework WEAK.**

| Гипотеза | Статус | Причина |
|---|---|---|
| T2 | 🔴 FALSIFIED | 0.919 / 1.000 / 1.111 при пороге > 0.8; потолок оракула 0.106 |
| D1 | 🔴 FALSIFIED | ΔAUC +0.0004; Meta-Level Kill Switch 3 |
| **T1** | ⛔ заблокирована | `Depends on T2 SUCCESS` |
| **D2, D3, вся Phase 3** | ⛔ заблокированы | `Depends on D1 SUCCESS` / `≥1 SUCCESS в Phase 1` |
| **H1** (митохондрии) | ✅ **единственное живое** | объявлена независимой от T2/D1 |

**⚠️ Две честные проблемы, записанные, а не сглаженные:**
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

**Scope-тест (`d1_spectral_3d/scope_test.md`) → REDIRECT**, затем D1 запущен в
переформулированном виде. Пре-регистрация заморожена `0f8cbb4` ДО первого AUC.

**Данные (публичные, без ключей, без оплаты):** Hi-C GM12878 4DN `4DNFINPH7UOD` — НЕ
скачан, читается по HTTP range (`shared_utils/remote_hdf5.py`, своя реализация:
`hic-straw` не собирается на Windows, `fsspec` даёт 404 там, где прямой range даёт 206).
eQTL — GTEx v8 `Cells_EBV-transformed_lymphocytes` = LCL = **тот же тип клеток, что
GM12878** (cell-type matching по построению). Итого 249 МБ трафика вместо 78-235 ГБ.

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

⚠️ **Это НЕ возобновление ARCHCODE.** Работа шла в `topology_control/` (ATR Framework) —
соседний трек, не рукопись и не код ARCHCODE. Проект ARCHCODE остаётся на паузе.

**Вердикт T2:** гипотеза «TOP2 распутывает ДНК по локальному геометрическому правилу»
закрыта по всем дешёвым вариантам Relaxation Map.

| Вариант | Правило | Медиана `advantage_score` (30 seed) | Коммит |
|---|---|---|---|
| v2 | угол перекрёстка | 0.919 | `6d683f1` |
| v3 / V1 | кривизна | 1.000 | `7fa2393` |
| v4 / V2 | плотность зацеплений | 1.111 | `62b3251` |
| — | **оракул** (знает `Lk`, не локальное правило) | **0.106 / 0.106 / 0.111** | потолок |

**Почему это информативный NULL, а не пустой:** потолок оракула устойчив в трёх
независимых прогонах — упрощение достижимо примерно в 9 раз. Значит провал специфичен
для правил, а не для механики или задачи.

**Три технических дефекта, из-за которых эксперимент физически не мог проверить свою
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
- **[VERIFIED, this session]** **DNA-Ladder audit** (`sergeeey/-DNA-Ladder-`, sibling project born
  2026-07-08, same day as ARCHCODE pause): cloned+audited via `gh`/`git`, 34/34 + 23/23 pytest pass
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
- [2026-08-30 20:49] `07da1f3`: H1: INCONCLUSIVE -- threshold passed at 4.52, but the magnitude is parameter-driven
- [2026-08-30 20:43] `274bbb8`: prereg(H1): frozen before the model is written
- [2026-08-30 20:34] `a8a98fe`: memory: tau_real found (2-5, not 100); H1 unblocked, both preconditions met
- [2026-08-30 20:33] `3cbb5bc`: H1 P1 CLOSED: tau_real is 2-5, not 100 -- mitochondrial translation is 10-16x SLOWER
- [2026-08-30 20:26] `05c2c06`: H1: fix header self-contradiction (it still claimed no criterion changed), memory updated
- [2026-08-30 20:25] `f528111`: H1 literature search: P2 closed, P1 blocked on one unmeasured number
- [2026-08-30 20:18] `93b2e44`: A-005: H1 criterion replaced -- the old one could not be failed
- [2026-08-30 20:09] `4de00f0`: memory: ATR Phase 1 concluded, framework WEAK, H1 is the only live direction
- [2026-08-30 19:58] `4de00f0`: memory: ATR Phase 1 concluded, framework WEAK, H1 is the only live direction
- [2026-08-30 19:58] `5db11f6`: Phase 1 CONCLUDED: kill switch fired, ATR framework marked WEAK
- [2026-08-30 19:51] `3de8d6f`: D1: lint cleanup, memory + cross-repo register updated (retroscan)
- [2026-08-30 19:50] `be22d59`: D1 (redirected): KILL — spectral adds nothing, and contact adds nothing either
- [2026-08-30 19:36] `0f8cbb4`: prereg(D1 redirect): frozen before any AUC is computed
- [2026-08-30 19:14] `086c0d3`: scope-test(D1): REDIRECT — comparator must change before D1 may run
- [2026-08-30 19:08] `ebf1969`: memory: T2 closed across all three cheap variants; D1 pivot gated on scope test
- [2026-08-30 19:06] `62b3251`: T2 v4/V2: KILL — local entanglement density carries no directional information
- [2026-08-30 01:22] `4be9e55`: prereg(T2 v4/V2): local entanglement density as local rule — frozen before implementation
- [2026-08-30 00:19] `7fa2393`: T2 v3/V1: KILL — curvature carries no directional information either
- [2026-08-30 00:16] `c168adf`: prereg(T2 v3/V1): curvature as local rule — frozen before implementation
- [2026-08-30 00:11] `6d683f1`: T2 v2: KILL after removing the failure-rate confound (A-003)
- [2026-08-29 23:49] `5630608`: T2 v2: INCONCLUSIVE — local angle rule carries no directional information
- [2026-08-29 23:44] `adbc66f`: prereg(T2 v2): freeze claim before any run
- [2026-08-29 21:30] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 21:26] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 21:25] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 20:51] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-07-08 15:15] `705fb59`: docs(memory): ARCHCODE paused — preprint live (DOI rs-10254695/v1), no further action
- [2026-07-08 15:10] `705fb59`: docs(memory): ARCHCODE paused — preprint live (DOI rs-10254695/v1), no further action
- [2026-07-08 14:53] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-08 14:39] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-05 13:40] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-05 13:40] `87b7807`: docs(github): add showcase audit — description/topics recommendations + branch drift finding
- [2026-07-05 13:00] `905c93b`: docs(memory): record Research Square submission — rs-10254695, Prescreening
- [2026-07-04 23:08] `6726953`: docs(paper): flatten to single authoritative source + archive scaffolding
- [2026-07-04 23:06] `efdad39`: fix(paper): full reviewer report response (7 major/minor) — data-tested first
- [2026-07-04 22:18] `8dc9834`: fix(paper): reviewer response — category-granularity robustness + narrowed claims
- [2026-07-04 22:07] `69fb031`: feat(figure): v2 money figure — 5 methods, two positive controls survive vs both ARCHCODE metrics collapse

[summarized] - [2026-07-04 21:59] `e62af65`: feat(paper): add unsupervised phyloP positive control — closes skeptic Attack 2
