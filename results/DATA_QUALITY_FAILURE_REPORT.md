# DATA QUALITY FAILURE REPORT

**Date:** 2026-04-28  
**Discovery:** Skeptic agent audit  
**Severity:** CRITICAL — 92% gnomAD queries failed  

---

## Problem

All PyPop validation analysis results (today's session) are **INVALID** due to gnomAD API query failures.

### Data Quality Breakdown

| Status | Count | % | Validity |
|--------|-------|---|----------|
| **query_failed** | 91 | 72% | ❌ INVALID |
| **api_error** | 21 | 17% | ❌ INVALID |
| **NOT_QUERYABLE** | 5 | 4% | ❌ INVALID (multi-allelic) |
| **Valid responses** | **10** | **8%** | ✅ VALID |

**Total:** 127 variants, **only 10 valid** (7.9% success rate)

---

## Invalid Claims (ALL MUST BE RETRACTED)

### Claim 1: "85.1% pearls absent (103/121)"
- **Status:** INVALID
- **Reason:** 103/121 based on failed queries (query_failed/api_error), not real AC=0
- **True status:** UNKNOWN (need re-query)

### Claim 2: "100% HBB pearls absent (27/27)"
- **Status:** INVALID
- **Reason:** All 27 HBB pearls show query_failed or api_error
- **gnomAD_source breakdown:**
  - query_failed: 18/27 (67%)
  - api_error: 7/27 (26%)
  - NOT_QUERYABLE: 2/27 (7%)
  - Valid: 0/27 (0%)

### Claim 3: "Tissue-specificity validated (95% vs 74%, p=0.002)"
- **Status:** INVALID
- **Reason:** Both matched and mis-matched loci queries failed at ~90% rate

### Claim 4: "VEP/CADD miss 96% of ARCHCODE constraint"
- **Status:** PARTIALLY VALID
- **Reason:** VEP/CADD annotations independent of gnomAD
- **But:** Cannot confirm "constraint" without valid gnomAD data

---

## Root Cause Analysis

### Why did 92% queries fail?

**Hypothesis 1:** gnomAD GraphQL API rate limiting
- Used 0.5 sec delay (conservative)
- But API may have stricter limits for batch queries
- Result: Silent failures (returned AC=0, AF=0, AN=0 instead of error)

**Hypothesis 2:** Variant ID format mismatch
- Used chr-pos-ref-alt format (e.g., "chr11-5227002-G-A")
- gnomAD v4 may require different format (e.g., "11-5227002-G-A" without "chr" prefix)

**Hypothesis 3:** GRCh37 vs GRCh38 coordinate mismatch
- ClinVar variants in GRCh38
- gnomAD API queried in wrong assembly?

**Hypothesis 4:** Multi-allelic site handling
- 5/127 variants classified as NOT_QUERYABLE
- But many more may be multi-allelic, silently failing

---

## Methodology Error

**Failed gnomAD query was classified as AC=0 (absent):**

```python
# WRONG (current code):
if response.ac is None:
    status = "ABSENT"  # ❌ WRONG — this is query failure, not absence

# CORRECT:
if response.ac is None:
    status = "QUERY_FAILED"  # ✅ CORRECT — distinguish failure from absence
elif response.ac == 0:
    status = "ABSENT"  # ✅ CORRECT — real population absence
```

**This silently converted 112 failed queries into false "absent" classifications.**

---

## Files Affected (ALL INVALID)

| File | Status | Action |
|------|--------|--------|
| purifying_selection_analysis.json | ❌ INVALID | DELETE or QUARANTINE |
| multi_locus_purifying_selection.json | ❌ INVALID | DELETE or QUARANTINE |
| gnomad_all_groups.csv | ⚠️ PARTIAL (10/127 valid) | KEEP raw data for debugging |
| multi_locus_gnomad_data.csv | ❌ INVALID | DELETE or QUARANTINE |
| LD_ANALYSIS_HBB.md | ⚠️ SPATIAL CLUSTERING VALID | LD blocks valid, gnomAD claims invalid |
| ARCHCODE_VS_VEP_CADD.md | ⚠️ PARTIAL | VEP/CADD annotations valid, gnomAD comparison invalid |
| PYPOP_PAPER_DRAFT.md | ❌ INVALID | DELETE — cannot submit |
| PYPOP_VALIDATION_COMPLETE_REPORT.md | ❌ INVALID | DELETE — all claims wrong |

**Action:** Move all invalid files to `results/QUARANTINE/2026-04-28/`

---

## Correct Next Steps

### Step 1: Download gnomAD VCF (local query)

```bash
# Download gnomAD v4.1 VCF for HBB region (chr11:5,225,000-5,230,000)
gsutil cp gs://gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz .
gsutil cp gs://gcp-public-data--gnomad/release/4.1/vcf/genomes/gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi .

# Extract HBB region
tabix gnomad.genomes.v4.1.sites.chr11.vcf.bgz 11:5225000-5230000 > hbb_gnomad_v4.vcf
```

### Step 2: Re-query locally (VCF parsing)

```python
import pysam

vcf = pysam.VariantFile("hbb_gnomad_v4.vcf")

for variant in clinvar_variants:
    chrom, pos, ref, alt = variant.split("-")
    
    # Query VCF
    for record in vcf.fetch(chrom, int(pos)-1, int(pos)):
        if record.ref == ref and alt in record.alts:
            ac = record.info.get("AC", None)
            an = record.info.get("AN", None)
            af = record.info.get("AF", None)
            
            if ac is not None:
                status = "ABSENT" if ac == 0 else "PRESENT"
            else:
                status = "NOT_IN_GNOMAD"  # variant not in gnomAD v4
```

### Step 3: Re-calculate ALL statistics

- Multi-locus constraint (with REAL AC values)
- Tissue-specificity (with REAL AC values)
- VEP/CADD comparison (with REAL gnomAD absence)

### Step 4: ONLY THEN consider publication

**Estimated time:** 1-2 days (download VCF + re-query + re-analyze)

---

## Lessons Learned

1. **NEVER trust API without validation**
   - Spot-check 10-20 random variants via gnomAD browser
   - Compare API results to VCF download

2. **Distinguish "not found" from "absent"**
   - AC=null (not in database) ≠ AC=0 (in database, zero observations)
   - Query failure ≠ population absence

3. **Skeptic agent is MANDATORY before publication**
   - Skeptic caught 92% data quality failure
   - Would have led to retraction if submitted

4. **Zero-Based Thinking saves time**
   - Tracy wanted to create figures → would have wasted time on bad data
   - Skeptic audit first → saved 2-3 days of wasted work

---

## Credit

**Skeptic agent (afcb676fca6c1b022) saved the project from retraction.**

Falsification-first methodology works.

---

**Status:** PUBLICATION BLOCKED until gnomAD data fixed.  
**Next A1:** Download gnomAD VCF + re-query locally.  
**ETA:** 1-2 days to valid results.
