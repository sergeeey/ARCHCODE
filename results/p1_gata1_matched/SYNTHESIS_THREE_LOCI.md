# Three-Locus Synthesis — What We Now Know (2026-06-05)

## Pattern across HBB, GATA1, HBA1

| Locus | Tissue source | Variant spread | Within-cat AUC (best) | K2 | Verdict |
|---|---|---|---:|---|---|
| HBB | HUDEP-2 Hi-C + K562 CTCF | 95kb window, but benign 87.7% intronic | 0.524 (intronic, n=667) | fires | FAIL |
| GATA1 | **K562** (wrong tissue) | **3,117 bp coding only** | 0.464 missense (wrong dir) | fires | FAIL |
| HBA1 | **K562** (wrong tissue) | coding-dominated | ~0.50 (not run fully) | expected | FAIL |
| BCL11A | unknown | not_observed_graphql | — | — | FAIL |

**Four loci. Four failures. Consistent pattern.**

## The structural problem — not just statistics

The failures share a root cause beyond statistics. The simulation uses:
1. **Analytical (mean-field) contact maps**, not measured Hi-C
2. **K562 CTCF/enhancer features** for erythroid genes (GATA1, HBA1) → wrong tissue
3. **Coding variants** dominating all atlases → LSSIM values are identical (same bin)
4. **CATEGORICAL_EFFECTS lookup** that makes LSSIM = f(category) by construction

The residual-signal hypothesis has a path to a fair test **only if**:
- Real measured Hi-C (correct erythroid tissue, e.g. HUDEP-2 — data already in repo for HBB)
- Non-coding, regulatory variants (promoter, enhancer, CTCF-binding disruption)
- A locus where erythroid-specific 3D structure is the mechanistic claim

**HBB with HUDEP-2 Hi-C data (`data/hudep2_wt_hic_hbb_locus.npy`)** is the only
location in the current repo that has the right tissue data. But even there, the
within-category test was null (intronic AUC 0.524, p=0.80). This is partially
explained by the degenerate intronic benign group — the right test is not possible
on HBB's ClinVar data.

## What the framework can honestly say

The falsification exercise across four loci **is itself the paper**:

> We applied a systematic falsification gate (category baseline → matched-category
> test → tissue-sanity check → position baseline) to four erythroid loci. In every
> case, LSSIM either:
> (a) adds no information over consequence category, or
> (b) shows the wrong direction in the most powered category, or
> (c) is computed on the wrong-tissue regulatory landscape.
>
> These negative results define exactly what a fair test requires: correct-tissue
> Hi-C, regulatory non-coding variants, and pre-registered matched controls.
> The ARCHCODE engine survives as a hypothesis-generating tool under these
> constraints; the pathogenicity-prediction claim does not.

## What to do next (ranked)

### A. The only credible residual-signal test remaining in the current data
**HBB × HUDEP-2 Hi-C** — the repo has `data/hudep2_wt_hic_hbb_locus.npy`.
Replace the analytical contact maps with the measured HUDEP-2 Hi-C for HBB variants,
run the matched-category test. This is the one case where tissue matches.
Even here, expect null (benign group is degenerate), but it is the scientifically
correct version of the experiment.

### B. Paper 3 — write it as what it is
The strongest framing is NOT "we found a signal" but:
> "We built a systematic matched-control falsification framework for 3D chromatin
> structural metrics, applied it to four loci, and characterized the conditions
> under which current analytical models fail the test. This framework is the
> contribution; the test conditions (right tissue, regulatory variants, real Hi-C)
> are the roadmap."

This is publishable at PLoS Computational Biology / Bioinformatics / PLOS Genetics
as a methodology + cautionary + framework paper. No positive signal required.

### C. EXP-004 threshold sensitivity (deferred but still useful)
Now it has a different meaning: not "does threshold 0.95 hold?" but "is the
null result threshold-independent?" Running sensitivity confirms the failure is
structural, not a threshold artefact. Easy to run, short section.

### D. Zenodo PDF immediate action (not deferred, zero cost)
The pre-reboot PDF on Zenodo still contains the phantom Sabaté 2025 reference and
clinical reclassification recommendations. Replacing or retracting it takes 1 day
and eliminates the scientific-misconduct risk entirely. This has nothing to do with
the analytical results and should not wait for Paper 3.
