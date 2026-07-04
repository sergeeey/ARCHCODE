# ARCHCODE Applicability Rules

**Created:** 2026-03-09
**Status:** Research planning — does NOT modify frozen/submitted manuscript
**Purpose:** Explicit rules for when ARCHCODE should and should not be used

---

## Where ARCHCODE Should Be Used

### Tier 1 — High confidence (validated)

- **Locus:** HBB (chr11:5,210,000–5,305,000)
- **Cell type:** K562 (erythroid)
- **Hi-C validation:** r = 0.53–0.59
- **Pearl detection:** 27 pearls, stable across thresholds 0.88–0.95
- **Variant types:** promoter, splice_region, UTR, synonymous, intronic (enhancer-proximal)
- **Use case:** Prioritize ClinVar VUS and Q2b candidates for Capture Hi-C / RT-PCR follow-up

### Tier 2 — Moderate confidence (signal present, weaker)

- **Loci:** TERT (K562, matched, Δ=0.019), MLH1 (K562, partial), LDLR (HepG2 enhancers, partial), BCL11A (K562, Δ=0.014)
- **Hi-C validation:** r = 0.29–0.59 (locus-dependent)
- **Pearl detection:** 0–2 pearls at standard threshold (threshold-proximal)
- **Use case:** Structural screening with caveats; results require locus-specific threshold calibration (Table 7 in manuscript)

### Tier 3 — Low confidence (exploratory only)

- **Loci:** BRCA1 (MCF7 partial), TP53 (K562 partial), CFTR (mismatch), PTEN (partial)
- **Hi-C validation:** r = 0.29–0.50 or not validated
- **Pearl detection:** 0 robust pearls; BRCA1 24 candidates = threshold artifacts (common polymorphisms)
- **Use case:** Hypothesis generation only; not for prioritization

---

## Where ARCHCODE Should NOT Be Used

### Absolute contraindications

1. **Tissue-mismatched loci without matched enhancer data.** SCN5A (cardiac), GJB2 (cochlear), HBA1, GATA1 in K562 model produce ΔLSSIM ≤ 0.006. Using these results for prioritization would be scientifically invalid.

2. **Missense variant pathogenicity assessment.** ARCHCODE has zero sensitivity to amino acid changes. Missense variants alter protein function, not chromatin architecture. Use VEP, CADD, AlphaMissense instead.

3. **Standalone clinical variant classification.** ARCHCODE cannot meet ACMG/AMP criteria alone. It is one line of evidence (PP3-equivalent for structural disruption), not a classifier.

4. **Variants >50 kb from nearest enhancer.** Outside the enhancer-proximal zone, ARCHCODE discrimination drops to background noise (ΔLSSIM < 0.005).

5. **Loci without configured enhancer/CTCF landscape.** Running ARCHCODE on an unconfigured region produces meaningless output — the model requires explicit enhancer positions and CTCF sites as input.

### Relative contraindications (use with extreme caution)

6. **Loci with Hi-C r < 0.25.** Model predictions are weakly grounded in experimental data. Results should be flagged as "unvalidated model output."

7. **Common polymorphisms (gnomAD AF > 0.01).** High allele frequency is strong evidence against pathogenicity regardless of LSSIM score. ARCHCODE should not override population genetics.

8. **Coding variants with clear VEP/CADD signal.** If VEP already classifies a variant as pathogenic with high confidence, ARCHCODE adds no information (the mechanism is sequence-level, not structural).

---

## Required Inputs for Valid Interpretation

| Input | Source | Required? | Notes |
|-------|--------|-----------|-------|
| Genomic coordinates (GRCh38) | ClinVar / user | Yes | Must be within configured window |
| Variant type | VEP annotation | Yes | For routing (missense → abstain) |
| Locus configuration | `config/locus/*.json` | Yes | Enhancers, CTCF sites, window |
| Cell-type enhancer peaks | ENCODE H3K27ac | Yes | Tissue match determines confidence |
| CTCF ChIP-seq peaks | ENCODE | Yes | Barrier positions |
| Hi-C validation correlation | Pre-computed | Recommended | Determines confidence tier |
| VEP/CADD scores | Ensembl / CADD server | Recommended | For concordance/discordance routing |
| gnomAD allele frequency | gnomAD v4 | Recommended | For population filter |
| ClinVar classification | NCBI | Recommended | For training/evaluation context |

---

## Unsupported Scenarios

| Scenario | Why unsupported | Alternative |
|----------|----------------|-------------|
| De novo variant in unconfigured locus | No enhancer landscape to simulate | Configure locus first using ENCODE data |
| Structural variants (CNV, inversions) | Model assumes point mutations affecting occupancy | Use specialized SV tools (AnnotSV, SVScore) |
| Somatic cancer mutations | Model calibrated for germline; somatic context differs | Future work (cancer somatic pearls in backlog) |
| Pharmacogenomic interactions | Follow-up branch only; not validated | See `feature/follow-up-structural-framework` |
| Multi-variant haplotype effects | Single-variant model; no epistasis | ARS proof-of-concept explores additive model |
| Non-human genomes | Only human GRCh38 configured | Mouse cross-species done for HBB only (r=0.82) |

---

## Confidence Tiers — Decision Matrix

```
INPUT VARIANT
    │
    ├─ Is locus configured? ──── NO ──→ ABSTAIN (no model coverage)
    │       │
    │      YES
    │       │
    ├─ Is variant missense? ──── YES ─→ DEFER to VEP/CADD (zero ARCHCODE sensitivity)
    │       │
    │       NO
    │       │
    ├─ Tissue match? ─── MISMATCH ──→ ABSTAIN (insufficient enhancer data)
    │       │
    │   MATCHED/PARTIAL
    │       │
    ├─ Distance to enhancer?
    │   │
    │   ├─ ≤1 kb ───→ HIGH CONFIDENCE (7× discrimination)
    │   ├─ 1–10 kb ─→ MODERATE CONFIDENCE
    │   ├─ 10–50 kb ─→ LOW CONFIDENCE
    │   └─ >50 kb ──→ ABSTAIN (below detection limit)
    │
    ├─ Hi-C validation for locus?
    │   │
    │   ├─ r > 0.40 ─→ TIER 1 (validated)
    │   ├─ r 0.25–0.40 → TIER 2 (moderate)
    │   └─ r < 0.25 ─→ TIER 3 (exploratory only)
    │
    └─ LSSIM result?
        │
        ├─ < per-locus threshold ─→ STRUCTURAL CANDIDATE → recommend experiment
        ├─ 0.95–0.99 ────────────→ AMBIGUOUS → flag for review
        └─ ≥ 0.99 ───────────────→ STRUCTURAL UNLIKELY → no structural concern
```

---

## Version History

- v1.0 (2026-03-09): Initial version based on v4 submission data and strategic review
