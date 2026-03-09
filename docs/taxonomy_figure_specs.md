# Taxonomy Figure Specifications

**Version:** 1.0
**Date:** 2026-03-09
**Track:** Mechanistic Taxonomy of Regulatory Pathogenicity

---

## Figure 1 — Mechanistic Taxonomy Map

### Concept
A schematic diagram showing the five classes of regulatory pathogenicity as a 2D landscape, with ARCHCODE's coverage area highlighted.

### Layout
**Two axes:**
- X-axis: "Sequence / Activity Signal" (left = absent, right = strong)
- Y-axis: "Architecture / Contact Signal" (bottom = absent, top = strong)

**Five zones in this space:**

```
                    ↑ Architecture Signal
                    |
         Class B    |    Class C
      (architecture)|    (mixed)
         ARCHCODE+  |  ARCHCODE+ & VEP+
         VEP−       |
                    |
    ────────────────┼────────────────→ Activity Signal
                    |
         Class D    |    Class A
      (coverage     |    (activity)
       gap)         |    VEP+
       VEP=N/A      |    ARCHCODE−
                    |
```

**Class E** shown as a red warning zone overlaying Class B: "Tissue-mismatch artifact zone — apparent architecture signal that collapses in wrong tissue"

### Visual Elements
- Each class zone colored differently (A=blue, B=orange, C=purple, D=gray, E=red striped)
- ARCHCODE detection zone: orange shading covering B + upper half of D + part of C
- VEP/CADD detection zone: blue shading covering A + part of C
- MPRA detection zone: blue dashed covering A only
- Overlap between tools visible in C
- Gap area (lower-left) where no tool has coverage
- Arrows from key ARCHCODE cases to their positions: HBB Q2b → B, TERT Q2a → D, SCN5A → E

### Caption (draft)
**Figure 1. Mechanistic taxonomy of regulatory pathogenicity.** Regulatory variants can be classified into five mechanistic classes based on their primary mode of action: activity-driven (A), architecture-driven (B), mixed (C), coverage gap (D), and tissue-mismatch artifact (E). Current sequence-based tools (VEP, CADD) cover classes A and partially C (blue zone). ARCHCODE specifically targets class B and provides complementary coverage for class D (orange zone). Class E represents systematic artifacts when tissue context is mismatched. No single tool covers all five classes, motivating multi-modal variant interpretation.

### Implementation
- Vector graphic (PDF/SVG) for publication
- Tool: matplotlib with patches/annotations or Inkscape for final polish
- Save: `figures/taxonomy/fig_taxonomy_map.pdf`

---

## Figure 2 — Real ARCHCODE Examples by Class

### Concept
A multi-panel figure showing concrete examples from ARCHCODE data for each class, grounding the abstract taxonomy in real results.

### Layout: 5 panels (A-E)

**Panel A — Activity-Driven (HBB Q3)**
- Scatter plot: VEP score (x) vs LSSIM (y) for HBB variants
- Q3 variants highlighted (high VEP, high LSSIM)
- Annotation: "75 variants: VEP detects, ARCHCODE silent"
- Mean enhancer distance: 25,138 bp (far from enhancers)

**Panel B — Architecture-Driven (HBB Q2b)**
- Same scatter, Q2b variants highlighted (low VEP, low LSSIM)
- Inset: enhancer proximity distribution (Q2b vs Q3)
- Annotation: "25 variants: mean 434 bp from enhancer, p = 2.51e-31"
- Key variant labels (top 3-5 by LSSIM disruption)

**Panel C — Mixed (HBB Q1)**
- Same scatter, Q1 variants highlighted (high VEP, low LSSIM)
- Annotation: "270 concordant pathogenic: both axes agree"

**Panel D — Coverage Gap (TERT Q2a)**
- Bar chart: TERT Q2 breakdown (34 Q2a vs 1 Q2b)
- Comparison: ARCHCODE AUC = 0.8405 (best model) vs M1 = 0.4893
- Annotation: "VEP cannot score; ARCHCODE provides structural read"

**Panel E — Tissue-Mismatch Artifact (EXP-003)**
- Heatmap: 3×3 tissue-mismatch matrix (HBB, LDLR, TP53)
- Diagonal (matched) = positive delta, off-diagonal = near-zero
- Annotation: "Matched: delta = 0.00357; Mismatch: delta ≈ 0"

### Caption (draft)
**Figure 2. ARCHCODE evidence for each mechanistic class.** (A) Activity-driven: HBB Q3 variants scored pathogenic by VEP but structurally neutral by ARCHCODE (mean enhancer distance 25,138 bp). (B) Architecture-driven: HBB Q2b variants scored benign by VEP but showing significant structural disruption (LSSIM < 0.95, enhancer proximity 434 bp, p = 2.51e-31). (C) Mixed: HBB Q1 concordant pathogenic variants detected by both tools. (D) Coverage gap: TERT Q2a variants unscored by VEP; ARCHCODE achieves AUC = 0.8405 (vs nearest-gene 0.4893). (E) Tissue-mismatch artifact: EXP-003 shows structural signal collapses when wrong-tissue enhancer configuration is applied (off-diagonal delta ≈ 0).

