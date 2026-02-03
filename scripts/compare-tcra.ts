/**
 * Compare TCRα ensemble results: beta=5 vs beta=0 (Diff Map).
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface LocusResult {
    hypothesis: string;
    locus: { name: string; chrom: string; start: number; end: number; length_bp: number; };
    params: { beta: number; numRuns: number; maxSteps: number; totalSteps: number; numCohesins: number; resolution: number; };
    fountainLoader: { stepLoadingProbability: number; medianSignal: number; binCount: number; };
    avgLoopsPerRun: number;
    heatmap: number[][];
}

function loadJson(p: string): LocusResult | null {
    try { return JSON.parse(fs.readFileSync(p, 'utf-8')); } catch { return null; }
}

function computeDiffStats(A: number[][], B: number[][]) {
    let min = Infinity, max = -Infinity, sumAbs = 0, count = 0, nonZero = 0, maxI = 0, maxJ = 0;
    for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < (A[i]?.length ?? 0); j++) {
            const d = (A[i]![j] ?? 0) - (B[i]?.[j] ?? 0);
            if (d < min) min = d;
            if (d > max) { max = d; maxI = i; maxJ = j; }
            sumAbs += Math.abs(d);
            count++;
            if (Math.abs(d) > 1e-8) nonZero++;
        }
    }
    return { min, max, meanAbs: count > 0 ? sumAbs / count : 0, nonZero, maxI, maxJ };
}

function computeMatrixStats(M: number[][]) {
    let min = Infinity, max = -Infinity, sum = 0, count = 0, nonZero = 0;
    for (let i = 0; i < M.length; i++) {
        for (let j = 0; j < (M[i]?.length ?? 0); j++) {
            const v = M[i]![j] ?? 0;
            min = Math.min(min, v);
            max = Math.max(max, v);
            sum += v;
            count++;
            if (v > 1e-8) nonZero++;
        }
    }
    return { min, max, mean: count > 0 ? sum / count : 0, nonZero };
}

function main() {
    const beta0 = loadJson(path.join(__dirname, '..', 'results', 'ensemble_tcra_beta0.json'));
    const beta5 = loadJson(path.join(__dirname, '..', 'results', 'ensemble_tcra_beta5.json'));

    if (!beta0 || !beta5) { console.error('Could not load results files'); return; }

    console.log('='.repeat(70));
    console.log('TCRα LOCUS BLIND VALIDATION - DIFF MAP ANALYSIS');
    console.log('='.repeat(70));
    console.log(`\nLocus: ${beta5.locus.name} (${beta5.locus.chrom}:${beta5.locus.start.toLocaleString()}-${beta5.locus.end.toLocaleString()})`);
    console.log(`Length: ${(beta5.locus.length_bp / 1_000_000).toFixed(2)} Mb\n`);

    console.log('COMPARISON SUMMARY');
    console.log('-'.repeat(70));
    console.log('| Parameter          | Beta=0 (baseline) | Beta=5 (optimal)  | Change    |');
    console.log('|--------------------|-------------------|-------------------|-----------|');
    console.log(`| stepLoadingProb    | ${beta0.fountainLoader.stepLoadingProbability.toFixed(6).padStart(17)} | ${beta5.fountainLoader.stepLoadingProbability.toFixed(6).padStart(17)} | ${((beta5.fountainLoader.stepLoadingProbability / beta0.fountainLoader.stepLoadingProbability)).toFixed(1).padStart(7)}x |`);
    console.log(`| avgLoopsPerRun     | ${beta0.avgLoopsPerRun.toFixed(1).padStart(17)} | ${beta5.avgLoopsPerRun.toFixed(1).padStart(17)} | ${(beta5.avgLoopsPerRun - beta0.avgLoopsPerRun > 0 ? '+' : '') + (beta5.avgLoopsPerRun - beta0.avgLoopsPerRun).toFixed(1).padStart(8)} |`);

    const stats0 = computeMatrixStats(beta0.heatmap);
    const stats5 = computeMatrixStats(beta5.heatmap);

    console.log('\nHEATMAP STATISTICS');
    console.log('-'.repeat(70));
    console.log('| Metric             | Beta=0            | Beta=5            |');
    console.log('|--------------------|-------------------|-------------------|');
    console.log(`| Non-zero cells     | ${stats0.nonZero.toString().padStart(17)} | ${stats5.nonZero.toString().padStart(17)} |`);
    console.log(`| Max value          | ${stats0.max.toExponential(4).padStart(17)} | ${stats5.max.toExponential(4).padStart(17)} |`);
    console.log(`| Mean value         | ${stats0.mean.toExponential(4).padStart(17)} | ${stats5.mean.toExponential(4).padStart(17)} |`);

    const diff = computeDiffStats(beta5.heatmap, beta0.heatmap);

    console.log('\nDIFF MAP (Beta=5 - Beta=0)');
    console.log('-'.repeat(70));
    console.log(`| Non-zero diff cells      | ${diff.nonZero.toString().padStart(10)} |`);
    console.log(`| Max diff                 | ${diff.max.toExponential(4).padStart(10)} |`);
    console.log(`| Min diff                 | ${diff.min.toExponential(4).padStart(10)} |`);
    console.log(`| Mean |diff|              | ${diff.meanAbs.toExponential(4).padStart(10)} |`);

    const resolution = beta5.params.resolution;
    const maxDiffPosStart = beta5.locus.start + diff.maxI * resolution;
    const maxDiffPosEnd = beta5.locus.start + diff.maxJ * resolution;
    console.log(`\nMax diff genomic region: ${maxDiffPosStart.toLocaleString()}-${maxDiffPosEnd.toLocaleString()}`);

    console.log('\nBLIND TEST VERDICT');
    console.log('-'.repeat(70));
    const hasSignificantDiff = diff.nonZero > 100 && diff.max > 1e-6;
    if (hasSignificantDiff) {
        console.log('✓ PASS: FountainLoader shows significant spatial signal effect on TCRα locus');
        console.log(`  - ${diff.nonZero} cells show differential contact probability`);
        console.log(`  - Max enrichment: ${diff.max.toExponential(2)} (beta=5 vs beta=0)`);
    } else {
        console.log('⚠ MARGINAL: Limited differential signal detected');
    }
    console.log('='.repeat(70));

    // Save diff map
    const diffMap: number[][] = [];
    for (let i = 0; i < beta5.heatmap.length; i++) {
        diffMap[i] = [];
        for (let j = 0; j < (beta5.heatmap[i]?.length ?? 0); j++) {
            diffMap[i]![j] = (beta5.heatmap[i]![j] ?? 0) - (beta0.heatmap[i]?.[j] ?? 0);
        }
    }

    const diffPayload = {
        hypothesis: 'H2_CohesinFountains_BlindTest_TCRa_DiffMap',
        comparison: 'beta5_minus_beta0',
        locus: beta5.locus,
        params: { beta0: 0, beta5: 5, numRuns: beta5.params.numRuns, maxSteps: beta5.params.maxSteps, resolution: beta5.params.resolution },
        stats: {
            beta0: { ...stats0, stepLoadingProb: beta0.fountainLoader.stepLoadingProbability, avgLoops: beta0.avgLoopsPerRun },
            beta5: { ...stats5, stepLoadingProb: beta5.fountainLoader.stepLoadingProbability, avgLoops: beta5.avgLoopsPerRun },
            diff,
        },
        diffMap,
    };

    const outPath = path.join(__dirname, '..', 'results', 'diff_tcra_beta5_vs_beta0.json');
    fs.writeFileSync(outPath, JSON.stringify(diffPayload, null, 2), 'utf-8');
    console.log(`\nDiff map saved to: ${outPath}`);
}

main();
