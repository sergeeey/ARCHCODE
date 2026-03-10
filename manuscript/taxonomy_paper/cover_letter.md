# Cover Letter — bioRxiv Submission

**Manuscript:** "Regulatory Pathogenicity Is Mechanistically Heterogeneous: A Taxonomy of Activity-, Architecture-, and Coverage-Driven Blind Spots"

**Author:** Sergey V. Boyko, Independent Researcher, Almaty, Kazakhstan

**Subject Area:** Genomics

**Date:** March 10, 2026

---

Dear bioRxiv editors,

We submit for consideration as a new preprint a framework paper proposing that regulatory variant pathogenicity decomposes into five mechanistically distinct classes, each requiring different computational and experimental approaches.

**Key contributions:**

1. **Five-class taxonomy** of regulatory pathogenicity (activity-driven, architecture-driven, mixed, coverage gap, tissue-mismatch artifact), with formal definitions and decision rules.

2. **Systematic evidence** across 30,318 ClinVar variants at 9 genomic loci using ARCHCODE (loop-extrusion structural simulation), integrated with VEP, CADD, MPRA, and CRISPRi benchmarking. We identify 54 architecture-driven variants (Class B) systematically invisible to all sequence-based tools.

3. **Seven-locus tissue-match panel** using ENCODE ChIP-seq data revealing four distinct amplification modes: positive (SCN5A, LDLR), tail (MLH1), null (BRCA1), and reverse (CFTR, TERT, TP53). The reverse cases decompose into three sub-mechanisms: overparameterization, enhancer loss, and enhancer dilution.

4. **Tool-mechanism blind-spot matrix** demonstrating that VEP, CADD, SpliceAI, and MPRA are structurally blind to Class B variants, while ARCHCODE is blind to Class A — establishing genuine complementarity rather than redundancy.

**Significance:** Current variant interpretation frameworks implicitly assume a single pathogenicity axis. Our taxonomy reveals that 20.7% of structural blind spots reflect true mechanistic orthogonality (Class B) — variants that cannot be detected by any existing sequence-based approach. This has immediate implications for clinical genetics pipelines and experimental validation strategies.

**Data and code availability:** All source code, configurations, and analysis scripts are publicly available at https://github.com/sergeeey/ARCHCODE. All ENCODE accessions are documented with experiment IDs and peak file IDs. No experimental data were generated; all analyses use publicly available ClinVar, ENCODE, and published datasets.

**Conflicts of interest:** None.

**Related preprints:** A companion data paper describing the ARCHCODE computational engine has been submitted separately (BIORXIV/2026/710343).

Sincerely,
Sergey V. Boyko
