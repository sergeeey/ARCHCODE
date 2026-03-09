# Related Work: Literature for Mechanistic Taxonomy Paper

**Date:** 2026-03-09
**Source:** Web search agent, all DOIs verified
**Purpose:** Related Work / Introduction section for the taxonomy position paper

---

## Three Thematic Pillars

### Pillar 1: Mechanism taxonomy exists but is incomplete

The closest existing taxonomy lacks the 3D genome dimension that our work adds.

### Pillar 2: 3D genome as a distinct pathogenic axis

Chromatin architecture creates tissue-dependent pathogenic mechanisms not captured by sequence-level scores.

### Pillar 3: Single-score approaches are demonstrably insufficient

Multiple lines of evidence — from deep learning benchmarks to multi-modal models — converge on the need for mechanism-aware interpretation.

---

## Papers

### 1. Cheng, Bohaczuk & Stergachis (2024) — MOST DIRECTLY RELEVANT [Pillar 1]

**Citation:** Cheng YHH, Bohaczuk SC, Stergachis AB. "Functional categorization of gene regulatory variants that cause Mendelian conditions." *Human Genetics* 143(4):559-605, 2024.
**DOI:** 10.1007/s00439-023-02639-w | **PMID:** 38436667 | [VERIFIED]

**Summary:** Proposes a three-category functional taxonomy for non-coding regulatory variants: (1) non-modular loss-of-expression (LOE), (2) modular loss-of-expression (mLOE) — tissue/stage-specific, and (3) gain-of-ectopic-expression (GOE). Reviews hundreds of pathogenic non-coding variants across Mendelian conditions.

**Relation:** Their LOE/mLOE/GOE taxonomy is complementary to but orthogonal from ours. They classify by *expression outcome*; we classify by *mechanism of disruption* (activity vs architecture). Our framework extends theirs by adding the 3D genome dimension they do not address. **Key citation for Introduction: "existing taxonomies focus on expression outcomes, not pathogenic mechanisms."**

---

### 2. Sreenivasan, Yumiceba & Spielmann (2025) [Pillar 2]

**Citation:** Sreenivasan VKA, Yumiceba V, Spielmann M. "Structural variants in the 3D genome as drivers of disease." *Nature Reviews Genetics* 26(11):742-760, 2025.
**DOI:** 10.1038/s41576-025-00862-x | **PMID:** 40588575 | [VERIFIED]

**Summary:** Comprehensive review of how structural variants disrupt 3D genome organization (TADs, loops, compartments) to cause disease. Covers position effects, enhancer hijacking, boundary disruption, and clinical consequences.

**Relation:** Establishes field consensus that 3D genome architecture is a distinct pathogenic dimension. Supports our Class B definition. **Key citation for "Why architecture-driven is a real class."**

---

### 3. Avsec et al. (2026) — AlphaGenome [Pillar 3]

**Citation:** Avsec Z, Latysheva N, Cheng J, et al. "Advancing regulatory variant effect prediction with AlphaGenome." *Nature* 649(8099):1206-1218, 2026.
**DOI:** 10.1038/s41586-025-10014-0 | [VERIFIED]

**Summary:** Unified DNA sequence model predicting thousands of functional genomic tracks. Explicitly states "specialized models alone are insufficient for capturing the diverse molecular consequences of variants across modalities."

**Relation:** Supports multi-modal argument. AlphaGenome is multi-output but doesn't classify *which mechanism* is disrupted — our taxonomy provides the interpretive layer. **Key citation for "even the most powerful models need mechanism-aware interpretation."**

---

### 4. Kim et al. (2024) — CTCF boundary dissection [Pillar 2]

**Citation:** Kim KL, Rahme GJ, Goel VY, El Farran CA, Hansen AS, Bernstein BE. "Dissection of a CTCF topological boundary uncovers principles of enhancer-oncogene regulation." *Molecular Cell* 84(7):1365-1376.e7, 2024.
**DOI:** 10.1016/j.molcel.2024.02.007 | **PMC:** 10997458 | [VERIFIED]

**Summary:** CTCF insulator boundaries operate through redundant sites (minimum 4 must be disrupted). Linear scaling between enhancer-promoter contact frequency and transcription (r=0.97). DNA hypermethylation disrupts multiple CTCF motifs in cancer.

**Relation:** Mechanistic evidence for Class B (boundary disruption). Shows single-variant effects depend on boundary redundancy context — single-score prediction insufficient without structural context.

---

### 5. Chakraborty et al. (2023) — Enhancers bypassing CTCF [Pillar 2]

**Citation:** Chakraborty S, Kopitchinski N, Zuo Z, et al. "Enhancer-promoter interactions can bypass CTCF-mediated boundaries and contribute to phenotypic robustness." *Nature Genetics* 55(2):280-290, 2023.
**DOI:** 10.1038/s41588-022-01295-6 | **PMC:** 10758292 | [VERIFIED]

**Summary:** Dense enhancer clusters can overcome CTCF insulation barriers, but tissue-dependently — neural tissues maintain cross-boundary contacts while foregut tissues cannot.

**Relation:** Directly relevant to tissue-dependent structural disruption (Class E). Challenges simple boundary-disruption models. **Key citation for "identical structural perturbations have different consequences depending on tissue context."**

