# Sections 7–9: Experimental Implications, Framework Implications, Discussion

---

## 7. Experimental Implications

The five-class taxonomy provides a direct mapping from mechanistic class to validating experiment. Rather than applying a single assay to all regulatory variants, mechanism-first classification enables targeted experimental design that maximizes the probability of detecting each variant's specific effect.

### Class-specific validation strategies

**Class A (Activity-Driven).** Variants that alter intrinsic regulatory element function are validated by reporter assays. MPRA and STARR-seq directly measure allele-specific enhancer or promoter activity in a high-throughput format. Because these variants operate through sequence-level mechanisms — TF binding disruption, motif alteration, accessibility changes — plasmid-based assays that decouple the element from its 3D genomic context remain informative. CRISPRi/a at the endogenous locus with RNA-seq readout provides orthogonal confirmation at lower throughput.

**Class B (Architecture-Driven).** Variants that disrupt chromatin contact topology cannot be detected by reporter assays, which by design remove 3D context. The appropriate validation is Capture Hi-C or 4C-seq in the disease-relevant cell type, measuring allele-specific contact frequency between the affected enhancer and its target promoter. For the 25 HBB Q2b variants, this requires HUDEP-2 cells (an erythroid progenitor line that recapitulates adult beta-globin regulation) rather than K562 (which expresses fetal gamma-globin). CRISPR base editing at Q2b positions followed by contact mapping would provide the strongest causal evidence.

**Class C (Mixed).** Variants affecting both activity and architecture require dual-readout experiments: simultaneous RNA-seq and contact assay (e.g., HiChIP or PLAC-seq) in the same cell population. Allele-specific Hi-C in heterozygous patient-derived cells can separate the two axes — measuring both expression change and contact change from the same allele.

**Class D (Coverage Gap).** These 207 variants are unscored by VEP (VEP = −1), making any functional assay informative for establishing a baseline. RNA-seq for splicing effects, ATAC-seq for accessibility changes, and MPRA for activity effects would all reduce the current blind spot. The priority is coverage expansion: even negative results reclassify these variants from "unknown" to "tested."

**Class E (Tissue-Mismatch Artifact).** Validation requires running the same variant through matched-tissue and mismatched-tissue assays in parallel. For loci such as SCN5A (cardiac) and GJB2 (cochlear), ARCHCODE configurations built from iPSC-derived cardiomyocytes or cochlear organoids would determine whether architecture-driven pathogenicity exists in the native tissue context that K562-based analysis cannot detect.

### Priority experiments

We propose five priority experiments based on expected information gain (Table 1).

**Table 1. Priority experiments by taxonomy class.**

| Priority | Class | Experiment | Target | Cell Type | Expected Result | Estimated Time | Estimated Cost |
|:--------:|:-----:|:-----------|:-------|:----------|:----------------|:--------------:|:--------------:|
| 1 | B | Capture Hi-C | Top 5 HBB Q2b positions | HUDEP-2 | Reduced LCR–HBB contact frequency at variant alleles | 3–4 months | $15–25K |
| 2 | B | MPRA for Q2b | Same 5 HBB Q2b positions | K562 | Null (confirms architecture, not activity, mechanism) | 2–3 months | $8–12K |
| 3 | D | Targeted RNA-seq | 34 TERT Q2a variants | HEK293T / U2OS | Splice or expression effects for VEP-blind variants | 2 months | $5–8K |
| 4 | E | Matched-tissue ARCHCODE | SCN5A full locus | iPSC-cardiomyocytes | Architecture-driven signal emerges in matched tissue | 4–6 months | $20–30K |
| 5 | C | HiChIP + RNA-seq | HBB Q1 concordant variants | HUDEP-2 | Dual disruption: expression change AND contact change | 4–5 months | $20–30K |

The expected MPRA null for Q2b variants (Priority 2) is itself informative: a negative result in a reporter assay, combined with a positive result in a contact assay, provides the strongest evidence for architecture-driven classification. This "null as evidence" logic inverts the standard interpretation of MPRA screens, where null results are typically discarded as uninformative.

---

## 8. Product and Framework Implications

### Mechanism-first interpretation

