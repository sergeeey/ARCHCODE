# 🔧 Эталонное ТЗ для Cursor: Risk Mitigation Sprint

## Задача: Risk Mitigation Sprint для RS-09 + RS-10

**Цель:** Укрепить модель перед публикацией, адресовав три зоны риска:
1. Compartmentalization (A/B-компартменты)
2. Интерпретация NIPBL как "velocity"
3. Bookmarking threshold (30–40%)

---

## БЛОК A — Processivity vs локальная среда (CTCF/компартменты)

### Задача A1: Добавить локальный модификатор EffectiveProcessivity

**Цель:** Показать, что глобальный processivity остается основным параметром, даже при локальных вариациях.

**Что сделать:**

1. **Создать модуль:** `src/archcode_core/environmental_factors.py`

2. **Реализовать функцию:**
   ```python
   def calculate_effective_processivity(
       global_processivity: float,
       position: int,
       ctcf_density_map: dict[int, float],
       compartment_mask: dict[int, str] | None = None,
   ) -> float:
       """
       Calculate effective processivity with local environmental factors.
       
       Args:
           global_processivity: Global processivity (NIPBL × WAPL)
           position: Genomic position
           ctcf_density_map: Map of CTCF site density (0.0-1.0)
           compartment_mask: Optional A/B compartment mask
       
       Returns:
           Effective processivity (0.0-2.0)
       """
       # Base: CTCF density factor (0.5-1.5)
       ctcf_factor = 0.5 + ctcf_density_map.get(position, 0.5)
       
       # Optional: Compartment factor
       compartment_factor = 1.0
       if compartment_mask:
           compartment = compartment_mask.get(position, "B")
           # A compartments: slightly higher processivity
           compartment_factor = 1.1 if compartment == "A" else 0.95
       
       env_factor = ctcf_factor * compartment_factor
       effective_processivity = global_processivity * env_factor
       
       return max(0.0, min(2.0, effective_processivity))
   ```

3. **Интегрировать в pipeline:**
   - Добавить параметр `enable_env_factors: bool = False` в `ARCHCODEPipeline`
   - При расчете stability использовать `effective_processivity` вместо `global_processivity`

---

### Задача A2: Robustness-анализ

**Цель:** Проверить, что фазовая структура сохраняется при включении env_factors.

**Что сделать:**

1. **Создать эксперимент:** `experiments/run_RS09_env_factor_robustness.py`

2. **Параметры:**
   - Global processivity values: [0.3, 0.5, 0.7, 1.0, 1.3]
   - Два режима:
     - Без env_factors (baseline)
     - С env_factors включенными

3. **Метрики для сравнения:**
   - Фазовая структура (unstable / transitional / stable)
   - Критические пороги processivity
   - Average stability
   - Collapse probability

4. **Сохранить результаты:**
   - `data/output/RS09_env_factor_robustness.json`

**Ожидаемый результат:**
- Фазовые режимы сохраняются
- Критические пороги могут немного сдвинуться, но не исчезнуть
- Глобальный processivity остается основным параметром

---

### Задача A3: Compartmentalization check (опционально)

**Цель:** Показать, что изменение global processivity влияет на TAD-level stability, а не на A/B-паттерн.

**Что сделать:**

1. **Создать простую A/B-маску:**
   ```python
   def create_synthetic_compartment_mask(
       positions: list[int],
       compartment_size: int = 500000,
   ) -> dict[int, str]:
       """
       Create synthetic A/B compartment mask.
       
       Alternating A/B compartments of given size.
       """
       mask = {}
       for i, pos in enumerate(positions):
           compartment_idx = pos // compartment_size
           mask[pos] = "A" if compartment_idx % 2 == 0 else "B"
       return mask
   ```

2. **Проверить:**
   - Изменение global processivity не меняет A/B-паттерн
   - Влияет только на TAD-level insulation

---

## БЛОК B — NIPBL: velocity vs loading rate

### Задача B1: Альтернативные сценарии NIPBL

**Цель:** Показать, что effective processivity остается ключевым параметром при разных механизмах действия NIPBL.

**Что сделать:**

1. **Создать модуль:** `src/archcode_core/nipbl_mechanisms.py`

2. **Реализовать три режима:**

   ```python
   class NIPBLMechanism(Enum):
       VELOCITY_ONLY = "velocity_only"  # Текущий режим
       DENSITY_ONLY = "density_only"    # Влияние на density экструдеров
       MIXED = "mixed"                   # Комбинированный
   
   def calculate_effective_extrusion_rate(
       nipbl_factor: float,
       mechanism: NIPBLMechanism,
       base_velocity: float = 1.0,
       base_density: float = 1.0,
   ) -> tuple[float, float]:
       """
       Calculate effective extrusion rate and density.
       
       Returns:
           (effective_velocity, effective_density)
       """
       if mechanism == NIPBLMechanism.VELOCITY_ONLY:
           return (base_velocity * nipbl_factor, base_density)
       elif mechanism == NIPBLMechanism.DENSITY_ONLY:
           return (base_velocity, base_density * nipbl_factor)
       elif mechanism == NIPBLMechanism.MIXED:
           # Например: 70% velocity, 70% density
           return (
               base_velocity * (nipbl_factor ** 0.7),
               base_density * (nipbl_factor ** 0.7)
           )
   ```

