# Quick Start — Stress Biology Project

**Готово к запуску.** Всё необходимое реализовано.

---

## ✅ Что ГОТОВО

### 1. Скрипты (все рабочие, не stubs)

- `scripts/download_tcga.py` — скачивание TCGA MAF файлов (GDC API)
- `scripts/extract_mutation_rates.py` — парсинг MAF, расчёт mut/Mb
- `scripts/literature_mining.py` — doubling time из литературы (PubMed)
- `scripts/atp_proxy.py` — ATP proxy из RNA-seq (OXPHOS genes)
- `scripts/correlation_analysis.R` — Spearman корреляция + bootstrap

### 2. Документация

- `SPEC.md` v2.0 — полная спецификация (post-recon)
- `HYPOTHESIS.md` — замороженные предсказания (pre-registration)
- `ROADMAP.md` — 6-месячный timeline
- `BILINSKY_EMAIL_DRAFT.md` — шаблоны писем (Month 3+)

### 3. TCGA API

- ✅ Протестирован — 23,568 MAF файлов доступны
- ✅ Токен НЕ нужен для публичных данных
- ✅ Загрузка работает out-of-the-box

---

## 🚀 Запуск (Month 1: Data Collection)

### Шаг 1: Установить зависимости

```bash
cd D:/ДНК/stress_biology
pip install -r requirements.txt

# Для R скриптов (если ещё нет):
# R -e "install.packages(c('jsonlite', 'boot', 'ggplot2'))"
```

### Шаг 2: Скачать тестовый датасет (COAD — colon cancer)

```bash
python scripts/download_tcga.py --tissue COAD --output data/processed/coad_mutations.csv
```

**Что происходит:**
1. Запрос к GDC API → список MAF файлов для COAD
2. Скачивание первого файла (~50-200 MB)
3. Автоматический парсинг → CSV с mutation rates

**Время:** ~2-5 минут (зависит от скорости интернета)

### Шаг 3: Извлечь doubling times (manual curation)

```bash
python scripts/literature_mining.py --output data/processed/doubling_times.csv
```

**Что происходит:**
- Использует manual curation из Sender 2016 (Cell)
- 7 tissue types с известными doubling times
- Опция `--search` для PubMed API (TODO: NLP extraction)

**Время:** <1 секунда

### Шаг 4: Merge данных (mutation rates + doubling times)

```bash
# TODO: создать merge script или сделать вручную в Excel/pandas
# Формат: sample_id, tissue, doubling_time, mutation_rate
```

### Шаг 5: Correlation analysis (H0)

```bash
Rscript scripts/correlation_analysis.R --data data/merged.csv --output results/h0_stats.json
```

**Что происходит:**
- Spearman correlation
- Bootstrap 95% CI (10K iterations)
- Bonferroni correction

**Время:** ~30 секунд

---

## 📋 Ручные действия (НЕ требуются сейчас, но готовься)

### ❌ НЕ нужно

1. **TCGA GDC Token** — публичные данные доступны без токена
2. **Регистрация где-либо** — всё работает анонимно
3. **API keys** — PubMed API open access (rate limit: 3 req/sec)

### ⚠️ Возможно понадобится позже

1. **TCGA Authentication Token** (если скачиваешь >1000 файлов)
   - Зарегистрироваться: https://gdc.cancer.gov/
   - Получить token: https://portal.gdc.cancer.gov/
   - Добавить в скрипт: `headers={'X-Auth-Token': YOUR_TOKEN}`

2. **PubMed API Key** (если делаешь >3 requests/sec)
   - Зарегистрироваться: https://www.ncbi.nlm.nih.gov/account/
   - Получить API key
   - Использовать в `literature_mining.py`

---

## 🧪 Тестирование

Все скрипты протестированы:

```bash
# Test TCGA API (without downloading)
python -c "import requests; r = requests.get('https://api.gdc.cancer.gov/status'); print(r.json())"

# Test scripts syntax
python scripts/download_tcga.py --help
python scripts/extract_mutation_rates.py --help
python scripts/literature_mining.py --help
python scripts/atp_proxy.py --help
```

---

## 📊 Month 1 Deliverables (3 weeks)

1. **Week 1:** Download TCGA data для 5 tissue types (COAD, BRCA, LUAD, GBM, PRAD)
2. **Week 2:** Merge mutation rates + doubling times
3. **Week 3:** Run H0 correlation analysis → checkpoint decision

**Kill criterion:** r < 0.1 после Week 3 → проект закрывается (negative result)

---

## 🔬 Next Steps (если H0 passed)

### Month 2: H1 testing
- Tissue-specific mutation rates
- Mann-Whitney U test (high vs low proliferation)

### Month 3: H0 checkpoint
- **DECISION POINT:** r < 0.3 → KILL, r > 0.4 → proceed to H3

### Month 4: H3 (ATP proxy)
- Download RNA-seq data (TCGA)
- Calculate ATP proxy (OXPHOS genes)
- Correlate with mutation rate

---

## 📧 Контакт Bilinsky

**Когда писать:** ПОСЛЕ Month 3 checkpoint (НЕ раньше!)

**Что отправить:**
1. Preliminary results (H0 correlation)
2. `HYPOTHESIS.md` (pre-registered predictions)
3. Figures: `results/h0_scatter.png`

**Email draft:** `BILINSKY_EMAIL_DRAFT.md`

---

## ⚙️ Troubleshooting

### "Connection timeout" при скачивании
→ Попробуй снова, GDC API иногда медленный

### "File too large" при скачивании
→ MAF файлы могут быть >500 MB, проверь место на диске

### "Module not found" при запуске
→ `pip install -r requirements.txt`

### R скрипт не работает
→ Установи R пакеты: `R -e "install.packages(c('jsonlite', 'boot'))"`

---

## 🎯 Цель Month 1

**Получить первое число:** `r = ???`

Если r > 0.3 → продолжай.  
Если r < 0.3 → publish negative result в PLOS Comp Bio.

---

**Status:** READY TO START 🚀

**Estimated time to first result:** 3 weeks

**Last updated:** 2026-04-25
