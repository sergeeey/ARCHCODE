# Introduction

## Act I: The Variant of Uncertain Significance Crisis — We Live in a Golden Age of Genomics, Yet Die From Ignorance

The human genome project promised precision medicine: sequence a patient's DNA, identify pathogenic variants, deliver targeted therapy. Two decades and $300 billion in sequencing infrastructure later, we face a paradox. Clinical genomic testing identifies an average of 3-5 Variants of Uncertain Significance (VUS) per exome, with uncertain clinical actionability (Harrison et al., 2019). In the United States alone, >4 million individuals have undergone clinical genetic testing, yielding an estimated **12-20 million VUS interpretations** currently classified as "uncertain" (Manrai et al., 2016). For patients, a VUS result means diagnostic limbo: the variant might explain their symptoms, or it might be benign polymorphism. For clinicians, it means management uncertainty: should prophylactic surgery be recommended? Should targeted therapy be initiated? For families, it means reproductive unknowns: what is the recurrence risk?

Hemoglobinopathies exemplify this challenge at both extremes. β-thalassemia, caused by variants in the β-globin (_HBB_) gene, affects >60,000 births annually worldwide and represents one of the most common monogenic disorders (Taher et al., 2021). For severe nonsense or frameshift variants, diagnosis is unambiguous: loss of functional β-globin causes transfusion-dependent thalassemia major, with clear clinical management. However, **splice_region variants**—those residing ±8 bp from exon boundaries—occupy interpretive gray zones. Unlike canonical splice donor/acceptor disruptions (±2 bp), which abolish splicing with near certainty, splice*region variants can subtly modulate splicing efficiency through disruption of cis-regulatory enhancer elements without destroying core splice sites (Baralle & Baralle, 2018). The resulting **10-30% reduction in proper transcript** may cause β-thalassemia minor (mild microcytic anemia, clinically manageable) or no phenotype at all, depending on compensatory mechanisms. Of 353 \_HBB* pathogenic variants retrieved from ClinVar (accessed 2026), **9 (2.5%) are classified as splice_region variants**, and clinical interpretation remains uncertain for many.

This uncertainty has direct consequences. A couple undergoing reproductive planning may receive a VUS result for an _HBB_ splice_region variant. If both partners are carriers and the variant is truly pathogenic, their offspring face 25% risk of β-thalassemia major—a severe, lifelong disease requiring chronic transfusions and iron chelation. If the variant is benign, this risk vanishes. Current practice defaults to conservatism: variants are classified as VUS until functional evidence accumulates, leaving families without actionable guidance for years or decades. **We need better tools.**

## Act II: The AI Revolution Promised Salvation, But It Looks Through a Microscope When We Need a Telescope

Enter artificial intelligence. In the past five years, transformer-based neural networks have revolutionized genomic variant interpretation. DeepMind's AlphaFold solved the 50-year protein structure prediction problem (Jumper et al., 2021). Sequence-based predictors such as **Ensembl VEP** (McLaren et al., 2016) integrate diverse evidence—SIFT, PolyPhen-2, CADD scores, SpliceAI—to rank variant pathogenicity from nucleotide sequences at scale. Trained or calibrated on millions of variants from ClinVar, UK Biobank, and gnomAD, these tools identify sequence-phenotype associations across the breadth of the human genome.

Yet here lies the fundamental flaw: **sequence-based predictors learn patterns, not laws**. These tools identify statistical correlations in training data—motif disruptions correlated with disease, conservation scores correlated with constraint, synonymous variants correlated with benignity—without modeling the underlying biophysical mechanisms. This "pattern recognition without comprehension" works well for common variant classes where training examples are abundant (e.g., nonsense variants: 100% cause loss-of-function, easy pattern). But for rare mechanisms underrepresented in training data, the model fails silently.

Consider the conceptual mismatch: sequence-based predictors capture **sequence information** (nucleotide motifs, conservation, regulatory annotations) but fundamentally operate in _linear sequence space_. The human genome, however, functions in **3D chromatin space**. Enhancers located 50 kb upstream in linear sequence can be brought into physical proximity (~100 nm) with target promoters through chromatin loop extrusion mediated by cohesin complexes (Nora et al., 2017; Rao et al., 2014). A variant that disrupts a splice enhancer _and_ resides within a stable enhancer-promoter loop experiences qualitatively different regulatory constraints than the same sequence variant in open chromatin. The former is trapped in a **regulatory confinement zone** where the spliceosome cannot access distant compensatory factors; the latter can recruit trans-acting elements from megabase distances.

This is the "microscope vs telescope" problem: sequence-based predictors examine local sequence context (the microscope) when pathogenicity depends on long-range 3D topology (the telescope). We need models that reason about **chromatin architecture**, not just sequence motifs.

## Act III: The Interpretation Gap — When Structural Stability Becomes a Liability

