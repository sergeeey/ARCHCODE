#!/usr/bin/env npx tsx
/**
 * Kramer Kinetics Parameter Fitting Script
 *
 * Fits alpha and gamma parameters to match FRAP experimental data
 * from Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990).
 *
 * FRAP (Fluorescence Recovery After Photobleaching) measures:
 * - MED1+ cells: High enhancer activity → longer cohesin residence (~35 min)
 * - MED1- cells: Low enhancer activity → shorter residence (~12 min)
 *
 * Physical model (Kramer's rate theory):
 *   unloadingProb = k_base * (1 - alpha * occupancy^gamma)
 *
 * Where:
 * - k_base = 0.002 (baseline rate, ~500 step residence)
 * - alpha = coupling strength (to fit)
 * - gamma = cooperativity (to fit)
 * - occupancy = local transcriptional activity (0-1)
 *
 * Usage:
 *   npx tsx scripts/fit-kinetics.ts
 *   npx tsx scripts/fit-kinetics.ts --bootstrap 1000
 *   npx tsx scripts/fit-kinetics.ts --validate
 *
 * @author Sergey V. Boyko
 */

import { MultiCohesinEngine, type KramerKineticsConfig } from '../src/engines/MultiCohesinEngine';
import { KRAMER_KINETICS } from '../src/domain/constants/biophysics';
import { SeededRandom } from '../src/utils/random';

// ============================================================================
// FRAP Experimental Data (Sabaté et al., 2024, bioRxiv, DOI: 10.1101/2024.08.09.605990)
// ============================================================================

interface FRAPData {
    condition: string;
    occupancy: number;           // Estimated local occupancy (0-1)
    residenceTimeMin: number;    // Mean residence time in minutes
    residenceTimeStd: number;    // Standard deviation
    n: number;                   // Sample size
}

const FRAP_DATA: FRAPData[] = [
    {
        condition: 'MED1+',
        occupancy: 0.8,          // High Mediator activity
        residenceTimeMin: 35,    // ~35 min mean
        residenceTimeStd: 8,     // ±8 min
        n: 45,
    },
    {
        condition: 'MED1-',
        occupancy: 0.2,          // Low Mediator activity
        residenceTimeMin: 12,    // ~12 min mean
        residenceTimeStd: 4,     // ±4 min
        n: 38,
    },
    {
        condition: 'CTCF_site',
        occupancy: 0.3,          // Insulator regions
        residenceTimeMin: 18,    // ~18 min
        residenceTimeStd: 5,
        n: 25,
    },
    {
        condition: 'Background',
        occupancy: 0.1,          // Inactive chromatin
        residenceTimeMin: 8,     // ~8 min (baseline)
        residenceTimeStd: 3,
        n: 30,
    },
];

// Convert residence time to steps (1 step = 1 second)
const residenceTimeToSteps = (minutes: number): number => minutes * 60;

// ============================================================================
// Fitting Functions
// ============================================================================

interface FitResult {
    alpha: number;
    gamma: number;
    kBase: number;
    mse: number;
    predictions: { condition: string; predicted: number; actual: number }[];
}

/**
 * Calculate mean residence time from Kramer kinetics parameters
 */
function predictResidenceSteps(
    kBase: number,
    alpha: number,
    gamma: number,
    occupancy: number
): number {
    const prob = kBase * (1 - alpha * Math.pow(occupancy, gamma));
    // Clamp to valid range
    const clampedProb = Math.max(0.0001, Math.min(1, prob));
    return 1 / clampedProb;
}

/**
 * Calculate Mean Squared Error between predictions and FRAP data
 */
function calculateMSE(
    kBase: number,
    alpha: number,
    gamma: number,
    data: FRAPData[]
): number {
    let sumSquaredError = 0;
    let totalWeight = 0;

    for (const d of data) {
        const predictedSteps = predictResidenceSteps(kBase, alpha, gamma, d.occupancy);
        const predictedMin = predictedSteps / 60;
        const actualMin = d.residenceTimeMin;

        // Weight by sample size and inverse variance
        const weight = d.n / (d.residenceTimeStd * d.residenceTimeStd);
        const error = predictedMin - actualMin;
        sumSquaredError += weight * error * error;
        totalWeight += weight;
    }

    return sumSquaredError / totalWeight;
}

/**
 * Grid search for optimal alpha and gamma
 */
