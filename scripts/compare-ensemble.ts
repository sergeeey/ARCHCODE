/**
 * Сравнение ensemble результатов.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BETAS = [0, 2, 5, 10, 15];

interface EnsembleResult {
    beta: number;
    stepLoadingProbability: number;
    avgLoopsPerRun: number;
    heatmap: number[][];
}

function loadJson(p: string): EnsembleResult | null {
    try { return JSON.parse(fs.readFileSync(p, 'utf-8')); } catch { return null; }
}

function computeDiffStats(A: number[][], B: number[][]) {
    let min = Infinity, max = -Infinity, sumAbs = 0, count = 0, nonZero = 0;
    for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < (A[i]?.length ?? 0); j++) {
            const d = (A[i]![j] ?? 0) - (B[i]![j] ?? 0);
            min = Math.min(min, d);
            max = Math.max(max, d);
            sumAbs += Math.abs(d);
            count++;
            if (Math.abs(d) > 1e-8) nonZero++;
        }
    }
    return { min, max, meanAbs: count > 0 ? sumAbs / count : 0, nonZero };
}

function main() {
    const baseline = loadJson(path.join(__dirname, '..', 'results', 'ensemble_beta0.json'));
    if (!baseline) { console.error('Baseline not found'); return; }

    console.log('Ensemble Comparison (10 runs each, averaged)');
    console.log('=============================================\n');
    console.log('| Beta | stepLoadProb | avgLoops | Diff Max | Mean|Diff| | NonZero |');
    console.log('|------|--------------|----------|----------|------------|---------|');

    for (const beta of BETAS) {
        const test = loadJson(path.join(__dirname, '..', 'results', `ensemble_beta${beta}.json`));
        if (!test) continue;
        const stats = beta === 0 ? { min: 0, max: 0, meanAbs: 0, nonZero: 0 } : computeDiffStats(test.heatmap, baseline.heatmap);
        console.log(`| ${beta.toString().padStart(4)} | ${test.stepLoadingProbability.toFixed(6).padStart(12)} | ${test.avgLoopsPerRun.toFixed(1).padStart(8)} | ${stats.max.toFixed(4).padStart(8)} | ${stats.meanAbs.toFixed(6).padStart(10)} | ${stats.nonZero.toString().padStart(7)} |`);
    }
}

main();
