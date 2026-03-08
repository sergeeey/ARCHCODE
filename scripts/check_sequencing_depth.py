# check_sequencing_depth.py
import pandas as pd

print("=" * 60)
print("  Sequencing Depth Check — HBB Locus")
print("=" * 60)
print()

for name, f in [
    ("WT", "WT_junctions.bed"),
    ("B6", "B6_junctions.bed"),
    ("A2", "A2_junctions.bed")
]:
    filepath = f"D:/ДНК/fastq_data/junctions/{f}"
    
    # Load all chr11 junctions
    df = pd.read_csv(filepath, sep='\t', header=None)
    chr11 = df[df[0].astype(str).isin(['11', 'chr11'])]
    
    # Total HBB reads (column 7 = index 6)
    total_reads = chr11[6].sum()
    
    # Total HBB junctions
    total_junctions = len(chr11)
    
    # HBB locus only (5.22-5.23 Mb)
    hbb = chr11[(chr11[1] >= 5_220_000) & (chr11[1] <= 5_232_000)]
    hbb_reads = hbb[6].sum()
    hbb_junctions = len(hbb)
    
    print(f"{name}:")
    print(f"  Total chr11 reads: {total_reads:,}")
    print(f"  Total chr11 junctions: {total_junctions:,}")
    print(f"  HBB locus reads: {hbb_reads:,}")
    print(f"  HBB locus junctions: {hbb_junctions}")
    print()
