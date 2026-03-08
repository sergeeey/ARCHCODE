#!/usr/bin/env python3
"""
Analyze CTCF ChIP-seq Signal at HBB Locus
Validate ARCHCODE predicted CTCF binding sites against experimental ChIP-seq

Input: BigWig files (GSE131055 CTCF ChIP-seq)
Output: CTCF signal at predicted vs actual binding sites
"""

import os
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Try importing pyBigWig
try:
    import pyBigWig
    PYBIGWIG_AVAILABLE = True
except ImportError:
    print("WARNING: pyBigWig not available. Will try alternative method.")
    PYBIGWIG_AVAILABLE = False

# Configuration
HBB_LOCUS = {
    'chr': '11',  # Note: BigWig may use "chr11" or "11"
    'start': 5_200_000,
    'end': 5_250_000
}

# CTCF sites from literature (from get_hbb_ctcf_literature.py)
LITERATURE_CTCF_SITES = [
    {"name": "HS5 (5'HS5)", "position": 5203300, "source": "ENCODE + Bender 2012"},
    {"name": "HS4 (5'HS4)", "position": 5205700, "source": "ENCODE + Bender 2012"},
    {"name": "HS3 (5'HS3)", "position": 5207100, "source": "ENCODE + Bender 2012"},
    {"name": "HS2 (5'HS2)", "position": 5209000, "source": "ENCODE + Bender 2012"},
    {"name": "Promoter (HBB)", "position": 5225700, "source": "ENCODE + Bender 2012"},
    {"name": "3'HS1", "position": 5247900, "source": "ENCODE + Bender 2012"}
]

# CTCF BigWig files
BIGWIG_FILES = {
    'HUDEP2_D3_CTCF': 'D:/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM3762814_1227501_Hudep2_D3_CTCF_R2_R1.bw',
    'CD34_D0_CTCF_R1': 'D:/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM3762801_1151782_CD34_D0_CTCF_R1_trim_50bp.bw',
    'CD34_D0_CTCF_R2': 'D:/ДНК/ДНК Образцы СКАЧЕННЫЙ/DNK OBRAZCI/GSM3762802_1151783_CD34_D0_CTCF_R2_trim_50bp.bw',
}

def extract_signal_pybigwig(bw_file, chrom, start, end):
    """Extract signal from BigWig using pyBigWig"""
    try:
        bw = pyBigWig.open(bw_file)

        # Try both "11" and "chr11" chromosome naming
        chroms = bw.chroms()
        if chrom in chroms:
            signal = bw.values(chrom, start, end, numpy=True)
        elif f"chr{chrom}" in chroms:
            signal = bw.values(f"chr{chrom}", start, end, numpy=True)
        else:
            print(f"ERROR: Chromosome {chrom} not found in {bw_file}")
            print(f"Available: {list(chroms.keys())[:5]}...")
            return None

        bw.close()
        return np.nan_to_num(signal)  # Replace NaN with 0

    except Exception as e:
        print(f"ERROR reading {bw_file}: {e}")
        return None