### Data sources
- Panels A-C: `analysis/discordance_2x2_matrix.csv`, `analysis/Q2b_true_blindspots.csv`
- Panel D: `analysis/ablation_study_summary.json`, `analysis/TERT_validation_summary.json`
- Panel E: `analysis/tissue_mismatch_controls_summary.json`

### Implementation
- 5-panel layout (2×3 grid, bottom-right empty or used for legend)
- matplotlib with seaborn styling
- Save: `figures/taxonomy/fig_archcode_examples.pdf`

---

## Figure 3 — Tool-to-Mechanism Comparison Matrix

### Concept
A heatmap showing which tools detect which mechanistic classes, making the coverage gaps visually obvious.

### Layout

**Rows (tools, 8):**
1. VEP
2. CADD
3. Sequence models (Enformer/Sei)
4. MPRA
5. CRISPRi
6. ARCHCODE
7. Hi-C / Capture-C
8. Conservation (PhyloP)

**Columns (classes, 5):**
1. A: Activity-Driven
2. B: Architecture-Driven
3. C: Mixed
4. D: Coverage Gap
5. E: Tissue Mismatch

**Cell values (color-coded):**
- GREEN (+++): Gold standard / primary detection
- YELLOW (++): Good detection
- LIGHT YELLOW (+): Partial / limited
- RED (−): Blind / cannot detect
- GRAY (?): Not applicable or untested
- STRIPED: Artifact source

### Specific cell assignments

| | A | B | C | D | E |
|---|---|---|---|---|---|
| VEP | ++ | − | + | − (no score) | N/A |
| CADD | +++ | − | + | + | N/A |
| Seq models | +++ | − | + | + | ? |
| MPRA | +++ | − (plasmid) | + | − | cell-dep |
| CRISPRi | ++ | + | ++ | − | cell-dep |
| **ARCHCODE** | − | +++ | + | ++ | ARTIFACT |
| Hi-C | − | +++ | ++ | − | tissue-dep |
| Conservation | ++ | + | ++ | + | N/A |

### Annotations
- Red box around B column for VEP/CADD/MPRA rows: "Systematic blind spot"
- Orange box around ARCHCODE row in B column: "Primary detector"
- Arrow from ARCHCODE to D column: "Complementary coverage (Q2a)"

### Caption (draft)
**Figure 3. Tool-to-mechanism coverage matrix.** Heatmap showing detection capability of eight computational and experimental tools across five mechanistic classes of regulatory pathogenicity. Green indicates primary detection capability; red indicates blindness. Sequence-based tools (VEP, CADD, MPRA) systematically miss architecture-driven variants (Class B, outlined in red). ARCHCODE is the only computational tool that primarily targets Class B, while being blind to activity-driven effects (Class A). No single tool covers all five classes, demonstrating that multi-modal integration is necessary for complete variant interpretation. Cell annotations indicate quantitative evidence from ARCHCODE experiments (NMI values, AUC, p-values).

### Implementation
- Heatmap with custom colormap (green-yellow-red + gray)
- Annotated cells with key statistics
- matplotlib/seaborn heatmap with custom cell borders
- Save: `figures/taxonomy/fig_tool_matrix.pdf`

---

## Summary Figure for Talks/Collaborations

### One-slide version combining all three figures:

**Left:** Simplified taxonomy map (Figure 1, reduced)
**Center:** HBB Q2b scatter as hero example (Figure 2B)
**Right:** Tool matrix heatmap (Figure 3, simplified to 4 key tools)

**Bottom banner:** "Single-axis scoring is the wrong abstraction. Mechanistic decomposition is the right abstraction."

Save: `figures/taxonomy/fig_taxonomy_summary_slide.pdf`

---

## Implementation Priority

| Figure | Priority | Complexity | Data Ready? |
|:-------|:--------:|:----------:|:-----------:|
| Fig 1 (Taxonomy Map) | P0 | Medium (schematic) | Yes (conceptual) |
| Fig 2 (ARCHCODE Examples) | P0 | High (5 panels) | Yes (all data exists) |
| Fig 3 (Tool Matrix) | P0 | Low (heatmap) | Yes (matrix defined) |
| Summary slide | P1 | Low (composite) | After Fig 1-3 |

---

## Script Plan

```python
# scripts/plot_taxonomy_figures.py
# Generates all 3 taxonomy figures from existing ARCHCODE data
# Dependencies: matplotlib, seaborn, pandas, numpy
# Input: analysis/*.csv, analysis/*.json
# Output: figures/taxonomy/fig_taxonomy_map.pdf
#         figures/taxonomy/fig_archcode_examples.pdf
#         figures/taxonomy/fig_tool_matrix.pdf
```