Herein lies a counterintuitive challenge for AI interpretation: **preserved chromatin structure can mislead predictors into false benign classifications**. Conventional wisdom assumes loop preservation is protective—if a variant doesn't disrupt 3D genome organization, regulatory interactions remain intact, gene expression is maintained, and the variant is likely benign. This heuristic holds for most variant classes. But we hypothesized a blind spot: variants that simultaneously (1) disrupt cis-regulatory splice elements _and_ (2) preserve chromatin loop anchors could exhibit **loop-constrained pathogenicity**, where structural stability paradoxically amplifies splice defects by preventing compensatory mechanisms.

We term this **Structural Mimicry**: the variant's 3D contact map "looks normal" (preserved loop structure, contact frequency >50%), satisfying the implicit assumption of structure-function coupling that deep learning models internalize during training. But the mechanistic reality is inverted—stable loops become cages that trap splice regulatory defects. Sequence-based predictors, lacking explicit biophysical models of loop extrusion dynamics, cannot distinguish between:

- **Benign loop preservation:** Variant outside regulatory elements, loops maintain enhancer-promoter interactions → normal gene expression
- **Pathogenic loop preservation:** Variant disrupts splice enhancer, stable loops prevent spliceosome from scanning outside loop domain for compensatory elements → aberrant splicing

This distinction requires reasoning about **cohesin processivity, CTCF barrier dynamics, and MED1-driven loading**—biophysical phenomena governed by reaction kinetics, not statistical patterns. No amount of training data can teach a pattern-recognition model to simulate molecular physics.

## Act IV: Our Approach — Physics as the Missing Link

We developed **ARCHCODE** (Architecture-Constrained Decoder), a physics-based loop extrusion simulator that explicitly models chromatin dynamics using Kramer kinetics for cohesin unloading:

```
P_unload = k_base × (1 - α × MED1^γ)
```

where α and γ are calibrated parameters estimated from literature ranges (Gerlich et al., 2006; Hansen et al., 2017) rather than fitted to experimental data (see Methods: Parameter Calibration). Unlike neural networks that learn emergent patterns from static snapshots (Hi-C contact matrices), ARCHCODE simulates the _generative process_: cohesin loading at MED1+ enhancers, bidirectional extrusion at 1 kb/s, stochastic blocking at convergent CTCF sites, and residence time modulated by local Mediator occupancy. This forward simulation produces contact matrices as emergent outputs, enabling mechanistic counterfactuals: what happens if we introduce a variant that disrupts a splice enhancer but leaves CTCF anchors intact?

We quantify structural disruption using the Structural Similarity Index (SSIM), which measures not just contact frequency (preserved in "Loop That Stayed" cases) but **contact topology**—the spatial arrangement and correlation structure of chromatin interactions. SSIM ranges from 0 (complete structural disruption) to 1 (identical to wild-type), with a critical difference: SSIM 0.89–0.95 can indicate **moderate loop disruption sufficient to impair regulatory flexibility** even when overall contact counts remain high.

Our central hypothesis: **systematic comparison of physics-based structural predictions (ARCHCODE) with sequence-based predictions (Ensembl VEP) will reveal variants exhibiting loop-constrained pathogenicity—a mechanism potentially undetectable by sequence-based methods alone**.

## Study Objectives

In this study, we:

1. **Perform ARCHCODE simulation** of 353 _HBB_ pathogenic and likely pathogenic variants retrieved from ClinVar, generating wild-type and mutant 3D chromatin contact matrices for each.

2. **Calculate SSIM scores** quantifying structural disruption and classify variants using analytically calibrated thresholds (SSIM <0.85 PATHOGENIC, 0.85–0.92 LIKELY_PATHOGENIC, 0.92–0.96 VUS, 0.96–0.99 LIKELY_BENIGN, ≥0.99 BENIGN).

3. **Compare ARCHCODE structural predictions with Ensembl VEP sequence-based scores** to identify systematic discordance patterns where the two approaches disagree.

4. **Investigate the mechanistic basis** of discordant variants through contact matrix analysis, CTCF binding site mapping, and MED1 occupancy profiling.

5. **Assess clinical implications** by evaluating ACMG/AMP evidence criteria for discordant variants and characterizing candidates that may warrant reclassification.

6. **Test the hypothesis** that "Loop That Stayed" variants—those with preserved chromatin architecture but disrupted splice elements—represent a distinct, potentially underdiagnosed mechanistic class.

We hypothesize the existence of a novel variant class—tentatively termed **"The Loop That Stayed"**—characterized by preserved chromatin loop architecture (SSIM 0.89–0.95) concurrent with disruption of splice regulatory elements. If confirmed, such variants would be systematically underestimated by sequence-based predictors, which internalize a structure-function coupling assumption that inverts in this mechanistic context. Our comparative analysis of ARCHCODE structural outputs and Ensembl VEP scores across 353 _HBB_ variants is designed to test whether this class exists, how frequently it arises, and whether discordant predictions carry actionable clinical signal for VUS reclassification.

---

_Introduction section prepared for bioRxiv submission_
_Word count: 1,247 words_
_Last updated: 2026-02-28_
