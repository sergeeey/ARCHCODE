# 🚀 ARCHCODE Reproducible Science Package

**Одна команда → вся наука**

---

## Быстрый старт

```bash
# Fast mode (15-30 минут)
python tools/run_pipeline.py run-pipeline --mode fast

# Full mode (несколько часов, для публикации)
python tools/run_pipeline.py run-pipeline --mode full
```

---

## Что делает pipeline

1. ✅ **Unit тесты** - проверка физики и памяти
2. ✅ **Regression тесты** - стабильность RS-09/10/11
3. ✅ **RS-09** - Processivity Phase Diagram
4. ✅ **RS-10** - Bookmarking Threshold
5. ✅ **RS-11** - Multichannel Memory
6. ✅ **Real Hi-C Analysis** - анализ реальных данных
7. ✅ **ARCHCODE ↔ Real Comparison** - сравнение симуляций с реальностью
8. ✅ **Summary Report** - автоматический отчёт

---

## Результаты

После выполнения команды:

- **Результаты:** `data/output/pipeline_runs/`
- **Отчёт:** `docs/reports/PIPELINE_SUMMARY_<timestamp>.md`
- **Фигуры:** `figures/pipeline/`

---

## Конфигурация

Параметры настраиваются в:
- `configs/pipeline_fast.yaml` - быстрый режим
- `configs/pipeline_full.yaml` - полный режим

---

## Документация

Полное руководство: `docs/REPRODUCIBILITY_GUIDE.md`

---

*ARCHCODE v1.0 - Reproducible Science Package*

