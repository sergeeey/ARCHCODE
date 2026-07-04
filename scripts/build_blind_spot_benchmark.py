#!/usr/bin/env python3
"""
ARCHCODE Blind Spot Benchmark Builder

Creates a benchmark dataset for evaluating structural blind spot detection.
This script processes ARCHCODE results and generates a standardized benchmark.

Usage:
    python scripts/build_blind_spot_benchmark.py

Output:
    results/blind_spot_benchmark_v1.0/
    ├── benchmark_variants.tsv
    ├── benchmark_summary.json
    └── README.md
"""

import json
import csv
from datetime import datetime
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

RESULTS_DIR = Path("results")
OUTPUT_DIR = RESULTS_DIR / "blind_spot_benchmark_v1.0"

# Input files (from unified atlas pipeline)
INPUT_FILES = {
    "hbb": RESULTS_DIR / "HBB_Unified_Atlas.csv",
    "brca1": RESULTS_DIR / "BRCA1_Unified_Atlas.csv",
    "cftr": RESULTS_DIR / "CFTR_Unified_Atlas.csv",
    "tp53": RESULTS_DIR / "TP53_Unified_Atlas.csv",
    "mlh1": RESULTS_DIR / "MLH1_Unified_Atlas.csv",
}

# Pearl definition thresholds
PEARL_THRESHOLDS = {
    "vep_max": 0.30,      # VEP score < 0.30 = blind
    "lssim_max": 0.95,    # LSSIM < 0.95 = structurally disruptive
    "cadd_ambiguous_min": 10,  # CADD phred 10-20 = ambiguous zone
    "cadd_ambiguous_max": 20,
}

# ============================================================================
# Data Loading
# ============================================================================

def load_atlas(filepath: Path) -> list:
    """Load unified atlas CSV file."""
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return []
    
    variants = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            variants.append(row)
    
    print(f"✅ Loaded {len(variants)} variants from {filepath.name}")
    return variants


def load_integrative_benchmark() -> dict:
    """Load CADD integrative benchmark summary."""
    filepath = RESULTS_DIR / "integrative_benchmark_summary.json"
    if not filepath.exists():
        print(f"⚠️  File not found: {filepath}")
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
    
# ============================================================================
# Pearl Detection
# ============================================================================

def is_pearl_variant(variant: dict) -> bool:
    """
    Determine if a variant is a 'pearl' (ARCHCODE-only detection).
    
    Pearl criteria:
    1. VEP score < 0.30 (VEP-blind)
    2. LSSIM < 0.95 (structurally disruptive)
    3. ClinVar pathogenic or likely pathogenic
    """
    try:
        # Column names from HBB_Unified_Atlas.csv
        vep_score = float(variant.get("VEP_Score", 0.99))
        lssim = float(variant.get("ARCHCODE_LSSIM", 1.0))
        clinvar_sig = variant.get("ClinVar_Significance", "").lower()
        
        # VEP-blind
        if vep_score >= PEARL_THRESHOLDS["vep_max"]:
            return False
        
        # Structurally disruptive
        if lssim >= PEARL_THRESHOLDS["lssim_max"]:
            return False
        
        # Pathogenic or likely pathogenic
        if not any(x in clinvar_sig for x in ["pathogenic", "likely pathogenic"]):
            return False
        
        return True
    
    except (ValueError, TypeError):
        return False


def classify_quadrant(variant: dict) -> str:
    """
    Classify variant into discordance quadrant.
    
    Q1: Both detect (VEP < 0.30 AND LSSIM >= 0.95)
    Q2: ARCHCODE only (VEP >= 0.30 AND LSSIM < 0.95) ← PEARLS
    Q3: VEP only (VEP < 0.30 AND LSSIM >= 0.95)
    Q4: Neither (VEP >= 0.30 AND LSSIM >= 0.95)
    """
    try:
        # Column names from HBB_Unified_Atlas.csv
        vep_score = float(variant.get("VEP_Score", 0.99))
        lssim = float(variant.get("ARCHCODE_LSSIM", 1.0))
        
        vep_detects = vep_score < 0.30
        archcode_detects = lssim < 0.95
        
        if vep_detects and archcode_detects:
            return "Q1_BOTH_DETECT"
        elif not vep_detects and archcode_detects:
            return "Q2_ARCHCODE_ONLY"  # Pearls
        elif vep_detects and not archcode_detects:
            return "Q3_VEP_ONLY"
        else:
            return "Q4_NEITHER"
    
    except (ValueError, TypeError):
        return "UNKNOWN"

