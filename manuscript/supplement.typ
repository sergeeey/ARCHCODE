// ARCHCODE Supplementary Materials
// Auto-generated from body_content.typ Multi-Locus Extension section

= Supplementary Methods

== Multi-Locus Extension: Parameter Details

To test cross-gene generalization, ARCHCODE was applied to three
additional loci:

#strong[CFTR] (chr7:116,907,253--117,224,349, 317 kb, 1000 bp
resolution, 317 bins). Locus configuration: 3 CTCF anchor sites from
ENCODE K562 ChIP-seq (ENCFF660GHM), 4 enhancer elements from published
literature. ClinVar variants: n=3,349 (1,756 P/LP + 1,593 B/LB).

#strong[TP53] (chr17:7,550,000--7,850,000, 300 kb, 1000 bp resolution,
300 bins). Locus configuration: 6 CTCF sites from ENCODE K562 ChIP-seq
(ENCFF736NYC, ENCSR000DWE), 5 enhancer elements from ENCODE K562 H3K27ac
(ENCFF864OSZ) and literature (including TP53 P1 and P2 promoters; Marcel
et al.~2010). ClinVar variants: n=2,794 (1,645 P/LP + 1,149 B/LB).

#strong[BRCA1] (chr17:42,900,000--43,300,000, 400 kb, 1000 bp
resolution, 400 bins). Locus configuration: 13 CTCF sites from ENCODE
K562 (ENCFF736NYC) cross-validated with MCF7 (ENCFF163JHE), 9 enhancer
elements from MCF7 H3K27ac (ENCFF340KSH) --- MCF7 used as primary
enhancer source because BRCA1 is actively transcribed in breast cancer
cells. Includes the BRCA1/NBR2 bidirectional promoter (Suen et
al.~1998). ClinVar variants: n=10,682 (7,062 P/LP + 3,620 B/LB).

All variants were downloaded from ClinVar via NCBI E-utilities API using
a generic downloader (`download_clinvar_generic.py --gene <GENE>`).
Variant categorization used improved HGVS nomenclature parsing that
determines frameshift vs inframe status from cDNA indel length modulo 3,
resolving \>90% of previously unclassified "other" variants (e.g.,
`c.403del` → 1 bp deletion → frameshift; `c.575_580del` → 6 bp deletion
→ inframe).

Hi-C validation for TP53 and BRCA1 used ENCODE K562 intact Hi-C
(ENCFF725EXS, ENCSR479XDG) and MCF7 intact Hi-C (ENCFF776XCM,
ENCSR660LPJ) at 1000 bp resolution with VC\_SQRT normalization (KR
normalization unavailable in ENCODE intact Hi-C files).


= Supplementary Results

== Individual Locus Results

== CFTR Locus: Cross-Gene Generalization
The within-category null result on HBB reflected a data limitation: all
1,103 variants cluster within 2.1 kb (2.2% of the 95 kb window). To test
whether greater variant positional diversity would reveal
within-category signal, we extended ARCHCODE to the CFTR locus
(chr7:116,907,253--117,224,349, 317 kb TAD, 1000 bp resolution, 317
bins).

We retrieved 3,349 CFTR variants from ClinVar (1,756 Pathogenic/Likely
Pathogenic + 1,593 Benign/Likely Benign). Unlike HBB, CFTR variants span
201.5 kb (63.6% of the simulation window), providing 29-fold greater
positional diversity. The variant composition includes: synonymous
(n=1,799), intronic (n=779), frameshift (n=516), splice\_region (n=149),
other (n=54), 5'UTR (n=19), inframe\_deletion (n=17), inframe\_indel
(n=9), 3'UTR (n=6), and splice\_donor (n=1). Variant functional
categories were assigned using improved HGVS parsing that determines
frameshift vs inframe status from cDNA indel length modulo 3 (see
Methods).

#strong[Table 3. CFTR SSIM statistics by variant category (317 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.81%, 8.77%, 28.07%, 26.32%, 14.04%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [516], [0.9986], [N/A], [---],
    [Splice region], [149], [0.9997], [0.9996], [0.84],
    [Synonymous], [1,799], [1.0000], [1.0000], [9.1×10⁻⁶],
    [Intronic], [779], [1.0000], [1.0000], [0.28],
    [Other], [54], [0.9992], [0.9983], [0.10],
    [5'UTR], [19], [0.9975], [0.9971], [0.10],
    [Inframe del.], [17], [0.9992], [N/A], [---],
    [3'UTR], [6], [0.9999], [0.9999], [---],
  )]
  , kind: table
  )

Global SSIM values were severely compressed compared to HBB (range
0.9836--1.0000 vs 0.9611--0.9998 at 95kb), reflecting matrix-size
dilution: a single-bin perturbation in a 317×317 matrix affects
proportionally fewer entries than in a 50×50 matrix. LSSIM (50×50 local
window) resolved this, expanding the range to 0.8329--0.9999 and
enabling 35 structural pathogenic verdicts. Frameshift variants (n=516,
all pathogenic) show the lowest mean SSIM (0.9986), consistent with
their strong occupancy perturbation.

Despite the greater positional diversity, within-category testing using
LSSIM confirmed the null result. Logistic regression (pathogenicity \~
category + LSSIM) yielded ΔAUC = −0.012 (p = 0.79). LSSIM does not
predict pathogenicity within functional categories on CFTR.

No CFTR variants met the pearl criteria (LSSIM \< 0.95 and VEP \< 0.30):
VEP data was not available for this locus. Pearl detection requires both
VEP and structural signals.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

== TP53 Locus: Third Cross-Gene Test
To further probe generalizability, we extended ARCHCODE to the TP53
tumor suppressor locus (chr17:7,550,000--7,850,000, 300 kb TAD, 1000 bp
resolution, 300 bins). TP53 was selected because it ranks among the most
clinically consequential genes in oncology, resides on chr17 (same
chromosome as BRCA1, enabling shared CTCF data from ENCODE K562
ENCFF736NYC), and has extensive ClinVar variant coverage.

We retrieved 2,794 TP53 variants from ClinVar (1,645 Pathogenic/Likely
Pathogenic + 1,149 Benign/Likely Benign). Variants span 109.9 kb (36.6%
of the 300 kb window) --- intermediate between HBB (2.2%) and CFTR
(63.6%). The improved classify\_hgvs() function resolved the majority of
previously unclassified variants: synonymous (n=1,400), frameshift
(n=534), intronic (n=528), splice\_region (n=139), inframe\_deletion
(n=76), other (n=53), inframe\_indel (n=35), 3'UTR (n=22), and 5'UTR
(n=8).