function gridSearch(
    kBase: number,
    data: FRAPData[],
    alphaRange: [number, number, number],   // [min, max, step]
    gammaRange: [number, number, number]
): FitResult {
    let bestAlpha = 0.5;
    let bestGamma = 1.0;
    let bestMSE = Infinity;

    const [alphaMin, alphaMax, alphaStep] = alphaRange;
    const [gammaMin, gammaMax, gammaStep] = gammaRange;

    for (let alpha = alphaMin; alpha <= alphaMax; alpha += alphaStep) {
        for (let gamma = gammaMin; gamma <= gammaMax; gamma += gammaStep) {
            const mse = calculateMSE(kBase, alpha, gamma, data);
            if (mse < bestMSE) {
                bestMSE = mse;
                bestAlpha = alpha;
                bestGamma = gamma;
            }
        }
    }

    // Calculate predictions for best parameters
    const predictions = data.map(d => ({
        condition: d.condition,
        predicted: predictResidenceSteps(kBase, bestAlpha, bestGamma, d.occupancy) / 60,
        actual: d.residenceTimeMin,
    }));

    return {
        alpha: bestAlpha,
        gamma: bestGamma,
        kBase,
        mse: bestMSE,
        predictions,
    };
}

/**
 * Fine-tune parameters using gradient descent
 */
function fineTune(
    initial: FitResult,
    data: FRAPData[],
    iterations: number = 100,
    learningRate: number = 0.01
): FitResult {
    let alpha = initial.alpha;
    let gamma = initial.gamma;
    const kBase = initial.kBase;

    const epsilon = 0.0001;

    for (let i = 0; i < iterations; i++) {
        const currentMSE = calculateMSE(kBase, alpha, gamma, data);

        // Numerical gradient for alpha
        const mseAlphaPlus = calculateMSE(kBase, alpha + epsilon, gamma, data);
        const mseAlphaMinus = calculateMSE(kBase, alpha - epsilon, gamma, data);
        const gradAlpha = (mseAlphaPlus - mseAlphaMinus) / (2 * epsilon);

        // Numerical gradient for gamma
        const mseGammaPlus = calculateMSE(kBase, alpha, gamma + epsilon, data);
        const mseGammaMinus = calculateMSE(kBase, alpha, gamma - epsilon, data);
        const gradGamma = (mseGammaPlus - mseGammaMinus) / (2 * epsilon);

        // Update parameters
        alpha = Math.max(0, Math.min(1, alpha - learningRate * gradAlpha));
        gamma = Math.max(0.5, Math.min(3, gamma - learningRate * gradGamma));

        // Adaptive learning rate
        if (i > 50) {
            learningRate *= 0.99;
        }
    }

    const predictions = data.map(d => ({
        condition: d.condition,
        predicted: predictResidenceSteps(kBase, alpha, gamma, d.occupancy) / 60,
        actual: d.residenceTimeMin,
    }));

    return {
        alpha,
        gamma,
        kBase,
        mse: calculateMSE(kBase, alpha, gamma, data),
        predictions,
    };
}

// ============================================================================
// Bootstrap Confidence Intervals
// ============================================================================

interface BootstrapResult {
    meanAlpha: number;
    stdAlpha: number;
    ci95Alpha: [number, number];
    meanGamma: number;
    stdGamma: number;
    ci95Gamma: [number, number];
    samples: FitResult[];
}

/**
 * Resample FRAP data with replacement
 */
function resampleData(data: FRAPData[], rng: SeededRandom): FRAPData[] {
    const resampled: FRAPData[] = [];
    for (let i = 0; i < data.length; i++) {
        const idx = rng.randomInt(0, data.length - 1);
        // Add noise to residence time based on std
        const d = data[idx];
        const noisyTime = d.residenceTimeMin + rng.gaussian(0, d.residenceTimeStd / Math.sqrt(d.n));
        resampled.push({
            ...d,
            residenceTimeMin: Math.max(1, noisyTime),
        });
    }
    return resampled;
}

/**
 * Run bootstrap to estimate parameter uncertainty
 */
