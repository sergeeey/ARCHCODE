# ✅ ARCHCODE Tonight Checklist — 2026-03-06

## 🎯 Goal
Запустить FASTQ download и подготовить почву для manuscript updates.

---

## ✅已完成 (Done)

- [x] Стратегическое позиционирование (Discovery Engine)
- [x] Benchmark скрипт создан
- [x] FASTQ download скрипты созданы
- [x] Документация обновлена
- [x] Status dashboard создан

---

## ⏳ Tonight (после 19:00)

### Option A: Если SRA Toolkit установлен

```bash
cd D:\ДНК
scripts\download_rnaseq_fastq.bat
```

**Ожидается:**
- 6 файлов FASTQ (~30 GB)
- 4-6 часов
- Утром: проверить файлы

---

### Option B: Если SRA Toolkit НЕ установлен (PowerShell, без установки)

```powershell
cd D:\ДНК
powershell -ExecutionPolicy Bypass -File scripts\download_fastq_alternative.ps1
```

**Ожидается:**
- Те же 6 файлов FASTQ
- Прямая загрузка с NCBI
- Не требует fastq-dump

---

### Option C: Установить SRA Toolkit

1. Прочитать: `fastq_data\INSTALL_SRA_TOOLKIT.md`
2. Установить SRA Toolkit
3. Запустить Option A

---

## 📊 Проверка утром (2026-03-07)

```bash
# Проверить файлы
dir fastq_data\raw\*.fastq.gz

# Ожидается:
# SRR12837671_1.fastq.gz  (~5 GB)
# SRR12837671_2.fastq.gz  (~5 GB)
# SRR12837674_1.fastq.gz  (~5 GB)
# SRR12837674_2.fastq.gz  (~5 GB)
# SRR12837675_1.fastq.gz  (~5 GB)
# SRR12837675_2.fastq.gz  (~5 GB)
# Total: ~30 GB
```

---

## 📋 Plan на завтра (2026-03-07)

- [ ] Проверить FASTQ файлы (утро)
- [ ] Review `docs\MANUSCRIPT_UPDATE_PLAN.md`
- [ ] Утвердить изменения в manuscript
- [ ] Запустить benchmark: `python scripts\build_blind_spot_benchmark.py`

---

## 🚨 Если что-то пошло не так

### FASTQ download не запустился
→ Прочитать: `fastq_data\INSTALL_SRA_TOOLKIT.md`
→ Использовать PowerShell script (Option B)

### Файлы повреждены
→ Удалить и запустить заново
→ Проверить checksums (если доступны)

### Мало места на диске
→ Очистить temp файлы
→ Переместить другие данные

---

## 📞 Контакты

**Вопросы?** sergeikuch80@gmail.com

**Документация:**
- `fastq_data\README.md` — общая информация
- `fastq_data\INSTALL_SRA_TOOLKIT.md` — установка SRA Toolkit
- `docs\STATUS_DASHBOARD.md` — текущий статус
- `docs\MANUSCRIPT_UPDATE_PLAN.md` — план manuscript

---

**Главный принцип: "First, do no harm" ✅**

Ничего не удалено, не перезаписано. Только новые файлы.
