---
experiment: exp_synonymous_codon_optimality
date: 2026-07-07
ladder_tier: Standard
question_type: Predictive
status: REJECT -- Cliff's delta -0.15 (primary), -0.17 (sensitivity), correctly signed and p<1e-6 but below pre-registered MCID (0.2); see decision.md
---

# Claim: Codon-usage-frequency delta discriminates Pathogenic from Benign ClinVar synonymous variants

## Background (Hypothesis C from the post-audit menu)

Deliberately a different mechanism than today's earlier work (chromatin/enhancer proximity,
which used ENCODE ChIP-seq + genome-build-sensitive coordinates and produced 3 REJECTs + 1
CANDIDATE FLAGGED). This tests a translation/mRNA-stability mechanism instead: does changing a
codon to a less-optimal synonym (same amino acid, different triplet) predict pathogenicity in
ClinVar, independent of any protein-sequence change?

## EstimandOps L0

**Question type:** Predictive.
"Does the change in codon-usage frequency (ALT codon per-mille usage minus REF codon per-mille
usage, i.e. more/less 'optimal') predict ClinVar Pathogenic vs Benign classification for
synonymous (silent) SNVs?"

Not causal as designed: no DAG, no identifiability analysis, no manipulation of an mRNA-decay
pathway. This is an association/classification test only -- confirmed correlation would be a
lead for follow-up causal work (e.g. reporter-construct decay-rate assay), not proof that codon
optimality *causes* the pathogenic phenotype for any individual variant.

## Novelty check (per falsification-ladder.md Step -3, mandatory for AI-generated hypotheses)

Ran via WebSearch, 2026-07-07, BEFORE any data work:

The BROAD mechanism -- codon optimality affects mRNA stability via translation-coupled decay,
and synonymous variants can be disease-relevant through this route -- is NOT novel. Confirmed:
- Hia & Takahashi / Buschauer et al., *Codon optimality, bias and usage in translation and mRNA
  decay*, Nature Reviews Molecular Cell Biology 2017 (nrm.2017.91) -- foundational review of the
  optimal-codon/mRNA-decay mechanism itself.
- Multiple published ENSEMBLE predictors already combine codon-usage features with splicing,
  mRNA-structure, and conservation features to classify ClinVar synonymous variants as
  pathogenic/benign, e.g. "An Ensemble Approach to Predict the Pathogenicity of Synonymous
  Variants" (PMC7565489, 29 features across 5 classes including codon usage bias) and the
  review "Decoding the effects of synonymous variants" (PMC8682775, Nucleic Acids Research
  2021) which explicitly lists codon bias, mRNA stability, splicing, and structure as the
  established feature categories these tools use.
- These existing tools are full ensembles (many features, trained classifiers). None of the
  search results found a report of the SINGLE simplest proxy -- raw codon-usage-frequency delta
  alone, with no other feature -- tested in isolation for standalone discriminative power.

**Reformulated, honest scope:** this experiment does NOT claim to discover that codon
optimality matters for synonymous-variant pathogenicity (well established) or to build a
better predictor than the existing multi-feature ensembles (out of scope, would need a trained
classifier + held-out validation against those published tools). It tests, independently and
with this project's own methodology/data, whether the SINGLE simplest univariate signal (Δ
codon-usage frequency, no splicing/structure/conservation features at all) carries ANY
standalone discriminative signal on real ClinVar data -- matching this project's established
practice of testing simple features before trusting complex ones (see
`exp_enhancer_proximity_replication`, `null_results/20260605-archcode-lssim-category-artifact.md`).
A null result here would be unsurprising (ensembles need multiple features precisely because
single features are individually weak) and is pre-registered as a valid, reportable outcome.

## L1 Estimand

- **Population:** ClinVar SNVs, GRCh37/hg19, genome-wide, restricted to synonymous
  (silent) coding changes -- identified directly from ClinVar's own `Name` field protein-change
  notation (e.g. `p.Leu5Leu`, ref and alt 3-letter amino acid codes identical), NOT via a
  separate VEP consequence call. This avoids a genome-wide VEP consequence-classification pass
  (expensive, rate-limited) while using a real, verifiable ClinVar-native field. Strict
  ClinicalSignificance: Pathogenic/Likely pathogenic vs Benign/Likely benign only (excludes
  VUS/conflicting, same PATH_SIGS/BENIGN_SIGS word-sets already used in
  `scripts/fetch_clinvar_erythroid_loci_hg19.py`).
