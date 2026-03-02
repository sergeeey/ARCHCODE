# Active Context — ARCHCODE

**Last Updated:** 2026-03-02 (session 22: Position-only control experiment)
**Branch:** main
**Last Commit:** 1141f86 (SCN5A multimodal cell-type mismatch — pushed)
**GitHub:** https://github.com/sergeeev/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — awaiting screening
**Status:** Position-only control experiment complete. Ready for commit + push.

---

## Текущий статус проекта

**Фаза:** v2.10 — position-only control experiment (AUC ablation)

### Session 22: Position-only control + CADD experiment

**Key finding:** AUC 0.977 → 0.551 when category information removed (fixed effectStrength=0.3).
This is the definitive proof that AUC = category-distribution effect, not independent prediction.

**Three effectStrength models tested:**

| Model                 | AUC   | Within-syn AUC | Verdict                                     |
| --------------------- | ----- | -------------- | ------------------------------------------- |
| Categorical (default) | 0.976 | 0.570          | Primary model (documented)                  |
| CADD-based            | 0.977 | 0.988          | REJECTED (CADD leaks pathogenicity)         |
| Position-only         | 0.551 | 0.558          | Control experiment (proves category effect) |

**Changes this session (not yet committed):**

1. `scripts/fetch_cadd_scores.py` — NEW — downloads CADD phred via Ensembl VEP REST API
2. `scripts/generate-unified-atlas.ts` — EDIT — dual-mode (categorical + position-only via --effect-mode)
3. `data/hbb_vep_results.csv` — EDIT — added cadd_phred, cadd_raw columns
4. `data/hbb_benign_vep_results.csv` — EDIT — added cadd_phred, cadd_raw columns
5. `results/HBB_Unified_Atlas_95kb_POSITION_ONLY.csv` — NEW — position-only atlas
6. `results/UNIFIED_ATLAS_SUMMARY_95kb_POSITION_ONLY.json` — NEW
7. `results/position_only_control_experiment.json` — NEW — comparison metrics
8. `manuscript/FULL_MANUSCRIPT.md` — EDIT — Position-Only Control section, Methods update, Discussion update

---

## Ключевые файлы (session 22)

| Файл                                               | Действие                                             |
| -------------------------------------------------- | ---------------------------------------------------- |
| `scripts/generate-unified-atlas.ts`                | EDIT — EFFECT_MODE flag, CADD parsing, position-only |
| `scripts/fetch_cadd_scores.py`                     | NEW — CADD score downloader                          |
| `results/position_only_control_experiment.json`    | NEW — ablation results                               |
| `results/HBB_Unified_Atlas_95kb_POSITION_ONLY.csv` | NEW — control atlas                                  |
| `manuscript/FULL_MANUSCRIPT.md`                    | EDIT — 3 sections updated                            |

---

## Для следующей сессии

1. **Commit + push** session 22 changes
2. **bioRxiv v2 preprint** — submit updated manuscript
3. Consider: Run position-only on other loci (CFTR, BRCA1) for multi-locus confirmation
4. Consider: iPSC-CM H3K27ac for SCN5A (tissue-matched positive control)
