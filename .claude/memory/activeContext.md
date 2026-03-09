# Active Context — ARCHCODE

**Last Updated:** 2026-03-09 (branch split: v4 core vs follow-up)
**Branch:** feature/v4-prioritization-framework (core paper)
**Follow-up Branch:** feature/follow-up-structural-framework (second paper material)
**Last Commit (v4):** b2a26d7 — `feat: EXP-003 tissue-mismatch controls + EXP-004 threshold robustness (P0)`
**Last Commit (follow-up):** 1a0a7cf — `feat: HDAC inhibitor pharmacological landscape integrated into manuscript`
**Git Tag:** v4.0-submission-ready + v2.14-experimental (both pushed)
**GitHub:** https://github.com/sergeeey/ARCHCODE — needs push (both branches)
**Zenodo DOI:** v2.16 — DOI закреплён
**bioRxiv:** BIORXIV/2026/710343 — pending resubmit
**arXiv:** ждём endorsement от Brackley/Michieletto (code B9P837)
**Status:** v4.1 core ready. Follow-up branch has 4 framework extensions.

### Branch Architecture (2026-03-09)
- **v4 core** (`feature/v4-prioritization-framework` @ `b2a26d7`): variant prioritization paper — fragility atlases, BET sweep, discordance taxonomy, external validations, P0 experiments (EXP-001–004 completed)
- **Follow-up** (`feature/follow-up-structural-framework` @ `1a0a7cf`): structural genomics framework — GWAS overlay (384 SNP, rs334), CRISPR compensatory screen (0/180 rescues), ARS proof-of-concept (ρ=0.94), HDAC 2D sweep (HBB +5% anomaly), manuscript v4.3 with 24 Summary items

---

## Текущий статус проекта

**Фаза:** v2.14 — PUBLICATION READY. **Канонические источники истины для claims:** `results/validation_canonical_index_2026-03-06.json`, `results/publication_claim_matrix_2026-03-06.json`. Legacy-нарративы: `docs/internal/LEGACY_CLAIM_HYGIENE_2026-03-06.md`.

### 2026-03-09: 30-Day Plan Execution (Day 1–30 complete)

**Deliverables completed:**
1. TERT validation — `analysis/TERT_validation.csv` (35 Q2, p=2.03e-15, 97% Q2a)
2. Discordance taxonomy figure — `figures/fig_discordance_taxonomy.pdf` (3 panels)
3. Q2b candidate cards — `docs/Q2b_candidate_cards.md` (7 HBB variants)
4. Per-locus verdict — `analysis/per_locus_verdict.csv` (9 loci: PRIMARY→NULL)
5. Coverage gap note — `manuscript/sections/coverage_gap_note.typ` + integrated in supplement
6. Discussion: 3 theses (A/B/C) in `body_content.typ:1619-1656`
7. Abstract updated with Q2a/Q2b decomposition
8. Significance Statement v2 with Thesis C
9. Negative controls table in Results (`@tab:negative-controls`)
10. REPRODUCE.md + requirements-analysis.txt + checksums.sha256 (38 files)
11. Lab collaboration letter — `docs/lab_collaboration_letter.md` (6 target labs)
12. **External validations (network restored):**
    - ABC/rE2G overlay: 68% Q2b overlap, Fisher p=0.36 NS → `analysis/abc_q2b_summary.json`
    - PCHi-C erythroblast: 25/46 significant, CHiCAGO up to 10.5 → `analysis/pchic_q2b_overlap.json`
    - CRISPRi K562: 0 Q2b overlaps in 65 tested elements → `analysis/crispri_q2b_overlap.json`
13. External validations integrated into Discussion paragraph
14. Integrity check: 9/9 key claims PASS against source data
15. Manuscript + supplement compile clean, PDF on desktop

**Key finding from external validations:** Q2b variants remain experimentally unvalidated across all three public datasets → reinforces their status as highest-priority candidates for targeted experiments.

### 2026-03-06 / 2026-03-07: Canonical Governance + Cold-Eye Audit + Post-Audit Fixes

