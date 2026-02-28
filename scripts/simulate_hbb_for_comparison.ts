/**
 * Generate ARCHCODE simulation for HBB locus (exact region for Hi-C comparison)
 *
 * Region: chr11:5,200,000-5,250,000 (50 KB)
 * Resolution: 5 KB bins (10x10 matrix)
 * Output: Simulation matrix matching experimental data format
 *
 * Run: npx tsx scripts/simulate_hbb_for_comparison.ts
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createCTCFSite } from "../src/domain/models/genome";
import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// HBB Locus parameters (matching experimental data)
const LOCUS = {
  chromosome: "chr11",
  start: 5200000,
  end: 5250000,
  length: 50000, // 50 KB
  resolution: 5000, // 5 KB bins
};

// CTCF sites in HBB region (mapped to 0-50kb coordinates)
// These are representative sites - real sites would need ChIP-seq data
const CTCF_SITES = [
  { pos: 5000, orient: "R" as const, strength: 0.9 }, // Potential anchor
  { pos: 12000, orient: "F" as const, strength: 0.85 },
  { pos: 20000, orient: "R" as const, strength: 0.8 },
  { pos: 28000, orient: "F" as const, strength: 0.85 },
  { pos: 35000, orient: "R" as const, strength: 0.9 },
  { pos: 45000, orient: "F" as const, strength: 0.85 },
];

async function runSimulation() {
  console.log("═══════════════════════════════════════════");
  console.log("  ARCHCODE Simulation: HBB Locus");
  console.log("  For comparison with HUDEP2 Hi-C data");
  console.log("═══════════════════════════════════════════\n");

  console.log(`📍 Region: ${LOCUS.chromosome}:${LOCUS.start}-${LOCUS.end}`);
  console.log(`📏 Length: ${LOCUS.length / 1000} KB`);
  console.log(`📏 Resolution: ${LOCUS.resolution / 1000} KB bins`);
  console.log(
    `📊 Expected matrix: ${LOCUS.length / LOCUS.resolution}x${LOCUS.length / LOCUS.resolution}\n`,
  );

  // Create CTCF sites
  const sites = CTCF_SITES.map((s) =>
    createCTCFSite(LOCUS.chromosome, s.pos, s.orient, s.strength),
  );

  console.log(`🧬 CTCF sites: ${sites.length}`);
  console.log(`   Convergent pairs: ${countConvergentPairs(sites)}\n`);

  // Configure engine
  const config = {
    genomeLength: LOCUS.length,
    ctcfSites: sites,
    numCohesins: 20, // Ensemble simulation
    velocity: 1000, // bp per step
    processivity: 600000, // 600 KB
    unloadingProbability: 0.0005,
    seed: 42, // Reproducible
    maxSteps: 10000,
  };

  console.log("⚙️  Simulation parameters:");
  console.log(`   Cohesins: ${config.numCohesins}`);
  console.log(`   Velocity: ${config.velocity} bp/step`);
  console.log(`   Seed: ${config.seed}`);
  console.log(`   Max steps: ${config.maxSteps}\n`);

  console.log("🔄 Running simulation...");
  const startTime = Date.now();

  const engine = new MultiCohesinEngine(config);
  const loops = engine.run(config.maxSteps);

  const elapsedTime = Date.now() - startTime;
  console.log(`✅ Simulation complete (${elapsedTime}ms)\n`);

  console.log(`📊 Results:`);
  console.log(`   Loops formed: ${loops.length}`);

  // Generate contact matrix (5 KB resolution)
  const binSize = LOCUS.resolution;
  const numBins = Math.floor(LOCUS.length / binSize);
  const matrix: number[][] = Array(numBins)
    .fill(0)
    .map(() => Array(numBins).fill(0));

  // Fill matrix from loops
  for (const loop of loops) {
    const bin1 = Math.floor(loop.leftAnchor / binSize);
    const bin2 = Math.floor(loop.rightAnchor / binSize);

    if (bin1 >= 0 && bin1 < numBins && bin2 >= 0 && bin2 < numBins) {
      matrix[bin1][bin2] += loop.strength;
      matrix[bin2][bin1] += loop.strength; // Symmetric
    }
  }

  // Add diagonal (self-contacts)
  for (let i = 0; i < numBins; i++) {
    matrix[i][i] += 1.0;
  }

  // Statistics
  const flatMatrix = matrix.flat();
  const nonZero = flatMatrix.filter((v) => v > 0).length;
  const min = Math.min(...flatMatrix.filter((v) => v > 0));
  const max = Math.max(...flatMatrix);
  const sum = flatMatrix.reduce((a, b) => a + b, 0);
  const mean = sum / nonZero;

  console.log(`   Matrix shape: ${numBins}x${numBins}`);
  console.log(`   Non-zero elements: ${nonZero} / ${flatMatrix.length}`);
  console.log(`   Min (non-zero): ${min.toFixed(4)}`);
  console.log(`   Max: ${max.toFixed(4)}`);
  console.log(`   Mean (non-zero): ${mean.toFixed(4)}`);
  console.log(`   Total sum: ${sum.toFixed(2)}\n`);

  // Save matrix
  const outputDir = path.join(__dirname, "..", "data");
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const matrixPath = path.join(
    outputDir,
    "archcode_hbb_simulation_matrix.json",
  );
  fs.writeFileSync(
    matrixPath,
    JSON.stringify(
      {
        locus: `${LOCUS.chromosome}:${LOCUS.start}-${LOCUS.end}`,
        resolution: LOCUS.resolution,
        matrix: matrix,
        loops: loops.length,
        metadata: {
          cohesins: config.numCohesins,
          velocity: config.velocity,
          seed: config.seed,
          ctcf_sites: sites.length,
          simulation_time_ms: elapsedTime,
        },
      },
      null,
      2,
    ),
  );

  console.log(`💾 Saved to: ${matrixPath}\n`);

  // Also save as NumPy-compatible format (flat array with shape)
  const numpyFormat = {
    shape: [numBins, numBins],
    data: flatMatrix,
  };

  const numpyPath = path.join(
    outputDir,
    "archcode_hbb_simulation_matrix_flat.json",
  );
  fs.writeFileSync(numpyPath, JSON.stringify(numpyFormat, null, 2));

  console.log(`💾 NumPy format: ${numpyPath}\n`);

  console.log("✅ Simulation ready for comparison with experimental data");
  console.log("   Next: Run correlation analysis\n");

  return matrix;
}

function countConvergentPairs(sites: any[]): number {
  let count = 0;
  for (let i = 0; i < sites.length - 1; i++) {
    for (let j = i + 1; j < sites.length; j++) {
      if (sites[i].orientation === "R" && sites[j].orientation === "F") {
        count++;
      }
    }
  }
  return count;
}

// Run simulation
runSimulation().catch(console.error);
