/**
 * In Silico MED1 Knockdown — проверка причинности (causality).
 *
 * Две параллельные симуляции локуса HBB:
 * - WT: текущие параметры (FountainLoader с MED1, beta > 0).
 * - MED1-KD: alpha = 0 в смысле влияния Медиатора — beta = 0 (равномерная загрузка).
 *
 * Выход: Diff Map (WT - KD), Insulation Score для обоих состояний, вердикт по четкости TAD-границ.
 * Нормализация: O/E (observed/expected) как в v1.5.
 *
 * Запуск: npx tsx scripts/run-knockdown-experiment.ts [--runs=20] [--out=med1_kd_hbb.json]
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import { createCTCFSite } from '../src/domain/models/genome';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';
import { FountainLoader } from '../src/simulation/SpatialLoadingModule';
import { SABATE_NATURE_2025 } from '../src/domain/constants/biophysics';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ========== HBB Locus (Beta-Globin) ==========
const HBB_CHR = 'chr11';
const HBB_START = 5_200_000;
const HBB_END = 5_300_000;
const HBB_LENGTH = HBB_END - HBB_START; // 100 kb

const HBB_CTCF_SITES = [
    { pos: 25_000, strength: 0.9, orient: 'F' as const },
    { pos: 30_000, strength: 0.85, orient: 'R' as const },
    { pos: 45_000, strength: 0.8, orient: 'F' as const },
    { pos: 55_000, strength: 0.9, orient: 'R' as const },
    { pos: 75_000, strength: 0.85, orient: 'F' as const },
    { pos: 90_000, strength: 0.9, orient: 'R' as const },
];

const RESOLUTION = 5000;
const BIN_COUNT = Math.floor(HBB_LENGTH / RESOLUTION); // 20
const MAX_STEPS = 50_000;
const NUM_COHESINS = 15;
const BETA_WT = 5;
const BETA_KD = 0;  // MED1-KD: выключение влияния Медиатора на загрузку

const MED1_BW_PATH = process.env.MED1_BW || 'D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/med1/MED1_GM12878_Rep1.bw';
const RESULTS_DIR = path.join(__dirname, '..', 'results');

// ========== O/E normalization (v1.5) ==========
/** Expected contact по степенному закону: E[i][j] ∝ (1 + |j-i|)^alpha */
function buildExpectedMatrix(nBins: number, alpha: number = -1): number[][] {
    const E: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));
    for (let i = 0; i < nBins; i++) {
        for (let j = 0; j < nBins; j++) {
            const d = Math.abs(j - i) || 1;
            E[i]![j] = Math.pow(d, alpha);
        }
    }
    return E;
}

/** Нормализация observed/expected. Защита от деления на ноль: OE = O / max(E, eps). */
function applyOENormalization(observed: number[][], expected: number[][]): number[][] {
    const n = observed.length;
    const eps = 1e-10;
    const oe: number[][] = Array(n).fill(null).map(() => Array(n).fill(0));
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            const o = observed[i]?.[j] ?? 0;
            const e = Math.max(expected[i]?.[j] ?? eps, eps);
            oe[i]![j] = o / e;
        }
    }
    return oe;
}

/** Insulation Score: для каждого бина i — средний контакт в полосе вокруг диагонали (локальные контакты). TAD-границы = локальные минимумы. */
function computeInsulationScore(matrix: number[][], halfWindow: number): number[] {
    const n = matrix.length;
    const scores: number[] = [];
    for (let i = 0; i < n; i++) {
        let sum = 0;
        let count = 0;
        for (let d = -halfWindow; d <= halfWindow; d++) {
            const j = i + d;
            if (j >= 0 && j < n) {
                sum += matrix[i]![j] ?? 0;
                count++;
            }
        }
        scores.push(count > 0 ? sum / count : 0);
    }
    return scores;
}

/** Четкость TAD-границ: чем выше разброс (std) и амплитуда (max-min) insulation, тем четче границы. */
function insulationClarity(scores: number[]): { mean: number; std: number; min: number; max: number; dynamicRange: number } {
    const n = scores.length;
    const mean = n ? scores.reduce((a, b) => a + b, 0) / n : 0;
    const variance = n ? scores.reduce((s, x) => s + (x - mean) ** 2, 0) / n : 0;
    const std = Math.sqrt(variance);
    const min = n ? Math.min(...scores) : 0;
    const max = n ? Math.max(...scores) : 0;
    return { mean, std, min, max, dynamicRange: max - min };
}

