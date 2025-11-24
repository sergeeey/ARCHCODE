# ARCHCODE ↔ TERAG API Contract

**Версия:** 1.0  
**Дата:** 25 ноября 2025  
**Статус:** Стабильный контракт

---

## 🎯 Цель

Определить стабильный формат данных между ARCHCODE и TERAG для всех типов миссий.

---

## 📋 Общая структура ответа адаптера

Все ответы от `ArchcodeAdapter.run_mission()` имеют общую структуру:

```json
{
  "status": "success" | "error",
  "mission_id": "string",
  "mission_type": "string",
  "mode": "fast" | "production",
  "execution_time_sec": float,
  "data": { ... },
  "phase_map": { ... }  // Опционально, для RS09/10/11
}
```

---

## RS-09: Processivity Phase Diagram

### Mission Type
`rs09_processivity_phase`

### Data Contract

```json
{
  "phase_diagram": {
    "0.0": {
      "phase": "collapse" | "transition" | "stable",
      "stability": 0.0-1.0
    },
    "0.5": { ... },
    ...
  },
  "critical_points": {
    "collapse_threshold": float | null,
    "stable_threshold": float | null
  },
  "stability_metrics": {
    "mean": float,
    "std": float,
    "min": float,
    "max": float
  },
  "stable_fraction": float,
  "processivity_range": {
    "min": float,
    "max": float,
    "steps": int
  }
}
```

### Phase Map Export (для 3D)

```json
{
  "nodes": [
    {
      "id": int,
      "x": float,  // processivity
      "y": 0.0,
      "z": float,  // stability
      "processivity": float,
      "stability": float,
      "phase": "collapse" | "transition" | "stable"
    },
    ...
  ],
  "edges": [
    {
      "source": int,
      "target": int,
      "weight": float
    },
    ...
  ],
  "values": {
    "processivity": [float, ...],
    "stability": [float, ...],
    "phase": ["collapse" | "transition" | "stable", ...],
    "color_map": {
      "collapse": [1.0, 0.0, 0.0],
      "transition": [1.0, 1.0, 0.0],
      "stable": [0.0, 1.0, 0.0]
    }
  },
  "mesh": {
    "vertices": [[float, float, float], ...],
    "faces": [[int, int, int], ...]
  },
  "metadata": {
    "critical_points": { ... },
    "phase_regions": {
      "collapse": [float, ...],
      "transition": [float, ...],
      "stable": [float, ...]
    },
    "stability_metrics": { ... },
    "num_points": int
  }
}
```

---

## RS-10: Bookmarking Threshold

### Mission Type
`rs10_bookmarking_threshold`

### Data Contract

```json
{
  "bookmarking_grid": {
    "0.0": {
      "final_jaccard": float,
      "mean_drift": float,
      "entropy": float
    },
    "0.1": { ... },
    ...
  },
  "drift_curves": {
    "0.0": [float, ...],  // drift per cycle
    "0.1": [float, ...],
    ...
  },
  "entropy": {
    "0.0": float,
    "0.1": float,
    ...
  },
  "estimated_threshold": float | null,
  "num_cycles": int
}
```

### Threshold Curve Export (для 3D)

```json
{
  "nodes": [
    {
      "id": int,
      "x": float,  // bookmarking
      "y": float,  // cycle
      "z": float,  // jaccard - drift
      "bookmarking": float,
      "cycle": int,
      "jaccard": float,
      "drift": float
    },
    ...
  ],
  "edges": [ ... ],
  "values": {
    "bookmarking": [float, ...],
    "jaccard": [float, ...],
    "drift": [float, ...],
    "entropy": [float, ...]
  },
  "mesh": {
    "vertices": [[float, float, float], ...],
    "faces": [[int, int, int], ...]
  },
  "metadata": {
    "estimated_threshold": float | null,
    "phase_regions": {
      "memory_loss": [float, ...],
      "memory_retention": [float, ...]
    },
    "num_cycles": int
  }
}
```

---

## RS-11: Multichannel Memory Surface

### Mission Type
`rs11_multichannel_memory`

### Data Contract

```json
{
  "memory_matrix": [
    [float, float, ...],  // Row per epigenetic value
    ...
  ],
  "bookmarking_values": [float, ...],
  "epigenetic_values": [float, ...],
  "critical_surface": {
    "bookmark_0.30_epi_0.50": float,
    ...
  },
  "phase_regimes": {
    "stable_memory": int,
    "partial_memory": int,
    "drift": int
  },
  "critical_line": [
    [float, float],  // [epigenetic, bookmarking]
    ...
  ],
  "processivity": float,
  "num_cycles": int
}
```

