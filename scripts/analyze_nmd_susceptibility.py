#!/usr/bin/env python3
"""
NMD (Nonsense-Mediated Decay) Susceptibility Analysis
Detects aberrant splicing events that trigger NMD pathway

Input: STAR splice junction files (SJ.out.tab) + BAM files
Output: NMD-susceptible transcript fraction, PTC (premature termination codon) locations
"""

import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

# HBB gene structure (GRCh38)
HBB_GENE = {
    'chr': '11',
    'strand': '+',
    'start': 5_225_464,
    'end': 5_227_071,
    'exons': [
        {'number': 1, 'start': 5_225_464, 'end': 5_225_726, 'cds_start': 5_225_618},  # ATG at chr11:5,225,618
        {'number': 2, 'start': 5_226_405, 'end': 5_226_627},
        {'number': 3, 'start': 5_227_020, 'end': 5_227_071, 'cds_end': 5_227_070}  # Stop at chr11:5,227,070
    ],
    'introns': [
        {'number': 1, 'start': 5_225_726, 'end': 5_226_405, 'length': 679},  # Intron 1
        {'number': 2, 'start': 5_226_627, 'end': 5_227_020, 'length': 393}   # Intron 2
    ]
}

# Canonical splice junctions
CANONICAL_JUNCTIONS = {
    'exon1_2': (5_225_726, 5_226_405),  # Exon 1 donor → Exon 2 acceptor
    'exon2_3': (5_226_627, 5_227_020)   # Exon 2 donor → Exon 3 acceptor
}

# Genetic code (for PTC detection)
GENETIC_CODE = {
    'TAA': '*', 'TAG': '*', 'TGA': '*',  # Stop codons
}

def load_splice_junctions(sj_file):
    """
    Load STAR splice junction file (SJ.out.tab)

    Format:
    1. chromosome
    2. first base of intron (1-based)
    3. last base of intron (1-based)
    4. strand (0: undefined, 1: +, 2: -)
    5. intron motif (0: non-canonical, 1: GT/AG, 2: CT/AC, 3: GC/AG, 4: CT/GC, 5: AT/AC, 6: GT/AT)
    6. 0: unannotated, 1: annotated
    7. number of uniquely mapping reads crossing junction
    8. number of multi-mapping reads crossing junction
    9. maximum spliced alignment overhang
    """
    print(f"Loading splice junctions from {sj_file}...")

    cols = ['chr', 'start', 'end', 'strand', 'motif', 'annotated',
            'unique_reads', 'multimap_reads', 'max_overhang']

    df = pd.read_csv(sj_file, sep='\t', names=cols, comment='#')

    # Filter for HBB locus (chr11:5.2-5.25 Mb)
    df = df[
        (df['chr'] == '11') &
        (df['start'] >= HBB_GENE['start'] - 10000) &
        (df['end'] <= HBB_GENE['end'] + 10000)
    ]

    print(f"  Found {len(df)} splice junctions in HBB region")

    return df

def classify_junction(row):
    """Classify junction as canonical or aberrant"""
    start, end = row['start'], row['end']

    # Check if matches canonical junctions
    for junction_name, (canon_start, canon_end) in CANONICAL_JUNCTIONS.items():
        if start == canon_start and end == canon_end:
            return 'canonical', junction_name

    # Check for exon skipping
    if start == HBB_GENE['exons'][0]['end'] and end == HBB_GENE['exons'][2]['start']:
        return 'exon_skipping', 'exon2_skipped'

    # Check for intron retention (junction within exon or spanning exon-intron)
    for intron in HBB_GENE['introns']:
        if intron['start'] < start < intron['end'] or intron['start'] < end < intron['end']:
            return 'intron_retention', f"intron{intron['number']}_retained"

    # Cryptic splice site
    return 'cryptic', 'unknown'

def detect_ptc_in_retained_intron(intron_number, reference_seq=None):
    """
    Detect premature termination codon (PTC) in retained intron

    NMD Rule: PTC >50-55 nt upstream of last exon-exon junction triggers NMD
    """
    intron = HBB_GENE['introns'][intron_number - 1]

    # If reference sequence provided, scan for stop codons
    if reference_seq:
        # Scan intron sequence for in-frame stop codons
        # (Simplified: assumes reading frame from exon 1)
        stop_codons_found = []
        for i in range(0, len(reference_seq) - 2, 3):
            codon = reference_seq[i:i+3].upper()
            if codon in ['TAA', 'TAG', 'TGA']:
                position = intron['start'] + i
                stop_codons_found.append({
                    'position': position,
                    'codon': codon,
                    'distance_to_last_junction': HBB_GENE['exons'][2]['start'] - position
                })

        return stop_codons_found

    # Without reference, use heuristic:
    # Intron retention usually introduces frameshift → high PTC probability
    # Conservative estimate: 1/3 probability of in-frame stop codon per 100 bp

    intron_length = intron['length']
    ptc_probability = 1 - (2/3) ** (intron_length / 100)  # Probability of at least one stop

    # Distance to last junction (NMD threshold)
    distance_to_last_junction = HBB_GENE['exons'][2]['start'] - intron['end']

    nmd_triggered = distance_to_last_junction > 55  # NMD rule: >50-55 nt

    return {
        'intron': intron_number,
        'length': intron_length,
        'ptc_probability': ptc_probability,
        'distance_to_last_junction': distance_to_last_junction,
        'nmd_triggered': nmd_triggered
    }

