# ARCHCODE: Physics-Based 3D Chromatin Simulation for Clinical Variant Interpretation

## A Complementary Approach to Machine Learning in Hemoglobinopathy Diagnosis

---

## Abstract

**Background:** Variants of uncertain significance (VUS) in the β-globin gene (*HBB*) pose significant challenges for clinical interpretation. While machine learning approaches like AlphaGenome provide sequence-based predictions, they may miss pathogenic mechanisms operating through 3D chromatin architecture disruption.

**Methods:** We developed ARCHCODE, a physics-based 3D loop extrusion simulator implementing Kramer kinetics for cohesin dynamics (α=0.92, γ=0.80, estimated from literature ranges (Gerlich et al., 2006; Hansen et al., 2017)). We performed high-throughput simulation of 367 pathogenic *HBB* variants from ClinVar and compared structural similarity index (SSIM) scores with AlphaGenome expression predictions.

**Results:** Of 367 clinically classified pathogenic variants:
- **203** (55.3%) showed significant 3D structural disruption (ARCHCODE: Pathogenic/Likely Pathogenic)
- **258** (70.3%) were predicted pathogenic by AlphaGenome
- **61** (16.6%) were discordant between methods
  - 3 detected by ARCHCODE only ("The Loop That Stayed")
  - 58 detected by AlphaGenome only (post-transcriptional mechanisms)

Mean SSIM score: 0.637
Mean AlphaGenome score: 0.636

**Conclusions:** ARCHCODE provides mechanistic insight complementary to expression-based predictors. The discordance analysis reveals:
1. Some variants disrupt 3D chromatin loops without affecting transcript levels
2. Other variants affect mRNA processing without chromatin reorganization

**Keywords:** β-thalassemia, sickle cell disease, chromatin loops, loop extrusion, variant interpretation

---

## Key Findings

### "The Loop That Stayed" - Top 5 Examples

1. **VCV000000302** @ chr11:5 225 620
   - Category: splice_region
   - ARCHCODE SSIM: 0.545 (LIKELY_PATHOGENIC)
   - AlphaGenome: 0.454 (VUS)
   - *Structural pathogenicity undetected by ML*

2. **VCV000000327** @ chr11:5 225 695
   - Category: splice_region
   - ARCHCODE SSIM: 0.547 (LIKELY_PATHOGENIC)
   - AlphaGenome: 0.456 (VUS)
   - *Structural pathogenicity undetected by ML*

3. **VCV000000026** @ chr11:5 226 830
   - Category: splice_region
   - ARCHCODE SSIM: 0.551 (LIKELY_PATHOGENIC)
   - AlphaGenome: 0.456 (VUS)
   - *Structural pathogenicity undetected by ML*

### Post-Transcriptional Mechanisms - Top 5 Examples

1. **VCV000000321** @ chr11:5 225 630
   - Category: missense
   - ARCHCODE SSIM: 0.812 (VUS)
   - AlphaGenome: 0.871 (Pathogenic)
   - *Expression impact without structural change*

2. **VCV000000341** @ chr11:5 226 402
   - Category: missense
   - ARCHCODE SSIM: 0.809 (VUS)
   - AlphaGenome: 0.840 (Pathogenic)
   - *Expression impact without structural change*

3. **VCV000000252** @ chr11:5 226 783
   - Category: missense
   - ARCHCODE SSIM: 0.726 (VUS)
   - AlphaGenome: 0.766 (Pathogenic)
   - *Expression impact without structural change*

4. **VCV000000048** @ chr11:5 226 848
   - Category: missense
   - ARCHCODE SSIM: 0.760 (VUS)
   - AlphaGenome: 0.733 (Pathogenic)
   - *Expression impact without structural change*

5. **VCV000000066** @ chr11:5 227 066
   - Category: promoter
   - ARCHCODE SSIM: 0.739 (VUS)
   - AlphaGenome: 0.731 (Pathogenic)
   - *Expression impact without structural change*

---

## Methods

### ARCHCODE Simulation
- **Kramer kinetics:** k_base = 0.002, α = 0.92, γ = 0.80
- **Locus:** chr11:5,200,000-5,400,000 (200 kb around HBB)
- **FountainLoader:** Mediator-driven cohesin loading
- **Validation:** Pearson r > 0.97 on blind loci

### AlphaGenome
- DeepMind transformer model (Nature 2026)
- 1M bp context, single-nucleotide resolution

---

## Data Availability

GitHub: https://github.com/sergeeey/ARCHCODE
- `results/HBB_Clinical_Atlas.csv`
- `scripts/generate-clinical-atlas.ts`

---

*Sergey V. Boyko | sergeikuch80@gmail.com*
*Preprint prepared for bioRxiv | 2026-02-03*

