// abstract_content.typ — включается в main.typ через #include
// Содержит Abstract + Keywords без обёртки в функцию

*Background.*
Current variant interpretation tools assign pathogenicity along a single axis --- typically
sequence conservation or predicted functional impact. This conflation obscures mechanistically
distinct classes of regulatory effect that require different computational approaches and
different experimental validations. Whether regulatory pathogenicity decomposes into separable
mechanistic axes, and how large the resulting blind spots are, has not been systematically
assessed.

*Results.*
We propose a five-class taxonomy of regulatory pathogenicity: (A) activity-driven, where
variants alter enhancer or promoter function detectable by reporter assays; (B)
architecture-driven, where variants disrupt 3D chromatin contact topology detectable by
structural simulation; (C) mixed, combining both mechanisms; (D) coverage gap, where current
tools lack scoring capability; and (E) tissue-mismatch artifact, where apparent signals reflect
incorrect tissue context. We classify 21 cases encompassing 30,318 ClinVar variants across 9
clinically important genomic loci using ARCHCODE, a loop-extrusion-based structural
pathogenicity engine, integrated with VEP, CADD, MPRA cross-validation, and CRISPRi
benchmarking. We show that 25 high-confidence and 29 candidate architecture-driven variants (Class B) are systematically missed by sequence-based tools: cross-locus weighted NMI(ARCHCODE, VEP) = 0.026; NMI at tissue-matched HBB = 0.495 (95% CI: 0.433--0.560). These
variants cluster within 434 bp of tissue-matched enhancers (p = $2.51 times 10^(-31)$), 58-fold
closer than activity-driven variants (25,138 bp), and return null results in both MPRA and
CRISPRi screens --- consistent with a contact-disruption rather than element-activity mechanism.
An additional 207 coverage-gap variants (Class D) are unscored by VEP but detectable by
structural simulation. Together, architecture-driven and coverage-gap variants account for 261
structural blind spots, of which 79.3% reflect tool absence (Class D) and 20.7% reflect true
mechanistic orthogonality (Class B). Tissue-mismatch analysis (EXP-003) demonstrates that
architecture-driven signal collapses by 700-fold in mismatched tissue (matched delta = 0.00357
vs. mismatch delta = $5.04 times 10^(-6)$), establishing tissue context as a necessary condition
for Class B detection. A seven-locus tissue-match panel using ENCODE ChIP-seq data reveals four
distinct outcome modes: positive amplification (SCN5A 1.37×, LDLR 1.43×), tail amplification
(MLH1 2.0×), null (BRCA1 0.99×), and reverse effect (CFTR 0.60×, TERT 0.39×, TP53 0.18×), with
reverse cases decomposing into overparameterization, enhancer loss, and enhancer dilution
sub-mechanisms. Eight canonical cases from the literature --- including TAD boundary
disruption (Lupiáñez et al. 2015), insulated neighborhood disruption (Hnisz et al. 2016), and
enhancer hijacking (Gröschel et al. 2014) --- independently validate the taxonomy across limb
malformations, leukemia, and medulloblastoma.

*Conclusions.*
Single-axis scoring is an inadequate abstraction for regulatory variant interpretation.
Mechanistic decomposition reveals that architecture-driven pathogenicity --- representing 20.7%
of structural blind spots --- requires dedicated 3D chromatin modeling that no current
sequence-based tool provides. We propose that variant interpretation frameworks should explicitly
assign mechanistic class before scoring, enabling targeted experimental validation and reducing
systematic blind spots in clinical genetics.

#v(0.6em)
*Keywords:* regulatory variant interpretation; chromatin architecture; loop extrusion; variant
pathogenicity taxonomy; non-coding variants; 3D genome; enhancer-promoter contacts; tissue
specificity; blind spot analysis; mechanistic decomposition
