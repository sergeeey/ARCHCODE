# Active Context — ARCHCODE

**Last Updated:** 2026-07-02
**Branch:** feat/archcode-sv-v1 (pushed to origin, incl. b463906 + 4407081 exp_orphan_enhancers).
  main updated via integrity/merge-bioadv-readme → pushed 1b14805;
  manuscript reference/abstract fixes on integrity/fix-manuscript-refs → pushed 1137e9c.
**GitHub:** https://github.com/sergeeey/ARCHCODE — all commits above confirmed on origin.

## DONE (2026-07-02) — exp_orphan_enhancers: REJECT, filed to null_results/

Hypothesis: are ClinVar VUS enriched near "orphan" enhancers (ABC-model target gene !=
nearest gene) vs regular enhancers? Data: ABC model (Nasser 2021, 131 biosamples, 325MB,
NOT in git — reproducible via `scripts/fetch_gencode_hg19_stranded.py` /
`fetch_clinvar_vus_hg19.py`) + ClinVar VUS genome-wide (also NOT in git, same reason).

**Three real bugs found and fixed before trusting any result** — a clean demonstration of
verify-before-claim discipline surviving contact with a brand-new pipeline:
1. GENCODE gene coords lacked strand → wrong TSS for ~49% of genes (minus-strand).
2. **Genome build mismatch**: ABC predictions file is hg19/GRCh37, not hg38 — confirmed
   empirically (NOC2L TSS in ABC file=894679 matches hg19=894689; hg38=959309, ~65kb miss).
   Caused an implausible 85-91% "orphan" rate (lit. range ~30-40%) in two early runs.
3. **`has_vus_overlap()` false-negative bug** (caught by `Agent(reviewer)`, not by me): a
   fixed +-5-record window around a bisect insertion point silently missed wide-spanning
   VUS (large CNVs/indels) behind dense variant clusters. Fixed with an exact O(log n)
   running-max-end interval check, verified against the reviewer's exact failing case +
   4 more unit tests.

**Final result (both bugs fixed, orphan rate now 43% — plausible)**:
Calibration OR=0.999 (p=0.93), held-out OR=1.221 (n=661,294, p~0 — significant only due to
enormous n, not practically meaningful). Pre-registered MCID (OR>=2.0) not met.
**REJECT** → `null_results/20260702-orphan-enhancer-vus-enrichment.md`.

An earlier `results.json` (07:21) was stale (predated the hg19 fix, silently identical to a
buggy run) — caught via file-timestamp comparison before it could be cited. Do not trust a
results file without checking it postdates the code/data it claims to summarize.

**Status:** ARCHCODE-SV Step+2 REPEAT (not PROMOTE) — out-of-sample FPR=22.7%/Recall=36.4%, MCID NOT MET.
  Physics layer FALSIFIED (H3 ablation, Youden J≈0). Gene-constraint layer shows real modest signal (J=0.137).
  SNV LSSIM AUC=0.977 finding formally REJECTed → null_results/. README/GitHub main now honest (commit 1b14805).
  Bioinformatics Advances submission draft (manuscript/main.typ) pre-submission checklist FAILED initial pass:
  5 broken citations + Abstract/Body mismatch found and fixed locally (commit 1137e9c on
  integrity/fix-manuscript-refs, not pushed — awaiting user confirmation).

---

## ЧТО БЫЛО СДЕЛАНО (2026-07-01, часть 2) — Manuscript pre-submission checklist audit [VERIFIED-REAL]

**Реальная точка сборки для Bioinformatics Advances submission:** `manuscript/main.typ`
(верхнеуровневый) — включает `abstract_content.typ` + `taxonomy_paper/body_content.typ` +
`references.typ` вместе. (НЕ `taxonomy_paper/main.typ` — та версия не используется.)

