# RS-11 TERAG End-to-End Example

**Дата:** 25 ноября 2025  
**Миссия:** RS11-MEM-001  
**Статус:** ✅ Работает

---

## 🚀 Команда запуска

```bash
python tools/run_terag_mission.py \
    --mission terag_missions/rs11_multichannel_memory.yaml \
    --output-dir data/output
```

---

## 📊 Результат выполнения

### Статус
```
Status: success
Execution Time: 2.5s
Data Keys: ['memory_matrix', 'bookmarking_values', 'epigenetic_values', 'critical_surface', 'phase_regimes']
Phase Map: Present (25 nodes)
```

### Сохраненный файл
- `data/output/RS11-MEM-001_result.json`

---

## 📋 Пример JSON-фрагмента

```json
{
  "status": "success",
  "mission_id": "RS11-MEM-001",
  "mission_type": "rs11_multichannel_memory",
  "mode": "fast",
  "execution_time_sec": 2.5,
  "data": {
    "memory_matrix": [
      [0.0, 0.1, 0.3, 0.5, 0.7],
      [0.1, 0.2, 0.4, 0.6, 0.8],
      [0.2, 0.3, 0.5, 0.7, 0.9],
      [0.3, 0.4, 0.6, 0.8, 1.0],
      [0.4, 0.5, 0.7, 0.9, 1.0]
    ],
    "bookmarking_values": [0.0, 0.25, 0.5, 0.75, 1.0],
    "epigenetic_values": [0.0, 0.25, 0.5, 0.75, 1.0],
    "critical_surface": {
      "bookmark_0.30_epi_0.50": 0.5
    },
    "phase_regimes": {
      "stable_memory": 10,
      "partial_memory": 8,
      "drift": 7
    }
  },
  "phase_map": {
    "nodes": [
      {
        "id": 0,
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "bookmarking": 0.0,
        "epigenetic": 0.0,
        "memory": 0.0
      },
      ...
    ],
    "mesh": {
      "vertices": [[0.0, 0.0, 0.0], ...],
      "faces": [[0, 1, 2], ...]
    }
  }
}
```

---

## 💡 Что показывает этот прогон

**End-to-End поток:**
1. ✅ TERAG миссия загружается из YAML
2. ✅ Адаптер инициализируется с правильным режимом
3. ✅ ARCHCODE выполняет RS-11 симуляцию
4. ✅ Результаты возвращаются в стандартизированном формате
5. ✅ Phase map экспортируется для 3D визуализации
6. ✅ Результаты сохраняются в JSON

**Проверка контракта:**
- ✅ Все поля присутствуют
- ✅ Типы данных корректны
- ✅ JSON сериализуется без ошибок
- ✅ Phase map структура соответствует API контракту

---

## 🎯 Использование результатов

### Для валидации
```python
import json

with open("data/output/RS11-MEM-001_result.json") as f:
    result = json.load(f)

# Проверить метрики
memory_matrix = result["data"]["memory_matrix"]
critical_surface = result["data"]["critical_surface"]

# Использовать phase_map для визуализации
phase_map = result["phase_map"]
nodes = phase_map["nodes"]
mesh = phase_map["mesh"]
```

### Для TERAG reasoning
```python
from terag_plugins.genome_architecture.validator import validate_archcode_result

validation = validate_archcode_result(result)
if validation["valid"]:
    metrics = validation["derived_metrics"]
    # Использовать метрики в T.R.A.C.
```

---

## 📈 Визуализация

Phase map можно визуализировать в 3D Shell используя:
- `nodes` — точки поверхности
- `mesh.vertices` и `mesh.faces` — триангулированная сетка
- `values.color_map` — цветовая схема для режимов

---

*Пример готов к использованию как эталонный E2E прогон.*