The central recommendation of this taxonomy is operational: clinical variant interpretation should assign mechanistic class before computing pathogenicity scores. Current workflows apply VEP or CADD as universal first-pass filters, implicitly assuming that all regulatory pathogenicity is activity-driven. This assumption produces systematic false negatives for the 54 architecture-driven variants (Class B) and 207 coverage-gap variants (Class D) identified in our analysis. A mechanism-first workflow would route each variant to the tool most likely to detect its specific effect class before scoring.

### Multi-modal interpretation engines

No single tool covers all five classes. VEP and CADD address Class A but are blind to Class B. ARCHCODE addresses Class B but is blind to Class A. MPRA validates Class A but cannot detect Class B by design. This complementarity argues for multi-modal interpretation engines that integrate sequence-level predictions (Enformer, Sei, SpliceAI), structural predictions (ARCHCODE, loop extrusion models), and activity measurements (MPRA, CRISPRi) into a unified variant report. AlphaGenome (Avsec et al. 2026) represents a step toward multi-output prediction, but its outputs still require an interpretive layer that maps predicted effects to mechanistic classes. The taxonomy proposed here provides that layer.

### ARCHCODE as module, not standalone

We explicitly position ARCHCODE as a Class B detection module within a multi-tool pipeline, not as a standalone variant interpreter. ARCHCODE contributes the architecture axis — chromatin contact disruption prediction via loop extrusion simulation — and should be combined with sequence-based tools that cover the activity axis. The Architecture Risk Score (ARS), which quantifies locus-level structural vulnerability, functions as a risk stratification layer within this taxonomy: loci with high ARS are expected to enrich for Class B variants that require structural validation.

### AI-assisted hypothesis generation

The taxonomy enables a specific form of computational hypothesis generation: given a variant's genomic context (enhancer proximity, tissue expression, tool coverage), an automated system can classify its most likely mechanism and suggest the discriminating experiment. For example, a variant within 500 bp of a tissue-matched enhancer that scores low on VEP and CADD would be flagged as a Class B candidate, with Capture Hi-C in matched tissue recommended as the validating experiment. This "classify mechanism, then suggest experiment" pipeline could reduce the time from variant discovery to functional validation by directing experimental resources to the assay most likely to detect each variant's effect.

### Complementing, not replacing, existing tools

This framework does not argue that ARCHCODE should replace VEP, or that structural analysis is more important than sequence analysis. The claim is narrower and more specific: a systematic blind spot exists for architecture-driven regulatory pathogenicity, and dedicated 3D chromatin modeling is required to address it. VEP remains the appropriate first-pass tool for coding and splice-site variants. CADD remains valuable for genome-wide prioritization. The taxonomy adds a routing step — asking "which mechanism?" before "how pathogenic?" — that directs each variant to the appropriate tool.

---

## 9. Discussion

### Four claims, ranked by evidential strength

We organize the discussion around four claims in decreasing order of evidential support.

**Claim 1 (Strongest): Activity and architecture are orthogonal axes of regulatory pathogenicity.** The quantitative evidence is unambiguous. Normalized mutual information between ARCHCODE and VEP is 0.101; between ARCHCODE and CADD, 0.024. Correlation with MaveDB saturation genome editing is r = −0.045. These values are near the theoretical minimum, indicating that structural pathogenicity scores capture information almost entirely absent from sequence-based tools. This orthogonality is not a limitation of any individual tool — it reflects a genuine biological distinction between what a regulatory element does (activity) and where it contacts (architecture). The finding aligns with the growing consensus that 3D genome organization constitutes a distinct pathogenic dimension (Sreenivasan, Yumiceba & Spielmann 2025; Kim et al. 2024), and with empirical benchmarks showing that distal non-coding variants are the hardest class for sequence models to predict (Benegas, Eraslan & Song 2025).

