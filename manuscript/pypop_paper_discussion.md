# Population Stratification Detects Misclassified Pathogenic Variants in HBB Locus

## DISCUSSION

### Principal Findings

We demonstrate that population stratification analysis, adapted from the PyPop immunogenetics framework (Lancaster et al., 2024), detects false positives in structural variant prediction that are invisible to sequence-based pathogenicity tools. Among 12 HBB promoter variants predicted to cause 3D chromatin disruption by ARCHCODE, **16.7% (2/12) were population-specific benign polymorphisms** enriched in East Asian ancestry — a population where beta-thalassemia is NOT prevalent. These false positives satisfied ACMG BS1 criteria (allele frequency 19-46× higher than expected for a pathogenic variant) and were correctly classified as MODIFIER (low impact) by VEP, demonstrating that **structural and sequence-based predictions capture orthogonal information**.

The key insight is that **cross-population consistency serves as a functional validation** for structural predictions. Truly pathogenic variants under purifying selection should be rare or absent across ALL populations. Population-specific presence, especially in populations where the disease is rare, indicates benign variation or population-specific adaptation rather than pathogenicity.

### Comparison with Existing Approaches

Current regulatory variant interpretation relies primarily on sequence conservation (PhyloP, GERP++) and functional genomics (ENCODE annotations, eQTL databases). These approaches miss structural disruptions in non-conserved enhancers and cannot distinguish pathogenic from benign variants with similar epigenetic profiles. Structural prediction tools (ARCHCODE, Akita, Enformer) address this gap but lack validation frameworks.

Our population genetics approach complements both strategies:
- **Sequence-based tools** detect coding/splicing pathogenicity but miss regulatory disruption
- **Structural tools** detect chromatin contact disruption but have high false positive rates (16.7% in this study)
- **Population stratification** validates structural predictions by leveraging disease epidemiology

The **integration of all three** maximizes accuracy: sequence annotation filters out obvious low-impact variants, structural prediction identifies candidates for deeper investigation, and population genetics validates or refutes pathogenicity claims.

### Limitations

1. **Small sample size:** 12 variants from a single locus (HBB promoter). False positive rate CI [4.7%, 42.8%] is wide. Multi-locus validation (BRCA1, CFTR, TP53) needed to confirm generalizability.

2. **gnomAD coverage:** 5/12 variants not found in gnomAD v4 (807K individuals). These may be extremely rare true pathogenic variants or technical artifacts (sequencing errors, alignment issues). Cannot validate variants absent from population databases.

3. **Disease-specific epidemiology required:** This approach depends on well-characterized disease prevalence by population. Applicable to Mendelian disorders with established epidemiology (thalassemias, cystic fibrosis, sickle cell) but not to complex or polygenic traits.

4. **Population stratification assumptions:** Assumes gnomAD population labels accurately reflect genetic ancestry and that modern population structure reflects historical selection pressures. Population admixture and recent migration may confound interpretation.

### Clinical Implications

The 2 FALSE PEARLS identified here (VCV000015471, VCV000015466) are currently annotated as **Benign** in ClinVar — our population analysis provides additional evidence supporting this classification. For clinical laboratories interpreting VUS in HBB, our findings suggest:

- **Population-aware interpretation:** A variant present at AF > 0.0001 in a population where the disease is rare (e.g., East Asian for beta-thal) should trigger BS1 application
- **Structural prediction with caution:** ARCHCODE and similar tools have value for hypothesis generation but require orthogonal validation (population genetics, functional assays, family segregation)
- **ClinVar submissions:** Population stratification data should be included in evidence packages for regulatory variant reclassifications

### Future Directions

1. **Multi-locus expansion:** Apply PyPop population validation to CFTR (cystic fibrosis), BRCA1/BRCA2 (breast cancer), and TP53 (Li-Fraumeni) to estimate locus-independent false positive rates

2. **Automated pipeline:** Integrate gnomAD population query into ARCHCODE workflow to flag high-AF population-specific predictions in real-time

3. **Bayesian integration:** Combine structural prediction scores (LSSIM), sequence-based scores (CADD), and population AF into a unified Bayesian pathogenicity classifier

4. **Experimental validation:** Hi-C or CRISPR perturbation experiments on FALSE PEARLS (chr11:5227099 T>C, chr11:5227102 T>C) to confirm lack of structural disruption

### Conclusion

Population stratification analysis, adapted from PyPop immunogenetics methodology, provides a scalable validation framework for structural variant predictions in regulatory regions. By leveraging disease epidemiology and cross-population allele frequency consistency, this approach detects false positives invisible to sequence-based pathogenicity tools. The 16.7% false positive rate observed in HBB promoter predictions underscores the necessity of multi-modal variant interpretation — integrating sequence annotation, structural modeling, and population genetics — for accurate clinical variant classification.

---

**Word count:** 646 words  
**Status:** COMPLETE
