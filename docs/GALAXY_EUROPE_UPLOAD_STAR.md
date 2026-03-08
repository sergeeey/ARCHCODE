# 🌐 Galaxy Europe — Upload + STAR Guide

**Сервер:** https://usegalaxy.eu/

---

## 📤 ШАГ 1: Загрузка FASTQ (30-45 мин)

### 1.1 Click "Загрузить"

В левой панели → Синяя кнопка **"Загрузить"** (Upload)

### 1.2 Выбрать файлы

**Click "Выберите локальный файл"**

Перейти в: `D:\ДНК\fastq_data\raw\`

**Выбрать все 6 файлов:**
```
SRR12935486_1.fastq.gz
SRR12935486_2.fastq.gz
SRR12935488_1.fastq.gz
SRR12935488_2.fastq.gz
SRR12935490_1.fastq.gz
SRR12935490_2.fastq.gz
```

### 1.3 Click "Начинать"

**Ждать загрузки:**
- Прогресс в History (справа)
- "Безымянная история"
- Зелёная галочка ✅ = готово

**Время:** 30-45 мин

---

## ✅ ШАГ 2: Проверка Загрузки

**В History (справа) должно быть 6 файлов:**

```
✅ SRR12935486_1.fastq.gz
✅ SRR12935486_2.fastq.gz
✅ SRR12935488_1.fastq.gz
✅ SRR12935488_2.fastq.gz
✅ SRR12935490_1.fastq.gz
✅ SRR12935490_2.fastq.gz
```

**Все зелёные** → Готово к STAR!

---

## 🧬 ШАГ 3: Запуск STAR (1-2 часа на sample)

### 3.1 Открыть инструмент STAR

**В левой панели:**
1. Прокрутить вниз до **"NGS: RNA Analysis"**
2. Click **"STAR"**
3. Select: **"STAR on data"**

### 3.2 Настроить для WT (SRR12935486)

```
┌─────────────────────────────────────────────────────────────┐
│  STAR Parameters                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Specify input type:                                        │
│  ● Paired-end (R1 and R2 files)  ← ВЫБРАТЬ                 │
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
│  GTF file:                                                  │
│  ▼ Use built-in                                 ← Оставить   │
│                                                             │
│  Output type:                                               │
│  ● BAM (sorted)                                 ← Выбрать   │
│                                                             │
│  Click "Run" (внизу)                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Ждать выполнения

**В History:**
- Жёлтая иконка ⏳ = running
- Зелёная галочка ✅ = готово

**Время:** 1-2 часа

---

### 3.4 Повторить для B6 и A2

**После WT:**

1. Click **"STAR"** снова
2. Выбрать файлы для **B6**:
   - R1: SRR12935488_1.fastq.gz
   - R2: SRR12935488_2.fastq.gz
3. Click "Run"
4. Ждать 1-2 часа

**После B6:**
1. Повторить для **A2**:
   - R1: SRR12935490_1.fastq.gz
   - R2: SRR12935490_2.fastq.gz

---

## 📥 ШАГ 4: Extract Junctions (10 мин)

### 4.1 Открыть regtools

**В левой панели:**
1. Search: `regtools`
2. Click: **"regtools junctions extract"**

### 4.2 Настроить для WT

