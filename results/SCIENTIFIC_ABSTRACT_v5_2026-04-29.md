# ARCHCODE: Physics-Based 3D Chromatin Simulation for Clinical Variant Interpretation

**Version:** v5.0 (Spectral Validation Edition)  
**Date:** 2026-04-29  
**Status:** Manuscript ready, spectral validation complete  
**Supersedes:** SCIENTIFIC_ABSTRACT.md (legacy 2026-03-06)

---

## One-Sentence Summary

ARCHCODE uses physics-based loop extrusion simulation to identify enhancer-proximal variants missed by sequence-based predictors, validated across nine genomic loci with tissue-dependent structural disruption and cross-locus spectral fragility analysis.

---

## Abstract

**Background:** Variants of uncertain significance (VUS) in regulatory regions pose diagnostic challenges. Machine learning tools like VEP/CADD prioritize coding variants well but show limited sensitivity for enhancer-proximal noncoding mutations that disrupt 3D chromatin architecture. We hypothesized that physics-based loop extrusion simulation could identify a complementary class of structural pathogenicity invisible to sequence-based methods.

**Methods:** We developed ARCHCODE, a graph-based loop extrusion simulator implementing Kramer kinetics for cohesin dynamics (parameters manually calibrated from literature: Gerlich et al. 2006, Hansen et al. 2017, Davidson et al. 2019). We performed high-throughput simulation of 32,201 ClinVar variants across nine loci (HBB, TP53, BRCA1, TERT, GJB2, MLH1, CFTR, SCN5A, GATA1) and computed structural similarity (LSSIM) between wildtype and variant contact maps.

**Tier System:**
- **PRIMARY (HBB):** 1,103 variants, 84% constraint, 27 pearls (VEP-blind, LSSIM-detected)
- **SUPPORTING (TP53, BRCA1, TERT):** Cross-locus validation, tissue-dependent signal
- **NULL (SCN5A, GJB2):** Negative controls (cardiac/hearing, no enhancer-proximal enrichment)

**Results:**

*Discordance Taxonomy (HBB):*
- **Q2b (blind spots, n=54):** ARCHCODE_HIGH × SEQ_LOW → 20.7% of discordant cases
  - 434bp median enhancer proximity vs 25,138bp (58-fold, p=2.5×10⁻³¹)
  - Tissue Spearman ρ=0.84, p=0.005 (erythroid > other tissues)
  - 73bp promoter cluster (chr11:5,226,540–5,227,172): 15/20 pearls
- **Q2a (coverage gaps, n=207):** TERT validation (23-fold enhancer enrichment, p=2×10⁻¹⁵), 79.3% of discordant
- **Q3 (both HIGH, n=641):** ARCHCODE + VEP concordant pathogenic

*Spectral Fragility Validation (H1-H4):*
- **H1 (Cross-locus):** Spectral Fragility Index (SFI) validated on HBB (d=1.36, p=0.0001), TP53 (d=0.87, p=0.0044), BRCA1 negative control (d=0.04, p=0.89)
  - SFI measures graph Laplacian eigenvalue perturbations (global topology), complementary to LSSIM (local structure)
- **H2 (Phase boundary):** REJECTED — 0/20 pearls in critical regime Φ≈1, all cluster in promoter (position > parameters)
- **H4 (Dosage-sensitivity):** REINTERPRETED — HBB shows 19.9% disruptive variants vs BRCA1 0.7%, TP53 0.2% (structural variance, not median robustness)

*External Validations:*
- **Hi-C correlation:** r=0.28–0.59 across loci (HUDEP-2, K562, MCF7)
- **ABC/rE2G overlap:** 68% Q2b in predicted enhancers (Fisher p=0.36, NS due to Q3 also enhancer-rich)
- **PCHi-C erythroblast:** 25 Q2b in HBB promoter bait, max CHiCAGO=10.5
- **AlphaGenome CAGE:** Pearls show 5.5× more expression disruption than benign (p=4×10⁻⁶)
- **Cross-species conservation:** r=0.82 (human-mouse LSSIM), 17/17 directional matches

