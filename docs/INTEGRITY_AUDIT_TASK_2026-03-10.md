# Задание: Аудит научной честности ARCHCODE (2026-03-10)

**Цель:** Независимая проверка всех числовых утверждений, источников данных и выводов в проекте ARCHCODE на предмет галлюцинаций, подгонки данных и фиктивных источников.

**Контекст:** Проект использует AI-assisted development. Все данные и код должны быть верифицируемы из первичных источников. Предыдущий аудит (2026-03-06) выявил проблемы: фиктивный Sabaté 2025 (Nature Genetics), mock AlphaGenome без disclosure, несовпадение параметров α/γ.

---

## 1. ПРОВЕРКА ЧИСЛОВЫХ CLAIMS В MANUSCRIPT

Файл: `manuscript/taxonomy_paper/body_content.typ`

Для каждого числового утверждения ниже:
- Найди первичный источник данных (CSV, JSON, скрипт)
- Пересчитай число из raw data
- Отметь: MATCH / MISMATCH / UNVERIFIABLE

### 1.1. Tissue-match amplification table (Supplementary S4a)

| Claim | Проверить в файле |
|-------|------------------|
| SCN5A: matched Δ = −0.00471, K562 Δ = −0.00343, amplification 1.37× | `analysis/scn5a_cardiac_comparison.json` + `results/SCN5A_Unified_Atlas_250kb.csv` |
| LDLR: matched Δ = −0.00241, K562 Δ = −0.00169, amplification 1.43× | `analysis/tissue_match_amplification.json` + `results/LDLR_Unified_Atlas_300kb.csv` + `results/LDLR_Unified_Atlas_300kb_K562.csv` |
| MLH1: matched Δ = −0.00977, K562 Δ = −0.00912, amplification 1.07× | `analysis/mlh1_tissue_match_comparison.json` + `results/MLH1_Unified_Atlas_300kb.csv` + `results/MLH1_Unified_Atlas_300kb_HCT116.csv` |
| MLH1 tail: LSSIM<0.95 count 72 (K562) → 144 (HCT116), ratio 2.0× | Same files as above |
| BRCA1: matched Δ = −0.00554, K562 Δ = −0.00558, amplification 0.99× | `analysis/tissue_match_amplification.json` + `results/BRCA1_Unified_Atlas_400kb.csv` + `results/BRCA1_Unified_Atlas_400kb_K562.csv` |
| CFTR: matched Δ = −0.00406, K562 Δ = −0.00678, amplification 0.60× | `analysis/cftr_tissue_match_comparison.json` + `results/CFTR_Unified_Atlas_317kb.csv` + `results/CFTR_Unified_Atlas_317kb_A549.csv` |
| CFTR: LSSIM<0.95 count 36 (K562) → 13 (A549) | Same files |

**Метод проверки:**
```python
import pandas as pd
df = pd.read_csv('results/MLH1_Unified_Atlas_300kb.csv')  # пример
p = df[df['Label']=='Pathogenic']['ARCHCODE_LSSIM'].mean()
b = df[df['Label']=='Benign']['ARCHCODE_LSSIM'].mean()
delta = p - b
print(f"Delta = {delta:.6f}")
print(f"LSSIM < 0.95: {(df['ARCHCODE_LSSIM'] < 0.95).sum()}")
```

### 1.2. Claim ladder (Table in body_content.typ, label tab:claim-ladder)

Проверить что каждый claim в колонке "Evidence" имеет реальный источник:

| Claim | Заявленный evidence | Где проверить |
|-------|-------------------|---------------|
| "HBB delta = −0.111" | Самый сильный сигнал | `results/HBB_Unified_Atlas.csv` или `results/cross_locus_atlas_comparison.json` |
| "25 Q2b variants" | HBB architecture-driven | `analysis/taxonomy_auto_assignment.csv` или `analysis/taxonomy_auto_assignment_summary.json` |
| "HUDEP-2 Hi-C 1.76× enrichment, p=0.0016" | Q2b contact enrichment | `analysis/hudep2_q2b_contacts.json` |
| "434 bp mean enhancer distance" | Q2b enhancer proximity | Проверить в atlas CSV: среднее расстояние Q2b позиций до ближайшего enhancer |

### 1.3. Discovery ranking (Table S5)

Файл: `analysis/discovery_locus_ranking.json`
Скрипт: `scripts/discovery_locus_ranking.py`

- Проверить что composite scores вычислены правильно (формула в скрипте)
- Проверить что n_variants, delta_pb, struct_calls для каждого локуса соответствуют реальным atlas CSV
- Проверить что ranking порядок соответствует composite score (sorted descending)

---

## 2. ПРОВЕРКА ENCODE ACCESSIONS

Файл: `analysis/encode_tissue_data_availability.json` + все config JSON в `config/locus/`

Для каждого ENCODE accession (ENCFF*, ENCSR*):
1. Проверить что accession существует: `curl -sH "Accept: application/json" "https://www.encodeproject.org/files/ENCFFXXXXXX/"` → должен вернуть JSON, не 404
2. Проверить что cell type, assay, assembly совпадают с заявленными
3. Проверить что peak file ID в config совпадает с реальным файлом эксперимента

