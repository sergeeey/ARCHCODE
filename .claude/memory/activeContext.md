# Active Context — ARCHCODE

**Last Updated:** 2026-03-04 (session 26: CADD benchmark + manuscript update)
**Branch:** main
**Last Commit:** pending
**GitHub:** https://github.com/sergeeev/ARCHCODE
**bioRxiv ID:** BIORXIV/2026/708672 — REJECTED ("not complete research with new data")
**Status:** Manuscript updated with CADD integrative benchmark. Ready for arXiv submission.

---

## Текущий статус проекта

**Фаза:** v3.0 — CADD integrative benchmark + honest domain of applicability

### Session 26: CADD Benchmark + Integrity Verification

**Key changes:**

1. **CADD v1.7 scoring** — 17,693/27,760 variants scored via Ensembl VEP REST API (63.7% coverage). All 7 loci: HBB (82%), CFTR (69%), TP53 (71%), BRCA1 (57%), MLH1 (61%), LDLR (62%), SCN5A (74%)
2. **Concordance matrix** — ARCHCODE×CADD: both+ 124 (0.7%), ARCHCODE-only 53 (0.3%), CADD-only 5,452 (30.8%), both− 12,064 (68.2%)
3. **53 ARCHCODE-only analysis** — honest breakdown: 25 HBB true positives (all ClinVar Pathogenic), 28 BRCA1/TP53 false positives (threshold artifacts)
4. **17 pearl-variants confirmed unique** — VEP-blind, CADD-ambiguous, ARCHCODE-positive. Only 17 of 53 are genuinely detected exclusively by ARCHCODE
5. **Per-locus threshold analysis** — universal 0.95 works only for HBB (0% FP, 79.6% sensitivity). For BRCA1: 0.7% FP, 0.75% sensitivity
6. **Selection bias disclosed** — pathogenic 49% skipped vs benign 17% (complex indels)
7. **Manuscript updated** — Discussion: CADD benchmark paragraph. Limitations: #9 universal threshold. Abstract: CADD pearl confirmation. Reference: Rentzsch 2019 CADD added
8. **ClinVar IDs verified** — 5 IDs checked via NCBI web, all real, classifications match

**Integrity audit results:**

- 5/5 ClinVar IDs verified live (VCV003766487, VCV000869288, VCV000015514, VCV000970693, VCV000382001)
- Concordance math verified: 124+53+5452+12064 = 17,693
- Cross-check atlas→benchmark: 5 variants, all fields match
- Pearl definition consistent: no exceptions in either direction
- 3 overclaims identified and corrected in manuscript

**New files:**

- `results/integrative_benchmark.csv` (27,760 rows, unified dataset)
- `results/integrative_benchmark_summary.json` (with verified_analysis)
- `results/cadd_scores_{CFTR,TP53,BRCA1,MLH1,LDLR,SCN5A}.csv`
- `data/cadd_cache/*.json` (per-locus CADD caches)
- `scripts/build_integrative_benchmark.py`
- `scripts/fetch_cadd_scores.py` (rewritten for unified atlas)

---

## Backlog

1. ~~bioRxiv screening~~ REJECTED — reframe as integrative analysis
2. **arXiv q-bio.GN** — submit current version, get DOI
3. SpliceAI локальная интеграция (postponed, requires TensorFlow + 3GB hg38.fa)
4. Supplementary violin plot: per-locus LSSIM distributions (Figure 7)
5. Bioinformatics (Oxford) submission — reformatted version after arXiv
6. Push to remote with CADD data