---

### 6. Hollingsworth et al. (2025) — Enhancer poising [Pillar 2]

**Citation:** Hollingsworth EW, Chen Z, Chen CX, Jacinto SH, Liu TA, Kvon EZ. "Enhancer Poising Enables Pathogenic Gene Activation by Noncoding Variants." *bioRxiv* preprint, 2025.
**DOI:** 10.1101/2025.06.20.660819 | **PMID:** 40667262 | [VERIFIED]

**Summary:** Tissue-specific enhancer poising creates vulnerability to non-coding mutations. Only tissues with poised chromatin states are affected by gain-of-function enhancer variants.

**Relation:** Explains WHY non-coding pathogenicity is tissue-dependent. Supports Class E (tissue-mismatch) framing.

---

### 7. Sanchez-Gaya & Rada-Iglesias (2023) — POSTRE [Pillar 1]

**Citation:** Sanchez-Gaya V, Rada-Iglesias A. "POSTRE: a tool to predict the pathological effects of human structural variants." *Nucleic Acids Research* 51(9):e54, 2023.
**DOI:** 10.1093/nar/gkad225 | **PMID:** 36999617 | [VERIFIED]

**Summary:** Computational tool predicting SV pathogenicity by modeling LOF (enhancer disconnection) and GOF (enhancer hijacking) mechanisms in the context of TADs.

**Relation:** Implements binary mechanism classification (LOF vs GOF) that our taxonomy extends to five classes. Demonstrates feasibility of mechanism-aware prediction.

---

### 8. Chin, Gardell & Corces (2024) [Pillar 3]

**Citation:** Chin IM, Gardell ZA, Corces MR. "Decoding polygenic diseases: Advances in noncoding variant prioritization and validation." *Trends in Cell Biology* 34(6):465-483, 2024.
**DOI:** 10.1016/j.tcb.2024.03.005 | **PMID:** 38719704 | [VERIFIED]

**Summary:** Reviews GWAS-to-causal-variant workflow, emphasizing "noncoding variants can exert their effects via multiple molecular mechanisms." Regulatory elements have "exquisitely cell type-specific usage."

**Relation:** Supports multi-mechanism, multi-modal argument. Their observation that most validation methods "focus narrowly on gene regulatory activity" aligns with our blind-spot argument.

---

### 9. Benegas, Eraslan & Song (2025) [Pillar 3]

**Citation:** Benegas G, Eraslan G, Song YS. "Benchmarking DNA Sequence Models for Causal Regulatory Variant Prediction in Human Genetics." *bioRxiv* preprint, 2025.
**DOI:** 10.1101/2025.02.11.637758 | [VERIFIED]

**Summary:** Systematic benchmark showing "distal non-exonic variants for complex traits are the hardest class." Model ensembling yields consistent improvements, implying no single model captures all variant classes.

**Relation:** Empirical evidence that single-score approaches fail differentially across variant classes. Supports need for mechanism-aware interpretation.

---

### 10. Wang et al. (2024) — Deep learning review [Pillar 3]

**Citation:** Wang X, Li F, Zhang Y, et al. "Deep learning approaches for non-coding genetic variant effect prediction: current progress and future prospects." *Briefings in Bioinformatics* 25(5):bbae446, 2024.
**DOI:** 10.1093/bib/bbae446 | **PMC:** 11401448 | [VERIFIED]

**Summary:** Comprehensive review identifying key limitations: single-sequence reference bias, missing post-transcriptional mechanisms, and long-range interaction challenges.

**Relation:** Documents systematic blind spots in current approaches, supporting mechanism-aware taxonomy.

---

## How to Use in the Paper

### Introduction (2-3 key citations):
- Cheng et al. 2024 → "existing taxonomies classify by expression outcome, not pathogenic mechanism"
- Chin et al. 2024 → "noncoding variants exert effects via multiple molecular mechanisms"
- Avsec et al. 2026 → "even multi-modal models need mechanism-aware interpretation"

### Section 2 "Why Current Tools Conflate Mechanisms" (3-4 citations):
- Benegas et al. 2025 → benchmark evidence that single scores fail differentially
- Wang et al. 2024 → systematic blind spots in deep learning approaches
- POSTRE (Sanchez-Gaya 2023) → precedent for mechanism-aware prediction

### Section 3 "Taxonomy" — Class B support (3-4 citations):
- Sreenivasan et al. 2025 → 3D genome as distinct pathogenic axis (NatRevGen consensus)
- Kim et al. 2024 → CTCF boundary redundancy and dose-dependent disruption
- Chakraborty et al. 2023 → tissue-dependent boundary bypass

### Section 3 — Class E support (1-2 citations):
- Chakraborty et al. 2023 → tissue-dependent structural effects
- Hollingsworth et al. 2025 → enhancer poising as tissue-specificity mechanism

---

## Summary Statistics

- **10 papers verified** (8 published, 2 bioRxiv preprints)
- **Journals:** Nature (1), NatRevGen (1), NatGen (1), MolCell (1), HumGen (1), NAR (1), TrendsCellBiol (1), BriefBioinform (1), bioRxiv (2)
- **Date range:** 2023-2026
- **All DOIs confirmed via web search**
