# Предложение: MCP Серверы для ARCHCODE

## Проблема

Текущие MCP серверы в Cursor ориентированы на геологию (GeoScan), но ARCHCODE работает с геномной архитектурой. Нужны специализированные MCP серверы для геномных данных.

## Предлагаемые MCP Серверы

### 1. Genomic Data Access MCP Server

**Назначение:** Доступ к публичным геномным базам данных.

**Функции:**
- `fetch_genomic_sequence(chr, start, end)` - Получение последовательности из UCSC/Ensembl
- `fetch_ctcf_chipseq(chr, start, end)` - CTCF ChIP-seq данные из ENCODE
- `fetch_hic_data(chr, resolution)` - Hi-C данные из публичных репозиториев
- `fetch_methylation_data(chr, start, end)` - Данные метилирования из GEO
- `search_gene(gene_name)` - Поиск генов и их координат

**Интеграция:**
- Заменяет placeholder данные в RS-01, RS-02
- Позволяет использовать реальные данные для калибровки

### 2. Hi-C Processing MCP Server

**Назначение:** Обработка Hi-C данных для сравнения с симуляцией.

**Функции:**
- `load_hic_file(file_path)` - Загрузка .cool/.mcool файлов
- `calculate_insulation_score(chr, window_size)` - Расчет insulation score
- `detect_tads(chr)` - Детекция TAD boundaries из Hi-C
- `compare_with_simulation(simulated_tads, experimental_tads)` - Сравнение результатов

**Интеграция:**
- Валидация результатов archcode_core
- Калибровка параметров модели

### 3. Epigenetic Data MCP Server

**Назначение:** Доступ к эпигенетическим данным.

**Функции:**
- `fetch_methylation_profile(chr, start, end)` - Профиль метилирования
- `fetch_histone_marks(chr, mark_type)` - Гистоновые модификации
- `fetch_atac_seq(chr, start, end)` - ATAC-seq данные (доступность хроматина)

**Интеграция:**
- Заполнение epigenetic_compiler реальными данными
- Калибровка порогов метилирования (Risk L3)

### 4. TE Annotation MCP Server

**Назначение:** Доступ к аннотациям транспозонов.

**Функции:**
- `fetch_te_annotations(chr, start, end)` - TE аннотации из RepeatMasker/Dfam
- `classify_te_family(sequence)` - Классификация TE семейства
- `find_wapl_motifs(chr, start, end)` - Поиск WAPL-recruiting мотивов

**Интеграция:**
- Заполнение te_grammar реальными данными (Risk S1)
- Реализация RS-02

## Реализация

### Вариант 1: Использовать Browser Extension MCP

Можно использовать существующий `cursor-browser-extension` для:
- Автоматизации скачивания данных с веб-интерфейсов
- Скрапинга публичных баз данных

**Плюсы:** Быстро, не требует создания новых серверов
**Минусы:** Медленно, зависит от веб-интерфейсов

### Вариант 2: Создать Python MCP Серверы

Создать специализированные MCP серверы на Python:
- Использовать существующие библиотеки (biopython, pyBigWig, cooler)
- Интегрировать с ARCHCODE модулями

**Плюсы:** Быстро, надежно, интегрируется с ARCHCODE
**Минусы:** Требует разработки

### Вариант 3: Адаптировать GeoScan MCP

Использовать архитектуру GeoScan MCP как шаблон:
- Заменить геологические функции на геномные
- Использовать ту же структуру (tools, resources)

**Плюсы:** Использует проверенную архитектуру
**Минусы:** Требует значительной переработки

## Рекомендация

**Вариант 2** - создать специализированные Python MCP серверы:
1. Использовать существующие библиотеки ARCHCODE
2. Интегрировать с текущими модулями
3. Следовать архитектуре GeoScan MCP как примеру

## Следующие шаги

1. Создать `mcp_genomic-data` сервер
2. Интегрировать с ARCHCODE модулями
3. Заменить placeholder данные на реальные
4. Калибровать модели на экспериментальных данных







