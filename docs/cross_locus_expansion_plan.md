# Cross-Locus Expansion Plan — AlphaGenome CAGE Validation

**Version:** 1.0  
**Date:** 2026-05-08  
**Purpose:** Expand HBB validation to MLH1, GJB2, TERT  
**Hypothesis:** Mechanism specificity generalizes (regulatory loci work, coding null)

---

## Executive Summary

**HBB результат (май 2026):**
- ✅ CAGE validated: pearls -18.0% vs controls -3.2%, p=2.77×10⁻⁴ (Mann-Whitney U)
- ✅ MLH1 confirmed: pathogenic 3.7× stronger, p=0.022
- ❌ BRCA1/TP53 null: p>0.4 (expected — coding loci)

**Гипотеза:** AlphaGenome CAGE mechanism-specific → работает на regulatory loci (промотеры, энхансеры), null на coding loci (миссенс, нонсенс).

**Цель:** Протестировать на 3 новых loci (2 regulatory, 1 coding) для подтверждения generalization.

---

## Locus Selection

| Locus | Type | Rationale | Expected Result |
|-------|------|-----------|-----------------|
| **MLH1** | Regulatory (promoter) | CpG island promoter mutations → Lynch syndrome. HBB validated this already (p=0.022). | ✅ PASS (CAGE detects) |
| **GJB2** | Coding (missense) | Connexin 26, hearing loss. Missense mutations in coding exon. | ❌ NULL (CAGE blind) |
| **TERT** | Regulatory (promoter) | Telomerase promoter mutations → cancer. Hotspot C228T, C250T. | ✅ PASS (CAGE detects) |

**Rationale:**
- MLH1: Already tested, включить для полноты
- GJB2: Coding-only locus, negative control (CAGE should fail)
- TERT: Promoter hotspot locus, strong regulatory signal expected

---

## Data Requirements

### Per Locus

**ClinVar variants:**
- ≥20 Pathogenic/Likely Pathogenic (pearls)
- ≥20 Benign/Likely Benign (controls)
- Category distribution: promoter, 5'UTR, 3'UTR, missense, nonsense

**AlphaGenome CAGE predictions:**
- Already available from `alphagenome_batch_cage_9loci.json` (March 30, 2026)
- No new API calls needed

**ARCHCODE structural fragility:**
- Available from existing pearl detection runs
- Not required (AlphaGenome standalone validation)

---

## Validation Protocol (per locus)

### Step 1: Load Data

```python
from ag_falsifier import AlphaGenomeValidator
import pandas as pd

# Load ClinVar variants for locus
pearls = load_clinvar_variants(locus='MLH1', label='Pathogenic')
controls = load_clinvar_variants(locus='MLH1', label='Benign')

# Merge with AlphaGenome CAGE predictions
pearls = pearls.merge(cage_predictions, on='Variant_ID')
controls = controls.merge(cage_predictions, on='Variant_ID')
```

### Step 2: Run Category-Matched Validation

```python
validator = AlphaGenomeValidator(
    pearls=pearls,
    controls=controls,
    api_key='not-needed-cached-data'
)

result = validator.validate(
    modality='CAGE',
    category_matched=True,
    permutation_test=True,
    n_permutations=10000,
    negative_controls=['shuffled_labels'],
    seed_sensitivity=[1, 7, 21, 42, 100]
)
```

### Step 3: Generate ADR

```python
result.to_adr(path=f'docs/ADR-029_{locus}_cage_validation.md')
result.to_json(path=f'results/{locus}_cage_validation.json')
```

### Step 4: Verdict Decision Tree

```
IF test_validity == "VALID" AND p < 0.01:
    → PASS (validated)
    
ELIF test_validity == "PARTIAL" AND p < 0.05:
    → WEAK (partial validation, acknowledge limitations)
    
ELIF test_validity == "INVALID":
    → FAIL (test not applicable, pivot to ISM scan)
    
ELSE:
    → FAIL (null result, document honestly)
```

---

## Expected Outcomes

### Scenario A: Mechanism Specificity Confirmed ✅

**Results:**
- MLH1 (regulatory): PASS, p<0.01
- TERT (regulatory): PASS, p<0.01
- GJB2 (coding): FAIL, p>0.4

**Interpretation:** AlphaGenome CAGE mechanism-specific, generalizes across loci.

**Next steps:**
- Manuscript submission: "AlphaGenome CAGE for Regulatory Variant Prioritization"
- Target: Bioinformatics, NAR Genomics
- Cross-modality validation (ATAC + RNA-seq)

---

### Scenario B: TERT Fails (Unexpected) ⚠️

**Results:**
- MLH1: PASS
- TERT: FAIL (p>0.05)
- GJB2: FAIL (expected)

**Possible explanations:**
1. TERT promoter mutations are position-specific (C228T, C250T hotspots) → ISM scan needed
2. Cell-type mismatch (K562 not cancer cells)
3. CAGE prediction inaccurate for TERT locus

**Next steps:**
- ISM scan on TERT promoter (-500 to +100 bp)
- Check if C228T, C250T are in hotspots
- If ISM PASS → positional specificity, not locus failure

---

### Scenario C: MLH1 Fails (Contradicts HBB Result) ❌

**Results:**
- MLH1: FAIL (but p=0.022 in cross-locus analysis?)
- Contradiction detected

**Possible explanations:**
1. Cross-locus analysis used wrong control set
2. MLH1 data contaminated
3. AlphaGenome CAGE prediction error

