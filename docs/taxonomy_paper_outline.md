# Taxonomy Paper Outline

**Track:** Regulatory Pathogenicity Is Mechanistically Heterogeneous
**Date:** 2026-03-09
**Status:** DRAFT — Phase 5 planning

---

## Title Options

1. **Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots**
2. **Beyond Single-Score Pathogenicity: A Mechanistic Decomposition of Regulatory Variant Effects**
3. **Five Classes of Regulatory Pathogenicity: Why No Single Tool Can Interpret Non-Coding Variants**
4. **The Architecture Axis: How 3D Chromatin Topology Creates a Systematic Blind Spot in Variant Interpretation**

**Recommended:** Option 1 — broadest, positions the taxonomy as the contribution (not ARCHCODE).

---

## Abstract Skeleton

**Background:** Current variant interpretation tools assign pathogenicity along a single axis — typically sequence conservation or predicted functional impact. This conflation obscures mechanistically distinct classes of regulatory effect that require different experimental validations and computational approaches.

**Results:** We propose a five-class taxonomy of regulatory pathogenicity: (A) activity-driven, where variants alter enhancer/promoter function detectable by reporter assays; (B) architecture-driven, where variants disrupt 3D chromatin contact topology detectable by structural simulation; (C) mixed, combining both mechanisms; (D) coverage gap, where current tools lack scoring capability; and (E) tissue-mismatch artifact, where apparent signals reflect incorrect tissue context. Using ARCHCODE, a loop-extrusion-based structural pathogenicity engine, we assign [N] variants across 9 genomic loci to these classes. We show that 54 architecture-driven variants (Class B) are systematically missed by VEP, CADD, and MPRA (NMI < 0.1), cluster within 434 bp of tissue-matched enhancers (p = 2.51e-31), and represent the highest-priority candidates for experimental validation. An additional 207 coverage-gap variants (Class D) are unscored by VEP but detectable by structural simulation.

**Conclusions:** Single-axis scoring is an inadequate abstraction for regulatory variant interpretation. Mechanistic decomposition reveals that architecture-driven pathogenicity — representing [X]% of structural blind spots — requires dedicated 3D chromatin modeling that no current sequence-based tool provides. We propose that variant interpretation frameworks should explicitly assign mechanistic class before scoring, enabling targeted experimental validation and reducing systematic blind spots.

**Key numbers to fill:** [N] total variants classified, [X]% architecture-driven fraction.

---

## Section Outline

### 1. Introduction: The Problem with Single-Score Pathogenicity

**Length:** ~800 words

**Key points:**
- Variant interpretation relies on single-axis scores (VEP, CADD, REVEL)
- Non-coding variants are particularly problematic: most tools trained on coding effects
- Growing evidence that regulatory pathogenicity operates through distinct mechanisms
- Current frameworks (ACMG, ClinGen) do not distinguish mechanistic classes
- Consequence: systematic blind spots where entire classes of pathogenic variants are missed

**What NOT to say:**
- NOT "ARCHCODE is better than VEP"
- NOT "3D is more important than sequence"
- INSTEAD: "Different mechanisms require different tools"

### 2. Why Current Tools Conflate Mechanisms

**Length:** ~1000 words

**Key points:**
- VEP/CADD architecture: trained on coding consequences, conservation, regulatory overlap
- What they capture: TF motif disruption, splice effects, conservation depletion (Class A)
- What they miss: chromatin contact topology, enhancer-promoter spatial proximity (Class B)
- MPRA: gold standard for activity but fundamentally blind to 3D (plasmid removes topology)
- CRISPRi: endogenous but cell-type limited (Gasperini K562 ≠ all tissues)
- Quantitative evidence: NMI(ARCHCODE, VEP) = 0.101, NMI(ARCHCODE, CADD) = 0.024

**Figures:** Figure 3 (tool-mechanism matrix)

### 3. A Taxonomy of Regulatory Pathogenicity

**Length:** ~1500 words

