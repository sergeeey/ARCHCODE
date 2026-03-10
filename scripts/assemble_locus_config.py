#!/usr/bin/env python3
"""
assemble_locus_config.py — Генератор конфигурационных JSON-файлов локусов ARCHCODE
из локально сохранённых BED-файлов ENCODE ChIP-seq.

НАЗНАЧЕНИЕ:
    Этот скрипт документирует и воспроизводит процесс сборки tissue-specific конфигов,
    которые используются движком ARCHCODE для построения матриц структурных контактов.
    Конфиги, созданные вручную (например, scn5a_cardiac_250kb.json), могут быть
    реконструированы этим скриптом при наличии исходных BED-файлов.

ФОРМАТ ВХОДНЫХ BED-ФАЙЛОВ:
    narrowPeak (ENCODE стандарт, 10 колонок):
      chrom  chromStart  chromEnd  name  score  strand  signalValue  pValue  qValue  peak
    Принимаются как plain-text, так и gzip-сжатые (.bed.gz) файлы.

ПРИМЕР ИСПОЛЬЗОВАНИЯ (SCN5A cardiac 250kb config):
    python scripts/assemble_locus_config.py \\
        --gene SCN5A \\
        --chrom chr3 \\
        --start 38500000 \\
        --end 38750000 \\
        --resolution 1000 \\
        --h3k27ac-bed data/encode/ENCFF287NJM.bed.gz \\
        --ctcf-bed data/encode/ENCFF130TVA.bed.gz \\
        --h3k27ac-accession ENCFF287NJM \\
        --h3k27ac-experiment ENCSR000NPF \\
        --ctcf-accession ENCFF130TVA \\
        --ctcf-experiment ENCSR713SXF \\
        --tissue cardiac_tissue \\
        --genes '[{"name":"SCN5A","start":38548061,"end":38649687,"strand":"-"},
                  {"name":"SCN10A","start":38696806,"end":38816217,"strand":"-"},
                  {"name":"EXOG","start":38496339,"end":38526303,"strand":"+"}]' \\
        --max-ctcf 6 \\
        --max-enhancers 15 \\
        --output config/locus/scn5a_cardiac_250kb_reconstructed.json

ПРИМЕЧАНИЕ ПО CALIBRATED-ПАРАМЕТРАМ:
    occupancy для H3K27ac вычисляется как signal/max_signal, нормализованная в
    диапазон [0.10, 0.95]. Это MANUALLY CALIBRATED значение — не результат
    молекулярного моделирования (см. CLAUDE.md, правило NO HARDCODED "FITTED" PARAMETERS).

    occupancy для CTCF вычисляется как (signal/max_signal) * 0.9 (потолок 0.9
    соответствует практике существующих конфигов).
"""

import argparse
import gzip
import json
import math
import re
import sys
from pathlib import Path
from typing import Optional

import structlog

# ПОЧЕМУ structlog, а не logging: structlog даёт structured output (key=value),
# который легко парсить машинно и читать человеку — стандарт в ARCHCODE-скриптах.
log = structlog.get_logger()

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config" / "locus"

# ---------------------------------------------------------------------------
# Pydantic-модели входных и выходных данных
# ---------------------------------------------------------------------------

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
except ImportError:
    log.error("pydantic_missing", hint="pip install pydantic>=2.0")
    sys.exit(1)


class GeneAnnotation(BaseModel):
    """Аннотация одного гена для раздела features.genes конфига."""

    name: str
    start: int
    end: int
    strand: str = "+"
    note: Optional[str] = None

    @field_validator("strand")
    @classmethod
    def validate_strand(cls, v: str) -> str:
        """Проверяет, что strand — допустимый символ."""
        if v not in ("+", "-", "."):
            raise ValueError(f"strand must be '+', '-' or '.', got {v!r}")
        return v


