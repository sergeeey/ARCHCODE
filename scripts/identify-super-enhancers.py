#!/usr/bin/env python3
"""
Super-Enhancer Identification from BigWig files.

This script implements the ROSE algorithm concept:
1. Identify peaks (regions with signal above threshold)
2. Stitch nearby peaks within 12.5kb
3. Rank by total signal
4. Find inflection point (hockey stick) to separate SE from typical enhancers

Input: H3K27ac BigWig (primary) + MED1 BigWig (optional validation)
Output: BED file with Super-Enhancer coordinates
"""

import sys
import os
import argparse
import numpy as np

def check_dependencies():
    """Check if pyBigWig is installed."""
    try:
        import pyBigWig
        return True
    except ImportError:
        print("ERROR: pyBigWig not installed. Install with: pip install pyBigWig")
        return False

def load_bigwig_signal(bw_path, chrom, start, end, resolution=1000):
    """Load signal from BigWig file."""
    import pyBigWig
    bw = pyBigWig.open(bw_path)

    # Get values
    values = bw.values(chrom, start, end)
    bw.close()

    if values is None:
        return np.zeros((end - start) // resolution)

    # Convert to numpy and handle NaN
    values = np.array(values)
    values = np.nan_to_num(values, nan=0.0)

    # Bin the values
    n_bins = (end - start) // resolution
    binned = np.zeros(n_bins)
    for i in range(n_bins):
        bin_start = i * resolution
        bin_end = min((i + 1) * resolution, len(values))
        if bin_start < len(values):
            binned[i] = np.mean(values[bin_start:bin_end])

    return binned

def call_peaks(signal, threshold_percentile=90, min_width=2):
    """Call peaks based on signal threshold."""
    threshold = np.percentile(signal[signal > 0], threshold_percentile) if np.any(signal > 0) else 0

    peaks = []
    in_peak = False
    peak_start = 0

    for i, val in enumerate(signal):
        if val > threshold and not in_peak:
            in_peak = True
            peak_start = i
        elif val <= threshold and in_peak:
            in_peak = False
            if i - peak_start >= min_width:
                peaks.append((peak_start, i, np.sum(signal[peak_start:i])))

    # Handle peak at end
    if in_peak and len(signal) - peak_start >= min_width:
        peaks.append((peak_start, len(signal), np.sum(signal[peak_start:])))

    return peaks

def stitch_peaks(peaks, stitch_distance=12):
    """Stitch peaks within stitch_distance bins."""
    if not peaks:
        return []

    # Sort by start position
    peaks = sorted(peaks, key=lambda x: x[0])

    stitched = []
    current_start, current_end, current_signal = peaks[0]

    for start, end, signal in peaks[1:]:
        if start - current_end <= stitch_distance:
            # Stitch
            current_end = end
            current_signal += signal
        else:
            # Save current and start new
            stitched.append((current_start, current_end, current_signal))
            current_start, current_end, current_signal = start, end, signal

    # Don't forget the last one
    stitched.append((current_start, current_end, current_signal))

    return stitched

def find_inflection_point(signals):
    """Find the inflection point using the hockey stick method."""
    if len(signals) < 3:
        return 0

    # Sort signals
    sorted_signals = np.sort(signals)[::-1]

    # Normalize to 0-1 range
    x = np.arange(len(sorted_signals)) / len(sorted_signals)
    y = sorted_signals / sorted_signals[0] if sorted_signals[0] > 0 else sorted_signals

    # Find point with maximum distance from diagonal
    diagonal = 1 - x
    distances = np.abs(y - diagonal)

    inflection_idx = np.argmax(distances)

    # Return the signal value at inflection point
    return sorted_signals[inflection_idx]

def identify_super_enhancers(bw_path, output_bed, genome='hg38', resolution=1000, stitch_kb=12.5):
    """Main function to identify super-enhancers."""
    import pyBigWig

    print(f"Loading BigWig: {bw_path}")
    bw = pyBigWig.open(bw_path)

    # Get chromosome sizes
    chroms = bw.chroms()
    bw.close()

    # Filter to main chromosomes
    main_chroms = [c for c in chroms.keys() if c.startswith('chr') and c[3:].isdigit() or c in ['chrX', 'chrY']]
    main_chroms = sorted(main_chroms, key=lambda x: (0, int(x[3:])) if x[3:].isdigit() else (1, x))

    print(f"Processing {len(main_chroms)} chromosomes...")

    all_enhancers = []
    stitch_bins = int(stitch_kb * 1000 / resolution)

    for chrom in main_chroms:
        chrom_size = chroms[chrom]

        # Load signal
        signal = load_bigwig_signal(bw_path, chrom, 0, chrom_size, resolution)

        if np.sum(signal) == 0:
            continue

        # Call peaks
        peaks = call_peaks(signal, threshold_percentile=85, min_width=2)

        # Stitch peaks
        stitched = stitch_peaks(peaks, stitch_distance=stitch_bins)

        # Convert to genomic coordinates
        for start_bin, end_bin, total_signal in stitched:
            start_bp = start_bin * resolution
            end_bp = end_bin * resolution
            all_enhancers.append({
                'chrom': chrom,
                'start': start_bp,
                'end': end_bp,
                'signal': total_signal,
                'length': end_bp - start_bp
            })

        print(f"  {chrom}: {len(stitched)} stitched regions")

    print(f"\nTotal enhancer regions: {len(all_enhancers)}")

    if not all_enhancers:
        print("No enhancers found!")
        return []

    # Find inflection point
    signals = np.array([e['signal'] for e in all_enhancers])
    inflection_signal = find_inflection_point(signals)

    print(f"Inflection point signal: {inflection_signal:.2f}")

    # Classify as Super-Enhancer or Typical Enhancer
    super_enhancers = []
    typical_enhancers = []

    for e in all_enhancers:
        if e['signal'] >= inflection_signal:
            e['type'] = 'SE'
            super_enhancers.append(e)
        else:
            e['type'] = 'TE'
            typical_enhancers.append(e)

    # Sort by signal (descending)
    super_enhancers = sorted(super_enhancers, key=lambda x: -x['signal'])

    print(f"\nSuper-Enhancers: {len(super_enhancers)}")
    print(f"Typical Enhancers: {len(typical_enhancers)}")

    # Write BED file
    with open(output_bed, 'w') as f:
        f.write("#chrom\tstart\tend\tname\tscore\tstrand\tsignal\ttype\n")

        for i, se in enumerate(super_enhancers):
            name = f"SE_{i+1}_{se['chrom']}"
            score = min(1000, int(se['signal']))
            f.write(f"{se['chrom']}\t{se['start']}\t{se['end']}\t{name}\t{score}\t.\t{se['signal']:.2f}\tSE\n")

    print(f"\nSuper-Enhancers written to: {output_bed}")

    # Also write all enhancers for reference
    all_bed = output_bed.replace('.bed', '_all.bed')
    with open(all_bed, 'w') as f:
        f.write("#chrom\tstart\tend\tname\tscore\tstrand\tsignal\ttype\n")

        all_sorted = sorted(all_enhancers, key=lambda x: -x['signal'])
        for i, e in enumerate(all_sorted):
            name = f"{e['type']}_{i+1}_{e['chrom']}"
            score = min(1000, int(e['signal']))
            f.write(f"{e['chrom']}\t{e['start']}\t{e['end']}\t{name}\t{score}\t.\t{e['signal']:.2f}\t{e['type']}\n")

    print(f"All enhancers written to: {all_bed}")

    # Print top 20 Super-Enhancers
    print("\n" + "="*70)
    print("TOP 20 SUPER-ENHANCERS")
    print("="*70)
    print(f"{'Rank':<6}{'Chrom':<8}{'Start':<12}{'End':<12}{'Length':<10}{'Signal':<12}")
    print("-"*70)

    for i, se in enumerate(super_enhancers[:20]):
        print(f"{i+1:<6}{se['chrom']:<8}{se['start']:<12}{se['end']:<12}{se['length']:<10}{se['signal']:<12.1f}")

    return super_enhancers

def main():
    parser = argparse.ArgumentParser(description='Identify Super-Enhancers from BigWig')
    parser.add_argument('--h3k27ac', required=True, help='H3K27ac BigWig file')
    parser.add_argument('--med1', help='MED1 BigWig file (optional, for validation)')
    parser.add_argument('--output', '-o', required=True, help='Output BED file')
    parser.add_argument('--resolution', type=int, default=1000, help='Bin resolution in bp (default: 1000)')
    parser.add_argument('--stitch', type=float, default=12.5, help='Stitch distance in kb (default: 12.5)')

    args = parser.parse_args()

    if not check_dependencies():
        sys.exit(1)

    if not os.path.exists(args.h3k27ac):
        print(f"ERROR: H3K27ac file not found: {args.h3k27ac}")
        sys.exit(1)

    super_enhancers = identify_super_enhancers(
        args.h3k27ac,
        args.output,
        resolution=args.resolution,
        stitch_kb=args.stitch
    )

    # If MED1 provided, validate overlap
    if args.med1 and os.path.exists(args.med1):
        print("\n" + "="*70)
        print("VALIDATING WITH MED1 SIGNAL")
        print("="*70)

        import pyBigWig
        bw = pyBigWig.open(args.med1)

        for i, se in enumerate(super_enhancers[:10]):
            try:
                med1_signal = bw.stats(se['chrom'], se['start'], se['end'], type='mean')[0]
                med1_signal = med1_signal if med1_signal else 0
                print(f"SE_{i+1} ({se['chrom']}:{se['start']}-{se['end']}): MED1 = {med1_signal:.2f}")
            except:
                pass

        bw.close()

if __name__ == '__main__':
    main()
