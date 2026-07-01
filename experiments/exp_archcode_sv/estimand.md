# Estimand — ARCHCODE-SV Step +2 (ClinVar gene-constraint classifier)

**Date:** 2026-07-01
**Ladder tier:** Full (upgraded from Standard — degradation pattern + research claim require it)
**Supersedes/extends:** `claim.md` (which covers only the original 12/12 curated-benchmark claim)

This estimand covers the SEPARATE, larger claim that grew out of the original 12/12 benchmark:
"ARCHCODE-SV Step +2 predicts ClinVar SV pathogenicity via gene-constraint + CTCF-adjacency
filtering." This claim was never formally pre-registered before the ClinVar work began — this
document is written retroactively, after results are known, and is explicitly marked as such.

## L0 — Question type

**Predictive.** "Given an SV's coordinates, does Step +2's rule (gnomAD LOEUF/pLI + CTCF-barrier
adjacency check) correctly predict ClinVar pathogenicity label?" Not causal (no claim about
mechanism being causally responsible beyond the disclosed H3 ablation finding), not purely
descriptive (used to classify held-out cases).

## L1 — Estimand attributes

- **Population:** ClinVar deletions/inversions, 50-400kb, strict Pathogenic/Benign (excludes VUS,
  conflicting, risk-factor), GRCh38, chromosomes 1-22+X.
- **Intervention:** Step +2 classifier — `find_hi_genes_step2()`: tier-1 body-overlap gene check
  (LOEUF≤0.80 or pLI≥0.9) OR tier-2 window check (±200kb, LOEUF≤0.35 or pLI≥0.9, gated by
  absence of a strong CTCF site (score≥50) between SV and gene).
- **Comparator:** ClinVar's own Pathogenic/Benign label (ground truth).
- **Endpoint:** Binary prediction (DISRUPTED_WITH_HI_GENE = predicted pathogenic) vs label.
- **Summary measure:** Recall, Precision, FPR (absolute proportions, not OR/HR — appropriate
  per estimand-ops.md noncollapsibility guidance for binary endpoints).
- **MCID:** FPR≤15% AND Recall≥65% (set 2026-06-26, before independent validation was run —
  this MCID was met in-sample but NOT met out-of-sample).
- **ICE:** None (no dropouts; every SV in the filtered set receives a prediction).

## Retroactive pre-registration disclosure (required — this estimand written after results known)

**This is a violation of proper estimand timing** per `estimand-ops.md` ("Estimand defined after
data access → STOP, mark exploratory only"). The MCID (FPR≤15%/Recall≥65%) WAS set before
seeing Step+2 results on 2026-06-26, but the specific thresholds inside Step +2
(`CTCF_BARRIER_SCORE=50`, `LOEUF_BODY=0.80`) were chosen by inspecting false positives/negatives
on the very same n=50 ClinVar set used to report the in-sample result — documented explicitly in
`clinvar_analysis.md:146-165`. This is fit-to-test-set, not blind calibration.

**Correct classification of the in-sample result:** EXPLORATORY, not confirmatory.

## Independent validation (the actual confirmatory test)

`scripts/clinvar_independent_validation.py` — frozen parameters, applied to chromosomes NOT in
the calibration set (all except chr2/chr7/chr17), n=44 (22 pathogenic + 22 benign).

**This is the estimand's real test of the pre-declared MCID.**

## Natural language statement (per estimand-ops.md requirement)

> We estimate Recall, Precision, and FPR of Step +2's binary pathogenicity prediction for
> ClinVar deletions/inversions (50-400kb) on chromosomes NOT used to select Step +2's internal
> thresholds, comparing prediction against ClinVar's own Pathogenic/Benign label, with no ICE
> (complete case classification).

## What this result does NOT mean

1. Does NOT mean the loop-extrusion physics layer (Step 0) contributes to this result — see
   [[archcode-sv-physics-null-h3]] / `h3_physics_ablation.md`: Step 0 alone shows Youden J≈0 on
   both calibration and validation. All discrimination comes from the gene-constraint layer.
2. Does NOT generalize to SV types outside deletion/inversion, sizes outside 50-400kb, or to
   duplications/translocations — untested.
3. Does NOT establish causality between CTCF-barrier absence and pathogenicity — this is a
   predictive classifier evaluation, not a causal claim.
4. Does NOT meet the pre-declared MCID (FPR≤15%/Recall≥65%) out-of-sample. In-sample result
   (FPR=8%/Recall=68%) met MCID but is confounded by fit-to-test-set threshold selection.

## Result (honest, in the estimand's own pre-declared terms)

| | In-sample (chr2/7/17, exploratory) | Out-of-sample (20 chroms, confirmatory) |
|---|---|---|
| n | 50 | 44 |
| FPR | 0.080 | 0.227 |
| Recall | 0.680 | 0.364 |
| Precision | 0.895 | 0.615 |
| Youden J | 0.600 | 0.137 |
| Meets MCID (FPR≤15% AND Recall≥65%)? | Yes (but exploratory, not valid confirmatory test) | **No** |

**Verdict per the classifier's own pre-declared MCID: NOT MET on the confirmatory (out-of-sample)
test.** J=0.137 out-of-sample indicates real but modest signal (not zero, not random) — see
decision.md addendum for the go/no-go/repeat classification.
