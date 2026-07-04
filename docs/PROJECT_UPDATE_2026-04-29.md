# ARCHCODE Project Update — 2026-04-29

**Status:** ✅ **SUBMISSION READY** — Spectral validation complete, comprehensive audit passed  
**Version:** v5.0 (Spectral Validation Edition)  
**Branch:** feature/stress-biology-atp-mutagenesis  
**Last Commits:** 4c362fa (spectral), 3a4fd90 (phantom fix)

---

## What Changed Since v4.0 (2026-03-09)

### Major Additions

**1. Spectral Fragility Validation (H1-H4)**
- **H1 Cross-locus:** SFI validated on 3 loci (HBB d=1.36, TP53 d=0.87, BRCA1 d=0.04 negative control)
- **H2 Phase boundary:** HYPOTHESIS REJECTED (0/20 pearls in critical regime, all cluster in promoter)
- **H3 TDRA:** Skipped (MPRA-ClinVar mapping too complex for exploratory scope)
- **H4 Codeword distance:** REINTERPRETED (dosage-sensitivity = structural variance 19.9% HBB vs <1% BRCA1/TP53)

**Key Scientific Insight:**  
Dosage-sensitive loci exhibit **narrow spatial vulnerability zones** (73bp HBB promoter cluster) with **high structural variance** (19.9% disruptive), not higher median robustness. This refines hypothesis from "dosage-sensitive loci are robust" to "dosage-sensitive loci have focal spatial constraints under purifying selection."

**2. Comprehensive Integrity Audit**
- 48/48 checks PASS (100%)
- Phantom reference fixed: Sabaté 2025 Nature Genetics → Sabaté 2024 bioRxiv (commit 3a4fd90)
- No mock data, no fabricated metrics, honest null results (H2 rejected, H4 reinterpreted)
- All manuscript numbers match CSV files (18/18 verified)

**3. Manuscript Integration**
- New section: `manuscript/spectral_results.typ` (78 lines, all 4 hypotheses)
- Integrated at line 1387 of `body_content.typ`
- Figures: S2 (phase boundary), S3 (codeword distance), S4 (LSSIM distributions)

---

## Obsidian Documentation Updated

**New files created:**
1. `results/SPECTRAL_VALIDATION_COMPLETE_2026-04-29.md` — comprehensive final report (H1-H4, cross-hypothesis synthesis, submission readiness)
2. `results/SCIENTIFIC_ABSTRACT_v5_2026-04-29.md` — updated abstract with spectral validation, supersedes 2026-03-06 version
3. `docs/PROJECT_UPDATE_2026-04-29.md` — this file (changelog)

**Updated files:**
4. `results/spectral_sprint_log.md` — Session 2026-04-29 H2-H4 completion appended
5. `.claude/memory/activeContext.md` — synchronized with Obsidian via write_note (already current from git)

**Superseded files (legacy, keep for history):**
- `results/SCIENTIFIC_ABSTRACT.md` (2026-03-06) — use v5 instead
- `manuscript/PHASE_A_COMPLETE.md` (2026-02-05) — old Hi-C validation r=0.16
- `docs/release_v4_summary.md` (2026-03-09) — pre-spectral version

---

## Key Metrics Summary

| Metric | Value | Source |
|--------|-------|--------|
| Total variants analyzed | 32,201 (9 loci) | Clinical atlases |
| HBB pearls | 27 (14 unique, 15 in 73bp cluster) | HBB_Clinical_Atlas.csv |
| Spectral validation loci | 3 (HBB, TP53, BRCA1) | H1 cross-locus |
| SFI effect sizes | d=1.36 (HBB), 0.87 (TP53), 0.04 (BRCA1) | spectral_results.typ |
| HBB structural variance | 19.9% disruptive (LSSIM<0.95) | H4 analysis |
| Phase boundary null | 0/20 pearls in Φ≈1 regime | H2 parameter sweep |
| Audit compliance | 48/48 checks PASS (100%) | AUDIT_REPORT_20260429.md |
| Manuscript sections | 9 + 7 supplementary + spectral | main.typ |
| Figures | 25 + 3 spectral (S2-S4) | figures/ |

---

## Submission Status

| Platform | Status | Next Action |
|----------|--------|-------------|
| **GitHub** | Current (3a4fd90, 4c362fa) | Push with tags |
| **Zenodo** | v2.17 LIVE | Update to v2.18 (add spectral) |
| **Research Square** | rs-9090074 LIVE (taxonomy) | Wait review feedback |
| **arXiv** | Awaiting endorsement (B9P837) | Follow-up endorsers |
| **bioRxiv** | Rejected ×2 (no affiliation) | Resubmit post-Ronin (~May 10) |
| **Ronin Institute** | Applied 2026-03-12 | Decision ~2026-05-10 |

---

