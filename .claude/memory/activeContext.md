# Active Context — ARCHCODE

**Last Updated:** 2026-02-28
**Branch:** main
**Last Commit:** 584171b (docs: update README with bioRxiv submission status)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment

---

## Текущий статус проекта

**Фаза:** bioRxiv submission complete, DOI pending

Все фазы завершены:

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes (FALSIFICATION_REPORT.md)
3. ✅ Phase 4-6: Real Hi-C validation (r=+0.16, не значимо)
4. ✅ Phase A: Documentation + hypothesis "The Loop That Stayed"
5. ✅ Phase B: Real Data Replacement (AlphaGenome → VEP)
6. ✅ Phase C: Consistency check (4 ошибки найдены и исправлены)
7. ✅ Phase D: PDF v2 rebuild + visual verification
8. ✅ Phase E: v1.0 freeze + ROADMAP_v2.md
9. ✅ Phase F: ROC analysis (750 Benign variants, AUC=1.000, Quadrant analysis)
10. ✅ Phase G: FULL_MANUSCRIPT.md updated + PDF rebuilt (28 стр, 628 KB)
11. ✅ Phase H: bioRxiv submission (файлы загружены, PDF конвертация пройдена)

---

## Коммиты этой сессии (2026-02-28)

1. `b10e5dc` — chore: sync src/ engine, UI, and config files (32 файла)
2. `0cf2a5c` — fix(pdf): rebuild preprint v2 with corrected VEP table and SIFT default
3. `3da1d91` — docs: add preprint page screenshots for visual verification
4. `9e935d1` — docs: lock v1.0 state and define rigorous cross-validation roadmap for v2.0
5. `763eea1` — feat: ROC analysis with 750 Benign variants + methodological defense
6. `d76fa71` — feat(manuscript): add ROC analysis to FULL_MANUSCRIPT.md and rebuild PDF
7. `584171b` — docs: update README with bioRxiv submission status and ROC results

---

## Ключевые результаты v1.0

### Данные

- **1,103** real ClinVar HBB variants (353 Pathogenic/LP + 750 Benign/LB)
- 161/353 (45.6%) structurally pathogenic by ARCHCODE
- 20 pearl variants (VEP < 0.30, SSIM < 0.95): 15 promoter, 3 missense, 1 frameshift, 1 splice_acceptor
- Discordance: 130/353 (36.8%)

### ROC Analysis

- AUC = 1.000 (reflects category-dependent occupancy scaling, NOT independent prediction)
- Zero false positives among 750 benign variants across all SSIM thresholds
- Youden optimum: SSIM < 0.99 (Sens=0.935, Spec=1.000)
- Q2 (pearls): 20 Pathogenic, 0 Benign — zero FPR

### Валидация

- Hi-C: r=+0.16 (p=0.30, n=12) — не значимо, честно задокументировано
- Категориальная стратификация биологически корректна

---

## Файлы bioRxiv (в `C:\Users\serge\Desktop\ДНК\2026 архив\`)

| Файл                          | Размер | Назначение                 |
| ----------------------------- | ------ | -------------------------- |
| `ARCHCODE_Preprint_v2.pdf`    | 628 KB | Manuscript (28 стр, с ROC) |
| `HBB_Clinical_Atlas_REAL.csv` | 91 KB  | 353 Pathogenic variants    |
| `HBB_Combined_Atlas.csv`      | 126 KB | 1,103 variants (353+750)   |
| `fig_roc_curve.png`           | 279 KB | ROC + SSIM distribution    |
| `fig_ssim_vs_vep.png`         | 374 KB | SSIM vs VEP scatter        |
| `roc_analysis.json`           | 1 KB   | Machine-readable stats     |

### Метаданные

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

## Для следующей сессии

1. Прочитай этот файл
2. Проверь: получен ли DOI от bioRxiv? (модерация 24-48 часов)
3. Если DOI получен → обнови README.md (бейдж зелёный + ссылка), обнови BibTeX
4. Если нет → жди модерации
5. Следующая цель: ROADMAP_v2.md Phase 1 (Micro-C download for K562)
6. Опционально: Twitter-тред о препринте после получения DOI
