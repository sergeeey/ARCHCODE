# Active Context — ARCHCODE

**Last Updated:** 2026-07-07
**Branch:** feat/archcode-sv-v1 (pushed to origin through 8075c15, see git log / Auto-commit log below).
  main updated via integrity/merge-bioadv-readme → pushed 1b14805;
  manuscript reference/abstract fixes on integrity/fix-manuscript-refs → pushed 1137e9c.
**GitHub:** https://github.com/sergeeey/ARCHCODE — all commits above confirmed on origin.

## DONE (2026-07-07) — Hypothesis C: synonymous-variant codon-usage optimality, REJECT

Ran the full pipeline for Hypothesis C (mRNA-stability/codon-optimality of ClinVar synonymous
variants), the "1" from the user's "1 и 2 го" instruction (2 = gnomAD follow-up, done earlier,
commit 8075c15). L0 gate (Predictive) + mandatory Novelty Check run first: broad mechanism
(codon optimality -> mRNA decay -> disease) is NOT novel (Nature Rev Mol Cell Biol 2017;
published multi-feature ensemble ClinVar predictors already exist, e.g. PMC7565489,
PMC8682775) -- honestly reformulated to test the SINGLE simplest proxy (Delta codon-usage
frequency alone, no other features) in isolation, matching this project's "test simple
features before trusting complex ones" discipline.

Real public data throughout: Kazusa human codon usage table, ClinVar genome-wide (829
pathogenic / 685,044 benign synonymous SNVs -- benign subsampled to 5,000, seed=42,
pre-registered before any VEP call), Ensembl VEP GRCh37 `codons` field, GENCODE v47lift37
exon boundaries (splice-proximity sensitivity check).

**Result: REJECT.** Primary Mann-Whitney/Cliff's delta = -0.151 (p_bh=7.9e-12), sensitivity
(>=10bp from splice boundary) = -0.166 (p_bh=2.3e-6). Direction correct in both, highly
"significant" by p-value, but BOTH below the pre-registered MCID (|delta|>=0.2) -- same
"significant only due to large n, not practically meaningful" pattern as the orphan-enhancer
null result. Notably the sensitivity check (splice-junction confound control) did NOT weaken
the effect, arguing the small signal is real and not purely a splicing-proxy artifact -- just
too small on its own to be useful, consistent with why published tools use it as one of many
ensemble features rather than standalone. Filed to
`null_results/20260707-synonymous-codon-optimality.md`. Engineering note: first VEP-annotation
run died at 2850/5829 batches (my own error: combined an explicit Bash `timeout` with
`run_in_background`, which still hard-kills at the timeout) with the cache only written at
loop end -- lost all progress. Fixed `scripts/synonymous_codon_optimality_analysis.py` to
save the VEP cache incrementally every batch and resume from partial cache; reran cleanly.

Both items of "1 и 2 го" are now complete. Six `null_results/` entries total, 1
CANDIDATE FLAGGED (BCL11A gnomAD lead, not yet functionally followed up), 0 confirmed
positive discoveries -- but every negative result this session has a specific, mechanistic
reason (genome build, gene-symbol contamination, wrong database class, underpowered
subgroup, effect-size-below-practical-threshold), not just "didn't work."

## DONE (2026-07-02, commit 3859583) — Hypothesis B': BCL11A enhancer VUS search, INCONCLUSIVE
[summarized] Before running Hypothesis B (BCL11A erythroid enhancer + Casgevy connection) as originally
covering all 3 published DHS sites.

**Result: 0 VUS found.** Not a biological null -- ClinVar is structurally the wrong database
for quantitative-trait GWAS variants (populated by clinical diagnostic labs, not population
genetics). Filed as INCONCLUSIVE (not REJECT) with a concrete next step: gnomAD population-
frequency lookup at this locus, not another ClinVar query. Not yet executed.

**Full session arc today (chronological, all in null_results/ or experiments/):**
1. exp_orphan_enhancers — REJECT (3 real bugs found+fixed: strand, hg19/hg38 mismatch,
   has_vus_overlap false-negative caught by Agent(reviewer))
