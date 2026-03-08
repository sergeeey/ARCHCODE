# scripts/classify_hbb_novel_junctions.py
# Deep dive analysis of novel HBB splice junctions
# Classifies junctions by type (alt splice, exon skip, intron retention, etc.)

import pandas as pd
import json
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

HBB_CHR = "chr11"
HBB_START = 5_220_000
HBB_END   = 5_232_000

# HBB Gene Structure (hg38, ENST00000335295)
# From Ensembl/UCSC
HBB_EXONS = [
    (5_225_613, 5_225_726),  # Exon 1 (5' UTR)
    (5_226_076, 5_226_576),  # Exon 2 (CDS)
    (5_226_929, 5_227_071),  # Exon 3 (CDS + 3' UTR)
]

# Canonical splice junctions
CANONICAL_JUNCTIONS = {
    (5_225_727, 5_226_576): "E1→E2",  # Exon 1 to Exon 2
    (5_226_800, 5_226_929): "E2→E3",  # Exon 2 to Exon 3
}

# Known alternative HBB isoforms (from literature)
# HBB has several known alternative transcripts
KNOWN_ALT_ISOFORMS = {
    # Alternative 3' splice site in exon 2
    (5_225_727, 5_226_500): "Alt 3'SS E2",
    # Alternative transcription start
    (5_225_613, 5_226_576): "Alt TSS",
    # Retained intron 1
    (5_225_613, 5_226_076): "Intron 1 retention",
}

# Tolerance for matching (bp)
TOLERANCE = 10

# ============================================================================
# Functions
# ============================================================================

def classify_junction(start, end):
    """
    Classify a splice junction by type.
    
    Returns dict with classification info.
    """
    result = {
        "start": start,
        "end": end,
        "span": end - start,
        "type": "unknown",
        "details": "",
        "affected_exon": None,
    }
    
    # Check if canonical
    if (start, end) in CANONICAL_JUNCTIONS:
        result["type"] = "canonical"
        result["details"] = CANONICAL_JUNCTIONS[(start, end)]
        return result
    
    # Check known alternative isoforms
    if (start, end) in KNOWN_ALT_ISOFORMS:
        result["type"] = "known_alternative"
        result["details"] = KNOWN_ALT_ISOFORMS[(start, end)]
        return result
    
    # Check for alternative 5' splice site (donor)
    for exon_start, exon_end in HBB_EXONS:
        # Alternative donor at exon end
        if abs(end - exon_end) <= TOLERANCE:
            if start > exon_start and start < exon_end:
                result["type"] = "alt_5ss"
                result["details"] = f"Alt 5'SS in exon ({exon_start}-{exon_end})"
                result["affected_exon"] = f"{exon_start}-{exon_end}"
                return result
    
    # Check for alternative 3' splice site (acceptor)
    for exon_start, exon_end in HBB_EXONS:
        # Alternative acceptor at exon start
        if abs(start - exon_start) <= TOLERANCE:
            if end > exon_start and end < exon_end:
                result["type"] = "alt_3ss"
                result["details"] = f"Alt 3'SS in exon ({exon_start}-{exon_end})"
                result["affected_exon"] = f"{exon_start}-{exon_end}"
                return result
    
    # Check for exon skipping
    # E1→E3 skip would be: start ~5_225_726, end ~5_227_071
    if abs(start - 5_225_726) <= TOLERANCE and abs(end - 5_227_071) <= TOLERANCE:
        result["type"] = "exon_skip"
        result["details"] = "Exon 2 skipping (E1→E3)"
        result["affected_exon"] = "Exon 2"
        return result
    
    # Check for intron retention
    for i, (exon_start, exon_end) in enumerate(HBB_EXONS):
        if i < len(HBB_EXONS) - 1:
            next_exon_start = HBB_EXONS[i+1][0]
            # Junction within intron
            if exon_end < start < end < next_exon_start:
                result["type"] = "intron_retention"
                result["details"] = f"Intron {i+1} retention"
                result["affected_exon"] = f"Intron {i+1}"
                return result
    
    # Check for alternative transcription start/end
    # Extended 5' UTR
    if start < HBB_EXONS[0][0] and end == HBB_EXONS[0][1]:
        result["type"] = "alt_tss"
        result["details"] = "Alternative transcription start"
        result["affected_exon"] = "Exon 1"
        return result
    
    # Extended 3' UTR
    if start == HBB_EXONS[-1][0] and end > HBB_EXONS[-1][1]:
        result["type"] = "alt_tes"
        result["details"] = "Alternative transcription end"
        result["affected_exon"] = "Exon 3"
        return result
    
    # Check if near known splice sites (cryptic)
    for exon_start, exon_end in HBB_EXONS:
        # Near exon boundaries
        if abs(start - exon_start) <= 100 or abs(start - exon_end) <= 100:
            result["type"] = "cryptic_5ss"
            result["details"] = f"Cryptic 5'SS near exon ({exon_start}-{exon_end})"
            result["affected_exon"] = f"{exon_start}-{exon_end}"
            return result
        
        if abs(end - exon_start) <= 100 or abs(end - exon_end) <= 100:
            result["type"] = "cryptic_3ss"
            result["details"] = f"Cryptic 3'SS near exon ({exon_start}-{exon_end})"
            result["affected_exon"] = f"{exon_start}-{exon_end}"
            return result
    
    # If none of the above, it's a novel/unclassified junction
    result["type"] = "novel"
    result["details"] = "Unclassified novel junction"
    
    return result

