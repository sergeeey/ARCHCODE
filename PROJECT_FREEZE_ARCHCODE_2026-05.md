# PROJECT FREEZE — ARCHCODE (2026-05-09)

**Status:** ACTIVE  
**Duration:** Until manuscript v1.0 submitted  
**Date:** 2026-05-09  
**Trigger:** Experiment X.1 complete, H6 hypothesis killed

---

## 1. FINAL THESIS (One Sentence)

**"ARCHCODE is a falsification-first structural hypothesis engine; broad pathogenicity prediction failed under systematic stress-testing, but the validation framework itself represents the project's primary contribution."**

---

## 2. CLAIMS LEDGER

### SUPPORTED (Can be stated without caveat)

| ID | Claim | Evidence | Confidence |
|---|---|---|---|
| S1 | 30,318 ClinVar variants across 9 loci analyzed | Unified Atlas files, validation suite | HIGH |
| S2 | Falsification-first validation framework (30 automated tests) | validation_suite/results/master_results.json | HIGH |
| S3 | Category mapping drives most signal (within-category AUC ≈ 0.48) | within_category_analysis.json, task5 summary | HIGH |
| S4 | Simple baselines match/beat SSIM on 8/9 loci | validation suite, README.md:44 | HIGH |
| S5 | Cross-locus threshold transfer fails | master_results.json, README.md | HIGH |
| S6 | HBB 25 pearls computational candidates (not validated pathogenic) | HBB_Unified_Atlas.csv, PROJECT_CANON.md | MEDIUM |
| S7 | MPRA cross-validation globally null (p=0.91) | publication_claim_matrix P08 | HIGH |

### EXPLORATORY (Hypothesis-generating, not confirmed)

| ID | Claim | Evidence | Caveat |
|---|---|---|---|
| E1 | HBB promoter-cluster AlphaGenome CAGE signal (p=2.77e-4) | alphagenome_pearl_vs_control.json | Auxiliary evidence only; promoter cluster (11/13 in 73bp); category artifact not ruled out |
| E2 | TP53 splice_region within-category AUC 0.69 | tp53_splice_region_deep_dive.json | RF baseline stronger (0.825); marginal signal |
| E3 | Tissue-specificity gradient observed | AUDIT_HYPOTHESIS_LEDGER.md | Insufficient formal testing |
| E4 | 29 non-HBB Class B candidates | VUS router results | Exploratory only, require tissue-matched follow-up |

### REJECTED (Falsified or blocked)

| ID | Claim | Why Rejected | Evidence |
|---|---|---|---|
| R1 | Broad structural pathogenicity predictor | Within-category AUC ≈ 0.50 (chance); cross-locus transfer fails | master_results.json, README.md:44 |
| R2 | HBB AUC proves independent physics | Category ablation: AUC 0.98 → category artifact dominates | publication_claim_matrix P09 |
| R3 | MPRA validates HBB pearls | Global null (p=0.91) | publication_claim_matrix P08 |
| R4 | Cross-locus threshold generalization | Fails on majority of loci | AUDIT_HYPOTHESIS_LEDGER.md |
| R5 | Compactness effect (H6) | **Spearman r=-0.05, p=0.90 (Experiment X.1)** | h6_compactness_test.json |
| R6 | AlphaGenome as independent validation | Auxiliary support only; training overlap possible | AUDIT_HYPOTHESIS_LEDGER.md |
| R7 | BCL11A public canonical locus | Technical bridge only | PROJECT_CANON.md |
| R8 | Class B matched-control test | p=0.996 (FAIL) | README.md:68 |

---

## 3. SINGLE SOURCE OF TRUTH MAP

### Key Numbers