1. **Канонизация валидации** — единый индекс Task1–Task5, матрица допущенных/запрещённых формулировок (C01–C08), legacy-файлы помечены non-canonical.
2. **Cold-Eye Audit** — по ТЗ `docs/COLD_EYE_AUDIT_TZ.md`; отчёт `docs/COLD_EYE_AUDIT_REPORT.md`. Скрытых моков нет; LSSIM из расчёта; тесты 63/63. Task3 weak_halved weakEncounter=0 — риск (геометрия/выборка).
3. **Post-audit fixes (2026-03-07):** цитирование в blind spot benchmark (без placeholder DOI); маппинг ключей в `build_blind_spot_benchmark.py`; «fitted» → «manually calibrated» в AlphaGenomeService.ts и validate-blind-loci.ts; ChromoGen → Schuette et al. 2025, Science Advances.
4. **Task1 1Mb:** гипотеза Pearson > 0.5 отклонена; статус EXPLORATORY.
5. **Task3:** SUPPORTED_IN_MODEL (weak_probe); внешняя валидация UNVERIFIED.
6. **RNA-seq:** анализ выполнен; после нормализации по глубине гипотеза Loop That Stayed не поддержана; в manuscript только как Limitations, без фиктивных p-values.

### Session 37: Publication Package + Integrity Check + Discovery Memo

