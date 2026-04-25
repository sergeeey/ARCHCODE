---
tags:
  - project-card
  - whatsapp
  - nlp
created: '2026-04-12'
---
# WhatsApp Analyzer

**Одно предложение:** AI-платформа эмоционального анализа WhatsApp переписок — 7 эмоций, PII masking, PDF-отчёт.
**Статус:** Frozen (MVP complete)
**Стек:** Python, Streamlit, ReportLab, Presidio (PII), NLTK
**Где:** D:\WhatsApp-Analyzer

## Главный результат
End-to-end: parse -> PII mask -> emotion detect (7 types) -> pattern analysis -> PDF report. 100% deterministic. 20 tests.

## Переиспользуемые компоненты
- PII masking pipeline (Presidio) -> Reflexio privacy
- Emotion detection patterns -> Reflexio enrichment

up:: [[Каталог всех проектов 2026]]