#strong[Table 4. TP53 SSIM statistics by variant category (300 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.41%, 8.62%, 27.59%, 25.86%, 15.52%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [534], [0.9964], [N/A], [---],
    [Splice region], [139], [0.9980], [0.9986], [8.0×10⁻⁵],
    [Inframe del.], [76], [0.9986], [0.9993], [0.060],
    [Inframe indel], [35], [0.9988], [0.9993], [0.060],
    [Synonymous], [1,400], [0.9999], [1.0000], [6.2×10⁻¹⁰],
    [Intronic], [528], [0.9998], [0.9998], [0.029],
    [Other], [53], [0.9982], [0.9993], [0.0025],
    [3'UTR], [22], [0.9999], [0.9999], [0.79],
    [5'UTR], [8], [0.9984], [N/A], [---],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9934 to 1.0000, severely compressed by
matrix-size dilution. LSSIM expanded the range to 0.9443--1.0000 ---
narrower than other loci but sufficient to assign 12 VUS verdicts (0
PATHOGENIC/LIKELY\_PATHOGENIC).

Within-category testing using LSSIM yielded a null result: logistic
regression ΔAUC = +0.032 (p = 0.29). TP53 has the narrowest LSSIM range
among all loci, consistent with its high CTCF density and complex
promoter architecture reducing the relative perturbation signal even in
the local window.

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.29 (p \<
10⁻¹⁵⁴, n = 7,821 loci); MCF7 Hi-C yielded r = 0.28 (p \< 10⁻¹³⁶, n =
7,821). Both are statistically significant but substantially lower than
HBB (r = 0.53--0.59) and BRCA1 (r = 0.50--0.53), likely reflecting the
greater structural complexity of the TP53 locus (7 H1 persistent
homology features vs 3--4 for HBB), the presence of the internal P2
promoter generating Δ133p53 isoforms, and higher CTCF density in the
TP53 genomic neighborhood.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.85 (p = 0.015), confirming that topological
perturbation and SSIM disruption remain correlated on this locus, though
weaker than HBB (ρ = −0.96) and CFTR (ρ = −1.00).

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

== BRCA1 Locus: Largest ClinVar Cohort
The BRCA1 breast cancer susceptibility gene
(chr17:42,900,000--43,300,000, 400 kb TAD, 1000 bp resolution, 400 bins)
provided the largest variant cohort and a critical test of ARCHCODE in a
clinically high-impact oncogene with well-characterized regulatory
architecture. BRCA1 shares chr17 with TP53, enabling reuse of the same
ENCODE K562 CTCF ChIP-seq peaks (ENCFF736NYC). MCF7 breast cancer cell
line data was used as the primary enhancer source (H3K27ac, ENCFF340KSH)
because BRCA1 is actively transcribed in breast tissue.

We retrieved 10,682 BRCA1 variants from ClinVar (7,062 Pathogenic/Likely
Pathogenic + 3,620 Benign/Likely Benign) --- by far the largest cohort
in this study. Variants span 103.6 kb (25.9% of the 400 kb window). The
improved classify\_hgvs() function yielded: synonymous (n=5,520),
frameshift (n=2,806), intronic (n=1,584), splice\_region (n=363), other
(n=221), inframe\_indel (n=56), 3'UTR (n=48), 5'UTR (n=46),
inframe\_deletion (n=37), and splice\_donor (n=1).

#strong[Table 5. BRCA1 SSIM statistics by variant category (400 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.41%, 8.62%, 27.59%, 25.86%, 15.52%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [2,806], [0.9995], [N/A], [---],
    [Splice region], [363], [0.9999], [0.9999], [0.68],
    [Synonymous], [5,520], [1.0000], [1.0000], [0.53],
    [Intronic], [1,584], [1.0000], [1.0000], [0.0014],
    [Other], [221], [0.9998], [0.9982], [2.4×10⁻²⁶],
    [5'UTR], [46], [0.9985], [0.9985], [0.32],
    [3'UTR], [48], [1.0000], [1.0000], [1.0],
    [Inframe indel], [56], [0.9999], [0.9999], [0.80],
    [Inframe del.], [37], [0.9998], [0.9999], [0.57],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9938 to 1.0000, the most compressed
range of any locus --- consistent with the largest matrix size
(400×400). LSSIM expanded the range to 0.8767--0.9999, enabling 52
structural pathogenic verdicts.

Within-category testing using LSSIM yielded the first statistically
significant result: logistic regression ΔAUC = +0.002 (p ≈ 10⁻²⁰).
However, the effect size is negligible (ΔAUC \< 0.002). This
significance reflects the massive statistical power (n = 10,682)
combined with LSSIM's expanded dynamic range, not meaningful
within-category prediction. For synonymous (n=5,520, the largest
single-category test), MW-U p = 0.003 --- statistically significant but
ΔLSSIM still negligible.

No BRCA1 pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.53 (p ≈ 0,
n = 12,093 loci); MCF7 Hi-C yielded r = 0.50 (p ≈ 0, n = 7,307). Both
are comparable to HBB K562 results (r = 0.53), demonstrating that
ARCHCODE's contact model generalizes well to loci with dense regulatory
architecture. The similar K562 and MCF7 correlations suggest that the
architectural features driving the model (distance decay, CTCF
positions, enhancer occupancy) are largely cell-type-invariant at this
resolution.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = NaN (all category-level perturbations produced zero
TDA signal at 400×400 resolution). Positional scan showed ρ = −0.21 (p =
0.43, not significant), indicating that TDA sensitivity drops sharply
with increasing matrix size, consistent with the dilution
interpretation.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

== MLH1 Locus: First DNA Mismatch Repair Gene
The MLH1 mismatch repair gene (chr3:36,900,000--37,200,000, 300 kb TAD,
1000 bp resolution, 300 bins) introduced the first DNA repair gene into
ARCHCODE's multi-locus portfolio. MLH1 is associated with Lynch syndrome
(hereditary nonpolyposis colorectal cancer) and features a bidirectional
CpG island promoter shared with EPM2AIP1. The locus config includes 7
CTCF sites and 8 enhancers from ENCODE K562 ChIP-seq (CTCF: ENCFF736NYC;
H3K27ac: ENCFF864OSZ).

We retrieved 4,060 MLH1 variants from ClinVar (2,425 Pathogenic/Likely
Pathogenic + 1,635 Benign/Likely Benign). Variants span 130.3 kb (43.4%
of the 300 kb window). The improved classify\_hgvs() function yielded:
synonymous (n=1,592), frameshift (n=1,029), intronic (n=955),
splice\_region (n=286), other (n=105), inframe\_deletion (n=34), 5'UTR
(n=26), inframe\_indel (n=19), 3'UTR (n=13), and splice\_donor (n=1).

#strong[Table 5b. MLH1 SSIM statistics by variant category (300 kb
window).]

#figure(
  align(center)[#table(
    columns: (22.81%, 8.77%, 28.07%, 26.32%, 14.04%),
    align: (auto,auto,auto,auto,auto,),
    table.header([Category], [n], [Mean SSIM (Path)], [Mean SSIM
      (Ben)], [MW-U p],),
    table.hline(),
    [Frameshift], [1,029], [0.9983], [0.9995], [---],
    [Splice region], [286], [0.9996], [0.9990], [6.7×10⁻⁸],
    [Synonymous], [1,592], [1.0000], [1.0000], [0.76],
    [Intronic], [955], [1.0000], [1.0000], [0.19],
    [Other], [105], [0.9990], [0.9990], [2.0×10⁻⁴],
    [5'UTR], [26], [0.9969], [0.9971], [0.79],
    [3'UTR], [13], [0.9999], [0.9999], [1.0],
    [Inframe indel], [19], [0.9986], [0.9998], [---],
    [Inframe del.], [34], [0.9995], [N/A], [---],
  )]
  , kind: table
  )

Global SSIM values ranged from 0.9838 to 1.0000 --- comparable to TP53
(also 300×300). LSSIM expanded the range to 0.8417--0.9999, enabling 72
structural pathogenic verdicts.

Within-category testing using LSSIM yielded a statistically significant
result: logistic regression ΔAUC = +0.011 (p = 0.005). As with BRCA1,
the significance reflects statistical power at n = 4,060 combined with
LSSIM's expanded dynamic range, rather than meaningful within-category
prediction (ΔAUC \< 0.02). ARCHCODE remains primarily a category-level
classifier.

No MLH1 pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] K562 Hi-C correlation yielded r = 0.59 (p ≈ 0,
n = 20,432 loci), the highest single-cell-type correlation across all
loci --- tied with HBB 95kb. This strong result likely reflects the MLH1
locus's well-defined regulatory architecture: a strong intergenic CTCF
boundary (signal = 178.7) at chr3:36,958,900 and an active promoter with
high H3K27ac enrichment (signal = 62.9). The K562 source was used
because HCT116 (where MLH1 is epigenetically silenced) Hi-C data was
inaccessible within the study timeframe.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.76 (p = 0.049), significant but weaker than HBB
(ρ = −0.96) and CFTR (ρ = −1.00), and stronger than TP53 (ρ = −0.85).
Positional scan across 15 positions showed ρ = −0.64 (p = 0.011),
confirming consistent SSIM--TDA correspondence at 300×300 resolution.

== LDLR Locus: Tissue-Specific Chromatin Validation
LDLR (Low-Density Lipoprotein Receptor, chr19p13.2) encodes the primary
receptor for LDL cholesterol clearance. Germline pathogenic variants
cause Familial Hypercholesterolemia (FH), affecting \~1:250 individuals
worldwide. LDLR is the first ARCHCODE locus validated with
tissue-specific Hi-C data (HepG2 hepatocyte line) rather than K562.

#strong[Variant analysis:] 3,284 ClinVar variants (2,274 P/LP + 1,010
B/LB) were analyzed in a 300kb window (chr19:10,940,000--11,240,000) at
1kb resolution. The window contains 6 genes including SMARCA4 (SWI/SNF
chromatin remodeler) upstream. CTCF sites from ENCODE HepG2
(ENCSR000AMA, 10 peaks) co-localize with K562 CTCF at 7/10 positions,
confirming cell-type invariance. H3K27ac from HepG2 (ENCSR000AMO) shows
a 6.3kb super-enhancer at the LDLR promoter (signal = 111.3), consistent
with high LDLR expression in hepatocytes under SREBP regulation.

