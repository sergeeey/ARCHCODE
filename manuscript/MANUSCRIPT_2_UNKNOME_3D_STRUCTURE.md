# Manuscript 2: Draft Structure — 3D-Guided Unknomics of Regulatory Variants

Draft: 2026-03-06  
Concept: Bridge between "dark genome" (understudied regulatory space), Unknome (poorly characterised conserved genes), and 3D chromatin architecture; prioritise Unknome genes by ARCHCODE 3D-structural vulnerability for experimental follow-up.

---

## Title (working)

**3D-guided unknomics: prioritising poorly characterised genes by chromatin structural vulnerability**

---

## Abstract (1 paragraph)

We combine the Unknome database (genes ranked by low functional annotation) with ARCHCODE, a physics-based 3D chromatin loop extrusion model, to rank human genes by the structural vulnerability of their regulatory neighbourhoods. In-silico perturbation of enhancer/CTCF-anchored loci yields a 3D-vulnerability score (1 − mean LSSIM) per gene locus. We apply this to a subset of genes overlapping existing ARCHCODE locus configs and report a prioritised list; genes with higher vulnerability are proposed as candidates for experimental functionalisation (e.g. with Unknome or erythroid/3D-genome labs). This approach links the "dark genome" and Unknome to 3D architecture without requiring wet-lab data as input.

---

## 1. Introduction (1 paragraph)

A large fraction of the human genome and of conserved genes remains poorly characterised. The Unknome database ranks proteins by "knownness" (GO annotation density) and has been used to prioritise essential but understudied genes in model organisms. Regulatory and 3D chromatin context is largely absent from knownness metrics. We ask whether genes that sit in structurally "vulnerable" loci—where local perturbations cause large changes in simulated contact topology—should be prioritised for functional study, and we use ARCHCODE to compute a 3D-vulnerability score per gene locus.

---

## 2. Methods (1 paragraph)

We take a list of human genes (from Unknome or a stub overlapping ARCHCODE loci). For each gene we map to an ARCHCODE locus config (promoter/enhancer/CTCF) when available. We run an in-silico perturbation scan: sample bins across the locus, apply a fixed occupancy reduction (effect strength 0.05) at each bin, and compute Local SSIM (LSSIM) between wild-type and mutant contact matrices. The 3D-vulnerability score is 1 − mean(LSSIM); higher score indicates greater structural sensitivity. Genes are ranked by this score. Data: Unknome (CC BY 4.0); ARCHCODE parameters as in Manuscript 1.

---

## 3. Results (1 paragraph)

We report a prototype run over 13 genes with existing locus configs (HBB, BRCA1, CFTR, TP53, MLH1, LDLR, TERT, GJB2, SCN5A, PTEN, BCL11A, GATA1, HBA1). Ranking by vulnerability score yields BCL11A, HBA1, TERT, PTEN, GATA1 among the top; full table in `results/unknome_3d_priority_*.json`. This demonstrates feasibility; expansion to the full Unknome human set requires mapping genes to coordinates and, where no config exists, building locus configs from ENCODE/ROADMAP.

---

## 4. Discussion (1 paragraph)

3D-guided unknomics adds a structural dimension to knownness-based prioritisation. Genes in loci with strong enhancer–CTCF architecture and high sensitivity to local perturbation may be particularly relevant to regulatory disease and to experimental screens (e.g. CRISPR, RNAi) that could be interpreted in 3D context. We propose collaboration with Unknome and experimental groups to validate prioritisation and to extend the pipeline to genes without pre-built ARCHCODE configs.

---

## 5. Limitations (1 paragraph)

The current run uses only genes that already have ARCHCODE locus configs; the full Unknome human list is not yet integrated. 3D-vulnerability is in-silico only and has not been validated against experimental perturbation (e.g. Hi-C after CRISPR). Claim level is EXPLORATORY per project validation protocol.

---

## 6. Data and code availability

- Unknome: https://unknome.mrc-lmb.cam.ac.uk/about/ (Rocha et al. PLoS Biol 2023).
- ARCHCODE: repository; script `scripts/unknome-3d-priority.ts`; config `config/unknome_genes_subset.json`; output `results/unknome_3d_priority_*.json`.
