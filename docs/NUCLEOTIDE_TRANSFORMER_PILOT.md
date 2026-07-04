# Nucleotide Transformer Pilot — Integration Pathway Analysis

**Date:** 2026-05-08  
**Context:** Сравнение ARCHCODE с Yang et al. (Nature 2026), ESM3 (Science 2025), Ginkgo/GPT-5 (bioRxiv 2026)  
**Question:** Почему они сделали breakthrough, а мы — нет? Что мы можем использовать?

---

## Исполнительное резюме

**Вывод analyst агента:** ARCHCODE НЕ проиграл гонку — это были **РАЗНЫЕ гонки**:
- **Yang et al.:** Baseline chromatin states (genome-wide, descriptive)
- **ESM3:** Protein design (другие молекулы)
- **Ginkgo/GPT-5:** Wet-lab automation (требует foundry)
- **ARCHCODE:** Regulatory variant perturbation (locus-specific, predictive)

**3 Integration Pathways:**
1. **Yang nucleosome states** → ARCHCODE chromatin layer (⏳ ждать публикации)
2. **ESM3-style foundation models** → DNA sequences (⭐ ЭТОТ PILOT)
3. **Ginkgo closed-loop** → computational equivalent (⚡ доступно сейчас)

---

## Pathway 2: DNA Foundation Models (ESM3 для геномных последовательностей)

### Проблема

**ARCHCODE текущий подход:**
```python
# Hand-crafted categorical effectStrength
effectStrength = {
    'frameshift': 0.8,
    'nonsense': 0.8,
    'missense': 0.3,
    'promoter': 0.4,
    'splice_acceptor': 0.7,
    # ...
}
```

**Результат:** AUC 0.977, но это **category artifact** — position-only AUC = 0.551, within-category AUC ≈ 0.52 (chance).

**Yang et al. / ESM3 подход:**
- Learned embeddings из foundation model
- Continuous representation вместо categorical buckets
- Может различать варианты **внутри категории**

### Решение: Nucleotide Transformer

**Модель:** InstaDeepAI/nucleotide-transformer-v2-500m-multi-species
- 500M параметров (ср. ESM3 = 98B, но for DNA)
- Обучена на multi-species genomic sequences
- 0.89 AUC на regulatory element classification (state-of-the-art)
- Доступна через Hugging Face (open-source)

**Архитектура:**
```python
from transformers import AutoTokenizer, AutoModel

# Load model (one-time ~2GB download)
model = AutoModel.from_pretrained("InstaDeepAI/nucleotide-transformer-v2-500m")
tokenizer = AutoTokenizer.from_pretrained("InstaDeepAI/nucleotide-transformer-v2-500m")

# For each variant:
wt_seq = fetch_sequence(chr, pos-128, pos+128)  # ±128bp window
mut_seq = apply_variant(wt_seq, variant)

# Compute embeddings
wt_emb = model(**tokenizer(wt_seq, return_tensors="pt")).last_hidden_state.mean(1)
mut_emb = model(**tokenizer(mut_seq, return_tensors="pt")).last_hidden_state.mean(1)

# Embedding delta replaces categorical effectStrength
delta = torch.norm(wt_emb - mut_emb).item()
```

### Pilot Experiment

**Dataset:** HBB 27 pearls vs 27 benign (seed=42, matching ADR-011)

**Hypothesis:**
- H0: Embedding delta НЕ различает pearls vs benign лучше категорий
- H1: Embedding delta УЛУЧШАЕТ within-category discrimination (AUC 0.52 → >0.60)

**Baseline:**
- Categorical effectStrength: AUC 0.977 (но category artifact)
- Within-category: AUC 0.52 (chance)
- ADR-011 multimodal: 10/10 тестов significant (signal concentration r=-0.70)

**Target:**
- Within-category AUC > 0.60 (meaningful improvement)
- Pearls embedding delta > Benign embedding delta (p < 0.05)

### MOCK Version (This Pilot)

**Почему MOCK?**
- Nucleotide Transformer требует:
  - `transformers` library install
  - 2GB model download
  - PyTorch (CPU или GPU)
- MOCK версия:
  - Edit distance (SequenceMatcher) как proxy
  - Проверка инфраструктуры (Ensembl API, variant application)
  - Baseline для сравнения

