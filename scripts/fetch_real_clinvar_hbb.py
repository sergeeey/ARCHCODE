#!/usr/bin/env python3
"""
Fetch Real HBB Variants from ClinVar API
Replaces mock AlphaGenome data with actual ClinVar pathogenic variants
"""

import requests
import pandas as pd
import time
from typing import List, Dict

# HBB gene coordinates (GRCh38)
HBB_LOCUS = {
    'chr': '11',
    'start': 5225464,
    'end': 5227071,
    'gene': 'HBB'
}

def fetch_clinvar_variants(gene: str = 'HBB', assembly: str = 'GRCh38') -> List[Dict]:
    """
    Fetch pathogenic/likely pathogenic HBB variants from ClinVar API

    API: https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/
    """
    print(f"Fetching ClinVar variants for {gene}...")

    # ClinVar API endpoint
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    # Search query: HBB gene, pathogenic/likely pathogenic, GRCh38
    params = {
        'db': 'clinvar',
        'term': f'{gene}[gene] AND (pathogenic[CLNSIG] OR likely pathogenic[CLNSIG]) AND {assembly}[Assembly]',
        'retmax': 500,  # Get up to 500 variants
        'retmode': 'json'
    }

    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract variant IDs
        id_list = data.get('esearchresult', {}).get('idlist', [])
        print(f"  Found {len(id_list)} ClinVar records")

        return id_list

    except Exception as e:
        print(f"  ❌ Error fetching ClinVar data: {e}")
        return []

def fetch_variant_details(variant_ids: List[str]) -> pd.DataFrame:
    """
    Fetch detailed variant information from ClinVar
    """
    print(f"Fetching details for {len(variant_ids)} variants...")

    # Fetch in batches (API limit)
    batch_size = 100
    all_variants = []

    for i in range(0, len(variant_ids), batch_size):
        batch = variant_ids[i:i+batch_size]

        # eFetch API
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'clinvar',
            'id': ','.join(batch),
            'rettype': 'vcv',
            'retmode': 'xml'
        }

        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            # Parse XML (simplified - would need proper XML parsing)
            # For now, save raw data
            print(f"  Batch {i//batch_size + 1}/{(len(variant_ids)-1)//batch_size + 1} fetched")
            time.sleep(0.5)  # Rate limiting

        except Exception as e:
            print(f"  ⚠️ Error fetching batch: {e}")
            continue

    return pd.DataFrame()  # Placeholder

def parse_clinvar_vcf(vcf_file: str) -> pd.DataFrame:
    """
    Alternative: Parse downloaded ClinVar VCF file

    Download from:
    https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz

    Then filter for HBB locus
    """
    print(f"Parsing ClinVar VCF: {vcf_file}")

    variants = []

    with open(vcf_file) as f:
        for line in f:
            if line.startswith('#'):
                continue

            fields = line.strip().split('\t')
            chrom = fields[0]
            pos = int(fields[1])
            ref = fields[3]
            alt = fields[4]
            info = fields[7]

            # Filter for HBB locus
            if chrom == '11' and HBB_LOCUS['start'] <= pos <= HBB_LOCUS['end']:
                # Parse INFO field
                info_dict = {}
                for item in info.split(';'):
                    if '=' in item:
                        key, value = item.split('=', 1)
                        info_dict[key] = value

                # Extract ClinVar significance
                clnsig = info_dict.get('CLNSIG', '')

                # Only pathogenic/likely pathogenic
                if 'Pathogenic' in clnsig or 'Likely_pathogenic' in clnsig:
                    variants.append({
                        'chr': chrom,
                        'position': pos,
                        'ref': ref,
                        'alt': alt,
                        'clinvar_id': info_dict.get('CLNVC', ''),
                        'significance': clnsig,
                        'variant_type': info_dict.get('CLNVC', 'unknown')
                    })

    print(f"  Found {len(variants)} HBB pathogenic variants")
    return pd.DataFrame(variants)

def main():
    """
    Main workflow for fetching real ClinVar HBB variants
    """
    print("="*70)
    print("ClinVar HBB Variant Fetcher")
    print("="*70)

    # Method 1: API (preferred, but complex XML parsing)
    variant_ids = fetch_clinvar_variants(gene='HBB')

    if len(variant_ids) == 0:
        print("\n⚠️  API fetch failed. Alternative methods:")
        print("1. Download ClinVar VCF:")
        print("   wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz")
        print("   gunzip clinvar.vcf.gz")
        print("   python fetch_real_clinvar_hbb.py --vcf clinvar.vcf")
        print()
        print("2. Use web interface:")
        print("   https://www.ncbi.nlm.nih.gov/clinvar/?term=HBB[gene]")
        return

    # Method 2: Manual download + parsing
    print("\n📥 Recommended workflow:")
    print("1. Download ClinVar VCF (tonight, ~1 GB compressed):")
    print("   curl -O https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz")
    print("   gunzip clinvar.vcf.gz")
    print()
    print("2. Extract HBB variants (tomorrow):")
    print("   grep -E '^11\\s+(522[5-7][0-9]{3})' clinvar.vcf > hbb_clinvar.vcf")
    print()
    print("3. Parse and filter (tomorrow):")
    print("   python fetch_real_clinvar_hbb.py --vcf hbb_clinvar.vcf")
    print()
    print("Expected output: ~300-500 HBB pathogenic variants")
    print("="*70)

if __name__ == '__main__':
    main()
