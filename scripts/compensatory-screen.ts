/**
 * ARCHCODE In Silico CRISPR Compensatory Screen — HBB Locus
 * ==========================================================
 * Therapeutic concept: if a pearl variant disrupts the 3D contact map,
 * and deleting a specific regulatory element (CTCF site or enhancer)
 * RESTORES the contact map toward wild-type, that element is a candidate
 * therapeutic target for CRISPR-based editing.
 *
 * Logic:
 *   1. Simulate WT contact map.
 *   2. Apply pearl variant → SSIM_single (damage baseline).
 *   3. For each regulatory element, simulate pearl + deletion → SSIM_double.
 *   4. Recovery = SSIM_double − SSIM_single.
 *      Positive recovery = deletion partially compensates the variant's damage.
 *
 * Biological rationale: aberrant structural contacts formed by pathogenic
 * variants may depend on specific CTCF insulators or active enhancers.
 * Removing the enabling element can dissipate the ectopic loop.
 * This mirrors the logic behind therapeutic enhancer silencing (e.g.
 * BCL11A erythroid enhancer deletion to reactivate fetal HBB expression).
 *
 * Usage: npx tsx scripts/compensatory-screen.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus config (identical to fragility-atlas.ts) ───────────────────────────

const SIM_START = 5_210_000;
const SIM_END = 5_305_000; // 95 kb sub-TAD window
const RESOLUTION = 600; // bp per bin
const N_BINS = Math.ceil((SIM_END - SIM_START) / RESOLUTION);

// Named regulatory elements with indices for deletion bookkeeping
interface Enhancer {
  position: number;
  occupancy: number;
  name: string;
}

interface CtcfSite {
  position: number;
  orientation: "+" | "-";
  name: string; // added for output readability
}

const ENHANCERS: Enhancer[] = [
  { position: 5_227_000, occupancy: 0.85, name: "HBB_promoter_enh" },
  { position: 5_225_500, occupancy: 0.75, name: "3prime_HS1" },
  { position: 5_230_000, occupancy: 0.70, name: "LCR_HS2_proximal" },
  { position: 5_233_000, occupancy: 0.65, name: "LCR_HS3_proximal" },
  { position: 5_220_000, occupancy: 0.50, name: "downstream_enhancer" },
  { position: 5_246_696, occupancy: 0.60, name: "HS2_core" },
  { position: 5_248_029, occupancy: 0.55, name: "HS3_region" },
  { position: 5_255_870, occupancy: 0.50, name: "HS4_region" },
];

const CTCF_SITES: CtcfSite[] = [
  { position: 5_212_000, orientation: "+", name: "CTCF_5212k" },
  { position: 5_218_000, orientation: "-", name: "CTCF_5218k" },
  { position: 5_224_000, orientation: "+", name: "CTCF_5224k" },
  { position: 5_228_000, orientation: "-", name: "CTCF_5228k_proximal" }, // closest to HBB TSS
  { position: 5_232_000, orientation: "+", name: "CTCF_5232k" },
  { position: 5_236_000, orientation: "-", name: "CTCF_5236k" },
  { position: 5_248_029, orientation: "+", name: "CTCF_5248k_HS3" },
  { position: 5_257_994, orientation: "-", name: "CTCF_5258k" },
  { position: 5_291_200, orientation: "+", name: "CTCF_5291k" },
  { position: 5_302_700, orientation: "-", name: "CTCF_5303k_boundary" },
];

// ── Pearl variant definitions (from prior analysis + task spec) ───────────────
// ПОЧЕМУ: используем representative positions из task spec, но корректируем
// на реальные координаты из pearl_validation_shortlist.json где они доступны.
// Эффект (effect) = occupancy retention при варианте (0.1 = severe, 0.5 = moderate).

interface PearlVariant {
  position: number;
  name: string;
  effect: number; // occupancy retention factor (lower = more damaging)
  category: "promoter" | "missense" | "frameshift" | "splice";
}

const PEARL_VARIANTS: PearlVariant[] = [
  { position: 5_226_774, name: "c.-79A>C", effect: 0.3, category: "promoter" },
  { position: 5_226_775, name: "c.-80T>C", effect: 0.3, category: "promoter" },
  { position: 5_226_857, name: "c.-138C>A", effect: 0.3, category: "promoter" },
  { position: 5_226_933, name: "c.20A>T", effect: 0.3, category: "missense" },
  { position: 5_227_002, name: "c.50dup", effect: 0.1, category: "frameshift" },
  { position: 5_227_055, name: "c.93-1G>A", effect: 0.2, category: "splice" },
  { position: 5_227_166, name: "c.118C>T", effect: 0.5, category: "missense" },
  { position: 5_226_796, name: "IVS-II-1", effect: 0.2, category: "splice" },
  { position: 5_225_600, name: "c.249G>C", effect: 0.5, category: "missense" },
  { position: 5_225_300, name: "c.315+1G>A", effect: 0.2, category: "splice" },
];

// ── Regulatory element union type for the screen ─────────────────────────────

type ElementType = "CTCF" | "Enhancer";

interface RegulatoryElement {
  type: ElementType;
  position: number;
  name: string;
  index: number; // index in ENHANCERS[] or CTCF_SITES[]
}

// Build unified list of targets for the screen
const ALL_TARGETS: RegulatoryElement[] = [
  ...CTCF_SITES.map((c, i) => ({
    type: "CTCF" as ElementType,
    position: c.position,
    name: c.name,
    index: i,
  })),
  ...ENHANCERS.map((e, i) => ({
    type: "Enhancer" as ElementType,
    position: e.position,
    name: e.name,
    index: i,
  })),
];

// ── Simulation engine ─────────────────────────────────────────────────────────

/**
 * Строит occupancy landscape (плотность кохезина) для локуса.
 * Принимает опциональный excludedEnhancerIdx: если задан, соответствующий
 * энхансер исключается (occupancy = 0 для этой позиции).
 */
