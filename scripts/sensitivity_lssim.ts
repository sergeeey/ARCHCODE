/**
 * Sensitivity analysis: LSSIM window size impact on verdict distribution.
 *
 * Uses the SAME simulation engine as generate-unified-atlas.ts (imports same modules).
 * Tests window sizes [20, 30, 40, 50, 60, 70, 80] on HBB 95kb locus.
 * Simulates each variant ONCE, then computes LSSIM for all windows → O(n) simulations.
 *
 * Usage: npx tsx scripts/sensitivity_lssim.ts
 */

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import { SeededRandom } from "../src/utils/random";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import {
  loadLocusConfig,
  resolveLocusPath,
  getLocusFeatures,
  type LocusConfig,
} from "../src/domain/config/locus-config";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ── SSIM functions (identical to generate-unified-atlas.ts) ──────────────

function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA: number[] = [];
  const flatB: number[] = [];
  const n = a.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      flatA.push(a[i][j]);
      flatB.push(b[i][j]);
    }
  }
  const N = flatA.length;
  if (N === 0) return 1.0;
  let muA = 0,
    muB = 0;
  for (let k = 0; k < N; k++) {
    muA += flatA[k];
    muB += flatB[k];
  }
  muA /= N;
  muB /= N;
  let sigA2 = 0,
    sigB2 = 0,
    sigAB = 0;
  for (let k = 0; k < N; k++) {
    const da = flatA[k] - muA;
    const db = flatB[k] - muB;
    sigA2 += da * da;
    sigB2 += db * db;
    sigAB += da * db;
  }
  sigA2 /= N;
  sigB2 /= N;
  sigAB /= N;
  const C1 = 0.0001,
    C2 = 0.0009;
  return (
    ((2 * muA * muB + C1) * (2 * sigAB + C2)) /
    ((muA * muA + muB * muB + C1) * (sigA2 + sigB2 + C2))
  );
}

function calculateLocalSSIM(
  ref: number[][],
  mut: number[][],
  variantBin: number,
  windowSize: number,
): number {
  const n = ref.length;
  if (n <= windowSize) return calculateSSIM(ref, mut);
  let start = variantBin - Math.floor(windowSize / 2);
  let end = start + windowSize;
  if (start < 0) {
    start = 0;
    end = windowSize;
  }
  if (end > n) {
    end = n;
    start = n - windowSize;
  }
  const refSub: number[][] = [];
  const mutSub: number[][] = [];
  for (let i = start; i < end; i++) {
    const rr: number[] = [];
    const mm: number[] = [];
    for (let j = start; j < end; j++) {
      rr.push(ref[i][j]);
      mm.push(mut[i][j]);
    }
    refSub.push(rr);
    mutSub.push(mm);
  }
  return calculateSSIM(refSub, mutSub);
}

// ── Effect strengths (identical to generate-unified-atlas.ts) ────────────

const EFFECT_STRENGTHS: Record<string, number> = {
  nonsense: 1.0,
  frameshift: 0.95,
  splice_donor: 0.85,
  splice_acceptor: 0.85,
  splice_region: 0.6,
  missense: 0.5,
  inframe_deletion: 0.45,
  inframe_indel: 0.4,
  promoter: 0.7,
  "5_prime_UTR": 0.3,
  "3_prime_UTR": 0.15,
  synonymous: 0.02,
  intronic: 0.02,
  other: 0.3,
};

function getEffectStrength(category: string): number {
  return EFFECT_STRENGTHS[category] ?? 0.3;
}

// ── Simulation (exact copy of simulatePairedMatrices from pipeline) ──────