// ========== Helpers ==========
function createZeroMatrix(size: number): number[][] {
    return Array(size).fill(null).map(() => Array(size).fill(0));
}

function scaleMatrix(A: number[][], factor: number): void {
    for (let i = 0; i < A.length; i++) {
        for (let j = 0; j < (A[i]?.length ?? 0); j++) {
            A[i]![j] = (A[i]![j] ?? 0) * factor;
        }
    }
}

async function readMed1Signal(bwPath: string, chr: string, start: number, end: number, binCount: number): Promise<number[]> {
    try {
        const { BigWig } = await import('@gmod/bbi');
        const file = new BigWig({ path: bwPath });
        await file.getHeader();
        const signalBins: number[] = [];
        const binWidth = Math.floor((end - start) / binCount);
        for (let i = 0; i < binCount; i++) {
            const s = start + i * binWidth;
            const e = Math.min(end, s + binWidth);
            const feats = await file.getFeatures(chr, s, e, { scale: 1 });
            let sum = 0, n = 0;
            for (const f of feats) {
                sum += (f as { score?: number }).score ?? 0;
                n++;
            }
            signalBins.push(n > 0 ? sum / n : 0);
        }
        return signalBins;
    } catch {
        return Array(binCount).fill(1);
    }
}

// ========== Simulation ==========
async function runCondition(
    signalBins: number[],
    beta: number,
    condition: 'WT' | 'MED1-KD',
    numRuns: number
): Promise<{ rawMatrix: number[][]; totalSteps: number; totalLoops: number }> {
    const effectiveSignal = condition === 'MED1-KD' ? Array(signalBins.length).fill(1) : signalBins;
    const fountain = new FountainLoader({
        signalBins: effectiveSignal,
        genomeStart: 0,
        genomeEnd: HBB_LENGTH,
        baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
        beta: condition === 'MED1-KD' ? BETA_KD : beta,
    });

    const ctcfSites = HBB_CTCF_SITES.map(s =>
        createCTCFSite(HBB_CHR, s.pos, s.orient, s.strength)
    );

    const nBins = Math.floor(HBB_LENGTH / RESOLUTION);
    const occupancyMatrix = createZeroMatrix(nBins);
    let totalLoops = 0;
    let totalSteps = 0;

    for (let run = 0; run < numRuns; run++) {
        const engine = new MultiCohesinEngine({
            genomeLength: HBB_LENGTH,
            ctcfSites,
            velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
            unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
            spatialLoader: fountain,
            numCohesins: NUM_COHESINS,
            trackLoopDuration: false,
            seed: run * 2000 + (condition === 'MED1-KD' ? 10000 : 0),
            maxSteps: MAX_STEPS,
        });

        for (let step = 0; step < MAX_STEPS; step++) {
            engine.step();
            engine.updateOccupancyMatrix(occupancyMatrix, RESOLUTION);
            totalSteps++;
        }
        totalLoops += engine.getLoops().length;
    }

    scaleMatrix(occupancyMatrix, 1 / totalSteps);
    return { rawMatrix: occupancyMatrix, totalSteps, totalLoops };
}

// ========== Main ==========
function parseArgs(): { runs: number; outFile: string } {
    let runs = 20;
    let outFile = 'med1_kd_hbb.json';
    for (const arg of process.argv.slice(2)) {
        if (arg.startsWith('--runs=')) runs = Number(arg.slice(7));
        else if (arg.startsWith('--out=')) outFile = arg.slice(6);
    }
    return { runs, outFile };
}