3. **Переопределить effective processivity:**
   ```python
   effective_processivity = effective_extrusion_rate * cohesin_lifetime
   ```
   где `effective_extrusion_rate` учитывает и velocity, и density.

---

### Задача B2: Сравнительный анализ механизмов

**Цель:** Проверить, что фазовая структура сохраняется при разных механизмах.

**Что сделать:**

1. **Создать эксперимент:** `experiments/run_RS09_nipbl_mechanisms_comparison.py`

2. **Параметры:**
   - NIPBL factors: [0.3, 0.5, 0.7, 1.0, 1.3]
   - WAPL lifetime: [0.3, 0.6, 1.0, 1.3]
   - Три режима: velocity_only, density_only, mixed

3. **Для каждого режима:**
   - Рассчитать effective_processivity
   - Запустить ограниченный sweep (например, 3×3 = 9 точек)
   - Измерить stability metrics

4. **Сравнить:**
   - Фазовая структура по effective_processivity
   - Критические пороги
   - Сохранение закономерностей

5. **Сохранить результаты:**
   - `data/output/RS09_nipbl_mechanisms_comparison.json`

**Ожидаемый результат:**
- Фазовая структура сохраняется
- Критические пороги по effective_processivity остаются примерно теми же
- Effective processivity остается ключевым параметром

---

## БЛОК C — Bookmarking Threshold и перколяционная природа

### Задача C1: Детальный анализ порога bookmarking

**Цель:** Показать, что порог 30–40% не произволен, а возникает как перколяционный переход.

**Что сделать:**

1. **Расширить RS-10 Experiment C:**
   - Добавить больше точек: bookmarking_fraction = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
   - Увеличить число циклов до 20

2. **Для каждого bookmarking_fraction:**
   - Запустить симуляцию на 20 циклов
   - Измерить метрики:
     - Jaccard index (baseline vs cycle N)
     - Largest connected stable component size
     - Entropy конфигурации границ
     - Memory retention score

3. **Построить кривые:**
   - Jaccard vs cycle (для разных fractions)
   - Entropy vs cycle
   - Memory retention vs bookmarking_fraction (после N циклов)

4. **Проверить перколяционный переход:**
   - Искать резкий излом в районе 0.3–0.4
   - При < threshold: Jaccard → 0 быстро
   - При > threshold: Jaccard остается выше уровня

---

### Задача C2: Визуализация порога

**Цель:** Создать фигуры, показывающие перколяционный переход.

**Что сделать:**

1. **Создать скрипт:** `experiments/visualize_bookmarking_threshold.py`

2. **Фигуры:**
   - `bookmarking_threshold_jaccard.png` — Jaccard vs bookmarking_fraction (после N циклов)
   - `bookmarking_threshold_entropy.png` — Entropy vs bookmarking_fraction
   - `bookmarking_threshold_curves.png` — Jaccard vs cycle для разных fractions

3. **Отметить критический порог:**
   - Вертикальная линия на 0.3–0.4
   - Аннотация: "Percolation-like transition"

---

### Задача C3: Второй канал памяти (опционально)

**Цель:** Показать, что добавление второго канала памяти сдвигает порог вниз.

**Что сделать:**

1. **Добавить transcriptional memory:**
   ```python
   def apply_transcriptional_memory(
       boundaries: list[Boundary],
       transcription_map: dict[int, float],
       threshold: float = 0.5,
   ) -> None:
       """
       Mark boundaries as "memory-enabled" if nearby transcription > threshold.
       """
       for boundary in boundaries:
           transcription_level = transcription_map.get(boundary.position, 0.0)
           if transcription_level > threshold:
               boundary.has_transcriptional_memory = True
   ```

2. **Модифицировать recovery:**
   - Границы с transcriptional_memory восстанавливаются независимо от CTCF bookmarking

3. **Повторить анализ:**
   - CTCF-only
   - CTCF + transcriptional memory
   - Сравнить пороги

---

## Ожидаемые результаты

### JSON файлы:
1. `data/output/RS09_env_factor_robustness.json`
2. `data/output/RS09_nipbl_mechanisms_comparison.json`
3. `data/output/RS10_bookmarking_threshold_analysis.json`

### Фигуры:
1. `figures/RS10/bookmarking_threshold_jaccard.png`
2. `figures/RS10/bookmarking_threshold_entropy.png`
3. `figures/RS10/bookmarking_threshold_curves.png`

### Выводы для статьи:
- Устойчивость фазовой структуры к локальным env-факторам
- Effective processivity остается главным параметром при разных механизмах NIPBL
- Наличие перколяционно-похожего порога bookmarking
- Возможное смещение порога при добавлении второго канала памяти

---

## Definition of Done

### ✔ Все три блока реализованы

### ✔ Эксперименты запускаются без ошибок

### ✔ Результаты сохранены в JSON

### ✔ Фигуры созданы

### ✔ Выводы задокументированы

### ✔ Существующие эксперименты RS-09/RS-10 не ломаются

---

**Дата:** 23 ноября 2025  
**Статус:** Ready for Implementation






