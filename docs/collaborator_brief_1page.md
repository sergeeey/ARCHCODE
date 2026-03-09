# ARCHCODE: Structural Prioritization of Enhancer-Proximal Variants

**One-Page Collaborator Brief | March 2026**

---

## The Problem

Sequence-based variant tools (VEP, CADD, SpliceAI) cannot detect pathogenic mechanisms arising from disruption of 3D chromatin contacts. Enhancer-proximal variants that alter loop extrusion dynamics are invisible to these tools — creating a systematic blind spot in clinical variant interpretation.

## What ARCHCODE Found

We analyzed **32,201 ClinVar variants** across 9 disease-associated loci using a polymer physics simulation of cohesin-mediated loop extrusion. Cross-tabulation against VEP/CADD revealed:

- **54 "true blind spot" variants (Q2b):** VEP scored them as low-impact, but ARCHCODE detects significant chromatin disruption
- **100% of Q2b variants** fall within 1 kb of annotated enhancers (vs 9% of sequence-flagged variants)
- The signal is **tissue-dependent**: strongest at erythroid-matched HBB (25 Q2b), absent at tissue-mismatched controls (0 Q2b)

## Top 5 Candidates for Experimental Validation

All are HBB locus, ClinVar pathogenic/likely pathogenic, absent from 9 orthogonal annotations:

| # | ClinVar ID | Position (GRCh38) | Type | LSSIM | Enhancer dist |
|---|-----------|-------------------|------|-------|--------------|
| 1 | VCV002024192 | chr11:5,226,796 | Splice acceptor | 0.822 | 528 bp |
| 2 | VCV000869358 | chr11:5,226,971 | Frameshift | 0.798 | 703 bp |
| 3 | VCV000801186 | chr11:5,226,598 | Missense | 0.909 | 330 bp |
| 4 | VCV000015208 | chr11:5,226,613 | Missense | 0.910 | 345 bp |
| 5 | VCV000869309 | chr11:5,226,596 | Other | 0.940 | 328 bp |

**PCHi-C confirmed:** All 5 reside in a bait fragment with 25 significant erythroblast interactions (CHiCAGO up to 10.5), including 5 LCR contacts.

## What We Propose

A targeted validation in **HUDEP-2 cells** (adult erythroid progenitors):

1. **Capture Hi-C** at the 5 candidate positions — does the variant disrupt local contact frequency?
2. **RT-qPCR** for HBB expression — does disruption reduce beta-globin output?
3. **CRISPR base editing** at top 2 positions — causal confirmation

**Estimated effort:** 3–4 months, 1 postdoc, standard molecular biology reagents.

## Why This Is Low-Cost / High-Yield

- Candidates are already **ClinVar pathogenic** — clinical relevance established
- The structural mechanism is **specific and testable** — contact frequency at defined positions
- **Positive result** = first demonstration that 3D chromatin disruption drives pathogenicity at enhancer-proximal variants invisible to sequence tools
- **Negative result** = equally informative — falsifies the structural blind spot hypothesis, publishable either way

## Resources

- **Preprint:** bioRxiv BIORXIV/2026/710343
- **Code + data:** https://zenodo.org/records/18867448 (CC BY 4.0)
- **Full reproducibility guide:** `REPRODUCE.md` in repository
- **Contact:** [your email]

---

*ARCHCODE is a structural prioritization engine, not a pathogenicity predictor. It identifies which variants to test first — not whether they are pathogenic.*
