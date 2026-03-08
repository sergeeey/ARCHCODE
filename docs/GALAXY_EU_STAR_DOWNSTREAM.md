# Что выжать из STAR на Galaxy EU — максимально для ARCHCODE

После того как у вас есть **BAM** и **splice junctions** для WT/B6/A2 (STAR + regtools на Galaxy EU), ниже — полный список анализов, которые можно запустить на тех же данных.

**Ссылки:** [GALAXY_EUROPE_UPLOAD_STAR.md](GALAXY_EUROPE_UPLOAD_STAR.md), [GALAXY_RNASEQ_GUIDE.md](GALAXY_RNASEQ_GUIDE.md).

---

## Уровень 1 — Базовый (сделать сегодня)

### 1. featureCounts (рекомендуется Galaxy)

- **Вход:** три mapped BAM (WT, B6, A2).
- **Действие:** Tools → **featureCounts** → подать BAM → считает reads на каждый ген.
- **Результат:** уровень экспрессии HBB в WT vs B6 vs A2.
- **Вопрос:** снижается ли HBB мРНК при нарушении петли?

**Параметры на Galaxy EU:**

```
Input BAM: datasets 36, 42, 48 (или ваши три mapped BAM)
Gene annotation: Human (hg38) — встроенный
Feature type: exon
Gene ID: gene_id
→ Execute
```

Итог: таблица с counts по генам → строка **HBB** даёт число ридов по образцам.

**После скачивания результата с Galaxy** можно локально сравнить HBB между образцами (WT/B6/A2): запустите скрипт [scripts/parse_featurecounts_hbb.py](../scripts/parse_featurecounts_hbb.py), передав путь к скачанному файлу featureCounts. Скрипт извлечёт counts по HBB, посчитает нормализацию на размер библиотеки (CPM) и запишет JSON в `results/hbb_featurecounts.json`; опционально флаг `--plot` строит bar plot в `results/hbb_featurecounts_comparison.png`. Пример: `python scripts/parse_featurecounts_hbb.py path/to/featurecounts.txt -o results/hbb_featurecounts.json --plot`.

### 2. MultiQC на логах STAR

- **Вход:** логи STAR (если Galaxy сохранил их в History).
- **Действие:** Tools → **MultiQC** → указать лог-файлы STAR.
- **Результат:** % выровненных ридов, mismatch rate, проверка качества alignment.

---

## Уровень 2 — Ключевой для гипотезы

### 3. Правильный splice junction анализ (фильтр по STAR manual)

Формат **STAR SJ.out.tab** (колонки 1–9):

| Колонка | Содержимое |
|---------|------------|
| 1 | Contig (chr) |
| 2 | First base of intron (1-based) |
| 3 | Last base of intron (1-based) |
| 4 | Strand (0/1/2) |
| 5 | Intron motif (0 = non-canonical, 1 = GT/AG, …) |
| 6 | Annotated (0 = novel, 1 = annotated) |
| 7 | Unique reads |
| 8 | Multimap reads |
| 9 | Max overhang |

**Рекомендуемый фильтр (STAR manual):**

- Колонка 5 > 0 (канонический мотив GT/AG и др.)
- Колонка 6 == 0 (NOVEL junction, не аннотированный)
- Колонка 7 > 5 (минимум 6 уникальных ридов)

Так отфильтровывается мусор и остаются **реальные novel junctions**. Сравнивать количество novel junctions на HBB между WT, B6 и A2 нужно **с нормализацией по глубине секвенирования** (см. [scripts/normalize_junctions_by_depth.py](../scripts/normalize_junctions_by_depth.py)).

**Важно:** n=1 на условие; все выводы — **exploratory**. Не использовать для сильных claims в manuscript без биологических реплик.

**Локальные скрипты:**

- [scripts/analyze_splice_junctions.py](../scripts/analyze_splice_junctions.py) — с флагом `--star-filter` применяет этот фильтр при чтении SJ.out.tab.
- [scripts/filter_star_novel_junctions_hbb.py](../scripts/filter_star_novel_junctions_hbb.py) — отдельный скрипт: три SJ.out.tab → фильтр → HBB locus → подсчёт novel по образцам и (опционально) нормализация по глубине.

Пример после скачивания SJ.out.tab с Galaxy (имена файлов подставьте свои):

```bash
cd D:\ДНК
python scripts/filter_star_novel_junctions_hbb.py fastq_data/junctions/WT.SJ.out.tab fastq_data/junctions/B6.SJ.out.tab fastq_data/junctions/A2.SJ.out.tab -o fastq_data/results/star_novel_hbb.json
```

