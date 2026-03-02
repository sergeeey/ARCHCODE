= Introduction
<introduction>
== Act I: The Variant of Uncertain Significance Crisis
<act-i-the-variant-of-uncertain-significance-crisis>
The human genome project promised precision medicine: sequence a
patient's DNA, identify pathogenic variants, deliver targeted therapy.
Two decades later, we face a paradox. Clinical genomic testing
identifies an average of 3--5 Variants of Uncertain Significance (VUS)
per exome (Harrison et al., 2019). In the United States alone, \>4
million individuals have undergone clinical genetic testing, yielding an
estimated 12--20 million VUS interpretations currently classified as
"uncertain" (Manrai et al., 2016). For patients, a VUS result means
diagnostic limbo. For clinicians, it means management uncertainty. For
families, it means reproductive unknowns.

Hemoglobinopathies exemplify this challenge. β-thalassemia, caused by
variants in the β-globin (#emph[HBB]) gene, affects \>60,000 births
annually worldwide and represents one of the most common monogenic
disorders (Taher et al., 2021). For severe nonsense or frameshift
variants, diagnosis is unambiguous: loss of functional β-globin causes
transfusion-dependent thalassemia major. However, #strong[splice\_region
variants] --- those residing ±8 bp from exon boundaries --- occupy
interpretive gray zones. Unlike canonical splice donor/acceptor
disruptions (±2 bp), which abolish splicing with near certainty,
splice\_region variants can subtly modulate splicing efficiency through
disruption of cis-regulatory enhancer elements without destroying core
splice sites (Baralle & Baralle, 2018). The resulting 10--30% reduction
in proper transcript may cause β-thalassemia minor or no phenotype at
all.

Of 353 #emph[HBB] pathogenic and likely-pathogenic variants in ClinVar
(as of 2026) that we analyzed, 9 are splice#emph[region variants, and
clinical interpretation of many remains uncertain. This uncertainty has
direct consequences: couples undergoing reproductive planning who
receive a VUS result for an \_HBB] splice\_region variant cannot know
their offspring's risk without functional evidence that may take years
to accumulate.

== Act II: Sequence-Based Predictors and Their Structural Blind Spot
<act-ii-sequence-based-predictors-and-their-structural-blind-spot>
Sequence-based variant effect predictors such as Ensembl VEP (McLaren et
al., 2016) and SIFT (Ng & Henikoff, 2003) evaluate pathogenicity through
protein-coding impact, splice motif disruption, and evolutionary
conservation. These tools excel at detecting variants acting through
well-characterized sequence-level mechanisms: nonsense codons,
frameshift insertions, canonical splice site disruption.

However, sequence-based predictors operate in #emph[linear sequence
space]. The human genome functions in #strong[3D chromatin space].
Enhancers located 50 kb upstream in linear sequence can be brought into
physical proximity with target promoters through chromatin loop
extrusion mediated by cohesin complexes (Davidson et al., 2019; Sanborn
et al., 2015). A variant residing within a stable enhancer--promoter
loop may experience qualitatively different regulatory constraints than
the same sequence variant in open chromatin, regardless of whether it
alters a protein residue or splice signal.

This creates what we term the #strong[structural blind spot]: variants
that disrupt 3D chromatin topology without altering coding sequence or
canonical splice motifs are invisible to sequence-based predictors.
Promoter-proximal variants, non-canonical regulatory elements, and
variants that subtly modify chromatin occupancy profiles may all fall
into this category. No sequence conservation score, SIFT prediction, or
motif disruption analysis can detect disruption of an enhancer--promoter
contact that operates at the level of cohesin processivity and CTCF
barrier dynamics.

== Act III: The "Loop That Stayed" --- A Theoretical Framework
<act-iii-the-loop-that-stayed-a-theoretical-framework>
We introduce the concept of #strong["The Loop That Stayed"] as a
theoretical framework for a specific class of potentially pathogenic
mechanism: variants that simultaneously (1) disrupt cis-regulatory
splice elements and (2) preserve chromatin loop anchors, creating what
we hypothesize to be #strong[loop-constrained pathogenicity] --- a
situation where structural stability paradoxically amplifies splice
defects by limiting access to compensatory trans-acting factors outside
the loop domain.

This framework is currently theoretical. The prediction is that stable
cohesin-mediated loops act as topological barriers, and variants
disrupting splice enhancers within such loops cannot recruit
compensatory spliceosome components from outside the loop domain. We
developed ARCHCODE to test, at the simulation level, whether this
mechanism produces a detectable SSIM signature.

We emphasize: this is a hypothesis-generating framework, not a confirmed
mechanism. The pearl variants we identify are computational predictions
of potential structural disruption. Whether stable loops genuinely
confine splice regulatory defects requires direct experimental testing
via RT-PCR and Capture Hi-C in erythroid cells.

== Act IV: Our Approach --- Physics as a Complementary Tool
<act-iv-our-approach-physics-as-a-complementary-tool>
We developed #strong[ARCHCODE] (Architecture-Constrained Decoder), an
analytical mean-field loop extrusion simulator implementing Kramer
kinetics for cohesin unloading:

```
P_unload = k_base × (1 - α × MED1^γ)
```

where α=0.92 and γ=0.80 are manually calibrated to published literature
ranges (Gerlich et al., 2006; Hansen et al., 2017; Sabaté et al., 2024).
The model computes contact probabilities analytically by combining
distance decay, chromatin occupancy, CTCF barrier permeability, and
Kramer-modulated cohesin residence time --- without stochastic Monte
Carlo sampling.

We quantify structural disruption using the Structural Similarity Index
(SSIM), comparing wild-type and mutant predicted contact maps. SSIM
ranges from 0 (complete structural disruption) to 1 (identical to
wild-type). To address matrix-size dilution on larger loci, we compute
Local SSIM (LSSIM) on a 50×50 submatrix centered on the variant,
normalizing perturbation fraction and enabling threshold transfer across
matrix sizes. A key limitation to state upfront: ARCHCODE parameters are
not fitted to experimental data. However, Hi-C validation against K562
erythroid chromatin yielded significant correlation (r = 0.53--0.59, p
\< 10⁻⁸²), indicating that ARCHCODE contact predictions capture
biologically meaningful chromatin architecture in the cell type where
HBB is actively transcribed.

== Study Objectives
<study-objectives>
In this study, we:

+ #strong[Retrieve and analyze 353 real ClinVar HBB variants] via NCBI
  E-utilities API, generating ARCHCODE structural predictions and
  Ensembl VEP v113 sequence-based predictions for each.

+ #strong[Calculate SSIM scores] quantifying structural disruption and
  classify variants using pre-defined thresholds (PATHOGENIC: SSIM \<
  0.85; LIKELY\_PATHOGENIC: 0.85--0.92; VUS: 0.92--0.96; LIKELY\_BENIGN:
  0.96--0.99; BENIGN: ≥ 0.99).

+ #strong[Compare ARCHCODE structural predictions with Ensembl VEP
  sequence-based scores] to identify systematic discordance patterns and
  characterize variant classes where each method provides complementary
  information.

+ #strong[Identify "pearl" variants] --- those where VEP provides no
  pathogenic signal (score \< 0.30) but ARCHCODE detects structural
  disruption (SSIM \< 0.95) --- as candidates for experimental
  follow-up.

+ #strong[Apply ACMG/AMP guidelines] to structurally disruptive variants
  with computational supporting evidence, acknowledging that
  experimental confirmation is required before any clinical
  reclassification.

+ #strong[Report Hi-C validation results] against K562 erythroid
  chromatin, demonstrating significant correlation (r = 0.53--0.59) that
  supports the model's biological relevance.

We do not claim to have discovered confirmed pathogenic mechanisms. We
propose ARCHCODE as an orthogonal, hypothesis-generating complement to
sequence-based prediction, specifically useful for promoter-proximal and
regulatory variants where VEP provides limited information.


---




---


= Methods
<methods>
== ARCHCODE Loop Extrusion Simulation
<archcode-loop-extrusion-simulation>
=== Physical Model
<physical-model>
ARCHCODE implements an analytical mean-field loop extrusion model based
on the cohesin processivity framework with Kramer kinetics for unloading
dynamics. The model computes contact probabilities analytically by
combining distance decay, local chromatin occupancy, CTCF barrier
permeability, and Kramer-modulated cohesin residence, without stochastic
Monte Carlo sampling.

=== Kramer Kinetics Parameterization
<kramer-kinetics-parameterization>
Cohesin unloading probability at each simulation step is governed by
Kramer's reaction rate theory:

$ P_"unload" = k_"base" times (1 - alpha times "MED1"^gamma) $ <eq:kramer>

where:

- $k_"base"$ = 0.002: baseline unloading rate (calibrated parameter)
- $alpha$ = 0.92: coupling strength between MED1 occupancy and cohesin
  residence time (estimated from literature ranges; Gerlich et al.~2006;
  Hansen et al.~2017)
- $gamma$ = 0.80: cooperativity exponent reflecting sub-linear dependence
  (estimated from literature ranges; Gerlich et al.~2006; Hansen et
  al.~2017)
- `MED1`: local Mediator occupancy normalized to \[0,1\]

#strong[Parameter Calibration:] α=0.92 and γ=0.80 were estimated from
literature ranges (Gerlich et al.~2006; Hansen et al.~2017) and manually
calibrated to reproduce qualitatively reasonable cohesin residence-time
behaviour:

- MED1+ enhancer regions: τ \~ 35 min (Gerlich et al.~2006)
- MED1- regions: τ \~ 12 min

No formal fitting to FRAP data was performed. No FRAP measurements are
available in this study. Parameter values should be regarded as manually
calibrated estimates consistent with published residence-time ranges.

=== Simulation Parameters
<simulation-parameters>
#figure(
  align(center)[#table(
    columns: (17.45%, 27.52%, 27.52%, 27.52%),
    align: (auto,auto,auto,auto,),
    table.header([Parameter], [30 kb window], [95 kb sub-TAD
      window], [Source],),
    table.hline(),
    [Genomic
    locus], [chr11:5,210,000--5,240,000], [chr11:5,200,000--5,295,000], [HBB
    gene region / full sub-TAD],
    [Resolution], [600 bp], [600 bp], [Analytical bin size],
    [N\_bins], [50], [159], [Derived from locus/resolution],
    [Cohesin velocity], [1000 bp/s], [1000 bp/s], [Davidson et
    al.~2019],
    [CTCF sites], [6 (MODEL\_PARAMETER)], [4 (ENCODE K562
    ENCFF660GHM)], [Annotated from ChIP-seq peaks],
    [Enhancer/occupancy regions], [5 (MODEL\_PARAMETER)], [5 (Literature
    \+ NCBI RefSeq TSS)], [ChIP-seq data / literature],
    [Genes covered], [HBB only], [HBB, HBD, HBBP1, HBG1, HBG2,
    HBE1], [NCBI RefSeq],
    [Method], [Analytical mean-field contact computation], [Analytical
    mean-field contact computation], [No Monte Carlo sampling],
    [Genomic locus (CFTR)], [chr7:116,907,253--117,224,349 (317
    kb)], [], [CFTR gene region],
    [Resolution (CFTR)], [1000 bp], [], [Analytical bin size],
    [N\_bins (CFTR)], [317], [], [Derived from locus/resolution],
    [CTCF sites (CFTR)], [3], [], [ENCODE K562 ChIP-seq (ENCFF660GHM)],
    [Enhancer/occupancy (CFTR)], [4], [], [Literature: CFTR promoter +
    intronic enh.],
  )]
  , kind: table
  )

=== Cohesin Loading (FountainLoader Model)
<cohesin-loading-fountainloader-model>
Cohesin complexes are loaded onto chromatin with spatial bias
proportional to MED1 occupancy:

```
P_load(i) = (MED1(i) + β) / Σ(MED1(j) + β)
```

where β=5 is a pseudocount preventing zero probability at MED1-depleted
regions. MED1 occupancy profiles were derived from ChIP-seq data (ENCODE
GM12878, biological replicates merged, RPKM-normalized).

=== CTCF Barrier Implementation
<ctcf-barrier-implementation>
CTCF sites were annotated using ChIP-seq peaks (ENCODE GM12878,
FDR\<0.01). Convergent CTCF pairs (motif orientations: Forward-Reverse)
act as loop anchors in the analytical model. Each CTCF site is assigned
a permeability value (default 0.15, i.e.~85% barrier strength) that
enters the contact formula as a multiplicative factor reducing contact
probability across the barrier.

=== Multi-Locus Extension
<multi-locus-extension>
To test cross-gene generalization, ARCHCODE was applied to three
additional loci:

#strong[CFTR] (chr7:116,907,253--117,224,349, 317 kb, 1000 bp
resolution, 317 bins). Locus configuration: 3 CTCF anchor sites from
ENCODE K562 ChIP-seq (ENCFF660GHM), 4 enhancer elements from published
literature. ClinVar variants: n=3,349 (1,756 P/LP + 1,593 B/LB).

#strong[TP53] (chr17:7,550,000--7,850,000, 300 kb, 1000 bp resolution,
300 bins). Locus configuration: 6 CTCF sites from ENCODE K562 ChIP-seq
(ENCFF736NYC, ENCSR000DWE), 5 enhancer elements from ENCODE K562 H3K27ac
(ENCFF864OSZ) and literature (including TP53 P1 and P2 promoters; Marcel
et al.~2010). ClinVar variants: n=2,794 (1,645 P/LP + 1,149 B/LB).

#strong[BRCA1] (chr17:42,900,000--43,300,000, 400 kb, 1000 bp
resolution, 400 bins). Locus configuration: 13 CTCF sites from ENCODE
K562 (ENCFF736NYC) cross-validated with MCF7 (ENCFF163JHE), 9 enhancer
elements from MCF7 H3K27ac (ENCFF340KSH) --- MCF7 used as primary
enhancer source because BRCA1 is actively transcribed in breast cancer
cells. Includes the BRCA1/NBR2 bidirectional promoter (Suen et
al.~1998). ClinVar variants: n=10,682 (7,062 P/LP + 3,620 B/LB).

All variants were downloaded from ClinVar via NCBI E-utilities API using
a generic downloader (`download_clinvar_generic.py --gene <GENE>`).
Variant categorization used improved HGVS nomenclature parsing that
determines frameshift vs inframe status from cDNA indel length modulo 3,
resolving \>90% of previously unclassified "other" variants (e.g.,
`c.403del` → 1 bp deletion → frameshift; `c.575_580del` → 6 bp deletion
→ inframe).

Hi-C validation for TP53 and BRCA1 used ENCODE K562 intact Hi-C
(ENCFF725EXS, ENCSR479XDG) and MCF7 intact Hi-C (ENCFF776XCM,
ENCSR660LPJ) at 1000 bp resolution with VC\_SQRT normalization (KR
normalization unavailable in ENCODE intact Hi-C files).

=== Bayesian Parameter Optimization
<bayesian-parameter-optimization>
Kinetics parameters (α, γ, k\_base) were subjected to Bayesian
optimization using Optuna 4.7.0 (Akiba et al., 2019) with Gaussian
Process sampling (GPSampler, n\_startup=20 random trials). The search
space was: α ∈ \[0.5, 1.0\], γ ∈ \[0.3, 1.5\], k\_base ∈ \[0.0005,
0.01\] with log-scale sampling for k\_base (reflecting its
multiplicative effect on unloading probability). The objective function
maximized the mean Pearson r between ARCHCODE wild-type contact matrices
and K562 Hi-C data across both HBB windows (30 kb and 95 kb). N=200
trials were evaluated. Parameter importance was assessed using
functional ANOVA (fANOVA). This is a post-hoc optimization on HBB K562
Hi-C data; cross- locus validation was not performed due to the absence
of CFTR-expressing cell Hi-C data.

=== Variant Introduction
<variant-introduction>
Variants modulate the local chromatin occupancy profile used in the
analytical contact computation. Each variant category is assigned a
functional impact strength that scales the reduction in local occupancy:

- #strong[Nonsense / frameshift] (highest impact): occupancy reduced by
  70--90% at the affected bin
- #strong[Splice donor / splice acceptor]: occupancy reduced by 60--80%;
  proximal CTCF permeability may also be modified
- #strong[Missense / splice region]: occupancy reduced by 20--50%
  depending on predicted severity
- #strong[Synonymous / intronic / UTR]: minimal or no occupancy change
  (\< 5%)

Categories with larger functional impact produce stronger reductions in
occupancy factors, which propagate through the contact formula (see
Contact Matrix Generation below) to yield lower SSIM values relative to
the wild-type reference.

#strong[Methodological note on occupancy scaling:] The
category-dependent occupancy impact functions as a standardized
perturbation to probe topological vulnerability at each genomic
position, not as an independent pathogenicity predictor. The scaling
magnitudes are motivated by the expected transcriptional impact of each
variant class on local chromatin environment (reviewed in Oudelaar &
Higgs, 2021): loss-of-function variants (nonsense, frameshift) cause
complete loss of nascent transcription, which is coupled to local
chromatin remodeling and Mediator occupancy; synonymous variants
preserve transcription and chromatin state. ARCHCODE does not use VEP
scores, ClinVar classifications, or any sequence-based predictor output
as input --- the two models are mechanistically independent.

#strong[Position-only control:] To quantify the contribution of
category-dependent scaling to classification performance, a control mode
(`--effect-mode position-only`) applies a fixed effectStrength = 0.3 to
all variants regardless of category. In this mode, the only source of
SSIM variance is variant position relative to architectural features
(CTCF barriers, enhancers, MED1 landscape). The resulting AUC = 0.551
confirms that the reported AUC = 0.977 is attributable to the
categorical occupancy scaling, not to position-dependent structural
sensitivity (see Results: Position-Only Control Experiment).

=== Contact Matrix Generation
<contact-matrix-generation>
Contact probabilities are computed analytically using a mean-field
formula that combines four factors:

$ C(i,j) = |i - j|^(-1) dot sqrt("occ"_i dot "occ"_j) dot product_(k in "CTCF"(i,j)) p_k dot K(i,j) $ <eq:contact>

where:

- $|i - j|^(-1)$: genomic distance decay (polymer scaling)
- $sqrt("occ"_i dot "occ"_j)$: geometric mean of chromatin occupancy at bins $i$
  and $j$
- $product p_k$: product of CTCF barrier permeability values
  for all sites between $i$ and $j$
- $K(i,j)$: Kramers modulation factor derived from kinetics applied
  to the mean occupancy between $i$ and $j$

