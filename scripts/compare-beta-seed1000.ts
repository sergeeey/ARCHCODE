/**
 * Сравнение серии beta тестов с baseline (seed=1000).
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASELINE_PATH = path.join(
  __dirname,
  "..",
  "results",
  "baseline_s1000.json",
);
const BETAS = [2, 5, 10, 15];

interface RunResult {
  heatmap: number[][];
  fountainLoader?: { stepLoadingProbability?: number };
  numLoops?: number;
}

function loadJson(p: string): RunResult | null {
  try {
    return JSON.parse(fs.readFileSync(p, "utf-8")) as RunResult;
  } catch {
    return null;
  }
}

function computeDiffStats(A: number[][], B: number[][]) {
  let min = Infinity,
    max = -Infinity,
    sum = 0,
    count = 0,
    nonZero = 0;
  for (let i = 0; i < A.length; i++) {
    for (let j = 0; j < (A[i]?.length ?? 0); j++) {
      const d = (A[i]![j] ?? 0) - (B[i]![j] ?? 0);
      min = Math.min(min, d);
      max = Math.max(max, d);
      sum += Math.abs(d);
      count++;
      if (d !== 0) nonZero++;
    }
  }
  return { min, max, meanAbs: count > 0 ? sum / count : 0, nonZero };
}

function main() {
  const baseline = loadJson(BASELINE_PATH);
  if (!baseline) {
    console.error("Baseline not found");
    return;
  }

  console.log("Beta Series Comparison (seed=1000)");
  console.log("===================================\n");
  console.log(
    "| Beta | stepLoadProb | Diff Max | Mean|Diff| | NonZero Cells |",
  );
  console.log(
    "|------|--------------|----------|------------|---------------|",
  );

  for (const beta of BETAS) {
    const test = loadJson(
      path.join(__dirname, "..", "results", `beta${beta}_s1000.json`),
    );
    if (!test) continue;
    const stats = computeDiffStats(test.heatmap, baseline.heatmap);
    const prob = test.fountainLoader?.stepLoadingProbability ?? 0;
    console.log(
      `| ${beta.toString().padStart(4)} | ${prob.toFixed(6).padStart(12)} | ${stats.max.toFixed(3).padStart(8)} | ${stats.meanAbs.toFixed(6).padStart(10)} | ${stats.nonZero.toString().padStart(13)} |`,
    );
  }

  console.log(`\nBaseline: loops=${baseline.numLoops}`);
}

main();
