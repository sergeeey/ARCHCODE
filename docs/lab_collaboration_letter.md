# Lab Collaboration Letter Template — ARCHCODE Experimental Validation

**Purpose:** Outreach to experimental chromatin biology labs for wet-lab validation of ARCHCODE Q2b candidates.
**Attach:** Q2b_candidate_cards.md, fig_discordance_taxonomy.png

---

## Letter Template

**Subject:** Collaboration opportunity: Experimental validation of computationally predicted structural blind spot variants at the HBB locus

Dear Dr. [NAME],

I am writing to propose a collaboration to experimentally validate a specific class of genomic variants that are invisible to all current sequence-based annotation tools.

**Background.** We have developed ARCHCODE (Architecture-Constrained Decoder), an analytical chromatin loop extrusion model that predicts structural disruption at genomic loci from CTCF anchors, enhancer positions, and cohesin dynamics. Across 32,201 ClinVar variants at nine disease-associated loci, we identified 54 "structural blind spot" variants (Q2b) — variants where VEP explicitly scores low impact (0–0.5) but the structural model detects significant chromatin contact disruption.

**The key finding.** Q2b variants cluster 58-fold closer to annotated enhancers than sequence-channel variants (434 bp vs 25,138 bp; p = 2.5 × 10⁻³¹) and show tissue-dependent enrichment (Spearman ρ = 0.84, p = 0.005). At the HBB locus, all 25 Q2b variants are ClinVar pathogenic and absent from nine orthogonal annotations including SpliceAI, MPRA, and gnomAD v4.

**What we need.** Experimental validation of 5–7 priority Q2b candidates (see attached candidate cards) using:

1. **Capture Hi-C** in HUDEP-2 erythroid cells — to quantify enhancer–promoter contact frequency changes at mutant vs wild-type alleles
2. **RT-qPCR** — to measure HBB mRNA levels after erythroid differentiation
3. **CRISPR base editing** — to introduce specific variants into isogenic HUDEP-2 clones

**What we provide:**
- Complete computational analysis (32,201 variants, 9 loci, published on bioRxiv)
- Prioritized candidate list with specific genomic coordinates, predicted effect sizes, and success criteria
- All code and data publicly available (Zenodo DOI: 10.5281/zenodo.18867448)
- Manuscript draft ready for co-authorship

**Why this matters.** If confirmed, these variants would represent the first experimental demonstration that 3D chromatin topology creates a systematic blind spot for sequence-based variant annotation — a finding with immediate implications for clinical VUS interpretation in hemoglobinopathies and potentially all enhancer-regulated loci.

**Priority candidates (top 3):**

| Variant | LSSIM | VEP | CADD | Category | Proposed assay |
|---------|-------|-----|------|----------|----------------|
| c.50dup (K18fs) | 0.798 | 0.15 | N/A | frameshift | Capture Hi-C + RT-qPCR |
| c.93-33_96delins | 0.822 | 0.20 | N/A | splice | RT-PCR + minigene |
| c.-79A>C (CCAAT box) | 0.914 | 0.20 | 19.3 | promoter | EMSA + luciferase |

**Success criterion:** Capture Hi-C contact ratio (mutant/WT) ≤ 0.70 AND RT-qPCR HBB/GAPDH ≤ 0.50 in ≥3 independent HUDEP-2 clones (p < 0.05).

**Preprint:** [bioRxiv link — BIORXIV/2026/710343]
**Code:** https://github.com/sergeeey/ARCHCODE

I would welcome the opportunity to discuss this further. The candidate cards with full experimental protocols are attached.

Best regards,
Sergei Boiko
[Affiliation]
[Email]

---

## Target Labs (suggested)

Labs with HUDEP-2 + Capture Hi-C capability and HBB/hemoglobinopathy expertise:

1. **Douglas Higgs Lab** (Oxford) — α/β-globin chromatin architecture, Capture Hi-C pioneer
2. **Mitchell Weiss Lab** (St. Jude) — HUDEP-2 developer, erythroid gene regulation
3. **Vijay Sankaran Lab** (Broad/Boston Children's) — hemoglobin switching, CRISPR in erythroid
4. **Gerd Blobel Lab** (UPenn/CHOP) — 3D chromatin in erythropoiesis, GATA-1
5. **Job Dekker Lab** (UMass) — Hi-C/4C methodology, chromatin architecture
6. **Wouter de Laat Lab** (Hubrecht) — 4C-seq pioneer, enhancer-promoter contacts

## Attachments Checklist

- [ ] Q2b_candidate_cards.md (7 candidates with full protocols)
- [ ] fig_discordance_taxonomy.png (visual summary of structural blind spots)
- [ ] per_locus_verdict.csv (9-locus evidence summary)
- [ ] bioRxiv preprint PDF
