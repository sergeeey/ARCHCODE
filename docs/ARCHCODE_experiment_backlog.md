# ARCHCODE Experiment Backlog

**Created:** 2026-03-09
**Status:** Research planning — does NOT modify frozen/submitted manuscript
**Format:** Each experiment has ID, type, hypothesis, rationale, requirements, risk, priority

---

## P0 — Must do before any follow-up claims

### EXP-001: Epigenome-only vs Epigenome+3D Ablation

| Field | Value |
|-------|-------|
| **ID** | EXP-001 |
| **Type** | Computational |
| **Hypothesis** | Full loop extrusion simulation (ARCHCODE) outperforms epigenome-only features (H3K27ac distance + CTCF proximity) for separating P/LP from B/LB at enhancer-proximal positions |
| **Why it matters** | If a simple distance-to-enhancer metric achieves comparable AUC, the 3D simulation adds complexity without value. This is the strongest possible self-challenge |
| **Required data** | Existing 30,318-variant atlas across 9 loci; H3K27ac peak BED files; CTCF peak BED files |
| **Required code** | New script: `scripts/ablation_study.py` — compute 4 feature sets, ROC curves, McNemar test |
| **Expected output** | 4-panel ROC comparison figure; per-locus AUC table; statistical test of ARCHCODE vs epigenome-only |
| **Risk** | Medium — if epigenome-only matches ARCHCODE, the paper's value proposition weakens. But honest result is better than unknown |
| **Status** | NOT STARTED |
| **Priority** | **P0** |

---

### EXP-002: Leave-One-Locus-Out Evaluation

| Field | Value |
|-------|-------|
| **ID** | EXP-002 |
| **Type** | Computational |
| **Hypothesis** | ARCHCODE pearl threshold (0.95) derived from HBB generalizes to other loci when HBB is excluded from training |
| **Why it matters** | If all pearl calls vanish when HBB is removed, the threshold is HBB-specific, not generalizable. Leave-one-out is standard in genomics benchmarking |
| **Required data** | Existing per-locus atlas CSVs; per-locus threshold calibration table |
| **Required code** | New script: `scripts/leave_one_locus_out.py` — iterate 9 folds, compute threshold on 8, evaluate on 1 |
| **Expected output** | 9-row table: locus, train AUC, test AUC, threshold, N pearls detected, sensitivity at FPR ≤ 1% |
| **Risk** | High — HBB drives 90%+ of pearl signal. Excluding it may collapse pearl detection entirely. This would be an important finding to report honestly |
| **Status** | NOT STARTED |
| **Priority** | **P0** |

---

### EXP-003: Tissue-Mismatch Negative Controls (Formalized)

| Field | Value |
|-------|-------|
| **ID** | EXP-003 |
| **Type** | Computational |
| **Hypothesis** | Running ARCHCODE with wrong-tissue enhancer annotations produces null discrimination (ΔLSSIM ≈ 0) at tissue-matched loci, confirming that structural signal requires correct enhancer landscape |
| **Why it matters** | Validates that ARCHCODE's signal comes from biology (tissue-specific enhancers), not from model artifacts (distance decay, CTCF patterns alone) |
| **Required data** | Existing atlas + enhancer annotations from 3+ cell types (K562, HepG2, MCF7 — all available from ENCODE) |
| **Required code** | New script: `scripts/tissue_mismatch_controls.ts` — run HBB with HepG2 enhancers, LDLR with K562 enhancers, etc. |
| **Expected output** | Heatmap: locus × cell-type → ΔLSSIM. Diagonal (matched) should be high, off-diagonal (mismatched) should be near zero |
| **Risk** | Low — we already know tissue mismatch gives null (SCN5A, GJB2). This formalizes and extends the observation |
| **Status** | NOT STARTED |
| **Priority** | **P0** |

---

### EXP-004: Threshold Robustness with Bootstrap CI

| Field | Value |
|-------|-------|
| **ID** | EXP-004 |
| **Type** | Computational |
| **Hypothesis** | Pearl count at HBB is stable (±10%) across perturbations: threshold sweep, CTCF ±1 site, enhancer occupancy ±20%, bootstrap resampling |
| **Why it matters** | If adding/removing one CTCF peak flips 10 pearls, the model is brittle. Robustness analysis is expected by reviewers |
| **Required data** | Existing HBB atlas; CTCF/enhancer config files |
| **Required code** | Extend existing `scripts/fragility-atlas.ts` with perturbation loops; new `scripts/threshold_robustness.py` for bootstrap |
| **Expected output** | Stability plot: pearl count vs perturbation magnitude; 95% CI on pearl count; "stability zone" definition |
| **Risk** | Low-medium — preliminary sweep (0.88–0.98) already shows HBB is robust. Adding CTCF perturbation is the harder test |
| **Status** | Partial (threshold sweep done in v2.10, CTCF/enhancer perturbation not done) |
| **Priority** | **P0** |

---

### EXP-005: HBB Q2b Top-5 Experiment Package

