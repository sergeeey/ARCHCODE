#!/usr/bin/env npx tsx
/**
 * AlphaGenome Diagnostic Script
 *
 * Analyzes the structural differences between AlphaGenome and ARCHCODE
 * contact matrices to identify the source of negative correlation.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// Load .env file manually
const __filename_env = fileURLToPath(import.meta.url);
const __dirname_env = path.dirname(__filename_env);
const envPath = path.join(__dirname_env, '..', '.env');
if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    for (const line of envContent.split('\n')) {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith('#')) {
            const [key, ...valueParts] = trimmed.split('=');
            const value = valueParts.join('=');
            if (key && value) {
                process.env[key.trim()] = value.trim();
            }
        }
    }
}

import { AlphaGenomeService, GenomeInterval } from '../src/services/AlphaGenomeService';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';
import { createCTCFSite } from '../src/domain/models/genome';
import { FountainLoader } from '../src/simulation/SpatialLoadingModule';
import { SABATE_NATURE_2025, KRAMER_KINETICS } from '../src/domain/constants/biophysics';
import type { KramerKineticsConfig } from '../src/engines/MultiCohesinEngine';

const HBB_LOCUS: GenomeInterval = {
    chromosome: 'chr11',
    start: 5200000,
    end: 5400000,
};

const RESOLUTION = 5000;

function analyzeMatrix(matrix: number[][], name: string): void {
    const n = matrix.length;
    console.log(`\n=== ${name} Analysis ===`);

    // Diagonal statistics
    const diagonalProfiles: { distance: number; mean: number; std: number }[] = [];
    for (let d = 0; d < Math.min(10, n); d++) {
        const values: number[] = [];
        for (let i = 0; i < n - d; i++) {
            values.push(matrix[i][i + d]);
        }
        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const std = Math.sqrt(values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length);
        diagonalProfiles.push({ distance: d, mean, std });
    }

    console.log('\nDiagonal profile (mean contact by distance):');
    console.log('  Dist | Mean    | Std');
    console.log('  -----|---------|-------');
    for (const p of diagonalProfiles) {
        console.log(`    ${p.distance.toString().padStart(2)} | ${p.mean.toFixed(4).padStart(7)} | ${p.std.toFixed(4).padStart(7)}`);
    }

    // Find peaks (high contact regions)
    const peaks: { i: number; j: number; value: number }[] = [];
    for (let i = 0; i < n; i++) {
        for (let j = i + 2; j < n; j++) {  // Skip near-diagonal
            if (matrix[i][j] > 0.3) {  // Threshold for "high contact"
                peaks.push({ i, j, value: matrix[i][j] });
            }
        }
    }
    peaks.sort((a, b) => b.value - a.value);

    console.log('\nTop 10 off-diagonal peaks (distance > 2):');
    console.log('  Bin_i | Bin_j | Distance | Value');
    console.log('  ------|-------|----------|-------');
    for (const p of peaks.slice(0, 10)) {
        const dist = p.j - p.i;
        console.log(`    ${p.i.toString().padStart(3)} |   ${p.j.toString().padStart(3)} |      ${dist.toString().padStart(3)} | ${p.value.toFixed(4)}`);
    }

    // Row/column sums (marginal distribution)
    const rowSums = matrix.map(row => row.reduce((a, b) => a + b, 0) / n);
    const topRows = rowSums.map((s, i) => ({ bin: i, sum: s }))
        .sort((a, b) => b.sum - a.sum)
        .slice(0, 5);

    console.log('\nTop 5 most active bins (by row sum):');
    for (const r of topRows) {
        const posKb = (r.bin * RESOLUTION / 1000).toFixed(0);
        console.log(`  Bin ${r.bin} (${posKb}kb): ${r.sum.toFixed(4)}`);
    }

    // Matrix statistics
    const flatValues = matrix.flat().filter(v => v > 0);
    const min = Math.min(...flatValues);
    const max = Math.max(...flatValues);
    const mean = flatValues.reduce((a, b) => a + b, 0) / flatValues.length;
    const nonZero = flatValues.length;

    console.log('\nMatrix statistics:');
    console.log(`  Min: ${min.toFixed(4)}`);
    console.log(`  Max: ${max.toFixed(4)}`);
    console.log(`  Mean (non-zero): ${mean.toFixed(4)}`);
    console.log(`  Non-zero entries: ${nonZero}/${n * n} (${(100 * nonZero / (n * n)).toFixed(1)}%)`);
}

function pearsonCorrelation(x: number[], y: number[]): number {
    const n = x.length;
    const meanX = x.reduce((a, b) => a + b, 0) / n;
    const meanY = y.reduce((a, b) => a + b, 0) / n;

    let sumXY = 0, sumX2 = 0, sumY2 = 0;
    for (let i = 0; i < n; i++) {
        const dx = x[i] - meanX;
        const dy = y[i] - meanY;
        sumXY += dx * dy;
        sumX2 += dx * dx;
        sumY2 += dy * dy;
    }

    const denom = Math.sqrt(sumX2 * sumY2);
    return denom > 0 ? sumXY / denom : 0;
}

function analyzeCorrelationByDistance(
    matrix1: number[][],
    matrix2: number[][],
    name1: string,
    name2: string
): void {
    const n = matrix1.length;
    console.log(`\n=== Correlation by Distance ===`);
    console.log(`Comparing ${name1} vs ${name2}\n`);

    console.log('  Distance | Pearson r | N pairs');
    console.log('  ---------|-----------|--------');

    for (let d = 0; d < Math.min(20, n); d++) {
        const values1: number[] = [];
        const values2: number[] = [];
        for (let i = 0; i < n - d; i++) {
            values1.push(matrix1[i][i + d]);
            values2.push(matrix2[i][i + d]);
        }
        const r = pearsonCorrelation(values1, values2);
        console.log(`       ${d.toString().padStart(3)} |   ${r.toFixed(4).padStart(7)} |    ${values1.length.toString().padStart(4)}`);
    }
}

async function main() {
    console.log('═'.repeat(70));
    console.log('  AlphaGenome vs ARCHCODE Diagnostic');
    console.log('═'.repeat(70));

    const apiKey = process.env.ALPHAGENOME_API_KEY || process.env.VITE_ALPHAGENOME_API_KEY || '';
    const alphaGenome = new AlphaGenomeService({ apiKey, mode: apiKey ? 'live' : 'mock' });

    // Get AlphaGenome prediction
    console.log('\n▶ Fetching AlphaGenome prediction...');
    const prediction = await alphaGenome.predict(HBB_LOCUS);
    const agMatrix = prediction.contactMap.matrix;

    // Run ARCHCODE simulation
    console.log('\n▶ Running ARCHCODE simulation...');
    const windowLength = HBB_LOCUS.end - HBB_LOCUS.start;
    const nBins = Math.ceil(windowLength / RESOLUTION);

    const signalBins = Array(nBins).fill(null).map((_, i) => {
        // Higher loading in center (like validation script)
        const distFromCenter = Math.abs(i - nBins/2) / (nBins/2);
        return 0.3 + 0.7 * (1 - distFromCenter);
    });

    const fountain = new FountainLoader({
        signalBins,
        genomeStart: 0,
        genomeEnd: windowLength,
        baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
        beta: 5,
    });

    const occupancyMap = new Map<number, number>();
    for (let bin = 0; bin < nBins; bin++) {
        const signal = signalBins[bin] ?? 0.5;
        occupancyMap.set(bin, 0.1 + 0.8 * signal);
    }

    const kramerConfig: KramerKineticsConfig = {
        enabled: true,
        kBase: KRAMER_KINETICS.K_BASE,
        alpha: KRAMER_KINETICS.DEFAULT_ALPHA,
        gamma: KRAMER_KINETICS.DEFAULT_GAMMA,
        occupancyMap,
        occupancyResolution: RESOLUTION,
    };

    // Use same CTCF positions as validation script
    const ctcfSitesFinal = [
        createCTCFSite(HBB_LOCUS.chromosome, 7500, 'R', 1.0),    // bin 1
        createCTCFSite(HBB_LOCUS.chromosome, 182500, 'F', 1.0),  // bin 36
    ];

    const contactMatrix: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));

    for (let run = 0; run < 10; run++) {
        const engine = new MultiCohesinEngine({
            genomeLength: windowLength,
            ctcfSites: ctcfSitesFinal,
            velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
            spatialLoader: fountain,
            numCohesins: 20,
            seed: run * 1000,
            maxSteps: 50000,
            kramerKinetics: kramerConfig,
        });

        for (let step = 0; step < 50000; step++) {
            engine.step();
            engine.updateContactMatrix(contactMatrix, RESOLUTION);
        }
        process.stdout.write(`\r  Run ${run + 1}/10`);
    }
    console.log(' Done!');

    // Finalize with TAD structure (matches AlphaGenome pattern)
    const archcodeMatrix = MultiCohesinEngine.finalizeContactMatrix(contactMatrix, 1, 36);

    // Analysis
    analyzeMatrix(agMatrix, 'AlphaGenome');
    analyzeMatrix(archcodeMatrix, 'ARCHCODE');
    analyzeCorrelationByDistance(agMatrix, archcodeMatrix, 'AlphaGenome', 'ARCHCODE');

    // Save matrices for visualization
    const outputDir = path.join(__dirname_env, '..', 'results');
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const diagOutput = {
        timestamp: new Date().toISOString(),
        alphagenome: agMatrix,
        archcode: archcodeMatrix,
        ctcfSites: ctcfSitesFinal.map(s => ({
            position: s.position,
            orientation: s.orientation,
            bin: Math.floor(s.position / RESOLUTION),
        })),
    };

    fs.writeFileSync(
        path.join(outputDir, 'diagnostic_matrices.json'),
        JSON.stringify(diagOutput, null, 2)
    );

    console.log('\n\nMatrices saved to: results/diagnostic_matrices.json');
}

main().catch(console.error);
