# Taxonomy Assignment Summary

**Date:** 2026-03-09
**Source:** `analysis/taxonomy_assignment_table.csv`
**Track:** Mechanistic Taxonomy of Regulatory Pathogenicity

---

## Overview

21 ARCHCODE cases were classified across the five mechanistic classes. Classification is based on existing ARCHCODE data (30,318 variants across 9 loci) and 8 robustness experiments (EXP-001 through EXP-008).

---

## Distribution by Class

| Class | N Cases | Key Examples | Confidence |
|:------|:-------:|:-------------|:-----------|
| **A: Activity-Driven** | 1 | HBB Q3 (75 variants: VEP+, ARCHCODE−) | MEDIUM |
| **B: Architecture-Driven** | 8 | HBB Q2b (25 var), MPRA null, CRISPRi null, ablation, ARS | HIGH (HBB), LOW (BRCA1/TP53) |
| **C: Mixed** | 1 | HBB Q1 concordant (270 variants) | MEDIUM |
| **D: Coverage Gap** | 5 | TERT Q2a (34), MLH1 Q2a (72), CFTR Q2a (36), BRCA1 Q2a (53) | HIGH |
| **E: Tissue Mismatch** | 4 | SCN5A null, GJB2 null, LDLR partial, EXP-003 | HIGH |

---

## Class A — Activity-Driven

**1 case, ~75 variants**

| Case | Evidence | Confidence |
|:-----|:---------|:-----------|
| HBB Q3 | VEP > 0.5, LSSIM > 0.95, enhancer dist = 25,138 bp | MEDIUM |

**Interpretation:** These variants are detected by sequence-based tools but show no structural disruption in ARCHCODE. They likely operate through coding/splice mechanisms independent of 3D chromatin architecture. Assigned as activity-driven by exclusion — they sit far from enhancers (25 kb mean) where architecture effects are minimal.

**Caveat:** "Activity-driven" is inferred from VEP positivity + ARCHCODE negativity. Direct MPRA validation would strengthen this assignment.

---

## Class B — Architecture-Driven

**8 cases, core finding of ARCHCODE**

### High Confidence

| Case | N Variants | Key Evidence |
|:-----|:----------:|:-------------|
| HBB Q2b | 25 | LSSIM < 0.95, VEP low, enhancer 434 bp, tissue match 1.0, p = 2.51e-31 |
| MPRA null for Q2b | — | Plasmid assay blind to 3D effects; null confirms architecture mechanism |
| CRISPRi null for Q2b | — | K562 fetal globin ≠ adult HBB; 0/25 Q2b in Gasperini screen |
| EXP-001 ablation | — | ARCHCODE AUC 0.6381 > nearest-gene 0.5266; architecture adds discriminative power |

### Low Confidence (tentative)

| Case | N Variants | Issue |
|:-----|:----------:|:------|
| BRCA1 Q2b | 26 | Threshold-proximal LSSIM (0.942-0.947), AF 40-50%, precision 3.8% |
| TP53 Q2b | 2 | Only 2 variants, insufficient for classification |
| TERT Q2b | 1 | Single variant, partial tissue match |

**Key insight:** HBB Q2b is the **canonical architecture-driven class**. BRCA1/TP53 Q2b assignments need additional evidence (tissue-matched Hi-C or CRISPR validation).

---

## Class C — Mixed

**1 case, ~270 variants**

| Case | Evidence | Confidence |
|:-----|:---------|:-----------|
| HBB Q1 concordant | VEP > 0.5 AND LSSIM < 0.95, tissue match 1.0 | MEDIUM |

**Interpretation:** Both sequence-based tools and ARCHCODE detect these variants. They may disrupt both element activity (coding/splice effect) AND chromatin contact architecture. Alternatively, the co-occurrence may be coincidental — a coding variant near an enhancer could score high on both axes independently.

**What would strengthen this:** Allele-specific Hi-C in patient cells showing both expression change AND contact disruption for the same variant.

---

## Class D — Coverage Gap

**5 cases, ~207 variants total**