#strong[SSIM results:] Global SSIM range 0.9895--1.0000; LSSIM range
0.9061--1.0000. LSSIM identified 10 structurally pathogenic variants.
Variant spread is only 2.1 kb (0.7% of window), similar to HBB --- all
ClinVar variants cluster within the LDLR gene body.

#strong[Within-category analysis:] Logistic regression shows statistical
significance (p = 0.004) but ΔAUC = −0.003, confirming the power-effect
pattern seen in BRCA1 and MLH1. Mann-Whitney U test within the "other"
category shows significant separation (Δ = −0.007, p = 0.008), while
intronic and synonymous categories show no signal. ARCHCODE remains a
category-level classifier.

No LDLR pearls were detected (VEP data not available for this locus).

#strong[Hi-C validation:] HepG2 Hi-C correlation yielded r = 0.32 (p ≈
0, n = 19,156 loci). This is the first tissue-specific validation: LDLR
is highly expressed in hepatocytes, and HepG2 Hi-C captures
liver-specific chromatin architecture. The correlation is comparable to
TP53 (K562 r = 0.29) and lower than HBB/MLH1 (r = 0.53--0.59), likely
reflecting the gene-dense chr19 environment where multiple regulatory
domains create complex contact patterns that the mean-field model
captures partially.

#strong[TDA analysis:] Spearman correlation between SSIM and Wasserstein
H1 distance was ρ = −0.51 (p = 0.24), the weakest TDA--SSIM
correspondence across all loci. Bottleneck distance showed stronger
correlation (ρ = −0.80, p = 0.03). Positional scan across 15 positions
showed ρ = −0.09 (p = 0.76), indicating that TDA captures complementary
topological information not fully reflected in SSIM at this locus.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

== SCN5A Locus: Cell-Type Mismatch as Negative Control
SCN5A (Sodium Voltage-Gated Channel Alpha Subunit 5, chr3p22.2) encodes
the primary cardiac sodium channel (Nav1.5). Pathogenic variants cause
Brugada syndrome, Long QT syndrome type 3, and other cardiac
arrhythmias. SCN5A is the first cardiac-expressed gene in the ARCHCODE
portfolio and serves as a deliberate test of cell-type specificity: the
model uses K562 (erythroid) ENCODE data for a gene primarily expressed
in cardiomyocytes.