**Найдено и исправлено (все DOI перепроверены через CrossRef API, не только WebFetch):**
1. 4 ссылки: реальные авторы/тема, но неверный DOI/год/страницы —
   Zhou (bioRxiv 2022→Nature Genetics 2018), Baralle (2018→2005), Fudenberg-Akita
   (неверный DOI+подзаголовок), Avsec-AlphaGenome (404→Nature 2026, реальный DOI)
2. Temple et al. — **выдуманный список соавторов** (4 из 5 не имеют отношения к статье);
   также "in press" без DOI — прямое нарушение правила CLAUDE.md
3. Zenodo DOI в Code/Data Availability указывал на чужой R-пакет → исправлен на
   верный ARCHCODE DOI (18908214, совпадает с cover letter)
4. **Abstract и Body — из разных черновиков**: "Simpson's Paradox" (3× в Abstract) —
   0 раз в Body; числа 0.791/0.640/0.657/MLH1 p=0.022/TERT+33-53%/ρ=0.014 — нигде
   в Body. Abstract переписан заново на основе реальных чисел из Body (0.977→0.551,
   within-category median=0.52, TP53 splice_region=0.69, enhancer proximity OR=34.05,
   AlphaGenome CAGE d=-2.1 с честной pseudoreplication оговоркой)

**Не исправлено (вне скоупа, для сведения):**
- Старый `manuscript/body_content.typ` (другой документ, не участвует в текущей заявке)
  имеет СВОЙ отдельный список литературы с ТРЕТЬЕЙ версией цитаты Baralle
- Affiliation/email автора расходится между `manuscript/main.typ` (ronininstitute.org) и
  cover letter (gmail.com) — личная информация автора, не мне решать какая верна

**Коммит:** `1137e9c` на ветке `integrity/fix-manuscript-refs`, worktree
`C:/Users/sboi/ARCHCODE_manuscript_fix` — НЕ запушено, ждёт подтверждения пользователя.

---

## ЧТО БЫЛО СДЕЛАНО (2026-07-01, часть 1) — Full audit + honest reconciliation [VERIFIED-REAL]

**boyko-method полный аудит проекта** нашёл: (1) SNV LSSIM AUC=0.977 давно опровергнут внутри
репо (2026-06-05), но никогда не долетал до README/GitHub; (2) уже существовала честная версия
манускрипта на неслитой ветке `manuscript/bioadv-submission` (26.06); (3) пороги Step+2 подобраны
глядя на ошибки на том же n=50 (fit-to-test-set); (4) `null_results/`/`parked/` никогда не
использовались, хотя правила проекта их требуют.

**Независимая валидация ARCHCODE-SV Step+2** (20 хромосом вне калибровки, n=44):
FPR=22.7%, Recall=36.4% — HE соответствует MCID (FPR≤15% AND Recall≥65%), заявленному 2026-06-26.

**H3-абляция [VERIFIED-REAL]:** физический слой (`boundary_ratio>1.35`) сам по себе — Youden J≈0
и на калибровке (-0.040), и на валидации (+0.045). Вся классифицирующая сила Step+2 идёт от
gnomAD LOEUF/pLI + CTCF-adjacency эвристики, НЕ от loop-extrusion физики.
См. `experiments/exp_archcode_sv/h3_physics_ablation.md`.

**Исправлено:**
- `experiments/exp_archcode_sv/decision.md` — добавлен addendum, verdict для ClinVar/Step+2 = REPEAT
- `experiments/exp_archcode_sv/estimand.md` — создан (ретроактивно, с явным disclosure нарушения timing)
- `null_results/20260605-archcode-lssim-category-artifact.md` — REJECT формализован
- `README.md` (main, GitHub) — добавлена оговорка про AUC=0.977 под headline-таблицей
- `submission_metadata.json` (main) — убраны нерабочие пути, помечена нестыковка версий
- `results/p2_hbb_truth/HBB_TRUTH_AUDIT.md` — перенесён в main (был только на archcode-sv-v1)

**Для Paper 3 §3.7:** НЕ писать "physics-based classifier". Правильно: "gnomAD gene-constraint
classifier with CTCF-adjacency filter; physics computed but shown non-discriminative (H3)".

