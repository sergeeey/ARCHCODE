# Spectral Fragility Validation Requirements

**Date:** 2026-04-29  
**Status:** Synthetic validation PASSED (r=0.233), contact matrix infrastructure NEEDED

---

## Executive Summary

**Synthetic decorrelation test (Day 3):** ✅ PASSED  
- SFI is complementary to LSSIM (max r=0.233 across 3 perturbation types)
- Graph Laplacian eigenvalue analysis captures distinct structural information
- No redundancy risk → safe to proceed to real data validation

**Next Blocker:** Raw contact matrices not accessible  
- ARCHCODE stores only LSSIM scalars in `within_category_analysis.json`
- Spectral analysis requires full WT/MUT 50×50 matrices for eigendecomposition
- Full dataset = 30,929 variants × 2 (WT+MUT) = 61,858 matrices (infrastructure gap)

---

## Hypothesis 1: Spectral Fragility Index (SFI)

### Claim
Pearl variants show elevated spectral fragility (graph Laplacian eigenvalue/eigenvector perturbations) compared to matched controls.

### What We Know (Validated)
- ✅ SFI prototype functional (tested on synthetic 50×50 matrices)
- ✅ SFI complementary to LSSIM (r=0.233, not redundant)
- ✅ Low-frequency eigenmodes sensitive to block structure disruption
- ✅ Eigenvalue shifts + eigenvector angles weighted combination works

### What We Need
1. **Contact matrices for HBB pearls (n=25):**
   - 25 WT matrices (50×50 each)
   - 25 MUT matrices (50×50 each)
   - Source: ARCHCODE re-simulation or export pipeline refactor

2. **Matched controls (n=25 benign HBB variants):**
   - Same region coverage as pearls (chr11:5,226,598–5,227,172)
   - VEP category-matched (intergenic_variant only)
   - 25 WT + 25 MUT matrices

3. **TP53 positive control (splice_region, n=50):**
   - AUC=0.685 known from LSSIM
   - Test if SFI replicates signal (expected: AUC>0.65)

4. **BRCA1 negative control (synonymous, n=50):**
   - AUC=0.516 known (pure chance)
   - Test if SFI correctly shows null (expected: AUC≈0.5)

### Validation Steps
```bash
# Step 1: Extract contact matrices from ARCHCODE
cd D:/ДНК/archcode-engine
# Refactor export: write contact_wt.json + contact_mut.json for each variant

# Step 2: Run SFI batch analysis
python scripts/spectral_fragility_batch.py --variants hbb_pearls.csv --output results/sfi_hbb.csv

# Step 3: Matched-control test
python scripts/matched_control_test.py --metric SFI --locus HBB --output results/sfi_matched_control.txt

# Step 4: Cross-locus validation
python scripts/spectral_fragility_batch.py --variants tp53_splice.csv --output results/sfi_tp53.csv
python scripts/spectral_fragility_batch.py --variants brca1_synonymous.csv --output results/sfi_brca1.csv
```

### Success Criteria
- **Pass:** HBB pearls vs controls Mann-Whitney p<0.05, Cohen d>0.5
- **Pass:** TP53 splice_region AUC>0.60 (signal detected)
- **Pass:** BRCA1 synonymous AUC=0.45-0.55 (correct null)
- **Kill:** Any criterion fails → SFI does not add value beyond LSSIM

### Time Estimate
- Pilot (n=100 variants): 3-4 hours simulation + 1 hour analysis
- Full dataset (n=30K): 1000 CPU-hours (requires cluster or cloud)

---

## Hypothesis 2: Loop-Extrusion Phase Boundary

### Claim
Pearl hotspots cluster in phase-transition regime where Φ = τ_cohesin × E_promoter / P_barrier ≈ 1 (critical sensitivity).

### What We Know
- ✅ HBB chr11:5,227,099-102 ISM peak = 43% CAGE disruption
- ✅ 11/25 pearls in 73bp promoter cluster (positional constraint)
- ⚠️ ARCHCODE parameters MANUALLY CALIBRATED (not fitted to FRAP data)

