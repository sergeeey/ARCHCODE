# ARCHCODE Strategy (high-level)

This document records high-level product and focus decisions for ARCHCODE. It does not affect code behavior.

---

## 🎯 Core Strategic Positioning

### CRITICAL DISTINCTION: Discovery Engine, NOT Prediction Tool

**ARCHCODE — это Discovery Engine, а НЕ Prediction Tool.**

| Критерий | Prediction Tool | Discovery Engine | ARCHCODE |
|----------|-----------------|------------------|----------|
| **Цель** | Классификация (pathogenic/benign) | Обнаружение нового | ✅ Discovery |
| **Конкуренция** | VEP, SpliceAI, CADD, AlphaGenome | Нет аналогов | ✅ Новая категория |
| **Метрика успеха** | AUC, accuracy, F1 | Novel findings, hypotheses | ✅ 27 pearls, 641 VUS candidates |
| **Ценность** | "Лучше предсказывает" | "Видит невидимое" | ✅ Structural blind spot |
| **Бизнес-модель** | Commodity ML | Unique capability | ✅ B2B pharma, in silico CRISPR |

**Стратегический императив:**
- ❌ НЕ позиционировать как "ещё один variant predictor"
- ✅ Позиционировать как "structural mechanism discovery platform"

---

## Focus and prioritization

- **Primary focus**: ARCHCODE as a **discovery engine** for structural variant mechanisms — not a prediction tool competing with ML.
- **Resource allocation**: Prioritize scientific publication (bioRxiv) and B2B positioning (pharma in silico screening) over generic "research tool" only.
- **No code impact**: These are product/portfolio choices; the repository remains a single product (ARCHCODE).

---

## Future differentiators (roadmap)

- **In silico CRISPR**: Virtual deletion/inversion of genomic regions to **discover** loop and TAD mechanisms. Commercial angle: B2B SaaS for pharma (test editing before wet lab). Pricing reference: comparable to molecular modeling platforms (e.g. Schrödinger).
- **Positioning**: "Affordable in silico screening for gene therapy" — target smaller biotechs that cannot run large-scale CRISPR screens in vivo.
- **Exit**: Long-term options include acquisition by biotech (e.g. BioNTech, Moderna) or standalone growth; timeline 5–7 years.

---

## Validation and publication

- **Publication**: Validation must be reported against **experimental Hi-C** (e.g. Rao et al. 2014), not mock AlphaGenome. See README, METHODS.md, KNOWN_ISSUES.md, and docs/ALPHAGENOME.md.
- **AlphaGenome**: Optional integration when API is available; mock in v1.0. Do not claim “AlphaGenome-validated” without explicit disclaimer.

---

_Last updated: 2026-02-01. For detailed roadmap and technical limits, see KNOWN_ISSUES.md and AUDIT_RESPONSE.md._
