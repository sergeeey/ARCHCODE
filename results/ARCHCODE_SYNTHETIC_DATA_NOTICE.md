# ARCHCODE Synthetic Data Notice

**Date:** 2026-05-17  
**Status:** MANDATORY DISCLOSURE  
**Applies to:** All ARCHCODE simulation outputs in `results/` directory

---

## ⚠️ CRITICAL: Data Type Classification

**All ARCHCODE contact matrices, LSSIM scores, and structural disruption metrics are:**

### [VERIFIED-SYNTHETIC]

**NOT derived from real Hi-C experiments.**

---

## What This Means

### Synthetic Generation Process

1. **Contact matrices** are generated via **biophysical loop-extrusion simulation**
   - Cohesin loading, extrusion, CTCF barriers modeled computationally
   - 10,000 Monte Carlo iterations per variant
   - Resolution: 64 base pairs
   - Deterministic: seed=42 (Python), seed=12345 (TypeScript)

2. **LSSIM scores** are computed from **simulated contact matrices**
   - SSIM (Structural Similarity Index) compares wildtype vs mutant matrices
   - LSSIM = 1 − SSIM (disruption score)
   - NOT measured from real chromatin conformation capture (Hi-C, Micro-C)

3. **ΔInsulation, LoopIntegrity** derived from **simulated matrices**
   - Computed metrics, not experimental observations

---

## Affected Files

### Primary Datasets (SYNTHETIC LSSIM scores)

| File | Variants | ARCHCODE Columns | Status |
|------|----------|------------------|--------|
| `HBB_Unified_Atlas.csv` | 1,103 | ARCHCODE_SSIM, ARCHCODE_LSSIM, ARCHCODE_DeltaInsulation, ARCHCODE_LoopIntegrity | [VERIFIED-SYNTHETIC] |
| `MLH1_Unified_Atlas_300kb.csv` | 4,060 | ARCHCODE_SSIM, ARCHCODE_LSSIM | [VERIFIED-SYNTHETIC] |
| `BRCA1_Unified_Atlas_400kb.csv` | ~20,000 | ARCHCODE_SSIM, ARCHCODE_LSSIM | [VERIFIED-SYNTHETIC] |

**Other loci:** TP53, TERT, GJB2, CFTR, GATA1, PTEN (if exist) — same status

---

### Summary Result Files (SYNTHETIC-derived statistics)

| File | Content | Status |
|------|---------|--------|
| `UNIFIED_ATLAS_SUMMARY_MLH1_300kb.json` | Mean LSSIM pathogenic/benign from SYNTHETIC simulations | [VERIFIED-SYNTHETIC] |
| `O3_benford_lssim_test.json` | Benford's Law test on SYNTHETIC LSSIM distribution | [VERIFIED-SYNTHETIC] |
| Any file with "ARCHCODE", "LSSIM", "SSIM" in name | Derived from synthetic contact matrices | [VERIFIED-SYNTHETIC] |

---

## What Is NOT Synthetic

### Real-World Data (Independent of ARCHCODE)

| File | Data Type | Status |
|------|-----------|--------|
| `alphagenome_*.json` | AlphaGenome CAGE predictions (sequence-based API) | [VERIFIED-REAL] |
| `tert_hotspots_cage_test.json` | AlphaGenome CAGE for TERT C228T, C250T | [VERIFIED-REAL] |
| VEP_Consequence, CADD_Phred columns in CSV | Variant Effect Predictor + CADD scores (real annotations) | [VERIFIED-REAL] |
| ClinVar_Significance, Position_GRCh38 | ClinVar labels (real clinical data) | [VERIFIED-REAL] |

**AlphaGenome note:** CAGE predictions use real DNA sequence context but are model-based proxies, not direct ATAC-seq measurements. Classification: [VERIFIED-REAL] for sequence input, but model output is a prediction, not ground truth.

---

## Validation Status

### What ARCHCODE Synthetic Data CANNOT Validate

❌ **Real-world chromatin loop existence**  
   - ARCHCODE simulates loops based on CTCF positions
   - Does NOT confirm loops exist in vivo via Hi-C/Micro-C

❌ **Actual contact frequency changes**  
   - Simulated ΔContact is model prediction
   - Requires experimental 4C-seq, Capture-C validation

❌ **Clinical variant pathogenicity**  
   - LSSIM does NOT predict pathogenicity (AUC=0.023 in HBB)
   - Category annotation (VEP) dominates (AUC=0.791)

### What ARCHCODE Synthetic Data CAN Validate

✅ **Simulation framework correctness**  
   - Reproducible (seed=42) across runs
   - Mechanistically plausible (cohesin extrusion model)

✅ **Relative disruption scores**  
   - Promoter variants show higher LSSIM than intronic (expected)
   - CTCF disruption → high LSSIM (model captures mechanism)

✅ **Null hypothesis testing**  
   - LSSIM within-category AUC=0.50 (random) confirms structural signal saturated by category

---

## Manuscript Disclosure (Compliance Check)

### Current Status: ✅ DISCLOSED

**Location:** `manuscript/manuscript_v2_full.md` line 154

