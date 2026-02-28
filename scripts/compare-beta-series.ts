/**
 * Сравнение серии beta тестов с baseline.
 * Выводит статистику diff для каждого beta.
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
  "fountain_baseline.json",
);
const BETAS = [2, 5, 10, 15, 20];

interface RunResult {
  heatmap: number[][];
  params?: { beta?: number };
  numLoops?: number;
  fountainLoader?: { stepLoadingProbability?: number };
}

function loadJson(p: string): RunResult | null {
  try {
    const raw = fs.readFileSync(p, "utf-8");
    return JSON.parse(raw) as RunResult;
  } catch {
    return null;
  }
}

function computeDiffStats(
  A: number[][],
  B: number[][],
): { min: number; max: number; mean: number; nonZeroCount: number } {
  let min = Infinity;
  let max = -Infinity;
  let sum = 0;
  let count = 0;
  let nonZeroCount = 0;

  for (let i = 0; i < A.length; i++) {
    for (let j = 0; j < (A[i]?.length ?? 0); j++) {
      const d = (A[i]![j] ?? 0) - (B[i]![j] ?? 0);
      if (d < min) min = d;
      if (d > max) max = d;
      sum += d;
      count++;
      if (d !== 0) nonZeroCount++;
    }
  }

  return { min, max, mean: count > 0 ? sum / count : 0, nonZeroCount };
}

function main(): void {
  const baseline = loadJson(BASELINE_PATH);
  if (!baseline) {
    console.error("Baseline not found:", BASELINE_PATH);
    return;
  }

  console.log("Beta Series Comparison");
  console.log("======================\n");
  console.log(
    "| Beta | Loops | stepLoadProb | Diff Min | Diff Max | Diff Mean | NonZero |",
  );
  console.log(
    "|------|-------|--------------|----------|----------|-----------|---------|",
  );

  for (const beta of BETAS) {
    const testPath = path.join(
      __dirname,
      "..",
      "results",
      `fountain_beta${beta}.json`,
    );
    const test = loadJson(testPath);

    if (!test) {
      // Try fountain_test_v1.json for beta=20
      if (beta === 20) {
        const altPath = path.join(
          __dirname,
          "..",
          "results",
          "fountain_test_v1.json",
        );
        const altTest = loadJson(altPath);
        if (altTest) {
          const stats = computeDiffStats(altTest.heatmap, baseline.heatmap);
          const prob = altTest.fountainLoader?.stepLoadingProbability ?? 0;
          console.log(
            `| ${beta.toString().padStart(4)} | ${(altTest.numLoops ?? 0).toString().padStart(5)} | ${prob.toFixed(6).padStart(12)} | ${stats.min.toFixed(3).padStart(8)} | ${stats.max.toFixed(3).padStart(8)} | ${stats.mean.toFixed(6).padStart(9)} | ${stats.nonZeroCount.toString().padStart(7)} |`,
          );
        }
      }
      continue;
    }

    const stats = computeDiffStats(test.heatmap, baseline.heatmap);
    const prob = test.fountainLoader?.stepLoadingProbability ?? 0;
    console.log(
      `| ${beta.toString().padStart(4)} | ${(test.numLoops ?? 0).toString().padStart(5)} | ${prob.toFixed(6).padStart(12)} | ${stats.min.toFixed(3).padStart(8)} | ${stats.max.toFixed(3).padStart(8)} | ${stats.mean.toFixed(6).padStart(9)} | ${stats.nonZeroCount.toString().padStart(7)} |`,
    );
  }

  console.log("\nBaseline: beta=0, loops=" + (baseline.numLoops ?? "N/A"));
}

main();
