# TECH MEMO: ARCHCODE KERNEL UPDATE v1.1

**Subject:** Parameterization of Engineering Unknowns via Deep Literature Analysis  
**Target:** ARCHCODE Core Simulation Engine  
**Date:** 2025-11-23  
**Status:** RESOLVED / READY FOR IMPLEMENTATION

---

## 1. Executive Summary

Проведенный анализ 40+ источников позволил закрыть критические пробелы в спецификации физического движка.

**Главные инсайты для обновления модели:**

1. **Cohesin Symmetry (P1):** Доказана строгая фазовая зависимость. Интерфаза = Симметричная экструзия; Митоз = Асимметричная.

2. **NIPBL Kinetics (P3):** NIPBL — это не бинарный загрузчик, а аналоговый регулятор скорости (Throttle), работающий в синергии с WAPL (Lifetime).

3. **Z-DNA Trigger (S1):** Определен точный физический порог суперспирализации ($\sigma \approx -0.06$) для перехода B-Z.

4. **CTCF Logic (L2):** Обнаружена асимметрия чувствительности к метилированию (Hemimethylation logic).

---

## 2. Resolved Physical Parameters (P-Series)

### P1: Cohesin vs Condensin Symmetry

**Проблема:** Был риск неверного моделирования топологии петель (односторонняя vs двусторонняя).

**Решение:** Данные подтверждают модель "Double-Hierarchical Loop".

- **Интерфаза (Cohesin):** Работает в симметричном режиме ("reel-in" с двух сторон). Это критично для формирования TADs.
- **Митоз (Condensin):** Работает асимметрично ("one-sided"), что необходимо для линейной компактизации хроматина.

**Config Update:** `config/physical/P1_extrusion_symmetry.yaml`

---

### P3: NIPBL Dosage & Kinetics

**Проблема:** Ранее NIPBL моделировался как вероятность старта ($P_{load}$).

**Решение:** NIPBL управляет скоростью экструзии ($V_{ext}$). Процессивность петли = $Rate(NIPBL) \times Lifetime(WAPL)$.

- Снижение NIPBL (как при синдроме Корнелии де Ланге) замедляет петли, но не останавливает их.
- Это объясняет, почему снижение WAPL (увеличение времени жизни) может компенсировать дефицит NIPBL.

**Config Update:** `config/physical/P3_rate_kinetics.yaml`

---

## 3. Resolved Structural Logic (S-Series)

### S1: Z-DNA Activation Threshold

**Проблема:** Отсутствие точного триггера для Z-DNA барьеров.

**Решение:** Установлен термодинамический порог плотности супервитков ($\sigma$).

- В физиологических условиях переход B → Z происходит при $\sigma \le -0.06$.
- Последовательности (dC-dG)n являются сенсорами.

**Config Update:** `config/structural/S1_zdna_thresholds.yaml`

---

### S2: WAPL Recruitment Logic

**Проблема:** Как WAPL узнает, где сбросить когезин?

**Решение:**

1. **FGF Motifs:** WAPL использует мотивы FGF для связывания с PDS5 и STAG.
2. **R-loop Dependency:** R-петли и G-квадриплексы (G4) рекрутируют WAPL, вызывая сброс когезина при конфликте с транскрипцией.

**Config Update:** `config/structural/S2_wapl_recruitment.yaml`

---

## 4. Resolved Logical Gates (L-Series)

### L2: CTCF Methylation Sensitivity (Quantitative)

**Проблема:** Бинарная модель (Methylated = Off) неточна.

**Решение:** Квантование сродства (Kd).

- **Полное метилирование:** Снижает связывание. Kd растет с 163 nM до 1075 nM (~7-кратное падение аффинности).
- **Гемиметилирование (Hemimethylation):** Асимметричный эффект.
  - Метилирование motif strand: Ингибирует (до 7x).
  - Метилирование opposite strand: Может стимулировать (до 4x).
- Это создает механизм "Strand-Specific Valving" для CTCF.

**Config Update:** `config/logical/L2_ctcf_logic.yaml`

---

### L3: Kinetochore Tension Sensing

**Проблема:** Механизм "Catch Bond" требовал уточнения.

**Решение:** Подтверждена роль Aurora B и пространственного разделения.

- Натяжение физически удаляет субстраты (Ndc80) от киназы (Aurora B).
- NIPBL также играет роль в регуляции транскрипции MYCN в нейробластоме, связывая митоз и онкогенез.

---

## 5. Next Steps for ARCHCODE

1. **Code Implementation:** Обновить классы `CohesinMotor` и `CTCFGate` в модуле `archcode_core` с новыми формулами.

2. **Simulation Run:** Запустить сценарий "CdLS Simulation" (Cornelia de Lange Syndrome), уменьшив параметр `nipbl_velocity_multiplier` до 0.5, и проверить, приведет ли это к "размытию" TAD границ.

3. **Risk Analysis:** Обновить матрицу рисков, добавив "Hemimethylation Failure" как новый вектор онкогенной дерегуляции (из-за возможного 4-кратного усиления связывания CTCF в неправильном контексте).

---

**Подпись:**  
ARCHCODE v1.0-alpha Core System

**Источники:**
1. NIPBL dosage shapes genome folding by tuning the rate of cohesin ..., дата последнего обращения: ноября 23, 2025, https://www.biorxiv.org/content/10.1101/2025.08.14.667581v1.full-text








