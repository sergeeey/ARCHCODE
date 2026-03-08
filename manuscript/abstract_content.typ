Sequence-based variant effect predictors evaluate pathogenicity through
protein-coding impact and splice motif disruption, leaving a structural
blind spot for variants that disrupt 3D chromatin topology without
altering coding sequence.

We developed ARCHCODE, an analytical mean-field loop extrusion simulator
implementing Kramer kinetics for cohesin barrier crossing (α=0.92,
γ=0.80; calibrated to published FRAP ranges). Applied to 32,201
clinically classified ClinVar variants across 13 genomic loci, ARCHCODE
computes Local SSIM (LSSIM) comparing wild-type and mutant predicted
contact maps on a 50×50 submatrix centered on the variant.

Across nine primary loci --- HBB (1,103), CFTR (3,349), TP53 (2,794),
BRCA1 (10,682), MLH1 (4,060), LDLR (3,284), SCN5A (2,488), TERT
(2,089), GJB2 (469) --- loss-of-function classes showed 86--100%
structural pathogenic concordance (nonsense/frameshift). Discordance
analysis identified 27 HBB "pearl" variants (95 kb atlas; 20 confirmed at stringent 30 kb threshold): VEP-blind (score \< 0.30),
CADD-ambiguous (phred 10--20), yet structurally disruptive (LSSIM \<
0.92) --- invisible to nine orthogonal methods including SpliceAI (0.00
for 20/20 SNVs), MPRA (p=0.91), and gnomAD v4 (85% absent).
AlphaGenome multimodal analysis independently confirms pearl disruption
(RNA-seq signal 2.8× higher than benign, p\<0.0001). Hi-C validation
against K562 erythroid chromatin yielded r=0.59 (p\<10⁻³⁰⁰). A
tissue-specificity gradient --- matched (HBB Δ=0.111) to mismatched
(GJB2 Δ=0.006, null) --- defines the domain of applicability.
Application to 30,952 VUS identifies 641 pearl-like reclassification
candidates.

ARCHCODE is a complementary, hypothesis-generating layer for variant
interpretation --- not a replacement for sequence-based tools. All data
are publicly available; experimental validation is required before
clinical use.

#strong[Keywords:] β-thalassemia, HBB, chromatin loop extrusion, cohesin,
LSSIM, structural pathogenicity, VEP, pearl variants, ClinVar, ARCHCODE
