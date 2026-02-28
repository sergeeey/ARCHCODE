/**
 * Population Diversity Analysis — 20 Samples
 *
 * Simulates genetic diversity by varying:
 * - MED1 occupancy profile (enhancer activity)
 * - CTCF binding strength (barrier efficiency)
 *
 * Outputs:
 * - Risk Score for each sample (based on SSIM vs reference)
 * - Top-3 Anomalous Samples (maximum structural deviation)
 *
 * @author Sergey V. Boyko
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";
import { createCTCFSite } from "../src/domain/models/genome";
import { FountainLoader } from "../src/simulation/SpatialLoadingModule";
import {
  SABATE_NATURE_2025,
  KRAMER_KINETICS,
} from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";
import type { KramerKineticsConfig } from "../src/engines/MultiCohesinEngine";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// Configuration
// ============================================================================

const HBB_LOCUS = {
  chromosome: "chr11",
  start: 5200000,
  end: 5400000,
  length: 200000,
};

const SIMULATION_CONFIG = {
  resolution: 5000,
  numRuns: 10,
  maxSteps: 30000,
  numCohesins: 15,
};

const NUM_SAMPLES = 20;
const SAMPLES_DIR = path.join(__dirname, "..", "data", "samples");
const RESULTS_DIR = path.join(__dirname, "..", "results");

// ============================================================================
// Sample Profile Generation
// ============================================================================

interface SampleProfile {
  id: string;
  name: string;
  description: string;
  med1Occupancy: number[]; // Per-bin MED1 signal (0-1)
  ctcfStrengths: number[]; // CTCF site strengths
  phenotype: "normal" | "mild" | "severe";
}

function generatePopulationProfiles(rng: SeededRandom): SampleProfile[] {
  const profiles: SampleProfile[] = [];
  const nBins = Math.ceil(HBB_LOCUS.length / SIMULATION_CONFIG.resolution);

  // Reference profile (healthy individual)
  const referenceOccupancy = generateHealthyOccupancy(nBins);
  const referenceCTCF = [1.0, 1.0]; // Strong CTCF sites

  profiles.push({
    id: "REF",
    name: "Reference (Healthy)",
    description: "Baseline healthy individual with normal MED1 and CTCF",
    med1Occupancy: referenceOccupancy,
    ctcfStrengths: referenceCTCF,
    phenotype: "normal",
  });

  // Generate 19 variant profiles with different perturbations
  const variants = [
    // Normal variants (5)
    {
      type: "normal",
      med1Factor: [0.9, 1.1],
      ctcfFactor: [0.95, 1.0],
      count: 5,
    },
    // Mild variants (8) - reduced MED1 or CTCF
    { type: "mild", med1Factor: [0.6, 0.85], ctcfFactor: [0.7, 0.9], count: 8 },
    // Severe variants (6) - significantly altered
    {
      type: "severe",
      med1Factor: [0.2, 0.5],
      ctcfFactor: [0.3, 0.6],
      count: 6,
    },
  ];

  let sampleIdx = 1;
  for (const variant of variants) {
    for (let i = 0; i < variant.count; i++) {
      const med1Factor = rng.randomFloat(
        variant.med1Factor[0],
        variant.med1Factor[1],
      );
      const ctcfFactor = rng.randomFloat(
        variant.ctcfFactor[0],
        variant.ctcfFactor[1],
      );

      // Perturb occupancy profile
      const occupancy = referenceOccupancy.map((v) => {
        const noise = rng.gaussian(0, 0.1);
        return Math.max(0, Math.min(1, v * med1Factor + noise));
      });

      // Perturb CTCF strengths
      const ctcf = referenceCTCF.map((s) => {
        const noise = rng.gaussian(0, 0.05);
        return Math.max(0.1, Math.min(1, s * ctcfFactor + noise));
      });

      const phenotype = variant.type as "normal" | "mild" | "severe";
      const phenotypeLabel =
        phenotype === "normal"
          ? "Normal"
          : phenotype === "mild"
            ? "Mild variant"
            : "Severe variant";

      profiles.push({
        id: `S${String(sampleIdx).padStart(2, "0")}`,
        name: `Sample ${sampleIdx} (${phenotypeLabel})`,
        description: `MED1×${med1Factor.toFixed(2)}, CTCF×${ctcfFactor.toFixed(2)}`,
        med1Occupancy: occupancy,
        ctcfStrengths: ctcf,
        phenotype,
      });

      sampleIdx++;
    }
  }

  return profiles;
}

function generateHealthyOccupancy(nBins: number): number[] {
  const occupancy: number[] = [];
  for (let i = 0; i < nBins; i++) {
    // Higher occupancy in center (enhancer region)
    const distFromCenter = Math.abs(i - nBins / 2) / (nBins / 2);
    const base = 0.3 + 0.6 * (1 - distFromCenter);
    occupancy.push(base);
  }
  return occupancy;
}

// ============================================================================
// SSIM Calculation
// ============================================================================

function calculateSSIM(img1: number[][], img2: number[][]): number {
  const n = Math.min(img1.length, img2.length);
  if (n === 0) return 0;

  // Flatten to 1D
  const flat1: number[] = [];
  const flat2: number[] = [];

  for (let i = 0; i < n; i++) {
    for (
      let j = 0;
      j < Math.min(img1[i]?.length ?? 0, img2[i]?.length ?? 0);
      j++
    ) {
      flat1.push(img1[i][j] ?? 0);
      flat2.push(img2[i][j] ?? 0);
    }
  }

  const len = flat1.length;
  if (len === 0) return 0;

  // Calculate means
  const mean1 = flat1.reduce((a, b) => a + b, 0) / len;
  const mean2 = flat2.reduce((a, b) => a + b, 0) / len;

  // Calculate variances and covariance
  let var1 = 0,
    var2 = 0,
    cov = 0;
  for (let i = 0; i < len; i++) {
    const d1 = flat1[i] - mean1;
    const d2 = flat2[i] - mean2;
    var1 += d1 * d1;
    var2 += d2 * d2;
    cov += d1 * d2;
  }
  var1 /= len;
  var2 /= len;
  cov /= len;

  // SSIM formula
  const c1 = 0.01 * 0.01; // (k1 * L)^2 where L=1, k1=0.01
  const c2 = 0.03 * 0.03; // (k2 * L)^2 where L=1, k2=0.03

  const ssim =
    ((2 * mean1 * mean2 + c1) * (2 * cov + c2)) /
    ((mean1 * mean1 + mean2 * mean2 + c1) * (var1 + var2 + c2));

  return ssim;
}

// ============================================================================
// Simulation
// ============================================================================

interface SampleResult {
  id: string;
  name: string;
  phenotype: string;
  contactMatrix: number[][];
  ssim: number;
  riskScore: number;
  loopsFormed: number;
  meanInsulation: number;
}

function runSimulation(profile: SampleProfile): number[][] {
  const nBins = Math.ceil(HBB_LOCUS.length / SIMULATION_CONFIG.resolution);

  // Vary beta based on phenotype for more diversity
  const betaMultiplier =
    profile.phenotype === "severe"
      ? 0.3
      : profile.phenotype === "mild"
        ? 0.7
        : 1.0;

  // Create FountainLoader with sample's MED1 profile
  const fountain = new FountainLoader({
    signalBins: profile.med1Occupancy,
    genomeStart: 0,
    genomeEnd: HBB_LOCUS.length,
    baselineRate: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
    beta: 5 * betaMultiplier,
  });

  // Create occupancy map for Kramer kinetics - directly from profile
  const occupancyMap = new Map<number, number>();
  for (let bin = 0; bin < nBins; bin++) {
    occupancyMap.set(bin, profile.med1Occupancy[bin] ?? 0.5);
  }

  // Vary Kramer alpha based on MED1 levels
  const meanOccupancy =
    profile.med1Occupancy.reduce((a, b) => a + b, 0) /
    profile.med1Occupancy.length;
  const adjustedAlpha = KRAMER_KINETICS.DEFAULT_ALPHA * meanOccupancy;

  const kramerConfig: KramerKineticsConfig = {
    enabled: true,
    kBase: KRAMER_KINETICS.K_BASE,
    alpha: adjustedAlpha,
    gamma: KRAMER_KINETICS.DEFAULT_GAMMA,
    occupancyMap,
    occupancyResolution: SIMULATION_CONFIG.resolution,
  };

  // Create CTCF sites with sample's strengths
  const ctcfSites = [
    createCTCFSite(HBB_LOCUS.chromosome, 7500, "R", profile.ctcfStrengths[0]),
    createCTCFSite(HBB_LOCUS.chromosome, 182500, "F", profile.ctcfStrengths[1]),
  ];

  // Run simulations
  const contactMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));
  let totalLoops = 0;

  for (let run = 0; run < SIMULATION_CONFIG.numRuns; run++) {
    const engine = new MultiCohesinEngine({
      genomeLength: HBB_LOCUS.length,
      ctcfSites,
      velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
      spatialLoader: fountain,
      numCohesins: SIMULATION_CONFIG.numCohesins,
      seed: run * 1000 + parseInt(profile.id.replace(/\D/g, "") || "0"),
      maxSteps: SIMULATION_CONFIG.maxSteps,
      kramerKinetics: kramerConfig,
    });

    for (let step = 0; step < SIMULATION_CONFIG.maxSteps; step++) {
      engine.step();
      // Use raw occupancy tracking instead of contact matrix
      engine.updateOccupancyMatrix(contactMatrix, SIMULATION_CONFIG.resolution);
    }
    totalLoops += engine.getLoops().length;
  }

  // Normalize raw matrix (preserve sample-specific differences)
  const maxVal = Math.max(...contactMatrix.flat().filter((v) => v > 0), 1);
  for (let i = 0; i < nBins; i++) {
    for (let j = 0; j < nBins; j++) {
      contactMatrix[i][j] /= maxVal;
    }
  }

  return contactMatrix;
}

function calculateInsulation(
  matrix: number[][],
  halfWindow: number = 2,
): number {
  const n = matrix.length;
  let totalInsulation = 0;

  for (let i = 0; i < n; i++) {
    let sum = 0,
      count = 0;
    for (let d = -halfWindow; d <= halfWindow; d++) {
      const j = i + d;
      if (j >= 0 && j < n) {
        sum += matrix[i][j] ?? 0;
        count++;
      }
    }
    totalInsulation += count > 0 ? sum / count : 0;
  }

  return totalInsulation / n;
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  console.log("");
  console.log("█".repeat(70));
  console.log("  ARCHCODE — Population Diversity Analysis");
  console.log("  20 Samples × HBB Locus");
  console.log("█".repeat(70));
  console.log("");
  console.log(
    `Kramer kinetics: α=${KRAMER_KINETICS.DEFAULT_ALPHA}, γ=${KRAMER_KINETICS.DEFAULT_GAMMA}`,
  );
  console.log(`Runs per sample: ${SIMULATION_CONFIG.numRuns}`);
  console.log(`Steps per run: ${SIMULATION_CONFIG.maxSteps}`);
  console.log("");

  // Ensure directories exist
  if (!fs.existsSync(SAMPLES_DIR))
    fs.mkdirSync(SAMPLES_DIR, { recursive: true });
  if (!fs.existsSync(RESULTS_DIR))
    fs.mkdirSync(RESULTS_DIR, { recursive: true });

  // Generate population profiles
  console.log("═".repeat(70));
  console.log("STEP 1: Generating Population Profiles");
  console.log("═".repeat(70));

  const rng = new SeededRandom(42);
  const profiles = generatePopulationProfiles(rng);

  console.log(`  Generated ${profiles.length} profiles:`);
  console.log(
    `    - Normal: ${profiles.filter((p) => p.phenotype === "normal").length}`,
  );
  console.log(
    `    - Mild variants: ${profiles.filter((p) => p.phenotype === "mild").length}`,
  );
  console.log(
    `    - Severe variants: ${profiles.filter((p) => p.phenotype === "severe").length}`,
  );

  // Save profiles
  for (const profile of profiles) {
    const profilePath = path.join(SAMPLES_DIR, `${profile.id}.json`);
    fs.writeFileSync(profilePath, JSON.stringify(profile, null, 2));
  }
  console.log(`  Profiles saved to: ${SAMPLES_DIR}`);
  console.log("");

  // Run simulations
  console.log("═".repeat(70));
  console.log("STEP 2: Running ARCHCODE Simulations");
  console.log("═".repeat(70));

  const results: SampleResult[] = [];
  let referenceMatrix: number[][] | null = null;

  for (let i = 0; i < profiles.length; i++) {
    const profile = profiles[i];
    process.stdout.write(
      `\r  [${i + 1}/${profiles.length}] ${profile.id}: ${profile.name.padEnd(30)}`,
    );

    const matrix = runSimulation(profile);

    if (profile.id === "REF") {
      referenceMatrix = matrix;
    }

    const loopsFormed = SIMULATION_CONFIG.numRuns; // Approximate
    const meanInsulation = calculateInsulation(matrix);

    results.push({
      id: profile.id,
      name: profile.name,
      phenotype: profile.phenotype,
      contactMatrix: matrix,
      ssim: 0, // Will calculate after reference is known
      riskScore: 0,
      loopsFormed,
      meanInsulation,
    });
  }
  console.log("\n");

  // Calculate SSIM and Risk Scores
  console.log("═".repeat(70));
  console.log("STEP 3: Calculating Risk Scores");
  console.log("═".repeat(70));

  if (!referenceMatrix) {
    console.error("ERROR: Reference matrix not found");
    process.exit(1);
  }

  for (const result of results) {
    result.ssim = calculateSSIM(result.contactMatrix, referenceMatrix);
    // Risk Score: 0 = identical to reference, 100 = completely different
    result.riskScore = Math.round((1 - result.ssim) * 100);
  }

  // Sort by risk score (descending) for anomaly detection
  const sortedByRisk = [...results].sort((a, b) => b.riskScore - a.riskScore);

  // Print results table
  console.log("");
  console.log(
    "┌──────┬────────────────────────────────┬──────────┬────────┬────────────┐",
  );
  console.log(
    "│  ID  │             Name               │ Phenotype│  SSIM  │ Risk Score │",
  );
  console.log(
    "├──────┼────────────────────────────────┼──────────┼────────┼────────────┤",
  );

  for (const r of results) {
    const phenoColor =
      r.phenotype === "normal" ? "🟢" : r.phenotype === "mild" ? "🟡" : "🔴";
    const riskBar = "█".repeat(Math.min(10, Math.floor(r.riskScore / 10)));
    console.log(
      `│ ${r.id.padEnd(4)} │ ${r.name.padEnd(30)} │ ${phenoColor} ${r.phenotype.padEnd(6)} │ ${r.ssim.toFixed(3).padStart(6)} │ ${String(r.riskScore).padStart(3)}% ${riskBar.padEnd(5)} │`,
    );
  }
  console.log(
    "└──────┴────────────────────────────────┴──────────┴────────┴────────────┘",
  );

  // Top-3 Anomalous Samples
  console.log("");
  console.log("═".repeat(70));
  console.log("TOP-3 ANOMALOUS SAMPLES");
  console.log("═".repeat(70));

  const top3 = sortedByRisk.slice(0, 3);
  for (let i = 0; i < top3.length; i++) {
    const s = top3[i];
    console.log(`\n  ${i + 1}. ${s.id}: ${s.name}`);
    console.log(`     Phenotype: ${s.phenotype}`);
    console.log(`     SSIM: ${s.ssim.toFixed(4)}`);
    console.log(`     Risk Score: ${s.riskScore}%`);
    console.log(`     Mean Insulation: ${s.meanInsulation.toFixed(6)}`);
  }

  // Summary statistics
  console.log("");
  console.log("═".repeat(70));
  console.log("POPULATION SUMMARY");
  console.log("═".repeat(70));

  const meanRisk =
    results.reduce((sum, r) => sum + r.riskScore, 0) / results.length;
  const stdRisk = Math.sqrt(
    results.reduce((sum, r) => sum + Math.pow(r.riskScore - meanRisk, 2), 0) /
      results.length,
  );
  const highRiskCount = results.filter((r) => r.riskScore > 30).length;

  console.log(`\n  Total samples: ${results.length}`);
  console.log(`  Mean Risk Score: ${meanRisk.toFixed(1)}%`);
  console.log(`  Std Dev: ${stdRisk.toFixed(1)}%`);
  console.log(`  High-risk samples (>30%): ${highRiskCount}`);

  // Risk distribution
  const riskBuckets = [0, 0, 0, 0, 0]; // 0-20, 20-40, 40-60, 60-80, 80-100
  for (const r of results) {
    const bucket = Math.min(4, Math.floor(r.riskScore / 20));
    riskBuckets[bucket]++;
  }

  console.log("\n  Risk Distribution:");
  console.log(`    0-20%:   ${"█".repeat(riskBuckets[0])} (${riskBuckets[0]})`);
  console.log(`    20-40%:  ${"█".repeat(riskBuckets[1])} (${riskBuckets[1]})`);
  console.log(`    40-60%:  ${"█".repeat(riskBuckets[2])} (${riskBuckets[2]})`);
  console.log(`    60-80%:  ${"█".repeat(riskBuckets[3])} (${riskBuckets[3]})`);
  console.log(`    80-100%: ${"█".repeat(riskBuckets[4])} (${riskBuckets[4]})`);

  // Save full report
  const report = {
    title: "ARCHCODE Population Diversity Analysis",
    date: new Date().toISOString(),
    locus: HBB_LOCUS,
    config: SIMULATION_CONFIG,
    kramerParams: {
      alpha: KRAMER_KINETICS.DEFAULT_ALPHA,
      gamma: KRAMER_KINETICS.DEFAULT_GAMMA,
      kBase: KRAMER_KINETICS.K_BASE,
    },
    results: results.map((r) => ({
      id: r.id,
      name: r.name,
      phenotype: r.phenotype,
      ssim: r.ssim,
      riskScore: r.riskScore,
      meanInsulation: r.meanInsulation,
    })),
    top3Anomalous: top3.map((s) => ({
      id: s.id,
      name: s.name,
      phenotype: s.phenotype,
      riskScore: s.riskScore,
      ssim: s.ssim,
    })),
    summary: {
      totalSamples: results.length,
      meanRiskScore: meanRisk,
      stdRiskScore: stdRisk,
      highRiskCount,
      riskDistribution: {
        "0-20": riskBuckets[0],
        "20-40": riskBuckets[1],
        "40-60": riskBuckets[2],
        "60-80": riskBuckets[3],
        "80-100": riskBuckets[4],
      },
    },
  };

  const reportPath = path.join(
    RESULTS_DIR,
    "population_diversity_analysis.json",
  );
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n\nReport saved: ${reportPath}`);

  // Final verdict
  console.log("");
  console.log(
    "╔═══════════════════════════════════════════════════════════════════╗",
  );
  if (highRiskCount > 5) {
    console.log(
      "║  ⚠️  HIGH GENETIC VARIABILITY DETECTED                            ║",
    );
    console.log(
      `║  ${highRiskCount} samples show significant structural deviation           ║`,
    );
  } else {
    console.log(
      "║  ✅ POPULATION WITHIN NORMAL RANGE                                ║",
    );
    console.log(
      `║  Only ${highRiskCount} samples show elevated risk                          ║`,
    );
  }
  console.log(
    "╚═══════════════════════════════════════════════════════════════════╝",
  );
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
