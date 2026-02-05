#!/usr/bin/env python3
"""
SpliceAI Predictions for HBB Variants
Replaces mock AlphaGenome scores with real splice impact predictions
"""

import pandas as pd
import numpy as np
from pathlib import Path

def install_spliceai():
    """
    Installation instructions (run at home)
    """
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  SpliceAI Installation (at home, requires internet)            ║
    ╚════════════════════════════════════════════════════════════════╝

    Step 1: Install SpliceAI
    ------------------------
    pip install spliceai

    Step 2: Download reference genome
    ----------------------------------
    # GRCh38 reference (needed for SpliceAI)
    wget http://hgdownload.cse.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz
    gunzip hg38.fa.gz

    Step 3: Download SpliceAI models
    ---------------------------------
    # Models automatically downloaded on first run (~500 MB)

    Step 4: Test installation
    --------------------------
    python -c "from spliceai.utils import get_delta_scores; print('OK')"

    ═══════════════════════════════════════════════════════════════
    """)

def run_spliceai_predictions(variants_file: str, reference_fasta: str, output_file: str):
    """
    Run SpliceAI on HBB variants

    Args:
        variants_file: CSV with columns [chr, position, ref, alt]
        reference_fasta: Path to hg38.fa
        output_file: Output CSV with SpliceAI scores
    """
    try:
        from spliceai.utils import get_delta_scores
    except ImportError:
        print("❌ SpliceAI not installed. Run install_spliceai() first.")
        return

    print("Loading variants...")
    variants_df = pd.read_csv(variants_file)

    print(f"Running SpliceAI on {len(variants_df)} variants...")
    print("This may take 10-30 minutes depending on variant count...")

    results = []

    for idx, row in variants_df.iterrows():
        # SpliceAI expects format: CHROM:POS:REF:ALT
        variant_str = f"{row['chr']}:{row['position']}:{row['ref']}:{row['alt']}"

        try:
            # Get splice impact scores
            scores = get_delta_scores(
                variant_str,
                reference_fasta,
                distance=50,  # Window around variant
                mask=0
            )

            # Extract max delta score (max impact on any splice site)
            max_score = max([
                scores['delta_scores'][0],  # Acceptor gain
                scores['delta_scores'][1],  # Acceptor loss
                scores['delta_scores'][2],  # Donor gain
                scores['delta_scores'][3]   # Donor loss
            ])

            results.append({
                'clinvar_id': row.get('clinvar_id', f"var_{idx}"),
                'position': row['position'],
                'ref': row['ref'],
                'alt': row['alt'],
                'spliceai_score': max_score,
                'acceptor_gain': scores['delta_scores'][0],
                'acceptor_loss': scores['delta_scores'][1],
                'donor_gain': scores['delta_scores'][2],
                'donor_loss': scores['delta_scores'][3],
                'interpretation': interpret_score(max_score)
            })

            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(variants_df)} variants...")

        except Exception as e:
            print(f"  ⚠️ Error processing {variant_str}: {e}")
            results.append({
                'clinvar_id': row.get('clinvar_id', f"var_{idx}"),
                'position': row['position'],
                'spliceai_score': np.nan,
                'interpretation': 'ERROR'
            })

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

    print(f"\n✅ SpliceAI predictions saved to: {output_file}")
    print(f"   Total variants: {len(results_df)}")
    print(f"   High impact (>0.5): {(results_df['spliceai_score'] > 0.5).sum()}")
    print(f"   Moderate impact (0.2-0.5): {((results_df['spliceai_score'] >= 0.2) & (results_df['spliceai_score'] <= 0.5)).sum()}")
    print(f"   Low impact (<0.2): {(results_df['spliceai_score'] < 0.2).sum()}")

    return results_df

def interpret_score(score: float) -> str:
    """
    Interpret SpliceAI score

    Thresholds from Jaganathan et al. 2019 (Cell):
    - >0.8: Very high impact
    - 0.5-0.8: High impact
    - 0.2-0.5: Moderate impact
    - <0.2: Low impact
    """
    if score >= 0.8:
        return 'Very High Impact'
    elif score >= 0.5:
        return 'High Impact'
    elif score >= 0.2:
        return 'Moderate Impact'
    else:
        return 'Low Impact'

def merge_with_archcode_results(archcode_file: str, spliceai_file: str, output_file: str):
    """
    Merge ARCHCODE SSIM predictions with SpliceAI scores

    Creates final comparison table for manuscript
    """
    print("Merging ARCHCODE and SpliceAI results...")

    archcode_df = pd.read_csv(archcode_file)
    spliceai_df = pd.read_csv(spliceai_file)

    # Merge on position
    merged_df = archcode_df.merge(
        spliceai_df,
        on='position',
        how='inner'
    )

    # Calculate concordance
    # ARCHCODE: low SSIM = pathogenic
    # SpliceAI: high score = pathogenic

    merged_df['archcode_pathogenic'] = merged_df['ARCHCODE_SSIM'] < 0.6
    merged_df['spliceai_pathogenic'] = merged_df['spliceai_score'] > 0.5

    merged_df['concordant'] = (
        merged_df['archcode_pathogenic'] == merged_df['spliceai_pathogenic']
    )

    concordance_rate = merged_df['concordant'].mean() * 100

    print(f"\n📊 Concordance Analysis:")
    print(f"   Total variants: {len(merged_df)}")
    print(f"   Concordant: {merged_df['concordant'].sum()} ({concordance_rate:.1f}%)")
    print(f"   ARCHCODE only: {(merged_df['archcode_pathogenic'] & ~merged_df['spliceai_pathogenic']).sum()}")
    print(f"   SpliceAI only: {(~merged_df['archcode_pathogenic'] & merged_df['spliceai_pathogenic']).sum()}")

    # Save merged results
    merged_df.to_csv(output_file, index=False)
    print(f"\n✅ Merged results saved to: {output_file}")

    return merged_df

def main():
    """
    Main workflow
    """
    import argparse

    parser = argparse.ArgumentParser(description='Run SpliceAI on HBB variants')
    parser.add_argument('--install', action='store_true', help='Show installation instructions')
    parser.add_argument('--variants', type=str, help='Input variants CSV')
    parser.add_argument('--reference', type=str, help='hg38.fa reference genome')
    parser.add_argument('--output', type=str, default='data/hbb_spliceai_results.csv',
                        help='Output file')

    args = parser.parse_args()

    if args.install:
        install_spliceai()
        return

    if not args.variants or not args.reference:
        print("Usage:")
        print("  python run_spliceai_hbb.py --install  # Show installation")
        print("  python run_spliceai_hbb.py --variants hbb_variants.csv --reference hg38.fa")
        return

    # Run SpliceAI
    results = run_spliceai_predictions(
        variants_file=args.variants,
        reference_fasta=args.reference,
        output_file=args.output
    )

    print("\n" + "="*70)
    print("SpliceAI Analysis Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Review results: data/hbb_spliceai_results.csv")
    print("2. Merge with ARCHCODE: merge_with_archcode_results(...)")
    print("3. Update manuscript figures and tables")

if __name__ == '__main__':
    main()
