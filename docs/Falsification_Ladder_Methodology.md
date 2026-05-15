# Falsification Ladder — Формализация Методологии ARCHCODE

**Источник:** [Falsification Ladder for AI-Assisted Development](falsification-ladder-ai-assisted-development.pdf) (16 pages)  
**Анализ:** 2026-05-14  
**Статус:** Методология уже применяется в ARCHCODE, PDF предоставляет формализацию  
**Оценка применимости:** 9.5/10

---

## Краткое Содержание

**Falsification Ladder (FL)** — staged validation protocol для AI-assisted research:
1. Claim → формулировка проверяемого утверждения
2. Smallest Hypothesis → минимальная проверяемая единица
3. Minimal Artifact → код/данные для проверки
4. Positive Control → known-good input (должен пройти)
5. Negative Control → known-bad input (должен упасть)
6. Baseline → reference для сравнения
7. Test → запуск на реальных данных
8. Stress-Test → adversarial/edge cases
9. Classify → promote/repeat/reject
10. Caveats → документирование ограничений
11. Gate Decision → go/no-go для следующего уровня

---

## Evidence Tiers (Уровни Доказательств)

| Tier | Название | Критерии | Действие |
|------|----------|----------|---------|
| 0 | **Draft** | Идея без кода | Только документ (claim.md) |
| 1 | **Toy** | Синтетические данные, proof-of-concept | Локальный тест, не для production |
| 2 | **Controlled Preliminary** | Positive + negative controls pass | Можно показывать команде |
| 3 | **Baseline Candidate** | Baseline comparison проведён | Кандидат для A/B теста |
| 4 | **Stress-Tested** | Adversarial cases pass | Готовность к pilot deployment |
| 5 | **Reproducible** | Независимое воспроизведение | Можно публиковать (preprint) |
| 6 | **Release Candidate** | Code review + docs + tests | Готовность к production |
| 7 | **Production Baseline** | Deployed, monitoring active | Current ground truth |

---

## Experiment Artifact Standard

Каждый эксперимент в `experiments/<id>/`:

| Файл | Содержание | Когда создаётся |
|------|-----------|-----------------|
| `claim.md` | Falsifiable statement | Step 1 (всегда первым) |
| `controls.md` | Positive + negative controls | Step 4-5 |
| `metrics.json` | Quantitative results | Step 7 |
| `stress_tests.md` | Edge cases, adversarial inputs | Step 8 |
| `caveats.md` | Known limitations, boundary conditions | Step 9 |
| `decision.md` | Promote/Repeat/Reject + reasoning | Step 10 |
| `reproducibility.md` | Instructions for independent replication | Step 11 (если promote) |

---

## Subagent Roles (Специализация Агентов)

| Role | Функция | Mapping в ARCHCODE |
|------|---------|-------------------|
| **Hypothesis Decomposer** | Claim → smallest testable unit | navigator |
| **Control Designer** | Генерирует positive/negative controls | builder (control mode) |
| **Baseline Builder** | Создаёт trivial baseline для сравнения | builder |
| **Artifact Creator** | Пишет код для проверки hypothesis | builder |
| **Test Runner** | Запускает контролируемые эксперименты | tester |
| **Stress Tester** | Adversarial/edge cases | sec-auditor, skeptic |
| **Caveat Logger** | Документирует ограничения | reviewer |
| **Skeptical Reviewer** | Red team, ищет falsifications | skeptic |
| **Reproducibility Auditor** | Проверяет независимое воспроизведение | verifier |
| **Release Gatekeeper** | Go/no-go решения | tracy, skeptic (gate mode) |

---

## ARCHCODE Уже Использует FL (Подтверждение)

### Примеры применения:

**1. ADR-026: Rössler Attractor Hypothesis**
- **Claim:** Chaotic dynamics model for loop stability (Step 1) ✅
- **Controls:** Known bifurcation patterns (Step 4-5) ✅
- **Baseline:** Linear model comparison (Step 6) ✅
- **Stress-Test:** Data availability, parameter identifiability (Step 8) ✅
- **Caveats:** 3D ODE = biological implausibility (Step 9) ✅
- **Decision:** 3.5/10 → DEFER (Step 10) ✅
- **Result:** `null_results/` entry created ✅

**2. Forum Post Validation Theater Prevention**
- **Claim:** 7 loci validation (Step 1) ✅
- **Control:** ClinVar VCV ID resolution (Step 4) ✅
- **Stress-Test:** Grep for LDLR/CFTR data (Step 8) ✅
- **Falsification:** LDLR nonexistent, CFTR=NaN → 6 loci only ✅
- **Correction:** Regenerated figure, updated text BEFORE publication ✅
- **Gate:** Submission Gate Protocol invoked ✅