---

## ЧТО БЫЛО СДЕЛАНО (2026-06-26) — Step +2 TAD-aware Gene Constraint [VERIFIED-REAL] `a02eeb5`
[summarized] **ЦЕЛЬ ДОСТИГНУТА: FPR=8% (≤15%) AND Recall=68% (≥65%) на ClinVar n=50**
| FPR | 0.800 | 0.480 | **0.080** |
| Recall | 0.760 | 0.680 | **0.680** |
| Precision | 0.487 | 0.586 | **0.895** |

### Ключевые открытия:
- ATG4B (chr2:241.7Mb): CTCF-барьер score=58.3 между ATG4B и SV → разные TAD → FP устранён
- KANSL1 (chr17:46.2Mb): CTCF-барьер между KANSL1 и SV → FP устранён  
- CTNS (chr17:3.6Mb, LOEUF=0.799): тело SV → tier 1 с порогом 0.80 → TP восстановлен

### Новые файлы:
- `scripts/archcode_sv.py` — добавлены `load_ctcf_strong()`, `has_ctcf_barrier()`, `find_hi_genes_step2()`
- `scripts/clinvar_step2_analysis.py` — Step +2 ClinVar runner
- `experiments/exp_archcode_sv/clinvar_step2_results.json` — результаты
- `experiments/exp_archcode_sv/clinvar_analysis.md` — обновлён с полным Step +2 анализом

### Оставшиеся 2 FP:
- PDCD1 (pLI=0.42, LOEUF=0.66) в теле benign SV chr2:241.77Mb — не классический HI ген
- NSF (pLI=0.02, LOEUF=0.60) в теле benign SV chr17:46.27Mb — не классический HI ген

---

## ЧТО БЫЛО СДЕЛАНО (2026-06-26) — Step +1 gnomAD Gene Constraint [VERIFIED-REAL]
[summarized] [summarized] ### Коммит: `6609526`
- `data/input/gencode_genes_chr2_7_17.json` — GENCODE v47, 3,368 protein-coding генов на chr2/7/17
- `scripts/archcode_sv.py` — добавлены `load_gene_constraint()` + `find_hi_genes()` + параметр `gene_constraint` в `score_sv()`
- `scripts/clinvar_step1_analysis.py` — применяет Step +1 к clinvar_results.json
- `experiments/exp_archcode_sv/clinvar_step1_results.json` — результаты Step +1
- `experiments/exp_archcode_sv/clinvar_analysis.md` — обновлён с полным анализом

**Результаты [VERIFIED-REAL] ClinVar n=50:**

| Метрика | Step 0 | Step +1 | Δ |
|---|---|---|---|
| FPR | 0.800 | 0.480 | **-0.320** |
| Recall | 0.760 | 0.680 | -0.080 |
| Precision | 0.487 | 0.586 | +0.099 |

**Ключевые находки:**
- chr2:110 Mb (ACMSD pLI≈0, TMEM163 pLI=0.04): 7 FPs → правильно rescued как DISRUPTED_NO_HI_GENE
- chr2:241-242 Mb (ATG4B pLI=0.96): 12 FPs остались — ATG4B в ±500kb окне, но вне тела SV → нужен TAD-aware window (Step +2)
- 12/12 benchmark score СОХРАНЁН

---

## ЧТО БЫЛО СДЕЛАНО (2026-06-24) — ARCHCODE-SV Pivot

### Контекст: почему пивот

Original ARCHCODE = SNV pathogenicity predictor. Проблема: global AUC 0.975 — артефакт категориальной таблицы `CATEGORICAL_EFFECTS` в `scripts/generate-unified-atlas.ts:291`. Реальной 3D-физики нет, только lookup. Enformer (Google DeepMind) на тех же вариантах (HBB, intronic) = AUC 0.86 vs ARCHCODE 0.57.