**Statistical Rigor:**
- Bootstrap CI (10K iterations) + Benjamini-Hochberg FDR correction
- Mann-Whitney U + Kruskal-Wallis for non-parametric testing
- Cohen's d effect sizes: HBB d=4.17 (very large), TERT d=1.35, GJB2 d=1.27

**Conclusions:**

1. **Enhancer-proximal blind spot confirmed:** 54 variants (Q2b) show tissue-dependent structural disruption missed by VEP/CADD, validated by 10 orthogonal methods
2. **Spatial constraint dominates:** 73bp promoter cluster (HBB pearls) reflects dosage-network epistasis (α₂β₂ hemoglobin stoichiometry), not genome-wide parameter tuning
3. **Spectral fragility extends LSSIM:** Graph Laplacian eigenanalysis captures global topology (d=1.36 HBB), complementary to pixel-wise similarity
4. **Structural variance as dosage signal:** HBB 19.9% disruptive variants (vs <1% BRCA1/TP53) reflects narrow vulnerability zone under purifying selection
5. **Honest null results strengthen model:** Phase boundary hypothesis rejected, dosage-sensitivity reinterpreted from variance analysis

**Limitations:**
- Single-tissue simulation (K562 enhancers, not erythroid-specific)
- Predicted contact maps (not experimental Hi-C for all loci)
- LSSIM threshold (0.95) manually calibrated, not machine-learned
- No wet-lab validation of Q2b variants yet (requires Capture Hi-C)
- Within-category AUC=0.48 (no positional discrimination, category-driven signal)

**Clinical Impact:**
ARCHCODE identifies a complementary variant class requiring 3D chromatin context for pathogenicity. Prioritization framework (Tier PRIMARY/SUPPORTING/NULL) enables dosage-sensitive locus focus (HBB, HBA1, GATA1) while avoiding false positives in coding-dominant genes (SCN5A cardiac, GJB2 hearing).

---

## Key Numbers (Canonical, Updated 2026-04-29)

**Dataset:**
- 32,201 variants across 9 loci
- 1,103 HBB (PRIMARY), 2,794 TP53, 10,682 BRCA1
- 27 HBB pearls (14 unique positions, 15 in 73bp promoter cluster)

**Validation Metrics:**
- Hi-C: r=0.28–0.59 (across 3 loci)
- AlphaGenome CAGE: 5.5× pearl disruption (p=4×10⁻⁶)
- Cross-species: r=0.82 (17/17 directional)
- Spectral fragility: HBB d=1.36, TP53 d=0.87, BRCA1 d=0.04 (negative control)

**Discordance:**
- Q2b blind spots: 54 variants (20.7%), 58-fold enhancer enrichment (p=2.5×10⁻³¹)
- Q2a coverage gaps: 207 variants (79.3%), TERT 23-fold enrichment (p=2×10⁻¹⁵)
- Q3 concordant: 641 variants (ARCHCODE + VEP both HIGH)

**Structural Variance:**
- HBB: 19.9% disruptive (LSSIM<0.95)
- BRCA1: 0.7% disruptive
- TP53: 0.2% disruptive

**gnomAD Constraint:**
- HBB pearls: 85% absent (purifying selection, floor effect in conserved locus)
- HBB overall: 84% constraint (PLI=0.91)

---

## Data Availability

**GitHub:** https://github.com/sergeeey/ARCHCODE  
**Zenodo:** v2.17 — https://zenodo.org/records/18908214 (v2.18 pending with spectral validation)  
**Research Square:** rs-9090074 (taxonomy paper, DOI: 10.21203/rs.3.rs-9090074/v1)  
**arXiv:** Awaiting endorsement (code B9P837, q-bio.GN)  

**Key Files:**
- `results/HBB_Clinical_Atlas.csv` — 1,103 variants with LSSIM, CAGE, MPRA
- `results/phase_boundary/` — H2 parameter sweep (27 simulations)
- `results/codeword_distances.csv` — H4 dosage-sensitivity analysis
- `manuscript/spectral_results.typ` — H1-H4 validation section (78 lines)

