# Active Context — ARCHCODE

**Last Updated:** 2026-03-01 (session 9, TP53 locus implementation + generic ClinVar downloader)
**Branch:** main
**Last Commit:** 6904d5a (docs + strategic prompt)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** SUBMITTED TO bioRxiv — awaiting DOI assignment

---

## Текущий статус проекта

**Фаза:** v2.1 — Multi-locus expansion (TP53 complete, 4 remaining)

### ✅ TP53 Locus — Complete (MILESTONE — 3rd locus)

| Метрика             | HBB (95kb)     | CFTR (317kb)     | TP53 (300kb)     |
| ------------------- | -------------- | ---------------- | ---------------- |
| ClinVar variants    | 1,103          | 3,349            | 2,795            |
| P/LP + B/LB         | 353 + 750      | 1,756 + 1,593    | 1,646 + 1,149    |
| Variant spread      | 2.1 kb (2.2%)  | 201.5 kb (63.6%) | 109.9 kb (36.6%) |
| SSIM range          | 0.9910–1.0000  | 0.9948–1.0000    | 0.9983–1.0000    |
| LR AUC (cat only)   | —              | —                | 0.7715           |
| LR AUC (cat+SSIM)   | —              | —                | 0.8001           |
| LR ΔAUC             | -0.001 (p=1.0) | +0.007 (p=1.0)   | +0.029 (p=0.77)  |
| MW-U synonymous     | p=0.22 ns      | p=6.1e-6 \*\*\*  | p=7.2e-10 \*\*\* |
| MW-U intronic       | p=0.69 ns      | p=0.13 ns        | p=1.7e-3 \*\*    |
| MW-U "other"        | p=0.058 ns     | p=1.6e-16 \*\*\* | p=1.1e-14 \*\*\* |
| TDA rho (SSIM↔W_H1) | -0.964         | -1.000           | -0.852           |

**Key insight:** TP53 confirms SSIM is a category-level classifier (LR p=0.77). MW-U shows statistically significant but practically negligible within-category differences. TDA correlation slightly weaker (rho=-0.85) but still strong. Category breakdown dominated by synonymous (1,399) and "other" (709) — no missense/frameshift detected by classify_hgvs().

### ✅ New Infrastructure

- **`scripts/download_clinvar_generic.py`** — Generic ClinVar downloader for any gene (replaces per-gene scripts)
- **Pipeline extended:** `--locus tp53` now works in generate-unified-atlas.ts, analyze_positional_signal.py, tda_proof_of_concept.py
- **Gene name resolution fix:** Pipeline now finds target gene by name match, not first gene in window

---

## Все фазы

1. ✅ Phase 0-2: Core engine + mock validation + manuscript draft
2. ✅ Phase 3: Audit & integrity fixes
3. ✅ Phase 4-6: Real Hi-C validation GM12878 (r=+0.16, p=0.30)
4. ✅ Phase A-H: Documentation, ROC, bioRxiv submission
5. ✅ Phase I: Unified pipeline (AUC 1.000 → 0.9766)
6. ✅ Locus config externalization (30kb + 95kb)
7. ✅ K562 Hi-C correlation (r=0.53/0.59, p<1e-82)
8. ✅ Manuscript K562 update (14 edits, de4ac71)
9. ✅ Within-category HBB → honest null (de84f7a)
10. ✅ Manuscript within-category update (8 edits, aa0f677)
11. ✅ CFTR locus — config, pipeline, within-category test
12. ✅ Bayesian fit (Optuna) — Δr=0.0001, confirmed near-optimal
13. ✅ Manuscript CFTR + Bayesian update — 17 edits
14. ✅ TDA proof-of-concept — ripser on HBB+CFTR+TP53
15. ✅ Multi-locus candidate research — 25 ACMG genes screened
16. ✅ **TP53 locus — config, ClinVar, pipeline, within-category, TDA**

---

## Ключевые файлы

| Файл                                     | Назначение                                          |
| ---------------------------------------- | --------------------------------------------------- |
| `config/locus/tp53_300kb.json`           | TP53 300kb config (ENCODE K562 CTCF + H3K27ac)      |
| `config/locus/cftr_317kb.json`           | CFTR 317kb config                                   |
| `config/locus/hbb_30kb_v2.json`          | HBB 30kb config                                     |
| `config/locus/hbb_95kb_subTAD.json`      | HBB 95kb config                                     |
| `scripts/download_clinvar_generic.py`    | Generic ClinVar downloader (--gene TP53/BRCA1/etc.) |
| `scripts/generate-unified-atlas.ts`      | Main pipeline (`--locus tp53\|cftr\|30kb\|95kb`)    |
| `scripts/analyze_positional_signal.py`   | Within-category analysis (all loci)                 |
| `scripts/tda_proof_of_concept.py`        | TDA analysis (all loci)                             |
| `data/tp53_variants.csv`                 | 2,795 TP53 variants                                 |
| `results/TP53_Unified_Atlas_300kb.csv`   | TP53 atlas output                                   |
| `results/positional_signal_tp53.json`    | TP53 within-category result                         |
| `results/tda_proof_of_concept_tp53.json` | TP53 TDA result                                     |
| `results/locus_selection_research.json`  | Tier 1/2 candidate data                             |
| `docs/STRATEGIC_PROMPT.md`               | Strategic development prompt                        |

---

## v2.1 Research Roadmap

1. ~~TP53~~ ✅ (2,795 variants, LR p=0.77, TDA rho=-0.85)
2. **BRCA1** — next Tier 1 (8,603 variants, MCF7 Hi-C, chr17)
3. **MLH1** — Tier 1 (4,314 variants, HCT116 Hi-C, chr3)
4. **LDLR** — Tier 1 (3,721 variants, HepG2 Hi-C, chr19)
5. **SCN5A** — Tier 1 (2,333 variants, iPSC-CM Hi-C, chr3)
6. **Hi-C data download** — MCF7 (GSE144380), HCT116 (GSE104334), HepG2 (ENCSR194SRI)
7. **Threshold recalibration** — SSIM thresholds for 300x300 matrices
8. **Manuscript update** — TP53 results + multi-locus comparison table
9. **bioRxiv revision** — upload updated manuscript

---

## Для следующей сессии

1. **BRCA1 implementation** — create config, download ClinVar, run pipeline
2. **MLH1 implementation** — same workflow as TP53
3. Consider classify_hgvs() improvement — misses missense/frameshift for TP53/CFTR
4. Проверь: получен ли DOI от bioRxiv?
5. **Multi-locus comparison table** — compile all 3 loci results
6. **Hi-C validation for TP53** — need MCF7 Hi-C data (GSE144380)
