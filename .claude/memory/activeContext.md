# Active Context — ARCHCODE

**Last Updated:** 2026-02-28
**Branch:** main
**Last Commit:** 9e935d1 (docs: lock v1.0 state and define rigorous cross-validation roadmap for v2.0)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** v1.0 FROZEN — READY FOR bioRxiv SUBMISSION

---

## Текущий статус проекта

**Фаза:** v1.0 LOCKED → bioRxiv submission

Все фазы завершены:

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes (FALSIFICATION_REPORT.md)
3. ✅ Phase 4-6: Real Hi-C validation (r=+0.16, не значимо)
4. ✅ Phase A: Documentation + hypothesis "The Loop That Stayed"
5. ✅ Phase B: Real Data Replacement (AlphaGenome → VEP)
6. ✅ Phase C: Consistency check (4 ошибки найдены и исправлены)
7. ✅ Phase D: PDF v2 rebuild + visual verification
8. ✅ Phase E: v1.0 freeze + ROADMAP_v2.md

---

## Что сделано в текущей сессии (2026-02-28)

### Коммиты этой сессии

1. `b10e5dc` — chore: sync src/ engine, UI, and config files (32 файла)
2. `0cf2a5c` — fix(pdf): rebuild preprint v2 with corrected VEP table and SIFT default
3. `3da1d91` — docs: add preprint page screenshots for visual verification
4. `9e935d1` — docs: lock v1.0 state and define rigorous cross-validation roadmap for v2.0

### Ключевые действия

- **Git sync:** Все 33 оставшихся src/ файла закоммичены и запушены
- **PDF v2:** Пересобран через Chrome headless (WeasyPrint требует GTK на Windows)
  - Исправленная 13-строчная VEP consequence mapping table
  - SIFT default = 0.50 (было 0.70)
  - Аффилиация: Independent Researcher, Almaty, Kazakhstan
  - 26 страниц, 573 KB
- **Visual verification:** Страницы 1-3 + VEP table (стр. 9) отрендерены через PyMuPDF
- **Pre-submission checklist:** 36 OK, 0 errors
- **Scope guard:** Отклонён запрос на Bayesian fitting + TDA перед публикацией
  - Причина: overfitting (3 params, 1 locus = circular validation)
  - Записан ROADMAP_v2.md с правильной методологией (cross-validation)

---

## Ключевые результаты v1.0

### Данные

- 353 real ClinVar HBB variants (Pathogenic + Likely Pathogenic)
- 161/353 (45.6%) structurally pathogenic by ARCHCODE
- 20 pearl variants (VEP < 0.30, SSIM < 0.95): 15 promoter, 3 missense, 1 frameshift, 1 splice_acceptor
- Discordance: 130/353 (36.8%)

### Валидация

- Hi-C: r=+0.16 (p=0.30, n=12) — не значимо, честно задокументировано
- Категориальная стратификация биологически корректна

### Гипотеза "The Loop That Stayed"

- Computational proof-of-concept, НЕ подтверждённое открытие
- Требует экспериментальной валидации (RT-PCR, Capture Hi-C)

---

## Файлы для bioRxiv

| Файл          | Путь                                  | Назначение           |
| ------------- | ------------------------------------- | -------------------- |
| PDF препринта | `results/ARCHCODE_Preprint_v2.pdf`    | Manuscript           |
| CSV атлас     | `results/HBB_Clinical_Atlas_REAL.csv` | Supplementary File 1 |
| Scatter plot  | `results/figures/fig_ssim_vs_vep.png` | Supplementary File 2 |

### Метаданные для формы

- **Author:** Sergey V. Boyko
- **Affiliation:** Independent Researcher, Almaty, Kazakhstan
- **Email:** sergeikuch80@gmail.com
- **Subject:** Bioinformatics
- **Article Type:** New Results
- **License:** CC-BY 4.0
- **Data:** https://github.com/sergeeey/ARCHCODE

---

## Post-Publication: ROADMAP v2.0

Подробный план в `ROADMAP_v2.md`. Ключевое:

1. Micro-C для двух локусов (HBB + SOX2, K562)
2. Bayesian fit на HBB → predict SOX2 (cross-validation)
3. TDA (Wasserstein distance) как топологическая метрика
4. Обновлённый препринт v2.0

**Принцип:** Fit on A, Predict on B — никакого overfitting.

---

## Тех. стек

- **Engine:** TypeScript (Vite + React + Three.js)
- **Validation:** Python (cooler, Ensembl VEP)
- **Analysis:** Analytical mean-field simulation
- **PDF:** Chrome headless + python-markdown + PyMuPDF
- **State:** Zustand
- **Config:** config/default.json

---

## Для следующей сессии

1. Прочитай этот файл
2. Проверь: получен ли DOI от bioRxiv?
3. Если да → обнови README.md со ссылкой на DOI, пости Twitter-тред
4. Если нет → жди модерации (24-48 часов)
5. Следующая цель: ROADMAP_v2.md Phase 1 (Micro-C download)