**Claim 2 (Strong): Architecture-driven pathogenicity is invisible to current standard tools.** The 54 Class B variants identified across our 9 loci share a consistent signature: LSSIM < 0.95, VEP scores of 0–0.5, MPRA null, CRISPRi null, and clustering within 434 bp of tissue-matched enhancers (p = 2.51 × 10⁻³¹) — 58-fold closer than Class A variants (25,138 bp). This enrichment near enhancer-promoter contact zones, combined with absence of activity-based signal, is consistent with a contact-disruption mechanism. Tissue specificity provides additional support: architecture-driven signal correlates with tissue match at rho = 0.840 (p = 0.0046) and collapses 700-fold in mismatched tissue (matched delta = 0.00357 vs. mismatch delta = 5.04 × 10⁻⁶). However, we cannot confirm that these variants are pathogenic through architecture without experimental validation. What we can state is that they are structurally disruptive, tissue-specific, and systematically undetected by all widely used interpretation tools.

**Claim 3 (Moderate): A five-class taxonomy provides actionable organization of blind spots.** The taxonomy — activity-driven, architecture-driven, mixed, coverage gap, tissue-mismatch artifact — imposes interpretive structure on the heterogeneity of regulatory variant effects. Its practical value lies in mapping each class to a specific validating experiment and a specific computational tool (Table 1; tool-mechanism matrix). Whether five is the correct number of classes is less important than the principle that mechanism should be assigned before score. The boundaries between classes are likely continuous rather than discrete: some variants may operate partly through activity and partly through architecture, making Class C a continuum rather than a category. The taxonomy should be understood as a working framework subject to revision as experimental data accumulate, not as a final classification.

**Claim 4 (Emerging): Coverage gaps are larger than mechanistic disagreements.** Of 261 variants in structural blind spots, 207 (79.3%) are Class D — regions where VEP cannot assign a score — while 54 (20.7%) are Class B — regions where VEP assigns a score but misses the architecture axis. This ratio suggests that tool development should prioritize coverage expansion (scoring more variants in more genomic contexts) alongside mechanistic refinement (distinguishing activity from architecture). The 207 Class D variants represent a lower bound: they are the variants ARCHCODE can score that VEP cannot, but additional coverage gaps likely exist beyond ARCHCODE's 300 kb simulation windows and 9 configured loci.

### Relationship to existing frameworks

The taxonomy proposed here is complementary to, not competing with, the expression-outcome taxonomy of Cheng, Bohaczuk, and Stergachis (2024), who classify non-coding regulatory variants into loss-of-expression (LOE), modular loss-of-expression (mLOE), and gain-of-ectopic-expression (GOE) categories. Their classification operates on the consequence axis (what happens to gene expression), while ours operates on the mechanism axis (how the variant disrupts regulation). A variant classified as mLOE in their framework could be Class A (activity-driven mLOE, e.g., tissue-specific enhancer disruption) or Class B (architecture-driven mLOE, e.g., tissue-specific contact disruption) in ours. The two taxonomies are orthogonal and could be combined into a two-dimensional classification: mechanism × consequence.

AlphaGenome (Avsec et al. 2026) predicts thousands of functional genomic tracks from DNA sequence, representing the most comprehensive single-model approach to variant effect prediction. Its multi-output architecture implicitly acknowledges that regulatory effects are multi-dimensional. However, multi-output prediction does not eliminate the need for mechanistic interpretation. A model that predicts both chromatin accessibility change and contact frequency change still requires a framework to determine which output is most relevant for a given variant in a given tissue. The taxonomy proposed here provides that interpretive layer: Class A variants should be evaluated primarily on activity-track predictions; Class B variants on contact-track predictions; Class C on both.

### The path forward

The central argument of this paper is that variant interpretation should adopt a "mechanism-first, then score" workflow. Rather than computing a single pathogenicity score and asking whether it exceeds a threshold, interpreters should first ask: through which mechanism might this variant be pathogenic? The answer to that question determines which tool to apply, which experiment to run, and how to interpret the result. Architecture-driven pathogenicity — operating through 3D chromatin contact disruption rather than regulatory element activity change — is one such mechanism, currently invisible to standard interpretation tools and requiring dedicated structural modeling for detection. Our five-class taxonomy is an initial decomposition of this heterogeneity into actionable categories. Its validation will come not from computational benchmarks alone but from the experiments it directs: Capture Hi-C in HUDEP-2 for HBB Q2b, matched-tissue ARCHCODE for SCN5A and GJB2, dual-readout assays for mixed-class candidates. The framework succeeds if it accelerates the experimental characterization of regulatory variants by routing each variant to the assay most likely to detect its effect.