| Field | Value |
|-------|-------|
| **ID** | EXP-005 |
| **Type** | Wet-lab (design phase) |
| **Hypothesis** | HBB Q2b pearl variants (c.-79A>C, c.-80T>C, c.-138C>A, c.249G>C, c.50dup) show measurable contact disruption at the HBB promoter–LCR HS2 interaction in HUDEP-2 cells |
| **Why it matters** | This IS the validation experiment. Without it, ARCHCODE remains computational-only. With it, structural blind spot becomes experimentally confirmed |
| **Required data** | HUDEP-2 cell line; base editing reagents; 4C-seq or Capture Hi-C protocol |
| **Required code** | Primer design script; contact quantification pipeline; statistical comparison framework |
| **Expected output** | Contact frequency change (ΔContact) at HBB–LCR for each variant; correlation with predicted ΔLSSIM |
| **Risk** | High — contact changes may be below detection limit of 4C-seq (~2-fold). Micro-C may be needed. Budget ~$5K minimum |
| **Status** | Protocol designed (see `docs/Q2b_candidate_cards.md`), not executed |
| **Priority** | **P0** |

---

## P1 — Important for second paper / robustness

### EXP-006: Contact Metric Robustness

| Field | Value |
|-------|-------|
| **ID** | EXP-006 |
| **Type** | Computational |
| **Hypothesis** | Pearl identification is robust across contact comparison metrics (SSIM, Pearson, SCC, insulation score, virtual 4C) |
| **Why it matters** | If pearls are SSIM-specific artifacts, the finding is fragile. Metric-independence confirms the structural signal is real |
| **Required data** | Existing contact matrices (WT + mutant) for all 9 loci |
| **Required code** | New script: `scripts/contact_metric_robustness.py` — implement 5 metrics, compare pearl sets |
| **Expected output** | Jaccard similarity of pearl sets across metrics; per-metric AUC; concordance table |
| **Risk** | Medium — SSIM is specifically designed for structural similarity; simpler metrics may miss subtle differences |
| **Status** | NOT STARTED |
| **Priority** | **P1** |

---

### EXP-007: iQTL / Allele-Specific Loop Scan

| Field | Value |
|-------|-------|
| **ID** | EXP-007 |
| **Type** | Computational (data mining) |
| **Hypothesis** | Published iQTL datasets contain variants that overlap ARCHCODE structural predictions, providing independent validation without new experiments |
| **Why it matters** | iQTLs (interaction QTLs) are genetic variants that alter chromatin contacts. Overlap with ARCHCODE pearls would be strong orthogonal evidence |
| **Required data** | Published iQTL catalogs (currently limited: Greenwald 2019, Delaneau 2019); allele-specific Hi-C from phased genomes |
| **Required code** | Download + overlap script; statistical enrichment test |
| **Expected output** | N overlapping variants; enrichment p-value; per-locus breakdown |
| **Risk** | High — iQTL catalogs are small and mostly in lymphoblastoid cells (GM12878), not erythroid. May yield zero overlaps |
| **Status** | NOT STARTED |
| **Priority** | **P1** |

---

### EXP-008: Variant-to-Gene Benchmark (CRISPR Gold Standards)

| Field | Value |
|-------|-------|
| **ID** | EXP-008 |
| **Type** | Computational |
| **Hypothesis** | ARCHCODE structural predictions correlate with experimentally validated variant-to-gene links from CRISPRi/CRISPRa screens (Gasperini 2019, Fulco 2019) |
| **Why it matters** | CRISPR perturbation screens provide ground-truth enhancer–gene links. If ARCHCODE LSSIM correlates with CRISPR effect size at regulatory elements, the model captures real biology |
| **Required data** | Gasperini 2019 K562 CRISPRi (already partially downloaded: `analysis/gasperini2019/`); Fulco 2019 ABC model data |
| **Required code** | Overlap script: ARCHCODE enhancer positions → Gasperini perturbation targets → effect size correlation |
| **Expected output** | Scatter plot: ARCHCODE ΔLSSIM vs CRISPRi effect size; Spearman correlation; per-enhancer concordance |
| **Risk** | Medium — Gasperini targets are genomic regions, not point variants. Resolution mismatch may limit correlation |
| **Status** | Data partially downloaded |
| **Priority** | **P1** |

---

### EXP-009: Activity vs Architecture Assay Design Sheet

| Field | Value |
|-------|-------|
| **ID** | EXP-009 |
| **Type** | Wet-lab (design phase) |
| **Hypothesis** | For HBB Q2b variants, contact change (architecture) and expression change (activity) can be independently measured, revealing whether the mechanism is structural, transcriptional, or coupled |
| **Why it matters** | ARCHCODE models architecture only. If variants disrupt contacts without expression change, ARCHCODE captures a real but phenotypically silent mechanism. If expression changes without contacts, ARCHCODE misses the biology |
| **Required data** | Same HUDEP-2 lines as EXP-005; RT-qPCR primers; H3K27ac CUT&Tag reagents |
| **Required code** | Analysis pipeline: 4C contact quantification + expression fold-change + H3K27ac signal at enhancer |
| **Expected output** | 2×2 matrix per variant: contact ↑↓ × expression ↑↓. Classification: architecture-only / activity-only / coupled / null |
| **Risk** | Medium — requires isogenic cell lines (CRISPR base editing), which adds ~4 weeks to timeline |
| **Status** | Design phase (see research plan Section C2) |
| **Priority** | **P1** |