2. 3-agent blind audit — found 2 process gaps (Loop That Stayed never formalized, D3 clone
   never tested) + tested the agents' convergent tissue-matching hypothesis -> REJECT
3. exp_enhancer_proximity_replication — GATA1 "pearl" (OR=10.83) found, then RETRACTED after
   user asked to strengthen it -> traced to a GeneSymbol-filter bug -> REJECT (0/3 loci)
4. exp_bcl11a_enhancer_vus (Hypothesis B') — 0 VUS, wrong database, INCONCLUSIVE

Net: 5 null_results/ entries, 0 confirmed positive discoveries, but 4 real bugs caught before
being reported as findings, and every negative result has a clear, specific reason (not just
"didn't work") — genome build, gene-symbol contamination, wrong database class, underpowered
subgroup. This is what the falsification-first methodology is supposed to produce.

## DONE (2026-07-02, commit 8120399) — GATA1 "pearl" from Hypothesis A retracted: REJECT
[summarized] Follow-up to the entry below (exp_enhancer_proximity_replication, was REPEAT with GATA1
- BCL11A: unchanged (large gene, window ~= gene body, minimal contamination)

**Final verdict: REJECT (0/3 loci meet MCID)**, filed to
`null_results/20260702-enhancer-proximity-replication.md`. Superseded the earlier REPEAT
verdict in both `decision.md` and `claim.md` frontmatter -- the timeline (both runs) is kept
visible in decision.md rather than silently overwritten, so the false-positive-then-caught
pattern is auditable later.

**Reusable lesson (also worth remembering for any future ClinVar-by-locus fetch):** when
extracting ClinVar variants for a named gene by coordinate window, ALWAYS filter by
ClinVar's own `GeneSymbol` column too -- coordinate windows alone silently admit neighboring
genes' variants, especially in gene-dense regions (chr19, chrX gene clusters). This bug was
specific to this one fetch script; `exp_orphan_enhancers` and `exp_archcode_sv` used
different, unaffected filtering logic.

**Process note:** this is the second time today a "promising positive result" was killed by
being asked to survive one more round of scrutiny before being trusted (see also: 3-agent
tissue-matching hypothesis, also REJECTed on testing). Treat any single-round positive
result in this project as provisional by default until it survives at least one adversarial
re-check -- this has now happened 2/2 times this session.

## DONE (2026-07-02, commit 5029918) — exp_enhancer_proximity_replication: REPEAT (1/3 loci)
[summarized] Hypothesis A (from the post-audit hypothesis menu): does the ONE surviving strong signal in
  original SNV/LSSIM project, rather than just diluting it. n=14 pathogenic missense is
  small -- a lead worth an independent replication cohort, not a confirmed finding yet.
- **KLF1:** null, WRONG direction (benign variants closer to peaks than pathogenic),
  well-powered (n=1139). Real evidence against generalization at this locus.
- **BCL11A: data-quality caveat, NOT a fair test.** Nearest H3K27ac peak to the whole gene
  body in this specific archived ENCODE replicate (ENCFF252DWA) is 1.7Mb away -- vastly
  exceeds chr2's ~67kb average peak spacing, biologically implausible for a locus with a
  famous erythroid enhancer (Casgevy/exa-cel therapy target). Flagged as a likely coverage
  gap in this one dataset, not a real absence of signal -- needs a different H3K27ac
  replicate before this locus counts as tested.

Full writeup: `experiments/exp_enhancer_proximity_replication/decision.md`. Reusable asset
committed: `data/encode_cache/ENCFF252DWA_H3K27ac_K562_hg19.bed.gz` (K562 H3K27ac, hg19,
52,000 peaks, 955KB -- small enough to keep in git unlike the large ABC/ClinVar files).

**Next steps if continuing this thread:** (1) re-fetch H3K27ac/ATAC-seq for BCL11A from a
non-archived ENCODE experiment to resolve the data gap; (2) find an independent GATA1
variant set to replicate the missense-proximity signal without reusing the same 14 variants;
(3) proceed to Hypothesis B (BCL11A erythroid enhancer + HbF GWAS) or C (synonymous variant
mRNA stability) from the same menu.

## DONE (2026-07-02, commit 768bf82) — Independent blind-spot audit + 2 follow-up null_results
[summarized] Ran 3 parallel Agent(Explore) audits, mutually blind (no shared context, didn't see each
   available in this environment (verified: `which STAR/hisat2/salmon` all empty, no pysam).
   Marked REPEAT (partial), not full REJECT — this is a genuinely open question, not faked.

2. **All 3 agents independently proposed the same fix for the orphan-enhancer REJECT**:
   restrict to tissue-matched (erythroid) ABC biosamples, since that's the one condition
   under which this project's strongest surviving signal (enhancer-proximity OR=34.05 at
   HBB) was found. Tested it (`scripts/orphan_enhancer_tissue_matched_exploratory.py`,
   EXPLORATORY/post-hoc, flagged as such): erythroid-only genome-wide OR=1.158 (WEAKER than
   the pooled OR=1.221, not stronger); HBB-locus-restricted n=36 (uninformative). The
   convergent 3-agent hypothesis did NOT pan out — filed as
   `null_results/20260702-orphan-enhancer-tissue-matched-followup.md` specifically so this
   idea isn't blindly re-tried in a future session.

3. A 4th agent hand-verified both existing REJECT verdicts by recomputing per-stratum odds
   ratios directly from the results JSON — confirmed both are robust nulls, no hidden signal
   averaged away by pooling.

**Net effect**: `null_results/` now has 4 entries. No new positive discovery, but two loose
threads closed (one fully, one partially) and one specific "maybe we missed it" hypothesis
(tissue-matching) explicitly tested and ruled out rather than left as an assumption.

## DONE (2026-07-02) — exp_orphan_enhancers: REJECT, filed to null_results/
[summarized] Hypothesis: are ClinVar VUS enriched near "orphan" enhancers (ABC-model target gene !=
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
[summarized] **Реальная точка сборки для Bioinformatics Advances submission:** `manuscript/main.typ`
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
[summarized] **boyko-method полный аудит проекта** нашёл: (1) SNV LSSIM AUC=0.977 давно опровергнут внутри
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
[summarized] [summarized] **ЦЕЛЬ ДОСТИГНУТА: FPR=8% (≤15%) AND Recall=68% (≥65%) на ClinVar n=50**
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
[summarized] [summarized] [summarized] ### Коммит: `6609526`
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
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Файл:** `scripts/archcode_sv.py`
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
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] ### Primary: Lupiáñez 2015 (EPHA4 locus, chr2) — 5/5
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
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] (empty section)
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
[summarized] - [2026-07-03 16:49] `8075c15`: feat: gnomAD follow-up on exp_bcl11a_enhancer_vus вЂ” 1 concrete candidate flagged
- [2026-07-03 16:31] `e2c5085`: docs: update activeContext with Hypothesis B' results and full session arc
- [2026-07-03 16:30] `3859583`: feat: exp_bcl11a_enhancer_vus вЂ” Hypothesis B' (honest reformulation of BCL11A/Casgevy idea)
- [2026-07-03 16:08] `ffcdbf5`: docs: document GATA1 pearl retraction and reusable GeneSymbol-filter lesson
- [2026-07-03 15:29] `8120399`: fix: GATA1 enhancer-proximity pearl was a gene-symbol filtering bug вЂ” REJECT
- [2026-07-03 14:29] `1324680`: docs: update activeContext with enhancer-proximity replication results
- [2026-07-03 13:40] `5029918`: feat: exp_enhancer_proximity_replication вЂ” test HBB enhancer-proximity signal at 3 new loci
- [2026-07-03 12:53] `4b156f0`: docs: update activeContext with blind-spot audit + follow-up results
- [2026-07-03 12:49] `768bf82`: feat: independent 3-agent blind-spot audit + follow-up on both open threads
- [2026-07-03 11:20] `fb6cdb8`: docs: update activeContext with final exp_orphan_enhancers REJECT status
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
