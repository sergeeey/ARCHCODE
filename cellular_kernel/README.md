# Cellular Kernel - Mitosis Distributed Consensus Simulation

Симуляция митоза как распределенного консенсуса с LTL верификацией безопасности.

## Архитектура

Проект реализует модель **Spindle Checkpoint как Distributed Consensus**:

- **agents.py** - Кинетохоры (локальные FSM узлы)
- **bus.py** - Цитоплазма/MCC (Shared Analog Bus)
- **kernel.py** - APC/C (System Controller)
- **verifier.py** - LTL Runtime Verification Engine

## Установка

```bash
pip install pyyaml
```

## Запуск

```bash
cd cellular_kernel
python main.py
```

## Структура проекта

```
cellular_kernel/
├── config/
│   └── vizier_protocol.yaml    # Спецификация системы и LTL-правила
├── src/
│   ├── __init__.py
│   ├── agents.py               # Кинетохоры (Hardware Agents)
│   ├── bus.py                  # Цитоплазма/MCC (Shared Analog Bus)
│   ├── kernel.py               # APC/C (System Controller)
│   └── verifier.py             # LTL Runtime Verification Engine
├── main.py                     # Точка входа симуляции
└── README.md
```

## LTL Свойства

### Safety Critical
```
G ( !ALL_NODES_READY -> !ANAPHASE_TRIGGER )
```
Система не должна переходить в анафазу, если есть ошибки.

### Liveness
```
F ( ANAPHASE_TRIGGER )
```
Система должна в конечном итоге завершить деление.

## Параметры симуляции

Настраиваются в `config/vizier_protocol.yaml`:

- `total_chromosomes`: Количество хромосом (по умолчанию 46)
- `tension_threshold`: Порог натяжения для READY (0.8)
- `attach_probability`: Вероятность прикрепления за тик (0.15)
- `apc_activation_threshold`: Порог MCC для анафазы (5.0)











