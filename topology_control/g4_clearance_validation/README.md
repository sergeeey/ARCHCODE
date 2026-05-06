# G4-3 Clearance Vulnerability — Clinical Validation

**Hypothesis:** H-G4-3 (Discovery Score 9.0/10)  
**Core Claim:** Λ = G4-load / helicase-capacity predicts drug sensitivity (phase transition at critical Λ_c)

**Clinical Target:** CX-5461 response prediction (Phase I data: 14% response rate, need stratification)

---

## Λ-Index Formula

```
Λ = G4_load / helicase_capacity

G4_load = Σ (G4_motifs × expression_level)  [genome-wide]
helicase_capacity = WRN + BLM + FANCJ + RTEL1 + PIF1 + HR_genes
```

---

## Week 1 Plan (2026-04-26 → 2026-05-02)

### Day 1-2: Data Download
- [ ] TCGA GDC API setup (GBM, BRCA, COAD — n=150 per type)
- [ ] Gene expression (RNA-seq TPM): helicases + oncogenes
- [ ] Mutation burden (somatic mutations/Mb)
- [ ] Clinical data (survival, drug response if available)

### Day 3-4: Λ-Index Calculation
- [ ] G4 load proxy: GC-skew promoters OR G4Hunter score
- [ ] Helicase capacity: WRN + BLM + FANCJ + RTEL1 + PIF1
- [ ] Λ-index per sample (n=450 total)
- [ ] Distribution analysis (median, IQR, outliers)

### Day 5-6: Baseline Comparison
- [ ] Baseline 1: mutation burden only (AUC_baseline1)
- [ ] Baseline 2: MYC expression only (AUC_baseline2)
- [ ] Λ-index model (AUC_Lambda)
- [ ] Combined model: Λ + MYC (AUC_combined)

### Day 7: Kill Criteria Check
- [ ] AUC(Λ) vs survival/mutation burden
- [ ] **KILL if:** AUC(Λ) ≤ 0.65
- [ ] **KILL if:** AUC(Λ) ≤ AUC(baseline) + 0.05
- [ ] **SUCCESS if:** AUC(Λ) > 0.75 across ≥2 cancer types

---

## Success Criteria (Pre-Registered)

**Minimum viable signal:**
- AUC(Λ → mutation burden) > 0.70 in ≥2/3 cancer types
- Λ quartile 4 vs quartile 1: mutation burden ratio > 1.5
- Robustness: effect holds after controlling for MYC/EGFR

**Clinical validation (Week 2+):**
- Isogenic lines: helicase KD → Λ↑ → CX-5461 sensitivity↑
- Patient cohort: retrospective CX-5461 response vs Λ

---

## Tech Stack

**Data:** TCGA GDC API (https://api.gdc.cancer.gov)  
**Compute:** Python 3.11, pandas, scipy, scikit-learn  
**G4 prediction:** G4Hunter algorithm OR EndoQuad database overlap  
**Stats:** ROC-AUC, Cox regression, quartile analysis

---

## File Structure

```
g4_clearance_validation/
├── README.md           (this file)
├── data/
│   ├── tcga_raw/       (downloaded from GDC)
│   ├── processed/      (Λ-index, expression matrix)
│   └── g4_annotations/ (G4Hunter scores, EndoQuad)
├── scripts/
│   ├── 01_download_tcga.py
│   ├── 02_calculate_lambda.py
│   ├── 03_baseline_models.py
│   └── 04_survival_analysis.py
├── results/
│   ├── lambda_distribution.png
│   ├── auc_comparison.csv
│   └── kill_criteria_check.md
└── WEEK1_LOG.md        (daily progress)
```

---

**Status:** ❌ HYPOTHESIS KILLED (AUC=0.467 < 0.65)  
**Result:** Negative result documented in `G4-3_KILLED.md`  
**Next:** Choose alternative hypothesis or pivot to other project