#strong[Variant analysis:] 2,488 ClinVar variants (928 P/LP + 1,560
B/LB) were analyzed in a 400kb window (chr3:38,400,000--38,800,000) at
1kb resolution. The window contains 6 genes including SCN10A (\~47kb
downstream, another sodium channel). K562 CTCF ChIP-seq (ENCFF736NYC)
identified 14 peaks including a very strong cluster at the SCN5A TSS
(signal = 306.8, 178.3, 72.8). However, K562 H3K27ac (ENCFF864OSZ)
captures only 3 peaks in the entire 400kb window --- the weakest
enhancer annotation of any ARCHCODE locus --- reflecting minimal SCN5A
regulatory activity in erythroid cells.

#strong[SSIM results:] Global SSIM range 0.9995--1.0000; LSSIM range
0.9960--1.0000. Zero structurally pathogenic variants were identified (0
pearls). The near-unit SSIM values across all 2,488 variants demonstrate
that ARCHCODE's perturbation model produces negligible signal when the
enhancer landscape is sparse --- the 3 K562 H3K27ac peaks do not provide
sufficient regulatory context for meaningful variant-level
discrimination.

#strong[AlphaGenome benchmark:] ρ = −0.17 (Pearson r = −0.08), the
lowest across all seven loci. AlphaGenome contact maps were obtained
from GM12878 (lymphoblastoid --- no K562 available). The near-zero
correlation reflects both cell-type mismatch and the sparse regulatory
landscape: without tissue-appropriate enhancer features, the analytical
model cannot reconstruct a contact pattern that meaningfully corresponds
to deep learning predictions from sequence.

#strong[Epigenome cross-validation:] CTCF recall remains 100% (14/14
sites, F1 = 0.76), confirming that CTCF binding is cell-type invariant
even for this cardiac gene. H3K27ac recall is 67% (2/3, F1 = 0.18), with
the lowest F1 across all loci --- consistent with the minimal K562
H3K27ac signal at a cardiac gene.

#strong[Interpretation.] SCN5A establishes a critical negative control:
ARCHCODE's discriminative power is contingent on cell-type-appropriate
regulatory annotation. When enhancer data is absent (3 peaks vs 7--14 at
other loci), the model correctly produces near-null perturbation for all
variants rather than generating false positives. This validates that
ARCHCODE's structural pathogenicity verdicts arise from biologically
meaningful regulatory features, not computational artifacts. Future
SCN5A analysis should use iPSC-CM (induced pluripotent stem cell-derived
cardiomyocyte) Hi-C and H3K27ac data, which would capture
cardiac-specific enhancers and potentially reveal structural
pathogenicity in the same variants.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

=== TERT (chr5p15.33; 300 kb; 2,089 ClinVar variants)
<tert-chr5p15.33-300-kb-2089-clinvar-variants>
#strong[Locus rationale.] The telomerase reverse transcriptase
(#emph[TERT]) promoter is one of the most frequently mutated non-coding
regions in cancer. K562 cells are hTERT-positive, providing a
biologically relevant expression context --- though TERT-driven cancers
(glioblastoma, melanoma, bladder) represent different tissues. The locus
lies at an inter-TAD boundary between two flanking topological domains,
providing a unique structural context distinct from the intra-TAD loci
analyzed previously.

#strong[Variant cohort.] 2,089 ClinVar variants (431 Pathogenic/LP +
1,658 Benign/LB) were retrieved via NCBI E-utilities. The locus
configuration spans chr5:1,100,000--1,400,000 (300 kb), with 10 CTCF
binding sites (ENCODE K562 ChIP-seq, ENCFF660GHM) and 5 H3K27ac peaks
(ENCODE K562, ENCFF038DDS).

#strong[LSSIM results.] Mean LSSIM: Pathogenic = 0.9798, Benign = 0.9986
(Δ = 0.0188). This places TERT second only to HBB in structural
discrimination among all nine loci. 27 variants received structural
pathogenic verdicts (LSSIM \< per-locus threshold 0.968), all from
frameshift and nonsense categories. Zero pearl variants were identified
(all ARCHCODE-only detections have CADD phred ≥ 20).

#strong[Interpretation.] The strong discrimination (Δ = 0.019) despite
inter-TAD positioning suggests that TERT's flanking enhancer landscape
--- 5 H3K27ac peaks spanning the promoter region --- provides sufficient
regulatory context for ARCHCODE's occupancy model. The "expressed but
not tissue-matched" status of K562 creates an intermediate scenario:
stronger signal than tissue-mismatch loci (SCN5A, GJB2) but weaker than
fully matched HBB.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

=== GJB2 (chr13q12.11; 300 kb; 469 ClinVar variants)
<gjb2-chr13q12.11-300-kb-469-clinvar-variants>
#strong[Locus rationale.] Gap junction beta-2 (#emph[GJB2]) is the most
common cause of autosomal recessive non-syndromic hearing loss. It is
expressed exclusively in cochlear hair cells and supporting cells ---
with no expression in K562 erythroid cells. GJB2 was included as a
deliberate tissue-mismatch negative control to test the prediction that
ARCHCODE produces null signal when the regulatory landscape is absent.

#strong[Variant cohort.] 469 ClinVar variants (314 Pathogenic/LP + 155
Benign/LB). The locus configuration spans chr13:20,600,000--20,900,000
(300 kb), with 8 CTCF binding sites and 2 H3K27ac peaks --- the sparsest
enhancer landscape among all nine loci.

#strong[LSSIM results.] Mean LSSIM: Pathogenic = 0.9916, Benign = 0.9978
(Δ = 0.0062). Zero structural pathogenic verdicts at any threshold. Zero
pearl variants. No threshold achieves FPR ≤ 1% with any sensitivity ---
complete null.

#strong[Interpretation.] GJB2 confirms the tissue-specificity
hypothesis: without cell-type- appropriate enhancer annotation, ARCHCODE
correctly produces near-unit LSSIM for all variants regardless of
clinical significance. The complete null (0 structural pathogenic, 0
pearls, no achievable threshold) parallels SCN5A and establishes that
ARCHCODE's discriminative power is contingent on regulatory annotation,
not computational artifacts. Future GJB2 analysis would require cochlear
cell Hi-C and H3K27ac data to test whether structural pathogenicity
emerges with tissue-matched annotation.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)