| Number | Source File | Line/Field | Notes |
|---|---|---|---|
| 30,318 variants | Results files | Unified Atlas CSVs | Total across 9 loci |
| 9 loci | PROJECT_CANON.md | Line 45 | HBB, BRCA1, TP53, MLH1, LDLR, CFTR, SCN5A, TERT, GJB2 |
| 25 HBB pearls | PROJECT_CANON.md | Line 46 | High-confidence canonical core |
| Within-category AUC 0.482 | task5_vus_stratification_summary_2026-03-06.json | Line 20 | Mean across loci |
| HBB CAGE p=2.77e-4 | results/alphagenome_pearl_vs_control.json | Line 7 | Mann-Whitney U, one-sided |
| Cohen's d=-1.53 | results/alphagenome_pearl_vs_control.json | Line 8 | Large effect size |
| TP53 AUC 0.69 | results/tp53_splice_region_deep_dive.json | Line 6 | Splice_region category |
| RF baseline 0.825 | results/tp53_splice_region_deep_dive.json | Line 22 | Stronger than SSIM |
| H6 correlation r=-0.05 | results/h6_compactness_test.json | statistics.spearman_r | No compactness effect |
| Class B matched p=0.996 | README.md | Line 68 | Indistinguishable from benign |

### Validation Contracts

| Artifact | Purpose | Status |
|---|---|---|
| validation_suite/results/master_results.json | 30 automated tests | PASSED (suite complete) |
| results/publication_claim_matrix_2026-03-30.json | 10 public claims | 5 SUPPORTED, 5 SUPPORTED_WITH_CAVEAT |
| AUDIT_HYPOTHESIS_LEDGER.md | 24 hypothesis statuses | 5 living, 12 closed/blocked |
| evidence_pack/ | Reproducibility package | Complete (May 9) |

---

## 4. MANUSCRIPT OUTLINE (6 Sections)

### Title (working)

**"Systematic falsification of a 3D chromatin variant model reveals category artifacts and validates a falsification-first framework"**

Alternative: "Stress-testing ARCHCODE: When 3D chromatin models fail, and what survives"

### Structure

**1. Introduction (800 words)**
- Why 3D-genome models need falsification-first testing
- ARCHCODE as test case: physics-based loop extrusion simulator
- Research question: Does 3D structural simulation add discriminative value beyond category + position?

**2. Methods (1200 words)**
- ARCHCODE engine (mean-field loop extrusion, SSIM scoring)
- 9 loci, 30,318 variants (ClinVar)
- Validation suite: 30 automated tests
  - Within-category AUC
  - Simple baselines (RF, logistic, position-only)
  - CTCF shuffle controls
  - Cross-locus threshold transfer
  - Matched-control tests

**3. Stress Tests That Failed Broad Predictor (1500 words)**
- **Category artifact dominates:** Overall AUC high, within-category ≈ 0.50
- **Simple baselines win:** RF/position match or beat SSIM on 8/9 loci
- **Cross-locus transfer fails:** No universal threshold
- **Matched controls indistinguishable:** Class B vs benign same category, p=0.996
- **Compactness hypothesis killed:** Experiment X.1, r=-0.05, p=0.90
- **Verdict:** Broad structural pathogenicity predictor refuted

**4. Surviving Signals (1000 words)**
- **HBB promoter-cluster:** AlphaGenome CAGE p=2.77e-4, Cohen's d=-1.53
  - Caveat: 11/13 pearls in 73bp cluster, category artifact not ruled out, auxiliary evidence only
- **TP53 splice_region:** Within-category AUC 0.69
  - Caveat: RF baseline stronger (0.825), marginal signal
- **Falsification framework:** 30 automated tests, reproducible, open-source
  - **Primary contribution:** Not the predictor, but the validation methodology

**5. Discussion: Limitations and Failure Modes (1200 words)**
- No wet-lab validation (all computational)
- AlphaGenome = auxiliary support, not independent validation
- Category artifact harder to eliminate than expected
- Compactness hypothesis tested and rejected
- Small N regulatory loci (HBB dominant)
- Matched controls reveal limits of VEP-blind claims
- **Honest assessment:** ARCHCODE useful for hypothesis generation, not clinical prediction

**6. Reproducibility Package (300 words)**
- Code: github.com/sergeeey/ARCHCODE
- Data: Zenodo v2.17 (DOI: 10.5281/zenodo.18908214)
- Validation suite: validation_suite/ (npm test)
- Evidence pack: evidence_pack/ (forensic audit + raw results)
- Experiment X.1 script: scripts/test_h6_compactness.py

