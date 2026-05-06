# G4-3 Data Sources — Manual Download Guide

**Status:** Automated downloads blocked → manual required

---

## Option A: DepMap (RECOMMENDED for drug response)

**URL:** https://depmap.org/portal/data_page/?tab=allData

**Download (Priority 1):**
1. `OmicsExpressionProteinCodingGenesTPMLogp1.csv` (~400 MB)
   - RNA-seq expression (TPM log2+1)
   - Contains: WRN, BLM, BRIP1, DHX36, PIF1, RTEL1, MYC, EGFR, etc.

2. `primary-screen-replicate-collapsed-logfold-change.csv`
   - PRISM Repurposing primary screen
   - Drug viability scores

3. `secondary-screen-dose-response-curve-parameters.csv`
   - PRISM dose-response (IC50, AUC)
   - Check for: CX-5461, pyridostatin, topotecan

4. `Model.csv`
   - Cell line metadata (cancer type, lineage)

**Save to:** `data/depmap/`

**Check for CX-5461:**
```bash
grep -i "cx-5461\|cxd101\|pidnarulex" secondary-screen-dose-response-curve-parameters.csv
```

If missing → use **pyridostatin** or **topotecan** as G4-related proxy

---

## Option B: cBioPortal (for TCGA clinical)

**URL:** https://www.cbioportal.org/

**Studies:**
- BRCA: `brca_tcga_pan_can_atlas_2018`
- GBM: `gbm_tcga_pan_can_atlas_2018`
- COAD: `coadread_tcga_pan_can_atlas_2018`

**Download steps:**
1. Select study
2. Query: Enter genes (WRN, BLM, BRIP1, DHX36, PIF1, RTEL1, MYC, EGFR, TP53)
3. Download:
   - mRNA expression (RNA Seq V2 RSEM)
   - Mutations (if needed)
   - Clinical data

4. Export → tab-delimited

**Save to:** `data/cbioportal/{cancer_type}_expression.txt`

---

## Option C: GDSC (for drug sensitivity validation)

**URL:** https://www.cancerrxgene.org/downloads/bulk_download

**Download:**
1. Cell line expression: `Cell_line_RMA_proc_basalExp.txt`
2. Drug response: `GDSC1_fitted_dose_response.xlsx` or `GDSC2_fitted_dose_response.xlsx`
3. Cell line info: `Cell_Lines_Details.xlsx`

**Check for:**
- CX-5461 (unlikely in GDSC1/2)
- Camptothecin, topotecan (TOP1 inhibitors, G4-related)

**Save to:** `data/gdsc/`

---

## Option D: GDC Data Portal (official TCGA source)

**URL:** https://portal.gdc.cancer.gov/

**Steps:**
1. Repository → Filter:
   - Program: TCGA
   - Project: TCGA-BRCA, TCGA-GBM, TCGA-COAD
   - Data Category: Transcriptome Profiling
   - Data Type: Gene Expression Quantification
   - Workflow: STAR - Counts

2. Add to Cart → Download Manifest
3. Use GDC Data Transfer Tool:
   ```bash
   gdc-client download -m gdc_manifest.txt
   ```

**Save to:** `data/gdc/`

---

## Quick Start (Minimum Viable)

**For Week 1 completion:**

1. **DepMap** (if available):
   - Expression + PRISM → run full pipeline
   - Expected: AUC test on real cell lines

2. **cBioPortal** (fallback):
   - TCGA expression → Λ-index distribution
   - Correlate with survival (no drug response)

3. **Mock data** (already working):
   - Pipeline validated (AUC=0.827)
   - Ready to swap data source

---

## What to do with data once downloaded

### DepMap path:
```bash
python scripts/06_depmap_to_lambda.py
# → reads data/depmap/*.csv
# → calculates Λ-index
# → AUC vs drug response
```

### cBioPortal path:
```bash
python scripts/07_cbioportal_to_lambda.py
# → reads data/cbioportal/*.txt
# → calculates Λ-index
# → correlation with survival (not drug)
```

---

## Status Tracking

- [ ] Data source selected (DepMap / cBioPortal / GDSC)
- [ ] Expression downloaded
- [ ] Drug response / clinical downloaded
- [ ] Files saved to correct directories
- [ ] Run pipeline on real data
- [ ] Compare with mock results (AUC=0.827)

---

**Next:** Once data downloaded → re-run `02_calculate_lambda.py` + `03_baseline_models.py` with real data