### Memory Surface Export (для 3D)

```json
{
  "nodes": [
    {
      "id": int,
      "x": float,  // bookmarking
      "y": float,  // epigenetic
      "z": float,  // memory
      "bookmarking": float,
      "epigenetic": float,
      "memory": float
    },
    ...
  ],
  "edges": [ ... ],
  "values": {
    "memory_matrix": [[float, ...], ...],
    "bookmarking": [float, ...],
    "epigenetic": [float, ...],
    "color_map": {
      "drift": [1.0, 0.0, 0.0],
      "partial": [1.0, 1.0, 0.0],
      "stable": [0.0, 1.0, 0.0]
    }
  },
  "mesh": {
    "vertices": [[float, float, float], ...],
    "faces": [[int, int, int], ...]
  },
  "metadata": {
    "critical_surface": { ... },
    "critical_line": [[float, float], ...],
    "phase_regimes": { ... },
    "processivity": float,
    "num_cycles": int,
    "grid_size": {
      "bookmarking": int,
      "epigenetic": int
    }
  }
}
```

---

## RS-12: Sci-Hi-C Validation

### Mission Type
`rs12_scihic_validation`

### Data Contract

```json
{
  "insulation_correlation": float,
  "ps_correlation": float,
  "compartment_agreement": float,
  "xci_prediction_accuracy": float,
  "conditions": {
    "d0": {
      "insulation_corr": float,
      "ps_corr": float,
      "compartment_agreement": float
    },
    "d7": { ... },
    "d20": { ... },
    "NPC": { ... }
  },
  "cell_types": {
    "autosomes": { ... },
    "X_chromosome": { ... }
  },
  "metrics": {
    "insulation": { ... },
    "tads": { ... },
    "apa": { ... },
    "ps": { ... },
    "compartments": { ... },
    "pearson": { ... }
  }
}
```

---

## RS-13: Multi-Condition Benchmark

### Mission Type
`rs13_multi_condition`

### Data Contract

```json
{
  "conditions": {
    "WT": {
      "processivity": float,
      "bookmarking": float,
      "insulation_correlation": float,
      "ps_correlation": float,
      "boundary_shift": float,
      "compartment_switch": "A" | "B" | null
    },
    "WAPL-KO": { ... },
    "CTCF-AID": { ... },
    "CdLS": { ... }
  },
  "comparison_metrics": {
    "boundary_shift_rmse": float,
    "ps_scaling_delta": float,
    "compartment_switch_accuracy": float,
    "processivity_correlation": float
  },
  "regions": [
    {
      "region": "chr8:127000000-130000000",
      "metrics": { ... }
    },
    ...
  ]
}
```

---

## 🔍 Типы данных

### Базовые типы

- `float` — число с плавающей точкой (JSON number)
- `int` — целое число (JSON number)
- `string` — строка (JSON string)
- `null` — отсутствие значения (JSON null)

### Специальные типы

- `phase`: `"collapse" | "transition" | "stable"`
- `compartment`: `"A" | "B"`
- `color`: `[float, float, float]` — RGB в диапазоне [0.0, 1.0]

---

## ✅ Валидация контракта

Все поля должны быть:
- Присутствовать (если не помечены как optional)
- Иметь правильный тип
- Не содержать `NaN` или `Infinity`
- Быть JSON-serializable

---

## 📝 Примеры использования

### Пример 1: RS-09 Response

```json
{
  "status": "success",
  "mission_id": "RS09-PROC-001",
  "mission_type": "rs09_processivity_phase",
  "mode": "fast",
  "execution_time_sec": 0.15,
  "data": {
    "phase_diagram": {
      "0.0": {"phase": "collapse", "stability": 0.1},
      "0.5": {"phase": "transition", "stability": 0.5},
      "1.0": {"phase": "stable", "stability": 0.9}
    },
    "critical_points": {
      "collapse_threshold": 0.5,
      "stable_threshold": 1.0
    },
    "stable_fraction": 0.6
  },
  "phase_map": {
    "nodes": [...],
    "edges": [...],
    "values": {...},
    "mesh": {...},
    "metadata": {...}
  }
}
```

### Пример 2: RS-11 Response

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
      ...
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
    "nodes": [...],
    "mesh": {...},
    "metadata": {...}
  }
}
```

---

## 🔄 Версионирование

При изменении контракта:
1. Обновить версию документа
2. Добавить changelog
3. Обновить адаптер для обратной совместимости
4. Обновить тесты

---

*Контракт зафиксирован и готов к использованию.*

