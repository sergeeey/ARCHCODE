# 🚀 RS-11 Quick Start Guide

## Шаг 1: Загрузка данных

**Вариант A: Автоматическая загрузка (если URL доступны)**

**Windows (PowerShell):**
```powershell
# Попытка автоматической загрузки
powershell -ExecutionPolicy Bypass -File download_datasets_updated.ps1

# После завершения загрузки конвертировать WAPL файл
powershell -ExecutionPolicy Bypass -File convert_hic_to_cool.ps1
```

**Linux/Mac/Git Bash:**
```bash
# Попытка автоматической загрузки
bash download_datasets.sh

# После завершения загрузки конвертировать WAPL файл
bash convert_hic_to_cool.sh
```

**Вариант B: Ручная загрузка (рекомендуется)**

Если автоматическая загрузка не работает (404 ошибки), используйте ручную загрузку:

1. **См. инструкции**: `DATA_DOWNLOAD_MANUAL.md`
2. **Основные источники**:
   - 4DNucleome Portal: https://data.4dnucleome.org/
   - GEO: https://www.ncbi.nlm.nih.gov/geo/
   - WT (GM12878): GSE63525
   - CdLS (HCT116): GSE104333
   - WAPL-KO (HAP1): GSE95014

3. После ручной загрузки проверьте файлы:
```powershell
Get-Item data/real/* | Format-Table Name, @{L='Size(GB)';E={[math]::Round($_.Length/1GB,2)}}
```

**Время загрузки:** ~1-2 часа (можно прервать и возобновить)

## Шаг 2: Запуск бенчмарка

### Вариант A: Автоматический режим (все условия)

Скрипт автоматически обработает все три условия из конфигурации:

```bash
python experiments/run_RS11_multi_condition.py
```

Это создаст:
- `figures/RS11/Figure_4_WT_GM12878.png`
- `figures/RS11/Figure_4_CdLS_HCT116_Auxin.png`
- `figures/RS11/Figure_4_WAPL_KO_HAP1.png`

### Вариант B: Одно условие

```bash
python experiments/run_RS11_multi_condition.py --condition WT_GM12878
```

### Вариант C: Legacy режим (один файл)

```bash
python experiments/run_RS11_multi_condition.py \
    --real-cooler "data/real/WT_GM12878.mcool::/resolutions/10000" \
    --region "chr8:127000000-130000000"
```

## 📊 Что делает скрипт

1. **Генерирует симуляции** для каждого условия с правильными параметрами:
   - **WT**: processivity=1.0 (эталон)
   - **CdLS**: processivity=0.5 (низкая processivity, нестабильная фаза)
   - **WAPL-KO**: processivity=2.0 (высокая processivity, гипер-стабильная фаза)

2. **Сравнивает с реальными данными** по трем метрикам:
   - **P(s) scaling** — зависимость контактов от расстояния
   - **Insulation Score** — распределение изоляции границ
   - **Contact Maps** — визуальное сравнение матриц

3. **Сохраняет результаты** в `data/output/RS11/RS11_multi_condition_results.json`

## ⚙️ Конфигурация

Конфигурация находится в начале `experiments/run_RS11_multi_condition.py`:

```python
TEST_REGION = "chr8:127000000-130000000"  # 3 Mb регион (MYC locus)

CONDITIONS = [
    {
        "name": "WT_GM12878",
        "real_path": "data/real/WT_GM12878.mcool::/resolutions/10000",
        "region": TEST_REGION,
        "sim_params": {
            "processivity": 1.0,
            "bookmarking": 0.8,
            "ctcf_occupancy": 0.9,
        },
    },
    # ... и т.д.
]
```

## 🔍 Проверка файлов

Перед запуском убедитесь, что файлы существуют:

```bash
# Windows PowerShell
Test-Path data/real/WT_GM12878.mcool
Test-Path data/real/CdLS_Like_HCT116.mcool
Test-Path data/real/WAPL_KO_HAP1_10kb.cool

# Linux/Mac/Git Bash
ls -lh data/real/*.mcool data/real/*.cool
```

## 📁 Структура результатов

```
figures/RS11/
├── Figure_4_WT_GM12878.png
├── Figure_4_CdLS_HCT116_Auxin.png
└── Figure_4_WAPL_KO_HAP1.png

data/output/RS11/
├── WT_GM12878_matrix.npy
├── CdLS_HCT116_Auxin_matrix.npy
├── WAPL_KO_HAP1_matrix.npy
└── RS11_multi_condition_results.json
```

## ⚠️ Troubleshooting

### Ошибка: File not found

Убедитесь, что:
1. Загрузка завершена (`download_datasets.sh`)
2. WAPL файл сконвертирован (`convert_hic_to_cool.sh`)
3. Пути в конфигурации правильные

### Ошибка: ImportError (cooler/cooltools)

```bash
pip install -r requirements_rs11.txt
```

### Ошибка: Memory error

Используйте меньший регион или разрешение:

```python
TEST_REGION = "chr8:128000000-129000000"  # 1 Mb вместо 3 Mb
```

## 🎯 Следующие шаги

После успешного запуска у вас будет полный набор Figure 4 для всех трех условий, готовый для публикации!

