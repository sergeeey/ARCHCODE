#strong[Background:] Sequence-based variant effect predictors (VEP) evaluate pathogenicity through protein-coding impact and splice motif disruption, but variants acting through 3D chromatin topology disruption --- particularly in non-coding regulatory regions --- remain systematically invisible. We developed ARCHCODE, an analytical mean-field loop extrusion simulator, to provide complementary structural variant assessment.

#strong[Methods:] ARCHCODE implements Kramer kinetics for cohesin barrier crossing (α=0.92, γ=0.80; manually calibrated to literature ranges). For each variant, the simulator computes a Structural Similarity Index (SSIM) comparing wild-type and mutant predicted contact maps. We analyzed 25,272 clinically classified ClinVar variants across 6 loci (HBB, CFTR, TP53, BRCA1, MLH1, LDLR) plus SCN5A as negative control (27,760 total). Local SSIM (LSSIM) --- computed on a 50×50 submatrix centered on the variant --- resolves matrix-size dilution across loci.

#strong[Results:] On HBB (n=1,103), ARCHCODE correctly stratified variants by functional category: loss-of-function classes (nonsense, frameshift) showed severe structural disruption (mean SSIM 0.88--0.90), while neutral classes (synonymous, intronic) preserved structure (mean SSIM \> 0.99). Twenty "pearl" variants were identified --- invisible to VEP (score \< 0.30) but structurally disruptive (SSIM \< 0.95). ROC analysis yielded AUC = 0.976; however, a position-only control experiment (fixed effectStrength = 0.3) produced AUC = 0.551, confirming the high AUC reflects category-distribution differences, not independent prediction. Within-category testing across all loci confirmed primarily null results (ΔAUC \< 0.02). Hi-C validation against K562, MCF7, and HepG2 experimental data yielded significant correlations (r = 0.29--0.59, all p \< 10#super[-82]).

#strong[Conclusions:] ARCHCODE provides a complementary structural layer for variant interpretation, identifying candidates invisible to sequence-based tools. We do not claim superiority over VEP; structural simulation serves as a hypothesis-generating complement in variant interpretation workflows.

#strong[Keywords:] β-thalassemia, HBB, chromatin loops, loop extrusion, cohesin, SSIM, structural pathogenicity, VEP, pearl variants, variant interpretation, mean-field simulation, multi-locus validation, Hi-C, ENCODE, Local SSIM



---


== Significance Statement
<significance-statement>
Sequence-based variant effect predictors score variants by their impact
on protein sequence and canonical splice motifs, leaving a structural
blind spot for variants that disrupt 3D chromatin topology without
altering coding sequence. We developed ARCHCODE, an analytical loop
extrusion simulator, and applied it to 27,760 clinically classified
variants across seven loci: HBB (1,103), CFTR (3,349), TP53 (2,794),
BRCA1 (10,682), MLH1 (4,060), LDLR (3,284), and SCN5A (2,488). ARCHCODE
correctly stratifies variants by functional class and identifies 20
"pearl" candidates on HBB --- variants invisible to VEP --- where
structural simulation predicts regulatory disruption. Local SSIM (LSSIM)
resolves matrix-size dilution, expanding SSIM dynamic range from
0.98--1.00 to 0.75--1.00 and enabling verdict assignment across all
matrix sizes. Within-category testing confirms ARCHCODE as primarily a
category-level structural classifier (CFTR/TP53 p \> 0.29;
BRCA1/MLH1/LDLR show statistical significance at ΔAUC \< 0.02 --- a
power effect, not meaningful prediction). K562 Hi-C correlation ranges
from r = 0.29 (TP53) to r = 0.59 (HBB 95kb, MLH1) using K562 data; HepG2
Hi-C validation for LDLR (r = 0.32) extends the framework to
tissue-specific chromatin. This work establishes a framework for
orthogonal structural scoring as a complement to existing sequence-based
tools in variant interpretation pipelines.



---


== Main Findings (for graphical abstract)
<main-findings-for-graphical-abstract>
+ #strong[25,272 real ClinVar variants across 6 loci] (HBB 1,103 + CFTR
  3,349 + TP53 2,794 + BRCA1 10,682 + MLH1 4,060 + LDLR 3,284) analyzed
+ #strong[45.6% (161/353) HBB structurally pathogenic] by ARCHCODE;
  loss-of-function classes show 86--100% concordance
+ #strong[20 "pearl" variants] identified on HBB: VEP-blind (VEP \<
  0.30), ARCHCODE-detected (SSIM \< 0.95)
+ #strong[ROC AUC = 0.977] (unified pipeline); reflects
  category-distribution differences, not independent prediction
+ #strong[Local SSIM (LSSIM)] resolves matrix-size dilution: dynamic
  range 0.75--1.00 (vs 0.98--1.00 global); verdicts now work on all
  matrix sizes
