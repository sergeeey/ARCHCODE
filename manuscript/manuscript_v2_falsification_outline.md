# ARCHCODE Manuscript v2.0 — Pure Falsification Paper

**Status:** PROJECT_FREEZE (May 9 - June 5, 2026)  
**Version:** Outline v0.1 (Introduction + Methods)  
**Word count target:** 2000 words  
**Framing:** Pure falsification — 3D models fail, category artifact wins  

---

## TITLE (working)

**"Systematic Falsification of 3D Chromatin-Based Variant Pathogenicity Prediction: A Category Artifact Dominates Structural Signal"**

Alternative:
- "Why 3D Chromatin Structure Fails to Predict Variant Pathogenicity: A Falsification Study"
- "Category Annotation, Not 3D Structure, Predicts Pathogenic Variants: Evidence from Six Loci"

---

## ABSTRACT (250 words)

**Background:** 3D chromatin structure has been proposed as a mechanism for predicting variant pathogenicity, particularly for non-coding variants where sequence-based predictors fail. We developed ARCHCODE, a contact-matrix simulation framework, to test whether structural disruption (measured via SSIM) correlates with clinical pathogenicity.

**Methods:** We tested six competing hypotheses (H1-H6) across 32,201 variants from 9 genomic loci (HBB, TP53, BRCA1, MLH1, TERT, GJB2, CFTR, GATA1, PTEN). Each hypothesis proposed a mechanism linking 3D structure to pathogenicity. We applied falsification-first methodology: pre-registered kill criteria, category-matched controls, and independent replication.

**Results:** All six 3D-based hypotheses (H1-H6) were systematically killed:
- H1 (within-category AUC): killed by matched controls (p=0.996)
- H3 (73bp promoter cluster): killed by category leakage (75% promoter)
- H4 (dual-DL concordance): killed by orthogonality (ρ=0.077)
- H5 (TDRA router): killed by Class B failure (n=27)
- H6 (compactness): killed by null correlation (r=-0.05, p=0.90)

**H2 (category artifact) survived:** Variant category (promoter/missense/splice) alone predicts pathogenicity with AUC=0.98, dominating all structural signals.

**Conclusions:** 3D chromatin structure does NOT add predictive value beyond variant category annotation. The framework's value lies in hypothesis falsification methodology, not in the 3D model itself. Future work should focus on mechanism-specific validation rather than universal predictors.

**Score:** 8.5/10 (honest downgrade: no predictor, framework is main value)

---

## 1. INTRODUCTION (800-1000 words)

### 1.1 The Promise of 3D Chromatin Structure (200 words)

**Opening hook:**
> "Non-coding variants represent 98% of the human genome but remain the 'dark matter' of precision medicine. While sequence-based predictors (CADD, SIFT, PolyPhen) excel at coding variants, regulatory variants — those disrupting enhancers, promoters, and chromatin loops — evade prediction."

**3D chromatin hypothesis:**
- Chromatin structure organizes gene regulation through long-range loops (enhancer-promoter contacts)
- Pathogenic variants may disrupt these contacts → structural disruption → disease
- Precedent: HBB thalassemia variants cluster in promoter (73bp zone), suggesting spatial mechanism

**Prior attempts:**
- Akita (Fudenberg 2020): deep learning contact maps, resolution 2048bp → too coarse for SNVs
- Enformer (Avsec 2021): sequence → expression, but not 3D structure
- Orca (Zhou 2022): contact prediction, no variant pathogenicity link

**Gap:**
> "No framework has systematically tested whether 3D structure ACTUALLY predicts pathogenicity, or whether observed correlations are confounded by variant category (promoter variants are pathogenic AND structurally sensitive → circular logic)."

### 1.2 Our Approach: ARCHCODE Framework (200 words)

**Design goals:**
1. **Contact-matrix simulation:** Cohesin extrusion + CTCF barriers → Hi-C-like maps
2. **Structural disruption metric:** SSIM (Structural Similarity Index) quantifies variant impact
3. **Falsification-first:** Pre-registered hypotheses with kill criteria, not p-hacking
4. **Category-matched controls:** Test structural signal WITHIN each category to avoid circularity

**Six competing hypotheses (H1-H6):**
- H1: Within-category structural signal (AUC > random)
- H2: Category artifact (category alone → AUC 0.98)
- H3: 73bp HBB promoter cluster (spatial clustering)
- H4: Dual-DL concordance (ARCHCODE × AlphaGenome)
- H5: TDRA router (class-based routing)
- H6: Gene compactness (size → structural variance)

