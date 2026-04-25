---
tags:
  - project-card
  - cogniml
  - infrastructure
created: '2026-04-12'
---
# CogniML 2026

**Одно предложение:** Knowledge registry для ML-команд — captures experiment outcomes в structured skills с retrieval-backed advice.
**Статус:** Active
**Стек:** Python 3.11, FastAPI, PostgreSQL (asyncpg), Qdrant, Ollama
**Где:** E:\CogniML 2026
**Тесты:** 755 passing

## Главный результат
POST /api/retrospective -> LLM extraction -> Skill -> Qdrant embed; /api/advise -> vector search + synthesis. Second Brain методология с auto-capture git commits.

## Связи
- Питает знаниями ARCHCODE, Reflexio, VeriFind, CogniRouter
- Shared memory infrastructure с ~/.claude/memory/raw/
- CogniML Corpus (E:\cogniml-corpus) — cross-project retrospective data

up:: [[Каталог всех проектов 2026]]