**Next steps:**
- Re-verify MLH1 data source
- Re-run cross-locus analysis from raw data
- Check for data integrity issues
- Document as falsification if confirmed

---

## Timeline

**Estimated:** 2-3 days (data already exists, no API calls)

| Day | Task | Deliverables |
|-----|------|--------------|
| **Day 1** | Load data, run MLH1 validation | ADR-029_MLH1_cage_validation.md |
| **Day 2** | Run GJB2, TERT validations | ADR-030_GJB2.md, ADR-031_TERT.md |
| **Day 3** | Cross-locus summary, mechanism analysis | cross_locus_summary.md |

**Total cost:** $0 (data cached)

---

## Success Metrics

### Primary Metric: Mechanism Specificity Confirmed

**Definition:** ≥2/2 regulatory loci PASS, 0/1 coding locus PASS

**Threshold:**
- Regulatory loci: p<0.01, test_validity ∈ {VALID, PARTIAL}
- Coding locus: p>0.05 (null result expected)

**If achieved:** Publish as "AlphaGenome CAGE validated for regulatory variant prioritization"

---

### Secondary Metric: Test Validity Distribution

**Question:** What fraction of loci have PARTIAL validity (insufficient controls)?

**HBB example:** 15/20 pearls skipped (PARTIAL)

**Expected:**
- MLH1: VALID (sufficient promoter controls)
- GJB2: VALID or PARTIAL (missense controls abundant)
- TERT: PARTIAL (promoter hotspot, few controls)

**Insight:** If >50% loci are PARTIAL → ag-falsifier critical for honest reporting.

---

## Integration with ag-falsifier

### New Feature: Multi-Locus Batch Validation

```python
from ag_falsifier import MultiLocusValidator

loci = ['MLH1', 'GJB2', 'TERT']
validator = MultiLocusValidator(loci=loci, api_key='...')

results = validator.batch_validate(
    modality='CAGE',
    category_matched=True,
    n_permutations=10000
)

# Generate cross-locus summary
results.to_summary(path='docs/cross_locus_summary.md')
results.to_figure(path='figures/cross_locus_cage_validation.png')
```

**Implementation:** ag-falsifier v0.2.0 (beta release, June 2026)

---

## Falsification-First Checkpoints

### Checkpoint 1: Before Starting

**Question:** "What would falsify mechanism specificity hypothesis?"

**Answer:** If ≥1 coding locus PASS OR ≥1 regulatory locus FAIL (excluding PARTIAL).

---

### Checkpoint 2: After MLH1

**If MLH1 FAIL:**
- STOP expansion
- Re-verify HBB result (possible data error)
- Document contradiction in ADR

---

### Checkpoint 3: After All Loci

**If mechanism hypothesis falsified:**
- Document null result honestly
- Re-frame as "AlphaGenome CAGE locus-specific, not mechanism-general"
- Pivot to ISM-based functional hotspot discovery

---

## Deliverables

### Per Locus (3×)
1. ADR-029_MLH1_cage_validation.md
2. ADR-030_GJB2_cage_validation.md
3. ADR-031_TERT_cage_validation.md

### Cross-Locus Summary (1)
4. cross_locus_summary.md
   - Mechanism specificity verdict
   - Test validity distribution
   - Figure: barplot (regulatory vs coding)

### ag-falsifier Enhancement (optional)
5. MultiLocusValidator class (beta feature)

---

## Risk Mitigation

### Risk 1: Data Quality

**Risk:** ClinVar annotations incorrect (misclassified variants)

**Mitigation:**
- Filter to ≥2★ review status
- Cross-check with ClinGen, HGMD
- Document review status in ADR

---

### Risk 2: Cell-Type Mismatch

**Risk:** K562 (myeloid) not representative for MLH1 (colon), TERT (cancer)

**Mitigation:**
- Acknowledge limitation in ADR
- Cite as "K562-specific validation, cell-type generalization unknown"
- Future: test on primary cell types (if AlphaGenome adds)

---

### Risk 3: Category Leakage

**Risk:** Regulatory loci PASS because all pathogenic are promoter category

**Mitigation:**
- ag-falsifier category-matched test detects this automatically
- If test_validity=PARTIAL → honest disclosure
- Cross-locus summary reports PARTIAL fraction

---

## Pivot Strategies

### If Mechanism Hypothesis Falsified

**Pivot 1:** ISM-based functional hotspot discovery
- Drop "mechanism-general" claim
- Focus on "AlphaGenome ISM identifies functional hotspots"
- Validate on TERT C228T, C250T hotspots

**Pivot 2:** AlphaGenome + ARCHCODE orthogonality
- Frame as complementary tools (3D + function)
- Multi-modality concordance (CAGE + ATAC + RNA-seq)

**Pivot 3:** Locus-specific validation platform
- Each locus validated independently
- No generalization claim
- Honest limitation: "HBB works, generalization unknown"

---

## Next Steps (Immediate)

1. **Load cross-locus data** (alphagenome_batch_cage_9loci.json)
2. **Run MLH1 validation** (ag-falsifier, save ADR-029)
3. **Check result:**
   - If PASS → continue to GJB2, TERT
   - If FAIL → STOP, verify HBB data integrity

---

**Version History:**
- v1.0 (2026-05-08): Initial plan, 3 loci (MLH1, GJB2, TERT)

---

_"Falsification checkpoints prevent sunk cost fallacy. STOP ≠ FAIL."_
