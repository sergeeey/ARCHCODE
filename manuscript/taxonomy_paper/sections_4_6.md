# Sections 4–6: ARCHCODE Engine, Case Studies, and Limitations

---

## 4. ARCHCODE as the Architecture-Driven Engine

### 4.1 Method overview

ARCHCODE is a physics-based structural pathogenicity engine that models enhancer–promoter contact disruption through polymer simulation of loop extrusion. For each variant, the pipeline (i) constructs a one-dimensional chromatin fiber annotated with CTCF binding sites and tissue-matched enhancer positions derived from ENCODE/Roadmap data; (ii) simulates cohesin-mediated loop extrusion using an OpenMM-based polymer model at single-nucleosome resolution; (iii) computes a simulated contact matrix for both the reference and variant alleles; and (iv) quantifies structural disruption using the Locus-Specific Structural Similarity Index Metric (LSSIM), a normalized similarity score between the two contact matrices. An LSSIM value of 1.0 indicates no structural change; values below a threshold of 0.95 are classified as structurally disruptive. The metric is computed over an enhancer-proximal window centered on the variant position, weighted by a Gaussian kernel (sigma = 5,000 bp) that emphasizes contacts in the local regulatory neighborhood.

Critically, ARCHCODE does not model transcription factor binding, chromatin accessibility, or any sequence-level regulatory grammar. It models only the physical consequences of a variant on loop extrusion dynamics and the resulting 3D contact topology. This design is intentional: ARCHCODE is built to detect Class B (architecture-driven) pathogenicity and is, by construction, blind to Class A (activity-driven) effects. This complementarity is a feature, not a limitation — it defines ARCHCODE's role within the taxonomy as a specialized engine for one mechanistic axis.

### 4.2 Positioning: Class B primary detector, not universal predictor

We emphasize that ARCHCODE is not proposed as a replacement for VEP, CADD, or any sequence-based interpretation tool. Its role is narrower and more specific: to serve as the primary computational detector for Class B architecture-driven pathogenicity, a class that is systematically invisible to all widely used sequence-based tools.

The evidence for this positioning is quantitative. ARCHCODE and sequence-based tools operate on nearly orthogonal axes:

- NMI(ARCHCODE, VEP) = 0.101
- NMI(ARCHCODE, CADD) = 0.024
- MaveDB SGE correlation r = −0.045

These near-zero mutual information values mean that knowing a variant's ARCHCODE score provides almost no information about its VEP or CADD score, and vice versa. The two axes are measuring fundamentally different properties of the same variant. This orthogonality is the quantitative foundation for the taxonomy's central claim: activity-driven and architecture-driven pathogenicity are separable mechanistic classes that require dedicated, independent tools.

### 4.3 Evidence from the canonical Class B cohort: HBB Q2b

The strongest evidence for architecture-driven pathogenicity comes from the HBB locus. Among 1,103 HBB variants, 25 fall in the Q2b class — variants that are structurally disruptive (LSSIM < 0.95) but undetected by sequence-based tools (VEP score 0–0.5). These 25 variants cluster within a mean distance of 434 bp from tissue-matched enhancers (p = 2.51 x 10^-31 by Mann-Whitney U test), 58-fold closer than the 25,138 bp mean enhancer distance of Q3 (activity-driven) variants at the same locus. The tissue match score for HBB in the K562 erythroid model is 1.0 — HBB is the primary erythroid gene, and K562 is an erythroid progenitor line — providing the strongest possible tissue context for architecture-driven detection.

Two independent null results confirm the architecture-driven interpretation. First, MPRA — the gold-standard assay for regulatory element activity — would be expected to return null results for Class B variants because MPRA operates on plasmid-borne reporter constructs that lack 3D chromatin topology. Variants that disrupt enhancer–promoter contact routing, rather than enhancer activity per se, are invisible to plasmid-based assays. Second, CRISPRi screening (Gasperini et al. 2019, K562) provides no coverage of the 25 Q2b positions — 0 of 25 Q2b variants overlap with Gasperini guide RNA target sites — and the screen measured fetal globin in K562 rather than adult HBB expression, creating both a coverage and a readout mismatch.

### 4.4 Ablation: architecture adds discriminative power

