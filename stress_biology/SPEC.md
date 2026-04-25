# SPEC — Stress Biology & Mutagenesis

**Version:** 1.0  
**Created:** 2026-04-25  
**Status:** Draft  
**Branch:** `feature/stress-biology-atp-mutagenesis`

---

## Цель проекта

Проверить гипотезу: **клеточный стресс (дефицит ATP) → повышенная частота мутаций**.

**Мотивация:** Bilinsky (2025) показала, что состояние клетки (R vs Q) определяет радиочувствительность через доступность ATP в ядре. Мы проверяем, применим ли тот же механизм к **эндогенному мутагенезу** (не радиация, а ошибки репликации).

---

## Главная гипотеза (H0)

> **H0:** Частота мутаций коррелирует с временем удвоения клетки (doubling time).
>
> - **Механизм:** Быстро делящиеся клетки → больше времени в state Q (низкий ATP) → слабая репарация → больше мутаций
> - **Предсказание:** Spearman correlation r > 0.4 между doubling time и mutation rate
> - **Kill criterion:** Если r < 0.3 после 3 месяцев работы → гипотеза убита, проект закрыт

---

## Подгипотезы

### H1: Tissue-specific mutation rates

**Утверждение:** Ткани с быстрой пролиферацией (кишечник, кожа, кровь) накапливают мутации быстрее, чем медленные ткани (мозг, сердце).

**Данные:**
- Somatic mutation rates из TCGA (The Cancer Genome Atlas)
- Tissue proliferation rates из литературы (Sender 2016, Cell)

**Метрика:** Spearman r (proliferation rate vs mutation rate)

**Kill criterion:** p > 0.05 или r < 0.3

---

### H2: Cell cycle phase vs mutation spectrum

**Утверждение:** Клетки в G1/S (высокая репликативная активность) показывают другой mutation spectrum, чем в G0 (покой).

**Данные:**
- Single-cell sequencing datasets (10X Genomics)
- Cell cycle markers (CCND1, CDK1, MKI67)

**Метрика:** Chi-square test на различие mutation spectra (C>T, A>G, indels)

**Kill criterion:** p > 0.01

---

### H3: ATP levels vs mutation rate (computational proxy)

**Утверждение:** Прокси-маркеры метаболизма (OXPHOS gene expression, glycolysis markers) коррелируют с mutation rate.

**Данные:**
- RNA-seq data + somatic mutations (TCGA, ICGC)
- ATP proxy: average expression of OXPHOS genes (COX1-8, ATP5A-F)

**Метрика:** Spearman r (ATP proxy vs mutation rate)

**Kill criterion:** r < 0.2

---

## Эксперименты (3 шага)

### Experiment 1: Meta-analysis (computational, 3 месяца)

**Цель:** Собрать данные из публичных источников и проверить корреляцию doubling time vs mutation rate.

**Datasets:**
1. TCGA — somatic mutations + RNA-seq (>10K samples)
2. ICGC — международная когорта рака
3. Literature mining — doubling time для разных тканей (PubMed API)

**Pipeline:**
```bash
1. Download TCGA mutation data (MAF files)
2. Extract mutation rates per sample (mutations / Mb)
3. Match with tissue type
4. Extract doubling time from literature
5. Correlation analysis (Spearman, bootstrapped CI)
```

**Output:**
- `results/h0_correlation.png` — scatter plot
- `results/h0_stats.json` — r, p-value, 95% CI

**Timeline:** 3 месяца

---

### Experiment 2: ATP proxy validation (optional, если H0 passed)

**Цель:** Проверить, коррелирует ли computational ATP proxy с реальными ATP measurements (литература).

**Datasets:**
- Published ATP measurements (fluorescence, luciferase assays)
- Matching RNA-seq data

**Метрика:** r > 0.5 между ATP proxy и real ATP

**Timeline:** 1 месяц

---

### Experiment 3: Wet-lab collaboration (если H0+H3 passed)

**Цель:** Экспериментально подтвердить: manipulate ATP → изменить mutation rate.

**Design:**
1. Культура клеток (HEK293, fibroblasts)
2. Conditions:
   - Control
   - ATP depletion (oligomycin, 2-DG)
   - ATP boost (pyruvate, creatine)
3. Measure mutation rate (whole-genome sequencing после 10 пассажей)

**Collaborator needed:** Wet-lab с live-cell imaging + WGS capacity

**Timeline:** 6 месяцев (после Experiment 1-2)

---

## Kill Criteria (falsification gates)

| Checkpoint | Condition | Action |
|------------|-----------|--------|
| **Month 1** | Data collection < 50% | Reassess feasibility |
| **Month 2** | H0: r < 0.1 (очень слабая корреляция) | Kill, publish negative result |
| **Month 3** | H0: r < 0.3, p > 0.05 | Kill, write theoretical paper |
| **Month 3** | H0: r > 0.4, p < 0.01 | Proceed to Experiment 2 |
| **Month 4** | H3: ATP proxy failed (r < 0.2) | Mechanism unclear, need wet-lab |
| **Month 6** | All H passed, but no collaborator | Publish computational paper, wait for wet-lab |

