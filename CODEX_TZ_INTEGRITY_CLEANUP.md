# ТЗ для Codex: Scientific Integrity Cleanup

**Проект:** D:\ДНК (ARCHCODE)
**Приоритет:** CRITICAL — блокирует публикацию
**Ожидаемое время:** 20-30 минут
**Режим:** suggest (только файлы из списка)

---

## КОНТЕКСТ

Проект ARCHCODE содержит научные утверждения, которые были идентифицированы аудитом как ложные или необоснованные. Нужна механическая чистка по 5 категориям. НЕ трогай логику движка, НЕ трогай тесты, НЕ создавай новые файлы.

**Правило:** Каждая замена — точечная. Не переписывай абзацы. Меняй только конкретную фразу.

---

## ЗАДАЧА 1: Sabaté 2025 → Sabaté 2024 (bioRxiv)

**Что:** Заменить ВСЕ оставшиеся "Sabaté et al., 2025" и "Sabaté et al. 2025" на корректную ссылку.

**Замена:**

```
BEFORE: Sabaté et al., 2025
AFTER:  Sabaté et al., 2024 (bioRxiv)

BEFORE: Sabaté et al. 2025
AFTER:  Sabaté et al. 2024 (bioRxiv)

BEFORE: Sabaté et al., Nature Genetics 2025
AFTER:  Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)
```

**Файлы (проверить каждый):**

- ARCHCODE_Preprint.html
- ARCHCODE_Preprint_RU.html
- config/nature2025.json
- PUBLICATION_READY.md
- SCIENTIFIC_PAPER_DRAFT.md (если есть)
- scripts/generate-clinical-atlas.ts
- scripts/generate-final-report.ts
- scripts/validate-mysterious-vus.ts
- scripts/quick-atlas.ts
- scripts/test-parser-integration.ts
- .claude/agents/vus-analyzer.md
- .claude/commands/validate-blind.md
- .claude/output-styles/scientific.md

**Verify:**

```bash
cd "D:\ДНК"
rg -i "Sabat[eé].*2025" --glob "!node_modules/**" --glob "!FALSIFICATION_REPORT.md" --glob "!CLAUDE.md" --glob "!PROJECT_AUDIT*" --glob "!AUDIT*" --glob "!HALUGATE*"
# Ожидаемый результат: 0 совпадений (кроме аудит-документов где это задокументировано как ошибка)
```

---

## ЗАДАЧА 2: "fitted to FRAP data" → honest labeling

**Что:** Заменить ВСЕ оставшиеся claims что параметры "fitted to FRAP data".

**Замена:**

```
BEFORE: fitted to FRAP data
AFTER:  estimated from literature ranges (Gerlich et al., 2006; Hansen et al., 2017)

BEFORE: fitted to experimental FRAP data
AFTER:  estimated from published FRAP measurements (Gerlich et al., 2006)

BEFORE: fitted to FRAP data (Sabaté et al., 2025)
AFTER:  estimated from literature ranges (Gerlich et al., 2006; Hansen et al., 2017)

BEFORE: fitted to FRAP data, R²=0.89
AFTER:  estimated from literature ranges; R²=0.89 on simulation self-consistency check
```

**Файлы:**

- ARCHCODE_Preprint.html
- ARCHCODE_Preprint_RU.html
- scripts/generate-clinical-atlas.ts
- scripts/validate-mysterious-vus.ts
- scripts/quick-atlas.ts
- scripts/test-parser-integration.ts

**Verify:**

```bash
rg "fitted to FRAP" --glob "!node_modules/**" --glob "!FALSIFICATION_REPORT.md" --glob "!CLAUDE.md" --glob "!AUDIT*" --glob "!HALUGATE*"
# Ожидаемый результат: 0 совпадений
```

---

## ЗАДАЧА 3: R²=0.89 — добавить disclaimer

**Что:** R²=0.89 нельзя просто удалить (оно в десятках мест). Нужно добавить контекст что это НЕ валидация на внешних данных.

**Замена (в manuscript/ файлах):**

```
BEFORE: R²=0.89 validation on blind loci
AFTER:  R²=0.89 on held-out simulation loci (not independently validated against experimental data)

BEFORE: achieving R²=0.89 validation
AFTER:  achieving R²=0.89 self-consistency

BEFORE: validated model (R²=0.89 on independent loci)
AFTER:  model self-consistency R²=0.89 (experimental Hi-C validation: r=0.16, not significant)
```

**Замена (в HTML preprints):**

```
BEFORE: R²=0.89
AFTER:  R²=0.89 (self-consistency; experimental validation pending)
```

**Файлы:**

- manuscript/ABSTRACT.md (строка 11)
- manuscript/METHODS.md
- manuscript/RESULTS.md
- manuscript/FULL_MANUSCRIPT.md
- manuscript/VALIDATION_DISCUSSION.md
- ARCHCODE_Preprint.html (все вхождения)
- ARCHCODE_Preprint_RU.html (все вхождения)
- results/LOOP_THAT_STAYED_INDEX.md
- results/LOOP_THAT_STAYED_EXECUTIVE_SUMMARY.md

**Verify:**

