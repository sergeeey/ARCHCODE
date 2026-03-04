# Active Context — ARCHCODE

**Last Updated:** 2026-03-04 (session 28-29: orthogonal validation + manuscript v2.8)
**Branch:** main
**Last Commit:** 638a5d9 — `feat: v2.8 orthogonal validation — SpliceAI null + MPRA cross-validation + Figure 10`
**GitHub:** https://github.com/sergeeey/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — REJECTED ("not complete research with new data")
**Zenodo DOI:** 10.5281/zenodo.18867051 (PUBLISHED, 2026-03-04)
**arXiv:** endorsement requested from Dr. Guang Shi (DIMES, polymer chromatin modeling), code B9P837
**Status:** v2.8 published on Zenodo. arXiv endorsement pending. gnomAD AF analysis complete.

---

## Текущий статус проекта

**Фаза:** v2.8 — orthogonal validation complete, arXiv submission pending

### Manuscript v2.8 (current) — what's new vs v2.7

1. **SpliceAI validation** — 20/20 pearl SNVs = 0.00 via Ensembl VEP REST API with SpliceAI plugin. Closes Limitation #4.
2. **MPRA cross-validation** — Kircher et al. 2019 (Nat Commun 10:3583), MaveDB urn:mavedb:00000018-a-1. 623 variants, HBB promoter 187bp, HEL 92.1.7 cells. Allele-specific match: n=22, r=−0.21 p=0.36. Informative null — MPRA = episomal, pearl = 3D structural.
3. **Figure 10** — AlphaGenome multimodal validation (dual-panel: signal concentration + 3-locus tissue gradient)
4. **Structural Blind Spot table** — 5 methods: VEP(0), SpliceAI(0.00), CADD(15.7), MPRA(null), ARCHCODE(<0.92)
5. **New Results section:** "Orthogonal Validation: SpliceAI and MPRA Cross-Reference"
6. **Discussion paragraph:** "Orthogonal Evidence Strengthens the Structural Blind Spot" — 5-method convergence
7. **Limitation #4 rewritten:** was "API unreachable" → now "SpliceAI confirms pearl invisibility"

### Core findings (unchanged from v2.7)

- 30,318 ClinVar variants across 9 loci (HBB/CFTR/TP53/BRCA1/MLH1/LDLR/SCN5A/TERT/GJB2)
- 27 pearl variants on HBB — VEP-blind, ARCHCODE-detected
- Enhancer proximity drives discrimination: ≤1kb Δ=0.039 (7× average)
- Tissue-specificity gradient: matched (HBB Δ=0.111) → mismatch (GJB2: null)
- Per-locus thresholds: HBB 0.977 (92.9% sens) to GJB2 (no threshold works)
- Hi-C validation: r=0.28-0.59 across loci
- AlphaGenome multimodal: pearl RNA-seq 2.8× higher than benign (p<0.0001)
- CADD complementarity: pearl CADD median=15.7 (ambiguous zone)

### Key files (v2.8)

**Manuscript:**

- `manuscript/body_content.typ` — English, main content
- `manuscript/body_content_ru.typ` — Russian translation
- `manuscript/main.typ` / `main_ru.typ` — entry points
- `manuscript/main.pdf` / `main_ru.pdf` — compiled PDFs
- Desktop copy: `C:\Users\serge\Desktop\arxiv 0403\ARCHCODE_arXiv_2026_v1.pdf`

**Validation data (new in v2.8):**

- `results/spliceai_pearl_variants.csv` — 20 pearl SNVs, all SpliceAI=0.00
- `data/mpra_kircher_hbb_raw.csv` — 623 MPRA variants from MaveDB
- `results/mpra_crossvalidation_summary.json` — analysis summary
- `results/mpra_archcode_crossvalidation.csv` — 22 allele-matched variants
- `results/mpra_archcode_position_match.csv` — 30 position-level matches
- `scripts/mpra_crossvalidation.py` — cross-validation analysis script

**Figures:**

- `figures/fig1-fig10` — all 10 publication figures (PDF+PNG)
- Figure 10 = AlphaGenome multimodal validation (new in v2.8)

**Core pipeline:**

- `scripts/generate_publication_figures.py` — all figure generation
- `scripts/per_locus_thresholds.py`, `scripts/ctcf_distance_analysis.py`
- `config/locus/*.json` — 9 locus configs
- `results/*_Unified_Atlas_*.csv` — per-locus atlases

### Compilation

```bash
cd D:/ДНК/manuscript
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='..')"
python -c "import typst; typst.compile('main_ru.typ', output='main_ru.pdf', root='..')"
```

**НЕ** typst CLI (не установлен), а Python package `typst` (v0.14.8). Обязательно `root='..'` для доступа к `../figures/`.

### Technical notes

- Windows: `python` не `python3`
- HBB minus strand: `genomic_pos = 5,227,208 - (mpra_pos - 1)` для MPRA координат
- SpliceAI: Ensembl VEP REST API POST `/vep/homo_sapiens/region` с `?SpliceAI=1` (Broad Institute API timeout)
- MaveDB API возвращает CSV не JSON
- Typst needs `root='..'` parameter

---

## Backlog

1. **P0: arXiv submission** — ждём endorsement от Dr. Guang Shi (q-bio.GN)
2. **P0: Zenodo upload** — вручную через браузер для DOI
3. **P2: gnomAD constraint** — HBB enhancer region depletion (бонус, не блокирует)
4. **P3: Bioinformatics (Oxford)** — after arXiv
5. **P3: GTEx AE check** — low priority, n=27 too small

---

## Commit history (recent)

```
638a5d9 feat: v2.8 orthogonal validation — SpliceAI null + MPRA cross-validation + Figure 10
8cb537d feat: v2.6 reproducibility infrastructure + Limitation #11
eac8376 feat: v2.6 — ablation analysis, conservation evidence, literature integration (3 refs)
5eccbfd chore: add H19/IGF2 ClinVar data + CADD VCF + minor template fixes
ce54d48 docs: update README and GitHub issue templates for 9-locus version
```
