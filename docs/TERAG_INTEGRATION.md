# TERAG ↔ ARCHCODE Integration Guide

**Версия:** 1.0  
**Дата:** 25 ноября 2025  
**Статус:** Active

---

## 🎯 Обзор

Интеграция ARCHCODE с TERAG (TErritorial RAG) позволяет использовать ARCHCODE как физический движок под управлением когнитивного слоя TERAG.

**Архитектура:**
```
TERAG (когнитивный слой)
    ↓
ArchcodeAdapter (адаптер)
    ↓
ARCHCODE Core (физический движок)
    ↓
Domain Validator (биофизическая валидация)
    ↓
T.R.A.C. Reasoning (интерпретация результатов)
```

---

## 📁 Структура интеграции

```
ARCHCODE/
├── src/
│   ├── archcode_core/
│   │   └── api.py                    # API функции для экспериментов
│   └── integration/
│       └── archcode_adapter.py       # Адаптер TERAG ↔ ARCHCODE
├── terag_missions/
│   ├── rs09_processivity_phase.yaml
│   ├── rs10_bookmarking_threshold.yaml
│   └── rs11_multichannel_memory.yaml
├── terag_plugins/
│   └── genome_architecture/
│       └── validator.py              # Биофизический валидатор
└── tests/
    └── integration/
        └── test_terag_archcode_integration.py
```

---

## 🚀 Быстрый старт

### 1. Запуск миссии через адаптер

```python
from src.integration.archcode_adapter import ArchcodeAdapter

# Создать адаптер
adapter = ArchcodeAdapter(mode="fast")  # или "production"

# Запустить миссию
mission_config = {
    "id": "RS11-MEM-001",
    "mission_type": "rs11_multichannel_memory",
    "parameters": {
        "bookmarking_range": (0.0, 1.0, 7),
        "epigenetic_range": (0.0, 1.0, 5),
        "num_cycles": 20,
        "processivity": 0.9,
    },
}

result = adapter.run_mission(mission_config)
print(result)
```

### 2. Валидация результатов

```python
from terag_plugins.genome_architecture.validator import validate_archcode_result

# Валидировать результат
validation = validate_archcode_result(result)

print(f"Valid: {validation['valid']}")
print(f"Issues: {validation['issues']}")
print(f"Derived metrics: {validation['derived_metrics']}")
```

### 3. Загрузка миссии из YAML

```python
import yaml

# Загрузить миссию
with open("terag_missions/rs11_multichannel_memory.yaml") as f:
    mission_config = yaml.safe_load(f)

# Запустить
adapter = ArchcodeAdapter(mode=mission_config["adapter"]["mode"])
result = adapter.run_mission(mission_config)
```

---

## 📊 Типы миссий

### RS-09: Processivity Phase Diagram

**Тип:** `rs09_processivity_phase`

**Параметры:**
- `processivity_min`: минимальное значение processivity (default: 0.0)
- `processivity_max`: максимальное значение (default: 2.0)
- `processivity_steps`: количество точек (fast: 10, production: 50)

**Возвращает:**
- `phase_diagram`: классификация фаз по processivity
- `critical_points`: пороги перехода между фазами
- `stability_metrics`: статистика стабильности
- `stable_fraction`: доля стабильной фазы

---

### RS-10: Bookmarking Threshold

**Тип:** `rs10_bookmarking_threshold`

**Параметры:**
- `bookmarking_range`: список значений или tuple(min, max, steps)
- `num_cycles`: количество циклов (fast: 10, production: 50)
- `processivity`: фиксированное значение processivity (default: 0.9)

**Возвращает:**
- `bookmarking_grid`: метрики для каждого значения bookmarking
- `drift_curves`: кривые дрейфа по циклам
- `entropy`: значения энтропии
- `estimated_threshold`: оценка критического порога

---

### RS-11: Multichannel Memory

**Тип:** `rs11_multichannel_memory`

**Параметры:**
- `bookmarking_range`: tuple(min, max, steps) (fast: 7, production: 50)
- `epigenetic_range`: tuple(min, max, steps) (fast: 5, production: 50)
- `num_cycles`: количество циклов (fast: 20, production: 100)
- `processivity`: фиксированное значение (default: 0.9)

**Возвращает:**
- `memory_matrix`: 2D матрица памяти
- `critical_surface`: точки на критической поверхности
- `phase_regimes`: классификация режимов
- `critical_line`: критическая линия

---

### Real Hi-C Benchmark

**Тип:** `real_hic_benchmark`

**Параметры:**
- `real_cooler_path`: путь к .cool файлу
- `nipbl_velocity`: фактор скорости NIPBL (default: 1.0)
- `wapl_lifetime`: фактор времени жизни WAPL (default: 1.0)