function buildOccupancyLandscape(
  seed: number,
  excludedEnhancerIdx: number | null = null,
): number[] {
  const rng = new SeededRandom(seed);
  const landscape: number[] = [];

  // ПОЧЕМУ: строим активные энхансеры заранее, чтобы не проверять
  // индекс внутри hot-path вложенного цикла.
  const activeEnhancers = ENHANCERS.filter((_, i) => i !== excludedEnhancerIdx);

  for (let i = 0; i < N_BINS; i++) {
    const genomicPos = SIM_START + i * RESOLUTION;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;

    for (const enh of activeEnhancers) {
      const dist = Math.abs(genomicPos - enh.position) / RESOLUTION;
      if (dist < 5) {
        // Gaussian decay within 5 bins (~3 kb)
        occ += enh.occupancy * Math.exp(-0.5 * dist * dist);
      }
    }
    landscape.push(Math.min(1, occ));
  }
  return landscape;
}

/**
 * Симулирует пару матриц (WT + мутант) для заданного варианта.
 *
 * Параметры:
 *   baseLandscape     — occupancy landscape (уже учитывает удаление энхансера)
 *   variantBin        — bin варианта (−1 = WT без варианта)
 *   effectStrength    — сила варианта (retention factor)
 *   excludedCtcfIdx   — индекс CTCF-сайта для удаления (null = все сохраняем)
 *
 * ПОЧЕМУ variantBin = -1 даёт WT: в этом случае цикл dist < 3 никогда
 * не срабатывает (dist от -1 до любого i всегда >= 1 → reduction = 1.0),
 * что эквивалентно отсутствию варианта.
 */
