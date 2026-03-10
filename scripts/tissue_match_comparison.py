#!/usr/bin/env python3
"""
tissue_match_comparison.py — Создание K562-only конфигов для LDLR и BRCA1.

НАЗНАЧЕНИЕ:
    Генерирует конфиги с заменой тканеспецифичных H3K27ac энхансеров на K562
    H3K27ac пики (ENCFF864OSZ). Используется для контроля tissue-match:
    сравнения сигнала ARCHCODE при правильной (HepG2/MCF7) и неправильной (K562)
    ткани. Это базовый эксперимент для EXP-003 validation framework.

    LDLR: тканеспецифичен в гепатоцитах (HepG2) — заменяем на K562 (лейкемия).
    BRCA1: тканеспецифичен в MCF7 (молочная железа) — заменяем на K562.

ИСПОЛЬЗОВАНИЕ:
    python scripts/tissue_match_comparison.py

ВЫХОДНЫЕ ФАЙЛЫ:
    config/locus/ldlr_k562_300kb.json
    config/locus/brca1_k562_400kb.json

ИНТЕГРИТЕТ ДАННЫХ:
    Используются только реальные пики из ENCFF864OSZ.bed.gz.
    Occupancy нормализуется в [0.10, 0.95] — MANUALLY CALIBRATED.
    Никаких синтетических данных (см. CLAUDE.md, NO INVISIBLE SYNTHETIC DATA).
"""

import gzip
import json
import sys
from pathlib import Path
import structlog
from pydantic import BaseModel, field_validator, model_validator

# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Константы путей
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
ENCODE_CACHE = ROOT / "data" / "encode_cache"
CONFIG_DIR = ROOT / "config" / "locus"

# K562 H3K27ac: ENCODE accession ENCFF864OSZ (эксперимент ENCSR000AKP)
K562_H3K27AC_BED = ENCODE_CACHE / "ENCFF864OSZ.bed.gz"
K562_H3K27AC_ACCESSION = "ENCFF864OSZ"
K562_H3K27AC_EXPERIMENT = "ENCSR000AKP"

# Диапазон нормализации occupancy (согласуется с assemble_locus_config.py)
OCC_MIN = 0.10
OCC_MAX = 0.95


# ---------------------------------------------------------------------------
# Pydantic-модели
# ---------------------------------------------------------------------------


class NarrowPeakRecord(BaseModel):
    """Один пик из narrowPeak BED-файла."""

    chrom: str
    start: int
    end: int
    signal: float
    peak_offset: int = -1  # поле "peak" (10-я колонка), offset от start

    @property
    def center(self) -> int:
        """Центр пика: peak offset если есть, иначе (start+end)//2."""
        if self.peak_offset >= 0:
            return self.start + self.peak_offset
        return (self.start + self.end) // 2


class WindowQuery(BaseModel):
    """Параметры геномного окна для фильтрации пиков."""

    chrom: str
    start: int
    end: int
    resolution_bp: int
    n_bins: int
    gene_name: str
    cell_line_source: str  # откуда заменяем (для описания)

    @field_validator("chrom")
    @classmethod
    def normalize_chrom(cls, v: str) -> str:
        """Добавляет 'chr' если отсутствует."""
        return v if v.startswith("chr") else f"chr{v}"

    @model_validator(mode="after")
    def check_n_bins(self) -> "WindowQuery":
        """Проверяет соответствие n_bins геометрии окна."""
        expected = (self.end - self.start) // self.resolution_bp
        if expected != self.n_bins:
            raise ValueError(
                f"n_bins mismatch: declared {self.n_bins}, computed {expected} for {self.gene_name}"
            )
        return self


