#!/usr/bin/env python3
"""
Загрузчик GWAS-ассоциаций из EBI GWAS Catalog REST API.

Скачивает SNP для гематологических трейтов и фильтрует по окнам ARCHCODE.
Дополнительно сохраняет все интергенные хиты — они наиболее ценны
для гипотезы о структурном нарушении (нет кодирующего механизма).

Использование:
    python scripts/download_gwas_catalog.py
    python scripts/download_gwas_catalog.py --dry-run
    python scripts/download_gwas_catalog.py --max-results 500
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Generator

import requests
import structlog

# ПОЧЕМУ: structlog вместо print — унифицированный формат логов,
# совместимый с остальными скриптами ARCHCODE
log = structlog.get_logger()

PROJECT = Path(__file__).parent.parent
GWAS_API = "https://www.ebi.ac.uk/gwas/rest/api"

# ПОЧЕМУ: page_size=1000 — максимум допустимый GWAS Catalog REST API (проверено в docs).
# Меньший размер страницы → больше запросов → дольше и выше риск rate-limit.
PAGE_SIZE = 1000

# Задержка между запросами — EBI рекомендует не более 1 rps для REST API
REQUEST_DELAY_SEC = 0.6

ARCHCODE_WINDOWS: dict[str, dict[str, Any]] = {
    "HBB": {"chr": "chr11", "start": 5210000, "end": 5305000},
    "BRCA1": {"chr": "chr17", "start": 43040000, "end": 43440000},
    "TP53": {"chr": "chr17", "start": 7661779, "end": 7691779},
    "TERT": {"chr": "chr5", "start": 1235000, "end": 1335000},
    "MLH1": {"chr": "chr3", "start": 36993000, "end": 37053000},
    "CFTR": {"chr": "chr7", "start": 117480000, "end": 117670000},
    "SCN5A": {"chr": "chr3", "start": 38550000, "end": 38700000},
    "GJB2": {"chr": "chr13", "start": 20187000, "end": 20207000},
    "LDLR": {"chr": "chr19", "start": 11089000, "end": 11139000},
}

# ПОЧЕМУ: трейты выбраны для максимального перекрытия с HBB-локусом (гематологические),
# но включаем и общие (MCV, RBC count) — они дают GWAS-хиты в βS-глобин-регуляторных регионах.
TRAITS: list[dict[str, str]] = [
    {"name": "beta-thalassemia", "query": "beta-thalassemia"},
    {"name": "mean corpuscular volume", "query": "mean corpuscular volume"},
    {"name": "fetal hemoglobin", "query": "fetal hemoglobin"},
    {"name": "hemoglobin concentration", "query": "hemoglobin concentration"},
    {"name": "red blood cell count", "query": "red blood cell count"},
    {"name": "anemia", "query": "anemia"},
    {"name": "sickle cell disease", "query": "sickle cell disease"},
]


def make_session() -> requests.Session:
    """Создаёт HTTP-сессию с правильными заголовками для GWAS Catalog API."""
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/json",
            # ПОЧЕМУ: User-Agent позволяет EBI идентифицировать скрипт при обращении к поддержке
            "User-Agent": "ARCHCODE-GWAS-Downloader/1.0 (research; contact via GitHub)",
        }
    )
    return session


def paginate_gwas(
    session: requests.Session,
    url: str,
    params: dict[str, Any],
    max_results: int | None = None,
    embedded_key: str | None = None,
) -> Generator[dict[str, Any], None, None]:
    """
    Итератор по страницам GWAS Catalog REST API (HAL-формат пагинации).

    GWAS Catalog использует Spring HATEOAS — следующая страница в _links.next.href.
    embedded_key: ключ внутри _embedded (например "singleNucleotidePolymorphisms").
    Если не задан — пробует associations и efoTraits автоматически.
    """
    current_url: str | None = url
    fetched = 0

    while current_url:
        time.sleep(REQUEST_DELAY_SEC)
        try:
            resp = session.get(current_url, params=params, timeout=30)
            resp.raise_for_status()
        except requests.HTTPError as e:
            log.error(
                "HTTP error from GWAS Catalog", url=current_url, status=e.response.status_code
            )
            break
        except requests.RequestException as e:
            log.error("Network error from GWAS Catalog", url=current_url, error=str(e))
            break

        data = resp.json()

        # ПОЧЕМУ: HAL-структура — данные в _embedded, навигация в _links.
        # Разные эндпоинты оборачивают результаты по-разному.
        embedded = data.get("_embedded", {})
        if embedded_key:
            items: list[dict] = embedded.get(embedded_key, [])
        else:
            items = embedded.get("associations", []) or embedded.get("efoTraits", []) or []

        for item in items:
            yield item
            fetched += 1
            if max_results and fetched >= max_results:
                return

        # Переход к следующей странице или выход
        links = data.get("_links", {})
        next_link = links.get("next", {}).get("href")

        # ПОЧЕМУ: убираем params после первого запроса — они уже закодированы в next href
        params = {}
        current_url = next_link


def normalise_chromosome(chrom_raw: str | None) -> str | None:
    """Приводит обозначение хромосомы к формату 'chrN'."""
    if not chrom_raw:
        return None
    chrom = str(chrom_raw).strip()
    if chrom.startswith("chr"):
        return chrom
    # GWAS Catalog возвращает "1", "X", "MT" — добавляем префикс
    return f"chr{chrom}"


def find_archcode_locus(chrom: str | None, position: int | None) -> str | None:
    """Возвращает название локуса ARCHCODE, если SNP попадает в окно, иначе None."""
    if chrom is None or position is None:
        return None
    for locus, window in ARCHCODE_WINDOWS.items():
        if window["chr"] == chrom and window["start"] <= position <= window["end"]:
            return locus
    return None


def parse_association(raw: dict[str, Any], trait_name: str) -> dict[str, Any] | None:
    """
    Извлекает плоскую запись из JSON-ассоциации GWAS Catalog.

    Возвращает None если нет rsID или хромосомных координат (нефункциональная запись).
    """
    snp_block = (
        raw.get("loci", [{}])[0].get("strongestRiskAlleles", [{}])[0] if raw.get("loci") else {}
    )
    # Альтернативная структура для ассоциаций из /associations эндпоинта
    if not snp_block:
        snp_block = {}

    # ПОЧЕМУ: GWAS Catalog имеет нестабильную вложенность — SNP-данные
    # могут быть в разных полях в зависимости от версии эндпоинта.
    # Пробуем несколько путей.
    rs_id: str | None = None
    chrom_raw: str | None = None
    position_raw: int | None = None

    # Путь 1: loci → strongestRiskAlleles → riskAlleleName
    loci = raw.get("loci", [])
    if loci:
        locus_entry = loci[0]
        alleles = locus_entry.get("strongestRiskAlleles", [])
        if alleles:
            rs_candidate = alleles[0].get("riskAlleleName", "")
            if "-" in rs_candidate:
                rs_id = rs_candidate.split("-")[0]
            else:
                rs_id = rs_candidate or None

        # Координаты из snpIds
        snp_ids = locus_entry.get("snpIds", [])
        if snp_ids:
            snp_meta = snp_ids[0]
            chrom_raw = snp_meta.get("chromosome")
            position_raw = snp_meta.get("chromosomePosition")

    # Путь 2: прямые поля для упрощённых ответов
    if not rs_id:
        rs_id = raw.get("rsId") or raw.get("riskAllele", "").split("-")[0] or None

    if not chrom_raw:
        chrom_raw = raw.get("chromosome") or raw.get("chr")

    if position_raw is None:
        pos_raw = raw.get("chromosomePosition") or raw.get("position")
        if pos_raw is not None:
            try:
                position_raw = int(pos_raw)
            except (ValueError, TypeError):
                position_raw = None

    if not rs_id or not rs_id.startswith("rs"):
        return None  # Пропускаем записи без валидного rsID

    chrom = normalise_chromosome(chrom_raw)

    # p-value может быть float или строка с экспонентой
    p_mantissa = raw.get("pvalueMantissa")
    p_exponent = raw.get("pvalueExponent")
    p_value: float | None = None
    if p_mantissa is not None and p_exponent is not None:
        try:
            p_value = float(p_mantissa) * (10 ** float(p_exponent))
        except (ValueError, TypeError):
            p_value = None

    # Размер эффекта: OR или бета-коэффициент
    effect_size: float | None = None
    if raw.get("orPerCopyNum") is not None:
        effect_size = raw["orPerCopyNum"]
    elif raw.get("betaNum") is not None:
        effect_size = raw["betaNum"]

    # Маппинг гена
    mapped_gene: str | None = None
    genomic_contexts = raw.get("loci", [{}])[0].get("genomicContexts", []) if loci else []
    if genomic_contexts:
        gene_names = [
            gc.get("gene", {}).get("geneName", "")
            for gc in genomic_contexts
            if gc.get("gene", {}).get("geneName")
        ]
        mapped_gene = ",".join(sorted(set(g for g in gene_names if g))) or None

    # ПОЧЕМУ: интергенный статус критичен для интерпретации ARCHCODE —
    # интергенные хиты не могут объясняться кодирующим механизмом.
    is_intergenic = not bool(mapped_gene) or any(
        ctx.get("isIntergenic", False) for ctx in genomic_contexts
    )

    archcode_locus = find_archcode_locus(chrom, position_raw)

    return {
        "rsID": rs_id,
        "Chromosome": chrom,
        "Position_GRCh38": position_raw,
        "P_Value": p_value,
        "Effect_Size": effect_size,
        "Mapped_Gene": mapped_gene or "",
        "Trait": trait_name,
        "Is_Intergenic": is_intergenic,
        "In_ARCHCODE_Window": archcode_locus is not None,
        "ARCHCODE_Locus": archcode_locus or "",
    }


def search_locus_region(
    session: requests.Session,
    locus_name: str,
    chrom: str,
    start: int,
    end: int,
    max_results: int | None,
    dry_run: bool,
) -> list[dict[str, Any]]:
    """
    Ищет GWAS SNPs по хромосомному окну через findByChromBpLocationRange.

    ПОЧЕМУ region-based вместо trait-based: (1) findBySearchQuery не существует в API,
    (2) findByEfoTrait требует exact match, (3) region query гарантированно возвращает
    ВСЕ GWAS-ассоциации в окне ARCHCODE независимо от trait — это то что нам нужно.
    """
    # Убираем 'chr' из хромосомы — GWAS API использует "11", не "chr11"
    chrom_num = chrom.replace("chr", "")

    log.info("Searching locus region", locus=locus_name, chrom=chrom_num, start=start, end=end)

    if dry_run:
        log.info("Dry-run: skipping actual API request")
        return []

    snp_url = f"{GWAS_API}/singleNucleotidePolymorphisms/search/findByChromBpLocationRange"
    snp_params = {
        "chrom": chrom_num,
        "bpStart": start,
        "bpEnd": end,
        "size": PAGE_SIZE,
        "page": 0,
    }

    results: list[dict[str, Any]] = []
    raw_count = 0

    for snp_data in paginate_gwas(
        session, snp_url, snp_params, max_results, embedded_key="singleNucleotidePolymorphisms"
    ):
        raw_count += 1
        parsed = parse_snp_entry(snp_data, locus_name)
        if parsed:
            results.extend(parsed)

    log.info(
        "Fetched SNPs for locus", locus=locus_name, raw_snps=raw_count, associations=len(results)
    )
    return results


def parse_snp_entry(snp: dict[str, Any], locus_name: str) -> list[dict[str, Any]]:
    """
    Парсит запись SNP из findByChromBpLocationRange.

    Один SNP может иметь несколько ассоциаций (разные трейты/исследования).
    Возвращает список записей — по одной на каждую ассоциацию.
    """
    rs_id = snp.get("rsId")
    if not rs_id or not rs_id.startswith("rs"):
        return []

    # Координаты из locations
    locations = snp.get("locations", [])
    chrom_raw: str | None = None
    position: int | None = None
    for loc in locations:
        chrom_raw = loc.get("chromosomeName")
        pos_raw = loc.get("chromosomePosition")
        if pos_raw is not None:
            try:
                position = int(pos_raw)
            except (ValueError, TypeError):
                pass
            break

    chrom = normalise_chromosome(chrom_raw)

    # Геномный контекст (intergenic, mapped gene)
    genomic_contexts = snp.get("genomicContexts", [])
    gene_names = []
    is_intergenic = False
    for ctx in genomic_contexts:
        if ctx.get("isIntergenic"):
            is_intergenic = True
        gene = ctx.get("gene", {})
        gn = gene.get("geneName")
        if gn:
            gene_names.append(gn)
    mapped_gene = ",".join(sorted(set(gene_names))) or ""
    if not mapped_gene:
        is_intergenic = True

    # Ассоциации — вложены в _links, но для полноты нужен отдельный запрос.
    # ПОЧЕМУ без sub-запроса: API не возвращает p-value и effect size в SNP endpoint.
    # Создаём одну запись без p-value; overlay скрипт обогатит данные.
    return [
        {
            "rsID": rs_id,
            "Chromosome": chrom,
            "Position_GRCh38": position,
            "P_Value": None,  # Not available in SNP endpoint directly
            "Effect_Size": None,
            "Mapped_Gene": mapped_gene,
            "Trait": f"GWAS hit in {locus_name} locus",
            "Is_Intergenic": is_intergenic,
            "In_ARCHCODE_Window": True,
            "ARCHCODE_Locus": locus_name,
        }
    ]


def deduplicate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Дедупликация по rsID + Trait: оставляем запись с наименьшим p-value.

    ПОЧЕМУ: один SNP может встречаться в нескольких EFO-трейтах одной группы,
    дублирование раздует таблицу и создаст ложную видимость большего числа хитов.
    """
    best: dict[str, dict] = {}
    for rec in records:
        key = f"{rec['rsID']}|{rec['Trait']}"
        existing = best.get(key)
        if existing is None:
            best[key] = rec
        else:
            # Предпочитаем запись с меньшим p-value (более значимая)
            p_new = rec.get("P_Value") or 1.0
            p_old = existing.get("P_Value") or 1.0
            if p_new < p_old:
                best[key] = rec

    return list(best.values())


