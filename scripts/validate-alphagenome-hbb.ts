/**
 * AlphaGenome Validation Script — HBB Locus (Beta-Globin)
 *
 * This script validates ARCHCODE against AlphaGenome predictions
 * using the HBB locus as a test bed.
 *
 * HBB (Beta-Globin) is chosen because:
 * - Compact (~200 kb)
 * - Classic gene regulation model
 * - Well-characterized CTCF/enhancer landscape
 *
 * @author Sergey V. Boyko (sergeikuch80@gmail.com)
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import { AlphaGenomeService, GenomeInterval } from '../src/services/AlphaGenomeService';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';
import { createCTCFSite } from '../src/domain/models/genome';
import { FountainLoader } from '../src/simulation/SpatialLoadingModule';
import { SABATE_NATURE_2025 } from '../src/domain/constants/biophysics';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// Configuration
// ============================================================================

const HBB_LOCUS: GenomeInterval = {
    chromosome: 'chr11',
    start: 5200000,
    end: 5400000, // 200 kb window
};

const SIMULATION_CONFIG = {
    beta: 5,
    numRuns: 20,
    maxSteps: 50000,
    numCohesins: 15,
    resolution: 5000, // 5 kb
};

// ============================================================================
// Main
// ============================================================================

async function main() {
    console.log('');
    console.log('█'.repeat(70));
    console.log('  ARCHCODE × AlphaGenome VALIDATION');
    console.log('  Locus: HBB (Beta-Globin)');
    console.log('█'.repeat(70));
    console.log('');

    // Check for API key
    const apiKey = process.env.ALPHAGENOME_API_KEY;
    const mode = apiKey ? 'live' : 'mock';

    console.log(`Mode: ${mode.toUpperCase()}`);
    if (!apiKey) {
        console.log('Note: Set ALPHAGENOME_API_KEY for live API validation');
    }
    console.log('');

    // Initialize AlphaGenome service
    const alphaGenome = new AlphaGenomeService({ apiKey, mode });

    // Get AlphaGenome prediction
    console.log('═'.repeat(70));
    console.log('STEP 1: Getting AlphaGenome Prediction');
    console.log('═'.repeat(70));

    const prediction = await alphaGenome.predict(HBB_LOCUS);
    console.log(`  Interval: ${prediction.interval.chromosome}:${prediction.interval.start}-${prediction.interval.end}`);
    console.log(`  Resolution: ${prediction.contactMap.resolution} bp`);
    console.log(`  Matrix size: ${prediction.contactMap.matrix.length}×${prediction.contactMap.matrix.length}`);
    console.log(`  Confidence: ${(prediction.confidence * 100).toFixed(1)}%`);
    console.log(`  Model: ${prediction.modelVersion}`);
    console.log('');

    // Run ARCHCODE simulation
    console.log('═'.repeat(70));
    console.log('STEP 2: Running ARCHCODE Simulation');
    console.log('═'.repeat(70));

    const windowLength = HBB_LOCUS.end - HBB_LOCUS.start;
    const nBins = Math.ceil(windowLength / SIMULATION_CONFIG.resolution);

    // Generate CTCF sites for HBB
    const ctcfSites = [
        createCTCFSite(HBB_LOCUS.chromosome, 20000, 'R', 0.9),   // HS4 insulator
        createCTCFSite(HBB_LOCUS.chromosome, 50000, 'F', 0.85),  // LCR region
        createCTCFSite(HBB_LOCUS.chromosome, 70000, 'R', 0.8),   // Enhancer
        createCTCFSite(HBB_LOCUS.chromosome, 100000, 'F', 0.9),  // HBB promoter
        createCTCFSite(HBB_LOCUS.chromosome, 130000, 'R', 0.85), // HBD
        createCTCFSite(HBB_LOCUS.chromosome, 160000, 'F', 0.8),  // HBG
        createCTCFSite(HBB_LOCUS.chromosome, 180000, 'R', 0.9),  // 3' boundary
    ];

    // Create FountainLoader with epigenetic signal
    const signalBins = prediction.epigenetics.h3k27ac ||
        Array(nBins).fill(null).map(() => 0.5 + Math.random() * 0.5);

    const fountain = new FountainLoader({
        signalBins,
        genomeStart: 0,
        genomeEnd: windowLength,
        baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
        beta: SIMULATION_CONFIG.beta,
    });

    // Run ensemble
    const occupancyMatrix: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));

    console.log(`  Running ${SIMULATION_CONFIG.numRuns} simulations...`);

    for (let run = 0; run < SIMULATION_CONFIG.numRuns; run++) {
        const engine = new MultiCohesinEngine({
            genomeLength: windowLength,
            ctcfSites,
            velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
            unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
            spatialLoader: fountain,
            numCohesins: SIMULATION_CONFIG.numCohesins,
            seed: run * 1000,
            maxSteps: SIMULATION_CONFIG.maxSteps,
        });

        for (let step = 0; step < SIMULATION_CONFIG.maxSteps; step++) {
            engine.step();
            engine.updateOccupancyMatrix(occupancyMatrix, SIMULATION_CONFIG.resolution);
        }

        process.stdout.write(`\r  Progress: ${run + 1}/${SIMULATION_CONFIG.numRuns}`);
    }
    console.log(' Done!');
    console.log('');

    // Normalize ARCHCODE matrix
    const maxVal = Math.max(...occupancyMatrix.flat());
    const archcodeMatrix = occupancyMatrix.map(row =>
        row.map(v => maxVal > 0 ? v / maxVal : 0)
    );

    // Validate
    console.log('═'.repeat(70));
    console.log('STEP 3: Validation');
    console.log('═'.repeat(70));

    const { metrics } = await alphaGenome.validateArchcode(HBB_LOCUS, archcodeMatrix);

    console.log('');
    console.log('┌' + '─'.repeat(68) + '┐');
    console.log('│' + '  VALIDATION METRICS'.padEnd(68) + '│');
    console.log('├' + '─'.repeat(68) + '┤');
    console.log('│' + `  Pearson r:       ${metrics.pearsonR.toFixed(4)}`.padEnd(68) + '│');
    console.log('│' + `  Spearman ρ:      ${metrics.spearmanRho.toFixed(4)}`.padEnd(68) + '│');
    console.log('│' + `  RMSE:            ${metrics.rmse.toFixed(4)}`.padEnd(68) + '│');
    console.log('│' + `  SSIM:            ${metrics.ssim.toFixed(4)}`.padEnd(68) + '│');
    console.log('├' + '─'.repeat(68) + '┤');

    // Verdict
    const verdict = metrics.pearsonR >= 0.7 ? 'PASS' :
                    metrics.pearsonR >= 0.5 ? 'MARGINAL' : 'FAIL';
    const verdictColor = verdict === 'PASS' ? '✓' : verdict === 'MARGINAL' ? '⚠' : '✗';

    console.log('│' + `  Verdict:         ${verdictColor} ${verdict}`.padEnd(68) + '│');
    console.log('└' + '─'.repeat(68) + '┘');
    console.log('');

    // Interpretation
    if (verdict === 'PASS') {
        console.log('╔' + '═'.repeat(68) + '╗');
        console.log('║' + '  ARCHCODE correlates well with AlphaGenome!'.padEnd(68) + '║');
        console.log('║' + '  Physics-based model validated against ML predictions.'.padEnd(68) + '║');
        console.log('╚' + '═'.repeat(68) + '╝');
    } else if (verdict === 'MARGINAL') {
        console.log('⚠ Moderate correlation. Consider adjusting parameters.');
    } else {
        console.log('✗ Low correlation. Review CTCF positions and beta value.');
    }

    // Save report
    const report = {
        locus: 'HBB',
        interval: HBB_LOCUS,
        mode,
        config: SIMULATION_CONFIG,
        alphagenome: {
            modelVersion: prediction.modelVersion,
            confidence: prediction.confidence,
            matrixSize: prediction.contactMap.matrix.length,
        },
        metrics,
        verdict,
        timestamp: new Date().toISOString(),
    };

    const resultsDir = path.join(__dirname, '..', 'results');
    if (!fs.existsSync(resultsDir)) {
        fs.mkdirSync(resultsDir, { recursive: true });
    }

    const reportPath = path.join(resultsDir, 'alphagenome_hbb_validation.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log('');
    console.log(`Report saved: ${reportPath}`);
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