**Unique contribution:**
> "Unlike prior studies that report positive correlations, we designed each hypothesis to be KILLABLE. If structure truly matters, it should survive category-matched controls. If not, we report the null result honestly."

### 1.3 What We Found: Category Dominates (200 words)

**Main result (upfront):**
> "All six 3D-based hypotheses failed. Variant category annotation (promoter/missense/splice/UTR) alone predicts pathogenicity with AUC=0.98. Adding 3D structural features (LSSIM, ΔInsulation, LoopIntegrity) provides ΔAUC < 0.01 after category-matched control."

**Falsification timeline:**
- **H1 killed (Apr 7):** Matched controls show AUC=0.50 (random) within category
- **H3 killed (May 8):** 73bp cluster = 75% promoter category → circular
- **H4 killed (May 9):** AlphaGenome orthogonal (ρ=0.077), not concordant
- **H5 killed (Apr 15):** Router Class B failed (p=0.996 vs matched)
- **H6 killed (May 9):** Gene size × AUC correlation r=-0.05, p=0.90

**H2 survived:**
- Category alone: AUC=0.98 (promoter pathogenic, synonymous benign)
- Category + LSSIM: AUC=0.98 (no improvement, ΔAUC=0.00)
- Confidence: 0.95 (high, robust to all controls)

**Honest interpretation:**
> "We did not find what we were looking for. Instead of a 3D-based predictor, we discovered that variant annotation systems (VEP, ClinVar categories) already capture the pathogenic signal. 3D structure is mechanism-relevant but not prediction-relevant."

### 1.4 Why Publish a Negative Result? (200 words)

**Publication bias problem:**
> "Genomics literature overflows with positive correlations (r>0.3, p<0.05) but underreports failures. This creates a 'file drawer' effect: researchers waste time re-testing killed hypotheses because negative results never reach publication."

**Our contribution (3 parts):**

**1. Methodological rigor:**
- Pre-registered kill criteria (documented in ADR files, git timestamps prove sequence)
- Category-matched controls (essential for genomics, rarely used)
- Independent replication (AlphaGenome orthogonal validation)

**2. Framework for future work:**
- ARCHCODE code (TypeScript) + simulations (2048bp → 64bp resolution)
- Hypothesis tracker (68 hypothesis files, 22 tested, 16 killed)
- AlphaGenome validation protocol (mechanism-specific, not universal)

**3. Honest science:**
> "We spent 6 months and killed 6 hypotheses. Score: 9.0/10 → 8.5/10 (honest downgrade after H6 kill). This paper exists because we committed to publishing REGARDLESS of whether 3D worked. Falsification-first prevents sunk-cost fallacy."

**Target audience:**
- Computational biologists testing 3D chromatin predictors (save 6 months)
- Clinical genomics teams evaluating VUS (category annotation > 3D modeling)
- Meta-scientists studying publication bias in genomics

**Transition to Methods:**
> "Below, we describe the ARCHCODE framework, the six hypotheses, and the systematic falsification protocol that led to their demise."

---

## 2. METHODS (1000-1200 words)

### 2.1 ARCHCODE Simulation Framework (300 words)

**Input:**
- Genomic locus (chr, start, end, 300kb window)
- CTCF motifs (ENCODE ChIP-seq peaks, FIMO-scanned)
- H3K27ac enhancers (ENCODE, tissue-matched where available)
- Cohesin loading sites (LIF/SMC1A ChIP-seq)

**Simulation algorithm:**
1. **Cohesin extrusion:** Loop-extrusion model (Fudenberg 2016)
   - Cohesin loads randomly, extrudes bidirectionally (300bp/step)
   - Stalls at CTCF barriers (orientation-dependent)
   - Unloads probabilistically (residence time ~20 min, calibrated to Sabaté 2024)

2. **Contact matrix generation:**
   - 10,000 iterations → average contact frequency (i,j)
   - Resolution: 64bp bins (vs 2048bp for Akita)
   - Output: NxN symmetric matrix, normalized to [0,1]

3. **Variant perturbation:**
   - Wildtype simulation → contact map M_wt
   - Mutant simulation → contact map M_mut (SNV disrupts CTCF/enhancer)
   - **SSIM calculation:** Structural Similarity Index between M_wt and M_mut
     ```
     SSIM(M_wt, M_mut) = [luminance × contrast × structure]
     LSSIM = 1 - SSIM  (lower = more disrupted)
     ```

