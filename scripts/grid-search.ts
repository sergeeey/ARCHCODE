/**
 * ARCHCODE Parameter Grid Search
 * Finds optimal parameters for maximum correlation with AlphaGenome
 *
 * Usage: npx tsx scripts/grid-search.ts
 */

import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";
import { createCTCFSite } from "../src/domain/models/genome";
import {
  AlphaGenomeClient,
  ValidationResult,
} from "../src/validation/alphagenome";
import * as fs from "fs";
import * as path from "path";

// Parameter grid to search
const PARAM_GRID = {
  velocity: [500, 1000, 2000], // bp/step
  processivity: [300, 600, 1200], // kb (not directly used in current model)
  cohesinCount: [10, 20, 50], // количество cohesin
  stallProbability: [0.8, 0.9, 1.0], // вероятность остановки на CTCF
};

// HBB Locus configuration (chr11:5.24-5.34Mb normalized to 0-100kb)
const HBB_CONFIG = {
  name: "HBB",
  chromosome: "chr11",
  start: 5240000,
  end: 5340000,
  genomeLength: 100000,
  // CTCF sites from ENCODE (GM12878)
  ctcfSites: [
    { pos: 25000, orient: "F" as const, strength: 0.9 }, // HS5
    { pos: 30000, orient: "R" as const, strength: 0.85 }, // HS4
    { pos: 45000, orient: "F" as const, strength: 0.8 }, // HS3
    { pos: 55000, orient: "R" as const, strength: 0.9 }, // HS2
    { pos: 75000, orient: "F" as const, strength: 0.85 }, // HS1
  ],
};

interface GridResult {
  params: {
    velocity: number;
    processivity: number;
    cohesinCount: number;
    stallProbability: number;
  };
  metrics: {
    pearson: number;
    spearman: number;
    rmse: number;
    loopCount: number;
    avgLoopSize: number;
  };
  timestamp: string;
}

/**
 * Run single simulation with given parameters
 */
function runSimulation(params: GridResult["params"]): {
  loops: any[];
  matrix: number[][];
} {
  const sites = HBB_CONFIG.ctcfSites.map((s) =>
    createCTCFSite(HBB_CONFIG.chromosome, s.pos, s.orient, s.strength),
  );

  const engine = new MultiCohesinEngine({
    genomeLength: HBB_CONFIG.genomeLength,
    ctcfSites: sites,
    numCohesins: params.cohesinCount,
    velocity: params.velocity,
    seed: 42, // Fixed seed for reproducibility
    maxSteps: 10000,
  });

  // Run simulation
  const loops = engine.run(10000);

  // Get contact matrix at 1kb resolution
  const matrix = engine.getContactMatrix(1000, 0.1);

  return { loops, matrix };
}

/**
 * Calculate correlation with AlphaGenome prediction
 */
async function validateWithAlphaGenome(
  matrix: number[][],
): Promise<ValidationResult> {
  const client = new AlphaGenomeClient({ apiKey: "mock" });

  return await client.validateArchcode(
    {
      chromosome: HBB_CONFIG.chromosome,
      start: HBB_CONFIG.start,
      end: HBB_CONFIG.end,
    },
    matrix,
  );
}

/**
 * Run grid search over all parameter combinations
 */
