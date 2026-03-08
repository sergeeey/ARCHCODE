# 🌐 Galaxy Quick Start — Пошаговая Инструкция

**Цель:** Загрузить FASTQ, запустить STAR, получить junctions

**Время:** 3-4 часа total

---

## ⏱️ Timeline

```
19:00 — Регистрация (5 мин)
19:05 — Загрузка FASTQ (30-60 мин)
20:05 — Запуск STAR для WT (1-2 часа)
22:05 — Запуск STAR для B6 (1-2 часа)
00:05 — Запуск STAR для A2 (1-2 часа)
02:00 — Скачать junctions (10 мин)
02:10 — Локальный анализ (1 мин)
02:15 — 🎉 RESULTS!
```

---

## 📝 ШАГ 1: Регистрация (5 мин)

### 1.1 Открыть Galaxy

**URL:** https://usegalaxy.org/

### 1.2 Click "Login or Register"

В правом верхнем углу → Click **"Login or Register"**

### 1.3 Click "Register"

В форме login → Click **"Register"**

### 1.4 Заполнить форму

```
Email:              [твой email]
Username:           [придумай username]
Password:           [надёжный пароль]
Confirm Password:   [повтори пароль]
First Name:         [твоё имя]
Last Name:          [твоя фамилия]
Institution:        [твоя организация или "Independent Researcher"]
Country:            Kazakhstan
```

### 1.5 Подтвердить email

- Проверь почту
- Click ссылку из письма от Galaxy
- ✅ Готово!

---

## 📤 ШАГ 2: Загрузка FASTQ (30-60 мин)

### 2.1 Click "Upload Data"

В левом верхнем углу → Синяя кнопка **"Upload Data"**

### 2.2 Выбрать файлы

**Способ А: Через браузер (проще)**

1. Click **"Choose local file"**
2. Перейти в: `D:\ДНК\fastq_data\raw\`
3. Выбрать **все 6 файлов**:
   ```
   SRR12935486_1.fastq.gz
   SRR12935486_2.fastq.gz
   SRR12935488_1.fastq.gz
   SRR12935488_2.fastq.gz
   SRR129354890_1.fastq.gz
   SRR12935490_2.fastq.gz
   ```
4. Click **"Start"**

**Способ Б: Через FTP (быстрее для больших файлов)**

```
FTP Server: ftp.usegalaxy.org
Username:   твой email
Password:   твой пароль

Команда (Windows PowerShell):
cd D:\ДНК\fastq_data\raw
curl -T SRR12935486_1.fastq.gz ftp://user:pass@ftp.usegalaxy.org/
curl -T SRR12935486_2.fastq.gz ftp://user:pass@ftp.usegalaxy.org/
... (повторить для всех 6 файлов)
```

### 2.3 Ждать загрузки

**Прогресс:**
- Покажется в **History** (справа)
- Зелёная галочка ✅ = готово

**Время:** ~30-60 мин для всех файлов

---

## 🧬 ШАГ 3: Запуск STAR (1-2 часа на sample)

### 3.1 Открыть инструмент STAR

1. В левой панели → **Tools**
2. Search box → Ввести: `STAR`
3. Click: **"STAR on data"**

### 3.2 Настроить параметры

```
┌─────────────────────────────────────────────────────────────┐
│  STAR Configuration                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Specify input type:                                        │
│  ○ Single-end                                               │
│  ● Paired-end (R1 and R2 files)  ← ВЫБРАТЬ ЭТО             │
│                                                             │
│  FASTQ file for R1:                                         │
│  ▼ SRR12935486_1.fastq.gz       ← Выбрать WT read 1        │
│                                                             │
│  FASTQ file for R2:                                         │
│  ▼ SRR12935486_2.fastq.gz       ← Выбрать WT read 2        │
│                                                             │
│  Reference genome:                                          │
│  ▼ Human (GRCh38) ensembl                       ← Выбрать   │
│                                                             │
│  GTF file (optional):                                       │
│  ▼ Use built-in                                 ← Оставить   │
│                                                             │
│  Output type:                                               │
│  ● BAM (sorted)                                 ← Выбрать   │
│                                                             │
│  Advanced parameters (раскрыть):                            │
│  - AlignSJoverhangMin: 8                        ← Оставить   │
│  - AlignSJDBoverhangMin: 1                      ← Оставить   │
│  - OutFilterMismatchNoverReadLmax: 0.04         ← Оставить   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Click "Run"

