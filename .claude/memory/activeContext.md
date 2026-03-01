# Active Context — ARCHCODE

**Last Updated:** 2026-03-01 (session 16: hallucination audit + integrity tools)
**Branch:** main
**Last Commit:** 4c558a4 (hallucination audit fixes — pushed)
**GitHub:** https://github.com/sergeeey/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — awaiting screening
**Status:** Integrity tools created. Ready for commit + next locus.

---

## Текущий статус проекта

**Фаза:** v2.4 — Post-audit, integrity enforcement layer built

### Session 16: Hallucination Audit + Integrity Tools

**Commits this session (all pushed):**

- `558ae7b` — MLH1 + LSSIM + manuscript v2.3 (39 files)
- `eebf11e` — LSSIM sensitivity analysis script + results
- `4c558a4` — hallucination audit fixes (5 DOIs, Table 6, TP53 count, overclaim guards)

**Hallucination audit findings (fixed in 4c558a4):**

- 5 citation DOIs/journals corrected (Akita, Taher, Baralle, Harrison, Whalen)
- Table 6 Global SSIM ranges recalculated from per-variant CSV min/max
- TP53 variant count: 2,795→2,794, propagated through all occurrences
- JSON interpretations updated with ΔAUC threshold guard (`_interpret_lr()`)

**Integrity tools created (uncommitted):**

| Tool                                               | Purpose                                                                              |
| -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `scripts/verify_manuscript.py`                     | 3-module automated verification: DOI check, Table 6 vs CSV/JSON, overclaim detection |
| `scripts/verify_manuscript.py --fix-table6`        | Auto-generates Table 6 from real data (CSV + JSON)                                   |
| `scripts/verify_manuscript.py --update-manuscript` | Writes generated Table 6 directly into manuscript                                    |
| `scripts/verify_manuscript.py --skip-doi`          | Offline mode (skips HTTP DOI checks)                                                 |
| `.claude/agents/integrity-checker.md`              | Agent for periodic integrity verification                                            |

**Verification results:** ALL CHECKS PASSED (14 DOIs verified, 5 loci consistent, 0 overclaims)

### Root cause analysis

CLAUDE.md policy prevents **intentional** fabrication but misses **drift** errors:

- Cross-source drift: numbers copied from wrong analysis window
- Accumulation errors: off-by-one from pipeline re-runs
- Stale logic: JSON interpretation not updated after methodology change

**Solution:** 3 layers of automated enforcement:

1. **verify_manuscript.py** — catches drift at commit time
2. **Generative Table 6** — eliminates manual copy entirely
3. **integrity-checker agent** — periodic holistic audit

---

## Ключевые файлы (session 16)

| Файл                                   | Изменения                                              |
| -------------------------------------- | ------------------------------------------------------ |
| `scripts/verify_manuscript.py`         | NEW — 917 lines, 3 modules, 4 modes                    |
| `.claude/agents/integrity-checker.md`  | NEW — agent definition for periodic verification       |
| `manuscript/FULL_MANUSCRIPT.md`        | 5 DOI fixes, Table 6 fix, TP53 count fix, inline fixes |
| `scripts/analyze_positional_signal.py` | `_interpret_lr()` function with ΔAUC threshold         |
| `results/positional_signal_brca1.json` | overclaim → power effect disclaimer                    |
| `results/positional_signal_mlh1.json`  | overclaim → power effect disclaimer                    |

---

## v3.0 Roadmap

1. ~~TP53~~ ✅
2. ~~BRCA1~~ ✅
3. ~~bioRxiv submission~~ ✅ (BIORXIV/2026/708672)
4. ~~MLH1~~ ✅
5. ~~LSSIM threshold recalibration~~ ✅
6. ~~LSSIM sensitivity analysis~~ ✅
7. ~~Hallucination audit~~ ✅
8. ~~Integrity enforcement tools~~ ✅
9. **LDLR** — Tier 1 (3,721 variants, HepG2 Hi-C, chr19)
10. **SCN5A** — Tier 1 (2,333 variants, iPSC-CM Hi-C, chr3)
11. **Akita/Enformer benchmarking**
12. **bioRxiv v2 update** — submit with LSSIM + audit fixes

---

## Для следующей сессии

1. **Git commit** integrity tools (verify_manuscript.py + integrity-checker agent)
2. Проверь: получен ли DOI от bioRxiv?
3. **bioRxiv v2 preprint** — submit updated version
4. **LDLR implementation** — next locus
5. Run `python scripts/verify_manuscript.py` before every commit
