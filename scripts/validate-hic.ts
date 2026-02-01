/**
 * Hi-C Validation Script
 * Validates ARCHCODE simulation against real Hi-C data from Rao et al. 2014
 *
 * Run: npx tsx scripts/validate-hic.ts
 *
 * Usage:
 *   npx tsx scripts/validate-hic.ts              # Run with defaults (power-law)
 *   npx tsx scripts/validate-hic.ts --power-law  # Quick validation using P(s) curve
 *   npx tsx scripts/validate-hic.ts --download   # Download real Hi-C data
 *   npx tsx scripts/validate-hic.ts --list       # List available datasets
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import { createCTCFSite } from '../src/domain/models/genome';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';
import {
    listHiCDatasets,
    validateAgainstHiC,
    validateAgainstPowerLaw,
    HiCDownloadProgress,
} from '../src/downloaders/hic';
import type { ContactMatrix } from '../src/domain/models/genome';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// HBB Locus CTCF sites (chr11:5,200,000-5,400,000)
const HBB_SITES = [
    { pos: 25000, orient: 'F' as const, strength: 0.9 },
    { pos: 30000, orient: 'R' as const, strength: 0.85 },
    { pos: 45000, orient: 'F' as const, strength: 0.8 },
    { pos: 55000, orient: 'R' as const, strength: 0.9 },
    { pos: 75000, orient: 'F' as const, strength: 0.85 },
    { pos: 90000, orient: 'R' as const, strength: 0.9 },
];

const GENOME_LENGTH = 100000;

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

    return { loops, matrix };
}

async function validatePowerLawMode(matrix: ContactMatrix) {
    console.log('\n📊 Power-law validation (P(s) curve)...');

    const result = validateAgainstPowerLaw(matrix, -1.0);

    console.log(`   Fitted α = ${result.alpha.toFixed(3)} (expected: -1.0)`);
    console.log(`   Error: ${result.alphaError.toFixed(3)}`);
    console.log(`   Pearson r vs expected: ${result.pearsonR.toFixed(3)}`);

    return result;
}

async function validateHiCMode(matrix: ContactMatrix, datasetId: string) {
    console.log(`\n📥 Downloading Hi-C data: ${datasetId}...`);

    const result = await validateAgainstHiC(matrix, datasetId, (progress: HiCDownloadProgress) => {
        process.stdout.write(`\r   ${progress.stage}: ${progress.percent}%`);
    });

    console.log('\n');
    console.log(`   Cell line: ${result.cellLine}`);
    console.log(`   Resolution: ${result.resolution} bp`);
    console.log(`   Pearson r: ${result.pearsonR.toFixed(3)}`);
    console.log(`   Spearman ρ: ${result.spearmanRho.toFixed(3)}`);
    console.log(`   RMSE: ${result.rmse.toFixed(4)}`);
    console.log(`   Passes threshold (r≥0.7): ${result.passesThreshold ? '✅ YES' : '❌ NO'}`);

    return result;
}

function showDatasets() {
    console.log('\n📋 Available Hi-C datasets:\n');

    const datasets = listHiCDatasets();

    console.log('ID                           | Cell Line | Resolution | Source');
    console.log('-----------------------------|-----------|------------|--------');

    for (const d of datasets) {
        console.log(
            `${d.id.padEnd(28)} | ` +
            `${d.cellLine.padEnd(9)} | ` +
            `${(d.resolution / 1000 + 'kb').padEnd(10)} | ` +
            `${d.source}`
        );
    }

    console.log('\nNote: "hic" format requires hic-straw library (npm install hic-straw)');
}

async function main() {
    const args = process.argv.slice(2);
    const usePowerLaw = args.includes('--power-law');
    const useDownload = args.includes('--download');
    const listOnly = args.includes('--list');
    const datasetArg = args.find(a => a.startsWith('--dataset='));
    const datasetId = datasetArg ? datasetArg.split('=')[1] : 'rao2014_gm12878_chr11_hbb';

    console.log('╔════════════════════════════════════════════════╗');
    console.log('║       ARCHCODE Hi-C Validation Pipeline        ║');
    console.log('║   Validate against real Hi-C data (Rao 2014)   ║');
    console.log('╚════════════════════════════════════════════════╝\n');

    if (listOnly) {
        showDatasets();
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
        if (result.alphaError < 0.2 && result.pearsonR > 0.7) {
            console.log('🎉 POWER-LAW VALIDATION PASSED');
        } else {
            console.log('⚠️  Power-law validation: needs improvement');
        }

    } else if (useDownload) {
        try {
            const result = await validateHiCMode(simulation.matrix, datasetId);

            console.log('\n' + '═'.repeat(50));
            if (result.passesThreshold) {
                console.log('🎉 HI-C VALIDATION PASSED (r ≥ 0.7)');
            } else {
                console.log(`⚠️  Validation: r = ${result.pearsonR.toFixed(3)} (target: 0.7)`);
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
            console.error('\n❌ Validation failed:', (error as Error).message);
            console.log('\nTip: Check internet connection or try --power-law for offline validation');
        }

    } else {
        console.log('Using power-law validation (offline). Use --download for real Hi-C data.\n');
        const result = await validatePowerLawMode(simulation.matrix);

        console.log('\n' + '═'.repeat(50));
        console.log('Options:');
        console.log('  --power-law   Quick P(s) curve validation (default)');
        console.log('  --download    Download and validate against real Hi-C');
        console.log('  --list        List available Hi-C datasets');
        console.log('  --dataset=ID  Use specific dataset (default: rao2014_gm12878_chr11_hbb)');
    }
}

main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});
