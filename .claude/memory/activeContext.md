# Active Context — ARCHCODE

**Last Updated:** 2026-06-24
**Branch:** main
**GitHub:** https://github.com/sergeeey/ARCHCODE
**Status:** ARCHCODE-SV v1.1 — FL Standard PROMOTE 12/12 ✅ (chr2 + chr17 + chr7)

---

## ЧТО БЫЛО СДЕЛАНО (2026-06-24) — ARCHCODE-SV Pivot

### Контекст: почему пивот

Original ARCHCODE = SNV pathogenicity predictor. Проблема: global AUC 0.975 — артефакт категориальной таблицы `CATEGORICAL_EFFECTS` в `scripts/generate-unified-atlas.ts:291`. Реальной 3D-физики нет, только lookup. Enformer (Google DeepMind) на тех же вариантах (HBB, intronic) = AUC 0.86 vs ARCHCODE 0.57.

**Пивот:** из SNV → в Structural Variants (SVs). Физический движок ARCHCODE (Kramer kinetics + CTCF barriers) идеально подходит для SVs. Конкурентов нет — ни один инструмент не делает физику TAD-disruption без GPU и обучения.

---


## ARCHCODE-SV: что реализовано
[summarized] **Файл:** `scripts/archcode_sv.py`
   - duplication: дублируем CTCF
4. boundary_delta() — ratio = cross_mut / cross_wt у сайта изменённого CTCF
5. Verdict: ratio > 1.35 → DISRUPTED (pathogenic), иначе → INTACT (benign)
```

**Порог 1.35 обоснован физически:**
- score > 40 → strength > 0.367 → ratio > 1.4 → выше порога
- score < 30 → strength < 0.35 → ratio ≈ 1.30 → ниже порога
- Это соответствует CTCF IDR confidence cutoff

### Ключевые параметры (Kramer kinetics)
```python
K_BASE = 0.05   # base extrusion rate
ALPHA  = 0.92   # pausing strength (from Sabaté 2024 bioRxiv)
GAMMA  = 0.80   # loop extension factor
RESOLUTION = 5000   # 5kb bins
N_BINS     = 200    # 1Mb window
```

---

## Benchmarks: результаты
[summarized] ### Primary: Lupiáñez 2015 (EPHA4 locus, chr2) — 5/5
| Pathogenic_inversion | inv chr2:221.3-221.7 Mb | 0 inverted | 1.437 | DISRUPTED | ✅ |

Ключевой CTCF: chr2:221,574,000 (score=88.9) — граница TAD.

### Generalizability: SOX9 locus (chr17) — 4/4
**Источник:** Benko et al. Nat Genet 2011. Pierre Robin syndrome от делеций границы KCNJ16/SOX9 TAD.
**K562 CTCF граница:** chr17:70,622,593 (score=53.5) — между KCNJ16 TAD и SOX9 регуляторным доменом.
**SOX9 gene (hg38):** chr17:72,121,020-72,126,580
**SOX9 регуляторная пустыня:** chr17:71.0-72.1 Mb (CTCF-sparse, max score=25.7)

| Label | SV | Ratio | Verdict | Correct? |
|---|---|---|---|---|
| Path_SOX9_boundary | del chr17:70.3-71.0 Mb | 1.632 | DISRUPTED | ✅ |
| Path_SOX9_large | del chr17:69.8-71.5 Mb | 1.629 | DISRUPTED | ✅ |
| Ben_SOX9_desert | del chr17:71.1-71.9 Mb | 1.300 | INTACT | ✅ |
| Ben_SOX9_inv | inv chr17:71.2-71.8 Mb | 1.300 | INTACT | ✅ |

### Generalizability: SHH/LMBR1 locus (chr7) — 3/3 [FL Standard 2026-06-26]
**Источник:** Lettice 2003 (Nat Rev Genet), Anderson 2014 (Development) — boundary disruption mechanism
**Ключевой CTCF:** chr7:156,909,000 (score=314.6) — граница между SHH-LMBR1 и KCNJ2 TAD
**SHH-ZRS CTCF desert:** chr7:156.16-156.47 Mb (317 kb gap, 0 IDR peaks)
**SHH TAD gap:** chr7:155.46-155.52 Mb (70 kb, 0 IDR peaks)

| Label | SV | Ratio | Verdict | Correct? |
|---|---|---|---|---|
| Path_SHH_boundary | del chr7:156.65-157.0 Mb | 3.299 | DISRUPTED | ✅ |
| Ben_SHH_desert | del chr7:156.2-156.4 Mb | 1.000 | INTACT | ✅ |
| Ben_SHH_gap | del chr7:155.46-155.52 Mb | 1.000 | INTACT | ✅ |

### ИТОГ: 12/12 на 3 локусах, 3 хромосомах (chr2 + chr17 + chr7), 3 типа SVs
**FL Standard PROMOTE** — experiments/exp_archcode_sv/decision.md

---

## Enformer experiment (параллельная ветка, завершена)

**Файл:** `results/paper3/experiments/exp_akita_mirror/DESIGN.md`
**Результаты:** `results_enformer_mini.json`

| Метрика | Значение |
|---|---|
| Enformer global AUC (HBB) | 0.65 |
| Enformer within-intronic AUC | **0.86** (n=6, p=0.003) |
| ARCHCODE within-intronic AUC | 0.57 (случайность) |
| mirror_gap | 0.0 (АРТЕФАКТ — математически = auc − (1−auc) = 0 всегда) |

**Вывод:** HBB intronic AUC 0.86 vs 0.57 — иллюстративное сравнение. Статус: ILLUSTRATIVE (n=6 слишком мало).

---


## Структура ключевых файлов
[summarized] (empty section)
```
scripts/
  archcode_sv.py              ← ARCHCODE-SV: физический движок для SVs (НОВЫЙ)
  generate-unified-atlas.ts   ← старый SNV pipeline (CATEGORICAL_EFFECTS bug)

