// Coverage Gap Note: Discordance Is Partly Mechanistic and Partly Infrastructural
// A standalone observation from the ARCHCODE discordance analysis
// Data: analysis/TERT_validation.csv, analysis/Q2b_true_blindspots.csv,
//       analysis/discordance_by_locus.csv
// All statistics verified against source CSV files.

= Annotation Coverage Gaps Inflate Apparent Discordance Between Structural and Sequence Predictors

== Summary

Cross-tabulation of ARCHCODE structural predictions against VEP sequence
annotations across 30,318 ClinVar variants at nine loci reveals 261
variants (Q2) where the structural model detects chromatin disruption
that VEP misses. However, decomposing Q2 into subtypes reveals that
*79.3% of apparent discordance reflects annotation infrastructure gaps,
not mechanistic disagreement*.

- *Q2a (n = 207):* VEP returned no consequence score (VEP = −1).
  These are non-coding frameshifts, complex indels, and intergenic
  variants outside Ensembl's annotation model. VEP did not fail to
  detect pathogenicity --- it could not attempt the assessment.

- *Q2b (n = 54):* VEP assigned a score in the 0--0.5 range (mean
  0.208) but rated the variant as low-impact. ARCHCODE detects
  structural disruption (mean LSSIM = 0.927). These are true
  mechanistic blind spots: explicit disagreement.

This distinction has immediate implications for interpreting
discordance between any pair of variant annotation tools. A "missed"
variant may represent a genuine mechanistic blind spot (correctable
through method improvement) or an infrastructure limitation
(correctable through expanded annotation coverage). Conflating the
two inflates claims about complementarity.

== The TERT Case Study

TERT provides the clearest illustration. Among 2,089 TERT variants,
35 fall in Q2 (ARCHCODE detects, VEP misses). Q2 variants are
23-fold closer to enhancers than Q3 variants (864 bp vs 19,966 bp;
Mann--Whitney p = 2.03 × 10#super[−15]), and Q2 precision is 0.971
(34/35 pathogenic in ClinVar).

By every aggregate metric, TERT appears to replicate the HBB finding.

However, *34 of 35 TERT Q2 variants are Q2a* (VEP = −1). Only 1 is
Q2b (a missense variant, VCV004182780, LSSIM = 0.949, VEP = 0.40).
TERT's apparent discordance is 97% infrastructure gap, 3% mechanistic
disagreement.

Contrast with HBB, where all 25 Q2 variants are Q2b: VEP assigned
scores (0.15--0.35), rated them as low-impact, but ARCHCODE detects
strong structural disruption (LSSIM 0.798--0.942). HBB's discordance
is 100% mechanistic.

== Per-Locus Q2a/Q2b Decomposition

#figure(
  align(center)[#table(
    columns: (12%, 9%, 8%, 8%, 11%, 11%, 12%, 29%),
    align: (left, right, right, right, right, right, right, left),
    table.header(
      [Locus], [N], [Q2], [Q2a], [Q2b], [Q2b/Q2], [Tissue], [Interpretation],
    ),
    table.hline(),
    [HBB], [1,103], [25], [0], [25], [100%], [1.0], [Pure mechanistic blind spot],
    [BRCA1], [10,682], [79], [53], [26], [33%], [0.5], [Mixed; Q2b mostly benign (artifacts)],
    [TERT], [2,089], [35], [34], [1], [3%], [0.5], [Pure infrastructure gap],
    [MLH1], [4,060], [72], [72], [0], [0%], [0.5], [Pure infrastructure gap],
    [CFTR], [3,349], [36], [36], [0], [0%], [0.0], [Infrastructure gap + tissue mismatch],
    [TP53], [2,794], [4], [2], [2], [50%], [0.5], [Small n; inconclusive],
    [LDLR], [3,284], [10], [10], [0], [0%], [0.0], [Infrastructure gap + tissue mismatch],
    [SCN5A], [2,488], [0], [0], [0], [---], [0.0], [No structural signal (negative control)],
    [GJB2], [469], [0], [0], [0], [---], [0.0], [No structural signal (negative control)],
    table.hline(),
    [*Total*], [*30,318*], [*261*], [*207*], [*54*], [*20.7%*], [], [],
  )]
  , caption: [Q2 decomposition across nine loci. Q2a = VEP coverage gap (VEP = −1).
    Q2b = true blind spot (VEP 0--0.5 but ARCHCODE LSSIM < 0.95).
    Only HBB shows pure mechanistic disagreement; most loci are dominated by
    annotation infrastructure limitations.]
  , kind: table
) <tab:coverage-gap>

== Implications

*For tool developers:* Expanding VEP's annotation model to cover
non-coding frameshifts and complex indels (currently returning VEP = −1)
would eliminate 207 of 261 Q2 variants (79.3%), substantially reducing
apparent discordance without any change to ARCHCODE. The "structural
advantage" at most loci is partly an annotation artifact.

*For benchmarking:* Cross-tool discordance metrics should always
decompose into coverage gap vs.\ genuine disagreement. Reporting "261
variants where ARCHCODE detects but VEP misses" without the Q2a/Q2b
split overstates complementarity by 4×.

*For ARCHCODE specifically:* The true unique value --- mechanistic
blind spots --- is concentrated at HBB (25 Q2b variants), with minor
contributions from BRCA1 (26 Q2b, mostly benign) and TP53 (2 Q2b).
This is not a weakness but a precise delimitation of the tool's domain:
strongest at tissue-matched loci with compact enhancer architecture.

*For the field:* Every claim about "complementary" or "orthogonal"
prediction methods should distinguish between methods that disagree
and methods that have non-overlapping input coverage. The former is
scientifically interesting; the latter is an engineering problem.