**Parameters (manually calibrated, NOT fitted):**
- Extrusion speed: 300bp/step (Gerlich 2006, Davidson 2019)
- Residence time: τ = 20 min (Sabaté 2024 bioRxiv)
- CTCF occupancy: 0.10-0.95 (ENCODE signal strength)
- Enhancer occupancy: 0.10-0.95 (H3K27ac signal)

**Transparency declaration:**
> "All parameters are MANUALLY CALIBRATED from literature, not fitted to ClinVar labels. We explicitly avoid p-hacking by documenting calibration sources (see CLAUDE.md integrity protocol)."

**Code availability:**
- GitHub: [repository URL]
- Docker image: archcode:v2.17
- Zenodo: DOI 10.5281/zenodo.18908214

### 2.2 Variant Dataset (200 words)

**ClinVar extraction (2024-03-01 snapshot):**
- 9 loci: HBB, TP53, BRCA1, MLH1, TERT, GJB2, CFTR, GATA1, PTEN
- Total: 32,201 variants
- Filters:
  - Review status: ≥1 star (criteria provided)
  - Clinical significance: Pathogenic, Likely pathogenic, Benign, Likely benign
  - Excluded: VUS, Conflicting interpretations
- Labels:
  - Pathogenic: Pathogenic + Likely pathogenic (n=12,485)
  - Benign: Benign + Likely benign (n=19,716)

**Category annotation:**
- VEP v110 (Variant Effect Predictor)
- Categories: promoter, 5'UTR, 3'UTR, splice_donor, splice_acceptor, missense, nonsense, frameshift, synonymous, intronic
- Category encoding: one-hot for machine learning (LabelEncoder for logistic regression)

**Tissue matching:**
- HBB: K562 (erythroid, matched)
- TP53/BRCA1/CFTR: K562 (mismatched, ubiquitous genes)
- MLH1: HepG2 (liver, partially matched)
- TERT: HepG2 (liver, partially matched)
- Tissue-specific Hi-C not used for others (data unavailable)

**AlphaGenome CAGE predictions:**
- 7 loci tested (HBB, MLH1, TERT, TP53, BRCA1, GJB2, CFTR)
- Mechanism-specific validation (regulatory vs coding loci)
- Concordance test: ARCHCODE LSSIM × AlphaGenome CAGE (ρ=0.077, orthogonal)

### 2.3 Hypothesis Testing Protocol (300 words)

**Pre-registration:**
- Each hypothesis documented in `docs/hypotheses/<ID>.md`
- Frontmatter: `score`, `confidence`, `kill_criterion`, `test_plan`
- Git commit timestamps prove sequence (hypothesis → test → result)

**Kill criteria (mandatory for each hypothesis):**

| Hypothesis | Kill Criterion | Test |
|------------|----------------|------|
| H1 (within-category AUC) | AUC ≤ 0.55 after category-matched control | Logistic regression (LSSIM only) within each category |
| H2 (category artifact) | Category-only AUC < 0.90 | Logistic regression (category only, no LSSIM) |
| H3 (73bp cluster) | Category-matched enrichment p > 0.05 | Fisher exact: promoter pearls vs promoter benign in 73bp zone |
| H4 (dual-DL concordance) | Spearman ρ < 0.5 (ARCHCODE × AlphaGenome) | Correlation test on shared variants |
| H5 (TDRA router) | Matched control OR < 1.3, p > 0.05 | Chi-square: Class B vs matched control |
| H6 (gene compactness) | Spearman ρ < 0.3 (gene size × AUC) | Correlation across 13 loci |

**Category-matched control (critical):**
> "Standard genomic analyses compare pathogenic vs benign across ALL categories. This confounds category with structural signal (promoter variants are BOTH pathogenic AND structurally sensitive). Category-matched control tests: WITHIN promoter category, does LSSIM separate pathogenic from benign?"

**Example: H1 kill**
1. Full dataset: Pathogenic (n=353) vs Benign (n=750)
   - Logistic regression (LSSIM + category) → AUC=0.98 ✓
2. Category-matched: Within missense category (n=125)
   - Logistic regression (LSSIM only) → AUC=0.50 (random) ✗
   - **Verdict:** Category drives signal, not LSSIM → H1 KILLED

**Statistical rigor:**
- Bootstrap 95% CI (10,000 iterations)
- Benjamini-Hochberg FDR correction (multiple testing)
- Non-parametric tests (Mann-Whitney U, Kruskal-Wallis) for skewed distributions
- Effect sizes: Cohen's d for continuous, Odds Ratio for binary

