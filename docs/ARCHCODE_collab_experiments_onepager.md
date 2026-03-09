# ARCHCODE — Collaborator Experiment One-Pager

**For:** Potential wet-lab collaborators (chromatin biology / hematology / functional genomics)
**Date:** March 2026
**Contact:** Sergey Boyko — github.com/sergeeey/ARCHCODE

---

## What ARCHCODE Is

A computational tool that simulates 3D chromatin loop extrusion to predict which genetic variants disrupt enhancer–promoter contacts. It identifies variants that are **invisible to sequence-based tools** (VEP, CADD, SpliceAI) because their pathogenic mechanism operates through 3D chromatin topology, not protein sequence or splice motifs.

**Core metric:** LSSIM (Local Structural Similarity Index) — compares wild-type and mutant predicted contact maps. Low LSSIM = structural disruption.

**Scale:** 30,318 classified ClinVar variants across 9 disease-associated loci. 27 "pearl" variants at HBB that no existing tool detects.

---

## What ARCHCODE Is Not

- Not a pathogenicity predictor — it is a **prioritization engine** (which variants to test first)
- Not a replacement for VEP/CADD — it covers a **different axis** (3D structure vs sequence)
- Not clinically validated — all results are computational predictions
- Not useful for missense variants — zero sensitivity to amino acid changes
- Not tissue-agnostic — requires matched cell-type enhancer data

---

## Best First Validation Experiment

**Goal:** Test whether ARCHCODE-predicted structural disruption corresponds to measurable chromatin contact changes.

| Parameter | Value |
|-----------|-------|
| **Cell line** | HUDEP-2 (human erythroid progenitor) |
| **Variants** | 3 HBB pearl variants: c.-79A>C, c.-80T>C, c.-138C>A |
| **Method** | CRISPR base editing → 4C-seq (HBB promoter viewpoint) |
| **Readout** | Contact frequency at HBB promoter–LCR HS2 interaction |
| **Negative control** | Same variants in HEK293 (tissue mismatch → expect null) |
| **Success criterion** | Pearson r > 0.5 between predicted ΔLSSIM and observed ΔContact |
| **Failure criterion** | No detectable contact change at any of 3 positions |
| **Timeline** | ~8 weeks (cell culture + editing + 4C-seq + analysis) |
| **Estimated budget** | $3,000–5,000 |

---

## Top Candidate Class

**"Pearl variants"** — ClinVar pathogenic/likely pathogenic variants that are:
- VEP score < 0.30 (invisible to sequence annotation)
- SpliceAI score = 0.00 (invisible to splice prediction)
- CADD phred ~15.7 (ambiguous zone)
- gnomAD AF = 0 (absent from 800K+ genomes)
- ARCHCODE LSSIM < 0.95 (structurally disruptive)
- Located within 1 kb of H3K27ac enhancer peaks

These variants sit in the **structural blind spot** — the region where sequence tools are blind and only 3D contact analysis provides signal.

---

## Suggested Assays (ranked by cost-effectiveness)

| Priority | Assay | What it tests | Resolution | Cost |
|----------|-------|---------------|------------|------|
| 1st | **4C-seq** | Contact frequency from HBB promoter viewpoint | 5–10 kb | ~$200/sample |
| 2nd | **Capture Hi-C** | Targeted contact map at HBB locus | 1–5 kb | ~$500/sample |
| 3rd | **RT-qPCR** | HBB mRNA expression (activity axis) | Gene-level | ~$50/sample |
| 4th | **CUT&Tag** | H3K27ac at LCR enhancers (epigenetic axis) | 200 bp | ~$150/sample |
| 5th | **Micro-C** | Nucleosome-resolution contacts (gold standard) | 200 bp | ~$2,000/sample |

**Minimum viable experiment:** 4C-seq + RT-qPCR for 3 variants + 1 negative control = ~$1,500.

---

## Why HBB Is Primary

1. **Strongest signal:** ΔLSSIM = 0.111 (pathogenic vs benign), 7× stronger than any other locus
2. **Most pearls:** 27 (next locus: 0 robust pearls)
3. **Best validated:** Hi-C r = 0.53–0.59 in K562
4. **Rich enhancer landscape:** LCR super-enhancer (5 enhancers within 13 kb) creates maximum structural discrimination
5. **Clinical relevance:** β-thalassemia affects >60,000 births/year worldwide
6. **Available cell models:** HUDEP-2 is well-established for erythroid chromatin studies
7. **Cross-species support:** Mouse Hbb-bs shows conserved structural signal (r = 0.82, 17/17 directions preserved)

---

## Why TERT Is Secondary (with Caveat)

**Strengths:**
- Tissue-matched in K562 (TERT actively transcribed)
- 35 Q2 variants with 23-fold enhancer proximity enrichment (p = 2.03 × 10⁻¹⁵)
- Clinically important: TERT promoter mutations in ~70% of glioblastomas

**Caveat:**
- 0 robust pearls at standard threshold (all 35 Q2 variants are Q2a = VEP coverage gaps, not genuine discordance)
- ΔLSSIM = 0.019 (6× weaker than HBB)
- Contact changes may be below 4C-seq detection limit
- Would need Capture Hi-C or Micro-C (higher resolution, higher cost)

**Recommendation:** Validate HBB first. If successful (r > 0.5), proceed to TERT as replication locus with upgraded assay.

---

## What We Provide

- Full ARCHCODE atlas for all 9 loci (30,318 variants with LSSIM scores)
- Predicted contact maps (WT + mutant) for any configured variant
- Per-variant experiment recommendation (assay, viewpoint, expected effect)
- Analysis pipeline for 4C-seq / Capture Hi-C data → ARCHCODE comparison
- Statistical framework for validation (correlation, permutation tests)

**Preprint:** BIORXIV/2026/710343 (pending resubmission)
**Code + data:** github.com/sergeeey/ARCHCODE | Zenodo DOI: 10.5281/zenodo.18867448

---

## Key Question This Collaboration Would Answer

> Do variants that ARCHCODE predicts will disrupt 3D chromatin contacts actually show altered enhancer–promoter interaction frequency in living cells?

If yes → ARCHCODE becomes a validated structural prioritization tool for clinical genomics.
If no → The structural blind spot hypothesis needs revision, and we report that honestly.
