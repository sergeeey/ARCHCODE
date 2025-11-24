# 🔧 Эталонное ТЗ для Cursor: RS-10 Experiment C Visualization

## Задача

Создать полный пакет визуализаций для RS-10 Experiment C: Pathological Bookmarking Defects & Multi-Cycle Drift.

**Цель:** Превратить данные из `RS10_pathological_bookmarking.json` в publication-quality фигуры, показывающие деградацию архитектурной памяти через клеточные циклы.

---

## 0. Контекст

1. **Данные готовы:** `data/output/RS10_pathological_bookmarking.json`
   - Множественные сценарии (complete loss, partial defect, threshold sweep, compensation)
   - Метрики для каждого цикла: Jaccard, Stability, Entropy, Drift Distance, Memory Retention

2. **Ключевые метрики:**
   - `jaccard_vs_baseline` — восстановление архитектуры относительно исходного состояния
   - `jaccard_vs_previous` — drift между соседними циклами
   - `entropy` — архитектурная энтропия (мера "уплывания")
   - `position_entropy` — энтропия позиций границ
   - `drift_distance` — средний сдвиг позиций (bp)
   - `memory_retention_score` — комбинированная метрика памяти

3. **Сценарии:**
   - Complete bookmarking loss (0.0)
   - Partial defect (0.3)
   - Threshold sweep (0.0-1.0)
   - Processivity compensation

---

## 1. Что нужно создать

### Файл: `experiments/visualize_RS10_pathological.py`

Скрипт для генерации всех визуализаций Experiment C.

---

## 2. Фигуры для создания

### Figure 1: Drift Curves (Jaccard per Cycle)

**Тип:** Multi-line Plot

**Оси:**
- X: Cycle number (0-20)
- Y: Jaccard index vs baseline (0.0-1.0)

**Линии:**
- Complete loss (bookmarking=0.0)
- Partial defect (bookmarking=0.3)
- Threshold sweep (bookmarking=0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
- Processivity compensation (different processivity levels)

**Требования:**
- Разные цвета для разных сценариев
- Легенда с объяснением
- Отметить критические точки (Jaccard < 0.3 = collapse)
- Показать тренды деградации

**Файл:** `figures/RS10/RS10_drift_curves.png`

---

### Figure 2: Entropy Growth Curves

**Тип:** Multi-line Plot

**Оси:**
- X: Cycle number
- Y: Architecture entropy (0.0-1.0)

**Линии:** Те же сценарии

**Требования:**
- Показать рост энтропии (распад памяти)
- Отметить зоны: Low entropy (memory intact) vs High entropy (memory lost)

**Файл:** `figures/RS10/RS10_entropy_growth.png`

---

### Figure 3: Drift Distance Evolution

**Тип:** Multi-line Plot

**Оси:**
- X: Cycle number
- Y: Average drift distance (bp)

**Линии:** Те же сценарии

**Требования:**
- Показать накопление сдвигов позиций
- Отметить критические пороги (drift > 20kb)

**Файл:** `figures/RS10/RS10_drift_distance.png`

---

### Figure 4: Memory Retention Heatmap

**Тип:** 2D Heatmap

**Оси:**
- X: Cycle number
- Y: Bookmarking fraction (или Processivity)

**Цвет:** Memory retention score (0.0-1.0)

**Требования:**
- Показать зоны сохранения памяти
- Contour lines для критических порогов
- Отметить "memory collapse zone"

**Файл:** `figures/RS10/RS10_memory_retention_heatmap.png`

---

### Figure 5: Processivity × Bookmarking × Cycles Surface

**Тип:** 3D Surface Plot или Multi-panel Heatmaps

**Оси:**
- X: Processivity
- Y: Bookmarking fraction
- Z: Final Jaccard (after N cycles)

**Требования:**
- Показать 3D поверхность памяти
- Или серию heatmaps для разных циклов (cycle 5, 10, 15, 20)
- Отметить критические линии компенсации

**Файл:** `figures/RS10/RS10_memory_surface_3d.png` или `RS10_memory_heatmaps_series.png`

---

### Figure 6: Combined Analysis (Multi-panel)

**Тип:** Multi-panel Figure (2×2 или 2×3)

**Панели:**
- A: Drift curves (Jaccard)
- B: Entropy growth
- C: Drift distance
- D: Memory retention heatmap (или summary)

**Требования:**
- Publication-quality layout
- Согласованные цветовые схемы
- Подписи панелей (A, B, C, D)

**Файл:** `figures/RS10/RS10_combined_analysis.png`

---

## 3. Технические требования

### Библиотеки

- `matplotlib` для базовых графиков
- `seaborn` для heatmaps
- `numpy` для обработки данных
- `mpl_toolkits.mplot3d` для 3D plots

### Стиль

- Publication-quality (300 DPI)
- Цветовая схема для печати (CMYK-friendly)
- Подписи осей на английском
- Легенды с объяснениями

### Структура данных

Загрузить JSON:
```python
with open("data/output/RS10_pathological_bookmarking.json") as f:
    data = json.load(f)
```

Обработать циклы:
- Для каждого сценария извлечь `cycles` массив
- Построить временные ряды для каждой метрики
- Группировать по типам сценариев

---

## 4. Definition of Done

### ✔ Создан файл `experiments/visualize_RS10_pathological.py`

### ✔ Скрипт запускается без ошибок

### ✔ Генерируются все 6 фигур

### ✔ Фигуры сохранены в `figures/RS10/`

### ✔ Фигуры имеют publication-quality формат

### ✔ Легенды и подписи понятны

---

## 5. Дополнительные требования

### Логирование

Каждый шаг должен писать:
```
[RS-10-C-Viz] Loading data...
[RS-10-C-Viz] Building drift curves...
[RS-10-C-Viz] Saving figure: figures/RS10/RS10_drift_curves.png
```

### Обработка данных

- Извлечение циклов из JSON
- Построение временных рядов
- Группировка по сценариям
- Обработка edge cases (NaN, missing cycles)

### Оптимизация

- Кэширование загруженных данных
- Эффективная работа с временными рядами

---

## 6. Финальная формулировка для Cursor

**Cursor, выполняй следующее:**

> Создай скрипт `experiments/visualize_RS10_pathological.py` для визуализации RS-10 Experiment C.
> 
> Загрузи данные из `data/output/RS10_pathological_bookmarking.json`.
> 
> Построй 6 фигур:
> 1. Drift curves (Jaccard per cycle)
> 2. Entropy growth curves
> 3. Drift distance evolution
> 4. Memory retention heatmap
> 5. Processivity × Bookmarking × Cycles surface
> 6. Combined analysis (multi-panel)
> 
> Используй matplotlib, seaborn, numpy.
> Сохрани фигуры в `figures/RS10/` с publication-quality форматом (300 DPI).
> Добавь логирование и обработку ошибок.
> 
> Не изменяй существующие файлы — создавай новый скрипт.

---

**Дата:** 23 ноября 2025  
**Статус:** Ready for Implementation






