# 🌐 Galaxy SRA Import — БЫСТРЫЙ СПОСОБ

**Время:** 5 минут (вместо 30-45 мин FTP + 1-2 часа download)

**Идея:** Galaxy импортирует напрямую из NCBI SRA, не через твой компьютер!

---

## 📋 Шаг 1: Открыть Galaxy

**URL:** https://usegalaxy.org/

**Login:**
- Email: твой email
- Password: твой пароль

**⚠️ Важно:** Если просит активировать email — проверь спам!

---

## 📋 Шаг 2: Get Data from NCBI SRA

### 2.1 Click "Get Data"

В левой панели → Click **"Get Data"**

### 2.2 Click "NCBI SRA"

В выпадающем меню → **"NCBI SRA"**

### 2.3 Ввести SRR номера

**В поле "SRA accession(s)":**

```
SRR12935486
SRR12935488
SRR12935490
```

**Можно все три сразу** (каждый с новой строки)

### 2.4 Выбрать тип данных

```
Data type:
● Paired-end (2 collections)  ← ВЫБРАТЬ ЭТО
```

### 2.5 Click "Submit"

Galaxy начнёт импортировать напрямую с NCBI!

---

## 📋 Шаг 3: Ждать Импорт (10-20 мин)

**Прогресс:**
- В History (справа)
- 3 sample × 2 files = 6 файлов
- Зелёная галочка ✅ = готово

**Время:** ~10-20 минут (NCBI → Galaxy быстро)

---

## 📋 Шаг 4: Проверить Файлы

**В History должно быть:**

```
✅ SRR12935486.1 (forward)
✅ SRR12935486.2 (reverse)
✅ SRR12935488.1 (forward)
✅ SRR12935488.2 (reverse)
✅ SRR12935490.1 (forward)
✅ SRR12935490.2 (reverse)
```

---

## 📋 Шаг 5: Запустить STAR

**Для каждого sample:**

1. Tools → Search "STAR"
2. Select: **"STAR on data"**
3. Параметры:
   ```
   Library type: Paired-end
   FASTQ file 1: ▼ SRR12935486.1
   FASTQ file 2: ▼ SRR12935486.2
   Reference: Human (GRCh38)
   ```
4. Click "Run"
5. Повторить для B6 и A2

**Время:** 1-2 часа на sample

---

## 📋 Шаг 6: Extract Junctions

**После завершения STAR:**

1. Tools → Search "regtools"
2. Select: **"regtools junctions extract"**
3. Input: BAM file от STAR
4. Click "Run"
5. Download результат

**Повторить для 3 sample**

---

## 📋 Шаг 7: Локальный Анализ

**Когда junctions скачаны:**

```bash
cd D:\ДНК
python scripts\analyze_splice_junctions.py
```

**Время:** 1-2 минуты

**Результат:** `fastq_data/results/splice_analysis_report.md`

---

## ⚡ Преимущества Этого Метода

| Метод | Время | Трафик |
|-------|-------|--------|
| **SRA Import** | 10-20 мин | 0 GB (Galaxy↔NCBI) |
| FTP Upload + Galaxy Download | 30-45 мин + 1-2 часа | 13 GB upload + 13 GB download |

**Экономия:** ~2 часа и 26 GB трафика!

---

## ⚠️ Troubleshooting

### Проблема: "Account not activated"

**Решение:**
1. Проверить email (включая Спам)
2. Найти письмо от Galaxy с темой "Activate your account"
3. Click ссылку активации
4. Если нет письма: User → Preferences → Resend activation

---

### Проблема: "SRA import failed"

**Причины:**
- SRR номер неверный
- Данные embargo (не публичные)
- NCBI сервер недоступен

**Решение:**
- Проверить SRR на https://www.ncbi.nlm.nih.gov/sra/
- Попробовать позже

---

### Проблема: "Only single-end imported"

**Решение:**
- При импорте выбрать "Paired-end"
- Если уже импортировано: объединить через "Build List of Dataset Pairs"

---

## ✅ Checklist

- [ ] Login на Galaxy
- [ ] Активировать аккаунт (если нужно)
- [ ] Get Data → NCBI SRA
- [ ] Ввести: SRR12935486, SRR12935488, SRR12935490
- [ ] Выбрать: Paired-end
- [ ] Click Submit
- [ ] Ждать 10-20 мин
- [ ] Проверить 6 файлов в History
- [ ] Запустить STAR (3 раза)
- [ ] Extract junctions (3 раза)
- [ ] Скачать junctions (3 файла)
- [ ] Запустить `analyze_splice_junctions.py`

---

**Время начала:** _____:_____  
**Ожидаемое завершение:** _____:_____ (+2-3 часа)

**Let's go! 🚀**