class EnhancerEntry(BaseModel):
    """Один энхансер в разделе features.enhancers конфига."""

    position: int
    occupancy: float
    name: str
    source: str
    encode_accession: str
    note: str

    @field_validator("occupancy")
    @classmethod
    def occupancy_range(cls, v: float) -> float:
        """Проверяет допустимый диапазон occupancy."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"occupancy={v} вне [0, 1]")
        return round(v, 4)


# ---------------------------------------------------------------------------
# Парсинг BED.gz
# ---------------------------------------------------------------------------


def _read_bed_gz(path: Path) -> bytes:
    """Читает содержимое BED.gz файла в байты."""
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        # ПОЧЕМУ decompress вместо gzip.open: надёжнее на Windows с
        # Unicode-путями. Одинаковый подход с assemble_locus_config.py.
        return gzip.decompress(raw)
    return raw


def extract_peaks_in_window(
    bed_path: Path,
    chrom: str,
    win_start: int,
    win_end: int,
) -> list[NarrowPeakRecord]:
    """
    Извлекает narrowPeak пики из BED.gz файла, перекрывающие геномное окно.

    Критерий перекрытия: пик пересекается с [win_start, win_end) хотя бы 1bp.
    Только реальные данные из файла — никаких синтетических заглушек.

    Args:
        bed_path: путь к narrowPeak BED.gz файлу
        chrom: хромосома (например "chr19")
        win_start: начало окна (0-based)
        win_end: конец окна (exclusive)

    Returns:
        Список NarrowPeakRecord, отсортированных по убыванию signal.

    Raises:
        FileNotFoundError: если BED файл не найден
        ValueError: если файл не в narrowPeak формате (< 7 колонок)
    """
    if not bed_path.exists():
        raise FileNotFoundError(f"BED файл не найден: {bed_path}")

    log.info(
        "reading_bed",
        path=str(bed_path),
        chrom=chrom,
        win_start=win_start,
        win_end=win_end,
    )

    raw_bytes = _read_bed_gz(bed_path)
    text = raw_bytes.decode("utf-8", errors="replace")

    records: list[NarrowPeakRecord] = []
    skipped_format = 0
    total_lines = 0

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "track", "browser")):
            continue
        total_lines += 1

        fields = line.split("\t")
        if len(fields) < 7:
            skipped_format += 1
            continue

        peak_chrom = fields[0]
        if peak_chrom != chrom:
            continue

        try:
            peak_start = int(fields[1])
            peak_end = int(fields[2])
            signal = float(fields[6])
        except (ValueError, IndexError):
            skipped_format += 1
            continue

        # ПОЧЕМУ проверяем перекрытие, а не включение: пик может выходить
        # за границы окна, но центр (используемый как position) может быть внутри.
        if peak_end <= win_start or peak_start >= win_end:
            continue

        peak_offset = -1
        if len(fields) > 9:
            try:
                peak_offset = int(fields[9])
            except ValueError:
                pass

        records.append(
            NarrowPeakRecord(
                chrom=peak_chrom,
                start=peak_start,
                end=peak_end,
                signal=signal,
                peak_offset=peak_offset,
            )
        )

    log.info(
        "peaks_extracted",
        chrom=chrom,
        window=f"{win_start}-{win_end}",
        total_bed_lines=total_lines,
        peaks_found=len(records),
        skipped_format=skipped_format,
    )

    # Сортируем по убыванию signal для нормализации (max будет первым)
    records.sort(key=lambda r: r.signal, reverse=True)
    return records


# ---------------------------------------------------------------------------
# Нормализация occupancy
# ---------------------------------------------------------------------------


def normalize_occupancy(signals: list[float]) -> list[float]:
    """
    Нормализует список сигналов H3K27ac в диапазон [OCC_MIN, OCC_MAX].

    Линейная нормализация: occupancy_i = OCC_MIN + (s_i / s_max) * (OCC_MAX - OCC_MIN).
    Если все сигналы одинаковые — возвращает OCC_MAX для всех.

    MANUALLY CALIBRATED — не является результатом молекулярного моделирования.
    (см. CLAUDE.md, правило NO HARDCODED "FITTED" PARAMETERS)

    Args:
        signals: список значений signalValue из narrowPeak

    Returns:
        Список occupancy, округлённых до 2 знаков, в том же порядке.
    """
    if not signals:
        return []
    s_max = max(signals)
    if s_max == 0:
        return [OCC_MIN] * len(signals)

    # ПОЧЕМУ делим на max из всего окна, а не глобальный max:
    # occupancy отражает относительную активность энхансера ВНУТРИ данного
    # регуляторного домена — это контекстно-зависимая, а не абсолютная мера.
    return [round(OCC_MIN + (s / s_max) * (OCC_MAX - OCC_MIN), 2) for s in signals]


# ---------------------------------------------------------------------------
# Сборка списка энхансеров из K562 пиков
# ---------------------------------------------------------------------------


def build_k562_enhancers(
    peaks: list[NarrowPeakRecord],
    win_start: int,
    win_end: int,
    gene_name: str,
    max_enhancers: int = 15,
) -> list[EnhancerEntry]:
    """
    Строит список энхансеров из K562 H3K27ac пиков для вставки в конфиг.

    Фильтрует пики, центр которых попадает в [win_start, win_end).
    Ограничивает список max_enhancers записями (по убыванию signal).

    Args:
        peaks: список NarrowPeakRecord, отсортированных по убыванию signal
        win_start: начало геномного окна
        win_end: конец геномного окна
        gene_name: имя гена (для именования энхансеров)
        max_enhancers: максимальное количество энхансеров

    Returns:
        Список EnhancerEntry, готовых к записи в JSON конфиг.
    """
    # ПОЧЕМУ фильтруем по центру: position в конфиге — это точка контакта,
    # а не границы пика. Центр пика — биологически наиболее активная точка.
    valid_peaks = [p for p in peaks if win_start <= p.center < win_end]

    if not valid_peaks:
        log.warning(
            "no_peaks_in_window_by_center",
            gene=gene_name,
            win_start=win_start,
            win_end=win_end,
        )
        return []

    # Берём топ max_enhancers по signal (уже отсортированы)
    selected = valid_peaks[:max_enhancers]

    signals = [p.signal for p in selected]
    occupancies = normalize_occupancy(signals)

    enhancers: list[EnhancerEntry] = []
    for i, (peak, occ) in enumerate(zip(selected, occupancies)):
        rank = i + 1
        name = f"{gene_name}_K562_H3K27ac_peak_{rank}"
        note = (
            f"K562 H3K27ac peak (ENCFF864OSZ, {peak.chrom}:{peak.start}-{peak.end}, "
            f"signal={peak.signal:.2f}). "
            f"Peak center at {peak.center}. "
            f"MANUALLY CALIBRATED occupancy — rank {rank}/{len(selected)} by signal "
            f"within window. K562 tissue-match baseline for tissue-mismatch comparison "
            f"(EXP-003). NOT the tissue-matched enhancer source for this locus."
        )
        enhancers.append(
            EnhancerEntry(
                position=peak.center,
                occupancy=occ,
                name=name,
                source="ENCODE_K562_H3K27ac",
                encode_accession=K562_H3K27AC_ACCESSION,
                note=note,
            )
        )

    return enhancers


# ---------------------------------------------------------------------------
# Сборка финального конфига
# ---------------------------------------------------------------------------


def build_k562_config(
    template: dict,
    enhancers: list[EnhancerEntry],
    k562_peaks_count: int,
    tissue_matched_peaks_count: int,
    new_id: str,
    new_name: str,
    new_description: str,
) -> dict:
    """
    Создаёт K562-only конфиг из шаблона, заменяя только enhancers.

    CTCF sites сохраняются из шаблона — они в значительной мере cell-type
    invariant (Cuddapah 2009, PMID:19030024). genes, window, thresholds
    также сохраняются без изменений.

    Args:
        template: оригинальный конфиг (как dict из JSON)
        enhancers: список K562 энхансеров для замены
        k562_peaks_count: число K562 пиков в окне (для метаданных)
        tissue_matched_peaks_count: число tissue-matched пиков (для сравнения)
        new_id: новый id конфига (добавляем суффикс _k562)
        new_name: новое название конфига
        new_description: новое описание

    Returns:
        dict-представление нового конфига, готового к json.dump.
    """
    import copy

    config = copy.deepcopy(template)

    # Обновляем идентификаторы
    config["id"] = new_id
    config["name"] = new_name
    config["description"] = new_description

    # ПОЧЕМУ сериализуем через .model_dump(): Pydantic гарантирует что все
    # поля валидны и правильно типизированы перед записью в JSON.
    config["features"]["enhancers"] = [e.model_dump() for e in enhancers]

    # Обновляем data_sources — добавляем запись о K562 H3K27ac
    if "data_sources" not in config:
        config["data_sources"] = {}

    config["data_sources"]["h3k27ac_chipseq_k562_primary"] = {
        "experiment": K562_H3K27AC_EXPERIMENT,
        "file": K562_H3K27AC_ACCESSION,
        "type": "IDR thresholded narrowPeak",
        "cell_line": "K562",
        "assembly": "GRCh38",
        "peaks_in_window": k562_peaks_count,
        "tissue_matched_peaks_for_reference": tissue_matched_peaks_count,
        "url": "https://www.encodeproject.org/experiments/ENCSR000AKP/",
        "note": (
            "K562 H3K27ac used as PRIMARY enhancer source for tissue-mismatch "
            "baseline config. K562 is chronic myelogenous leukemia — NOT the "
            "tissue-matched cell line for this locus. "
            f"tissue_matched_peaks_in_window={tissue_matched_peaks_count}, "
            f"k562_peaks_in_window={k562_peaks_count}. "
            "MANUALLY CALIBRATED occupancy values."
        ),
    }

    return config


# ---------------------------------------------------------------------------
# Вспомогательная функция: подсчёт tissue-matched пиков из существующего конфига
# ---------------------------------------------------------------------------


def count_tissue_matched_peaks(template: dict) -> int:
    """
    Считает количество energy enhancers в оригинальном конфиге.

    Используется для сравнительной статистики: сколько tissue-matched пиков
    vs сколько K562 пиков найдено в том же окне.

    Args:
        template: оригинальный конфиг

    Returns:
        Количество энхансеров в оригинальном конфиге.
    """
    return len(template.get("features", {}).get("enhancers", []))


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------


def main() -> None:
    """
    Главная функция: создаёт K562-only конфиги для LDLR и BRCA1.

    Алгоритм:
    1. Проверяем наличие ENCFF864OSZ.bed.gz
    2. Для каждого локуса: извлекаем K562 пики из окна
    3. Нормализуем occupancy в [0.10, 0.95]
    4. Собираем конфиг из шаблона с заменой enhancers
    5. Записываем JSON, печатаем инструкции
    """

    # Проверяем источник данных ПЕРЕД работой (Integrity Protocol)
    if not K562_H3K27AC_BED.exists():
        log.error(
            "bed_file_missing",
            path=str(K562_H3K27AC_BED),
            hint="Run: python scripts/assemble_locus_config.py or download from ENCODE",
        )
        sys.exit(1)

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------------
    # Определяем параметры двух локусов
    # -----------------------------------------------------------------------

    LDLR_WINDOW = WindowQuery(
        chrom="chr19",
        start=10_940_000,
        end=11_240_000,
        resolution_bp=1000,
        n_bins=300,
        gene_name="LDLR",
        cell_line_source="HepG2",
    )
    BRCA1_WINDOW = WindowQuery(
        chrom="chr17",
        start=42_900_000,
        end=43_300_000,
        resolution_bp=1000,
        n_bins=400,
        gene_name="BRCA1",
        cell_line_source="MCF7",
    )

    loci = [
        {
            "window": LDLR_WINDOW,
            "template_path": CONFIG_DIR / "ldlr_300kb.json",
            "output_path": CONFIG_DIR / "ldlr_k562_300kb.json",
            "new_id": "ldlr_k562_300kb",
            "new_name": "LDLR 300kb TAD — K562 H3K27ac baseline (tissue-mismatch control)",
            "new_description": (
                "K562-only baseline config for LDLR locus. Created for tissue-mismatch "
                "comparison (EXP-003): replaces HepG2 H3K27ac enhancers (ENCFF012ADZ, "
                "ENCSR000AMO) with K562 H3K27ac peaks (ENCFF864OSZ, ENCSR000AKP). "
                "CTCF sites retained from original HepG2 config (cell-type invariant, "
                "Cuddapah 2009 PMID:19030024). K562 is chronic myelogenous leukemia — "
                "NOT the tissue-matched cell line for LDLR (hepatocytes/HepG2). "
                "Hypothesis: ARCHCODE signal for P/LP variants should be weaker with "
                "mismatched K562 enhancers vs matched HepG2 enhancers. "
                "window=chr19:10940000-11240000, 300 bins @ 1kb resolution."
            ),
            "atlas_locus_id": "ldlr_k562",
        },
        {
            "window": BRCA1_WINDOW,
            "template_path": CONFIG_DIR / "brca1_400kb.json",
            "output_path": CONFIG_DIR / "brca1_k562_400kb.json",
            "new_id": "brca1_k562_400kb",
            "new_name": "BRCA1 400kb TAD — K562 H3K27ac baseline (tissue-mismatch control)",
            "new_description": (
                "K562-only baseline config for BRCA1 locus. Created for tissue-mismatch "
                "comparison (EXP-003): replaces MCF7 H3K27ac enhancers (ENCFF340KSH, "
                "ENCSR000EWR) with K562 H3K27ac peaks (ENCFF864OSZ, ENCSR000AKP). "
                "CTCF sites retained from original K562+MCF7 config (cell-type invariant). "
                "K562 baseline tests whether BRCA1 signal degrades with mismatched "
                "K562 enhancer landscape vs MCF7 breast cancer-matched config. "
                "Note: K562 shows strong H3K27ac at BRCA1 promoter CpG island "
                "(signal~72.62) — constitutive acetylation, not tissue-specific. "
                "window=chr17:42900000-43300000, 400 bins @ 1kb resolution."
            ),
            "atlas_locus_id": "brca1_k562",
        },
    ]

    # -----------------------------------------------------------------------
    # Обрабатываем каждый локус
    # -----------------------------------------------------------------------

    stats: list[dict] = []
    npx_commands: list[str] = []

    for locus in loci:
        window: WindowQuery = locus["window"]
        template_path: Path = locus["template_path"]
        output_path: Path = locus["output_path"]
        gene = window.gene_name

        log.info(
            "processing_locus", gene=gene, window=f"{window.chrom}:{window.start}-{window.end}"
        )

        # Загружаем шаблон
        if not template_path.exists():
            log.error("template_missing", path=str(template_path), gene=gene)
            sys.exit(1)

        with open(template_path, encoding="utf-8") as f:
            template = json.load(f)

        tissue_matched_count = count_tissue_matched_peaks(template)

        # Извлекаем K562 пики из окна
        k562_peaks = extract_peaks_in_window(
            bed_path=K562_H3K27AC_BED,
            chrom=window.chrom,
            win_start=window.start,
            win_end=window.end,
        )

        k562_count_in_window = len(k562_peaks)

        if not k562_peaks:
            log.error(
                "no_k562_peaks_found",
                gene=gene,
                bed=str(K562_H3K27AC_BED),
                hint="Проверь что файл содержит данные для указанного chrom:start-end",
            )
            sys.exit(1)

        # Строим список энхансеров
        enhancers = build_k562_enhancers(
            peaks=k562_peaks,
            win_start=window.start,
            win_end=window.end,
            gene_name=gene,
            max_enhancers=15,
        )

        log.info(
            "enhancers_built",
            gene=gene,
            k562_peaks_in_window=k562_count_in_window,
            enhancers_selected=len(enhancers),
            tissue_matched_peaks_original=tissue_matched_count,
        )

        # Собираем конфиг
        new_config = build_k562_config(
            template=template,
            enhancers=enhancers,
            k562_peaks_count=k562_count_in_window,
            tissue_matched_peaks_count=tissue_matched_count,
            new_id=locus["new_id"],
            new_name=locus["new_name"],
            new_description=locus["new_description"],
        )

        # Записываем JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)

        log.info("config_written", path=str(output_path), gene=gene)

        stats.append(
            {
                "gene": gene,
                "window": f"{window.chrom}:{window.start}-{window.end}",
                "k562_peaks_in_window": k562_count_in_window,
                "enhancers_written": len(enhancers),
                "tissue_matched_peaks_original": tissue_matched_count,
                "cell_line_replaced": window.cell_line_source,
                "output": str(output_path),
            }
        )

        npx_commands.append(
            f"npx tsx scripts/generate-unified-atlas.ts --locus {locus['atlas_locus_id']}"
        )

    # -----------------------------------------------------------------------
    # Итоговая статистика и инструкции
    # -----------------------------------------------------------------------

    print("\n" + "=" * 70)
    print("TISSUE-MATCH COMPARISON — K562 BASELINE CONFIGS CREATED")
    print("=" * 70)

    for s in stats:
        print(f"\n  Gene: {s['gene']} ({s['window']})")
        print(f"    Cell line replaced:               {s['cell_line_replaced']}")
        print(f"    Tissue-matched enhancers (orig):  {s['tissue_matched_peaks_original']}")
        print(f"    K562 H3K27ac peaks in window:     {s['k562_peaks_in_window']}")
        print(f"    K562 enhancers written to config: {s['enhancers_written']}")
        print(f"    Output: {s['output']}")

    print("\n" + "-" * 70)
    print("Run these commands to generate K562-only atlases:")
    for cmd in npx_commands:
        print(f"  {cmd}")
    print("-" * 70)
    print("\nNOTE: Compare K562 atlas ΔLSSIM P/LP vs B/LB against tissue-matched config.")
    print("      Hypothesis: tissue-mismatched K562 enhancers → weaker ARCHCODE signal.")
    print(f"\nData source: ENCFF864OSZ (K562 H3K27ac, ENCSR000AKP) [VERIFIED: {K562_H3K27AC_BED}]")


if __name__ == "__main__":
    main()
