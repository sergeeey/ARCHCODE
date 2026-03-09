Sequence-based variant predictors do not model 3D chromatin
topology, leaving enhancer-proximal variants without
structural interpretation.

We analyzed 32,201 ClinVar variants across nine disease-associated
loci and found that enhancer-proximal variants show tissue-dependent
local contact disruption --- strongest in erythroid-matched HBB
(ΔLSSIM = 0.111), attenuated in expressed-but-mismatched TERT
(Δ = 0.019), and absent in tissue-mismatched negative controls
SCN5A and GJB2 (Δ ≤ 0.006).

Cross-tabulation against VEP/CADD sequence annotations reveals that
apparent discordance decomposes into coverage gaps (Q2a, 79.3% of
discordant variants) where VEP lacks annotation, and true structural
blind spots (Q2b, 20.7%) where VEP explicitly scores low impact but
the structural model detects disruption. Q2b variants cluster 58-fold
closer to enhancers than sequence-channel variants
(434 bp vs 25,138 bp; p = 2.5 × 10#super[−31]) and show
tissue-dependent enrichment (Spearman ρ = 0.84, p = 0.005).

In HBB, 25 Q2b variants --- all ClinVar pathogenic/likely pathogenic --- are absent from
nine orthogonal annotations including SpliceAI, MPRA, and gnomAD v4.
TERT independently replicates the enhancer-proximity signal (23-fold
enrichment, p = 2 × 10#super[−15]) but through coverage gaps (97% Q2a),
not mechanistic disagreement.

Predicted contact maps showed locus-dependent agreement with
experimental Hi-C (r = 0.28--0.59) and cross-species conservation
(human--mouse r = 0.82, 17/17 directional).

ARCHCODE functions as a structural prioritization engine, not an
independent pathogenicity predictor. Within functional categories,
positional discrimination is null (mean within-category AUC = 0.48);
the overall AUC of 0.977 reflects category-level structural scaling.
The primary utility is identifying which enhancer-proximal variants
to test first via Capture Hi-C and RT-PCR --- a complementary axis
invisible to sequence-based tools.

#strong[Keywords:] chromatin architecture, enhancer-promoter regulation,
noncoding variants, ClinVar, tissue specificity, 3D genome,
β-thalassemia, HBB, structural disruption, loop extrusion