function simulatePairedMatrices(
  baseLandscape: number[],
  variantBin: number,
  effectStrength: number,
  excludedCtcfIdx: number | null = null,
): { reference: number[][]; mutant: number[][] } {
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  // WT occupancy = landscape as-is (no variant perturbation)
  const refOccupancy = [...baseLandscape];

  // Mutant occupancy = variant suppresses occupancy in ~3-bin neighborhood
  const mutOccupancy = baseLandscape.map((occ, i) => {
    if (variantBin >= 0) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        // ПОЧЕМУ линейная интерполяция: variant full effect at center,
        // falling off to zero effect at boundary (dist = 3)
        const retention = effectStrength + (1 - effectStrength) * (dist / 3);
        return occ * retention;
      }
    }
    return occ;
  });

  // Build active CTCF bin lists (exclude deleted site if requested)
  const allCtcfBins = CTCF_SITES.map((c) =>
    Math.floor((c.position - SIM_START) / RESOLUTION),
  ).filter((b) => b >= 0 && b < N_BINS);

  // ПОЧЕМУ: при удалении CTCF убираем конкретный сайт по индексу,
  // а не по proximity к variantBin (как в fragility-atlas.ts).
  // Это даёт точечное удаление для терапевтического скрининга.
  const activeCtcfBins =
    excludedCtcfIdx !== null
      ? allCtcfBins.filter((_, i) => i !== excludedCtcfIdx)
      : allCtcfBins;

  // Allocate contact matrices
  const refMatrix: number[][] = Array.from({ length: N_BINS }, () =>
    Array(N_BINS).fill(0),
  );
  const mutMatrix: number[][] = Array.from({ length: N_BINS }, () =>
    Array(N_BINS).fill(0),
  );

  // Fill upper triangle, then mirror — identical physics to fragility-atlas.ts
  for (let i = 0; i < N_BINS; i++) {
    for (let j = i + 1; j < N_BINS; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0); // polymer contact decay

      const refOccFactor = Math.sqrt(refOccupancy[i] * refOccupancy[j]);
      const mutOccFactor = Math.sqrt(mutOccupancy[i] * mutOccupancy[j]);

      // CTCF barrier effect: each CTCF between i and j reduces permeability by 85%
      let refPerm = 1.0;
      let mutPerm = 1.0;
      for (const ctcf of activeCtcfBins) {
        if (ctcf > i && ctcf < j) {
          refPerm *= 0.15;
          mutPerm *= 0.15;
        }
      }

      // Kramer escape rate modulation
      const refKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, refOccFactor), DEFAULT_GAMMA));
      const mutKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, mutOccFactor), DEFAULT_GAMMA));

      refMatrix[i][j] = distFactor * refOccFactor * refPerm * refKramer;
      refMatrix[j][i] = refMatrix[i][j];
      mutMatrix[i][j] = distFactor * mutOccFactor * mutPerm * mutKramer;
      mutMatrix[j][i] = mutMatrix[i][j];
    }
  }

  // Joint normalization — same WT reference scale for ref and mutant
  let maxVal = 0;
  for (let i = 0; i < N_BINS; i++) {
    for (let j = 0; j < N_BINS; j++) {
      if (refMatrix[i][j] > maxVal) maxVal = refMatrix[i][j];
      if (mutMatrix[i][j] > maxVal) maxVal = mutMatrix[i][j];
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < N_BINS; i++) {
      for (let j = 0; j < N_BINS; j++) {
        refMatrix[i][j] /= maxVal;
        mutMatrix[i][j] /= maxVal;
      }
    }
  }

  return { reference: refMatrix, mutant: mutMatrix };
}

/**
 * Структурное сходство (SSIM) между двумя контактными матрицами.
 * SSIM = 1.0 → идентичны, SSIM → 0 → полное разрушение структуры.
 */
function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat();
  const flatB = b.flat();
  const n = flatA.length;

  const muA = flatA.reduce((s, v) => s + v, 0) / n;
  const muB = flatB.reduce((s, v) => s + v, 0) / n;

  let sigmaA2 = 0;
  let sigmaB2 = 0;
  let sigmaAB = 0;
  for (let i = 0; i < n; i++) {
    sigmaA2 += (flatA[i] - muA) ** 2;
    sigmaB2 += (flatB[i] - muB) ** 2;
    sigmaAB += (flatA[i] - muA) * (flatB[i] - muB);
  }
  sigmaA2 /= n;
  sigmaB2 /= n;
  sigmaAB /= n;

  // Standard stabilizing constants (C1, C2) from Wang et al. 2004
  const c1 = 0.0001;
  const c2 = 0.0009;
  return (
    ((2 * muA * muB + c1) * (2 * sigmaAB + c2)) /
    ((muA ** 2 + muB ** 2 + c1) * (sigmaA2 + sigmaB2 + c2))
  );
}