**Критические accessions для проверки:**
- ENCFF899XEF (HCT116 H3K27ac) → должен быть из ENCSR661KMA
- ENCFF463FGL (HCT116 CTCF) → должен быть из ENCSR240PRQ
- ENCFF548GIF (A549 H3K27ac) → должен быть из ENCSR000AUI
- ENCFF535MZG (A549 CTCF) → проверить эксперимент
- ENCFF864OSZ (K562 H3K27ac) → baseline для всех K562 configs
- ENCFF736NYC (K562 CTCF) → baseline CTCF

---

## 3. ПРОВЕРКА СОГЛАСОВАННОСТИ МЕЖДУ ФАЙЛАМИ

### 3.1. Config ↔ Atlas consistency

Для MLH1 HCT116:
- Config window: chr3:36900000-37200000, 300 bins → все позиции в atlas CSV должны быть в этом окне
- Config enhancers: 7 штук → peak positions из `data/hct116/ENCFF899XEF_H3K27ac_HCT116_hg38.bed` filtered to window должны совпадать с config enhancer positions

Для CFTR A549:
- Config window: chr7:117400000-117717000, 317 bins
- Config enhancers: 9 штук → проверить vs `data/a549/ENCFF548GIF_H3K27ac_A549.bed`

### 3.2. Manuscript ↔ JSON consistency

- Числа в manuscript body_content.typ (S4a table) должны точно совпадать с `analysis/*_tissue_match_comparison.json`
- Discovery ranking table S5 числа должны совпадать с `analysis/discovery_locus_ranking.json`

### 3.3. Locus-config.ts aliases

Файл: `src/domain/config/locus-config.ts`
- Alias `mlh1_hct116` → `mlh1_hct116_300kb.json` (файл существует?)
- Alias `cftr_a549` → `cftr_a549_317kb.json` (файл существует?)
- В `generate-unified-atlas.ts`: маппинги isGenericLocus, csvLocus, geneMatchArg — все три содержат новые aliases?

---

## 4. ПРОВЕРКА НА OVERCLAIMS

### 4.1. Каузальный язык

Поискать в body_content.typ слова: "proves", "demonstrates causality", "confirms mechanism", "validates".
Для каждого найденного: проверить что claim не выходит за рамки вычислительного evidence.

Допустимо: "consistent with", "suggests", "supports", "computationally demonstrated"
Недопустимо: "proves", "confirms" (для невалидированных computational predictions)

### 4.2. N=1 caveat

Проверить что manuscript содержит explicit caveat: HBB = единственный локус с confident Class B variants. Найти строку с "N = 1" или "sole locus".

### 4.3. "What This Paper Does NOT Claim" box

Проверить что Discussion содержит 4 explicit disclaimers:
1. Not a universal predictor
2. Not experimentally validated
3. Not a clinical diagnostic tool
4. Not a replacement for sequence-based tools

---

## 5. ПРОВЕРКА DOI / REFERENCES

В body_content.typ найти все DOI (pattern: `doi:10.`).
Для каждого DOI:
```bash
curl -sI "https://doi.org/10.XXXX/YYYY" | head -5
```
Должен вернуть 302 redirect (DOI exists), не 404.

**Известные проблемные DOI из прошлых аудитов:**
- Sabaté 2025 Nature Genetics — НЕ ДОЛЖЕН присутствовать (фиктивный)
- Gröschel 2014 — должен быть doi:10.1016/j.cell.2014.11.019 (не .023)

---

## 6. RED FLAGS — ИСКАТЬ АКТИВНО

1. **Фиктивные числа без источника:** Числа в тексте, которые не прослеживаются ни к одному CSV/JSON
2. **Mock data без маркировки:** Файлы с synthetic/generated данными без MOCK_ prefix
3. **Phantom references:** Ссылки на несуществующие статьи
4. **Self-referential claims:** "As we showed in Section X" → но Section X ссылается обратно
5. **Threshold p-hacking:** Если threshold 0.95 выбран post-hoc для максимального эффекта
6. **Cherry-picked loci:** Если tissue-match story работает только потому что выбраны удобные локусы

---

## ФОРМАТ ОТЧЁТА

```markdown
# Integrity Audit Report — 2026-03-10

## Summary
- Total claims checked: X
- MATCH: X
- MISMATCH: X
- UNVERIFIABLE: X

## Detailed Findings

### [MATCH] Claim: "MLH1 delta = -0.00912 (K562)"
- Source: results/MLH1_Unified_Atlas_300kb.csv
- Computed: -0.009115
- Rounding: OK (0.00912 rounds correctly)

### [MISMATCH] Claim: "..."
- Source: ...
- Expected: ...
- Actual: ...
- Severity: HIGH/MEDIUM/LOW

### [UNVERIFIABLE] Claim: "..."
- Reason: no source file found / external data not accessible
```

Сохранить отчёт в: `docs/INTEGRITY_AUDIT_REPORT_2026-03-10.md`

---

## ВАЖНО

- НЕ исправлять ничего — только документировать
- Каждый MISMATCH = potential hallucination
- Каждый UNVERIFIABLE = risk area
- Честные null результаты (BRCA1 0.99×, CFTR 0.60×) — это НЕ ошибки, а informative findings
- Проверять не "нравится ли интерпретация", а "совпадают ли числа с raw data"