### What We Need
1. **Parameter sensitivity analysis:**
   - Vary τ_cohesin (residence time) ±50%
   - Vary E_promoter (enhancer strength) ±50%
   - Vary P_barrier (promoter barrier) ±50%
   - Generate 3D parameter space map: (τ, E, P) → LSSIM sensitivity

2. **Critical regime validation:**
   - Compute Φ = τ × E / P for each bin in 500kb window
   - Test correlation: Φ≈1 regions vs pearl density (Spearman)
   - Expected: r>0.5 if phase boundary hypothesis valid

3. **Tissue-specificity control:**
   - Repeat analysis with K562 (erythroid) vs GM12878 (lymphoblastoid) Hi-C
   - Expected: HBB pearls sensitive in K562, NOT GM12878 (tissue-matched)

### Validation Steps
```bash
# Step 1: Parameter sweep (ARCHCODE simulation)
cd D:/ДНК/archcode-engine
npm run parameter-sweep -- --locus HBB --tau 5,10,20,30 --E_promoter 0.5,1.0,2.0 --P_barrier 0.1,0.5,1.0

# Step 2: Compute Φ for each genomic bin
python scripts/compute_phase_parameter.py --locus HBB --output results/phase_boundary_HBB.csv

# Step 3: Correlation analysis
python scripts/phase_boundary_correlation.py --phase results/phase_boundary_HBB.csv --pearls data/hbb_pearls.csv
```

### Success Criteria
- **Pass:** Pearls cluster in Φ∈[0.7, 1.5] range (narrow critical regime)
- **Pass:** Spearman r>0.4 between Φ≈1 bins and pearl density
- **Pass:** Signal present in K562, absent in GM12878 (tissue control)
- **Kill:** Uniform Φ distribution or r<0.2 (no phase boundary structure)

### Time Estimate
- Parameter sweep: 6-8 hours (3×3×3=27 simulations per locus)
- Analysis: 2-3 hours

---

## Hypothesis 3: Topology-Dependent Regulatory Alleles (TDRAs)

### Claim
A subset of variants shows MPRA-null but endogenous-positive signal due to 3D context dependency (require chromatin looping).

### What We Know
- ✅ HBB MPRA cross-validation: pearls vs non-pearls p=0.91 (INDISTINGUISHABLE)
- ✅ AlphaGenome CAGE: pearls -19% vs benign -0.1% (p=4×10⁻⁶, in 3D context)
- ✅ ISM peak chr11:5,227,099-102 matches pearl cluster (spatial convergence)

### What We Need
1. **TDRA candidates identification:**
   - Filter: LSSIM<0.95 (structural disruption) + MPRA effect size <0.2 (MPRA-null)
   - n≈50-100 candidates across 9 loci

2. **Endogenous validation (AlphaGenome):**
   - CAGE disruption for TDRA candidates vs MPRA-positive controls
   - Expected: TDRAs show CAGE signal but MPRA null

3. **3D-independent control (linear motifs):**
   - TF motif disruption score (FIMO) for GATA1/KLF1/NF-Y sites
   - If TF motif disrupted → NOT a TDRA (linear mechanism)

### Validation Steps
```bash
# Step 1: Identify TDRA candidates
python scripts/identify_tdras.py --lssim results/within_category_analysis.json --mpra data/mpra_results.csv --output results/tdra_candidates.csv

# Step 2: AlphaGenome CAGE batch
# (requires AlphaGenome API access, 100 variants × 28 cell lines = 2800 queries)

# Step 3: TF motif analysis
python scripts/tf_motif_disruption.py --variants results/tdra_candidates.csv --motifs data/gata1_klf1_nfy.pwm --output results/tdra_motif_scores.csv
```