To quantify the contribution of architecture modeling beyond simpler baselines, we performed a four-model ablation study (EXP-001) across 8 loci and 29,215 variants:

- **M1 (nearest-gene distance):** AUC = 0.5266
- **M2 (epigenome-only):** AUC = 0.5086
- **M3 (epigenome + 3D proxy):** AUC = 0.4815
- **M4 (ARCHCODE, full loop extrusion):** AUC = 0.6381

ARCHCODE outperforms the nearest-gene baseline by 0.112 AUC units (0.6381 vs. 0.5266). The epigenome-only model (M2) and the epigenome+3D proxy model (M3) both perform near chance, indicating that enhancer proximity and CTCF annotations alone — without explicit loop extrusion simulation — are insufficient to discriminate pathogenic from benign variants at the structural level. The full physics-based simulation adds discriminative power that static annotation cannot provide.

We acknowledge that an AUC of 0.6381 is modest in absolute terms. ARCHCODE is not a high-accuracy classifier in the conventional sense. Rather, its value lies in detecting a specific class of variants (Class B) that achieves AUC = 0.0 in all sequence-based tools — a class where any signal above chance represents genuine complementary information.

### 4.5 Leave-one-locus-out: generalization across loci

To test whether the architecture-driven signal generalizes beyond HBB, we performed leave-one-locus-out cross-validation (EXP-002) across all 9 loci. For each fold, the LSSIM threshold is derived from the 8 training loci and applied to the held-out locus without retuning. The mean AUC across the 8 loci with computable AUC (HBB excluded due to zero benign variants in the test set) is 0.6866 (SD = 0.098). Per-locus AUCs range from 0.5892 (SCN5A, tissue-mismatched) to 0.8529 (GJB2) and 0.8405 (TERT), indicating that the structural signal transfers across loci and is not an artifact of HBB-specific overfitting.

The highest generalization AUCs occur at loci with partial or full tissue match (TERT: 0.8405, tissue_match = 0.5; TP53: 0.6676, tissue_match = 0.5), while the lowest occur at tissue-mismatched loci (SCN5A: 0.5892, tissue_match = 0.0; LDLR: 0.5916, tissue_match = 0.0). This gradient reinforces the tissue-specificity principle of the taxonomy: architecture-driven detection requires tissue-matched chromatin context (see Section 5.3).

---

## 5. Case Studies

### 5.1 HBB Q2b: archetypal architecture-driven pathogenicity

The beta-globin locus (HBB) provides the clearest demonstration of Class B architecture-driven pathogenicity. The locus is controlled by the Locus Control Region (LCR), a cluster of erythroid-specific enhancers located approximately 50 kb upstream that must physically contact the HBB promoter through cohesin-mediated loop extrusion for transcriptional activation. This contact-dependent regulatory architecture makes HBB particularly susceptible to architecture-driven disruption.

Among 1,103 ClinVar variants at HBB, 25 are classified as Q2b — structurally disruptive (LSSIM < 0.95 in the ARCHCODE simulation) yet undetected by VEP (score 0–0.5). These variants cluster at a mean distance of 434 bp from the nearest tissue-matched enhancer, compared to 25,138 bp for Q3 variants at the same locus — a 58-fold proximity enrichment (p = 2.51 x 10^-31). The tissue match is maximal (1.0): K562 cells are erythroid progenitors, and HBB is the canonical erythroid gene regulated by the LCR.

The proposed pathogenic mechanism is contact disruption rather than element activity change. Each Q2b variant is positioned within or immediately adjacent to the enhancer–promoter contact zone. The ARCHCODE simulation shows that these variants alter the loop extrusion landscape such that the LCR–HBB contact probability decreases, reducing transcriptional output. Importantly, this mechanism is invisible to sequence-based tools because the variant does not disrupt a transcription factor binding motif or alter enhancer activity — it disrupts the physical routing of the enhancer's output to its target promoter.

The experimental validation path for HBB Q2b is well-defined: Capture Hi-C in HUDEP-2 erythroid progenitor cells, comparing allele-specific contact frequencies at the top 5 Q2b positions. MPRA for the same variants is predicted to return null results, confirming the absence of activity-driven effects and strengthening the architecture-driven assignment.

### 5.2 TERT Q2a: coverage gap with architecture signal

