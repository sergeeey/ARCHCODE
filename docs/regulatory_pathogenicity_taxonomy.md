# Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy

**Version:** 1.0
**Date:** 2026-03-09
**Track:** Mechanistic Taxonomy of Regulatory Pathogenicity
**Status:** DRAFT — Phase 1 formalization

---

## Motivation

Current variant interpretation tools assign a single pathogenicity score along a single axis — typically sequence conservation or predicted functional impact. This conflates mechanistically distinct classes of regulatory effect:

- A variant that disrupts TF binding at an enhancer (activity-driven)
- A variant that disrupts a CTCF insulator boundary (architecture-driven)
- A variant in a region no tool can score (coverage gap)

These require different experimental validations, respond to different therapeutic strategies, and are detected by different computational approaches. Treating them as one class leads to systematic blind spots.

**Central thesis:**
> Regulatory pathogenicity is mechanistically heterogeneous, and current tools systematically conflate distinct classes of effect. A mechanistic decomposition into at least five classes is needed for accurate variant interpretation.

---

## The Five Classes

### Class A — Activity-Driven

**Definition:**
The variant alters the *intrinsic regulatory activity* of a cis-regulatory element — enhancer strength, promoter output, TF binding affinity, chromatin accessibility — without necessarily changing 3D chromatin architecture.

**Typical evidence:**
- MPRA signal (reporter assay positive)
- Altered TF binding motif (JASPAR/HOCOMOCO match disrupted)
- Changed chromatin accessibility (ATAC-seq, DNase-seq)
- eQTL association
- Sequence-based predictor positive (DeepSEA, Enformer, Sei)

**Typical failure mode:**
- Assumes cis-element operates independently of 3D context
- Misses cases where element is active but physically disconnected from target
- Plasmid-based assays (MPRA) cannot capture 3D topology effects

**Relevant tools:**
- PRIMARY: MPRA, STARR-seq, sequence-based deep learning (Enformer, Sei)
- SECONDARY: VEP, CADD (partial), SpliceAI (splice-proximal)
- BLIND: ARCHCODE, Hi-C-based methods

**Best validating experiment:**
- MPRA / STARR-seq (direct activity measurement)
- CRISPRi/a at endogenous locus with RNA readout

**ARCHCODE behavior:** Typically neutral (LSSIM ≈ 1.0). The variant changes what the element does, not where it contacts.

---

### Class B — Architecture-Driven

**Definition:**
The variant alters the *3D chromatin contact landscape* — loop extrusion outcome, insulator function, enhancer-promoter spatial proximity, TAD boundary integrity — without necessarily changing intrinsic element activity.

**Typical evidence:**
- ARCHCODE structural disruption (LSSIM < 0.95)
- Enhancer proximity < 1 kb (variant near enhancer-promoter contact zone)
- Tissue-matched context required (signal disappears in wrong tissue)
- Hi-C / Capture-C contact change
- CTCF binding site disruption