// ── Result types ──────────────────────────────────────────────────────────────

interface ScreenRow {
  pearl_variant: string;
  pearl_position: number;
  pearl_category: string;
  target_element: string;
  target_type: ElementType;
  target_position: number;
  ssim_pearl_only: number;
  ssim_pearl_plus_deletion: number;
  recovery: number; // SSIM_double − SSIM_single (positive = compensatory)
  recovery_pct: number; // recovery / (1 − SSIM_single) × 100
}

// ── Main screen ───────────────────────────────────────────────────────────────

function main(): void {
  console.log("=".repeat(72));
  console.log("ARCHCODE In Silico CRISPR Compensatory Screen — HBB 95 kb");
  console.log("=".repeat(72));
  console.log(`Window:      chr11:${SIM_START.toLocaleString()}-${SIM_END.toLocaleString()} (${(SIM_END - SIM_START) / 1000} kb)`);
  console.log(`Resolution:  ${RESOLUTION} bp → ${N_BINS} bins`);
  console.log(`Pearl variants:      ${PEARL_VARIANTS.length}`);
  console.log(`Regulatory targets:  ${ALL_TARGETS.length} (${CTCF_SITES.length} CTCF + ${ENHANCERS.length} enhancers)`);
  console.log(`Total simulations:   ${PEARL_VARIANTS.length * (1 + ALL_TARGETS.length)} (single + double mutants per pearl)`);
  console.log();

  const results: ScreenRow[] = [];

  // ПОЧЕМУ seed=42: воспроизводимость + согласованность с fragility-atlas.ts.
  // Base WT landscape (no deletions) — shared anchor for WT SSIM reference.
  const wtLandscape = buildOccupancyLandscape(42);

  // Pre-compute WT contact matrix once — all SSIMs compare against this.
  // variantBin = -1 means "no variant" (see simulatePairedMatrices docs above).
  const { reference: wtMatrix } = simulatePairedMatrices(wtLandscape, -1, 1.0);

  let simCount = 0;
  const totalSims = PEARL_VARIANTS.length * (1 + ALL_TARGETS.length);

  for (const pearl of PEARL_VARIANTS) {
    const variantBin = Math.floor((pearl.position - SIM_START) / RESOLUTION);

    // ── Step A: pearl-only (single mutant vs WT) ──────────────────────────
    // ПОЧЕМУ: используем WT landscape (без делеций), мутируем только вариант.
    const { mutant: singleMutant } = simulatePairedMatrices(
      wtLandscape,
      variantBin,
      pearl.effect,
    );
    const ssimSingle = calculateSSIM(wtMatrix, singleMutant);
    const damage = 1 - ssimSingle; // how much the pearl disrupts structure

    simCount++;
    process.stdout.write(
      `\r  [${simCount}/${totalSims}] ${pearl.name.padEnd(14)} — single SSIM=${ssimSingle.toFixed(4)}`,
    );

    // ── Step B: double mutants (pearl + each regulatory deletion) ─────────
    for (const target of ALL_TARGETS) {
      let doubleMutantMatrix: number[][];

      if (target.type === "CTCF") {
        // CTCF deletion: remove the barrier; landscape unchanged
        const { mutant } = simulatePairedMatrices(
          wtLandscape,
          variantBin,
          pearl.effect,
          target.index, // excludedCtcfIdx
        );
        doubleMutantMatrix = mutant;
      } else {
        // Enhancer deletion: rebuild landscape without this enhancer
        const delLandscape = buildOccupancyLandscape(42, target.index);
        const { mutant } = simulatePairedMatrices(
          delLandscape,
          variantBin,
          pearl.effect,
          null,
        );
        doubleMutantMatrix = mutant;
      }

      const ssimDouble = calculateSSIM(wtMatrix, doubleMutantMatrix);

      // Recovery: positive = deletion helps restore WT structure
      const recovery = ssimDouble - ssimSingle;
      // Recovery as fraction of total damage (avoids division-by-zero for undamaged variants)
      const recoveryPct =
        damage > 0.0001 ? (recovery / damage) * 100 : 0;

      results.push({
        pearl_variant: pearl.name,
        pearl_position: pearl.position,
        pearl_category: pearl.category,
        target_element: target.name,
        target_type: target.type,
        target_position: target.position,
        ssim_pearl_only: Math.round(ssimSingle * 1e6) / 1e6,
        ssim_pearl_plus_deletion: Math.round(ssimDouble * 1e6) / 1e6,
        recovery: Math.round(recovery * 1e6) / 1e6,
        recovery_pct: Math.round(recoveryPct * 100) / 100,
      });

      simCount++;
    }
  }

  console.log(`\n  Done — ${simCount} simulations completed.\n`);

  // ── Save CSV ──────────────────────────────────────────────────────────────
  const csvPath = path.join(
    process.cwd(),
    "analysis",
    "compensatory_screen_hbb.csv",
  );
  const csvHeader = [
    "Pearl_Variant",
    "Pearl_Position",
    "Pearl_Category",
    "Target_Element",
    "Target_Type",
    "Target_Position",
    "SSIM_Pearl_Only",
    "SSIM_Pearl_Plus_Deletion",
    "Recovery",
    "Recovery_Pct",
  ].join(",");

  const csvRows = results.map((r) =>
    [
      r.pearl_variant,
      r.pearl_position,
      r.pearl_category,
      r.target_element,
      r.target_type,
      r.target_position,
      r.ssim_pearl_only,
      r.ssim_pearl_plus_deletion,
      r.recovery,
      r.recovery_pct,
    ].join(","),
  );
  fs.writeFileSync(csvPath, [csvHeader, ...csvRows].join("\n"));
  console.log(`Saved CSV:  ${csvPath} (${results.length} rows)`);

  // ── Compute mean recovery per target across all pearls ───────────────────
  // ПОЧЕМУ: терапевтическая ценность элемента определяется его способностью
  // компенсировать РАЗНЫЕ варианты, а не только один. Берём mean(recovery)
  // как надёжную агрегатную меру.

  type TargetSummary = {
    target_element: string;
    target_type: ElementType;
    target_position: number;
    mean_recovery: number;
    mean_recovery_pct: number;
    max_recovery: number;
    n_compensatory: number; // # pearls where recovery > 0
    compensatory_variants: string[];
  };

  const targetMap = new Map<string, TargetSummary>();

  for (const target of ALL_TARGETS) {
    const targetRows = results.filter(
      (r) => r.target_element === target.name,
    );
    const recoveries = targetRows.map((r) => r.recovery);
    const recoveryPcts = targetRows.map((r) => r.recovery_pct);
    const compensatory = targetRows.filter((r) => r.recovery > 0);

    const meanRecovery =
      recoveries.reduce((a, b) => a + b, 0) / recoveries.length;
    const meanRecoveryPct =
      recoveryPcts.reduce((a, b) => a + b, 0) / recoveryPcts.length;
    const maxRecovery = Math.max(...recoveries);

    targetMap.set(target.name, {
      target_element: target.name,
      target_type: target.type,
      target_position: target.position,
      mean_recovery: Math.round(meanRecovery * 1e6) / 1e6,
      mean_recovery_pct: Math.round(meanRecoveryPct * 100) / 100,
      max_recovery: Math.round(maxRecovery * 1e6) / 1e6,
      n_compensatory: compensatory.length,
      compensatory_variants: compensatory.map((r) => r.pearl_variant),
    });
  }

  // Sort by mean_recovery descending
  const rankedTargets = [...targetMap.values()].sort(
    (a, b) => b.mean_recovery - a.mean_recovery,
  );

  // ── Save JSON summary ─────────────────────────────────────────────────────
  const jsonPath = path.join(
    process.cwd(),
    "analysis",
    "compensatory_screen_summary.json",
  );

  const summary = {
    analysis: "ARCHCODE In Silico CRISPR Compensatory Screen — HBB",
    version: "v1.0",
    date: new Date().toISOString().split("T")[0],
    locus: "HBB",
    window: `${SIM_START}-${SIM_END}`,
    resolution_bp: RESOLUTION,
    n_bins: N_BINS,
    n_pearl_variants: PEARL_VARIANTS.length,
    n_targets_screened: ALL_TARGETS.length,
    n_ctcf_targets: CTCF_SITES.length,
    n_enhancer_targets: ENHANCERS.length,
    total_simulations: simCount,
    pearl_variants: PEARL_VARIANTS.map((p) => ({
      name: p.name,
      position: p.position,
      category: p.category,
      effect: p.effect,
    })),
    top_therapeutic_targets: rankedTargets.slice(0, 10),
    all_targets_ranked: rankedTargets,
  };

  fs.writeFileSync(jsonPath, JSON.stringify(summary, null, 2));
  console.log(`Saved JSON: ${jsonPath}`);

  // ── Console summary table ─────────────────────────────────────────────────
  console.log("\n=== Top 10 Therapeutic Targets (ranked by mean recovery across all pearls) ===\n");
  console.log(
    "Rank  Element                Type       Position     MeanRecov  MaxRecov  N_Comp/10",
  );
  console.log("-".repeat(85));

  for (const [idx, t] of rankedTargets.slice(0, 10).entries()) {
    const recovSign = t.mean_recovery >= 0 ? "+" : "";
    console.log(
      `  ${String(idx + 1).padStart(2)}  ${t.target_element.padEnd(22)} ${t.target_type.padEnd(10)} ${String(t.target_position).padStart(10)}   ${recovSign}${t.mean_recovery.toFixed(5)}  ${t.max_recovery >= 0 ? "+" : ""}${t.max_recovery.toFixed(5)}  ${t.n_compensatory}/${PEARL_VARIANTS.length}`,
    );
  }

  // ── Per-pearl damage summary ──────────────────────────────────────────────
  console.log("\n=== Pearl Variant Damage (SSIM_single vs WT) ===\n");
  console.log("Variant         Category    SSIM_single  Damage    Best_Target");
  console.log("-".repeat(72));

  for (const pearl of PEARL_VARIANTS) {
    const pearlRows = results.filter((r) => r.pearl_variant === pearl.name);
    const ssimSingle = pearlRows[0]?.ssim_pearl_only ?? 0;
    const damage = 1 - ssimSingle;
    const bestRow = [...pearlRows].sort((a, b) => b.recovery - a.recovery)[0];
    console.log(
      `${pearl.name.padEnd(15)} ${pearl.category.padEnd(11)} ${ssimSingle.toFixed(6)}   ${damage.toFixed(6)}  ${bestRow?.target_element ?? "—"}`,
    );
  }

  // ── Biological interpretation ─────────────────────────────────────────────
  const topTarget = rankedTargets[0];
  const topCtcf = rankedTargets.find((t) => t.target_type === "CTCF");
  const topEnhancer = rankedTargets.find((t) => t.target_type === "Enhancer");

  console.log("\n=== Biological Interpretation ===\n");
  console.log(`Top overall target:  ${topTarget.target_element} (${topTarget.target_type})`);
  console.log(`  Mean recovery: ${topTarget.mean_recovery >= 0 ? "+" : ""}${topTarget.mean_recovery.toFixed(5)} SSIM units`);
  console.log(`  Compensates:   ${topTarget.n_compensatory}/${PEARL_VARIANTS.length} pearl variants`);

  if (topCtcf) {
    console.log(`\nTop CTCF target:     ${topCtcf.target_element} at chr11:${topCtcf.target_position.toLocaleString()}`);
    console.log(`  Recovery %: ${topCtcf.mean_recovery_pct.toFixed(1)}% of pearl damage restored`);
  }
  if (topEnhancer) {
    console.log(`\nTop Enhancer target: ${topEnhancer.target_element} at chr11:${topEnhancer.target_position.toLocaleString()}`);
    console.log(`  Recovery %: ${topEnhancer.mean_recovery_pct.toFixed(1)}% of pearl damage restored`);
  }

  console.log("\nNote: Positive recovery = deletion partially restores WT contact map.");
  console.log("      Negative recovery = deletion exacerbates structural damage.");
  console.log("      Top targets are candidates for CRISPR therapeutic intervention.\n");
}

main();
