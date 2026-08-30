# Active Context — ARCHCODE Project

**Last Updated:** 2026-08-30
**Current Branch:** experiment/spectral-collapse-pilot
**Session Focus:** ⏸️ **PROJECT STILL PAUSED.** No ARCHCODE code/manuscript work resumed. 2026-08-29 session was exploratory/archival (see below), not a resumption. Do NOT raise new ARCHCODE work unprompted.
**Reality source:** session 2026-08-30 (T2 topology_control — три KILL, гипотеза исчерпана)

## 🧪 Session 2026-08-30: T2 (topology_control) — три локальных правила убиты, гипотеза исчерпана

⚠️ **Это НЕ возобновление ARCHCODE.** Работа шла в `topology_control/` (ATR Framework) —
соседний трек, не рукопись и не код ARCHCODE. Проект ARCHCODE остаётся на паузе.

**Вердикт T2:** гипотеза «TOP2 распутывает ДНК по локальному геометрическому правилу»
закрыта по всем дешёвым вариантам Relaxation Map.

| Вариант | Правило | Медиана `advantage_score` (30 seed) | Коммит |
|---|---|---|---|
| v2 | угол перекрёстка | 0.919 | `6d683f1` |
| v3 / V1 | кривизна | 1.000 | `7fa2393` |
| v4 / V2 | плотность зацеплений | 1.111 | `62b3251` |
| — | **оракул** (знает `Lk`, не локальное правило) | **0.106 / 0.106 / 0.111** | потолок |

**Почему это информативный NULL, а не пустой:** потолок оракула устойчив в трёх
независимых прогонах — упрощение достижимо примерно в 9 раз. Значит провал специфичен
для правил, а не для механики или задачи.

**Три технических дефекта, из-за которых эксперимент физически не мог проверить свою
гипотезу** (`AMENDMENTS.md`): A-002 `create_linked_rings` никогда не создавала
зацеплений (все прогоны v1 от апреля 2026 информационно пусты) · A-003 срывы passage
различались между армами втрое и двигали метрику сильнее правила (после починки вердикт
v2 сменился INCONCLUSIVE → KILL) · A-001 метрика инвертирована в трёх местах.
Плюс ускорение >90 мин → 8.1 с, эквивалентность доказана 16 тестами.

**[VERIFIED] Ретроактивная поправка, применена к `decision_v3.md`:** базовая линия
согласия с оракулом — **0.368** (замерено на арме `random`), а не 0.5. v3 сообщал
«0.400 (0.5 = случайно)», из чего читалось «хуже случайного»; на деле слегка лучше.
Вердикты не меняются, но строка была бы унаследована третьим отчётом. Ошибка типа 3 по
`research-methodology.md` — результат верен при неозвученном условии, само условие не
проверялось.

**Следующий шаг и его блокировка:** по `KILL_CRITERIA.md` при T2 KILL → pivot на **D1
(spectral 3D)**. ⚠️ **Перед D1 обязателен scope-тест.** Близкий эстиманд закрыт дважды
независимо: ARCHCODE 2026-04-15 (RF на distance+category = 0.9921) и DNA-Ladder
2026-07-20 (holdout ΔAUC = −0.007). Без scope-теста D1 будет третьей проверкой того же.

**Kill switch НЕ сработал:** требует `T2 KILL AND D1 KILL`, а D1 никогда не запускался
(папки `d1_spectral_3d/` не существует). ATR-фреймворк не опровергнут.