class WindowConfig(BaseModel):
    """Описание геномного окна."""

    chromosome: str
    start: int
    end: int
    resolution_bp: int
    n_bins: int

    @model_validator(mode="after")
    def check_n_bins(self) -> "WindowConfig":
        """Проверяет соответствие n_bins геометрии окна."""
        # ПОЧЕМУ math.ceil: если окно не кратно resolution, добавляем крайний бин,
        # чтобы покрыть весь регион — это согласуется с поведением locus_config.py.
        expected = math.ceil((self.end - self.start) / self.resolution_bp)
        if self.n_bins != expected:
            raise ValueError(
                f"n_bins mismatch: declared {self.n_bins}, "
                f"computed {expected} from ({self.end}-{self.start})/{self.resolution_bp}"
            )
        return self


class AssemblyArgs(BaseModel):
    """Валидированные аргументы командной строки."""

    gene: str
    chrom: str
    start: int
    end: int
    resolution: int
    h3k27ac_bed: Optional[Path] = None
    ctcf_bed: Optional[Path] = None
    h3k27ac_accession: str = "UNKNOWN"
    h3k27ac_experiment: str = "UNKNOWN"
    ctcf_accession: str = "UNKNOWN"
    ctcf_experiment: str = "UNKNOWN"
    tissue: str = "unknown_tissue"
    assembly: str = "GRCh38"
    genes: list[GeneAnnotation] = Field(default_factory=list)
    max_ctcf: int = 10
    max_enhancers: int = 15
    output: Optional[Path] = None

    @field_validator("chrom")
    @classmethod
    def normalize_chrom(cls, v: str) -> str:
        """Добавляет 'chr' если отсутствует."""
        return v if v.startswith("chr") else f"chr{v}"

    @model_validator(mode="after")
    def at_least_one_bed(self) -> "AssemblyArgs":
        """Предупреждает если не передан ни один BED-файл."""
        if self.h3k27ac_bed is None and self.ctcf_bed is None:
            # Не фатальная ошибка — скрипт создаст конфиг с пустыми массивами.
            log.warning(
                "no_bed_files_provided",
                hint="pass --h3k27ac-bed and/or --ctcf-bed for non-empty features",
            )
        return self


# ---------------------------------------------------------------------------
# BED-парсинг
# ---------------------------------------------------------------------------


def _open_bed(path: Path):
    """Открывает BED-файл (plain или gzip) и возвращает итератор строк."""
    raw = path.read_bytes()
    if raw[:2] == b"\x1f\x8b":
        # ПОЧЕМУ не gzip.open(path): read_bytes() + decompress работает надёжнее
        # на Windows с Unicode-путями, где gzip.open иногда спотыкается.
        text = gzip.decompress(raw).decode("utf-8", errors="replace")
    else:
        text = raw.decode("utf-8", errors="replace")
    return (
        line
        for line in text.splitlines()
        if line and not line.startswith(("#", "track", "browser"))
    )


def _extract_accession_from_filename(path: Path) -> str:
    """Пытается извлечь ENCODE accession вида ENCFF[A-Z0-9]+ из имени файла."""
    match = re.search(r"(ENCFF[A-Z0-9]+)", path.stem, re.IGNORECASE)
    return match.group(1).upper() if match else path.stem


