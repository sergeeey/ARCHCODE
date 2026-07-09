# Active Context — ARCHCODE Project

**Last Updated:** 2026-07-08
**Current Branch:** experiment/spectral-collapse-pilot
**Session Focus:** ⏸️ **PROJECT PAUSED (2026-07-08).** Preprint LIVE — DOI 10.21203/rs.3.rs-10254695/v1. User's explicit final decision: NO v2, NO editorial note, nothing further on ARCHCODE. AI-disclosure rule is saved for the NEXT paper (patterns.md [REPEAT] + Obsidian knowledge/research/AI-disclosure-in-submissions.md) — apply it THEN, not retroactively here. Declarations text is already staged in the manuscript source if ever needed. Do NOT raise new ARCHCODE work unprompted.
**Reality source:** session 2026-07-08 (Research Square DOI email + user pause decision)

## 🔍 Session 2026-07-05 (part 3): Harvest/Capture sweep

- 2026-07-05: harvest scan (7 questions) + capture routing done. 2 reusable patterns captured →
  `~/.claude/memory/_auto/patterns.md` (stratified-eval-with-positive-control; docx-not-PDF for
  Research Square). 1 open research question → `~/.claude/memory/knowledge/projects/ARCHCODE/pearl_registry/INDEX.md`
  (TP53 sole surviving within-category signal, next_check 2026-08-01). AlphaGenome wrapper + GitHub
  showcase methodology assessed but did NOT pass Zero-Signal Gate (code reuse / successful tool use,
  not new falsifiable claims) — intentionally not captured, not an oversight.
- 2026-07-06: harvest-capture re-run (user asked "may we find something else"). 2 NEW process assets
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










## 🎯 Session 2026-05-25: Code Audit Hardening Complete ✅
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...
**Status:** 🟢 **P0 BLOCKERS RESOLVED** — All CRITICAL issues fixed

**Audit Results:**
- Layer 5 (Invariants): ✅ COMPLETE — 13/13 tests PASS (commit 82cd3e1)
- Layer 7 (Provenance): ✅ RESOLVED — 26,225 variants verified (commit a3bbef2)
- Overall verdict: 🟢 HARDENED (P0 complete, P1 optional)

**Commits (May 25):**
1. `a3bbef2` — fix(data): dataset count verification — 26,225 variants (manuscript updated)
2. `82cd3e1` — test(alphagenome): add Layer 5 invariant auto-tests (13/13 PASS)
3. `3e0690d` — docs(audit): Layer 5 complete, P0 blockers resolved

**Key Findings:**
- CFTR: NaN values correctly handled as documented interval mismatch (not silent corruption)
- HBB stored as "HBB_reference" in AlphaGenome results
- Dataset count: 26,225 core 9 loci (manuscript corrected from 25,850)

**Audit Document:** `docs/CODE_AUDIT_HARDENING_2026-05-25.md` (666 lines)

---

## 🚪 Publication Gates Status (CORRECTED 2026-05-25 from Obsidian)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...
- **Action P0:** Verify appeal sent. If not — send today.

### arXiv ⏸️ PAUSED (Max REFUSED May 20)
- **Status:** ⏸️ **PAUSED** — 4/4 direct attempts failed
- **Endorser timeline:**
  - Fudenberg (USC): bounced Apr 1
  - Paulsen (Oslo): refused Apr 15
  - Polovnikov (Skoltech): no q-bio track record
  - **Max Imakaev (MIT):** Willing May 17 → **REFUSED May 20** ("insufficient arxiv submissions")
  - Hansen, Giorgetti, Mirny (MIT): ghosted 50+ days
- **Probability of success:** <10% per Obsidian assessment
- **Action:** NO follow-up. Path effectively closed for now.

### Bioinformatics Advances 📋 NEXT TARGET
- **Status:** Planned, 2-4 weeks
- **Type:** Methods note (H1 negative result + validation suite)
- **APC:** ~$1000-1500 — **funding source UNKNOWN** (Ronin? Personal? Need verify)
- **Acceptance probability:** 40-50% with HBB pilot reframe (skeptic estimate)

---

## 📊 Scientific Results Summary (REFRAMED 2026-05-25, ADR-036)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...
- ⚠️ Exploratory 6-locus extension: directional only (1/4 regulatory significant)
- ⚠️ MLH1: p=0.022 nominal, fails Bonferroni
- ⚠️ TERT hotspots (+33-53% CAGE): descriptive, no variant-matched controls
- ✅ Coding null (TP53, BRCA1, CFTR, GJB2; p>0.40): consistent with prediction
- ✅ Data integrity: 5/5 layers forensic audit PASS (May 9)
- ✅ Code trust: HARDENED after P0 audit (May 25)

**Honest Limitations (now in abstract):**
- N=1 locus statistically robust (HBB pilot only)
- Loci selection POST pilot → garden of forking paths concern (Gelman & Loken, 2013)
- No wet-lab validation (ATAC-seq, Hi-C)
- Category classification hardcoded

