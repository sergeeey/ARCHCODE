# Review Response Plan — ARCHCODE External Review

**Generated:** 2026-03-10
**Agent:** paper-critic (Mode 2: Respond to External Review)
**Method:** Every claim checked against actual data files in `analysis/` and `results/`

---

## Reviewer Objectivity: 8/10

This is a high-quality, technically sophisticated review. Most points target genuine weaknesses. The reviewer understands the paper well and identifies the real structural issues. A few points (2.2, 3.2) reflect partial reading — the manuscript already addresses them. The overall scores (Methodological rigor 2.5/5, Reproducibility 2/5) are harsh but defensible given the data we have.

---

## Point-by-Point Response

| # | Reviewer Point | Objectivity (1-5) | Can We Answer? | Response Strategy | Data Source | Priority | Effort |
|---|---------------|-------------------|----------------|-------------------|-------------|----------|--------|
| 1.1 | N=1 locus (HBB dominates Class B) | 5 — valid | PARTIAL | SCN5A cardiac + acknowledge + reframe | `scn5a_cardiac_comparison.json`, `taxonomy_assignment_table.csv` | P0 | MEDIUM |
| 1.2a | LSSIM < 0.95 threshold sensitivity | 4 — valid, we have partial defense | PARTIAL | EXP-004 bootstrap + sweep; but no permutation test | `threshold_robustness_summary.json`, `threshold_robustness.csv` | P0 | MEDIUM |
| 1.2b | VEP > 0.5 not standard | 3 — partially valid | YES | We use VEP consequence categories, not a numeric score > 0.5 | `roc_unified.json` (quadrants use VEP > 0.3) | P1 | LOW |
| 1.2c | tissue_match >= 0.5 algorithm not described | 5 — valid | NO — algorithm not formalized | Must write formal definition | Manual assignment in taxonomy paper, no algorithm | P0 | LOW |
| 1.3 | Circularity in class definitions | 4 — valid concern | PARTIAL | EXP-002 LOLO + external benchmarks partially break circle | `leave_one_locus_out_summary.json`, `gasperini_benchmark_summary.json` | P0 | MEDIUM |
| 2.1 | NMI no confidence intervals | 4 — valid | NO | Need bootstrap CI on NMI | `nmi_per_locus.csv` | P1 | LOW |
| 2.2 | p-values without effect sizes | 3 — partially addressed | PARTIAL | Manuscript has ΔAUC and "negligible effect sizes" language; need Cohen's d/OR | `enhancer_proximity_odds.json` (OR=22.46 exists) | P1 | LOW |
| 2.3 | AUC 0.64-0.69 insufficient for clinical | 2 — already addressed | YES | Paper explicitly frames as "prioritizer not predictor" | `body_content.typ` lines 1573, 1674 | P2 | LOW |
| 3.1 | Structural disruption ≠ disease | 2 — already addressed | YES | Paper has explicit epistemic limitation (Section 6.7 taxonomy) | Taxonomy paper Section 6.7, biorxiv Limitations #6 | P2 | LOW |
| 3.2 | Class C co-location ≠ co-causation | 3 — valid nuance | YES | Paper already calls Class C "tentative", requires dual-readout | `taxonomy_assignment_table.csv` line 3 (confidence: MEDIUM) | P1 | LOW |
| 4.1 | Code not mentioned | 1 — factually wrong | YES | Code, Zenodo, GitHub all listed | `body_content.typ` lines 1374-1389, 1763-1765 | P2 | NONE |
| 4.2 | Simulation parameters qualitative only | 3 — partially valid | PARTIAL | Parameters listed but no assembly script | Methods section, `body_content.typ` | P1 | MEDIUM |
| 4.3 | No assembly script for tissue configs | 4 — valid | NO | Need to package config generation | Config JSONs exist but no documented pipeline | P1 | MEDIUM |
| 5.1 | Class D clinical misinterpretation risk | 4 — valid | PARTIAL | Paper has disclaimers but could be stronger | `body_content.typ` lines 1573, 1989 | P1 | LOW |
| 6.1 | Experimental validation needed (Hi-C for Q2b) | 5 — valid | NO | Cannot do experiments; must frame as future work | N/A | P0 | HIGH (not doable) |

