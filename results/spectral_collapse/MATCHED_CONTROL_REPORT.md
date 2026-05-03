# Matched Control Report

**Date:** 2026-05-03
**Branch:** `experiment/spectral-collapse-pilot`

## HBB Baseline

- Pearls: 20
- Benign controls: 25
- SFI p-value: 0.00020453214097175136
- Spectral gap p-value: 6.67538766891713e-05

## Transform Sensitivity

- baseline: pearls_mean_SFI=0.322201 benign_mean_SFI=0.117105 p=0.00020453214097175136
- threshold_keep_0.75: pearls_mean_SFI=0.300962 benign_mean_SFI=0.106547 p=9.772858283377435e-05
- threshold_keep_0.50: pearls_mean_SFI=0.408135 benign_mean_SFI=0.130444 p=1.0880402969921667e-05
- window_40: pearls_mean_SFI=0.549331 benign_mean_SFI=0.220680 p=2.966719011573052e-06
- window_30: pearls_mean_SFI=0.601408 benign_mean_SFI=0.211681 p=2.0069497413132658e-07
- coverage_keep_0.75: pearls_mean_SFI=0.764248 benign_mean_SFI=0.771946 p=0.6726091804237861
- coverage_keep_0.50: pearls_mean_SFI=1.002469 benign_mean_SFI=0.913051 p=0.5757390449173081
- degree_preserving_null: pearls_mean_SFI=1.019039 benign_mean_SFI=1.010660 p=0.9000257225381322
- weight_shuffled_null: pearls_mean_SFI=1.075383 benign_mean_SFI=1.058591 p=0.08881163592817248

## Negative Comparison

- BRCA1 control-category mean SFI: 0.006514469674398899
- TP53 control-category mean SFI: 0.1397399700878832

## Decision

- Continue: False
- Reason: HBB survives baseline and threshold/window perturbations, but coverage/downsampling controls erase the separation, so the spectral-collapse interpretation remains unresolved.