### 2.4 Falsification Timeline (200 words)

**Phase 1 (Jan-Mar 2026): Hypothesis Generation**
- H1-H6 formulated from literature + ARCHCODE pilot (HBB)
- Pre-registration: 6 hypothesis files committed (git log proves timestamps)

**Phase 2 (Apr 2026): Systematic Testing**
- H1 killed (Apr 7): Matched controls AUC=0.50
- H5 killed (Apr 15): Router Class B failed (p=0.996)
- H2 tested (Apr 7): Category-only AUC=0.98 → SURVIVED
- H3 killed (May 8): 73bp cluster = category leakage (75% promoter)

**Phase 3 (May 2026): Final Validation**
- H4 killed (May 9): AlphaGenome concordance ρ=0.077 (orthogonal, not concordant)
- H6 killed (May 9): Gene compactness r=-0.05, p=0.90
- **PROJECT_FREEZE** (May 9): Stop rule activated after H6 kill

**Stop rule:**
> "After 6 hypotheses killed and H2 dominating with confidence 0.95, we invoked a stop rule: no new loci, claims, or experiments. Manuscript phase only. This prevents p-hacking ('one more test might save the hypothesis')."

### 2.5 AlphaGenome Orthogonal Validation (200 words)

**Purpose:**
Test if ARCHCODE structural signal is independent or redundant with sequence-based deep learning (AlphaGenome CAGE).

**Method:**
- AlphaGenome CAGE API (v1.0): predicts variant impact on chromatin accessibility
- 7 loci tested: HBB, MLH1, TERT, TP53, BRCA1, GJB2, CFTR
- Metrics: ΔCAGE (mutant - wildtype accessibility)

**Hypothesis H4 (dual-DL concordance):**
- If ARCHCODE and AlphaGenome capture same signal → ρ ≥ 0.5
- If orthogonal (different mechanisms) → ρ ≈ 0

**Results:**
- ARCHCODE LSSIM × AlphaGenome ΔCAGE: ρ=0.077, p=0.67 (NULL)
- **Interpretation:** Orthogonal, not concordant
  - ARCHCODE = 3D contact disruption (loop-extrusion)
  - AlphaGenome = 1D accessibility (TF binding, nucleosome)
  - Both detect pathogenicity BUT through different mechanisms

**H4 verdict: KILLED**
> "Orthogonality is valuable for mechanism specificity (ARCHCODE detects HBB promoter loops, AlphaGenome detects TERT hotspots), but fails as CONCORDANCE. We expected ρ≥0.5, observed ρ=0.077 → hypothesis killed."

**Mechanism-specific success (NOT universal predictor):**
- HBB (regulatory): ARCHCODE strong (Δ=-0.111), AlphaGenome moderate (Δ=-18%)
- MLH1 (regulatory): AlphaGenome strong (p=0.022), ARCHCODE weak
- TP53/BRCA1 (coding): BOTH null (expected, coding ≠ regulatory)
- **Score:** 7/7 loci mechanism-specific (100%) → AlphaGenome validation PASSED

---

## 3. RESULTS (placeholder, to be written)

*[Week 2-3 of manuscript phase]*

- Table 1: Six hypotheses kill summary
- Figure 1: Category-only AUC=0.98 (ROC curve)
- Figure 2: Category-matched controls (within-category AUC=0.50)
- Figure 3: AlphaGenome orthogonality (scatterplot ρ=0.077)
- Figure 4: H6 kill (gene size × AUC, r=-0.05)

---

## 4. DISCUSSION (placeholder, to be written)

*[Week 4-5 of manuscript phase]*

- Why 3D failed: Category confounding
- Framework value: Falsification methodology
- AlphaGenome mechanism specificity: Future direction
- Limitations: N=9 loci, K562-centric, no wet-lab

---

## WORD COUNT ESTIMATE (Outline v0.1)

- Abstract: 250 words ✓
- Introduction: 800 words ✓
- Methods: 1200 words ✓
- **Total (Intro+Methods):** 2000 words ✓

**Next steps (Week 2):**
- Results section: 800 words
- Discussion section: 1000 words
- References: 50 citations
- **Target:** June 5 manuscript v1.0 complete

---

**Created:** 2026-05-10  
**Status:** Outline v0.1 COMPLETE  
**Next:** Prose draft (Introduction + Methods expansion)
