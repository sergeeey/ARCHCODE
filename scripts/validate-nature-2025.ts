/**
 * Blind-test validation: Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)
 * In silico HBB / Sox2 loci, loop duration vs experimental 6–19 min.
 *
 * Run: npx tsx scripts/validate-nature-2025.ts [--locus=HBB|SOX2|HBB_CTCFKD] [--runs=1000] [--steps=36000]
 */

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { parseArgs } from "util";

import {
  createCTCFSite,
  Loop,
  getLoopDurationSteps,
} from "../src/domain/models/genome";
import { MultiCohesinEngine } from "../src/engines/MultiCohesinEngine";
import { SABATE_NATURE_2025 } from "../src/domain/constants/biophysics";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Единый формат CTCF-сайтов: { pos, strength, orient }
const HBB_SITES = [
  { pos: 25000, strength: 0.9, orient: "F" as const },
  { pos: 30000, strength: 0.85, orient: "R" as const },
  { pos: 45000, strength: 0.8, orient: "F" as const },
  { pos: 55000, strength: 0.9, orient: "R" as const },
  { pos: 75000, strength: 0.85, orient: "F" as const },
  { pos: 90000, strength: 0.9, orient: "R" as const },
];

const SOX2_SITES = [
  { pos: 5000, strength: 0.9, orient: "F" as const },
  { pos: 10000, strength: 0.9, orient: "R" as const },
  { pos: 25000, strength: 0.8, orient: "F" as const },
  { pos: 35000, strength: 0.8, orient: "R" as const },
  { pos: 45000, strength: 0.85, orient: "F" as const },
  { pos: 55000, strength: 0.85, orient: "R" as const },
];

const SOX2_GENOME_LENGTH = 60000; // 60 kb локус Sox2

const args = parseArgs({
  options: {
    locus: { type: "string", default: "HBB" },
    runs: { type: "string", default: "1000" },
    steps: { type: "string", default: "36000" },
    seed: { type: "string" },
    seedOffset: { type: "string", default: "0" },
  },
});

const LOCI = {
  HBB: HBB_SITES,
  SOX2: SOX2_SITES,
  HBB_CTCFKD: HBB_SITES.filter((s) => s.strength > 0.8), // только сильные сайты
} as const;

const locusKey = (
  args.values.locus ?? "HBB"
).toUpperCase() as keyof typeof LOCI;
const SELECTED_SITES = LOCI[locusKey] ?? LOCI.HBB;
const NUM_RUNS = Number(args.values.runs ?? process.env.NUM_RUNS) || 1000;
const STEPS_PER_RUN =
  Number(args.values.steps ?? process.env.STEPS_PER_RUN) || 36_000;
const BASE_SEED = Number(args.values.seed ?? args.values.seedOffset ?? 0);

const GENOME_LENGTH = 100_000; // HBB / HBB_CTCFKD
const STEPS_PER_MINUTE = 60;

function runSingleSimulation(seed: number): Loop[] {
  const chrom = locusKey === "SOX2" ? "chr3" : "chr11";
  const genomeLength = locusKey === "SOX2" ? SOX2_GENOME_LENGTH : GENOME_LENGTH;
  const ctcfSites = SELECTED_SITES.map((s) =>
    createCTCFSite(chrom, s.pos, s.orient, s.strength),
  );
  const engine = new MultiCohesinEngine({
    genomeLength,
    ctcfSites,
    velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
    unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
    loadingProbabilityPerStep: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
    trackLoopDuration: true,
    seed,
    maxSteps: STEPS_PER_RUN,
  });
  engine.run(STEPS_PER_RUN);
  return engine.getLoops();
}

function computeStats(durationsSteps: number[]) {
  const n = durationsSteps.length;
  if (n === 0) {
    return { mean: 0, std: 0, ci95Lower: 0, ci95Upper: 0, n: 0 };
  }
  const mean = durationsSteps.reduce((a, b) => a + b, 0) / n;
  const variance = durationsSteps.reduce((s, x) => s + (x - mean) ** 2, 0) / n;
  const std = Math.sqrt(variance);
  const se = std / Math.sqrt(n);
  const z95 = 1.96;
  return {
    mean,
    std,
    ci95Lower: mean - z95 * se,
    ci95Upper: mean + z95 * se,
    n,
  };
}

function histogram(
  durationsSteps: number[],
  binMinutes: number,
): Map<number, number> {
  const stepsPerBin = binMinutes * STEPS_PER_MINUTE;
  const bins = new Map<number, number>();
  for (const d of durationsSteps) {
    const binStart = Math.floor(d / stepsPerBin) * stepsPerBin;
    const binMin = Math.round(binStart / STEPS_PER_MINUTE);
    bins.set(binMin, (bins.get(binMin) ?? 0) + 1);
  }
  return bins;
}

function contactProbabilityFromDurations(
  loops: Loop[],
  totalSteps: number,
  numRuns: number,
): number {
  const totalStepSeconds = totalSteps * numRuns;
  let contactTime = 0;
  for (const loop of loops) {
    const dur = getLoopDurationSteps(loop);
    if (dur != null) contactTime += dur;
  }
  return totalStepSeconds > 0 ? contactTime / totalStepSeconds : 0;
}

