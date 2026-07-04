/**
 * H2: Blind Validation — Cohesin Fountains on SOX2 locus (chr3).
 *
 * SOX2 is a key pluripotency transcription factor with a large regulatory
 * landscape containing multiple enhancers (SCR - SOX2 Control Region).
 *
 * This is a BLIND TEST: model was calibrated on MYC, now tested on SOX2.
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

// === SOX2 Locus Parameters (hg38) ===
const MED1_BW_PATH =
  "D:\\ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ\\data\\inputs\\med1\\MED1_GM12878_Rep1.bw";
const SOX2_CHR = "chr3";
const SOX2_START = 181_000_000;
const SOX2_END = 181_800_000;
const SOX2_LENGTH = SOX2_END - SOX2_START; // 800,000 bp

const BIN_COUNT = 500;
const RESOLUTION = 5000;
const MAX_STEPS = 50_000;
const NUM_COHESINS = 15;
const DEFAULT_BETA = 5.0;
const DEFAULT_RUNS = 20;

/**
 * CTCF sites for SOX2 locus (approximate positions based on literature).
 *
 * SOX2 gene is located around chr3:181,711,925-181,714,436 (hg38).
 * The SCR (SOX2 Control Region) is ~100kb downstream.
 * Multiple enhancers are spread across the regulatory domain.
 *
 * Positions are relative to SOX2_START (0 = 181,000,000).
 */
const SOX2_CTCF_SITES = [
  // 5' boundary of TAD
  { pos: 50_000, strength: 0.9, orient: "R" as const },
  { pos: 150_000, strength: 0.85, orient: "R" as const },

  // Upstream enhancer region
  { pos: 300_000, strength: 0.85, orient: "F" as const },
  { pos: 400_000, strength: 0.9, orient: "R" as const },

  // Near SOX2 gene (~711,925 relative = 711kb from 181M)
  { pos: 500_000, strength: 0.9, orient: "F" as const },
  { pos: 600_000, strength: 0.85, orient: "R" as const },

  // SCR enhancer region (downstream)
  { pos: 700_000, strength: 0.95, orient: "F" as const },
  { pos: 750_000, strength: 0.9, orient: "R" as const },
];

function parseArgs() {
  let beta = DEFAULT_BETA;
  let numRuns = DEFAULT_RUNS;
  let outFile = "ensemble_sox2_beta5.json";
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
    const binWidth = Math.floor(SOX2_LENGTH / BIN_COUNT);
    for (let i = 0; i < BIN_COUNT; i++) {
      const start = SOX2_START + i * binWidth;
      const end = Math.min(SOX2_END, start + binWidth);
      const feats = await file.getFeatures(SOX2_CHR, start, end, { scale: 1 });
      let sum = 0,
        n = 0;
      for (const f of feats) {
        sum += (f as { score?: number }).score ?? 0;
        n++;
      }
      signalBins.push(n > 0 ? sum / n : 0);
    }
    console.log(
      `[SOX2] MED1 signal loaded: ${signalBins.filter((x) => x > 0).length} non-zero bins`,
    );
    return signalBins;
  } catch (e) {
    console.warn("[SOX2] BigWig read failed:", (e as Error).message);
    return null;
  }
}

function constantSignal(n: number): number[] {
  return Array(n).fill(1);
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

  console.log("=".repeat(60));
  console.log("SOX2 LOCUS BLIND VALIDATION");
  console.log("=".repeat(60));
  console.log(
    `Locus: ${SOX2_CHR}:${SOX2_START.toLocaleString()}-${SOX2_END.toLocaleString()}`,
  );
  console.log(`Length: ${(SOX2_LENGTH / 1_000_000).toFixed(2)} Mb`);
  console.log(`CTCF sites: ${SOX2_CTCF_SITES.length}`);
  console.log("");

  const bwPath = process.env.MED1_BW ?? MED1_BW_PATH;
  let signalBins = fs.existsSync(bwPath) ? await readMed1BigWig(bwPath) : null;
  const med1Source = signalBins ? bwPath : "constant (file not found)";
  if (!signalBins) signalBins = constantSignal(BIN_COUNT);

  const fountain = new FountainLoader({
    signalBins,
    genomeStart: 0,
    genomeEnd: SOX2_LENGTH,
    baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
    beta,
  });

  const ctcfSites = SOX2_CTCF_SITES.map((s) =>
    createCTCFSite(SOX2_CHR, s.pos, s.orient, s.strength),
  );

  const nBins = Math.floor(SOX2_LENGTH / RESOLUTION);
  console.log(
    `[ensemble] beta=${beta}, runs=${numRuns}, steps=${MAX_STEPS}, bins=${nBins}`,
  );
  console.log(
    `  stepLoadingProbability = ${fountain.getStepLoadingProbability().toFixed(6)}`,
  );
  console.log(`  medianSignal = ${fountain.getMedianSignal().toFixed(4)}`);
  console.log("");

  const occupancyMatrix = createZeroMatrix(nBins);
  let totalLoops = 0;
  let totalSteps = 0;

  for (let run = 0; run < numRuns; run++) {
    const engine = new MultiCohesinEngine({
      genomeLength: SOX2_LENGTH,
      ctcfSites,
      velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
      unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
      spatialLoader: fountain,
      numCohesins: NUM_COHESINS,
      trackLoopDuration: false,
      seed: run * 1000,
      maxSteps: MAX_STEPS,
    });

    for (let step = 0; step < MAX_STEPS; step++) {
      engine.step();
      engine.updateOccupancyMatrix(occupancyMatrix, RESOLUTION);
      totalSteps++;
    }
    totalLoops += engine.getLoops().length;

    if ((run + 1) % 5 === 0) {
      console.log(
        `  run ${run + 1}/${numRuns} done, loops so far: ${totalLoops}`,
      );
    }
  }

  scaleMatrix(occupancyMatrix, 1 / totalSteps);

  const payload = {
    hypothesis: "H2_CohesinFountains_BlindTest",
    locus: {
      name: "SOX2",
      chrom: SOX2_CHR,
      start: SOX2_START,
      end: SOX2_END,
      length_bp: SOX2_LENGTH,
    },
    ctcfSites: SOX2_CTCF_SITES,
    params: {
      beta,
      numRuns,
      maxSteps: MAX_STEPS,
      totalSteps,
      numCohesins: NUM_COHESINS,
      resolution: RESOLUTION,
    },
    med1Source,
    fountainLoader: {
      stepLoadingProbability: fountain.getStepLoadingProbability(),
      medianSignal: fountain.getMedianSignal(),
      binCount: fountain.getBinCount(),
    },
    avgLoopsPerRun: totalLoops / numRuns,
    heatmap: occupancyMatrix,
  };

  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2), "utf-8");
  console.log("");
  console.log(`[SOX2] Written ${outPath}`);
  console.log(`[SOX2] avgLoops = ${(totalLoops / numRuns).toFixed(1)}`);
  console.log("=".repeat(60));
}

main().catch(console.error);