The resulting matrix is symmetric ($C(i,j) = C(j,i)$) and max-normalised
so that values lie in $[0, 1]$. The diagonal is set to 1.0. No Monte
Carlo steps are required.

#figure(
  image("../figures/fig6_contact_maps.png", width: 100%),
  caption: [ARCHCODE predicted contact maps for HBB 30 kb locus (50×50 matrix, 600 bp resolution). (A) Wild-type contact matrix showing distance-decay pattern modulated by CTCF barriers and enhancer occupancy. (B) Mutant contact matrix for Cd39 (C→T) nonsense variant, the most common β#super[0]-thalassemia allele. (C) Differential matrix (WT − Mutant) revealing localized contact loss near the mutation site (dotted crosshair). Color scale: contact probability (A, B); contact difference (C, diverging).],
) <fig:contact-maps>

=== SSIM Calculation
<ssim-calculation>
Structural Similarity Index (SSIM) between wild-type (WT) and mutant
(MUT) contact matrices:

$ "SSIM"("WT", "MUT") = frac((2 mu_"WT" mu_"MUT" + C_1)(2 sigma_("WT","MUT") + C_2), (mu_"WT"^2 + mu_"MUT"^2 + C_1)(sigma_"WT"^2 + sigma_"MUT"^2 + C_2)) $ <eq:ssim>

where:

- $mu$: mean intensity
- $sigma$: standard deviation
- $sigma_("WT","MUT")$: covariance
- $C_1 = (0.01 times L)^2$, $C_2 = (0.03 times L)^2$: stabilization constants ($L$ =
  dynamic range = 1.0)

SSIM was calculated over the upper triangular matrix (excluding
diagonal, k=1) to avoid self-contact artifacts.

== Ensembl VEP Comparison
<ensembl-vep-comparison>
=== VEP Methodology
<vep-methodology>
Sequence-level pathogenicity predictions were obtained using the Ensembl
Variant Effect Predictor (VEP) v113 REST API:

```
POST https://rest.ensembl.org/vep/homo_sapiens/region
```

Variants were submitted in batch mode (200 variants per request) with
hg38 reference coordinates. Each response was parsed for the most severe
consequence and, where available, SIFT scores for missense variants.

#strong[Consequence severity mapping] (consequence term → pathogenicity
score):

#figure(
  align(center)[#table(
    columns: (60.81%, 39.19%),
    align: (auto,auto,),
    table.header([Consequence], [Score],),
    table.hline(),
    [splice\_donor\_variant, splice\_acceptor\_variant], [0.95],
    [stop\_gained, frameshift\_variant], [0.90],
    [start\_lost, stop\_lost], [0.85],
    [missense\_variant], [derived from SIFT (see below)],
    [splice\_region\_variant], [0.50],
    [coding\_sequence\_variant], [0.20],
    [5\_prime\_UTR\_variant], [0.20],
    [upstream\_gene\_variant], [0.15],
    [3\_prime\_UTR\_variant], [0.15],
    [intron\_variant], [0.10],
    [synonymous\_variant], [0.05],
    [intergenic\_variant], [0.05],
    [other / unmapped], [0.10],
  )]
  , kind: table
  )

#strong[SIFT integration for missense variants:]

```
vep_score = 0.4 + 0.5 × (1 − sift_score)
```

where `sift_score` ∈ \[0, 1\] (0 = deleterious, 1 = tolerated). If SIFT
was unavailable, missense variants received a default score of 0.50.

#strong[Pearl detection threshold:] a variant was flagged as a Pearl
(ARCHCODE-VEP discordant case) when VEP score \< 0.30 AND SSIM \< 0.95.

=== Discordance Analysis
<discordance-analysis>
Variants were classified as discordant if verdicts differed between
methods:

#strong[ARCHCODE thresholds (analytical mean-field calibration):]

- SSIM \< 0.85: PATHOGENIC
- 0.85 ≤ SSIM \< 0.92: LIKELY\_PATHOGENIC
- 0.92 ≤ SSIM \< 0.96: VUS
- 0.96 ≤ SSIM \< 0.99: LIKELY\_BENIGN
- SSIM ≥ 0.99: BENIGN

#strong[VEP thresholds:]

- Score ≥ 0.50: Pathogenic / Likely Pathogenic
- Score \< 0.50: Benign / Likely Benign / VUS

== ClinVar Variant Dataset
<clinvar-variant-dataset>
=== Data Acquisition
<data-acquisition>
HBB variants were downloaded from ClinVar (2026-02-01 release) via the
NCBI E-utilities API (esearch + esummary endpoints), querying for gene
HBB with clinical significance Pathogenic, Likely Pathogenic, or VUS on
GRCh38/hg38 assembly.

#strong[Inclusion criteria:]

- Gene: #emph[HBB] (HGNC:4827)
- Clinical significance: Pathogenic OR Likely Pathogenic OR VUS
- Assembly: GRCh38/hg38
- Review status: ≥1 star (at least reviewed by submitter)
- Parseable ref/alt alleles (single-base substitutions, small
  insertions/deletions)

#strong[Exclusion criteria:]

- Complex indels without parseable ref/alt alleles (n=78 excluded)
- Large structural variants (\>100 bp)
- Variants in non-coding regions \>10 kb from gene body

Total downloaded: #strong[431 variants]\; after exclusion of 78 complex
indels: #strong[Final dataset: n=353 variants]

=== Variant Categorization
<variant-categorization>
Variants were annotated using VEP v113 REST API with the following
categories and counts:

#figure(
  align(center)[#table(
    columns: 2,
    align: (auto,auto,),
    table.header([Category], [n],),
    table.hline(),
    [missense], [125],
    [frameshift], [99],
    [nonsense], [40],
    [splice\_donor], [22],
    [promoter], [15],
    [3\_prime\_UTR], [13],
    [other], [12],
    [splice\_region], [9],
    [intronic], [9],
    [5\_prime\_UTR], [3],
    [splice\_acceptor], [3],
    [synonymous], [3],
    [#strong[Total]], [#strong[353]],
  )]
  , kind: table
  )

Category definitions:

- `splice_donor`, `splice_acceptor`: ±2 bp from exon boundary
- `splice_region`: ±8 bp from exon boundary (excluding donor/acceptor)
- `missense`, `nonsense`, `frameshift`
- `promoter`: -2000 to +200 bp from TSS
- `5_prime_UTR`, `3_prime_UTR`, `intronic`

== Statistical Analysis
<statistical-analysis>
=== Clustering Analysis
<clustering-analysis>
SSIM clustering was assessed using:

- #strong[Standard deviation:] σ = sqrt(Σ(x\_i - μ)² / (n-1))
- #strong[Coefficient of variation:] CV = σ / μ
- #strong[Z-score normalization:] z\_i = (x\_i - μ) / σ

Statistical significance of SSIM clustering for "Loop That Stayed"
variants was evaluated via permutation test:

+ Randomly sample 3 variants from the full 353-variant dataset
+ Calculate SD of SSIM scores
+ Repeat 10,000 times
+ Empirical p-value: fraction of permutations with SD ≤ observed SD
  (0.0022)

Result: p \< 0.0001 (none of 10,000 permutations achieved SD ≤ 0.0022)

=== ACMG Criteria Application
<acmg-criteria-application>
Variants were evaluated using ACMG/AMP 2015 guidelines (Richards et al.)
with the following evidence:

#strong[PS3\_moderate] (Functional studies):

- ARCHCODE SSIM-based prediction (analytical mean-field model)
- Supporting evidence: qualitative consistency with published cohesin
  dynamics; no formal R² validation against experimental data is
  available
- Moderate strength (not strong) due to computational vs experimental
  nature

#strong[PM2] (Rarity):

- gnomAD v4.0 allele frequency
- Threshold: MAF \< 0.0001 in all populations

#strong[PP3] (Multiple computational predictors):

- Conservation: PhyloP (vertebrate), PhastCons (mammalian)
- Structural: ARCHCODE SSIM
- Sequence: CADD, REVEL (supporting, though less weight for
  splice\_region)

#strong[Point assignment:]

- PS3\_moderate: 4 points
- PM2: 2 points
- PP3: 1 point
- #strong[Total: 7 points] (threshold for Likely Pathogenic: 6 points
  per ACMG)

== ROC Analysis and Benign Variant Evaluation
<roc-analysis-and-benign-variant-evaluation>
To assess discriminative performance, the pathogenic dataset (353
variants) was supplemented with 750 Benign/Likely Benign HBB variants
from ClinVar (queried via NCBI E-utilities API with significance filter
"benign" OR "likely benign"). #strong[All 1,103 variants were processed
through a single unified TypeScript simulation engine]
(`generate-unified-atlas.ts`), ensuring that `getEffectStrength()`
receives only the variant's functional category and never the ClinVar
classification label. This eliminates a pipeline discrepancy present in
the initial analysis where pathogenic and benign variants were processed
through different engines with incompatible perturbation scales. The
combined cohort (n=1,103) was used for ROC analysis with ClinVar
classification as ground truth (Pathogenic/LP = positive, Benign/LB =
negative) and (1 − SSIM) as the continuous predictor. AUC, sensitivity,
specificity, and Youden's J index were computed using scikit-learn v1.6.
Optimal SSIM threshold was determined by maximizing J = Sensitivity +
Specificity − 1.

== Within-Category Positional Signal Analysis
<within-category-positional-signal-analysis>
To test whether SSIM captures positional pathogenicity signal
independent of variant category, we performed three complementary
analyses on the unified 95 kb atlas (n = 1,103 variants):

#strong[Logistic regression (additive value test).] We fit two models:
Model 1: pathogenicity \~ category (11 dummy-coded categories); Model 2:
pathogenicity \~ category + SSIM. AUC improvement (ΔAUC) and
log-likelihood ratio test assessed whether SSIM adds predictive value
beyond category assignment.

#strong[Within-category Mann--Whitney U tests.] For each category with
≥3 pathogenic and ≥3 benign variants, a two-sided Mann--Whitney U test
compared SSIM distributions. Categories tested: intronic (9 pathogenic
vs 658 benign), other (12 vs 7), synonymous (3 vs 83).

#strong[Permutation testing.] For categories with ≥5 pathogenic
variants, we shuffled pathogenicity labels within category 10,000 times
and computed AUC(SSIM) for each permutation to derive empirical
p-values.

#strong[Distance-to-TSS correlation.] Spearman correlation between each
variant's distance to the HBB transcription start site (chr11:5,227,071)
and SSIM was computed per category to assess positional sensitivity of
the model independent of pathogenicity.

All analyses were performed using `scripts/analyze_positional_signal.py`
(SciPy 1.12.0, scikit-learn 1.6).

=== Experimental Scope Declaration
<experimental-scope-declaration>
This study is explicitly computational. All variant effect predictions
are _in silico_. No cell culture, animal work, or human subjects
research was performed. ARCHCODE generates structural hypotheses from
analytical physics; experimental validation by specialized laboratories
with erythroid differentiation and chromatin conformation assay
expertise is the intended next step (see Path to Clinical Translation).

== Software and Code Availability
<software-and-code-availability>
- #strong[ARCHCODE simulator:] https:/\/github.com/sergeeey/ARCHCODE
  (v1.1.0)
- #strong[Analysis scripts:] TypeScript (Node.js v20), Python 3.11;
  `scripts/bayesian_fit_hic.py` (Bayesian optimization)
- #strong[Visualization:] matplotlib 3.8.2
- #strong[Statistical analysis:] NumPy 1.26.3, SciPy 1.12.0, Optuna
  4.7.0
- #strong[Random number generation:] SeededRandom class (Mersenne
  Twister, seed=2026)

All simulations were run on:

- #strong[CPU:] AMD Ryzen 9 5900X (12 cores)
- #strong[RAM:] 64 GB DDR4-3200
- #strong[OS:] Windows 11 Pro (WSL2 for Python scripts)
- #strong[Compute time:] \< 1 second per variant (analytical approach),
  \~50 seconds total for 1,103 variants (unified pipeline)

== Data Availability
<data-availability>
All data supporting the findings of this study are available from the
corresponding author upon reasonable request. Key datasets include:

- Unified variant analysis (353 pathogenic + 750 benign = 1,103
  variants): `HBB_Unified_Atlas.csv`
- Legacy combined analysis (v1.0, dual-pipeline):
  `HBB_Combined_Atlas.csv`
- Pathogenic-only analysis (353 variants): `HBB_Clinical_Atlas_REAL.csv`
- Pearl analysis summary: `REAL_ATLAS_SUMMARY.json`
- VEP sequence-level predictions: `hbb_vep_results.csv`,
  `hbb_benign_vep_results.csv`
- ROC analysis (unified): `roc_unified.json`
- CFTR unified dataset: `CFTR_Unified_Atlas_317kb.csv` (3,349 rows)
- CFTR within-category analysis: `positional_signal_cftr.json`
- MLH1 unified dataset: `MLH1_Unified_Atlas_300kb.csv` (4,060 rows)
- MLH1 within-category analysis: `positional_signal_mlh1.json`
- Bayesian optimization results: `bayesian_fit_hic.json`
- Position-only control atlas:
  `HBB_Unified_Atlas_95kb_POSITION_ONLY.csv` (1,103 rows, fixed
  effectStrength=0.3)
- Source code: GitHub repository (see Software and Code Availability)


---




---


= Results
<results>
== ClinVar HBB variant dataset
<clinvar-hbb-variant-dataset>
We downloaded 431 HBB variant records from ClinVar via NCBI E-utilities
(esearch + esummary API, accessed 2026-02-28). After filtering for
records that contained both reference and alternate allele information,
353 variants were retained for analysis (78 records were excluded due to
missing allele data in the esummary response). The retained set
comprised 12 molecular consequence categories: nonsense (40), frameshift
(99), missense (125), splice\_donor (22), splice\_acceptor (3),
splice\_region (9), promoter (15), 5\_prime\_UTR (3), 3\_prime\_UTR
(13), intronic (9), synonymous (3), and other (12). ClinVar clinical
significance labels in the retained set included Pathogenic (234),
Pathogenic/Likely pathogenic (44), Likely pathogenic (46), Pathogenic
with other interpretations (28), and Pathogenic/Likely pathogenic with
other interpretations (1). No VUS remained in the final dataset after
filtering. All downstream analyses used clinical significance as
recorded in ClinVar without modification.


---


== ARCHCODE simulation of 353 HBB variants
<archcode-simulation-of-353-hbb-variants>
Each variant was simulated using the ARCHCODE analytical mean-field
contact model with Kramer kinetics (parameters: α=0.92, γ=0.80,
k\_base=0.002; see Methods for parameter provenance). Simulations
covered a 30 kb window centered on the HBB locus
(chr11:5,210,000--5,240,000, GRCh38) at 600 bp resolution (50 bins),
incorporating 6 CTCF anchor sites and 5 annotated enhancer/regulatory
elements (HBB proximal promoter, 3'HS1, and LCR-proximal elements). For
each variant, a wild-type (WT) contact matrix and a mutant contact
matrix were computed analytically. Structural disruption was quantified
using the Structural Similarity Index (SSIM) between WT and mutant
matrices, where SSIM = 1 indicates no structural change and SSIM
approaching 0 indicates complete disruption of the contact pattern. A
variant was classified as ARCHCODE-pathogenic if SSIM fell below the
threshold of 0.95 (see Methods for threshold selection rationale).


---


== ARCHCODE SSIM correlates with expected functional severity
<archcode-ssim-correlates-with-expected-functional-severity>
Mean SSIM values showed a clear monotonic relationship with expected
functional impact when variants were grouped by molecular consequence
category (Table 1). Synonymous variants, which do not alter the protein
sequence and are not expected to disrupt chromatin topology, returned
the highest mean SSIM (0.9989, n=3). Intronic and 3'UTR variants
likewise showed near-complete structural preservation (mean SSIM 0.9957
and 0.9942, respectively). Missense variants showed intermediate
structural preservation (mean SSIM 0.9526, n=125), consistent with
single amino-acid substitutions that do not typically remodel
loop-anchor sequences. Splice-donor variants showed more substantial
structural disruption (mean SSIM 0.9087, n=22), followed by frameshift
(0.8919, n=99) and nonsense variants (0.8753, n=40). The complete rank
order across all 12 categories is:

synonymous (0.9989) \> intronic (0.9957) \> 3'UTR (0.9942) \> 5'UTR
(0.9801) \> other (0.9676) \> splice\_region (0.9641) \> missense
(0.9526) \> promoter (0.9285) \> splice\_donor (0.9087) \>
splice\_acceptor (0.9019) \> frameshift (0.8919) \> nonsense (0.8753)

This ordering is biologically expected: loss-of-function variant classes
(nonsense, frameshift) produce the most severe chromatin disruption in
the model, while conservative substitutions (synonymous, deep intronic)
produce the least. The mean SSIM across all 353 variants was 0.9267
(per-variant values are available in Supplementary Table S1).

#strong[Table 1. ARCHCODE SSIM statistics by variant category.]

#figure(
  align(center)[#table(
    columns: (20.27%, 9.46%, 13.51%, 44.59%, 12.16%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM], [ARCHCODE Pathogenic
      (SSIM \< 0.95)], [%],),
    table.hline(),
    [nonsense], [40], [0.8753], [40], [100%],
    [frameshift], [99], [0.8919], [99], [100%],
    [splice\_acceptor], [3], [0.9019], [3], [100%],
    [splice\_donor], [22], [0.9087], [19], [86%],
    [promoter], [15], [0.9285], [0], [0%],
    [missense], [125], [0.9526], [0], [0%],
    [splice\_region], [9], [0.9641], [0], [0%],
    [other], [12], [0.9676], [0], [0%],
    [5\_prime\_UTR], [3], [0.9801], [0], [0%],
    [3\_prime\_UTR], [13], [0.9942], [0], [0%],
    [intronic], [9], [0.9957], [0], [0%],
    [synonymous], [3], [0.9989], [0], [0%],
    [#strong[Total]], [#strong[353]], [#strong[0.9267]], [#strong[161]], [#strong[45.6%]],
  )]
  , kind: table
  )

#figure(
  image("../figures/fig1_ssim_violin.png", width: 100%),
  caption: [LSSIM distribution across variant categories for 1,103 HBB ClinVar variants (353 Pathogenic/LP + 750 Benign/LB). Violin plots show density, with individual data points overlaid. Red: Pathogenic; Blue: Benign; Diamond markers: pearl variants (VEP-blind, structurally disruptive). Loss-of-function categories (nonsense, frameshift) cluster at low LSSIM, while neutral categories (synonymous, intronic) cluster near 1.0. Dashed red line: PATHOGENIC threshold (LSSIM \< 0.85); dotted gray line: VUS/LB boundary (LSSIM = 0.95).],
) <fig:ssim-violin>


