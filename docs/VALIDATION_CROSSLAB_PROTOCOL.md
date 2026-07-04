# Cross-Lab Validation Protocol: ARCHCODE Structural Blind Spot

Date: 2026-03-06  
Project: ARCHCODE  
Purpose: Experimental validation of pearl variants (VEP-blind, ARCHCODE structural signal) via cross-lab collaboration.

## 1. Goal

Test whether ARCHCODE-identified "pearl" variants (pathogenic by 3D chromatin structure, invisible to VEP/SpliceAI/CADD) show measurable functional impact in erythroid cells:

- **Primary:** Reproduce predicted drop in promoter–LCR contact and/or aberrant splicing for ≥1 of the top-priority pearl candidates.
- **Secondary:** Provide orthogonal evidence for the structural blind spot (sequence-based predictors miss; ARCHCODE + experiment agree).

No clinical reclassification is proposed until validation data are obtained and reviewed.

## 2. Variant Selection

**Source:** [results/pearl_validation_shortlist.json](../results/pearl_validation_shortlist.json)

**Minimum panel (top 3 positions):**

| Rank | Position (GRCh38) | HGVS (HBB)   | LSSIM  | Rationale                          |
|------|-------------------|--------------|--------|------------------------------------|
| 1    | 5,227,100         | c.-79A>C     | 0.9361 | Promoter TATA-proximal, VEP-blind  |
| 2    | 5,227,101         | c.-80T>C     | 0.938  | TATA box, known beta-thal association |
| 3    | 5,227,159         | c.-138C>A    | 0.9423 | Distal promoter, beta-thal minor   |

**Extended panel (optional):** Include rank 4–5 (c.249G>C missense, c.50dup frameshift positive control) and/or additional promoter pearls from the shortlist for statistical power.

**Locus:** HBB, chr11:5,225,464–5,229,395 (GRCh38), or equivalent window covering LCR–HBB promoter.

## 3. Methods

### 3.1 RT-PCR (splicing / transcript level)

- **Objective:** Quantify aberrant splice products or change in HBB transcript abundance at pearl positions vs wild-type.
- **Cell models:** K562 and/or HUDEP-2 (or equivalent erythroid line with LCR–HBB activity).
- **Design:** Compare wild-type vs engineered or patient-derived cells carrying the variant at the chosen position(s). If base editing or CRISPR is used, isogenic control preferred.
- **Outputs:** Proportion of aberrant splice product (or Δ transcript level) per variant; comparison to ARCHCODE LSSIM and to VEP/SpliceAI (expected null for pearls).

### 3.2 Capture Hi-C (contact structure)

- **Objective:** Measure promoter–LCR (e.g. HBB promoter ↔ LCR HS2/HS3) contact frequency in wild-type vs variant.
- **Cell models:** Same as above (K562, HUDEP-2, or equivalent).
- **Design:** Capture Hi-C at HBB locus; compare contact matrices or anchor-to-anchor counts between conditions.
- **Outputs:** Contact frequency (or normalized counts) for key anchor pairs; correlation with ARCHCODE-predicted Δ contact (e.g. from Virtual CRISPR: ~17% drop for top promoter pearls, see [manuscript/TABLE_VCRISPR_TOP3.md](../manuscript/TABLE_VCRISPR_TOP3.md)).

## 4. Success Criteria (Go/No-Go)

- **Go (positive):** For ≥1 of the top-3 (or extended) panel: (a) significant change in splice product or transcript level (RT-PCR) and/or (b) significant change in promoter–LCR contact (Capture Hi-C) in the direction predicted by ARCHCODE (e.g. contact drop where ARCHCODE predicts disruption).
- **No-Go (negative):** No significant effect for any tested variant; document and report as negative result; do not claim structural blind spot as validated for those variants.
- **Inconclusive:** Underpowered or technically failed experiments; report as inconclusive and list limitations.

All outcomes (positive, negative, inconclusive) should be reported with exact methods, sample sizes, and provenance (EXPERIMENTAL per [VALIDATION_PROTOCOL.md](VALIDATION_PROTOCOL.md)).

## 5. Cell Models and Scope

| Model    | Use case                    | Notes                          |
|----------|-----------------------------|--------------------------------|
| K562     | Erythroid, widely available | LCR–HBB active; Hi-C data exist |
| HUDEP-2  | Erythroid, primary-like    | Preferred for physiological relevance |
| G1E-ER4  | Erythroid differentiation  | Optional for differentiation context |

**Estimated scope (minimal):**

- RT-PCR: 3–5 variants × 2 replicates → on the order of 1–2 weeks wet-lab.
- Capture Hi-C: 1–2 conditions (e.g. WT vs 1 variant) → protocol-dependent (typically weeks to months including library prep and sequencing).

## 6. Data and Code Provenance

- **Shortlist:** [results/pearl_validation_shortlist.json](../results/pearl_validation_shortlist.json)  
- **ARCHCODE parameters and Virtual CRISPR:** [manuscript/METHODS.md](../manuscript/METHODS.md), [manuscript/TABLE_VCRISPR_TOP3.md](../manuscript/TABLE_VCRISPR_TOP3.md), [results/virtual_crispr_pearls.json](../results/virtual_crispr_pearls.json)  
- **Claim levels:** Per [VALIDATION_PROTOCOL.md](VALIDATION_PROTOCOL.md), validation claims require EXPERIMENTAL provenance and explicit acceptance criteria (this protocol).

## 7. Contact and Collaboration

For interest in running this protocol (or a subset), open an issue in the repository or contact the maintainers. We can provide:

- Variant list in table/BED format.
- ARCHCODE predictions (LSSIM, contact change) for the chosen panel.
- One-page summary for grant or lab meeting (see [docs/COLLABORATOR_SUMMARY_STRUCTURAL_BLIND_SPOT.md](COLLABORATOR_SUMMARY_STRUCTURAL_BLIND_SPOT.md)).
