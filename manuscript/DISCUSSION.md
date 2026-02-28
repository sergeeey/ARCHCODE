# Discussion

> **NOTE (2026-02-28):** This standalone Discussion file is from an earlier manuscript phase
> and uses outdated SSIM thresholds (0.50–0.60). The current Discussion section is in
> `FULL_MANUSCRIPT.md` (lines 807–951), which uses analytically calibrated thresholds
> (PATHOGENIC < 0.85, LP 0.85–0.92, VUS 0.92–0.96, LB 0.96–0.99, B ≥ 0.99).
> Pearl SSIM range: 0.89–0.95. **Use FULL_MANUSCRIPT.md as the authoritative version.**

## Revisiting the Paradox: When Chromatin Stability Becomes a Molecular Cage

We began this study with a counterintuitive hypothesis: chromatin loop preservation, traditionally
assumed protective, could paradoxically amplify pathogenicity for variants disrupting cis-regulatory
splice elements. The computational framework "The Loop That Stayed" explores this inversion across
our dataset of 353 _HBB_ variants. Among the 20 "pearl" variants identified by ARCHCODE — variants
where structural loop integrity is preserved yet regulatory disruption is predicted — the dominant
mechanistic class is **promoter variants** (the primary pearl category), with splice_region variants
representing a secondary class. All pearl variants exhibit simulated contact preservation
(SSIM 0.50–0.60), placing them in the **Goldilocks zone of structural stability** within our dataset.
Yet ARCHCODE predicts significant regulatory disruption for these same variants.

This paradigm inversion has implications for how we interpret computational variant evidence. For
decades, computational biology has operated under an implicit structure-function heuristic: _if
chromatin architecture is preserved, gene regulation remains intact_. This assumption guided the
design of Hi-C interpretation algorithms, 3D genome visualization tools, and — critically — the
architecture of sequence-based deep learning variant predictors. Preserved contact maps signal
"normalcy" to these systems. Our simulations suggest that **this heuristic may fail for a specific
mechanistic class**: variants where stable loops create regulatory confinement zones that prevent
access to compensatory regulatory elements.

The Goldilocks zone (SSIM 0.50–0.60) in our 353-variant HBB dataset represents a computational
signature where loop stability may transition from protective to pathogenic. Below this threshold
(SSIM <0.45), simulated chromatin architecture collapses severely enough that ARCHCODE detects
massive regulatory disruption — these correspond to the unambiguous structural-loss class. Above
this threshold (SSIM >0.85), structural preservation in our simulations correlates with benign
ARCHCODE classification — variants reside in non-regulatory regions with minimal predicted impact.
Within the Goldilocks zone, however, **loops may be stable enough to confine compensatory mechanisms
yet disrupted enough to impair gene expression**. This is the computational blind spot we seek to
characterize.

We propose a mechanistic hypothesis: cohesin-mediated loop extrusion may create topological barriers
limiting access to compensatory regulatory elements. Normally, when a splice enhancer is disrupted,
compensatory mechanisms can recruit trans-acting factors from distal chromatin regions — a process
that may occur over megabase distances given sufficient chromatin flexibility (Blencowe, 2017).
However, when the disrupted enhancer resides within a stable LCR-promoter loop (~50 kb in _HBB_),
and both CTCF anchors remain functional, we hypothesize the spliceosome may become **topologically
constrained**. Testing this model requires direct measurement of spliceosome dynamics and
MED1-dependent loop lifetimes — experiments not yet performed.

## The Computational Blind Spot: Orthogonal Models for Orthogonal Mechanisms

Sequence-based variant effect predictors (VEP tools such as CADD, REVEL, SpliceAI, and their
successors) represent a triumph of pattern recognition: vast training corpora of annotated variants
distilled into models capturing sequence-phenotype associations at scale. Yet our analysis reveals a
systematic pattern in discordant variants: ARCHCODE classifies 161 of 353 variants (45.6%) as
pathogenic, while sequence-based predictors classify 128 of those same variants differently
(VEP-only discordance). Two variants are classified as pathogenic by ARCHCODE only. The total
discordance rate is 130/353 (36.8%).

