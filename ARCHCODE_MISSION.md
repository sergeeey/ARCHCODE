# CURSOR MISSION FILE

## ARCHCODE: Full-Stack Genome Architecture Simulation

### Mission Profile

Вы работаете в проекте **ARCHCODE v1.0** — инженерной модели некодирующей архитектуры 3D-генома, интегрированной с симулятором митотического ядра (**Cellular Kernel**).

Cursor должен функционировать как **инженерный ассистент**, создающий код, спецификации, YAML-конфигурации и документацию строго в техническом стиле (не биологическом).

---

# 1. Purpose

Обеспечить разработку полноценной архитектурной симуляции ядра клетки:

```
DNA sequence → chromatin topology → mitotic tension → SAC consensus → anaphase decision
```

Model = ARCHCODE Core + Cellular Kernel + TE Grammar + Non-B Logic + LTL Verification.

Cursor должен генерировать код и документы строго по спецификации ниже.

---

# 2. System Modules

Cursor должен поддерживать разработку следующих модулей:

```
/cellular_kernel/       — SAC Consensus Engine (уже интегрирован)
/archcode_core/         — Loop Extrusion Engine (TAD/TAD-boundary simulation)
/te_grammar/            — Транспозонная грамматика некодирующего генома
/nonB_logic/            — Модели G4, Z-DNA, R-loops (энергетические барьеры)
/epigenetic_compiler/   — Метилирование, компиляция топологии
/genome_to_tension/     — Связка 3D-топологии и рисков меротелии
/risk_matrix/           — VIZIR Risk Analyzer
/research_specs/        — Research tasks generation
/config/                — YAML configs for all modules
/docs/                  — Markdown specs (RFC-like)
```

---

# 3. Engineering Unknowns

Cursor должен держать в контексте, что эти пункты — **неизвестные параметры**, которые нужно либо аппроксимировать, либо вынести в конфигурацию:

### Physical Unknowns:

* P1: правила загрузки когезина (NIPBL sites)
* P2: асимметрия экструзии (one-sided vs symmetric)
* P3: влияние ядерных органелл на барьеры

### Syntax Unknowns:

* S1: полный словарь TE-мотивов
* S2: код разрушения границ (WAPL-recruiting sequences)
* S3: иерархия барьеров (CTCF vs Pol II vs R-loops)

### Logic Unknowns:

* L1: порог перехода B → Z-DNA
* L2: условия формирования G4 *in vivo*
* L3: порог CpG-метилирования для отключения CTCF

Cursor должен использовать их как **риски модели**, отмечая TODO и создавая интерфейсы для подстановки данных.

---

# 4. Risk Matrix (VIZIR)

Cursor должен сопровождать большие изменения файлами вида:

```
/risk_matrix/P1.yaml
/risk_matrix/L2.yaml
```

Формат каждого файла:

```yaml
risk_id: P1
category: Physical
uncertainty: 0.8
impact_on_model: 0.9
priority: 0.72
notes: >
  Unknown cohesin loader logic; requires ChIP-seq NIPBL dataset and TE-motif analysis.
```

---

# 5. ResearchSpec Tasks (RS-01…RS-05)

Cursor должен уметь по запросу создавать полностью формализованные Research Specification files:

Например `/research_specs/RS-01.md`:

```
# RS-01: Cohesin Loader Determinism

Goal:
  Вычислить правила выбора NIPBL-сайтов загрузки.

Method:
  - Integrate NIPBL ChIP-seq
  - Compare TE-motif distribution
  - Build Loader Map v1.0

Deliverable:
  archcode_core/loader_map.py

Constraints:
  Использовать модульную архитектуру, YAML-конфиг, тесты.
```

---

# 6. Coding Style Requirements

Cursor должен:

* генерировать код в стиле **production-quality Python**
* использовать `dataclass`, `Enum`, строгие интерфейсы
* хранить параметры **только** в YAML
* писать документацию в Markdown-формате, структурированную как RFC
* генерировать диаграммы (Mermaid) по запросу
* избегать художественных описаний
* сохранять инженерный стиль VIZIR 2.0:
  **Validation, Integration, Zero-trust, Iterative Refinement**

---

# 7. Folder Templates

Cursor должен поддерживать и автоматически дополнять шаблоны:

### 7.1 Engine Config

```
config/
  archcode_engine.yaml
  cellular_kernel.yaml
  te_grammar.yaml
  nonB_logic.yaml
  epigenetic_compiler.yaml
  risk_matrix.yaml
```

### 7.2 Source Code

```
src/
  archcode_core/
  cellular_kernel/
  te_grammar/
  nonB_logic/
  epigenetic_compiler/
  genome_to_tension/
  risk_matrix/
  utils/
```

---

# 8. Mission Rules

Cursor должен соблюдать:

### Rule 1 — Строгая инженерная терминология

Никакой биологической метафорики.
Только термины: *tension, torque, boundary strength, extrusion events, energy barriers, insulation score*.

### Rule 2 — Модульность

Все новые функции помещаются в отдельные модули, разделены по директориям.

### Rule 3 — Версионирование

Каждый модуль имеет файл:

```
VERSION
CHANGELOG.md
```

### Rule 4 — Верификация

Для сложных модулей Cursor должен автоматически предлагать **тесты** и **LTL-инварианты**.

### Rule 5 — Zero-trust

Все неизвестные параметры должны быть вынесены в конфиги — никаких "магических констант".

---

# 9. Mission Objective

К финалу работы Cursor должен собрать:

### **ARCHCODE v1.0-alpha**

* Loop Extrusion Engine (1D)
* TE Grammar Layer
* Non-B Logic Layer
* Epigenetic Compiler
* Genome→Tension Bridge
* Full SAC Integration via Cellular Kernel
* Risk Matrix Module
* Predictor of Enhancer Hijacking
* Full YAML-driven simulation pipeline

---

# 10. Cursor Expected Behavior

Когда разработчик пишет:

* **"Создай модуль RS-02"** → Cursor создаёт `/research_specs/RS-02.md`
* **"Добавь TE Grammar Engine"** → Cursor создаёт `src/te_grammar/…`
* **"Добавь конфиг NonB Logic"** → Cursor создаёт YAML + интерфейс
* **"Обнови Risk Matrix"** → Cursor патчит YAML-файл
* **"Построй диаграмму архитектуры"** → Cursor выводит Mermaid
* **"Собери релиз ARCHCODE v1.0"** → Cursor собирает сборку, версии и документацию