+ #strong[Within-category: primarily null] (CFTR/TP53 p \> 0.29);
  BRCA1/MLH1/LDLR statistically significant at ΔAUC \< 0.02 (power
  effect, not meaningful prediction); #strong[position-only control: AUC
  \= 0.551] (confirms category-distribution effect)
+ #strong[Multi-locus Hi-C validation:] MLH1 r = 0.59, HBB r =
  0.53--0.59, BRCA1 r = 0.50--0.53, LDLR r = 0.32 (HepG2), TP53 r =
  0.28--0.29 (K562 + MCF7 + HepG2)
+ #strong[Improved classify\_hgvs()] detects frameshift vs inframe from
  cDNA indel length, resolving \>90% of "other" variants


---


== Data Transparency Declaration
<data-transparency-declaration>
#figure(
  align(center)[#table(
    columns: (18.99%, 12.03%, 68.99%),
    align: (auto,auto,auto,),
    table.header([Data source], [Status], [Notes],),
    table.hline(),
    [ClinVar HBB pathogenic (n=353)], [REAL], [NCBI E-utilities API,
    March 2026],
    [ClinVar HBB benign (n=750)], [REAL], [NCBI E-utilities API, March
    2026],
    [Ensembl VEP v113 SIFT scores], [REAL], [Standard Ensembl REST API],
    [ARCHCODE SSIM/LSSIM scores], [COMPUTATIONAL], [Analytical
    simulation; LSSIM = 50×50 local window],
    [ROC analysis (n=1,103)], [COMPUTATIONAL], [AUC=0.977; unified
    pipeline, category-distribution effect],
    [Hi-C correlation (K562)], [REAL (positive)], [r=0.53 (30kb), r=0.59
    (95kb); p\<10⁻⁸²; 4DNFI18UHVRO],
    [Hi-C correlation (GM12878)], [REAL (negative)], [r=0.16, p=ns; 12
    loci (HBB silent in B-cells)],
    [SpliceAI predictions], [NOT AVAILABLE], [API unreachable; replaced
    by VEP],
    [AlphaGenome benchmark], [REAL], [SDK v0.6.0; contact maps from 4DN;
    Spearman ρ=0.12--0.52 across 6 loci (HBB lowest due to resolution
    mismatch)],
    [Kramer parameters (α, γ)], [MANUALLY CALIBRATED], [Literature
    ranges; Bayesian optimization confirmed near-optimal (Δr=0.0001)],
    [ClinVar CFTR (n=3,349)], [REAL], [NCBI E-utilities API; 1,756 P/LP
    \+ 1,593 B/LB],
    [ClinVar TP53 (n=2,794)], [REAL], [NCBI E-utilities API; 1,645 P/LP
    \+ 1,149 B/LB],
    [ClinVar BRCA1 (n=10,682)], [REAL], [NCBI E-utilities API; 7,062
    P/LP + 3,620 B/LB],
    [CFTR within-category (LSSIM)], [COMPUTATIONAL], [LR ΔAUC=−0.012,
    p=0.79; null result],
    [TP53 within-category (LSSIM)], [COMPUTATIONAL], [LR ΔAUC=+0.032,
    p=0.29; null result],
    [BRCA1 within-category (LSSIM)], [COMPUTATIONAL], [LR ΔAUC=+0.002,
    p≈10⁻²⁰; significant but ΔAUC negligible],
    [ClinVar MLH1 (n=4,060)], [REAL], [NCBI E-utilities API; 2,425 P/LP
    \+ 1,635 B/LB],
    [MLH1 within-category (LSSIM)], [COMPUTATIONAL], [LR ΔAUC=+0.011,
    p=0.005; significant but ΔAUC negligible],
    [Hi-C correlation (MLH1)], [REAL (positive)], [K562 r=0.59; p≈0],
    [Hi-C correlation (BRCA1)], [REAL (positive)], [K562 r=0.53; MCF7
    r=0.50; p≈0],
    [Hi-C correlation (TP53)], [REAL (moderate)], [K562 r=0.29; MCF7
    r=0.28; p\<10⁻¹³⁶],
    [Hi-C correlation (LDLR)], [REAL (positive)], [HepG2 r=0.32; p≈0;
    first tissue-specific validation],
    [LDLR within-category (LSSIM)], [COMPUTATIONAL], [LR ΔAUC=−0.003,
    p=0.004; significant but ΔAUC negligible],
    [Position-only control], [COMPUTATIONAL], [Fixed effectStrength=0.3;
    AUC=0.551 (≈chance); confirms AUC 0.977 = category effect],
    [Bayesian optimization], [COMPUTATIONAL], [Optuna 4.7.0, 200 trials;
    Δr=0.0001],
    [Multimodal AG (RNA-seq/ATAC)], [REAL], [SDK v0.6.0; 1bp resolution;
    K562; detectable signal (RNA max\_delta=28.13)],
  )]
  , kind: table
  )


---


#emph[Manuscript prepared for bioRxiv preprint submission] #emph[Correspondence: sergeikuch80\@gmail.com]


---