```
┌─────────────────────────────────────────────────────────────┐
│  regtools junctions extract                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input BAM file:                                            │
│  ▼ STAR on data 1: BAM file                     ← Выбрать   │
│                                                             │
│  Output format:                                             │
│  ● TSV                                          ← Выбрать   │
│                                                             │
│  Click "Run"                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Повторить для B6 и A2

**Для каждого BAM файла:**
- B6: STAR on data 2 → regtools
- A2: STAR on data 3 → regtools

---

## 💾 ШАГ 5: Скачать Junctions (5 мин)

### 5.1 Найти junctions файлы

**В History:**
```
✅ regtools junctions extract 1: TSV (WT)
✅ regtools junctions extract 2: TSV (B6)
✅ regtools junctions extract 3: TSV (A2)
```

### 5.2 Скачать

**Для каждого файла:**
1. Click на файл в History
2. Click **стрелку вниз** ⬇️
3. Сохранить в: `D:\ДНК\fastq_data\junctions\`

**Переименовать:**
```
WT_junctions.tab
B6_junctions.tab
A2_junctions.tab
```

---

## 📊 Дополнительные анализы (опционально)

После STAR и junctions можно запустить на тех же данных:

- **featureCounts** — подсчёт ридов по генам → уровень экспрессии HBB в WT/B6/A2.
- **MultiQC** — сводка по логам STAR (% aligned, качество).

Подробный чеклист (три уровня, фильтр novel junctions, StringTie, IGV): **[GALAXY_EU_STAR_DOWNSTREAM.md](GALAXY_EU_STAR_DOWNSTREAM.md)**.

---

## 🔬 ШАГ 6: Локальный Анализ (1 мин)

**Если junctions скачали в Downloads** (а не сразу в `fastq_data\junctions`), сначала перенесите и переименуйте:

```powershell
# Создать папку
New-Item -ItemType Directory -Path "D:\ДНК\fastq_data\junctions" -Force

# Посмотреть точные имена в Downloads (подставьте свои, если отличаются)
Get-ChildItem "$env:USERPROFILE\Downloads" | Where-Object { $_.Name -match "SRR12935486|SRR12935488|SRR12935490|junction|regtools" }

# Переместить и переименовать (если файлы называются SRR12935486..., SRR12935488..., SRR12935490...)
Move-Item "$env:USERPROFILE\Downloads\*SRR12935486*" "D:\ДНК\fastq_data\junctions\WT_junctions.bed" -Force
Move-Item "$env:USERPROFILE\Downloads\*SRR12935488*" "D:\ДНК\fastq_data\junctions\B6_junctions.bed" -Force
Move-Item "$env:USERPROFILE\Downloads\*SRR12935490*" "D:\ДНК\fastq_data\junctions\A2_junctions.bed" -Force
```

Скрипт принимает и `.bed`, и `.tab`. Имена должны заканчиваться на `_junctions.bed` или `_junctions.tab` (например `WT_junctions.bed`).

### 6.1 Проверить файлы

```powershell
dir D:\ДНК\fastq_data\junctions\
```

**Ожидается:** 3 файла (WT_junctions.*, B6_junctions.*, A2_junctions.*)

### 6.2 Запустить анализ

```bash
cd D:\ДНК
python scripts\analyze_splice_junctions.py
```

### 6.3 Смотреть результаты

**Открыть:**
```
D:\ДНК\fastq_data\results\splice_analysis_report.md
```

---

## ⏱️ Timeline

```
19:00 — Загрузка FASTQ (30-45 мин)
19:45 — Проверка загрузки (5 мин)
19:50 — STAR для WT (1-2 часа)
21:50 — STAR для B6 (1-2 часа)
23:50 — STAR для A2 (1-2 часа)
01:50 — Extract junctions (10 мин)
02:00 — Скачать junctions (5 мин)
02:05 — Локальный анализ (1 мин)
02:10 — 🎉 RESULTS!
```

---

## 📊 Ожидаемые Результаты

```
┌─────────────────────────────────────────────────────────────┐
│  Splice Analysis (Ожидание)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WT:  <5% aberrant   ✅ Baseline                            │
│  B6:  15-30% aberrant ✅ HYPOTHESIS!                        │
│  A2:  <10% aberrant  ✅ Control                             │
│                                                             │
│  Если B6 = 15-30% → "Loop That Stayed" VALIDATED!          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📞 Когда Завершится Загрузка

**Пришли скриншот** History с 6 зелёными файлами → покажу куда нажать для STAR!

**Good luck! 🍀**