---


== Concordance and discordance with VEP sequence-based predictions
<concordance-and-discordance-with-vep-sequence-based-predictions>
Across all 353 variants, ARCHCODE classified 161 (45.6%) as pathogenic
and the sequence- based VEP pipeline classified 287 (81.3%) as
pathogenic (mean VEP score 0.754 across the full dataset). Overall
discordance --- defined as variants where ARCHCODE and VEP verdicts
differ --- was observed in 130 variants (36.8% of the dataset). The
discordance was strongly asymmetric: 128 variants were called pathogenic
by VEP but not by ARCHCODE (VEP-only), and only 2 variants were called
pathogenic by ARCHCODE but not by VEP (ARCHCODE-only).

This asymmetry is mechanistically expected. VEP integrates SIFT,
consequence annotations (stop\_gained, frameshift\_variant,
splice\_donor\_variant, etc.), and conservation scores --- tools
calibrated primarily to detect local sequence-level damage to proteins
and splice signals. Most pathogenic HBB variants act through exactly
these local mechanisms: amino- acid substitution (missense, n=125) or
disruption of protein-coding reading frame (nonsense, frameshift, n=139
combined). ARCHCODE models 3D chromatin contact rearrangements within
the 30 kb simulation window, which is most sensitive to changes at CTCF
anchor sequences and enhancer elements --- changes that predominantly
occur in loss-of-function variants. Consequently, the 128 VEP-only
discordant variants are enriched for missense and splice\_region classes
where the pathogenic mechanism operates at the protein or spliceosome
level rather than through chromatin loop topology.

The 2 ARCHCODE-only variants (detected by ARCHCODE, missed by VEP)
represent candidates for further investigation. Their genomic positions
and variant details are provided in Supplementary Table S1; experimental
validation would be required before clinical conclusions could be drawn.


---


== Pearl variant discovery: structural disruption in VEP-blind loci
<pearl-variant-discovery-structural-disruption-in-vep-blind-loci>
We defined a "pearl variant" as a variant satisfying two criteria
simultaneously: VEP score \< 0.30 (indicating VEP classifies it as
low-impact or benign) AND SSIM \< 0.95 (indicating ARCHCODE detects
structural disruption). Twenty variants met both criteria (Table 2).
These represent cases where sequence-based prediction is blind but the
structural model detects disruption.

The 20 pearl variants fall into three groups by molecular context:

#strong[Group 1 --- Promoter variants (15 of 20 pearls).] Fifteen
variants map to positions 5,227,099--5,227,172 on chr11, within the HBB
proximal promoter region (SSIM range 0.927--0.930; VEP score 0.20 for
all). VEP annotates these as #emph[upstream\_gene\_variant], a
consequence term associated with low predicted impact in standard VEP
weighting schemes. However, the ARCHCODE simulation places this region
within a simulated enhancer element (LCR--HBB contact domain), and
substitutions here reduce modeled enhancer--promoter contact scores,
yielding SSIM values that fall below the 0.95 threshold. This represents
the key complementarity between the two approaches: VEP does not model
enhancer--promoter loop contacts and therefore cannot detect disruption
of these interactions, whereas ARCHCODE's physics-based loop extrusion
model is sensitive to changes at simulated anchor and enhancer sites.
Whether this simulated sensitivity corresponds to genuine experimental
disruption of chromatin contacts at these positions has not been
validated and remains to be tested.

#strong[Group 2 --- Missense variants at position 5,226,613 (3 of 20
pearls).] Three variants at chr11:5,226,613 returned SSIM=0.949 and
VEP=0.20. VEP annotates these as #emph[coding\_sequence\_variant], a
term typically applied to complex indels where consequence prediction is
ambiguous (poor annotation coverage). SSIM falls marginally below the
0.95 threshold. These are low-confidence pearls: the SSIM deviation is
small (0.001 below threshold) and VEP annotation quality is reduced for
complex indels.

#strong[Group 3 --- Loss-of-function variants with low VEP scores (2 of
20 pearls).] One frameshift variant at position 5,226,971 (SSIM=0.891,
VEP=0.15) and one splice\_acceptor variant at position 5,226,796
(SSIM=0.900, VEP=0.20) completed the pearl set. Their low VEP scores
likely reflect incomplete VEP annotation rather than genuinely low
pathogenicity; ClinVar records these as Pathogenic. These variants are
correctly identified by ARCHCODE (SSIM well below 0.95) but are included
here for completeness as they technically satisfy the pearl criteria.

Representative ClinVar accessions in the pearl set include (but are not
limited to): VCV002664746, VCV000811500, VCV000015208, VCV002024192,
VCV000869358, VCV000015471, VCV000015470, VCV000869288, VCV000869290,
VCV000015466. Full accession lists for all 20 pearl variants are
provided in Supplementary Table S1.

#strong[Table 2. Top 5 pearl variants by ARCHCODE structural disruption
(of 20 total; VEP \< 0.30 AND SSIM \< 0.95).]

#block[
  #set text(size: 9pt)
  #figure(
    align(center)[#table(
      columns: (18%, 14%, 12%, 7%, 6%, 43%),
      align: (left, left, left, right, right, left),
      inset: (x: 0.4em, y: 0.35em),
      table.header([*ClinVar\_ID*], [*HGVS\_c*], [*Category*], [*SSIM*], [*VEP*], [*Mechanism*]),
      table.hline(),
      [VCV000869358], [c.50dup], [frameshift], [0.892], [0.15], [LoF, VEP misannotated as synonymous\_variant],
      [VCV002024192], [c.93-33\_96delins…], [splice\_acc.], [0.900], [0.20], [Complex indel, VEP underscored],
      [VCV000015471], [c.-78A\>G], [promoter], [0.928], [0.20], [Promoter--enhancer loop disruption],
      [VCV000015470], [c.-78A\>C], [promoter], [0.928], [0.20], [Promoter--enhancer loop disruption],
      [VCV000036284], [c.-136C\>T], [promoter], [0.928], [0.20], [Promoter--enhancer loop disruption],
    )]
    , kind: table
  )
]

#emph[Full list of 20 pearls sorted by SSIM: Supplementary Table S1
(manuscript/TABLE\_S1\_PEARLS.md).]

#strong[Pearl summary by group:]

#figure(
  align(center)[#table(
    columns: (23.15%, 5.56%, 19.44%, 8.33%, 7.41%, 36.11%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([Group], [n], [Positions (chr11)], [Mean SSIM], [Mean
      VEP], [Molecular context],),
    table.hline(),
    [Promoter], [15], [5,227,099--5,227,172], [0.928], [0.20], [5\_prime\_UTR\_variant
    (HBB promoter)],
    [Missense at
    5226613], [3], [5,226,613], [0.949], [0.20], [coding\_sequence\_variant
    (complex indel)],
    [LoF (frameshift + splice)], [2], [5,226,796 /
    5,226,971], [0.896], [0.18], [frameshift / splice\_acceptor],
    [#strong[Total]], [#strong[20]], [---], [#strong[0.928]], [#strong[0.20]], [---],
  )]
  , kind: table
  )

#figure(
  image("../figures/fig3_pearl_quadrant.png", width: 80%),
  caption: [Pearl variant identification via VEP--ARCHCODE discordance. Scatter plot of VEP Score (sequence-based) vs ARCHCODE LSSIM (structural) for 1,103 HBB variants. Quadrants defined by VEP = 0.30 (horizontal) and LSSIM = 0.95 (vertical) thresholds. Q4 (bottom-right, gold): Pearl zone --- variants invisible to VEP but structurally disruptive by ARCHCODE. Star markers with red edge: pearl variants (n shown in quadrant label). Colors indicate variant category.],
) <fig:pearl-quadrant>


---


== ARCHCODE does not detect missense pathogenicity: an expected limitation
<archcode-does-not-detect-missense-pathogenicity-an-expected-limitation>
ARCHCODE classified 0% of missense variants as pathogenic (Table 1;
n=125, mean SSIM 0.9526). This is the most prominent limitation of the
current approach and must be stated explicitly. Missense variants are
the largest category in the HBB ClinVar dataset and include
well-validated pathogenic variants such as HbS (rs334, p.Glu7Val,
responsible for sickle-cell disease). These variants act through protein
structural perturbation --- a mechanism entirely outside ARCHCODE's
scope. ARCHCODE models chromatin contact topology, not protein folding
or function. A single-nucleotide substitution in a coding exon does not
substantially displace CTCF anchor sequences or enhancer elements at 600
bp resolution within a 30 kb window, and therefore produces SSIM near
1.0 regardless of protein-level impact.

Similarly, ARCHCODE classified 0% of intronic (n=9), synonymous (n=3),
3'UTR (n=13), and splice\_region (n=9) variants as pathogenic. While
some of these (particularly splice\_region and intronic) may carry
genuine pathogenicity through mechanisms such as cryptic splice-site
activation or branch-point disruption, the current ARCHCODE model does
not include sequence- based splice scoring. These variants are therefore
invisible to ARCHCODE unless they happen to coincide with a simulated
CTCF anchor or enhancer element at 600 bp resolution.

These results reinforce the interpretation that ARCHCODE and
sequence-based predictors such as VEP are orthogonal tools, each
capturing a distinct mechanism. ARCHCODE is sensitive to structural
disruption of chromatin loop domains (strongest signal for nonsense and
frameshift at CTCF-adjacent positions) and, in the pearl analysis,
potentially to enhancer--promoter contact disruption in the HBB promoter
region. VEP is sensitive to protein-level changes, canonical splice-site
disruption, and sequence conservation. The clinical utility of combining
both approaches lies precisely in the complementarity between these two
mechanistic blind spots.


---


== ROC Analysis: Discrimination of Pathogenic vs Benign Variants
<roc-analysis-discrimination-of-pathogenic-vs-benign-variants>
To evaluate ARCHCODE's discriminative performance, we expanded the
dataset to include 750 Benign/Likely Benign HBB variants from ClinVar
(predominantly intronic, n=658; synonymous, n=83), yielding a combined
cohort of 1,103 variants (353 Pathogenic/LP + 750 Benign/LB).
#strong[All 1,103 variants were processed through a single unified
TypeScript simulation engine], ensuring label-blind physics:
`getEffectStrength()` receives only the functional category, never the
ClinVar classification. Using ClinVar classification as ground truth and
(1 − SSIM) as the predictor, ROC analysis yielded AUC = 0.977
(Pathogenic mean SSIM = 0.927; Benign mean SSIM = 0.996; range
0.968--0.999).

#strong[Threshold evaluation by Youden's J index:]

#figure(
  align(center)[#table(
    columns: (51.61%, 17.74%, 17.74%, 12.9%),
    align: (auto,auto,auto,auto,),
    table.header([SSIM threshold], [Sensitivity], [Specificity], [Youden
      J],),
    table.hline(),
    [\< 0.994 (Youden optimum)], [0.966], [0.988], [0.954],
    [\< 0.99], [0.935], [0.989], [0.924],
    [\< 0.96], [0.875], [1.000], [0.875],
    [\< 0.95 (current pearl threshold)], [0.620], [1.000], [0.620],
    [\< 0.92 (LIKELY\_PATHOGENIC)], [0.456], [1.000], [0.456],
    [\< 0.85 (PATHOGENIC)], [0.009], [1.000], [0.009],
  )]
  , kind: table
  )

At stringent thresholds (SSIM \< 0.96 and below), specificity remains
1.000. At the Youden optimum (SSIM \< 0.994), 8 Benign variants fall
below the threshold (all from the "other" and "5\_prime\_UTR"
categories), yielding specificity = 0.988.

#strong[Note on pipeline unification:] An initial analysis using
separate processing pipelines for pathogenic (TypeScript) and benign
(Python) variants yielded AUC = 1.000 due to a 10-fold difference in
perturbation scaling between engines (e.g., intronic: 20% vs 2%
occupancy reduction). After unifying all variants through a single
engine, benign intronic SSIM decreased from 1.000 to 0.996 --- matching
pathogenic intronic SSIM (0.996) --- and AUC dropped to 0.977. This
confirms that the previous perfect AUC was a pipeline artifact. The
current AUC of 0.977 reflects the genuine category-distribution
difference between Pathogenic (enriched in nonsense/frameshift/splice)
and Benign (enriched in intronic/ synonymous) cohorts, not independent
variant-level prediction.

#strong[Critical caveat on AUC interpretation:] The AUC reflects
category-distribution differences between the Pathogenic and Benign
cohorts (see Methods: Variant Introduction). Benign ClinVar variants are
predominantly intronic and synonymous, which receive minimal occupancy
perturbation by design. Pathogenic variants include nonsense,
frameshift, and splice categories, which receive stronger perturbation.
Formal within-category testing confirms that SSIM does not add
significant predictive value beyond category on this locus:

- #strong[Logistic regression:] pathogenicity \~ category + SSIM yields
  ΔAUC = −0.001 relative to category-only model (log-likelihood ratio p
  \= 1.0).
- #strong[Mann--Whitney U (intronic):] 9 pathogenic vs 658 benign, Δ
  mean SSIM = 0.000008, p = 0.69 (two-sided).
- #strong[Mann--Whitney U (other):] 12 pathogenic vs 7 benign, Δ =
  −0.0009, p = 0.058.
- #strong[Mann--Whitney U (synonymous):] 3 pathogenic vs 83 benign, Δ =
  −0.00006, p = 0.22.
- #strong[Permutation test (other, n = 19):] observed AUC = 0.77,
  empirical p = 0.032.

The null result is consistent with a fundamental data limitation: all
1,103 ClinVar HBB variants cluster within 2.1 kb of the 95 kb simulation
window (2.2%), producing near-zero variance in distance to regulatory
features (CTCF anchors: 20--23 kb, LCR: 53--55 kb). The model #emph[is]
positionally sensitive --- distance-to-TSS correlates strongly with SSIM
(intronic Spearman ρ = 0.80, splice\_donor ρ = 0.92, p \< 10⁻⁹) --- but
this sensitivity affects pathogenic and benign variants equally because
they occupy the same narrow genomic interval.

The model's scientific contribution on HBB is therefore a category-level
structural model: it correctly assigns perturbation magnitude to
functional categories and identifies 20 pearl candidates, but does not
independently predict pathogenicity within categories at this locus.

=== Position-Only Control Experiment
<position-only-control-experiment>
To definitively quantify the contribution of variant category to the
AUC, we ran an ablation experiment: all 1,103 HBB variants were
re-processed with a fixed effectStrength = 0.3 for every variant
regardless of functional category (`--effect-mode position-only`). In
this configuration, the only source of SSIM variance is variant
#strong[position] relative to CTCF barriers, enhancers, and the MED1
occupancy landscape --- no sequence-level information enters the model.

#figure(
  align(center)[#table(
    columns: 3,
    align: (auto,center,center,),
    table.header([Metric], [Categorical model], [Position-only model],),
    table.hline(),
    [Global LSSIM AUC], [0.976], [#strong[0.551]],
    [Path mean LSSIM], [0.882], [0.895],
    [Ben mean LSSIM], [0.993], [0.890],
    [Δ(mean LSSIM)], [−0.111], [+0.005],
    [Within-intronic AUC], [0.524], [0.530],
    [Within-synonymous AUC], [0.570], [0.558],
  )]
  , kind: table
  )

The position-only AUC of 0.551 is indistinguishable from chance (0.5),
confirming that variant position within the 95 kb window does not
discriminate pathogenic from benign variants. Both cohorts occupy a 2.1
kb cluster in the gene body, producing near-identical MED1 occupancy
environments. The within-category AUC remains unchanged (\~0.53),
consistent with position being the sole residual signal in both models.

We also tested a CADD-based effectStrength mapping (sigmoid transform of
CADD phred scores), which yielded within-synonymous AUC = 0.988 ---
revealing that CADD scores themselves discriminate pathogenic from
benign within categories, creating a new circularity rather than
resolving the original one. This approach was therefore rejected.

#strong[Conclusion:] The AUC of 0.977 is entirely attributable to the
categorical effectStrength mapping (nonsense = 0.1 vs intronic = 0.8),
which encodes the well-established correlation between functional
consequence and clinical significance. ARCHCODE's structural model
provides value through Hi-C contact prediction (r = 0.53--0.59) and
pearl identification, not through independent variant-level
pathogenicity discrimination.

#figure(
  image("../figures/fig2_roc_curves.png", width: 80%),
  caption: [ROC analysis: categorical model (AUC = 0.976, solid blue) vs position-only control (AUC = 0.551, dashed gray) for 1,103 HBB variants. Red dot: Youden optimal threshold. Inset: within-category AUC comparison for categories containing both pathogenic and benign variants. The position-only model (fixed effectStrength = 0.3 for all variants) performs at chance, confirming that the categorical model's AUC reflects category-distribution differences, not independent structural prediction.],
) <fig:roc-curves>


---


== CFTR Locus: Cross-Gene Generalization
<cftr-locus-cross-gene-generalization>
The within-category null result on HBB reflected a data limitation: all
1,103 variants cluster within 2.1 kb (2.2% of the 95 kb window). To test
whether greater variant positional diversity would reveal
within-category signal, we extended ARCHCODE to the CFTR locus
(chr7:116,907,253--117,224,349, 317 kb TAD, 1000 bp resolution, 317
bins).

We retrieved 3,349 CFTR variants from ClinVar (1,756 Pathogenic/Likely
Pathogenic + 1,593 Benign/Likely Benign). Unlike HBB, CFTR variants span
201.5 kb (63.6% of the simulation window), providing 29-fold greater
positional diversity. The variant composition includes: synonymous
(n=1,799), intronic (n=779), frameshift (n=516), splice\_region (n=149),
other (n=54), 5'UTR (n=19), inframe\_deletion (n=17), inframe\_indel
(n=9), 3'UTR (n=6), and splice\_donor (n=1). Variant functional
categories were assigned using improved HGVS parsing that determines
frameshift vs inframe status from cDNA indel length modulo 3 (see
Methods).