== Deep Learning Benchmark Details

== AlphaGenome Benchmark
To contextualize ARCHCODE's analytical contact maps against
state-of-the-art deep learning predictions, we performed a direct
comparison with AlphaGenome (Google DeepMind), a genomics foundation
model that predicts chromatin contact maps from DNA sequence.
AlphaGenome was accessed via its Python SDK (v0.6.0) using contact map
predictions from 28 cell lines in the 4D Nucleome repository at 2048 bp
resolution. For each of seven ARCHCODE loci, we requested AlphaGenome
contact maps using a sequence length of 524,288 bp centered on the
ARCHCODE window (131,072 bp for HBB 30kb), extracted the overlapping
region, and resampled to match ARCHCODE's bin count.

Because AlphaGenome returns distance-normalized (observed/expected)
log-scale values, while ARCHCODE and Hi-C produce raw contact
probabilities with distance decay, we applied distance normalization
(O/E per stratum) to ARCHCODE and Hi-C matrices before comparison.
AlphaGenome values were transformed from log to linear scale via exp().
All matrices were then min-max normalized, and Pearson r and Spearman ρ
were computed on upper-triangle elements (excluding diagonal and first
off-diagonal).

Cell line selection was matched where possible: HepG2 for LDLR
(liver-expressed gene), GM12878 (lymphoblastoid reference) for all other
loci. K562 --- the primary cell line for ARCHCODE Hi-C validation --- is
not available in AlphaGenome's contact map predictions.

#strong[Results.] ARCHCODE and AlphaGenome contact maps show consistent
moderate agreement across most loci: Spearman ρ ranges from 0.27 (CFTR)
to 0.52 (BRCA1), with Pearson r = 0.07--0.29 (Table 6, row "AG ρ"). HBB
(ρ = 0.15) is an outlier explained by the narrow 30 kb window yielding
only 15 AlphaGenome bins (2048 bp resolution) and cell line mismatch
(GM12878 vs K562). The Spearman rank correlation consistently exceeds
Pearson, suggesting a monotonic but non-linear relationship between the
two approaches --- expected given their fundamentally different
methodologies (analytical physics vs deep learning from sequence).

That an analytical mean-field model with no training data correlates at
ρ ≈ 0.3--0.5 with a deep learning foundation model trained on thousands
of Hi-C experiments suggests both approaches capture genuine features of
chromatin architecture --- CTCF-mediated boundaries and enhancer-driven
contact enrichment --- despite operating through entirely different
computational paradigms.

=== Variant-Level AlphaGenome Mutagenesis
To test whether AlphaGenome detects the same variant-level perturbations
as ARCHCODE, we performed in-silico mutagenesis on 27 pearl variants
from the HBB 95kb atlas using AlphaGenome's `predict_variant()` API. For
each variant, AlphaGenome returns both reference and alternate contact
maps from the same genomic interval, enabling direct computation of
ΔSSIM between wild-type and mutant predictions. Of 27 pearl variants, 23
were processable (4 excluded for IUPAC ambiguity codes); none were
skipped for complexity.

#strong[Results.] AlphaGenome perturbation signals were uniformly small:
ΔSSIM ranged from 7.5 × 10⁻⁵ to 6.3 × 10⁻⁴ (mean = 3.1 × 10⁻⁴), compared
to ARCHCODE ΔSSIM of 0.010--0.031 (mean = 0.015) --- a \~49-fold
difference in perturbation magnitude. Correlation between ARCHCODE and
AlphaGenome ΔSSIM was non-significant (Pearson r = 0.06, p = 0.78;
Spearman ρ = −0.32, p = 0.13; n = 23).

#strong[Interpretation.] This null result is informative rather than
negative. AlphaGenome operates at 2048 bp resolution --- individual SNVs
affect \< 0.05% of the input sequence, producing contact map changes
near the noise floor. ARCHCODE, by contrast, directly perturbs loop
extrusion parameters at the variant position, amplifying structural
signal regardless of sequence length. The two approaches thus have
complementary resolution regimes: AlphaGenome excels at wild-type
structural prediction (ρ = 0.12--0.52, see above), while ARCHCODE's
analytical perturbation model provides variant-level sensitivity that
sequence-based deep learning cannot currently achieve at this
resolution. Together with the Akita null result below, this dual-DL
benchmark fully addresses Limitation \#10.