Внизу формы → Синяя кнопка **"Run"**

### 3.4 Ждать выполнения

**Прогресс:**
- В History (справа)
- Жёлтая иконка ⏳ = running
- Зелёная галочка ✅ = готово

**Время:** ~1-2 часа

### 3.5 Повторить для B6 и A2

**После завершения WT:**

1. Click **"STAR on data"** снова
2. Выбрать файлы для B6:
   - R1: SRR12935488_1.fastq.gz
   - R2: SRR12935488_2.fastq.gz
3. Click "Run"
4. Ждать 1-2 часа

**После B6:**
1. Повторить для A2 (SRR12935490_1 и SRR12935490_2)

---

## 📥 ШАГ 4: Экспорт Junctions (10 мин)

### 4.1 Найти output STAR

В History (справа) → Найти:
```
STAR on data 1: BAM file
STAR on data 2: BAM file
STAR on data 3: BAM file
```

### 4.2 Извлечь junctions

**Способ А: Через regtools (рекомендуется)**

1. Tools → Search: `regtools`
2. Click: **"regtools junctions extract"**
3. Параметры:
   ```
   Input BAM file: ▼ STAR on data 1 (WT)
   Output format: TSV
   ```
4. Click "Run"
5. Повторить для B6 и A2

**Способ Б: Через Sashimi Plot**

1. Click на BAM файл в History
2. Click **"Visualize"** → **"Sashimi Plot"**
3. В Sashimi Plot → Export junctions

### 4.3 Скачать junctions файлы

Для каждого junctions файла:

1. Click на файл в History
2. Click **стрелку вниз** ⬇️ (Download)
3. Сохранить в: `D:\ДНК\fastq_data\junctions\`

**Имена файлов:**
```
WT_junctions.tab
B6_junctions.tab
A2_junctions.tab
```

---

## 🔬 ШАГ 5: Локальный Анализ (1 мин)

### 5.1 Проверить файлы

```bash
dir D:\ДНК\fastq_data\junctions\*.tab
```

**Ожидается:** 3 файла

### 5.2 Запустить анализ

```bash
cd D:\ДНК
python scripts\analyze_splice_junctions.py
```

### 5.3 Смотреть результаты

**Открыть:**
```
D:\ДНК\fastq_data\results\splice_analysis_report.md
```

**Или в браузере:**
- Просто открыть файл в любом браузере

---

## 📊 Ожидаемые Результаты

```
┌─────────────────────────────────────────────────────────────┐
│  Splice Analysis Results (Ожидание)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WT (SRR12935486):                                          │
│    Aberrant: 2-4%  ✅ <5% (baseline)                        │
│                                                             │
│  B6 (SRR12935488):                                          │
│    Aberrant: 15-30% ✅ Hypothesis validated!                │
│                                                             │
│  A2 (SRR12935490):                                          │
│    Aberrant: 5-8%   ✅ <10% (loop preserved)                │
│                                                             │
│  VERDICT: ✅ LOOP THAT STAYED VALIDATED!                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Troubleshooting

### Проблема: "File upload failed"

**Решение:**
- Использовать FTP вместо браузера
- Проверить интернет-соединение
- Попробовать по одному файлу

---

### Проблема: "STAR failed"

**Решение:**
- Проверить что выбран правильный reference (Human GRCh38)
- Попробовать "STAR with built-in index"

---

### Проблема: "No junctions in output"

**Решение:**
- Проверить что BAM файл не пустой
- Использовать regtools для извлечения

---

## 📞 Поддержка

**Galaxy Training:**
- https://training.galaxyproject.org/

**RNA-seq Tutorial:**
- https://training.galaxyproject.org/training-material/topics/transcriptomics/

**Help Forum:**
- https://help.galaxyproject.org/

---

## ✅ Checklist

- [ ] Зарегистрироваться на Galaxy
- [ ] Загрузить 6 FASTQ файлов
- [ ] Запустить STAR для WT
- [ ] Запустить STAR для B6
- [ ] Запустить STAR для A2
- [ ] Извлечь junctions (regtools)
- [ ] Скачать 3 junctions файла
- [ ] Запустить `analyze_splice_junctions.py`
- [ ] Открыть `splice_analysis_report.md`
- [ ] 🎉 VALIDATED!

---

**Время начала:** _____:_____  
**Ожидаемое завершение:** _____:_____ ( +3-4 часа)

**Good luck! 🍀**
