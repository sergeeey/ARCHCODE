# MCP Genomic Data Server

MCP сервер для доступа к геномным данным, интегрированный с ARCHCODE.

## Установка

```bash
pip install mcp biopython pyfaidx cooler cooltools
```

## Запуск

```bash
python -m mcp_genomic_data.server
```

## Доступные инструменты

### 1. fetch_genomic_sequence
Получение геномной последовательности.

**Параметры:**
- `chromosome`: Хромосома (например, "chr1")
- `start`: Начальная позиция (bp)
- `end`: Конечная позиция (bp)
- `assembly`: Сборка генома (по умолчанию "hg38")

**Использование:**
```python
result = await fetch_genomic_sequence("chr1", 1000000, 2000000)
```

### 2. fetch_ctcf_chipseq
Получение CTCF ChIP-seq данных из ENCODE.

**Параметры:**
- `chromosome`: Хромосома
- `start`: Начальная позиция
- `end`: Конечная позиция
- `cell_type`: Тип клетки (опционально)

### 3. fetch_hic_data
Получение Hi-C контактных данных.

**Параметры:**
- `chromosome`: Хромосома
- `resolution`: Разрешение в bp
- `file_path`: Путь к .cool файлу (опционально)

### 4. fetch_methylation_data
Получение данных метилирования CpG.

**Параметры:**
- `chromosome`: Хромосома
- `start`: Начальная позиция
- `end`: Конечная позиция
- `data_source`: Источник данных (GEO, ENCODE)

### 5. search_gene
Поиск гена и получение координат.

**Параметры:**
- `gene_name`: Название гена
- `assembly`: Сборка генома

### 6. fetch_te_annotations
Получение аннотаций транспозонов.

**Параметры:**
- `chromosome`: Хромосома
- `start`: Начальная позиция
- `end`: Конечная позиция
- `annotation_source`: Источник (RepeatMasker, Dfam)

### 7. classify_te_family
Классификация семейства TE по последовательности.

**Параметры:**
- `sequence`: DNA последовательность

### 8. calculate_insulation_score
Расчет insulation score из Hi-C данных.

**Параметры:**
- `chromosome`: Хромосома
- `file_path`: Путь к .cool файлу
- `window_size`: Размер окна в bp

### 9. detect_tads_from_hic
Детекция TAD границ из Hi-C данных.

**Параметры:**
- `chromosome`: Хромосома
- `file_path`: Путь к .cool файлу
- `resolution`: Разрешение в bp

## Интеграция с ARCHCODE

Сервер интегрируется с ARCHCODE модулями:

- **archcode_core**: Загрузка последовательностей для экструзии
- **te_grammar**: Получение TE аннотаций (RS-02)
- **epigenetic_compiler**: Данные метилирования (RS-04)
- **boundary_stability**: CTCF ChIP-seq для калибровки
- **genome_to_tension**: Hi-C данные для валидации

## Конфигурация

Настройки в `config.yaml`:
- Источники данных (UCSC, Ensembl, ENCODE)
- Локальные пути к данным
- Настройки кэширования

## Статус

Текущая версия использует placeholder данные. Реальная интеграция с API требует:
- API ключи для ENCODE/GEO
- Доступ к UCSC/Ensembl API
- Локальные файлы данных (.cool, FASTA)








