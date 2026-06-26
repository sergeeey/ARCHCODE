# Experiment: External-Tool Mirror Test (Enformer / Akita)
# Paper 3 — Extension addressing Reviewer W5

**Date:** 2026-06-24
**Leads:** W5 (self_review.md) — "apply mirror to ≥1 tool the author did NOT build"
**Status:** STAGE 1 COMPLETE — 2026-06-24. Results: `results_enformer_mini.json`
**Verdict:** ILLUSTRATIVE (not breakthrough) — see Stage 1 Findings below

---

## Stage 1 Findings (2026-06-24)

| Метрика | Значение | Интерпретация |
|---|---|---|
| Enformer global AUC (path > benign) | 0.65 | Умеренный сигнал |
| Enformer within-intronic AUC (path > benign) | **0.86** (p=0.003) | Сильный — но n=6 |
| ARCHCODE within-intronic AUC | 0.57 | Монетка |
| mirror_gap Enformer | 0.0 | **АРТЕФАКТ** — auc_inv = 1−auc_std по построению |
| Статус | **ILLUSTRATIVE** | Не прорыв (см. ограничения ниже) |

### Ограничения Stage 1

1. **n=6 pathogenic intronic** в HBB атласе — фундаментальный лимит, не баг
2. **mirror_gap для Enformer = 0 всегда** — "инверсия" для DL модели не имеет смысла
3. **within-missense AUC не вычислен** — в HBB нет benign missense SNVs
4. **AUC=0.86 при n=6** — p=0.003 но один выброс меняет результат

### Что Stage 1 добавляет к Paper 3

Иллюстративное сравнение: "Enformer находит сигнал (0.86) там где ARCHCODE не находит (0.57)".
НЕ является: новым методом, прорывом, основным результатом.

---

## Estimand (EstimandOps L0)

**Question type:** Descriptive → "what is the mirror-gap of Enformer/Akita ΔContact
scores on our 9-locus ClinVar atlases?"

**Population:** ClinVar variants from our 9 loci with path/benign labels (n=8,134)
**Intervention:** Enformer WT→mutant ΔTrack score (CTCF + ATAC tracks)
**Comparator:** random noise floor (shuffle labels)
**Endpoint:** AUC(ΔTrack, pathogenic vs benign) global + within-category
**Summary measure:** mirror_gap = |AUC_std − (1 − AUC_inv)|

**What this does NOT mean:**
1. Does NOT validate Enformer as a pathogenicity predictor
2. Does NOT prove ARCHCODE is worse than Enformer
3. Does NOT apply to non-ClinVar variants or non-coding loci

---

## Hypothesis

- **H_mirror_holds**: Enformer also shows mirror_gap < 0.10 → category-confounding
  is NOT specific to ARCHCODE's hardcoded lookup but emerges from category imbalance
  in ClinVar itself
- **H_mirror_absent**: Enformer shows mirror_gap > 0.10 AND within-category AUC > 0.6
  → shows what genuine structure signal looks like; ARCHCODE gap = instrument failure

Either outcome is publishable:
- H_mirror_holds → "diagnostic detects category-confounding in ANY tool"
- H_mirror_absent → "here is what a fair test looks like; ARCHCODE fails it"

---

## 4-Stage Progressive Plan

### Stage 1 — Minimal proof of concept (1 day, CPU)
- **Locus:** HBB only (n=353 path + 750 benign, 1103 total)
- **Model:** Enformer via HuggingFace (`EleutherAI/enformer-official-rough` or
  `anthropics/enformer`) — PyTorch, CPU-feasible
- **Sequence fetch:** NCBI E-utilities (no local FASTA needed)
  - Rate limit: 3 req/sec unauthenticated, 10 with NCBI_API_KEY
  - Window: 393,216 bp centered on variant (Enformer input)
- **Output tracks used:** CTCF ChIP-seq (tracks 447-455 in Enformer output),
  ATAC-seq (tracks 684-688), DNase (tracks 694-698)
- **ΔTrack:** max(|pred_mut[t] - pred_wt[t]|) over CTCF tracks at variant ±10kb
- **Metrics:** global AUC, within-missense AUC, mirror_gap
- **Expected runtime:** ~5 sec/variant × 1103 = ~90 min CPU
- **Completion criteria:** AUC computed for ≥200 HBB variants with path/benign labels

### Stage 2 — Three-locus generality (3 days, CPU or cloud)
- **Loci:** HBB + GATA1 + GJB2 (most informative, different disease classes)
- **Model:** Enformer + optionally Akita (if TF available)
- **Additional metric:** Pearson(Enformer_ΔTrack, ARCHCODE_LSSIM) — are they measuring
  the same thing?
- **Completion criteria:** AUC computed per locus, category breakdown

### Stage 3 — All 9 loci (1 week, cloud recommended)
- All 8,134 variants
- Both Enformer and Orca (if available)
- Statistical testing: bootstrap 95% CI for AUC, Wilcoxon between models

### Stage 4 — Ablation: which tracks matter?
- CTCF-only vs ATAC-only vs DNase-only vs all
- Determines whether structure (CTCF) or accessibility (ATAC) drives any signal

---

## Interpretation Criteria

| Result | Verdict | Action |
|---|---|---|
| Enformer mirror_gap < 0.10 | H_mirror_holds: confounding is ClinVar-wide | Paper 3 §3.6 extension: "even Enformer shows the mirror" |
| Enformer within-cat AUC > 0.60 | Genuine signal exists in Enformer | ARCHCODE comparison: "ARCHCODE misses what Enformer finds" |
| Enformer global AUC ≈ ARCHCODE | Same performance, same mechanism | "Both reduce to category lookup" |
| Pearson(Enformer, ARCHCODE) > 0.7 | Models agree | "Convergent validation of null" |

---

## Infrastructure Requirements

| Stage | CPU time (est.) | GPU time (est.) | Disk |
|---|---|---|---|
| Stage 1 (HBB) | 90 min | 5 min | 2 GB (Enformer weights) |
| Stage 2 (3 loci) | 6 hr | 20 min | 2 GB |
| Stage 3 (9 loci) | 24 hr | 2 hr | 2 GB |

Enformer weights: `~/.cache/huggingface/hub/` auto-downloaded on first run.

**Akita alternative** (if TF available):
```bash
pip install basenji kipoiseq tensorflow
# Download weights from gs://basenji_barnyard2/model_best.h5
# Needs hg38 FASTA: ~3.1 GB from UCSC
```

---

## Source

Script: `run_enformer_mirror_test.py` (this directory)
Output: `results_enformer_mirror.json` (per-variant ΔTrack + labels)
Paper target: §3.6 extension, Figure 5 panel D