---

## Methods Summary

**ARCHCODE Simulation:**
- Loop extrusion model: FountainLoader (mediator-driven cohesin loading)
- Kramer kinetics: k_base=0.002, α=0.92, γ=0.80 (MANUALLY CALIBRATED from literature, not fitted)
- Contact matrix: 50×50 bins (resolution 100bp–8kb depending on locus size)
- LSSIM threshold: 0.95 (exploratory, based on blind locus correlation)

**Statistical Validation:**
- Bootstrap confidence intervals (10K iterations)
- Benjamini-Hochberg FDR correction (q<0.05)
- Mann-Whitney U (non-parametric)
- Kruskal-Wallis (multi-group)
- Cohen's d effect sizes (small <0.5, medium 0.5–0.8, large >0.8)

**Spectral Fragility Index (SFI):**
- Graph Laplacian eigendecomposition (numpy.linalg.eigh)
- Eigenvalue Frobenius norm: ||λ_mut − λ_wt||_F / ||λ_wt||_F
- Eigenvector alignment: 1 − mean(|v_mut · v_wt|) for top-k eigenvectors (k=10)
- Final SFI: weighted average (0.4 eigenvalue + 0.6 eigenvector)

---

## Submission Timeline

**Current Status (2026-04-29):**
- ✅ Spectral validation complete (H1-H4)
- ✅ Comprehensive audit PASS (48/48 checks, 100%)
- ✅ Phantom reference fixed (commit 3a4fd90)
- ✅ Manuscript integrated (spectral_results.typ)

**Pending Actions:**
1. Compile final PDF (typst.compile)
2. Push to GitHub with tags
3. Update Zenodo to v2.18 (include spectral section)
4. Submit to arXiv (post-endorsement)
5. Resubmit to bioRxiv (post-Ronin approval, ~2026-05-10)

**Target Journals (post-preprint):**
- American Journal of Human Genetics (AJHG) — primary target
- Genome Research — alternative
- PLoS Computational Biology — methods track

---

## Future Directions

**Immediate (Month 1):**
1. H3 TDRA pipeline (build HGVS→ClinVar mapper)
2. FOXP3/BCL11A in silico mutagenesis (expand to 18 loci)
3. Cross-locus structural variance validation (HBA1, GATA1, SOX2)

**Medium-term (Month 2-3):**
4. Wet-lab partner (Capture Hi-C at HBB 73bp promoter cluster)
5. Multi-tissue simulation (HUDEP-2 enhancers for HBB)
6. ML integration (Random Forest on LSSIM + SFI + category features)

**Long-term (6-12 months):**
7. Genome-wide prediction (~20,000 genes)
8. Clinical diagnostic pipeline (VUS prioritization workflow)
9. Hybrid physics+ML model (residual network, benchmark vs Akita/Enformer)

---

## Keywords

β-thalassemia, sickle cell disease, chromatin loops, loop extrusion, variant interpretation, spectral graph theory, dosage sensitivity, enhancer-proximal variants, VUS prioritization, tissue-dependent regulation, graph Laplacian, physics-based simulation, clinical genomics

---

## Citation (Preprint)

Boyko SV. (2026). ARCHCODE: Physics-Based 3D Chromatin Simulation for Clinical Variant Interpretation. Research Square. DOI: 10.21203/rs.3.rs-9090074/v1

---

## Contact

**Sergey V. Boyko**  
Email: sergeikuch80@gmail.com  
ORCID: 0009-0009-2178-5701  
GitHub: https://github.com/sergeeey

**Affiliation (pending):** Ronin Institute RIIS 2.0 (application submitted 2026-03-12, decision ~2026-05-10)

---

_Prepared for bioRxiv/arXiv submission | 2026-04-29_  
_Supersedes SCIENTIFIC_ABSTRACT.md (2026-03-06 legacy version)_
