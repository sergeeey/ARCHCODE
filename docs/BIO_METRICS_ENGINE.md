# Bio-Metrics Engine: Real Hi-C Data Analysis

**Версия:** 1.0  
**Дата:** 25 ноября 2025  
**Статус:** ✅ Готово

---

## 🎯 Цель

Реализовать вычисление всех ключевых биоинформационных метрик для валидации ARCHCODE ↔ реальных Hi-C данных.

---

## 📁 Структура модуля

```
archcode_bio/
├── __init__.py
└── analysis/
    ├── __init__.py
    ├── insulation.py      # Insulation Score
    ├── tad_calls.py       # TAD boundary calling
    ├── compartments.py    # A/B compartment analysis
    ├── ps_curve.py        # P(s) scaling curve
    ├── pearson.py         # Pearson correlation matrix
    └── apa.py             # Aggregate Peak Analysis
```

---

## 🔧 Функции

### 1. `compute_insulation(cool_file, window=5)`

**Назначение:** Вычисление Insulation Score

**Параметры:**
- `cool_file`: путь к .cool или .mcool файлу
- `window`: размер окна в бинах (default: 5)

**Возвращает:**
```json
{
  "insulation_scores": [float, ...],
  "bin_positions": [{"chrom": str, "start": int, "end": int}, ...],
  "mean_insulation": float,
  "std_insulation": float,
  "min_insulation": float,
  "max_insulation": float,
  "window_size": int,
  "num_bins": int
}
```

---

### 2. `call_tads(insulation_data, threshold=0.1)`

**Назначение:** Вызов TAD границ из Insulation Score

**Параметры:**
- `insulation_data`: результат `compute_insulation()`
- `threshold`: порог для детекции (fraction of mean)

**Возвращает:**
```json
{
  "tad_boundaries": [{"chrom": str, "position": int, "insulation_score": float}, ...],
  "tad_domains": [{"chrom": str, "start": int, "end": int}, ...],
  "num_boundaries": int,
  "num_domains": int,
  "threshold": float,
  "threshold_value": float
}
```

---

### 3. `compute_compartments(cool_file)`

**Назначение:** Вычисление A/B компартментов через PCA

**Параметры:**
- `cool_file`: путь к .cool или .mcool файлу

**Возвращает:**
```json
{
  "compartment_labels": ["A" | "B", ...],
  "pc1_scores": [float, ...],
  "compartment_strength": float,
  "compartment_fraction": float,
  "bin_positions": [...],
  "num_bins": int
}
```

---

### 4. `compute_ps_curve(cool_file, bins=50)`

**Назначение:** Вычисление P(s) кривой (contact probability vs distance)

**Параметры:**
- `cool_file`: путь к .cool или .mcool файлу
- `bins`: количество бинов расстояния (logarithmic)

**Возвращает:**
```json
{
  "distances": [float, ...],
  "ps_values": [float, ...],
  "scaling_exponent": float,
  "num_contacts": int,
  "num_bins": int
}
```

---

### 5. `compute_pearson_matrix(cool_file)`

**Назначение:** Вычисление матрицы корреляции Пирсона

**Параметры:**
- `cool_file`: путь к .cool или .mcool файлу

**Возвращает:**
```json
{
  "correlation_matrix": [[float, ...], ...],
  "mean_correlation": float,
  "std_correlation": float,
  "bin_positions": [...],
  "matrix_shape": [int, int]
}
```

---

### 6. `compute_apa(cool_file, loops_list)`

**Назначение:** Aggregate Peak Analysis для валидации петель

**Параметры:**
- `cool_file`: путь к .cool или .mcool файлу
- `loops_list`: список петель `[{"chrom": str, "start1": int, "end1": int, "start2": int, "end2": int}, ...]`

**Возвращает:**
```json
{
  "apa_matrix": [[float, ...], ...],
  "mean_peak_strength": float,
  "peak_detection_rate": float,
  "num_loops": int,
  "window_size": int
}
```

---

## 📊 Использование

### Пример 1: Полный анализ

```python
from archcode_bio.analysis import (
    compute_insulation,
    call_tads,
    compute_compartments,
    compute_ps_curve,
    compute_pearson_matrix,
)

cool_file = "data/real_hic/WT/Rao2014_GM12878_1000kb.cool"

# Insulation
insulation = compute_insulation(cool_file, window=5)

# TADs
tads = call_tads(insulation, threshold=0.1)

# Compartments
compartments = compute_compartments(cool_file)

# P(s)
ps = compute_ps_curve(cool_file, bins=50)

# Pearson
pearson = compute_pearson_matrix(cool_file)
```

### Пример 2: Сохранение результатов

```python
import json
from pathlib import Path

results_dir = Path("results/real_hic_metrics/GM12878")
results_dir.mkdir(parents=True, exist_ok=True)

# Compute and save
insulation = compute_insulation(cool_file)
with open(results_dir / "insulation.json", "w") as f:
    json.dump(insulation, f, indent=2)
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
pytest tests/biometrics/test_real_hic_metrics.py -v
```

### Покрытие тестами

- ✅ `compute_insulation()` — базовый тест
- ✅ `call_tads()` — тест с insulation data
- ✅ `compute_compartments()` — тест PCA
- ✅ `compute_ps_curve()` — тест P(s)
- ✅ `compute_pearson_matrix()` — тест корреляции
- ✅ `compute_apa()` — тест APA
- ✅ JSON serializability — все функции

---

## 📋 Требования

**Зависимости:**
- `cooler` — работа с Hi-C данными
- `bioframe` — работа с геномными интервалами
- `numpy` — численные вычисления
- `scipy` — научные вычисления
- `scikit-learn` — PCA для компартментов

**Установка:**
```bash
pip install cooler bioframe numpy scipy scikit-learn
```

---

## ✅ Definition of Done

- [x] ✅ Все функции реализованы
- [x] ✅ Все функции возвращают JSON-serializable dict
- [x] ✅ Интеграционный тест создан
- [x] ✅ Документация создана

---

## 🔄 Интеграция с ARCHCODE

Bio-Metrics Engine используется в:

1. **Real Hi-C Benchmark** (`run_real_benchmark_summary()`)
2. **RS-12 Sci-Hi-C Validation**
3. **RS-13 Multi-Condition Benchmark**

Все метрики вычисляются независимо от ARCHCODE и могут использоваться для сравнения.

---

*Готово к использованию для валидации ARCHCODE против реальных данных.*