- **Exposure:** Δ codon-usage frequency = usage_per_1000(ALT codon) − usage_per_1000(REF codon),
  from the Kazusa Codon Usage Database, *Homo sapiens* [gbpri] table (93,487 CDSs, 40,662,582
  codons; www.kazusa.or.jp/codon, fetched live, real public source, not a hardcoded/fitted
  constant). REF/ALT codon triplets obtained from Ensembl VEP GRCh37 REST API `codons` field
  (confirmed present in response schema via a live test call, 2026-07-07, e.g.
  `"codons": "cGc/cAc"` for a known missense test variant -- same field returns for synonymous
  changes).
- **Comparator:** Benign/Likely benign Δusage distribution vs Pathogenic/Likely pathogenic
  Δusage distribution.
- **Endpoint:** ClinVar clinical significance label.
- **Summary measure:** Mann-Whitney U on Δusage (continuous, two-sided) as the primary test;
  effect size reported as Cliff's delta (rank-based, bounded [-1,1], computed directly from the
  U statistic: δ = 2U/(n1·n2) − 1 -- no scipy dependency, consistent with this project's
  from-scratch stats implementations).
- **MCID:** |Cliff's delta| ≥ 0.2 (conventional small-to-medium threshold) AND
  Benjamini-Hochberg-corrected p < 0.05, evaluated jointly across the primary test and the one
  pre-registered sensitivity check below (2 tests total).
- **ICE:** None (complete-case classification; variants where VEP fails to return a codons
  field, or where the Name-field parse is ambiguous, are excluded and the exclusion count is
  reported, not imputed).

**Addendum (2026-07-07, after fetching real population sizes, BEFORE any VEP annotation or
test statistic was computed):** the genome-wide ClinVar fetch returned 829 pathogenic vs
685,044 benign synonymous SNVs -- VEP-annotating all 685K benign variants is computationally
impractical in this session (~hours at the rate-limited batch size already used throughout this
project). Pre-registering here, before touching VEP or the codon-usage table: the benign group
is randomly subsampled to 5,000 records (fixed seed=42, `random.Random(42).sample(...)`,
~6:1 benign:pathogenic ratio) purely for VEP query budget, not based on any outcome. All 829
pathogenic records are retained in full (the constrained side of the imbalance). This is
documented here rather than silently done.

## Pre-registered sensitivity check (Standard tier requires >=1)

**Splice-proximity confound control.** The novelty-check literature is explicit that synonymous
variants can be pathogenic via splicing disruption (exonic splicing enhancer/silencer loss),
NOT via codon-optimality/mRNA-stability -- a real, literature-documented confound for this
exact question, not a hypothetical one. Pre-registered secondary analysis: repeat the primary
Mann-Whitney test restricted to variants ≥10bp from the nearest exon/intron boundary (using
GENCODE exon coordinates already fetched in this repo, `scripts/fetch_gencode_hg19_stranded.py`
/ `fetch_gencode_stranded.py`), to reduce (not eliminate) splice-driven contamination of the
"Pathogenic" bucket. This is reported regardless of outcome, BH-corrected jointly with the
primary test.

## Natural Language Statement

We estimate the Mann-Whitney U / Cliff's delta effect size of codon-usage-frequency change
(ALT vs REF codon, Kazusa human table) between ClinVar Pathogenic and Benign synonymous SNVs,
genome-wide, with a pre-registered splice-proximity-restricted sensitivity check, BH-corrected
across both tests.

## What This Does NOT Mean

1. A positive result does NOT mean codon-usage delta alone is a clinically useful predictor --
   published ensemble tools already combine this with several other features specifically
   because single features underperform; this only tests standalone signal, not utility.
2. A positive result does NOT establish that mRNA-stability/translation-elongation is the
   causal mechanism for any specific variant -- splicing disruption is a real, documented
   alternative mechanism for "pathogenic synonymous" variants (see sensitivity check above);
   the primary test cannot distinguish the two mechanisms, only the sensitivity check partially
   controls for it.
3. A negative result does NOT mean codon optimality is irrelevant to disease -- only that this
   single simple proxy, in isolation, does not discriminate on this dataset; established
   ensemble predictors' success does not require any single feature (including this one) to be
   independently discriminative.
4. Does NOT establish causality in either direction -- descriptive/predictive association only,
   no DAG, no identifiability analysis (this is not a causal-tier question as designed).

## Go/No-Go Criterion

- PROMOTE: primary test meets MCID AND sensitivity check trends in the same direction
  (same sign, even if it doesn't independently meet MCID after BH correction).
- REPEAT: primary test meets MCID but sensitivity check reverses direction or is far weaker
  (suggests splice-confound driven, not a clean codon-optimality signal) -- would need a real
  splice-disruption predictor (e.g. SpliceAI) to properly deconfound, out of this session's scope.
- REJECT: primary test does not meet MCID -> null_results/.
