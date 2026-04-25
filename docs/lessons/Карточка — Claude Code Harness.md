---
tags:
  - project-card
  - claude-code
  - tooling
created: '2026-04-12'
---
# Claude Code Harness (claude-cod-top-2026)

**Одно предложение:** Production-grade конфигурация Claude Code — 40 детерминированных hooks, 13 agents, Evidence Policy, memory persistence.
**Статус:** Released (v3.2.0)
**Стек:** Python hooks, CLAUDE.md + rules/, 726 tests, mypy, 86% coverage
**Где:** D:\Claude-cod-top-2026

## Главный результат
Modular hook system (pre-tool, post-tool, lifecycle guards). CircuitBreaker для MCP. Zero token overhead. Используется во всех проектах.

## Переиспользуемые компоненты
- 40 hooks (session_start, pre_commit, memory_guard, drift_guard и др.)
- Evidence Policy (VERIFIED/INFERRED/UNKNOWN)
- Agent definitions (navigator, builder, reviewer, tester, explorer и др.)

up:: [[Каталог всех проектов 2026]]