**Возвращает:**
- `insulation_correlation`: корреляция Insulation Score
- `ps_correlation`: корреляция P(s) scaling
- `summary_stats`: сводная статистика
- `pass_fail`: флаги валидации

---

## 🔧 Режимы работы

### Fast Mode

**Использование:** Разработка, тестирование, быстрые проверки

**Параметры:**
- Минимальные размеры сетки
- Минимальное количество циклов
- Быстрое выполнение (минуты)

**Пример:**
```python
adapter = ArchcodeAdapter(mode="fast")
```

---

### Production Mode

**Использование:** Полная валидация, публикация, ночные джобы

**Параметры:**
- Полные размеры сетки (50×50, 100 циклов)
- Долгое выполнение (часы)

**Пример:**
```python
adapter = ArchcodeAdapter(mode="production")
```

---

## ✅ Валидация результатов

Валидатор проверяет:

1. **Корректность данных:** наличие всех необходимых полей
2. **Теоретические предсказания:** соответствие ожидаемым диапазонам
3. **Биологические ограничения:** реалистичность значений
4. **Качество результатов:** достаточность данных для выводов

**Пример использования:**
```python
from terag_plugins.genome_architecture.validator import validate_archcode_result

validation = validate_archcode_result(result)

if validation["valid"]:
    print("✅ Results are valid")
    print(f"Derived metrics: {validation['derived_metrics']}")
else:
    print("❌ Issues found:")
    for issue in validation["issues"]:
        print(f"  - {issue}")
```

---

## 🧪 Тестирование

### Запуск интеграционных тестов

```bash
pytest tests/integration/test_terag_archcode_integration.py -v
```

### Тесты покрывают:

1. ✅ RS-09 mission (fast mode)
2. ✅ RS-10 mission (fast mode)
3. ✅ RS-11 mission (fast mode)
4. ✅ Real Hi-C benchmark
5. ✅ Error handling
6. ✅ Mode injection

---

## 📝 Примеры использования

### Пример 1: Запуск RS-11 через адаптер

```python
from src.integration.archcode_adapter import ArchcodeAdapter

adapter = ArchcodeAdapter(mode="fast")

mission = {
    "id": "RS11-TEST",
    "mission_type": "rs11_multichannel_memory",
    "parameters": {
        "bookmarking_range": (0.0, 1.0, 7),
        "epigenetic_range": (0.0, 1.0, 5),
        "num_cycles": 20,
    },
}

result = adapter.run_mission(mission)
print(f"Status: {result['status']}")
print(f"Time: {result['execution_time_sec']}s")
```

### Пример 2: Валидация и reasoning

```python
from terag_plugins.genome_architecture.validator import validate_archcode_result

# После получения результата от адаптера
validation = validate_archcode_result(result)

if validation["valid"]:
    metrics = validation["derived_metrics"]
    
    # Использовать метрики для reasoning
    if "bookmark_threshold" in metrics:
        threshold = metrics["bookmark_threshold"]
        print(f"Critical bookmarking threshold: {threshold:.3f}")
        
        if 0.3 <= threshold <= 0.4:
            print("✅ Threshold in expected range (0.3-0.4)")
        else:
            print(f"⚠️ Threshold outside expected range")
```

---

## 🔍 Отладка

### Проверка статуса миссии

```python
result = adapter.run_mission(mission_config)

if result["status"] == "error":
    print(f"Error: {result['error']}")
    print(f"Mission type: {result['mission_type']}")
    print(f"Execution time: {result['execution_time_sec']}s")
```

### Логирование

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("archcode_adapter")

# Адаптер будет логировать детали выполнения
```

---

## 📚 Дополнительная документация

- **API Reference:** `src/archcode_core/api.py`
- **Adapter Reference:** `src/integration/archcode_adapter.py`
- **Validator Reference:** `terag_plugins/genome_architecture/validator.py`
- **Mission Examples:** `terag_missions/*.yaml`

---

## 🚧 Ограничения

1. **Fast mode:** Результаты приблизительные, для разработки
2. **Production mode:** Требует времени (часы для полной валидации)
3. **Данные:** Real Hi-C benchmark требует наличия .cool файлов

---

## 🔄 Интеграция с TERAG

TERAG может вызывать адаптер через:

```python
# В TERAG коде:
from src.integration.archcode_adapter import ArchcodeAdapter

adapter = ArchcodeAdapter(mode="fast")
result = adapter.run_mission(mission_config)

# Валидация
from terag_plugins.genome_architecture.validator import validate_archcode_result
validation = validate_archcode_result(result)

# Использование в reasoning
if validation["valid"]:
    metrics = validation["derived_metrics"]
    # Передать метрики в T.R.A.C. reasoning engine
```

---

*Интеграция готова к использованию. Для вопросов см. исходный код или создайте issue.*