def extract_signal_ucsc_tools(bw_file, chrom, start, end):
    """Alternative: Extract using UCSC bigWigToBedGraph (if installed)"""
    import subprocess
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bedGraph', delete=False) as out_bg:
            out_path = out_bg.name

        # Security: never use shell=True with dynamic file paths.
        cmd = [
            "bigWigToBedGraph",
            bw_file,
            out_path,
            f"-chrom=chr{chrom}",
            f"-start={start}",
            f"-end={end}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Fallback for files using "11" chromosome naming instead of "chr11".
        if result.returncode != 0:
            cmd = [
                "bigWigToBedGraph",
                bw_file,
                out_path,
                f"-chrom={chrom}",
                f"-start={start}",
                f"-end={end}",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            signal = np.zeros(end - start)
            with open(out_path, 'r', encoding='utf-8') as fh:
                content = fh.read().strip()
            for line in content.split('\n'):
                if line:
                    parts = line.split('\t')
                    s, e, val = int(parts[1]), int(parts[2]), float(parts[3])
                    signal[s-start:e-start] = val
            return signal
        else:
            return None

    except Exception as e:
        print(f"ERROR with bigWigToBedGraph: {e}")
        return None
    finally:
        if 'out_path' in locals() and os.path.exists(out_path):
            os.unlink(out_path)

def get_peak_signal(signal_array, position, locus_start, window=500):
    """Get average signal in window around position"""
    if signal_array is None:
        return np.nan

    rel_pos = position - locus_start
    start_idx = max(0, rel_pos - window)
    end_idx = min(len(signal_array), rel_pos + window)

    if start_idx < len(signal_array) and end_idx > 0:
        return np.mean(signal_array[start_idx:end_idx])
    else:
        return np.nan

def analyze_ctcf_chipseq():
    """Main analysis function"""
    print("="*70)
    print("CTCF ChIP-seq Validation for ARCHCODE HBB Locus")
    print("="*70)

    results = []

    for sample_name, bw_path in BIGWIG_FILES.items():
        print(f"\n📊 Analyzing: {sample_name}")
        print(f"   File: {Path(bw_path).name}")

        if not os.path.exists(bw_path):
            print(f"   ⚠️  File not found, skipping")
            continue

        # Extract signal
        if PYBIGWIG_AVAILABLE:
            signal = extract_signal_pybigwig(bw_path, HBB_LOCUS['chr'],
                                            HBB_LOCUS['start'], HBB_LOCUS['end'])
        else:
            signal = extract_signal_ucsc_tools(bw_path, HBB_LOCUS['chr'],
                                              HBB_LOCUS['start'], HBB_LOCUS['end'])

        if signal is None:
            print(f"   ❌ Failed to extract signal")
            continue

        print(f"   ✅ Signal extracted: {len(signal)} bp")
        print(f"   Range: {np.min(signal):.2f} - {np.max(signal):.2f}")
        print(f"   Mean: {np.mean(signal):.2f}")

        # Check signal at each literature CTCF site
        print(f"\n   CTCF Sites:")
        for site in LITERATURE_CTCF_SITES:
            peak_signal = get_peak_signal(signal, site['position'],
                                         HBB_LOCUS['start'], window=500)

            print(f"   - {site['name']:20s} (chr11:{site['position']:,}): "
                  f"Signal = {peak_signal:.2f}")

            results.append({
                'sample': sample_name,
                'site_name': site['name'],
                'position': site['position'],
                'signal': peak_signal,
                'source': site['source']
            })

    # Save results
    df = pd.DataFrame(results)
    output_file = 'D:/ДНК/data/ctcf_chipseq_validation.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✅ Results saved to: {output_file}")

    # Summary statistics
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if len(df) > 0:
        pivot = df.pivot(index='site_name', columns='sample', values='signal')
        print("\nCTCF Signal at Each Site (Average across samples):")
        print(pivot.to_string())

        # Check which sites have strong signal (>threshold)
        threshold = df['signal'].quantile(0.75)  # Top 25%
        print(f"\nThreshold for 'strong' signal: {threshold:.2f} (75th percentile)")

        strong_sites = df.groupby('site_name')['signal'].mean()
        strong_sites = strong_sites[strong_sites > threshold].sort_values(ascending=False)

        print(f"\nSites with Strong CTCF Binding ({len(strong_sites)}/{len(LITERATURE_CTCF_SITES)}):")
        for site, signal in strong_sites.items():
            print(f"  ✅ {site:20s} Signal = {signal:.2f}")

        weak_sites = set(df['site_name'].unique()) - set(strong_sites.index)
        if weak_sites:
            print(f"\nSites with Weak/No CTCF Binding ({len(weak_sites)}/{len(LITERATURE_CTCF_SITES)}):")
            for site in weak_sites:
                avg_signal = df[df['site_name']==site]['signal'].mean()
                print(f"  ⚠️  {site:20s} Signal = {avg_signal:.2f}")

        # Calculate validation rate
        validation_rate = len(strong_sites) / len(LITERATURE_CTCF_SITES) * 100
        print(f"\n📊 Validation Rate: {validation_rate:.1f}% of predicted sites show strong CTCF binding")

        # Save summary
        summary = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'locus': f"chr{HBB_LOCUS['chr']}:{HBB_LOCUS['start']:,}-{HBB_LOCUS['end']:,}",
            'n_sites_tested': len(LITERATURE_CTCF_SITES),
            'n_sites_validated': len(strong_sites),
            'validation_rate_pct': validation_rate,
            'threshold': threshold,
            'samples_analyzed': list(BIGWIG_FILES.keys()),
            'strong_sites': list(strong_sites.index),
            'weak_sites': list(weak_sites)
        }

        with open('D:/ДНК/data/ctcf_chipseq_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n✅ Summary saved to: D:/ДНК/data/ctcf_chipseq_summary.json")

    else:
        print("\n❌ No results to analyze")

    print("\n" + "="*70)
    print("Analysis Complete")
    print("="*70)

    return df

if __name__ == '__main__':
    # Check dependencies
    if not PYBIGWIG_AVAILABLE:
        print("\n⚠️  WARNING: pyBigWig not installed")
        print("Install with: conda install -c bioconda pybigwig")
        print("Or: pip install pyBigWig")
        print("\nTrying alternative method with UCSC tools...")
        print("(Requires bigWigToBedGraph in PATH)\n")

    # Run analysis
    df = analyze_ctcf_chipseq()

    print("\n📋 Next Steps:")
    print("1. Check results in: data/ctcf_chipseq_validation.csv")
    print("2. Compare with ARCHCODE predictions")
    print("3. Calculate correlation: CTCF signal vs Loop strength")
    print("4. Add to manuscript as mechanistic validation")