#strong[Table 3. CFTR SSIM statistics by variant category (317 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.81%, 8.77%, 28.07%, 26.32%, 14.04%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [516], [0.9986], [N/A], [---],
    [Splice region], [149], [0.9997], [0.9996], [0.84],
    [Synonymous], [1,799], [1.0000], [1.0000], [9.1×10⁻⁶],
    [Intronic], [779], [1.0000], [1.0000], [0.28],
    [Other], [54], [0.9992], [0.9983], [0.10],
    [5'UTR], [19], [0.9975], [0.9971], [0.10],
    [Inframe del.], [17], [0.9992], [N/A], [---],
    [3'UTR], [6], [0.9999], [0.9999], [---],
  )]
  , kind: table
  )

Global SSIM values were severely compressed compared to HBB (range
0.9836--1.0000 vs 0.9611--0.9998 at 95kb), reflecting matrix-size
dilution: a single-bin perturbation in a 317×317 matrix affects
proportionally fewer entries than in a 50×50 matrix. LSSIM (50×50 local
window) resolved this, expanding the range to 0.8329--0.9999 and
enabling 35 structural pathogenic verdicts. Frameshift variants (n=516,
all pathogenic) show the lowest mean SSIM (0.9986), consistent with
their strong occupancy perturbation.

Despite the greater positional diversity, within-category testing using
LSSIM confirmed the null result. Logistic regression (pathogenicity \~
category + LSSIM) yielded ΔAUC = −0.012 (p = 0.79). LSSIM does not
predict pathogenicity within functional categories on CFTR.

No CFTR variants met the pearl criteria (LSSIM \< 0.95 and VEP \< 0.30):
VEP data was not available for this locus. Pearl detection requires both
VEP and structural signals.


---


== TP53 Locus: Third Cross-Gene Test
<tp53-locus-third-cross-gene-test>
To further probe generalizability, we extended ARCHCODE to the TP53
tumor suppressor locus (chr17:7,550,000--7,850,000, 300 kb TAD, 1000 bp
resolution, 300 bins). TP53 was selected because it ranks among the most
clinically consequential genes in oncology, resides on chr17 (same
chromosome as BRCA1, enabling shared CTCF data from ENCODE K562
ENCFF736NYC), and has extensive ClinVar variant coverage.

We retrieved 2,794 TP53 variants from ClinVar (1,645 Pathogenic/Likely
Pathogenic + 1,149 Benign/Likely Benign). Variants span 109.9 kb (36.6%
of the 300 kb window) --- intermediate between HBB (2.2%) and CFTR
(63.6%). The improved classify\_hgvs() function resolved the majority of
previously unclassified variants: synonymous (n=1,400), frameshift
(n=534), intronic (n=528), splice\_region (n=139), inframe\_deletion
(n=76), other (n=53), inframe\_indel (n=35), 3'UTR (n=22), and 5'UTR
(n=8).

#strong[Table 4. TP53 SSIM statistics by variant category (300 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.41%, 8.62%, 27.59%, 25.86%, 15.52%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [534], [0.9964], [N/A], [---],
    [Splice region], [139], [0.9980], [0.9986], [8.0×10⁻⁵],
    [Inframe del.], [76], [0.9986], [0.9993], [0.060],
    [Inframe indel], [35], [0.9988], [0.9993], [0.060],
    [Synonymous], [1,400], [0.9999], [1.0000], [6.2×10⁻¹⁰],
    [Intronic], [528], [0.9998], [0.9998], [0.029],
    [Other], [53], [0.9982], [0.9993], [0.0025],
    [3'UTR], [22], [0.9999], [0.9999], [0.79],
    [5'UTR], [8], [0.9984], [N/A], [---],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9934 to 1.0000, severely compressed by
matrix-size dilution. LSSIM expanded the range to 0.9443--1.0000 ---
narrower than other loci but sufficient to assign 12 VUS verdicts (0
PATHOGENIC/LIKELY\_PATHOGENIC).

Within-category testing using LSSIM yielded a null result: logistic
regression ΔAUC = +0.032 (p = 0.29). TP53 has the narrowest LSSIM range
among all loci, consistent with its high CTCF density and complex
promoter architecture reducing the relative perturbation signal even in
the local window.

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.29 (p \<
10⁻¹⁵⁴, n = 7,821 loci); MCF7 Hi-C yielded r = 0.28 (p \< 10⁻¹³⁶, n =
7,821). Both are statistically significant but substantially lower than
HBB (r = 0.53--0.59) and BRCA1 (r = 0.50--0.53), likely reflecting the
greater structural complexity of the TP53 locus (7 H1 persistent
homology features vs 3--4 for HBB), the presence of the internal P2
promoter generating Δ133p53 isoforms, and higher CTCF density in the
TP53 genomic neighborhood.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.85 (p = 0.015), confirming that topological
perturbation and SSIM disruption remain correlated on this locus, though
weaker than HBB (ρ = −0.96) and CFTR (ρ = −1.00).


---


== BRCA1 Locus: Largest ClinVar Cohort
<brca1-locus-largest-clinvar-cohort>
The BRCA1 breast cancer susceptibility gene
(chr17:42,900,000--43,300,000, 400 kb TAD, 1000 bp resolution, 400 bins)
provided the largest variant cohort and a critical test of ARCHCODE in a
clinically high-impact oncogene with well-characterized regulatory
architecture. BRCA1 shares chr17 with TP53, enabling reuse of the same
ENCODE K562 CTCF ChIP-seq peaks (ENCFF736NYC). MCF7 breast cancer cell
line data was used as the primary enhancer source (H3K27ac, ENCFF340KSH)
because BRCA1 is actively transcribed in breast tissue.

We retrieved 10,682 BRCA1 variants from ClinVar (7,062 Pathogenic/Likely
Pathogenic + 3,620 Benign/Likely Benign) --- by far the largest cohort
in this study. Variants span 103.6 kb (25.9% of the 400 kb window). The
improved classify\_hgvs() function yielded: synonymous (n=5,520),
frameshift (n=2,806), intronic (n=1,584), splice\_region (n=363), other
(n=221), inframe\_indel (n=56), 3'UTR (n=48), 5'UTR (n=46),
inframe\_deletion (n=37), and splice\_donor (n=1).

#strong[Table 5. BRCA1 SSIM statistics by variant category (400 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.41%, 8.62%, 27.59%, 25.86%, 15.52%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [2,806], [0.9995], [N/A], [---],
    [Splice region], [363], [0.9999], [0.9999], [0.68],
    [Synonymous], [5,520], [1.0000], [1.0000], [0.53],
    [Intronic], [1,584], [1.0000], [1.0000], [0.0014],
    [Other], [221], [0.9998], [0.9982], [2.4×10⁻²⁶],
    [5'UTR], [46], [0.9985], [0.9985], [0.32],
    [3'UTR], [48], [1.0000], [1.0000], [1.0],
    [Inframe indel], [56], [0.9999], [0.9999], [0.80],
    [Inframe del.], [37], [0.9998], [0.9999], [0.57],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9938 to 1.0000, the most compressed
range of any locus --- consistent with the largest matrix size
(400×400). LSSIM expanded the range to 0.8767--0.9999, enabling 52
structural pathogenic verdicts.

Within-category testing using LSSIM yielded the first statistically
significant result: logistic regression ΔAUC = +0.002 (p ≈ 10⁻²⁰).
However, the effect size is negligible (ΔAUC \< 0.002). This
significance reflects the massive statistical power (n = 10,682)
combined with LSSIM's expanded dynamic range, not meaningful
within-category prediction. For synonymous (n=5,520, the largest
single-category test), MW-U p = 0.003 --- statistically significant but
ΔLSSIM still negligible.

No BRCA1 pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.53 (p ≈ 0,
n = 12,093 loci); MCF7 Hi-C yielded r = 0.50 (p ≈ 0, n = 7,307). Both
are comparable to HBB K562 results (r = 0.53), demonstrating that
ARCHCODE's contact model generalizes well to loci with dense regulatory
architecture. The similar K562 and MCF7 correlations suggest that the
architectural features driving the model (distance decay, CTCF
positions, enhancer occupancy) are largely cell-type-invariant at this
resolution.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = NaN (all category-level perturbations produced zero
TDA signal at 400×400 resolution). Positional scan showed ρ = −0.21 (p =
0.43, not significant), indicating that TDA sensitivity drops sharply
with increasing matrix size, consistent with the dilution
interpretation.


---


== MLH1 Locus: First DNA Mismatch Repair Gene
<mlh1-locus-first-dna-mismatch-repair-gene>
The MLH1 mismatch repair gene (chr3:36,900,000--37,200,000, 300 kb TAD,
1000 bp resolution, 300 bins) introduced the first DNA repair gene into
ARCHCODE's multi-locus portfolio. MLH1 is associated with Lynch syndrome
(hereditary nonpolyposis colorectal cancer) and features a bidirectional
CpG island promoter shared with EPM2AIP1. The locus config includes 7
CTCF sites and 8 enhancers from ENCODE K562 ChIP-seq (CTCF: ENCFF736NYC;
H3K27ac: ENCFF864OSZ).

We retrieved 4,060 MLH1 variants from ClinVar (2,425 Pathogenic/Likely
Pathogenic + 1,635 Benign/Likely Benign). Variants span 130.3 kb (43.4%
of the 300 kb window). The improved classify\_hgvs() function yielded:
synonymous (n=1,592), frameshift (n=1,029), intronic (n=955),
splice\_region (n=286), other (n=105), inframe\_deletion (n=34), 5'UTR
(n=26), inframe\_indel (n=19), 3'UTR (n=13), and splice\_donor (n=1).

#strong[Table 5b. MLH1 SSIM statistics by variant category (300 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.81%, 8.77%, 28.07%, 26.32%, 14.04%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [1,029], [0.9983], [0.9995], [---],
    [Splice region], [286], [0.9996], [0.9990], [6.7×10⁻⁸],
    [Synonymous], [1,592], [1.0000], [1.0000], [0.76],
    [Intronic], [955], [1.0000], [1.0000], [0.19],
    [Other], [105], [0.9990], [0.9990], [2.0×10⁻⁴],
    [5'UTR], [26], [0.9969], [0.9971], [0.79],
    [3'UTR], [13], [0.9999], [0.9999], [1.0],
    [Inframe indel], [19], [0.9986], [0.9998], [---],
    [Inframe del.], [34], [0.9995], [N/A], [---],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9838 to 1.0000 --- comparable to TP53
(also 300×300). LSSIM expanded the range to 0.8417--0.9999, enabling 72
structural pathogenic verdicts.

Within-category testing using LSSIM yielded a statistically significant
result: logistic regression ΔAUC = +0.011 (p = 0.005). As with BRCA1,
the significance reflects statistical power at n = 4,060 combined with
LSSIM's expanded dynamic range, rather than meaningful within-category
prediction (ΔAUC \< 0.02). ARCHCODE remains primarily a category-level
classifier.

No MLH1 pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.59 (p ≈ 0,
n = 20,432 loci), the highest single-cell-type correlation across all
loci --- tied with HBB 95kb. This strong result likely reflects the MLH1
locus's well-defined regulatory architecture: a strong intergenic CTCF
boundary (signal = 178.7) at chr3:36,958,900 and an active promoter with
high H3K27ac enrichment (signal = 62.9). The K562 source was used
because HCT116 (where MLH1 is epigenetically silenced) Hi-C data was
inaccessible within the study timeframe.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.76 (p = 0.049), significant but weaker than HBB
(ρ = −0.96) and CFTR (ρ = −1.00), and stronger than TP53 (ρ = −0.85).
Positional scan across 15 positions showed ρ = −0.64 (p = 0.011),
confirming consistent SSIM--TDA correspondence at 300×300 resolution.

== LDLR Locus: Tissue-Specific Chromatin Validation
<ldlr-locus-tissue-specific-chromatin-validation>
LDLR (Low-Density Lipoprotein Receptor, chr19p13.2) encodes the primary
receptor for LDL cholesterol clearance. Germline pathogenic variants
cause Familial Hypercholesterolemia (FH), affecting \~1:250 individuals
worldwide. LDLR is the first ARCHCODE locus validated with
tissue-specific Hi-C data (HepG2 hepatocyte line) rather than K562.

#strong[Variant analysis:] 3,284 ClinVar variants (2,274 P/LP + 1,010
B/LB) were analyzed in a 300kb window (chr19:10,940,000--11,240,000) at
1kb resolution. The window contains 6 genes including SMARCA4 (SWI/SNF
chromatin remodeler) upstream. CTCF sites from ENCODE HepG2
(ENCSR000AMA, 10 peaks) co-localize with K562 CTCF at 7/10 positions,
confirming cell-type invariance. H3K27ac from HepG2 (ENCSR000AMO) shows
a 6.3kb super-enhancer at the LDLR promoter (signal = 111.3), consistent
with high LDLR expression in hepatocytes under SREBP regulation.

#strong[SSIM results:] Global SSIM range 0.9895--1.0000; LSSIM range
0.9061--1.0000. LSSIM identified 10 structurally pathogenic variants.
Variant spread is only 2.1 kb (0.7% of window), similar to HBB --- all
ClinVar variants cluster within the LDLR gene body.

#strong[Within-category analysis:] Logistic regression shows statistical
significance (p = 0.004) but ΔAUC = −0.003, confirming the power-effect
pattern seen in BRCA1 and MLH1. Mann-Whitney U test within the "other"
category shows significant separation (Δ = −0.007, p = 0.008), while
intronic and synonymous categories show no signal. ARCHCODE remains a
category-level classifier.

No LDLR pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] HepG2 Hi-C correlation yielded r = 0.32 (p ≈
0, n = 19,156 loci). This is the first tissue-specific validation: LDLR
is highly expressed in hepatocytes, and HepG2 Hi-C captures
liver-specific chromatin architecture. The correlation is comparable to
TP53 (K562 r = 0.29) and lower than HBB/MLH1 (r = 0.53--0.59), likely
reflecting the gene-dense chr19 environment where multiple regulatory
domains create complex contact patterns that the mean-field model
captures partially.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.51 (p = 0.24), the weakest TDA--SSIM
correspondence across all loci. Bottleneck distance showed stronger
correlation (ρ = −0.80, p = 0.03). Positional scan across 15 positions
showed ρ = −0.09 (p = 0.76), indicating that TDA captures complementary
topological information not fully reflected in SSIM at this locus.


---


== SCN5A Locus: Cell-Type Mismatch as Negative Control
<scn5a-locus-cell-type-mismatch-as-negative-control>
SCN5A (Sodium Voltage-Gated Channel Alpha Subunit 5, chr3p22.2) encodes
the primary cardiac sodium channel (Nav1.5). Pathogenic variants cause
Brugada syndrome, Long QT syndrome type 3, and other cardiac
arrhythmias. SCN5A is the first cardiac-expressed gene in the ARCHCODE
portfolio and serves as a deliberate test of cell-type specificity: the
model uses K562 (erythroid) ENCODE data for a gene primarily expressed
in cardiomyocytes.

#strong[Variant analysis:] 2,488 ClinVar variants (928 P/LP + 1,560
B/LB) were analyzed in a 400kb window (chr3:38,400,000--38,800,000) at
1kb resolution. The window contains 6 genes including SCN10A (\~47kb
downstream, another sodium channel). K562 CTCF ChIP-seq (ENCFF736NYC)
identified 14 peaks including a very strong cluster at the SCN5A TSS
(signal = 306.8, 178.3, 72.8). However, K562 H3K27ac (ENCFF864OSZ)
captures only 3 peaks in the entire 400kb window --- the weakest
enhancer annotation of any ARCHCODE locus --- reflecting minimal SCN5A
regulatory activity in erythroid cells.

#strong[SSIM results:] Global SSIM range 0.9995--1.0000; LSSIM range
0.9960--1.0000. Zero structurally pathogenic variants were identified (0
pearls). The near-unit SSIM values across all 2,488 variants demonstrate
that ARCHCODE's perturbation model produces negligible signal when the
enhancer annotation is sparse --- the 3 K562 H3K27ac peaks do not provide
sufficient regulatory context for meaningful variant-level
discrimination.

#strong[AlphaGenome benchmark:] ρ = −0.17 (Pearson r = −0.08), the
lowest across all seven loci. AlphaGenome contact maps were obtained
from GM12878 (lymphoblastoid --- no K562 available). The near-zero
correlation reflects both cell-type mismatch and the sparse regulatory
context: without tissue-appropriate enhancer features, the analytical
model cannot reconstruct a contact pattern that meaningfully corresponds
to deep learning predictions from sequence.

#strong[Epigenome cross-validation:] CTCF recall remains 100% (14/14
sites, F1 = 0.76), confirming that CTCF binding is cell-type invariant
even for this cardiac gene. H3K27ac recall is 67% (2/3, F1 = 0.18), with
the lowest F1 across all loci --- consistent with the minimal K562
H3K27ac signal at a cardiac gene.

#strong[Interpretation.] SCN5A establishes a critical negative control:
ARCHCODE's discriminative power is contingent on cell-type-appropriate
regulatory annotation. When enhancer data is absent (3 peaks vs 7--14 at
other loci), the model correctly produces near-null perturbation for all
variants rather than generating false positives. This validates that
ARCHCODE's structural pathogenicity verdicts arise from biologically
meaningful regulatory features, not computational artifacts. Future
SCN5A analysis should use iPSC-CM (induced pluripotent stem cell-derived
cardiomyocyte) Hi-C and H3K27ac data, which would capture
cardiac-specific enhancers and potentially reveal structural
pathogenicity in the same variants.


---


== Multi-Locus Comparison
<multi-locus-comparison>
#strong[Table 6a. Dataset overview and structural classification across seven loci.]

#figure(
  align(center)[#table(
    columns: (18%, 10%, 16%, 14%, 14%, 12%, 8%),
    align: (left, center, center, center, center, center, center),
    table.header([Locus (window)], [_n_], [P/LP + B/LB], [Variant spread], [LSSIM range], [Struct. path.], [Pearls]),
    table.hline(),
    [HBB (95 kb)], [1,103], [353 + 750], [2.1 kb (2.2%)], [0.75--1.00], [254], [27],
    [CFTR (317 kb)], [3,349], [1,756 + 1,593], [201.5 kb (63.6%)], [0.83--1.00], [35], [0],
    [TP53 (300 kb)], [2,794], [1,645 + 1,149], [109.9 kb (36.6%)], [0.94--1.00], [0 (12 VUS)], [0],
    [BRCA1 (400 kb)], [10,682], [7,062 + 3,620], [103.6 kb (25.9%)], [0.88--1.00], [52], [0],
    [MLH1 (300 kb)], [4,060], [2,425 + 1,635], [130.3 kb (43.4%)], [0.84--1.00], [72], [0],
    [LDLR (300 kb)], [3,284], [2,274 + 1,010], [2.1 kb (0.7%)], [0.91--1.00], [10], [0],
    [SCN5A (400 kb)], [2,488], [928 + 1,560], [101.7 kb (25.4%)], [1.00--1.00], [0], [0],
    table.hline(),
    [*Total*], [*27,760*], [], [], [], [*423*], [*27*],
  )]
  , kind: table
)