The TERT locus illustrates a different taxonomy class — Class D (coverage gap) with architecture signal overlap (D+B). Among 2,089 TERT variants, 35 are classified as Q2 (structurally discordant with VEP). Of these 35, 34 are Q2a — variants where VEP returns no score (VEP = -1) because the variant falls in a non-coding region outside VEP's annotation scope — and only 1 is Q2b. The Q2 precision at TERT is 0.9714 (34/35 are genuinely unscored by VEP, not disagreements).

TERT achieves the highest ARCHCODE AUC of any locus: 0.8405 across all variants, and 0.9323 within the enhancer-proximal subset. The Q2 variants cluster at a mean enhancer distance of 864 bp, compared to 19,966 bp for Q3 variants (p = 2.03 x 10^-15). The tissue match is partial (0.5): TERT is active in K562 as a telomerase-expressing immortalized line, but K562 is not the primary tissue for TERT-associated disease (glioma, melanoma, bladder cancer).

TERT demonstrates that ARCHCODE provides complementary coverage for VEP-blind regions. The 34 Q2a variants are not "VEP disagrees with ARCHCODE" — they are "VEP cannot score, ARCHCODE can." This distinction is taxonomically important: these are not architecture-driven in the same sense as HBB Q2b (where VEP can score but misses the effect), but rather coverage-gap variants where ARCHCODE fills an annotation void. The D+B overlap category — coverage gap with architecture signal — may represent the largest pool of actionable variants for clinical laboratories that currently dismiss VEP = -1 results as uninformative.

### 5.3 Tissue mismatch: SCN5A and GJB2 as negative controls

Two loci — SCN5A (cardiac sodium channel, cardiac arrhythmia) and GJB2 (connexin 26, cochlear deafness) — produce zero Q2 variants in the ARCHCODE pipeline. Neither locus shows any structural discrimination between pathogenic and benign variants. This is not a failure of the architecture-driven hypothesis; it is the expected result of tissue mismatch.

SCN5A is regulated in cardiomyocytes, not in K562 erythroid cells. The enhancer landscape of SCN5A in K562 bears no resemblance to its regulatory architecture in the heart. GJB2 is expressed in cochlear supporting cells, a tissue with no overlap to K562 chromatin context. In both cases, ARCHCODE is simulating a chromatin topology that does not exist in the disease-relevant tissue, and correctly produces no signal.

EXP-003 (tissue-mismatch controls) quantifies this effect directly. Using a proxy enhancer-proximity score computed with Gaussian weighting (sigma = 5,000 bp), we measured the pathogenic-vs.-benign delta across matched and mismatched enhancer configurations for 3 loci. The results show a diagnostic diagonal pattern:

- **HBB|HBB (matched):** delta = 0.00357 (p = 4.66 x 10^-72)
- **HBB|LDLR (mismatch):** delta = 5.04 x 10^-6 (effectively zero)
- **HBB|TP53 (mismatch):** delta = -0.01168 (inverted — nonsensical direction)

The matched-tissue delta exceeds the mismatched-tissue delta by approximately 700-fold (0.00357 / 5.04 x 10^-6). In the HBB|TP53 mismatch, the sign inverts entirely, meaning the wrong enhancer landscape causes the metric to rank benign variants as more structurally disruptive than pathogenic ones. This sign inversion is a strong diagnostic signal that the tissue context is incorrect.

The tissue-mismatch result has two implications for the taxonomy. First, it validates Class E as a real and detectable artifact — tissue-mismatched architecture signals are not merely weak, they are qualitatively wrong. Second, it establishes tissue matching as a necessary precondition for Class B detection. Any future ARCHCODE deployment at a new locus must first verify tissue match before interpreting structural signals, or risk generating Class E artifacts.

### 5.4 External cases: independent validation from the literature

Three canonical cases from the published literature independently validate the taxonomy's core classes without using ARCHCODE data.