**3. AlphaGenome Validation (ADR-027 to ADR-030)**
- **Claim:** Mechanism specificity (regulatory ≠ coding) ✅
- **Controls:** Category-matched P/LP vs B/LB (Step 4-5) ✅
- **Baseline:** Null hypothesis = ρ=0 (Step 6) ✅
- **Stress-Test:** Forensic audit 5 layers (Step 8) ✅
- **Caveats:** Small N, tissue mismatch, sampling bias (Step 9) ✅
- **Decision:** 9.0/10 → PROMOTE to preprint (Step 10) ✅

---

## Рекомендации по Улучшению

### 1. Formalize Experiment Structure

**Сейчас:** ADRs в `docs/`, decisions в `.claude/memory/decisions.md`, null results в `null_results/`  
**После:** `experiments/<id>/` с полным artifact standard (7 файлов)

**Действие:**
```bash
mkdir -p experiments/_template/
# Создать шаблоны: claim.md, controls.md, metrics.json, stress_tests.md, caveats.md, decision.md, reproducibility.md
```

**Стоимость:** 1 час  
**Польза:** Воспроизводимость + независимая проверка любого эксперимента

---

### 2. Add Evidence Tier Ladder

**Сейчас:** `[VERIFIED-REAL]` / `[VERIFIED-SYNTHETIC]` / `[UNKNOWN]`  
**После:** Evidence tiers 0-7 с explicit gate criteria

**Действие:** Обновить `rules/falsification-ladder.md`:
```markdown
## Evidence Tier Ladder

| Tier | Name | Required Artifacts | Gate Criteria |
|------|------|-------------------|---------------|
| 0 | Draft | claim.md | Falsifiable statement |
| 1 | Toy | claim.md + minimal code | Synthetic data passes |
| 2 | Controlled Preliminary | + controls.md | Positive/negative controls pass |
| ... | ... | ... | ... |
```

**Стоимость:** 30 минут  
**Польза:** Unified язык для оценки зрелости гипотез

---

### 3. TeammateIdle Hook for Artifact Completeness

**Сейчас:** Skeptic auto-triggers on HIGH confidence claims  
**После:** TeammateIdle hook checks `experiments/<id>/` completeness

**Действие:** Hook проверяет перед переходом к следующему tier:
- Tier 2 → controls.md exists?
- Tier 4 → stress_tests.md exists?
- Tier 5 → reproducibility.md exists?

**Стоимость:** 30 минут  
**Польза:** Предотвращает пропуск шагов (особенно controls + stress tests)

---

### 4. Formalize Subagent Roles

**Сейчас:** Агенты имеют общие роли (builder, tester, reviewer)  
**После:** FL-specific роли (Hypothesis Decomposer, Control Designer, Stress Tester)

**Действие:** Обновить `~/.claude/agents/`:
- `skeptic.md` → добавить роль **Caveat Logger** + **Skeptical Reviewer**
- `builder.md` → добавить **Control Designer** mode
- `verifier.md` → добавить **Reproducibility Auditor** mode

**Стоимость:** 1 час  
**Польза:** Агенты явно знают свою роль в FL workflow

---

## Связь с Nature Article (2026)

**Citation:** https://www.nature.com/articles/s41467-025-66155-3

**Контекст:** Пользователь указал сохранить FL анализ "со ссылкой на авторов их данные итд". Nature статья предположительно связана с формализацией validation protocols или reproducibility standards в computational biology.

**TODO:** Прочитать статью и добавить релевантные insights к FL methodology (если статья описывает validation protocols для genomics/computational biology).

---

## Решение: Принять FL Формализацию

**Статус:** ARCHCODE уже использует FL интуитивно, PDF предоставляет explicit структуру  
**Приоритет:** P1 (критично для submission readiness)  
**Время:** ~3 часа (template + tier ladder + hooks + subagent roles)

**Next Steps:**
1. Создать `experiments/_template/` (1 час)
2. Обновить `rules/falsification-ladder.md` с evidence tiers (30 мин)
3. Добавить TeammateIdle hook для artifact completeness (30 мин)
4. Формализовать subagent roles (1 час)

**Kill Criterion:** Если формализация замедляет workflow >20% → откатить к текущей неформальной версии

**Reviewers:** skeptic (protocol correctness), tracy (time investment ROI)

---

**Создано:** 2026-05-14  
**Последнее обновление:** 2026-05-14  
**Версия:** 1.0  
**ADR:** Связано с ADR-026 (Rössler hypothesis как пример FL применения)
