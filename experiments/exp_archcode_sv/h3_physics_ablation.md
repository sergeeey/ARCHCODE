# H3 Ablation — Does the physics layer (Step 0) carry independent signal?

**Date:** 2026-07-01
**Evidence:** [VERIFIED-REAL] computed directly from `clinvar_independent_results.json` + re-scored via `archcode_sv.score_sv()`

---

## Hypothesis (from boyko-method audit, 2026-07-01)

H3: If ARCHCODE-SV's boundary-physics signal (Kramer kinetics, `boundary_ratio > 1.35`) carries real
discriminative information independent of the gene-constraint gating layer (Step +1/+2), then Step 0
alone should show meaningful discrimination (Youden J significantly > 0) on the independent
20-chromosome validation set.

## Result: REJECTED

| Sample | n | TP | FN | FP | TN | Recall | FPR | Youden J |
|--------|---|----|----|----|----|--------|-----|----------|
| Calibration (chr2/7/17, in-sample) | 50 | 19 | 6 | 20 | 5 | 0.760 | 0.800 | **-0.040** |
| Validation (20 chroms, out-of-sample) | 44 | 12 | 10 | 11 | 11 | 0.545 | 0.500 | **+0.045** |

Youden J = Recall - FPR. J=0 means the classifier performs identically to random guessing.
Both calibration and validation Youden J are statistically indistinguishable from zero.

### Direct distribution check

```
boundary_ratio, independent validation set (n=44):
  Pathogenic (n=22): mean=1.422, median=1.389
  Benign     (n=22): mean=1.428, median=1.333
  Welch t-statistic: t=-0.048 (not significant; |t|>2 needed at this n)
```

The physics-computed `boundary_ratio` shows **no separation** between pathogenic and benign SVs —
not on calibration data, not on validation data. It is a near-universal trigger (fires on ~80% of
deletions/inversions in the 50-400kb size range regardless of pathogenicity), not a discriminative
signal.

## Implication

All of the classifying power in Step +2 (FPR 8% in-sample / 22.7% out-of-sample) comes from the
gene-constraint gating layer (`find_hi_genes_step2`: gnomAD pLI/LOEUF thresholds + CTCF-adjacency
"same TAD" heuristic) — **not** from the physics-flavored contact-matrix / boundary-ratio computation.

The "physics-based" framing for ARCHCODE-SV is **not supported** by this analysis. A more accurate
description: "gnomAD gene-constraint classifier with a CTCF-adjacency filter, using
boundary-disruption as a non-discriminative pre-gate that does not itself add classification value."

## Required correction

Paper 3 §3.7 MUST NOT claim the loop-extrusion physics contributes to classification accuracy without
citing this ablation. If a physics contribution is claimed, it requires a demonstration that Step 0
alone outperforms random on some dataset — none exists as of this writing.

## What this does NOT mean

1. Does NOT mean CTCF ChIP-seq data is useless — it IS used, just as a binary "is there a barrier"
   gate inside Step +2's gene-search logic, not via the boundary_ratio physics score.
2. Does NOT mean the loop-extrusion simulator (`simulate_contact_matrix`, Kramer kinetics) is
   mathematically wrong — only that its output (`boundary_ratio`) does not correlate with
   ClinVar pathogenicity labels in this size range (50-400kb) and gene set.
3. Does NOT rule out physics signal existing at a different threshold, SV size range, or with
   tissue-specific (non-K562) CTCF data — untested.
