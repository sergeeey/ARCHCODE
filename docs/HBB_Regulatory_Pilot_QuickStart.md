# HBB Regulatory Pilot — Quick Start Guide

**Goal:** Execute 2-week pilot in 4 commands

---

## Step 1: Query gnomAD (Day 1-2)

```python
# Install dependencies
pip install requests pandas

# Script: query_gnomad.py
import pandas as pd
import requests
import time

pilot = pd.read_csv('docs/HBB_Regulatory_Pilot_50_Enhanced.csv')

def query_gnomad(chrom, pos, ref, alt):
    """Query gnomAD v4.1 API for variant AF"""
    url = "https://gnomad.broadinstitute.org/api"
    query = """
    query Variant($variantId: String!) {
      variant(variantId: $variantId, dataset: gnomad_r4) {
        genome {
          ac
          an
          af
          af_afr
          af_eur
          af_eas
          af_sas
          hom_count
        }
      }
    }
    """
    
    variant_id = f"{chrom}-{pos}-{ref}-{alt}"
    response = requests.post(url, json={
        'query': query,
        'variables': {'variantId': variant_id}
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data', {}).get('variant'):
            return data['data']['variant']['genome']
    return None

# Query all variants
for idx, row in pilot.iterrows():
    print(f"Querying {idx+1}/50: {row['ClinVar_ID']}")
    
    af_data = query_gnomad(
        chrom='11',
        pos=row['Position_GRCh38'],
        ref=row['Ref'],
        alt=row['Alt']
    )
    
    if af_data:
        pilot.at[idx, 'gnomAD_AF_Global'] = af_data.get('af', 0)
        pilot.at[idx, 'gnomAD_AF_AFR'] = af_data.get('af_afr', 0)
        pilot.at[idx, 'gnomAD_AF_EUR'] = af_data.get('af_eur', 0)
        pilot.at[idx, 'gnomAD_Hom_Count'] = af_data.get('hom_count', 0)
    
    time.sleep(0.5)  # Rate limiting

pilot.to_csv('docs/HBB_Regulatory_Pilot_50_AF.csv', index=False)
print("✅ gnomAD data collected")
```

**Expected output:** `HBB_Regulatory_Pilot_50_AF.csv` with AF columns filled

---

## Step 2: Query AlphaGenome CAGE (Day 3-4)

```python
# Script: query_alphagenome.py
import pandas as pd
import requests

pilot = pd.read_csv('docs/HBB_Regulatory_Pilot_50_AF.csv')

# Filter: promoter + 5'UTR only (regulatory)
pilot_reg = pilot[pilot['Category'].isin(['promoter', '5_prime_UTR'])].copy()

def query_alphagenome_cage(chrom, pos, ref, alt):
    """Query AlphaGenome predict_variant API"""
    url = "https://api.alphagenome.com/v1/predict_variant"
    
    payload = {
        "genome": "hg38",
        "chromosome": chrom,
        "position": pos,
        "ref": ref,
        "alt": alt,
        "tracks": ["CAGE"]
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'cage_ref': data['tracks']['CAGE']['ref'],
            'cage_alt': data['tracks']['CAGE']['alt'],
            'cage_delta': data['tracks']['CAGE']['delta']
        }
    return None

# Query regulatory variants
for idx, row in pilot_reg.iterrows():
    print(f"Querying CAGE: {row['ClinVar_ID']}")
    
    cage_data = query_alphagenome_cage(
        chrom='chr11',
        pos=row['Position_GRCh38'],
        ref=row['Ref'],
        alt=row['Alt']
    )
    
    if cage_data:
        pilot.at[idx, 'AlphaGenome_CAGE_Effect'] = cage_data['cage_delta']

pilot.to_csv('docs/HBB_Regulatory_Pilot_50_Full.csv', index=False)
print("✅ AlphaGenome CAGE data collected")
```

**Note:** If AlphaGenome API unavailable, use local predictions from `results/alphagenome_batch_cage_9loci.json`

---

## Step 3: Detect Evidence Conflicts (Day 5)

