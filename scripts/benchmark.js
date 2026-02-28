/**
 * ARCHCODE Performance Benchmark
 * Generates timing and memory usage statistics for publication Methods
 *
 * Run: node scripts/benchmark.js
 */

const { MultiCohesinEngine } = require("../dist/engines/MultiCohesinEngine.js");
const { createCTCFSite } = require("../dist/domain/models/genome.js");
const fs = require("fs");
const path = require("path");

// Test configurations
const CONFIGS = [
  { name: "Small (10 LEFs)", genomeLength: 100000, cohesins: 10 },
  { name: "Medium (20 LEFs)", genomeLength: 100000, cohesins: 20 },
  { name: "Large (50 LEFs)", genomeLength: 100000, cohesins: 50 },
  { name: "Extended (20 LEFs, 500kb)", genomeLength: 500000, cohesins: 20 },
];

const CTCF_SITES = [
  { pos: 25000, orient: "F", strength: 0.9 },
  { pos: 30000, orient: "R", strength: 0.85 },
  { pos: 45000, orient: "F", strength: 0.8 },
  { pos: 55000, orient: "R", strength: 0.9 },
  { pos: 75000, orient: "F", strength: 0.85 },
];

function benchmark(config, steps) {
  const sites = CTCF_SITES.map((s) =>
    createCTCFSite("chr1", s.pos % config.genomeLength, s.orient, s.strength),
  );

  const engine = new MultiCohesinEngine({
    genomeLength: config.genomeLength,
    ctcfSites: sites,
    numCohesins: config.cohesins,
    velocity: 1000,
    seed: 42,
    maxSteps: steps,
  });

  // Measure time
  const startTime = process.hrtime.bigint();
  const startMemory = process.memoryUsage();

  const loops = engine.run(steps);

  const endTime = process.hrtime.bigint();
  const endMemory = process.memoryUsage();

  const durationMs = Number(endTime - startTime) / 1_000_000;
  const memoryDelta = (endMemory.heapUsed - startMemory.heapUsed) / 1024 / 1024;

  // Calculate steps per second
  const stepsPerSecond = (steps / (durationMs / 1000)).toFixed(0);

  return {
    config: config.name,
    genomeLength: config.genomeLength,
    cohesinCount: config.cohesins,
    steps,
    durationMs: durationMs.toFixed(2),
    stepsPerSecond,
    memoryDeltaMB: memoryDelta.toFixed(2),
    peakMemoryMB: (endMemory.heapUsed / 1024 / 1024).toFixed(2),
    loopsFormed: loops.length,
  };
}

async function main() {
  console.log("╔════════════════════════════════════════╗");
  console.log("║      ARCHCODE Performance Benchmark    ║");
  console.log("╚════════════════════════════════════════╝");
  console.log("");

  const results = [];

  // Benchmark different configurations
  for (const config of CONFIGS) {
    console.log(`Running: ${config.name}...`);

    // Warmup
    benchmark(config, 100);

    // Actual benchmark
    const result = benchmark(config, 10000);
    results.push(result);

    console.log(
      `  ✓ ${result.durationMs}ms (${result.stepsPerSecond} steps/s)`,
    );
  }

  // Print summary table
  console.log("");
  console.log("📊 Performance Results");
  console.log("======================");
  console.log("");
  console.log(
    "Configuration              | Steps   | Time (ms) | Steps/s | Memory (MB) | Loops",
  );
  console.log(
    "---------------------------|---------|-----------|---------|-------------|-------",
  );

  results.forEach((r) => {
    console.log(
      `${r.config.padEnd(26)} | ` +
        `${r.steps.toString().padStart(7)} | ` +
        `${r.durationMs.padStart(9)} | ` +
        `${r.stepsPerSecond.padStart(7)} | ` +
        `${r.peakMemoryMB.padStart(11)} | ` +
        `${r.loopsFormed}`,
    );
  });

  // Hardware info
  console.log("");
  console.log("💻 Hardware Information");
  console.log("=======================");
  console.log(`Platform: ${process.platform}`);
  console.log(`Architecture: ${process.arch}`);
  console.log(`Node.js: ${process.version}`);
  console.log(`CPUs: ${require("os").cpus().length}`);
  console.log(
    `Total Memory: ${(require("os").totalmem() / 1024 / 1024 / 1024).toFixed(1)} GB`,
  );

  // Save results
  const outputPath = path.join(process.cwd(), "publication", "benchmark.md");
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  const markdown = `# ARCHCODE Performance Benchmark

Generated: ${new Date().toISOString()}

## Results

| Configuration | Steps | Time (ms) | Steps/s | Memory (MB) | Loops |
|--------------|-------|-----------|---------|-------------|-------|
${results
  .map(
    (r) =>
      `| ${r.config} | ${r.steps} | ${r.durationMs} | ${r.stepsPerSecond} | ${r.peakMemoryMB} | ${r.loopsFormed} |`,
  )
  .join("\n")}

## Hardware

- **Platform**: ${process.platform}
- **Architecture**: ${process.arch}
- **Node.js**: ${process.version}
- **CPUs**: ${require("os").cpus().length}
- **Total Memory**: ${(require("os").totalmem() / 1024 / 1024 / 1024).toFixed(1)} GB

## For Publication Methods

> "Simulations were performed on a ${require("os").cpus()[0].model} with ${(require("os").totalmem() / 1024 / 1024 / 1024).toFixed(0)} GB RAM. 
> A typical 100kb locus with 20 loop extrusion factors completed 10,000 simulation steps in ${results.find((r) => r.config === "Medium (20 LEFs)")?.durationMs}ms 
> (≈${results.find((r) => r.config === "Medium (20 LEFs)")?.stepsPerSecond} steps/second)."
`;

  fs.writeFileSync(outputPath, markdown);
  console.log("");
  console.log(`💾 Benchmark saved to: ${outputPath}`);
}

main().catch(console.error);