def parse_narrowpeak_bed(
    path: Path,
    chrom: str,
    win_start: int,
    win_end: int,
) -> list[dict]:
    """
    Читает narrowPeak BED-файл и возвращает пики внутри геномного окна.

    Формат narrowPeak (10 колонок):
      1. chrom
      2. chromStart (0-based)
      3. chromEnd
      4. name
      5. score (0-1000)
      6. strand (+/-/.)
      7. signalValue
      8. pValue (-log10)
      9. qValue (-log10)
      10. peak (offset от chromStart до точки максимума, -1 если неизвестно)

    Возвращает список словарей, отсортированных по signalValue убыванию.
    """
    if not path.exists():
        raise FileNotFoundError(f"BED file not found: {path}")

    peaks: list[dict] = []
    malformed_lines = 0

    for raw_line in _open_bed(path):
        fields = raw_line.split("\t")
        if len(fields) < 3:
            malformed_lines += 1
            continue

        p_chrom = fields[0]
        if p_chrom != chrom:
            continue

        try:
            p_start = int(fields[1])
            p_end = int(fields[2])
        except ValueError:
            malformed_lines += 1
            continue

        # ПОЧЕМУ проверка p_end < win_start or p_start > win_end: стандартный
        # half-open interval overlap — пик должен хоть частично попасть в окно.
        if p_end < win_start or p_start > win_end:
            continue

        name = fields[3] if len(fields) > 3 else "."
        score = int(fields[4]) if len(fields) > 4 and fields[4].lstrip("-").isdigit() else 0
        strand = fields[5] if len(fields) > 5 and fields[5] in ("+", "-", ".") else "."

        try:
            signal = float(fields[6]) if len(fields) > 6 else 0.0
        except ValueError:
            signal = 0.0

        try:
            pvalue = float(fields[7]) if len(fields) > 7 else -1.0
        except ValueError:
            pvalue = -1.0

        try:
            qvalue = float(fields[8]) if len(fields) > 8 else -1.0
        except ValueError:
            qvalue = -1.0

        try:
            peak_offset = int(fields[9]) if len(fields) > 9 else -1
        except ValueError:
            peak_offset = -1

        # ПОЧЕМУ peak_offset для центра: ENCODE narrowPeak col10 хранит смещение
        # точки максимума сигнала внутри пика. Это точнее, чем (start+end)//2.
        if peak_offset >= 0:
            center = p_start + peak_offset
        else:
            center = (p_start + p_end) // 2

        peaks.append(
            {
                "chrom": p_chrom,
                "start": p_start,
                "end": p_end,
                "name": name,
                "score": score,
                "strand": strand,
                "signal": signal,
                "pvalue": pvalue,
                "qvalue": qvalue,
                "peak_offset": peak_offset,
                "center": center,
            }
        )

    if malformed_lines > 0:
        log.warning("malformed_bed_lines_skipped", count=malformed_lines, path=str(path))

    # Сортировка по signal убыванию — topN выбираем позже.
    return sorted(peaks, key=lambda p: p["signal"], reverse=True)


# ---------------------------------------------------------------------------
# Преобразование пиков в features конфига
# ---------------------------------------------------------------------------

# ПОЧЕМУ константы 0.1 / 0.95: эмпирически выверенный диапазон из существующих
# конфигов (hbb_30kb_v2 occupancy 0.5–0.85, brca1_400kb 0.5–0.9, scn5a_cardiac 0.3–0.9).
# Нижний порог 0.1 предотвращает нулевые значения, верхний 0.95 оставляет место
# для промоторов с вручную проставленным occupancy=1.0.
_H3K27AC_OCC_MIN = 0.10
_H3K27AC_OCC_MAX = 0.95
_CTCF_OCC_CEILING = 0.90


def _signal_to_h3k27ac_occupancy(signal: float, max_signal: float) -> float:
    """
    Нормализует сигнал H3K27ac в occupancy [0.10, 0.95].

    Формула: occ = H3K27AC_OCC_MIN + (H3K27AC_OCC_MAX - H3K27AC_OCC_MIN) * (signal / max_signal)
    Результат округляется до 2 знаков.
    """
    if max_signal <= 0:
        return 0.30  # ASSUMED placeholder при отсутствии данных
    ratio = max(0.0, min(1.0, signal / max_signal))
    occ = _H3K27AC_OCC_MIN + (_H3K27AC_OCC_MAX - _H3K27AC_OCC_MIN) * ratio
    return round(occ, 2)


def _signal_to_ctcf_occupancy(signal: float, max_signal: float) -> float:
    """
    Нормализует сигнал CTCF в occupancy [0.0, 0.90].

    Формула: (signal / max_signal) * CTCF_OCC_CEILING.
    Соответствует практике scn5a_cardiac_250kb.json: пик с max_signal → 0.90,
    остальные пропорционально ниже.
    """
    if max_signal <= 0:
        return 0.50
    ratio = max(0.0, min(1.0, signal / max_signal))
    return round(ratio * _CTCF_OCC_CEILING, 2)