| Case | N Variants | Gap Type | ARCHCODE Signal |
|:-----|:----------:|:---------|:----------------|
| TERT Q2a | 34 | VEP = -1 (non-coding) | LSSIM variable, AUC 0.8405 |
| MLH1 Q2a | 72 | VEP = -1 (100% nc frameshift) | Moderate signal |
| BRCA1 Q2a | 53 | VEP = -1 (52 nc frameshift) | Weak signal |
| CFTR Q2a | 36 | VEP = -1 (35 nc frameshift) | Weak + tissue mismatch |
| LDLR Q2a | 10 | VEP = -1 (10 nc frameshift) | Weak + tissue mismatch |

**Key insight:** Coverage gap is the **dominant Q2 mechanism** (207/261 = 79.3%). These variants are not "VEP disagrees" but "VEP cannot score." ARCHCODE provides complementary coverage for this class, though signal strength varies by tissue match.

**Subcategories:**
- **D-pure:** VEP gap + ARCHCODE neutral (variant unscored by all tools)
- **D+B overlap:** VEP gap + ARCHCODE positive (architecture signal in VEP-blind region)

---

## Class E — Tissue-Mismatch Artifact

**4 cases, diagnostic**

| Case | Evidence | Confidence |
|:-----|:---------|:-----------|
| SCN5A null | 0 Q2 variants, cardiac tissue, K562 mismatch | HIGH |
| GJB2 null | 0 Q2 variants, cochlear tissue, K562 mismatch | HIGH |
| LDLR partial | 0 Q2b, 10 Q2a, hepatic tissue, K562 mismatch | MEDIUM |
| EXP-003 diagnostic | Matched delta = 0.00357, mismatch delta = 5e-6 | HIGH |

**Key insight:** Tissue mismatch creates a **systematic absence of signal**, not a false positive. The danger is *interpreting* this absence as evidence of no architecture-driven effect. These loci may have architecture-driven pathogenicity in their native tissue that K562-based ARCHCODE cannot detect.

**EXP-003 quantification:**
- HBB|HBB (matched): delta = 0.00357 (significant, p = 4.66e-72)
- HBB|LDLR (mismatch): delta = 5.04e-06 (effectively zero)
- HBB|TP53 (mismatch): delta = -0.01168 (inverted — nonsensical)

---

## Cross-Class Patterns

### 1. Enhancer Proximity Gradient

| Class | Mean Enhancer Distance | N |
|:------|:----------------------:|:---:|
| B (Architecture) | 434 bp | 54 |
| D (Coverage Gap) | 668 bp | 207 |
| A (Activity) | 25,138 bp | 75 |

Architecture-driven variants cluster near enhancers (58× closer than activity-driven).

### 2. Tissue Specificity Gradient

| Class | Tissue Match Correlation | Evidence |
|:------|:------------------------:|:---------|
| B (Architecture) | rho = 0.840, p = 0.0046 | Strongest tissue dependence |
| E (Tissue Mismatch) | Definitional | Signal collapses in wrong tissue |
| A (Activity) | N/A | Not tissue-dependent in ARCHCODE |
| D (Coverage Gap) | Moderate | Some D variants in mismatched loci |

### 3. Tool Orthogonality

Architecture-driven class shows near-zero mutual information with sequence tools:
- NMI(ARCHCODE, CADD) = 0.024
- NMI(ARCHCODE, VEP) = 0.101
- MaveDB SGE r = -0.045

This orthogonality is the **quantitative foundation** for claiming ARCHCODE captures an independent mechanistic axis.

---

## What's Missing (Gaps for Future Work)

1. **No direct MPRA data for Q2b variants** — would confirm activity-driven null
2. **No tissue-matched Hi-C for HBB Q2b** — would confirm contact disruption
3. **No ARCHCODE in native tissues** for SCN5A (cardiac), GJB2 (cochlear), CFTR (lung)
4. **Mixed class (C) is inferential** — needs dual-readout experiments
5. **ARS interaction with taxonomy** not yet tested (do fragile loci enrich for Class B?)
6. **Only 9 loci** — taxonomy generalizability to genome-wide scale unknown

---

## Files

- Source: `analysis/taxonomy_assignment_table.csv` (21 cases)
- Taxonomy: `docs/regulatory_pathogenicity_taxonomy.md` (5 class definitions)
- Tool matrix: `docs/tool_mechanism_matrix.md` (12 tools × 5 classes)
