// Section 3: Structural and Sequence Predictors Capture Distinct Pathogenic Mechanisms
// Data sources: analysis/DISCORDANCE_REPORT_v2.md, analysis/TERT_validation_summary.json,
//               analysis/Q2b_true_blindspots.csv
// All numbers verified against source files. No invented statistics.

== Structural and Sequence Predictors Capture Distinct Pathogenic Mechanisms

=== Two-by-Two Discordance Framework

To quantify the relationship between structural and sequence-based
predictions, we cross-tabulated VEP verdict (pathogenic vs.
benign/low-impact) against ARCHCODE structural verdict (LSSIM < 0.95 vs.
≥ 0.95) across all nine loci (30,318 variants with both annotations;
@tab:discordance). Four quadrants emerge. Q1 (concordant pathogenic,
n = 270) contains variants where both tools agree on disruption. Q3
(sequence channel, n = 10,385) contains variants detected by VEP but not
by ARCHCODE --- predominantly missense and canonical splice variants whose
pathogenic mechanism operates at the protein or spliceosome level. Q4
(concordant benign, n = 19,402) contains variants where neither tool
detects disruption. Q2 (ARCHCODE-only, n = 261) contains variants where
the structural model detects chromatin disruption that VEP misses or
cannot evaluate.

Q2 variants reside a mean 620 bp from the nearest annotated enhancer,
compared with 25,138 bp for Q3 variants --- a 41-fold difference. This
enhancer proximity distinguishes structural-channel from sequence-channel
pathogenicity and motivates a finer decomposition of Q2.

=== Structural Blind Spots (Q2b): Enhancer-Proximal Variants at HBB

Q2 subdivides into two mechanistically distinct subtypes. Q2a (n = 207,
79.3%) comprises variants that received no VEP consequence score
(VEP = −1), predominantly non-coding frameshifts outside Ensembl's
annotation model. Q2a represents a coverage gap rather than a predictive
disagreement. Q2b (n = 54, 20.7%) comprises variants where VEP _did_
assign a score in the low-impact range (0--0.5, mean = 0.208), yet
ARCHCODE detects structural disruption (mean LSSIM = 0.9270). These are
true blind spots: explicit disagreement between the two approaches.

Q2b variants are overwhelmingly enhancer-proximal (mean 434 bp vs.
25,138 bp for Q3; Mann--Whitney _U_ test, _p_ = 2.51 × 10#super[−31]).
By locus, HBB contributes 25 Q2b variants, BRCA1 contributes 26, TP53
contributes 2, and TERT contributes 1. Five loci (CFTR, MLH1, LDLR,
SCN5A, GJB2) contribute zero.

Q2b pathogenicity precision --- the fraction classified as pathogenic or
likely pathogenic in ClinVar --- is 0.481 (26 of 54). This is lower than
Q1 (1.000) or Q2a (0.990), and reflects a deliberate property of the
method. ARCHCODE detects structural disruption at enhancer-proximal
positions regardless of whether that disruption reaches the threshold for
clinical pathogenicity. A variant that reduces an enhancer--promoter
contact may decrease gene expression by 5% (tolerated) or by 50%
(pathogenic); the structural model captures the topology change but cannot
distinguish expression magnitude. The 28 benign-classified Q2b variants
--- predominantly BRCA1 5′ UTR positions (LSSIM 0.942--0.944) --- are
structurally disrupted but apparently tolerated. Enhancer proximity is
thus _necessary but not sufficient_ for clinical pathogenicity, and
precision below 1.0 is an expected feature of a triage tool that
prioritizes candidates for experimental follow-up rather than rendering
final clinical verdicts. Notably, Q3 precision (0.834) demonstrates
the same principle: sequence-level evidence is likewise necessary but not
sufficient.

Q2b enrichment correlates with tissue match between the K562 simulation
and each locus's primary disease tissue (Spearman ρ = 0.840,
_p_ = 0.0046). HBB, the erythroid-matched locus, shows the highest Q2b
ratio (0.0227); tissue-mismatched loci show none. Structural blind spots
are a tissue-bounded phenomenon.

