/**
 * ARCHCODE Structural Fragility Atlas — HBB 95kb
 * ================================================
 * Saturation in-silico mutagenesis: for every position in the HBB locus,
 * compute SSIM under 4 effect strengths (severe → minimal).
 * Identifies "structural fragile zones" where single variants cause
 * catastrophic contact map disruption.
 *
 * Usage: npx tsx scripts/fragility-atlas.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus config (same as generate-real-atlas.ts) ────────────────

const SIM_START = 5210000;
const SIM_END = 5305000; // 95kb window (full sub-TAD)
const RESOLUTION = 600;
const N_BINS = Math.ceil((SIM_END - SIM_START) / RESOLUTION);

// Biologically accurate features (GRCh38, HBB locus)
const LOCUS_FEATURES = {
  enhancers: [
    { position: 5227000, occupancy: 0.85, name: "HBB_promoter" },
    { position: 5225500, occupancy: 0.75, name: "3prime_HS1" },
    { position: 5230000, occupancy: 0.70, name: "LCR_HS2_proximal" },
    { position: 5233000, occupancy: 0.65, name: "LCR_HS3_proximal" },
    { position: 5220000, occupancy: 0.50, name: "downstream_enhancer" },
    // Extended features for 95kb window (from config/locus/hbb_95kb_subTAD.json)
    { position: 5246696, occupancy: 0.60, name: "HS2_core" },
    { position: 5248029, occupancy: 0.55, name: "HS3_region" },
    { position: 5255870, occupancy: 0.50, name: "HS4_region" },
  ],
  ctcfSites: [
    { position: 5212000, orientation: "+" },
    { position: 5218000, orientation: "-" },
    { position: 5224000, orientation: "+" },
    { position: 5228000, orientation: "-" },
    { position: 5232000, orientation: "+" },
    { position: 5236000, orientation: "-" },
    { position: 5248029, orientation: "+" },
    { position: 5257994, orientation: "-" },
    { position: 5291200, orientation: "+" },
    { position: 5302700, orientation: "-" },
  ],
};

// Effect strengths to scan (from severe to minimal)
const EFFECT_LEVELS: Record<string, number> = {
  severe: 0.1,     // nonsense/frameshift equivalent
  strong: 0.3,     // splice/promoter equivalent
  moderate: 0.5,   // missense equivalent
  weak: 0.8,       // intronic equivalent
};

// ── Simulation engine (reused from generate-real-atlas.ts) ───────

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

  const refMatrix: number[][] = Array(N_BINS).fill(null).map(() => Array(N_BINS).fill(0));
  const mutMatrix: number[][] = Array(N_BINS).fill(null).map(() => Array(N_BINS).fill(0));

  for (let i = 0; i < N_BINS; i++) {
    for (let j = i + 1; j < N_BINS; j++) {
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

      refMatrix[i][j] = distFactor * refOccFactor * refPerm * refKramer;
      refMatrix[j][i] = refMatrix[i][j];
      mutMatrix[i][j] = distFactor * mutOccFactor * mutPerm * mutKramer;
      mutMatrix[j][i] = mutMatrix[i][j];
    }
  }

  // Joint normalization
  let maxVal = 0;
  for (let i = 0; i < N_BINS; i++) {
    for (let j = 0; j < N_BINS; j++) {
      if (refMatrix[i][j] > maxVal) maxVal = refMatrix[i][j];
      if (mutMatrix[i][j] > maxVal) maxVal = mutMatrix[i][j];
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < N_BINS; i++) {
      for (let j = 0; j < N_BINS; j++) {
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
  console.log("ARCHCODE Structural Fragility Atlas — HBB 95kb");
  console.log("=".repeat(70));
  console.log(`Window: ${SIM_START}-${SIM_END} (${(SIM_END - SIM_START) / 1000}kb)`);
  console.log(`Resolution: ${RESOLUTION}bp → ${N_BINS} bins`);
  console.log(`Effect levels: ${Object.keys(EFFECT_LEVELS).join(", ")}`);
  console.log();

  const baseLandscape = buildOccupancyLandscape(42);

  // Scan every RESOLUTION-sized bin
  const STEP = RESOLUTION; // one per bin
  const positions: number[] = [];
  for (let pos = SIM_START; pos < SIM_END; pos += STEP) {
    positions.push(pos);
  }
  console.log(`Scanning ${positions.length} positions × ${Object.keys(EFFECT_LEVELS).length} effects = ${positions.length * Object.keys(EFFECT_LEVELS).length} simulations`);

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
  }> = [];

  const enhancerPositions = LOCUS_FEATURES.enhancers.map(e => e.position);
  const ctcfPositions = LOCUS_FEATURES.ctcfSites.map(c => c.position);

  let count = 0;
  for (const pos of positions) {
    const bin = Math.floor((pos - SIM_START) / RESOLUTION);

    for (const [levelName, strength] of Object.entries(EFFECT_LEVELS)) {
      // Only severe/strong disrupt CTCF
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
        near_enhancer: enhDist <= 2000,
        near_ctcf: ctcfDist <= 1000,
        enhancer_dist: enhDist,
        ctcf_dist: ctcfDist,
      });

      count++;
    }

    if (count % 200 === 0) {
      process.stdout.write(`\r  Progress: ${count}/${positions.length * 4} (${Math.round(100 * count / (positions.length * 4))}%)`);
    }
  }
  console.log(`\r  Progress: ${count}/${count} (100%)              `);

  // ── Save CSV ────────────────────────────────────────────────
  const outPath = path.join(process.cwd(), "analysis", "fragility_atlas_hbb.csv");
  const header = "Position,Bin,Effect_Level,Effect_Strength,SSIM,Delta_SSIM,Near_Enhancer,Near_CTCF,Enhancer_Dist,CTCF_Dist";
  const rows = results.map(r =>
    `${r.position},${r.bin},${r.effect_level},${r.effect_strength},${r.ssim},${r.delta_ssim},${r.near_enhancer},${r.near_ctcf},${r.enhancer_dist},${r.ctcf_dist}`
  );
  fs.writeFileSync(outPath, [header, ...rows].join("\n"));
  console.log(`\nSaved: ${outPath} (${results.length} rows)`);

  // ── Summary statistics ──────────────────────────────────────
  console.log("\n=== Fragility Summary ===");
  for (const [level, strength] of Object.entries(EFFECT_LEVELS)) {
    const levelResults = results.filter(r => r.effect_level === level);
    const ssimValues = levelResults.map(r => r.ssim);
    const mean = ssimValues.reduce((a, b) => a + b, 0) / ssimValues.length;
    const min = Math.min(...ssimValues);
    const fragile = levelResults.filter(r => r.ssim < 0.90).length;
    const fragileEnhancer = levelResults.filter(r => r.ssim < 0.90 && r.near_enhancer).length;

    console.log(`  ${level} (effect=${strength}): mean_SSIM=${mean.toFixed(4)}, min=${min.toFixed(4)}, fragile_bins=${fragile}/${levelResults.length} (${fragileEnhancer} near enhancers)`);
  }

  // ── Top 10 most fragile positions (at severe effect) ────────
  const severeResults = results
    .filter(r => r.effect_level === "severe")
    .sort((a, b) => a.ssim - b.ssim);

  console.log("\n=== Top 10 Most Fragile Positions (severe effect) ===");
  for (const r of severeResults.slice(0, 10)) {
    console.log(`  pos=${r.position} (chr11:${r.position.toLocaleString()}) SSIM=${r.ssim} Δ=${r.delta_ssim} enh_dist=${r.enhancer_dist}bp ctcf_dist=${r.ctcf_dist}bp`);
  }

  // ── Fragile zone detection ──────────────────────────────────
  // Contiguous bins with SSIM < threshold = "fragile zone"
  const FRAGILE_THRESHOLD = 0.90;
  const fragileZones: Array<{ start: number; end: number; min_ssim: number; bins: number }> = [];
  let zoneStart = -1;
  let zoneMin = 1.0;

  for (const r of severeResults.sort((a, b) => a.position - b.position)) {
    if (r.ssim < FRAGILE_THRESHOLD) {
      if (zoneStart < 0) zoneStart = r.position;
      zoneMin = Math.min(zoneMin, r.ssim);
    } else {
      if (zoneStart >= 0) {
        fragileZones.push({
          start: zoneStart,
          end: r.position,
          min_ssim: Math.round(zoneMin * 10000) / 10000,
          bins: Math.round((r.position - zoneStart) / RESOLUTION),
        });
        zoneStart = -1;
        zoneMin = 1.0;
      }
    }
  }
  // Close last zone if open
  if (zoneStart >= 0) {
    const lastPos = severeResults[severeResults.length - 1].position;
    fragileZones.push({
      start: zoneStart,
      end: lastPos,
      min_ssim: Math.round(zoneMin * 10000) / 10000,
      bins: Math.round((lastPos - zoneStart) / RESOLUTION),
    });
  }

  console.log(`\n=== Structural Fragile Zones (SSIM < ${FRAGILE_THRESHOLD} at severe effect) ===`);
  for (const z of fragileZones) {
    console.log(`  chr11:${z.start.toLocaleString()}-${z.end.toLocaleString()} (${z.bins} bins, ${z.bins * RESOLUTION / 1000}kb) min_SSIM=${z.min_ssim}`);
  }

  // Save fragile zones JSON
  const zonesPath = path.join(process.cwd(), "analysis", "fragility_zones_hbb.json");
  fs.writeFileSync(zonesPath, JSON.stringify({
    locus: "HBB",
    window: `${SIM_START}-${SIM_END}`,
    resolution: RESOLUTION,
    n_bins: N_BINS,
    fragile_threshold: FRAGILE_THRESHOLD,
    n_positions_scanned: positions.length,
    effect_levels: EFFECT_LEVELS,
    zones: fragileZones,
    top10_fragile: severeResults.slice(0, 10).map(r => ({
      position: r.position,
      ssim: r.ssim,
      enhancer_dist: r.enhancer_dist,
      ctcf_dist: r.ctcf_dist,
    })),
  }, null, 2));
  console.log(`\nSaved: ${zonesPath}`);
}

main();
