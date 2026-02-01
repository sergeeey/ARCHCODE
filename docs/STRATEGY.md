# ARCHCODE Strategy (high-level)

This document records high-level product and focus decisions for ARCHCODE. It does not affect code behavior.

---

## Focus and prioritization

- **Primary focus**: ARCHCODE as a publication-ready loop extrusion simulator and, longer term, as a platform for in silico experiments (e.g. ARCHCODE Pharma).
- **Resource allocation**: Prioritize scientific publication and B2B positioning (e.g. pharma in silico screening) over generic “research tool” only. Other projects (e.g. GeoScan, DeepTrust) can be deprioritized or delegated to align with this focus.
- **No code impact**: These are product/portfolio choices; the repository remains a single product (ARCHCODE).

---

## Future differentiators (roadmap)

- **In silico CRISPR**: Virtual deletion/inversion of genomic regions to predict loop and TAD changes. Commercial angle: B2B SaaS for pharma (test editing before wet lab). Pricing reference: comparable to molecular modeling platforms (e.g. Schrödinger).
- **Positioning**: “Affordable in silico screening for gene therapy” — target smaller biotechs that cannot run large-scale CRISPR screens in vivo.
- **Exit**: Long-term options include acquisition by biotech (e.g. BioNTech, Moderna) or standalone growth; timeline 5–7 years.

---

## Validation and publication

- **Publication**: Validation must be reported against **experimental Hi-C** (e.g. Rao et al. 2014), not mock AlphaGenome. See README, METHODS.md, KNOWN_ISSUES.md, and docs/ALPHAGENOME.md.
- **AlphaGenome**: Optional integration when API is available; mock in v1.0. Do not claim “AlphaGenome-validated” without explicit disclaimer.

---

*Last updated: 2026-02-01. For detailed roadmap and technical limits, see KNOWN_ISSUES.md and AUDIT_RESPONSE.md.*
