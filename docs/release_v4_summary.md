# Release v4.0 — Submission-Ready Package

**Tag:** v4.0-submission-ready
**Branch:** feature/v4-prioritization-framework
**Date:** 2026-03-09

---

## What Changed (v4 vs v2.16)

### Framing
- Reframed from "predictor" to **prioritization engine** (Thesis C)
- Added Q2a/Q2b discordance taxonomy (Thesis A)
- Added enhancer-proximity + tissue-dependent signal (Thesis B)
- Tier system: PRIMARY (HBB) → SUPPORTING (TERT, BRCA1) → NULL (SCN5A, GJB2)

### New Analyses
- **Discordance 2×2 matrix:** ARCHCODE_HIGH × SEQ_HIGH → Q1–Q4, split Q2 into Q2a (coverage gap, 79.3%) and Q2b (true blind spot, 20.7%)
- **TERT validation:** 35 Q2 variants, 23-fold enhancer enrichment, p = 2×10⁻¹⁵, 97% Q2a
- **External validations:**
  - ABC/rE2G overlay: 68% Q2b overlap, Fisher p = 0.36 NS
  - PCHi-C erythroblast: 25 Q2b in HBB promoter bait, 25 significant interactions, max CHiCAGO = 10.5
  - CRISPRi K562: 0/65 overlap with Q2b (HBB silenced in K562)

### Manuscript Changes
- Abstract: Q2a/Q2b decomposition, Hi-C range corrected to 0.28–0.59
- Significance Statement: added prioritization framing + Thesis C
- Results: negative controls table (9 loci), discordance taxonomy figure
- Discussion: 3 theses (A/B/C) + external validations paragraph
- Supplement: Coverage Gaps note with per-locus Q2a/Q2b table
- Wording: "pathogenic" → "pathogenic/likely pathogenic" where applicable

### Integrity Fixes
- Hi-C range: 0.29–0.59 → 0.28–0.59 (TP53/MCF7 r = 0.276 rounds to 0.28)
- P/LP wording: 14/25 Q2b are LP or P/LP, not all strictly P
- PCHi-C interpretation: Q2b within bait (not upstream), coordinates verified via hg19→hg38 liftover

---

## Key Results (Frozen)

| Metric | Value |
|--------|-------|
| Total variants | 32,201 across 9 loci |
| Q2b blind spots | 54 (20.7% of discordant) |
| Q2a coverage gaps | 207 (79.3% of discordant) |
| HBB Δ LSSIM | 0.111 (tissue-matched) |
| TERT enrichment | 23-fold, p = 2×10⁻¹⁵ |
| Q2b enhancer proximity | 434 bp vs 25,138 bp (58-fold, p = 2.5×10⁻³¹) |
| Tissue Spearman ρ | 0.84, p = 0.005 |
| Hi-C validation | r = 0.28–0.59 |
| Cross-species | r = 0.82, 17/17 directional |
| Overall AUC | 0.977 (category-level, not positional) |
| Within-category AUC | 0.48 (null discrimination) |

---

## Submission Artifacts

| File | Description |
|------|-------------|
| `manuscript/biorxiv_version/main.pdf` | bioRxiv manuscript (~52 pages) |
| `manuscript/supplement.typ` | Supplementary material source |
| `figures/*.pdf` (25 files) | Publication figures |
| `checksums.sha256` | Data integrity (38 files) |
| `REPRODUCE.md` | Full reproducibility guide |
| `requirements-analysis.txt` | Python dependencies |
| `docs/lab_collaboration_letter.md` | Template for wet-lab outreach |

---

## Known Limitations (Frozen)

1. Single-tissue simulation (K562 enhancers only)
2. Predicted contact maps, not experimental
3. LSSIM threshold (0.95) manually calibrated, not fitted
4. No wet-lab validation of Q2b variants yet
5. CRISPRi gap: HBB silenced in K562 — needs HUDEP-2
6. PCHi-C: hg19 coordinates, liftover introduces ±1kb uncertainty
7. ABC enrichment NS (Fisher p = 0.36) — both Q2b and Q3 in enhancer-rich regions
8. Within-category AUC = 0.48 — no positional discrimination within functional categories

---

## Remaining Manual Steps

1. **bioRxiv resubmit:** Upload main.pdf + supplement via bioRxiv portal (ID: BIORXIV/2026/710343)
2. **arXiv endorsement:** Follow up with Brackley/Michieletto (code B9P837, q-bio.GN)
3. **Zenodo update:** Upload v4.0 archive, update DOI metadata
4. **Lab outreach:** Send collaboration letters to 6 target labs
5. **git push:** `git push origin feature/v4-prioritization-framework --tags`