## Immediate Next Steps (Week 1)

### Technical
1. **Compile final PDF:**
   ```bash
   cd D:/ДНК/manuscript
   python -c "import typst; typst.compile('main.typ', output='main.pdf', root='..')"
   ```
2. **Push to GitHub:**
   ```bash
   git push origin feature/stress-biology-atp-mutagenesis --tags
   git tag v5.0-spectral-validation
   git push origin v5.0-spectral-validation
   ```

### Publishing
3. **Update Zenodo:** Upload v2.18 archive with spectral validation section
4. **Send endorser follow-ups:** Nora (UCSF), Giorgetti (Basel), Hansen (MIT) — 2 weeks since last contact
5. **Prepare bioRxiv resubmit:** Ready for immediate upload post-Ronin approval

### Documentation
6. **Update README.md:** Add spectral validation to "What Survived" section
7. **Create release notes:** v5.0 changelog (H1-H4, audit, phantom fix)

---

## Optional Extensions (Month 1-2)

### Scientific
- H3 TDRA pipeline (build HGVS→ClinVar mapper)
- Cross-locus H4 validation (HBA1, GATA1, SOX2 structural variance)
- FOXP3/BCL11A mutagenesis expansion (18 loci total)

### Validation
- Wet-lab partner outreach (Capture Hi-C for HBB 73bp cluster)
- Multi-tissue simulation (HUDEP-2 enhancers instead of K562)
- ML integration (Random Forest on LSSIM + SFI + category)

### Infrastructure
- Parameter sweep parallelization (5×5×5 grid = 125 simulations, $5-10 AWS)
- Contact matrix persistence refactor (export 50×50 arrays for all loci)
- Automated figure generation pipeline (reproducible S2-S4)

---

## Lessons from This Sprint

### What Worked
1. **Falsification-first approach:** H2 rejection refined hypothesis instead of hiding null result
2. **Negative controls:** BRCA1 synonymous (d=0.04) proved SFI specificity
3. **Cross-hypothesis synthesis:** H2 null + H4 variance + H1 SFI all point to spatial constraint model
4. **Comprehensive audit:** 48 checks caught phantom reference before submission
5. **Obsidian integration:** Real-time documentation preserved decision points

### What Was Refined
1. **Dosage-sensitivity model:** "Robust loci" → "Focal vulnerability zones with high variance"
2. **Phase boundary theory:** Parameter-sensitive → Position-dependent (promoter clustering)
3. **Codeword distance:** Min(LSSIM) alone insufficient, variance analysis required

### What to Avoid
1. **Exploratory scope creep:** H3 TDRA skipped instead of half-implemented (correct decision)
2. **Confirmation bias:** H4 median contradiction forced reinterpretation, not data manipulation
3. **Premature parameter tuning:** Kept manual calibration instead of fitting to H2 null result

---

## Project Governance

**Scientific Integrity:** 100% (CLAUDE.md compliance, audit verified)  
**Reproducibility:** Full (git SHA 4c362fa + 3a4fd90, all scripts public)  
**Transparency:** High (null results documented, limitations stated)  
**Code Quality:** Production-ready (ruff format, type hints, error handling)  

**Compliance Matrix:**
- ✅ NO PHANTOM REFERENCES (Sabaté 2025 fixed to bioRxiv 2024)
- ✅ NO INVISIBLE SYNTHETIC DATA (all simulations labeled)
- ✅ NO HARDCODED FITTED PARAMS (manual calibration from literature)
- ✅ HONEST NULL RESULTS (H2 rejected, H4 reinterpreted)
- ✅ TRANSPARENT LIMITATIONS (H3 skipped, LSSIM threshold exploratory)

---

## Version History

- **v5.0 (2026-04-29):** Spectral validation complete (H1-H4), audit PASS, phantom fix
- **v4.0 (2026-03-09):** Discordance taxonomy (Q2a/Q2b), Tier system, TERT validation
- **v2.17 (2026-03-20):** FOXP3/BCL11A mutagenesis, multi-locus atlas S7
- **v2.16 (2026-03-01):** AlphaGenome real API validation, MPRA cross-validation
- **v2.15 (2026-02-05):** Phase A Hi-C validation (r=0.16 pilot)

---

## Contact & Links

**Author:** Sergey V. Boyko  
**Email:** sergeikuch80@gmail.com  
**ORCID:** 0009-0009-2178-5701  
**GitHub:** https://github.com/sergeeey/ARCHCODE  
**Zenodo (v2.17):** https://zenodo.org/records/18908214  
**Research Square:** DOI: 10.21203/rs.3.rs-9090074/v1  

**Affiliation (pending):** Ronin Institute RIIS 2.0

---

_Project update compiled: 2026-04-29_  
_Next update: Post-Ronin decision (~2026-05-10)_
