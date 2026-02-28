/**
 * Quick validation script for HBB locus
 * Run: node scripts/quick-validate.js
 *
 * This script validates the current parameters against AlphaGenome
 * without requiring a full grid search.
 */

const { MultiCohesinEngine } = require("../dist/engines/MultiCohesinEngine.js");
const { createCTCFSite } = require("../dist/domain/models/genome.js");
const { AlphaGenomeClient } = require("../dist/validation/alphagenome.js");
const fs = require("fs");
const path = require("path");

// HBB Locus CTCF sites
const HBB_SITES = [
  { pos: 25000, orient: "F", strength: 0.9 },
  { pos: 30000, orient: "R", strength: 0.85 },
  { pos: 45000, orient: "F", strength: 0.8 },
  { pos: 55000, orient: "R", strength: 0.9 },
  { pos: 75000, orient: "F", strength: 0.85 },
];

const GENOME_LENGTH = 100000;

async function validate(params) {
  console.log(
    `\n🔬 Validating: velocity=${params.velocity}, cohesins=${params.cohesinCount}`,
  );

  const sites = HBB_SITES.map((s) =>
    createCTCFSite("chr11", s.pos, s.orient, s.strength),
  );

  const engine = new MultiCohesinEngine({
    genomeLength: GENOME_LENGTH,
    ctcfSites: sites,
    numCohesins: params.cohesinCount,
    velocity: params.velocity,
    seed: 42,
    maxSteps: 10000,
  });

  const loops = engine.run(10000);
  const matrix = engine.getContactMatrix(1000, 0.1);

  const client = new AlphaGenomeClient({ apiKey: "mock" });
  const validation = await client.validateArchcode(
    { chromosome: "chr11", start: 5240000, end: 5340000 },
    matrix,
  );

  const avgLoopSize =
    loops.length > 0
      ? loops.reduce((sum, l) => sum + (l.rightAnchor - l.leftAnchor), 0) /
        loops.length
      : 0;

  console.log(
    `   Loops: ${loops.length}, Pearson r: ${validation.pearsonCorrelation.toFixed(3)}`,
  );

  return {
    params,
    metrics: {
      pearson: validation.pearsonCorrelation,
      spearman: validation.spearmanCorrelation,
      rmse: validation.rmse,
      loopCount: loops.length,
      avgLoopSize,
    },
  };
}

async function main() {
  console.log("╔════════════════════════════════════════╗");
  console.log("║      ARCHCODE Quick Validation         ║");
  console.log("║   HBB locus vs AlphaGenome (mock)      ║");
  console.log("╚════════════════════════════════════════╝");

  const results = [];

  // Test a few parameter combinations
  const tests = [
    { velocity: 500, cohesinCount: 10 },
    { velocity: 1000, cohesinCount: 10 },
    { velocity: 1000, cohesinCount: 20 },
    { velocity: 2000, cohesinCount: 20 },
  ];

  for (const params of tests) {
    const result = await validate(params);
    results.push(result);
  }

  // Summary
  console.log("\n📊 Summary:");
  console.log("Velocity | Cohesins | Pearson r | Loops");
  console.log("---------|----------|-----------|-------");
  results.forEach((r) => {
    console.log(
      `${r.params.velocity.toString().padStart(8)} | ` +
        `${r.params.cohesinCount.toString().padStart(8)} | ` +
        `${r.metrics.pearson.toFixed(3).padStart(9)} | ` +
        `${r.metrics.loopCount}`,
    );
  });

  // Best result
  const best = results.reduce((max, r) =>
    r.metrics.pearson > max.metrics.pearson ? r : max,
  );
  console.log(
    `\n🏆 Best: velocity=${best.params.velocity}, cohesins=${best.params.cohesinCount}`,
  );
  console.log(`   Pearson r = ${best.metrics.pearson.toFixed(3)}`);

  if (best.metrics.pearson >= 0.7) {
    console.log("\n🎉 TARGET ACHIEVED: r >= 0.7");
  } else {
    console.log(
      "\n⚠️  Target not reached. Run grid search for more combinations.",
    );
  }

  // Save results
  const outputPath = path.join(process.cwd(), "results", "quick-validate.json");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  console.log(`\n💾 Results saved to: ${outputPath}`);
}

main().catch(console.error);