### Success Criteria
- **Pass:** TDRA candidates show CAGE disruption (p<0.05) despite MPRA null
- **Pass:** Non-TDRA controls show MPRA+CAGE correlation (linear mechanism)
- **Pass:** TF motif-disrupted variants excluded from TDRA class (orthogonal check)
- **Kill:** CAGE also null for TDRA candidates → no 3D-specific effect

### Time Estimate
- TDRA identification: 1 hour
- AlphaGenome batch: 2-3 days (API rate limits)
- Motif analysis: 2 hours

---

## Hypothesis 4: 3D Regulatory Error-Correcting Code

### Claim
Dosage-sensitive loci (HBB, HBA1, TP53) have higher contact-map "codeword distance" (minimum perturbation to disrupt function) than dosage-tolerant loci (BRCA1, CFTR).

### What We Know
- ✅ HBB within-category AUC=0.623 (signal)
- ✅ TP53 within-category AUC=0.623 (signal, dosage-sensitive tumor suppressor)
- ✅ BRCA1 within-category AUC=0.493 (null, haploinsufficient but large gene)
- ✅ HBA1 population constraint 91.7% (higher than HBB 84%, dosage network effect)

### What We Need
1. **Codeword distance metric:**
   - For each locus: minimum LSSIM disruption across all tested variants
   - Expected: HBB/HBA1/TP53 require larger perturbations to cross LSSIM=0.95 threshold

2. **Dosage-sensitivity panel (18 genes):**
   - Dosage-sensitive: HBB, HBA1, TP53, FOXP3, PAX6, GJB2 (known haploinsufficient)
   - Dosage-tolerant: BRCA1, CFTR, MLH1 (function via protein quality, not transcription dose)
   - Test correlation: dosage score vs minimum LSSIM disruption

3. **Network robustness simulation:**
   - Perturb random contact matrix elements → measure LSSIM decay curve
   - Fit exponential: LSSIM = exp(-k × perturbation_strength)
   - Higher k = more fragile (opposite of error correction)

### Validation Steps
```bash
# Step 1: Compute minimum LSSIM disruption per locus
python scripts/compute_codeword_distance.py --loci HBB,HBA1,TP53,BRCA1,CFTR,GJB2 --output results/codeword_distances.csv

# Step 2: Dosage sensitivity correlation
python scripts/dosage_correlation.py --codewords results/codeword_distances.csv --dosage data/dosage_scores.csv --output results/dosage_vs_codeword.txt

# Step 3: Robustness simulation
python scripts/network_robustness.py --locus HBB --iterations 1000 --output results/robustness_HBB.csv
```

### Success Criteria
- **Pass:** Dosage-sensitive loci require 2× larger perturbations to disrupt (codeword distance effect)
- **Pass:** Spearman r>0.5 between dosage intolerance score and robustness k
- **Pass:** HBB/HBA1 show steeper LSSIM decay than BRCA1/CFTR (fragility gradient)
- **Kill:** No correlation (r<0.2) or inverted sign (dosage-sensitive = more fragile)

### Time Estimate
- Codeword distance: 4-6 hours (requires full LSSIM distributions per locus)
- Dosage correlation: 1 hour
- Robustness simulation: 8-10 hours (1000 iterations × 6 loci)

---

## Infrastructure Requirements

### Immediate (Pilot Phase)
1. **Contact matrix export from ARCHCODE:**
   - Refactor `simulation.ts` to write `contact_wt.json` + `contact_mut.json`
   - Storage: ~50×50×8 bytes = 20KB per variant × 100 variants = 2MB (manageable)

2. **Spectral analysis pipeline:**
   - ✅ `spectral_fragility.py` already implemented
   - Need: `spectral_fragility_batch.py` for CSV input/output
   - Need: `matched_control_test.py` for statistical validation

3. **Phase boundary computation:**
   - Script: `compute_phase_parameter.py` (Φ = τ × E / P calculation)
   - Input: ARCHCODE parameter files + genomic coordinates
   - Output: Φ values per 5kb bin across locus

