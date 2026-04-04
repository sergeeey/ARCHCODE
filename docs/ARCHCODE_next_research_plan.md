# ARCHCODE Next Research Plan

**Created:** 2026-03-09
**Status:** Research planning layer — does NOT modify frozen/submitted manuscript
**Branch context:** Applies to both `feature/v4-prioritization-framework` (core) and `feature/follow-up-structural-framework` (extensions)

---

## A. Core Conclusions (Anchored from v4 submission)

### What ARCHCODE is

1. **Tissue-aware structural prioritization engine.** ARCHCODE identifies which enhancer-proximal variants to test first via Capture Hi-C and RT-PCR. It is not an independent pathogenicity predictor and does not replace sequence-based tools (VEP, CADD, SpliceAI).

2. **3D adds value as triage / experimental bridge.** The primary utility is narrowing the search space: from thousands of VUS to dozens of structurally suspicious candidates that warrant targeted contact assays. The 3D layer converts an open-ended functional screen into a focused experiment.

3. **Strongest validity zone: enhancer-proximal, tissue-matched, structurally suspicious variants.** ARCHCODE discrimination is maximal within 1 kb of H3K27ac peaks (7x average ΔLSSIM), at tissue-matched loci (HBB Δ=0.111 vs GJB2 Δ=0.000), for variants that existing tools miss (Q2b class).

4. **Q2a/Q2b decomposition is central.** 79.3% of apparent VEP-ARCHCODE discordance reflects VEP coverage gaps (Q2a), not genuine mechanistic disagreement. Only Q2b (54 variants across 9 loci, 25 at HBB) represents the true structural blind spot where ARCHCODE provides unique information.

5. **TAD heuristics alone are insufficient.** Binary TAD membership (inside/outside boundary) does not capture enhancer-promoter contact dynamics. ARCHCODE's contact-matrix approach models occupancy gradients, CTCF barrier permeability, and Kramer kinetics — continuous rather than categorical.

6. **Tissue mismatch is a primary failure mode.** At tissue-mismatched loci (SCN5A/cardiac, GJB2/cochlear in K562 model), ARCHCODE produces null results (ΔLSSIM ≤ 0.006). This is a feature, not a bug — it defines the domain boundary. But it means ARCHCODE cannot be applied naively to any locus without verifying enhancer landscape relevance.

---

## B. Priority Computational Experiments

### B1. Ablation study: what does 3D add?

Compare four models on the same 30,318-variant dataset:
- **Nearest-gene only:** pathogenicity = f(distance to TSS)
- **Epigenome-only:** pathogenicity = f(H3K27ac overlap, CTCF proximity)
- **Epigenome + 3D (simplified):** pathogenicity = f(TAD membership, contact frequency)
- **ARCHCODE (full):** LSSIM from loop extrusion simulation

Metric: AUC for P/LP vs B/LB separation within enhancer-proximal variants only (the zone where ARCHCODE claims advantage). If nearest-gene already achieves comparable AUC, the 3D simulation overhead is unjustified.

### B2. Leave-one-locus-out evaluation

For each of the 9 primary loci: train threshold on 8, test on 1. Report per-locus AUC, sensitivity at FPR ≤ 1%, and pearl detection rate. This tests whether HBB-derived insights generalize — or whether HBB is an outlier whose performance inflates the aggregate.

### B3. Tissue-mismatch negative controls

Formalize the existing null results (SCN5A, GJB2 = zero pearls) into a structured negative control analysis. For each locus, compute ΔLSSIM using both matched and mismatched cell-type enhancer annotations (e.g., HBB with HepG2 enhancers, LDLR with K562 enhancers). Quantify the tissue-mismatch penalty as a ratio.

### B4. Threshold robustness analysis

Extend the existing threshold sweep (0.88–0.98) with:
- Bootstrap confidence intervals on pearl counts
- Sensitivity to CTCF peak calling stringency (±1 peak)
- Sensitivity to enhancer occupancy ±20%
- Report stability zone (threshold range where pearl count is constant ±10%)

### B5. Contact-metric robustness

Replace SSIM with alternative contact comparison metrics:
- Pearson correlation of flattened matrices
- Stratum-adjusted correlation (SCC, used in Hi-C reproducibility)
- Insulation score difference at variant position
- Virtual 4C signal change (single-row extraction)