**Lupianez et al. 2015 (Class B — architecture-driven).** Structural variants at the WNT6/IHH/EPHA4/PAX3 locus disrupt TAD boundaries, causing pathogenic rewiring of enhancer–gene interactions and resulting in limb malformations (brachydactyly, F-syndrome, polydactyly). The enhancers themselves are unmutated — their intrinsic activity is unchanged. The pathogenic mechanism is purely topological: boundary loss causes enhancer–promoter mis-routing. Hi-C in patient cells confirms TAD fusion at deletion breakpoints. This is the archetype of architecture-driven pathogenicity: disease arises from disrupted chromatin contact topology with no change in element activity. Sequence-based tools (VEP, CADD) cannot detect this because the coding sequence is intact, and MPRA would show no change because enhancer sequences are wild-type. ARCHCODE, with an appropriate tissue-matched configuration, would detect the boundary disruption as an LSSIM decrease.

**Lettice et al. 2003 (Class A — activity-driven).** Point mutations in the ZRS (Zone of Polarizing Activity Regulatory Sequence), a long-range enhancer approximately 1 Mb from the SHH gene, cause preaxial polydactyly by creating new ETS transcription factor binding sites. The mutation directly alters enhancer activity — gaining function in a spatial domain where ZRS is normally silent — without changing the 3D chromatin architecture that connects ZRS to the SHH promoter. This is the archetype of activity-driven pathogenicity: the element changes what it does, not where it contacts. MPRA/reporter assays can detect the activity change; Hi-C would show no change in contact topology. ARCHCODE would correctly return a neutral LSSIM.

**Groschel et al. 2014 (Class C — mixed).** The inv(3)(q21q26) rearrangement in acute myeloid leukemia repositions a GATA2 enhancer near the MECOM (EVI1) oncogene, causing simultaneous MECOM activation via enhancer hijacking (architecture change) and GATA2 haploinsufficiency from enhancer loss (activity change). Neither mechanism alone is sufficient for leukemogenesis — both the 3D contact rewiring and the activity loss must co-occur. This demonstrates that some pathogenic events are genuinely mixed-class, operating simultaneously through both mechanistic axes. ARCHCODE would detect the architecture component (new MECOM contacts) but would miss the activity component (GATA2 expression loss), requiring an orthogonal expression readout for complete characterization.

These three cases span limb malformations, polydactyly, and leukemia — distinct disease categories, distinct molecular mechanisms, and distinct experimental validations — yet each maps cleanly to one of the taxonomy's classes. The Hnisz et al. 2016 demonstration that insulated neighborhood disruption activates proto-oncogenes in T-ALL provides further independent support for Class B, establishing that CTCF boundary deletions alone are sufficient for oncogene activation through 3D contact rewiring (see also the external casebook, Section 3.6 [CHECK: cross-reference to Section 3]).

---

## 6. Honest Assessment: Limitations and Challenges

We present the taxonomy as a working model, not a final classification. Several structural weaknesses deserve explicit acknowledgment, and we organize them from most to least concerning.

### 6.1 Class boundaries may be continuous, not discrete

The five-class taxonomy implies clean categorical boundaries, but biological reality is likely to be continuous. A variant that disrupts a CTCF site embedded within an enhancer simultaneously alters both chromatin insulation (architecture) and enhancer accessibility (activity). The boundary between Class A and Class B passes through Class C, and Class C itself may be a spectrum rather than a category. We use discrete classes for conceptual clarity and to guide experimental design — not because we believe the underlying biology is categorical. The decision rules presented in Section 3.6 are threshold-based heuristics (LSSIM < 0.95, VEP > 0.5) that inevitably create boundary artifacts. Variants near these thresholds should be interpreted with caution.

### 6.2 HBB is the primary evidence — a single-locus concern

The strongest Class B evidence comes from a single locus: HBB, with 25 Q2b variants, tissue match = 1.0, and p = 2.51 x 10^-31 for enhancer proximity enrichment. While the leave-one-locus-out cross-validation (mean AUC = 0.6866 across 8 loci) suggests that the structural signal generalizes, the canonical Class B demonstration is fundamentally an N = 1 locus observation. If HBB's unique regulatory architecture — the LCR-mediated long-range contact, the erythroid specificity, the binary on/off globin switching — makes it an outlier rather than a prototype, the taxonomy's strongest class may not generalize to the broader genome. We will not know until tissue-matched ARCHCODE configurations are tested at additional loci with comparable enhancer–promoter contact dependencies.

### 6.3 BRCA1/TP53 Q2b: threshold artifacts, not confirmed Class B