### Full Dataset (Production Phase)
1. **Contact matrix storage:**
   - 30,929 variants × 2 (WT+MUT) × 20KB = 1.2GB
   - Solution: HDF5 format (compressed) or SQLite BLOB storage

2. **Compute cluster:**
   - 1000 CPU-hours for full spectral analysis
   - Options: AWS Batch, Google Cloud Run, local workstation overnight runs

3. **AlphaGenome API credits:**
   - 2800 CAGE queries for TDRA validation
   - Current rate: ~$0.01 per query = $28 (affordable)

---

## Decision Tree (Week 1-2 Sprint)

### Day 4-5: Contact Matrix Pilot
- **Option A:** Refactor ARCHCODE export (2-3 hours dev) → run pilot (3 hours)
- **Option B:** Manual extraction from ARCHCODE debug logs (hacky, 1 hour)
- **Decision gate:** If pilot shows signal (p<0.05) → invest in full infrastructure

### Day 6-10: Hypothesis Validation
- **Priority 1:** SFI matched-control test (HBB pearls, highest confidence)
- **Priority 2:** Phase boundary correlation (addresses mechanism question)
- **Priority 3:** TDRA identification (connects MPRA null to 3D context)
- **Priority 4:** Error-correcting code (ambitious, requires 18-gene panel)

### Day 11-14: Manuscript Integration
- **If ≥2 hypotheses pass:** Add "Spectral Fragility" section to Results
- **If 1 hypothesis passes:** Add to Supplement as exploratory analysis
- **If 0 hypotheses pass:** Submit manuscript with current validation (84% constraint sufficient)

---

## Fallback Plan (If Infrastructure Blocked)

### Current Manuscript Strength (Without Spectral Analysis)
1. ✅ 84% HBB population constraint validated (21/25 pearls)
2. ✅ 91.7% HBA1 cross-validation (generalizability to dosage-sensitive loci)
3. ✅ Tissue gradient: TP53/HBB signal (dosage+tissue), BRCA1 null (size dilution explained)
4. ✅ BRCA1 contradiction resolved via synonymous baseline (AUC=0.516 vs TP53=0.614)
5. ✅ Mechanistic alternatives documented (dosage network epistasis primary)

**Verdict:** Manuscript is publication-ready WITHOUT spectral analysis.  
Spectral track = **enhancement**, not **requirement**.

### Alternative Research Directions
1. **Dosage-sensitivity panel (18 genes):**
   - Population constraint validation (gnomAD) for HBA1/HBA2/FOXP3/PAX6/GJB2
   - Lower infrastructure cost (VCF queries only, no simulation)
   - Directly tests dosage network hypothesis

2. **Tissue-specificity gradient:**
   - Within-category AUC across 9 loci vs tissue-matched Hi-C correlation
   - Tests whether signal = chromatin architecture match
   - Uses existing LSSIM data (no new infrastructure)

3. **Class D (VEP=NULL) matched-control:**
   - 49 VUS where VEP cannot classify (splice_region at boundaries)
   - Test if ARCHCODE provides orthogonal signal
   - Lower priority (Router already killed Class B)

---

## Recommendation

**Short-term (Week 1):** Run contact matrix pilot (Option B: manual extraction, 1 hour)  
- Test SFI on HBB pearls (n=25) vs controls (n=25)
- If p<0.05 → invest in infrastructure refactor
- If p>0.1 → pivot to dosage panel (faster, lower risk)

**Medium-term (Week 2-3):** Full spectral validation (if pilot passes)  
- Refactor ARCHCODE export pipeline
- Run 4-hypothesis validation suite
- Integrate 1-2 surviving hypotheses into manuscript Results

**Long-term (Month 2):** Submit manuscript regardless of spectral outcome  
- Current validation sufficient for bioRxiv/medRxiv submission
- Spectral analysis = value-add, not blocker
- Ronin affiliation expected ~May 10 (enables bioRxiv resubmission)

---

**Generated:** 2026-04-29  
**Next Action:** User decision on pilot approach (refactor vs manual extraction)
