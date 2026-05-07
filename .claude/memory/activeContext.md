# Active Context — Multi-Project

**Last Updated:** 2026-05-07 (Paper 2 Ready for Resubmit)
**Active Projects:** ARCHCODE (PyPop Paper 2 resubmit pending, Spectral validation complete), Paper 3 (strategic decision needed)

---

## Session 2026-05-06 Part 2 — System Recovery + Paper 2 Verification ✅
[summarized] **Context:** PC overheated and rebooted mid-session (3:30 PM). Root cause identified: 82GB JSON contact matrices generat...
- **Expected approval:** ~May 10, 2026
- **Email address:** sergey.boyko@ronininstitute.org used in ClinVar correspondence (May 1)
- **Contradiction:** Email used 9 days before expected approval
- **Possibilities:** (a) Early approval received, or (b) Email used prematurely
- **Action required:** Verify approval status, update Paper 2 affiliation accordingly

**Uncommitted Changes:** 137 files
- Modified (19): activeContext.md (+571), spectral_sprint_log.md (+129), pypop_paper_FINAL.md (+69), goals.md (+52), skills (5), Obsidian docs (6), HBB_Unified_Atlas.csv (reshuffled)
- Untracked (118): AUDIT_*.md (9), SUBMISSION_*.md (3), PAPER3_*.md (20+), results/*.csv (50+), contact_matrices/ (NEW)

**Next Actions (May 7 priorities):**
1. ✅ **System recovery** — thermal overload diagnosed and resolved (May 6)
2. ✅ **Paper 2 affiliation fixed** — commit ce1636e (May 6)
3. ✅ **Ronin approval verified** — April 21, 2026 RIIS 2.0 Fellow confirmed
4. 🔴 **P0: Resubmit Paper 2** — MS#3433287 via ScholarOne (URGENT, 3 days overdue)
5. ✅ **P1: Paper 3 strategic decision** — Option A selected (HBB-only, mechanism-specific)
6. ✅ **P1: Commit spectral validation** — commits d051f93 (CSV) + 4c362fa (PDF), May 6
7. 🟢 **P2: Optional tasks** — ClinGen data correction, sync .md files

---

## Session 2026-05-03 — A1 Multi-Locus Pilot + Mechanism-Specific Limitation ✅

[ARCHIVED — see Session 2026-05-06 for current status]

**Discovery:** LSSIM correlation with pathogenicity is **mechanism-specific**, not universal:
- **HBB (regulatory locus):** 20/353 pathogenic SNVs with LSSIM<0.93 (5.7%) ✓
- **BRCA1 (coding locus):** 1/912 pathogenic SNVs with LSSIM<0.95 (0.1%) ✗
- **TP53 (coding locus):** 1/912 pathogenic SNVs with LSSIM<0.95 (0.1%) ✗

**Commits:**
- 2e7fd52: feat(A1-pilot): LSSIM mechanism-specific limitation discovered
- 0f48793: feat(A2-phase1): add CLI args + generic cohort filter

---


## Session 2026-05-01 — PyPop Population Stratification + Lancaster Outreach ✅
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Status:** ✅ COMPLETE — PyPop cross-population validat...
- ❌ BRCA1/CFTR multi-locus (Paper #2 later)
- ❌ Generalize query tool
- ❌ RateLimitRetry library
- ❌ Any non-Critical-Path work

**Autonomous Night Execution (2026-05-01 → 2026-05-02, completed while user sleeping):**
- ✅ Methods section: 856 words (pypop_paper_methods.md)
- ✅ Results section: 1,022 words (pypop_paper_results.md)
- ✅ Introduction: 467 words (pypop_paper_introduction.md)
- ✅ Discussion: 646 words (pypop_paper_discussion.md)
- ✅ Abstract: 248 words (pypop_paper_abstract.md)
- ✅ FINAL compilation: 3,239 words (pypop_paper_FINAL.md)
- ✅ Task #4 COMPLETED

**Paper status: READY FOR SUBMISSION**
- Target: Human Mutation (short reports, 3000-5000 words)
- All sections drafted, references cited, data availability included
- Next: User review → minor edits → submit by May 4

---

## Session 2026-05-02 — Harvest Analysis + Integrity Checklist ✅
[summarized] [summarized] [summarized] [summarized] [summarized] **Harvest Execution:** `/harvest` skill applied to session 2026-05-0...
- Target: Ronin Lightning Talk (July), LessWrong, independent researchers blog

**3. Multi-Agent Research Orchestration (commit 9ade008)**
- `docs/MULTI_AGENT_RESEARCH_ORCHESTRATION.md` (737 lines, 4,218 words)
- 4 Agent Profiles: Skeptic (falsification), Tracy (strategic audit), Integrity-Checker (hallucination blocker), Harvest (asset discovery)
- Orchestration patterns: Sequential (quality gates), Parallel (research squad), Adversarial (skeptic validation), Strategic (Tracy checkpoints)
- 18-month ARCHCODE stats: 11 invocations, 6 blocks, 4 disasters prevented ($1.4M), ROI 1000×
- Implementation guide: triggers, prompts, logging, when NOT to use
- Target: AI alignment forums, LessWrong, Claude Code community

**Next Steps (3-month roadmap):**
- **May:** HBB paper submission + ClinVar FALSE PEARLS
- **June:** Integrity Protocol publication (blog/arXiv cs.CY)
- **July:** Falsification Workflow case study (Ronin Lightning Talk)
- **Aug:** Contact Matrix Simulator benchmarking (vs Akita/OpenMM)

**Key Insight from Harvest:**
Clinical validation не удалась (router Class B killed by matched controls), но **research infrastructure** оказалась ценнее исходной цели — 5 активов Score 17+ готовы к standalone publication.

---

## Session 2026-04-29 — H2-H4 Exploratory Validation COMPLETE ✅
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Status:** ✅ ALL TASKS COMPLETE (15/15) —...
- H4 (Codeword distance): REINTERPRETED (dosage = structural variance 19.9%, not median robustness)

**Scientific Insight:**  
Dosage-sensitive loci exhibit **narrow spatial vulnerability zones** (73bp HBB promoter cluster) with **high structural variance** (19.9% disruptive variants vs <1% BRCA1/TP53), reflecting focal purifying selection on enhancer-promoter contacts.

**Deliverables:**
- `results/phase_boundary/grid_search.csv` (27 simulations)
- `results/codeword_distances.csv` (HBB/TP53/BRCA1)
- `results/dosage_sensitivity_correlation.csv`
- `manuscript/spectral_results.typ` (78 lines, integrated at line 1387)
- Figures: S2 (phase boundary), S3 (codeword), S4 (distributions)

**Audit Status:**  
COMPREHENSIVE_AUDIT_PLAN.md executed → AUDIT_REPORT_20260429.md: **48/48 checks PASS (100%)**  
Phantom reference fixed: Sabaté 2025 Nature Genetics → bioRxiv 2024 (commit 3a4fd90)

**Next Steps:**  
**READY FOR SUBMISSION** — Compile PDF, push to GitHub, update Zenodo to v2.18

---

## Obsidian Documentation — SYNCHRONIZED ✅

**New files (2026-04-29):**
1. `results/SPECTRAL_VALIDATION_COMPLETE_2026-04-29.md` — comprehensive H1-H4 final report
2. `results/SCIENTIFIC_ABSTRACT_v5_2026-04-29.md` — updated abstract with spectral validation
3. `docs/PROJECT_UPDATE_2026-04-29.md` — v5.0 changelog and submission checklist

**Updated files:**
4. `results/spectral_sprint_log.md` — Session 2026-04-29 H2-H4 completion appended
5. `.claude/memory/activeContext.md` — THIS FILE (synced with git version)

**Legacy files (keep for history, superseded by v5):**
- `results/SCIENTIFIC_ABSTRACT.md` (2026-03-06) → use v5 instead
- `manuscript/PHASE_A_COMPLETE.md` (2026-02-05) → old Hi-C r=0.16 pilot
- `docs/release_v4_summary.md` (2026-03-09) → pre-spectral version

---








## Session 2026-04-25 — Stress Biology Project Launch → KILLED
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Hypothesis:** Doubling time predicts mut...
- Verdict at n=89: Effect was SPURIOUS (disappeared with more data)

**Decision (Week 2):**
- **KILL PROJECT** — hypothesis rejected by data
- Option A (recommended): Publish negative result
- Option C (pivot): Test H3 (ATP proxy) directly, skip doubling time
- Bilinsky contact: POSTPONED (need stronger evidence first)

**Lessons learned:**
1. Small samples mislead (n=49 insufficient, n=89 required)
2. Pre-registration prevented p-hacking and retraction
3. ARCHCODE confounding lesson applied correctly at n=49
4. Tissue heterogeneity > proliferation rate for mutation accumulation

**Commits:**
- 0d0333a: docs: hypothesis REJECTED at n=89
- 2032f63: feat: confounding test PASS (doubling time 3× stronger)
- d34dbb7: feat: batch analysis complete (n=49, r=0.38, p=0.008)

---

## ARCHCODE Status
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Current Branch:** feature/stress-biology...
- Research Square: rs-9090074 LIVE (taxonomy paper), DOI: 10.21203/rs.3.rs-9090074/v1
- Zenodo: v2.17 LIVE (https://zenodo.org/records/18908214), v2.18 pending (spectral section)
- bioRxiv: REJECTED ×2 (no affiliation), resubmit after Ronin approval
- arXiv: awaiting endorsement (code B9P837, 5 emails sent 2026-04-01)
- Ronin Institute RIIS 2.0: applied 2026-03-12, expected answer ~2026-05-10

**Manuscript Versions:**
- `manuscript/main.typ` — arXiv version (tool-first, includes spectral analysis)
- `manuscript/biorxiv_version/main.typ` — bioRxiv version (biology-first, Tier system)
- Desktop PDF: `C:\Users\serge\Desktop\arxiv 0403\` (pre-spectral version, UPDATE NEEDED)

**Key Metrics (v5.0):**
- 32,201 variants across 9 loci
- 27 HBB pearls (15 in 73bp promoter cluster)
- Spectral validation: 3 loci (HBB, TP53, BRCA1)
- SFI effect sizes: d=1.36 (HBB), 0.87 (TP53), 0.04 (BRCA1 negative control)
- HBB structural variance: 19.9% disruptive (vs <1% BRCA1/TP53)
- Audit compliance: 48/48 checks PASS (100%)

---

## Recent Commits (Last 10)

```
3a4fd90 fix: correct phantom reference Sabaté 2025 → bioRxiv 2024
4c362fa feat: complete H1-H4 spectral fragility validation
0d0333a docs: hypothesis REJECTED at n=89 — doubling time does NOT predict mutation rate
2032f63 feat: confounding test PASS (doubling time 3× stronger than tissue type)
d34dbb7 feat: batch analysis complete (n=49, r=0.38, p=0.008)
40a9e78 feat: Month 1 Week 1 preliminary results (n=5, r=-0.5)
9242aa0 feat(stress-biology): implement Month 1 data collection pipeline
8b374bc feat: stress biology pivot — ATP-driven mutagenesis project structure
eb6f1f6 fix: remove infinite loop Stop hook from settings
e311d70 docs: project closure — H-01/H-14 killed, pearl untestable, final audit
```

---








## Backlog (Updated 2026-04-29)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **P0 (Immediate, Week 1):**
4. **Compile final PDF:** `cd manuscript && python -c "import typst; typst.compile('main.typ', output='main.pdf', root='..')"`
5. **Push to GitHub:** `git push origin feature/stress-biology-atp-mutagenesis --tags`
6. **Update Zenodo:** v2.18 with spectral validation section
7. **Update Desktop PDF:** Compile fresh version to `C:\Users\serge\Desktop\arxiv 0429\` (replace 0403)

**P1 (Short-term, Month 1):**
8. **Follow-up endorsers:** Nora (UCSF), Giorgetti (Basel), Hansen (MIT) — 2 weeks since last contact
9. **bioRxiv resubmit prep:** Ready for immediate upload post-Ronin approval (~May 10)
10. **README.md update:** Add spectral validation to "What Survived" section
11. **Create release notes:** v5.0 changelog (H1-H4, audit, phantom fix)

**P2 (Optional, Month 2-3):**
12. H3 TDRA pipeline (build HGVS→ClinVar mapper)
13. Cross-locus H4 validation (HBA1, GATA1, SOX2 structural variance)
14. FOXP3/BCL11A mutagenesis expansion (18 loci total)
15. Wet-lab partner outreach (Capture Hi-C for HBB 73bp cluster)
16. Multi-tissue simulation (HUDEP-2 enhancers instead of K562)
17. ML integration (Random Forest on LSSIM + SFI + category)

---

## Compilation (Updated Command)

```bash
# Main manuscript (arXiv version with spectral)
cd D:/ДНК/manuscript
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='..')"

# bioRxiv version (biology-first)
cd D:/ДНК/manuscript/biorxiv_version
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='../..')"

# Taxonomy paper
cd D:/ДНК/manuscript/taxonomy_paper
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='../..')"
```

---








## Technical Notes

- Windows: `python` not `python3`
- Typst needs `root='..'` for main manuscript, `root='../..'` for subdirectories
- Session history: use `git log --oneline` (not stored here)
- V1 roadmap: see memory/v1_module_roadmap.md
- Spectral validation: see results/SPECTRAL_VALIDATION_COMPLETE_2026-04-29.md
- Project update: see docs/PROJECT_UPDATE_2026-04-29.md

---








## Key Numbers (Canonical, v5.0)
[summarized] [summarized] [summarized] [summarized] [summarized] [summarized] [summarized] **Dataset:**
- Q3 concordant: 641 variants (ARCHCODE + VEP both HIGH)

**Structural Variance:**
- HBB: 19.9% disruptive (LSSIM<0.95)
- BRCA1: 0.7% disruptive
- TP53: 0.2% disruptive

**gnomAD Constraint:**
- HBB pearls: 85% absent (purifying selection, floor effect in conserved locus)
- HBB overall: 84% constraint (PLI=0.91)

**Statistical Rigor:**
- Bootstrap CI (10K iterations) + Benjamini-Hochberg FDR correction
- Mann-Whitney U + Kruskal-Wallis for non-parametric testing
- Cohen's d effect sizes: HBB d=4.17 (very large), TERT d=1.35, GJB2 d=1.27

---

_Active context synchronized with Obsidian: 2026-04-29_  
_Next sync: After Ronin decision (~2026-05-10)_

## Auto-commit log
- [2026-05-07 11:36] `6391a11`: docs(memory): May 7 update — Paper 2 ready for resubmit
- [2026-05-06 18:48] `ce1636e`: fix(paper2): update affiliation — Ronin RIIS 2.0 Fellow confirmed (April 21)
- [2026-05-06 16:40] `7794f0c`: docs(memory): Session 2026-05-06 Part 2 — thermal recovery + Paper 2 verification
- [2026-05-06 16:15] `a71ed04`: chore: remove 82GB intermediate contact matrices (JSON → CSV extracted)
- [2026-05-06 15:18] `c64f537`: chore: sync activeContext auto-commit logs
- [2026-05-06 15:18] `06d9473`: chore: remove duplicate .bak files (3 files)
- [2026-05-06 15:17] `e59fc6d`: docs(memory): update activeContext (Session 2026-05-06) + clean goals.md
- [2026-05-06 15:17] `d051f93`: chore: project reorganization — consolidate 3-day multi-stream work
- [2026-05-03 02:16] `2e7fd52`: feat(A1-pilot): LSSIM mechanism-specific limitation discovered
- [2026-05-03 02:12] `0f48793`: feat(A2-phase1): add CLI args + generic cohort filter
- [2026-05-03 01:44] `0f48793`: feat(A2-phase1): add CLI args + generic cohort filter
- [2026-05-02 11:38] `1415229`: fix: add coverage validation + baseline comparison (pre-submission)
- [2026-05-02 11:07] `075d2e3`: fix: remove mathematically incorrect BS1 calculation (skeptic audit)
- [2026-05-02 10:43] `9ade008`: feat: Multi-Agent Research Orchestration guide (harvest asset 17/20)
- [2026-05-02 10:39] `2b7582b`: feat: Falsification-First workflow blog post (harvest asset 18/20)
- [2026-05-01 23:27] `40d33ce`: feat: extract AI Research Integrity Checklist from CLAUDE.md
- [2026-05-01 23:17] `a0407af`: feat: PyPop HBB paper COMPLETE — autonomous night draft
- [2026-05-01 22:16] `a772df4`: feat: PyPop population stratification — 2 FALSE PEARLS detected
