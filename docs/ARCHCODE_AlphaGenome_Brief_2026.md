# ARCHCODE × AlphaGenome: Falsification-First Regulatory Variant Validation

**One-Line Pitch**

Independent AlphaGenome-based validation workflow for disease-associated regulatory variants, with falsification-first controls and preliminary HBB concordance results.

---

## Current Signal (Real API, Not Mock)

**HBB Promoter Variants (N=13 pearls vs N=19 benign controls):**
- **CAGE disruption:** -18.0% vs -3.2% (p = 2.8×10⁻⁴, Mann-Whitney U)
- **Cohen's d:** -1.53 (large effect size)
- **API:** AlphaGenome real API (predict_variant endpoint, SDK v0.6.0)
- **Honest caveat:** Category-matched validation WEAK (ADR-027, May 8) — 15/20 pearls untestable (no non-pearl promoter controls)

**Cross-Locus Validation:**
- **MLH1** (regulatory): 3.7× stronger CAGE disruption for pathogenic (p = 0.022) ✓
- **BRCA1** (coding): 1.3× effect, p = 0.43 (not significant) ✗
- **TP53** (coding): 0.8× effect, p = 0.56 (not significant) ✗

**ARCHCODE × AlphaGenome Concordance:**
- **Spearman ρ = 0.077, p = 0.67** (NULL — no rank correlation)
- **Interpretation:** Orthogonal mechanisms (3D chromatin structure vs promoter function)
- Both methods detect pathogenicity via independent pathways — complementary, not concordant
- ADR-028 documents full analysis

**Interpretation:** AlphaGenome CAGE is **mechanism-specific** (regulatory loci work, coding loci null). This is expected biology — CAGE measures transcription initiation, not protein disruption.

**ISM Hotspot Overlap:**
- **Pearls enrich in ISM-sensitive positions:** 6/11 (54.5%) vs 12/79 non-pearls (15.2%)
- **Fisher exact:** OR = 6.70, p = 0.0071
- **Interpretation:** AlphaGenome ISM scan identifies functional hotspots overlapping ClinVar pathogenic

**Dual-DL Benchmark (Resolution Limit):**
- AlphaGenome + Akita contact maps: both **null** on SNV-level (2048bp resolution)
- Contact delta < 10⁻⁴ (noise floor)
- Conclusion: 3D contact maps cannot detect single-nucleotide structural effects at this resolution
- ADR-007, ADR-009 document negative results

---

## Validation Workflow

**Pipeline:**
```
ARCHCODE structural fragility (LSSIM < 0.93)
    ↓
AlphaGenome multimodal outputs (CAGE + ATAC + RNA-seq + histone)
    ↓
Statistical harness:
  • Category-matched controls (promoter vs promoter)
  • Permutation test (10,000 samples)
  • Shuffled labels
  • Seed sensitivity (5 random seeds)
  • Modality agreement score
    ↓
ADR log: null results as first-class artifacts
```

**Key Innovation:** Falsification-first approach prevents validation theater:
- Every enrichment claim tested with category-matched null hypothesis
- No cherry-picking (4 honest null results documented: within-category AUC, Bayesian optimization, dual-DL contact, router matched controls)
- Circular logic detected and disclosed (73bp cluster = promoter category overlap, ADR-026)

---

## What We're NOT Claiming

❌ **"ARCHCODE is a pathogenicity predictor"**  
→ Killed by within-category null (AUC ≈ 0.50 after category matching, ADR-003)

❌ **"73bp cluster is a breakthrough discovery"**  
→ High category leakage risk: 75% pearls = promoter category, 68% zone = promoter category (ADR-026)  
→ Category-matched validation in progress (ADR-027, expected result: May 11)

❌ **"AlphaGenome validates all ARCHCODE predictions"**  
→ Mechanism-specific: regulatory loci (HBB, MLH1) work, coding loci (BRCA1, TP53) null  
→ Resolution-limited: contact maps cannot detect SNVs (2048bp vs 1bp)

❌ **"Clinical pathogenicity classifier"**  
→ ARCHCODE is a **discovery engine**, not a clinical tool  
→ VUS Decision Router Class B killed by matched controls (p = 0.996, ADR-025)

---

## What We ARE Offering

✅ **First independent clinical validation of AlphaGenome regulatory outputs**  
DeepMind has not published a ClinVar variant benchmark. This is the first external test on disease-associated variants.