**Пивот:** из SNV → в Structural Variants (SVs). Физический движок ARCHCODE (Kramer kinetics + CTCF barriers) идеально подходит для SVs. Конкурентов нет — ни один инструмент не делает физику TAD-disruption без GPU и обучения.

---






## ARCHCODE-SV: что реализовано
[summarized] [summarized] [summarized] [summarized] [summarized] **Файл:** `scripts/archcode_sv.py`
   - duplication: дублируем CTCF
4. boundary_delta() — ratio = cross_mut / cross_wt у сайта изменённого CTCF
5. Verdict: ratio > 1.35 → DISRUPTED (pathogenic), иначе → INTACT (benign)
```

**Порог 1.35 обоснован физически:**
- score > 40 → strength > 0.367 → ratio > 1.4 → выше порога
- score < 30 → strength < 0.35 → ratio ≈ 1.30 → ниже порога
- Это соответствует CTCF IDR confidence cutoff

### Ключевые параметры (Kramer kinetics)
```python
K_BASE = 0.05   # base extrusion rate
ALPHA  = 0.92   # pausing strength (from Sabaté 2024 bioRxiv)
GAMMA  = 0.80   # loop extension factor
RESOLUTION = 5000   # 5kb bins
N_BINS     = 200    # 1Mb window
```

---

## Benchmarks: результаты
[summarized] [summarized] [summarized] [summarized] [summarized] ### Primary: Lupiáñez 2015 (EPHA4 locus, chr2) — 5/5
| Path_SOX9_large | del chr17:69.8-71.5 Mb | 1.629 | DISRUPTED | ✅ |
| Ben_SOX9_desert | del chr17:71.1-71.9 Mb | 1.300 | INTACT | ✅ |
| Ben_SOX9_inv | inv chr17:71.2-71.8 Mb | 1.300 | INTACT | ✅ |

### Generalizability: SHH/LMBR1 locus (chr7) — 3/3 [FL Standard 2026-06-26]
**Источник:** Lettice 2003 (Nat Rev Genet), Anderson 2014 (Development) — boundary disruption mechanism
**Ключевой CTCF:** chr7:156,909,000 (score=314.6) — граница между SHH-LMBR1 и KCNJ2 TAD
**SHH-ZRS CTCF desert:** chr7:156.16-156.47 Mb (317 kb gap, 0 IDR peaks)
**SHH TAD gap:** chr7:155.46-155.52 Mb (70 kb, 0 IDR peaks)

| Label | SV | Ratio | Verdict | Correct? |
|---|---|---|---|---|
| Path_SHH_boundary | del chr7:156.65-157.0 Mb | 3.299 | DISRUPTED | ✅ |
| Ben_SHH_desert | del chr7:156.2-156.4 Mb | 1.000 | INTACT | ✅ |
| Ben_SHH_gap | del chr7:155.46-155.52 Mb | 1.000 | INTACT | ✅ |

### ИТОГ: 12/12 на 3 локусах, 3 хромосомах (chr2 + chr17 + chr7), 3 типа SVs
**FL Standard PROMOTE** — experiments/exp_archcode_sv/decision.md

---

## Enformer experiment (параллельная ветка, завершена)

**Файл:** `results/paper3/experiments/exp_akita_mirror/DESIGN.md`
**Результаты:** `results_enformer_mini.json`

| Метрика | Значение |
|---|---|
| Enformer global AUC (HBB) | 0.65 |
| Enformer within-intronic AUC | **0.86** (n=6, p=0.003) |
| ARCHCODE within-intronic AUC | 0.57 (случайность) |
| mirror_gap | 0.0 (АРТЕФАКТ — математически = auc − (1−auc) = 0 всегда) |

**Вывод:** HBB intronic AUC 0.86 vs 0.57 — иллюстративное сравнение. Статус: ILLUSTRATIVE (n=6 слишком мало).

---






## Структура ключевых файлов
[summarized] [summarized] [summarized] [summarized] [summarized] (empty section)
```
scripts/
  archcode_sv.py              ← ARCHCODE-SV: физический движок для SVs (НОВЫЙ)
  generate-unified-atlas.ts   ← старый SNV pipeline (CATEGORICAL_EFFECTS bug)

