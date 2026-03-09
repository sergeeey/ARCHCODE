# ARCHCODE Dataset Watchlist

**Created:** 2026-03-09
**Status:** Research planning — living document, update as new datasets become available
**Purpose:** Track public datasets that could validate or extend ARCHCODE predictions

---

## 1. Tissue-Matched 3D Contact Datasets

Priority: datasets in erythroid or K562 cells at highest resolution.

| Dataset | Cell type | Resolution | Status | Use for ARCHCODE |
|---------|-----------|------------|--------|-----------------|
| Rao 2014 K562 Hi-C | K562 | 1 kb | **USED** (r=0.53–0.59) | Primary validation |
| ENCODE K562 Hi-C (4DNFI1UEG1HD) | K562 | 5 kb | **USED** | Cross-validation |
| 4DN G1E-ER4 Hi-C (4DNFIB3Y8ECJ) | G1E-ER4 (mouse erythroid) | 1 kb | **USED** (r=0.531) | Mouse cross-species |
| ENCODE MCF7 Hi-C | MCF7 | 5 kb | **USED** (BRCA1 r=0.50) | BRCA1 locus |
| ENCODE HepG2 Hi-C | HepG2 | 5 kb | **USED** (LDLR r=0.32) | LDLR locus |
| Oudelaar 2020 Capture-C | Mouse erythroid (primary) | 1 kb | NOT USED | HBB ortholog high-res validation |
| Huang 2017 HUDEP-2 Hi-C | HUDEP-2 | 5 kb | NOT USED — check availability | Direct match to proposed experiment cell line |
| Kubo 2021 Tri-C | Mouse erythroid | <1 kb | NOT USED | Multi-way contact validation at globin locus |

**Watchlist — emerging:**
- Any new K562 or HUDEP-2 Micro-C dataset (200bp resolution would enable variant-level validation)
- 4DN erythroid differentiation time-course Hi-C (pseudo-temporal validation)

---

## 2. Micro-C / Capture-C Resources

Nucleosome-resolution contacts — the gold standard for variant-level validation.

| Dataset | Cell type | Resolution | Access | Notes |
|---------|-----------|------------|--------|-------|
| Krietenstein 2020 Micro-C | hESC, HFF | 200 bp | GEO: GSE130275 | Not erythroid, but method benchmark |
| Hsieh 2020 Micro-C | mESC | 200 bp | GEO: GSE130275 | Mouse, not erythroid |
| Goel 2023 Micro-C | K562 | 200 bp | 4DN (check) | **HIGH PRIORITY if exists** — direct K562 match |
| Open Chromatin Collaborative Micro-C | Multiple cell types | 200 bp | Pending release | Monitor for K562/erythroid |

**Capture-C / HiCap:**
- Hughes lab Capture-C protocol (Oxford) — applicable to any viewpoint
- Javierre 2016 PCHi-C (erythroblasts) — **partially used** (25/46 Q2b overlap, CHiCAGO 10.5)
- Mifsud 2015 Capture Hi-C (GM12878) — lymphoblastoid, not erythroid

**Action item:** Search 4DN portal quarterly for new K562/HUDEP-2 Micro-C submissions.

---

## 3. CRISPR Perturbation Gold Standards

Experimental ground truth for enhancer–gene links.

| Dataset | Cell type | Method | N targets | Access | ARCHCODE overlap |
|---------|-----------|--------|-----------|--------|-----------------|
| Gasperini 2019 | K562 | CRISPRi (dCas9-KRAB) | 5,920 elements | GEO: GSE120861 | **Partially downloaded** (`analysis/gasperini2019/`). K562 = direct match |
| Fulco 2019 (ABC model) | K562 | CRISPRi + ABC scoring | 664 enhancer–gene pairs | GitHub + GEO | **Partially used** (ABC/rE2G overlay: 68% Q2b overlap) |
| Findlay 2018 (BRCA1 SGE) | HAP1 | Saturation genome editing | 3,893 variants | MaveDB: urn:mavedb:00000097-0-2 | **Cross-validated** (r = −0.045, orthogonal) |
| Kircher 2019 (MPRA) | HEL 92.1.7 | Massively parallel reporter assay | 31,628 oligos | GEO: GSE126550 | **Cross-validated** (r = −0.21, null — expected) |
| Morris 2023 CRISPRi screen | K562 | CRISPRi | ~10,000 elements | GEO (check) | NOT USED — potential new validation source |
| Nasser 2021 (ABC v2) | Multiple | ABC model + CRISPRi | 3,512 enhancer–gene | GitHub: broadinstitute/ABC-Enhancer-Gene-Prediction | **Partially used** |

**Key gap:** No existing CRISPR screen targets HBB pearl positions directly. EXP-005 (wet-lab) would generate the first ground truth.

