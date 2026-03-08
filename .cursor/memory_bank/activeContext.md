# Active Context

**Last Updated:** 2026-03-07
**Mode:** VERIFY → PLAN (canonical governance active)
**Branch:** main

---

## Правила проекта (источники истины)

- **CLAUDE.md** — научная целостность (NO phantom refs, NO invisible synthetic data, NO "fitted" без кода). Обязательны для всех правок.
- **AGENTS.md** — протокол Codex: Plan → APPROVE → Execute; Implemented vs Verified; zero hallucinations.
- **Канонические claims:** `results/validation_canonical_index_2026-03-06.json`, `results/publication_claim_matrix_2026-03-06.json`.
- **Legacy-нарративы:** `docs/internal/LEGACY_CLAIM_HYGIENE_2026-03-06.md` — DISCUSSION.md, LOOP*THAT_STAYED*\* и др. помечены как non-canonical; для публикации использовать только формулировки из claim matrix.

---

## Текущий статус (2026-03-07)

### Валидация и аудит

- **Cold-Eye Audit** (2026-03-06): выполнено по `docs/COLD_EYE_AUDIT_TZ.md`. Скрытых моков нет; LSSIM из расчёта; тесты 63/63. Риск: Task3 weak_halved weakEncounter=0 (интерпретировано как геометрия). Отчёт: `docs/COLD_EYE_AUDIT_REPORT.md`.
- **Post-audit fixes** (2026-03-07): цитирование в blind spot benchmark (без placeholder DOI); маппинг ключей в `build_blind_spot_benchmark.py` (pearls_by_locus заполняется); «fitted» → «manually calibrated» в AlphaGenomeService.ts и validate-blind-loci.ts; ChromoGen → Schuette et al. 2025, Science Advances.

### Task-статусы (канонические)

- **Task1 1Mb:** гипотеза Pearson > 0.5 REJECTED; статус EXPLORATORY. См. `docs/internal/VALIDATION_EXECUTION_2026-03-06_TASK1_1MB.md`.
- **Task3 weak-CTCF:** SUPPORTED_IN_MODEL (weak_probe); внешняя валидация UNVERIFIED.
- **Task2/4/5:** см. `results/task*_canonical_status_2026-03-06.json` и `validation_canonical_index_2026-03-06.json`.

### RNA-seq и Loop That Stayed

- FASTQ: образцы верифицированы (WT SRR12935486, B6 SRR12935488, A2 SRR12935490). См. `docs/STATUS_DASHBOARD.md`.
- Анализ splice junctions выполнен; после нормализации по глубине секвенирования **гипотеза не поддержана** (разница объясняется глубиной). В manuscript — только как Limitations, без p-values без теста. См. `docs/COLD_EYE_AUDIT_REPORT.md` и честный verdict в сессии (ДНК для курсора).

### Blind Spot Benchmark

- `results/blind_spot_benchmark_v1.0/` — README и benchmark_summary.json с заполненными pearls_by_locus; цитирование без placeholder DOI.

---

## Критические флаги (CLAUDE.md)

1. Не использовать phantom references (проверять DOI).
2. Не использовать «fitted» без кода подгонки — только «manually calibrated» / «calibrated to literature».
3. Публикационные утверждения сверять с `publication_claim_matrix_2026-03-06.json` (BLOCKED/ALLOWED/ALLOWED_WITH_CAVEAT).
4. Legacy-файлы не использовать для клинических/каузальных claims.

---

## Следующие шаги (на усмотрение пользователя)

- Обновление manuscript по каноническим формулировкам (ABSTRACT, DISCUSSION, Limitations).
- Чеклист перед препринтом: `docs/CODEX_ZERO_HALLUCINATION_GATES.md` (секреты, build, test).

---

## Полный контекст версий и сессий

Подробная хроника (v2.14, Session 37, VUS, MaveDB, cross-species и т.д.): **`.claude/memory/activeContext.md`**.

Полный список архитектурных решений (ADR-001 … ADR-022): **`.claude/memory/decisions.md`**.
