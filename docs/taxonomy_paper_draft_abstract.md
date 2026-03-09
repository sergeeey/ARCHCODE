# Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots

---

## Abstract

**Background.**
Current variant interpretation tools assign pathogenicity along a single axis — typically sequence conservation or predicted functional impact. This conflation obscures mechanistically distinct classes of regulatory effect that require different computational approaches and different experimental validations. Whether regulatory pathogenicity decomposes into separable mechanistic axes, and how large the resulting blind spots are, has not been systematically assessed.

**Results.**
We propose a five-class taxonomy of regulatory pathogenicity: (A) activity-driven, where variants alter enhancer or promoter function detectable by reporter assays; (B) architecture-driven, where variants disrupt 3D chromatin contact topology detectable by structural simulation; (C) mixed, combining both mechanisms; (D) coverage gap, where current tools lack scoring capability; and (E) tissue-mismatch artifact, where apparent signals reflect incorrect tissue context. We classify 21 cases encompassing 30,318 ClinVar variants across 9 clinically important genomic loci using ARCHCODE, a loop-extrusion-based structural pathogenicity engine, integrated with VEP, CADD, MPRA cross-validation, and CRISPRi benchmarking. We show that 54 architecture-driven variants (Class B) are systematically missed by sequence-based tools: NMI(ARCHCODE, VEP) = 0.101; NMI(ARCHCODE, CADD) = 0.024. These variants cluster within 434 bp of tissue-matched enhancers (p = 2.51 × 10⁻³¹), 58-fold closer than activity-driven variants (25,138 bp), and return null results in both MPRA and CRISPRi screens — consistent with a contact-disruption rather than element-activity mechanism. An additional 207 coverage-gap variants (Class D) are unscored by VEP but detectable by structural simulation. Together, architecture-driven and coverage-gap variants account for 261 structural blind spots, of which 79.3% reflect tool absence (Class D) and 20.7% reflect true mechanistic orthogonality (Class B). Tissue-mismatch analysis (EXP-003) demonstrates that architecture-driven signal collapses by 700-fold in mismatched tissue (matched delta = 0.00357 vs. mismatch delta = 5.04 × 10⁻⁶), establishing tissue context as a necessary condition for Class B detection. Eight canonical cases from the literature — including TAD boundary disruption (Lupiáñez et al. 2015), insulated neighborhood disruption (Hnisz et al. 2016), and enhancer hijacking (Gröschel et al. 2014) — independently validate the taxonomy across limb malformations, leukemia, and medulloblastoma.

**Conclusions.**
Single-axis scoring is an inadequate abstraction for regulatory variant interpretation. Mechanistic decomposition reveals that architecture-driven pathogenicity — representing 20.7% of structural blind spots — requires dedicated 3D chromatin modeling that no current sequence-based tool provides. We propose that variant interpretation frameworks should explicitly assign mechanistic class before scoring, enabling targeted experimental validation and reducing systematic blind spots in clinical genetics.

**Word count:** ~310 [CHECK: trim to ~250 if targeting journals with strict limits; current length appropriate for bioRxiv/Genome Research]

---

## Significance Statement

Genetic testing for non-coding variants relies on tools that score pathogenicity along a single axis — sequence conservation or predicted regulatory disruption. We show that regulatory pathogenicity is mechanistically heterogeneous, decomposing into at least five distinct classes that require different tools and different experiments. One class — architecture-driven pathogenicity, where variants disrupt 3D chromatin contacts rather than regulatory element activity — is invisible to all widely used sequence-based interpretation tools (VEP, CADD, MPRA). Across 9 clinically important loci and 30,318 variants, we identify 261 variants in systematic blind spots, including 54 that can only be detected through chromatin structure simulation. Adopting mechanism-first classification before pathogenicity scoring could reduce false-negative rates and direct experimental resources to the assay most likely to detect each variant's effect.

**Word count:** ~120 [CHECK: trim to ~100 if journal requires]

---

## Keywords

regulatory variant interpretation; chromatin architecture; loop extrusion; variant pathogenicity taxonomy; non-coding variants; 3D genome; enhancer-promoter contacts; tissue specificity; blind spot analysis; mechanistic decomposition

---

## One-Paragraph Summary (for collaborators and talks)

We propose that regulatory pathogenicity is not a single-axis phenomenon but decomposes into at least five mechanistic classes: activity-driven (enhancer/promoter function change), architecture-driven (3D chromatin contact disruption), mixed, coverage gap, and tissue-mismatch artifact. Analyzing 30,318 ClinVar variants across 9 loci, we find 54 architecture-driven variants invisible to VEP, CADD, and MPRA (NMI < 0.1), clustering within 434 bp of enhancers (p = 2.51 × 10⁻³¹), plus 207 coverage-gap variants unscored by existing tools. We argue that variant interpretation should assign mechanistic class before computing pathogenicity scores, matching each variant to the tool and experiment most likely to detect its effect.

**Word count:** ~110 [CHECK: trim to ~80 if needed]
