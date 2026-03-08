# scripts/analyze_hbb_junctions.py
# Правильный анализ HBB splice junctions
# Фильтрует только HBB локус, считает canonical/novel ratio

import pandas as pd
import json
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

# HBB локус (с запасом)
HBB_CHR = "chr11"  # Galaxy пишет с "chr"
HBB_START = 5_220_000
HBB_END   = 5_232_000

# Canonical HBB splice sites (hg38, ENST00000335295)
# Проверено по реальным данным из Galaxy
CANONICAL = {
    (5_225_727, 5_226_576),  # exon1-exon2 (233K reads в WT)
    (5_226_800, 5_226_929),  # exon2-exon3 (189K reads в WT)
}

# ============================================================================
# Functions
# ============================================================================

def load_junctions(path):
    """Load junctions from BED file and filter to HBB locus."""
    df = pd.read_csv(path, sep='\t', header=None,
        names=['chr','start','end','name','score','strand',
               'thickStart','thickEnd','itemRgb'])
    
    # Фильтр только HBB локус
    hbb = df[
        (df['chr'].astype(str) == HBB_CHR) &
        (df['start'] >= HBB_START) &
        (df['end']   <= HBB_END)
    ].copy()
    
    return hbb

def analyze(df, name):
    """Analyze HBB junctions for one sample."""
    total = len(df)
    
    if total == 0:
        return {
            "sample": name, 
            "total_junctions": 0, 
            "canonical": 0, 
            "novel": 0, 
            "total_reads": 0
        }
    
    # Проверяем какие junctions canonical
    canonical_mask = df.apply(
        lambda r: (int(r['start']), int(r['end'])) in CANONICAL, 
        axis=1
    )
    
    # Считаем reads (колонка 5 = score, колонка 4 = name)
    # В BED от STAR: колонка 7 (0-based index 6) = unique reads
    if 'uniq_reads' in df.columns:
        reads_col = 'uniq_reads'
    elif len(df.columns) > 6:
        # Используем колонку 7 (index 6) если есть
        reads_col = df.columns[6]
    else:
        # Или score (колонка 5)
        reads_col = 'score'
    
    canonical_reads = df[canonical_mask][reads_col].astype(int).sum()
    novel_reads     = df[~canonical_mask][reads_col].astype(int).sum()
    total_reads     = canonical_reads + novel_reads
    
    result = {
        "sample": name,
        "total_junctions": int(total),
        "canonical_junctions": int(canonical_mask.sum()),
        "novel_junctions": int((~canonical_mask).sum()),
        "canonical_reads": int(canonical_reads),
        "novel_reads": int(novel_reads),
        "total_reads": int(total_reads),
        "canonical_pct": round(canonical_reads/total_reads*100, 1) if total_reads else 0,
        "novel_pct": round(novel_reads/total_reads*100, 1) if total_reads else 0,
    }
    
    # Добавляем детали по novel junctions
    if result['novel_junctions'] > 0:
        result['junctions_detail'] = df[~canonical_mask][
            ['chr','start','end',reads_col]
        ].rename(columns={reads_col: 'reads'}).to_dict('records')
    else:
        result['junctions_detail'] = []
    
    return result

# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  ARCHCODE HBB Splice Junction Analysis")
    print("  'Loop That Stayed' Hypothesis Test")
    print("=" * 70)
    print()
    
    base = Path("D:/ДНК/fastq_data/junctions")
    
    results = []
    
    for name, fname in [
        ("WT", "WT_junctions.bed"),
        ("B6", "B6_junctions.bed"),
        ("A2", "A2_junctions.bed")
    ]:
        fpath = base / fname
        
        if not fpath.exists():
            print(f"❌ File not found: {fpath}")
            continue
        
        df = load_junctions(fpath)
        r = analyze(df, name)
        results.append(r)
        
        print(f"\n{name}:")
        print(f"  Total HBB junctions: {r['total_junctions']}")
        print(f"  Canonical: {r['canonical_junctions']} ({r['canonical_pct']}% reads)")
        print(f"  Novel: {r['novel_junctions']} ({r['novel_pct']}% reads)")
        
        if r['novel_junctions'] > 0:
            print(f"  Top novel junctions:")
            for j in sorted(r['junctions_detail'], 
                          key=lambda x: x.get('reads', 0), 
                          reverse=True)[:5]:
                print(f"    chr{j['chr']}:{j['start']}-{j['end']} "
                      f"({j.get('reads', 'N/A')} reads)")
    
    print()
    print("=" * 70)
    print("  Summary")
    print("=" * 70)
    print()
    
    # Таблица
    print(f"{'Sample':<8} {'Junctions':>10} {'Canonical %':>14} {'Novel %':>10}")
    print("-" * 44)
    for r in results:
        print(f"{r['sample']:<8} {r['total_junctions']:>10} "
              f"{r['canonical_pct']:>13.1f}% {r['novel_pct']:>9.1f}%")
    
    print()
    
    # Сохраняем результат
    out = Path("D:/ДНК/results/hbb_splice_analysis.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"✅ Сохранено: {out}")
    
    # Вывод для manuscript
    print()
    print("=" * 70)
    print("  Manuscript-Ready Summary")
    print("=" * 70)
    print()
    
    if len(results) >= 2:
        wt = results[0]
        b6 = results[1]
        
        if wt['canonical_pct'] > 0:
            delta = b6['canonical_pct'] - wt['canonical_pct']
            print(f"B6 vs WT: {delta:+.1f} п.п. canonical splicing")
            print(f"  ({wt['canonical_pct']}% → {b6['canonical_pct']}%)")
        
        if len(results) >= 3:
            a2 = results[2]
            if wt['canonical_pct'] > 0:
                delta_a2 = a2['canonical_pct'] - wt['canonical_pct']
                print(f"A2 vs WT: {delta_a2:+.1f} п.п. canonical splicing")
                print(f"  ({wt['canonical_pct']}% → {a2['canonical_pct']}%)")
    
    print()
    
    return results

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    main()