async function main(): Promise<void> {
    const { runs: numRuns, outFile } = parseArgs();
    if (!fs.existsSync(RESULTS_DIR)) fs.mkdirSync(RESULTS_DIR, { recursive: true });

    console.log('='.repeat(60));
    console.log('In Silico MED1 Knockdown — HBB Locus');
    console.log('='.repeat(60));
    console.log(`Locus: ${HBB_CHR}:${HBB_START}-${HBB_END} (${HBB_LENGTH / 1000} kb)`);
    console.log(`WT: beta=${BETA_WT}, MED1-KD: beta=${BETA_KD}`);
    console.log(`Runs: ${numRuns}, steps/run: ${MAX_STEPS}, resolution: ${RESOLUTION} bp`);
    console.log('');

    const bwPath = MED1_BW_PATH;
    const signalBins = fs.existsSync(bwPath)
        ? await readMed1Signal(bwPath, HBB_CHR, HBB_START, HBB_END, BIN_COUNT)
        : Array(BIN_COUNT).fill(1);
    console.log(`MED1 signal: ${fs.existsSync(bwPath) ? 'BigWig' : 'constant (file not found)'}`);
    console.log('');

    // Параллельные симуляции
    console.log('Running WT...');
    const wtResult = await runCondition(signalBins, BETA_WT, 'WT', numRuns);
    console.log('Running MED1-KD...');
    const kdResult = await runCondition(signalBins, BETA_KD, 'MED1-KD', numRuns);

    const nBins = wtResult.rawMatrix.length;
    const expected = buildExpectedMatrix(nBins, -1);

    // O/E нормализация (v1.5)
    const wtOE = applyOENormalization(wtResult.rawMatrix, expected);
    const kdOE = applyOENormalization(kdResult.rawMatrix, expected);

    // Diff Map: WT - KD (по O/E матрицам)
    const diffMap: number[][] = [];
    let minD = Infinity, maxD = -Infinity;
    for (let i = 0; i < nBins; i++) {
        const row: number[] = [];
        for (let j = 0; j < nBins; j++) {
            const d = (wtOE[i]?.[j] ?? 0) - (kdOE[i]?.[j] ?? 0);
            row.push(d);
            if (d < minD) minD = d;
            if (d > maxD) maxD = d;
        }
        diffMap.push(row);
    }

    // Insulation Score (полоса ±2 бина от диагонали)
    const halfWindow = 2;
    const wtInsulation = computeInsulationScore(wtOE, halfWindow);
    const kdInsulation = computeInsulationScore(kdOE, halfWindow);
    const wtClarity = insulationClarity(wtInsulation);
    const kdClarity = insulationClarity(kdInsulation);

    // Вердикт: снизилась ли четкость TAD-границ в KD?
    // Четкость = std или dynamicRange; при KD ожидаем более плоский профиль → меньше std/dynamicRange
    const clarityReduced = kdClarity.std < wtClarity.std || kdClarity.dynamicRange < wtClarity.dynamicRange;
    const verdict = clarityReduced
        ? 'ДА — четкость TAD-границ в режиме MED1-KD снизилась (более плоский insulation profile).'
        : 'НЕТ — четкость TAD-границ в режиме MED1-KD не снизилась по выбранной метрике.';

    const payload = {
        experiment: 'MED1_Knockdown_HBB',
        locus: { chrom: HBB_CHR, start: HBB_START, end: HBB_END, length_bp: HBB_LENGTH },
        params: {
            resolution: RESOLUTION,
            maxSteps: MAX_STEPS,
            numRuns,
            betaWT: BETA_WT,
            betaKD: BETA_KD,
            normalization: 'O/E (observed/expected, power-law alpha=-1)',
        },
        wt: {
            totalSteps: wtResult.totalSteps,
            totalLoops: wtResult.totalLoops,
            heatmap_raw: wtResult.rawMatrix,
            heatmap_oe: wtOE,
            insulationScore: wtInsulation,
            insulationClarity: wtClarity,
        },
        med1KD: {
            totalSteps: kdResult.totalSteps,
            totalLoops: kdResult.totalLoops,
            heatmap_raw: kdResult.rawMatrix,
            heatmap_oe: kdOE,
            insulationScore: kdInsulation,
            insulationClarity: kdClarity,
        },
        diffMap: {
            description: 'WT_OE - KD_OE',
            matrix: diffMap,
            stats: { min: minD, max: maxD },
        },
        insulationComparison: {
            wt: wtClarity,
            kd: kdClarity,
            clarityReduced,
        },
        verdict,
    };

    const outPath = path.join(RESULTS_DIR, outFile);
    fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf-8');
    console.log('');
    console.log('Written:', outPath);
    console.log('');
    console.log('--- Insulation (O/E) ---');
    console.log('  WT:     mean=', wtClarity.mean.toFixed(4), ' std=', wtClarity.std.toFixed(4), ' range=', wtClarity.dynamicRange.toFixed(4));
    console.log('  MED1-KD: mean=', kdClarity.mean.toFixed(4), ' std=', kdClarity.std.toFixed(4), ' range=', kdClarity.dynamicRange.toFixed(4));
    console.log('');
    console.log('--- Verdict ---');
    console.log('  Снизилась ли четкость TAD-границ в режиме KD?', verdict);
    console.log('='.repeat(60));
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