---

### EXP-010: TERT Secondary Locus Validation

| Field | Value |
|-------|-------|
| **ID** | EXP-010 |
| **Type** | Computational + wet-lab design |
| **Hypothesis** | TERT Q2 variants (35 total, p=2.03e-15, 97% Q2a) include structural candidates detectable by ARCHCODE in a tissue-matched cell line (hTERT-immortalized or K562) |
| **Why it matters** | HBB is the primary locus, but single-locus findings are inherently limited. TERT is the strongest secondary candidate (tissue-matched, 35 Q2 variants, strong enhancer proximity enrichment) |
| **Required data** | Existing TERT atlas; K562 enhancer data; TERT-expressing cell line |
| **Required code** | Existing TERT simulation pipeline; need Capture Hi-C primer design for TERT promoter viewpoint |
| **Expected output** | TERT-specific experiment package: top 3 candidates, assay design, expected effect sizes |
| **Risk** | Medium — TERT has 0 pearls at standard threshold (all Q2a = coverage gaps). Signal may be too weak for contact assay detection |
| **Status** | Atlas complete; experiment design NOT STARTED |
| **Priority** | **P1** |

---

## P2 — Future extensions / lower urgency

### EXP-011: Micro-C / Capture-C Target Shortlist

| Field | Value |
|-------|-------|
| **ID** | EXP-011 |
| **Type** | Infrastructure |
| **Hypothesis** | N/A — this is a preparation task |
| **Why it matters** | High-resolution contact maps (Micro-C: 200bp, Capture-C: 1kb) would enable direct comparison with ARCHCODE predictions at variant-level resolution. Current Hi-C (5kb) is too coarse for single-variant validation |
| **Required data** | Published Micro-C datasets in K562 / erythroid cells; Capture-C probe design tools |
| **Required code** | Dataset download + processing pipeline; probe design script for HBB + TERT viewpoints |
| **Expected output** | Curated list of public Micro-C/Capture-C datasets; probe sequences for top 10 ARCHCODE positions |
| **Risk** | Low — preparation only |
| **Status** | NOT STARTED |
| **Priority** | **P2** |

---

### EXP-012: Cross-Locus Structural Transfer Study

| Field | Value |
|-------|-------|
| **ID** | EXP-012 |
| **Type** | Computational |
| **Hypothesis** | Structural disruption patterns learned at one locus (HBB) transfer to other tissue-matched loci (TERT, BCL11A) without re-training — i.e., the enhancer-proximity rule is universal, not locus-specific |
| **Why it matters** | If the structural blind spot is a general phenomenon (not HBB-specific), ARCHCODE has broad applicability. Transfer learning across loci would demonstrate this |
| **Required data** | All 13 locus atlases; enhancer proximity annotations per locus |
| **Required code** | New script: `scripts/cross_locus_transfer.py` — train enhancer-proximity model on HBB, test on each other locus |
| **Expected output** | Transfer AUC per locus; feature importance comparison; domain adaptation analysis |
| **Risk** | Medium — HBB has uniquely strong signal due to LCR. Transfer may fail at weaker-signal loci |
| **Status** | NOT STARTED |
| **Priority** | **P2** |

---

## Summary Table

| ID | Type | Priority | Hypothesis (short) | Status |
|----|------|----------|-------------------|--------|
| EXP-001 | Comp | **P0** | 3D adds value beyond epigenome features | NOT STARTED |
| EXP-002 | Comp | **P0** | Threshold generalizes across loci | NOT STARTED |
| EXP-003 | Comp | **P0** | Wrong-tissue = null signal | NOT STARTED |
| EXP-004 | Comp | **P0** | Pearl count robust to perturbations | Partial |
| EXP-005 | Wet-lab | **P0** | Q2b variants show contact change | Protocol designed |
| EXP-006 | Comp | P1 | Pearls robust across contact metrics | NOT STARTED |
| EXP-007 | Comp | P1 | iQTL overlap with ARCHCODE | NOT STARTED |
| EXP-008 | Comp | P1 | CRISPR gold standard correlation | Data partial |
| EXP-009 | Wet-lab | P1 | Architecture vs activity separation | Design phase |
| EXP-010 | Both | P1 | TERT as second validated locus | Atlas complete |
| EXP-011 | Infra | P2 | Micro-C target preparation | NOT STARTED |
| EXP-012 | Comp | P2 | Cross-locus transfer learning | NOT STARTED |
