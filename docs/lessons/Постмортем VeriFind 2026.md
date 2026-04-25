---
tags:
  - lessons
  - postmortem
  - verifind
  - finance
  - product
created: '2026-04-12'
project: VeriFind 2026
---
# Постмортем VeriFind / APE 2026

**Проект:** Financial decision support system с zero-hallucination guardrails
**Период:** 2026-02 — ongoing (production)
**Статус:** PRODUCTION. 983 теста, 9 Docker контейнеров, Hetzner deployment, paper trading $1000.

## Что это

"Финансовый интеллект, который отказывается галлюцинировать числа." LLM планирует и пишет код (не числа). Код исполняется в VEE sandbox. Числа проходят Truth Boundary Gate. Multi-agent debate (Bull/Bear/Arbiter). Paper trading. SEC + EU AI Act compliance.

## Результат

- Directional accuracy: 55.5% (14d), 57.2% (30d) — честно для финансов
- 7d и 90d horizons excluded (coin-flip level)
- Golden Set: 5/20 (25%) pass rate на pilot
- Live paper trading: $1000, TSLA/NVDA positions

## Положительные уроки

1. **"LLM generates code, not numbers"** — архитектурный инвариант, убивает класс галлюцинаций
2. **Golden Set** — regression suite для качества ответов (30 queries, HIT/NEAR/MISS)
3. **Fail-closed** — uncertainty -> UNCERTAIN, не fabricate
4. **Temporal Integrity** — no look-ahead bias (asof_timestamp + publication_lag)
5. **Sweep -> OOS -> GO/NO-GO -> live** — полный research-to-production pipeline
6. **Compliance as tests** — SEC + EU AI Act = CI gate
7. **Honest 55-57%** — реальные числа, контраст с ARCHCODE AUC=0.975

## Отрицательные уроки

8. **Golden Set 25% pass** — pipeline не справляется с большинством запросов
9. **7 smoke test attempts** — 9 контейнеров + 4 LLM = огромная failure surface
10. **Scope creep** — от QA до trading + backtesting + market intel + causal inference
11. **50+ docs + logs в корне** — documentation sprawl
12. **5 LLM провайдеров** — fragile dependencies

up:: [[Каталог проектов — 7 постмортемов]]