def build_enhancer_features(
    peaks: list[dict],
    accession: str,
    experiment: str,
    tissue: str,
    max_enhancers: int,
) -> list[dict]:
    """
    Преобразует topN H3K27ac пиков в формат features.enhancers конфига.

    Параметры:
        peaks: список пиков из parse_narrowpeak_bed, отсортированный по signal↓
        accession: ENCODE file accession (ENCFF...)
        experiment: ENCODE experiment accession (ENCSR...)
        tissue: строка-метка ткани (например, "cardiac_tissue")
        max_enhancers: максимальное число включаемых enhancers

    Возвращает список словарей в формате LocusConfig.features.enhancers.
    """
    selected = peaks[:max_enhancers]
    if not selected:
        log.info("no_h3k27ac_peaks_in_window", accession=accession)
        return []

    max_signal = selected[0]["signal"]  # пики уже отсортированы по убыванию
    source_label = f"ENCODE_{tissue}_H3K27ac"

    features = []
    for i, p in enumerate(selected):
        occupancy = _signal_to_h3k27ac_occupancy(p["signal"], max_signal)
        feature_name = p["name"] if p["name"] != "." else f"H3K27ac_peak_{i + 1}"
        note = (
            f"H3K27ac peak ({p['name']}, {p['chrom']}:{p['start']}-{p['end']}, "
            f"signal={p['signal']:.2f}). "
            f"occupancy MANUALLY CALIBRATED: signal={p['signal']:.2f}, "
            f"max_signal={max_signal:.2f} → {occupancy:.2f}"
        )
        features.append(
            {
                "position": p["center"],
                "occupancy": occupancy,
                "name": feature_name,
                "source": source_label,
                "encode_accession": accession,
                "note": note,
            }
        )
    return features


def build_ctcf_features(
    peaks: list[dict],
    accession: str,
    experiment: str,
    tissue: str,
    max_ctcf: int,
) -> list[dict]:
    """
    Преобразует topN CTCF пиков в формат features.ctcf_sites конфига.

    Ориентация берётся из колонки strand BED-файла если она '+' или '-'.
    Если strand='.' (неизвестно) — проставляется "unknown", что соответствует
    практике scn5a_cardiac_250kb.json (cardiac CTCF без strand-информации).

    Параметры аналогичны build_enhancer_features.
    """
    selected = peaks[:max_ctcf]
    if not selected:
        log.info("no_ctcf_peaks_in_window", accession=accession)
        return []

    max_signal = selected[0]["signal"]
    source_label = f"ENCODE_{tissue}_CTCF"

    features = []
    for i, p in enumerate(selected):
        occupancy = _signal_to_ctcf_occupancy(p["signal"], max_signal)

        # ПОЧЕМУ "unknown" вместо ".": downstream TypeScript код ожидает строку,
        # а "." может ломать display-логику. "unknown" явно сигнализирует отсутствие данных.
        orientation = p["strand"] if p["strand"] in ("+", "-") else "unknown"

        feature_name = p["name"] if p["name"] != "." else f"CTCF_peak_{i + 1}"
        note = (
            f"CTCF peak ({p['name']}, {p['chrom']}:{p['start']}-{p['end']}, "
            f"signal={p['signal']:.2f}). "
            f"occupancy MANUALLY CALIBRATED: {p['signal']:.2f}/{max_signal:.2f} "
            f"* {_CTCF_OCC_CEILING} = {occupancy:.2f}"
        )
        features.append(
            {
                "position": p["center"],
                "orientation": orientation,
                "signal": round(p["signal"], 2),
                "occupancy": occupancy,
                "name": feature_name,
                "source": source_label,
                "encode_accession": accession,
                "note": note,
            }
        )
    return features


# ---------------------------------------------------------------------------
# Сборка итогового конфига
# ---------------------------------------------------------------------------


