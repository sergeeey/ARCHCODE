/**
 * Download Real ClinVar HBB Variants
 *
 * Replaces synthetic dataset with real pathogenic variants from NCBI ClinVar.
 *
 * Data Source: ClinVar API + NCBI E-utilities
 * Gene: HBB (HGNC:4827)
 * Coordinates: chr11:5225464-5227079 (GRCh38)
 *
 * Output: data/clinvar_hbb_raw.json
 *
 * Usage: npx tsx scripts/download_clinvar_hbb.ts
 */

import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';

// HBB gene parameters
const HBB_GENE = {
    symbol: 'HBB',
    hgnc_id: 4827,
    gene_id: 3043,
    chromosome: 'chr11',
    start: 5225464,
    end: 5227079,
    assembly: 'GRCh38',
};

interface ClinVarVariant {
    vcv_id: string;
    variation_id: number;
    position: number;
    ref: string;
    alt: string;
    hgvs_genomic: string;
    hgvs_coding: string;
    hgvs_protein: string;
    molecular_consequence: string;
    clinical_significance: string;
    review_status: string;
    last_evaluated: string;
    submission_count: number;
}

/**
 * Download variants from ClinVar E-utilities API
 */
async function downloadClinVarVariants(): Promise<ClinVarVariant[]> {
    console.log('🔍 Searching ClinVar for HBB variants...');

    // Step 1: Search for HBB variants
    // esearch: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
    const searchQuery = `HBB[gene] AND ("clinsig pathogenic"[Properties] OR "clinsig likely pathogenic"[Properties])`;
    const searchUrl = `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=${encodeURIComponent(searchQuery)}&retmax=5000&retmode=json`;

    const searchResults = await fetchJSON(searchUrl);
    const variantIds = searchResults.esearchresult?.idlist || [];

    console.log(`✅ Found ${variantIds.length} pathogenic/likely pathogenic HBB variants`);

    if (variantIds.length === 0) {
        console.error('❌ No variants found. Check API or use VCF download instead.');
        process.exit(1);
    }

    // Step 2: Fetch detailed records in batches
    const variants: ClinVarVariant[] = [];
    const batchSize = 100;

    for (let i = 0; i < variantIds.length; i += batchSize) {
        const batch = variantIds.slice(i, i + batchSize);
        console.log(`📥 Downloading batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(variantIds.length / batchSize)}...`);

        const summaryUrl = `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=${batch.join(',')}&retmode=json`;

        try {
            const summaries = await fetchJSON(summaryUrl);

            for (const id of batch) {
                const variant = summaries.result?.[id];
                if (!variant) continue;

                // Extract variant details
                const variantData = parseVariantSummary(variant);
                if (variantData) {
                    variants.push(variantData);
                }
            }
        } catch (error) {
            console.error(`⚠️ Error fetching batch: ${error}`);
        }

        // Rate limiting (NCBI: 3 requests/second)
        await sleep(400);
    }

    console.log(`✅ Downloaded ${variants.length} detailed variant records`);
    return variants;
}

/**
 * Parse ClinVar variant summary
 */
function parseVariantSummary(data: any): ClinVarVariant | null {
    try {
        // Extract VCV accession
        const vcvAccession = data.accession || `VCV${String(data.uid).padStart(9, '0')}`;

        // Extract position from variant_set
        const variantSet = data.variation_set?.[0] || data;
        const position = variantSet.chr_coords?.[0]?.start || 0;

        // Filter: only variants within HBB locus
        if (position < HBB_GENE.start || position > HBB_GENE.end) {
            return null;
        }

        return {
            vcv_id: vcvAccession,
            variation_id: data.uid,
            position: position,
            ref: variantSet.chr_coords?.[0]?.reference_allele || 'N',
            alt: variantSet.chr_coords?.[0]?.alternate_allele || 'N',
            hgvs_genomic: variantSet.chr_coords?.[0]?.assembly_accession_version || '',
            hgvs_coding: data.canonical_spdi || '',
            hgvs_protein: data.protein_change || '',
            molecular_consequence: data.molecular_consequence || '',
            clinical_significance: data.clinical_significance?.description || '',
            review_status: data.clinical_significance?.review_status || '',
            last_evaluated: data.clinical_significance?.last_evaluated || '',
            submission_count: data.supporting_submissions?.length || 0,
        };
    } catch (error) {
        console.error(`⚠️ Error parsing variant: ${error}`);
        return null;
    }
}

/**
 * Fetch JSON from URL with retry
 */
async function fetchJSON(url: string, retries = 3): Promise<any> {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    if (retries > 0) {
                        console.log(`⚠️ Parse error, retrying... (${retries} left)`);
                        setTimeout(() => {
                            fetchJSON(url, retries - 1).then(resolve).catch(reject);
                        }, 1000);
                    } else {
                        reject(e);
                    }
                }
            });
        }).on('error', reject);
    });
}

/**
 * Sleep helper
 */
function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Main execution
 */
async function main() {
    console.log('═══════════════════════════════════════════');
    console.log('  ClinVar HBB Variant Download');
    console.log('═══════════════════════════════════════════');
    console.log(`Gene: ${HBB_GENE.symbol} (HGNC:${HBB_GENE.hgnc_id})`);
    console.log(`Locus: ${HBB_GENE.chromosome}:${HBB_GENE.start}-${HBB_GENE.end}`);
    console.log(`Assembly: ${HBB_GENE.assembly}`);
    console.log('');

    // Download variants
    const variants = await downloadClinVarVariants();

    // Save raw data
    const dataDir = path.join(__dirname, '..', 'data');
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }

    const outputPath = path.join(dataDir, 'clinvar_hbb_raw.json');
    fs.writeFileSync(outputPath, JSON.stringify({
        metadata: {
            gene: HBB_GENE,
            download_date: new Date().toISOString(),
            source: 'NCBI ClinVar E-utilities API',
            total_variants: variants.length,
        },
        variants,
    }, null, 2));

    console.log('');
    console.log('═══════════════════════════════════════════');
    console.log(`✅ Downloaded ${variants.length} variants`);
    console.log(`📁 Saved to: ${outputPath}`);
    console.log('═══════════════════════════════════════════');
    console.log('');
    console.log('📊 Summary by Clinical Significance:');

    const sigCounts = variants.reduce((acc, v) => {
        acc[v.clinical_significance] = (acc[v.clinical_significance] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    for (const [sig, count] of Object.entries(sigCounts)) {
        console.log(`  ${sig}: ${count}`);
    }

    console.log('');
    console.log('Next steps:');
    console.log('1. Run: npx tsx scripts/process_clinvar_hbb.ts');
    console.log('2. Then: npx tsx scripts/simulate_real_variants.ts');
}

main().catch(console.error);