function simulatePairedMatrices(
  nBins: number,
  simStart: number,
  resolution: number,
  features: ReturnType<typeof getLocusFeatures>,
  variantBin: number,
  effectStrength: number,
  category: string,
  seed: number,
): { reference: number[][]; mutant: number[][] } {
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  // MED1 occupancy landscape
  const baseLandscape: number[] = [];
  const landscapeRng = new SeededRandom(seed);
  for (let i = 0; i < nBins; i++) {
    const genomicPos = simStart + i * resolution;
    let occ =
      KRAMER_KINETICS.BACKGROUND_OCCUPANCY + landscapeRng.random() * 0.05;
    for (const enh of features.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / resolution;
      if (dist < 5) {
        occ += enh.occupancy * Math.exp(-0.5 * (dist * dist));
      }
    }
    baseLandscape.push(Math.min(1, occ));
  }

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

  // CTCF barriers
  const ctcfBins = features.ctcfSites
    .map((c) => Math.floor((c.position - simStart) / resolution))
    .filter((b) => b >= 0 && b < nBins);
  const refCTCF = ctcfBins;
  const mutCTCF =
    category.includes("splice") || category.includes("promoter")
      ? ctcfBins.filter((b) => variantBin < 0 || Math.abs(b - variantBin) > 2)
      : ctcfBins;

  // Analytical contact map
  const refMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));
  const mutMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);

      const refOccFactor = Math.sqrt(refOccupancy[i] * refOccupancy[j]);
      const mutOccFactor = Math.sqrt(mutOccupancy[i] * mutOccupancy[j]);

      let refPerm = 1.0;
      let mutPerm = 1.0;
      for (const ctcf of refCTCF) {
        if (ctcf > i && ctcf < j) refPerm *= 0.15;
      }
      for (const ctcf of mutCTCF) {
        if (ctcf > i && ctcf < j) mutPerm *= 0.15;
      }

      const refKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, refOccFactor), DEFAULT_GAMMA));
      const mutKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, mutOccFactor), DEFAULT_GAMMA));

      refMatrix[i][j] = distFactor * refOccFactor * refPerm * refKramer;
      refMatrix[j][i] = refMatrix[i][j];
      mutMatrix[i][j] = distFactor * mutOccFactor * mutPerm * mutKramer;
      mutMatrix[j][i] = mutMatrix[i][j];
    }
  }

  // Joint normalization
  let maxVal = 0;
  for (let i = 0; i < nBins; i++) {
    for (let j = 0; j < nBins; j++) {
      if (refMatrix[i][j] > maxVal) maxVal = refMatrix[i][j];
      if (mutMatrix[i][j] > maxVal) maxVal = mutMatrix[i][j];
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < nBins; i++) {
      for (let j = 0; j < nBins; j++) {
        refMatrix[i][j] /= maxVal;
        mutMatrix[i][j] /= maxVal;
      }
    }
  }

  return { reference: refMatrix, mutant: mutMatrix };
}

// ── Thresholds (from HBB 30kb calibration) ──────────────────────────────

const THRESHOLDS = {
  ssim_pathogenic: 0.85,
  ssim_likely_pathogenic: 0.92,
  ssim_vus: 0.96,
  ssim_likely_benign: 0.99,
};

// ── Main ─────────────────────────────────────────────────────────────────