```bash
rg "R²=0.89" --glob "!node_modules/**" --glob "!FALSIFICATION*" --glob "!AUDIT*" --glob "!CLAUDE.md" -c
# Результат: каждое оставшееся вхождение должно содержать "(self-consistency" или "(experimental validation pending)"
rg "R²=0.89" --glob "manuscript/**" -A1
# Проверить что контекст корректный
```

---

## ЗАДАЧА 4: AlphaGenome mock disclosure

**Что:** В manuscript и preprint AlphaGenome scores (0.454-0.456) представлены как реальные. Нужно добавить disclosure.

**Замена (в manuscript/ABSTRACT.md и FULL_MANUSCRIPT.md):**

```
BEFORE: missed by AlphaGenome (scores 0.454-0.456, all VUS)
AFTER:  scored as VUS by mock AlphaGenome baseline (scores 0.454-0.456; synthetic predictions pending real API availability)
```

**Замена (в manuscript/RESULTS.md):**

```
BEFORE: AlphaGenome exhibits systematic blind spot
AFTER:  Mock AlphaGenome baseline shows systematic score divergence (pending validation with real AlphaGenome API)
```

**Замена (в manuscript/INTRODUCTION.md и DISCUSSION.md):**

```
BEFORE: AlphaGenome systematically misses
AFTER:  Sequence-based predictors may systematically miss

BEFORE: AlphaGenome blind spot
AFTER:  potential blind spot for sequence-based predictors
```

**Файлы:**

- manuscript/ABSTRACT.md
- manuscript/FULL_MANUSCRIPT.md
- manuscript/RESULTS.md
- manuscript/INTRODUCTION.md
- manuscript/DISCUSSION.md (если есть)
- ARCHCODE_Preprint.html
- ARCHCODE_Preprint_RU.html

**ВАЖНО:** НЕ трогай METHODS.md и VALIDATION_DISCUSSION.md — там уже есть disclosure после предыдущих правок.

**Verify:**

```bash
rg "missed by AlphaGenome" --glob "manuscript/**"
# Ожидаемый результат: 0 совпадений
rg "AlphaGenome blind spot" --glob "manuscript/**"
# Ожидаемый результат: 0 совпадений
rg "AlphaGenome exhibits systematic" --glob "manuscript/**"
# Ожидаемый результат: 0 совпадений
```

---

## ЗАДАЧА 5: README.md status fix

**Файл:** README.md

**Замена:**

```
BEFORE: **Status**: Publication Ready ✅
AFTER:  **Status**: In Development (scientific integrity review in progress)
```

**Verify:**

```bash
rg "Publication Ready" README.md
# Ожидаемый результат: 0 совпадений
```

---

## НЕ ТРОГАТЬ (whitelist)

Эти файлы документируют ОШИБКИ (не содержат их):

- FALSIFICATION_REPORT.md
- CLAUDE.md
- AUDIT_REPORT.md
- AUDIT_RESPONSE.md
- AUDIT_HIDDEN_FAILURE_MODES_2026-02-05.md
- HALUGATE_REPORT.md
- PROJECT_AUDIT_2026-02-05.md
- docs/FAILURE_MODES.md
- KNOWN_ISSUES.md

---

## ПОСЛЕ ВСЕХ ПРАВОК

### Verify-команды (запустить все):

```bash
cd "D:\ДНК"

# 1. Sabaté 2025 — должно быть 0 (кроме audit docs)
echo "=== Sabaté 2025 check ==="
rg -c "Sabat[eé].*2025" --glob "!node_modules/**" --glob "!FALSIFICATION*" --glob "!CLAUDE.md" --glob "!AUDIT*" --glob "!HALUGATE*" --glob "!PROJECT_AUDIT*" --glob "!KNOWN_ISSUES*" --glob "!docs/FAILURE_MODES*"

# 2. fitted to FRAP — должно быть 0
echo "=== fitted to FRAP check ==="
rg -c "fitted to FRAP" --glob "!node_modules/**" --glob "!FALSIFICATION*" --glob "!CLAUDE.md" --glob "!AUDIT*" --glob "!HALUGATE*"

# 3. R²=0.89 без disclaimer — проверить вручную
echo "=== R²=0.89 check ==="
rg "R²=0.89" --glob "manuscript/**" --glob "!node_modules/**"

# 4. AlphaGenome blind spot — должно быть 0 в manuscript
echo "=== AlphaGenome blind spot check ==="
rg "AlphaGenome blind spot" --glob "manuscript/**"

# 5. Publication Ready в README — должно быть 0
echo "=== Publication Ready check ==="
rg "Publication Ready" README.md

# 6. Build проходит
echo "=== Build check ==="
npm run build

# 7. Tests проходят
echo "=== Test check ==="
npm run test
```

### Commit:

```bash
git add -A
git commit -m "fix(integrity): remove all fabricated claims and add honest disclaimers

- Replace remaining Sabaté 2025 → Sabaté 2024 (bioRxiv) in scripts, config, preprints
- Replace 'fitted to FRAP data' → 'estimated from literature ranges' everywhere
- Add R²=0.89 disclaimer: 'self-consistency, experimental validation pending'
- Add AlphaGenome mock disclosure in manuscript (mock baseline, not real API)
- Fix README status: Publication Ready → In Development

Addresses FALSIFICATION_REPORT.md findings (60+ violations across 20+ files).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## КРИТЕРИЙ УСПЕХА

Все 5 verify-проверок дают 0 нарушений. Build и tests проходят.
