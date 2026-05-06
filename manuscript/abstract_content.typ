Sequence-based variant effect predictors evaluate pathogenicity through
protein-coding impact and splice motif disruption, leaving a structural
blind spot for variants that disrupt 3D chromatin topology without
altering coding sequence.

We developed ARCHCODE, an analytical mean-field loop extrusion simulator
implementing Kramer kinetics for cohesin barrier crossing (alpha=0.92,
gamma=0.80; manually calibrated to published literature ranges). Applied to
30,318 clinically classified ClinVar variants across 9 genomic loci,
ARCHCODE computes Local SSIM (LSSIM) comparing wild-type and mutant
predicted contact maps on a 50x50 submatrix centered on the variant.

Across nine loci --- HBB (1,103), CFTR (3,349), TP53 (2,794),
BRCA1 (10,682), MLH1 (4,060), LDLR (3,284), SCN5A (2,488), TERT
(2,089), GJB2 (469) --- loss-of-function classes showed 86--100%
structural pathogenic concordance (nonsense/frameshift). Discordance
analysis identified 25 high-confidence HBB "pearl" variants: VEP-blind
(score less than 0.30), CADD-ambiguous (phred 10--20), yet structurally
disruptive (LSSIM less than 0.92) --- invisible to nine orthogonal methods
including SpliceAI (0.00 for 20/20 SNVs), MPRA (p=0.91), and gnomAD v4
(84% constraint, 21/25 verified). AlphaGenome CAGE analysis independently confirms pearl
disruption (-19% vs -0.1% for benign, p=4e-6). Hi-C validation against
K562 erythroid chromatin yielded r=0.28-0.59 across loci. A
tissue-specificity gradient --- matched (HBB delta=0.111) to mismatched
(GJB2 delta=0.006, null) --- defines the domain of applicability.

Critical limitation: the overall AUC of 0.977 on HBB is primarily
category-driven (a trivial category-to-score mapping achieves 0.98
without simulation; within-category AUC median is 0.52). Matched-control
testing of Class B VUS against benign variants of the same category and
locus shows no significant difference (p=0.996). ARCHCODE does not
provide variant-level discriminative utility beyond consequence category
and genomic position.

ARCHCODE is a hypothesis-generating structural interpretation layer ---
not a pathogenicity predictor or replacement for sequence-based tools.
All data are publicly available; experimental validation is required
before clinical use.

#strong[Keywords:] β-thalassemia, HBB, chromatin loop extrusion, cohesin,
LSSIM, structural pathogenicity, VEP, pearl variants, ClinVar, ARCHCODE