**Publication Readiness (REVISED after reframe):**
- Research Square: ✅ LIVE (DOI: 10.21203/rs.3.rs-9090074/v1)
- Bioinformatics Advances target: 40-50% acceptance (was 25% with 7/7 framing)
- Nature Genetics / AJHG: <5% (don't target — under-powered)
- Skeptic verdict: reframe addresses 70% rejection risk → 40-50% acceptance probability

---

## 🎯 Tracy Strategic Verdict (CORRECTED 2026-05-25)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...
1. `git push` 7 commits (5 min) — make today's work public
2. Verify bioRxiv appeal sent (5 min) — check email sent folder
3. APC funding source check (15 min) — Ronin? Personal? Find out
4. [IF appeal accepted by May 28] Submit to bioRxiv with HBB framing
5. [PARALLEL] Plan Bioinformatics Advances submission (2-4 weeks)

**Decision Tree (CORRECTED):**
```
bioRxiv appeal (response by ~May 28)
├─ ACCEPTED → submit BIORXIV/2026/726008 v2 with HBB framing (1-2 days)
├─ REJECTED → Research Square stays primary, focus journal submission
└─ NO RESPONSE by Jun 5 → follow-up appeal email

Bioinformatics Advances (next 2-4 weeks)
├─ IF APC funded → submit methods note with HBB pilot + validation suite
├─ IF NOT funded → look at MDPI / PeerJ / PLOS ONE (lower APC or fee waivers)
└─ ELSE → Research Square stays as final venue
```

---

## 🔍 External Code Audit (2026-05-25, post-session)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...

**Findings:** 3 critical + 3 medium + 2 low bugs in `LoopExtrusionEngine.ts`,
`MultiCohesinEngine.ts`, `contactMatrix.ts`, `correlate_hic_archcode.py`,
`generate-unified-atlas.ts`, `random.ts`, `biophysics.ts`.

**Materiality verdict:** ❌ NOT material for active AlphaGenome 7/7 claim.
All bugs in router code path (killed April 2026, commit f6016ed).

**Bug #1 (CTCF retroactive detection):** Minimal fix broke 4 regression tests.
Proper fix requires state-based stalled semantics (4-6h invasive in dead code).
DECISION: DEFER. Documented as known limitation in code comments + ADR-035.

**Bugs #2-8:** Same materiality verdict. Documented but not fixed.

**Tracy verdict:** abandon audit fixes → focus on publication gates
(Ronin Discord check + Max Imakaev follow-up = 8 min).

**Commit:** 3aef138 — docs(audit): document external audit bug #1 (ADR-035)

---

## 📋 Next Actions (Priority Order — CORRECTED 2026-05-25)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [su...
**B3:** Outreach update with HBB framing + RS DOI (1h)
- Nora UCSF follow-up (May 29 deadline)
- AlphaGenome forum post
- LinkedIn announcement

**B4:** Bioinformatics Advances submission prep (2-3h)
- Match Author Guidelines
- Cover letter (HBB pilot framing)
- Supplement: ADR-035 (CTCF bug), ADR-036 (reframe), power analysis

### P2 — POST-PREPRINT (deferred until submitted)

- Category-matched HBB controls (4-5h) — strengthen for journal
- FDR sensitivity table (1h)
- Move router code to `archived/` (2h)
- Docker for journal submission (4-6h)
- Reproducibility smoke test on clean machine
- ChernoffPy paper (#2 in pipeline)

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
- [2026-07-04 21:59] `e62af65`: feat(paper): add unsupervised phyloP positive control — closes skeptic Attack 2
- [2026-07-04 21:50] `d089b09`: fix(paper): skeptic-pass revisions — add SSIM metric, reject Simpson's paradox, strengthen CADD caveat
- [2026-07-04 21:33] `3762f4c`: feat(paper): category-confound negative-result paper — figure, abstract, related work, methods
- [2026-07-04 00:32] `8a8a603`: chore(memory): sync session state — gnomAD NULL + phyloP confound + AlphaGenome neg-control next-action
- [2026-07-02 19:31] `c168a4c`: chore(session): commit 2026-06-28 discovery audit results
- [2026-06-25 22:39] `c852232`: docs(manuscript): add cover letter + references + competitor table (main body)
- [2026-06-25 22:26] `703e398`: fix(manuscript): resolve abstract/body mismatch + correct headline statistics
- [2026-05-30 20:49] `25d1406`: chore: archive May audit docs + update activeContext/results
- [2026-05-25 19:50] `2dde83c`: docs(memory): sync activeContext with Obsidian vault reality (5 days stale)
- [2026-05-25 19:03] `40aeae5`: docs(trust-repair): number provenance + canonical env + REPRODUCE.md
- [2026-05-25 18:40] `d81e0cd`: feat(power-analysis): MLH1 post-hoc sample-size calculation (closes ADR-036 OQ#1)
- [2026-05-25 18:35] `c3f62b3`: docs(manuscript): reframe 7/7 claim to HBB pilot + exploratory (ADR-036)
- [2026-05-25 16:42] `3aef138`: docs(audit): document external audit bug #1 as known limitation (ADR-035)