#v(0.5em)

#strong[Table 6b. Validation metrics across seven loci.]

#figure(
  align(center)[#table(
    columns: (12%, 16%, 10%, 12%, 10%, 10%, 14%, 14%),
    align: (left, center, center, center, center, center, center, center),
    table.header([Locus], [LR ΔAUC], [K562 _r_], [Other _r_], [AG ρ], [Akita ρ], [CTCF F1], [H3K27ac F1]),
    table.hline(),
    [HBB], [−0.001 (p=1.0)], [0.53 / 0.59], [---], [0.15 / 0.12†], [0.13 / −0.27†], [0.83], [---],
    [CFTR], [−0.012 (p=0.79)], [---], [---], [0.27], [0.41], [0.65], [---],
    [TP53], [+0.031 (p=0.29)], [0.29], [MCF7: 0.28], [0.32], [0.17], [0.74], [0.40],
    [BRCA1], [+0.002 (p≈10⁻²⁰)], [0.53], [MCF7: 0.50], [0.52], [0.43], [0.80], [0.67],
    [MLH1], [+0.011 (p=0.005)], [0.59], [---], [0.49], [0.22], [0.54], [0.29],
    [LDLR], [−0.003 (p=0.004)], [---], [HepG2: 0.32], [0.43], [0.34], [0.65], [0.57],
    [SCN5A], [‡], [---], [---], [−0.17], [---], [0.76], [0.18],
  )]
  , kind: table
)

CTCF recall = 100% for all loci; F1 values shown. †HBB AG/Akita values:
30kb / 95kb windows. Both DL models yield only 15 (30kb) or 47 (95kb)
bins at 2048 bp resolution, requiring 3.4× upsampling to match
ARCHCODE's 159 bins. The negative Akita ρ for 95kb likely reflects
interpolation artifacts. ‡SCN5A: LR ΔAUC not computed --- zero
structural pathogenicity calls (all LSSIM \> 0.99).

The multi-locus comparison reveals three consistent patterns: (1) LSSIM
resolves matrix-size dilution, expanding dynamic range from 0.98--1.00
(global SSIM) to 0.75--1.00 across all loci, enabling verdict assignment
on matrices up to 400×400; (2) within-category LSSIM shows null results
on smaller cohorts (CFTR p = 0.79, TP53 p = 0.29) but statistically
significant signal on larger cohorts (BRCA1 p ≈ 10⁻²⁰, MLH1 p = 0.005),
though effect sizes are negligible (ΔAUC \< 0.02 in both cases); (3)
Hi-C correlation varies by locus, with the highest values for loci where
the model's enhancer/CTCF configuration best captures the dominant
regulatory architecture. The BRCA1 and MLH1 within-category significance
reflects statistical power (n \> 4,000) rather than meaningful
positional prediction. MLH1 achieves the joint-highest K562 Hi-C
correlation (r = 0.59, tied with HBB 95kb), suggesting that strong CTCF
boundaries and well-characterized promoter architecture are key drivers
of model fidelity. (4) AlphaGenome benchmark (AG ρ) shows consistent
moderate correlation (Spearman ρ = 0.12--0.52) between ARCHCODE's
analytical contact maps and AlphaGenome's deep learning predictions
across six of seven loci after distance normalization (O/E), with the
strongest agreement at BRCA1 (ρ = 0.52) and MLH1 (ρ = 0.49) --- loci
with the most complete CTCF/enhancer annotation. SCN5A is the exception
(ρ = −0.17), consistent with severe cell-type mismatch: K562 captures
only 3 H3K27ac peaks across the 400 kb window, producing a near-empty
enhancer environment for this cardiac-expressed gene. (5) Epigenome
cross-validation confirms 100% CTCF recall across all seven loci (mean
F1 = 0.71): AlphaGenome independently predicts CTCF binding at every
ENCODE-annotated position used in ARCHCODE configs, validating the input
data for the structural model. (6) SCN5A serves as a deliberate negative
control for cell-type specificity: zero structural pathogenicity calls
(0 pearls), near-unit SSIM across all 2,488 variants, and the lowest
AlphaGenome correlation demonstrate that ARCHCODE's discriminative power
depends on appropriate cell-type-matched regulatory annotation --- not
on computational artifacts.

#figure(
  image("../figures/fig4_hic_validation.png", width: 100%),
  caption: [Hi-C validation across loci and cell types. Pearson correlation between ARCHCODE predicted contact matrices and experimental Hi-C data (KR-balanced, 1 kb resolution). Cell types: K562 (erythroid, red), MCF7 (breast cancer, purple), HepG2 (hepatocyte, green). All correlations are significant (p \< 10#super[-82]). The highest correlations occur at loci with strong CTCF boundaries and well-characterized enhancer architecture (MLH1, HBB 95 kb: r = 0.59). Number of valid contact pairs shown inside each bar.],
) <fig:hic-validation>

#figure(
  image("../figures/fig5_multilocus_summary.png", width: 100%),
  caption: [Multi-locus summary of ARCHCODE validation metrics across seven genomic loci. ΔLSSIM: difference between mean benign and mean pathogenic LSSIM (higher indicates better structural separation). Hi-C Pearson r: correlation with experimental contact maps. AG Spearman ρ: correlation with AlphaGenome deep learning predictions (O/E normalization). SCN5A (grayed) serves as negative control (K562 cell-type mismatch for this cardiac gene). Green cells: Hi-C r ≥ 0.50; Yellow: r ≥ 0.30.],
) <fig:multilocus-summary>


---


== AlphaGenome Benchmark
<alphagenome-benchmark>
To contextualize ARCHCODE's analytical contact maps against
deep learning predictions, we performed a direct
comparison with AlphaGenome (Google DeepMind), a genomics foundation
model that predicts chromatin contact maps from DNA sequence.
AlphaGenome was accessed via its Python SDK (v0.6.0) using contact map
predictions from 28 cell lines in the 4D Nucleome repository at 2048 bp
resolution. For each of seven ARCHCODE loci, we requested AlphaGenome
contact maps using a sequence length of 524,288 bp centered on the
ARCHCODE window (131,072 bp for HBB 30kb), extracted the overlapping
region, and resampled to match ARCHCODE's bin count.

Because AlphaGenome returns distance-normalized (observed/expected)
log-scale values, while ARCHCODE and Hi-C produce raw contact
probabilities with distance decay, we applied distance normalization
(O/E per stratum) to ARCHCODE and Hi-C matrices before comparison.
AlphaGenome values were transformed from log to linear scale via exp().
All matrices were then min-max normalized, and Pearson r and Spearman ρ
were computed on upper-triangle elements (excluding diagonal and first
off-diagonal).

Cell line selection was matched where possible: HepG2 for LDLR
(liver-expressed gene), GM12878 (lymphoblastoid reference) for all other
loci. K562 --- the primary cell line for ARCHCODE Hi-C validation --- is
not available in AlphaGenome's contact map predictions.

#strong[Results.] ARCHCODE and AlphaGenome contact maps show consistent
moderate agreement across most loci: Spearman ρ ranges from 0.27 (CFTR)
to 0.52 (BRCA1), with Pearson r = 0.07--0.29 (Table 6b). HBB
(ρ = 0.15) is an outlier explained by the narrow 30 kb window yielding
only 15 AlphaGenome bins (2048 bp resolution) and cell line mismatch
(GM12878 vs K562). The Spearman rank correlation consistently exceeds
Pearson, suggesting a monotonic but non-linear relationship between the
two approaches --- expected given their distinct
methodologies (analytical physics vs deep learning from sequence).

That an analytical mean-field model with no training data correlates at
ρ ≈ 0.3--0.5 with a deep learning foundation model trained on thousands
of Hi-C experiments suggests both approaches capture genuine features of
chromatin architecture --- CTCF-mediated boundaries and enhancer-driven
contact enrichment --- despite operating through entirely different
computational paradigms.

=== Variant-Level AlphaGenome Mutagenesis
<variant-level-alphagenome-mutagenesis>
To test whether AlphaGenome detects the same variant-level perturbations
as ARCHCODE, we performed in-silico mutagenesis on 27 pearl variants
from the HBB 95kb atlas using AlphaGenome's `predict_variant()` API. For
each variant, AlphaGenome returns both reference and alternate contact
maps from the same genomic interval, enabling direct computation of
ΔSSIM between wild-type and mutant predictions. Of 27 pearl variants, 23
were processable (4 excluded for IUPAC ambiguity codes); none were
skipped for complexity.

#strong[Results.] AlphaGenome perturbation signals were uniformly small:
ΔSSIM ranged from 7.5 × 10⁻⁵ to 6.3 × 10⁻⁴ (mean = 3.1 × 10⁻⁴), compared
to ARCHCODE ΔSSIM of 0.010--0.031 (mean = 0.015) --- a \~49-fold
difference in perturbation magnitude. Correlation between ARCHCODE and
AlphaGenome ΔSSIM was non-significant (Pearson r = 0.06, p = 0.78;
Spearman ρ = −0.32, p = 0.13; n = 23).

#strong[Interpretation.] This null result is informative rather than
negative. AlphaGenome operates at 2048 bp resolution --- individual SNVs
affect \< 0.05% of the input sequence, producing contact map changes
near the noise floor. ARCHCODE, by contrast, directly perturbs loop
extrusion parameters at the variant position, amplifying structural
signal regardless of sequence length. The two approaches thus have
complementary resolution regimes: AlphaGenome excels at wild-type
structural prediction (ρ = 0.12--0.52, see above), while ARCHCODE's
analytical perturbation model provides variant-level sensitivity that
sequence-based deep learning cannot currently achieve at this
resolution. Together with the Akita null result below, this dual-DL
benchmark fully addresses Limitation \#10.

=== Akita Benchmark
<akita-benchmark>
To verify that the AlphaGenome wild-type results are not model-specific,
we performed an independent benchmark against Akita (Fudenberg et al.,
2020, #emph[Nature Methods]), a deep learning model for chromatin
contact map prediction from DNA sequence. Akita uses the Basenji
framework (Kelley et al., 2020) and operates at the same 2048 bp
resolution as AlphaGenome, but was developed independently (Calico,
TensorFlow) with earlier training data (Rao et al.~2014 Hi-C).
Akita is fully open-source --- model weights, architecture,
and training code are publicly available --- enabling local CPU
inference without cloud API dependency.

For each of six ARCHCODE loci (excluding SCN5A), we fetched a 1,048,576
bp reference sequence centered on the locus (Ensembl REST API, GRCh38),
one-hot encoded it, and predicted a 448×448 contact map (GM12878, target
index 2). The Akita output (upper triangle vector of 99,681 elements)
was reshaped to a 2D matrix, the locus window extracted, resampled to
match ARCHCODE's bin count, and distance-normalized identically to the
AlphaGenome comparison.

#strong[Results.] Akita and ARCHCODE contact maps show moderate
agreement across large loci: Spearman ρ ranges from 0.17 (TP53) to 0.43
(BRCA1), comparable to AlphaGenome's 0.12--0.52 (Table 6b). The pattern across loci is consistent: larger windows with more
Akita bins yield stronger correlations (BRCA1: 195 bins, ρ = 0.43; CFTR:
155 bins, ρ = 0.41), while narrow HBB windows produce weak or
artifactual results due to aggressive upsampling (95kb: 47→159 bins, ρ =
−0.27).

#strong[Variant-level mutagenesis.] To test whether Akita detects
variant-level perturbations, we performed ref/alt in-silico mutagenesis
on the same 23 pearl variants from the HBB 95kb atlas. Unlike
AlphaGenome (which provides a `predict_variant()` API), Akita requires
manual sequence substitution: for each variant, we created an alternate
1Mb sequence, predicted both ref and alt contact maps, and computed
ΔSSIM. Akita ΔSSIM ranged from 4.6 × 10⁻⁷ to 5.5 × 10⁻² (mean = 5.7 ×
10⁻³), with the upper range driven by three large indels (≥25 bp) that
alter a detectable fraction of the 1Mb input. For point mutations
(SNVs), Akita ΔSSIM was uniformly \< 10⁻⁴ --- comparable to
AlphaGenome's noise floor. Spearman rank correlation between ARCHCODE
and Akita ΔSSIM was non-significant (ρ = −0.17, p = 0.45; n = 23), while
Pearson r = 0.56 (p = 0.005) was driven entirely by the shared indel
signal. This constitutes a dual-DL null result for point mutations ---
two independent models, same conclusion.

#strong[Interpretation.] The concordance between AlphaGenome and Akita
wild-type results (both showing ρ ≈ 0.2--0.5) and their shared inability
to detect SNV-level perturbations strengthens two conclusions: (1)
ARCHCODE's analytical contact maps capture genuine features of chromatin
architecture that two independent DL approaches independently recover;
(2) ARCHCODE's direct perturbation of loop extrusion parameters provides
variant-level sensitivity that sequence-based DL models at 2048 bp
resolution cannot match. Akita's sensitivity to large indels but not
SNVs is consistent with the 2048 bp resolution limit: a 25 bp
duplication alters \~1.2% of a bin, while a single SNV alters \< 0.05%.
Akita was trained on Rao et al.~2014 Hi-C data (not 4DN), so
the wild-type concordance cannot be attributed to shared training signal
--- unlike AlphaGenome (see Limitation \#10).

=== Multimodal AlphaGenome Validation (RNA-seq + ATAC)
<multimodal-alphagenome-validation-rna-seq-atac>
Contact maps operate at 2048 bp resolution, where individual SNVs alter
\< 0.05% of an input bin --- producing perturbation signals near the
noise floor. However, AlphaGenome also predicts RNA-seq and ATAC-seq
tracks at #strong[1 bp resolution] --- a 2048-fold increase. At this
resolution, each SNV directly modifies 1 of \~131,000 bins (0.0008%), a
substantially larger fractional effect than the contact map case. We
therefore tested whether these orthogonal epigenomic modalities detect
variant-level signal invisible to contact maps.

Using AlphaGenome's `predict_variant()` API, we obtained reference and
alternate RNA-seq and ATAC-seq predictions for all 23 processable pearl
variants (20 SNVs, 3 indels) from the HBB 95kb atlas. Predictions were
filtered to K562 (EFO:0002067) --- the most biologically relevant cell
line for the HBB locus --- yielding 5 RNA-seq tracks (polyA+/total,
±strand and unstranded) and 1 ATAC-seq track per variant. Metrics were
computed on the unstranded polyA+ RNA-seq track and the K562 ATAC-seq
track within the 95 kb locus window.

#strong[Results.] In sharp contrast to the contact map null (ΔSSIM \<
10⁻⁴), both modalities show substantial variant-level signal at 1 bp
resolution:

#figure(
  align(center)[#table(
    columns: (26.6%, 14.89%, 15.96%, 23.4%, 4.26%, 14.89%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [RNA-seq (K562)], [ATAC-seq (K562)], [Contact
      maps (2048 bp)], [], [],),
    table.hline(),
    [Mean max], [ref − alt], [], [28.13], [5.70], [\< 10⁻⁴ (ΔSSIM)],
    [Mean delta at variant bin], [0.38], [0.27], [---], [], [],
    [Mean cosine similarity], [0.9954], [0.9205], [\~1.0000], [], [],
    [Mean signal concentration], [16.97×], [11.15×], [---], [], [],
    [Indel max delta range], [99.8--220.7], [23.4--23.9], [---], [], [],
    [SNV max delta range], [6.0--15.1], [0.5--6.6], [---], [], [],
  )]
  , kind: table
  )

Signal concentration ratio measures the mean delta within ±500 bp of the
variant divided by the mean delta across the full locus window. Values
of 11--17× indicate that perturbation signal is strongly localized
around the variant position rather than uniformly distributed (which
would give a ratio of \~1.0). This confirms genuine variant-level effect
rather than global numerical noise.

Indels show dramatically larger deltas than SNVs (RNA-seq: 99--221 vs
6--15; ATAC: 23 vs 0.5--7), consistent with the resolution-dependent
pattern observed in Akita contact maps (where large indels but not SNVs
were detectable at 2048 bp).

#strong[Correlation with ARCHCODE.] Spearman rank correlation between
ARCHCODE ΔSSIM and AlphaGenome multimodal deltas was non-significant:
RNA-seq max\_delta ρ = −0.22 (p = 0.31); ATAC max\_delta ρ = −0.32 (p =
0.14); n = 23. This indicates that while both methods detect
variant-level perturbations, they rank variants differently ---
consistent with different mechanisms (analytical loop
extrusion vs deep learning from sequence).

#strong[Interpretation.] The multimodal analysis reveals a
resolution-dependent hierarchy in AlphaGenome's ability to detect
variant effects: contact maps (2048 bp) → null; RNA-seq and ATAC-seq (1
bp) → detectable signal. This demonstrates that the contact map null
result (Limitation \#10) is a resolution limitation, not a fundamental
inability of deep learning to detect sequence variants. The lack of rank
correlation with ARCHCODE is expected: RNA-seq reflects transcriptional
effects, ATAC-seq reflects chromatin accessibility, while ARCHCODE
models loop extrusion dynamics --- three distinct biological mechanisms
that need not correlate for individual variants.

#strong[Pearl vs Benign Control.] To test whether the multimodal signal
is specific to pathogenic pearl variants or a generic property of all
variants in the locus, we ran the identical analysis on 23 randomly
sampled benign non-pearl variants (seed = 42, matched sample size).
Mann-Whitney U tests (two-sided, non-parametric) reveal that pearl
variants produce significantly different signal across all 10 metric ×
modality combinations (p \< 0.05 for all):

#figure(
  align(center)[#table(
    columns: (24.69%, 9.88%, 17.28%, 18.52%, 3.7%, 9.88%, 16.05%),
    align: (auto,auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [Modality], [Pearl (n = 23)], [Benign (n =
      23)], [U], [p-value], [Effect size r],),
    table.hline(),
    [Signal concentration], [RNA-seq], [16.97×], [6.09×], [450], [\<
    0.0001], [−0.70],
    [Delta at variant
    bin], [RNA-seq], [0.381], [0.109], [410], [0.0014], [−0.55],
    [Mean abs
    delta], [RNA-seq], [0.075], [0.032], [407], [0.0018], [−0.54],
    [Signal
    concentration], [ATAC], [11.15×], [6.39×], [402], [0.0026], [−0.52],
    [Mean abs
    delta], [ATAC], [0.046], [0.058], [401], [0.0028], [−0.52],
    [Cosine
    similarity], [ATAC], [0.921], [0.891], [132], [0.0037], [+0.50],
    [Max abs delta], [ATAC], [5.70], [4.88], [394], [0.0045], [−0.49],
    [Cosine
    similarity], [RNA-seq], [0.995], [0.999], [148], [0.011], [+0.44],
    [Max abs
    delta], [RNA-seq], [28.13], [27.43], [370], [0.012], [−0.40],
    [Delta at variant
    bin], [ATAC], [0.268], [0.098], [364], [0.029], [−0.38],
  )]
  , kind: table
  )

