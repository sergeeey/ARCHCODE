/**
 * H2: Phase Boundary Parameter Sweep
 * ===================================
 * Tests hypothesis: Pearl hotspots cluster in phase-transition regime
 * where Φ = τ_cohesin × E_promoter / P_barrier ≈ 1 (critical sensitivity)
 *
 * Sweeps 3D parameter space:
 * - τ (tau): cohesin residence time [0.5×, 1.0×, 2.0× baseline]
 * - E: enhancer strength [0.5×, 1.0×, 2.0× baseline]
 * - P: CTCF barrier strength [0.5×, 1.0×, 1.5× baseline]
 *
 * Output: 27 simulations → results/phase_boundary/grid_search.csv
 * Time estimate: 6-8 hours (with checkpointing)
 *
 * Usage: npx tsx scripts/phase_boundary_parameter_sweep.ts --locus HBB
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── CLI arguments ────────────────────────────────────────────────
const LOCUS_ARG = process.argv.find((arg) => arg.startsWith("--locus="))?.split("=")[1] || "HBB";

// ── Locus configuration ──────────────────────────────────────────
const LOCUS_CONFIG = {
  HBB: {
    start: 5210000,
    end: 5240000, // 30kb window
    enhancers: [
      { position: 5227000, occupancy: 0.85, name: "HBB_promoter" },
      { position: 5225500, occupancy: 0.75, name: "3prime_HS1" },
      { position: 5230000, occupancy: 0.70, name: "LCR_HS2" },
      { position: 5233000, occupancy: 0.65, name: "LCR_HS3" },
    ],
    ctcfSites: [
      { position: 5212000, orientation: "+" },
      { position: 5218000, orientation: "-" },
      { position: 5224000, orientation: "+" },
      { position: 5228000, orientation: "-" },
      { position: 5232000, orientation: "+" },
      { position: 5236000, orientation: "-" },
    ],
  },
};

const config = LOCUS_CONFIG[LOCUS_ARG as keyof typeof LOCUS_CONFIG];
if (!config) {
  console.error(`Unknown locus: ${LOCUS_ARG}`);
  process.exit(1);
}

const RESOLUTION = 600; // bins
const N_BINS = Math.ceil((config.end - config.start) / RESOLUTION);

// ── Parameter grid ───────────────────────────────────────────────
const TAU_FACTORS = [0.5, 1.0, 2.0]; // cohesin residence time multipliers
const E_FACTORS = [0.5, 1.0, 2.0]; // enhancer strength multipliers
const P_FACTORS = [0.5, 1.0, 1.5]; // CTCF blocking multipliers

// ── Simulation functions ─────────────────────────────────────────

function buildOccupancyLandscape(enhancerScale: number): number[] {
  const rng = new SeededRandom(42);
  const landscape: number[] = [];

  for (let i = 0; i < N_BINS; i++) {
    const genomicPos = config.start + i * RESOLUTION;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;

    for (const enh of config.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / RESOLUTION;
      if (dist < 5) {
        occ += enh.occupancy * enhancerScale * Math.exp(-0.5 * dist * dist);
      }
    }

    landscape.push(Math.min(1, occ));
  }

  return landscape;
}

function simulateContactMatrix(
  occupancy: number[],
  kBase: number,
  ctcfBlocking: number,
): number[][] {
  const matrix: number[][] = Array.from({ length: N_BINS }, () =>
    Array(N_BINS).fill(0),
  );
  const rng = new SeededRandom(42);

  // Kramer kinetics: loop extrusion with CTCF barriers
  const alpha = KRAMER_KINETICS.ALPHA;
  const gamma = KRAMER_KINETICS.GAMMA;

  for (let i = 0; i < N_BINS; i++) {
    for (let j = i; j < N_BINS; j++) {
      const dist = j - i;

      // Base contact frequency (distance decay)
      let contactProb = kBase * Math.pow(dist + 1, -alpha);

      // Enhancer-driven contacts
      const occProduct = occupancy[i] * occupancy[j];
      contactProb *= 1 + occProduct * gamma;

      // CTCF barrier effect
      let barrierPenalty = 1.0;
      for (const ctcf of config.ctcfSites) {
        const ctcfBin = Math.floor((ctcf.position - config.start) / RESOLUTION);
        if (ctcfBin > i && ctcfBin < j) {
          barrierPenalty *= 1 - ctcfBlocking * 0.5; // blocking strength
        }
      }

      contactProb *= barrierPenalty;

      // Add noise
      contactProb *= 1 + rng.random() * 0.1 - 0.05;

      matrix[i][j] = contactProb;
      matrix[j][i] = contactProb; // symmetric
    }
  }

  return matrix;
}

function computePhiParameter(
  tauFactor: number,
  eFactor: number,
  pFactor: number,
): number {
  // Φ = τ × E / P
  // Baseline: τ=1.0, E=1.0, P=1.0 → Φ=1.0
  return (tauFactor * eFactor) / pFactor;
}

function computeLSSIM(matrix1: number[][], matrix2: number[][]): number {
  // Local Structural Similarity Index
  const windowSize = 50;
  const n = Math.min(matrix1.length, windowSize);

  let ssimSum = 0;
  let count = 0;

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const mean1 = matrix1[i][j];
      const mean2 = matrix2[i][j];
      const variance1 = Math.abs(mean1 - mean2);
      const variance2 = Math.abs(mean1 + mean2) / 2;

      if (variance2 > 0) {
        const ssim = 1 - variance1 / variance2;
        ssimSum += Math.max(0, ssim);
        count++;
      }
    }
  }

  return count > 0 ? ssimSum / count : 1.0;
}

// ── Main sweep loop ──────────────────────────────────────────────

async function runParameterSweep() {
  console.log("=".repeat(70));
  console.log(`H2 PHASE BOUNDARY PARAMETER SWEEP: ${LOCUS_ARG}`);
  console.log("=".repeat(70));
  console.log();

  const outputDir = path.join(process.cwd(), "results", "phase_boundary");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const checkpointPath = path.join(outputDir, "checkpoint.json");
  const resultsPath = path.join(outputDir, "grid_search.csv");

  // Load checkpoint if exists
  let completed: Set<string> = new Set();
  if (fs.existsSync(checkpointPath)) {
    const checkpoint = JSON.parse(fs.readFileSync(checkpointPath, "utf-8"));
    completed = new Set(checkpoint.completed);
    console.log(`✅ Resuming from checkpoint: ${completed.size} simulations already done\n`);
  }

  // Prepare CSV header
  if (!fs.existsSync(resultsPath)) {
    fs.writeFileSync(
      resultsPath,
      "tau_factor,E_factor,P_factor,Phi,k_base,enhancer_scale,ctcf_blocking,mean_LSSIM,iteration\n",
    );
  }

  let iteration = 0;
  const totalSims = TAU_FACTORS.length * E_FACTORS.length * P_FACTORS.length;

  console.log(`Grid: ${TAU_FACTORS.length} × ${E_FACTORS.length} × ${P_FACTORS.length} = ${totalSims} simulations`);
  console.log(`Resolution: ${RESOLUTION}bp, Bins: ${N_BINS}\n`);

  const startTime = Date.now();

  for (const tauFactor of TAU_FACTORS) {
    for (const eFactor of E_FACTORS) {
      for (const pFactor of P_FACTORS) {
        const simId = `${tauFactor}_${eFactor}_${pFactor}`;
        iteration++;

        if (completed.has(simId)) {
          console.log(`[${iteration}/${totalSims}] SKIP: τ=${tauFactor}, E=${eFactor}, P=${pFactor} (checkpoint)`);
          continue;
        }

        const phi = computePhiParameter(tauFactor, eFactor, pFactor);
        const kBase = KRAMER_KINETICS.K_BASE * tauFactor;
        const enhancerScale = eFactor;
        const ctcfBlocking = pFactor;

        console.log(
          `[${iteration}/${totalSims}] τ=${tauFactor}, E=${eFactor}, P=${pFactor} → Φ=${phi.toFixed(3)}`,
        );

        // Build occupancy landscape
        const occupancy = buildOccupancyLandscape(enhancerScale);

        // Simulate contact matrix
        const contactMatrix = simulateContactMatrix(occupancy, kBase, ctcfBlocking);

        // Compare with baseline (τ=1.0, E=1.0, P=1.0)
        const baselineOccupancy = buildOccupancyLandscape(1.0);
        const baselineMatrix = simulateContactMatrix(
          baselineOccupancy,
          KRAMER_KINETICS.K_BASE,
          1.0,
        );

        const lssim = computeLSSIM(contactMatrix, baselineMatrix);

        // Save result
        fs.appendFileSync(
          resultsPath,
          `${tauFactor},${eFactor},${pFactor},${phi},${kBase},${enhancerScale},${ctcfBlocking},${lssim},${iteration}\n`,
        );

        // Update checkpoint
        completed.add(simId);
        fs.writeFileSync(
          checkpointPath,
          JSON.stringify({ completed: Array.from(completed) }, null, 2),
        );

        const elapsed = (Date.now() - startTime) / 1000;
        const avgTime = elapsed / iteration;
        const remaining = (totalSims - iteration) * avgTime;
        console.log(
          `  LSSIM=${lssim.toFixed(4)} | Elapsed: ${(elapsed / 60).toFixed(1)}m | ETA: ${(remaining / 60).toFixed(1)}m\n`,
        );
      }
    }
  }

  const totalTime = (Date.now() - startTime) / 1000;
  console.log("=".repeat(70));
  console.log(`✅ PARAMETER SWEEP COMPLETE`);
  console.log(`   Total time: ${(totalTime / 60).toFixed(1)} minutes`);
  console.log(`   Results: ${resultsPath}`);
  console.log("=".repeat(70));

  // Clean up checkpoint
  if (fs.existsSync(checkpointPath)) {
    fs.unlinkSync(checkpointPath);
  }
}

runParameterSweep().catch((err) => {
  console.error("ERROR:", err);
  process.exit(1);
});