If pearl identification is SSIM-specific, the finding is fragile. If robust across metrics, the structural signal is real.

### B6. Public dataset watchlist for iQTL / allele-specific loops

Monitor for datasets that would enable direct validation:
- iQTL maps linking genetic variants to 3D contact changes (currently rare)
- Allele-specific loop calls from phased Hi-C (e.g., GM12878, K562)
- Single-cell Hi-C with variant phasing

See `docs/ARCHCODE_dataset_watchlist.md` for specific resources.

---

## C. Priority Wet-Lab Experiments

### C1. HBB Q2b top candidates (3–5 variants)

**Target variants:** c.-79A>C, c.-80T>C, c.-138C>A (promoter cluster); c.249G>C, c.50dup (coding with structural signal). All are ClinVar pathogenic/likely pathogenic, invisible to VEP/SpliceAI/CADD, and predict LSSIM < 0.95.

**Primary assay:** Capture Hi-C (HiCap or Tri-C) in HUDEP-2 cells (human erythroid progenitor) carrying the variant allele. Compare contact frequency at HBB promoter–LCR HS2 interaction against isogenic WT.

**Readout:** If ΔSSIM_predicted correlates with ΔContact_observed (r > 0.5), ARCHCODE structural predictions have experimental support. If not, the model needs recalibration or the mechanism is activity-based, not contact-based.

### C2. Activity vs architecture disentangling

**Problem:** A variant near an enhancer could disrupt gene activity (via TF binding site loss) or chromatin architecture (via occupancy change) or both. ARCHCODE only models the second.

**Design:** For each Q2b candidate, measure both:
- Contact change: Capture Hi-C (architecture)
- Expression change: RT-qPCR of HBB mRNA (activity)
- Enhancer activity: H3K27ac CUT&Tag at the enhancer

If contact changes without expression change → architecture-only effect (ARCHCODE's domain). If expression changes without contact change → activity-only (outside ARCHCODE's scope). If both change → coupled mechanism (most likely for promoter variants).

### C3. Targeted contact assay options (ranked by cost/feasibility)

| Assay | Resolution | Throughput | Cost/sample | Best for |
|-------|-----------|------------|-------------|----------|
| Capture Hi-C (HiCap) | 1–5 kb | Low (1 viewpoint) | ~$500 | Single locus validation |
| Tri-C | 1 kb | Low | ~$300 | Multi-way contacts |
| 4C-seq | 5–10 kb | Medium | ~$200 | Quick survey |
| Micro-C | 200 bp | Low | ~$2,000 | Nucleosome-resolution |
| FISH (3D-FISH) | 100 nm | Medium | ~$100 | Visual confirmation |

**Recommendation:** Start with 4C-seq (cheapest, sufficient resolution) for 3 variants, then Capture Hi-C for top hit.

### C4. Negative tissue/context controls

Include at minimum:
- Same variants in a non-erythroid cell type (e.g., HEK293, MCF7) → expect null contact change
- A tissue-mismatched locus variant (e.g., SCN5A variant in HUDEP-2) → expect null
- A coding-only variant far from enhancers (e.g., HBB c.92+1G>T canonical splice) → expect expression change but NOT contact change

### C5. Minimal pilot package for collaborators

See `docs/ARCHCODE_collab_experiments_onepager.md` for the one-pager. The minimum viable experiment:
- 1 cell line (HUDEP-2)
- 3 variants (c.-79A>C, c.-80T>C, c.-138C>A)
- 1 assay (4C-seq with HBB promoter viewpoint)
- 1 negative control (same variants in HEK293)
- Timeline: ~8 weeks from cell culture to data
- Budget: ~$3,000–5,000

---

## D. Product Implications

### D1. Candidate routing sheet

For each input variant, ARCHCODE should output a routing decision:

```
VARIANT → [Tissue check] → [Enhancer proximity check] → [LSSIM computation] → ROUTING
  ├─ ROUTE A: Structural candidate (LSSIM < threshold, enhancer-proximal, tissue-matched)
  │           → Recommend: Capture Hi-C validation
  ├─ ROUTE B: Coverage gap (VEP null, ARCHCODE signal present)
  │           → Recommend: VEP re-annotation + structural follow-up
  ├─ ROUTE C: Concordant benign (VEP benign, ARCHCODE benign)
  │           → No structural concern
  ├─ ROUTE D: Outside domain (tissue mismatch, no enhancer landscape)
  │           → ABSTAIN: insufficient model coverage
  └─ ROUTE E: Coding-only (ARCHCODE null, VEP pathogenic)
              → Defer to sequence-based tools
```