**Key points:**
- Formal definitions of five classes (A through E)
- Signature evidence profiles for each class
- Decision rules for class assignment
- Worked examples from ARCHCODE data

**Figures:** Figure 1 (taxonomy map)

**Subsections:**
- 3.1 Class A: Activity-Driven
- 3.2 Class B: Architecture-Driven
- 3.3 Class C: Mixed
- 3.4 Class D: Coverage / Annotation Gap
- 3.5 Class E: Tissue-Mismatch Artifact
- 3.6 Decision Rules

### 4. ARCHCODE as the Architecture-Driven Engine

**Length:** ~1200 words

**Key points:**
- Brief ARCHCODE method description (loop extrusion simulation, LSSIM metric)
- ARCHCODE positioned as Class B primary detector, not universal predictor
- Evidence: 25 HBB Q2b variants (architecture-driven canonical class)
- Evidence: MPRA null, CRISPRi null, orthogonality metrics
- Ablation: architecture component adds discriminative power (AUC 0.64 vs 0.53)
- Leave-one-locus-out: mean AUC 0.69, Class B signal generalizes

**Figures:** Figure 2 (ARCHCODE examples by class)

### 5. Case Studies

**Length:** ~1500 words

**Subsections:**

#### 5.1 HBB Q2b: Archetypal Architecture-Driven Pathogenicity
- 25 variants, enhancer proximity 434 bp, LSSIM < 0.95
- VEP scores 0-0.5, MPRA null, CRISPRi no coverage
- Tissue match = 1.0 (K562 erythroid, HBB primary locus)
- Proposed mechanism: LCR-promoter contact disruption via loop extrusion perturbation

#### 5.2 TERT Q2a: Coverage Gap with Architecture Signal
- 34/35 Q2 = Q2a (VEP cannot score)
- ARCHCODE AUC = 0.8405 (best of 4 models)
- Partial tissue match (0.5) — TERT active in K562 but not primary
- Demonstrates ARCHCODE complementary coverage for VEP gaps

#### 5.3 Tissue-Mismatched Loci: SCN5A, GJB2
- Zero structural signal in K562 (wrong tissue)
- EXP-003 diagnostic: matched delta >> mismatch delta
- NOT evidence against architecture-driven pathogenicity in native tissue
- Cautionary tale for all tissue-specific methods

#### 5.4 External Cases (3-5 from literature)
- Architecture-driven: [Lupiáñez 2015, TAD boundary disruption]
- Activity-driven: [SHH ZRS enhancer mutations]
- Mixed: [enhancer hijacking + activity change]
- Each mapped to taxonomy classes

### 6. Contrarian Section: Limitations and Challenges

**Length:** ~800 words

**Key points:**
- Class boundaries may be fuzzy (continuous, not discrete)
- Current evidence for Class B is primarily from HBB (one locus)
- BRCA1/TP53 Q2b may be threshold artifacts, not true Class B
- Tissue-matched ARCHCODE configs exist for only 9 loci
- Mixed class (C) is the hardest to validate experimentally
- Assignment rules are heuristic, not algorithmic

**Honest limitations:**
- We cannot prove that Q2b variants are pathogenic through architecture — only that they are *structurally disruptive* and *undetected by current tools*
- Experimental validation (Capture Hi-C, CRISPR) is required to confirm mechanism
- Taxonomy is a working model, not a final classification

### 7. Experimental Implications

**Length:** ~600 words

**Key points:**
- Class A → validate with MPRA/STARR-seq
- Class B → validate with Capture Hi-C in matched tissue (HUDEP-2 for HBB)
- Class C → dual readout: RNA + contact assay
- Class D → any functional assay to establish baseline
- Class E → matched-tissue replication required

**Priority experiments:**
1. HUDEP-2 Capture Hi-C for top 5 HBB Q2b positions
2. MPRA for same variants (expected null, but confirms activity-driven absence)
3. Tissue-matched ARCHCODE for SCN5A (iPSC-cardiomyocytes)

