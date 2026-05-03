# Matched Control Plan

**Branch:** `experiment/spectral-collapse-pilot`  
**Date:** 2026-05-03  
**Scope:** robustness checks for the HBB spectral-collapse pilot, with BRCA1/TP53 negative comparison

## Goal

Test whether the HBB spectral-collapse signal survives simple matched-control perturbations instead of disappearing under thresholding, window shifts, coverage loss, or graph nulls.

## Frozen Inputs

- HBB contact matrices: `results/contact_matrices/30KB`
- HBB pilot results: `results/sfi_30kb_pilot_recheck.csv`
- HBB atlas: `results/HBB_Unified_Atlas.csv`
- BRCA1 full spectral output: `results/sfi_brca1_all.csv`
- BRCA1 atlas: `results/BRCA1_Unified_Atlas_brca1.csv`
- TP53 full spectral output: `results/sfi_tp53_all.csv`
- TP53 atlas: `results/TP53_Unified_Atlas_tp53.csv`

## HBB Robustness Tests

1. Baseline HBB pilot.
2. Threshold sensitivity.
3. Window-size sensitivity.
4. Coverage/downsampling control.
5. Degree-preserving random graph null.
6. Weight-shuffled null graph.

## Negative Comparison

Use existing BRCA1 and TP53 full-locus spectral outputs to verify that the HBB signal is not a generic property of all loci.

BRCA1 should remain near-null on spectral metrics. TP53 may show a weaker, broader structural signal but should not match HBB.

## Kill / Continue Criteria

Continue if:

- HBB remains separated from matched benign controls after threshold, window, and coverage perturbations.
- Degree-preserving and weight-shuffled nulls collapse or substantially weaken the signal.
- BRCA1 stays near-null.

Downgrade if:

- HBB separation vanishes under simple coverage/window corrections.
- Randomized graph nulls reproduce the same effect size.
- BRCA1 behaves like HBB.

## Output Files

- `results/spectral_collapse/matched_control_results.csv`
- `results/spectral_collapse/matched_control_summary.json`
- `results/spectral_collapse/MATCHED_CONTROL_REPORT.md`