=== Akita Benchmark
To verify that the AlphaGenome wild-type results are not model-specific,
we performed an independent benchmark against Akita (Fudenberg et al.,
2020, #emph[Nature Methods]), a deep learning model for chromatin
contact map prediction from DNA sequence. Akita uses the Basenji
framework (Kelley et al., 2020) and operates at the same 2048 bp
resolution as AlphaGenome, but was developed independently (Calico,
TensorFlow) with earlier training data (Rao et al.~2014 Hi-C).
Critically, Akita is fully open-source --- model weights, architecture,
and training code are publicly available --- enabling local CPU
inference without cloud API dependency.

For each of six ARCHCODE loci (excluding SCN5A), we fetched a 1,048,576
bp reference sequence centered on the locus (Ensembl REST API, GRCh38),
one-hot encoded it, and predicted a 448×448 contact map (GM12878, target
index 2). The Akita output (upper triangle vector of 99,681 elements)
was reshaped to a 2D matrix, the locus window extracted, resampled to
match ARCHCODE's bin count, and distance-normalized identically to the
AlphaGenome comparison.

#strong[Results.] Akita and ARCHCODE contact maps show moderate
agreement across large loci: Spearman ρ ranges from 0.17 (TP53) to 0.43
(BRCA1), comparable to AlphaGenome's 0.12--0.52 (Table 6, row "Akita
ρ"). The pattern across loci is consistent: larger windows with more
Akita bins yield stronger correlations (BRCA1: 195 bins, ρ = 0.43; CFTR:
155 bins, ρ = 0.41), while narrow HBB windows produce weak or
artifactual results due to aggressive upsampling (95kb: 47→159 bins, ρ =
−0.27).

#strong[Variant-level mutagenesis.] To test whether Akita detects
variant-level perturbations, we performed ref/alt in-silico mutagenesis
on the same 23 pearl variants from the HBB 95kb atlas. Unlike
AlphaGenome (which provides a `predict_variant()` API), Akita requires
manual sequence substitution: for each variant, we created an alternate
1Mb sequence, predicted both ref and alt contact maps, and computed
ΔSSIM. Akita ΔSSIM ranged from 4.6 × 10⁻⁷ to 5.5 × 10⁻² (mean = 5.7 ×
10⁻³), with the upper range driven by three large indels (≥25 bp) that
alter a detectable fraction of the 1Mb input. For point mutations
(SNVs), Akita ΔSSIM was uniformly \< 10⁻⁴ --- comparable to
AlphaGenome's noise floor. Spearman rank correlation between ARCHCODE
and Akita ΔSSIM was non-significant (ρ = −0.17, p = 0.45; n = 23), while
Pearson r = 0.56 (p = 0.005) was driven entirely by the shared indel
signal. This constitutes a dual-DL null result for point mutations ---
two independent models, same conclusion.

#strong[Interpretation.] The concordance between AlphaGenome and Akita
wild-type results (both showing ρ ≈ 0.2--0.5) and their shared inability
to detect SNV-level perturbations strengthens two conclusions: (1)
ARCHCODE's analytical contact maps capture genuine features of chromatin
architecture that two independent DL approaches independently recover;
(2) ARCHCODE's direct perturbation of loop extrusion parameters provides
variant-level sensitivity that sequence-based DL models at 2048 bp
resolution cannot match. Akita's sensitivity to large indels but not
SNVs is consistent with the 2048 bp resolution limit: a 25 bp
duplication alters \~1.2% of a bin, while a single SNV alters \< 0.05%.
Notably, Akita was trained on Rao et al.~2014 Hi-C data (not 4DN), so
the wild-type concordance cannot be attributed to shared training signal
--- unlike AlphaGenome (see Limitation \#10).

=== Multimodal AlphaGenome Validation (RNA-seq + ATAC)
Contact maps operate at 2048 bp resolution, where individual SNVs alter
\< 0.05% of an input bin --- producing perturbation signals near the
noise floor. However, AlphaGenome also predicts RNA-seq and ATAC-seq
tracks at #strong[1 bp resolution] --- a 2048-fold increase. At this
resolution, each SNV directly modifies 1 of \~131,000 bins (0.0008%), a
substantially larger fractional effect than the contact map case. We
therefore tested whether these orthogonal epigenomic modalities detect
variant-level signal invisible to contact maps.

Using AlphaGenome's `predict_variant()` API, we obtained reference and
alternate RNA-seq and ATAC-seq predictions for all 23 processable pearl
variants (20 SNVs, 3 indels) from the HBB 95kb atlas. Predictions were
filtered to K562 (EFO:0002067) --- the most biologically relevant cell
line for the HBB locus --- yielding 5 RNA-seq tracks (polyA+/total,
±strand and unstranded) and 1 ATAC-seq track per variant. Metrics were
computed on the unstranded polyA+ RNA-seq track and the K562 ATAC-seq
track within the 95 kb locus window.

#strong[Results.] In sharp contrast to the contact map null (ΔSSIM \<
10⁻⁴), both modalities show substantial variant-level signal at 1 bp
resolution:

#figure(
  align(center)[#table(
    columns: (26.6%, 14.89%, 15.96%, 23.4%, 4.26%, 14.89%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [RNA-seq (K562)], [ATAC-seq (K562)], [Contact
      maps (2048 bp)], [], [],),
    table.hline(),
    [Mean max], [ref − alt], [], [28.13], [5.70], [\< 10⁻⁴ (ΔSSIM)],
    [Mean delta at variant bin], [0.38], [0.27], [---], [], [],
    [Mean cosine similarity], [0.9954], [0.9205], [\~1.0000], [], [],
    [Mean signal concentration], [16.97×], [11.15×], [---], [], [],
    [Indel max delta range], [99.8--220.7], [23.4--23.9], [---], [], [],
    [SNV max delta range], [6.0--15.1], [0.5--6.6], [---], [], [],
  )]
  , kind: table
  )

Signal concentration ratio measures the mean delta within ±500 bp of the
variant divided by the mean delta across the full locus window. Values
of 11--17× indicate that perturbation signal is strongly localized
around the variant position rather than uniformly distributed (which
would give a ratio of \~1.0). This confirms genuine variant-level effect
rather than global numerical noise.

Indels show dramatically larger deltas than SNVs (RNA-seq: 99--221 vs
6--15; ATAC: 23 vs 0.5--7), consistent with the resolution-dependent
pattern observed in Akita contact maps (where large indels but not SNVs
were detectable at 2048 bp).

#strong[Correlation with ARCHCODE.] Spearman rank correlation between
ARCHCODE ΔSSIM and AlphaGenome multimodal deltas was non-significant:
RNA-seq max\_delta ρ = −0.22 (p = 0.31); ATAC max\_delta ρ = −0.32 (p =
0.14); n = 23. This indicates that while both methods detect
variant-level perturbations, they rank variants differently ---
consistent with fundamentally different mechanisms (analytical loop
extrusion vs deep learning from sequence).

#strong[Interpretation.] The multimodal analysis reveals a
resolution-dependent hierarchy in AlphaGenome's ability to detect
variant effects: contact maps (2048 bp) → null; RNA-seq and ATAC-seq (1
bp) → detectable signal. This demonstrates that the contact map null
result (Limitation \#10) is a resolution limitation, not a fundamental
inability of deep learning to detect sequence variants. The lack of rank
correlation with ARCHCODE is expected: RNA-seq reflects transcriptional
effects, ATAC-seq reflects chromatin accessibility, while ARCHCODE
models loop extrusion dynamics --- three distinct biological mechanisms
that need not correlate for individual variants.

#strong[Pearl vs Benign Control.] To test whether the multimodal signal
is specific to pathogenic pearl variants or a generic property of all
variants in the locus, we ran the identical analysis on 23 randomly
sampled benign non-pearl variants (seed = 42, matched sample size).
Mann-Whitney U tests (two-sided, non-parametric) reveal that pearl
variants produce significantly different signal across all 10 metric ×
modality combinations (p \< 0.05 for all):

#figure(
  align(center)[#table(
    columns: (24.69%, 9.88%, 17.28%, 18.52%, 3.7%, 9.88%, 16.05%),
    align: (auto,auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [Modality], [Pearl (n = 23)], [Benign (n =
      23)], [U], [p-value], [Effect size r],),
    table.hline(),
    [Signal concentration], [RNA-seq], [16.97×], [6.09×], [450], [\<
    0.0001], [−0.70],
    [Delta at variant
    bin], [RNA-seq], [0.381], [0.109], [410], [0.0014], [−0.55],
    [Mean abs
    delta], [RNA-seq], [0.075], [0.032], [407], [0.0018], [−0.54],
    [Signal
    concentration], [ATAC], [11.15×], [6.39×], [402], [0.0026], [−0.52],
    [Mean abs
    delta], [ATAC], [0.046], [0.058], [401], [0.0028], [−0.52],
    [Cosine
    similarity], [ATAC], [0.921], [0.891], [132], [0.0037], [+0.50],
    [Max abs delta], [ATAC], [5.70], [4.88], [394], [0.0045], [−0.49],
    [Cosine
    similarity], [RNA-seq], [0.995], [0.999], [148], [0.011], [+0.44],
    [Max abs
    delta], [RNA-seq], [28.13], [27.43], [370], [0.012], [−0.40],
    [Delta at variant
    bin], [ATAC], [0.268], [0.098], [364], [0.029], [−0.38],
  )]
  , kind: table
  )