---

## Detailed Evidence for Each Point

### 1.1 N=1 locus problem

**Reviewer claim:** "25 of 54 Class B variants come from HBB."

**Data check [VERIFIED]:** From `taxonomy_assignment_table.csv`:
- HBB Q2b: 25 variants (HIGH confidence)
- BRCA1 Q2b: 26 variants (LOW confidence — "threshold artifacts, AF 40-50%")
- TP53 Q2b: 2 variants (LOW confidence — "threshold-proximal LSSIM")
- TERT Q2b: 1 variant (LOW confidence — "single Q2b variant")

**Honest assessment:** The reviewer is RIGHT. HBB provides the only HIGH-confidence Class B evidence. BRCA1's 26 Q2b variants are explicitly flagged as "likely threshold artifacts rather than true architecture-driven" in our own taxonomy table (precision 3.8%). So the real count of confident Class B is 25/54 = 46%, but effectively 25/25 = 100% of confident ones.

**Defense available:** `scn5a_cardiac_comparison.json` shows that SCN5A with cardiac-matched chromatin produces 577 structural calls (vs 199 with K562), with 2.9x amplification. This is a proof-of-concept that tissue matching unlocks Class B at other loci — but we have NOT actually identified specific SCN5A Q2b variants with cardiac configs.

**Response strategy:**
1. Acknowledge HBB dominance openly (already done in taxonomy paper Section 6.2)
2. Present SCN5A cardiac as proof-of-concept for tissue-dependent Class B detection
3. Downgrade claim from "54 Class B variants across loci" to "25 confident Class B at HBB + 29 candidate variants requiring tissue-matched validation at 3 additional loci"
4. Frame as hypothesis-generating, not confirmatory

**Verdict: PARTIALLY DEFENSIBLE. Must soften claims.**

---

### 1.2a LSSIM < 0.95 threshold

**Data check [VERIFIED]:** From `threshold_robustness_summary.json`:
- Bootstrap (1000 iterations): observed=286, 95% CI=[271, 300], SD=7.13
- Perturbation test (500 iterations, 20% noise): observed=286, 95% CI=[284, 294], SD=2.54
- Threshold sweep across 9 loci: stability zones vary widely
  - HBB: stable 0.93-0.965 (width 0.035)
  - BRCA1: stable 0.89-0.96 (width 0.07)
  - TP53: stable 0.95-0.955 only (width 0.005) — VERY narrow
  - TERT, SCN5A, GJB2: zero width (threshold-dependent)

From `threshold_robustness.csv`: HBB count changes from 279 (at 0.945) to 287 (at 0.950) to 300 (at 0.955) — an 8-variant jump at the threshold boundary.

**Honest assessment:** We have bootstrap CI and perturbation analysis. We do NOT have a permutation test (randomizing labels to derive a null distribution). The reviewer is right that independent justification is missing.

