/**
 * Ensemble run: запускает N симуляций с разными seeds и усредняет тепловую карту.
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

import { createCTCFSite } from "../src/domain/models/genome";
import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";
import { FountainLoader } from "../src/simulation/SpatialLoadingModule";
import { SABATE_NATURE_2025 } from "../src/domain/constants/biophysics";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const MED1_BW_PATH =
  "D:\\ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ\\data\\inputs\\med1\\MED1_GM12878_Rep1.bw";
const MYC_CHR = "chr8";
const MYC_START = 127_700_000;
const MYC_END = 128_800_000;
const MYC_LENGTH = MYC_END - MYC_START;
const BIN_COUNT = 500;
const RESOLUTION = 5000;
const MAX_STEPS = 50_000;
const NUM_COHESINS = 15;

const MYC_CTCF_SITES = [
  { pos: 100_000, strength: 0.9, orient: "F" as const },
  { pos: 250_000, strength: 0.85, orient: "R" as const },
  { pos: 500_000, strength: 0.8, orient: "F" as const },
  { pos: 650_000, strength: 0.9, orient: "R" as const },
  { pos: 900_000, strength: 0.85, orient: "F" as const },
  { pos: 1_050_000, strength: 0.9, orient: "R" as const },
];

function parseArgs() {
  let beta = 0;
  let numRuns = 10;
  let outFile = "ensemble_result.json";
  for (const arg of process.argv.slice(2)) {
    if (arg.startsWith("--beta=")) beta = Number(arg.slice(7));
    else if (arg.startsWith("--runs=")) numRuns = Number(arg.slice(7));
    else if (arg.startsWith("--out=")) outFile = arg.slice(6);
  }
  return { beta, numRuns, outFile };
}

async function readMed1BigWig(bwPath: string): Promise<number[] | null> {
  try {
    const { BigWig } = await import("@gmod/bbi");
    const file = new BigWig({ path: bwPath });
    await file.getHeader();
    const signalBins: number[] = [];
    const binWidth = Math.floor((MYC_END - MYC_START) / BIN_COUNT);
    for (let i = 0; i < BIN_COUNT; i++) {
      const start = MYC_START + i * binWidth;
      const end = Math.min(MYC_END, start + binWidth);
      const feats = await file.getFeatures(MYC_CHR, start, end, { scale: 1 });
      let sum = 0,
        n = 0;
      for (const f of feats) {
        sum += (f as { score?: number }).score ?? 0;
        n++;
      }
      signalBins.push(n > 0 ? sum / n : 0);
    }
    return signalBins;
  } catch {
    return null;
  }
}

function constantSignal(n: number): number[] {
  return Array(n).fill(1);
}

function addMatrix(A: number[][], B: number[][]): void {
  for (let i = 0; i < A.length; i++) {
    for (let j = 0; j < (A[i]?.length ?? 0); j++) {
      A[i]![j] = (A[i]![j] ?? 0) + (B[i]?.[j] ?? 0);
    }
  }
}

function scaleMatrix(A: number[][], factor: number): void {
  for (let i = 0; i < A.length; i++) {
    for (let j = 0; j < (A[i]?.length ?? 0); j++) {
      A[i]![j] = (A[i]![j] ?? 0) * factor;
    }
  }
}

function createZeroMatrix(size: number): number[][] {
  return Array(size)
    .fill(null)
    .map(() => Array(size).fill(0));
}

async function main() {
  const { beta, numRuns, outFile } = parseArgs();
  const outPath = path.join(__dirname, "..", "results", outFile);

  const bwPath = process.env.MED1_BW ?? MED1_BW_PATH;
  let signalBins = fs.existsSync(bwPath) ? await readMed1BigWig(bwPath) : null;
  if (!signalBins) signalBins = constantSignal(BIN_COUNT);

  const fountain = new FountainLoader({
    signalBins,
    genomeStart: 0,
    genomeEnd: MYC_LENGTH,
    baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
    beta,
  });

  const ctcfSites = MYC_CTCF_SITES.map((s) =>
    createCTCFSite(MYC_CHR, s.pos, s.orient, s.strength),
  );

  const nBins = Math.floor(MYC_LENGTH / RESOLUTION);
  console.log(
    `[ensemble] beta=${beta}, runs=${numRuns}, steps=${MAX_STEPS}, bins=${nBins}`,
  );
  console.log(
    `  stepLoadingProbability = ${fountain.getStepLoadingProbability()}`,
  );

  // Accumulate occupancy across all runs
  const occupancyMatrix = createZeroMatrix(nBins);
  let totalLoops = 0;
  let totalSteps = 0;

  for (let run = 0; run < numRuns; run++) {
    const engine = new MultiCohesinEngine({
      genomeLength: MYC_LENGTH,
      ctcfSites,
      velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
      unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
      spatialLoader: fountain,
      numCohesins: NUM_COHESINS,
      trackLoopDuration: false,
      seed: run * 1000, // Different seed per run
      maxSteps: MAX_STEPS,
    });

    // Run step-by-step and accumulate occupancy
    for (let step = 0; step < MAX_STEPS; step++) {
      engine.step();
      engine.updateOccupancyMatrix(occupancyMatrix, RESOLUTION);
      totalSteps++;
    }
    totalLoops += engine.getLoops().length;

    if ((run + 1) % 5 === 0) {
      console.log(`  run ${run + 1}/${numRuns} done`);
    }
  }

  // Normalize by total steps to get contact probability
  scaleMatrix(occupancyMatrix, 1 / totalSteps);

  const payload = {
    beta,
    numRuns,
    maxSteps: MAX_STEPS,
    totalSteps,
    stepLoadingProbability: fountain.getStepLoadingProbability(),
    avgLoopsPerRun: totalLoops / numRuns,
    heatmap: occupancyMatrix,
  };

  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), "utf-8");
  console.log(
    `[ensemble] Written ${outPath} | avgLoops=${(totalLoops / numRuns).toFixed(1)}`,
  );
}

main().catch(console.error);
