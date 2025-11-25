# Анализ MCP Серверов в Cursor

## Обзор

В Cursor настроено несколько MCP (Model Context Protocol) серверов для расширения функциональности. Ниже анализ каждого сервера и его возможностей.

---

## 1. GeoScan Core MCP Server

**Сервер:** `mcp_geoscan-core`

### Назначение
Геологический анализ и прогнозирование перспективных зон для поиска полезных ископаемых (золото, медь).

### Доступные функции

#### Спутниковый ETL
- `run_satellite_etl_tool` - Запуск спутникового ETL для региона
  - Параметры: region_id, start_date, end_date, sensors (sentinel2, landsat, dem)
  - Возвращает: Результат выполнения ETL в JSON
  
- `get_satellite_etl_manifest_tool` - Чтение etl_manifest.json для региона
- `list_satellite_regions_tool` - Список доступных регионов

#### Анализ перспективных зон
- `list_prospect_zones_tool` - Список перспективных зон из графа (Neo4j)
  - Фильтры: commodity (Au, Cu), region, min_probability
  - Возвращает: Список зон с вероятностями
  
- `get_zone_context_tool` - Детальный контекст по зоне
  - Возвращает: Узлы, связи, reasoning path из графа знаний

#### Статусные отчёты
- `list_status_reports_tool` - Список статусных отчётов
  - Фильтры: region, report_type (status, summary)

#### Датакуб и предиктор
- `build_datacube_tool` - Построение датакуба признаков
  - Объединяет спутниковые слои в мультиканальный датакуб (H, W, C)
  
- `run_hybrid_predictor_tool` - Запуск предиктора перспективности
  - Режимы: train (обучение), predict (прогноз)
  - Возвращает: Топ-N точек для извлечения

#### Информация о регионах
- `get_region_info_tool` - Информация о регионе
  - Возвращает: bbox, CRS, описание, назначение

#### CoVe анализ
- `run_cove_analysis` - Chain-of-Verification цикл
  - Проверка ответов через Graph RAG и физические законы (PINN)
  - Ключевой инструмент для C-TRL 6: самокритика и аудируемость

### Регионы
- `bestobe_gold` - Регион для золота
- `chu_sarysu_cu` - Регион для меди

### Использование для ARCHCODE
**НЕ ПРИМЕНИМО** - это геологический сервер, не связан с геномной архитектурой.

---

## 2. Google Maps MCP Server

**Сервер:** `mcp_google-maps`

### Назначение
Работа с Google Maps API для геолокации и маршрутизации.

### Доступные функции
- `search_places` - Поиск мест через Google Places API
  - Параметры: query (например, "Балхаш, Казахстан")
  - Возвращает: название, адрес, координаты
  
- `get_directions` - Построение маршрута между точками
  - Параметры: origin, destination, mode (driving, walking, bicycling, transit)
  - Возвращает: дистанция, время в пути, шаги маршрута

### Использование для ARCHCODE
**НЕ ПРИМЕНИМО** - географический сервис, не связан с геномной архитектурой.

---

## 3. Sentinel Hub MCP Server

**Сервер:** `mcp_sentinel-hub`

### Назначение
Анализ геологии через Sentinel Hub API (спутниковые снимки).

### Доступные функции
- `analyze_geology` - Анализ геологии через Sentinel Hub API
  - Параметры: lat, lng, radius_km
  - Ищет: Sentinel-2 L2A снимки (безоблачные, <10% облаков)
  - Скачивает: каналы B04, B08, B11, B12
  - Рассчитывает: индексы для поиска минерализации
  - Возвращает: дата снимка, NDVI, аномалии железа

### Использование для ARCHCODE
**НЕ ПРИМЕНИМО** - геологический анализ спутниковых данных.

---

## 4. Reporting MCP Server

**Сервер:** `mcp_reporting`

### Назначение
Сохранение геологических отчётов.

### Доступные функции
- `save_report` - Сохраняет геологический отчёт
  - Форматы: Markdown и JSON
  - Параметры: location_name, lat, lng, iron_oxide, ndvi, anomalies_count, summary
  - Возвращает: пути к сохраненным файлам

### Использование для ARCHCODE
**ЧАСТИЧНО ПРИМЕНИМО** - можно адаптировать для сохранения результатов анализа границ TAD.

---

## 5. NX MCP Server

**Сервер:** `mcp_extension-nx-mcp`

### Назначение
Работа с Nx (монорепозиторий инструмент для JavaScript/TypeScript).

### Доступные функции
- `nx_docs` - Поиск документации Nx по запросу
- `nx_available_plugins` - Список доступных Nx плагинов

### Использование для ARCHCODE
**НЕ ПРИМЕНИМО** - инструмент для JavaScript/TypeScript проектов, ARCHCODE - Python проект.

---

## 6. Cursor Browser Extension MCP Server

**Сервер:** `mcp_cursor-browser-extension`

### Назначение
Автоматизация браузера для веб-скрапинга и тестирования.

### Доступные функции

#### Навигация
- `browser_navigate` - Переход по URL
- `browser_navigate_back` - Назад
- `browser_resize` - Изменение размера окна

#### Информация
- `browser_snapshot` - Снимок доступности страницы (лучше чем screenshot)
- `browser_console_messages` - Сообщения консоли
- `browser_network_requests` - Сетевые запросы
- `browser_tabs` - Управление вкладками

#### Взаимодействие
- `browser_click` - Клик по элементу
- `browser_hover` - Наведение
- `browser_type` - Ввод текста
- `browser_select_option` - Выбор опции
- `browser_drag` - Drag and drop
- `browser_fill_form` - Заполнение формы

#### Выполнение
- `browser_evaluate` - Выполнение JavaScript
- `browser_handle_dialog` - Обработка диалогов

#### Скриншоты
- `browser_take_screenshot` - Скриншот страницы/элемента

### Использование для ARCHCODE
**ПОТЕНЦИАЛЬНО ПРИМЕНИМО** - можно использовать для:
- Скачивания геномных данных с публичных баз (UCSC, Ensembl)
- Автоматизации работы с браузерными инструментами анализа
- Скрапинга данных из публичных репозиториев

---

## Резюме

### Применимые для ARCHCODE
1. **Cursor Browser Extension** - для автоматизации скачивания данных
2. **Reporting** - для сохранения результатов (с адаптацией)

### НЕ применимые
1. **GeoScan Core** - геологический анализ
2. **Google Maps** - географические сервисы
3. **Sentinel Hub** - спутниковые данные для геологии
4. **NX** - JavaScript/TypeScript инструмент

### Рекомендации

Для ARCHCODE было бы полезно иметь MCP серверы для:
- **Genomic Data Access** - доступ к публичным базам (UCSC, Ensembl, NCBI)
- **Hi-C Data Processing** - работа с Hi-C файлами (.cool, .mcool)
- **ChIP-seq Data** - доступ к ChIP-seq данным (ENCODE, GEO)
- **Epigenetic Data** - доступ к данным метилирования (GEO, ENCODE)

Эти серверы можно создать как расширение существующей архитектуры ARCHCODE.