---

## Уровень 3 — Публикационный уровень

### 4. DESeq2 / edgeR (дифференциальная экспрессия)

- **Ограничение:** нужны реплики. При n=1 на условие **статистически неприменимо**.

### 5. StringTie (сборка транскриптов)

- **Вход:** BAM от STAR.
- **Действие:** Tools → **StringTie** → указать BAM + аннотацию (hg38).
- **Результат:** сборка транскриптов; можно смотреть новые изоформы HBB в B6/A2.
- Работает с n=1 как **exploration** (без статистики).

### 6. IGV (локально, не в Galaxy)

- Скачать BAM с Galaxy → открыть в IGV.
- Регион: **chr11:5,225,000–5,230,000** (HBB).
- Визуально: coverage drop или необычные риды в B6/A2; подходит для фигуры в статье.

---

## Что реально даёт результат для статьи

| Анализ | Реалистично? | Что даёт |
|--------|--------------|----------|
| featureCounts → HBB expression | Да, сегодня, ~10 мин | «HBB снижен на X% в B6/A2» (с оговоркой n=1) |
| Novel junctions (фильтр STAR) | Да, сегодня, ~20 мин | Реальные novel junctions, сравнение с нормализацией по глубине |
| StringTie изоформы | Да, позже, ~1 ч | Новые транскрипты (exploration) |
| IGV визуализация | Да, позже, ~30 мин | Картинка для статьи |
| DESeq2 | Нет | Нет реплик — невозможно |

---

## Конкретный следующий шаг

**Запустить featureCounts на Galaxy EU** (~10 минут):

1. Galaxy EU → **Tools** → поиск **featureCounts**.
2. **Input:** три BAM (WT, B6, A2 mapped).
3. **Gene annotation:** Human (GRCh38/hg38), встроенный.
4. **Feature type:** exon.
5. **Gene ID:** gene_id.
6. **Execute.**

Результат: таблица с counts по генам → строка **HBB** — число ридов по образцам. Интерпретировать с учётом глубины секвенирования и n=1.

---

## Финальный шаг: featureCounts → HBB expression (WT vs B6 vs A2)

### Предусловие

- На usegalaxy.eu в History зелёный датасет **#52: gencode.v46.basic.annotation.gtf.gz**
- Зелёные BAM коллекции: **#36** (WT), **#42** (B6), **#48** (A2)

### Galaxy EU — featureCounts

Tools → поиск `featureCounts` → открыть форму:

| Параметр | Значение |
|----------|----------|
| Файл выравнивания | Иконка папки → выбрать #36, #42, #48 |
| Файл аннотации | «Файл из истории» → #52 gencode.v46 GTF |
| Укажите информацию о нити | Не застрявший |
| Feature type | exon (по умолчанию) |
| Gene attribute | gene_id (по умолчанию) |

→ **Run** → ждать ~5 мин → скачать результат (`.txt`)

### Локально — парсинг и график

```powershell
# Позиционный аргумент или --input <путь>:
python scripts\parse_featurecounts_hbb.py "$env:USERPROFILE\Downloads\<имя_файла>.txt" --plot
```

Выходы:

- `results/hbb_featurecounts.json` — сырые counts и CPM для WT/B6/A2
- `results/hbb_featurecounts_comparison.png` — bar plot

### Ожидаемый результат

HBB CPM: WT > B6 ≥ A2 (нарушение петли LCR → снижение экспрессии β-глобина). Интерпретация: exploratory, n=1 на условие.

---

## Соответствие правилам проекта

- **Результаты exploratory:** не заявлять «подтверждено» без реплик; при упоминании в manuscript — только в **Limitations** с формулировками из [results/publication_claim_matrix_2026-03-06.json](../results/publication_claim_matrix_2026-03-06.json).
- **Нормализация по глубине:** при сравнении counts между образцами (featureCounts, novel junction counts) обязательно учитывать разную глубину (см. [scripts/check_sequencing_depth.py](../scripts/check_sequencing_depth.py), [scripts/normalize_junctions_by_depth.py](../scripts/normalize_junctions_by_depth.py)).
- **Legacy-нарративы:** не использовать старые формулировки для сильных claims; см. [docs/internal/LEGACY_CLAIM_HYGIENE_2026-03-06.md](internal/LEGACY_CLAIM_HYGIENE_2026-03-06.md).
