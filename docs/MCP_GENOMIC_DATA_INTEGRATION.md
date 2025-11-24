# MCP Genomic Data Server - Интеграция с ARCHCODE

## Обзор

MCP Genomic Data Server предоставляет инструменты для доступа к геномным данным и интегрируется с ARCHCODE модулями.

## Архитектура

```
MCP Genomic Data Server
├── Tools (API endpoints)
│   ├── fetch_genomic_sequence
│   ├── fetch_ctcf_chipseq
│   ├── fetch_hic_data
│   ├── fetch_methylation_data
│   ├── search_gene
│   ├── fetch_te_annotations
│   ├── classify_te_family
│   ├── calculate_insulation_score
│   └── detect_tads_from_hic
│
└── Integration with ARCHCODE
    ├── archcode_core → sequences
    ├── te_grammar → TE annotations
    ├── epigenetic_compiler → methylation
    ├── boundary_stability → CTCF ChIP-seq
    └── genome_to_tension → Hi-C validation
```

## Использование в ARCHCODE

### Пример 1: Загрузка данных для RS-01

```python
from mcp_genomic_data.tools import fetch_ctcf_chipseq, fetch_genomic_sequence

# Получить CTCF ChIP-seq данные для калибровки NIPBL сайтов
ctcf_data = await fetch_ctcf_chipseq("chr1", 1000000, 2000000)

# Получить последовательность для анализа мотивов
sequence = await fetch_genomic_sequence("chr1", 1000000, 2000000)
```

### Пример 2: Загрузка данных для RS-02

```python
from mcp_genomic_data.tools import fetch_te_annotations

# Получить TE аннотации для построения словаря
te_data = await fetch_te_annotations("chr1", 1000000, 2000000, "RepeatMasker")
```

### Пример 3: Валидация результатов

```python
from mcp_genomic_data.tools import detect_tads_from_hic, calculate_insulation_score

# Детектировать TAD из экспериментальных Hi-C данных
experimental_tads = await detect_tads_from_hic("chr1", "data/hic/GM12878.cool")

# Сравнить с симулированными TAD
simulated_tads = pipeline.detect_tads()

# Валидация
compare_tads(simulated_tads, experimental_tads)
```

## Текущий статус

### Реализовано
- ✅ Структура MCP сервера
- ✅ Все инструменты (placeholder реализации)
- ✅ Интеграция с ARCHCODE pipeline
- ✅ Примеры использования

### Требует реализации
- ⚠️ Реальный доступ к UCSC/Ensembl API
- ⚠️ Реальный доступ к ENCODE API
- ⚠️ Реальный доступ к GEO API
- ⚠️ Кэширование данных
- ⚠️ Обработка ошибок API

## Следующие шаги

1. **Реализовать реальный доступ к API**
   - UCSC Genome Browser API
   - Ensembl REST API
   - ENCODE API
   - GEO API

2. **Добавить кэширование**
   - Локальное кэширование данных
   - TTL для кэша

3. **Расширить функциональность**
   - Batch requests
   - Streaming для больших данных
   - Параллельная загрузка

4. **Интеграция с Browser Extension**
   - Использовать browser extension для веб-скрапинга
   - Автоматизация скачивания данных







