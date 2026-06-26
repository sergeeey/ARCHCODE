---
experiment: exp_archcode_sv
date: 2026-06-26
ladder_tier: Standard
question_type: Predictive
status: COMPLETE — 12/12 ✅
---

# Claim: ARCHCODE-SV correctly classifies TAD boundary-disrupting SVs

## EstimandOps L0

**Question type:** Predictive  
→ "Does boundary_ratio > 1.35 correctly predict whether an SV disrupts a TAD boundary?"

**Population:** Published structural variants (deletions/inversions) at CTCF-defined TAD boundaries,
from independent literature sources (Lupiáñez 2015, Benko 2011, Williamson 2019/PPD).

**Intervention:** Structural variant (deletion/inversion/duplication) applied to ENCODE K562 CTCF data.

**Comparator:** WT contact matrix (same locus, no SV).

**Endpoint:** boundary_ratio = cross_boundary_contacts(mut) / cross_boundary_contacts(wt)
at the CTCF site with largest score change.

**Summary measure:** Classification accuracy (N correct / N total).

**MCID:** ≥ 75% accuracy across ≥ 3 independent loci on ≥ 3 chromosomes.
Below 75% = algorithm fails; above 75% = proof-of-concept.

**ICE:** None applicable (in silico experiment, no dropouts).

## Falsifiable Claim

> ARCHCODE-SV boundary_ratio > 1.35 correctly classifies the pathogenic/benign status
> of structural variants across ≥ 3 independent genomic loci on different chromosomes,
> achieving ≥ 75% accuracy WITHOUT any training on the test loci.

**Null hypothesis (to falsify):** Algorithm performs at chance (50%) or below.

## Natural Language Statement

We predict whether boundary_ratio > 1.35 correctly classifies each SV as DISRUPTED
(pathogenic, removes strong CTCF) or INTACT (benign, avoids strong CTCF),
comparing mutant vs wildtype contact matrices derived from Kramer loop extrusion physics
applied to ENCODE K562 hg38 CTCF peaks.

## What this does NOT mean

1. Does NOT mean ARCHCODE-SV is a clinical-grade pathogenicity predictor.
2. Does NOT apply to SVs whose pathogenicity is due to enhancer loss (not TAD boundary disruption).
3. Does NOT generalize to non-K562 cell types or non-CTCF TAD mechanisms.
4. Does NOT validate on real patient outcomes — only matches literature-derived classification.

---

## Test Matrix (pre-registered before running)

| SV | Chromosome | Type | Expected | Basis |
|---|---|---|---|---|
| Pathogenic_boundary | chr2 | deletion | DISRUPTED | Lupiáñez 2015, Cell |
| Pathogenic_large | chr2 | deletion | DISRUPTED | Lupiáñez 2015, Cell |
| Benign_internal | chr2 | deletion | INTACT | Lupiáñez 2015, Cell |
| Benign_downstream | chr2 | deletion | INTACT | Lupiáñez 2015, Cell |
| Pathogenic_inversion | chr2 | inversion | DISRUPTED | Lupiáñez 2015, Cell |
| Path_SOX9_boundary | chr17 | deletion | DISRUPTED | Benko 2011, Nat Genet |
| Path_SOX9_large | chr17 | deletion | DISRUPTED | Benko 2011, Nat Genet |
| Ben_SOX9_desert | chr17 | deletion | INTACT | Benko 2011 + CTCF landscape |
| Ben_SOX9_inv | chr17 | inversion | INTACT | CTCF landscape (no boundary) |
| Path_SHH_boundary | chr7 | deletion | DISRUPTED | Boundary disruption mechanism (Lettice 2003, Anderson 2014) |
| Ben_SHH_desert | chr7 | deletion | INTACT | SHH-ZRS CTCF desert: chr7:156.16-156.47 Mb (317 kb, 0 peaks) |
| Ben_SHH_gap | chr7 | deletion | INTACT | SHH TAD internal gap: chr7:155.45-155.52 Mb (70 kb, 0 peaks) |

Total: 12 SVs, 3 chromosomes (chr2, chr7, chr17), 3 SV types.

**Go criterion:** ≥ 9/12 correct (75%) → PROMOTE
**No-go criterion:** < 9/12 correct → REPEAT with threshold tuning or REJECT

---

## Controls

See controls.md.

---

## Parameters (locked pre-run)

```python
CTCF_BED    = "data/input/ctcf/K562_CTCF_hg38.bed"  # ENCODE ENCFF736NYC
K_BASE      = 0.05   # Kramer kinetics base rate
ALPHA       = 0.92   # pausing strength
GAMMA       = 0.80   # loop extension
RESOLUTION  = 5000   # 5kb bins
N_BINS      = 200    # 1Mb window
THRESHOLD   = 1.35   # boundary_ratio cutoff
WINDOW_PAD  = 400_000  # ±400kb around SV
```

All parameters were set BEFORE this experiment. No post-hoc tuning allowed.