# ============================================================================
# Benchmark Generation
# ============================================================================

def build_benchmark():
    """Build the complete blind spot benchmark dataset."""
    
    print("=" * 70)
    print("  ARCHCODE Blind Spot Benchmark Builder v1.0")
    print("=" * 70)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print()
    
    # Load all atlases
    all_variants = {}
    for locus, filepath in INPUT_FILES.items():
        variants = load_atlas(filepath)
        if variants:
            all_variants[locus] = variants
    
    if not all_variants:
        print("❌ No input files found. Run generate-unified-atlas.ts first.")
        return
    
    print()
    print(f"📊 Loaded {len(all_variants)} loci")
    print()
    
    # Process variants
    benchmark_variants = []
    quadrant_counts = {
        "Q1_BOTH_DETECT": 0,
        "Q2_ARCHCODE_ONLY": 0,
        "Q3_VEP_ONLY": 0,
        "Q4_NEITHER": 0,
    }
    pearl_variants = []
    
    for locus, variants in all_variants.items():
        print(f"🔬 Processing {locus.upper()}...")
        
        for variant in variants:
            quadrant = classify_quadrant(variant)
            is_pearl = is_pearl_variant(variant)
            
            quadrant_counts[quadrant] += 1
            
            if is_pearl:
                pearl_variants.append({
                    "locus": locus,
                    "variant": variant,
                })
            
            # Add to benchmark (subset: pathogenic + VUS)
            clinvar_sig = variant.get("ClinVar_Significance", "").lower()
            if any(x in clinvar_sig for x in ["pathogenic", "likely pathogenic", "vus"]):
                benchmark_variants.append({
                    "locus": locus,
                    "clinvar_id": variant.get("ClinVar_ID", ""),
                    "hgvs_c": variant.get("HGVS_c", ""),
                    "chrom": "chr11",  # HBB is on chr11
                    "pos": variant.get("Position_GRCh38", ""),
                    "ref": variant.get("Ref", ""),
                    "alt": variant.get("Alt", ""),
                    "lssim": variant.get("ARCHCODE_LSSIM", ""),
                    "vep_score": variant.get("VEP_Score", ""),
                    "cadd_phred": variant.get("CADD_Phred", ""),
                    "category": variant.get("Category", ""),
                    "clinvar_significance": variant.get("ClinVar_Significance", ""),
                    "quadrant": quadrant,
                    "pearl": is_pearl,
                })
        
        print(f"   Quadrants: Q1={quadrant_counts['Q1_BOTH_DETECT']}, "
              f"Q2={quadrant_counts['Q2_ARCHCODE_ONLY']}, "
              f"Q3={quadrant_counts['Q3_VEP_ONLY']}, "
              f"Q4={quadrant_counts['Q4_NEITHER']}")
    
    print()
    print(f"✨ Total pearls discovered: {len(pearl_variants)}")
    print()
    
    # Write benchmark TSV
    tsv_path = OUTPUT_DIR / "benchmark_variants.tsv"
    with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
        if benchmark_variants:
            writer = csv.DictWriter(f, fieldnames=benchmark_variants[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(benchmark_variants)
    
    print(f"📄 Written: {tsv_path} ({len(benchmark_variants)} variants)")
    
    # Write summary JSON
    summary = {
        "version": "1.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "thresholds": PEARL_THRESHOLDS,
        "quadrant_counts": quadrant_counts,
        "total_variants": len(benchmark_variants),
        "total_pearls": len(pearl_variants),
        "pearls_by_locus": {},
        "blind_spot_detection_rate": 0.0,
    }
    
    # Count pearls by locus
    for pearl in pearl_variants:
        locus = pearl["locus"]
        if locus not in summary["pearls_by_locus"]:
            summary["pearls_by_locus"][locus] = []
        summary["pearls_by_locus"][locus].append({
            "clinvar_id": pearl["variant"].get("ClinVar_ID", ""),
            "hgvs_c": pearl["variant"].get("HGVS_c", ""),
            "lssim": str(pearl["variant"].get("ARCHCODE_LSSIM", "")),
            "vep_score": str(pearl["variant"].get("VEP_Score", "")),
        })
    
    # Calculate blind spot detection rate
    # (proportion of pathogenic variants in Q2)
    pathogenic_in_q2 = sum(1 for v in benchmark_variants 
                          if v["quadrant"] == "Q2_ARCHCODE_ONLY" 
                          and "pathogenic" in v["clinvar_significance"].lower())
    total_pathogenic = sum(1 for v in benchmark_variants 
                          if "pathogenic" in v["clinvar_significance"].lower())
    
    if total_pathogenic > 0:
        summary["blind_spot_detection_rate"] = pathogenic_in_q2 / total_pathogenic
    
    summary_path = OUTPUT_DIR / "benchmark_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📄 Written: {summary_path}")
    
    # Write README
    readme_path = OUTPUT_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(f"""# ARCHCODE Blind Spot Benchmark v1.0

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d')}

## Overview

This benchmark dataset evaluates the ability of variant effect predictors to detect
structural variants that are invisible to sequence-based methods.

## Pearl Definition

A "pearl" variant meets all criteria:
- **VEP score < 0.30** (sequence-blind)
- **LSSIM < 0.95** (structurally disruptive)
- **ClinVar: Pathogenic or Likely Pathogenic**

## Statistics

| Metric | Value |
|--------|-------|
| Total variants | {summary['total_variants']} |
| Total pearls | {summary['total_pearls']} |
| Blind spot detection rate | {summary['blind_spot_detection_rate']:.2%} |

## Quadrant Distribution

| Quadrant | Description | Count |
|----------|-------------|-------|
| Q1 | Both detect | {quadrant_counts['Q1_BOTH_DETECT']} |
| Q2 | ARCHCODE only (pearls) | {quadrant_counts['Q2_ARCHCODE_ONLY']} |
| Q3 | VEP only | {quadrant_counts['Q3_VEP_ONLY']} |
| Q4 | Neither | {quadrant_counts['Q4_NEITHER']} |

## Pearls by Locus

""")
        for locus, pearls in summary["pearls_by_locus"].items():
            f.write(f"### {locus.upper()} ({len(pearls)} pearls)\n\n")
            for p in pearls[:5]:  # Show top 5
                f.write(f"- {p['clinvar_id']}: {p['hgvs_c']} "
                       f"(LSSIM={p['lssim']}, VEP={p['vep_score']})\n")
            if len(pearls) > 5:
                f.write(f"- ... and {len(pearls) - 5} more\n")
            f.write("\n")
        
        f.write("""## Usage

### Baseline Comparison

Compare sequence-based predictors (VEP, SpliceAI, CADD) against ARCHCODE:

```python
import pandas as pd

df = pd.read_csv("benchmark_variants.tsv", sep="\\t")

# Blind spot detection rate
pearls = df[df["pearl"] == True]
print(f"Blind spot rate: {len(pearls) / len(df):.2%}")

# By locus
for locus in df["locus"].unique():
    locus_df = df[df["locus"] == locus]
    locus_pearls = locus_df[locus_df["pearl"] == True]
    print(f"{locus}: {len(locus_pearls)} pearls ({len(locus_pearls) / len(locus_df):.2%})")
```

## Citation

If you use this benchmark, please cite:

```
Boyko, S.V. ARCHCODE reveals structural blind spot in variant interpretation.
Preprint planned; DOI to be added upon submission.
```

## License

MIT License - See LICENSE file in main repository.
""")
    
    print(f"📄 Written: {readme_path}")
    
    # Print summary
    print()
    print("=" * 70)
    print("  Benchmark Complete")
    print("=" * 70)
    print()
    print(f"📊 Total variants: {summary['total_variants']}")
    print(f"🔬 Total pearls: {summary['total_pearls']}")
    print(f"📈 Blind spot detection rate: {summary['blind_spot_detection_rate']:.2%}")
    print()
    print("📁 Output files:")
    print(f"   - {tsv_path}")
    print(f"   - {summary_path}")
    print(f"   - {readme_path}")
    print()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    build_benchmark()