def save_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    """Сохраняет список записей в CSV с фиксированным порядком колонок."""
    import csv

    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "rsID",
        "Chromosome",
        "Position_GRCh38",
        "P_Value",
        "Effect_Size",
        "Mapped_Gene",
        "Trait",
        "Is_Intergenic",
        "In_ARCHCODE_Window",
        "ARCHCODE_Locus",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for rec in records:
            writer.writerow({col: rec.get(col, "") for col in columns})

    log.info("CSV saved", path=str(output_path), rows=len(records))


def build_summary(
    all_records: list[dict[str, Any]],
    archcode_records: list[dict[str, Any]],
    intergenic_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Строит JSON-сводку по результатам загрузки."""
    from collections import Counter

    locus_counts = Counter(r["ARCHCODE_Locus"] for r in archcode_records if r["ARCHCODE_Locus"])
    trait_counts = Counter(r["Trait"].split(" (")[0] for r in all_records)

    return {
        "total_associations": len(all_records),
        "in_archcode_windows": len(archcode_records),
        "intergenic_total": len(intergenic_records),
        "intergenic_in_archcode": sum(1 for r in archcode_records if r.get("Is_Intergenic")),
        "by_locus": dict(locus_counts),
        "by_trait": dict(trait_counts),
        "data_source": "EBI GWAS Catalog REST API v2",
        "genome_build": "GRCh38",
        "p_value_threshold": "5e-8 (GWAS-significant, as returned by Catalog)",
    }


def main() -> int:
    """Основной поток выполнения."""
    parser = argparse.ArgumentParser(description="Download GWAS Catalog hematological associations")
    parser.add_argument(
        "--dry-run", action="store_true", help="Проверить логику без реальных запросов"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Максимум ассоциаций на трейт (для тестирования)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT / "data" / "gwas",
        help="Директория для выходных файлов",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    session = make_session()

    # ПОЧЕМУ: сначала проверяем доступность API — явная ошибка лучше,
    # чем молчаливый провал после нескольких минут работы.
    if not args.dry_run:
        log.info("Checking GWAS Catalog API availability...")
        try:
            probe = session.get(f"{GWAS_API}/associations", params={"size": 1}, timeout=15)
            probe.raise_for_status()
            log.info("API reachable", status=probe.status_code)
        except requests.RequestException as e:
            log.error(
                "GWAS Catalog API unreachable",
                url=GWAS_API,
                error=str(e),
                hint="Check network connection or try again later",
            )
            return 1

    all_records: list[dict[str, Any]] = []

    # ПОЧЕМУ region-based вместо trait-based:
    # findByChromBpLocationRange возвращает ВСЕ GWAS SNPs в окне ARCHCODE,
    # независимо от trait. Это надёжнее, чем искать по названию трейта
    # (которое требует exact match EFO URI).
    for locus_name, window in ARCHCODE_WINDOWS.items():
        chrom = window["chr"]
        start = window["start"]
        end = window["end"]

        locus_records = search_locus_region(
            session=session,
            locus_name=locus_name,
            chrom=chrom,
            start=start,
            end=end,
            max_results=args.max_results,
            dry_run=args.dry_run,
        )
        all_records.extend(locus_records)
        log.info(
            "Locus complete",
            locus=locus_name,
            fetched=len(locus_records),
            total_so_far=len(all_records),
        )

    # Дедупликация
    all_records = deduplicate(all_records)
    log.info("After deduplication", total=len(all_records))

    # Разделяем: попавшие в окна ARCHCODE и все интергенные
    archcode_records = [r for r in all_records if r["In_ARCHCODE_Window"]]
    intergenic_records = [r for r in all_records if r["Is_Intergenic"]]

    log.info(
        "Filtering complete",
        in_archcode_windows=len(archcode_records),
        intergenic_total=len(intergenic_records),
    )

    # Сохраняем: главный файл = ARCHCODE-окна + все интергенные
    # ПОЧЕМУ: интергенные хиты вне окон тоже ценны — их можно использовать
    # как негативный контроль (нет структурного объяснения в этих локусах).
    main_records = list({r["rsID"]: r for r in archcode_records + intergenic_records}.values())
    save_csv(main_records, output_dir / "gwas_hematological_hits.csv")

    # Отдельный файл только с ARCHCODE-окнами для оверлея
    save_csv(archcode_records, output_dir / "gwas_archcode_only.csv")

    # JSON-сводка
    summary = build_summary(all_records, archcode_records, intergenic_records)
    summary_path = output_dir / "gwas_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info("Summary saved", path=str(summary_path))

    # Итоговый вывод
    print("\n=== GWAS Catalog Download Complete ===")
    print(f"Total associations fetched:  {summary['total_associations']}")
    print(f"In ARCHCODE windows:         {summary['in_archcode_windows']}")
    print(f"Intergenic (all):            {summary['intergenic_total']}")
    print(f"Intergenic in ARCHCODE:      {summary['intergenic_in_archcode']}")
    print(f"\nBy locus: {summary['by_locus']}")
    print(f"\nOutputs written to: {output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
