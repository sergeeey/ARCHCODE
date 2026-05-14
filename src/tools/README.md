# Cross-Omics Orthogonality Detector

**Version:** 1.0  
**Author:** Sergey Boyko (ARCHCODE Project)  
**Date:** 2026-05-14  
**License:** MIT  

---

## 🎯 Назначение

Классифицирует отношения между двумя методами измерения (omics datasets, ML predictions, биомаркеры) как:

| Класс | Корреляция (ρ) | Группы разделяются | Интерпретация | Действие |
|-------|----------------|-------------------|---------------|----------|
| **CONCORDANT** | ρ > 0.5 | Оба/один | Измеряют одно и то же | Выбрать один метод |
| **ORTHOGONAL** | -0.3 < ρ < 0.3 | **Оба** | Измеряют РАЗНЫЕ механизмы | **Комбинировать!** |
| **WEAK-ORTHOGONAL** | -0.3 < ρ < 0.3 | **Только один** | Разные механизмы, один сильнее | Использовать сильный |
| **CONFLICTING** | ρ < -0.3 | Противоречат | Один ошибочен | Разобраться |
| **AMBIGUOUS** | - | Ни один | Проблема с данными | Проверить метки |

---

## 🧬 Мотивация (ARCHCODE Case Study)

**Проблема:**  
В 2026-05-08 мы анализировали ARCHCODE (3D structure) × AlphaGenome (transcription):
- Корреляция: ρ = 0.077 (почти ноль)
- Первая реакция: "Методы не согласуются, один не работает" ❌

**Реальность:**  
Оба работают, но измеряют **ортогональные механизмы**:
- ARCHCODE: структурные disruptions (Hi-C, chromatin loops)
- AlphaGenome: функциональные disruptions (CAGE, promoter activity)

**Вывод:**  
Низкая корреляция ≠ провал. Может означать **дополнительность** (как термометр + барометр).

---

## 🚀 Установка

```bash
# Требования
pip install numpy scipy

# Копировать файл
cp orthogonality_detector.py your_project/
```

---

## 📖 Использование

### Пример 1: ORTHOGONAL (ARCHCODE × AlphaGenome)

```python
import numpy as np
from orthogonality_detector import classify_orthogonality, print_result

# Реальные данные: ARCHCODE SSIM vs AlphaGenome CAGE delta
A = np.array([0.95, 0.93, 0.87, ...])  # structural scores
B = np.array([-0.18, -0.12, -0.35, ...])  # functional scores
labels = np.array([1, 1, 1, 0, 0, 0, ...])  # pathogenic=1, benign=0

result = classify_orthogonality(A, B, labels)
print_result(result)

# Output:
# CLASSIFICATION: WEAK-ORTHOGONAL
# ρ = 0.069 ≈ 0 (низкая корреляция)
# Метод B значим (p=0.0006), метод A слабее (p=0.21, CV=3.4%)
# Интерпретация: методы ортогональны, используйте оба (AlphaGenome сильнее на этом датасете)
```

### Пример 2: CONCORDANT (synthetic)

```python
A = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
B = A * 1.2 + np.random.normal(0, 0.3, 10)  # высокая корреляция
labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

result = classify_orthogonality(A, B, labels)
# Output: CONCORDANT (ρ ≈ 1.0)
```

### Пример 3: CONFLICTING (synthetic)

```python
A = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
B = -A + np.random.normal(0, 0.5, 10)  # отрицательная корреляция
labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])

result = classify_orthogonality(A, B, labels)
# Output: CONFLICTING (ρ < -0.3)
```

### Batch Processing

```python
from orthogonality_detector import batch_classify

datasets = [
    ("ARCHCODE_x_AlphaGenome", A1, B1, labels1),
    ("CAGE_x_ATAC", A2, B2, labels2),
    ("VEP_x_CADD", A3, B3, labels3),
]

results = batch_classify(datasets)
for name, res in results.items():
    print(f"{name}: {res['classification']} (ρ={res['rho']:.3f})")
```

---

## 🔬 Методология

### 1. Корреляция Спирмена (ранговая)
- Устойчива к выбросам
- Не требует линейности (monotonic relationship)

### 2. Mann-Whitney U test (two-sided)
- Проверяет разделяют ли группы (pathogenic vs benign)
- Независимо для каждого метода

### 3. Коэффициент вариации (CV)
- Проверка разброса данных: CV = (σ / |μ|) × 100%
- Warning если CV < 5% (корреляция ненадёжна)

### 4. Классификация (4-tier + AMBIGUOUS)

**Логика:**

```
if ρ > 0.5:
    → CONCORDANT (измеряют одно и то же)

elif -0.3 ≤ ρ ≤ 0.3:
    if оба метода разделяют группы (p < 0.05):
        → ORTHOGONAL (дополняют друг друга) ✅ КОМБИНИРОВАТЬ
    elif только один метод разделяет:
        → WEAK-ORTHOGONAL (один сильнее на этом датасете)
    else:
        → AMBIGUOUS (проблема с данными)

elif ρ < -0.3:
    → CONFLICTING (методы противоречат)
```

---

## ⚠️ Limitations & Caveats

### 1. Малая выборка (N < 15)
- Корреляция и Mann-Whitney ненадёжны
- Рекомендуется N ≥ 30 для стабильных результатов

### 2. Низкая вариация (CV < 5%)
- Корреляция может быть артефактом
- **Пример:** ARCHCODE на HBB pearls (CV=3.4%) → все SSIM близки → слабый сигнал