The discordance is concentrated in **promoter and regulatory variants** — precisely the class where
3D chromatin topology most directly mediates gene expression. The answer to why discordance occurs
lies in **complementarity, not competition**. Sequence-based VEP tools excel at detecting
sequence-level defects — splice donor/acceptor disruptions, frameshift-induced nonsense, missense
variants destabilizing protein folds — but they cannot simulate chromatin loop extrusion dynamics,
CTCF barrier stochasticity, or MED1-driven cohesin loading kinetics. ARCHCODE addresses a
complementary dimension: 3D chromatin topology as a regulatory layer.

Consider the statin analogy. Statins lower LDL cholesterol, preventing atherosclerotic plaques —
but they don't detect existing plaques, assess plaque stability, or predict acute rupture risk. For
those tasks, you need imaging (MRI, CT angiography). Similarly, sequence-based VEP tools excel at
detecting sequence-level defects but cannot simulate structural chromatin dynamics. For those
mechanisms, physics-based simulation provides an orthogonal perspective.

The critical insight is that **these tools are not redundant**. Orthogonal computational models
capture orthogonal biological mechanisms:

- **Sequence-based VEP tools:** Post-transcriptional mechanisms (mRNA stability, protein folding,
  canonical splice site disruption) — effective for protein-coding and canonical splice variants
- **ARCHCODE:** Topological mechanisms (regulatory confinement, loop-mediated enhancer access) —
  addresses promoter and regulatory variants operating via 3D chromatin architecture

It is essential to note a critical limitation of ARCHCODE: **the tool cannot detect missense
pathogenicity**. Missense variants that cause disease through protein misfolding, loss of catalytic
activity, or dominant-negative mechanisms operate entirely at the protein level — a dimension
invisible to chromatin topology simulation. For missense variants, sequence-based VEP tools remain
the appropriate primary tool. ARCHCODE provides orthogonal evidence _specifically_ for regulatory,
promoter, and structural variants where 3D genome organization mediates the mechanism.

A comprehensive variant interpretation pipeline may benefit from both approaches. Single-model
strategies — whether purely sequence-based or purely structural — will systematically miss variants
operating through mechanisms outside their detection range.

This has potential implications for interpretation guidelines. Current ACMG/AMP guidelines
(Richards et al., 2015) recommend using "multiple lines of computational evidence" (PP3 criterion)
but do not distinguish between _redundant_ predictors (e.g., CADD, REVEL, MetaSVM — all trained on
overlapping sequence features) versus _orthogonal_ predictors (e.g., sequence-based VEP for
sequence mechanisms, ARCHCODE for structural mechanisms). We propose that evidence from
physics-based structural simulation, if experimentally validated, should carry independent weight
beyond sequence-based predictions for splice_region and regulatory variants where 3D topology is
functionally critical. This proposal requires experimental validation before clinical adoption.

## Computational Evidence and the Path to Clinical Translation

The computational signature of "The Loop That Stayed" — particularly for the 20 pearl variants
identified in our 353-variant HBB dataset — has potential clinical implications, contingent on
experimental validation. The dominant pearl class, **promoter variants**, currently lacks structural
pathogenicity assessment in most variant interpretation workflows. If ARCHCODE's predictions are
experimentally confirmed, this would represent a clinically actionable finding for a class of
variants systematically undercharacterized by sequence-based tools.

We explicitly note that no ClinVar accession identifiers are cited in this section: the specific
variants in our dataset require independent experimental confirmation before ClinVar evidence
submission would be appropriate.

Contingent on functional validation (RT-PCR confirmation of aberrant splicing, experimental Hi-C
measurement of loop lifetimes), we propose:

**1. Hypothesis-driven experimental testing:** ARCHCODE SSIM-based predictions constitute
computational hypotheses requiring functional validation. RT-PCR in erythroid cells (K562, HUDEP-2)
would test splice defect predictions directly for splice_region pearl variants. Promoter pearl
variants would require reporter assays or CRISPR-mediated mutagenesis to assess transcriptional
impact. Only upon experimental confirmation should ACMG evidence codes (PS3 for functional studies)
be considered for ClinVar submissions.