---

## 4. iQTL / Allele-Specific Loop Resources

Genetic variants that alter 3D chromatin contacts — the most direct validation type.

| Dataset | Cell type | Method | N iQTLs | Access | Notes |
|---------|-----------|--------|---------|--------|-------|
| Greenwald 2019 | LCLs (GM12878 etc.) | Hi-C + eQTL co-mapping | ~200 | Paper supplement | Lymphoblastoid, NOT erythroid |
| Delaneau 2019 | LCLs | Hi-C + population variation | ~150 | Paper supplement | Same tissue limitation |
| Rao 2014 allele-specific | GM12878 | Phased Hi-C | ~50 loci | GEO: GSE63525 | Lymphoblastoid; HBB locus not covered |
| Gorkin 2019 | Mouse tissues | Hi-C across strains | Strain-specific loops | GEO: GSE118150 | Mouse, but includes erythroid tissue |
| GTEx v8 3D QTL | Multiple tissues | Hi-C + eQTL integration | Pending | GTEx portal | **WATCH** — if erythroid tissue included, high priority |

**Key limitation:** No published iQTL catalog exists for erythroid cells / K562. This is a major gap. If one appears, it becomes immediate P0 validation.

**Action item:** Set alerts for "iQTL erythroid" / "allele-specific Hi-C K562" on PubMed and bioRxiv.

---

## 5. Loop Catalogs / Variant-to-Gene Resources

Curated databases of chromatin loops and enhancer–gene assignments.

| Resource | Content | Access | ARCHCODE use |
|----------|---------|--------|-------------|
| 4DN Loop Catalog | CTCF loops across cell types | 4DN portal | Validate ARCHCODE CTCF loop calls |
| BENGI (Moore 2020) | Benchmark of enhancer–gene interactions | ENCODE | Gold standard for V2G methods |
| EpiMap (Boix 2021) | Enhancer–gene links across 833 biosamples | Roadmap + web | Tissue-specific enhancer maps for new loci |
| ENCODE cCRE v4 | Candidate cis-regulatory elements | ENCODE portal | Regulatory element annotations |
| Open Targets V2G | Variant-to-gene pipeline | Open Targets | Benchmark for ARCHCODE V2G claims |
| 3D Genome Browser | Hi-C + TAD + loop visualization | 3dgb.cs.ucsd.edu | Visual validation of ARCHCODE contact maps |
| Pekowska 2018 | Enhancer–promoter contact dynamics (mouse) | GEO | Temporal dynamics reference |

---

## 6. Single-Cell Multiome / Enhancer–Gene Linking

Emerging datasets that connect enhancer activity to gene expression at single-cell level.

| Dataset | Cell type | Modality | Access | ARCHCODE relevance |
|---------|-----------|----------|--------|-------------------|
| 10x Multiome (scRNA + scATAC) | K562 | Joint RNA + ATAC | 10x Genomics | Enhancer-gene links at single-cell level |
| Muto 2021 | Human bone marrow | scRNA-seq + scATAC-seq | GEO: GSE139369 | Erythroid differentiation trajectory |
| Granja 2019 | Hematopoietic | scATAC-seq | GEO: GSE129785 | Erythroid-specific enhancer landscape |
| Satpathy 2019 | Hematopoietic | scATAC-seq | GEO: GSE129785 | Immune + erythroid lineages |
| SHARE-seq (Ma 2020) | Mouse skin | Joint ATAC + RNA | GEO: GSE140203 | Method reference (not erythroid) |
| Paired-Tag (Zhu 2021) | Mouse brain | Histone mod + RNA | GEO: GSE152020 | Method reference |

**Emerging opportunity:** Single-cell Hi-C (scHi-C) in erythroid cells would enable cell-state-specific contact validation. Currently no erythroid scHi-C published — monitor Nagano/Tanay/Ren labs.

**Key gap for ARCHCODE:** No single-cell 3D contact data in erythroid lineage. If available, would enable:
- Pseudo-temporal structural trajectories (Direction 3 from roadmap)
- Cell-state-specific LSSIM variation
- Direct validation of enhancer-proximity hypothesis at single-cell level

---

## Update Protocol

1. **Monthly:** Search PubMed + bioRxiv for "Hi-C K562", "Micro-C erythroid", "iQTL chromatin", "allele-specific loop"
2. **Quarterly:** Check 4DN portal for new K562/HUDEP-2 submissions
3. **On publication:** When ARCHCODE preprint is live, search citing papers for relevant new datasets
4. **On discovery:** Add to this file with date, assess priority, link to experiment backlog

---

## Version History

- v1.0 (2026-03-09): Initial watchlist based on v4 submission knowledge
