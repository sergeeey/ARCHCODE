/**
 * EXP-009: Genome-wide vs Focal Cohesin Loading — Ablation Study
 *
 * Tests Anderson et al. 2026 (bioRxiv) finding that focal enhancer loading
 * is incompatible with long-range transcriptional control.
 *
 * Mode A: Genome-wide stochastic loading (ARCHCODE default)
 * Mode B: Focal loading concentrated at LCR enhancer positions
 *
 * Compares both against K562 Hi-C reference data (Pearson r).
 *
 * Run: npx tsx scripts/exp_loading_mode_ablation.ts
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createCTCFSite } from "../src/domain/models/genome";
import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";
import { FountainLoader } from "../src/simulation/SpatialLoadingModule";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// HBB 95kb sub-TAD config (ENCODE-validated)
const LOCUS = {
  chromosome: "chr11",
  start: 5200000,
  end: 5295000,
  length: 95000,
  resolution: 1000, // 1kb bins for Hi-C comparison
};

const N_BINS = Math.floor(LOCUS.length / LOCUS.resolution);

// CTCF sites from ENCODE K562 (ENCFF660GHM)
const CTCF_SITES = [
  { pos: 4979, orient: "F" as const, strength: 0.9 },   // 3'HS1, signal=225
  { pos: 80811, orient: "R" as const, strength: 0.5 },   // near_HS2, signal=22
  { pos: 89092, orient: "F" as const, strength: 0.5 },   // near_HS4, signal=21.5
  { pos: 91442, orient: "R" as const, strength: 0.95 },  // HS5, signal=260
];

// LCR enhancer positions (relative to locus start)
const ENHANCER_POSITIONS = [
  { relPos: 26268, name: "HBB_promoter", occupancy: 0.85 },
  { relPos: 75800, name: "LCR_HS1", occupancy: 0.4 },
  { relPos: 80700, name: "LCR_HS2", occupancy: 0.9 },
  { relPos: 84800, name: "LCR_HS3", occupancy: 0.7 },
  { relPos: 88250, name: "LCR_HS4", occupancy: 0.6 },
];

const N_SIMULATIONS = 20; // Ensemble runs for robust statistics
const MAX_STEPS = 50000; // Long runs to accumulate loop signal
const NUM_COHESINS = 20;

function createFocalLoader(): FountainLoader {
  // Create signal array: near-zero everywhere, high peaks at enhancer positions
  const signalBins = new Array(N_BINS).fill(0.01); // minimal background
  for (const enh of ENHANCER_POSITIONS) {
    const bin = Math.floor(enh.relPos / LOCUS.resolution);
    // Gaussian peak around enhancer (sigma = 2kb)
    const sigma = 2; // bins
    for (let i = Math.max(0, bin - 10); i < Math.min(N_BINS, bin + 10); i++) {
      const dist = Math.abs(i - bin);
      signalBins[i] += enh.occupancy * 100 * Math.exp(-0.5 * (dist / sigma) ** 2);
    }
  }

  return new FountainLoader({
    signalBins,
    genomeStart: 0,
    genomeEnd: LOCUS.length,
    baselineRate: 1 / 3600,
    beta: 5.0, // Strong focal bias
  });
}

function runSimulation(
  mode: "genome-wide" | "focal",
  seed: number,
): number[][] {
  const sites = CTCF_SITES.map((s) =>
    createCTCFSite(LOCUS.chromosome, s.pos, s.orient, s.strength),
  );

  const config: any = {
    genomeLength: LOCUS.length,
    ctcfSites: sites,
    numCohesins: NUM_COHESINS,
    velocity: 1000,
    unloadingProbability: 0.001,
    seed,
    maxSteps: MAX_STEPS,
    verbose: false,
  };

  if (mode === "focal") {
    config.spatialLoader = createFocalLoader();
    // Focal mode: spatialLoader overrides uniform loading
    // Engine starts with 1 cohesin at midpoint, loads new via FountainLoader
    config.numCohesins = 1;
  }

  const engine = new MultiCohesinEngine(config);
  const loops = engine.run(MAX_STEPS);

  // Build contact matrix at specified resolution
  const matrix: number[][] = Array(N_BINS)
    .fill(0)
    .map(() => Array(N_BINS).fill(0));

  for (const loop of loops) {
    const bin1 = Math.floor(loop.leftAnchor / LOCUS.resolution);
    const bin2 = Math.floor(loop.rightAnchor / LOCUS.resolution);
    if (bin1 >= 0 && bin1 < N_BINS && bin2 >= 0 && bin2 < N_BINS) {
      matrix[bin1][bin2] += loop.strength;
      matrix[bin2][bin1] += loop.strength;
    }
  }

  return { matrix, loopCount: loops.length, loops };
}

function averageMatrices(matrices: number[][][]): number[][] {
  const n = matrices[0].length;
  const avg: number[][] = Array(n)
    .fill(0)
    .map(() => Array(n).fill(0));
  for (const m of matrices) {
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        avg[i][j] += m[i][j] / matrices.length;
      }
    }
  }
  return avg;
}

function pearsonCorrelation(a: number[], b: number[]): number {
  const n = a.length;
  if (n !== b.length || n === 0) return 0;

  let sumA = 0, sumB = 0, sumAB = 0, sumA2 = 0, sumB2 = 0;
  for (let i = 0; i < n; i++) {
    sumA += a[i];
    sumB += b[i];
    sumAB += a[i] * b[i];
    sumA2 += a[i] * a[i];
    sumB2 += b[i] * b[i];
  }

  const numerator = n * sumAB - sumA * sumB;
  const denominator = Math.sqrt(
    (n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB),
  );

  return denominator === 0 ? 0 : numerator / denominator;
}

function flattenUpperTriangle(matrix: number[][]): number[] {
  const flat: number[] = [];
  const n = matrix.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      flat.push(matrix[i][j]);
    }
  }
  return flat;
}

function matrixStats(matrix: number[][]): {
  mean: number;
  max: number;
  nonZero: number;
  totalContacts: number;
} {
  let sum = 0, max = 0, nonZero = 0;
  const n = matrix.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const v = matrix[i][j];
      sum += v;
      if (v > max) max = v;
      if (v > 0) nonZero++;
    }
  }
  const total = (n * (n - 1)) / 2;
  return {
    mean: sum / total,
    max,
    nonZero,
    totalContacts: sum,
  };
}

async function main() {
  console.log("═══════════════════════════════════════════════════════════");
  console.log("  EXP-009: Cohesin Loading Mode Ablation");
  console.log("  Genome-wide (A) vs Focal enhancer loading (B)");
  console.log("  Anderson et al. 2026 validation");
  console.log("═══════════════════════════════════════════════════════════\n");

  // Load Hi-C reference
  const hicPath = path.join(
    __dirname,
    "..",
    "data",
    "reference",
    "HBB_K562_HiC_95kb_1000bp.npy",
  );

  let hicMatrix: number[][] | null = null;
  let hicFlat: number[] | null = null;

  if (fs.existsSync(hicPath)) {
    console.log(`📊 Loading Hi-C reference: ${hicPath}`);
    // Load numpy file via python
    const { execSync } = await import("child_process");
    try {
      const pyCode = `
import numpy as np, json, sys
m = np.load(r'${hicPath.replace(/\\/g, "\\\\")}')
if m.shape[0] != ${N_BINS}:
    from scipy.ndimage import zoom
    factor = ${N_BINS} / m.shape[0]
    m = zoom(m, factor, order=1)
print(json.dumps(m.tolist()))
`;
      const result = execSync(`python -c "${pyCode}"`, {
        maxBuffer: 50 * 1024 * 1024,
      }).toString();
      hicMatrix = JSON.parse(result);
      hicFlat = flattenUpperTriangle(hicMatrix!);
      console.log(`   Shape: ${hicMatrix!.length}x${hicMatrix![0].length}\n`);
    } catch (e) {
      console.log(`   ⚠️ Could not load Hi-C (will compare modes only)\n`);
    }
  } else {
    console.log(`⚠️ Hi-C reference not found at ${hicPath}`);
    console.log(`   Will compare Mode A vs Mode B without external reference\n`);
  }

  // Run Mode A: Genome-wide loading
  console.log("🔄 Mode A: Genome-wide stochastic loading...");
  const modeAMatrices: number[][][] = [];
  let modeALoops = 0;
  const modeALoopLengths: number[] = [];
  for (let i = 0; i < N_SIMULATIONS; i++) {
    const result = runSimulation("genome-wide", 42 + i);
    modeAMatrices.push(result.matrix);
    modeALoops += result.loopCount;
    for (const loop of result.loops) {
      modeALoopLengths.push(Math.abs(loop.rightAnchor - loop.leftAnchor));
    }
    process.stdout.write(`   Run ${i + 1}/${N_SIMULATIONS}\r`);
  }
  const modeAAvg = averageMatrices(modeAMatrices);
  const modeAFlat = flattenUpperTriangle(modeAAvg);
  const modeAStats = matrixStats(modeAAvg);
  const modeAMeanLoopLen = modeALoopLengths.length > 0
    ? modeALoopLengths.reduce((a, b) => a + b, 0) / modeALoopLengths.length
    : 0;
  console.log(`✅ Mode A complete`);
  console.log(`   Total loops: ${modeALoops} (${(modeALoops / N_SIMULATIONS).toFixed(1)} per run)`);
  console.log(`   Mean loop length: ${(modeAMeanLoopLen / 1000).toFixed(1)} kb`);
  console.log(`   Total contacts: ${modeAStats.totalContacts.toFixed(2)}`);
  console.log(`   Non-zero bins: ${modeAStats.nonZero}\n`);

  // Run Mode B: Focal loading
  console.log("🔄 Mode B: Focal enhancer loading...");
  const modeBMatrices: number[][][] = [];
  let modeBLoops = 0;
  const modeBLoopLengths: number[] = [];
  for (let i = 0; i < N_SIMULATIONS; i++) {
    const result = runSimulation("focal", 42 + i);
    modeBMatrices.push(result.matrix);
    modeBLoops += result.loopCount;
    for (const loop of result.loops) {
      modeBLoopLengths.push(Math.abs(loop.rightAnchor - loop.leftAnchor));
    }
    process.stdout.write(`   Run ${i + 1}/${N_SIMULATIONS}\r`);
  }
  const modeBAvg = averageMatrices(modeBMatrices);
  const modeBFlat = flattenUpperTriangle(modeBAvg);
  const modeBStats = matrixStats(modeBAvg);
  const modeBMeanLoopLen = modeBLoopLengths.length > 0
    ? modeBLoopLengths.reduce((a, b) => a + b, 0) / modeBLoopLengths.length
    : 0;
  console.log(`✅ Mode B complete`);
  console.log(`   Total loops: ${modeBLoops} (${(modeBLoops / N_SIMULATIONS).toFixed(1)} per run)`);
  console.log(`   Mean loop length: ${(modeBMeanLoopLen / 1000).toFixed(1)} kb`);
  console.log(`   Total contacts: ${modeBStats.totalContacts.toFixed(2)}`);
  console.log(`   Non-zero bins: ${modeBStats.nonZero}\n`);

  // Compute correlations
  console.log("📈 Correlation analysis:");
  console.log("─────────────────────────────────────────────");

  const rAB = pearsonCorrelation(modeAFlat, modeBFlat);
  console.log(`   Mode A vs Mode B (inter-model): r = ${rAB.toFixed(4)}`);

  if (hicFlat) {
    const rA_HiC = pearsonCorrelation(modeAFlat, hicFlat);
    const rB_HiC = pearsonCorrelation(modeBFlat, hicFlat);
    console.log(`   Mode A vs Hi-C (genome-wide):   r = ${rA_HiC.toFixed(4)}`);
    console.log(`   Mode B vs Hi-C (focal):         r = ${rB_HiC.toFixed(4)}`);
    console.log(`\n   Δr (A - B) = ${(rA_HiC - rB_HiC).toFixed(4)}`);

    if (rA_HiC > rB_HiC) {
      console.log(`   ✅ Genome-wide loading BETTER correlates with experimental Hi-C`);
      console.log(`   → Consistent with Anderson et al. 2026`);
    } else {
      console.log(`   ⚠️ Focal loading shows higher Hi-C correlation`);
      console.log(`   → Unexpected — investigate further`);
    }

    // Save results
    const results = {
      experiment: "EXP-009",
      title: "Cohesin Loading Mode Ablation",
      reference: "Anderson et al. 2026 (bioRxiv 10.64898/2026.01.20.700462v2)",
      locus: "HBB 95kb sub-TAD (chr11:5,200,000-5,295,000)",
      resolution_bp: LOCUS.resolution,
      n_bins: N_BINS,
      n_simulations: N_SIMULATIONS,
      max_steps: MAX_STEPS,
      mode_A: {
        description: "Genome-wide stochastic loading (ARCHCODE default)",
        num_cohesins: NUM_COHESINS,
        loading: "uniform random in [10%, 90%] of genome",
        hi_c_correlation: rA_HiC,
        total_loops: modeALoops,
        loops_per_run: modeALoops / N_SIMULATIONS,
        mean_loop_length_kb: modeAMeanLoopLen / 1000,
        stats: modeAStats,
      },
      mode_B: {
        description: "Focal loading at LCR enhancer positions",
        loading: "FountainLoader with beta=5.0, concentrated at 5 enhancers",
        hi_c_correlation: rB_HiC,
        total_loops: modeBLoops,
        loops_per_run: modeBLoops / N_SIMULATIONS,
        mean_loop_length_kb: modeBMeanLoopLen / 1000,
        stats: modeBStats,
      },
      inter_model_correlation: rAB,
      delta_r: rA_HiC - rB_HiC,
      conclusion:
        rA_HiC > rB_HiC
          ? "Genome-wide loading produces better Hi-C correlation, consistent with Anderson et al. 2026 finding that focal enhancer loading is incompatible with long-range transcriptional control."
          : "Focal loading shows unexpected advantage — requires investigation.",
      anderson_2026_key_finding:
        "Strong focal cohesin loading at enhancers inhibits transcription from target distal promoters. ~75% of cohesin is engaged in active extrusion between CTCF barriers.",
    };

    const outPath = path.join(
      __dirname,
      "..",
      "analysis",
      "exp009_loading_mode_ablation.json",
    );
    fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
    console.log(`\n💾 Results saved: ${outPath}`);
  } else {
    // No Hi-C — save what we have
    const results = {
      experiment: "EXP-009",
      title: "Cohesin Loading Mode Ablation",
      reference: "Anderson et al. 2026 (bioRxiv 10.64898/2026.01.20.700462v2)",
      locus: "HBB 95kb sub-TAD",
      note: "Hi-C reference not available — inter-model comparison only",
      inter_model_correlation: rAB,
      mode_A_stats: modeAStats,
      mode_B_stats: modeBStats,
    };

    const outPath = path.join(
      __dirname,
      "..",
      "analysis",
      "exp009_loading_mode_ablation.json",
    );
    fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
    console.log(`\n💾 Results saved: ${outPath}`);
  }

  console.log("\n═══════════════════════════════════════════════════════════");
  console.log("  EXP-009 complete");
  console.log("═══════════════════════════════════════════════════════════");
}

main().catch(console.error);
