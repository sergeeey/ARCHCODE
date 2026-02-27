# Real Data Replacement Plan — AlphaGenome → SpliceAI

**Status:** 🟡 Ready to execute (at home with good internet)
**Duration:** 2-3 hours (mostly download time)
**Output:** Real clinical validation replacing mock data

---

## TIMELINE

### Tonight (at home, 1-2 hours)

**Step 1: Environment Setup (10 min)**

```bash
cd D:\ДНК

# Install SpliceAI
pip install spliceai

# Verify installation
python -c "from spliceai.utils import get_delta_scores; print('✅ SpliceAI OK')"
```

**Step 2: Download ClinVar VCF (30-60 min, leave running)**

```bash
# Download ClinVar variants (~1 GB compressed)
curl -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz

# Decompress (~3 GB uncompressed)
gunzip clinvar.vcf.gz

# Extract HBB locus only (chr11:5,225,464-5,227,071)
grep -E '^11\s+(522[5-7][0-9]{3})' clinvar.vcf > hbb_clinvar.vcf

# Count HBB variants
wc -l hbb_clinvar.vcf
# Expected: 300-500 variants
```

**Step 3: Download Reference Genome (30-60 min, can run parallel)**

```bash
# hg38 reference for SpliceAI (~900 MB compressed)
wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
gunzip hg38.fa.gz

# Verify
ls -lh hg38.fa
# Expected: ~3 GB
```

---

### Tomorrow Morning (30 min)

**Step 4: Parse ClinVar Variants**

```bash
python scripts/fetch_real_clinvar_hbb.py --vcf hbb_clinvar.vcf --output data/hbb_real_clinvar_variants.csv

# Verify output
head data/hbb_real_clinvar_variants.csv
wc -l data/hbb_real_clinvar_variants.csv
```

**Expected output format:**

```csv
chr,position,ref,alt,clinvar_id,significance,variant_type
11,5225464,C,T,VCV000000020,Pathogenic,missense
11,5225465,G,A,VCV000000274,Likely_pathogenic,promoter
...
```

---

### Tomorrow Afternoon (20-40 min)

**Step 5: Run SpliceAI Predictions**

```bash
python scripts/run_spliceai_hbb.py \
    --variants data/hbb_real_clinvar_variants.csv \
    --reference hg38.fa \
    --output data/hbb_spliceai_results.csv

# Expected duration: 10-30 minutes for 300-500 variants
```

**Expected output:**

```csv
clinvar_id,position,spliceai_score,acceptor_gain,acceptor_loss,donor_gain,donor_loss,interpretation
VCV000000020,5225464,0.82,0.01,0.82,0.03,0.12,Very High Impact
VCV000000274,5225465,0.45,0.15,0.30,0.05,0.10,Moderate Impact
...
```

---

### Tomorrow Evening (1 hour)

**Step 6: Merge with ARCHCODE Results**

```python
# In Python
from scripts.run_spliceai_hbb import merge_with_archcode_results

merge_with_archcode_results(
    archcode_file='results/HBB_Clinical_Atlas.csv',  # OLD (with mock AlphaGenome)
    spliceai_file='data/hbb_spliceai_results.csv',   # NEW (real SpliceAI)
    output_file='results/HBB_Clinical_Atlas_REAL.csv'  # UPDATED
)
```

**Expected concordance:**

- High concordance (>70%) → ARCHCODE validated!
- Moderate (50-70%) → Complementary (structure vs sequence)
- Low (<50%) → Investigate discordance patterns

---

## STEP 7: Update Manuscript (30 min)

### Files to Update (10 files)

**Priority 1: Core Results**

1. `results/HBB_Clinical_Atlas.csv` → Replace with REAL data
2. `manuscript/RESULTS.md` → Update concordance stats
3. `manuscript/ABSTRACT.md` → Change "AlphaGenome" → "SpliceAI"

**Priority 2: Methods** 4. `manuscript/METHODS.md` → Add SpliceAI section, remove AlphaGenome mock 5. `manuscript/SUPPLEMENTARY_TABLE_S1.md` → Update variant details

**Priority 3: Other Sections** 6. `manuscript/INTRODUCTION.md` → Remove AlphaGenome references 7. `manuscript/DISCUSSION.md` → Update with real concordance 8. `manuscript/ACKNOWLEDGMENTS.md` → Add SpliceAI citation 9. `FALSIFICATION_REPORT.md` → Mark Audit Point 10 as RESOLVED 10. `PROJECT_PLAN_OPTION_B.md` → Update status

---

## STEP 8: Key Manuscript Changes

### ABSTRACT.md

**OLD (Mock):**

```markdown
We compared ARCHCODE structural predictions with AlphaGenome
expression-based predictions to identify systematic discordance patterns.
```

**NEW (Real):**

```markdown
We compared ARCHCODE structural predictions with SpliceAI
sequence-based splice impact scores for 366 pathogenic HBB variants,
demonstrating XX% concordance and identifying structural mechanisms
missed by sequence analysis alone.
```

### METHODS.md

**REMOVE:**

```markdown
### AlphaGenome Predictions

AlphaGenome predictions from DeepMind's transformer-based model...
```

**ADD:**