**Target length:** 6000 words  
**Figures:** 4-5 (validation suite summary, within-category AUC heatmap, baseline comparison, HBB CAGE, TP53 splice)  
**Target journal:** bioRxiv → PLoS Computational Biology or Bioinformatics

---

## 5. STOP RULES (Hard Constraints for Next 4-6 Weeks)

### ❌ FORBIDDEN ACTIONS

| Action | Why Forbidden | Penalty if Violated |
|---|---|---|
| Add new loci to atlas | Scope creep, delays manuscript | Restart 4-week timer |
| Create new headline claims | All major claims tested, ledger frozen | Integrity violation |
| Run new AlphaGenome predictions | Auxiliary evidence only, not needed | Waste of $10-50 |
| Run Experiment X.2 (full Hi-C) | X.1 already killed H6, diminishing returns | Waste of 5-7 days |
| Run H4a (temporal leakage) | Low ROI, won't change conclusion | Waste of 2-3 days |
| Run H5a (tissue-matched test) | Insufficient data, won't change conclusion | Waste of 3-5 days |
| Start wet-lab experiments | No collaborator, premature | $1000s wasted |
| Modify validation suite tests | Tests frozen, reproducibility critical | Break reproducibility |
| Expand HBB pearl set beyond 25 | Canonical core frozen | Break canonical claims |
| Promote BCL11A to public canon | Technical only, already blocked | Violate governance |

### ✅ ALLOWED ACTIONS

| Action | Purpose | Timeline |
|---|---|---|
| Write manuscript sections | Primary deliverable | Weeks 1-4 |
| Update evidence_pack/ | Reproducibility | Week 1 |
| Create figures for manuscript | Visualization | Week 2 |
| Internal review (reviewer agent) | Quality gate | Week 3 |
| Polish manuscript to v1.0 | Final cleanup | Week 4 |
| Commit to git, tag v1.0 | Version control | Week 4 |
| Submit to bioRxiv | Publication | Week 4-5 |
| Create Zenodo v2.18 | Archive | Week 4-5 |

### ⚠️ CONDITIONAL ACTIONS (Require Explicit User Approval)

- Expand Discussion beyond 1200 words (if needed for honest caveats)
- Add 6th section (Future Work) if journal requires
- Create supplementary materials (if >6000 words)
- Respond to Nora outreach (if reply received)

---

## 6. SUCCESS CRITERIA (Week-by-Week Milestones)

### Week 1 (May 9-15): Foundation

- [x] Experiment X.1 complete (DONE May 9)
- [x] PROJECT_FREEZE created (DONE May 9)
- [ ] Manuscript outline v0.1 (Introduction + Methods draft)
- [ ] Update activeContext.md with freeze status
- [ ] Evidence pack finalized (no new files)

**Deliverable:** 2000 words draft (Intro + Methods)

### Week 2 (May 16-22): Core Content

- [ ] Section 3 (Stress Tests) draft
- [ ] Section 4 (Surviving Signals) draft
- [ ] 4-5 figures created
- [ ] Within-category AUC heatmap
- [ ] Baseline comparison table

**Deliverable:** 4000 words draft (Sections 1-4)

### Week 3 (May 23-29): Polish + Review

- [ ] Section 5 (Discussion) draft
- [ ] Section 6 (Reproducibility) draft
- [ ] Manuscript v0.9 complete (6000 words)
- [ ] Internal review (reviewer agent)
- [ ] Address review feedback

**Deliverable:** 6000 words draft v0.9

### Week 4 (May 30 - June 5): Submit

- [ ] Manuscript v1.0 final
- [ ] Abstract + cover letter
- [ ] Supplementary materials (if needed)
- [ ] Git tag v1.0-falsification-paper
- [ ] Submit to bioRxiv
- [ ] Zenodo v2.18 archive

**Deliverable:** Submitted manuscript + DOI

### Week 5-6 (June 6-19): Post-Submit

- [ ] Monitor bioRxiv review (2-5 days)
- [ ] Address any immediate errors
- [ ] Post to r/genomics, Biostars (if approved)
- [ ] LinkedIn post (professional)
- [ ] Close project or pivot to next

**Deliverable:** Public preprint + community feedback

---

## 7. ABANDON CRITERIA (When to Stop)

**If by Week 4:**