## 🗂️ Session 2026-08-29: DNA-Ladder sibling audit + NotebookLM mining + 3-item verification
- **[VERIFIED, this session]** **DNA-Ladder audit** (`sergeeey/-DNA-Ladder-`, sibling project born
  2026-07-08, same day as ARCHCODE pause): cloned+audited via `gh`/`git`, 34/34 + 23/23 pytest pass
  (actually run), 0 secrets in git history (grepped), 2 minor hygiene issues found (Windows long-path
  checkout failure — reproduced; stale `C:\Users\sboi\` cross-machine path in CLAUDE.md — read
  directly). TE/Alu-3D track paused at wet-lab boundary — `GO_A1_READY_PACK_v1.md` read directly:
  ready but `date_signed: null` (machine-enforced NO-GO), B0 reporter-path recommended first,
  RADIL_mm3 off-target still open. SE/LLPS track fully closed (7 convergent REJECTs on
  missing-heritability-via-SE, read from `null_results/META_missing_heritability_2026-07-10.md`,
  positive control validated pipeline at Cliff's delta +0.609). Full audit content in prior turns;
  not re-summarized here.
- **NotebookLM access recovered** (auth had expired; `nlm login` re-auth via existing Chrome session
  worked without manual browser interaction — worth noting for future sessions).
- **Mined 5 DNA-related notebooks** (215+ sources: ДНК РЕСТРАКТ 2, ДНК 2026 рестракт, ДНК ARCHCODE
  3D-Генома, Продвижение проекта ДНК, GenomicsGPU) after user scoped down from "all 115 notebooks"
  via AskUserQuestion (most notebooks are unrelated to DNA — Брак, bedtime stories, Ray Dalio, etc).
  Large trove of ARCHCODE historical findings surfaced — mostly ALREADY KNOWN incidents (Sabaté
  phantom ref, mock AlphaGenome, circular AUC=0.977, MPRA hallucination) independently
  cross-confirmed, not new. Also surfaced a previously-unknown parked idea: **GenomicsGPU**
  (GPU-accelerated RNA-seq quantification tool, kallisto/salmon competitor) — planning-only,
  never started, no repo/folder exists anywhere.

[summarized] - **3-item verification round (user explicitly asked to re-check before trusting):**


## 🔍 Session 2026-07-05 (part 3): Harvest/Capture sweep
[summarized] - 2026-07-05: harvest scan (7 questions) + capture routing done. 2 reusable patterns captured →

  captured → `~/.claude/memory/_auto/patterns.md`: [REPEAT][HIGH] portable integrity-protocol
  (CLAUDE.md + integrity-checker, "вынести во все research-репо"); [REPEAT] self-correcting companion
  preprint (rs-9090074 → rs-10254695, honest: reputational payoff not yet measured). ALSO: the
  "skill run without checking its assumption" [AVOID] pattern RECURRED (harvest asked 7 Qs on a project
  Claude ran all session) → incremented to [×2] in patterns.md; at [×3] → fix the harvest skill itself.
- 2026-07-08 (DOI-live wrap-up + PAUSE): rs-10254695 LIVE (DOI 10.21203/rs.3.rs-10254695/v1, Prescreening
  passed ~2 days). Commits this session:
  · `f4c8ca6` (D:/ДНК `feature/readme-link-new-preprint`, pushed) — README callout DOI fix
  · `da9e072` (same branch, pushed) — CITATION.cff + README Preprint/Citation now cite rs-10254695
    (were citing a NEVER-published arXiv paper — stale). Done via `git worktree` (hook kept re-dirtying
    activeContext, blocking checkout).
  · `ac96ad2`, `635f51c` (~/.claude `fix/quality-v13`, LOCAL only — that repo has NO git remote) —
    harvest-capture `--auto` fix; [REPEAT] "disclose AI in every submission"; integrity/self-correction patterns
  · `705fb59` (D:/ДНК) — PAUSE record
  DECISIONS (final): NO v2, NO editorial note now — AI-disclosure DEFERRED to the NEXT paper (rule saved in
  patterns.md + Obsidian). Declarations text (Competing Interests + Funding + Use of AI) staged in manuscript
  source `category_confound_paper.md` §8, UNCOMMITTED. dotfiles `~/.claude` has NO remote → memory commits
  stay local (safe, by design — user confirmed).
  OPEN (user-side, optional, non-blocking): merge PR `feature/readme-link-new-preprint` → main (gh auth broken
  here) to make DOI callout + "Cite this repository" button live on the public repo. **PROJECT PAUSED.**


## 📦 Session 2026-07-05 (part 2): GitHub showcase audit — repo README/description/topics
[summarized] **What was done (after preprint submission, same session):**

  the working branch (63,153/13 loci on main vs 26,225/9 loci locally), no mention of rs-10254695, topics
  field is completely empty (`[]`).
- **Executed (approved, "option A" only):** added a one-line pointer in `main`'s README (right after the
  existing AUC-caveat callout) linking to rs-10254695 (status Prescreening) and to the
  `backup/snapshot-20260706` branch with the reproducible code. Done via proper workflow — repo has a
  branch-protection hook blocking direct commits to `main` (requires `feature/` prefix branch + PR).
  Commit `19aeb56` on branch `feature/readme-link-new-preprint`, pushed to origin.
- **🔴 PR NOT YET MERGED — user needs to do this manually:**
  https://github.com/sergeeey/ARCHCODE/pull/new/feature/readme-link-new-preprint
  (gh CLI auth is broken in this environment — 401 Bad credentials — cannot merge via API)
- **NOT done (parked, user only approved option A):** repo description update, 12 topics, and the fuller
  README merge (options B/C in the audit). Exact recommended description text + topics list are in
  `docs/GITHUB_SHOWCASE_AUDIT.md` sections 5-6 — ready to paste via GitHub web UI "About" gear icon
  whenever user wants, no session needed for that (2-minute manual task).
- Minor hygiene note: during branch-switching this session, ~49 unrelated tracked files showed as
  "modified" on `main` (residue from earlier orphan-branch operations) — did NOT touch/commit any of
  them, only ever staged README.md explicitly. Harmless but worth a `git checkout main -- .` cleanup
  in a future session if it recurs.

---


## ✅ Session 2026-07-05 (part 1): Preprint SUBMITTED — Research Square rs-10254695, status Prescreening
[summarized] **What happened:** User submitted the category-confound paper as a new, separate Research Square preprint.

  stale `main`). Re-verify this link before citing it anywhere else (e.g. cover letters, correspondence).
- Also caught and declined: a marketing-email link to **SCIRP (Scientific Research Publishing)** —
  confirmed via search this is a well-known predatory publisher (Cabells 2021, Norwegian Index rating 0).
  Do not let user submit there under any circumstance if this resurfaces.

**User signal (still valid — user is stepping away from ARCHCODE after this):** two years on one project,
low sense of payoff, moving attention to other projects (GeoScan mentioned once, then reverted back to
ARCHCODE same session — mild confusion/fatigue, resolved by asking directly). Do NOT push new ARCHCODE
hypotheses or re-open old discovery threads (pearls, ATPH, QEC-MWPM) unprompted in future sessions.

**🔴 NEXT (when user returns, in priority order):**
1. Check Research Square dashboard for rs-10254695 — did it pass Prescreening? Is DOI assigned?
2. Once DOI live: add an editorial note/comment on the OLD preprint rs-9090074 linking to the new DOI,
   framed as self-correction/companion (rs-9090074's own Limitations already flagged category-driven AUC —
   this is not a retraction, just don't skip this step or the two preprints look contradictory in isolation).
3. Optional, not urgent: journal submission (check current APC/fee before committing to any venue — do not
   quote remembered numbers, they drift).
4. If the user does NOT bring up ARCHCODE next session, do not raise it either — respect the wind-down.

---


## 📄 Session 2026-07-06 (historical — superseded by submission above): Paper flattened + off-site backup
[summarized] **What was done:**

  matched-control p=0.996". Decision: do NOT withdraw/kill it — new paper is a companion/self-correction,
  not a refutation of fabricated data. No fabrication ever occurred.
- `manuscript/category_confound_paper.md` is now the SOLE authoritative source (v2). Section scaffolding
  moved to `manuscript/_archive_category_confound_sections/` (deprecated, historical only).
- Off-site backup: `backup/snapshot-20260706` pushed to GitHub (orphan branch, no big-file history issue).
- Pre-submission checklist updated in paper.md: most items DONE (integrity, refs, skeptic, reviewer,
  robustness, backup). Remaining: post to Research Square (free, no affiliation gate — user's own login
  required), link old↔new preprints via editorial note, format to typst template.

**User signal (important, read before next session):** user explicitly said they will submit this preprint,
then STEP AWAY from ARCHCODE ("на этом успокоюсь... перейду на другой проект... два года мучаюсь, не
ощутил результата"). Two years on one project, low sense of payoff. Do NOT push new ARCHCODE hypotheses
or re-open old discovery threads (pearls, ATPH, QEC-MWPM) unprompted next session — respect the wind-down.
If they return, lead with "post the preprint" as the one remaining action, not new science.

**🔴 NEXT (when user returns):**
1. User posts to Research Square (their login, ~20 min) — I cannot do this step.
2. After posted: add editorial note on rs-9090074 linking to new DOI (self-correction, not error).
3. Optional: journal submission later (Bioinformatics non-OA track is free-to-author; check current fees
   before committing — do not quote remembered numbers).


## 🔬 Session 2026-06-28: Discovery Audit — 4 Converging Lines [VERIFIED]
[summarized] **What was done:**

**✅ RESOLVED (2026-07-04): AlphaGenome rescue-or-kill test → KILL**
- Existing promoter ISM scan re-analyzed as neg control: −43% was peak of contiguous 6bp element (5227097-5227102),
  2 non-pearls in it equally disruptive (−24 to −28%). Fisher OR=14.5 but MW p=0.31 (pearls bimodal).
- New distal test (real ClinVar SNVs): pearl 5226613 CAGE −0.04% vs 10 controls −0.45%, MW p=0.70. No signal.
- Results: `results/distal_pearl_cage_test.json`, scratchpad `distal_pearl_cage_test.py`

**✅ PIVOT EXECUTED (2026-07-04): negative-result paper DRAFTED + verified + skeptic-hardened.**
Category-confound methods paper, systematic across 9 loci. Files: `manuscript/category_confound_*.md`
(paper.md = assembled draft) + `results/fig_category_confound.png`/stats + `analysis/fig_category_confound.py`
+ `analysis/phylop_control.py`. Commits 3762f4c → d089b09 → e62af65.
- Core: ARCHCODE marginal 0.754→within 0.430 (LSSIM), 0.783→0.507 (SSIM); category-only 0.827; 7/8 loci collapse.
- TWO positive controls SURVIVE: CADD (supervised) 0.989→0.991, phyloP (unsupervised) 0.790→0.894.
- Verified: integrity-checker CLEAR, 10 refs confirmed, skeptic 3 attacks addressed (Simpson tested+rejected; Attack 2 closed by phyloP).

**Science + figure DONE (commit 69fb031):** Fig v2 shows 5 methods — both ARCHCODE metrics collapse,
CADD+phyloP survive. Paper draft complete, verified, skeptic-hardened, figure matches text.
**🔴 NEXT (production, not science):** (1) Decide relationship to LIVE preprint rs-9090074 (positive ARCHCODE
claim) — erratum/companion. (2) Venue (NAR GAB / Bioinformatics) + format to template + cover letter + 24h cooling-off.
(3) Optional: verify remaining DOIs resolve.
- Parked: ATPH, QEC-MWPM `[CANDIDATE]`. Old ARCHCODE discovery claim = FALSIFIED (block above).


## 🔧 Session 2026-06-25: Manuscript Fixed for Submission (commit 703e398)

**What was done:**
- paper-critic + integrity-checker ran pre-submission review → found 2 FATAL, 4 MAJOR issues
- FATAL 1 resolved: switched body from `body_content.typ` → `taxonomy_paper/body_content.typ`
- FATAL 2 resolved: fixed headline stats — d=−1.53→−2.1, fold 5.4→5.5, Bonferroni α=0.007/7→α=0.008/6
- Variant count standardized: 30,318→26,225 (6 occurrences in taxonomy body)
- Competitor comparison table added to Introduction (svMIL/POSTRE/Daly/AlphaGenome vs ARCHCODE)
- PDF compiled: manuscript/main.pdf (2.7 MB)

**Current state:** manuscript coherent — abstract (CAGE/Simpson's Paradox) matches body (taxonomy + CAGE validation)
**Next:** write cover letter → submit to Bioinformatics Advances

---












## 🗂️ Key Documents

**Manuscript:**
- `manuscript/manuscript_v2_full.md` (77K, May 18) — biology-first framing
- `manuscript/manuscript_v2_full.docx` (36 KB) — submission-ready

**Validation Reports:**
- `docs/CODE_AUDIT_HARDENING_2026-05-25.md` — P0 audit complete
- `docs/CONSILIENCE_ASSESSMENT_2026-05-18.md` — H2 AlphaGenome 6/10 score
- `docs/ADR-029_MLH1_mechanism_specificity.md` — cross-locus validation PASS
- `docs/ADR-030_TERT_sampling_bias_solved.md` — hotspots validated
- `docs/ADR-033_Forensic_Audit_Summary.md` — data integrity 5/5 PASS

**Published:**
- Research Square: rs-9090074 — LIVE, DOI: 10.21203/rs.3.rs-9090074/v1
- Zenodo: v2.17 DOI — https://zenodo.org/records/18908214

---


















## ⚠️ Critical Constraints (CORRECTED)

**DO NOT:**
- ❌ Max Imakaev follow-up — REFUSED May 20, path closed
- ❌ Ronin Discord check — affiliation already works on Research Square
- ❌ Wait for arXiv endorsement — <10% probability, paused
- ❌ Submit to Nature Genetics/AJHG — <5% acceptance with N=1 robust
- ❌ "7/7" claim anywhere — manuscript reframed (commit c3f62b3)
- ❌ Promise clinical predictor — README discloses "Discovery Engine, not Predictor"

**DO:**
- ✅ Push 7 unpushed commits (public state stale)
- ✅ Verify bioRxiv appeal sent (response expected May 28)
- ✅ Target Bioinformatics Advances (40-50% with HBB framing)
- ✅ Use Research Square DOI as primary citation
- ✅ Disclose limitations honestly (N=1 robust, garden of forking paths, Gelman & Loken)

---


















## 🧭 Success Criteria (CORRECTED)

**Today (25 min):**
- ✅ 7 commits pushed to GitHub
- ✅ bioRxiv appeal status confirmed (sent or just-sent)
- ✅ APC funding source identified

**This week (5-7h):**
- ✅ AlphaGenome training overlap verified (kills #1 reviewer attack)
- ✅ Outreach updated with HBB framing + RS DOI
- ✅ Bioinformatics Advances submission prep started
- ✅ bioRxiv appeal response received (May 28 expected)

**This month (Jun 25):**
- ✅ Bioinformatics Advances submitted with HBB pilot framing
- ✅ Research Square v2 updated with HBB reframe (if appeal rejected, this becomes primary)
- ✅ Decision: continue ARCHCODE polish OR pivot to next project (ChernoffPy / GeoScan)

---


















## 📖 Context for Next Session
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...

- Research Square LIVE since May 18 ✅
- bioRxiv rejected May 21 (3rd attempt) → appeal drafted
- Max Imakaev REFUSED May 20 (arXiv path closed)
- Bioinformatics Advances = next target

**Decision tree branches:**
- IF appeal accepted (May 28) → bioRxiv preprint with HBB reframe
- IF appeal rejected → Research Square stays primary, focus Bioinformatics Advances
- IF no APC funding → MDPI/PeerJ alternatives (fee waivers)

**Next immediate action:** `git push` (5 min) → verify appeal sent (5 min) → APC funding check (15 min)

**Blocker:** None external. All internal/operational.

**Critical question:** Was bioRxiv appeal email sent May 21, or only drafted?

---

**Last Session Duration:** ~6 hours (P0 audit cleanup + skeptic + reframe + power + trust repair + reality sync)  
**Next Session Goal:** Push + bioRxiv appeal verification + Bioinformatics Advances prep


## Auto-commit log
- [2026-08-30 19:06] `62b3251`: T2 v4/V2: KILL — local entanglement density carries no directional information
- [2026-08-30 01:22] `4be9e55`: prereg(T2 v4/V2): local entanglement density as local rule — frozen before implementation
- [2026-08-30 00:19] `7fa2393`: T2 v3/V1: KILL — curvature carries no directional information either
- [2026-08-30 00:16] `c168adf`: prereg(T2 v3/V1): curvature as local rule — frozen before implementation
- [2026-08-30 00:11] `6d683f1`: T2 v2: KILL after removing the failure-rate confound (A-003)
- [2026-08-29 23:49] `5630608`: T2 v2: INCONCLUSIVE — local angle rule carries no directional information
- [2026-08-29 23:44] `adbc66f`: prereg(T2 v2): freeze claim before any run
- [2026-08-29 21:30] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 21:26] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 21:25] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-08-29 20:51] `a5f8821`: docs(memory): session wrap — DNA-Ladder audit + NotebookLM mining + verification round
- [2026-07-08 15:15] `705fb59`: docs(memory): ARCHCODE paused — preprint live (DOI rs-10254695/v1), no further action
- [2026-07-08 15:10] `705fb59`: docs(memory): ARCHCODE paused — preprint live (DOI rs-10254695/v1), no further action
- [2026-07-08 14:53] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-08 14:39] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-05 13:40] `e934b0e`: docs(memory): record GitHub showcase audit + README PR pending merge
- [2026-07-05 13:40] `87b7807`: docs(github): add showcase audit — description/topics recommendations + branch drift finding
- [2026-07-05 13:00] `905c93b`: docs(memory): record Research Square submission — rs-10254695, Prescreening
- [2026-07-04 23:08] `6726953`: docs(paper): flatten to single authoritative source + archive scaffolding
- [2026-07-04 23:06] `efdad39`: fix(paper): full reviewer report response (7 major/minor) — data-tested first
- [2026-07-04 22:18] `8dc9834`: fix(paper): reviewer response — category-granularity robustness + narrowed claims
- [2026-07-04 22:07] `69fb031`: feat(figure): v2 money figure — 5 methods, two positive controls survive vs both ARCHCODE metrics collapse

[summarized] - [2026-07-04 21:59] `e62af65`: feat(paper): add unsupervised phyloP positive control — closes skeptic Attack 2
