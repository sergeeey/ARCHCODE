# SEC_AUDIT_KODEKS

**Date:** 2026-03-05  
**Project:** ARCHCODE (`D:\ДНК`)  
**Audit Type:** Security + Quality + Architecture (Codex-assisted)  
**Status:** HARDENED_BASELINE

---

## Scope

Аудит охватывает:
- security hardening в Python/Node/CI;
- стабильность regression/gold-standard проверок;
- архитектурные риски на границе browser/node;
- зрелость gate-by-default практик.

---

## Executive Summary

**Итоговая оценка:** `8.6/10`.

Сильные стороны:
- внедрены базовые security-gates в CI;
- устранены high-risk паттерны в Python;
- сборка и линт стабильны.

Ключевые слабые места (остаточные):
- высокий операционный шум из-за множества скриптов/режимов;
- часть quality/security automation еще не полностью "жесткая" (coverage gate и scheduled history secret scan пока не обязательны);
- для долгосрочной прозрачности нужен формальный threat model для `mock/real`.

Validation decision update (2026-03-06):
- HBB VUS strict gate зафиксирован как `NO_GO`.
- Следствие: claim-уровень для HBB VUS ranking остается `EXPLORATORY`, clinical utility escalation заблокирован до прохождения порогов.
- Артефакты:
  - `results/hbb_vus_validation_report_2026-03-06.json`
  - `docs/internal/VALIDATION_EXECUTION_2026-03-06_HBB_VUS.md`

---

## Findings by Priority

## P0: Regression and Gold-Standard

1. **Статус: устранено**
- gold-standard suite стабилизирован;
- введен явный режим `ALPHAGENOME_TEST_MODE`;
- удален неявный `real->mock` fallback.

Остаточный риск:
- дрейф данных/порогов при будущих обновлениях набора референсов.

Поддерживающее действие:
- держать `test:gold` обязательным PR-gate и фиксировать baseline-артефакты при изменении порогов.

## P1: Architecture Boundary (Browser/Node)

1. **Статус: существенно снижено**

Сделано:
- вынесен browser-safe сервис (`AlphaGenomeBrowserService`);
- node scripts переведены на `AlphaGenomeNodeService`;
- validation path отделен от node-only импортов.

Остаточный риск:
- необходима дисциплина новых импортов (не возвращать node-модули в browser path).

## P1: Dependencies / Advisories

1. **Статус: устранено**

Факт:
- выполнен апгрейд на `vite@^7.3.1`, `vitest@^4.0.18`, `@vitejs/plugin-react@^5.1.0`;
- `npm audit` показывает `0 vulnerabilities`.

## P2: Gate-by-Default in CI

Минимальные обязательные проверки на PR:
- `npm run lint`
- `npm run build`
- `npm test` (включая gold-standard без mock)
- `npm run security:deps` (fail при high/critical)
- `npm run security:python` (bandit, fail при high)
- `npm run security:secrets`

Дополнительно:
- coverage gate (например, 70-80%);
- branch protection с required checks;
- merge-block при high/critical advisory и найденных секретах.

## P2: Secret Hygiene

Требуемое действие:
- добавить `gitleaks` в CI для diff scan;
- плановый full-history scan по расписанию;
- pre-commit hook для `secret_scan.py` и/или `gitleaks protect`.

---

## Implemented

- `scripts/analyze_ctcf_chipseq.py`
  - Убрано `shell=True`, subprocess переведен на аргументы.
- `scripts/generate_pdf_v2.py`
  - Убран `mktemp`, использован `NamedTemporaryFile`.
- `Dockerfile`
  - Перевод контейнера на non-root user (`archcode`).
- `.eslintrc.cjs`
  - Добавлен рабочий ESLint-конфиг.
- `scripts/secret_scan.py`
  - Добавлен локальный secret scanner.
- `.github/workflows/security-gates.yml`
  - Добавлены security checks (deps/python/secrets/lint/build).
- `package.json` + lockfile
  - Добавлены `overrides`; затем выполнен апгрейд dev-chain до веток без известных advisory.
- `src/services/AlphaGenomeBrowserService.ts`, `src/services/AlphaGenomeNodeService.ts`, `src/validation/alphagenome.ts`
  - Разведена browser/node граница для AlphaGenome path.
- `src/__tests__/regression/gold-standard.test.ts`
  - Введен явный режим тестирования + стабилизированы пороги по validated baseline.

---

## Verified

- `npm run lint` -> PASS
- `npm run build` -> PASS (с warnings по browser/node boundary)
- `npm run security:deps` -> PASS (`0 vulnerabilities`)
- `npm run security:python` -> PASS для high (`bandit -lll`)
- `npm run security:secrets` -> PASS
- `npm run test:gold` -> PASS
- `npm test -- --silent` -> PASS (6 files, 40 tests)

---

## Not Verified / Gaps

- Нет подтверждения полного отсутствия secret leakage по истории git (только текущее дерево/гейты).
- Threat model для `mock/real` режимов формально не оформлен в отдельном документе.

---

## Residual Risks

- Operational drift при параллельном существовании `mock/real` режимов (если policy ослабнет).
- Потенциальный regressions drift при обновлениях reference данных без baseline-процедуры.
- Secret exposure risk в git history до выполнения scheduled full-history scans.

---

## Action Plan

1. **P2:** включить coverage threshold как обязательный PR-gate (70-80%).
2. **P2:** добавить scheduled full-history secret scan (gitleaks) + policy реагирования.
3. **P2:** оформить threat model для `mock/real` режимов в отдельном документе.
4. **P3:** добавить SBOM + license policy check в CI.

---

## Artifacts / Evidence

Ключевые артефакты изменений:
- `D:\ДНК\scripts\analyze_ctcf_chipseq.py`
- `D:\ДНК\scripts\generate_pdf_v2.py`
- `D:\ДНК\Dockerfile`
- `D:\ДНК\.eslintrc.cjs`
- `D:\ДНК\scripts\secret_scan.py`
- `D:\ДНК\.github\workflows\security-gates.yml`
- `D:\ДНК\package.json`

Релевантные audit-документы проекта:
- `D:\ДНК\docs\internal\AUDIT_REPORT.md`
- `D:\ДНК\docs\internal\AUDIT_RESPONSE.md`
- `D:\ДНК\docs\CODEX_ZERO_HALLUCINATION_GATES.md`