### 3. Неравные группы
- Если pathogenic/benign сильно несбалансированы (например 5 vs 50) → Mann-Whitney смещён
- Рекомендуется баланс ±30% (например 10 vs 15 OK, 5 vs 50 плохо)

### 4. Категориальные конфаундеры
- Если группы отобраны по категории (promoter vs missense) → может маскировать корреляцию
- **Пример:** ARCHCODE pearls отобраны по promoter → SSIM вариация низкая

### 5. Бинарные метки
- Инструмент работает только с binary classification (pathogenic/benign)
- Для multi-class нужна модификация (one-vs-rest)

---

## 📊 Реальные примеры (ARCHCODE Project)

### Test 1: ARCHCODE × AlphaGenome (HBB pearl dataset)

**Данные:**
- N = 32 variants (13 pathogenic pearls, 19 benign controls)
- ARCHCODE: Local Structural Similarity Index (LSSIM, 0-1)
- AlphaGenome: CAGE delta % (transcription change)

**Результат:**
```
Classification: WEAK-ORTHOGONAL
ρ = 0.069 (p = 0.71, не значимо)
ARCHCODE: p = 0.21 (не разделяет)
AlphaGenome: p = 0.0006 (разделяет)
CV: ARCHCODE 3.4% (LOW), AlphaGenome 124.5% (OK)
```

**Интерпретация:**
- Методы ортогональны (ρ ≈ 0)
- AlphaGenome сильнее на ЭТОМ датасете
- Причина слабости ARCHCODE: pearls отобраны по category (promoter), не по structural disruption → малая вариация SSIM

**Вывод:**
ARCHCODE × AlphaGenome **дополняют** друг друга:
- ARCHCODE: сильнее на structural variants (enhancer loops)
- AlphaGenome: сильнее на transcriptional variants (promoter motifs)

---

## 🧪 Тесты

```bash
# Demo (3 synthetic examples)
python orthogonality_detector.py

# Реальные данные (ARCHCODE × AlphaGenome)
python test_real_archcode_alphag.py

# Визуализация (single plot)
python plot_classification.py

# Batch examples (2×2 grid)
python test_batch_examples.py
```

**Expected output:**
```
Test 1: WEAK-ORTHOGONAL (real ARCHCODE × AlphaGenome)
Test 2: CONCORDANT (synthetic high correlation)
Test 3: CONFLICTING (synthetic negative correlation)
Batch: 4 examples in 2×2 grid
```

**Figures generated:**
- `results/fig_orthogonality_archcode_alphag.png` — single plot (ARCHCODE × AlphaGenome)
- `results/fig_orthogonality_batch_examples.png` — batch plot (4 examples)

---

## 🌍 Применения (вне геномики)

### 1. Machine Learning Ensemble
**Вопрос:** Стоит ли комбинировать два ML-модели?
- A = Model 1 predictions
- B = Model 2 predictions
- labels = ground truth
- **ORTHOGONAL** → ensemble улучшит (разные фичи)
- **CONCORDANT** → ensemble бесполезен (дублируют)

### 2. Медицинские биомаркеры
**Вопрос:** Два теста крови дают разную информацию?
- A = Cholesterol levels
- B = Blood pressure
- labels = cardiovascular disease
- **ORTHOGONAL** → оба теста нужны

### 3. Финансовые индикаторы
**Вопрос:** Income и Debt независимы для credit scoring?
- A = Income
- B = Debt
- labels = default risk
- **WEAK-ORTHOGONAL** → Debt сильнее, но Income добавляет информацию

---

## 📚 References

### Scientific Background

1. **Spearman Rank Correlation**  
   Spearman, C. (1904). "The Proof and Measurement of Association between Two Things."  
   *American Journal of Psychology*, 15(1), 72–101.

2. **Mann-Whitney U Test**  
   Mann, H. B., & Whitney, D. R. (1947). "On a Test of Whether one of Two Random Variables is Stochastically Larger than the Other."  
   *Annals of Mathematical Statistics*, 18(1), 50–60.

3. **Orthogonality in Multi-Omics**  
   Subramanian, I., et al. (2020). "Multi-omics Data Integration, Interpretation, and Its Application."  
   *Bioinformatics and Biology Insights*, 14, 1177932219899051.

### ARCHCODE Project (Case Study)

4. **ADR-028: ARCHCODE × AlphaGenome Concordance — NULL (Orthogonal Mechanisms)**  
   Boyko, S. (2026-05-08). ARCHCODE Project Documentation.  
   DOI: 10.21203/rs.3.rs-9090074/v1

5. **AlphaGenome Mechanism Specificity Brief**  
   Boyko, S. (2026-05-09). 7/7 loci perfect mechanism specificity validation.

---

## 🤝 Contributing

Contributions welcome! Особенно:
- Multi-class support (one-vs-rest)
- Non-parametric correlation alternatives (Kendall tau, distance correlation)
- Visualizations (scatter plots with classification overlay)
- More real-world examples

---

## 📄 License

MIT License

Copyright (c) 2026 Sergey Boyko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📧 Contact

**Sergey Boyko**  
Ronin Institute RIIS 2.0 Fellow (confirmed April 21, 2026)  
Email: sergeikuch80@gmail.com  
ORCID: https://orcid.org/0009-0009-2178-5701  
GitHub: https://github.com/geoserg/archcode  

---

**Version History:**
- v1.0 (2026-05-14): Initial release
  - 4 classification types: CONCORDANT, ORTHOGONAL, WEAK-ORTHOGONAL, CONFLICTING
  - Real-world validation: ARCHCODE × AlphaGenome
  - Batch processing support
  - CV and small-N warnings
