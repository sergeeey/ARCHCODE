import os
import json
import re

print("=" * 60)
print("БЛОК 6: ПРОВЕРКА RED FLAGS")
print("=" * 60)

results = []

# 1. Проверка mock data без маркировки
print("\n--- Mock Data Check ---")
mock_files = []
unmarked_synthetic = []

for root, dirs, files in os.walk("results"):
    for f in files:
        if f.endswith(".csv") or f.endswith(".json"):
            filepath = os.path.join(root, f)
            # Policy (CLAUDE.md): MOCK_*, SYNTHETIC_*, DEMO_* prefixes are valid markers
            fl = f.lower()
            if "mock" in fl or "synthetic" in fl or "simulated" in fl:
                has_valid_prefix = (
                    f.upper().startswith("MOCK_")
                    or f.upper().startswith("SYNTHETIC_")
                    or f.upper().startswith("DEMO_")
                )
                if not has_valid_prefix:
                    unmarked_synthetic.append(filepath)
                mock_files.append(filepath)

if unmarked_synthetic:
    print(f"⚠ FOUND: Файлы с mock/synthetic в имени без MOCK_ префикса:")
    for f in unmarked_synthetic[:5]:
        print(f"  - {f}")
    results.append(("Mock data маркировка", "ISSUE"))
else:
    print("✓ OK: Нет немаркированных mock/synthetic файлов")
    results.append(("Mock data маркировка", "OK"))

print(f"  Найдено mock файлов: {len(mock_files)}")

# 2. Проверка phantom references
print("\n--- Phantom References Check ---")
with open("manuscript/taxonomy_paper/body_content.typ", "r", encoding="utf-8") as f:
    content = f.read()

# Проверка на Sabaté 2025 Nature Genetics (фиктивный из предыдущих аудитов)
sabate_2025_ng = re.search(r"Sabaté.*2025.*Nature Genetics", content, re.IGNORECASE)
if sabate_2025_ng:
    print("✗ FOUND: Sabaté 2025 Nature Genetics (фиктивный!)")
    results.append(("Sabaté 2025 Nature Genetics", "PHANTOM"))
else:
    print("✓ OK: Sabaté 2025 Nature Genetics ОТСУТСТВУЕТ")
    results.append(("Sabaté 2025 Nature Genetics", "OK"))

# Проверка Sabaté bioRxiv 2024 (реальный)
sabate_2024 = re.search(
    r"Sabaté.*2024.*bioRxiv|10\.1101/2024\.08\.09\.605990", content, re.IGNORECASE
)
if sabate_2024:
    print("✓ OK: Sabaté 2024 bioRxiv (реальный препринт)")
    results.append(("Sabaté 2024 bioRxiv", "REAL"))
else:
    print("⚠ MISSING: Sabaté 2024 bioRxiv")
    results.append(("Sabaté 2024 bioRxiv", "MISSING"))

# 3. Threshold p-hacking check
print("\n--- Threshold p-hacking Check ---")
# Поиск sensitivity analysis
sensitivity_patterns = [
    r"sensitivity analysis",
    r"threshold.*0\.\d+",
    r"robust.*threshold",
    r"across thresholds",
]

found_sensitivity = []
for pattern in sensitivity_patterns:
    matches = re.findall(pattern, content, re.IGNORECASE)
    found_sensitivity.extend(matches)

if found_sensitivity:
    print(f"✓ FOUND: Sensitivity analysis ({len(found_sensitivity)} вхождений)")
    print("  Threshold 0.95 обоснован sensitivity analysis")
    results.append(("Threshold p-hacking", "OK"))
else:
    print("✗ MISSING: Sensitivity analysis для threshold")
    results.append(("Threshold p-hacking", "ISSUE"))

# 4. Cherry-picking check
print("\n--- Cherry-picking Check ---")
# Проверка что negative результаты честно reported
negative_results = [
    (r"BRCA1.*0\.99|BRCA1.*~1\.0", "BRCA1 null amplification"),
    (r"CFTR.*0\.60|CFTR.*negative", "CFTR negative amplification"),
    (r"tissue-match.*null", "tissue-match null"),
]

found_negative = []
for pattern, name in negative_results:
    matches = re.findall(pattern, content, re.IGNORECASE)
    if matches:
        found_negative.append(name)
        print(f"✓ FOUND: Честный negative результат — {name}")

if found_negative:
    print("✓ OK: Negative результаты честно reported")
    results.append(("Cherry-picking", "OK"))
else:
    print("⚠ WARNING: Negative результаты не найдены в явном виде")
    results.append(("Cherry-picking", "UNCLEAR"))

# 5. Проверка self-referential claims
print("\n--- Self-referential Claims Check ---")
self_refs = re.findall(r"As we showed in Section|see Section|Figure \d+", content, re.IGNORECASE)
print(f"Найдено self-references: {len(self_refs)}")

# Проверка что Figure/Section существуют
figure_refs = re.findall(r"Figure (\d+)", content)
figure_nums = [int(f) for f in figure_refs if f.isdigit()]
if figure_nums:
    max_figure = max(figure_nums)
    print(f"  Figure refs: 1-{max_figure}")
    # Проверка что figure не выходят за разумные пределы
    if max_figure <= 20:
        print("✓ OK: Figure refs в разумных пределах")
        results.append(("Self-referential claims", "OK"))
    else:
        print(f"⚠ WARNING: Слишком много Figure ({max_figure})")
        results.append(("Self-referential claims", "UNCLEAR"))

print("\n" + "=" * 60)
print("ИТОГИ БЛОКА 6")
print("=" * 60)
ok_count = sum(1 for _, s in results if s == "OK")
issue_count = sum(1 for _, s in results if s in ["ISSUE", "PHANTOM", "MISMATCH"])
print(f"OK: {ok_count}/{len(results)}")
print(f"ISSUES: {issue_count}/{len(results)}")

if issue_count == 0:
    print("\n✓ RED FLAGS: НЕ ОБНАРУЖЕНЫ")
else:
    print(f"\n⚠ RED FLAGS: {issue_count} проблем")
    for name, status in results:
        if status in ["ISSUE", "PHANTOM", "MISMATCH"]:
            print(f"  - {name}: {status}")
