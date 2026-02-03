/**
 * Hi-C Validation Script
 * Validates ARCHCODE simulation against real Hi-C loop calls from Rao et al. 2014
 *
 * Run: npx tsx scripts/validate-hic.ts
 *
 * Usage:
 *   npx tsx scripts/validate-hic.ts              # Run with defaults (power-law)
 *   npx tsx scripts/validate-hic.ts --download   # Download real loop calls
 *   npx tsx scripts/validate-hic.ts --list       # List available datasets
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import { createCTCFSite, Loop } from '../src/domain/models/genome';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';
import {
    listHiCDatasets,
    validateLoops,
    validateAgainstPowerLaw,
    downloadLoopList,
    filterLoops,
    LoopDownloadProgress,
} from '../src/downloaders/hic';
import type { ContactMatrix } from '../src/domain/models/genome';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// HBB Locus CTCF sites (chr11:5,200,000-5,400,000)
// Mapped to simulation coordinates (0-100kb)
const HBB_SITES = [
    { pos: 25000, orient: 'F' as const, strength: 0.9 },
    { pos: 30000, orient: 'R' as const, strength: 0.85 },
    { pos: 45000, orient: 'F' as const, strength: 0.8 },
    { pos: 55000, orient: 'R' as const, strength: 0.9 },
    { pos: 75000, orient: 'F' as const, strength: 0.85 },
    { pos: 90000, orient: 'R' as const, strength: 0.9 },
];

const GENOME_LENGTH = 100000;
const REGION_START = 5200000; // chr11 HBB region start
const REGION_END = 5300000;   // chr11 HBB region end

async function runSimulation(params: { velocity: number; cohesinCount: number }) {
    console.log(`🧬 Running simulation: velocity=${params.velocity}, cohesins=${params.cohesinCount}`);

    const sites = HBB_SITES.map(s =>
        createCTCFSite('chr11', s.pos, s.orient, s.strength)
    );

    const engine = new MultiCohesinEngine({
        genomeLength: GENOME_LENGTH,
        ctcfSites: sites,
        numCohesins: params.cohesinCount,
        velocity: params.velocity,
        seed: 42,
        maxSteps: 10000,
    });

    const loops = engine.run(10000);
    const matrix = engine.getContactMatrix(1000, 0.1);

    console.log(`   ✓ Loops formed: ${loops.length}`);
    console.log(`   ✓ Matrix size: ${matrix.length}x${matrix.length}`);

    // Convert to genomic coordinates for comparison
    const genomicLoops: Loop[] = loops.map(l => ({
        leftAnchor: l.leftAnchor + REGION_START,
        rightAnchor: l.rightAnchor + REGION_START,
        strength: l.strength,
    }));

    return { loops, genomicLoops, matrix };
}

async function validatePowerLawMode(matrix: ContactMatrix) {
    console.log('\n📊 Power-law validation (P(s) curve)...');

    const result = validateAgainstPowerLaw(matrix, -1.0);

    console.log(`   Fitted α = ${result.alpha.toFixed(3)} (expected: -1.0)`);
    console.log(`   Error: ${result.alphaError.toFixed(3)}`);
    console.log(`   Pearson r vs expected: ${result.pearsonR.toFixed(3)}`);

    return result;
}

async function validateLoopMode(genomicLoops: Loop[], datasetId: string) {
    console.log(`\n📥 Downloading HiCCUPS loop calls: ${datasetId}...`);

    try {
        const result = await validateLoops(
            genomicLoops,
            datasetId,
            'chr11',
            { start: REGION_START, end: REGION_END },
            (progress: LoopDownloadProgress) => {
                process.stdout.write(`\r   ${progress.stage}: ${progress.percent}%`);
            }
        );

        console.log('\n');
        console.log(`   Cell line: ${result.cellLine}`);
        console.log(`   Region: ${result.chromosome}:${result.region?.start}-${result.region?.end}`);
        console.log(`   Simulated loops: ${result.simulatedLoops}`);
        console.log(`   Experimental loops: ${result.experimentalLoops}`);
        console.log(`   Matched loops: ${result.matchedLoops}`);
        console.log(`   Precision: ${(result.precision * 100).toFixed(1)}%`);
        console.log(`   Recall: ${(result.recall * 100).toFixed(1)}%`);
        console.log(`   F1 Score: ${(result.f1Score * 100).toFixed(1)}%`);
        console.log(`   Avg loop size (sim): ${(result.avgSizeSimulated / 1000).toFixed(1)} kb`);
        console.log(`   Avg loop size (exp): ${(result.avgSizeExperimental / 1000).toFixed(1)} kb`);

        return result;

    } catch (error) {
        console.error('\n❌ Validation failed:', (error as Error).message);
        throw error;
    }
}

async function exploreLoops(datasetId: string) {
    console.log(`\n🔬 Exploring loops in dataset: ${datasetId}...`);

    const { downloadLoopList, filterLoops, getLoopAnchors } = await import('../src/downloaders/hic');

    const result = await downloadLoopList(datasetId, (progress) => {
        process.stdout.write(`\r   ${progress.stage}: ${progress.percent}%`);
    });

    if (!result.success || !result.loops) {
        console.error('\n❌ Download failed:', result.error);
        return;
    }

    console.log(`\n   Total loops: ${result.loopCount}`);

    // Group by chromosome
    const byChromosome = new Map<string, number>();
    for (const loop of result.loops) {
        const chr = loop.chr1;
        byChromosome.set(chr, (byChromosome.get(chr) || 0) + 1);
    }

    console.log('\n   Loops per chromosome:');
    const sorted = [...byChromosome.entries()].sort((a, b) => b[1] - a[1]);
    for (const [chr, count] of sorted.slice(0, 10)) {
        console.log(`     ${chr}: ${count}`);
    }

    // Check all chr11 loops
    const allChr11 = result.loops.filter(l => l.chr1 === 'chr11' || l.chr1 === '11');
    console.log(`\n   All chr11 loops: ${allChr11.length}`);

    // Show size distribution
    const sizes = allChr11.map(l => getLoopAnchors(l).size);
    sizes.sort((a, b) => a - b);
    if (sizes.length > 0) {
        console.log(`   Size range: ${(sizes[0] / 1000).toFixed(0)} kb - ${(sizes[sizes.length - 1] / 1000).toFixed(0)} kb`);
        console.log(`   Median size: ${(sizes[Math.floor(sizes.length / 2)] / 1000).toFixed(0)} kb`);
    }

    // Show first 5 chr11 loops with details
    console.log('\n   Sample chr11 loops (raw):');
    for (const loop of allChr11.slice(0, 5)) {
        const { left, right, size } = getLoopAnchors(loop);
        console.log(`     x1=${loop.x1}, x2=${loop.x2}, y1=${loop.y1}, y2=${loop.y2}`);
        console.log(`       → anchors: ${left.toFixed(0)} - ${right.toFixed(0)} (${(size / 1000).toFixed(1)} kb)`);
    }

    // Check HBB region
    const chr11Loops = filterLoops(result.loops, 'chr11', { start: REGION_START, end: REGION_END });
    console.log(`\n   Loops in HBB region (chr11:${REGION_START}-${REGION_END}): ${chr11Loops.length}`);

    if (chr11Loops.length > 0) {
        console.log('   HBB region loops:');
        for (const loop of chr11Loops.slice(0, 5)) {
            const { left, right, size } = getLoopAnchors(loop);
            console.log(`     ${left.toFixed(0)} - ${right.toFixed(0)} (${(size / 1000).toFixed(1)} kb)`);
        }
    }

    // Check wider region around HBB
    const widerRegion = filterLoops(result.loops, 'chr11', { start: 0, end: 10000000 });
    console.log(`\n   Loops in first 10 Mb of chr11: ${widerRegion.length}`);
}

function showDatasets() {
    console.log('\n📋 Available Hi-C loop datasets:\n');

    const datasets = listHiCDatasets();

    console.log('ID                              | Cell Line | Source');
    console.log('--------------------------------|-----------|--------');

    for (const d of datasets) {
        console.log(
            `${d.id.padEnd(31)} | ` +
            `${d.cellLine.padEnd(9)} | ` +
            `${d.source}`
        );
    }

    console.log('\nData source: Rao et al. (2014) Cell - HiCCUPS loop calls');
}

async function main() {
    const args = process.argv.slice(2);
    const usePowerLaw = args.includes('--power-law');
    const useDownload = args.includes('--download');
    const listOnly = args.includes('--list');
    const exploreOnly = args.includes('--explore');
    const datasetArg = args.find(a => a.startsWith('--dataset='));
    const datasetId = datasetArg ? datasetArg.split('=')[1] : 'rao2014_gm12878_loops';

    console.log('╔════════════════════════════════════════════════╗');
    console.log('║       ARCHCODE Hi-C Validation Pipeline        ║');
    console.log('║   Validate against Rao 2014 HiCCUPS loops      ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    if (listOnly) {
        showDatasets();
        return;
    }

    if (exploreOnly) {
        await exploreLoops(datasetId);
        return;
    }

    // Run simulation
    const simulation = await runSimulation({
        velocity: 1000,
        cohesinCount: 10,
    });

    if (usePowerLaw) {
        const result = await validatePowerLawMode(simulation.matrix);

        console.log('\n' + '═'.repeat(50));
        if (result.alphaError < 0.2 && result.pearsonR > 0.5) {
            console.log('🎉 POWER-LAW VALIDATION PASSED');
        } else {
            console.log('⚠️  Power-law validation: needs improvement');
        }

    } else if (useDownload) {
        try {
            const result = await validateLoopMode(simulation.genomicLoops, datasetId);

            console.log('\n' + '═'.repeat(50));
            if (result.f1Score >= 0.5) {
                console.log('🎉 LOOP VALIDATION PASSED (F1 ≥ 50%)');
            } else if (result.experimentalLoops === 0) {
                console.log('⚠️  No experimental loops in this region');
                console.log('   Try: --explore to see available loops');
            } else {
                console.log(`⚠️  Validation: F1 = ${(result.f1Score * 100).toFixed(1)}% (target: 50%)`);
            }

            // Save results
            const outputPath = path.join(__dirname, '..', 'results', 'hic-validation.json');
            fs.mkdirSync(path.dirname(outputPath), { recursive: true });
            fs.writeFileSync(outputPath, JSON.stringify({
                timestamp: new Date().toISOString(),
                simulation: {
                    loops: simulation.loops.length,
                    matrixSize: simulation.matrix.length,
                },
                validation: result,
            }, null, 2));
            console.log(`\n💾 Results saved to: ${outputPath}`);

        } catch (error) {
            console.log('\nTip: Try --explore to see what loops are available');
            console.log('     Or use --power-law for offline validation');
        }

    } else {
        console.log('Using power-law validation (offline). Use --download for real Hi-C data.\n');
        const result = await validatePowerLawMode(simulation.matrix);

        console.log('\n' + '═'.repeat(50));
        console.log('Options:');
        console.log('  --power-law   Quick P(s) curve validation (default)');
        console.log('  --download    Download and validate against HiCCUPS loops');
        console.log('  --explore     Explore loops in a dataset');
        console.log('  --list        List available datasets');
        console.log('  --dataset=ID  Use specific dataset (default: rao2014_gm12878_loops)');
    }
}

main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