async function main() {
  const WINDOWS = [20, 30, 40, 50, 60, 70, 80];
  const LOCUS_ARG = "95kb";

  // Load config using same infrastructure as main pipeline
  const configPath = resolveLocusPath(LOCUS_ARG);
  const locusConfig = loadLocusConfig(configPath);
  const features = getLocusFeatures(locusConfig);
  const simStart = locusConfig.window.start;
  const resolution = locusConfig.window.resolution_bp;
  const nBins = locusConfig.window.n_bins;

  // Load variants CSV
  const csvPath = path.resolve(
    __dirname,
    "../results/HBB_Unified_Atlas_95kb.csv",
  );
  if (!fs.existsSync(csvPath)) {
    console.error(`CSV not found: ${csvPath}`);
    process.exit(1);
  }
  const csvLines = fs.readFileSync(csvPath, "utf-8").trim().split("\n");
  const header = csvLines[0].split(",");
  const posIdx = header.indexOf("Position_GRCh38");
  const catIdx = header.indexOf("Category");

  interface VariantRow {
    pos: number;
    category: string;
    bin: number;
  }
  const variants: VariantRow[] = [];
  for (let i = 1; i < csvLines.length; i++) {
    const cols = csvLines[i].split(",");
    const pos = parseInt(cols[posIdx]);
    const category = cols[catIdx];
    const bin = Math.floor((pos - simStart) / resolution);
    if (bin >= 0 && bin < nBins) {
      variants.push({ pos, category, bin });
    }
  }

  console.log(`\n=== LSSIM Sensitivity Analysis ===`);
  console.log(`Locus: HBB ${LOCUS_ARG} (${nBins} bins)`);
  console.log(`Variants: ${variants.length}`);
  console.log(`Windows: ${WINDOWS.join(", ")}`);
  console.log(
    `Simulating all variants once, then computing LSSIM for each window...\n`,
  );

  // Step 1: Simulate all variants ONCE, store (ref, mut, bin) triples
  const matrices: { ref: number[][]; mut: number[][]; bin: number }[] = [];
  for (let vi = 0; vi < variants.length; vi++) {
    const v = variants[vi];
    const es = getEffectStrength(v.category);
    const { reference, mutant } = simulatePairedMatrices(
      nBins,
      simStart,
      resolution,
      features,
      v.bin,
      es,
      v.category,
      vi + 42,
    );
    matrices.push({ ref: reference, mut: mutant, bin: v.bin });
    if ((vi + 1) % 200 === 0) {
      console.log(`  Simulated ${vi + 1}/${variants.length} variants...`);
    }
  }
  console.log(`  Simulated ${variants.length}/${variants.length} variants.\n`);

  // Step 2: For each window, compute LSSIM on stored matrices
  interface WindowResult {
    window: number;
    lssim_min: number;
    lssim_max: number;
    lssim_mean: number;
    pathogenic: number;
    likely_pathogenic: number;
    vus: number;
    likely_benign: number;
    benign: number;
  }
  const results: WindowResult[] = [];

  for (const w of WINDOWS) {
    const lssimVals: number[] = [];
    let pathogenic = 0,
      likely_pathogenic = 0,
      vus = 0,
      likely_benign = 0,
      benign = 0;

    for (const m of matrices) {
      const lssim = calculateLocalSSIM(m.ref, m.mut, m.bin, w);
      lssimVals.push(lssim);

      if (lssim < THRESHOLDS.ssim_pathogenic) pathogenic++;
      else if (lssim < THRESHOLDS.ssim_likely_pathogenic) likely_pathogenic++;
      else if (lssim < THRESHOLDS.ssim_vus) vus++;
      else if (lssim < THRESHOLDS.ssim_likely_benign) likely_benign++;
      else benign++;
    }

    const lssimMin = Math.min(...lssimVals);
    const lssimMax = Math.max(...lssimVals);
    const lssimMean = lssimVals.reduce((a, b) => a + b, 0) / lssimVals.length;

    results.push({
      window: w,
      lssim_min: parseFloat(lssimMin.toFixed(4)),
      lssim_max: parseFloat(lssimMax.toFixed(4)),
      lssim_mean: parseFloat(lssimMean.toFixed(4)),
      pathogenic,
      likely_pathogenic,
      vus,
      likely_benign,
      benign,
    });

    console.log(
      `Window=${w.toString().padStart(2)}  ` +
        `LSSIM=[${lssimMin.toFixed(4)}, ${lssimMax.toFixed(4)}]  ` +
        `mean=${lssimMean.toFixed(4)}  ` +
        `PATH=${pathogenic} LP=${likely_pathogenic} VUS=${vus} LB=${likely_benign} B=${benign}`,
    );
  }

  // Save JSON
  const outPath = path.resolve(
    __dirname,
    "../results/sensitivity_lssim_window.json",
  );
  const output = {
    title: "LSSIM Window Size Sensitivity Analysis",
    locus: `HBB ${LOCUS_ARG}`,
    n_bins: nBins,
    n_variants: variants.length,
    date: new Date().toISOString(),
    thresholds: THRESHOLDS,
    results,
  };
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log(`\nSaved: ${outPath}`);

  // Summary
  console.log(`\n--- Summary ---`);
  const w50 = results.find((r) => r.window === 50)!;
  const sp50 = w50.pathogenic + w50.likely_pathogenic;
  console.log(
    `Default window (50): LSSIM range [${w50.lssim_min}, ${w50.lssim_max}], ${sp50} structurally pathogenic`,
  );

  for (const r of results) {
    if (r.window === 50) continue;
    const sp = r.pathogenic + r.likely_pathogenic;
    const delta = sp - sp50;
    console.log(
      `Window ${r.window}: Δstruct_path=${delta >= 0 ? "+" : ""}${delta}, ` +
        `LSSIM range [${r.lssim_min}, ${r.lssim_max}]`,
    );
  }
}

main().catch(console.error);
