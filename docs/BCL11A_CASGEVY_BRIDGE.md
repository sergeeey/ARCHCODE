# BCL11A / Casgevy Bridge

**Canon Tier:** Technical Full-Scope  
**Release-facing:** No  
**Status:** Technical Current  
**Scope:** Translational bridge candidate after Canonical Core freeze

## Purpose

This document packages the current BCL11A evidence into one technical surface without promoting it
into the public canonical layer.

The goal is narrower than "ARCHCODE predicted Casgevy." The current evidence supports a more
defensible statement:

- within the known BCL11A erythroid enhancer complex, ARCHCODE recapitulates the experimentally
  established sensitivity ranking of the DHS elements
- the Casgevy-aligned DHS +58 element is the most structurally sensitive enhancer in the current
  focused model
- this is a translational bridge, not a clinical or guide-design claim

## Current Evidence Pack

### 1. Real ClinVar BCL11A remains coding-dominated

Real BCL11A ClinVar evidence exists, but it does not currently validate enhancer-space Class B
calls:

- [config/locus/bcl11a_300kb.json](../config/locus/bcl11a_300kb.json)
- [results/UNIFIED_ATLAS_SUMMARY_BCL11A_300kb.json](../results/UNIFIED_ATLAS_SUMMARY_BCL11A_300kb.json)
- [config/locus/bcl11a_erythroid_95kb.json](../config/locus/bcl11a_erythroid_95kb.json)
- [results/UNIFIED_ATLAS_SUMMARY_bcl11a_erythroid.json](../results/UNIFIED_ATLAS_SUMMARY_bcl11a_erythroid.json)

Confirmed from the current structured summaries:

- `93` ClinVar variants in the broad 300 kb BCL11A locus config
- `182` variants in the focused erythroid 95 kb atlas
- `0` structural pathogenic calls
- `0` pearls

Interpretation:

- BCL11A is useful as a translational bridge because the enhancer biology is strong
- BCL11A is not yet a second public-canonical Class B locus because the real clinical variants do
  not populate the enhancer hotspot

### 2. Synthetic mutagenesis identifies DHS +58 as the most sensitive enhancer

The focused bridge signal comes from the synthetic mutagenesis pack:

- [scripts/bcl11a_in_silico_mutagenesis.py](../scripts/bcl11a_in_silico_mutagenesis.py)
- [data/SYNTHETIC_bcl11a_erythroid_mutagenesis.csv](../data/SYNTHETIC_bcl11a_erythroid_mutagenesis.csv)
- [results/BCL11A_Unified_Atlas_bcl11a_mutagenesis.csv](../results/BCL11A_Unified_Atlas_bcl11a_mutagenesis.csv)
- [results/UNIFIED_ATLAS_SUMMARY_bcl11a_mutagenesis.json](../results/UNIFIED_ATLAS_SUMMARY_bcl11a_mutagenesis.json)

The current mutagenesis atlas contains `314` synthetic SNVs across DHS +55, DHS +58, DHS +62,
CTCF sites, the promoter, and background positions.

Enhancer-level structural sensitivity ranking in the focused erythroid model:

- `DHS +58 / Casgevy-aligned enhancer`: mean `LSSIM = 0.9660`, minimum `0.9632`
- `DHS +55`: mean `LSSIM = 0.9784`, minimum `0.9764`
- `DHS +62`: mean `LSSIM = 0.9840`, minimum `0.9818`

The nearest synthetic variant to the Casgevy guide target at `chr2:60,495,279` has
`LSSIM = 0.9639`, placing it inside the most disrupted enhancer cluster in the current model.

### 3. Important non-claim: promoter positions are even more sensitive globally

The current focused model does **not** support the stronger claim that DHS +58 is the single most
sensitive position in the entire 95 kb window.

From the same mutagenesis atlas:

- `Promoter mean LSSIM = 0.9518`
- `Promoter minimum LSSIM = 0.9400`
- `Background mean LSSIM = 0.9954`

So the correct interpretation is:

- DHS +58 is the most sensitive *enhancer* in the known BCL11A erythroid enhancer complex
- the promoter remains more sensitive than enhancer positions in absolute LSSIM terms
- the bridge value is enhancer prioritization within a validated therapeutic region, not de novo
  CRISPR target discovery across the whole locus

## Why This Is Still the Right Next Bridge

BCL11A remains the best next technical bridge after the HBB-centered public core because:

- it stays in the erythroid domain, so it does not force a new tissue system prematurely
- the enhancer biology is externally validated and translationally relevant
- the Casgevy connection gives a concrete downstream use-case without forcing ARCHCODE to claim
  clinical prediction
- it can remain fully in the technical layer until stronger orthogonal validation exists

## Explicit Non-Claims

This bridge pack does **not** claim:

- that ARCHCODE independently discovered the Casgevy target
- that BCL11A is already a second public-canonical validated Class B locus
- that the current focused model is a CRISPR guide-design engine
- that synthetic mutagenesis alone justifies clinical or therapeutic ranking

## Evidence Gaps To Close Next

The following items are intentionally left out of the current bridge summary unless they are
surfaced as dedicated tracked result artifacts:

- uniform-occupancy control
- GWAS/HbF comparison
- GATA1 motif-specific analysis
- orthogonal public 3D or perturbation benchmarks beyond the current literature-configured setup

## Recommended Next Step

Do not widen the public canon. Instead:

1. keep BCL11A as a technical-full-scope bridge
2. add any missing orthogonal validations as standalone tracked artifacts
3. promote only after a dedicated non-circularity pack exists