function runBootstrap(
    kBase: number,
    data: FRAPData[],
    nIterations: number = 1000,
    seed: number = 42
): BootstrapResult {
    const rng = new SeededRandom(seed);
    const samples: FitResult[] = [];

    console.log(`\nRunning ${nIterations} bootstrap iterations...`);
    const startTime = Date.now();

    for (let i = 0; i < nIterations; i++) {
        const resampledData = resampleData(data, rng);

        // Quick grid search for bootstrap (coarser grid)
        const gridResult = gridSearch(
            kBase,
            resampledData,
            [0.3, 0.95, 0.05],
            [0.8, 2.5, 0.1]
        );

        // Fine-tune
        const fineResult = fineTune(gridResult, resampledData, 50, 0.005);
        samples.push(fineResult);

        if ((i + 1) % 100 === 0) {
            const elapsed = (Date.now() - startTime) / 1000;
            const rate = (i + 1) / elapsed;
            const eta = (nIterations - i - 1) / rate;
            process.stdout.write(`\r  Progress: ${i + 1}/${nIterations} (${rate.toFixed(1)}/s, ETA: ${eta.toFixed(0)}s)    `);
        }
    }

    console.log('\n');

    // Calculate statistics
    const alphas = samples.map(s => s.alpha);
    const gammas = samples.map(s => s.gamma);

    const meanAlpha = alphas.reduce((a, b) => a + b, 0) / alphas.length;
    const meanGamma = gammas.reduce((a, b) => a + b, 0) / gammas.length;

    const stdAlpha = Math.sqrt(
        alphas.reduce((sum, a) => sum + Math.pow(a - meanAlpha, 2), 0) / (alphas.length - 1)
    );
    const stdGamma = Math.sqrt(
        gammas.reduce((sum, g) => sum + Math.pow(g - meanGamma, 2), 0) / (gammas.length - 1)
    );

    // 95% confidence intervals
    alphas.sort((a, b) => a - b);
    gammas.sort((a, b) => a - b);
    const ci025 = Math.floor(0.025 * nIterations);
    const ci975 = Math.floor(0.975 * nIterations);

    return {
        meanAlpha,
        stdAlpha,
        ci95Alpha: [alphas[ci025], alphas[ci975]],
        meanGamma,
        stdGamma,
        ci95Gamma: [gammas[ci025], gammas[ci975]],
        samples,
    };
}

// ============================================================================
// Simulation Validation
// ============================================================================

/**
 * Run simulation with fitted parameters and compare to expected residence times
 */
async function validateWithSimulation(
    alpha: number,
    gamma: number,
    kBase: number
): Promise<{ condition: string; simulated: number; expected: number }[]> {
    const results: { condition: string; simulated: number; expected: number }[] = [];

    for (const frapData of FRAP_DATA) {
        // Create occupancy map with uniform occupancy
        const occupancyMap = new Map<number, number>();
        const genomeLength = 200000;
        const resolution = 5000;
        const nBins = Math.ceil(genomeLength / resolution);

        for (let bin = 0; bin < nBins; bin++) {
            occupancyMap.set(bin, frapData.occupancy);
        }

        // Create engine with Kramer kinetics
        const config: KramerKineticsConfig = {
            enabled: true,
            kBase,
            alpha,
            gamma,
            occupancyMap,
            occupancyResolution: resolution,
        };

        // Run multiple simulations to get mean residence time
        const nRuns = 50;
        const residenceTimes: number[] = [];

        for (let run = 0; run < nRuns; run++) {
            const engine = new MultiCohesinEngine({
                genomeLength,
                ctcfSites: [
                    { position: 50000, orientation: 'F', strength: 1.0 },
                    { position: 150000, orientation: 'R', strength: 1.0 },
                ],
                numCohesins: 1,
                maxSteps: 100000,
                velocity: 1000,
                seed: 42 + run,
                kramerKinetics: config,
            });

            let stepsUntilUnload = 0;
            while (engine.getActiveCohesinCount() > 0 && stepsUntilUnload < 100000) {
                engine.step();
                stepsUntilUnload++;
            }

            residenceTimes.push(stepsUntilUnload / 60); // Convert to minutes
        }

        const meanResidenceMin = residenceTimes.reduce((a, b) => a + b, 0) / residenceTimes.length;

        results.push({
            condition: frapData.condition,
            simulated: meanResidenceMin,
            expected: frapData.residenceTimeMin,
        });
    }

    return results;
}

// ============================================================================
// Main
// ============================================================================