1. **Cannot formulate honest thesis** without overclaims or hiding limitations → STOP, archive as research exploration
2. **Reproducibility package fails** independent run (validation suite breaks) → FIX before submit, or delay
3. **Manuscript blocked** by reviewer risk register (critical flaws) → Address or abandon
4. **User burnout** after 4 weeks writing → Acceptable to pause, revisit in 1-2 months
5. **External feedback** (Nora, collaborators) suggests fundamental flaw → Reassess, possibly abandon

**Hard stop date:** June 19, 2026 (6 weeks from freeze)

If manuscript not submitted by June 19 → **Archive project**, move to next priority.

---

## 8. RISK REGISTER (Top 5 Threats)

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Reviewer finds fatal flaw in validation suite | Medium | HIGH | Run internal review (Week 3), stress-test all claims |
| Manuscript rejected by bioRxiv (affiliation) | Low | MEDIUM | Ronin RIIS 2.0 approval expected ~May 10; fallback: arXiv |
| Burnout before Week 4 | Medium | HIGH | 4-week hard limit; pause allowed if needed |
| Category artifact explanation unclear | Low | MEDIUM | Write Discussion carefully, cite ablation study |
| HBB CAGE signal dismissed as artifact | Medium | MEDIUM | Frame as auxiliary, exploratory; primary = framework |

---

## 9. VERSION CONTROL

**Git tag:** v1.0-project-freeze (commit 4e1625b + this file)

**Branches:**
- `experiment/spectral-collapse-pilot` (current) → merge to `main` after manuscript submit
- `main` (stable) → update after v1.0 manuscript tag

**Zenodo:**
- v2.17 (current) — pre-freeze
- v2.18 (planned) — post-manuscript, includes PROJECT_FREEZE

---

## 10. FINAL NOTES

### What Changed (Post-Experiment X.1)

**Before Experiment X.1:**
- Unclear if compactness explains residual signal (H6 untested)
- Possibility of H2 + H6 combination
- Paper framing uncertain

**After Experiment X.1:**
- H6 **killed** (r=-0.05, p=0.90)
- H2 (Category Artifact) **dominates completely**
- Paper framing: **Pure falsification** (no ambiguity)

**Decision:** 5 weeks timeline (not 6), pure falsification framing, no deeper compactness analysis needed.

### Chamberlin-Platt Verdict

From 6 competing hypotheses:
- **H1 (Broad Predictor):** KILLED by validation suite
- **H2 (Category Artifact):** **WINNER** (confidence 0.85 → 0.95 post-X.1)
- **H3 (Island Hypothesis):** WEAK (post-hoc rationalization)
- **H4 (Data Leakage):** INDIRECT (no smoking gun, but pattern consistent)
- **H5 (Tissue Grammar):** INSUFFICIENT (interesting but untested)
- **H6 (Compactness):** **KILLED** by Experiment X.1

**Surviving explanation:** H2 alone. No combination needed.

### Honest Self-Assessment

**What ARCHCODE is:**
- Fast structural perturbation engine (sub-second per variant)
- Hypothesis generator for follow-up wet-lab
- Falsification-first validation framework (primary contribution)

**What ARCHCODE is NOT:**
- Clinical pathogenicity predictor
- Cross-locus generalizable model
- Independent validation of variant pathogenicity
- Replacement for VEP, SpliceAI, CADD

**Realistic impact:**
- Methodological paper (falsification framework)
- Cautionary tale (category artifacts in genomics ML)
- Open-source tool for exploratory structural screening
- Honest negative result (rare in genomics)

### Why This Matters

Most genomics papers report AUC >0.9 and claim "novel predictor." Few test:
- Within-category discrimination (exposes category artifact)
- Simple baselines (exposes feature leakage)
- Cross-locus transfer (exposes overfitting)
- Matched controls (exposes confounders)

**ARCHCODE's contribution:** Built and documented a falsification framework that **kills most genomics ML claims** — including its own.

This is more valuable than another "AUC=0.98 predictor."

---

**Last Updated:** 2026-05-09  
**Status:** ACTIVE  
**Next Review:** Week 2 milestone check (May 22)

---

_"The project did not fail. It found what it was not looking for."_