**Typical failure mode:**
- Sequence-based tools see no motif disruption → score as benign
- MPRA reports no activity change (because the element IS active; it's the routing that breaks)
- Requires tissue-matched chromatin context that most databases lack

**Relevant tools:**
- PRIMARY: ARCHCODE, Hi-C differential, Capture-C
- SECONDARY: CTCF ChIP-seq (boundary variants)
- BLIND: MPRA, VEP, CADD, sequence models

**Best validating experiment:**
- Capture Hi-C in disease-relevant cell type (HUDEP-2 for HBB)
- 4C-seq from target promoter
- CRISPR base editing + contact assay

**ARCHCODE behavior:** Strong signal (LSSIM << 0.95). This is ARCHCODE's primary detection class.

**Canonical ARCHCODE examples:**
- HBB Q2b variants (25 variants, mean LSSIM = 0.927, enhancer dist = 434 bp)
- Promoter-proximal variants that disrupt LCR-HBB contact geometry

---

### Class C — Mixed (Activity + Architecture)

**Definition:**
The variant simultaneously affects both intrinsic regulatory element activity AND 3D chromatin contact topology. These are potentially the most severely pathogenic variants because they disrupt multiple axes.

**Typical evidence:**
- MPRA/STARR-seq positive AND ARCHCODE positive
- Sequence model predicts functional impact AND contact matrix shows disruption
- Often at regulatory element boundaries or CTCF-adjacent enhancers
- Can involve structural variants (deletions, inversions) that remove elements AND change topology

**Typical failure mode:**
- Each single-axis tool captures only partial effect
- Total pathogenic load underestimated by any one method
- Attribution problem: is the disease caused by activity loss or contact disruption?

**Relevant tools:**
- ALL tools partially informative
- No single tool captures full effect
- Multi-modal integration required

**Best validating experiment:**
- MPRA + Capture Hi-C in same cell type
- Allele-specific Hi-C in heterozygous patient cells
- CRISPR knock-in + both RNA and contact readout

**ARCHCODE behavior:** Positive signal, but ARCHCODE captures only the architecture axis. The activity component requires orthogonal measurement.

---

### Class D — Coverage / Annotation Gap

**Definition:**
The variant falls in a region where current sequence-based tools *cannot assign a score* — not because they disagree, but because the variant type or genomic context is outside their training data or annotation scope.

**Typical evidence:**
- VEP returns no consequence or "sentinel" value (VEP = -1)
- Non-coding frameshifts in intergenic regions
- Variants in unannotated regulatory elements
- Deep intronic variants far from splice sites

**Typical failure mode:**
- Mistaken for "benign" when actually "unscored"
- Tool absence ≠ biological absence of effect
- Creates false sense of safety in clinical reporting

**Relevant tools:**
- BLIND: VEP, CADD (for certain variant types)
- PARTIAL: ARCHCODE (can score if within simulation window)
- INFORMATIVE: Conservation scores (PhyloP, GERP)

**Best validating experiment:**
- RNA-seq for splicing effects
- ATAC-seq for accessibility
- Any functional assay in appropriate cell type

**ARCHCODE behavior:** Variable. ARCHCODE can sometimes score variants that VEP cannot (207 Q2a variants in ARCHCODE data), providing complementary coverage.

**Canonical ARCHCODE examples:**
- Q2a variants (207 total): VEP = -1 but ARCHCODE detects structural disruption
- TERT: 34/35 Q2 variants are Q2a (coverage gap dominant)
- MLH1: all 72 Q2 variants are Q2a

---

### Class E — Tissue-Mismatch Artifact

**Definition:**
An apparent pathogenic signal that arises from applying a tissue-mismatched regulatory context. The variant appears structurally disruptive in one tissue's enhancer landscape but shows no effect in the biologically correct tissue.

**Typical evidence:**
- Signal present in one tissue configuration, absent in correct tissue
- Wrong-tissue enhancers create spurious proximity effects
- EXP-003 diagonal pattern: matched tissues show signal, off-diagonal near zero

**Typical failure mode:**
- Accepting wrong-tissue results as generalizable
- Using K562 data for non-erythroid loci without caveat
- Over-interpreting structural signals in universally-expressed genes

**Relevant tools:**
- DIAGNOSTIC: Tissue-mismatch control experiments
- ARCHCODE with matched vs. mismatched enhancer configs
- Cell-type-specific Hi-C / ATAC-seq

**Best validating experiment:**
- Same variant, two tissue contexts (matched vs. mismatched)
- ARCHCODE EXP-003 protocol

**ARCHCODE behavior:** Signal collapses when correct tissue context applied. This class represents a *systematic artifact* that all tissue-specific methods must guard against.

**Canonical ARCHCODE examples:**
- HBB|LDLR mismatch: delta = 5.04e-06 (vs matched HBB|HBB: delta = 0.00357)
- HBB|TP53 mismatch: delta = -0.01168 (inverted, nonsensical)
- GJB2 locus: zero structural signal (cochlear tissue, not K562)
- SCN5A locus: zero Q2b (cardiac tissue, not K562)

---

## Class Signature Matrix

| Feature | A: Activity | B: Architecture | C: Mixed | D: Coverage Gap | E: Tissue Mismatch |
|---------|:-----------:|:---------------:|:--------:|:---------------:|:------------------:|
| MPRA/STARR-seq | + | − | + | ? | variable |
| Sequence model (Enformer) | + | − | + | − | variable |
| VEP/CADD | + | − | + | NO SCORE | variable |
| ARCHCODE (LSSIM) | − | + | + | partial | ARTIFACT |
| Hi-C contact change | − | + | + | ? | tissue-dependent |
| CTCF ChIP disruption | − | +(subset) | +(subset) | ? | tissue-dependent |
| Enhancer proximity | not required | required | required | N/A | misleading |
| Tissue specificity | moderate | strong | strong | N/A | diagnostic |
| Conservation (PhyloP) | often high | variable | high | variable | N/A |

**Legend:** + = typically detected, − = typically missed, ? = unknown/variable

---

## Decision Rules for Class Assignment

```
IF VEP = -1 (no score):
    → Class D (Coverage Gap)
    IF ARCHCODE LSSIM < 0.95:
        → Class D with architecture signal (D+B overlap)

IF MPRA+ AND ARCHCODE−:
    → Class A (Activity-Driven)

IF MPRA− AND ARCHCODE+ AND tissue_matched:
    → Class B (Architecture-Driven)

IF MPRA+ AND ARCHCODE+:
    → Class C (Mixed)

IF signal_collapses_in_wrong_tissue:
    → Class E (Tissue-Mismatch Artifact)

IF ARCHCODE+ AND NOT tissue_matched:
    → Cannot distinguish B from E without matched-tissue data
```

---

## Implications for Clinical Variant Interpretation

1. **Single-score approaches are insufficient.** A variant scored "benign" by VEP may be architecture-driven pathogenic (Class B). A variant scored "pathogenic" by ARCHCODE in wrong tissue may be artifact (Class E).

2. **Tool selection should be mechanism-aware.** MPRA validates Class A. Capture Hi-C validates Class B. Both are needed for Class C. Neither validates Class D without additional context.

3. **Tissue context is not optional.** Classes B and E are defined by tissue specificity. Tissue-agnostic scoring misclassifies both.

4. **Coverage gaps are not benign calls.** Class D variants (VEP = -1) include 207 ARCHCODE-detected structural disruptions. "No score" ≠ "no effect."

---

## Relationship to ARCHCODE

ARCHCODE is positioned as the **primary engine for Class B (architecture-driven)** detection:

| ARCHCODE Role | Class | Evidence |
|---------------|-------|----------|
| Primary detector | B (Architecture) | 25 HBB Q2b, LSSIM < 0.95, p = 2.51e-31 |
| Complementary coverage | D (Coverage Gap) | 207 Q2a scored by ARCHCODE, VEP blind |
| Partial signal | C (Mixed) | Architecture axis only; needs MPRA for activity |
| Artifact source | E (Tissue Mismatch) | EXP-003 demonstrates collapse |
| Blind | A (Activity) | By design: ARCHCODE does not model TF binding |

---

## Files Referenced

- `analysis/DISCORDANCE_REPORT_v2.md` — Q2a/Q2b split analysis
- `analysis/per_locus_verdict.csv` — per-locus classification
- `analysis/tissue_mismatch_controls_summary.json` — EXP-003 results
- `analysis/gasperini_benchmark_summary.json` — CRISPRi coverage gaps
- `analysis/ablation_study_summary.json` — EXP-001 model comparison
- `analysis/contact_metric_robustness_summary.json` — EXP-006 metric comparison