async function runGridSearch(): Promise<GridResult[]> {
  const results: GridResult[] = [];
  const totalRuns =
    PARAM_GRID.velocity.length *
    PARAM_GRID.processivity.length *
    PARAM_GRID.cohesinCount.length *
    PARAM_GRID.stallProbability.length;

  console.log(`🔬 Starting grid search: ${totalRuns} parameter combinations`);
  console.log(`   Velocity: ${PARAM_GRID.velocity.join(", ")}`);
  console.log(`   Cohesin count: ${PARAM_GRID.cohesinCount.join(", ")}`);
  console.log("");

  let currentRun = 0;

  for (const velocity of PARAM_GRID.velocity) {
    for (const processivity of PARAM_GRID.processivity) {
      for (const cohesinCount of PARAM_GRID.cohesinCount) {
        for (const stallProbability of PARAM_GRID.stallProbability) {
          currentRun++;
          const params = {
            velocity,
            processivity,
            cohesinCount,
            stallProbability,
          };

          console.log(
            `[${currentRun}/${totalRuns}] Testing: v=${velocity}, n=${cohesinCount}`,
          );

          try {
            // Run simulation
            const { loops, matrix } = runSimulation(params);

            // Validate against AlphaGenome
            const validation = await validateWithAlphaGenome(matrix);

            // Calculate loop statistics
            const avgLoopSize =
              loops.length > 0
                ? loops.reduce(
                    (sum, l) => sum + (l.rightAnchor - l.leftAnchor),
                    0,
                  ) / loops.length
                : 0;

            const result: GridResult = {
              params,
              metrics: {
                pearson: validation.pearsonCorrelation,
                spearman: validation.spearmanCorrelation,
                rmse: validation.rmse,
                loopCount: loops.length,
                avgLoopSize,
              },
              timestamp: new Date().toISOString(),
            };

            results.push(result);

            console.log(
              `   ✅ Pearson r = ${validation.pearsonCorrelation.toFixed(3)}, Loops: ${loops.length}`,
            );
          } catch (error) {
            console.error(`   ❌ Error:`, error);
          }
        }
      }
    }
  }

  return results;
}

/**
 * Find best parameters from results
 */
function findBestParams(results: GridResult[]): GridResult | null {
  if (results.length === 0) return null;

  // Sort by Pearson correlation (descending)
  const sorted = [...results].sort(
    (a, b) => b.metrics.pearson - a.metrics.pearson,
  );
  return sorted[0];
}

/**
 * Save results to JSON file
 */
function saveResults(results: GridResult[], best: GridResult | null): void {
  const outputPath = path.join(process.cwd(), "results", "grid-search.json");

  const output = {
    summary: {
      totalRuns: results.length,
      bestParams: best?.params ?? null,
      bestMetrics: best?.metrics ?? null,
      timestamp: new Date().toISOString(),
    },
    allResults: results,
  };

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`\n💾 Results saved to: ${outputPath}`);
}

/**
 * Print summary table
 */
function printSummary(results: GridResult[]): void {
  console.log("\n📊 Grid Search Summary");
  console.log("======================");
  console.log("Top 5 parameter combinations by Pearson r:");
  console.log("");

  const sorted = [...results]
    .sort((a, b) => b.metrics.pearson - a.metrics.pearson)
    .slice(0, 5);

  console.log("Rank | Velocity | Cohesins | Pearson r | Loops | Avg Size");
  console.log("-----|----------|----------|-----------|-------|----------");

  sorted.forEach((r, i) => {
    console.log(
      ` ${i + 1}   | ` +
        `${r.params.velocity.toString().padStart(8)} | ` +
        `${r.params.cohesinCount.toString().padStart(8)} | ` +
        `${r.metrics.pearson.toFixed(3).padStart(9)} | ` +
        `${r.metrics.loopCount.toString().padStart(5)} | ` +
        `${(r.metrics.avgLoopSize / 1000).toFixed(1)} kb`,
    );
  });
}

// Main execution
async function main(): Promise<void> {
  console.log("╔════════════════════════════════════════╗");
  console.log("║     ARCHCODE Parameter Grid Search     ║");
  console.log("║   Optimizing for AlphaGenome r > 0.7   ║");
  console.log("╚════════════════════════════════════════╝");
  console.log("");

  const startTime = Date.now();

  // Run grid search
  const results = await runGridSearch();

  // Find best parameters
  const best = findBestParams(results);

  // Print summary
  printSummary(results);

  // Save results
  saveResults(results, best);

  // Final report
  const duration = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log("");
  console.log("✅ Grid search complete!");
  console.log(`   Duration: ${duration}s`);
  console.log(`   Total runs: ${results.length}`);

  if (best) {
    console.log("");
    console.log("🏆 Best Parameters:");
    console.log(`   Velocity: ${best.params.velocity} bp/step`);
    console.log(`   Cohesin count: ${best.params.cohesinCount}`);
    console.log(`   Pearson r: ${best.metrics.pearson.toFixed(3)}`);

    if (best.metrics.pearson >= 0.7) {
      console.log("");
      console.log("🎉 TARGET ACHIEVED: r >= 0.7");
    } else {
      console.log("");
      console.log("⚠️  Target not reached. Consider expanding parameter grid.");
    }
  }
}

main().catch(console.error);