data/input/ctcf/
  K562_CTCF_hg38.bed          ← ENCODE CTCF K562 hg38 (46,160 пиков, НОВЫЙ)

results/paper3/
  PAPER3_SKELETON.md           ← манускрипт Paper 3 (negative results note)
  experiments/exp_akita_mirror/
    DESIGN.md                  ← Enformer эксперимент, Stage 1 Complete
    results_enformer_mini.json ← 152/152 вариантов, HBB locus
  figures/Figure1-5.png        ← финальные фигуры (300 dpi)

results/p5_instrument/
  INSTRUMENT_CHARACTERIZATION.md ← характеризация инструмента (transfer function)
```

---

## Следующие шаги (приоритет)

1. **✅ DONE (2026-06-26):** FL Standard claim.md + controls.md + decision.md → PROMOTE 12/12
2. **Реальные clinical SVs (DECIPHER)** — тест на пациентских SVs с известным патогенным статусом
3. **Мотивная ориентация CTCF** — скачать JASPAR/FIMO данные для замены -1.0 heuristic реальной ориентацией
4. **Paper 3: §3.7** — добавить ARCHCODE-SV как proof-of-concept extension (не основной результат)
5. **bioRxiv/arXiv** — Paper 3 как negative-results + SV pivot note

---


## История сессий (краткая)

- **2026-03-08:** bioRxiv submission v2.16, Paper 3 skeleton
- **2026-06-05:** Falsification-First reboot, instrument characterization
- **2026-06-23:** Hypothesis revival, Enformer comparison planned
- **2026-06-24:** 
  - Enformer Stage 1 Complete (HBB, 152/152)
  - Deep research → SV pivot decision
  - ARCHCODE-SV implemented (4h): 9/9 on 2 loci without training

## Auto-commit log
- [2026-06-26 09:38] `7480acc`: feat: ARCHCODE-SV v1.0 вЂ” physics-based structural variant pathogenicity engine