```python
# Script: detect_conflicts.py
import pandas as pd

pilot = pd.read_csv('docs/HBB_Regulatory_Pilot_50_Full.csv')

def detect_conflicts(row):
    """Flag evidence conflicts"""
    conflicts = []
    
    # Conflict 1: High AF for "severe pathogenic"
    if row.get('gnomAD_AF_Global', 0) > 0.001:  # 0.1%
        conflicts.append('POP_FREQ_CONFLICT')
    
    # Conflict 2: Weak regulatory signal
    if (row['Category'] in ['promoter', '5_prime_UTR'] and
        abs(row.get('AlphaGenome_CAGE_Effect', 0)) < 0.05):
        conflicts.append('WEAK_REGULATORY_SIGNAL')
    
    # Conflict 3: Category artifact (low CADD, not pearl)
    if (row['Category'] == 'promoter' and
        row['CADD_Phred'] < 15 and
        row['Pearl'] == False):
        conflicts.append('CATEGORY_ARTIFACT')
    
    return conflicts

# Apply conflict detection
pilot['Conflict_Types'] = pilot.apply(
    lambda row: ', '.join(detect_conflicts(row)), 
    axis=1
)
pilot['Conflict_Score'] = pilot.apply(
    lambda row: len(detect_conflicts(row)), 
    axis=1
)

# Save
pilot.to_csv('docs/HBB_Regulatory_Evidence_Conflicts.csv', index=False)

# Summary
flagged = pilot[pilot['Conflict_Score'] > 0]
print(f"\n✅ Conflicts detected")
print(f"Total flagged: {len(flagged)}/50 ({len(flagged)/50*100:.1f}%)")
print(f"\nBy conflict type:")
print(pilot['Conflict_Types'].value_counts())
```

**Expected output:** `HBB_Regulatory_Evidence_Conflicts.csv` with conflict flags

---

## Step 4: Manual Review (Week 2)

```python
# Script: manual_review.py
import pandas as pd

conflicts = pd.read_csv('docs/HBB_Regulatory_Evidence_Conflicts.csv')
flagged = conflicts[conflicts['Conflict_Score'] > 0].copy()

print(f"Manual review required: {len(flagged)} variants\n")

for idx, row in flagged.iterrows():
    print(f"--- {row['ClinVar_ID']} ---")
    print(f"Category: {row['Category']}")
    print(f"HGVS: {row['HGVS_c']}")
    print(f"AF: {row.get('gnomAD_AF_Global', 'N/A')}")
    print(f"CAGE: {row.get('AlphaGenome_CAGE_Effect', 'N/A')}")
    print(f"Conflicts: {row['Conflict_Types']}")
    print(f"\nClinVar: https://www.ncbi.nlm.nih.gov/clinvar/variation/{row['ClinVar_ID'].split('VCV')[-1]}/")
    print(f"PubMed: https://pubmed.ncbi.nlm.nih.gov/?term={row['HGVS_c']}+AND+beta+thalassemia")
    print()
    
    # Manual input
    novel = input("Novel conflict? (y/n): ")
    verdict = input("Verdict (CONFIRMED/REFUTED/UNCERTAIN): ")
    notes = input("Notes: ")
    
    flagged.at[idx, 'Novel'] = (novel.lower() == 'y')
    flagged.at[idx, 'Audit_Verdict'] = verdict
    flagged.at[idx, 'Audit_Notes'] = notes

flagged.to_csv('docs/HBB_Regulatory_Conflicts_Reviewed.csv', index=False)

# Count novel
novel_count = flagged['Novel'].sum()
print(f"\n✅ Review complete")
print(f"Novel conflicts: {novel_count}/{len(flagged)}")
print(f"Precision: {novel_count/len(flagged)*100:.1f}%")

# Kill criterion check
if novel_count < 5:
    print("\n⚠️  KILL CRITERION TRIGGERED: <5 novel conflicts")
    print("Recommended: PIVOT to narrower scope or FREEZE")
else:
    print(f"\n✅ PASSED: {novel_count} ≥ 5 novel conflicts")
    print("Recommended: GO — draft grant proposal")
```

---

## Quick Stats (Current Cohort)

**File:** `docs/HBB_Regulatory_Pilot_50_Enhanced.csv`

```
Total variants:     50
Pathogenic:         50 (100%)
Categories:
  - Promoter:       15 (30%)
  - Splice donor:   22 (44%)
  - Splice region:   9 (18%)
  - Other:           4 (8%)

Pearl variants:     16 (32%)
Mean ARCHCODE LSSIM: 0.9257
Mean CADD:          18.3

Position range:     chr11:5,225,727-5,227,172 (1.4 kb span)
```

---

## Timeline

| Day | Task | Output |
|-----|------|--------|
| 1-2 | Query gnomAD | `*_AF.csv` |
| 3-4 | Query AlphaGenome | `*_Full.csv` |
| 5 | Detect conflicts | `*_Conflicts.csv` |
| 6-10 | Manual review | `*_Reviewed.csv` |
| 11-12 | Write report | `Pilot_Report.md` |
| 13-14 | Case studies | `Case_Studies.md` |

**Decision:** Day 14 (Friday Week 2)

---

## Kill Criterion

```
IF novel_conflicts < 5:
    STOP → pivot or freeze
    
IF precision < 20%:
    STOP → too many false positives
    
ELSE:
    GO → expand to 200 variants + grant
```

---

## Support

**Questions:** Check `HBB_Regulatory_Pilot_Protocol.md`  
**Issues:** GitHub repo (TBD)  
**Data:** `docs/HBB_Regulatory_Pilot_50_Enhanced.csv`
