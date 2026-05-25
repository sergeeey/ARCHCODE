# Active Context — ARCHCODE Project

**Last Updated:** 2026-05-25 (synced with Obsidian vault — was 5 days stale)
**Current Branch:** experiment/spectral-collapse-pilot
**Session Focus:** Manuscript reframe COMPLETE → Bioinformatics Advances prep + bioRxiv appeal wait
**Reality source:** `Projects/ARCHCODE/Publication Status 2026-05-21.md` (Obsidian)

---

## 🎯 Session 2026-05-25: Code Audit Hardening Complete ✅

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

**Source of truth:** `Projects/ARCHCODE/Publication Status 2026-05-21.md` (Obsidian)

**Priority:** 🟡 **NOT gate-blocked** — Research Square LIVE, bioRxiv awaits appeal response, arXiv PAUSED

### Research Square ✅ PRIMARY PREPRINT
- **Status:** ✅ **LIVE** since 2026-05-18
- **DOI:** [10.21203/rs.3.rs-9090074/v1](https://doi.org/10.21203/rs.3.rs-9090074/v1)
- **Affiliation:** Ronin Institute for Independent Scholarship (works)
- **Action:** Already citable. Use as primary in outreach.

### Ronin Institute (RIIS 2.0)
- **Status:** ✅ Parent Ronin Institute affiliation WORKS (used on Research Square + ORCID)
- **RIIS 2.0:** New version may NOT be in bioRxiv database — separate issue from approval
- **Action:** NONE — affiliation is functional. Discord check obsolete.

### bioRxiv 🔴 REJECTED (3rd attempt)
- **Status:** ❌ REJECTED 2026-05-21 (BIORXIV/2026/726008)
- **Previous attempts:**
  - BIORXIV/2026/708672 — rejected ("not complete research")
  - BIORXIV/2026/710343 — rejected (no affiliation)
  - BIORXIV/2026/726008 — rejected (RIIS 2.0 not in database)
- **Appeal:** Draft exists `docs/bioRxiv_appeal_draft.md` — **STATUS UNKNOWN (sent?)**
- **Expected response:** ~2026-05-28 (if appeal sent May 21)
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

**Main Claim (post-skeptic):** "HBB pilot demonstrates AlphaGenome CAGE detects mechanism-specific regulatory disruption (p=4×10⁻⁶, Bonferroni-robust); 6-locus exploratory extension directionally consistent with regulatory-vs-coding dichotomy"

**Evidence Strength:**
- ✅ HBB pilot: p=4×10⁻⁶, Cohen's d=−1.53, Bonferroni-robust (α=0.007)
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

**Goal:** Move ARCHCODE from preprint (Research Square LIVE) to peer-reviewed publication (Bioinformatics Advances)

**Real Bottleneck:** 🟡 NOT external gates (Research Square works). Real bottleneck:
1. bioRxiv appeal pending (response ~May 28)
2. APC funding for Bioinformatics Advances ($1000-1500) — source unclear
3. Manuscript reframe today (commit c3f62b3) — ready to submit

**ABCDE Analysis (CORRECTED):**

**A-Tier (серьёзные последствия):**
- A1: Verify bioRxiv appeal sent (5 min) — if not sent, send today
- A2: Push 7 unpushed commits (5 min) — public state stale
- A3: APC funding verification (15 min) — blocker for Bioinformatics Advances

**B-Tier (важно но не критично):**
- B1: Update PRE_SUBMISSION_REVIEWER_DEFENSE.md to match HBB pilot reframe (1h)
- B2: AlphaGenome training overlap check (2h) — kill #1 reviewer attack
- B3: Update outreach materials with Research Square DOI (1h)

**C-Tier (defer to journal submission):**
- C1: Category-matched HBB controls (4-5h) — risky
- C2: FDR sensitivity table (1h)
- C3: Move router code to archived/ (2h)
- C4: Docker (4-6h) — journal-grade only

**E-Tier (исключить):**
- E1: Max Imakaev follow-up — REFUSED already (May 20)
- E2: Ronin Discord check — affiliation already works
- E3: arXiv path — PAUSED (<10% probability)
- E4: Expand to more loci pending gate — gate concept obsolete

**80/20 Analysis (REVISED):**
- 80% value = Bioinformatics Advances submission (with HBB pilot framing)
- 20% effort = (a) verify appeal sent, (b) push commits, (c) check APC funding

**Zero-Based Thinking:** "Начал бы я ARCHCODE снова?" → возможно ДА для methodology paper.
Research Square LIVE + HBB pilot reframe + 6 ADR-documented kills = real scientific contribution.

**Critical Path (CORRECTED):**
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

**Source:** User-provided audit report (TypeScript simulation engine)

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

### P0 — TODAY (25 min total)

**A1:** `git push` 7 unpushed commits (5 min)
- Today's reframe (c3f62b3), power analysis (d81e0cd), trust repair (40aeae5), ADR-035 (3aef138)
- Without push: reviewer sees old "7/7" framing on GitHub URL

**A2:** Verify bioRxiv appeal sent (5 min)
- Check sent emails: was `docs/bioRxiv_appeal_draft.md` actually sent May 21?
- Subject: "Re: BIORXIV/2026/726008 — Appeal regarding institutional affiliation"
- If NOT sent: send today (response expected May 28)

**A3:** APC funding for Bioinformatics Advances (15 min)
- Question: Ronin Institute provides APC funding? Personal? Need verify
- Budget: $1000-1500 (Bioinformatics Advances OA fee)
- Alternative venues if no funding: MDPI Biomedicines, PeerJ (fee waivers for independent)

### P1 — THIS WEEK (4-5h, DO if appeal accepted OR rejected)

**B1:** Update PRE_SUBMISSION_REVIEWER_DEFENSE.md (1h)
- Currently still 7/7 framing — needs HBB pilot update per ADR-036
- Reviewer-defense addresses Skeptic attack vectors

**B2:** AlphaGenome training overlap check (2h)
- Verify HBB variants NOT in AlphaGenome training data
- Kills attack vector #1 ("memorization, not generalization")
- Critical for Bioinformatics Advances reviewer trust

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

**What happened today (2026-05-25, ~6 hours of work):**

Sessions:
1. P0 code audit complete (commits a3bbef2, 82cd3e1, 3e0690d — pre-session)
2. External audit triage → ADR-035 (commit 3aef138)
3. Skeptic red-team → discovered "7/7" overclaim (70% rejection probability)
4. Manuscript reframe → HBB pilot + exploratory (commit c3f62b3) — restored internal consistency
5. MLH1 power analysis → N≥167 required (commit d81e0cd, closes ADR-036 OQ#1)
6. Trust repair triad → number provenance + canonical env + REPRODUCE.md (commit 40aeae5)
7. Obsidian reality check → discovered activeContext was 5 days stale

**Key insight:** ActiveContext.md (auto-memory) ≠ Obsidian vault reality. Always cross-check vault for external gate status before action.

**Reality from Obsidian (May 21):**
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
- [2026-05-25 19:03] `40aeae5`: docs(trust-repair): number provenance + canonical env + REPRODUCE.md
- [2026-05-25 18:40] `d81e0cd`: feat(power-analysis): MLH1 post-hoc sample-size calculation (closes ADR-036 OQ#1)
- [2026-05-25 18:35] `c3f62b3`: docs(manuscript): reframe 7/7 claim to HBB pilot + exploratory (ADR-036)
- [2026-05-25 16:42] `3aef138`: docs(audit): document external audit bug #1 as known limitation (ADR-035)
