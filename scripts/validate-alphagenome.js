#!/usr/bin/env node
/**
 * CLI script to validate ARCHCODE against AlphaGenome
 * Usage: node scripts/validate-alphagenome.js --api-key YOUR_KEY --interval chr11:5200000-5350000
 */

const { AlphaGenomeClient } = require("../dist/validation/alphagenome.js");
const {
  LoopExtrusionEngine,
} = require("../dist/engines/LoopExtrusionEngine.js");
const { loadCTCFFromBED } = require("../dist/parsers/bed.js");
const fs = require("fs");
const path = require("path");

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    apiKey: process.env.ALPHAGENOME_API_KEY,
    interval: "chr11:5200000-5350000",
    ctcfFile: "data/input/ctcf/GM12878_HBB_CTCF_peaks.bed",
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--api-key":
      case "-k":
        options.apiKey = args[++i];
        break;
      case "--interval":
      case "-i":
        options.interval = args[++i];
        break;
      case "--ctcf":
      case "-c":
        options.ctcfFile = args[++i];
        break;
      case "--help":
      case "-h":
        showHelp();
        process.exit(0);
    }
  }

  return options;
}

function showHelp() {
  console.log(`
ARCHCODE AlphaGenome Validator

Usage:
  node scripts/validate-alphagenome.js [options]

Options:
  -k, --api-key <key>     AlphaGenome API key (or set ALPHAGENOME_API_KEY env var)
  -i, --interval <chr:start-end>  Genomic interval (default: chr11:5200000-5350000)
  -c, --ctcf <file>       CTCF BED file (default: data/input/ctcf/GM12878_HBB_CTCF_peaks.bed)
  -h, --help              Show this help

Examples:
  # Validate with environment variable
  ALPHAGENOME_API_KEY=xxx node scripts/validate-alphagenome.js

  # Validate specific interval
  node scripts/validate-alphagenome.js -k YOUR_KEY -i chr11:5000000-5500000
`);
}

function parseInterval(str) {
  const match = str.match(/^(chr\w+):(\d+)-(\d+)$/);
  if (!match) {
    throw new Error(
      `Invalid interval format: ${str}. Expected: chr11:5200000-5350000`,
    );
  }
  return {
    chromosome: match[1],
    start: parseInt(match[2]),
    end: parseInt(match[3]),
  };
}

async function main() {
  const options = parseArgs();

  if (!options.apiKey) {
    console.error("❌ Error: AlphaGenome API key required");
    console.error(
      "Set ALPHAGENOME_API_KEY environment variable or use --api-key",
    );
    process.exit(1);
  }

  console.log("🔬 ARCHCODE AlphaGenome Validation\n");

  // Parse interval
  const interval = parseInterval(options.interval);
  console.log(
    `Interval: ${interval.chromosome}:${interval.start.toLocaleString()}-${interval.end.toLocaleString()}`,
  );

  // Load CTCF data
  const ctcfPath = path.join(__dirname, "..", options.ctcfFile);
  if (!fs.existsSync(ctcfPath)) {
    console.error(`❌ CTCF file not found: ${ctcfPath}`);
    process.exit(1);
  }

  const bedContent = fs.readFileSync(ctcfPath, "utf-8");
  const { sites } = loadCTCFFromBED(bedContent);
  console.log(`Loaded ${sites.length} CTCF sites\n`);

  // Run ARCHCODE simulation
  console.log("Running ARCHCODE simulation...");
  const engine = new LoopExtrusionEngine({
    genomeLength: interval.end - interval.start,
    ctcfSites: sites,
    cohesinLoadPosition: Math.floor((interval.start + interval.end) / 2),
    velocity: 1000,
    seed: 42,
  });

  const loops = engine.run(500);
  console.log(`✓ Formed ${loops.length} loop(s)`);

  // Generate contact matrix
  const {
    loopsToContactMatrix,
  } = require("../dist/engines/LoopExtrusionEngine.js");
  const archcodeMatrix = loopsToContactMatrix(
    loops,
    interval.start,
    interval.end,
    10000,
  );

  // Validate against AlphaGenome
  console.log("\nQuerying AlphaGenome API...");
  const client = new AlphaGenomeClient({ apiKey: options.apiKey });

  try {
    const result = await client.validateArchcode(interval, archcodeMatrix);

    // Display results
    console.log("\n=== Validation Results ===\n");

    const pearsonColor =
      result.pearsonCorrelation > 0.8
        ? "\x1b[32m"
        : result.pearsonCorrelation > 0.6
          ? "\x1b[33m"
          : "\x1b[31m";
    const reset = "\x1b[0m";

    console.log(
      `Pearson Correlation:  ${pearsonColor}${result.pearsonCorrelation.toFixed(4)}${reset}`,
    );
    console.log(
      `Spearman Correlation: ${result.spearmanCorrelation.toFixed(4)}`,
    );
    console.log(`RMSE:                 ${result.rmse.toFixed(6)}`);
    console.log(`MSE:                  ${result.mse.toFixed(6)}`);

    // Interpretation
    console.log("\n=== Interpretation ===\n");
    if (result.pearsonCorrelation > 0.8) {
      console.log("✅ EXCELLENT: Your simulation closely matches AlphaGenome");
      console.log("   The physical model is well-calibrated.");
    } else if (result.pearsonCorrelation > 0.6) {
      console.log("⚠️  GOOD: Reasonable agreement with some differences");
      console.log("   Consider tuning extrusion speed or CTCF strength.");
    } else {
      console.log("❌ POOR: Significant deviation from AlphaGenome");
      console.log("   Check model assumptions and parameters.");
    }

    // Save results
    const outputPath = path.join(
      __dirname,
      "..",
      "data",
      "output",
      `validation_${Date.now()}.json`,
    );
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(
      outputPath,
      JSON.stringify(
        {
          interval,
          metrics: {
            pearson: result.pearsonCorrelation,
            spearman: result.spearmanCorrelation,
            rmse: result.rmse,
            mse: result.mse,
          },
          timestamp: new Date().toISOString(),
        },
        null,
        2,
      ),
    );
    console.log(`\n💾 Results saved to: ${outputPath}`);
  } catch (err) {
    console.error("\n❌ Validation failed:", err.message);
    process.exit(1);
  }
}

main().catch(console.error);
