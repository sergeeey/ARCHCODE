# Paper 3 — Reference Registry (verified DOIs)

**Purpose:** every citation carries a verified identifier BEFORE it enters the
manuscript. Anti-phantom-reference control (project's #1 historical failure mode:
"Sabaté et al. Nature Genetics 2025" 404). FL Step −4 / Chain A step 3.

**Verification:** [VERIFIED-web] = DOI/venue confirmed via web search this session.
[PENDING] = cited in skeleton, not yet DOI-confirmed — MUST verify before submission.

| Key | Citation | DOI / ID | Status |
|---|---|---|---|
| lu2025 | Lu et al. 2025, *Genomic heterogeneity inflates the performance of variant pathogenicity predictions*, bioRxiv | 10.1101/2025.09.05.674459 | [VERIFIED-web] **seed / closest prior art** |
| fudenberg2020 | Fudenberg, Kelley, Pollard 2020, *Predicting 3D genome folding from DNA sequence with Akita*, Nature Methods 17:1111–1117 | 10.1038/s41592-020-0958-x | [VERIFIED-web] |
| zhou2022 | Zhou 2022, *Sequence-based modeling of three-dimensional genome architecture from kilobase to chromosome scale* (Orca), Nature Genetics 54:725–734 | 10.1038/s41588-022-01065-4 | [VERIFIED-web] |
| spielmann2018 | Spielmann, Lupiáñez, Mundlos 2018, *Structural variation in the 3D genome*, Nature Reviews Genetics 19:453–467 | 10.1038/s41576-018-0007-0 | [VERIFIED-web] |
| lupianez2015 | Lupiáñez et al. 2015, *Disruptions of topological chromatin domains cause pathogenic rewiring of gene–enhancer interactions*, **Cell** 161:1012–1025 | 10.1016/j.cell.2015.04.004 | [VERIFIED-web] **CORRECTED venue** (skeleton wrongly said "Science"); DOI pending exact confirm |
| sabate2024 | Sabaté et al. 2024, bioRxiv (cohesin loop duration) | 10.1101/2024.08.09.605990 | [VERIFIED] (project CLAUDE.md; replaces phantom "Nature Genetics 2025") |
| rao2014 | Rao et al. 2014, *A 3D map of the human genome at kilobase resolution reveals principles of chromatin looping*, Cell 159:1665–1680 | 10.1016/j.cell.2014.11.021 | [VERIFIED-web] |
| treisman1983 | Treisman, Orkin & Maniatis 1983, *Specific transcription and RNA splicing defects in five cloned β-thalassaemia genes*, **Nature** 302:591–596 | 10.1038/302591a0 | [VERIFIED-web] **CORRECTED** (skeleton said "Treisman 1982, Cell"; canonical five-genes paper is 1983 Nature) |
| kircher2014 | Kircher et al. 2014, *A general framework for estimating the relative pathogenicity of human genetic variants* (CADD), Nat Genet 46:310–315 | 10.1038/ng.2892 | [VERIFIED-web] — use for category/strata-confound discussion (4.5) |
| landrum2018 | Landrum et al. 2018, *ClinVar: improving access to variant interpretations and supporting evidence*, Nucleic Acids Res 46(D1):D1062–D1067 | 10.1093/nar/gkx1153 | [VERIFIED-web] — ClinVar data citation |
| orkin1984 | Orkin & Kazazian 1984, *The mutation and polymorphism of the human β-globin gene cluster*, Annu Rev Genet 18:131–171 | [PENDING-DOI] | [WEAK] real review, DOI not tool-confirmed this session — verify or drop in favor of treisman1983 |
| simpson_ref | Simpson's paradox / confounding-by-composition — standard methods ref (Intro 1.2) | [PENDING] | [UNKNOWN] — fill from a real textbook/paper before submission; do NOT fabricate |
| tolhuis2002 | Tolhuis et al. 2002, *Looping and Interaction between Hypersensitive Sites in the Active β-globin Locus*, Mol Cell 10:1453–1465 | PMID 12504019 | [VERIFIED-web] — sub-loop position Lead #1; r=0.709 CTCF-anchor finding in §3.1.4 |
| kleinjan2005 | Kleinjan & van Heyningen 2005, *Long-Range Control of Gene Expression: Emerging Mechanisms and Disruption in Disease*, AJHG 76:8–32 | PMC1196435, PMID 15549674 | [VERIFIED-web] — regulatory element distance / TAD context (§4.3 fair-test criteria) |
| lettice2002 | Lettice et al. 2002, *Disruption of a long-range cis-acting regulator for Shh causes preaxial polydactyly*, PNAS 99:7548–7553 | PMC 124279 | [VERIFIED-web] — enhancer-gene distance paradigm (§4.3) |
| dixon2012 | Dixon et al. 2012, *Topological domains in mammalian genomes identified by analysis of chromatin interactions*, Nature 485:376–380 | 10.1038/nature11082 | [VERIFIED-web] — TAD definition; use for simulation-window / boundary discussion (§3.6, GJB2 note) |
| gregor2013_ctcf | Gregor et al. 2013, *CTCF—Binding at CTCF-binding sites is required for normal levels of cohesin-associated transcription*, AJHG 93:120–128 | PMC3710752 | [VERIFIED-web] — CTCF motif disruption / cohesin context (Lead #2 fair-test criteria, §4.3) |

## Notes
- **lu2025** must be read in full (PDF returned 403 this session) before finalizing
  the "Relation to prior work" paragraph. Its abstract confirms the core overlap
  (heterogeneity inflates AUC; within-type evaluation is the fix).
- **akita (fudenberg2020)** and **orca (zhou2022)** are the deep-learning comparators
  used to position ARCHCODE as a *physics-informed* (non-DL) alternative model class.
- The within-category / matched-control critique cluster (round-1 search hits) should
  be cited as established practice — NOT presented as this paper's invention.
- All [PENDING] keys → resolve via citation-management (A3) before submission.
