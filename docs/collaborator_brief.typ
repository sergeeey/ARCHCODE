#set page(
  paper: "a4",
  margin: (top: 2cm, bottom: 2cm, left: 2.2cm, right: 2.2cm),
)
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true, leading: 0.58em)

#align(center)[
  #text(size: 16pt, weight: "bold")[ARCHCODE: Structural Prioritization\ of Enhancer-Proximal Variants]
  #v(0.3em)
  #text(size: 9pt, fill: luma(100))[One-Page Collaborator Brief · March 2026 · bioRxiv BIORXIV/2026/710343]
]

#v(0.6em)
#line(length: 100%, stroke: 0.5pt + luma(180))
#v(0.4em)

== The Problem

Sequence-based variant tools (VEP, CADD, SpliceAI) cannot detect pathogenic mechanisms arising from disruption of 3D chromatin contacts. Enhancer-proximal variants that alter cohesin-mediated loop extrusion are *invisible* to these tools --- a systematic blind spot in clinical variant interpretation.

== What ARCHCODE Found

We analyzed *32,201 ClinVar variants* across 9 disease-associated loci using a polymer physics simulation of loop extrusion. Cross-tabulation against VEP/CADD revealed:

- *54 "true blind spot" variants (Q2b):* VEP scored them low-impact, but ARCHCODE detects significant chromatin disruption
- *100% of Q2b* fall within 1 kb of annotated enhancers (vs 9% of sequence-flagged variants; OR = 22.5 at 500 bp)
- Signal is *tissue-dependent:* strongest at erythroid-matched HBB (25 Q2b), zero at tissue-mismatched controls

== Top 5 Candidates for Experimental Validation

All HBB locus, ClinVar pathogenic/likely pathogenic, absent from 9 orthogonal annotation sources:

#figure(
  align(center)[#table(
    columns: (5%, 16%, 18%, 14%, 10%, 13%, 24%),
    align: (center, left, left, left, right, right, left),
    table.header(
      [\#], [ClinVar ID], [Position (GRCh38)], [Type], [LSSIM], [Enh. dist], [Note],
    ),
    table.hline(),
    [1], [VCV002024192], [chr11:5,226,796], [Splice acc.], [0.822], [528 bp], [Strongest disruption],
    [2], [VCV000869358], [chr11:5,226,971], [Frameshift], [0.798], [703 bp], [Lowest LSSIM],
    [3], [VCV000801186], [chr11:5,226,598], [Missense], [0.909], [330 bp], [Closest to enhancer],
    [4], [VCV000015208], [chr11:5,226,613], [Missense], [0.910], [345 bp], [Cluster with \#3],
    [5], [VCV000869309], [chr11:5,226,596], [Other], [0.940], [328 bp], [Promoter-proximal],
    table.hline(),
  )]
  , kind: table
)

*PCHi-C confirmed:* all 5 reside in a bait fragment with 25 significant erythroblast interactions (CHiCAGO up to 10.5), including 5 LCR contacts (Javierre et al., 2016).

== Proposed Experiments

Targeted validation in *HUDEP-2 cells* (adult erythroid progenitors):

+ *Capture Hi-C* at 5 candidate positions --- does the variant disrupt local contact frequency?
+ *RT-qPCR* for HBB expression --- does disruption reduce β-globin output?
+ *CRISPR base editing* at top 2 positions --- causal confirmation

*Estimated effort:* 3--4 months, 1 postdoc, standard molecular biology reagents.

== Why This Is Low-Cost / High-Yield

#grid(
  columns: (1fr, 1fr),
  gutter: 1em,
  [
    *If positive:* First demonstration that 3D chromatin disruption drives pathogenicity at enhancer-proximal variants invisible to sequence tools. High-impact mechanistic result.
  ],
  [
    *If negative:* Falsifies the structural blind spot hypothesis at HBB. Equally informative, publishable, and resolves an open question.
  ],
)

#v(0.4em)
#line(length: 100%, stroke: 0.3pt + luma(200))
#v(0.2em)

#text(size: 8.5pt)[
  *Code + data:* #link("https://zenodo.org/records/18867448") (CC BY 4.0) ·
  *Reproducibility:* `REPRODUCE.md` in repository ·
  *Contact:* sergey.boyko\@example.com
]

#v(0.2em)
#align(center)[
  #text(size: 8pt, fill: luma(120), style: "italic")[
    ARCHCODE is a structural prioritization engine, not a pathogenicity predictor.
    It identifies which variants to test first --- not whether they are pathogenic.
  ]
]
