# ARCHCODE Structural Blind Spot — One-Page Summary for Collaborators

**Project:** ARCHCODE (3D chromatin loop extrusion simulation)  
**Finding:** 27 "pearl" variants on HBB are pathogenic in ClinVar and show structural disruption in our model (LSSIM &lt; 0.95) but are **invisible** to VEP, SpliceAI, CADD, and MPRA — a structural blind spot for sequence-based and episomal assays.

**Evidence:** Nine orthogonal lines (VEP &lt; 0.30 for all 27; SpliceAI = 0.00 for 20 SNVs; CADD ambiguous; MPRA null; gnomAD 85% absent; conservation; Hi-C correlation r = 0.28–0.59; tissue gradient; genome-wide 13 loci). Virtual CRISPR in silico: top promoter pearls show ~17% promoter–LCR contact drop.

**Ask:** Experimental validation in erythroid cells (K562 / HUDEP-2): (1) **RT-PCR** — aberrant splicing or transcript change at pearl positions; (2) **Capture Hi-C** — promoter–LCR contact change vs wild-type. We provide a shortlist of 3–5 priority variants and a formal protocol.

**Variant panel (top 3):** c.-79A>C, c.-80T>C, c.-138C>A (HBB promoter); full list and LSSIM in `results/pearl_validation_shortlist.json`.

**Success criterion:** ≥1 variant shows significant effect in the direction predicted by ARCHCODE (contact drop or splice/transcript change). Negative and inconclusive results are reported as such; no overclaim.

**Deliverables we provide:** Protocol ([docs/VALIDATION_CROSSLAB_PROTOCOL.md](VALIDATION_CROSSLAB_PROTOCOL.md)), variant table, ARCHCODE predictions, preprint/manuscript when submitted.

**Contact:** Repository issues or maintainer contact as per repository.
