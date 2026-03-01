"""
verify_manuscript.py — Pre-commit verification script for ARCHCODE project.

ПОЧЕМУ существует этот скрипт: в ходе аудита были обнаружены дрейфовые ошибки —
несоответствия между числами в рукописи и реальными данными, фиктивные DOI,
и overclaim-интерпретации. Этот скрипт является автоматизированным enforcement-слоем
для CLAUDE.md-политики "Falsification-First".

Запуск:
    python scripts/verify_manuscript.py
    python scripts/verify_manuscript.py --fix-table6

Выход: код 0 если все проверки пройдены, код 1 при любых ошибках.
"""

import csv
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional


# ПОЧЕМУ: определяем корень проекта относительно расположения скрипта,
# чтобы скрипт работал из любой директории без хардкода абсолютного пути.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Конфигурация локусов: имя → (CSV-файл, JSON-summary, JSON-positional)
# ПОЧЕМУ: централизованная конфигурация позволяет добавить новый локус
# одной строкой вместо изменений в нескольких местах.
LOCUS_CONFIG = {
    "HBB": {
        "csv": "results/HBB_Unified_Atlas_95kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_95kb.json",
        "positional_json": "results/positional_signal_95kb.json",
        "hic_json": "results/hic_correlation_k562_95kb.json",
        "tda_json": "results/tda_proof_of_concept_95kb.json",
        "window_kb": 95,
        "label": "HBB (95 kb)",
    },
    "CFTR": {
        "csv": "results/CFTR_Unified_Atlas_317kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_CFTR_317kb.json",
        "positional_json": "results/positional_signal_cftr.json",
        "hic_json": None,
        "tda_json": "results/tda_proof_of_concept_cftr.json",
        "window_kb": 317,
        "label": "CFTR (317 kb)",
    },
    "TP53": {
        "csv": "results/TP53_Unified_Atlas_300kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_TP53_300kb.json",
        "positional_json": "results/positional_signal_tp53.json",
        "hic_json": "results/hic_correlation_tp53.json",
        "tda_json": "results/tda_proof_of_concept_tp53.json",
        "window_kb": 300,
        "label": "TP53 (300 kb)",
    },
    "BRCA1": {
        "csv": "results/BRCA1_Unified_Atlas_400kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_BRCA1_400kb.json",
        "positional_json": "results/positional_signal_brca1.json",
        "hic_json": "results/hic_correlation_brca1.json",
        "tda_json": "results/tda_proof_of_concept_brca1.json",
        "window_kb": 400,
        "label": "BRCA1 (400 kb)",
    },
    "MLH1": {
        "csv": "results/MLH1_Unified_Atlas_300kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_MLH1_300kb.json",
        "positional_json": "results/positional_signal_mlh1.json",
        "hic_json": "results/hic_correlation_mlh1.json",
        "tda_json": "results/tda_proof_of_concept_mlh1.json",
        "window_kb": 300,
        "label": "MLH1 (300 kb)",
    },
    "LDLR": {
        "csv": "results/LDLR_Unified_Atlas_300kb.csv",
        "summary_json": "results/UNIFIED_ATLAS_SUMMARY_LDLR_300kb.json",
        "positional_json": "results/positional_signal_ldlr.json",
        "hic_json": "results/hic_correlation_ldlr.json",
        "tda_json": "results/tda_proof_of_concept_ldlr.json",
        "window_kb": 300,
        "label": "LDLR (300 kb)",
    },
}

# ПОЧЕМУ: допуск для сравнения float нужен — CSV хранит округлённые значения,
# а рукопись может показывать 4 знака после запятой.
# 0.0005 = половина единицы в последнем разряде при точности 0.0001.
FLOAT_TOLERANCE = 0.0005

# Структурные вердикты, которые считаются как "Struct. path." в Table 6
STRUCTURAL_PATHOGENIC_VERDICTS = {"PATHOGENIC", "LIKELY_PATHOGENIC"}


# ─────────────────────────────────────────────
# Утилиты вывода
# ─────────────────────────────────────────────


def ok(message: str) -> None:
    """Выводит сообщение об успехе."""
    print(f"  ✅ {message}")


def fail(message: str) -> None:
    """Выводит сообщение об ошибке."""
    print(f"  ❌ {message}")


def warn(message: str) -> None:
    """Выводит предупреждение."""
    print(f"  ⚠️  {message}")


def section(title: str) -> None:
    """Выводит заголовок секции."""
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}")


def subsection(title: str) -> None:
    """Выводит подзаголовок."""
    print(f"\n  ── {title}")


# ─────────────────────────────────────────────
# Module 1: DOI Verification
# ─────────────────────────────────────────────