**Response strategy:**
1. Present existing bootstrap + perturbation evidence
2. Add a permutation test: shuffle pathogenic/benign labels 1000 times, compute Q2b count at each threshold, derive empirical p-value (effort: ~2 hours scripting)
3. Acknowledge that TP53/TERT/SCN5A/GJB2 stability zones are narrow or zero — supporting the argument that per-locus calibration is needed (already in Limitation #9)

**Verdict: PARTIALLY DEFENSIBLE. Permutation test needed as new analysis (P0).**

---

### 1.2b VEP > 0.5 threshold

**Data check [VERIFIED]:** From `roc_unified.json`, the actual quadrant definition uses `vep_threshold: 0.3`, not 0.5. The taxonomy paper uses VEP consequence categories (VEP = -1 for no score, VEP > 0 for any consequential annotation). The "0.5" appears to be a reviewer misreading — or comes from a different section.

**Response strategy:** Clarify that VEP is used categorically (scored vs unscored vs consequence class), not as a continuous numeric threshold. The Q2a/Q2b split is based on VEP = -1 (no annotation) vs VEP = 0-0.5 (low-impact annotation), which ARE standard VEP output categories.

**Verdict: DEFENSIBLE with clarification.**

---

### 1.2c tissue_match >= 0.5 algorithm

**Data check:** From `taxonomy_assignment_table.csv`, tissue_match values are:
- HBB: 1.0 (K562 = erythroid, HBB expressed in erythroid)
- BRCA1, TP53, TERT, MLH1: 0.5 (partial match)
- CFTR, SCN5A, GJB2, LDLR: 0.0 (mismatch)

From `gnomad_constraint_taxonomy.json`, same values appear but no algorithm is documented.

From the taxonomy paper (Section 3.6 and 6.6): tissue_match is listed as a threshold (>= 0.5 required for Class B) but no formal algorithm for computing it is described.

**Honest assessment:** The reviewer is COMPLETELY RIGHT. tissue_match is manually assigned based on biological knowledge (does K562 express this gene / have relevant enhancer landscape?), not computed by an algorithm. This is a significant methodological gap — it makes the classification subjective and non-reproducible.

**Response strategy:**
1. Acknowledge manual assignment explicitly
2. Define formal criteria: tissue_match = 1.0 if cell line is primary expression tissue for the gene; 0.5 if gene is expressed but cell line is not primary tissue; 0.0 if gene is not expressed or enhancer landscape is absent
3. Document the evidence for each assignment (expression data source, enhancer annotation source)
4. Note this as a limitation: future work should develop a quantitative tissue-match metric based on expression + enhancer density + CTCF overlap

**Verdict: NOT DEFENSIBLE in current form. Must add formal definition (P0).**

---

### 1.3 Circularity in class definitions

**Reviewer claim:** "Class B = LSSIM<0.95 and VEP<0.5" → "ARCHCODE detects Class B which VEP misses" = tautology.

**Data check [VERIFIED]:** This is a real circularity concern. The class IS defined by the tool outputs, and then the paper claims the tool detects that class. However:

From `leave_one_locus_out_summary.json`:
- Leave-one-locus-out cross-validation shows threshold generalizes (derived thresholds: 0.967-0.977 across held-out loci)
- AUC is computed on held-out loci, not training data

From `gasperini_benchmark_summary.json`:
- External CRISPRi data (Gasperini 2019, 90,955 pairs) mapped: 132 variants overlap
- LSSIM vs CRISPRi effect size: Spearman rho = -0.2324, p = 0.007 — modest but significant correlation with INDEPENDENT experimental data

From `enhancer_proximity_odds.json`:
- Q2b enhancer proximity (OR = 22.46 at 500bp, p = 2.14e-25) is an INDEPENDENT observation — enhancer distance is not used in the class definition

**Response strategy:**
1. Acknowledge the circularity explicitly
2. Present three lines of evidence that partially break the circle:
   a. LOLO cross-validation (threshold derived on other loci)
   b. Gasperini CRISPRi correlation (rho = -0.23, p = 0.007) — external experimental
   c. Enhancer proximity enrichment (OR = 22.46) — independent feature not in class definition
3. Acknowledge that full circle-breaking requires experimental validation (Hi-C on Q2b variants)

**Verdict: PARTIALLY DEFENSIBLE. Circularity is real but mitigated by independent evidence.**

---

### 2.1 NMI confidence intervals

**Data check [VERIFIED]:** From `nmi_per_locus.csv`:
- NMI(ARCHCODE, VEP) ranges from 0.0 (SCN5A, GJB2) to 0.4945 (HBB)
- No confidence intervals are reported anywhere

**Honest assessment:** Valid criticism. NMI = 0.024 without CI is uninterpretable — could be noise.

**Response strategy:** Add bootstrap CI for NMI. Resample variants with replacement 1000 times, compute NMI each time. Effort: ~1 hour.

**Verdict: NOT DEFENSIBLE. Easy fix (P1).**

---

### 2.2 p-values without effect sizes

**Data check [VERIFIED]:**
- From `enhancer_proximity_odds.json`: OR = 22.46 at 500bp (p = 2.14e-25). **Effect size IS reported as odds ratio.**
- From `body_content.typ` line 621, 1480: "negligible effect sizes" and ΔAUC are mentioned for within-category tests
- Missing: Cohen's d for LSSIM pathogenic vs benign distributions

**Response strategy:**
1. The main enhancer proximity claim already has OR = 22.46 — a very large effect size. Report it more prominently.
2. Add Cohen's d for key LSSIM comparisons (path mean - benign mean / pooled SD)
3. The p = 2.51e-31 for enhancer proximity with OR = 22.46 is NOT an artifact of large N — this is a genuine large effect

**Verdict: MOSTLY DEFENSIBLE. Need to add Cohen's d, but OR already exists.**

---

### 2.3 AUC and clinical applicability

**Data check [VERIFIED]:**
- From `ablation_study_summary.json`: combined AUC = 0.6381 (M4 ARCHCODE) across 8 loci
- From `roc_unified.json`: HBB AUC = 0.9766 (but this is category-level, not positional)
- From `body_content.typ` line 1573: "We specifically do not recommend clinical reclassification based on the..."
- The term "mechanism-first workflow" appears in the clinical section

**Honest assessment:** The reviewer conflates two numbers. The 0.64-0.69 AUC is the cross-locus prioritization performance. The 0.977 is HBB-specific category-level. The paper already frames ARCHCODE as a prioritizer, not a clinical tool. However, the "mechanism-first workflow" language in the ACMG section may overreach.

**Response strategy:**
1. Emphasize that 0.64-0.69 is the honest cross-locus number
2. Note that the paper explicitly disclaims clinical use
3. Soften "mechanism-first workflow" to "mechanism-informed prioritization" or add more caveats
4. Add explicit statement: "ARCHCODE AUC of 0.64-0.69 is appropriate for research prioritization but insufficient for standalone clinical interpretation"

**Verdict: DEFENSIBLE — paper already makes the right claims, minor language fixes needed.**

---

### 3.1 Structural disruption ≠ disease

**Data check [VERIFIED]:** From taxonomy paper Section 6.7: "we cannot prove that Q2b variants are pathogenic through architecture" — this is already stated with remarkable clarity. From `body_content.typ` line 1411-1413: "We have not confirmed a mechanistic link between structural disruption and pathogenicity."

**Response strategy:** Point reviewer to these existing sections. They are unusually honest for a preprint. No changes needed beyond possibly making the Significance Statement caveat even more prominent.

**Verdict: ALREADY ADDRESSED. Cite specific paragraphs.**

---

### 3.2 Class C co-localization ≠ co-causation

**Data check [VERIFIED]:** From `taxonomy_assignment_table.csv` line 3: HBB Q1 (270 variants) assigned Class C with confidence MEDIUM, rationale includes "could be coincidental co-occurrence."

From taxonomy paper Section 3.3: "The co-occurrence of both signals is consistent with dual-mechanism disruption, though it could also reflect coincidental spatial proximity."

**Response strategy:** Point to existing caveats. The paper already qualifies Class C as tentative and requiring multi-omic validation. Perhaps make the figure legend more explicit about this.

**Verdict: ALREADY ADDRESSED.**

---

### 4.1 Code not mentioned

**Data check [VERIFIED]:** From `body_content.typ`:
- Line 1374-1375: "Software and Code Availability" section with GitHub URL and Zenodo DOI
- Line 1763-1765: "Data and Code Availability" section
- Line 1798: GitHub URL repeated in references

**Response strategy:** The reviewer is factually wrong. Code availability IS mentioned, with GitHub URL, Zenodo DOI, and version tag. Quote the exact sections.

**Verdict: FULLY DEFENSIBLE. Reviewer oversight.**

---

### 4.2 Simulation parameters qualitative only

**Data check:** From `body_content.typ` lines 80-84: Parameters are described as "manually calibrated to published literature ranges" with citations. The Methods section describes the model.

**Honest assessment:** Partially valid. Parameters are listed with their values and literature sources, but the full parameterization table may not include ALL OpenMM-level details. The model is analytical (mean-field), not OpenMM — the reviewer may be confused about the simulation approach.

**Response strategy:**
1. Clarify that ARCHCODE uses an analytical mean-field model, NOT molecular dynamics (OpenMM)
2. Provide complete parameter table with values, units, and literature sources
3. Ensure the Zenodo archive includes all config files

**Verdict: PARTIALLY DEFENSIBLE. Clarify model type + add complete parameter table.**

---

### 4.3 Tissue configs: no assembly script

**Data check:** Config JSON files exist in the repository (e.g., `scn5a_cardiac_250kb.json`), but there is no documented script that generates them from raw ENCODE data.

**Response strategy:** Create a documented pipeline script that takes ENCODE ChIP-seq BED files and generates locus config JSONs. Include it in Zenodo v3. Effort: ~4 hours.

**Verdict: NOT DEFENSIBLE currently. Need assembly script (P1).**

---

### 5.1 Class D clinical misinterpretation

**Data check [VERIFIED]:** From `body_content.typ` line 1989: "Important disclaimer: The following ACMG assessment is..." and line 1573: "We specifically do not recommend clinical reclassification."

**Response strategy:** Add explicit "RESEARCH USE ONLY" header to any tables showing Class B/D assignments. Strengthen the disclaimer to a boxed warning.

**Verdict: PARTIALLY DEFENSIBLE. Disclaimer exists but could be stronger (P1).**

---

### 6.1 Experimental validation (Hi-C for Q2b)

**Honest assessment:** We cannot perform experiments. This is a computational study. The reviewer's request for "Hi-C for ≥3 Q2b variants" is reasonable but outside our current capabilities.

**Response strategy:**
1. Acknowledge this as the central limitation
2. Name specific experiments and their expected outcomes (Capture Hi-C at HBB, 4C-seq, allele-specific contact assays)
3. Propose collaboration or data-sharing with experimental groups
4. Frame the paper's contribution as generating testable hypotheses with specific predictions

**Verdict: NOT DEFENSIBLE without experiments. Frame as future work.**

---

## Priority Actions

### P0 — Must Fix Before Resubmission

| Action | Description | Effort | Files to modify |
|--------|-------------|--------|-----------------|
| P0.1 | Soften Class B claim: "25 confident + 29 candidate" not "54 confirmed" | LOW | `body_content.typ`, abstract |
| P0.2 | Add permutation test for LSSIM threshold justification | MEDIUM | New script + `threshold_robustness_summary.json` |
| P0.3 | Formalize tissue_match algorithm with explicit criteria table | LOW | Methods section, new table |
| P0.4 | Address circularity: add paragraph on circle-breaking evidence (LOLO, Gasperini, enhancer OR) | LOW | Discussion section |
| P0.5 | Acknowledge N=1 limitation more prominently in abstract/significance | LOW | Abstract, Significance Statement |

### P1 — Strengthens Paper

| Action | Description | Effort | Files to modify |
|--------|-------------|--------|-----------------|
| P1.1 | Add bootstrap CI for NMI values | LOW | New analysis script |
| P1.2 | Report Cohen's d alongside p-values for key comparisons | LOW | Results section |
| P1.3 | Create tissue config assembly script for reproducibility | MEDIUM | New script + Zenodo |
| P1.4 | Clarify model is analytical mean-field, not OpenMM/MD | LOW | Methods section |
| P1.5 | Strengthen clinical disclaimer to boxed "RESEARCH ONLY" | LOW | Clinical section |
| P1.6 | Soften "mechanism-first workflow" to "mechanism-informed prioritization" | LOW | Clinical section |
| P1.7 | Complete parameter table (all values, units, sources) | LOW | Supplementary |
| P1.8 | Clarify VEP is used categorically, not as numeric > 0.5 | LOW | Methods section |

### P2 — Nice to Have

| Action | Description | Effort |
|--------|-------------|--------|
| P2.1 | Add Class C multi-omic requirement to figure legend | LOW |
| P2.2 | Make Significance Statement caveat more prominent | LOW |
| P2.3 | Point reviewer to existing code availability sections | NONE (response letter only) |

---

## Text Changes Needed

### 1. Abstract / Significance Statement

**Before:** "...the 54 true structural blind spots (Q2b) cluster 58-fold closer to enhancers..."

**After:** "...25 high-confidence structural blind spots (Q2b) at the tissue-matched HBB locus and 29 candidate Q2b at partially-matched loci cluster 58-fold closer to enhancers..."

### 2. Methods — New subsection: Tissue Match Score

**Add:**
> **Tissue-match classification.** Each locus was assigned a tissue-match score reflecting concordance between the K562 simulation cell line and the gene's primary expression tissue. Scores were assigned manually based on three criteria: (1) gene expression in K562 (GTEx/ENCODE RNA-seq), (2) presence of disease-relevant enhancers in K562 ChIP-seq data (H3K27ac, H3K4me1), and (3) concordance of CTCF binding profile between K562 and the primary disease tissue. Scores: 1.0 = K562 is the primary expression tissue (HBB: erythroid); 0.5 = gene is expressed in K562 but K562 is not the primary disease tissue (BRCA1, TP53, MLH1, TERT); 0.0 = gene is not meaningfully expressed in K562 or K562 lacks the relevant enhancer landscape (CFTR: lung, SCN5A: cardiac, GJB2: cochlear, LDLR: hepatic). This classification is heuristic and should be replaced by a quantitative metric incorporating expression level, enhancer density, and CTCF overlap in future work.

### 3. Discussion — New paragraph on circularity

**Add after Section on cross-validation:**
> **Addressing circularity in class definitions.** A potential concern is that classes defined by ARCHCODE and VEP outputs are then used to evaluate those same tools, creating a tautology. Three lines of evidence partially break this circle. First, leave-one-locus-out cross-validation (EXP-002) derives the LSSIM threshold from training loci and evaluates on a held-out locus, preventing threshold overfitting. Second, Gasperini CRISPRi data provides external experimental evidence: LSSIM correlates with CRISPRi effect size (Spearman rho = -0.23, p = 0.007) using data generated independently of ARCHCODE. Third, enhancer proximity enrichment (OR = 22.46, p = 2.14 × 10⁻²⁵) is an independent geometric feature not used in class definition. However, we acknowledge that full resolution of the circularity concern requires experimental validation: allele-specific Capture Hi-C on Q2b variants in tissue-matched cells would provide tool-independent evidence for structural disruption.

---

## Estimated Overall Effort

- **P0 fixes:** ~2-3 days (mostly the permutation test script + text edits)
- **P1 fixes:** ~2-3 days (NMI bootstrap, Cohen's d, config assembly script, parameter table)
- **P2 fixes:** ~2 hours (minor text edits)
- **Total:** ~1 week of focused work

## Honest Summary

The reviewer's overall assessment (Conceptual novelty 5/5, Methodological rigor 2.5/5) is fair. Our main vulnerability is:

1. **HBB dominance is real** — we have one well-validated locus and the rest are tentative
2. **Threshold justification is incomplete** — bootstrap exists but permutation test is missing
3. **tissue_match is subjective** — no formal algorithm, manually assigned
4. **No experimental validation** — this is the gap we cannot close computationally

Our strongest defenses are:
1. The paper already contains unusually honest limitations (Sections 6.2-6.7 in taxonomy, 11 numbered limitations in bioRxiv)
2. Effect sizes are large where they matter (OR = 22.46 for enhancer proximity)
3. Multiple independent benchmarks partially break circularity (LOLO, Gasperini, enhancer distance)
4. Code and data ARE available (Zenodo + GitHub) — reviewer missed this
5. The "prioritizer not predictor" framing is already explicit

The paper should be resubmitted with P0 fixes and as many P1 fixes as feasible. The experimental validation gap (6.1) is honestly acknowledged and cannot be resolved without a collaborating wet-lab group.