function main() {
  console.log("Blind-test validation: Sabaté et al. 2024 (bioRxiv)");
  console.log(`Locus: ${locusKey} (${SELECTED_SITES.length} CTCF sites)`);
  console.log(
    `Parameters: v=${SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP} bp/step, T_res=${SABATE_NATURE_2025.MEAN_RESIDENCE_STEPS} steps, loading=1/3600, 1 step=1 s`,
  );
  console.log(
    `Running ${NUM_RUNS} independent simulations (${STEPS_PER_RUN} steps each)...\n`,
  );

  const allDurationsSteps: number[] = [];
  let totalLoopsWithDuration = 0;
  let contactTimeSum = 0;

  const log = console.log;
  console.log = () => {}; // suppress engine logs during batch

  for (let i = 0; i < NUM_RUNS; i++) {
    const loops = runSingleSimulation(i + BASE_SEED);
    for (const loop of loops) {
      const dur = getLoopDurationSteps(loop);
      if (dur != null) {
        allDurationsSteps.push(dur);
        totalLoopsWithDuration++;
        contactTimeSum += dur;
      }
    }
    if ((i + 1) % 100 === 0) {
      console.log = log;
      log(
        `  Run ${i + 1}/${NUM_RUNS} — loops with duration so far: ${allDurationsSteps.length}`,
      );
      console.log = () => {};
    }
  }

  console.log = log;
  console.log(
    `\nTotal loops with dissolved duration: ${totalLoopsWithDuration}`,
  );

  const stats = computeStats(allDurationsSteps);
  const meanMin = stats.mean / STEPS_PER_MINUTE;
  const stdMin = stats.std / STEPS_PER_MINUTE;
  const ci95LowerMin = stats.ci95Lower / STEPS_PER_MINUTE;
  const ci95UpperMin = stats.ci95Upper / STEPS_PER_MINUTE;

  const totalStepSeconds = STEPS_PER_RUN * NUM_RUNS;
  const contactProb =
    totalStepSeconds > 0 ? contactTimeSum / totalStepSeconds : 0;

  const targetMin =
    SABATE_NATURE_2025.LOOP_DURATION_TARGET_MIN_STEPS / STEPS_PER_MINUTE;
  const targetMax =
    SABATE_NATURE_2025.LOOP_DURATION_TARGET_MAX_STEPS / STEPS_PER_MINUTE;
  const inRange = meanMin >= targetMin && meanMin <= targetMax;
  const verdict = inRange ? "PASS" : "FAIL";

  // ASCII histogram (bins by 2 min)
  const hist = histogram(allDurationsSteps, 2);
  const histMinutes = [...hist.keys()].sort((a, b) => a - b);
  const maxCount = Math.max(...hist.values(), 1);

  let report = `# Blind-test validation: Sabaté et al. 2024 (bioRxiv)

## Methodology

- **Source:** Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)
- **Time mapping:** 1 simulation step = 1 second
- **Cohesin speed (v):** 0.3 kb/s → 300 bp/step
- **Residence time (T_res):** ${(SABATE_NATURE_2025.MEAN_RESIDENCE_STEPS / 60).toFixed(2)} min = ${SABATE_NATURE_2025.MEAN_RESIDENCE_STEPS} steps → unloading probability = ${SABATE_NATURE_2025.UNLOADING_PROBABILITY} (calibrated within literature 10–30 min)
- **Loading:** ~1 event per hour per TAD → loading probability = 1/3600 per step
- **Locus:** ${locusKey} (${locusKey === "SOX2" ? "chr3" : "chr11"}), ${SELECTED_SITES.length} CTCF sites
- **Runs:** ${NUM_RUNS} independent simulations, ${STEPS_PER_RUN} steps each (${(STEPS_PER_RUN / 3600).toFixed(1)} h model time per run)

## Results

### Loop duration (steps → minutes)

| Metric | Steps | Minutes |
|--------|-------|---------|
| Mean   | ${stats.mean.toFixed(1)} | ${meanMin.toFixed(2)} |
| Std    | ${stats.std.toFixed(1)} | ${stdMin.toFixed(2)} |
| 95% CI | [${stats.ci95Lower.toFixed(0)}, ${stats.ci95Upper.toFixed(0)}] | [${ci95LowerMin.toFixed(2)}, ${ci95UpperMin.toFixed(2)}] |
| N (loops with duration) | ${stats.n} | — |

### Contact probability (anchor pairs)

Fraction of simulation time with a stable loop (any anchor pair): **${(contactProb * 100).toFixed(4)}%**

### Distribution (duration in minutes, bin width 2 min)

\`\`\`
`;

  for (const m of histMinutes) {
    const count = hist.get(m)!;
    const barLen = Math.round((count / maxCount) * 40);
    const bar = "█".repeat(barLen);
    report += `${String(m).padStart(4)} min | ${bar} ${count}\n`;
  }

  report += `\`\`\`

### Experimental target

Loop duration in vivo (Sabaté et al., 2024, bioRxiv): **6–19 minutes** (360–1140 steps).

## Verdict

**${verdict}** — Mean loop duration in simulation: **${meanMin.toFixed(2)} min** (95% CI: [${ci95LowerMin.toFixed(2)}, ${ci95UpperMin.toFixed(2)}] min).

${
  inRange
    ? "✅ Mean falls within the experimental range 6–19 min. The model reproduces loop kinetics without fitting."
    : "❌ Mean falls outside 6–19 min. Review parameters or time mapping."
}
`;

  const outPath = path.join(
    __dirname,
    "..",
    "results",
    "blind_test_validation_2025.md",
  );
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, report, "utf8");

  console.log("\n--- Summary ---");
  console.log(
    `Mean loop duration: ${meanMin.toFixed(2)} min (target 6–19 min)`,
  );
  console.log(
    `95% CI: [${ci95LowerMin.toFixed(2)}, ${ci95UpperMin.toFixed(2)}] min`,
  );
  console.log(`Contact probability: ${(contactProb * 100).toFixed(4)}%`);
  console.log(`Verdict: ${verdict}`);
  console.log(`Report written to ${outPath}`);
}

main();
