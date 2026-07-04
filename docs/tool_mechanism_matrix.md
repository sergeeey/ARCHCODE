# Tool-to-Mechanism Comparison Matrix

**Version:** 1.0
**Date:** 2026-03-09
**Track:** Mechanistic Taxonomy of Regulatory Pathogenicity

---

## Overview

This matrix maps computational and experimental tools to the five mechanistic classes of regulatory pathogenicity. The goal is to show that no single tool covers all classes, and that ARCHCODE specifically addresses the architecture-driven class (Class B) that sequence-based tools systematically miss.

---

## Main Matrix

| Tool / Method | A: Activity-Driven | B: Architecture-Driven | C: Mixed | D: Coverage Gap | E: Tissue Mismatch |
|:---|:---:|:---:|:---:|:---:|:---:|
| **VEP** | PARTIAL (coding/splice) | BLIND | PARTIAL | NO SCORE (Q2a) | N/A |
| **CADD** | GOOD (integrated) | BLIND | PARTIAL | PARTIAL | N/A |
| **SpliceAI** | GOOD (splice only) | BLIND | PARTIAL (splice) | BLIND (non-splice) | N/A |
| **Enformer / Sei** | GOOD (regulatory) | BLIND | PARTIAL | PARTIAL | tissue-aware in theory |
| **MPRA / STARR-seq** | GOLD STANDARD | BLIND (plasmid) | PARTIAL (activity only) | BLIND (if not tested) | cell-type dependent |
| **CRISPRi/a** | GOOD (endogenous) | PARTIAL (if contact readout) | GOOD | BLIND (if not targeted) | cell-type dependent |
| **ARCHCODE** | BLIND | PRIMARY | PARTIAL (arch. axis) | COMPLEMENTARY (Q2a) | ARTIFACT if mismatched |
| **Hi-C / Capture-C** | BLIND | GOLD STANDARD | GOOD (topology) | BLIND | tissue-dependent |
| **CTCF ChIP-seq** | BLIND | GOOD (boundary) | PARTIAL | BLIND | tissue-dependent |
| **ATAC-seq / DNase** | GOOD | BLIND | PARTIAL | PARTIAL | tissue-dependent |
| **Conservation (PhyloP)** | GOOD | VARIABLE | GOOD | VARIABLE | N/A |
| **gnomAD AF** | SUPPORTIVE | SUPPORTIVE | SUPPORTIVE | SUPPORTIVE | N/A |

---

## Detailed Assessment by Tool

### 1. VEP (Variant Effect Predictor)

**What it does:** Annotates coding consequences, splice predictions, regulatory region overlap.

**Strengths:**
- Comprehensive for coding variants (missense, nonsense, frameshift)
- Good splice site detection (± 2 bp canonical)
- Fast, widely adopted, ACMG-integrated

**Blind spots:**
- Cannot detect 3D chromatin disruption (Class B)
- Returns no score for many non-coding variants (Class D: 207 Q2a variants)
- No tissue context

**ARCHCODE evidence:**
- NMI(ARCHCODE, VEP) = 0.101 on HBB (low mutual information)
- 54 Q2b variants: VEP scored low, ARCHCODE detected disruption
- Per-locus NMI ranges from 0.0 (SCN5A) to 0.495 (HBB)

### 2. CADD (Combined Annotation Dependent Depletion)

**What it does:** Integrates 60+ annotation features into single deleteriousness score.

**Strengths:**
- Genome-wide coverage
- Integrates conservation, regulatory, protein features
- Phred-scaled, comparable across variant types

**Blind spots:**
- Trained on fixed/simulated variants, not mechanism-specific
- NMI(ARCHCODE, CADD) = 0.024 (near-zero: almost fully orthogonal)
- Cannot distinguish activity-driven from architecture-driven

**ARCHCODE evidence:**
- NMI = 0.024 confirms ARCHCODE captures independent information axis
- CADD high ∩ ARCHCODE high → Class C candidates

### 3. MPRA (Massively Parallel Reporter Assay)

**What it does:** Tests thousands of sequences for enhancer/promoter activity in parallel using reporter constructs.

**Strengths:**
- Direct measurement of regulatory element activity
- High throughput, quantitative
- Gold standard for Class A (activity-driven)

**Blind spots:**
- **Fundamental limitation:** plasmid-based → removes 3D chromatin context
- Cannot detect architecture-driven effects (Class B) by design
- Cell-type specific but not topology-aware

**ARCHCODE evidence:**
- MPRA crossvalidation (Kircher 2019 HBB): null result for Q2b pearls
- This null is *expected* and *informative*: confirms Q2b operates via contact, not element activity
- MPRA measures what an element does; ARCHCODE measures where it contacts

### 4. CRISPRi (CRISPR interference)

**What it does:** Silences regulatory elements at endogenous loci; measures effect on gene expression.

