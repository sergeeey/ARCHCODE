/**
 * ARCHCODE Drug Targeting Parameter Sweep
 * ========================================
 * Models pharmacological modulation of cohesin dynamics:
 * - WAPL depletion → increased residence time → vermicelli phenotype
 * - Cohesin inhibitors → decreased residence time → loop loss
 * - BET inhibitor → reduced enhancer occupancy → altered contacts
 *
 * Sweeps: residence time (5-60 min) × CTCF blocking (0.5-1.0)
 * Output: how HBB structural signal changes under perturbation
 *
 * Usage: npx tsx scripts/parameter-sweep.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus config ─────────────────────────────────────────────────

const SIM_START = 5210000;
const SIM_END = 5240000; // 30kb focused window (same as atlas generator)
const RESOLUTION = 600;
const N_BINS = Math.ceil((SIM_END - SIM_START) / RESOLUTION);

const LOCUS_FEATURES = {
  enhancers: [
    { position: 5227000, occupancy: 0.85, name: "HBB_promoter" },
    { position: 5225500, occupancy: 0.75, name: "3prime_HS1" },
    { position: 5230000, occupancy: 0.70, name: "LCR_HS2_proximal" },
    { position: 5233000, occupancy: 0.65, name: "LCR_HS3_proximal" },
    { position: 5220000, occupancy: 0.50, name: "downstream_enhancer" },
  ],
  ctcfSites: [
    { position: 5212000, orientation: "+" },
    { position: 5218000, orientation: "-" },
    { position: 5224000, orientation: "+" },
    { position: 5228000, orientation: "-" },
    { position: 5232000, orientation: "+" },
    { position: 5236000, orientation: "-" },
  ],
};

// ── A known pathogenic variant (Q2b top candidate) ───────────────
const VARIANT_BIN = Math.floor((5226796 - SIM_START) / RESOLUTION); // VCV002024192
const VARIANT_EFFECT = 0.2; // splice_acceptor

// ── Simulation engine ────────────────────────────────────────────

function buildOccupancy(enhancerScale: number): number[] {
  const rng = new SeededRandom(42);
  const landscape: number[] = [];
  for (let i = 0; i < N_BINS; i++) {
    const genomicPos = SIM_START + i * RESOLUTION;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;
    for (const enh of LOCUS_FEATURES.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / RESOLUTION;
      if (dist < 5) {
        // enhancerScale simulates BET inhibitor effect (0=full inhibition, 1=normal)
        occ += enh.occupancy * enhancerScale * Math.exp(-0.5 * dist * dist);
      }
    }
    landscape.push(Math.min(1, occ));
  }
  return landscape;
}

function simulateContactMap(
  occupancy: number[],
  kBase: number,
  alpha: number,
  gamma: number,
  ctcfBlocking: number,
  variantBin: number,
  effectStrength: number,
): number[][] {
  // Apply variant effect
  const modOccupancy = occupancy.map((occ, i) => {
    if (variantBin >= 0) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        const reduction = effectStrength + (1 - effectStrength) * (dist / 3);
        return occ * reduction;
      }
    }
    return occ;
  });

  const ctcfBins = LOCUS_FEATURES.ctcfSites
    .map(c => Math.floor((c.position - SIM_START) / RESOLUTION))
    .filter(b => b >= 0 && b < N_BINS);

  const matrix: number[][] = Array(N_BINS).fill(null).map(() => Array(N_BINS).fill(0));

  for (let i = 0; i < N_BINS; i++) {
    for (let j = i + 1; j < N_BINS; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);
      const occFactor = Math.sqrt(modOccupancy[i] * modOccupancy[j]);

      let perm = 1.0;
      for (const ctcf of ctcfBins) {
        if (ctcf > i && ctcf < j) perm *= (1 - ctcfBlocking);
      }

      const kramer = 1 - kBase * (1 - alpha * Math.pow(Math.max(0.001, occFactor), gamma));

      matrix[i][j] = distFactor * occFactor * perm * kramer;
      matrix[j][i] = matrix[i][j];
    }
  }

  // Normalize
  let maxVal = 0;
  for (let i = 0; i < N_BINS; i++)
    for (let j = 0; j < N_BINS; j++)
      if (matrix[i][j] > maxVal) maxVal = matrix[i][j];
  if (maxVal > 0)
    for (let i = 0; i < N_BINS; i++)
      for (let j = 0; j < N_BINS; j++)
        matrix[i][j] /= maxVal;

  return matrix;
}

function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat(), flatB = b.flat();
  const muA = flatA.reduce((s, v) => s + v, 0) / flatA.length;
  const muB = flatB.reduce((s, v) => s + v, 0) / flatB.length;
  let sA2 = 0, sB2 = 0, sAB = 0;
  for (let i = 0; i < flatA.length; i++) {
    sA2 += (flatA[i] - muA) ** 2;
    sB2 += (flatB[i] - muB) ** 2;
    sAB += (flatA[i] - muA) * (flatB[i] - muB);
  }
  sA2 /= flatA.length; sB2 /= flatB.length; sAB /= flatA.length;
  const c1 = 0.0001, c2 = 0.0009;
  return ((2 * muA * muB + c1) * (2 * sAB + c2)) /
    ((muA ** 2 + muB ** 2 + c1) * (sA2 + sB2 + c2));
}

// ── Main sweep ───────────────────────────────────────────────────

function main() {
  console.log("=".repeat(70));
  console.log("ARCHCODE Drug Targeting Parameter Sweep");
  console.log("=".repeat(70));

  const { DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  // Sweep 1: Residence time (kBase → unloading rate)
  // kBase=0.001 → ~16 min residence, kBase=0.005 → ~3 min, kBase=0.0003 → ~55 min
  const kBaseValues = [0.0003, 0.0005, 0.001, 0.002, 0.003, 0.005, 0.008, 0.01];
  // Approximate residence times (minutes)
  const residenceTimes = kBaseValues.map(k => Math.round(1 / (k * 60)));

  // Sweep 2: CTCF blocking efficiency
  const ctcfBlockingValues = [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, 1.00];

  // Sweep 3: Enhancer occupancy scale (BET inhibitor)
  const enhancerScales = [0.0, 0.25, 0.50, 0.75, 1.0];

  const results: Array<{
    sweep: string;
    param_name: string;
    param_value: number;
    secondary_param: string;
    secondary_value: number;
    ssim_wt: number;
    ssim_variant: number;
    delta_ssim: number;
    discriminative_power: number;
  }> = [];

  // ── Sweep 1: kBase (residence time) × default CTCF ────────
  console.log("\n--- Sweep 1: Cohesin residence time ---");
  const defaultOcc = buildOccupancy(1.0);

  for (const kBase of kBaseValues) {
    const refMap = simulateContactMap(defaultOcc, kBase, DEFAULT_ALPHA, DEFAULT_GAMMA, 0.85, -1, 1.0);
    const mutMap = simulateContactMap(defaultOcc, kBase, DEFAULT_ALPHA, DEFAULT_GAMMA, 0.85, VARIANT_BIN, VARIANT_EFFECT);
    const ssimWT = calculateSSIM(refMap, refMap); // should be 1.0
    const ssimVar = calculateSSIM(refMap, mutMap);

    const resTime = Math.round(1 / (kBase * 60));
    results.push({
      sweep: "residence_time",
      param_name: "kBase",
      param_value: kBase,
      secondary_param: "residence_min",
      secondary_value: resTime,
      ssim_wt: 1.0,
      ssim_variant: Math.round(ssimVar * 10000) / 10000,
      delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
      discriminative_power: Math.round((1 - ssimVar) * 10000) / 10000,
    });
    console.log(`  kBase=${kBase} (~${resTime} min): ΔSSIM=${(1 - ssimVar).toFixed(4)}`);
  }

  // ── Sweep 2: CTCF blocking efficiency ─────────────────────
  console.log("\n--- Sweep 2: CTCF blocking efficiency ---");
  const defaultKBase = KRAMER_KINETICS.K_BASE;

  for (const blocking of ctcfBlockingValues) {
    const refMap = simulateContactMap(defaultOcc, defaultKBase, DEFAULT_ALPHA, DEFAULT_GAMMA, blocking, -1, 1.0);
    const mutMap = simulateContactMap(defaultOcc, defaultKBase, DEFAULT_ALPHA, DEFAULT_GAMMA, blocking, VARIANT_BIN, VARIANT_EFFECT);
    const ssimVar = calculateSSIM(refMap, mutMap);

    results.push({
      sweep: "ctcf_blocking",
      param_name: "ctcf_blocking",
      param_value: blocking,
      secondary_param: "permeability",
      secondary_value: Math.round((1 - blocking) * 100) / 100,
      ssim_wt: 1.0,
      ssim_variant: Math.round(ssimVar * 10000) / 10000,
      delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
      discriminative_power: Math.round((1 - ssimVar) * 10000) / 10000,
    });
    console.log(`  CTCF blocking=${blocking} (perm=${(1 - blocking).toFixed(2)}): ΔSSIM=${(1 - ssimVar).toFixed(4)}`);
  }

  // ── Sweep 3: Enhancer occupancy (BET inhibitor) ───────────
  console.log("\n--- Sweep 3: Enhancer occupancy (BET inhibitor model) ---");

  for (const scale of enhancerScales) {
    const occ = buildOccupancy(scale);
    const refMap = simulateContactMap(occ, defaultKBase, DEFAULT_ALPHA, DEFAULT_GAMMA, 0.85, -1, 1.0);
    const mutMap = simulateContactMap(occ, defaultKBase, DEFAULT_ALPHA, DEFAULT_GAMMA, 0.85, VARIANT_BIN, VARIANT_EFFECT);
    const ssimVar = calculateSSIM(refMap, mutMap);

    results.push({
      sweep: "enhancer_occupancy",
      param_name: "enhancer_scale",
      param_value: scale,
      secondary_param: "bet_inhibition_pct",
      secondary_value: Math.round((1 - scale) * 100),
      ssim_wt: 1.0,
      ssim_variant: Math.round(ssimVar * 10000) / 10000,
      delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
      discriminative_power: Math.round((1 - ssimVar) * 10000) / 10000,
    });
    console.log(`  Enhancer scale=${scale} (${Math.round((1 - scale) * 100)}% BET inhib): ΔSSIM=${(1 - ssimVar).toFixed(4)}`);
  }

  // ── 2D Grid: kBase × ctcf_blocking ────────────────────────
  console.log("\n--- 2D Grid: residence time × CTCF blocking ---");
  const grid2d: Array<{
    kBase: number;
    ctcf_blocking: number;
    residence_min: number;
    delta_ssim: number;
  }> = [];

  for (const kBase of kBaseValues) {
    for (const blocking of ctcfBlockingValues) {
      const refMap = simulateContactMap(defaultOcc, kBase, DEFAULT_ALPHA, DEFAULT_GAMMA, blocking, -1, 1.0);
      const mutMap = simulateContactMap(defaultOcc, kBase, DEFAULT_ALPHA, DEFAULT_GAMMA, blocking, VARIANT_BIN, VARIANT_EFFECT);
      const ssimVar = calculateSSIM(refMap, mutMap);
      grid2d.push({
        kBase,
        ctcf_blocking: blocking,
        residence_min: Math.round(1 / (kBase * 60)),
        delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
      });
    }
  }

  // ── Save outputs ──────────────────────────────────────────
  const sweepPath = path.join(process.cwd(), "analysis", "parameter_sweep.csv");
  const sweepHeader = "Sweep,Param_Name,Param_Value,Secondary_Param,Secondary_Value,SSIM_WT,SSIM_Variant,Delta_SSIM,Discriminative_Power";
  const sweepRows = results.map(r =>
    `${r.sweep},${r.param_name},${r.param_value},${r.secondary_param},${r.secondary_value},${r.ssim_wt},${r.ssim_variant},${r.delta_ssim},${r.discriminative_power}`
  );
  fs.writeFileSync(sweepPath, [sweepHeader, ...sweepRows].join("\n"));
  console.log(`\nSaved: ${sweepPath} (${results.length} rows)`);

  const gridPath = path.join(process.cwd(), "analysis", "parameter_grid_2d.csv");
  const gridHeader = "kBase,CTCF_Blocking,Residence_Min,Delta_SSIM";
  const gridRows = grid2d.map(r => `${r.kBase},${r.ctcf_blocking},${r.residence_min},${r.delta_ssim}`);
  fs.writeFileSync(gridPath, [gridHeader, ...gridRows].join("\n"));
  console.log(`Saved: ${gridPath} (${grid2d.length} rows)`);

  // ── Key findings ──────────────────────────────────────────
  console.log("\n=== Key Findings ===");

  // Find optimal sensitivity window
  const residenceSweep = results.filter(r => r.sweep === "residence_time");
  const maxDelta = Math.max(...residenceSweep.map(r => r.delta_ssim));
  const optimalResidence = residenceSweep.find(r => r.delta_ssim === maxDelta);
  console.log(`  Optimal residence time: ~${optimalResidence?.secondary_value} min (kBase=${optimalResidence?.param_value}), ΔSSIM=${maxDelta}`);

  // CTCF blocking threshold
  const ctcfSweep = results.filter(r => r.sweep === "ctcf_blocking");
  const maxCtcfDelta = Math.max(...ctcfSweep.map(r => r.delta_ssim));
  const optCtcf = ctcfSweep.find(r => r.delta_ssim === maxCtcfDelta);
  console.log(`  Optimal CTCF blocking: ${optCtcf?.param_value} (ΔSSIM=${maxCtcfDelta})`);

  // BET inhibitor effect
  const betSweep = results.filter(r => r.sweep === "enhancer_occupancy");
  const betBaseline = betSweep.find(r => r.param_value === 1.0)?.delta_ssim || 0;
  const betFull = betSweep.find(r => r.param_value === 0.0)?.delta_ssim || 0;
  console.log(`  BET inhibitor: ΔSSIM ${betBaseline} → ${betFull} (${betFull > betBaseline ? "increases" : "decreases"} discrimination at full inhibition)`);
}

main();