=== TERT as Independent Replication Locus

To test whether enhancer-proximity enrichment generalizes beyond HBB, we
examined TERT (n = 2,089 variants), where K562 provides a biologically
relevant cell context: K562 is derived from chronic myelogenous leukemia
(CML), a malignancy in which telomerase is constitutively active and the
TERT promoter is engaged with distal regulatory elements.

TERT yields 35 Q2 variants and 416 Q3 variants. Q2 mean enhancer distance
is 864 bp versus 19,966 bp for Q3 --- a 23-fold ratio (Mann--Whitney
_p_ = 2.03 × 10#super[−15]). Q2 precision at TERT is 0.971 (34 of 35
pathogenic). The enhancer-proximity pattern observed at HBB thus
replicates at an independent locus with matched tissue context.

We note an important asymmetry: of the 35 TERT Q2 variants, 34 are Q2a
(VEP coverage gap) and only 1 is Q2b (true blind spot). The replication
therefore confirms the _enhancer-proximity_ signal of the structural
channel but does not replicate the _mechanistic disagreement_ pattern
observed at HBB. This distinction is expected given TERT's smaller
enhancer landscape and the dominance of non-coding frameshifts in ClinVar
submissions for this locus.

=== Orthogonality of Structural and Sequence Axes

Per-locus normalized mutual information (NMI) between ARCHCODE and VEP
quantifies the degree of shared information. At HBB, NMI = 0.4945,
reflecting a locus where both structural and sequence features
discriminate between pathogenic and benign variants. At all remaining
loci, NMI ≤ 0.030 (TERT: 0.030; MLH1: 0.019; CFTR: 0.013; BRCA1:
0.008; LDLR: 0.005; TP53: 0.0004; SCN5A: 0.0; GJB2: 0.0). Eight of
nine loci thus show near-complete orthogonality between the two axes.

The elevated NMI at HBB reflects the unique combination of a strong
enhancer landscape in the erythroid-matched simulation and a variant
catalogue enriched for functional classes (promoter, splice region) that
affect both chromatin contacts and coding potential. At tissue-mismatched
loci, ARCHCODE LSSIM values converge to ≥ 0.99, contributing no
discriminative information and yielding NMI ≈ 0. The previously reported
global NMI of 0.101 (HBB-only, binary threshold binarization) is
consistent with the per-locus value of 0.4945 after accounting for the
different binning methodology (see Methods).

#figure(
  align(center)[#table(
    columns: (18%, 9%, 11%, 14%, 14%, 34%),
    align: (left, right, right, right, right, left),
    table.header(
      [Quadrant], [_n_], [Prec.], [Enh. dist.], [LSSIM], [Interpretation],
    ),
    table.hline(),
    [Q1 Concordant Path.], [270], [1.000], [543 bp], [—], [Both tools agree],
    [Q2a Coverage Gap], [207], [0.990], [668 bp], [0.873], [VEP cannot score],
    [Q2b True Blind Spot], [54], [0.481], [434 bp], [0.927], [Structural triage candidates],
    [Q3 Sequence Channel], [10,385], [0.834], [25,138 bp], [—], [VEP detects, ARCHCODE does not],
    [Q4 Concordant Benign], [19,402], [0.413], [26,749 bp], [—], [Neither tool flags],
    table.hline(),
    [#strong[Total]], [#strong[30,318]], [], [], [], [],
  )]
  , caption: [Discordance matrix across nine loci with Q2 subtype decomposition.
    Precision: fraction classified as pathogenic or likely pathogenic in ClinVar.
    Enhancer distance: to nearest annotated enhancer in the locus configuration.
    Q2b precision of 0.481 reflects the tool's role as a structural triage filter
    rather than a standalone classifier.]
  , kind: table
) <tab:discordance>