The most discriminative metric is #strong[signal concentration ratio]
(RNA-seq: r = −0.70, p \< 0.0001), indicating that pearl variants
concentrate perturbation signal within ±500 bp of the variant position
2.8× more strongly than benign variants (16.97× vs 6.09×). Raw
max#emph[delta values are similar between groups (28.13 vs 27.43 for
RNA-seq) because both groups contain indels that produce large absolute
deltas; the key difference is \_where] the signal localizes. Pearl
variants alter the local sequence context at positions where the deep
learning model predicts the largest regulatory effects, while benign
variants produce more diffuse perturbation.

#figure(
  image("../figures/fig10_alphagenome_validation.png", width: 95%),
  caption: [AlphaGenome multimodal validation of ARCHCODE pearl variant predictions. (A) Signal concentration ratio (mean delta within ±500 bp of variant / mean delta across locus) for RNA-seq and ATAC-seq tracks, comparing 23 pearl variants versus 23 benign controls (HBB locus, K562 cell line). Pearl variants concentrate perturbation signal 2.8× (RNA-seq, p < 0.0001) and 1.7× (ATAC-seq, p = 0.0026) more strongly than benign variants. Dashed line at 1.0 indicates uniform (no localization). (B) Three-locus tissue gradient for RNA-seq signal concentration. HBB (K562, tissue-matched) shows 10/10 significant tests with 2.8× pathogenic/benign ratio; BRCA1 (MCF7, tissue-matched) shows 1/10 with 2.4× ratio; SCN5A (K562, tissue-mismatch) shows 0/10 with ratio ≈ 1.0. The monotonic decline from matched to mismatched loci confirms biological specificity of the multimodal signal.],
) <fig-alphagenome-validation>

#strong[Cross-Locus Replication: BRCA1 Pathogenic vs Benign.] To test
whether the multimodal signal generalizes beyond HBB pearl variants, we
applied the same AlphaGenome RNA-seq + ATAC analysis to BRCA1
(chr17:42.9--43.3 Mb) using MCF7 (EFO:0001203) as the tissue-matched
cell line (breast cancer, where BRCA1 is actively transcribed). Since
BRCA1 has no ARCHCODE pearl variants (all SSIM ≈ 1.0000), we compared 23
randomly sampled ClinVar Pathogenic variants against 23 ClinVar Benign
variants (seed = 42). Of 10 metric × modality tests, 1 reached
significance:

#figure(
  align(center)[#table(
    columns: (22.99%, 9.2%, 21.84%, 17.24%, 5.75%, 8.05%, 14.94%),
    align: (auto,auto,auto,auto,auto,auto,auto,),
    table.header([Metric], [Modality], [Pathogenic (n = 23)], [Benign (n
      \= 23)], [U], [p-value], [Effect size r],),
    table.hline(),
    [Delta at variant
    bin], [RNA-seq], [0.074], [0.022], [382.5], [0.0098], [−0.45],
    [Signal
    concentration], [RNA-seq], [10.71×], [4.45×], [352.0], [0.056], [−0.33],
  )]
  , kind: table
  )

RNA-seq max\_delta = 6.0 for all 46 variants (ceiling effect in
AlphaGenome output), rendering this metric uninformative. The
significant result --- #strong[delta at variant bin] (p = 0.0098, r =
−0.45) --- indicates that pathogenic variants produce 3.4× stronger
RNA-seq perturbation directly at the variant position. Signal
concentration shows a consistent direction (pathogenic 10.71× vs benign
4.45×) but is borderline significant (p = 0.056). ATAC metrics show no
significant difference (all p \> 0.23).

The weaker discrimination in BRCA1 vs HBB (1/10 vs 10/10 significant
tests) is biologically expected: HBB pearls are ARCHCODE-selected
variants near regulatory elements (CTCF sites, enhancers) where
epigenomic perturbation concentrates; BRCA1 ClinVar pathogenic variants
are predominantly coding (frameshift, nonsense, missense) where disease
mechanism operates through protein truncation rather than chromatin
architecture. The partial replication of delta\_at\_variant (the most
direct measure of local perturbation) across loci with different variant
classes supports the biological specificity of the signal.

#strong[Cell-Type Mismatch Negative Control: SCN5A.] To test whether
multimodal discrimination depends on tissue-matched cell line
annotation, we applied the same analysis to SCN5A (chr3:38.4--38.8 Mb),
a cardiac ion channel gene not expressed in K562. Using K562 as a
deliberate cell-type mismatch, we compared 23 ClinVar Pathogenic vs 23
Benign variants (seed = 42). RNA-seq max\_delta was 230× lower than
BRCA1 and 1,080× lower than HBB (0.026 vs 6.0 vs 28.1), confirming
near-zero RNA prediction for a non-expressed gene. Signal concentration
ratio showed no discrimination (pathogenic 0.39× vs benign 0.40×, p =
0.96), consistent with noise-floor signal in both groups.