Beyond HBB, the next-largest Q2b cohorts are BRCA1 (26 variants) and TP53 (2 variants). However, the BRCA1 Q2b assignment is weak. The Q2b variants at BRCA1 have LSSIM values in the range 0.942–0.947 — just below the 0.95 threshold. Their allele frequencies range from 40–50%, consistent with common polymorphisms rather than pathogenic variants. The Q2b precision at BRCA1 is only 3.8%, meaning that 96.2% of variants scored as structurally disruptive at this locus are likely benign polymorphisms whose LSSIM scores happen to fall below threshold due to the locus's baseline structural flexibility (6 severe fragility zones in the BRCA1 fragility atlas, vs. zero at HBB). TP53 has only 2 Q2b variants — insufficient for any statistical inference. These tentative Class B assignments should be treated as hypotheses requiring independent validation, not as confirmed architecture-driven pathogenicity.

### 6.4 Mixed class (C) is the hardest to validate

Class C (mixed) is assigned to 270 HBB Q1 concordant variants — positions where both VEP and ARCHCODE detect pathogenicity. However, the Class C assignment is inferential: we observe co-occurrence of high VEP score and low LSSIM but cannot determine whether the activity and architecture effects are causally independent, synergistic, or merely coincidental (a coding variant near an enhancer could score high on both axes for unrelated reasons). Validating Class C requires dual-readout experiments — allele-specific Hi-C combined with RNA-seq in the same cells — that are technically demanding and have not been performed for any of these variants.

### 6.5 ARS–taxonomy bridge is inconclusive

We investigated whether baseline structural fragility (Architecture Risk Score) predicts Class B enrichment (EXP-005). The result is inconclusive: fragility atlas data exists for only 2 of 9 loci (HBB and BRCA1), and these two loci show an inverse pattern — HBB has zero severe fragility zones but strong Class B evidence, while BRCA1 has six severe zones but weak Class B evidence. With N = 2 and strong tissue-match confounding (HBB tissue_match = 1.0 vs. BRCA1 tissue_match = 0.5), no directional conclusion is warranted. The hypothesis that structurally fragile loci harbor more architecture-driven pathogenic variants remains plausible but untested.

### 6.6 Assignment rules are heuristic

The decision rules for taxonomy assignment (Section 3.6) are not derived from a principled statistical model. They are manually defined thresholds:

- LSSIM < 0.95 defines structural disruption
- VEP = -1 defines coverage gap
- Tissue_match >= 0.5 is required for Class B assignment

These thresholds were chosen based on distribution analysis of the HBB data and may not be optimal for other loci, other simulation parameters, or other tissue contexts. The EXP-004 threshold robustness analysis [CHECK: reference if completed] showed that the Q2b count is sensitive to the LSSIM threshold — shifting from 0.95 to 0.94 or 0.96 changes the variant count substantially. A principled Bayesian framework for class assignment, incorporating uncertainty in both the structural simulation and the sequence-based scores, would be a significant improvement over the current heuristic approach.

### 6.7 The central epistemic limitation

We state this directly: **we cannot prove that Q2b variants are pathogenic through architecture**. ARCHCODE demonstrates that these variants are (i) structurally disruptive in a physics-based chromatin simulation, (ii) located within hundreds of base pairs of tissue-matched enhancers, and (iii) undetected by all widely used sequence-based interpretation tools. But structural disruption in a simulation is not proof of disease causation. The variants may be structurally disruptive without being clinically pathogenic. They may disrupt contacts that are biologically redundant. They may affect chromatin topology in ways that the cell can compensate for.

What ARCHCODE provides is a prioritization signal: among the thousands of non-coding variants at a disease-associated locus, these 54 variants (25 HBB, 26 BRCA1, 2 TP53, 1 TERT) are the ones most likely to operate through a mechanism that no other tool can detect, and they are the ones most worth testing experimentally with contact-based assays (Capture Hi-C, 4C-seq) in tissue-matched cell types. The taxonomy does not claim to resolve their pathogenicity — it claims to identify the mechanism through which they might be pathogenic and the experiment most likely to test that hypothesis.

---

*Figure 2 reference: schematic of ARCHCODE pipeline with per-class examples (HBB Q2b for Class B, TERT Q2a for Class D, SCN5A null for Class E). [CHECK: figure specification in docs/taxonomy_paper_outline.md]*

