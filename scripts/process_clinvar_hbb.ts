/**
 * Process Real ClinVar HBB Variants for ARCHCODE
 *
 * Converts raw ClinVar JSON to structured format for simulation.
 *
 * Input: data/clinvar_hbb_raw.json
 * Output: data/clinvar_hbb_processed.json
 *
 * Processing:
 * - Categorize by variant type (missense, nonsense, splice, etc.)
 * - Filter pathogenic/likely pathogenic only
 * - Add GRCh38 coordinates
 * - Normalize HGVS notation
 *
 * Usage: npx tsx scripts/process_clinvar_hbb.ts
 */

import * as fs from 'fs';
import * as path from 'path';

interface ProcessedVariant {
    vcv_id: string;
    position: number;
    ref: string;
    alt: string;
    hgvs_c: string;
    hgvs_p: string;
    category: string;
    clinical_significance: string;
    review_status: string;
    submission_count: number;
}

/**
 * Categorize variant by molecular consequence
 */
function categorizeVariant(consequence: string, hgvs_c: string, hgvs_p: string): string {
    const c = consequence.toLowerCase();
    const coding = hgvs_c.toLowerCase();
    const protein = hgvs_p.toLowerCase();

    // Splice variants (±2 bp from exon boundary)
    if (c.includes('splice_donor') || coding.match(/ivs.*[+-][12]g/)) {
        return 'splice_donor';
    }
    if (c.includes('splice_acceptor') || coding.match(/ivs.*-[12]g/)) {
        return 'splice_acceptor';
    }

    // Splice region (±3-8 bp from exon boundary)
    if (c.includes('splice_region') || coding.match(/ivs.*[+-][3-8]/)) {
        return 'splice_region';
    }

    // Frameshift
    if (c.includes('frameshift') || protein.includes('fs')) {
        return 'frameshift';
    }

    // Nonsense (stop gain)
    if (c.includes('stop_gained') || c.includes('nonsense') || protein.includes('ter') || protein.includes('*')) {
        return 'nonsense';
    }

    // Missense
    if (c.includes('missense') || (protein && !protein.includes('='))) {
        return 'missense';
    }

    // UTR
    if (c.includes('5_prime_utr') || coding.includes('5utr')) {
        return '5_prime_UTR';
    }
    if (c.includes('3_prime_utr') || coding.includes('3utr')) {
        return '3_prime_UTR';
    }

    // Promoter
    if (coding.includes('-') && !coding.includes('ivs')) {
        return 'promoter';
    }

    // Intronic
    if (c.includes('intron') || coding.includes('ivs')) {
        return 'intronic';
    }

    // Synonymous
    if (c.includes('synonymous') || protein.includes('=')) {
        return 'synonymous';
    }

    // Default
    return 'other';
}

/**
 * Main processing
 */
async function main() {
    console.log('═══════════════════════════════════════════');
    console.log('  Process ClinVar HBB Variants');
    console.log('═══════════════════════════════════════════\n');

    // Load raw data
    const rawPath = path.join(__dirname, '..', 'data', 'clinvar_hbb_raw.json');
    if (!fs.existsSync(rawPath)) {
        console.error('❌ Error: data/clinvar_hbb_raw.json not found');
        console.error('   Run: npx tsx scripts/download_clinvar_hbb.ts first');
        process.exit(1);
    }

    const rawData = JSON.parse(fs.readFileSync(rawPath, 'utf-8'));
    const rawVariants = rawData.variants;

    console.log(`📥 Loaded ${rawVariants.length} raw variants`);

    // Filter pathogenic/likely pathogenic only
    const pathogenicVariants = rawVariants.filter((v: any) =>
        v.clinical_significance.toLowerCase().includes('pathogenic') &&
        !v.clinical_significance.toLowerCase().includes('benign')
    );

    console.log(`✅ Filtered to ${pathogenicVariants.length} pathogenic/likely pathogenic`);

    // Process variants
    const processed: ProcessedVariant[] = pathogenicVariants.map((v: any) => {
        const category = categorizeVariant(
            v.molecular_consequence,
            v.hgvs_coding,
            v.hgvs_protein
        );

        return {
            vcv_id: v.vcv_id,
            position: v.position,
            ref: v.ref,
            alt: v.alt,
            hgvs_c: v.hgvs_coding || '',
            hgvs_p: v.hgvs_protein || '',
            category,
            clinical_significance: v.clinical_significance,
            review_status: v.review_status,
            submission_count: v.submission_count,
        };
    });

    // Sort by position
    processed.sort((a, b) => a.position - b.position);

    // Save processed data
    const outputPath = path.join(__dirname, '..', 'data', 'clinvar_hbb_processed.json');
    fs.writeFileSync(outputPath, JSON.stringify({
        metadata: {
            source: rawData.metadata,
            processed_date: new Date().toISOString(),
            total_variants: processed.length,
            filter: 'pathogenic OR likely_pathogenic',
        },
        variants: processed,
    }, null, 2));

    console.log(`\n✅ Processed ${processed.length} variants`);
    console.log(`📁 Saved to: ${outputPath}\n`);

    // Summary by category
    console.log('📊 Variants by Category:');
    const categoryCounts = processed.reduce((acc, v) => {
        acc[v.category] = (acc[v.category] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);

    for (const [cat, count] of Object.entries(categoryCounts).sort((a, b) => b[1] - a[1])) {
        console.log(`  ${cat.padEnd(20)} ${count}`);
    }

    console.log('\n═══════════════════════════════════════════');
    console.log('Next step: npx tsx scripts/simulate_real_variants.ts');
    console.log('═══════════════════════════════════════════\n');
}

main().catch(console.error);