def assemble_config(args: AssemblyArgs) -> dict:
    """
    Собирает полный словарь конфига локуса в формате LocusConfig.

    Читает BED-файлы, извлекает пики, строит features, добавляет метаданные
    data_sources и placeholder thresholds (требуют калибровки).

    Возвращает dict, готовый для json.dump.
    """
    window_size = args.end - args.start
    n_bins = math.ceil(window_size / args.resolution)

    log.info(
        "assembling_config",
        gene=args.gene,
        window=f"{args.chrom}:{args.start}-{args.end}",
        window_kb=window_size // 1000,
        resolution_bp=args.resolution,
        n_bins=n_bins,
    )

    # Валидируем геометрию окна через Pydantic (бросит ValueError при несоответствии).
    window_cfg = WindowConfig(
        chromosome=args.chrom,
        start=args.start,
        end=args.end,
        resolution_bp=args.resolution,
        n_bins=n_bins,
    )

    # --- H3K27ac ---
    h3k27ac_peaks: list[dict] = []
    h3k27ac_accession = args.h3k27ac_accession

    if args.h3k27ac_bed is not None:
        # Если accession не передан явно — пробуем извлечь из имени файла.
        if h3k27ac_accession == "UNKNOWN":
            h3k27ac_accession = _extract_accession_from_filename(args.h3k27ac_bed)
            log.info("h3k27ac_accession_inferred", accession=h3k27ac_accession)

        log.info("parsing_h3k27ac_bed", path=str(args.h3k27ac_bed))
        try:
            h3k27ac_peaks = parse_narrowpeak_bed(args.h3k27ac_bed, args.chrom, args.start, args.end)
        except FileNotFoundError as exc:
            log.error("h3k27ac_bed_not_found", error=str(exc))
            sys.exit(1)

        log.info(
            "h3k27ac_peaks_found",
            total_in_window=len(h3k27ac_peaks),
            included=min(len(h3k27ac_peaks), args.max_enhancers),
        )

    enhancer_features = build_enhancer_features(
        h3k27ac_peaks,
        accession=h3k27ac_accession,
        experiment=args.h3k27ac_experiment,
        tissue=args.tissue,
        max_enhancers=args.max_enhancers,
    )

    # --- CTCF ---
    ctcf_peaks: list[dict] = []
    ctcf_accession = args.ctcf_accession

    if args.ctcf_bed is not None:
        if ctcf_accession == "UNKNOWN":
            ctcf_accession = _extract_accession_from_filename(args.ctcf_bed)
            log.info("ctcf_accession_inferred", accession=ctcf_accession)

        log.info("parsing_ctcf_bed", path=str(args.ctcf_bed))
        try:
            ctcf_peaks = parse_narrowpeak_bed(args.ctcf_bed, args.chrom, args.start, args.end)
        except FileNotFoundError as exc:
            log.error("ctcf_bed_not_found", error=str(exc))
            sys.exit(1)

        log.info(
            "ctcf_peaks_found",
            total_in_window=len(ctcf_peaks),
            included=min(len(ctcf_peaks), args.max_ctcf),
        )

    ctcf_features = build_ctcf_features(
        ctcf_peaks,
        accession=ctcf_accession,
        experiment=args.ctcf_experiment,
        tissue=args.tissue,
        max_ctcf=args.max_ctcf,
    )

    # --- ID конфига из параметров ---
    window_kb = window_size // 1000
    config_id = f"{args.gene.lower()}_{args.tissue}_{window_kb}kb"

    # --- Аннотации генов ---
    genes_out = []
    for g in args.genes:
        entry: dict = {
            "name": g.name,
            "start": g.start,
            "end": g.end,
            "strand": g.strand,
        }
        if g.note:
            entry["note"] = g.note
        genes_out.append(entry)

    # --- data_sources ---
    # ПОЧЕМУ явно фиксируем peaks_in_window / peaks_included: это критичная
    # информация для воспроизводимости — чтобы рецензент мог понять какие пики
    # попали в конфиг без перезапуска скрипта.
    data_sources: dict = {}

    if args.ctcf_bed is not None or ctcf_accession != "UNKNOWN":
        ctcf_excluded = max(0, len(ctcf_peaks) - args.max_ctcf)
        data_sources["ctcf_chipseq"] = {
            "experiment": args.ctcf_experiment,
            "file": ctcf_accession,
            "type": "IDR thresholded narrowPeak",
            "tissue": args.tissue,
            "assembly": args.assembly,
            "peaks_in_window": len(ctcf_peaks),
            "peaks_included": len(ctcf_features),
            "peaks_excluded": ctcf_excluded,
            "url": f"https://www.encodeproject.org/experiments/{args.ctcf_experiment}/",
        }

    if args.h3k27ac_bed is not None or h3k27ac_accession != "UNKNOWN":
        data_sources["h3k27ac_chipseq"] = {
            "experiment": args.h3k27ac_experiment,
            "file": h3k27ac_accession,
            "type": "IDR thresholded narrowPeak",
            "tissue": args.tissue,
            "assembly": args.assembly,
            "peaks_in_window": len(h3k27ac_peaks),
            "peaks_included": len(enhancer_features),
            "url": f"https://www.encodeproject.org/experiments/{args.h3k27ac_experiment}/",
        }

    if genes_out:
        data_sources["gene_annotations"] = {
            "source": "NCBI RefSeq via UCSC API",
            "assembly": args.assembly,
            "track": "ncbiRefSeqCurated",
        }

    # --- Сборка итогового словаря ---
    config: dict = {
        "id": config_id,
        "name": f"{args.gene} {window_kb}kb ({args.tissue} CTCF + {args.tissue} H3K27ac)",
        "description": (
            f"{window_kb}kb window spanning the {args.gene} locus on "
            f"{args.chrom}. CTCF: ENCODE {args.tissue} ChIP-seq ({ctcf_accession}, "
            f"{args.ctcf_experiment}). H3K27ac: ENCODE {args.tissue} ({h3k27ac_accession}, "
            f"{args.h3k27ac_experiment}). "
            f"Config assembled by assemble_locus_config.py from local BED files. "
            f"occupancy values MANUALLY CALIBRATED — see feature notes."
        ),
        "genome_assembly": args.assembly,
        "window": window_cfg.model_dump(),
        "features": {
            "enhancers": enhancer_features,
            "ctcf_sites": ctcf_features,
            "tad_boundaries": [],
            "genes": genes_out,
        },
    }

    if data_sources:
        config["data_sources"] = data_sources

    # ПОЧЕМУ placeholder thresholds с явным предупреждением: downstream код
    # ARCHCODE требует поле thresholds. Пустой конфиг вызовет runtime-ошибку.
    # Placeholder с предупреждением честнее, чем молча скопировать чужие числа.
    config["thresholds"] = {
        "ssim_pathogenic": 0.95,
        "ssim_likely_pathogenic": 0.975,
        "ssim_vus": 0.99,
        "ssim_likely_benign": 0.999,
        "note": (
            "PLACEHOLDER — REQUIRES CALIBRATION. "
            f"These values are NOT calibrated for {config_id}. "
            "Run ARCHCODE with known pathogenic variants to establish "
            "empirical thresholds at FPR <= 1%."
        ),
    }
    config["_thresholds_note"] = (
        "MANDATORY RECALIBRATION BEFORE USE IN PUBLICATION. "
        "Threshold values above are structural placeholders only."
    )

    return config


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Создаёт и возвращает ArgumentParser для скрипта."""
    parser = argparse.ArgumentParser(
        description="Assemble an ARCHCODE locus config JSON from ENCODE ChIP-seq BED files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Обязательные геномные координаты
    req = parser.add_argument_group("genomic window (required)")
    req.add_argument("--gene", required=True, help="Gene symbol (e.g. SCN5A)")
    req.add_argument("--chrom", required=True, help="Chromosome (e.g. chr3 or 3)")
    req.add_argument("--start", required=True, type=int, help="Window start (0-based)")
    req.add_argument("--end", required=True, type=int, help="Window end")
    req.add_argument(
        "--resolution",
        required=True,
        type=int,
        help="Bin size in bp (e.g. 1000)",
    )

    # Входные BED-файлы
    beds = parser.add_argument_group("input BED files")
    beds.add_argument(
        "--h3k27ac-bed",
        type=Path,
        default=None,
        help="Path to H3K27ac narrowPeak BED (plain or .gz)",
    )
    beds.add_argument(
        "--ctcf-bed",
        type=Path,
        default=None,
        help="Path to CTCF narrowPeak BED (plain or .gz)",
    )

    # ENCODE провенанс
    prov = parser.add_argument_group("ENCODE provenance")
    prov.add_argument(
        "--h3k27ac-accession", default="UNKNOWN", help="H3K27ac file accession (ENCFF...)"
    )
    prov.add_argument(
        "--h3k27ac-experiment", default="UNKNOWN", help="H3K27ac experiment accession (ENCSR...)"
    )
    prov.add_argument("--ctcf-accession", default="UNKNOWN", help="CTCF file accession (ENCFF...)")
    prov.add_argument(
        "--ctcf-experiment", default="UNKNOWN", help="CTCF experiment accession (ENCSR...)"
    )
    prov.add_argument(
        "--tissue", default="unknown_tissue", help="Tissue/cell-type label (e.g. cardiac_tissue)"
    )
    prov.add_argument("--assembly", default="GRCh38", help="Genome assembly (default: GRCh38)")

    # Аннотации генов
    parser.add_argument(
        "--genes",
        default="[]",
        help=(
            "JSON array of gene annotations: "
            '[{"name":"SCN5A","start":38548061,"end":38649687,"strand":"-"}]'
        ),
    )

    # Фильтры
    filt = parser.add_argument_group("peak filters")
    filt.add_argument(
        "--max-ctcf", type=int, default=10, help="Max CTCF sites to include (default: 10)"
    )
    filt.add_argument(
        "--max-enhancers",
        type=int,
        default=15,
        help="Max H3K27ac enhancer peaks to include (default: 15)",
    )

    # Вывод
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help=("Output JSON path. Default: config/locus/<gene>_<tissue>_<size>kb.json"),
    )

    return parser


def parse_genes_json(raw: str) -> list[GeneAnnotation]:
    """
    Парсит JSON-строку аннотаций генов в список GeneAnnotation.

    При ошибке парсинга — завершает процесс с понятным сообщением.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        log.error(
            "invalid_genes_json",
            error=str(exc),
            hint='Example: \'[{"name":"SCN5A","start":38548061,"end":38649687,"strand":"-"}]\'',
        )
        sys.exit(1)

    if not isinstance(data, list):
        log.error("genes_json_must_be_array", got=type(data).__name__)
        sys.exit(1)

    genes: list[GeneAnnotation] = []
    for i, item in enumerate(data):
        try:
            genes.append(GeneAnnotation(**item))
        except Exception as exc:
            log.error("invalid_gene_entry", index=i, error=str(exc))
            sys.exit(1)
    return genes


