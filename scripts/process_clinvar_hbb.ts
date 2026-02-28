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
    // Normalize: ClinVar uses spaces ("splice donor variant"), code uses underscores
    const c = consequence.toLowerCase().replace(/ /g, '_');
    const coding = hgvs_c.toLowerCase();
    const protein = hgvs_p.toLowerCase();

    // Splice variants (±2 bp from exon boundary)
    // HGVS: c.93-1G>A, c.315+1G>A — canonical splice sites
    if (c.includes('splice_donor') || coding.match(/[+-][12][gatc]>[gatc]/)) {
        return 'splice_donor';
    }
    if (c.includes('splice_acceptor') || coding.match(/-[12][gatc]>[gatc]/)) {
        return 'splice_acceptor';
    }

    // Splice region (±3-8 bp from exon boundary)
    if (c.includes('splice_region') || coding.match(/[+-][3-8][gatc]?>/)) {
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
    if (c.includes('missense') || (protein && protein.length > 0 && !protein.includes('='))) {
        return 'missense';
    }

    // UTR
    if (c.includes('5_prime_utr') || c.includes('5\'_utr') || coding.includes('5utr') || coding.includes('-5\'utr')) {
        return '5_prime_UTR';
    }
    if (c.includes('3_prime_utr') || c.includes('3\'_utr') || coding.includes('3utr') || coding.includes('*')) {
        return '3_prime_UTR';
    }

    // Intronic (check before promoter — intron variants have "intron" in consequence)
    if (c.includes('intron') || coding.includes('ivs')) {
        return 'intronic';
    }

    // Promoter (upstream of gene, negative HGVS positions like c.-101C>T)
    if (coding.match(/c\.-\d/) && !coding.includes('ivs')) {
        return 'promoter';
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
    const rawPath = path.join(process.cwd(), 'data', 'clinvar_hbb_raw.json');
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
    const outputPath = path.join(process.cwd(), 'data', 'clinvar_hbb_processed.json');
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

    // Also export CSV for SpliceAI (needs: clinvar_id, chr, position, ref, alt)
    const csvVariants = processed.filter(v => v.ref !== 'N' && v.alt !== 'N');
    const csvHeader = 'clinvar_id,chr,position,ref,alt,category,hgvs_c,hgvs_p,clinical_significance';
    const csvRows = csvVariants.map(v =>
        [v.vcv_id, '11', v.position, v.ref, v.alt, v.category,
         `"${v.hgvs_c.replace(/"/g, '""')}"`,
         `"${v.hgvs_p.replace(/"/g, '""')}"`,
         v.clinical_significance].join(',')
    );
    const csvPath = path.join(process.cwd(), 'data', 'hbb_real_variants.csv');
    fs.writeFileSync(csvPath, [csvHeader, ...csvRows].join('\n'));
    console.log(`\n📁 CSV for SpliceAI: ${csvPath} (${csvVariants.length} variants with ref/alt)`);

    console.log('\n═══════════════════════════════════════════');
    console.log('Next step: python scripts/run_spliceai_hbb.py --variants data/hbb_real_variants.csv');
    console.log('═══════════════════════════════════════════\n');
}

main().catch(console.error);
