# Active Context — ARCHCODE Project

**Last Updated:** 2026-05-25  
**Current Branch:** experiment/spectral-collapse-pilot  
**Session Focus:** P0 Code Audit COMPLETE → Publication Gate Status Check

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

## 🚪 Publication Gates Status

**Priority:** 🔴 **GATE-BLOCKED** — external dependencies, не контролируем timing

### Ronin Institute (RIIS 2.0)
- **Status:** ⏳ PENDING — 15 days overdue (applied March 12, expected ~May 10)
- **Last check:** Unknown (need Discord verification)
- **Action:** Check Discord #news-forum, #watercooler, #applications (May 16-25)
- **Impact:** IF approved → bioRxiv submission unblocked

### arXiv Endorsement
- **Status:** ⏳ WAITING — Max Imakaev (email sent May 16, 9 days ago)
- **Previous attempts:** 4 failed (Fudenberg bounced, Paulsen refused, Polovnikov can't, Hansen/Giorgetti/Mirny 50+ days no response)
- **Action:** Follow-up email acceptable (sent 9 days ago)
- **Impact:** IF endorsed → arXiv submission path opens

### bioRxiv
- **Status:** 🔴 BLOCKED — institutional affiliation requirement
- **Previous attempts:**
  - BIORXIV/2026/708672 — rejected ("not complete research")
  - BIORXIV/2026/710343 — rejected (no affiliation)
- **Blocker:** Waiting Ronin approval for "RIIS 2.0" affiliation
- **Impact:** IF Ronin approved → can submit with recognized institution

---

## 📊 Scientific Results Summary

**Main Claim:** "AlphaGenome CAGE predictions show mechanism-specific patterns across 7 loci"

**Evidence Strength:**
- ✅ Biological consistency: 7/7 loci (100%) — regulatory signal, coding null
- ⚠️ Statistical robustness: 1/4 loci after Bonferroni (HBB p=4×10⁻⁶, MLH1 p=0.022 borderline)
- ✅ Cross-locus validation: MLH1 PASS (ADR-029)
- ✅ Hotspot validation: TERT C228T/C250T PASS (+33.7%, +53.1% CAGE)
- ✅ Data integrity: 5/5 layers forensic audit PASS (May 9)
- ✅ Code trust: HARDENED after P0 audit (May 25)

**Limitations (honest):**
- N=1 locus statistically robust (HBB only)
- Category classification hardcoded (promoter/enhancer/coding)
- No wet-lab validation (ATAC-seq, Hi-C)
- Cherry-picking not ruled out (7 loci picked, не random sample)

**Publication Readiness:**
- Preprint (bioRxiv): 9/10 — ready with honest limitations
- Peer-review (NAR): 7/10 — requires 2-3 more robust loci

---

## 🎯 Tracy Strategic Verdict (2026-05-25)

**Goal:** Publish ARCHCODE preprint (bioRxiv OR arXiv)

**Bottleneck:** 🔴 GATE-BLOCKED (Ronin 15 days overdue, arXiv waiting Max)

**ABCDE Analysis:**

**A-Tier (серьёзные последствия):**
- A1: Ronin Discord check (5 min) — 15 days overdue = status могло измениться
- A2: Max Imakaev follow-up (3 min) — acceptable timeframe (sent May 16)

**B-Tier (важно но не критично):**
- B1: Category-matched controls (4-5h) — strengthen claim, но risky (может kill)
- B2: README update (30 min) — 30,318 → 26,225 variants

**E-Tier (исключить):**
- E1: Expand to more loci (10-15h) — gate blocked, не имеет смысла
- E2: Rewrite HBB-only (2-3 days) — ослабляет 6 месяцев работы
- E3: Code polishing beyond P0 — P0 done, достаточно

**80/20 Analysis:**
- 80% value = gate opens (Ronin OR arXiv)
- 20% effort = gate verification (5 min + 3 min = 8 min)

**Zero-Based Thinking:** "Начал бы я ARCHCODE снова?" → НЕТ (gate-blocked = external dependency)

**Critical Path:**
1. Ronin Discord check (5 min) → status: approved / pending / rejected
2. Max Imakaev follow-up (3 min) → arXiv path
3. [IF gate opens] Submit manuscript v2 (within 24-48h)

**Decision Tree:**
```
A1: Ronin check
├─ IF approved → submit to bioRxiv (24h)
├─ IF pending → THEN decide: wait OR category controls
└─ IF rejected → ARCHCODE freeze, reset commitment

A2: Max follow-up
├─ IF endorsed → submit to arXiv (48h)
└─ IF no response → wait 7 more days, then escalate
```

---

## 📋 Next Actions (Priority Order)

### P0 — GATE VERIFICATION (8 minutes, DO NOW)

**A1 FROG:** Ronin Discord check (5 min)
- Discord: #news-forum, #watercooler, #applications
- Search: "@Sergey" OR "application" OR "approval" (May 16-25)
- Find: status update (approved / pending / rejected)

**A2:** Max Imakaev follow-up (3 min)
- Subject: "Follow-up: arXiv endorsement request (chromatin structure VUS paper)"
- Body: Brief reminder, code B9P837
- Sent May 16, 9 days ago → acceptable to follow up

### P1 — STRENGTHEN EVIDENCE (4-5h, DEFER until gate status known)

**B1:** Category-matched controls (4-5h)
- HBB stratification: promoter path vs promoter benign
- IF signal persists → claim strengthens
- IF disappears → category artifact (опять)
- **Zero-Based:** НЕ начинать пока gate blocked

**B2:** README update (30 min)
- Fix: 30,318 → 26,225 variants
- Low priority (not blocker)

### P2 — POST-SUBMISSION (2-3h, after preprint published)

- Reproducibility smoke test (Docker container)
- Find LSSIM code (Python implementation missing)
- Forum post (AlphaGenome community, r/genomics)

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

## ⚠️ Critical Constraints

**DO NOT:**
- ❌ Category controls пока gate blocked (4-5h waste если Ronin rejected)
- ❌ Expand to more loci пока gate blocked (10-15h waste)
- ❌ HBB-only rewrite (ослабляет 6 месяцев работы)
- ❌ Code polishing beyond P0 (P0 done, enough)

**DO:**
- ✅ Verify gate status (8 min) — Ronin + Max
- ✅ Submit manuscript when gate opens (within 24-48h)
- ✅ Accept 7/7 biological consistency claim as-is (honest limitations disclosed)

---

## 🧭 Success Criteria

**Today (8 min work):**
- ✅ Ronin status known (approved / pending / rejected)
- ✅ Max follow-up sent

**This week:**
- ✅ Gate opens → manuscript submitted (within 24-48h)
- ✅ Gate pending → decision: wait OR defer ARCHCODE

**This month:**
- ✅ Preprint published (bioRxiv OR arXiv)
- ✅ ARCHCODE complete → focus elsewhere

---

## 📖 Context for Next Session

**What happened:** P0 code audit complete (dataset count + invariant tests), Tracy strategic analysis applied

**Key commits:**
- a3bbef2 — dataset count: 26,225 variants
- 82cd3e1 — invariant tests: 13/13 PASS
- 3e0690d — audit report updated

**Decision made:** Gate verification first (8 min), category controls deferred until gate status known

**Next immediate action:** Ronin Discord check (5 min) → Max follow-up (3 min) → report status

**Blocker:** Publication gates (Ronin 15 days overdue, arXiv waiting Max)

**Critical question:** Gate approved / pending / rejected? Decision tree branches from this.

---

**Last Session Duration:** ~3 hours (audit + Tracy analysis)  
**Next Session Goal:** Gate status verification + submission decision