def detect_ptc_in_exon_skipping():
    """
    Detect PTC from exon 2 skipping

    Exon 1 (92 aa) + Exon 3 (17 aa) direct junction creates frameshift
    """
    # HBB exon 2 is 223 bp (not divisible by 3)
    # Skipping creates frameshift → PTC very likely in exon 3

    # Exon 2: 223 bp = 74 aa + 1 nt
    # Exon 2 skipping: exon 1 last codon joins exon 3 first nt → frameshift

    # Distance from junction to end of exon 3
    distance_to_end = HBB_GENE['exons'][2]['end'] - HBB_GENE['exons'][2]['start']

    # NMD triggered (exon 2 skipping creates junction >55 nt from end)
    nmd_triggered = True  # Always triggers NMD for HBB exon 2 skipping

    return {
        'event': 'exon2_skipping',
        'frameshift': True,
        'ptc_expected': True,
        'ptc_location': 'exon3',
        'nmd_triggered': nmd_triggered,
        'mechanism': 'Frameshift from exon1-3 junction (223 bp exon2 skipped)'
    }

def calculate_nmd_susceptibility(junctions_df):
    """
    Calculate NMD-susceptible transcript fraction

    NMD-susceptible = aberrant junctions that create PTCs >50 nt upstream of last junction
    """
    results = []

    for _, row in junctions_df.iterrows():
        junction_type, junction_name = classify_junction(row)

        reads = row['unique_reads']

        # Analyze NMD potential
        if junction_type == 'canonical':
            nmd_susceptible = False
            ptc_info = None

        elif junction_type == 'exon_skipping':
            nmd_susceptible = True
            ptc_info = detect_ptc_in_exon_skipping()

        elif junction_type == 'intron_retention':
            # Extract intron number
            intron_num = int(junction_name.split('intron')[1].split('_')[0])
            ptc_info = detect_ptc_in_retained_intron(intron_num)
            nmd_susceptible = ptc_info.get('nmd_triggered', True)

        elif junction_type == 'cryptic':
            # Cryptic sites: assume NMD-susceptible (conservative)
            nmd_susceptible = True
            ptc_info = {'mechanism': 'Cryptic splice site, PTC likely'}

        else:
            nmd_susceptible = False
            ptc_info = None

        results.append({
            'junction_start': row['start'],
            'junction_end': row['end'],
            'junction_type': junction_type,
            'junction_name': junction_name,
            'reads': reads,
            'nmd_susceptible': nmd_susceptible,
            'ptc_info': ptc_info
        })

    return pd.DataFrame(results)

def summarize_nmd_analysis(nmd_df):
    """Generate summary statistics"""
    total_reads = nmd_df['reads'].sum()
    canonical_reads = nmd_df[nmd_df['junction_type'] == 'canonical']['reads'].sum()
    aberrant_reads = nmd_df[nmd_df['junction_type'] != 'canonical']['reads'].sum()
    nmd_susceptible_reads = nmd_df[nmd_df['nmd_susceptible'] == True]['reads'].sum()

    # Calculate fractions
    aberrant_fraction = (aberrant_reads / total_reads * 100) if total_reads > 0 else 0
    nmd_susceptible_fraction = (nmd_susceptible_reads / total_reads * 100) if total_reads > 0 else 0

    # NMD efficiency (what % of aberrant transcripts are NMD-susceptible)
    nmd_efficiency = (nmd_susceptible_reads / aberrant_reads * 100) if aberrant_reads > 0 else 0

    summary = {
        'total_reads': total_reads,
        'canonical_reads': canonical_reads,
        'aberrant_reads': aberrant_reads,
        'nmd_susceptible_reads': nmd_susceptible_reads,
        'aberrant_fraction_%': aberrant_fraction,
        'nmd_susceptible_fraction_%': nmd_susceptible_fraction,
        'nmd_efficiency_%': nmd_efficiency
    }

    return summary