---

## Success Metrics

### Minimal Success (publishable negative result)

- H0 tested with n > 1000 samples
- Clear null result (r < 0.3, p > 0.05)
- Publication: PLOS Computational Biology, F1000Research

### Medium Success (theoretical framework)

- H0 weak positive (0.3 < r < 0.5)
- H3 passed (ATP proxy works)
- Publication: Bioessays, Trends in Cell Biology (theoretical)

### High Success (Nature/Science track)

- H0 strong positive (r > 0.5, p < 1e-10)
- H3 passed
- Wet-lab validation (Experiment 3)
- Publication: Nature Cell Biology, Nature Genetics

---

## Resources Needed

### Computational

- **Data storage:** 100GB (TCGA MAF files)
- **Compute:** Local (Python, R, no GPU needed)
- **Cost:** $0 (public data)

### Wet-lab (if Experiment 3)

- **Collaborator:** Bilinsky (radiobiology expertise) OR other RIIS Fellow
- **Cost estimate:** $5K-10K (cell culture, WGS)
- **Funding source:** TBD (RIIS micro-grants? Crowdfunding?)

---

## Timeline

```
Month 1: Data collection + pipeline setup
Month 2: H1 testing (tissue-specific rates)
Month 3: H0 checkpoint (kill or continue)
  ├─ KILL → write negative result paper
  └─ PASS → proceed to H3
Month 4: H3 (ATP proxy)
Month 5: Draft computational paper
Month 6: Submit + seek wet-lab collaborator
```

---

## Deliverables

### Code

- `scripts/download_tcga.py` — download TCGA data
- `scripts/extract_mutation_rates.py` — parse MAF files
- `scripts/literature_mining.py` — PubMed API для doubling time
- `scripts/correlation_analysis.R` — Spearman + bootstrap
- `scripts/atp_proxy.py` — compute ATP proxy from RNA-seq

### Documents

- `HYPOTHESIS.md` — гипотезы и kill criteria (этот файл)
- `RESULTS.md` — результаты экспериментов
- `BILINSKY_EMAIL.md` — draft письма Bilinsky (после Experiment 1)
- `MANUSCRIPT_DRAFT.md` — черновик статьи

### Figures

- `results/fig1_correlation.png` — H0: doubling time vs mutation rate
- `results/fig2_tissue_heatmap.png` — H1: tissue-specific rates
- `results/fig3_atp_proxy.png` — H3: ATP proxy validation

---

## Связь с ARCHCODE v1

**Что переиспользуем:**

1. **Validation suite** — 10 ортогональных методов проверки гипотез
2. **Falsification protocol** — matched controls, kill criteria
3. **17 уроков** — null hypothesis first, category leakage, baseline comparison

**Что НЕ используем:**

- 3D chromatin simulation (не нужна для stress biology)
- Hi-C data (не релевантны)
- VUS classification (другая задача)

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Data unavailable | 20% | High | Pre-check TCGA API access |
| Correlation weak (r < 0.3) | 60% | Medium | Expected — это negative result, publishable |
| No wet-lab collaborator | 70% | Low | Computational paper still valuable |
| Bilinsky not interested | 40% | Low | Ищем других RIIS Fellows in cell biology |

---

## Next Steps (immediate)

1. ✅ Create branch `feature/stress-biology-atp-mutagenesis`
2. ✅ Write SPEC.md (this file)
3. ⬜ Write `scripts/download_tcga.py` stub
4. ⬜ Test TCGA API access
5. ⬜ Create `HYPOTHESIS.md` with detailed predictions
6. ⬜ Start Month 1: data collection

---

## Contact for Collaboration (after Experiment 1)

**Draft email to Bilinsky:**

> Subject: Collaboration proposal — ATP & mutagenesis (inspired by your Biomath 2025 paper)
>
> Dear Dr. Bilinsky,
>
> I read your recent paper on dose-survival curves and the R/Q state hypothesis (Biomath 14, 2025). Your ATP-based mechanism for radiosensitivity inspired me to test a related hypothesis: **does cellular stress (ATP deficit) also drive endogenous mutagenesis?**
>
> I completed a 3-month computational meta-analysis (TCGA data, n=1000+ samples) and found [RESULTS FROM EXPERIMENT 1]. I believe this connects to your framework: state Q (low ATP, vulnerable nuclear envelope) may not only increase radiosensitivity, but also permit DNA replication errors.
>
> Would you be interested in discussing this? I'm a RIIS Fellow candidate [STATUS], working on computational genomics. Happy to share preliminary data.
>
> Best regards,  
> [Your Name]

---

**Status:** Ready for work. Начинай с Experiment 1, Month 1.
