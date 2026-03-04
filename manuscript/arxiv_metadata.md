# arXiv Submission Metadata — ARCHCODE

## Title

ARCHCODE: 3D Chromatin Loop Extrusion Simulation Reveals Enhancer-Proximal Structural Pathogenicity Across Nine Genomic Loci

## Authors

Sergey V. Boyko

## Affiliation

Independent Researcher, Almaty, Kazakhstan

## Email

sergeikuch80@gmail.com

## Category

**Primary:** q-bio.GN (Genomics)
**Cross-list:** q-bio.QM (Quantitative Methods)

## Abstract (plain text for arXiv form)

Sequence-based variant effect predictors (VEP) evaluate pathogenicity through protein-coding impact and splice motif disruption, but structurally-mediated effects on 3D chromatin topology remain outside their scope. We developed ARCHCODE, an analytical mean-field loop extrusion simulator implementing Kramer kinetics for cohesin barrier crossing, and applied it to 30,318 clinically classified variants across nine genomic loci: HBB (1,103), CFTR (3,349), TP53 (2,794), BRCA1 (10,682), MLH1 (4,060), LDLR (3,284), SCN5A (2,488), TERT (2,089), and GJB2 (469). ARCHCODE identifies 27 "pearl" variants on HBB — VEP-blind yet structurally disruptive — and reveals that enhancer proximity is the primary driver of structural discrimination: variants within 1 kb of enhancers show 7-fold greater pathogenic-benign separation. A tissue-specificity gradient from matched (HBB) through expressed (TERT) to mismatched (SCN5A, GJB2) negative controls defines the domain of applicability. Per-locus threshold calibration demonstrates that universal thresholds are locus-specific; locus-calibrated thresholds improve sensitivity from 79.6% to 92.9% for HBB while maintaining specificity. We propose structural simulation as a complementary, hypothesis-generating layer that reveals a dimension of pathogenicity invisible to sequence-based tools.

## Comments

30,318 variants, 9 genomic loci, 23 references, 55 pages. Source code: https://github.com/sergeeey/ARCHCODE

## License

CC BY 4.0

---

## Submission Instructions (step-by-step)

### Prerequisites

1. arXiv account at https://arxiv.org (register if needed; takes ~24h for first approval)
2. PDF file: `ARCHCODE_arXiv_2026.pdf` (55 pages, ~960 KB)

### Step-by-step

1. **Go to** https://arxiv.org/submit
2. **Choose submission type:** "PDF" (single file upload)
3. **Upload** `ARCHCODE_arXiv_2026.pdf`
4. **Fill metadata:**
   - **Title:** copy from above
   - **Authors:** `Sergey V. Boyko`
   - **Abstract:** copy plain text from above
   - **Primary category:** `q-bio.GN` (Genomics)
   - **Cross-list categories:** `q-bio.QM` (Quantitative Methods) — optional but recommended
   - **Comments:** `30,318 variants, 9 genomic loci, 23 references, 55 pages. Source code: https://github.com/sergeeey/ARCHCODE`
   - **License:** CC BY 4.0 (recommended for open science)
5. **Review** the preview — check that tables and Greek symbols render correctly
6. **Submit**

### After submission

- arXiv assigns a temporary submission ID immediately
- Moderation typically takes 1-2 business days for q-bio
- Once accepted: permanent arXiv ID (e.g., 2603.XXXXX) + DOI
- Paper appears on next business day's listing after acceptance

### Important notes

- arXiv does NOT require peer review — it's a preprint server
- First-time submitters may need endorsement from an existing arXiv author in q-bio
  - If endorsement needed: email a colleague who has published in q-bio.GN
  - Alternative: submit to q-bio.QM first (sometimes fewer endorsement requirements)
- You can update the paper later with `Replace` (new version, old versions preserved)
- arXiv provides a permanent, citable DOI: `10.48550/arXiv.XXXX.XXXXX`
