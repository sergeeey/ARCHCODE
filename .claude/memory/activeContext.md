# Active Context — ARCHCODE

**Last Updated:** 2026-03-02 (session 14: LSSIM threshold recalibration)
**Branch:** main
**Last Commit:** 82fee0a (Limitation #10 — Akita/Enformer benchmarking planned)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — awaiting screening (24-48h) → DOI assignment
**Status:** LSSIM COMPLETE. Manuscript v2.3 (5 loci, 21,989 variants, LSSIM). Ready for commit.

---

## Текущий статус проекта

**Фаза:** v2.3 — LSSIM threshold recalibration (matrix-size dilution resolved)

### Session 14: LSSIM Implementation

**Problem solved:** Matrix-size dilution killed pearl detection on all loci except HBB 30kb.
Global SSIM range compressed to 0.98–1.00 on matrices >100×100, making thresholds unreachable.

**Solution:** Local SSIM (LSSIM) — compute SSIM on 50×50 submatrix centered on variant bin.
Normalizes perturbation fraction to ~12% regardless of matrix size. Thresholds from HBB 30kb
transfer directly.

### 6-Locus Summary Table (with LSSIM)

| Метрика           | HBB (30kb)     | HBB (95kb)     | CFTR (317kb)    | TP53 (300kb)    | BRCA1 (400kb)    | MLH1 (300kb)     |
| ----------------- | -------------- | -------------- | --------------- | --------------- | ---------------- | ---------------- |
| Matrix size       | 50×50          | 159×159        | 317×317         | 300×300         | 400×400          | 300×300          |
| LSSIM range       | 0.8753–0.9989  | 0.7537–0.9992  | 0.8329–0.9999   | 0.9443–1.0000   | 0.8767–0.9999    | 0.8417–0.9999    |
| Global SSIM range | (same)         | 0.9611–0.9998  | 0.9948–1.0000   | 0.9983–1.0000   | 0.9982–1.0000    | 0.9838–1.0000    |
| Struct. path.     | 161            | 254            | 35              | 0 (12 VUS)      | 52               | 72               |
| Pearls            | 20             | 27             | 0 (no VEP)      | 0 (no VEP)      | 0 (no VEP)       | 0 (no VEP)       |
| LR ΔAUC (LSSIM)   | −0.001 (p=1.0) | −0.001 (p=1.0) | −0.012 (p=0.79) | +0.032 (p=0.29) | +0.002 (p≈10⁻²⁰) | +0.011 (p=0.005) |

**Key findings:**

- LSSIM resolves matrix-size dilution: dynamic range 0.75–1.00 (vs 0.98–1.00 global)
- HBB 30kb: LSSIM ≡ SSIM (regression test passed, 20 pearls preserved)
- HBB 95kb: 27 pearls detected (previously 0)
- Within-category: CFTR/TP53 null (p > 0.29); BRCA1/MLH1 significant but ΔAUC < 0.02 (power effect)
- TP53 has narrowest LSSIM range (0.9443–1.0000) — highest CTCF density reduces perturbation

### ✅ Session 14 Completed Steps

1. ✅ `calculateLocalSSIM()` — 50×50 window, clamp+shift edges, returns global SSIM for ≤50 bins
2. ✅ Interface: `ARCHCODE_LSSIM` added to `UnifiedAtlasRow`
3. ✅ Pipeline: verdict/pearl use LSSIM; global SSIM preserved for backward compat
4. ✅ Statistics: `mean_lssim_all/pathogenic/benign` in categoryBreakdown + summary JSON
5. ✅ HBB 30kb regression: LSSIM ≡ SSIM, 20 pearls preserved
6. ✅ All 6 loci re-run (HBB 30kb, 95kb, CFTR, TP53, BRCA1, MLH1)
7. ✅ Python scripts updated: `analyze_positional_signal.py` reads ARCHCODE_LSSIM; `tda_proof_of_concept.py` computes local SSIM
8. ✅ Within-category re-run: CFTR/TP53/BRCA1/MLH1
9. ✅ TDA re-run: CFTR/TP53/BRCA1/MLH1
10. ✅ Manuscript v2.3: ~18 edits (Abstract, Significance, Table 6, Methods, Results, Limitations, Discussion)

---

## Ключевые файлы (changed in session 14)

| Файл                                   | Изменения                                                             |
| -------------------------------------- | --------------------------------------------------------------------- |
| `scripts/generate-unified-atlas.ts`    | +calculateLocalSSIM(), LSSIM in interface/compute/verdict/pearl/stats |
| `scripts/analyze_positional_signal.py` | Reads ARCHCODE_LSSIM (fallback to ARCHCODE_SSIM)                      |
| `scripts/tda_proof_of_concept.py`      | +\_compute_local_ssim(), LSSIM correlations                           |
| `manuscript/FULL_MANUSCRIPT.md`        | v2.3 (~18 edits, LSSIM throughout)                                    |
| `results/*.csv`                        | All 6 CSVs regenerated with ARCHCODE_LSSIM column                     |
| `results/UNIFIED_ATLAS_SUMMARY_*.json` | All 6 JSONs updated with lssim statistics                             |

---

## Все фазы

1–22. (see previous sessions) 23. ✅ **LSSIM threshold recalibration** — 50×50 local window, all loci re-run, manuscript v2.3

---

## v3.0 Roadmap — Post-Submission

1. ~~TP53~~ ✅
2. ~~BRCA1~~ ✅
3. ~~bioRxiv submission~~ ✅ (BIORXIV/2026/708672)
4. ~~MLH1~~ ✅
5. ~~LSSIM threshold recalibration~~ ✅
6. **Git commit** — LSSIM + manuscript v2.3
7. **LDLR** — Tier 1 (3,721 variants, HepG2 Hi-C, chr19)
8. **SCN5A** — Tier 1 (2,333 variants, iPSC-CM Hi-C, chr3)
9. **Akita/Enformer benchmarking** — pearl detection rate comparison
10. **bioRxiv v2 update** — submit revised preprint with LSSIM

---

## Для следующей сессии

1. **Git commit** — LSSIM + manuscript v2.3 (all changes uncommitted)
2. Проверь: получен ли DOI от bioRxiv?
3. **bioRxiv v2 preprint** — submit updated version with LSSIM
4. **LDLR implementation** — next locus
5. **Akita/Enformer research** — feasibility check