````markdown
### SpliceAI Splice Impact Prediction

We used SpliceAI (v1.3.1; Jaganathan et al. 2019, Cell) to predict
splice-altering impact for each HBB variant. SpliceAI computes delta
scores (Δ) for acceptor/donor gain/loss within ±50 nt of each variant.

**Interpretation thresholds:**

- Δ > 0.8: Very high impact
- Δ 0.5-0.8: High impact
- Δ 0.2-0.5: Moderate impact
- Δ < 0.2: Low impact

**Reference genome:** GRCh38 (hg38.fa)
**Command:**

```bash
spliceai -I variants.vcf -O predictions.vcf -R hg38.fa -A grch38
```
````

Variants were classified as splice-altering if max(Δ) > 0.5.

````

### RESULTS.md

**Update concordance section:**
```markdown
### Comparison with Sequence-Based Prediction (SpliceAI)

We compared ARCHCODE structural predictions with SpliceAI splice
impact scores across 366 pathogenic HBB variants:

**Concordance:** XX% (YYY/366 variants)
- Both pathogenic: ZZZ variants (structural + splice defect)
- ARCHCODE only: AAA variants (structural mechanism, normal splice)
- SpliceAI only: BBB variants (splice defect, stable structure)

**Key findings:**
1. High concordance validates structural-functional link
2. ARCHCODE-only variants suggest loop-mediated transcriptional defects
3. SpliceAI-only variants suggest compensatory structural changes

[Figure: Scatter plot ARCHCODE SSIM vs SpliceAI Δscore]
````

---

## EXPECTED OUTCOMES

### Scenario 1: High Concordance (>70%)

**Interpretation:** ARCHCODE validated! Structural changes correlate with splice defects.
**Manuscript claim:** "Structural predictions concordant with splice impact (XX% agreement)"

### Scenario 2: Moderate Concordance (50-70%)

**Interpretation:** Complementary! Structure and sequence capture different mechanisms.
**Manuscript claim:** "ARCHCODE identifies structural mechanisms orthogonal to sequence-based prediction"

### Scenario 3: Low Concordance (<50%)

**Interpretation:** Investigate! Either ARCHCODE miscalibrated or splice != structure.
**Action:** Deep dive into discordant cases, check if CTCF/loop predictions correct.

---

## VERIFICATION CHECKLIST

Before updating manuscript:

- [ ] **Data integrity:** 366 variants (no duplicates, all HBB locus)
- [ ] **Score range:** SpliceAI Δ scores 0-1 (not NaN/inf)
- [ ] **Pathogenicity:** ClinVar significance = Pathogenic/Likely pathogenic
- [ ] **Concordance:** Calculated both ways (ARCHCODE→SpliceAI and SpliceAI→ARCHCODE)
- [ ] **Reference:** Jaganathan et al. 2019, Cell (doi:10.1016/j.cell.2018.12.015) cited
- [ ] **Reproducibility:** Commands documented, data/code in GitHub

---

## FALLBACK OPTIONS

### If SpliceAI installation fails:

**Alternative:** Use CADD scores (pre-computed, download only)

```bash
wget https://krishna.gs.washington.edu/download/CADD/v1.6/GRCh38/whole_genome_SNVs.tsv.gz
tabix -p vcf whole_genome_SNVs.tsv.gz 11:5225464-5227071
```

### If ClinVar download too slow:

**Alternative:** Use smaller subset (top 100 pathogenic variants)

- Still sufficient for validation
- Faster download/processing
- Update manuscript: "100 high-confidence pathogenic variants"

### If hg38 download fails:

**Alternative:** Use chr11 only

```bash
wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/chromosomes/chr11.fa.gz
```

---

## SUCCESS CRITERIA

✅ **Minimum Viable:**

- 100+ real ClinVar HBB variants analyzed
- SpliceAI scores computed successfully
- Concordance rate calculated
- Manuscript updated with real data

✅ **Target:**

- 300+ variants (comprehensive)
- Concordance >60%
- Publication-ready figures
- Reproducible workflow documented

✅ **Stretch:**

- All 366+ ClinVar HBB variants
- Concordance >70%
- Discordance analysis (structure-only vs splice-only)
- Preprint submission ready

---

## ESTIMATED EFFORT

| Task                 | Time          | When                    |
| -------------------- | ------------- | ----------------------- |
| Setup + Downloads    | 1-2 hours     | Tonight (leave running) |
| ClinVar parsing      | 30 min        | Tomorrow AM             |
| SpliceAI predictions | 30 min        | Tomorrow PM             |
| Merge + analysis     | 30 min        | Tomorrow PM             |
| Manuscript updates   | 1 hour        | Tomorrow evening        |
| **Total**            | **3-4 hours** | **Over 2 days**         |

---

**Status:** 🚀 Ready to execute!
**Next action:** Tonight at home → Install SpliceAI → Start downloads
**Blocker removed:** No more mock data, real validation incoming!

---

_Real Data Replacement Plan_
_Created: 2026-02-05_
_Replaces: Mock AlphaGenome (Audit Point 10 FALSIFIED)_
_Tool: SpliceAI v1.3.1 (Jaganathan et al. 2019, Cell)_