### 8. Product and Framework Implications

**Length:** ~500 words

**Key points:**
- Clinical variant interpretation should assign mechanistic class before scoring
- Multi-modal interpretation engines needed: sequence + structure + activity
- ARCHCODE as module in multi-tool pipeline (not standalone predictor)
- ARS (Architecture Risk Score) as locus-level risk layer within this taxonomy
- AI hypothesis engine: classify mechanism → suggest discriminating experiment

**NOT claiming:**
- NOT "replace VEP with ARCHCODE"
- NOT "architecture is more important"
- INSTEAD: "different mechanisms, different tools, different experiments"

### 9. Discussion

**Length:** ~800 words

**Key claims (ranked by strength):**

1. **Strongest:** Regulatory pathogenicity operates through at least two mechanistically distinct axes (activity and architecture) that are nearly orthogonal (NMI < 0.1). Current tools cover activity but not architecture.

2. **Strong:** Architecture-driven pathogenicity (Class B) is enriched near tissue-matched enhancers (p = 2.51e-31) and is invisible to sequence-based tools (VEP, CADD, MPRA).

3. **Moderate:** A five-class taxonomy provides a useful framework for organizing variant interpretation blind spots and directing experimental validation.

4. **Emerging:** Coverage gaps (Class D) represent a larger fraction of blind spots (79.3%) than true mechanistic disagreements (20.7%), suggesting that tool development should prioritize coverage expansion alongside mechanistic refinement.

---

## Main Claim

**NOT:**
- "ARCHCODE is the best predictor"
- "3D chromatin is more important than sequence"

**YES:**
- "Single-axis scoring is the wrong abstraction; mechanistic decomposition is the right abstraction."
- "Architecture-driven pathogenicity is a real, distinct class that requires dedicated tools."
- "The field needs mechanism-first, then score — not score-first, then mechanism."

---

## Relationship to Existing ARCHCODE Paper

| Aspect | Core Paper (v4) | Taxonomy Paper (this) |
|:-------|:----------------|:----------------------|
| Focus | ARCHCODE method + HBB results | Mechanistic framework for the field |
| Claim | ARCHCODE detects structural blind spots | Regulatory pathogenicity has 5 classes |
| ARCHCODE role | Central tool | One tool among many (Class B engine) |
| Data | Same 30,318 variants | Same data, new classification |
| Novelty | Method + empirical results | Conceptual framework + implications |
| Format | Full research article | Position paper / perspective |

**Key difference:** The core paper says "here is a tool and what it found." The taxonomy paper says "here is why the field needs to think about variant interpretation differently."

---

## Target Journals

| Journal | Fit | Format |
|:--------|:----|:-------|
| Nature Genetics (Perspective) | HIGH | Short, conceptual, high-impact |
| Genome Research | HIGH | Full paper with methods |
| Genome Biology (Commentary) | MEDIUM | Shorter, opinion-adjacent |
| American Journal of Human Genetics | HIGH | Genetics community |
| bioRxiv (preprint) | FIRST | Immediate, establishes priority |

**Recommended path:** bioRxiv preprint → Nature Genetics Perspective or AJHG full paper.

---

## Timeline

| Phase | Deliverable | Status |
|:------|:------------|:-------|
| Phase 1: Taxonomy formalization | `regulatory_pathogenicity_taxonomy.md` | DONE |
| Phase 2: Case assignment | `taxonomy_assignment_table.csv` + summary | DONE |
| Phase 3: Figures | 3 figure specs | DONE (specs); code TBD |
| Phase 4: External cases | `external_casebook_mechanistic_classes.md` | IN PROGRESS |
| Phase 5: Paper draft | This outline | DONE (outline) |
| Phase 6: Figure code | `scripts/plot_taxonomy_figures.py` | TBD |
| Phase 7: Manuscript draft | `manuscript/taxonomy_paper/` | TBD |
