# 🌐 Galaxy RNA-seq Analysis Guide

**Вариант В:** Использование Galaxy Web Platform для STAR alignment

---

## 📋 Обзор

**Galaxy:** https://usegalaxy.org/

**Преимущества:**
- ✅ Не нужна локальная установка STAR
- ✅ Бесплатно для академических исследований
- ✅ Полноценный STAR alignment
- ✅ Экспорт splice junctions

**Время:** 2-3 часа (включая загрузку/выгрузку)

---

## 🚀 Пошаговая Инструкция

### Шаг 1: Регистрация

1. Открыть: https://usegalaxy.org/
2. Click "Login or Register" → "Register"
3. Заполнить форму (email, institution)
4. Подтвердить email

---

### Шаг 2: Загрузка FASTQ файлов

**Файлы для загрузки:**

| Sample | Files | Size |
|--------|-------|------|
| WT | SRR12935486_1.fastq.gz, SRR12935486_2.fastq.gz | 3.8 GB |
| B6 | SRR12935488_1.fastq.gz, SRR12935488_2.fastq.gz | 4.0 GB |
| A2 | SRR12935490_1.fastq.gz, SRR12935490_2.fastq.gz | 4.6 GB |

**В Galaxy:**
1. Click "Upload Data" (top left)
2. Click "Choose local file"
3. Select files (можно несколько сразу)
4. Wait for upload (30-60 min для всех)

**Альтернатива (быстрее):** Загрузить через FTP

```
FTP Server: ftp.usegalaxy.org
Username: ваш email
Password: ваш пароль
```

---

### Шаг 3: Запуск STAR

**В Galaxy:**

1. **Tools** → Search "STAR"
2. Select: **"STAR on data"**
3. Configure:

```
Parameter          Value
─────────────────────────────────────────────────────
Library type       Paired-end
FASTQ file 1       SRR12935486_1 (WT read 1)
FASTQ file 2       SRR12935486_2 (WT read 2)
Reference genome   Human (GRCh38)
Gene model         Use built-in or upload GTF
Output format      BAM (sorted)
```

4. Click "Run"
5. Repeat for B6 и A2 samples

**Время:** ~1-2 часа на sample

---

### Шаг 4: Экспорт Splice Junctions

**После завершения STAR:**

1. Найти output файл (BAM)
2. Click на файл → **"Visualize"** → **"Sashimi Plot"** или **"Junctions"**
3. Или использовать инструмент: **"BAM to junctions"**
4. Export как TSV/TXT

**Альтернатива:**
1. Tools → Search "regtools"
2. Select: **"regtools junctions extract"**
3. Input: BAM file
4. Output: TSV файл с junctions

---

### Шаг 5: Download Results

**Скачать файлы:**

1. Найти junctions файл в истории
2. Click на файл → **Download** (стрелка вниз)
3. Сохранить в: `D:\ДНК\fastq_data\junctions\`

**Имя файла:**
```
WT_junctions.tab
B6_junctions.tab
A2_junctions.tab
```

---

## 📊 Ожидаемый Выход

**Формат junctions файла (TSV):**

```
chromosome    donor    acceptor    strand    motif    unique_reads    total_reads
chr11         5225726  5226405     +         1        150             180
chr11         5226626  5227079     +         1        200             220
...
```

---

## 🔧 Локальная Обработка (после Galaxy)

**После скачивания junctions:**

```bash
# 1. Переместить в правильную директорию
mv Downloads/WTSample_junctions.tab D:\ДНК\fastq_data\junctions\WT_junctions.tab
mv Downloads/B6Sample_junctions.tab D:\ДНК\fastq_data\junctions\B6_junctions.tab
mv Downloads/A2Sample_junctions.tab D:\ДНК\fastq_data\junctions\A2_junctions.tab

# 2. Запустить splice analysis
cd D:\ДНК
python scripts\analyze_splice_junctions.py
```

---

## ⚡ Оптимизация (Параллельная Загрузка)

### Быстрая загрузка через command line:

**Создать файл `upload_to_galaxy.sh`:**

```bash
#!/bin/bash
# Upload FASTQ to Galaxy via FTP

FTP_SERVER="ftp.usegalaxy.org"
FTP_USER="your_email@example.com"
FTP_PASS="your_password"

cd D:/ДНК/fastq_data/raw

# Upload all FASTQ files
for file in *.fastq.gz; do
    echo "Uploading $file..."
    curl -T "$file" "ftp://$FTP_USER:$FTP_PASS@$FTP_SERVER/"
done

echo "Upload complete!"
```

---

## 📊 Альтернативы Galaxy

### 1. GenePattern (Broad Institute)

**URL:** https://genepattern.broadinstitute.org/

**Преимущества:**
-STAR available
- Бесплатно для academics
- Меньше очередь чем Galaxy

---

### 2. CyVerse

**URL:** https://cyverse.org/

**Преимущества:**
- 100 TB free storage
- STAR, HISAT2, Salmon
- Good for large datasets

---

### 3. AnVIL

**URL:** https://anvil.terra.bio/

**Преимущества:**
- Google Cloud based
- STAR, RNA-seq pipelines
- Free for NIH-funded research

---

## 🎯 Критерии Успеха

**После Galaxy анализа:**

- [ ] 3 BAM файла (WT, B6, A2)
- [ ] 3 junctions файла
- [ ] Junctions файлы импортированы в `fastq_data/junctions/`
- [ ] Запущен `analyze_splice_junctions.py`
- [ ] Получен `splice_analysis_report.md`

---

## 📞 Поддержка

**Galaxy Documentation:**
- https://galaxyproject.org/learn/

**RNA-seq Tutorials:**
- https://training.galaxyproject.org/

**Вопросы?**
- Galaxy Help Forum: https://help.galaxyproject.org/

---

## 🚀 Quick Start Checklist

- [ ] Зарегистрироваться на Galaxy
- [ ] Загрузить FASTQ файлы (6 файлов)
- [ ] Запустить STAR для WT
- [ ] Запустить STAR для B6
- [ ] Запустить STAR для A2
- [ ] Экспортировать junctions файлы
- [ ] Скачать локально
- [ ] Запустить `analyze_splice_junctions.py`

**Estimated time:** 3-4 hours total
