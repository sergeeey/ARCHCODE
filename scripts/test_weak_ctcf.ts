/**
 * Isolated weak-CTCF experiment for Task 3.
 *
 * Compares barrier readthrough in three scenarios:
 * 1) baseline
 * 2) weak_halved (only weak sites: strength < 0.85 -> 0.5)
 * 3) strong_control (only strong sites: strength >= 0.85 -> 0.5)
 *
 * Run:
 *   npx tsx scripts/test_weak_ctcf.ts --runs=200 --steps=36000
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { parseArgs } from "util";

import { createCTCFSite } from "../src/domain/models/genome";
import { SABATE_NATURE_2025 } from "../src/domain/constants/biophysics";
import {
  BarrierStatsSnapshot,
  MultiCohesinEngine,
} from "../src/engines/MultiCohesinEngine";

type SiteDef = { pos: number; strength: number; orient: "F" | "R" };

type ScenarioName = "baseline" | "weak_halved" | "strong_control";
type LocusPreset = "hbb" | "weak_probe";

interface ScenarioResult {
  name: ScenarioName;
  runs: number;
  stepsPerRun: number;
  weakThreshold: number;
  weakEncounter: number;
  weakBlocked: number;
  weakReadthrough: number;
  strongEncounter: number;
  strongBlocked: number;
  strongReadthrough: number;
  weakReadthroughRate: number;
  strongReadthroughRate: number;
  weakReadthroughCi95: [number, number] | null;
  strongReadthroughCi95: [number, number] | null;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const HBB_SITES: SiteDef[] = [
  { pos: 25000, strength: 0.9, orient: "F" },
  { pos: 30000, strength: 0.85, orient: "R" },
  { pos: 45000, strength: 0.8, orient: "F" },
  { pos: 55000, strength: 0.9, orient: "R" },
  { pos: 75000, strength: 0.85, orient: "F" },
  { pos: 90000, strength: 0.9, orient: "R" },
];

// Purpose-built preset for Task 3 isolation:
// central R...F weak convergent pair guarantees weak barrier encounters.
const WEAK_PROBE_SITES: SiteDef[] = [
  { pos: 25000, strength: 0.95, orient: "R" },
  { pos: 45000, strength: 0.72, orient: "R" },
  { pos: 55000, strength: 0.72, orient: "F" },
  { pos: 75000, strength: 0.95, orient: "F" },
];

const GENOME_LENGTH = 100_000;
const WEAK_THRESHOLD = 0.85;
const TARGET_WEAK_STRENGTH = 0.5;
const STEPS_PER_MINUTE = 60;

const args = parseArgs({
  options: {
    runs: { type: "string", default: "200" },
    steps: { type: "string", default: "36000" },
    seedOffset: { type: "string", default: "0" },
    locusPreset: { type: "string", default: "hbb" },
    out: { type: "string" },
  },
});

const NUM_RUNS = Number(args.values.runs ?? 200);
const STEPS_PER_RUN = Number(args.values.steps ?? 36000);
const SEED_OFFSET = Number(args.values.seedOffset ?? 0);
const LOCUS_PRESET = ((args.values.locusPreset ?? "hbb").toLowerCase() ===
"weak_probe"
  ? "weak_probe"
  : "hbb") as LocusPreset;

function getSitesForPreset(preset: LocusPreset): SiteDef[] {
  return preset === "weak_probe" ? WEAK_PROBE_SITES : HBB_SITES;
}

function withScenarioStrengths(
  sites: SiteDef[],
  scenario: ScenarioName,
): SiteDef[] {
  if (scenario === "baseline") return sites.map((s) => ({ ...s }));
  if (scenario === "weak_halved") {
    return sites.map((s) =>
      s.strength < WEAK_THRESHOLD
        ? { ...s, strength: TARGET_WEAK_STRENGTH }
        : { ...s },
    );
  }
  return sites.map((s) =>
    s.strength >= WEAK_THRESHOLD
      ? { ...s, strength: TARGET_WEAK_STRENGTH }
      : { ...s },
  );
}

function rate(numerator: number, denominator: number): number {
  return denominator > 0 ? numerator / denominator : 0;
}

function ci95Binomial(p: number, n: number): [number, number] | null {
  if (n <= 0) return null;
  const se = Math.sqrt((p * (1 - p)) / n);
  const z = 1.96;
  return [Math.max(0, p - z * se), Math.min(1, p + z * se)];
}

function runOneScenario(name: ScenarioName): ScenarioResult {
  const baseSites = getSitesForPreset(LOCUS_PRESET);
  const sites = withScenarioStrengths(baseSites, name);

  const totals: BarrierStatsSnapshot = {
    weakThreshold: WEAK_THRESHOLD,
    weakEncounter: 0,
    weakBlocked: 0,
    weakReadthrough: 0,
    strongEncounter: 0,
    strongBlocked: 0,
    strongReadthrough: 0,
  };

  const chrom = "chr11";
  const ctcfSites = sites.map((s) =>
    createCTCFSite(chrom, s.pos, s.orient, s.strength),
  );

  for (let i = 0; i < NUM_RUNS; i++) {
    const engine = new MultiCohesinEngine({
      genomeLength: GENOME_LENGTH,
      ctcfSites,
      velocity: SABATE_NATURE_2025.EXTRUSION_SPEED_BP_PER_STEP,
      unloadingProbability: SABATE_NATURE_2025.UNLOADING_PROBABILITY,
      loadingProbabilityPerStep: SABATE_NATURE_2025.LOADING_PROBABILITY_PER_STEP,
      seed: SEED_OFFSET + i,
      maxSteps: STEPS_PER_RUN,
      verbose: false,
      barrierStats: { enabled: true, weakThreshold: WEAK_THRESHOLD },
    });
    engine.run(STEPS_PER_RUN);
    const stats = engine.getBarrierStats();
    totals.weakEncounter += stats.weakEncounter;
    totals.weakBlocked += stats.weakBlocked;
    totals.weakReadthrough += stats.weakReadthrough;
    totals.strongEncounter += stats.strongEncounter;
    totals.strongBlocked += stats.strongBlocked;
    totals.strongReadthrough += stats.strongReadthrough;
  }

  const weakRate = rate(totals.weakReadthrough, totals.weakEncounter);
  const strongRate = rate(totals.strongReadthrough, totals.strongEncounter);

  return {
    name,
    runs: NUM_RUNS,
    stepsPerRun: STEPS_PER_RUN,
    weakThreshold: WEAK_THRESHOLD,
    weakEncounter: totals.weakEncounter,
    weakBlocked: totals.weakBlocked,
    weakReadthrough: totals.weakReadthrough,
    strongEncounter: totals.strongEncounter,
    strongBlocked: totals.strongBlocked,
    strongReadthrough: totals.strongReadthrough,
    weakReadthroughRate: weakRate,
    strongReadthroughRate: strongRate,
    weakReadthroughCi95: ci95Binomial(weakRate, totals.weakEncounter),
    strongReadthroughCi95: ci95Binomial(strongRate, totals.strongEncounter),
  };
}

function diff(a: number, b: number): number {
  return a - b;
}

function main() {
  const baseline = runOneScenario("baseline");
  const weakHalved = runOneScenario("weak_halved");
  const strongControl = runOneScenario("strong_control");

  const weakDelta = diff(
    weakHalved.weakReadthroughRate,
    baseline.weakReadthroughRate,
  );
  const strongDelta = diff(
    strongControl.strongReadthroughRate,
    baseline.strongReadthroughRate,
  );

  const noEffectThreshold = 0.02; // 2 percentage points absolute delta
  const hasWeakEvents =
    baseline.weakEncounter > 0 && weakHalved.weakEncounter > 0;
  const weakNoEffectObserved =
    hasWeakEvents && Math.abs(weakDelta) <= noEffectThreshold;
  const verdict =
    hasWeakEvents
      ? weakNoEffectObserved
        ? "SUPPORTED_IN_MODEL"
        : "NEEDS_FIXES"
      : "NO_GO_NO_WEAK_EVENTS";
  const goNoGo = hasWeakEvents ? "GO" : "NO_GO";
  const noGoReason = hasWeakEvents
    ? null
    : "weakEncounter=0 in baseline and/or perturbation; ablation cannot be interpreted";
  const dateStamp = new Date().toISOString().slice(0, 10);

  const report = {
    generated_at_utc: new Date().toISOString(),
    task: "Task3_Weak_CTCF_Isolated",
    provenance: "SIMULATION",
    configuration: {
      locus: LOCUS_PRESET.toUpperCase(),
      locusPreset: LOCUS_PRESET,
      genomeLength: GENOME_LENGTH,
      runs: NUM_RUNS,
      stepsPerRun: STEPS_PER_RUN,
      modelTimePerRunMin: Number((STEPS_PER_RUN / STEPS_PER_MINUTE).toFixed(2)),
      weakThreshold: WEAK_THRESHOLD,
      targetWeakStrength: TARGET_WEAK_STRENGTH,
      seedOffset: SEED_OFFSET,
    },
    scenarios: {
      baseline,
      weak_halved: weakHalved,
      strong_control: strongControl,
    },
    comparisons: {
      weakReadthroughRateDelta_vs_baseline: weakDelta,
      strongReadthroughRateDelta_vs_baseline: strongDelta,
      noEffectThresholdAbs: noEffectThreshold,
      hasWeakEvents,
      weakNoEffectObserved,
      goNoGo,
      noGoReason,
    },
    verdict,
    note: "This is an in-model isolated perturbation. External biological validation remains required.",
  };

  const outputPath =
    args.values.out ??
    path.join(
      __dirname,
      "..",
      "results",
      `task3_weak_ctcf_isolated_${dateStamp}.json`,
    );

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2), "utf8");

  console.log("Task3 weak-CTCF isolated experiment complete");
  console.log(`Output: ${outputPath}`);
  console.log(
    `weak delta vs baseline: ${(weakDelta * 100).toFixed(2)} pp | verdict: ${verdict}`,
  );
}

main();
