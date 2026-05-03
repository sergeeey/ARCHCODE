# Cover Letter Addendum — Human Mutation Submission

**ADD TO EXISTING COVER LETTER** (`manuscript/cover_letter_HumanMutation.docx`)

Insert after main letter body, before closing signature.

---

## Data Provenance Note

**Important clarification for reviewers:**

The manuscript cites allele frequency data from two sources with different query dates:

1. **Primary dataset:** `gnomad_populations_pearls.csv` (May 1, 2026)  
   Contains 15 HBB promoter variants with population-stratified allele frequencies across 5 genetic ancestry groups (AFR, AMR, EAS, EUR, SAS).

2. **Coverage validation:** `gnomad_coverage_check.json` (May 2, 2026)  
   Re-queried two East Asian-enriched variants (VCV000015471, VCV000015466) with extended coverage to verify preliminary findings. Updated allele numbers (AN): 37,034 and 36,610 respectively (vs. initial query AN: 152,146).

**Key point:** The manuscript uses **updated values** from the May 2 coverage check for VCV000015471 (AF_EAS = 0.000648, AC=24/AN=37,034) and VCV000015466 (AF_EAS = 0.000464, AC=17/AN=36,610). The preliminary CSV file contains one superseded value (VCV000015471: 0.000193) and is included in the repository for transparency and reproducibility but is **not** the source of truth cited in the manuscript.

This two-stage querying approach reflects standard practice when initial results flag variants requiring validation with expanded datasets.

---

## Methodology Clarification

**PyPop Framework Reference:**

The manuscript adapts the population stratification **methodology** pioneered by the PyPop framework (Lancaster et al., 2024) but does **not** execute the PyPop software itself. Our analysis applies PyPop's cross-population meta-analysis principles to rare pathogenic-variant candidates (AF < 0.001) using a custom gnomAD v4 GraphQL query tool (`population_filter.py`). This distinction is important for reproducibility: reviewers can replicate our analysis using the provided script and gnomAD v4 API, independent of PyPop software installation.

We acknowledge the PyPop developers (Lancaster et al.) in the manuscript for inspiring this methodological adaptation.

---

## ARCHCODE Tool Disclosure

**Conflict of Interest Transparency:**

ARCHCODE, the structural variant prediction pipeline that identified the 15 HBB promoter variants analyzed in this study, was developed by the corresponding author (Zenodo DOI: 10.5281/zenodo.18908214, v2.17). This is disclosed in the manuscript FUNDING section ("Tool disclosure: ARCHCODE was developed by the author").

Importantly, the epidemiological context presented in this Brief Report uses **independent population genetics data** (gnomAD v4, 807,162 individuals) and does not rely on ARCHCODE for allele frequency determination or epidemiological analysis. The cross-population stratification findings are orthogonal to ARCHCODE's structural predictions and may help prioritize regulatory variants for follow-up.

---

## Brief Report Scope

This submission is a **proof-of-concept demonstration** (n=15 variants, single locus) that population stratification can identify potential epidemiology-discordant structural variant classifications. The Discussion section explicitly acknowledges limitations:

- Small sample precludes precise false positive rate quantification
- Single-locus analysis (HBB) limits generalizability
- Multi-locus validation (n≥50) needed for systematic error rate estimation

These caveats position the work appropriately as a **Brief Report** rather than a comprehensive validation study, consistent with *Human Mutation*'s scope for short reports demonstrating novel methodological approaches.

---

## Data Availability Commitment

All code, data, and analysis scripts are openly available:

- **GitHub:** https://github.com/sergeeey/ARCHCODE (commit 1415229)
- **Zenodo:** DOI: 10.5281/zenodo.18908214 (v2.17, archived)
- **gnomAD:** Public database (v4 exome + genome, 807,162 individuals)

Reviewers can fully reproduce the analysis from provided scripts and publicly available data sources.

---

**Suggested Insertion Point:**

Add these three sections after the main cover letter narrative, before the closing ("We look forward to your consideration...").

**Total addition:** ~500 words (keeps cover letter under 1 page if original is concise)

---

*Created: 2026-05-03*  
*Purpose: Address anticipated reviewer questions proactively*