def load_and_classify(path, sample_name):
    """Load junctions from BED file and classify each."""
    df = pd.read_csv(path, sep='\t', header=None,
        names=['chr','start','end','name','score','strand',
               'thickStart','thickEnd','itemRgb'])
    
    # Filter to HBB locus
    hbb = df[
        (df['chr'].astype(str) == HBB_CHR) &
        (df['start'] >= HBB_START) &
        (df['end']   <= HBB_END)
    ].copy()
    
    # Classify each junction
    classified = []
    for idx, row in hbb.iterrows():
        start = int(row['start'])
        end = int(row['end'])
        reads = int(row['itemRgb']) if 'itemRgb' in row else int(row.get('score', 0))
        
        classification = classify_junction(start, end)
        classification['sample'] = sample_name
        classification['reads'] = reads
        
        classified.append(classification)
    
    return classified

def summarize_classifications(classified_list):
    """Summarize classifications across all samples."""
    df = pd.DataFrame(classified_list)
    
    # Pivot table: type × sample
    pivot = df.pivot_table(
        index='type', 
        columns='sample', 
        values='reads', 
        aggfunc='sum',
        fill_value=0
    )
    
    # Count junctions per type
    junction_counts = df.groupby(['type', 'sample']).size().unstack(fill_value=0)
    
    return pivot, junction_counts, df

# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  HBB Novel Junctions — Deep Classification Analysis")
    print("=" * 70)
    print()
    
    base = Path("D:/ДНК/fastq_data/junctions")
    
    all_classified = []
    
    for name, fname in [
        ("WT", "WT_junctions.bed"),
        ("B6", "B6_junctions.bed"),
        ("A2", "A2_junctions.bed")
    ]:
        fpath = base / fname
        
        if not fpath.exists():
            print(f"❌ File not found: {fpath}")
            continue
        
        classified = load_and_classify(fpath, name)
        all_classified.extend(classified)
        
        # Summary for this sample
        sample_df = pd.DataFrame(classified)
        
        print(f"\n{name}:")
        print(f"  Total junctions: {len(sample_df)}")
        
        # By type
        type_counts = sample_df.groupby('type').size()
        print(f"  By type:")
        for t, c in type_counts.items():
            print(f"    {t}: {c}")
    
    print()
    print("=" * 70)
    print("  Cross-Sample Comparison")
    print("=" * 70)
    print()
    
    # Summarize
    pivot, junction_counts, df = summarize_classifications(all_classified)
    
    print("Junction counts by type:")
    print(junction_counts.to_string())
    print()
    
    print("Read counts by type:")
    print(pivot.to_string())
    print()
    
    # Find junctions that increase in B6/A2
    print("=" * 70)
    print("  Junctions Enriched in B6/A2 vs WT")
    print("=" * 70)
    print()
    
    # Get novel junctions only
    novel_df = df[df['type'] != 'canonical'].copy()
    
    # Pivot by junction
    junction_pivot = novel_df.pivot_table(
        index=['start', 'end', 'type', 'details'],
        columns='sample',
        values='reads',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    # Calculate enrichment
    junction_pivot['B6_vs_WT'] = junction_pivot['B6'] - junction_pivot['WT']
    junction_pivot['A2_vs_WT'] = junction_pivot['A2'] - junction_pivot['WT']
    
    # Sort by enrichment
    enriched_b6 = junction_pivot.sort_values('B6_vs_WT', ascending=False).head(10)
    enriched_a2 = junction_pivot.sort_values('A2_vs_WT', ascending=False).head(10)
    
    print("Top 10 junctions enriched in B6:")
    for idx, row in enriched_b6.iterrows():
        print(f"  chr11:{row['start']}-{row['end']} ({row['type']})")
        print(f"    WT={row['WT']}, B6={row['B6']}, A2={row['A2']}")
        print(f"    Details: {row['details']}")
        print()
    
    print("Top 10 junctions enriched in A2:")
    for idx, row in enriched_a2.iterrows():
        print(f"  chr11:{row['start']}-{row['end']} ({row['type']})")
        print(f"    WT={row['WT']}, B6={row['B6']}, A2={row['A2']}")
        print(f"    Details: {row['details']}")
        print()
    
    # Save results
    out_json = Path("D:/ДНК/results/hbb_novel_junctions_classified.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to serializable format
    output_data = {
        "all_classified": all_classified,
        "junction_counts": junction_counts.to_dict(),
        "read_counts": pivot.to_dict(),
        "enriched_b6": enriched_b6.to_dict('records'),
        "enriched_a2": enriched_a2.to_dict('records'),
    }
    
    out_json.write_text(json.dumps(output_data, indent=2))
    print(f"✅ Сохранено: {out_json}")
    
    # Manuscript-ready summary
    print()
    print("=" * 70)
    print("  Manuscript-Ready Summary")
    print("=" * 70)
    print()
    
    # Count by type
    total_novel_wt = len(df[(df['sample']=='WT') & (df['type']!='canonical')])
    total_novel_b6 = len(df[(df['sample']=='B6') & (df['type']!='canonical')])
    total_novel_a2 = len(df[(df['sample']=='A2') & (df['type']!='canonical')])
    
    print(f"Novel junctions detected:")
    print(f"  WT: {total_novel_wt}")
    print(f"  B6: {total_novel_b6} ({(total_novel_b6/total_novel_wt-1)*100:+.0f}% vs WT)")
    print(f"  A2: {total_novel_a2} ({(total_novel_a2/total_novel_wt-1)*100:+.0f}% vs WT)")
    print()
    
    # By type
    print("Novel junction types:")
    for jtype in ['alt_5ss', 'alt_3ss', 'cryptic_5ss', 'cryptic_3ss', 
                  'exon_skip', 'intron_retention', 'alt_tss', 'alt_tes', 'novel']:
        wt_count = len(df[(df['sample']=='WT') & (df['type']==jtype)])
        b6_count = len(df[(df['sample']=='B6') & (df['type']==jtype)])
        a2_count = len(df[(df['sample']=='A2') & (df['type']==jtype)])
        
        if wt_count + b6_count + a2_count > 0:
            print(f"  {jtype}: WT={wt_count}, B6={b6_count}, A2={a2_count}")
    
    print()
    
    return output_data

# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    main()
