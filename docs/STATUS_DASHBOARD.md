# ARCHCODE Status Dashboard

**Last Updated:** 2026-03-06  
**Current Phase:** Phase 0 Complete — FASTQ Ready!

---

## 🎯 Strategic Positioning

| Status | Description |
|--------|-------------|
| ✅ **DONE** | Discovery Engine positioning (not Prediction Tool) |
| ✅ **DONE** | STRATEGY.md updated |
| ✅ **DONE** | README.md updated |
| ✅ **DONE** | DISCOVERY_ENGINE_POSITIONING.md created |
| ✅ **DONE** | VALIDATION_PROTOCOL.md updated |

---

## 📅 Phase 0: FASTQ Status — ✅ COMPLETE!

### FASTQ Download

| Task | Status | Notes |
|------|--------|-------|
| Directory structure | ✅ Ready | `fastq_data/raw/` exists |
| FASTQ files | ✅ **READY** | Downloaded 2026-02-05 |
| Sample identification | ✅ **VERIFIED** | WT, B6 (deletion), A2 (inversion) |
| Total size | ✅ 12.4 GB | 6 files |

**Confirmed samples:**
```
✅ SRR12935486 (WT) — Wild-type, intact 3'HS1
✅ SRR12935488 (B6) — 3'HS1 deletion clone
✅ SRR12935490 (A2) — 3'HS1 inversion clone
```

**Note:** B6 clone instead of D3 — both are 3'HS1 deletion clones from same study (Himadewi et al. 2021). Equally valid for hypothesis testing.

---

## 📅 Phase 1: Week 1 (2026-03-06 — 2026-03-13)

### Manuscript Updates

| Task | File | Status | Duedate |
|------|------|--------|---------|
| Discovery Engine positioning | `docs/` | ✅ DONE | 2026-03-06 |
| Benchmark script | `scripts/` | ✅ DONE | 2026-03-06 |
| Manuscript update plan | `docs/` | ✅ DONE | 2026-03-06 |
| Update ABSTRACT.md | `manuscript/` | ⏳ Pending | 2026-03-08 |
| Update INTRODUCTION.md | `manuscript/` | ⏳ Pending | 2026-03-08 |
| Update DISCUSSION.md | `manuscript/` | ⏳ Pending | 2026-03-10 |
| Update FULL_MANUSCRIPT.md | `manuscript/` | ⏳ Pending | 2026-03-12 |
| **bioRxiv submission** | — | ⏳ Pending | **2026-03-13** |

### Benchmark Dataset

| Task | Status | Duedate |
|------|--------|---------|
| Build benchmark script | ✅ DONE | 2026-03-06 |
| Run benchmark builder | ⏳ Pending | 2026-03-10 |
| Generate benchmark dataset | ⏳ Pending | 2026-03-11 |
| Write benchmark README | ⏳ Pending | 2026-03-12 |

---

## 📅 Phase 2: Weeks 2-4 (2026-03-14 — 2026-04-03)

### RNA-seq Analysis

| Task | Status | Duedate |
|------|--------|---------|
| FASTQ QC (FastQC) | ⏳ Pending | 2026-03-16 |
| Alignment (STAR) | ✅ Done (Galaxy EU) | — |
| Splice junction quantification | ✅ Done (exploratory; depth-normalized) | — |
| Aberrant splicing calculation | ✅ Done (null after depth norm; see Limitations) | — |
| featureCounts (HBB expression) | ⏳ Pending | 2026-03-20 |
| MultiQC (STAR logs) | ⏳ Pending | 2026-03-20 |
| STAR novel filter (optional) | ⏳ Optional | — |
| **Validation report** | ⏳ Pending | **2026-03-25** |

Downstream checklist: [GALAXY_EU_STAR_DOWNSTREAM.md](GALAXY_EU_STAR_DOWNSTREAM.md).

### Multi-Locus Analysis

| Locus | Status | Duedate |
|-------|--------|---------|
| HBB | ✅ DONE | — |
| BRCA1 | ⏳ Pending | 2026-03-25 |
| MLH1 | ⏳ Pending | 2026-03-28 |
| TP53 | ⏳ Pending | 2026-03-30 |
| CFTR | ⏳ Pending | 2026-04-03 |

### 3D Variant Atlas

| Component | Status | Duedate |
|-----------|--------|---------|
| Variants VCF | ⏳ Pending | 2026-03-28 |
| LSSIM scores | ⏳ Pending | 2026-03-28 |
| Contact maps | ⏳ Pending | 2026-03-30 |
| Metadata JSON | ⏳ Pending | 2026-03-30 |
| UCSC Track Hub | ⏳ Pending | 2026-04-03 |

---

## 📊 Key Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Manuscript progress | 100% | ~80% | 🟡 In Progress |
| RNA-seq validation | Complete | 0% | ⏳ Pending |
| Multi-locus pearls | ≥2 loci | 0/4 | ⏳ Pending |
| Benchmark dataset | Complete | Script ready | 🟡 In Progress |
| Atlas publication | Zenodo DOI | 0% | ⏳ Pending |

---

## ⚠️ Risks & Blockers

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| FASTQ download fails | High | Low | Retry with individual accessions |
| RNA-seq null result | High | 30% | Pivot to 27 pearls (not splice mechanism) |
| No pearls on other loci | Medium | 40% | Focus on HBB + tissue-matched only |
| Manuscript rejection | Medium | 50% | Submit to 3 journals (tiered) |

---

## ✅ Completed This Week

- [x] Strategic positioning (Discovery Engine)
- [x] STRATEGY.md updated
- [x] README.md updated
- [x] DISCOVERY_ENGINE_POSITIONING.md created
- [x] VALIDATION_PROTOCOL.md updated
- [x] Benchmark script created
- [x] FASTQ download scripts created
- [x] Manuscript update plan documented

---

## 📞 Next Actions

### Tonight (after 19:00):
1. Run `scripts\download_rnaseq_fastq.bat`
2. Monitor download progress
3. Verify files in morning

### Tomorrow (2026-03-07):
1. Check FASTQ files downloaded correctly
2. Review manuscript update plan
3. Approve/reject proposed changes

### Week 1:
1. Complete manuscript updates
2. Run benchmark builder
3. Submit to bioRxiv

---

**Contact:** sergeikuch80@gmail.com  
**Repository:** https://github.com/sergeeey/ARCHCODE
