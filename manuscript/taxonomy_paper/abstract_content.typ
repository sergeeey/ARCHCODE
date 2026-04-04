// CANON_TIER: PUBLIC_CANONICAL
// STATUS: current public canonical manuscript entry surface
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
clinically important genomic loci using ARCHCODE, a loop-extrusion-based structural mechanism
discovery engine integrated with VEP, CADD, MPRA cross-validation, and orthogonal chromatin
benchmarking. We identify 25 high-confidence architecture-driven variants (Class B) at the
tissue-matched HBB locus and 29 additional exploratory candidates at partially matched loci.
At HBB, the high-confidence Class B set clusters within 434 bp of tissue-matched enhancers (p =
$2.51 times 10^(-31)$), is not isolated by MPRA score (p = 0.91), and shows substantially larger
AlphaGenome CAGE disruption than pathogenic non-pearls or benign controls. An additional 207
coverage-gap variants (Class D) are unscored by VEP but detectable by structural simulation.
Together, architecture-driven and coverage-gap variants account for 261 structural blind spots,
of which 79.3% reflect tool absence (Class D) and 20.7% reflect mechanistic orthogonality
(Class B). Tissue-mismatch analysis demonstrates that architecture-driven signal collapses
outside matched context, establishing tissue specificity as a necessary condition for confident
Class B interpretation.

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