def main() -> None:
    """Точка входа: парсит аргументы, собирает конфиг, записывает JSON."""
    parser = build_parser()
    ns = parser.parse_args()

    # Парсим аннотации генов из JSON-строки
    genes = parse_genes_json(ns.genes)

    # Собираем и валидируем аргументы через Pydantic
    try:
        args = AssemblyArgs(
            gene=ns.gene,
            chrom=ns.chrom,
            start=ns.start,
            end=ns.end,
            resolution=ns.resolution,
            h3k27ac_bed=ns.h3k27ac_bed,
            ctcf_bed=ns.ctcf_bed,
            h3k27ac_accession=ns.h3k27ac_accession,
            h3k27ac_experiment=ns.h3k27ac_experiment,
            ctcf_accession=ns.ctcf_accession,
            ctcf_experiment=ns.ctcf_experiment,
            tissue=ns.tissue,
            assembly=ns.assembly,
            genes=genes,
            max_ctcf=ns.max_ctcf,
            max_enhancers=ns.max_enhancers,
            output=ns.output,
        )
    except Exception as exc:
        log.error("argument_validation_failed", error=str(exc))
        sys.exit(1)

    # Собираем конфиг
    config = assemble_config(args)

    # Определяем путь для сохранения
    if args.output is not None:
        out_path = args.output
    else:
        window_kb = (args.end - args.start) // 1000
        filename = f"{args.gene.lower()}_{args.tissue}_{window_kb}kb.json"
        out_path = CONFIG_DIR / filename

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2, ensure_ascii=False)

    log.info(
        "config_written",
        path=str(out_path),
        enhancers=len(config["features"]["enhancers"]),
        ctcf_sites=len(config["features"]["ctcf_sites"]),
        genes=len(config["features"]["genes"]),
    )

    # Напоминание о калибровке порогов — ключевое требование CLAUDE.md
    print(
        f"\n[REMINDER] {out_path.name} written. "
        "Threshold values are PLACEHOLDERS — calibrate with known pathogenic variants "
        "before any publication use.\n"
    )


if __name__ == "__main__":
    main()
