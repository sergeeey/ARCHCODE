Sequence-based variant predictors do not model 3D chromatin
topology, leaving enhancer-proximal variants without
structural interpretation.

We analyzed 32,201 ClinVar variants across nine disease-associated
loci and found that enhancer-proximal variants show tissue-dependent
local contact disruption --- strongest in erythroid-matched HBB
(ΔLSSIM = 0.111), attenuated in expressed-but-mismatched TERT
(Δ = 0.019), and absent in tissue-mismatched negative controls
SCN5A and GJB2 (Δ ≤ 0.006).

In HBB, this approach identified 27 enhancer-proximal candidates
(95 kb atlas; 20 at stringent 30 kb threshold) absent from nine
orthogonal annotations including SpliceAI, MPRA, and gnomAD v4.

Predicted contact maps showed locus-dependent agreement with
experimental Hi-C (r = 0.29--0.59, K562 and tissue-matched
cell lines).

Contact disruption was quantified using Local SSIM on analytical
mean-field loop extrusion contact maps comparing wild-type and
variant-specific chromatin occupancy profiles.

ARCHCODE functions as a structural prioritization framework, not an independent pathogenicity predictor. Within functional categories, positional discrimination is minimal (position-only AUC = 0.551); the overall AUC of 0.977 reflects category-level structural scaling rather than independent variant-level prediction. All candidate variants require experimental validation via Capture Hi-C and RT-PCR before any clinical interpretation. The primary utility is identifying enhancer-proximal structural hypotheses invisible to sequence-based tools.

#strong[Keywords:] chromatin architecture, enhancer-promoter regulation,
noncoding variants, ClinVar, tissue specificity, 3D genome,
β-thalassemia, HBB, structural disruption, loop extrusion