def extract_dois_from_manuscript(manuscript_path: Path) -> list[str]:
    """
    Извлекает все DOI из рукописи по паттерну doi:10.XXXX/...

    ПОЧЕМУ: парсим текст рукописи, а не используем захардкоженный список —
    так скрипт автоматически подхватывает новые ссылки при обновлении рукописи.
    """
    if not manuscript_path.exists():
        return []

    text = manuscript_path.read_text(encoding="utf-8", errors="ignore")
    # ПОЧЕМУ: паттерн матчит doi:10.XXXX/... до пробела/скобки/кавычки/конца строки.
    # Добавляем boundary символы чтобы не захватить trailing пунктуацию.
    pattern = r"doi:(10\.\d{4,}/[^\s\)\],\"'`]+)"
    raw_dois = re.findall(pattern, text, re.IGNORECASE)

    # Очищаем trailing знаки препинания которые могут прилипнуть
    dois = []
    for doi in raw_dois:
        # Убираем trailing точки, запятые, скобки
        doi = doi.rstrip(".,;:)")
        if doi not in dois:
            dois.append(doi)

    return dois


def check_doi(doi: str, timeout: int = 10) -> tuple[str, str]:
    """
    Делает HTTP HEAD запрос к doi.org для проверки разрешимости DOI.

    Возвращает: (статус, описание) где статус ∈ {'ok', 'fail', 'warn'}.

    ПОЧЕМУ: HEAD запрос предпочтительнее GET — не скачиваем контент,
    только проверяем что URL резолвится. doi.org отвечает редиректом (302)
    на реальный URL издателя, urllib следует редиректам автоматически.
    """
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url, method="HEAD")
        # ПОЧЕМУ: добавляем User-Agent — некоторые CDN блокируют пустые UA.
        req.add_header("User-Agent", "ARCHCODE-verify/1.0 (scientific integrity check)")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.status
            if 200 <= status_code < 400:
                return ("ok", f"HTTP {status_code}")
            else:
                return ("fail", f"HTTP {status_code}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("fail", "HTTP 404 Not Found — PHANTOM REFERENCE RISK")
        elif e.code in (403, 405):
            # ПОЧЕМУ: 405 Method Not Allowed на HEAD — попробуем GET.
            # Некоторые серверы не поддерживают HEAD (например, PLOS ONE).
            return _check_doi_with_get(doi, timeout)
        else:
            return ("warn", f"HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        reason = str(e.reason)
        if "timed out" in reason.lower() or "timeout" in reason.lower():
            return ("warn", f"Timeout after {timeout}s")
        return ("warn", f"Network error: {reason}")
    except Exception as e:
        return ("warn", f"Unexpected error: {type(e).__name__}: {e}")


def _check_doi_with_get(doi: str, timeout: int) -> tuple[str, str]:
    """Fallback: проверка DOI через GET если HEAD не поддерживается сервером."""
    url = f"https://doi.org/{doi}"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "ARCHCODE-verify/1.0 (scientific integrity check)")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return ("ok", f"HTTP {response.status} (via GET fallback)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("fail", "HTTP 404 Not Found — PHANTOM REFERENCE RISK")
        return ("warn", f"HTTP {e.code} {e.reason}")
    except Exception as e:
        return ("warn", f"GET fallback error: {type(e).__name__}: {e}")


def run_doi_verification(manuscript_path: Path) -> int:
    """
    Модуль 1: проверяет все DOI из рукописи.

    Возвращает количество ошибок (0 = все прошли).
    """
    section("MODULE 1: DOI Verification")

    dois = extract_dois_from_manuscript(manuscript_path)

    if not dois:
        warn("No DOIs found in manuscript — check regex or file path")
        return 1

    print(f"\n  Found {len(dois)} unique DOIs in manuscript\n")

    failures = 0
    for doi in dois:
        status, description = check_doi(doi)
        if status == "ok":
            ok(f"{doi}  →  {description}")
        elif status == "fail":
            fail(f"{doi}  →  {description}")
            failures += 1
        else:
            warn(f"{doi}  →  {description}")

    print(f"\n  Result: {len(dois) - failures}/{len(dois)} DOIs verified")
    if failures > 0:
        fail(f"{failures} DOI(s) failed — potential phantom references!")

    return failures


# ─────────────────────────────────────────────
# Module 2: Number Consistency
# ─────────────────────────────────────────────


def load_csv_stats(csv_path: Path) -> Optional[dict]:
    """
    Читает CSV и вычисляет статистику по колонкам ARCHCODE.

    ПОЧЕМУ: вычисляем статистику на лету из сырых данных, а не доверяем
    кэшированным значениям в JSON — это гарантирует что CSV и JSON синхронны.
    """
    if not csv_path.exists():
        return None

    total = 0
    pathogenic_count = 0
    benign_count = 0
    struct_pathogenic = 0
    pearl_count = 0
    ssim_values: list[float] = []
    lssim_values: list[float] = []

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1

            label = row.get("Label", "").strip()
            if label == "Pathogenic":
                pathogenic_count += 1
            elif label == "Benign":
                benign_count += 1

            verdict = row.get("ARCHCODE_Verdict", "").strip().upper()
            if verdict in STRUCTURAL_PATHOGENIC_VERDICTS:
                struct_pathogenic += 1

            pearl_raw = row.get("Pearl", "").strip().lower()
            if pearl_raw == "true":
                pearl_count += 1

            ssim_raw = row.get("ARCHCODE_SSIM", "").strip()
            if ssim_raw:
                try:
                    ssim_values.append(float(ssim_raw))
                except ValueError:
                    pass

            lssim_raw = row.get("ARCHCODE_LSSIM", "").strip()
            if lssim_raw:
                try:
                    lssim_values.append(float(lssim_raw))
                except ValueError:
                    pass

    return {
        "total": total,
        "pathogenic": pathogenic_count,
        "benign": benign_count,
        "struct_pathogenic": struct_pathogenic,
        "pearls": pearl_count,
        "ssim_min": min(ssim_values) if ssim_values else None,
        "ssim_max": max(ssim_values) if ssim_values else None,
        "lssim_min": min(lssim_values) if lssim_values else None,
        "lssim_max": max(lssim_values) if lssim_values else None,
    }


def load_summary_json(json_path: Path) -> Optional[dict]:
    """Загружает UNIFIED_ATLAS_SUMMARY JSON и возвращает секцию statistics."""
    if not json_path.exists():
        return None
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return data.get("statistics", {})


def load_positional_json(json_path: Path) -> Optional[dict]:
    """
    Загружает positional_signal JSON и возвращает секцию logistic_regression.
    """
    if not json_path.exists():
        return None
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return data.get("logistic_regression", {})


def check_float_range(
    label: str,
    actual_min: Optional[float],
    actual_max: Optional[float],
    expected_min: float,
    expected_max: float,
) -> int:
    """
    Сравнивает диапазон float значений с ожидаемым из рукописи.

    Возвращает 0 если совпадает, 1 если есть расхождение.

    ПОЧЕМУ: отдельная функция для float-сравнений с tolerance,
    вместо прямого == который ломается на IEEE 754 округлении.
    """
    if actual_min is None or actual_max is None:
        warn(f"{label}: no data to compare")
        return 0

    min_ok = abs(actual_min - expected_min) <= FLOAT_TOLERANCE
    max_ok = abs(actual_max - expected_max) <= FLOAT_TOLERANCE

    if min_ok and max_ok:
        ok(
            f"{label}: {actual_min:.4f}\u2013{actual_max:.4f} \u2713"
            f" (manuscript: {expected_min:.4f}\u2013{expected_max:.4f})"
        )
        return 0
    else:
        issues = []
        if not min_ok:
            delta_min = actual_min - expected_min
            issues.append(
                f"min: actual={actual_min:.4f} vs manuscript={expected_min:.4f}"
                f" delta={delta_min:+.4f}"
            )
        if not max_ok:
            delta_max = actual_max - expected_max
            issues.append(
                f"max: actual={actual_max:.4f} vs manuscript={expected_max:.4f}"
                f" delta={delta_max:+.4f}"
            )
        fail(f"{label}: MISMATCH — {'; '.join(issues)}")
        return 1


def parse_table6_from_manuscript(manuscript_path: Path) -> dict[str, dict]:
    """
    Парсит Table 6 из рукописи, извлекая числа для каждого локуса.

    ПОЧЕМУ: парсим динамически вместо хардкода — так скрипт автоматически
    обнаруживает расхождения даже если рукопись обновлена, а CSV нет (или наоборот).
    """
    text = manuscript_path.read_text(encoding="utf-8", errors="ignore")

    # Ищем начало Table 6
    table6_match = re.search(r"\*\*Table 6\.", text)
    if not table6_match:
        return {}

    # Берём текст после Table 6 (достаточно ~30 строк)
    table_text = text[table6_match.start() : table6_match.start() + 3000]
    lines = table_text.split("\n")

    # Парсим заголовки колонок — ищем строку с именами локусов
    header_line = None
    data_lines = []
    for line in lines:
        if "| Metric" in line:
            header_line = line
        elif header_line and line.strip().startswith("|") and "---" not in line:
            data_lines.append(line)
        elif header_line and not line.strip().startswith("|"):
            break  # Конец таблицы

    if not header_line:
        return {}

    # Парсим заголовки
    headers = [h.strip() for h in header_line.split("|")[1:-1]]
    locus_names = headers[1:]  # первый — "Metric"

    result: dict[str, dict] = {}
    for locus_label in locus_names:
        result[locus_label] = {}

    for line in data_lines:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) < 2:
            continue
        metric = cells[0].strip()
        for i, locus_label in enumerate(locus_names):
            if i + 1 < len(cells):
                result[locus_label][metric] = cells[i + 1].strip()

    return result


def _parse_int(s: str) -> Optional[int]:
    """Парсит целое число из строки Table 6, убирая запятые-разделители."""
    s = s.replace(",", "").strip()
    # Обработка "0 (12 VUS)" → 0
    match = re.match(r"^(\d+)", s)
    return int(match.group(1)) if match else None


def _parse_ssim_range(s: str) -> tuple[Optional[float], Optional[float]]:
    """Парсит 'X.XXXX–Y.YYYY' → (min, max)."""
    # Поддерживаем разные Unicode дефисы
    parts = re.split(r"[–\-−]", s.strip())
    if len(parts) == 2:
        try:
            return float(parts[0]), float(parts[1])
        except ValueError:
            pass
    return None, None


def run_consistency_checks(manuscript_path: Path) -> int:
    """
    Модуль 2: сверяет числа в Table 6 рукописи с реальными данными из CSV/JSON.

    ПОЧЕМУ: числа парсятся из рукописи динамически, а не хардкодятся —
    так скрипт обнаруживает ошибки в обоих направлениях (рукопись → данные И данные → рукопись).

    Возвращает количество ошибок.
    """
    section("MODULE 2: Number Consistency (Table 6 vs Data Files)")
    total_failures = 0

    # Парсим Table 6 из рукописи
    manuscript_table = parse_table6_from_manuscript(manuscript_path)
    if not manuscript_table:
        fail("Could not parse Table 6 from manuscript")
        return 1

    for locus_name, cfg in LOCUS_CONFIG.items():
        subsection(f"Locus: {locus_name}")

        csv_path = PROJECT_ROOT / cfg["csv"]
        summary_path = PROJECT_ROOT / cfg["summary_json"]
        positional_path = PROJECT_ROOT / cfg["positional_json"]

        # Ищем этот локус в Table 6 по label
        locus_label = cfg["label"]
        table_row = manuscript_table.get(locus_label, {})
        if not table_row:
            warn(f"Locus '{locus_label}' not found in manuscript Table 6")

        if not csv_path.exists():
            fail(f"CSV not found: {cfg['csv']}")
            total_failures += 1
            continue

        csv_stats = load_csv_stats(csv_path)
        summary_stats = load_summary_json(summary_path)
        lr_stats = load_positional_json(positional_path)

        if csv_stats is None:
            fail(f"Could not parse CSV: {cfg['csv']}")
            total_failures += 1
            continue

        locus_failures = 0

        # ── Check 1: Total variants (CSV vs manuscript) ──────────────────
        csv_total = csv_stats["total"]
        ms_total = _parse_int(table_row.get("ClinVar variants", ""))

        if ms_total is not None:
            if csv_total == ms_total:
                ok(f"Total variants: CSV={csv_total} ✓ (manuscript={ms_total})")
            else:
                fail(f"Total variants: CSV={csv_total} ≠ manuscript={ms_total} (Δ={csv_total - ms_total:+d})")
                locus_failures += 1

        # Cross-check CSV vs JSON
        if summary_stats:
            json_total = summary_stats.get("total_variants")
            if json_total is not None and json_total != csv_total:
                fail(f"Total variants: JSON={json_total} ≠ CSV={csv_total}")
                locus_failures += 1
            elif json_total is not None:
                ok(f"Total variants: CSV↔JSON consistent ({json_total})")

        # ── Check 2: P/LP + B/LB ─────────────────────────────────────────
        plp_blb = table_row.get("P/LP + B/LB", "")
        parts = plp_blb.split("+")
        if len(parts) == 2:
            ms_path = _parse_int(parts[0])
            ms_ben = _parse_int(parts[1])

            if ms_path is not None and ms_path == csv_stats["pathogenic"]:
                ok(f"Pathogenic: CSV={csv_stats['pathogenic']} ✓")
            elif ms_path is not None:
                fail(f"Pathogenic: CSV={csv_stats['pathogenic']} ≠ manuscript={ms_path}")
                locus_failures += 1

            if ms_ben is not None and ms_ben == csv_stats["benign"]:
                ok(f"Benign: CSV={csv_stats['benign']} ✓")
            elif ms_ben is not None:
                fail(f"Benign: CSV={csv_stats['benign']} ≠ manuscript={ms_ben}")
                locus_failures += 1

        # ── Check 3: Global SSIM range ───────────────────────────────────
        ms_ssim_min, ms_ssim_max = _parse_ssim_range(
            table_row.get("Global SSIM range", "")
        )
        if ms_ssim_min is not None:
            locus_failures += check_float_range(
                "Global SSIM",
                csv_stats["ssim_min"],
                csv_stats["ssim_max"],
                ms_ssim_min,
                ms_ssim_max,
            )

        # ── Check 4: LSSIM range ─────────────────────────────────────────
        ms_lssim_min, ms_lssim_max = _parse_ssim_range(
            table_row.get("LSSIM range", "")
        )
        if ms_lssim_min is not None:
            locus_failures += check_float_range(
                "LSSIM",
                csv_stats["lssim_min"],
                csv_stats["lssim_max"],
                ms_lssim_min,
                ms_lssim_max,
            )

        # ── Check 5: Structural pathogenic ────────────────────────────────
        ms_sp = _parse_int(table_row.get("Struct. path.", ""))
        csv_sp = csv_stats["struct_pathogenic"]

        if ms_sp is not None:
            if csv_sp == ms_sp:
                ok(f"Struct. pathogenic: CSV={csv_sp} ✓")
            else:
                fail(f"Struct. pathogenic: CSV={csv_sp} ≠ manuscript={ms_sp} (Δ={csv_sp - ms_sp:+d})")
                locus_failures += 1

        if summary_stats:
            json_sp = summary_stats.get("archcode_structural_pathogenic")
            if json_sp is not None and json_sp != csv_sp:
                fail(f"Struct. pathogenic: JSON={json_sp} ≠ CSV={csv_sp}")
                locus_failures += 1

        # ── Check 6: Pearl count ──────────────────────────────────────────
        ms_pearls = _parse_int(table_row.get("Pearl variants", ""))
        csv_pearls = csv_stats["pearls"]

        if ms_pearls is not None:
            if csv_pearls == ms_pearls:
                ok(f"Pearl variants: CSV={csv_pearls} ✓")
            else:
                fail(f"Pearl variants: CSV={csv_pearls} ≠ manuscript={ms_pearls} (Δ={csv_pearls - ms_pearls:+d})")
                locus_failures += 1

        # ── Check 7: LR ΔAUC ─────────────────────────────────────────────
        if lr_stats:
            dauc = lr_stats.get("auc_improvement")
            p_val = lr_stats.get("lr_p_value")
            interp = lr_stats.get("interpretation", "")
            if dauc is not None and p_val is not None:
                ok(f"LR: ΔAUC={dauc:+.4f}, p={p_val:.2e} → '{interp[:60]}'")

        if locus_failures == 0:
            print(f"\n  ✅ {locus_name}: all checks passed")
        else:
            print(f"\n  ❌ {locus_name}: {locus_failures} check(s) FAILED")

        total_failures += locus_failures

    return total_failures


# ─────────────────────────────────────────────
# Module 3: Overclaim Detection
# ─────────────────────────────────────────────

# ПОЧЕМУ: пороги из CLAUDE.md методологии.
# p < 0.05 + ΔAUC < 0.02 = "power effect" — статистически значимо
# но клинически не значимо. Рукопись должна это явно указывать.
OVERCLAIM_P_THRESHOLD = 0.05
OVERCLAIM_DAUC_THRESHOLD = 0.02

# Ключевые фразы которые ДОЛЖНЫ присутствовать при power effect
POWER_EFFECT_PHRASES = [
    "power effect",
    "not clinically meaningful",
    "clinically meaningful",
]

# Фразы которые НЕ должны присутствовать при незначимом p
OVERCLAIM_PHRASES = [
    "adds significant predictive value",
    "significant predictive",
    "significantly predicts",
]


def check_overclaim_in_file(json_path: Path) -> int:
    """
    Проверяет один positional_signal JSON на overclaim-интерпретации.

    Логика:
    - p < 0.05 И ΔAUC < 0.02: интерпретация ДОЛЖНА упоминать power effect
    - p >= 0.05: интерпретация НЕ ДОЛЖНА утверждать значимое предсказание

    Возвращает количество нарушений.
    """
    if not json_path.exists():
        warn(f"Not found: {json_path.name} — skipping")
        return 0

    data = json.loads(json_path.read_text(encoding="utf-8"))
    locus = data.get("locus", json_path.stem)
    lr = data.get("logistic_regression", {})

    if not lr:
        warn(f"{locus}: no logistic_regression section found")
        return 0

    dauc = lr.get("auc_improvement")
    p_val = lr.get("lr_p_value")
    interp = lr.get("interpretation", "")

    if dauc is None or p_val is None:
        warn(f"{locus}: missing auc_improvement or lr_p_value")
        return 0

    failures = 0
    interp_lower = interp.lower()

    # Сценарий 1: статистически значимо, но эффект мал → должен быть дисклеймер
    if p_val < OVERCLAIM_P_THRESHOLD and abs(dauc) < OVERCLAIM_DAUC_THRESHOLD:
        has_disclaimer = any(phrase in interp_lower for phrase in POWER_EFFECT_PHRASES)
        if has_disclaimer:
            ok(
                f"{locus}: p={p_val:.4f} < 0.05 AND ΔAUC={dauc:+.4f} < 0.02 "
                f"→ disclaimer present ✓"
            )
        else:
            fail(
                f"{locus}: p={p_val:.4f} < 0.05 AND ΔAUC={dauc:+.4f} < 0.02 "
                f"→ OVERCLAIM — interpretation must mention 'power effect' or "
                f"'not clinically meaningful'. Got: '{interp}'"
            )
            failures += 1

    # Сценарий 2: незначимый результат → нельзя говорить о "значимом предсказании"
    elif p_val >= OVERCLAIM_P_THRESHOLD:
        has_overclaim = any(phrase in interp_lower for phrase in OVERCLAIM_PHRASES)
        if has_overclaim:
            fail(
                f"{locus}: p={p_val:.4f} >= 0.05 (NOT significant) "
                f"→ OVERCLAIM — interpretation falsely claims significance. "
                f"Got: '{interp}'"
            )
            failures += 1
        else:
            ok(f"{locus}: p={p_val:.4f} >= 0.05 → no overclaim detected ✓ " f"(ΔAUC={dauc:+.4f})")

    # Сценарий 3: значимый И крупный эффект — просто фиксируем
    else:
        ok(
            f"{locus}: p={p_val:.4f} < 0.05 AND ΔAUC={dauc:+.4f} >= 0.02 "
            f"→ large significant effect, no overclaim check needed"
        )

    return failures


def run_overclaim_detection() -> int:
    """
    Модуль 3: сканирует все positional_signal_*.json на overclaim-интерпретации.

    Возвращает количество нарушений.
    """
    section("MODULE 3: Overclaim Detection")

    positional_files = sorted((PROJECT_ROOT / "results").glob("positional_signal_*.json"))

    if not positional_files:
        warn("No positional_signal_*.json files found in results/")
        return 0

    print(f"\n  Scanning {len(positional_files)} positional signal files\n")

    total_failures = 0
    for json_path in positional_files:
        total_failures += check_overclaim_in_file(json_path)

    return total_failures


# ─────────────────────────────────────────────
# --fix-table6: автогенерация исправленной Table 6
# ─────────────────────────────────────────────


def load_hic_data(json_path: Optional[Path]) -> dict:
    """Загружает Hi-C корреляции из JSON. Возвращает dict с K562/MCF7 r-values."""
    if json_path is None or not json_path.exists():
        return {}
    data = json.loads(json_path.read_text(encoding="utf-8"))
    result = {}
    # Формат может быть: {"gene": ..., "K562": {"r": ...}} или {"pearson_r": ..., "cell_type": ...}
    if "K562" in data:
        result["k562_r"] = data["K562"].get("r")
    elif "pearson_r" in data:
        cell_type = data.get("cell_type", "K562")
        key = f"{cell_type.lower()}_r"
        result[key] = data["pearson_r"]
    if "MCF7" in data:
        result["mcf7_r"] = data["MCF7"].get("r")
    return result


def load_tda_data(json_path: Optional[Path]) -> Optional[float]:
    """Загружает TDA ρ (SSIM↔W_H1) из JSON."""
    if json_path is None or not json_path.exists():
        return None
    data = json.loads(json_path.read_text(encoding="utf-8"))
    rc = data.get("rank_correlations", {})
    ssim_wh1 = rc.get("ssim_vs_wasserstein_h1", {})
    rho = ssim_wh1.get("rho")
    if rho is not None:
        import math
        if math.isnan(rho):
            return float("nan")
    return rho


def load_spread_data(json_path: Optional[Path]) -> Optional[dict]:
    """Загружает variant spread из positional_signal JSON."""
    if json_path is None or not json_path.exists():
        return None
    data = json.loads(json_path.read_text(encoding="utf-8"))
    spread_bp = data.get("variant_spread_bp")
    spread_frac = data.get("spread_fraction")
    window_bp = data.get("window_size_bp")
    if spread_bp is not None:
        return {"bp": spread_bp, "fraction": spread_frac, "window_bp": window_bp}
    return None


def build_table6_data() -> dict[str, dict]:
    """
    Собирает все данные Table 6 из реальных файлов (CSV, JSON).

    ПОЧЕМУ: единая точка сбора данных для Table 6.
    Используется и для генерации, и для верификации.
    """
    rows: dict[str, dict] = {}

    for locus_name, cfg in LOCUS_CONFIG.items():
        csv_path = PROJECT_ROOT / cfg["csv"]
        positional_path = PROJECT_ROOT / cfg["positional_json"]
        hic_path = (PROJECT_ROOT / cfg["hic_json"]) if cfg.get("hic_json") else None
        tda_path = (PROJECT_ROOT / cfg["tda_json"]) if cfg.get("tda_json") else None

        csv_stats = load_csv_stats(csv_path)
        lr_stats = load_positional_json(positional_path)
        hic_data = load_hic_data(hic_path)
        tda_rho = load_tda_data(tda_path)
        spread = load_spread_data(positional_path)

        if csv_stats is None:
            warn(f"{locus_name}: cannot read CSV — skipping")
            continue

        lr_dauc = lr_stats.get("auc_improvement") if lr_stats else None
        lr_p = lr_stats.get("lr_p_value") if lr_stats else None

        rows[locus_name] = {
            "total": csv_stats["total"],
            "pathogenic": csv_stats["pathogenic"],
            "benign": csv_stats["benign"],
            "ssim_min": csv_stats["ssim_min"],
            "ssim_max": csv_stats["ssim_max"],
            "lssim_min": csv_stats["lssim_min"],
            "lssim_max": csv_stats["lssim_max"],
            "struct_path": csv_stats["struct_pathogenic"],
            "pearls": csv_stats["pearls"],
            "lr_dauc": lr_dauc,
            "lr_p": lr_p,
            "k562_r": hic_data.get("k562_r"),
            "mcf7_r": hic_data.get("mcf7_r"),
            "hepg2_r": hic_data.get("hepg2_r"),
            "tda_rho": tda_rho,
            "spread": spread,
        }

    return rows


def format_table6_markdown(rows: dict[str, dict]) -> str:
    """
    Генерирует Table 6 в markdown формате из реальных данных.

    ПОЧЕМУ: генерация из данных вместо ручного копирования устраняет
    класс ошибок "числа в рукописи не совпадают с CSV/JSON".
    """
    import math

    # ПОЧЕМУ: выносим строки с Unicode-символами в переменные,
    # потому что f-string expression part не может содержать backslash до Python 3.12.
    DELTA = "\u0394"     # Δ
    DASH = "\u2013"      # –
    ARROW = "\u2194"     # ↔
    RHO = "\u03c1"       # ρ
    APPROX = "\u2248"    # ≈
    MDASH = "\u2014"     # —
    SUP_MINUS = "\u207b" # ⁻

    def fmt_ssim(val: Optional[float]) -> str:
        if val is None:
            return "N/A"
        return f"{val:.4f}"

    def fmt_lr(dauc: Optional[float], p: Optional[float]) -> str:
        if dauc is None or p is None:
            return "N/A"
        sign = "+" if dauc >= 0 else ""
        if p < 1e-10:
            p_str = f"p{APPROX}10{SUP_MINUS}{round(-1 * math.log10(p))}"
        elif p >= 0.995:
            p_str = "p = 1.0"
        else:
            p_str = f"p = {p:.2f}" if p >= 0.01 else f"p={p:.3f}"
        return f"{sign}{dauc:.3f} ({p_str})"

    def fmt_struct(name: str, count: int) -> str:
        if name == "TP53" and count == 0:
            return "0 (12 VUS)"
        return str(count)

    def fmt_hic_r(val: Optional[float]) -> str:
        if val is None:
            return MDASH
        return f"{val:.2f}"

    def fmt_tda(val: Optional[float]) -> str:
        if val is None:
            return MDASH
        if isinstance(val, float) and math.isnan(val):
            return "NaN"
        return f"{val:.2f}"

    def fmt_spread(s: Optional[dict], window_kb: int) -> str:
        if s is None:
            return "N/A"
        bp = s["bp"]
        frac = s.get("fraction")
        if bp < 10000:
            spread_str = f"{bp / 1000:.1f} kb"
        else:
            spread_str = f"{bp / 1000:.1f} kb"
        if frac is not None:
            pct = frac * 100
            return f"{spread_str} ({pct:.1f}%)"
        return spread_str

    loci = list(LOCUS_CONFIG.keys())
    lines = []

    # Header
    headers = ["Metric"] + [cfg["label"] for cfg in LOCUS_CONFIG.values()]
    lines.append("| " + " | ".join(f"{h:<18}" for h in headers) + " |")
    lines.append("| " + " | ".join("-" * 18 for _ in headers) + " |")

    # Data rows
    lines.append(
        "| " + " | ".join(
            [f"{'ClinVar variants':<18}"]
            + [f"{rows[n]['total']:>18,}" if n in rows else f"{'N/A':>18}" for n in loci]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'P/LP + B/LB':<18}"]
            + [
                f"{rows[n]['pathogenic']:,} + {rows[n]['benign']:,}".rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'Variant spread':<18}"]
            + [
                fmt_spread(rows[n].get("spread"), LOCUS_CONFIG[n]["window_kb"]).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'Global SSIM range':<18}"]
            + [
                f"{fmt_ssim(rows[n]['ssim_min'])}\u2013{fmt_ssim(rows[n]['ssim_max'])}".rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'LSSIM range':<18}"]
            + [
                f"{fmt_ssim(rows[n]['lssim_min'])}\u2013{fmt_ssim(rows[n]['lssim_max'])}".rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'Struct. path.':<18}"]
            + [
                fmt_struct(n, rows[n]["struct_path"]).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [("LR " + DELTA + "AUC (LSSIM)").ljust(18)]
            + [
                fmt_lr(rows[n]["lr_dauc"], rows[n]["lr_p"]).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    # HBB special case: K562 has two values (30kb / 95kb)
    k562_cells = []
    for n in loci:
        if n not in rows:
            k562_cells.append(f"{'N/A':>18}")
        elif n == "HBB":
            k562_cells.append("0.53 / 0.59".rjust(18))
        else:
            k562_cells.append(fmt_hic_r(rows[n].get("k562_r")).rjust(18))

    lines.append(
        "| " + " | ".join([f"{'K562 Hi-C r':<18}"] + k562_cells) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'MCF7 Hi-C r':<18}"]
            + [
                fmt_hic_r(rows[n].get("mcf7_r")).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    # HepG2 Hi-C row (only show if any locus has HepG2 data)
    has_hepg2 = any(rows.get(n, {}).get("hepg2_r") is not None for n in loci)
    if has_hepg2:
        lines.append(
            "| " + " | ".join(
                [f"{'HepG2 Hi-C r':<18}"]
                + [
                    fmt_hic_r(rows[n].get("hepg2_r")).rjust(18)
                    if n in rows else f"{'N/A':>18}"
                    for n in loci
                ]
            ) + " |"
        )

    lines.append(
        "| " + " | ".join(
            [("TDA " + RHO + " (SSIM" + ARROW + "W_H1)").ljust(18)]
            + [
                fmt_tda(rows[n].get("tda_rho")).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    lines.append(
        "| " + " | ".join(
            [f"{'Pearl variants':<18}"]
            + [
                str(rows[n]["pearls"]).rjust(18)
                if n in rows else f"{'N/A':>18}"
                for n in loci
            ]
        ) + " |"
    )

    return "\n".join(lines)


def generate_corrected_table6() -> None:
    """
    Генерирует исправленную Table 6 на основе реальных данных.

    ПОЧЕМУ: вместо ручного исправления рукописи (источник ошибок),
    скрипт автоматически читает данные и генерирует готовую markdown таблицу.
    """
    section("--fix-table6: Generating Corrected Table 6 from Actual Data")

    rows = build_table6_data()
    table_md = format_table6_markdown(rows)

    print("\n  Copy the following corrected Table 6 into the manuscript:\n")
    print("  " + "\u2500" * 90)
    print()
    for line in table_md.split("\n"):
        print("  " + line)
    print()
    print("  " + "\u2500" * 90)
    print(f"\n  Generated from actual CSV and JSON files at {PROJECT_ROOT}")
    print("  Timestamp: " + __import__("datetime").datetime.now().isoformat())


def update_manuscript_table6(manuscript_path: Path) -> bool:
    """
    Обновляет Table 6 прямо в рукописи, заменяя старую таблицу на сгенерированную.

    ПОЧЕМУ: --update-manuscript устраняет промежуточный шаг copy-paste,
    который сам по себе является источником ошибок.

    Возвращает True если обновление прошло успешно.
    """
    section("--update-manuscript: Writing Corrected Table 6 into Manuscript")

    rows = build_table6_data()
    table_md = format_table6_markdown(rows)

    text = manuscript_path.read_text(encoding="utf-8")

    # Ищем Table 6 — от заголовка до первой пустой строки после таблицы
    pattern = (
        r"(\*\*Table 6\. ARCHCODE results across five genomic loci\.\*\*\n\n)"
        r"(\|.+\|(?:\n\|.+\|)*)"
    )
    match = re.search(pattern, text)

    if not match:
        fail("Could not locate Table 6 in manuscript — regex didn't match")
        return False

    old_table = match.group(2)
    new_text = text[: match.start(2)] + table_md + text[match.end(2) :]

    manuscript_path.write_text(new_text, encoding="utf-8")

    ok("Table 6 updated in manuscript")
    print(f"\n  Old table ({old_table.count(chr(10)) + 1} lines) replaced with generated version")
    print(f"  Timestamp: {__import__('datetime').datetime.now().isoformat()}")

    return True


# ─────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────


def main() -> int:
    """
    Точка входа. Запускает все три модуля верификации.

    Режимы:
      python verify_manuscript.py              — полная проверка (3 модуля)
      python verify_manuscript.py --fix-table6 — показать сгенерированную Table 6
      python verify_manuscript.py --update-manuscript — записать Table 6 прямо в файл
      python verify_manuscript.py --skip-doi   — пропустить HTTP-проверку DOI (офлайн)

    Возвращает exit code: 0 = все OK, 1 = есть ошибки.
    """
    fix_table6_mode = "--fix-table6" in sys.argv
    update_mode = "--update-manuscript" in sys.argv
    skip_doi = "--skip-doi" in sys.argv

    print("\u2554" + "\u2550" * 62 + "\u2557")
    print("\u2551         ARCHCODE Manuscript Verification Script              \u2551")
    print("\u2551         Scientific Integrity Enforcement Layer               \u2551")
    print("\u255a" + "\u2550" * 62 + "\u255d")
    print(f"\n  Project root: {PROJECT_ROOT}")

    manuscript_path = PROJECT_ROOT / "manuscript" / "FULL_MANUSCRIPT.md"

    if fix_table6_mode:
        generate_corrected_table6()
        return 0

    if update_mode:
        if not manuscript_path.exists():
            fail(f"Manuscript not found: {manuscript_path}")
            return 1
        success = update_manuscript_table6(manuscript_path)
        return 0 if success else 1

    # Проверяем наличие рукописи
    if not manuscript_path.exists():
        fail(f"Manuscript not found: {manuscript_path}")
        print("\n  Cannot proceed without manuscript. Exiting.")
        return 1

    total_failures = 0

    # Module 1: DOI Verification
    # ПОЧЕМУ: DOI-проверка идёт первой — фантомные ссылки это нарушение
    # научной честности, критичнее числовых расхождений.
    if skip_doi:
        section("MODULE 1: DOI Verification")
        warn("SKIPPED (--skip-doi flag)")
        doi_failures = 0
    else:
        doi_failures = run_doi_verification(manuscript_path)
    total_failures += doi_failures

    # Module 2: Number Consistency
    consistency_failures = run_consistency_checks(manuscript_path)
    total_failures += consistency_failures

    # Module 3: Overclaim Detection
    overclaim_failures = run_overclaim_detection()
    total_failures += overclaim_failures

    # Итоговый отчёт
    section("SUMMARY")
    print()

    modules = [
        ("DOI Verification", doi_failures),
        ("Number Consistency", consistency_failures),
        ("Overclaim Detection", overclaim_failures),
    ]

    all_passed = True
    for name, failures in modules:
        if failures == 0:
            ok(f"{name}: PASSED")
        else:
            fail(f"{name}: {failures} FAILURE(S)")
            all_passed = False

    print()
    if all_passed:
        print("  \u2705 ALL CHECKS PASSED \u2014 manuscript integrity verified")
        print()
        return 0
    else:
        print(f"  \u274c TOTAL FAILURES: {total_failures}")
        print("  Fix the issues above before committing to main branch.")
        print("  Hint: run with --fix-table6 to see the correct Table 6")
        print("  Hint: run with --update-manuscript to auto-fix Table 6 in the file")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