### D2. Applicability gate

Before computing LSSIM, check:
1. Is the locus in a configured genomic window? (if not → ABSTAIN)
2. Is the cell type tissue-matched? (check ΔLSSIM gradient > 0.01)
3. Are there ≥2 enhancers within 50 kb? (if not → low-confidence)
4. Is Hi-C validation r > 0.25 for this locus? (if not → unvalidated)

See `docs/ARCHCODE_applicability_rules.md` for full rules.

### D3. Evidence ladder

| Level | Evidence | Claim allowed |
|-------|----------|---------------|
| 0 | LSSIM computed, no validation | "Computational structural prediction" |
| 1 | + Hi-C correlation r > 0.25 | "Model-supported structural disruption" |
| 2 | + Capture Hi-C contact change observed | "Experimentally confirmed contact disruption" |
| 3 | + Expression/phenotype correlation | "Functionally validated structural variant" |
| 4 | + Replicated in independent cohort | "Clinically actionable structural annotation" |

ARCHCODE v4 operates at Level 0–1. Level 2+ requires wet-lab follow-up.

### D4. "When to abstain" rules

ARCHCODE should output "INSUFFICIENT DATA" when:
- Locus has no configured enhancer landscape
- Tissue match score = "mismatch" and no tissue-specific enhancer data available
- Variant is >50 kb from nearest enhancer
- Variant type is missense (ARCHCODE has zero sensitivity to amino acid changes)
- Hi-C validation for the locus yields r < 0.15

### D5. Experiment recommendation output schema

```json
{
  "variant_id": "VCV002024192",
  "archcode_route": "A",
  "lssim": 0.904,
  "enhancer_distance_bp": 831,
  "tissue_match": "matched",
  "recommended_assay": "4C-seq",
  "recommended_cell_line": "HUDEP-2",
  "viewpoint": "HBB promoter (chr11:5,226,576–5,227,021)",
  "expected_contact_change": "Decreased LCR HS2-HBB contact frequency",
  "negative_control": "Same variant in HEK293",
  "confidence_tier": "Tier 1 (tissue-matched, enhancer-proximal, Hi-C validated)"
}
```

---

## E. Decision Tree

### What supports triage-only claims (current position)

- LSSIM discriminates P/LP vs B/LB at category level (AUC = 0.977 on HBB combined)
- Hi-C validation (r = 0.28–0.59) confirms model outputs are biologically plausible
- 9 orthogonal methods are blind to pearl variants → structural blind spot is real
- Q2a/Q2b decomposition shows most discordance is infrastructural, not mechanistic
- Cross-species conservation (17/17 direction preserved) → evolutionary signal

**Sufficient for:** "ARCHCODE identifies candidates for experimental follow-up"

### What would justify stronger mechanistic claims

- Capture Hi-C showing contact change at ≥3 pearl positions (r > 0.5 with LSSIM)
- CRISPR base editing of a pearl variant → measurable expression change in HUDEP-2
- Allele-specific Hi-C in heterozygous patient cells → phased contact disruption
- Multi-locus replication: TERT pearl candidates validated in tissue-matched cells (e.g., hTERT-immortalized line)

**Would enable:** "ARCHCODE predicts experimentally confirmed structural disruption"

### What evidence is still insufficient for clinical classification

Even with experimental validation, ARCHCODE alone cannot:
- Meet ACMG/AMP PS3/BS3 criteria without independent functional assay
- Replace segregation analysis (PP1/BS4)
- Substitute for population frequency data (PM2/BA1)
- Provide definitive pathogenicity assessment for individual patients

**ARCHCODE can contribute:** PP3-equivalent supporting evidence for structural disruption, within a multi-evidence framework. It is one line of evidence, not a standalone classifier.

---

## Cross-references

- Experiment backlog: `docs/ARCHCODE_experiment_backlog.md`
- Applicability rules: `docs/ARCHCODE_applicability_rules.md`
- Collaborator one-pager: `docs/ARCHCODE_collab_experiments_onepager.md`
- Dataset watchlist: `docs/ARCHCODE_dataset_watchlist.md`
- Follow-up code: branch `feature/follow-up-structural-framework`