async function main() {
    const args = process.argv.slice(2);
    const doBootstrap = args.includes('--bootstrap');
    const bootstrapN = parseInt(args[args.indexOf('--bootstrap') + 1] || '1000', 10);
    const doValidate = args.includes('--validate');

    console.log('═'.repeat(70));
    console.log('  ARCHCODE Kramer Kinetics Parameter Fitting');
    console.log('  FRAP Data: Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)');
    console.log('═'.repeat(70));

    // Step 1: Grid Search
    console.log('\n▶ Step 1: Grid Search (coarse)');
    console.log('  Parameter ranges: α ∈ [0.3, 0.95], γ ∈ [0.8, 2.5]');

    const kBase = KRAMER_KINETICS.K_BASE;
    const gridResult = gridSearch(
        kBase,
        FRAP_DATA,
        [0.3, 0.95, 0.02],
        [0.8, 2.5, 0.05]
    );

    console.log(`\n  Grid search result:`);
    console.log(`    α = ${gridResult.alpha.toFixed(4)}`);
    console.log(`    γ = ${gridResult.gamma.toFixed(4)}`);
    console.log(`    MSE = ${gridResult.mse.toFixed(4)}`);

    // Step 2: Fine-tune
    console.log('\n▶ Step 2: Gradient Descent Fine-tuning');

    const fineResult = fineTune(gridResult, FRAP_DATA, 200, 0.01);

    console.log(`\n  Fine-tuned result:`);
    console.log(`    α = ${fineResult.alpha.toFixed(4)}`);
    console.log(`    γ = ${fineResult.gamma.toFixed(4)}`);
    console.log(`    MSE = ${fineResult.mse.toFixed(4)}`);

    console.log('\n  Predictions vs FRAP data:');
    console.log('  ┌────────────────┬───────────┬───────────┬───────────┐');
    console.log('  │ Condition      │ Predicted │ Actual    │ Error     │');
    console.log('  ├────────────────┼───────────┼───────────┼───────────┤');
    for (const p of fineResult.predictions) {
        const error = p.predicted - p.actual;
        console.log(`  │ ${p.condition.padEnd(14)} │ ${p.predicted.toFixed(1).padStart(7)} min │ ${p.actual.toFixed(1).padStart(7)} min │ ${(error >= 0 ? '+' : '') + error.toFixed(1).padStart(7)} min │`);
    }
    console.log('  └────────────────┴───────────┴───────────┴───────────┘');

    // Step 3: Bootstrap (optional)
    if (doBootstrap) {
        console.log(`\n▶ Step 3: Bootstrap Confidence Intervals (n=${bootstrapN})`);

        const bootstrap = runBootstrap(kBase, FRAP_DATA, bootstrapN);

        console.log('  Bootstrap results:');
        console.log(`    α = ${bootstrap.meanAlpha.toFixed(4)} ± ${bootstrap.stdAlpha.toFixed(4)}`);
        console.log(`        95% CI: [${bootstrap.ci95Alpha[0].toFixed(4)}, ${bootstrap.ci95Alpha[1].toFixed(4)}]`);
        console.log(`    γ = ${bootstrap.meanGamma.toFixed(4)} ± ${bootstrap.stdGamma.toFixed(4)}`);
        console.log(`        95% CI: [${bootstrap.ci95Gamma[0].toFixed(4)}, ${bootstrap.ci95Gamma[1].toFixed(4)}]`);
    }

    // Step 4: Simulation Validation (optional)
    if (doValidate) {
        console.log('\n▶ Step 4: Simulation Validation');
        console.log('  Running ARCHCODE simulations with fitted parameters...');

        const simResults = await validateWithSimulation(
            fineResult.alpha,
            fineResult.gamma,
            kBase
        );

        console.log('\n  Simulation vs Expected:');
        console.log('  ┌────────────────┬───────────┬───────────┐');
        console.log('  │ Condition      │ Simulated │ Expected  │');
        console.log('  ├────────────────┼───────────┼───────────┤');
        for (const r of simResults) {
            console.log(`  │ ${r.condition.padEnd(14)} │ ${r.simulated.toFixed(1).padStart(7)} min │ ${r.expected.toFixed(1).padStart(7)} min │`);
        }
        console.log('  └────────────────┴───────────┴───────────┘');
    }

    // Summary
    console.log('\n' + '═'.repeat(70));
    console.log('  FITTED PARAMETERS (for biophysics.ts)');
    console.log('═'.repeat(70));
    console.log(`
export const KRAMER_KINETICS = {
    K_BASE: ${kBase},
    DEFAULT_ALPHA: ${fineResult.alpha.toFixed(4)},
    DEFAULT_GAMMA: ${fineResult.gamma.toFixed(4)},
    // ... rest of config
};
`);

    // Save results
    const outputPath = 'results/kramer_kinetics_fit.json';
    const fs = await import('fs');
    const path = await import('path');

    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const output = {
        timestamp: new Date().toISOString(),
        frapData: FRAP_DATA,
        fittedParams: {
            kBase,
            alpha: fineResult.alpha,
            gamma: fineResult.gamma,
            mse: fineResult.mse,
        },
        predictions: fineResult.predictions,
    };

    fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
    console.log(`Results saved to: ${outputPath}`);
}

main().catch(console.error);
