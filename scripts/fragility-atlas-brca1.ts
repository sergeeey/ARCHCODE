/**
 * ARCHCODE Structural Fragility Atlas — BRCA1 400kb
 * ===================================================
 * Saturation in-silico mutagenesis for BRCA1 locus.
 * Replicates HBB fragility atlas methodology on a second gene
 * to test reproducibility of enhancer-proximity fragility hypothesis.
 *
 * Key difference: BRCA1 uses MCF7 enhancers (breast tissue-matched),
 * 400kb window, 1000bp resolution → 400 bins.
 * For speed, we scan every 2nd bin (200 positions × 4 effects = 800 sims).
 *
 * Usage: npx tsx scripts/fragility-atlas-brca1.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus config (from config/locus/brca1_400kb.json) ────────────

const SIM_START = 42900000;
const SIM_END = 43300000; // 400kb window
const RESOLUTION = 1000;
const N_BINS = Math.ceil((SIM_END - SIM_START) / RESOLUTION); // 400

// BRCA1 features — ENCODE MCF7 H3K27ac + K562/MCF7 CTCF
const LOCUS_FEATURES = {
  enhancers: [
    { position: 43125364, occupancy: 0.90, name: "BRCA1_TSS_NBR2" },
    { position: 43170700, occupancy: 0.85, name: "NBR1_promoter" },
    { position: 42981500, occupancy: 0.70, name: "PTGES3L_RUNDC1" },
    { position: 43007000, occupancy: 0.65, name: "IFI35_promoter" },
    { position: 42998900, occupancy: 0.60, name: "RPL27_promoter" },
    { position: 42929000, occupancy: 0.50, name: "G6PC1_downstream" },
    { position: 42964500, occupancy: 0.45, name: "AARSD1_promoter" },
    { position: 43024600, occupancy: 0.55, name: "VAT1_RND2_boundary" },
    { position: 43021500, occupancy: 0.40, name: "VAT1_promoter" },
  ],
  ctcfSites: [
    { position: 42929437, orientation: "?" },
    { position: 42937930, orientation: "?" },
    { position: 42964377, orientation: "?" },
    { position: 42980938, orientation: "?" },
    { position: 42998141, orientation: "?" },
    { position: 43004047, orientation: "?" },
    { position: 43006741, orientation: "?" },
    { position: 43024579, orientation: "?" },
    { position: 43042287, orientation: "?" },
    { position: 43085710, orientation: "?" },
    { position: 43124566, orientation: "?" },
    { position: 43171272, orientation: "?" },
    { position: 43172342, orientation: "?" },
    { position: 43214276, orientation: "?" },
  ],
};

// BRCA1 gene boundaries (minus strand)
const BRCA1_START = 43044294;
const BRCA1_END = 43125364;

// Effect strengths (same as HBB atlas)
const EFFECT_LEVELS: Record<string, number> = {
  severe: 0.1,
  strong: 0.3,
  moderate: 0.5,
  weak: 0.8,
};

// ── Simulation engine (identical physics to HBB atlas) ───────────

function buildOccupancyLandscape(seed: number): number[] {
  const rng = new SeededRandom(seed);
  const landscape: number[] = [];
  for (let i = 0; i < N_BINS; i++) {
    const genomicPos = SIM_START + i * RESOLUTION;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;
    for (const enh of LOCUS_FEATURES.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / RESOLUTION;
      if (dist < 5) {
        occ += enh.occupancy * Math.exp(-0.5 * dist * dist);
      }
    }
    landscape.push(Math.min(1, occ));
  }
  return landscape;
}

function simulatePairedMatrices(
  baseLandscape: number[],
  variantBin: number,
  effectStrength: number,
  disruptCTCF: boolean,
): { reference: number[][]; mutant: number[][] } {
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  const refOccupancy = [...baseLandscape];
  const mutOccupancy = baseLandscape.map((occ, i) => {
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
  const refCTCF = ctcfBins;
  const mutCTCF = disruptCTCF
    ? ctcfBins.filter(b => variantBin < 0 || Math.abs(b - variantBin) > 2)
    : ctcfBins;

  // LSSIM: use 50×50 local window centered on variant for large matrices
  // For fragility atlas we compute global SSIM on submatrix around variant
  const WINDOW = 50; // bins
  const wStart = Math.max(0, variantBin - WINDOW);
  const wEnd = Math.min(N_BINS, variantBin + WINDOW);
  const wSize = wEnd - wStart;

  const refMatrix: number[][] = Array(wSize).fill(null).map(() => Array(wSize).fill(0));
  const mutMatrix: number[][] = Array(wSize).fill(null).map(() => Array(wSize).fill(0));

  for (let ii = 0; ii < wSize; ii++) {
    const i = wStart + ii;
    for (let jj = ii + 1; jj < wSize; jj++) {
      const j = wStart + jj;
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);

      const refOccFactor = Math.sqrt(refOccupancy[i] * refOccupancy[j]);
      const mutOccFactor = Math.sqrt(mutOccupancy[i] * mutOccupancy[j]);

      let refPerm = 1.0, mutPerm = 1.0;
      for (const ctcf of refCTCF) {
        if (ctcf > i && ctcf < j) refPerm *= 0.15;
      }
      for (const ctcf of mutCTCF) {
        if (ctcf > i && ctcf < j) mutPerm *= 0.15;
      }

      const refKramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * Math.pow(Math.max(0.001, refOccFactor), DEFAULT_GAMMA));
      const mutKramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * Math.pow(Math.max(0.001, mutOccFactor), DEFAULT_GAMMA));

      refMatrix[ii][jj] = distFactor * refOccFactor * refPerm * refKramer;
      refMatrix[jj][ii] = refMatrix[ii][jj];
      mutMatrix[ii][jj] = distFactor * mutOccFactor * mutPerm * mutKramer;
      mutMatrix[jj][ii] = mutMatrix[ii][jj];
    }
  }

  // Joint normalization
  let maxVal = 0;
  for (let i = 0; i < wSize; i++) {
    for (let j = 0; j < wSize; j++) {
      if (refMatrix[i][j] > maxVal) maxVal = refMatrix[i][j];
      if (mutMatrix[i][j] > maxVal) maxVal = mutMatrix[i][j];
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < wSize; i++) {
      for (let j = 0; j < wSize; j++) {
        refMatrix[i][j] /= maxVal;
        mutMatrix[i][j] /= maxVal;
      }
    }
  }

  return { reference: refMatrix, mutant: mutMatrix };
}

function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat();
  const flatB = b.flat();
  const muA = flatA.reduce((s, v) => s + v, 0) / flatA.length;
  const muB = flatB.reduce((s, v) => s + v, 0) / flatB.length;

  let sigmaA2 = 0, sigmaB2 = 0, sigmaAB = 0;
  for (let i = 0; i < flatA.length; i++) {
    sigmaA2 += (flatA[i] - muA) ** 2;
    sigmaB2 += (flatB[i] - muB) ** 2;
    sigmaAB += (flatA[i] - muA) * (flatB[i] - muB);
  }
  sigmaA2 /= flatA.length;
  sigmaB2 /= flatB.length;
  sigmaAB /= flatA.length;

  const c1 = 0.0001, c2 = 0.0009;
  return ((2 * muA * muB + c1) * (2 * sigmaAB + c2)) /
    ((muA * muA + muB * muB + c1) * (sigmaA2 + sigmaB2 + c2));
}

// ── Main: saturation scan ────────────────────────────────────────

function main() {
  console.log("=".repeat(70));
  console.log("ARCHCODE Structural Fragility Atlas — BRCA1 400kb");
  console.log("=".repeat(70));
  console.log(`Window: chr17:${SIM_START}-${SIM_END} (${(SIM_END - SIM_START) / 1000}kb)`);
  console.log(`Resolution: ${RESOLUTION}bp → ${N_BINS} bins`);
  console.log(`Using LSSIM (50-bin local window) for large matrix`);
  console.log(`Effect levels: ${Object.keys(EFFECT_LEVELS).join(", ")}`);
  console.log();

  const baseLandscape = buildOccupancyLandscape(42);

  // Scan every 2nd bin for speed (400kb/1000bp = 400 bins → 200 positions)
  const STEP = 2;
  const positions: number[] = [];
  for (let bin = 0; bin < N_BINS; bin += STEP) {
    positions.push(SIM_START + bin * RESOLUTION);
  }
  console.log(`Scanning ${positions.length} positions × ${Object.keys(EFFECT_LEVELS).length} effects = ${positions.length * Object.keys(EFFECT_LEVELS).length} simulations`);

  const enhancerPositions = LOCUS_FEATURES.enhancers.map(e => e.position);
  const ctcfPositions = LOCUS_FEATURES.ctcfSites.map(c => c.position);

  const results: Array<{
    position: number;
    bin: number;
    effect_level: string;
    effect_strength: number;
    ssim: number;
    delta_ssim: number;
    near_enhancer: boolean;
    near_ctcf: boolean;
    enhancer_dist: number;
    ctcf_dist: number;
    in_brca1_gene: boolean;
  }> = [];

  let count = 0;
  const totalSims = positions.length * Object.keys(EFFECT_LEVELS).length;

  for (const pos of positions) {
    const bin = Math.floor((pos - SIM_START) / RESOLUTION);

    for (const [levelName, strength] of Object.entries(EFFECT_LEVELS)) {
      const disruptCTCF = strength <= 0.3;

      const { reference, mutant } = simulatePairedMatrices(
        baseLandscape, bin, strength, disruptCTCF
      );
      const ssim = calculateSSIM(reference, mutant);

      const enhDist = Math.min(...enhancerPositions.map(e => Math.abs(pos - e)));
      const ctcfDist = Math.min(...ctcfPositions.map(c => Math.abs(pos - c)));

      results.push({
        position: pos,
        bin,
        effect_level: levelName,
        effect_strength: strength,
        ssim: Math.round(ssim * 10000) / 10000,
        delta_ssim: Math.round((1 - ssim) * 10000) / 10000,
        near_enhancer: enhDist <= 3000, // 3kb for BRCA1 (wider spread enhancers)
        near_ctcf: ctcfDist <= 2000,
        enhancer_dist: enhDist,
        ctcf_dist: ctcfDist,
        in_brca1_gene: pos >= BRCA1_START && pos <= BRCA1_END,
      });

      count++;
    }

    if (count % 100 === 0) {
      process.stdout.write(`\r  Progress: ${count}/${totalSims} (${Math.round(100 * count / totalSims)}%)`);
    }
  }
  console.log(`\r  Progress: ${count}/${count} (100%)              `);

  // ── Save CSV ────────────────────────────────────────────────
  const outPath = path.join(process.cwd(), "analysis", "fragility_atlas_brca1.csv");
  const header = "Position,Bin,Effect_Level,Effect_Strength,SSIM,Delta_SSIM,Near_Enhancer,Near_CTCF,Enhancer_Dist,CTCF_Dist,In_BRCA1_Gene";
  const rows = results.map(r =>
    `${r.position},${r.bin},${r.effect_level},${r.effect_strength},${r.ssim},${r.delta_ssim},${r.near_enhancer},${r.near_ctcf},${r.enhancer_dist},${r.ctcf_dist},${r.in_brca1_gene}`
  );
  fs.writeFileSync(outPath, [header, ...rows].join("\n"));
  console.log(`\nSaved: ${outPath} (${results.length} rows)`);

  // ── Summary statistics ──────────────────────────────────────
  console.log("\n=== Fragility Summary (BRCA1) ===");
  for (const [level, strength] of Object.entries(EFFECT_LEVELS)) {
    const levelResults = results.filter(r => r.effect_level === level);
    const ssimValues = levelResults.map(r => r.ssim);
    const mean = ssimValues.reduce((a, b) => a + b, 0) / ssimValues.length;
    const min = Math.min(...ssimValues);
    const fragile = levelResults.filter(r => r.ssim < 0.95).length;
    const fragileEnhancer = levelResults.filter(r => r.ssim < 0.95 && r.near_enhancer).length;

    console.log(`  ${level} (effect=${strength}): mean_SSIM=${mean.toFixed(4)}, min=${min.toFixed(4)}, fragile_bins=${fragile}/${levelResults.length} (${fragileEnhancer} near enhancers)`);
  }

  // ── Top 10 most fragile (severe) ────────────────────────────
  const severeResults = results
    .filter(r => r.effect_level === "severe")
    .sort((a, b) => a.ssim - b.ssim);

  console.log("\n=== Top 10 Most Fragile Positions (severe effect) ===");
  for (const r of severeResults.slice(0, 10)) {
    const inGene = r.in_brca1_gene ? " [IN BRCA1]" : "";
    console.log(`  chr17:${r.position.toLocaleString()} SSIM=${r.ssim} Δ=${r.delta_ssim} enh_dist=${r.enhancer_dist}bp ctcf_dist=${r.ctcf_dist}bp${inGene}`);
  }

  // ── Enhancer proximity correlation ──────────────────────────
  console.log("\n=== Enhancer Proximity vs Fragility (severe) ===");
  const nearEnhSevere = severeResults.filter(r => r.near_enhancer);
  const farEnhSevere = severeResults.filter(r => !r.near_enhancer);
  const nearMean = nearEnhSevere.length > 0
    ? nearEnhSevere.reduce((s, r) => s + r.delta_ssim, 0) / nearEnhSevere.length : 0;
  const farMean = farEnhSevere.length > 0
    ? farEnhSevere.reduce((s, r) => s + r.delta_ssim, 0) / farEnhSevere.length : 0;
  console.log(`  Near enhancer (≤3kb): n=${nearEnhSevere.length}, mean ΔSSIM=${nearMean.toFixed(4)}`);
  console.log(`  Far from enhancer:    n=${farEnhSevere.length}, mean ΔSSIM=${farMean.toFixed(4)}`);
  if (farMean > 0) {
    console.log(`  Enrichment ratio: ${(nearMean / farMean).toFixed(1)}×`);
  }

  // ── Save summary JSON ───────────────────────────────────────
  const summaryPath = path.join(process.cwd(), "analysis", "fragility_atlas_brca1_summary.json");
  fs.writeFileSync(summaryPath, JSON.stringify({
    locus: "BRCA1",
    chromosome: "chr17",
    window: `${SIM_START}-${SIM_END}`,
    resolution: RESOLUTION,
    n_bins: N_BINS,
    n_positions_scanned: positions.length,
    scan_step: STEP,
    effect_levels: EFFECT_LEVELS,
    top10_fragile: severeResults.slice(0, 10).map(r => ({
      position: r.position,
      ssim: r.ssim,
      delta_ssim: r.delta_ssim,
      enhancer_dist: r.enhancer_dist,
      ctcf_dist: r.ctcf_dist,
      in_brca1_gene: r.in_brca1_gene,
    })),
    enhancer_proximity_enrichment: {
      near_enhancer_mean_delta: Math.round(nearMean * 10000) / 10000,
      far_enhancer_mean_delta: Math.round(farMean * 10000) / 10000,
      ratio: farMean > 0 ? Math.round((nearMean / farMean) * 10) / 10 : null,
    },
    summary_by_level: Object.entries(EFFECT_LEVELS).map(([level, strength]) => {
      const lr = results.filter(r => r.effect_level === level);
      const vals = lr.map(r => r.ssim);
      return {
        level,
        strength,
        mean_ssim: Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10000) / 10000,
        min_ssim: Math.round(Math.min(...vals) * 10000) / 10000,
        fragile_count: lr.filter(r => r.ssim < 0.95).length,
        fragile_near_enhancer: lr.filter(r => r.ssim < 0.95 && r.near_enhancer).length,
      };
    }),
  }, null, 2));
  console.log(`Saved: ${summaryPath}`);
}

main();