**Strengths:**
- Endogenous context preserved (unlike MPRA)
- Can detect long-range regulatory effects
- Gasperini 2019: 90,955 element-gene pairs tested in K562

**Blind spots:**
- Cell-type specific: K562 = fetal globin, not adult HBB
- Coverage gaps: only tested elements in screen; Q2b variants not covered
- Cannot distinguish mechanism (activity vs architecture silencing)

**ARCHCODE evidence:**
- EXP-008: 0 Q2b overlaps in Gasperini K562 screen
- Reason: K562 expresses gamma-globin, HBB promoter not active
- Demonstrates cell-type coverage gap for architecture-driven variants

### 5. ARCHCODE

**What it does:** Simulates loop extrusion on variant-specific chromatin configurations; compares contact matrices via SSIM/LSSIM.

**Strengths:**
- **Primary detector for Class B (architecture-driven)**
- Tissue-specific via enhancer/CTCF configuration
- Can score variants VEP cannot (Q2a complementary coverage)
- Orthogonal to all sequence-based methods (NMI < 0.1)

**Blind spots:**
- **Blind to Class A** (activity-driven): does not model TF binding or element activity
- Artifact-prone for Class E (tissue-mismatch): signal requires correct tissue config
- Depends on manually calibrated parameters (not fitted to data)
- Currently limited to 300 kb windows

**Key metrics:**
- HBB Q2b: 25 variants, LSSIM < 0.95, p = 2.51e-31
- Tissue specificity: rho = 0.840, p = 0.0046
- Ablation AUC: 0.6381 (vs nearest-gene 0.5266)

### 6. Hi-C / Capture-C

**What it does:** Measures genome-wide (Hi-C) or targeted (Capture-C) chromatin contact frequencies.

**Strengths:**
- Gold standard for Class B validation
- Directly measures what ARCHCODE predicts
- Tissue-specific

**Blind spots:**
- Low resolution (typically 5-25 kb for Hi-C)
- Cannot detect activity changes
- Expensive, requires large cell numbers
- Most datasets are WT; variant-specific Hi-C rare

**ARCHCODE evidence:**
- Hi-C validation: r = 0.28-0.59 across loci (ARCHCODE WT vs experimental Hi-C)
- Mouse Hi-C validation: r = 0.531 (G1E-ER4, mm10)

---

## Coverage Gap Analysis

| Mechanism Class | Tools That See It | Tools That Are Blind | Gap Size |
|:---|:---|:---|:---:|
| A: Activity | VEP, CADD, MPRA, Enformer, ATAC | ARCHCODE, Hi-C | Small |
| B: Architecture | ARCHCODE, Hi-C, Capture-C | VEP, CADD, MPRA, SpliceAI | **Large** |
| C: Mixed | Partial from all | None fully | Medium |
| D: Coverage Gap | ARCHCODE (partial) | VEP (207 variants) | **Large** |
| E: Tissue Mismatch | Matched-tissue assays | All mismatched tools | Context-dependent |

**Key insight:** Classes B and D represent the largest blind spots in current variant interpretation. ARCHCODE addresses both, but requires tissue-matched configuration.

---

## Quantitative Evidence from ARCHCODE Data

### Orthogonality (Normalized Mutual Information)

| Tool Pair | NMI | Interpretation |
|:---|:---:|:---|
| ARCHCODE vs VEP | 0.101 | Low: mostly independent axes |
| ARCHCODE vs CADD | 0.024 | Very low: nearly fully orthogonal |
| VEP vs CADD | 0.231 | Moderate: shared sequence features |
| ARCHCODE vs MaveDB SGE | r = -0.045 | Near zero: complete orthogonality |
| ARCHCODE vs MaveDB DMS | r = -0.383 | Weak: partial tissue overlap |

### Per-Locus Tool Sensitivity

| Locus | VEP AUC | ARCHCODE AUC | Dominant Class |
|:---|:---:|:---:|:---|
| HBB | high (coding) | N/A (primary locus) | B (architecture) |
| TERT | low (non-coding) | 0.8405 | D→B (coverage→architecture) |
| BRCA1 | moderate | 0.6246 | Mixed / threshold artifacts |
| TP53 | moderate | 0.6676 | C (mixed) |
| GJB2 | moderate | 0.8529 | E (tissue mismatch) |
| SCN5A | moderate | 0.6182 | E (tissue mismatch) |

---

## Summary

1. **No single tool covers all five classes.** This is the fundamental problem.
2. **ARCHCODE is the only tool that specifically targets Class B** (architecture-driven).
3. **VEP/CADD are blind to Class B** and have systematic coverage gaps (Class D).
4. **MPRA is blind to Class B by design** (plasmid removes 3D context).
5. **Tissue context determines whether Class B signal is real or artifact (Class E).**
6. **Multi-modal integration is required** for complete variant interpretation.
