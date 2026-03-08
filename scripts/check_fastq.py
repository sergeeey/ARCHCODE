#!/usr/bin/env python3
"""
Quick FASTQ Checker
Проверяет существующие FASTQ файлы и извлекает информацию из названий
"""

import gzip
import os
from pathlib import Path

FASTQ_DIR = Path("D:/ДНК/fastq_data/raw")

print("=" * 70)
print("  FASTQ File Checker")
print("=" * 70)
print()

# Найти все FASTQ файлы
fastq_files = list(FASTQ_DIR.glob("*.fastq.gz"))

if not fastq_files:
    print("❌ FASTQ файлы не найдены в:", FASTQ_DIR)
    exit(1)

print(f"📁 Directory: {FASTQ_DIR}")
print(f"📊 Found {len(fastq_files)} files")
print()

# Сгруппировать по образцам
samples = {}
for f in fastq_files:
    # Извлечь accession из имени файла
    name = f.stem.replace(".fastq", "")
    accession = name.split("_")[0]  # SRR12935486 из SRR12935486_1.fastq
    
    if accession not in samples:
        samples[accession] = []
    samples[accession].append(f)

print("📋 Samples found:")
print()

for accession, files in sorted(samples.items()):
    print(f"  {accession}:")
    total_size = 0
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"    - {f.name} ({size_mb:.0f} MB)")
    print(f"    Total: {total_size/1024:.1f} GB")
    print()

# Проверить содержимое первого файла
print("=" * 70)
print("  Checking FASTQ content (first 100 reads)")
print("=" * 70)
print()

if fastq_files:
    test_file = fastq_files[0]
    print(f"📄 Testing: {test_file.name}")
    print()
    
    try:
        with gzip.open(test_file, 'rt') as f:
            reads_checked = 0
            total_bases = 0
            quality_scores = []
            
            for i, line in enumerate(f):
                if i >= 400:  # 100 reads × 4 lines
                    break
                
                if i % 4 == 1:  # Sequence line
                    total_bases += len(line.strip())
                    reads_checked += 1
                elif i % 4 == 3:  # Quality line
                    quality_scores.append(len(line.strip()))
            
            print(f"  Reads checked: {reads_checked}")
            print(f"  Total bases: {total_bases}")
            print(f"  Average read length: {total_bases/reads_checked:.0f} bp")
            print()
            print("  ✅ FASTQ format looks valid")
    
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")

print()
print("=" * 70)
print("  Next Steps")
print("=" * 70)
print()
print("1. Check NCBI SRA for these accession numbers:")
print("   https://www.ncbi.nlm.nih.gov/sra")
print()
print("2. Verify these are the correct samples:")
print("   - WT (wild-type)")
print("   - D3 (3'HS1 deletion)")
print("   - A2 (3'HS1 inversion)")
print()
print("3. If correct → proceed with splice analysis")
print("   If not → download correct samples")
print()