1. **Publication package** — `C:\Users\serge\Desktop\arxiv 0403\` (63 files, 14 MB)
   - 2 PDFs (EN + RU), 8 Typst sources, 36 figures, 10 data JSONs, 4 supplementary
   - Cover letter, Research Square checklist, arXiv endorsement email, Zenodo metadata
2. **Integrity check** — 49/51 PASS, 0 MISMATCH, 2 UNVERIFIABLE (enhancer proximity numbers from fig8 pipeline)
3. **FigJam diagrams** — 4 created: Pipeline (GA), 9 Methods Blind, Tissue Gradient, VUS Pathway
4. **Discovery Readiness Memo** — 15 pearls shortlisted (8 positions), wet-lab protocol:
   - HUDEP-2 + Capture Hi-C + RT-qPCR + CRISPR base editing
   - 5 priority positions: c.-79A>C, c.-80T>C, c.-138C>A, c.249G>C, c.50dup
   - Success/failure criteria defined for each experiment
5. **Pearl validation shortlist** — `results/pearl_validation_shortlist.json`
6. **Sensitivity analysis** — threshold stable (core pearls at 0.90-0.95), annotation robust (TSS-fixed)
7. **Zenodo v2.14 metadata** — prepared for browser upload (network blocked)
8. **Git push blocked** — TLS handshake reset, needs VPN

### Session 36: VUS Reclassification Candidates

1. **ClinVar VUS download** — 30,952 VUS across 13 loci via NCBI E-utilities (batched per-locus)
2. **Position-based LSSIM lookup** — matched VUS to existing atlas positions, no new simulations
3. **760 candidates** (LSSIM < 0.95), **641 pearl-like** after excluding nonsense/frameshift
4. **Tissue-specificity confirmed**: HBB 22.3% candidate rate; SCN5A/GJB2/HBA1/GATA1/BCL11A = 0
5. **Figure 18** — `figures/fig18_vus_reclassification.pdf/png` (dual panel: VUS counts + pearl-like)
6. **Per-locus candidate CSVs** — HBB (327), MLH1 (122), BRCA1 (81), TERT (79), PTEN (73), CFTR (54), TP53 (13), LDLR (11)
7. **Manuscript v2.14** — new Results section (EN+RU), Main Findings + Data Transparency updated
8. Desktop: `ARCHCODE_v2.14_EN.pdf` / `_RU.pdf`

### Session 35: MaveDB Cross-Validation + Expression/MI Analysis

1. **MaveDB BRCA1 SGE cross-validation** — Findlay et al. Nature 2018 (PMID 30209399)
   - MaveDB URN: urn:mavedb:00000097-0-2, 3,893 normalized scores
   - **1,422 matched** to ARCHCODE BRCA1 atlas
   - **Pearson r = −0.045 (p = 0.086)** — near-zero → complete orthogonality
   - SGE separates P/B perfectly (−1.35 vs −0.08), ARCHCODE LSSIM uniform (0.9995 vs 0.9991)
2. **MaveDB TP53 DMS cross-validation** — HCT116 deep mutational scan
   - MaveDB URN: urn:mavedb:00001213-a-1, 8,052 scores
   - **1,080 matched** to ARCHCODE TP53 atlas
   - **Pearson r = −0.383 (p = 4.3e-39)** — weak correlation (partial tissue-match)
   - R² = 0.147 → ARCHCODE captures 85% independent information
3. **Figure 17** — `figures/fig17_mavedb_crossvalidation.pdf/png` (dual scatter: SGE vs LSSIM, DMS vs LSSIM)
4. **Expression vs LSSIM** (session 34 cont.) — K562 TPM vs |Δ LSSIM|: Spearman ρ = −0.448, p = 0.124 (NS)
5. **Mutual Information** — NMI: ARCHCODE vs CADD = 0.024, vs VEP = 0.101, VEP vs CADD = 0.231
6. **Figures 15-16** — expression/enhancer correlation + NMI orthogonality
7. **Manuscript v2.13** — 9 orthogonal methods (was 8), MaveDB section added EN+RU
8. Desktop: `ARCHCODE_v2.13_EN.pdf` / `_RU.pdf`

### Session 34: HBA1 Atlas + Generic ClinVar Pipeline

1. **`scripts/download_clinvar_generic.py`** — generic ClinVar downloader (any gene → ClinVar E-utilities → filtered CSV)
   - Fixed: ClinVar API renamed `clinical_significance` → `germline_classification`
2. **HBA1 atlas** — `results/HBA1_Unified_Atlas_300kb.csv`
   - 111 variants (67 P/LP + 44 B/LB), 0 pearls
   - Δ LSSIM = -0.0024 (vs HBB -0.111) — 46× weaker signal
   - Nonsense show lowest LSSIM (0.9857-0.9901) — trend preserved
   - Confirms tissue-specificity: K562 enhancers weaker for HBA1 vs HBB LCR
3. **New aliases:** `hba1`, `gata1`, `bcl11a`, `pten` added to TS + Python locus config resolvers
4. **GATA1 atlas** — 183 variants, 0 pearls, Δ LSSIM = -0.0036 (erythroid TF, moderate signal)
5. **BCL11A atlas** — 93 variants, 0 pearls, Δ LSSIM = -0.0137 (HbF repressor, strong signal)
6. **PTEN atlas** — 1,496 variants, 9 struct calls, Δ LSSIM = -0.0097 (tumor suppressor)
7. **Figure 14** — `figures/fig14_cross_locus_comparison.pdf/png` (cross-locus Δ LSSIM bars + struct calls)
8. **Manuscript v2.12** — new Results section "Genome-Wide Scaling", 8 orthogonal methods, 32,201 variants
9. **`results/cross_locus_atlas_comparison.json`** — summary JSON for all 13 loci
10. Desktop: `ARCHCODE_v2.12_EN.pdf` / `_RU.pdf`

### Session 32-33: Cross-Species Conservation + Mouse Hi-C Validation

1. **Mouse HBB config** — `config/locus/mouse_hbb_130kb.json`
   - ENCODE MEL CTCF: ENCSR000CFH / ENCFF142CNG (mm10), 3 CTCF sites
   - ENCODE MEL H3K27ac: ENCSR000CEV / ENCFF078RJZ (mm10), 6 enhancers (real peaks, not literature)
   - 4 genes (Hbb-bt, Hbb-bs, Hbb-bh1, Hbb-y) on chr7, 130kb window
2. **Cross-species LSSIM comparison** — `scripts/cross_species_comparison.ts`
   - TSS-relative coordinate mapping, 17 pearl positions
   - **Pearson r = 0.82** (human vs mouse LSSIM) after ENCODE H3K27ac integration
   - Direction conserved: 17/17 positions show mouse LSSIM < WT baseline
   - Category order conserved: frameshift > splice > promoter > missense > other
3. **Mouse Hi-C validation** — `scripts/extract_mouse_hic.py`
   - Source: 4DN 4DNFIB3Y8ECJ (G1E-ER4 in situ Hi-C, DpnII, mm10), experiment set 4DNESWNF3Y23
   - Downloaded: `data/mouse/4DNFIB3Y8ECJ_G1E-ER4_HiC_mm10.mcool` (2.5 GB)
   - Resolution: 1kb (best available), 130 bins → resampled to 217
   - **Hi-C vs ARCHCODE WT: Pearson r = 0.531** (p ≈ 0, n = 15,055)
   - Consistent with human Hi-C validation range (r = 0.28-0.59)
4. **Figure 12** — `figures/fig12_cross_species.pdf/png` (LSSIM scatter + category bars)
5. **Figure 13** — `figures/fig13_mouse_hic_validation.pdf/png` (Hi-C vs ARCHCODE 4-panel)
6. **Data files:**
   - `data/mouse/ENCFF142CNG_CTCF_MEL_mm10.bed` (37,035 CTCF peaks)
   - `data/mouse/ENCFF078RJZ_H3K27ac_MEL_mm10.bed` (51,597 H3K27ac peaks)
   - `data/mouse/4DNFIB3Y8ECJ_G1E-ER4_HiC_mm10.mcool` (2.5 GB, publicly accessible)
   - `results/mouse_hic_beta_globin.json` (extracted contact matrix + metadata)
   - `results/cross_species_hbb_comparison.json` (LSSIM results + mouseWT matrix)

### Manuscript v2.10 (current) — what's new vs v2.9

1. **Cross-locus VEP scoring** — 21,254 SNVs scored across 8 non-HBB loci via Ensembl VEP REST API
2. **Pearl sensitivity analysis** — threshold sweep 0.88-0.98; HBB robust (27 pearls stable), BRCA1/TP53 threshold artifacts
3. **Figure 11** — dual-panel: threshold sweep + LSSIM distribution (fig11_pearl_sensitivity.pdf/png)
4. **New Results section:** "Cross-Locus VEP Scoring and Pearl Sensitivity Analysis"
5. **Limitation #8 updated:** was "VEP available only for HBB" → now VEP scored across all 8 loci
6. **Summary point (18):** cross-locus VEP confirms pearl specificity
7. **Significance Statement updated:** adds cross-locus VEP sentence
8. **BRCA1 pearl debunking:** 24 candidates = threshold artifacts (LSSIM 0.942-0.947, common polymorphisms AF 40-50%)

### Key VEP results per locus

| Locus | Scored | Pearls | Notes                                     |
| ----- | ------ | ------ | ----------------------------------------- |
| MLH1  | 2,580  | 0      | —                                         |
| CFTR  | 2,594  | 0      | —                                         |
| TP53  | 1,978  | 2      | Threshold-proximal (LSSIM ~0.945)         |
| BRCA1 | 7,219  | 24     | Threshold artifacts, common polymorphisms |
| LDLR  | 2,345  | 0      | —                                         |
| SCN5A | 2,202  | 0      | —                                         |
| TERT  | 1,957  | 0      | —                                         |
| GJB2  | 379    | 0      | —                                         |

### Core findings (unchanged)

- 30,318 ClinVar variants across 9 loci
- 27 pearl variants on HBB — robust across thresholds 0.88-0.95
- Enhancer proximity drives discrimination: ≤1kb Δ=0.039 (7× average)
- Tissue-specificity gradient: matched (HBB Δ=0.111) → mismatch (GJB2: null)
- Hi-C validation: r=0.28-0.59 across loci
- 6 orthogonal methods blind to pearls: VEP, SpliceAI, CADD, MPRA, gnomAD, cross-locus VEP

### Key files (v2.10)

**New in v2.10:**

- `scripts/vep_batch_scoring.py` — multi-locus VEP scoring script
- `results/vep_multilocus_summary.json` — per-locus VEP stats
- `figures/fig11_pearl_sensitivity.pdf/png` — sensitivity analysis figure
- All 8 atlas CSVs updated with VEP columns
- Desktop: `C:\Users\serge\Desktop\ARCHCODE_v2.10_EN.pdf` / `_RU.pdf`

**Manuscript:**

- `manuscript/body_content.typ` — English
- `manuscript/body_content_ru.typ` — Russian
- `manuscript/main.pdf` / `main_ru.pdf` — compiled PDFs

### Compilation

```bash
cd D:/ДНК/manuscript
python -c "import typst; typst.compile('main.typ', output='main.pdf', root='..')"
python -c "import typst; typst.compile('main_ru.typ', output='main_ru.pdf', root='..')"
```

### Technical notes

- Windows: `python` не `python3`
- Typst needs `root='..'` parameter
- VEP API: POST `/vep/homo_sapiens/region`, batch 200, 0.5s delay
- Pearl threshold: VEP < 0.30 AND LSSIM < 0.95
- BRCA1 pearls: all LSSIM 0.942-0.947 (threshold-proximal)

---

## Backlog

1. **P0: arXiv submission** — ждём endorsement от Dr. Guang Shi (q-bio.GN)
2. ~~**P0: Manuscript v2.11**~~ — **DONE** (cross-species + mouse Hi-C sections written, compiled)
3. ~~**P1: Mouse Hi-C validation**~~ — **DONE** (r=0.531, 4DNFIB3Y8ECJ)
4. ~~**P1: H3K27ac for MEL**~~ — **DONE** (ENCSR000CEV / ENCFF078RJZ, 6 peaks integrated)
5. ~~**P2: Genome-wide pipeline**~~ — **DONE** (auto_config_pipeline.py + batch runner, 20 new genes, 31 total configs)
6. ~~**P1: HBA1 atlas**~~ — **DONE** (111 variants, 0 pearls, Δ LSSIM = -0.0024 — weak signal confirms tissue-specificity)
7. **P2: CRISPR collaboration** — after arXiv preprint is live
8. **P2: Evolutionary fragility map** — cross-species on auto-generated configs
9. **P3: Cancer somatic pearls** — MYC super-enhancer test case
10. **P3: VUS reclassification database** — web tool after scaling

---

## Commit history (recent)

```
18e8bea fix: PhyloP mean 2.39→2.37 + Significance Statement update + integrity check passed
51700ab feat: v2.9 — gnomAD v4 population analysis added to manuscript
93e856c feat: v2.8.1 — gnomAD AF analysis, README v2.8, Zenodo DOI
638a5d9 feat: v2.8 orthogonal validation — SpliceAI null + MPRA cross-validation + Figure 10
```

## Auto-commit log
- [2026-03-09 20:16] `b2a26d7`: feat: EXP-003 tissue-mismatch controls + EXP-004 threshold robustness (P0)
- [2026-03-09 20:06] `2f91172`: feat: EXP-001 ablation study + EXP-002 leave-one-locus-out (P0 experiments)
- [2026-03-09 20:01] `99d75bc`: docs: ARCHCODE next-step research plan — 5 planning documents
- [2026-03-09 13:17] `da4a9cc`: feat: freeze v4 submission-ready package — external validations + integrity fixes
- [2026-03-09 11:55] `642b149`: feat: discordance analysis — ARCHCODE vs VEP/CADD 2x2 matrix + Q2a/Q2b split

- [2026-03-09 11:15] `2776906`: feat: v4 bioRxiv resubmission — prioritization framework framing + Tier system

- [2026-03-08 14:03] `799ae1f`: feat: v2.16 — bioRxiv biology-first manuscript + arXiv compressed version

- [2026-03-05 18:43] `5cf0d98`: fix: PR Gate blockers — per-locus thresholds + monotonicity test + caveats

- [2026-03-05 18:17] `bf39ad8`: docs: update README + submission metadata to v2.14 (63,153 variants, 641 VUS candidates)

- [2026-03-05 17:15] `a94c881`: feat: v2.14 — VUS reclassification candidates (30,952 VUS, 760 candidates, 641 pearl-like across 13 loci)

- [2026-03-05 15:51] `2596e99`: docs: Data Transparency Declaration — add MaveDB, expression, MI, mouse, new loci rows

- [2026-03-05 15:48] `c2510b6`: feat: v2.13 — MaveDB cross-validation + genome-wide scaling (13 loci, 32,201 variants, 9 orthogonal methods)