**2. Patient cohort screening (if validated):** Should functional assays confirm regulatory defects,
β-thalassemia patients with unexplained genetic etiology could undergo targeted sequencing of
predicted pearl variant positions. Genotype-phenotype correlation (HbA2 >3.5%, MCV 60–75 fL) would
provide clinical evidence strengthening pathogenicity assessment.

**3. Genome-wide computational screening:** Systematic ARCHCODE simulation of regulatory VUS in
genes with documented enhancer-promoter loops (FGFR2, SOX9, SHH, HBG1/2) could identify
additional candidates for experimental prioritization. This represents a hypothesis-generation
pipeline, not a clinical diagnostic tool. The scale of such extrapolation — how many genome-wide
variants might fall into the structural blind spot — remains speculative without locus-specific
validation.

**4. Integration into variant interpretation workflows:** Physics-based structural simulation
(ARCHCODE) could complement sequence-based VEP tools in research laboratories. Discordant
predictions (e.g., VEP=VUS, ARCHCODE=Likely Pathogenic) would flag variants for functional
follow-up, not immediate clinical reclassification. This orthogonal evidence framework requires
experimental validation before clinical deployment.

ARCHCODE simulations require ~8 seconds per variant on standard hardware (12-core CPU, 64 GB RAM).
Batch processing of a 50-gene panel (~500 variants) completes in <2 hours, consistent with research
turnaround constraints — though clinical utility depends on experimental validation of predictions.

## Falsification Plan and Boundary Conditions

Our findings constitute a **computational discovery requiring experimental falsification**, not a
clinical diagnostic claim. We formulate testable predictions with explicit kill-criteria:

**Null hypothesis (H0):** The 20 pearl variants identified by ARCHCODE do _not_ exhibit functional
regulatory disruption in erythroid cells; SSIM clustering in the Goldilocks zone is a statistical
artifact of the simulation model unrelated to actual regulatory function.

**Kill-criteria (rejecting our model):**

1. RT-PCR in K562/HUDEP-2 shows <5% aberrant splicing for splice_region pearl variants (vs
   predicted 10–35%)
2. Promoter reporter assays show no significant transcriptional reduction for promoter pearl
   variants
3. FRAP-measured cohesin residence times at _HBB_ LCR do _not_ correlate with MED1 occupancy
   (invalidating Kramer kinetics assumption)
4. MED1 knockdown fails to alter chromatin contact frequencies at the _HBB_ locus (invalidating
   fountain-loading model)
5. Patient genotype-phenotype data contradicts predictions (e.g., homozygotes with normal HbA2,
   carriers with β-thalassemia major)

**Boundary of claims:** Our SSIM-based predictions are **computational hypotheses**, not
ACMG-compliant functional evidence (PS3). Clinical reclassification requires experimental
confirmation. The Goldilocks zone (SSIM 0.50–0.60) is specific to our _HBB_ dataset; generalization
to other genes requires locus-specific validation and potential recalibration of thresholds.

## Limitations and the Path to Experimental Validation

We acknowledge critical limitations that temper interpretation and underscore the need for
experimental follow-up:

**1. Computational predictions, not experimental proof:** ARCHCODE simulations remain _in silico_
models. Experimental Hi-C validation showed weak correlation (r=0.16, not statistically
significant), which must be acknowledged as a serious limitation of the current model. The predicted
regulatory disruption for pearl variants requires functional confirmation — RT-PCR for splice_region
variants, reporter assays for promoter variants — before any clinical inference is warranted.

**2. No missense pathogenicity detection:** ARCHCODE operates on chromatin topology and cannot
assess protein-level mechanisms. Missense variants causing disease via protein misfolding, loss of
function at the protein level, or dominant-negative effects are outside ARCHCODE's scope entirely.
Comparison with sequence-based VEP tools on missense variants is therefore inappropriate, and such
variants were excluded from discordance analysis.

**3. Simplified physics:** Our Kramer kinetics model assumes cohesin unloading probability depends
solely on local MED1 occupancy, neglecting DNA sequence-dependent processivity, ATP-dependent motor
activity, and potential cohesin-cohesin interactions. More sophisticated models incorporating these
factors may refine SSIM threshold boundaries.

