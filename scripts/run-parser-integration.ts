/**
 * ARCHCODE Parser Integration Runner
 *
 * Runs integrated analysis with Scientific News Parser data
 * and saves results to JSON report.
 *
 * Usage: npx tsx scripts/run-parser-integration.ts [parserPath] [chromosome:start-end]
 *
 * Examples:
 *   npx tsx scripts/run-parser-integration.ts
 *   npx tsx scripts/run-parser-integration.ts "D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs"
 *   npx tsx scripts/run-parser-integration.ts "D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs" "chr11:5200000-5400000"
 */

import * as fs from "fs";
import * as path from "path";
import {
  AlphaGenomeService,
  GenomeInterval,
} from "../src/services/AlphaGenomeNodeService";

const DEFAULT_PARSER_PATH = "D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs";
const OUTPUT_DIR = path.join(process.cwd(), "results");

interface IntegrationReport {
  title: string;
  date: string;
  parserPath: string;
  kramerParams: {
    alpha: number;
    gamma: number;
    kBase: number;
  };
  analyses: Array<{
    name: string;
    interval: GenomeInterval;
    matrixSize: number;
    loopsDetected: number;
    riskScore: number;
    topLoops: Array<{ start: number; end: number; strength: number }>;
  }>;
  summary: {
    totalAnalyses: number;
    meanRiskScore: number;
    totalLoops: number;
    bigWigStatus: "loaded" | "mock";
  };
}

async function main() {
  const args = process.argv.slice(2);
  const parserPath = args[0] || DEFAULT_PARSER_PATH;

  // Parse interval if provided
  let customInterval: GenomeInterval | undefined;
  if (args[1]) {
    const match = args[1].match(/^(chr\w+):(\d+)-(\d+)$/);
    if (match) {
      customInterval = {
        chromosome: match[1],
        start: parseInt(match[2]),
        end: parseInt(match[3]),
      };
    }
  }

  console.log("═".repeat(70));
  console.log("ARCHCODE × Parser Integration Report Generator");
  console.log("═".repeat(70));
  console.log(`Parser: ${parserPath}`);
  console.log(`Date: ${new Date().toISOString()}`);
  console.log();

  const service = new AlphaGenomeService({ mode: "mock" });

  // Define loci to analyze
  const loci: Array<{ name: string; interval: GenomeInterval }> = customInterval
    ? [{ name: "Custom", interval: customInterval }]
    : [
        {
          name: "HBB (Beta-Globin)",
          interval: { chromosome: "chr11", start: 5200000, end: 5400000 },
        },
        {
          name: "MYC",
          interval: { chromosome: "chr8", start: 127735000, end: 128835000 },
        },
        {
          name: "SOX2",
          interval: { chromosome: "chr3", start: 181500000, end: 182300000 },
        },
        {
          name: "IGH",
          interval: { chromosome: "chr14", start: 105586000, end: 106886000 },
        },
      ];

  const report: IntegrationReport = {
    title: "ARCHCODE Parser Integration Analysis",
    date: new Date().toISOString(),
    parserPath,
    kramerParams: { alpha: 0.92, gamma: 0.8, kBase: 0.002 },
    analyses: [],
    summary: {
      totalAnalyses: 0,
      meanRiskScore: 0,
      totalLoops: 0,
      bigWigStatus: "mock",
    },
  };

  let totalRiskScore = 0;
  let totalLoops = 0;

  for (const { name, interval } of loci) {
    console.log(`\nAnalyzing ${name}...`);
    console.log(`  ${interval.chromosome}:${interval.start}-${interval.end}`);

    try {
      const result = await service.importFromParser(parserPath, interval);

      const analysis = {
        name,
        interval: result.interval,
        matrixSize: result.simulation.contactMatrix.length,
        loopsDetected: result.simulation.loops.length,
        riskScore: result.riskScore,
        topLoops: result.simulation.loops.slice(0, 5),
      };

      report.analyses.push(analysis);
      totalRiskScore += result.riskScore;
      totalLoops += result.simulation.loops.length;

      console.log(
        `  ✓ Completed: ${analysis.loopsDetected} loops, risk=${analysis.riskScore}%`,
      );
    } catch (error) {
      console.error(`  ✗ Failed:`, error);
    }
  }

  // Update summary
  report.summary = {
    totalAnalyses: report.analyses.length,
    meanRiskScore: Math.round(totalRiskScore / report.analyses.length),
    totalLoops,
    bigWigStatus: "mock", // Would be 'loaded' if pyBigWig worked
  };

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Save report
  const outputPath = path.join(OUTPUT_DIR, "parser_integration_report.json");
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  console.log(`\n✓ Report saved: ${outputPath}`);

  // Print summary
  console.log("\n" + "═".repeat(70));
  console.log("Summary");
  console.log("═".repeat(70));
  console.log(`Total Analyses: ${report.summary.totalAnalyses}`);
  console.log(`Mean Risk Score: ${report.summary.meanRiskScore}%`);
  console.log(`Total Loops Detected: ${report.summary.totalLoops}`);
  console.log(`BigWig Status: ${report.summary.bigWigStatus}`);
  console.log(
    `\nKramer Kinetics: α=${report.kramerParams.alpha}, γ=${report.kramerParams.gamma}, k_base=${report.kramerParams.kBase}`,
  );

  // Details table
  console.log("\n" + "─".repeat(70));
  console.log("| Locus                | Chr   | Loops | Risk  |");
  console.log(
    "|" +
      "─".repeat(22) +
      "|" +
      "─".repeat(7) +
      "|" +
      "─".repeat(7) +
      "|" +
      "─".repeat(7) +
      "|",
  );
  for (const a of report.analyses) {
    const name = a.name.padEnd(20).slice(0, 20);
    const chr = a.interval.chromosome.padEnd(5);
    const loops = String(a.loopsDetected).padStart(5);
    const risk = (a.riskScore + "%").padStart(5);
    console.log(`| ${name} | ${chr} | ${loops} | ${risk} |`);
  }
  console.log("─".repeat(70));
}

main().catch(console.error);

