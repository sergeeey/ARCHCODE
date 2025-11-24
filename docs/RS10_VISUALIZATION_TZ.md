# 🔧 Эталонное ТЗ для Cursor: RS-10 Experiment B Visualization

## Задача

Создать полный пакет визуализаций для RS-10 Experiment B: Processivity × Bookmarking Matrix.

**Цель:** Превратить данные из `RS10_processivity_bookmarking_matrix.json` в publication-quality фигуры для статьи.

---

## 0. Контекст

1. **Данные готовы:** `data/output/RS10_processivity_bookmarking_matrix.json`
   - 80 комбинаций параметров
   - Метрики: stability, jaccard, matched_stable, collapse_events, risk

2. **Параметры:**
   - NIPBL velocity: [0.3, 0.6, 1.0, 1.3]
   - WAPL lifetime: [0.3, 0.6, 1.0, 1.3]
   - Bookmarking fractions: [0.0, 0.25, 0.5, 0.75, 1.0]

3. **Диапазоны метрик:**
   - Jaccard: 0.000 - 1.000
   - Stability: 0.057 - 0.895

---

## 1. Что нужно создать

### Файл: `experiments/visualize_RS10_matrix.py`

Скрипт для генерации всех визуализаций.

---

## 2. Фигуры для создания

### Figure 1: Stability Heatmap (Processivity × Bookmarking)

**Тип:** 2D Heatmap

**Оси:**
- X: Processivity (вычисляется как NIPBL × WAPL)
- Y: Bookmarking fraction [0.0, 0.25, 0.5, 0.75, 1.0]

**Цвет:** Average stability after recovery (0.0-1.0)

**Требования:**
- Цветовая схема: RdYlGn (красный-желтый-зеленый)
- Contour lines для фазовых границ
- Отметить критические пороги (stability = 0.5, 0.7)

**Файл:** `figures/RS10/RS10_stability_heatmap.png`

---

### Figure 2: Jaccard Index Heatmap (Architectural Memory)

**Тип:** 2D Heatmap

**Оси:** Те же (Processivity × Bookmarking)

**Цвет:** Jaccard index (0.0-1.0) - мера восстановления архитектуры

**Требования:**
- Цветовая схема: Blues (синий = полное восстановление)
- Contour lines для критических значений (Jaccard = 0.5, 0.7)
- Отметить зоны "полного восстановления" (Jaccard > 0.7)

**Файл:** `figures/RS10/RS10_jaccard_heatmap.png`

---

### Figure 3: 3D Surface Plot (Memory Surface)

**Тип:** 3D Surface

**Оси:**
- X: Processivity
- Y: Bookmarking fraction
- Z: Jaccard index (высота поверхности)

**Требования:**
- Плавная поверхность с цветовым кодированием высоты
- Вид сверху как heatmap
- Отметить "обрывы" (cliffs) где память резко падает

**Файл:** `figures/RS10/RS10_3d_memory_surface.png`

---

### Figure 4: Critical Lines Plot

**Тип:** Line Plot

**Оси:**
- X: Processivity
- Y: Bookmarking fraction

**Линии:**
- Линия минимального bookmarking для восстановления (Jaccard > 0.5)
- Линия оптимального bookmarking (Jaccard > 0.7)
- Линия processivity compensation (где низкий processivity компенсируется высоким bookmarking)

**Требования:**
- Разные стили линий для разных порогов
- Легенда с объяснением
- Отметить зоны: "Recovery", "Partial", "Failure"

**Файл:** `figures/RS10/RS10_critical_lines.png`

---

### Figure 5: Bookmarking Compensation Analysis

**Тип:** Multi-panel Figure

**Панели:**
- A: Stability vs Bookmarking (для разных уровней processivity)
- B: Jaccard vs Bookmarking (для разных уровней processivity)
- C: Минимальный bookmarking для восстановления vs Processivity

**Требования:**
- Показывает компенсацию: как bookmarking компенсирует низкий processivity
- Отметить критические точки

**Файл:** `figures/RS10/RS10_bookmarking_compensation.png`

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
with open("data/output/RS10_processivity_bookmarking_matrix.json") as f:
    data = json.load(f)
```

Построить матрицы:
- Для каждого (processivity, bookmarking_fraction) → значение метрики
- Использовать numpy для создания 2D массивов

---

## 4. Definition of Done

### ✔ Создан файл `experiments/visualize_RS10_matrix.py`

### ✔ Скрипт запускается без ошибок

### ✔ Генерируются все 5 фигур

### ✔ Фигуры сохранены в `figures/RS10/`

### ✔ Фигуры имеют publication-quality формат

### ✔ Легенды и подписи понятны

---

## 5. Дополнительные требования

### Логирование

Каждый шаг должен писать:
```
[RS-10-Viz] Loading data...
[RS-10-Viz] Building stability heatmap...
[RS-10-Viz] Saving figure: figures/RS10/RS10_stability_heatmap.png
```

### Обработка данных

- Построить 2D матрицы из JSON данных
- Интерполяция для плавных поверхностей (опционально)
- Обработка edge cases (NaN, missing data)

### Оптимизация

- Кэширование загруженных данных
- Эффективная работа с большими матрицами

---

## 6. Финальная формулировка для Cursor

**Cursor, выполняй следующее:**

> Создай скрипт `experiments/visualize_RS10_matrix.py` для визуализации RS-10 Experiment B.
> 
> Загрузи данные из `data/output/RS10_processivity_bookmarking_matrix.json`.
> 
> Построй 5 фигур:
> 1. Stability heatmap (Processivity × Bookmarking)
> 2. Jaccard heatmap (Architectural Memory)
> 3. 3D Surface plot (Memory Surface)
> 4. Critical lines plot
> 5. Bookmarking compensation analysis
> 
> Используй matplotlib, seaborn, numpy.
> Сохрани фигуры в `figures/RS10/` с publication-quality форматом (300 DPI).
> Добавь логирование и обработку ошибок.
> 
> Не изменяй существующие файлы — создавай новый скрипт.

---

**Дата:** 23 ноября 2025  
**Статус:** Ready for Implementation