**4. Static epigenetic landscape:** We model _HBB_ chromatin architecture using MED1 and CTCF
ChIP-seq from GM12878 lymphoblastoid cells, extrapolating to erythroid context where β-globin is
actively expressed. Cell-type-specific differences in Mediator occupancy or CTCF binding may alter
loop dynamics substantially, affecting SSIM predictions. Erythroid-specific Hi-C (HUDEP-2) would
provide optimal validation data.

**5. 1D simulation of 3D reality:** ARCHCODE models chromatin in 1D (genomic coordinate space) with
contact frequency as a proxy for 3D proximity. True 3D polymer simulations (e.g., Molecular
Dynamics) could capture steric effects, chromatin compaction, and phase separation dynamics absent
from our model — but at 1000× computational cost, rendering genome-scale screening infeasible with
current hardware.

**6. No patient-level validation:** The strongest clinical evidence would be identification of
patients carrying pearl variants with documented β-thalassemia phenotypes. No such patient data is
currently available for the specific variants in our dataset, either because of rarity (MAF<0.0001)
or because phenotypic mildness (β-thalassemia minor may go undiagnosed). This absence of patient
data is a limitation, not evidence of rarity.

We propose a tiered validation strategy balancing rigor with feasibility:

- **Tier 1 (3–4 months, $90–150K):** RT-PCR in K562 cells (splice*region pearl variants) + promoter
  reporter assays (promoter pearl variants) + Capture Hi-C at \_HBB* locus (experimental SSIM
  measurement to test the r=0.16 baseline)
- **Tier 2 (6–9 months, $110–170K):** CRISPR base editing to generate isogenic panel + minigene
  assays ± LCR loop anchors
- **Tier 3 (9–12 months, $60–100K):** CRISPRi-mediated CTCF disruption to test loop rescue
  hypothesis + patient cohort screening

Successful Tier 1 validation (functional defect confirmed, SSIM experimentally correlated with
measured contact frequencies) would provide functional evidence supporting pathogenicity assessment
under ACMG PS3 criterion, enabling ClinVar evidence submission pending expert panel review. Tier
2–3 provide mechanistic validation of the topological confinement hypothesis and enable
generalization to other loop-constrained loci.

## The Future: Orthogonal Computation and Mechanistic Hypothesis Generation

We conclude where we began: with a paradox. The human genome project delivered sequence;
high-throughput screening delivered phenotypes; deep learning delivered patterns. Yet **patterns
without principles** leave systematic blind spots. Physics-based simulation provides a complementary
dimension — mechanistic hypotheses that explain when and why statistical patterns may fail.

"The Loop That Stayed" is not a confirmed biological discovery. It is a **computational
proof-of-concept** that 3D genome topology simulation may identify a class of regulatory variants
— primarily promoter variants — that sequence-based tools systematically undercharacterize. The
weak Hi-C correlation (r=0.16) and absence of experimental functional data mean this framework
remains a hypothesis requiring rigorous testing.

The era of single-model variant interpretation faces a choice. The future may belong to **orthogonal
computational ensembles** — physics-based structural simulation complementing sequence-based pattern
recognition, with experimental validation confirming or refuting computational predictions, and
evidence-based guidelines integrating orthogonal mechanistic insights. Whether ARCHCODE's structural
predictions represent genuine regulatory biology, or are artifacts of an insufficiently validated
simulation model, is precisely the question that motivates the experimental program outlined above.

We have proposed a hypothesis, grounded in 353 computationally analyzed variants, with explicit
discordance statistics (36.8%) and explicit limitations (r=0.16 Hi-C correlation, no experimental
functional data). We have identified testable predictions with falsification criteria. What remains
is rigorous experimental validation.

---

_Discussion section prepared for bioRxiv submission_
_Word count: ~1,800 words_
_Last updated: 2026-02-28_
_Status: Computational discovery paper — experimental validation required for all functional claims_
_Data integrity: AlphaGenome references removed; fake ClinVar IDs removed; statistics updated to
n=353, 161 pathogenic (45.6%), 20 pearl variants, discordance 130/353 (36.8%)_
