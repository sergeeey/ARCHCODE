---
tags:
  - archcode
  - session
  - paper3
  - decision
  - 2026-05
created: '2026-05-07'
status: complete
type: session-log
project: ARCHCODE
---
# Сессия 2026-05-07 — Paper 3 Option A

## Summary

Session продолжена после context compaction. Завершены критические задачи May 7:
- ✅ Spectral validation commit verified (already done May 6)
- ✅ Paper 3 strategic decision — Option A selected
- 🔴 Paper 2 resubmit — URGENT (3 days overdue)

## Paper 3 Decision: Option A (HBB-only)

**Выбрано:** Option A — HBB-only, mechanism-specific framing  
**Дата решения:** 2026-05-07  
**Commit:** 40c5cbd

### Опции рассмотрены

| Option | Description | Timeline | Verdict |
|--------|-------------|----------|---------|
| **A** | HBB-only (accept mechanism-specific limitation) | 1 week | ✅ SELECTED |
| B | Continue multi-locus search | 4 weeks, uncertain | ❌ REJECTED |
| C | Mechanistic pivot (LSSIM as regulatory marker) | 2 weeks | ❌ NOT NEEDED |

### Rationale

1. **Sunk cost avoidance**
   - 31 commits spent on multi-locus search without second regulatory locus
   - BCL11A pilot: position controls returned same "not observed" result (no LSSIM separation)
   - CFTR: opposite direction (common variants in low-LSSIM, not constraint)
   - P(success | 31 failed attempts) ≈ 0.1 (low)

2. **Paper 2 urgency**
   - Already 3 days overdue for resubmit (May 4 deadline passed)
   - Further delay = risk to submission
   - Fast iteration: submit → peer review → feedback → THEN decide Paper 3 expansion

3. **Scientific honesty**
   - N=1 locus with clear mechanism-specific framing > overclaim multi-locus without evidence
   - Paper 2 already correctly framed as regulatory-specific (HBB promoter region)
   - AUTONOMOUS_STATUS_20260503.md (line 159): "A second true positive regulatory locus has not yet been found"

4. **Evidence-based decision**
   - [VERIFIED-Read] PAPER3_AUTONOMOUS_STATUS: BCL11A source audit → 7/11 coding, 3/11 splice, 1/11 nonsense (not clean regulatory)
   - [VERIFIED-Read] Position-matched controls: 6/6 also "not observed" (no discrimination)
   - [VERIFIED-Read] HBA1/GATA1: not ready for SNV queries (Ref/Alt fields = `.`/`.`)

### Option B — Why Rejected

- 4 weeks additional investment vs 31 commits already spent
- Uncertain outcome: no guarantee of finding clean regulatory locus
- Delay compounds Paper 2 overdue status
- Bayesian update: P(success) dropped from 0.5 (prior) to ~0.1 (posterior after 31 attempts)

### Option C — Why Not Needed

- Paper 2 already has correct mechanistic framing ("regulatory variant disruption in HBB promoter")
- No pivot required — framing is mechanism-specific by design
- MECHANISM_STRATIFIED_FALSIFICATION_PLAN already written (May 3)

## Spectral Validation Status

**Status:** ✅ COMMITTED (May 6)

- CSV files: commit d051f93 (May 6, 15:15)
  - `results/sfi_brca1_all.csv` — 2.0MB, 10,493 variants
  - `results/sfi_tp53_all.csv` — 524KB, 2,795 variants
  
- PDF figures: commit 4c362fa (earlier)
  - `results/figures/spectral_S2_phase_boundary.pdf` — 30KB
  - `results/figures/spectral_S3_codeword_distance.pdf` — 32KB
  - `results/figures/spectral_S4_lssim_distributions.pdf` — 35KB

**Root cause (thermal overload May 6):**
- 82GB JSON contact matrices generated during spectral validation
- Inefficient storage: 3.4MB per 50×50 matrix (JSON) vs 50KB (.npy)
- 68× compression ratio wasted
- Final results extracted to CSV, 82GB deleted

## Paper 2 Status

**MS#3433287 — Human Mutation**

### Timeline
- May 2, 18:00: Submitted
- May 4, 06:23: RETURNED TO DRAFT
- May 6: Affiliation fixed, new DOCX created
- May 7: **AWAITING RESUBMIT** (3 days overdue)

### Return Reason
"Further information required regarding identity of institutions"

### Root Cause
DOCX contained "(affiliation pending confirmation, decision expected May 2026)"

### Resolution (May 6)
1. Verified Ronin approval: April 21, 2026 (not May 10 expected)
2. Fixed affiliation: "Ronin Institute for Independent Scholarship 2.0"
3. Changed email: sergeikuch80@gmail.com → sergey.boyko@ronininstitute.org
4. Created new file: `pypop_paper_HumanMutation_SUBMIT_FINAL.docx`

### Action Required
**URGENT:** Resubmit MS#3433287 via ScholarOne portal
- Portal: https://mc.manuscriptcentral.com/humu
- Navigate: Author Center → Manuscripts Requiring Revision → MS#3433287
- Upload: `pypop_paper_HumanMutation_SUBMIT_FINAL.docx`
- Add response to editor explaining affiliation correction

## Commits Today

1. **40c5cbd** — Paper 3 decision (Option A)
   - `goals.md`: Option A selected with rationale
   - `activeContext.md`: P1 Paper 3 decision marked ✅

2. **6391a11** (earlier) — May 7 activeContext update
   - Paper 2 timeline documented
   - Next Actions updated with emoji priorities

## Next Actions

| Priority | Task | Status |
|----------|------|--------|
| 🔴 P0 | Resubmit Paper 2 — MS#3433287 | URGENT, 3 days overdue |
| 🟢 P2 | ClinGen data correction email | Optional |
| 🟢 P2 | Sync sectional .md files with correct data | Optional |

## Связи

- [[ARCHCODE — актуальный контекст 2026-05-05]]
- [[Карточка — ARCHCODE]]
- [[План закрытия ARCHCODE]]
- [[10 уроков ARCHCODE — MOC]]

up:: [[Каталог всех проектов 2026]]