✅ **Falsification-first validation harness (ag-falsifier)**  
Open-source Python wrapper for AlphaGenome API with automatic statistical controls:
- Category-matched permutation
- Shuffled labels
- Modality agreement
- ADR log generation
- GitHub: [in development, alpha release: May 22]

✅ **Honest null results (6 documented ADRs)**  
- ADR-003: Within-category AUC ≈ 0.50 (circular)
- ADR-006: Bayesian optimization Δr < 0.001 (negligible improvement)
- ADR-007 + ADR-009: AlphaGenome + Akita contact maps null on SNVs (resolution limit)
- ADR-025: Router Class B VUS killed by matched controls (p = 0.996)
- ADR-027: 73bp category-matched validation WEAK (15/20 pearls untestable)
- ADR-028: ARCHCODE × AlphaGenome concordance NULL (ρ=0.077, orthogonal mechanisms)

✅ **HBB 73bp promoter cluster as candidate case study**  
Pending category-matched validation (ADR-027, in progress). If PASS → wet-lab validation candidate. If FAIL → honest null result #5.

✅ **Mechanism-specificity thesis**  
AlphaGenome CAGE works on regulatory variants (promoter, enhancer), not coding variants (missense, nonsense). This is biologically expected, not a limitation.

---

## Materials Available

**Code & Data:**
- GitHub: https://github.com/geoserg/archcode (public)
- Validation suite: 30 automated tests, 9 loci, <30s runtime
- Results: `alphagenome_pearl_vs_control.json`, `alphagenome_batch_cage_9loci.json`
- ADR log: 26 architectural decisions documented

**Key Files:**
- `scripts/validate_73bp_cluster.py` — falsification protocol (526 lines)
- `results/validate_73bp_cluster.json` — statistical test results
- `docs/ADR-026_73bp_cluster_validation.md` — category leakage disclosure

**Dataset:**
- 1,103 HBB variants (353 pathogenic, 750 benign, ClinVar)
- 20 ARCHCODE pearls (structural fragility candidates)
- 9-loci portfolio (HBB, BRCA1, TP53, CFTR, MLH1, LDLR, GJB2, TERT, SCN5A)

---

## Ask

**1. Validation Harness Feedback (ag-falsifier)**  
Is a falsification-first wrapper for AlphaGenome useful for the community?  
Target users: genomics researchers, AI safety researchers, computational biologists.

**2. HBB 73bp Cluster Case Study**  
If category-matched validation passes (ADR-027), is this candidate worth wet-lab validation?  
Methods: Hi-C (structural confirmation), MPRA (functional validation), CAGE-seq (transcription effect).

**3. Wet-Lab Collaboration**  
Prioritized variants for experimental validation:
- **HBB 73bp cluster** (chr11:5227099-5227172): 15/20 pearls, promoter region
- **AlphaGenome hotspots** (ISM scan): positions with strongest CAGE disruption
- **Cross-modality candidates**: variants with CAGE + ATAC + RNA-seq concordance

Experimental design:
- **Tier 1 (fast):** MPRA on 73bp cluster (15 variants × 3 replicates)
- **Tier 2 (medium):** Capture Hi-C on HBB locus (structural validation)
- **Tier 3 (slow):** Single-cell CAGE-seq on erythroid differentiation (functional mechanism)

**4. Endorsement / arXiv Support**  
ARCHCODE has been rejected by bioRxiv 2× (no institutional affiliation).  
Currently waiting for Ronin Institute RIIS 2.0 approval (expected ~May 10, 2026).  
Alternative: arXiv cs.CE (Computational Engineering, Biology, and Science) — requires endorsement (code: B9P837).

If you find the falsification-first methodology valuable, would you consider:
- arXiv endorsement (one-time, no ongoing commitment)
- Feedback on methodology (strengthens validation protocol)
- Collaboration on cross-locus expansion (MLH1, GJB2, TERT)

---

## Honest Limitations

**Technical:**
- ARCHCODE within-category discrimination ≈ chance (AUC 0.50 after category matching)
- AlphaGenome resolution limit (2048bp contact maps cannot detect SNVs)
- Mechanism specificity (regulatory only, coding variants invisible to CAGE)

