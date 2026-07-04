Dear Editors of Bioinformatics Advances,

We submit for your consideration "ARCHCODE: A Falsification-First Framework for Evaluating 3D Chromatin Signals in Variant Pathogenicity," a methods article describing a computational approach to identifying architecture-driven regulatory variants — a class of pathogenic mutations systematically invisible to current sequence-based tools.

**Why Bioinformatics Advances**

This manuscript presents a novel computational method for a problem of growing relevance to clinical bioinformatics: the interpretation of non-coding variants of uncertain significance (VUS). Our approach combines loop-extrusion-based structural simulation with AlphaGenome CAGE validation and falsification-first methodology, producing results that are both reproducible and honestly bounded. The falsification-first framing, explicit null-result reporting, and direct comparison with existing tools align with the journal's emphasis on rigorous, practically applicable computational methods.

**Summary of findings**

Current variant interpretation tools score pathogenicity along a single axis (sequence conservation or predicted functional impact), obscuring mechanistically distinct classes of regulatory effect. We demonstrate this fundamental limit across 26,225 ClinVar variants at 9 genomic loci, and propose a five-class taxonomy — activity-driven, architecture-driven, mixed, coverage gap, and tissue-mismatch — that assigns mechanistic class before computing pathogenicity scores.

Key results:

1. **Simpson's Paradox in variant scoring:** Variant category alone achieves pooled AUC = 0.791, but this masks within-category structural signal (intronic AUC = 0.640, synonymous AUC = 0.657). Standard pooled metrics systematically overstate tool performance.

2. **Architecture-driven variants (Class B) are orthogonal to all sequence-based tools:** NMI(ARCHCODE, VEP) = 0.495 at the tissue-matched HBB locus; cross-locus weighted average NMI = 0.026, confirming that structural simulation captures a mechanistic axis absent from sequence-based methods.

3. **AlphaGenome CAGE validation at HBB:** In the pre-registered pilot locus (HBB), pathogenic pearl variants reduce promoter accessibility 5.5-fold versus benign controls (Mann–Whitney p = 4×10⁻⁶, Cohen's d = −2.1), surviving Bonferroni correction (α = 0.008 for 6 tests). Exploratory extension to 6 additional loci shows mechanism-appropriate trends but only HBB is statistically robust.

4. **Honest null results:** Matched-control testing shows no significant separation for Class B VUS versus benign variants of the same category and position (p = 0.996), and within-category AUC is near chance (median 0.52). We report these null results explicitly, consistent with a falsification-first approach.

5. **207 coverage-gap variants (Class D):** VEP returns no annotation for these variants despite their proximity to known regulatory elements; structural simulation provides the only available computational signal.

**Novelty and positioning**

ARCHCODE is, to our knowledge, the first analytical loop-extrusion model applied to germline ClinVar variants across multiple loci with clinical ground truth. Existing tools address adjacent problems: svMIL (Nieboer & de Ridder, 2020, Bioinformatics) applies to somatic SVs in cancer; POSTRE (Sánchez-Gaya & Rada-Iglesias, 2023, NAR) is validated at a single locus (GPR101); experimental Hi-C (Daly et al., 2024, Genome Medicine) requires patient-specific profiling. ARCHCODE addresses the gap for germline SNPs/indels at scale, using AI-predicted chromatin contacts (AlphaGenome) rather than experimental Hi-C.

**Limitations (disclosed)**

We disclose that: (1) statistical robustness is demonstrated at a single locus (HBB), with 6-locus extension exploratory; (2) loci selection was post-hoc relative to the pilot, introducing garden-of-forking-paths risk (Gelman & Loken, 2013); (3) no wet-lab validation (ATAC-seq, experimental Hi-C) has been performed; (4) AlphaGenome training data overlaps with ARCHCODE's chromatin annotations (K562), making CAGE validation partially non-independent.

**Data and code availability**

Code: github.com/sergeeey/ARCHCODE | Preprint: Research Square DOI 10.21203/rs.3.rs-9090074/v1 | Data: Zenodo DOI 10.5281/zenodo.18908214

We have no conflicts of interest to declare. The manuscript has not been submitted elsewhere.

Sincerely,

Sergey V. Boyko
Ronin Institute for Independent Scholarship (RIIS 2.0)
sergeikuch80@gmail.com