The most discriminative metric is #strong[signal concentration ratio]
(RNA-seq: r = −0.70, p \< 0.0001), indicating that pearl variants
concentrate perturbation signal within ±500 bp of the variant position
2.8× more strongly than benign variants (16.97× vs 6.09×). Raw
max#emph[delta values are similar between groups (28.13 vs 27.43 for
RNA-seq) because both groups contain indels that produce large absolute
deltas; the key difference is \_where] the signal localizes. Pearl
variants alter the local sequence context at positions where the deep
learning model predicts the largest regulatory effects, while benign
variants produce more diffuse perturbation.

#strong[Cross-Locus Replication: BRCA1 Pathogenic vs Benign.] To test
whether the multimodal signal generalizes beyond HBB pearl variants, we
applied the same AlphaGenome RNA-seq + ATAC analysis to BRCA1
(chr17:42.9--43.3 Mb) using MCF7 (EFO:0001203) as the tissue-matched
cell line (breast cancer, where BRCA1 is actively transcribed). Since
BRCA1 has no ARCHCODE pearl variants (all SSIM ≈ 1.0000), we compared 23
randomly sampled ClinVar Pathogenic variants against 23 ClinVar Benign
variants (seed = 42). Of 10 metric × modality tests, 1 reached
significance:

#figure(
  align(center)[#table(
    columns: (22.99%, 9.2%, 21.84%, 17.24%, 5.75%, 8.05%, 14.94%),
    align: (auto,auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [Modality], [Pathogenic (n = 23)], [Benign (n
      \= 23)], [U], [p-value], [Effect size r],),
    table.hline(),
    [Delta at variant
    bin], [RNA-seq], [0.074], [0.022], [382.5], [0.0098], [−0.45],
    [Signal
    concentration], [RNA-seq], [10.71×], [4.45×], [352.0], [0.056], [−0.33],
  )]
  , kind: table
  )

RNA-seq max\_delta = 6.0 for all 46 variants (ceiling effect in
AlphaGenome output), rendering this metric uninformative. The
significant result --- #strong[delta at variant bin] (p = 0.0098, r =
−0.45) --- indicates that pathogenic variants produce 3.4× stronger
RNA-seq perturbation directly at the variant position. Signal
concentration shows a consistent direction (pathogenic 10.71× vs benign
4.45×) but is borderline significant (p = 0.056). ATAC metrics show no
significant difference (all p \> 0.23).

The weaker discrimination in BRCA1 vs HBB (1/10 vs 10/10 significant
tests) is biologically expected: HBB pearls are ARCHCODE-selected
variants near regulatory elements (CTCF sites, enhancers) where
epigenomic perturbation concentrates; BRCA1 ClinVar pathogenic variants
are predominantly coding (frameshift, nonsense, missense) where disease
mechanism operates through protein truncation rather than chromatin
architecture. The partial replication of delta\_at\_variant (the most
direct measure of local perturbation) across loci with different variant
classes supports the biological specificity of the signal.

#strong[Cell-Type Mismatch Negative Control: SCN5A.] To test whether
multimodal discrimination depends on tissue-matched cell line
annotation, we applied the same analysis to SCN5A (chr3:38.4--38.8 Mb),
a cardiac ion channel gene not expressed in K562. Using K562 as a
deliberate cell-type mismatch, we compared 23 ClinVar Pathogenic vs 23
Benign variants (seed = 42). RNA-seq max\_delta was 230× lower than
BRCA1 and 1,080× lower than HBB (0.026 vs 6.0 vs 28.1), confirming
near-zero RNA prediction for a non-expressed gene. Signal concentration
ratio showed no discrimination (pathogenic 0.39× vs benign 0.40×, p =
0.96), consistent with noise-floor signal in both groups.

#figure(
  align(center)[#table(
    columns: (6.85%, 12.33%, 10.96%, 45.21%, 10.96%, 13.7%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([Locus], [Cell line], [Match], [RNA concentration (Path
      \/ Benign)], [p-value], [Sig. tests],),
    table.hline(),
    [HBB], [K562], [Matched], [16.97× / 6.09× = 2.78×], [\<
    0.0001], [10/10],
    [BRCA1], [MCF7], [Matched], [10.71× / 4.45× =
    2.41×], [0.056], [1/10],
    [SCN5A], [K562], [Mismatch], [0.39× / 0.40× =
    0.96×], [0.96], [0/10†],
  )]
  , kind: table
  )

†SCN5A had 2 nominally significant tests (RNA max\_abs\_delta p = 0.017,
ATAC concentration p = 0.036) but both reflect technical artifacts: RNA
max\_delta difference (0.026 vs 0.024) is within quantization noise, and
ATAC concentration is in the opposite direction (benign \> pathogenic, r
\= +0.37), inconsistent with the tissue-matched pattern. We count 0/10
biologically meaningful significant tests.

The three-locus gradient --- strong discrimination with tissue-matched
regulatory variants (HBB), partial discrimination with tissue-matched
coding variants (BRCA1), null discrimination with cell-type mismatch
(SCN5A) --- demonstrates that multimodal signal specificity depends on
both variant class and tissue context.

=== Epigenome Cross-Validation
<epigenome-cross-validation>
To independently validate the ENCODE ChIP-seq features used as ARCHCODE
input parameters (CTCF binding sites and H3K27ac enhancer peaks), we
queried AlphaGenome's epigenomic prediction tracks (CHIP\_TF for CTCF,
CHIP\_HISTONE for H3K27ac) across all seven loci. These tracks predict
transcription factor binding and histone modifications directly from DNA
sequence at 128 bp resolution --- an independent method from
experimental ChIP-seq.

#strong[CTCF validation.] AlphaGenome predicted CTCF binding at 100% of
ENCODE-annotated CTCF positions across all seven loci (68/68 sites
recovered within 2 kb tolerance), with mean F1 = 0.71 (range:
0.54--0.83). The lower precision (37--71%) reflects AlphaGenome
predicting additional CTCF sites beyond our curated set, which may
represent real binding sites not included in our configs rather than
false positives.

#strong[H3K27ac validation.] For the five loci with ENCODE H3K27ac
annotations (TP53, BRCA1, MLH1, LDLR, SCN5A), AlphaGenome recovered 81%
of annotated enhancer peaks (31/37), with mean F1 = 0.42 (range:
0.18--0.67). SCN5A showed the lowest F1 (0.18, only 3 K562 peaks for a
cardiac gene) and MLH1 the lowest recall (62%), reflecting
cell-type-specific enhancer activity not captured by the generic
AlphaGenome prediction.

#strong[Significance.] Perfect CTCF recall (100%) across seven
independent loci confirms that ARCHCODE's structural model is built on
experimentally validated chromatin boundary positions. The H3K27ac
validation (85% recall) provides additional confidence that enhancer
annotations reflect genuine regulatory features, though cell-type
specificity remains a limitation.


---


== Bayesian Parameter Optimization
<bayesian-parameter-optimization-1>
To assess whether ARCHCODE's manually calibrated kinetics parameters
(α=0.92, γ=0.80, k\_base=0.002) could be improved, we performed Bayesian
optimization using Optuna 4.7.0 (Akiba et al., 2019) with Gaussian
Process sampling (GPSampler, 20 startup trials). The search space
covered α ∈ \[0.5, 1.0\], γ ∈ \[0.3, 1.5\], and k\_base ∈ \[0.0005,
0.01\] (log-scale). The objective function maximized mean Pearson r
between ARCHCODE wild-type matrices and K562 Hi-C for the 30 kb and 95
kb HBB windows jointly. Two hundred trials completed in 12.9 seconds.

The optimization yielded negligible improvement: Δr = +0.0001 for both
scales (r\_30kb: 0.5299 → 0.5300; r\_95kb: 0.5876 → 0.5877). All three
best-trial parameters converged to their lower bounds (α=0.50, γ=0.30,
k\_base=0.0005), indicating the optimizer minimized the Kramer kinetics
term entirely. Parameter importance analysis (fANOVA) confirmed that
k\_base accounts for 90% of objective variance, with α (5%) and γ (5%)
contributing negligibly. This reveals a structural insight: Hi-C
correlation is driven by the architectural features of the contact model
(distance decay, MED1 occupancy landscape, CTCF barrier permeability),
not by kinetics parameters. The kinetics parameters serve a different
function --- modulating SSIM perturbation magnitude for variant
classification --- that is orthogonal to wild-type contact map fidelity.

Original parameters were retained. The Bayesian search should be
interpreted as confirming the grid-search estimates as near-optimal, not
as a failed optimization.


---


#strong[Quadrant analysis] (SSIM threshold 0.95 / VEP threshold 0.30):

#figure(
  align(center)[#table(
    columns: (10.39%, 62.34%, 12.99%, 7.79%, 6.49%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Quadrant], [Description], [Pathogenic], [Benign], [Total],),
    table.hline(),
    [Q1], [Both detect (SSIM \< 0.95, VEP ≥ 0.30)], [199], [0], [199],
    [Q2], [ARCHCODE only / pearls (SSIM \< 0.95, VEP \<
    0.30)], [20], [0], [20],
    [Q3], [VEP only (SSIM ≥ 0.95, VEP ≥ 0.30)], [95], [41], [136],
    [Q4], [Neither (SSIM ≥ 0.95, VEP \< 0.30)], [39], [709], [748],
  )]
  , kind: table
  )

Q2 (ARCHCODE-only detections / pearl variants) contains 20
Pathogenic variants and 0 Benign variants under the unified pipeline.
This demonstrates that pearl identification has zero false-positive rate
among confirmed benign variants in the current dataset.


---


== Summary
<summary>
ARCHCODE simulation of 353 real ClinVar HBB variants demonstrates: (1)
mean SSIM values rank variant categories in the biologically expected
order from nonsense (most disruptive) to synonymous (least disruptive);
(2) overall discordance with VEP is 36.8%, predominantly VEP-only (128
variants), reflecting VEP's sensitivity to protein-level mechanisms that
lie outside ARCHCODE's scope; (3) 20 pearl variants with VEP score \<
0.30 and SSIM \< 0.95 suggest candidate cases for structural-level
re-evaluation, with the strongest biological signal in promoter-region
variants where the LCR--HBB enhancer--promoter contact model detects
disruption not captured by VEP consequence annotation; (4) ROC analysis
on a combined cohort of 1,103 variants (353 Pathogenic + 750 Benign),
processed through a unified pipeline, yielded AUC = 0.977 with near-zero
false positives among benign variants at stringent thresholds,
reflecting category-distribution differences rather than independent
sequence-based prediction; (5) formal within-category testing (logistic
regression p = 1.0, Mann--Whitney p = 0.22--0.69) confirms that SSIM
does not add significant predictive value beyond category at this locus,
consistent with all ClinVar variants clustering in 2.1 kb (2.2% of the
95 kb window); (6) ARCHCODE shows zero sensitivity to missense variants,
its most important limitation for clinical variant classification; (7)
Local SSIM (LSSIM) resolves matrix-size dilution by computing SSIM on a
50×50 submatrix centered on each variant, expanding dynamic range from
0.98--1.00 to 0.75--1.00; (8) cross-gene within-category testing using
LSSIM: CFTR (ΔAUC = −0.012, p = 0.79) and TP53 (ΔAUC = +0.032, p = 0.29)
null; BRCA1 (ΔAUC = +0.002, p ≈ 10⁻²⁰), MLH1 (ΔAUC = +0.011, p = 0.005),
and LDLR (ΔAUC = −0.003, p = 0.004) statistically significant but ΔAUC
\< 0.02 (power effect); (9) Bayesian parameter optimization (200 trials)
confirms grid-search kinetics estimates as near-optimal (Δr = 0.0001),
with Hi-C correlation driven by structural architecture rather than
kinetics parameters; (10) Hi-C validation: MLH1 K562 r = 0.59, BRCA1
K562 r = 0.53 / MCF7 r = 0.50, LDLR HepG2 r = 0.32, TP53 K562 r = 0.29
--- locus-dependent performance; (11) LSSIM enables structural
pathogenic verdicts on all loci (HBB 95kb: 254, MLH1: 72, BRCA1: 52,
CFTR: 35, TP53: 12 VUS, LDLR: 10).

All reported SSIM values and VEP scores are derived from computational
models. Hi-C validation against K562, MCF7, and HepG2 experimental data
shows significant correlation (r = 0.28--0.59 across seven loci; see
Discussion). Multimodal AlphaGenome analysis (RNA-seq and ATAC-seq at 1
bp resolution) detects variant-level perturbation signal invisible to
contact maps, but does not rank variants concordantly with ARCHCODE
(Spearman ρ = −0.22 to −0.32, ns). Patient phenotype validation and
experimental functional validation (RT-PCR, CRISPR) remain outstanding.
Experimental validation is required before any variant reclassification
should be considered.


---




---


= Discussion
<discussion>
== What ARCHCODE Reveals --- and What It Cannot
<what-archcode-reveals-and-what-it-cannot>
We began this study with a clear question: can an analytical mean-field
loop extrusion simulator identify pathogenic signal in HBB variants that
sequence-based predictors miss? The answer is yes, but with important
quantitative caveats.

ARCHCODE correctly stratifies 353 ClinVar HBB variants by functional
severity: mean SSIM follows the biologically expected ranking from
nonsense (0.8753) through missense (0.9526) to synonymous (0.9989). The
20 pearl variants --- particularly the 15 promoter-region candidates ---
represent a concrete, testable prediction: that variants in the HBB
proximal promoter region (chr11:5,227,099--5,227,172) disrupt modeled
LCR--HBB enhancer--promoter contacts in ways invisible to VEP's
consequence-based scoring.

The Hi-C validation trajectory illustrates how cell-type matching and
window geometry transform model performance. Our initial GM12878
validation (r = 0.16, p = 0.301, not significant; n = 12 loci) used
non-erythroid Hi-C data in a 30 kb window containing zero experimentally
confirmed CTCF peaks. Switching to K562 erythroid Hi-C data
(4DNFI18UHVRO, 4DN Data Portal; KR-balanced, 1 kb resolution) produced r
\= 0.530 (Spearman ρ = 0.680, p = 2.19 × 10⁻⁸², n = 1,124) at 30 kb.
Expanding the simulation window to the full 95 kb HBB sub-TAD
(chr11:5,200,000--5,295,000) --- capturing both CTCF boundary anchors
3'HS1 (signal = 225) and HS5 (signal = 260) from ENCODE K562 ChIP-seq
(ENCFF660GHM) --- further improved correlation to r = 0.588 (p \<
10⁻³⁰⁰, n = 11,649). This progression demonstrates that ARCHCODE's
analytical loop extrusion engine captures genuine chromatin contact
topology when supplied with cell-type-appropriate anchors.

Multi-locus Hi-C validation reveals locus-dependent performance. MLH1
achieves the joint-highest K562 correlation (r = 0.59, tied with HBB
95kb), likely driven by its strong intergenic CTCF boundary and
well-characterized promoter architecture. BRCA1 achieves K562 r = 0.53
and MCF7 r = 0.50 (comparable to HBB K562), while TP53 shows lower
correlation (K562 r = 0.29, MCF7 r = 0.28). The TP53 result likely
reflects greater structural complexity: 7 persistent homology H1
features (vs 3--4 for HBB), an internal P2 promoter generating Δ133p53
isoforms, and higher CTCF density creating a denser contact
pattern that the mean-field model captures less completely. The BRCA1
result is encouraging: despite a 400×400 matrix (the largest tested),
Hi-C correlation matches HBB, suggesting that dense enhancer/CTCF
annotation compensates for dilution effects in contact map fidelity.
LDLR (HepG2 r = 0.32) is the first tissue-specific validation, using
hepatocyte Hi-C instead of K562. The moderate correlation is comparable
to TP53 and likely reflects the gene-dense chr19 environment, where
multiple overlapping regulatory domains (including the upstream SMARCA4
chromatin remodeler) create complex contact patterns. SSIM values should
still be interpreted as relative disruption scores within the model, not
as absolute predictions of chromatin contact frequency.

The AlphaGenome benchmark provides an independent line of structural
validation. ARCHCODE's analytically computed contact maps correlate with
AlphaGenome's deep learning predictions at Spearman ρ = 0.12--0.52
across six of seven loci (SCN5A excluded; see below) --- a moderate but
consistent agreement between a physics-based model with zero training
data and a foundation model trained on thousands of Hi-C experiments.
The correlation is strongest at BRCA1 (ρ = 0.52) and MLH1 (ρ = 0.49),
loci with the most complete CTCF/enhancer annotation, and weakest at HBB
(ρ = 0.15), where the narrow 30 kb window yields only 15 AlphaGenome
bins. This suggests that both approaches converge on genuine chromatin
features --- CTCF boundaries and enhancer-driven contact enrichment ---
despite different computational approaches. However, this
concordance should not be over-interpreted: AlphaGenome's training data
includes 4DN Hi-C from the same cell lines used in our Hi-C validation,
so the correlation may partly reflect shared data provenance rather than
independent convergence on biological truth.

The AUC of 0.977 reflects a category-level structural model, not
evidence of within-category positional prediction. A position-only
control experiment (fixed effectStrength = 0.3 for all variants,
removing all category information) yielded AUC = 0.551 ---
indistinguishable from chance --- confirming that the AUC is entirely
attributable to the categorical effectStrength mapping. Multi-locus
testing using LSSIM across seven loci (25,272 variants total) confirms
that LSSIM adds no clinically meaningful predictive value beyond
category assignment: CFTR and TP53 show clear null results (p \> 0.29),
while BRCA1 (p ≈ 10⁻²⁰) and MLH1 (p = 0.005) show statistical
significance with negligible effect sizes (ΔAUC \< 0.02). The
significance at larger loci reflects statistical power rather than a
biologically meaningful within-category signal. This is a structural
property of the occupancy-scaling approach: perturbation magnitude is
assigned by functional category, not by genomic position within
category. The model #emph[is] positionally sensitive --- distance-to-TSS
correlates with SSIM at multiple loci --- but this sensitivity affects
pathogenic and benign variants equally when they share similar genomic
positions within each category.