def main(sj_files, output_dir='D:/ДНК/data/nmd_analysis'):
    """
    Main NMD analysis pipeline

    Args:
        sj_files: List of STAR SJ.out.tab files (WT, D3, A2)
        output_dir: Output directory for results
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    print("="*70)
    print("NMD Susceptibility Analysis for HBB Locus")
    print("="*70)

    all_results = []

    for sj_file in sj_files:
        sample_name = Path(sj_file).stem.replace('_SJ.out', '')
        print(f"\n📊 Analyzing sample: {sample_name}")

        # Load junctions
        junctions_df = load_splice_junctions(sj_file)

        if len(junctions_df) == 0:
            print(f"  ⚠️  No junctions found in HBB region")
            continue

        # Classify and analyze NMD
        nmd_df = calculate_nmd_susceptibility(junctions_df)

        # Summarize
        summary = summarize_nmd_analysis(nmd_df)
        summary['sample'] = sample_name

        # Print results
        print(f"\n  Results:")
        print(f"    Total reads: {summary['total_reads']:,}")
        print(f"    Canonical:   {summary['canonical_reads']:,} ({100-summary['aberrant_fraction_%']:.1f}%)")
        print(f"    Aberrant:    {summary['aberrant_reads']:,} ({summary['aberrant_fraction_%']:.1f}%)")
        print(f"    NMD-susceptible: {summary['nmd_susceptible_reads']:,} ({summary['nmd_susceptible_fraction_%']:.1f}%)")
        print(f"    NMD efficiency:  {summary['nmd_efficiency_%']:.1f}%")

        # Save detailed results
        nmd_df.to_csv(f"{output_dir}/{sample_name}_nmd_details.csv", index=False)
        all_results.append(summary)

    # Compare samples
    if len(all_results) > 1:
        print("\n" + "="*70)
        print("COMPARISON ACROSS SAMPLES")
        print("="*70)

        comparison_df = pd.DataFrame(all_results)
        comparison_df = comparison_df.set_index('sample')

        print("\nAberrant Splicing % (includes all non-canonical junctions):")
        print(comparison_df[['aberrant_fraction_%']].to_string())

        print("\nNMD-Susceptible % (aberrant junctions that trigger NMD):")
        print(comparison_df[['nmd_susceptible_fraction_%']].to_string())

        # Save comparison
        comparison_df.to_csv(f"{output_dir}/nmd_comparison_summary.csv")

        # Hypothesis test
        print("\n" + "="*70)
        print("HYPOTHESIS TEST: 'Loop That Stayed'")
        print("="*70)

        # Check if D3 shows high NMD-susceptible fraction
        if 'D3' in comparison_df.index:
            d3_nmd = comparison_df.loc['D3', 'nmd_susceptible_fraction_%']
            wt_nmd = comparison_df.loc[comparison_df.index.str.contains('WT', case=False), 'nmd_susceptible_fraction_%'].mean()

            fold_change = d3_nmd / wt_nmd if wt_nmd > 0 else float('inf')

            print(f"\nD3 NMD-susceptible fraction: {d3_nmd:.1f}%")
            print(f"WT NMD-susceptible fraction: {wt_nmd:.1f}%")
            print(f"Fold change: {fold_change:.2f}×")

            if d3_nmd >= 15:  # Threshold from hypothesis
                print(f"\n✅ HYPOTHESIS SUPPORTED")
                print(f"   D3 shows ≥15% NMD-susceptible transcripts")
                print(f"   Loop disruption → aberrant splicing → NMD")
            else:
                print(f"\n⚠️  HYPOTHESIS CHALLENGED")
                print(f"   D3 shows <15% NMD-susceptible transcripts")
                print(f"   Alternative mechanism may be involved")

        # Check A2 (control)
        if 'A2' in comparison_df.index:
            a2_nmd = comparison_df.loc['A2', 'nmd_susceptible_fraction_%']

            print(f"\nA2 (inversion control) NMD-susceptible: {a2_nmd:.1f}%")

            if a2_nmd < 10:  # Expected for preserved loop
                print(f"✅ A2 control as expected (<10% aberrant)")
            else:
                print(f"⚠️  A2 also shows elevated aberrant splicing")

    print("\n" + "="*70)
    print(f"Analysis complete. Results saved to: {output_dir}")
    print("="*70)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Analyze NMD susceptibility from STAR splice junctions')
    parser.add_argument('sj_files', nargs='+', help='STAR SJ.out.tab files')
    parser.add_argument('--output-dir', default='D:/ДНК/data/nmd_analysis', help='Output directory')

    args = parser.parse_args()

    main(args.sj_files, args.output_dir)
