# RS-11 Benchmarking Module — Setup Guide

## Установка зависимостей

RS-11 требует дополнительные библиотеки для работы с Hi-C данными:

```bash
pip install cooler cooltools matplotlib numpy pandas scipy hic2cool
```

Или используйте файл зависимостей:

```bash
pip install -r requirements_rs11.txt
```

### Проверка установки

```bash
python -c "import cooler; import cooltools; print('OK')"
```

---

## Источники данных

### Автоматическая загрузка эталонных датасетов

Для валидации теории используются **эталонные датасеты (Gold Standard)** с глубоким секвенированием:

1. **Wild Type (WT) — GM12878:**
   - **Rao et al., 2014** — эталон нормы
   - Формат: `.mcool` (все разрешения)
   - Accession: `4DNFI1UEG1O1` (4DN Portal)

2. **Cohesin Loss / CdLS-like — HCT116-RAD21-AID:**
   - **Rao et al., 2017** — аналог NIPBL↓ / CdLS
   - При добавлении ауксина когезин исчезает, архитектура коллапсирует (Processivity → 0)
   - Формат: `.mcool`
   - Accession: `4DNFI2TK7L2F` (4DN Portal)

3. **WAPL-KO — HAP1:**
   - **Haarhuis et al., 2017** — режим гипер-стабильности
   - Формат: `.hic` (требует конвертации в `.cool`)
   - Accession: GEO `GSE95014`

### Загрузка датасетов

Используйте скрипт `download_datasets.sh` для автоматической загрузки всех трех датасетов:

```bash
# Запуск загрузки (может занять 1-2 часа в зависимости от скорости интернета)
bash download_datasets.sh

# После загрузки конвертируйте WAPL файл из .hic в .cool
bash convert_hic_to_cool.sh
```

**Примечание:** Общий объем датасетов составляет ~20-30 ГБ. Скрипт использует докачку (`-c`), поэтому можно безопасно прервать и возобновить загрузку.

### Ручная загрузка

Если автоматическая загрузка не работает, можно скачать датасеты вручную:

1. **WT (GM12878):** [4DN Portal](https://data.4dnucleome.org/files-processed/4DNFI1UEG1O1/)
2. **CdLS-like (HCT116):** [4DN Portal](https://data.4dnucleome.org/files-processed/4DNFI2TK7L2F/)
3. **WAPL-KO (HAP1):** [GEO GSE95014](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE95014)

---

## Использование

### Single Condition Benchmark

```bash
python experiments/benchmark_vs_real.py \
    --real-cooler "path/to/real.cool" \
    --sim-matrix "data/output/simulation.npy" \
    --output "Figure_4.png" \
    --condition "WT"
```

### Multi-Condition Benchmark

После загрузки датасетов запустите multi-condition бенчмарк:

```bash
# Для WT (GM12878)
python experiments/run_RS11_multi_condition.py \
    --real-cooler "data/real/WT_GM12878.mcool::/resolutions/10000" \
    --region "chr1:1000000-2000000"

# Для CdLS-like (HCT116)
python experiments/run_RS11_multi_condition.py \
    --real-cooler "data/real/CdLS_Like_HCT116.mcool::/resolutions/10000" \
    --region "chr1:1000000-2000000"

# Для WAPL-KO (HAP1) - после конвертации
python experiments/run_RS11_multi_condition.py \
    --real-cooler "data/real/WAPL_KO_HAP1_10kb.cool" \
    --region "chr1:1000000-2000000"
```

---

## Примечания

- Файлы `.mcool` могут быть очень большими (гигабайты)
- Используйте `region` параметр для работы с подмножеством данных
- Для стриминга данных используйте URI формат: `file.mcool::/resolutions/10000`