We have not "confirmed" the "Loop That Stayed" mechanism. We have
generated a computational prediction that specific promoter-region HBB
variants show structural disruption by our model. Whether this reflects
genuine regulatory biology requires experimental testing.

== The Structural Blind Spot of Sequence-Based Prediction
<the-structural-blind-spot-of-sequence-based-prediction>
The 130 discordant variants (36.8% of dataset) illuminate the
complementary nature of structural and sequence-based approaches. The
128 VEP-only variants --- those called pathogenic by VEP but not by
ARCHCODE --- consist predominantly of missense variants acting through
protein structural perturbation, a mechanism ARCHCODE cannot detect.
This is expected and appropriate: ARCHCODE does not model protein
folding.

The reverse discordance is more interesting: 2 variants and the 20 pearl
candidates were detected by ARCHCODE but assigned low pathogenicity by
VEP. For the promoter-region pearls, the mechanism is clear in model
terms: VEP annotates upstream\_gene\_variant as low-impact because the
standard consequence weighting does not account for LCR--HBB contact
disruption. ARCHCODE's physics-based model, by contrast, is sensitive to
changes at positions it has annotated as enhancer elements, regardless
of whether these positions match a recognized splice or coding motif.

This complementarity mirrors the relationship between different imaging
modalities in clinical medicine. VEP is sensitive to sequence-level
defects in protein-coding and canonical splice sequences. ARCHCODE is
sensitive to regulatory topology --- changes at simulated CTCF anchors
and enhancer elements within the 30 kb simulation window. A variant
outside both detection ranges will be missed by both; a variant detected
by only one provides hypothesis-generating signal for follow-up.

#strong[Model independence:] ARCHCODE is mechanistically orthogonal to
VEP. ARCHCODE receives no input from VEP scores, SIFT predictions,
ClinVar classifications, or any sequence-based tool. The two models
operate on fundamentally different biological layers: VEP evaluates
protein- coding impact and splice motif disruption from primary
sequence; ARCHCODE simulates cohesin- mediated loop extrusion and
chromatin contact topology from occupancy profiles. Their outputs are
statistically compared post hoc but are generated independently. The
absence of missense sensitivity in ARCHCODE is therefore a topological
feature of the model, not a failure --- missense variants that cause
disease through protein misfolding, loss of catalytic activity, or
dominant-negative mechanisms operate entirely at the protein level, a
dimension invisible to chromatin topology simulation. For missense
variants, sequence-based VEP tools remain the appropriate primary tool.
ARCHCODE provides orthogonal evidence #emph[specifically] for
regulatory, promoter, and structural variants where 3D genome
organization mediates the mechanism.

== "The Loop That Stayed" as Theoretical Framework
<the-loop-that-stayed-as-theoretical-framework>
The "Loop That Stayed" framework posits that stable cohesin-mediated
loops can confine splice regulatory defects by limiting spliceosome
access to trans-acting factors outside the loop domain. Our
computational results are consistent with this framework in a narrow
sense: splice\_region and promoter variants within the simulated
LCR--HBB loop domain show structural disruption signals (SSIM \< 0.95)
that VEP does not detect.

However, we emphasize that this is a theoretical mechanism, not an
experimentally confirmed pathway. The simulation shows disruption of a
modeled contact pattern; it does not demonstrate that any spliceosome is
topologically confined. The following chain of inference is required to
connect our computational results to a clinical finding:

+ ARCHCODE simulation predicts structural disruption at promoter-region
  positions (SSIM \~0.928)
+ Experimental Capture Hi-C would need to confirm reduced
  enhancer--promoter contact frequency
+ RT-PCR in erythroid cells (K562, HUDEP-2) would need to confirm
  aberrant splicing or reduced transcription
+ Patient genotype-phenotype correlation would need to link the variant
  to disease severity

We have completed step 1. Steps 2--4 are required before any variant
reclassification.

== Limitations
<limitations>
#strong[\1. Computational model only; Hi-C validation locus-dependent (r
\= 0.28--0.59).] ARCHCODE simulations remain #emph[in silico]
predictions. Multi-locus Hi-C correlation ranges from r = 0.28 (TP53
MCF7) to r = 0.59 (HBB K562 95kb, MLH1 K562), explaining 8--35% of
variance in experimental contact frequencies. Performance is best for
loci with well-characterized enhancer/CTCF architecture and drops for
structurally complex loci like TP53.

#strong[\2. Kinetics parameters confirmed near-optimal; no room for
improvement.] α=0.92 and γ=0.80 are grid-search estimates from
literature ranges. Bayesian optimization (Optuna GPSampler, 200 trials)
yielded Δr = +0.0001 --- negligible improvement. All three parameters
converged to their lower bounds (α=0.50, γ=0.30, k\_base=0.0005),
indicating the optimizer minimizes the Kramer kinetics term entirely.
Parameter importance analysis (fANOVA) confirms k\_base dominates (90%),
while α and γ contribute \<5% each. This reveals that Hi-C correlation
is driven by structural architecture (distance decay, MED1 landscape,
CTCF barriers), not by kinetics parameters --- which serve a different
role in SSIM perturbation for variant classification.

#strong[\3. Analytical mean-field model.] The model lacks polymer
physics baseline, A/B compartmentalization, non-CTCF enhancer loops
(YY1, LDB1), and cell-to-cell heterogeneity. These omissions likely
explain the remaining \~65--70% of unexplained Hi-C variance.

#strong[\4. VEP instead of SpliceAI.] The SpliceAI API was unreachable
during the study period. SpliceAI provides higher-resolution splice
disruption prediction than VEP/SIFT and would likely improve the
sequence-based baseline, potentially reclassifying some current pearls.
Future iterations will integrate the locally installable SpliceAI model
(Jaganathan et al., 2019; available via `pip install spliceai`) to
replace VEP as the sequence-based comparator.

#strong[\5. No patient-level validation.] No patients with these
variants and phenotype data are available in ClinVar records to validate
computational predictions against clinical reality.

#strong[\6. Pearl variants not experimentally validated.] The 20 pearl
variants are computational candidates. None have been tested by RT-PCR,
Capture Hi-C, or functional assay in this study.

#strong[\7. Within-category positional signal: primarily null,
power-driven on large cohorts.] Testing across seven loci with LSSIM:
HBB (p = 1.0), CFTR (p = 0.79), and TP53 (p = 0.29) show clear null
results. BRCA1 (p ≈ 10⁻²⁰, ΔAUC = +0.002), MLH1 (p = 0.005, ΔAUC =
\+0.011), and LDLR (p = 0.004, ΔAUC = −0.003) are statistically
significant but with negligible effect sizes. This reflects statistical
power at large n (\>4,000 variants) with expanded LSSIM dynamic range,
not meaningful within-category prediction. ARCHCODE remains primarily a
category-level structural classifier.

#strong[\8. Matrix-size dilution addressed by Local SSIM (LSSIM).]
Global SSIM dynamic range decreases monotonically with matrix size: HBB
50×50 yields SSIM 0.8659--0.9990; BRCA1 400×400 yields 0.9938--1.0000.
We introduced LSSIM (50×50 submatrix centered on variant) to normalize
perturbation fraction. LSSIM ranges: HBB 95kb 0.7537--0.9992; CFTR
0.8329--0.9999; BRCA1 0.8767--0.9999; MLH1 0.8417--0.9999; TP53
0.9443--1.0000. Verdict assignment now works across all matrix sizes.
However, pearl detection still requires VEP data (available only for
HBB); 20 pearls in the 30kb window, 27 pearls in the 95kb window (which
encompasses the 30kb region plus 7 additional candidates in the extended
LCR).

#strong[\9. Hi-C correlation does not validate variant-level
predictions.] Multi-locus Hi-C correlation (r = 0.28--0.59) validates
wild-type contact map fidelity, not variant-specific structural
disruption. No variant-level Hi-C perturbation data exists to validate
SSIM as a variant classifier directly.

#strong[\10. Resolution-dependent DL variant sensitivity: null at 2048
bp, detectable at 1 bp.] Variant-level mutagenesis was performed with
both AlphaGenome (`predict_variant()` API) and Akita (Fudenberg et
al.~2020; local ref/alt mutagenesis) on 23 pearl variants from the HBB
95kb atlas. For #strong[contact maps] (2048 bp resolution): AlphaGenome
ΔSSIM (7.5 × 10⁻⁵ to 6.3 × 10⁻⁴, \~49× smaller than ARCHCODE) and Akita
ΔSSIM (\< 10⁻⁴ for SNVs; up to 0.055 for large indels, Spearman ρ =
−0.17, p = 0.45) both showed negligible SNV-level signal. For
#strong[RNA-seq and ATAC-seq] (1 bp resolution): AlphaGenome shows
substantial signal --- RNA-seq mean max\_delta = 28.13, ATAC mean
max\_delta = 5.70, with signal concentration 11--17× higher around the
variant than background (confirming localized, non-noise effects).
However, rank correlation with ARCHCODE remains non-significant (ρ =
−0.22 to −0.32, p \> 0.13), indicating the methods detect perturbations
through different biological mechanisms. This establishes a resolution
hierarchy: DL models detect variant effects in epigenomic tracks (1 bp)
but not contact maps (2048 bp), while ARCHCODE's analytical loop
extrusion approach provides variant sensitivity regardless of
resolution. Wild-type concordance remains moderate for both contact map
models (AlphaGenome ρ = 0.12--0.52; Akita ρ = 0.17--0.43). AlphaGenome's
training set includes 4DN Hi-C data, so its wild-type correlation may
partly reflect shared training signal; Akita (trained on Rao et
al.~2014) does not share this confound.

== Path to Clinical Translation
<path-to-clinical-translation>
Clinical reclassification of any variant based on ARCHCODE predictions
alone would be premature. The appropriate translational pathway is:

#strong[Step 1 (immediate):] Release pearl variant list and ARCHCODE
analysis as bioRxiv preprint. Invite experimental groups with HBB
expertise and erythroid cell models to test predictions.

#strong[Step 2 (3--6 months):] RT-PCR in K562 or HUDEP-2 cells for the
15 promoter-region pearl variants. This directly tests whether VEP-blind
promoter variants cause measurable changes in HBB transcript abundance
or splicing.

#strong[Step 3 (6--12 months):] Capture Hi-C at the HBB locus in
erythroid cells, comparing wild-type to variants with the largest SSIM
deviations. This would validate or refute the model's contact disruption
predictions and extend the current r = 0.59 correlation to
variant-specific perturbation resolution.

#strong[Step 4 (if experimental evidence positive):] Apply ACMG PS3
criteria (functional studies) with experimental RT-PCR data and submit
evidence to ClinVar for affected accessions.

We specifically do not recommend clinical reclassification based on the
computational results reported here.

== Broader Implications
<broader-implications>
Despite the quantitative limitations, the ARCHCODE approach demonstrates
a proof-of-concept for orthogonal structural scoring. The identification
of 20 pearl variants on HBB provides a concrete, size-limited
prioritization list for experimental groups --- far more tractable than
screening all 353 variants individually.

We deliberately prioritize computational breadth over experimental
depth: systematic analysis of 27,760 variants across seven disease loci
provides a genome-wide hypothesis map that no single wet-lab study could
replicate in comparable time. This is not a substitute for experimental
validation --- it is its prerequisite. By narrowing 353 HBB variants to
20 structurally prioritized candidates, ARCHCODE reduces the
experimental search space by 94%, transforming an intractable screening
problem into a focused validation study amenable to CRISPR editing in
erythroid cell lines (HUDEP-2, K562) or Capture Hi-C at specific
genomic coordinates.

For the broader field of variant interpretation, this work illustrates
that different computational tools capture different biological
dimensions. Multi-locus Hi-C validation (r = 0.28--0.59 across seven
loci) grounds the model in experimental reality, with performance
varying by locus complexity. MLH1 (K562 r = 0.59, 4,060 variants)
achieves the joint-highest correlation, and LDLR (HepG2 r = 0.32, 3,284
variants) extends validation to tissue-specific (hepatocyte) chromatin,
adding cholesterol metabolism and DNA mismatch repair genes to the
portfolio. The BRCA1 result (K562 r = 0.53, MCF7 r = 0.50 with 10,682
variants) demonstrates scalability to clinically important oncogenes.

Cross-gene analysis across seven loci (27,760 total variants) using
LSSIM showed a nuanced picture: CFTR and TP53 produced clear null
results (p \> 0.29), while BRCA1 (p ≈ 10⁻²⁰), MLH1 (p = 0.005), and LDLR
(p = 0.004) showed statistical significance --- but with negligible
effect sizes (ΔAUC \< 0.02). This pattern is consistent with a power
effect: at n \> 4,000 with expanded LSSIM dynamic range, even tiny
positional SSIM variations become statistically detectable without being
clinically meaningful. Combined with the Bayesian optimization null (Δr
\= 0.0001), these results clarify ARCHCODE's scope: primarily a
category-level structural classifier with locus-dependent Hi-C
correlation (r = 0.28--0.59). The LSSIM expansion enables meaningful
verdict assignment across all matrix sizes while preserving the honest
reporting of within-category limitations.

The progressive matrix-size dilution observed with global SSIM (HBB
50×50 → BRCA1 400×400) was addressed in v2.3 by Local SSIM (LSSIM):
computing SSIM on a 50×50 submatrix centered on each variant. This
normalizes perturbation fraction to \~12% regardless of total matrix
size, expanding the dynamic range from 0.98--1.00 (global) to 0.75--1.00
(LSSIM) and enabling threshold transfer from the calibrated HBB 30kb
locus. LSSIM revealed structural pathogenic verdicts across all loci
(HBB 95kb: 254; MLH1: 72; BRCA1: 52; CFTR: 35; TP53: 12 VUS; LDLR: 10),
demonstrating that matrix-size dilution was the primary barrier to
verdict assignment, not lack of structural signal. Topological data
analysis (ρ = −0.51 to −1.00 correlation with SSIM on smaller loci)
provides a complementary perspective on structural disruption.


---




---


= References
<references>
+ Gerlich et al.~(2006). Live-cell imaging reveals a stable
  cohesin-chromatin interaction. Curr Biol.
+ Gabriele et al.~(2022). Dynamics of CTCF- and cohesin-mediated
  chromatin looping. Science. doi:10.1126/science.abn6583
+ Avsec et al.~(2021). Enformer. Nature Methods.
  doi:10.1038/s41592-021-01252-x
+ Fudenberg et al.~(2020). Predicting 3D genome folding from DNA
  sequence with Akita. Nature Methods. doi:10.1038/s41592-020-0958-x
+ Richards et al.~(2015). ACMG Guidelines. Genetics in Medicine.
  doi:10.1038/gim.2015.30
+ Taher et al.~(2021). β-Thalassemia. NEJM. doi:10.1056/NEJMra2021838
+ Baralle & Baralle (2018). The splicing code. Biosystems.
  doi:10.1016/j.biosystems.2017.11.002
+ Wang et al.~(2004). SSIM. IEEE TIP. doi:10.1109/TIP.2003.819861
+ Harrison et al.~(2019). Overview of Specifications to the ACMG/AMP
  Variant Interpretation Guidelines. Current Protocols in Human
  Genetics. doi:10.1002/cphg.93
+ Manrai et al.~(2016). Genetic Misdiagnoses. NEJM.
+ Hansen et al.~(2017). CTCF and Cohesin. eLife.
+ Davidson et al.~(2019). DNA Loop Extrusion. Science.
+ Sanborn et al.~(2015). Chromatin extrusion. PNAS.
+ Schwarzer et al.~(2017). Cohesin removal. Nature.
+ Kagey et al.~(2010). Mediator and cohesin. Nature.
+ Landrum et al.~(2018). ClinVar. NAR.
+ Boyko (2026). ARCHCODE GitHub: https:/\/github.com/sergeeey/ARCHCODE
+ Whalen et al.~(2022). Navigating the pitfalls of applying machine
  learning in genomics. Nature Reviews Genetics.
  doi:10.1038/s41576-021-00434-9
+ McLaren et al.~(2016). The Ensembl Variant Effect Predictor. Genome
  Biology. doi:10.1186/s13059-016-0974-4
+ Jaganathan et al.~(2019). Predicting Splicing from Primary Sequence
  with Deep Learning. Cell. doi:10.1016/j.cell.2018.12.015
+ Ng & Henikoff (2003). SIFT: predicting amino acid changes that affect
  protein function. Nucleic Acids Research. doi:10.1093/nar/gkg509
+ Sabaté et al.~(2024). 3D genome dynamics during cohesin loop
  extrusion. bioRxiv. doi:10.1101/2024.08.09.605990
+ Akiba et al.~(2019). Optuna: A Next-generation Hyperparameter
  Optimization Framework. KDD. doi:10.1145/3292500.3330701

\[Full bibliography in BibTeX available in repo.\]


---


= Supplementary Table S1: Comprehensive Analysis of 353 HBB Variants
<supplementary-table-s1-comprehensive-analysis-of-353-hbb-variants>
== Table Legend
<table-legend>
Complete dataset of 353 β-globin (#emph[HBB]) pathogenic and likely
pathogenic variants analyzed using ARCHCODE (analytical mean-field 3D
chromatin simulation) and Ensembl VEP v113 (sequence-based predictor).
Variants are sorted by SSIM ascending (most structurally disruptive
first).

#strong[Full dataset file:] `HBB_Clinical_Atlas_REAL.csv` (353 rows,
available from corresponding author or GitHub repository)

#strong[Columns in full dataset:]

+ #strong[ClinVar\_ID]: ClinVar accession (VCV format)
+ #strong[Position]: Genomic coordinate on chr11 (GRCh38/hg38)
+ #strong[Ref / Alt]: Reference and alternate alleles
+ #strong[Category]: Variant functional category (VEP annotation; see
  Methods for definitions)
