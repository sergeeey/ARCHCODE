/**
 * H2: Mediator-driven Cohesin Fountains — тест на локусе MYC.
 * Параметры Sabaté 2024 (bioRxiv): unloadingProb = 1/1000, velocity = 300.
 * FountainLoader с beta = 2.0, MED1 из BigWig (или fallback).
 * Результат: results/fountain_test_v1.json (теплокарта + метаданные).
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

const MED1_BW_PATH = 'D:\\ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ\\data\\inputs\\med1\\MED1_GM12878_Rep1.bw';
const MYC_CHR = 'chr8';
const MYC_START = 127_700_000;
const MYC_END = 128_800_000;
const MYC_LENGTH = MYC_END - MYC_START; // 1_100_000
const BIN_COUNT = 500;
const DEFAULT_BETA = 20.0;  // Экстремальное значение для теста
const RESOLUTION = 5000;

function parseArgs(): { beta: number; outFile: string; seed: number; runs: number } {
    let beta = DEFAULT_BETA;
    let outFile = 'fountain_test_v1.json';
    let seed = SEED;
    let runs = 1;
    for (const arg of process.argv.slice(2)) {
        if (arg.startsWith('--beta=')) beta = Number(arg.slice(7));
        else if (arg.startsWith('--out=')) outFile = arg.slice(6);
        else if (arg.startsWith('--seed=')) seed = Number(arg.slice(7));
        else if (arg.startsWith('--runs=')) runs = Number(arg.slice(7));
    }
    return { beta, outFile, seed, runs };
}
const MAX_STEPS = 50_000;  // Увеличено для статистики
const NUM_COHESINS = 20;   // Больше машин на шоссе
const SEED = 2000;

/** Минимальный набор CTCF-подобных сайтов для MYC (конвергентные пары для петель) */
const MYC_CTCF_SITES = [
    { pos: 100_000, strength: 0.9, orient: 'F' as const },
    { pos: 250_000, strength: 0.85, orient: 'R' as const },
    { pos: 500_000, strength: 0.8, orient: 'F' as const },
    { pos: 650_000, strength: 0.9, orient: 'R' as const },
    { pos: 900_000, strength: 0.85, orient: 'F' as const },
    { pos: 1_050_000, strength: 0.9, orient: 'R' as const },
];

async function readMed1BigWig(bwPath: string): Promise<number[] | null> {
    try {
        const { BigWig } = await import('@gmod/bbi');
        const file = new BigWig({ path: bwPath });
        await file.getHeader();
        const signalBins: number[] = [];
        const binWidth = Math.floor((MYC_END - MYC_START) / BIN_COUNT);
        for (let i = 0; i < BIN_COUNT; i++) {
            const start = MYC_START + i * binWidth;
            const end = Math.min(MYC_END, start + binWidth);
            const feats = await file.getFeatures(MYC_CHR, start, end, { scale: 1 });
            let sum = 0;
            let n = 0;
            for (const f of feats) {
                const score = (f as { score?: number }).score ?? 0;
                sum += score;
                n++;
            }
            signalBins.push(n > 0 ? sum / n : 0);
        }
        return signalBins;
    } catch (e) {
        console.warn('[run-fountain-myc] BigWig read failed, using constant signal:', (e as Error).message);
        return null;
    }
}

/** Fallback: постоянный сигнал (медиана = 1, P_loading равномерная) */
function constantSignal(n: number): number[] {
    return Array(n).fill(1);
}

async function main(): Promise<void> {
    const { beta: BETA, outFile, seed: SEED_ARG, runs: NUM_RUNS } = parseArgs();
    const outPath = path.join(__dirname, '..', 'results', outFile);
    const resultsDir = path.dirname(outPath);
    if (!fs.existsSync(resultsDir)) {
        fs.mkdirSync(resultsDir, { recursive: true });
    }

    let signalBins: number[];
    let med1Source: string;

    const bwPath = process.env.MED1_BW ?? MED1_BW_PATH;
    if (fs.existsSync(bwPath)) {
        const read = await readMed1BigWig(bwPath);
        if (read != null) {
            signalBins = read;
            med1Source = bwPath;
        } else {
            signalBins = constantSignal(BIN_COUNT);
            med1Source = 'constant (BigWig unavailable)';
        }
    } else {
        signalBins = constantSignal(BIN_COUNT);
        med1Source = 'constant (file not found: ' + bwPath + ')';
    }

    const fountain = new FountainLoader({
        signalBins,
        genomeStart: 0,
        genomeEnd: MYC_LENGTH,
        baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
        beta: BETA,
    });

    const ctcfSites = MYC_CTCF_SITES.map(s =>
        createCTCFSite(MYC_CHR, s.pos, s.orient, s.strength)
    );

    const engine = new MultiCohesinEngine({
        genomeLength: MYC_LENGTH,
        ctcfSites,
        velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
        unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
        spatialLoader: fountain,
        numCohesins: NUM_COHESINS,
        trackLoopDuration: false,
        seed: SEED_ARG,
        maxSteps: MAX_STEPS,
    });

    // Debug: логирование каждые 1000 шагов
    console.log('[run-fountain-myc] Starting simulation...');
    console.log(`  stepLoadingProbability = ${fountain.getStepLoadingProbability()}`);
    console.log(`  medianSignal = ${fountain.getMedianSignal()}`);
    console.log(`  beta = ${BETA}, numCohesins = ${NUM_COHESINS}, maxSteps = ${MAX_STEPS}`);

    for (let step = 0; step < MAX_STEPS; step++) {
        engine.step();
        if (step % 10000 === 0) {
            const cohesins = engine.getCohesins();
            const activeCount = cohesins.filter(c => c.active).length;
            console.log(`  step ${step}: active cohesins = ${activeCount}, total loops = ${engine.getLoops().length}`);
        }
    }
    const loops = engine.getLoops();
    const matrix = engine.getContactMatrix(RESOLUTION, 0.1);

    const payload = {
        hypothesis: 'H2_MediatorDrivenCohesinFountains',
        locus: { chrom: MYC_CHR, start: MYC_START, end: MYC_END, length_bp: MYC_LENGTH },
        params: {
            unloadingProb: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
            velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
            beta: BETA,
            baselineLoadingRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
            maxSteps: MAX_STEPS,
            resolution: RESOLUTION,
            seed: SEED_ARG,
        },
        med1Source,
        fountainLoader: {
            stepLoadingProbability: fountain.getStepLoadingProbability(),
            medianSignal: fountain.getMedianSignal(),
            binCount: fountain.getBinCount(),
        },
        numLoops: loops.length,
        heatmap: matrix,
        loopsSummary: loops.slice(0, 50).map(l => ({
            leftAnchor: l.leftAnchor,
            rightAnchor: l.rightAnchor,
            strength: l.strength,
        })),
    };

    fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), 'utf-8');
    console.log('[run-fountain-myc] Written', outPath, '| loops:', loops.length, '| matrix:', matrix.length, 'x', matrix[0]?.length);
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