**Ожидания MOCK:**
- Edit distance пропорционален длине варианта (indels >> SNVs)
- НЕ ожидается биологически осмысленный сигнал
- Proof-of-concept для pipeline

**Upgrade Path:**
```bash
# После MOCK pilot:
pip install transformers torch

# Uncomment real embedding function в scripts/nucleotide_transformer_pilot.py
# Re-run на тех же 54 вариантах
# Сравнить MOCK vs REAL
```

---

## Методология

### Данные

**Pearl variants (n=27):**
```csv
VCV002664746,5226613,G,C,missense,0.9492
VCV000811500,5226613,G,T,missense,0.9492
VCV002024192,5226796,CAGCCT...,TAATCT...,splice_acceptor,0.9004
VCV000869358,5226971,CCCC,CCCCC,frameshift,0.8915
VCV000015471,5227099,T,C,promoter,0.9276
...
```

**Benign variants (n=27, seed=42):**
- Random sample из `Label == 'Benign'`
- Matching ADR-011 control sampling strategy

### Pipeline

1. **Load variants** — 27 pearls + 27 benign
2. **Fetch sequences** — Ensembl REST API, ±128bp window (256bp total)
3. **Apply variants** — WT → MUT (SNV/indel substitution)
4. **Compute embeddings** — MOCK: edit distance / REAL: Nucleotide Transformer
5. **Statistical tests:**
   - Mann-Whitney U (pearl vs benign)
   - ROC AUC (overall)
   - Within-category AUC (missense, promoter, frameshift, etc.)

### Success Criteria

| Metric | MOCK (expected) | REAL (target) | Baseline |
|--------|----------------|---------------|----------|
| Pearl vs Benign p-value | >0.05 (null) | <0.05 | ADR-011: <0.001 |
| Overall AUC | ~0.50 (chance) | >0.70 | Categorical: 0.977 |
| Within-category AUC | ~0.50 | >0.60 | Current: 0.52 |
| Signal concentration | N/A | r < -0.50 | ADR-011: -0.70 |

---

## Next Steps

### If MOCK shows promise (p < 0.10)
1. ✅ Install `transformers` + `torch`
2. ✅ Download Nucleotide Transformer v2 (2GB)
3. ✅ Replace `compute_embedding_delta_mock()` with real function
4. ✅ Re-run on same 54 variants
5. ✅ Compare MOCK vs REAL improvement

### If REAL shows improvement (within-category AUC > 0.60)
6. ✅ Expand to all 9 loci (30,318 variants)
7. ✅ Replace categorical effectStrength в main ARCHCODE pipeline
8. ✅ Re-run validation suite (30 tests)
9. ✅ Update manuscript: "learned embeddings vs hand-crafted features"

### If REAL fails (AUC ≈ 0.50)
- Pivot to **Pathway 3: Computational Closed-Loop**
- Или try **Pathway 1: Yang nucleosome states** (если станет публичным)

---

## Связь с ARCHCODE falsification framework

**Честный null result handling:**
- Если MOCK fails → document as informative null
- Если REAL fails → add to ADR (honest limitation)
- Не cherry-pick успешные метрики

**Skeptic check:**
- Threshold: если within-category AUC improvement < 0.05 → статистически незначимо
- Если p > 0.05 → cannot reject H0

**Validation suite:**
- Add new test: `test_embedding_vs_categorical_discrimination()`
- Baseline: categorical effectStrength
- Hypothesis: learned embeddings improve within-category AUC

---

## Литература

**Foundation models для DNA:**
- Nucleotide Transformer (Instadeep, 2023): https://doi.org/10.1101/2023.01.11.523679
- DNABERT (Microsoft, 2021): https://doi.org/10.1093/bioinformatics/btab083
- Enformer (DeepMind, 2021): https://doi.org/10.1038/s41592-021-01252-x

**ESM3 analogy:**
- Hayes et al., Science 2025: esmGFP (58% identity, 500M years divergence)
- EvolutionaryScale: 770B protein tokens → learned protein representation
- ARCHCODE analogy: genomic sequences → learned regulatory variant representation

---

**Status:** MOCK pilot running (ETA 5-6 min)  
**Output:** `results/nucleotide_transformer_pilot.json`  
**Next:** Review results → decide install REAL model or pivot