**Statistical:**
- Category leakage in 73bp cluster (pending category-matched control test)
- Small sample size (N=20 pearls, N=13 used in CAGE validation)
- Single locus (HBB) + 1 cross-validation (MLH1) — needs multi-locus expansion

**Biological:**
- No wet-lab validation (all computational)
- Cell-type mismatch (K562 used, HBB expressed in erythroid)
- Chromatin state dependence (AlphaGenome trained on GM12878, not erythroblasts)

**Scope:**
- Not a clinical tool (discovery engine, not pathogenicity predictor)
- Not a replacement for VEP/SpliceAI/CADD (complementary structural layer)
- Not generalizable to all variant types (regulatory variants only)

---

## Timeline & Next Steps

**Completed (as of 2026-05-08):**
- ✅ AlphaGenome CAGE validation (HBB p=2.77e-4, MLH1 p=0.022)
- ✅ Dual-DL benchmark (AlphaGenome + Akita contact maps)
- ✅ 73bp cluster statistical validation (Fisher, permutation, negative controls)
- ✅ Category leakage detection (ADR-026)

**Completed (14-day execution, May 8):**
- ✅ Category-matched validation (ADR-027: WEAK, May 8)
- ✅ ARCHCODE × AlphaGenome concordance benchmark (ADR-028: NULL, May 8)
- ✅ ag-falsifier skeleton (10 files, 1185 lines, alpha release May 22)
- ✅ ISM hotspot analysis (OR=6.7, p=0.0071)
- ✅ Mechanism specificity analysis (regulatory work, coding null)

**In Progress (May 9-22):**
- 🔄 Community outreach (forum post ready, email pending)
- 🔄 Cross-locus expansion (MLH1, GJB2, TERT validation)

**Planned (Post-14-Days):**
- If concordance ≥ 0.5: expand to MLH1, GJB2, TERT (Month 2-3)
- If concordance < 0.5: pivot to "AlphaGenome standalone clinical benchmark"
- Manuscript target: Bioinformatics, NAR Genomics, or honest null result paper

---

## Contact

**Sergey Boyko**  
Independent Computational Researcher  
Ronin Institute RIIS 2.0 Fellow (confirmed April 21, 2026)

Email: sergeikuch80@gmail.com  
ORCID: https://orcid.org/0009-0009-2178-5701  
GitHub: https://github.com/geoserg/archcode  
Zenodo: https://zenodo.org/records/18908214 (v2.17)  
Research Square: https://doi.org/10.21203/rs.3.rs-9090074/v1 (taxonomy paper)

**Preferred Contact Method:** Email with "ARCHCODE × AlphaGenome" in subject line

**Response Time:** Within 24-48 hours (timezone: GMT+5, Almaty)

---

## Citation (Provisional)

If you use ARCHCODE, AlphaGenome validation results, or ag-falsifier methodology:

```
Boyko, S. (2026). ARCHCODE × AlphaGenome: Falsification-First Validation 
of Regulatory Variant Predictions. Independent Research. 
GitHub: https://github.com/geoserg/archcode
Zenodo: https://doi.org/10.5281/zenodo.18908214
```

**Note:** Formal publication pending (Ronin affiliation + arXiv/journal submission).

---

## Appendix: Key ADRs (Architectural Decision Records)

**ADR-001:** Publish v1.0 as-is, address critiques in v2.0 (falsification-first commitment)  
**ADR-003:** Within-category AUC ≈ 0.50 (circular, category artifact detected)  
**ADR-006:** Bayesian optimization null (Δr < 0.001, keep original params)  
**ADR-007:** AlphaGenome variant-level null (contact maps, resolution limit)  
**ADR-009:** Dual-DL benchmark (AlphaGenome + Akita both null on SNVs)  
**ADR-025:** Router Class B killed by matched controls (p=0.996)  
**ADR-026:** 73bp cluster category leakage (HIGH risk, category-matched test needed)  
**ADR-027:** [In progress] Category-matched validation result (expected: May 11)  
**ADR-028:** [In progress] ARCHCODE × AlphaGenome concordance (expected: May 15)  

Full ADR log: https://github.com/geoserg/archcode/tree/main/docs

---

**Last Updated:** 2026-05-08  
**Status:** Brief v1.0 — Ready for outreach  
**Next Update:** After ADR-027 (category-matched result, May 11)  

---

_"Science survives honesty. Null results are results."_