+ #strong[ARCHCODE\_SSIM]: Structural Similarity Index (WT vs Mutant
  contact matrices)
  - Range: \[0,1\], higher = more similar to WT (less structural
    disruption)
  - Thresholds: SSIM \< 0.85 PATHOGENIC; 0.85--0.92 LIKELY\_PATHOGENIC;
    0.92--0.96 VUS; 0.96--0.99 LIKELY\_BENIGN; ≥ 0.99 BENIGN
+ #strong[VEP\_Score]: Ensembl VEP v113 pathogenicity score (consequence
  \+ SIFT integration)
  - Range: \[0,1\], higher = more pathogenic
  - Thresholds: ≥ 0.50 Pathogenic/Likely Pathogenic; \< 0.50
    Benign/Likely Benign/VUS
+ #strong[ARCHCODE\_Verdict]: ARCHCODE classification based on SSIM
  threshold
+ #strong[VEP\_Verdict]: VEP classification based on score threshold
+ #strong[Discordant]: YES if verdicts differ between methods, NO
  otherwise
+ #strong[Pearl]: YES if VEP score \< 0.30 AND SSIM \< 0.95 (both
  criteria required)


---


== Summary Statistics by Category
<summary-statistics-by-category>
#figure(
  align(center)[#table(
    columns: (22.39%, 10.45%, 14.93%, 20.9%, 31.34%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM], [Mean VEP Score], [%
      ARCHCODE Pathogenic],),
    table.hline(),
    [nonsense], [40], [0.8753], [0.90], [100%],
    [frameshift], [99], [0.8919], [0.90], [100%],
    [splice\_acceptor], [3], [0.9019], [0.95], [100%],
    [splice\_donor], [22], [0.9087], [0.95], [86%],
    [promoter], [15], [0.9285], [0.20], [0%],
    [missense], [125], [0.9526], [\~0.70], [0%],
    [splice\_region], [9], [0.9641], [0.50], [0%],
    [other], [12], [0.9676], [varies], [0%],
    [5\_prime\_UTR], [3], [0.9801], [0.20], [0%],
    [3\_prime\_UTR], [13], [0.9942], [0.15], [0%],
    [intronic], [9], [0.9957], [0.10], [0%],
    [synonymous], [3], [0.9989], [0.05], [0%],
    [#strong[Total]], [#strong[353]], [#strong[0.9267]], [#strong[0.754]], [#strong[45.6%]],
  )]
  , kind: table
  )

#strong[Interpretation:] ARCHCODE SSIM and VEP are anti-correlated by
design for non-coding categories: promoter, UTR, and intronic variants
have low VEP scores (not annotated as high-impact by sequence analysis)
but show moderate SSIM disruption in the structural model (0.92--0.98
range). This is the source of the pearl candidates. Concordance is
highest for loss-of-function classes (nonsense, frameshift) where both
methods detect severe disruption.


---


== Discordance Summary
<discordance-summary>
#figure(
  align(center)[#table(
    columns: (28.57%, 8.33%, 11.9%, 51.19%),
    align: (auto,auto,auto,auto,),
    table.header([Discordance type], [n], [% of total], [Dominant
      variant classes],),
    table.hline(),
    [VEP-only pathogenic], [128], [36.3%], [missense (125),
    splice\_region (3)],
    [ARCHCODE-only pathogenic], [2], [0.6%], [frameshift (1),
    splice\_acceptor (1)],
    [Concordant pathogenic], [159], [45.0%], [nonsense, frameshift,
    splice donor/acceptor],
    [Concordant benign/VUS], [64], [18.1%], [synonymous, intronic, UTR,
    promoter],
    [#strong[Total]], [#strong[353]], [#strong[100%]], [],
  )]
  , kind: table
  )


---


== Pearl Variants: Real ClinVar Accessions
<pearl-variants-real-clinvar-accessions>
The following variants met both pearl criteria (VEP score \< 0.30 AND
SSIM \< 0.95). ClinVar accession numbers are real; they can be verified
at: https:/\/www.ncbi.nlm.nih.gov/clinvar/

=== Group 1: Promoter-Region Pearls (n=15)
<group-1-promoter-region-pearls-n15>
These variants map to the HBB proximal promoter region
(chr11:5,227,099--5,227,172, GRCh38). VEP annotates them as
`upstream_gene_variant` (low predicted impact). ARCHCODE places this
region within a simulated LCR--HBB enhancer--promoter contact domain and
detects disruption (mean SSIM 0.928, mean VEP 0.20).

#figure(
  align(center)[#table(
    columns: (16.44%, 21.92%, 10.96%, 6.85%, 12.33%, 31.51%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([ClinVar\_ID], [Position
      (chr11)], [Category], [SSIM], [VEP Score], [ClinVar Significance],),
    table.hline(),
    [VCV000015471], [5,227,099], [promoter], [0.928], [0.20], [Pathogenic/Likely
    path.],
    [VCV000015470], [5,227,099], [promoter], [0.928], [0.20], [Pathogenic],
    [VCV000869288], [5,227,100], [promoter], [0.929], [0.20], [Pathogenic],
    [VCV000869290], [5,227,101], [promoter], [0.928], [0.20], [Pathogenic],
    [VCV000015466], [5,227,102], [promoter], [0.929], [0.20], [Pathogenic],
    [VCV000801184], [5,227,142], [promoter], [0.928], [0.20], [Pathogenic/Likely
    path.],
    [VCV000036284], [5,227,157], [promoter], [0.928], [0.20], [Pathogenic/Likely
    path.],
  )]
  , kind: table
  )

#emph[7 of 15 promoter pearl accessions shown. All 15 with exact
positions and alleles are available in HBB\_Clinical\_Atlas\_REAL.csv.]

=== Group 2: Missense Pearls at chr11:5,226,613 (n=3)
<group-2-missense-pearls-at-chr115226613-n3>
Three variants at position 5,226,613 are annotated as
`coding_sequence_variant` by VEP (incomplete consequence prediction for
complex indels). SSIM = 0.949 (marginally below the 0.95 threshold).
These are low-confidence pearls.

#figure(
  align(center)[#table(
    columns: (49.12%, 14.04%, 7.02%, 4.39%, 7.89%, 17.54%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([ClinVar\_ID], [Position
      (chr11)], [Category], [SSIM], [VEP Score], [ClinVar Significance],),
    table.hline(),
    [VCV002664746], [5,226,613], [missense], [0.949], [0.20], [VUS],
    [\(2 additional accessions in
    HBB\_Clinical\_Atlas\_REAL.csv)], [], [], [], [], [],
  )]
  , kind: table
  )

=== Group 3: Loss-of-Function Pearls with Low VEP Annotation (n=2)
<group-3-loss-of-function-pearls-with-low-vep-annotation-n2>
These LoF variants have low VEP scores due to incomplete annotation, not
because they are genuinely low-impact. ClinVar records both as
Pathogenic.

#figure(
  align(center)[#table(
    columns: (15.58%, 20.78%, 19.48%, 6.49%, 11.69%, 25.97%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([ClinVar\_ID], [Position
      (chr11)], [Category], [SSIM], [VEP Score], [ClinVar Significance],),
    table.hline(),
    [VCV002024192], [5,226,796], [splice\_acceptor], [0.900], [0.20], [Pathogenic],
    [VCV000869358], [5,226,971], [frameshift], [0.891], [0.15], [Pathogenic],
  )]
  , kind: table
  )


---


== ACMG Evidence Assessment for Pearl Variants (Exploratory)
<acmg-evidence-assessment-for-pearl-variants-exploratory>
#strong[Important disclaimer:] The following ACMG assessment is
exploratory and computational only. No experimental functional data
exists for these variants in this study. Clinical reclassification
requires experimental evidence (PS3 from functional studies with actual
RT-PCR/RNA data).

For promoter-region pearl variants (Group 1) where ClinVar records
Pathogenic:

#figure(
  align(center)[#table(
    columns: (13.21%, 59.43%, 27.36%),
    align: (auto,auto,auto,),
    table.header([ACMG Criterion], [Evidence], [Strength],),
    table.hline(),
    [PS3\_moderate], [ARCHCODE SSIM-based structural disruption
    prediction], [Moderate (computational only)],
    [PM2], [gnomAD v4.0 MAF \< 0.0001 (consistent with rare disease
    variant)], [Moderate],
    [PP3], [ARCHCODE structural prediction + PhyloP
    conservation], [Supporting],
    [#strong[Total]], [#strong[PS3\_mod (4) + PM2 (2) + PP3 (1) = 7
    points]], [#strong[Meets LP threshold (≥6)]],
  )]
  , kind: table
  )

This assessment supports the existing ClinVar Pathogenic/Likely
Pathogenic classifications for Group 1 variants, but does not
independently justify reclassification of VUS variants without
experimental confirmation.


---


== Data Availability
<data-availability-1>
#strong[Unified dataset (v2.0):] `HBB_Unified_Atlas.csv` (1,103 rows:
353 Pathogenic + 750 Benign, single pipeline)

#strong[Legacy combined dataset (v1.0):] `HBB_Combined_Atlas.csv` (1,103
rows, dual-pipeline; preserved for reproducibility)

#strong[Pathogenic-only dataset:] `HBB_Clinical_Atlas_REAL.csv` (353
rows × 10 columns)

#strong[Pearl analysis summary:] `REAL_ATLAS_SUMMARY.json`

#strong[VEP predictions:] `hbb_vep_results.csv` (pathogenic),
`hbb_benign_vep_results.csv` (benign)

#strong[ROC analysis (unified):] `roc_unified.json`

#strong[ROC analysis (v1.0 legacy):] `roc_analysis.json`

#strong[CFTR unified dataset:] `CFTR_Unified_Atlas_317kb.csv` (3,349
rows)

#strong[CFTR within-category analysis:] `positional_signal_cftr.json`

#strong[TP53 unified dataset:] `TP53_Unified_Atlas_300kb.csv` (2,794
rows)

#strong[TP53 within-category analysis:] `positional_signal_tp53.json`

#strong[BRCA1 unified dataset:] `BRCA1_Unified_Atlas_400kb.csv` (10,682
rows)

#strong[BRCA1 within-category analysis:] `positional_signal_brca1.json`

#strong[MLH1 unified dataset:] `MLH1_Unified_Atlas_300kb.csv` (4,060
rows)

#strong[MLH1 within-category analysis:] `positional_signal_mlh1.json`

#strong[LDLR unified dataset:] `LDLR_Unified_Atlas_300kb.csv` (3,284
rows)

#strong[SCN5A unified dataset:] `SCN5A_Unified_Atlas_400kb.csv` (2,488
rows)

#strong[Multimodal AlphaGenome validation:]
`multimodal_alphagenome_hbb.json` (pearl),
`multimodal_alphagenome_hbb_benign_control.json` (benign control),
`multimodal_pearl_vs_benign_comparison.json` (Mann-Whitney U
comparison), `multimodal_alphagenome_brca1_pathogenic.json`,
`multimodal_alphagenome_brca1_benign.json`,
`multimodal_brca1_path_vs_benign_comparison.json` (BRCA1 cross-locus),
`multimodal_alphagenome_scn5a_pathogenic.json`,
`multimodal_alphagenome_scn5a_benign.json`,
`multimodal_scn5a_path_vs_benign_comparison.json` (SCN5A cell-type
mismatch control)

#strong[Hi-C correlation results:] `hic_correlation_brca1.json`,
`hic_correlation_tp53.json`, `hic_correlation_mlh1.json`

#strong[TDA results:] `tda_proof_of_concept_tp53.json`,
`tda_proof_of_concept_brca1.json`, `tda_proof_of_concept_mlh1.json`

#strong[Bayesian optimization results:] `bayesian_fit_hic.json`

#strong[Format:] Comma-separated values (CSV), UTF-8 encoding

#strong[Repository:] https:/\/github.com/sergeeey/ARCHCODE

#strong[Contact:] sergeikuch80\@gmail.com


---


== Methods Summary (Supplementary)
<methods-summary-supplementary>
#strong[ARCHCODE simulation:]

- Analytical mean-field contact computation (no Monte Carlo sampling)
- Kramer kinetics: α=0.92, γ=0.80 (grid-search; Bayesian optimization
  Δr=0.0001, confirmed near-optimal)
- HBB: 50 bins × 600 bp = 30 kb; 159 bins × 600 bp = 95 kb
- CFTR: 317 bins × 1000 bp = 317 kb; 3 CTCF (ENCODE K562 ENCFF660GHM), 4
  enhancers (literature)
- TP53: 300 bins × 1000 bp = 300 kb; 6 CTCF (ENCODE K562 ENCFF736NYC), 5
  enhancers (ENCODE K562 H3K27ac ENCFF864OSZ + literature)
- BRCA1: 400 bins × 1000 bp = 400 kb; 13 CTCF (ENCODE K562 ENCFF736NYC),
  9 enhancers (ENCODE MCF7 H3K27ac ENCFF340KSH)
- MLH1: 300 bins × 1000 bp = 300 kb; 7 CTCF (ENCODE K562 ENCFF736NYC), 8
  enhancers (ENCODE K562 H3K27ac ENCFF864OSZ)
- Global SSIM calculated on full N×N matrix (upper triangular, k=1)
- Local SSIM (LSSIM): SSIM on 50×50 submatrix centered on variant bin;
  clamp+shift edge handling; for matrices ≤50 bins LSSIM ≡ global SSIM
- Verdict thresholds applied to LSSIM: PATHOGENIC (\<0.85),
  LIKELY\_PATHOGENIC (0.85--0.92), VUS (0.92--0.96), LIKELY\_BENIGN
  (0.96--0.99), BENIGN (≥0.99)
- Both global SSIM and LSSIM reported in output CSV for backward
  compatibility
- Seed=2026 for reproducibility
- classify\_hgvs(): cDNA indel length modulo 3 for frameshift/inframe
  detection (resolves \>90% of "other" category)

#strong[VEP predictions:]

- Ensembl VEP v113 REST API
- Consequence-based scoring + SIFT integration for missense
- SpliceAI not available (API unreachable during study period)

#strong[Statistical analysis:]

- Permutation testing (10,000 iterations) for SSIM clustering
  significance
- ACMG/AMP 2015 guidelines for exploratory evidence assessment
- Discordance defined as ARCHCODE verdict ≠ VEP verdict (pathogenic vs
  benign/VUS)

#strong[Known limitations for interpretation:]

- Hi-C validation (HBB): GM12878 r = 0.16, p = 0.301, ns (n = 12); K562
  30kb r = 0.530, p = 2.19 × 10⁻⁸² (n = 1,124); K562 95kb r = 0.588, p
  \< 10⁻³⁰⁰ (n = 11,649)
- Hi-C validation (TP53): K562 r = 0.293, MCF7 r = 0.276; both p \<
  10⁻¹³⁶ (n = 7,821)
- Hi-C validation (BRCA1): K562 r = 0.530 (n = 12,093), MCF7 r = 0.500
  (n = 7,307); both p ≈ 0
- Hi-C validation (MLH1): K562 r = 0.589 (n = 20,432); p ≈ 0
- Hi-C validation (LDLR): HepG2 r = 0.320 (n = 19,156); p ≈ 0
- Parameters manually calibrated, not fitted to HBB locus; Bayesian
  optimization (Optuna, 200 trials) confirmed near-optimal (Δr=0.0001)
- Within-category (LSSIM): null on HBB/CFTR/TP53 (p \> 0.29);
  BRCA1/MLH1/LDLR significant but ΔAUC \< 0.02 (power effect)
- Matrix-size dilution resolved by LSSIM (50×50 window); LSSIM range
  0.75--1.00 across all loci

#strong[AlphaGenome benchmark:]

- AlphaGenome SDK v0.6.0 (Google DeepMind); contact maps from 4DN at
  2048 bp resolution
- Cell lines: GM12878 (EFO:0002784) for HBB/CFTR/TP53/BRCA1/MLH1; HepG2
  (EFO:0001187) for LDLR
- Distance normalization: O/E per genomic distance stratum; AlphaGenome
  log→linear via exp()
- Correlation: Spearman ρ on upper triangle (k=2); ρ = 0.12 (HBB 95kb)
  to 0.52 (BRCA1)
- CFTR benchmark: no Hi-C ground truth available (no cross-locus
  fallback used)
- Variant-level: `predict_variant()` API on 23 pearl variants; ΔSSIM via
  scikit-image SSIM
- Epigenome: CHIP\_TF (CTCF) and CHIP\_HISTONE (H3K27ac) at 128 bp
  resolution; peak detection at 90th percentile; overlap tolerance 2 kb
- Multimodal: `predict_variant()` with RNA\_SEQ + ATAC at 1 bp
  resolution; K562 (EFO:0002067); 23 pearl variants; metrics:
  max\_abs\_delta, cosine\_similarity, signal\_concentration\_ratio
  (±500 bp window)
- Scripts: `benchmark_alphagenome.py`,
  `variant_mutagenesis_alphagenome.py`,
  `epigenome_crossval_alphagenome.py`, `multimodal_alphagenome.py`

#strong[Akita benchmark:]

- Akita (Fudenberg et al.~2020, Nature Methods); Basenji framework
  (Kelley et al.~2020), TensorFlow 2.20.0, local CPU inference
- Model: `model_best.h5` from `gs://basenji_hic/1m/models/9-14/`\;
  751,653 parameters
- Input: 1,048,576 bp one-hot DNA; output: 448×448 contact map (upper
  triangle, 99,681 elements) at 2048 bp resolution
- Cell types: HFF, H1-hESC, GM12878 (idx=2), IMR-90, HCT-116; GM12878
  used for all loci
- Reference sequences: Ensembl REST API (GRCh38), cached locally
- Distance normalization and correlation: identical to AlphaGenome
  benchmark (O/E, Spearman ρ, k=2)
- Variant-level: manual ref/alt sequence substitution + dual prediction
  \+ ΔSSIM; 23 pearl variants
- Scripts: `benchmark_akita.py`, `variant_mutagenesis_akita.py`

#strong[Software:]

- ARCHCODE v2.5 (TypeScript + Python), Optuna 4.7.0, ripser 0.6.10,
  alphagenome 0.6.0, scikit-image 0.26.0, tensorflow-cpu 2.20.0, basenji
  (Calico)
- Scripts: `generate-unified-atlas.ts`, `analyze_positional_signal.py`,
  `tda_proof_of_concept.py`, `download_clinvar_generic.py`,
  `bayesian_fit_hic.py`, `benchmark_alphagenome.py`,
  `variant_mutagenesis_alphagenome.py`,
  `epigenome_crossval_alphagenome.py`, `multimodal_alphagenome.py`,
  `benchmark_akita.py`, `variant_mutagenesis_akita.py`


---


