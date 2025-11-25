# Руководство по использованию MCP Genomic Data Server

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r mcp_genomic_data/requirements.txt
```

### 2. Настройка MCP сервера в Cursor

```bash
python mcp_genomic_data/setup_mcp.py
```

Это создаст конфигурацию в `~/.cursor/mcp/genomic-data.json`.

### 3. Перезапуск Cursor

После настройки перезапустите Cursor, чтобы MCP сервер стал доступен.

## Использование в Cursor

После настройки MCP сервер доступен через Cursor AI:

### Пример запроса:

```
"Получи CTCF ChIP-seq данные для хромосомы 1, позиции 1000000-2000000"
```

Cursor автоматически вызовет:
```python
fetch_ctcf_chipseq("chr1", 1000000, 2000000)
```

### Примеры запросов:

1. **"Найди ген MYC и получи его последовательность"**
   - Вызовет `search_gene("MYC")` → `fetch_genomic_sequence(...)`

2. **"Получи данные метилирования для хромосомы 8"**
   - Вызовет `fetch_methylation_data("chr8", start, end)`

3. **"Найди все транспозоны в области HOXA кластера"**
   - Вызовет `search_gene("HOXA")` → `fetch_te_annotations(...)`

4. **"Рассчитай insulation score из Hi-C файла"**
   - Вызовет `calculate_insulation_score(...)`

## Интеграция с ARCHCODE

MCP сервер автоматически интегрируется с ARCHCODE модулями:

### В коде Python:

```python
from mcp_genomic_data.tools import fetch_ctcf_chipseq
from src.archcode_core.pipeline import ARCHCODEPipeline

# Получить CTCF данные через MCP
ctcf_data = await fetch_ctcf_chipseq("chr1", 1000000, 2000000)

# Использовать в ARCHCODE pipeline
pipeline = ARCHCODEPipeline(...)
for peak in ctcf_data["peaks"]:
    pipeline.add_boundary(
        position=peak["start"],
        strength=peak["strength"],
    )
```

## Доступные инструменты

### Геномные данные
- `fetch_genomic_sequence` - Последовательности
- `search_gene` - Поиск генов

### Эпигенетика
- `fetch_ctcf_chipseq` - CTCF ChIP-seq
- `fetch_methylation_data` - Метилирование CpG

### Структура хроматина
- `fetch_hic_data` - Hi-C контакты
- `calculate_insulation_score` - Insulation score
- `detect_tads_from_hic` - TAD boundaries

### Транспозоны
- `fetch_te_annotations` - TE аннотации
- `classify_te_family` - Классификация TE

## Конфигурация

Настройки в `mcp_genomic_data/config.yaml`:

- Источники данных (UCSC, Ensembl, ENCODE)
- Локальные пути к данным
- Кэширование

## Расширение функциональности

Для добавления реального доступа к API:

1. Реализовать функции в `tools.py`
2. Добавить API ключи в `config.yaml`
3. Обновить документацию

## Troubleshooting

### MCP сервер не запускается
- Проверьте установку: `pip install mcp`
- Проверьте конфигурацию: `~/.cursor/mcp/genomic-data.json`

### Ошибки импорта
- Установите зависимости: `pip install -r mcp_genomic_data/requirements.txt`

### Placeholder данные
- Текущая версия использует mock данные
- Для реальных данных нужна реализация API доступа