data/input/ctcf/
  K562_CTCF_hg38.bed          ← ENCODE CTCF K562 hg38 (46,160 пиков, НОВЫЙ)

results/paper3/
  PAPER3_SKELETON.md           ← манускрипт Paper 3 (negative results note)
  experiments/exp_akita_mirror/
    DESIGN.md                  ← Enformer эксперимент, Stage 1 Complete
    results_enformer_mini.json ← 152/152 вариантов, HBB locus
  figures/Figure1-5.png        ← финальные фигуры (300 dpi)

results/p5_instrument/
  INSTRUMENT_CHARACTERIZATION.md ← характеризация инструмента (transfer function)
```

---

## Следующие шаги (приоритет)

1. **✅ DONE (2026-06-26):** FL Standard claim.md + controls.md + decision.md → PROMOTE 12/12
2. **✅ DONE (2026-06-26):** ClinVar validation n=50 → Step 0: FPR=80%, Step +1: FPR=48%
3. **Step +2 (TAD-aware window)** — вместо ±500kb найти границы TAD из CTCF landscape самого SV
   - Цель: исправить chr2:241-242 Mb FPs (ATG4B вне тела SV, но в 500kb окне)
   - Подход: расширить `score_sv()` чтобы возвращал `tad_extent` (левый + правый CTCF boundary)
4. **Paper 3: §3.7** — добавить ARCHCODE-SV + Step +1 как proof-of-concept extension
5. **bioRxiv/arXiv** — Paper 3 как negative-results + SV pivot note

---






## История сессий (краткая)

- **2026-03-08:** bioRxiv submission v2.16, Paper 3 skeleton
- **2026-06-05:** Falsification-First reboot, instrument characterization
- **2026-06-23:** Hypothesis revival, Enformer comparison planned
- **2026-06-24:** 
  - Enformer Stage 1 Complete (HBB, 152/152)
  - Deep research → SV pivot decision
  - ARCHCODE-SV implemented (4h): 9/9 on 2 loci without training





## Auto-commit log
- [2026-07-03 11:19] `4407081`: fix: has_vus_overlap() false-negative bug (reviewer-caught) + final REJECT result
- [2026-07-03 11:09] `b463906`: feat: exp_orphan_enhancers вЂ” hypothesis test on ABC orphan enhancers vs ClinVar VUS
- [2026-07-01 16:55] `59345c8`: fix: honest close-out вЂ” external validation, H3 physics ablation, FL process gaps
- [2026-07-01 16:34] `59345c8`: fix: honest close-out вЂ” external validation, H3 physics ablation, FL process gaps
- [2026-07-01 16:25] `babdf56`: fix: reproducibility вЂ” remove hardcoded paths, add data provenance, add numpy dep
- [2026-06-26 17:13] `babdf56`: fix: reproducibility вЂ” remove hardcoded paths, add data provenance, add numpy dep
- [2026-06-26 16:54] `a02eeb5`: feat: ARCHCODE-SV Step +2 вЂ” TAD-aware gene constraint [VERIFIED-REAL]
- [2026-06-26 13:03] `6609526`: feat: ARCHCODE-SV Step +1 вЂ” gnomAD gene constraint filter [VERIFIED-REAL]
- [2026-06-26 10:07] `3da89d4`: feat: ARCHCODE-SV ClinVar real-world validation [VERIFIED-REAL]
- [2026-06-26 09:51] `748d72d`: feat: ARCHCODE-SV v1.1 вЂ” FL Standard PROMOTE, 12/12 on chr2+chr17+chr7
- [2026-06-26 09:38] `7480acc`: feat: ARCHCODE-SV v1.0 вЂ” physics-based structural variant pathogenicity engine
