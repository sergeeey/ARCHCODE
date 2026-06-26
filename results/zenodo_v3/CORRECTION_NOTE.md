# Zenodo Correction Note — ARCHCODE (v3)

**Record:** https://doi.org/10.5281/zenodo.18867448
**Date of correction:** 2026-06-05
**Author:** Sergey V. Boyko (sergeikuch80@gmail.com)

---

## Summary of corrections

This new version (v3) replaces the earlier deposited PDF/HTML (v1–v2, February–March 2026)
which contained the following errors:

### 1. Invalid / phantom reference (CRITICAL)
- **v1/v2 contained:** "fitted to experimental FRAP data (Sabaté et al., Nature Genetics 2025, DOI: 10.1038/s41588-025-02406-9)"
- **Fact:** This DOI returns 404. The paper does not exist. The parameters (α=0.92, γ=0.80) were manually calibrated to literature ranges, not fitted to experimental data.
- **v3 correction:** "manually calibrated to published literature ranges" with correct reference Sabaté et al. bioRxiv 2024 (DOI: 10.1101/2024.08.09.605990).

### 2. Clinical reclassification recommendation (CRITICAL)
- **v1/v2 contained:** "we propose reclassifying all three 'Loop That Stayed' variants from VUS to Likely Pathogenic"
- **Fact:** No ACMG-compliant functional evidence (PS3) was obtained. No wet-lab validation was performed.
- **v3 correction:** The claim is removed entirely. The correct framing is: these variants are computational hypotheses for experimental follow-up. Clinical reclassification requires experimental confirmation.

### 3. Overclaim about structural pathogenicity prediction (CRITICAL)
- **v1/v2 contained:** AUC 0.977 presented as evidence of independent structural pathogenicity prediction.
- **Fact:** Subsequent matched-control audit (June 2026) showed the AUC is a consequence-category distribution artifact. The naive Cohen's d (path vs benign LSSIM) collapses from −2.67 to −0.34 after category stratification. Within-category AUC (the only non-circular test) = 0.524 (intronic) and 0.570 (synonymous), both at chance (Mann–Whitney p > 0.67).
- **v3 correction:** The paper is reframed as a falsification-first audit framework. The headline is explicitly "LSSIM does not demonstrate independent pathogenicity signal under matched controls" rather than "ARCHCODE predicts pathogenicity."

### 4. AlphaGenome disclosure inconsistency (MAJOR)
- **v1/v2 contained:** Multiple contradictory statements: "excluded entirely" / "independently confirms" / "REAL SDK."
- **Fact:** AlphaGenome validation used a mock/synthetic implementation (`mode: 'mock'`, random number generator seeded by category).
- **v3 correction:** AlphaGenome results are excluded from all claims. Only the sequence comparison (Pearson r = 0.052, near-zero correlation) from the real API access is retained.

### 5. "Blind" validation not pre-registered (MAJOR)
- **v1/v2 stated:** "pre-registered blind validation"
- **Fact:** Parameters and results were committed in the same Git commit (2026-02-03, 5c061bc), with ~10 minutes difference. No pre-registration timestamp exists.
- **v3 correction:** Language changed to "computational validation."

---

## What is NOT changed

- The loop-extrusion simulation engine (working, correctly described)
- The ClinVar HBB variant dataset (real, correctly cited)
- The Hi-C correlation (r = 0.16, weak, honestly reported in v2+)
- The Zenodo DOI (same record, new version)
- The AI co-authorship disclosure in commit history

---

## Falsification audit context (June 2026)

After the March 2026 audit that produced the v2/v3 corrections, a further systematic falsification audit (June 2026) was conducted across five experiments:

1. HBB matched-control audit: headline AUC 0.977 → category-distribution artifact (d −2.67 → −0.34 stratified; within-cat AUC ≈ 0.52)
2. Regulatory-confound test: LSSIM ≈ f(category + CTCF distance); no residual 3D signal
3. BCL11A: failed as positive locus (position-matched controls: not_observed)
4. GATA1: FAIL_PROXY_ONLY; wrong-direction within missense (AUC 0.464); K562 tissue mismatch
5. HUDEP-2 real Hi-C (GSM4873116): FAILS_SAME_BIN; all HBB variants in single 5kb bin; analytical model r = 0.16 vs real Hi-C (p=0.30)

**The June 2026 audit confirms:** ARCHCODE/LSSIM does not demonstrate independent 3D chromatin pathogenicity signal in any of the five tested configurations. The contribution is reframed as a falsification framework — a systematic method for auditing chromatin-based variant scores under category, positional, tissue, and resolution controls.

All audit artifacts: https://github.com/sergeeey/ARCHCODE (results/p0_governance/ through results/p4_hudep2_hbb/).