**Quote:**
> "**Note on synthetic data:** ARCHCODE contact matrices are generated via loop-extrusion simulation, not derived from real Hi-C experiments. The seed=42 implementation ensures reproducibility across independent runs; LSSIM scores (Figures 1–3) are therefore [VERIFIED-SYNTHETIC] for deterministic reconstruction, not [VERIFIED-REAL] for real-world variant interpretation."

**Figures affected:** Figure 1 (category vs LSSIM), Figure 2 (within-category AUC), Figure 3 (AlphaGenome vs ARCHCODE)

**Tables affected:** Table 2 (locus-specific AUC with LSSIM)

---

## Usage Guidelines

### For Researchers Using ARCHCODE Data

1. **Cite synthetic nature in Methods:**
   - "ARCHCODE LSSIM scores were generated via Monte Carlo loop-extrusion simulation (seed=42), not derived from experimental Hi-C data."

2. **Do NOT claim:**
   - "LSSIM measures real chromatin loops"
   - "Validated with Hi-C data"
   - "Experimental contact matrices"

3. **DO claim (appropriately):**
   - "LSSIM quantifies predicted structural disruption based on biophysical modeling"
   - "Simulation-based scores, validated against AlphaGenome (independent model)"
   - "Mechanistically plausible but requires experimental validation"

---

## Zenodo Archive Compliance

**DOI:** 10.5281/zenodo.18908214  
**Status:** Archive includes synthetic contact matrices

### Required Metadata Update

Zenodo record should include:
- **Data Type:** Synthetic (simulation-derived)
- **Method:** Monte Carlo loop extrusion (Kramer kinetics)
- **Deterministic:** Yes (seed=42)
- **Validation:** Cross-validated with AlphaGenome CAGE (orthogonal model)
- **Limitation:** NOT experimental Hi-C data

---

## Historical Context

### Why This Notice Exists

**Trigger:** ТОП-10 incident (May 2026) — validation theater where synthetic validators claimed 100% success on mock data.

**Lesson:** Synthetic data validation proves code runs, NOT that it works on real data.

**ARCHCODE case:** LSSIM is synthetic but honestly disclosed. Null result (AUC=0.50 within-category) is real finding. Synthetic nature transparent.

**Best practice:** Label synthetic data explicitly to prevent:
1. Over-interpretation of model outputs as ground truth
2. Circular validation (synthetic → synthetic)
3. Validation theater (synthetic claimed as real)

---

## Reproducibility Details

### Seeds

| Component | Seed | Purpose |
|-----------|------|---------|
| TypeScript simulation | 12345 | Monte Carlo cohesin loading positions |
| Python analysis | 42 | Cross-validation fold splits, bootstrap resampling |

### Determinism Guarantee

- Same input variant → same LSSIM score (bit-exact)
- Same fold split → same AUC estimate
- Docker container `archcode:v2.17` ensures environment consistency

---

## FAQs

**Q: Is ARCHCODE data "fake"?**  
A: No. ARCHCODE data is **synthetic** (simulation-derived) but **mechanistically plausible** and **honestly disclosed**. It models biophysical loop extrusion based on published parameters (Gerlich 2006, Davidson 2019, Sabaté 2024).

**Q: Can I use ARCHCODE data to validate my hypothesis?**  
A: **Only if your hypothesis is about simulation behavior**, not real chromatin. Example:
- ✅ "Kramer kinetics model predicts X" → use ARCHCODE
- ❌ "Real chromatin loops show X" → need experimental Hi-C

**Q: Why use synthetic data if it doesn't predict pathogenicity?**  
A: **Falsification value.** ARCHCODE's null result (within-category AUC=0.50) is a real finding: chromatin structure adds no predictive value beyond category annotation. This negative result prevents others from wasting time on failed approaches.

**Q: How is this different from AlphaGenome?**  
A: **AlphaGenome** predicts from real DNA sequence via deep learning (trained on ATAC-seq data). **ARCHCODE** simulates contact matrices via biophysical rules. Both are model predictions, not direct measurements, but AlphaGenome uses real sequence input. Classification: AlphaGenome = [VERIFIED-REAL] input, ARCHCODE = [VERIFIED-SYNTHETIC] input.

---

## Compliance Checklist

- [x] Manuscript discloses synthetic nature (line 154)
- [x] Figures labeled with [VERIFIED-SYNTHETIC] in Methods
- [x] README.md mentions simulation-based approach
- [x] This notice file created (ARCHCODE_SYNTHETIC_DATA_NOTICE.md)
- [ ] Zenodo metadata updated (PENDING — requires upload)
- [x] GitHub repository includes simulation source code

---

## Contact

For questions about ARCHCODE synthetic data classification:
- **Maintainer:** Sergey Kuchinsky (sergeikuch80@gmail.com)
- **Affiliation:** Ronin Institute for Independent Scholarship
- **Repository:** [GitHub placeholder]
- **Zenodo:** DOI 10.5281/zenodo.18908214

---

**Last Updated:** 2026-05-17  
**Version:** 1.0  
**Status:** ACTIVE — applies to all ARCHCODE outputs retroactively

---

**Key Takeaway:** ARCHCODE data is synthetic (simulation-derived), honestly disclosed, and mechanistically plausible. It serves falsification purposes (null result is real), not real-world chromatin measurements. Always cite synthetic nature when using ARCHCODE LSSIM scores.