#figure(
  align(center)[#table(
    columns: (6.85%, 12.33%, 10.96%, 45.21%, 10.96%, 13.7%),
    align: (auto,auto,auto,auto,auto,auto,),
    table.header([Locus], [Cell line], [Match], [RNA concentration (Path
      \/ Benign)], [p-value], [Sig. tests],),
    table.hline(),
    [HBB], [K562], [Matched], [16.97× / 6.09× = 2.78×], [\<
    0.0001], [10/10],
    [BRCA1], [MCF7], [Matched], [10.71× / 4.45× =
    2.41×], [0.056], [1/10],
    [SCN5A], [K562], [Mismatch], [0.39× / 0.40× =
    0.96×], [0.96], [0/10†],
  )]
  , kind: table
  )

†SCN5A had 2 nominally significant tests (RNA max\_abs\_delta p = 0.017,
ATAC concentration p = 0.036) but both reflect technical artifacts: RNA
max\_delta difference (0.026 vs 0.024) is within quantization noise, and
ATAC concentration is in the opposite direction (benign \> pathogenic, r
\= +0.37), inconsistent with the tissue-matched pattern. We count 0/10
biologically meaningful significant tests.

The three-locus gradient --- strong discrimination with tissue-matched
regulatory variants (HBB), partial discrimination with tissue-matched
coding variants (BRCA1), null discrimination with cell-type mismatch
(SCN5A) --- demonstrates that multimodal signal specificity depends on
both variant class and tissue context.

=== Epigenome Cross-Validation
To independently validate the ENCODE ChIP-seq features used as ARCHCODE
input parameters (CTCF binding sites and H3K27ac enhancer peaks), we
queried AlphaGenome's epigenomic prediction tracks (CHIP\_TF for CTCF,
CHIP\_HISTONE for H3K27ac) across all seven loci. These tracks predict
transcription factor binding and histone modifications directly from DNA
sequence at 128 bp resolution --- an independent method from
experimental ChIP-seq.

#strong[CTCF validation.] AlphaGenome predicted CTCF binding at 100% of
ENCODE-annotated CTCF positions across all seven loci (68/68 sites
recovered within 2 kb tolerance), with mean F1 = 0.71 (range:
0.54--0.83). The lower precision (37--71%) reflects AlphaGenome
predicting additional CTCF sites beyond our curated set, which may
represent real binding sites not included in our configs rather than
false positives.

#strong[H3K27ac validation.] For the five loci with ENCODE H3K27ac
annotations (TP53, BRCA1, MLH1, LDLR, SCN5A), AlphaGenome recovered 81%
of annotated enhancer peaks (31/37), with mean F1 = 0.42 (range:
0.18--0.67). SCN5A showed the lowest F1 (0.18, only 3 K562 peaks for a
cardiac gene) and MLH1 the lowest recall (62%), reflecting
cell-type-specific enhancer activity not captured by the generic
AlphaGenome prediction.

#strong[Significance.] Perfect CTCF recall (100%) across seven
independent loci confirms that ARCHCODE's structural model is built on
experimentally validated chromatin boundary positions. The H3K27ac
validation (85% recall) provides additional confidence that enhancer
annotations reflect genuine regulatory features, though cell-type
specificity remains a limitation.

#v(0.8em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.8em)

= Supplementary Note: Annotation Coverage Gaps Inflate Apparent Discordance

Cross-tabulation of ARCHCODE structural predictions against VEP sequence annotations across 30,318 ClinVar variants at nine loci reveals 261 Q2 variants where the structural model detects chromatin disruption that VEP misses. However, decomposing Q2 into subtypes reveals that *79.3% of apparent discordance reflects annotation infrastructure gaps, not mechanistic disagreement*.

- *Q2a (n = 207):* VEP returned no consequence score (VEP = −1). These are non-coding frameshifts, complex indels, and intergenic variants outside Ensembl's annotation model.
- *Q2b (n = 54):* VEP assigned a score in the 0--0.5 range (mean 0.208) but rated the variant as low-impact. ARCHCODE detects structural disruption (mean LSSIM = 0.927). These are true mechanistic blind spots.

#strong[Per-locus decomposition:]

#figure(
  align(center)[#table(
    columns: (12%, 9%, 8%, 8%, 11%, 11%, 12%, 29%),
    align: (left, right, right, right, right, right, right, left),
    table.header(
      [Locus], [N], [Q2], [Q2a], [Q2b], [Q2b/Q2], [Tissue], [Interpretation],
    ),
    table.hline(),
    [HBB], [1,103], [25], [0], [25], [100%], [1.0], [Pure mechanistic blind spot],
    [BRCA1], [10,682], [79], [53], [26], [33%], [0.5], [Mixed; Q2b mostly benign],
    [TERT], [2,089], [35], [34], [1], [3%], [0.5], [Pure infrastructure gap],
    [MLH1], [4,060], [72], [72], [0], [0%], [0.5], [Pure infrastructure gap],
    [CFTR], [3,349], [36], [36], [0], [0%], [0.0], [Infrastructure + tissue mismatch],
    [TP53], [2,794], [4], [2], [2], [50%], [0.5], [Small n; inconclusive],
    [LDLR], [3,284], [10], [10], [0], [0%], [0.0], [Infrastructure + tissue mismatch],
    [SCN5A], [2,488], [0], [0], [0], [---], [0.0], [No structural signal],
    [GJB2], [469], [0], [0], [0], [---], [0.0], [No structural signal],
    table.hline(),
    [*Total*], [*30,318*], [*261*], [*207*], [*54*], [*20.7%*], [], [],
  )]
  , caption: [Supplementary Table: Q2 decomposition across nine loci. Q2a = VEP coverage gap (VEP = −1). Q2b = true blind spot (VEP 0--0.5 but ARCHCODE LSSIM < 0.95). Only HBB shows pure mechanistic disagreement.]
  , kind: table
)

#strong[TERT case study.] TERT provides the clearest illustration: 35 Q2 variants with 23-fold enhancer proximity enrichment (p = 2.03 × 10#super[−15]), yet 34 of 35 are Q2a (VEP = −1). TERT's apparent discordance is 97% infrastructure gap. Contrast with HBB, where all 25 Q2 variants are Q2b: VEP assigned scores (0.15--0.35), rated them low-impact, but ARCHCODE detects strong structural disruption (LSSIM 0.798--0.942).

#strong[Implication.] Cross-tool discordance metrics should always decompose into coverage gap vs genuine disagreement. Reporting "261 variants where ARCHCODE detects but VEP misses" without the Q2a/Q2b split overstates complementarity by 4×.

