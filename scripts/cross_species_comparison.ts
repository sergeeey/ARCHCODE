/**
 * ARCHCODE Cross-Species Comparison: Human HBB vs Mouse Hbb
 *
 * ПОЧЕМУ: если структурно патогенные позиции (pearls) консервированы между
 * человеком и мышью, это доказывает что ARCHCODE ловит реальный биологический
 * сигнал, а не артефакт конкретного конфига.
 *
 * Подход:
 * 1. Генерируем WT contact matrices для обоих видов
 * 2. Маппим pearl позиции human → mouse через относительные координаты
 *    (дистанция от TSS и LCR HS2, нормализованная на размер окна)
 * 3. Прогоняем ARCHCODE на mouse config с perturbation в ортологичных позициях
 * 4. Сравниваем LSSIM: conserved disruption → conserved structural pathogenicity
 *
 * Usage: npx tsx scripts/cross_species_comparison.ts
 */

import * as fs from "fs";
import * as path from "path";
import { SeededRandom } from "../src/utils/random";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import {
  loadLocusConfig,
  resolveLocusPath,
  getLocusFeatures,
  type LocusConfig,
} from "../src/domain/config/locus-config";

// ============================================================================
// Load both configs
// ============================================================================

const humanConfigPath = resolveLocusPath("95kb");
const mouseConfigPath = resolveLocusPath("mouse_hbb");
const humanConfig = loadLocusConfig(humanConfigPath);
const mouseConfig = loadLocusConfig(mouseConfigPath);
const humanFeatures = getLocusFeatures(humanConfig);
const mouseFeatures = getLocusFeatures(mouseConfig);

console.log("=== ARCHCODE Cross-Species Comparison ===");
console.log(`Human: ${humanConfig.id} (${humanConfig.window.start}-${humanConfig.window.end}, ${humanConfig.window.n_bins} bins)`);
console.log(`Mouse: ${mouseConfig.id} (${mouseConfig.window.start}-${mouseConfig.window.end}, ${mouseConfig.window.n_bins} bins)`);
console.log();

// ============================================================================
// Architectural landmarks for coordinate mapping
// ============================================================================

// Human landmarks (GRCh38, minus strand)
const HUMAN = {
  tss: 5227021,        // HBB TSS
  lcrHS2: 5280700,     // LCR HS2 (strongest enhancer)
  ctcf3prime: 5204979, // 3'HS1 CTCF
  ctcf5prime: 5291442, // HS5 CTCF
  simStart: humanConfig.window.start,
  simEnd: humanConfig.window.end,
  resolution: humanConfig.window.resolution_bp,
  nBins: humanConfig.window.n_bins,
};

// Mouse landmarks (mm10, minus strand)
const MOUSE = {
  tss: 103827928,       // Hbb-bs TSS
  lcrHS2: 103862207,    // LCR HS2 (strongest enhancer)
  ctcf3prime: 103793148, // 3'HS1 CTCF
  ctcf5prime: 103913187, // HS-85 CTCF
  simStart: mouseConfig.window.start,
  simEnd: mouseConfig.window.end,
  resolution: mouseConfig.window.resolution_bp,
  nBins: mouseConfig.window.n_bins,
};

console.log("Architectural landmarks:");
console.log(`  Human: TSS=${HUMAN.tss}, HS2=${HUMAN.lcrHS2}, 3'HS1=${HUMAN.ctcf3prime}, HS5=${HUMAN.ctcf5prime}`);
console.log(`  Mouse: TSS=${MOUSE.tss}, HS2=${MOUSE.lcrHS2}, 3'HS1=${MOUSE.ctcf3prime}, HS85=${MOUSE.ctcf5prime}`);
console.log(`  TSS-to-HS2 distance: human=${HUMAN.lcrHS2 - HUMAN.tss}bp, mouse=${MOUSE.lcrHS2 - MOUSE.tss}bp`);
console.log(`  3'HS1-to-HS5/85 span: human=${HUMAN.ctcf5prime - HUMAN.ctcf3prime}bp, mouse=${MOUSE.ctcf5prime - MOUSE.ctcf3prime}bp`);
console.log();

// ============================================================================
// Position mapping: human → mouse
// ============================================================================

function mapHumanToMouse(humanPos: number): {
  mousePos: number;
  method: string;
  relativePos: number;
} {
  // Method: TSS-relative mapping
  // Pearl variants cluster around HBB TSS (±500bp), so the most biologically
  // meaningful mapping preserves distance-from-TSS.
  //
  // Human HBB TSS = 5227021 → Mouse Hbb-bs TSS = 103827928
  // For positions near TSS: map directly (TSS-relative offset)
  // For positions near LCR: use LCR-relative offset (HS2 anchor)
  // For positions in between: linear interpolation TSS↔HS2

  const humanDistToTSS = humanPos - HUMAN.tss;
  const humanDistToHS2 = humanPos - HUMAN.lcrHS2;
  const humanTSStoHS2 = HUMAN.lcrHS2 - HUMAN.tss;
  const mouseTSStoHS2 = MOUSE.lcrHS2 - MOUSE.tss;

  let mousePos: number;
  let method: string;

  if (Math.abs(humanDistToTSS) < 2000) {
    // Near TSS: direct TSS-relative mapping (preserves gene-level position)
    mousePos = MOUSE.tss + humanDistToTSS;
    method = "tss_relative";
  } else if (Math.abs(humanDistToHS2) < 2000) {
    // Near LCR HS2: HS2-relative mapping
    mousePos = MOUSE.lcrHS2 + humanDistToHS2;
    method = "hs2_relative";
  } else {
    // In between: scale proportionally between TSS and HS2
    const relFraction = (humanPos - HUMAN.tss) / humanTSStoHS2;
    mousePos = Math.round(MOUSE.tss + relFraction * mouseTSStoHS2);
    method = "tss_hs2_interpolation";
  }

  const relativePos = (humanPos - HUMAN.ctcf3prime) / (HUMAN.ctcf5prime - HUMAN.ctcf3prime);
  return { mousePos, method, relativePos };
}

// ============================================================================
// Simulation engine (same as generate-unified-atlas.ts)
// ============================================================================

function simulateContactMatrix(
  config: LocusConfig,
  features: ReturnType<typeof getLocusFeatures>,
  variantBin: number = -1,
  effectStrength: number = 1.0,
  category: string = "other",
  seed: number = 42,
): number[][] {
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;
  const nBins = config.window.n_bins;
  const resolution = config.window.resolution_bp;
  const simStart = config.window.start;

  // Build MED1 occupancy landscape
  const occupancy: number[] = [];
  const rng = new SeededRandom(seed);
  for (let i = 0; i < nBins; i++) {
    const genomicPos = simStart + i * resolution;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;

    for (const enh of features.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / resolution;
      if (dist < 5) {
        occ += enh.occupancy * Math.exp(-0.5 * dist * dist);
      }
    }
    occupancy.push(Math.min(1, occ));
  }

  // Apply variant perturbation
  if (variantBin >= 0) {
    for (let i = 0; i < nBins; i++) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        const reduction = effectStrength + (1 - effectStrength) * (dist / 3);
        occupancy[i] *= reduction;
      }
    }
  }

  // CTCF barriers
  const ctcfBins = features.ctcfSites
    .map((c) => Math.floor((c.position - simStart) / resolution))
    .filter((b) => b >= 0 && b < nBins);

  const activeCTCF =
    category.includes("splice") || category.includes("promoter")
      ? ctcfBins.filter((b) => variantBin < 0 || Math.abs(b - variantBin) > 2)
      : ctcfBins;

  // Build contact matrix
  const matrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);
      const occFactor = Math.sqrt(occupancy[i] * occupancy[j]);

      let perm = 1.0;
      for (const ctcf of activeCTCF) {
        if (ctcf > i && ctcf < j) perm *= 0.15;
      }

      const kramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, occFactor), DEFAULT_GAMMA));

      matrix[i][j] = distFactor * occFactor * perm * kramer;
      matrix[j][i] = matrix[i][j];
    }
  }

  return matrix;
}

// ============================================================================
// SSIM calculation (same as ARCHCODE engine)
// ============================================================================

function computeSSIM(mat1: number[][], mat2: number[][]): number {
  const n = mat1.length;
  const values1: number[] = [];
  const values2: number[] = [];

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      values1.push(mat1[i][j]);
      values2.push(mat2[i][j]);
    }
  }

  const mean1 = values1.reduce((a, b) => a + b, 0) / values1.length;
  const mean2 = values2.reduce((a, b) => a + b, 0) / values2.length;

  let var1 = 0, var2 = 0, cov = 0;
  for (let i = 0; i < values1.length; i++) {
    const d1 = values1[i] - mean1;
    const d2 = values2[i] - mean2;
    var1 += d1 * d1;
    var2 += d2 * d2;
    cov += d1 * d2;
  }
  var1 /= values1.length;
  var2 /= values2.length;
  cov /= values1.length;

  const C1 = 0.0001;
  const C2 = 0.0003;

  return (
    ((2 * mean1 * mean2 + C1) * (2 * cov + C2)) /
    ((mean1 * mean1 + mean2 * mean2 + C1) * (var1 + var2 + C2))
  );
}

// Local SSIM (LSSIM) — average of window-based SSIM
function computeLSSIM(mat1: number[][], mat2: number[][], windowSize: number = 11): number {
  const n = mat1.length;
  const halfW = Math.floor(windowSize / 2);
  const ssimValues: number[] = [];

  for (let center = halfW; center < n - halfW; center++) {
    const start = center - halfW;
    const end = center + halfW + 1;
    const sub1: number[][] = [];
    const sub2: number[][] = [];

    for (let i = start; i < end; i++) {
      const row1: number[] = [];
      const row2: number[] = [];
      for (let j = start; j < end; j++) {
        row1.push(mat1[i][j]);
        row2.push(mat2[i][j]);
      }
      sub1.push(row1);
      sub2.push(row2);
    }

    ssimValues.push(computeSSIM(sub1, sub2));
  }

  return ssimValues.reduce((a, b) => a + b, 0) / ssimValues.length;
}

// ============================================================================
// Human pearl positions (from HBB_Unified_Atlas_95kb.csv)
// ============================================================================

interface PearlPosition {
  humanPos: number;
  category: string;
  hgvs: string;
  humanLSSIM: number;
}

function loadPearlPositions(): PearlPosition[] {
  const atlasPath = path.join(process.cwd(), "results", "HBB_Unified_Atlas_95kb.csv");
  const content = fs.readFileSync(atlasPath, "utf-8");
  const lines = content.trim().split("\n");
  const headers = lines[0].split(",").map(h => h.trim());

  const posIdx = headers.indexOf("Position_GRCh38");
  const catIdx = headers.indexOf("Category");
  const hgvsIdx = headers.indexOf("HGVS_c");
  const lssimIdx = headers.indexOf("ARCHCODE_LSSIM");
  const pearlIdx = headers.indexOf("Pearl");

  const seen = new Set<number>();
  const pearls: PearlPosition[] = [];

  for (let i = 1; i < lines.length; i++) {
    const vals = lines[i].split(",").map(v => v.trim());
    if (vals[pearlIdx] !== "True" && vals[pearlIdx] !== "true") continue;

    const pos = parseInt(vals[posIdx]);
    if (seen.has(pos)) continue;
    seen.add(pos);

    pearls.push({
      humanPos: pos,
      category: vals[catIdx],
      hgvs: vals[hgvsIdx],
      humanLSSIM: parseFloat(vals[lssimIdx]),
    });
  }

  return pearls.sort((a, b) => a.humanPos - b.humanPos);
}

// ============================================================================
// Main analysis
// ============================================================================

console.log("Phase 1: Generating WT contact matrices...");
const humanWT = simulateContactMatrix(humanConfig, humanFeatures);
const mouseWT = simulateContactMatrix(mouseConfig, mouseFeatures);
console.log(`  Human WT: ${humanWT.length}x${humanWT.length}`);
console.log(`  Mouse WT: ${mouseWT.length}x${mouseWT.length}`);
console.log();

console.log("Phase 2: Loading human pearl positions and mapping to mouse...");
const pearls = loadPearlPositions();
console.log(`  Loaded ${pearls.length} unique pearl positions`);
console.log();

// Run perturbations on both species
console.log("Phase 3: Running cross-species perturbation analysis...");
console.log();
console.log("Position mapping and LSSIM comparison:");
console.log("─".repeat(120));
console.log(
  "Human_Pos".padEnd(12) +
  "Mouse_Pos".padEnd(12) +
  "RelPos".padEnd(8) +
  "Category".padEnd(18) +
  "Human_LSSIM".padEnd(14) +
  "Mouse_LSSIM".padEnd(14) +
  "Delta".padEnd(10) +
  "Conserved?".padEnd(12) +
  "HGVS"
);
console.log("─".repeat(120));

interface CrossSpeciesResult {
  humanPos: number;
  mousePos: number;
  relativePos: number;
  category: string;
  hgvs: string;
  humanLSSIM: number;
  mouseLSSIM: number;
  delta: number;
  conserved: boolean;
}

const results: CrossSpeciesResult[] = [];
const PEARL_THRESHOLD = 0.95; // LSSIM < 0.95 = structural disruption

for (const pearl of pearls) {
  const mapping = mapHumanToMouse(pearl.humanPos);

  // Check if mouse position falls within simulation window
  if (mapping.mousePos < MOUSE.simStart || mapping.mousePos > MOUSE.simEnd) {
    console.log(`  ${pearl.humanPos} → OUT OF RANGE (${mapping.mousePos})`);
    continue;
  }

  // Compute variant bin in mouse config
  const mouseBin = Math.floor((mapping.mousePos - MOUSE.simStart) / MOUSE.resolution);

  // Get effectStrength from category (same as human)
  const CATEGORICAL_EFFECTS: Record<string, number> = {
    nonsense: 0.1, frameshift: 0.15, splice_donor: 0.2, splice_acceptor: 0.2,
    splice_region: 0.5, missense: 0.4, promoter: 0.3, "5_prime_UTR": 0.6,
    "3_prime_UTR": 0.7, intronic: 0.8, synonymous: 0.9, other: 0.5,
  };
  const effectStrength = CATEGORICAL_EFFECTS[pearl.category] || 0.5;

  // Generate mutant matrix for mouse
  const mouseMUT = simulateContactMatrix(
    mouseConfig, mouseFeatures, mouseBin, effectStrength, pearl.category, 42
  );

  // Compute LSSIM
  const mouseLSSIM = computeLSSIM(mouseWT, mouseMUT);

  const delta = Math.abs(pearl.humanLSSIM - mouseLSSIM);
  const conserved = mouseLSSIM < PEARL_THRESHOLD;

  results.push({
    humanPos: pearl.humanPos,
    mousePos: mapping.mousePos,
    relativePos: mapping.relativePos,
    category: pearl.category,
    hgvs: pearl.hgvs,
    humanLSSIM: pearl.humanLSSIM,
    mouseLSSIM,
    delta,
    conserved,
  });

  console.log(
    String(pearl.humanPos).padEnd(12) +
    String(mapping.mousePos).padEnd(12) +
    mapping.relativePos.toFixed(3).padEnd(8) +
    pearl.category.padEnd(18) +
    pearl.humanLSSIM.toFixed(4).padEnd(14) +
    mouseLSSIM.toFixed(4).padEnd(14) +
    delta.toFixed(4).padEnd(10) +
    (conserved ? "YES" : "no").padEnd(12) +
    pearl.hgvs.substring(0, 30)
  );
}

console.log("─".repeat(120));

// ============================================================================
// Summary statistics
// ============================================================================

const conservedCount = results.filter(r => r.conserved).length;
const humanMeanLSSIM = results.reduce((s, r) => s + r.humanLSSIM, 0) / results.length;
const mouseMeanLSSIM = results.reduce((s, r) => s + r.mouseLSSIM, 0) / results.length;
const meanDelta = results.reduce((s, r) => s + r.delta, 0) / results.length;

// Pearson correlation
const n = results.length;
const sumHuman = results.reduce((s, r) => s + r.humanLSSIM, 0);
const sumMouse = results.reduce((s, r) => s + r.mouseLSSIM, 0);
const sumHH = results.reduce((s, r) => s + r.humanLSSIM * r.humanLSSIM, 0);
const sumMM = results.reduce((s, r) => s + r.mouseLSSIM * r.mouseLSSIM, 0);
const sumHM = results.reduce((s, r) => s + r.humanLSSIM * r.mouseLSSIM, 0);
const pearsonR =
  (n * sumHM - sumHuman * sumMouse) /
  Math.sqrt((n * sumHH - sumHuman * sumHuman) * (n * sumMM - sumMouse * sumMouse));

console.log();
console.log("=== Summary ===");
console.log(`Total pearl positions analyzed: ${results.length}`);
console.log(`Conserved disruption (LSSIM < ${PEARL_THRESHOLD}): ${conservedCount}/${results.length} (${(100*conservedCount/results.length).toFixed(1)}%)`);
console.log(`Mean LSSIM — Human: ${humanMeanLSSIM.toFixed(4)}, Mouse: ${mouseMeanLSSIM.toFixed(4)}`);
console.log(`Mean |delta|: ${meanDelta.toFixed(4)}`);
console.log(`Pearson r (human vs mouse LSSIM): ${pearsonR.toFixed(4)}`);
console.log();

// Save results
const outputPath = path.join(process.cwd(), "results", "cross_species_hbb_comparison.json");
const output = {
  generated: new Date().toISOString().split("T")[0],
  human_config: humanConfig.id,
  mouse_config: mouseConfig.id,
  n_positions: results.length,
  conserved_count: conservedCount,
  conserved_pct: (100 * conservedCount / results.length),
  mean_human_lssim: humanMeanLSSIM,
  mean_mouse_lssim: mouseMeanLSSIM,
  mean_delta: meanDelta,
  pearson_r: pearsonR,
  pearl_threshold: PEARL_THRESHOLD,
  mapping_method: "tss_relative_with_interpolation",
  results: results,
  mouseWTMatrix: mouseWT,
};

fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
console.log(`Results saved to: ${outputPath}`);

// Also generate a control: random non-pearl positions
console.log();
console.log("=== Control: Random non-pearl positions ===");
const controlRng = new SeededRandom(42);
const controlResults: { mouseLSSIM: number }[] = [];
for (let i = 0; i < results.length; i++) {
  // Random position within the human window
  const humanPos = HUMAN.simStart + Math.floor(controlRng.random() * (HUMAN.simEnd - HUMAN.simStart));
  const mapping = mapHumanToMouse(humanPos);
  if (mapping.mousePos < MOUSE.simStart || mapping.mousePos > MOUSE.simEnd) continue;

  const mouseBin = Math.floor((mapping.mousePos - MOUSE.simStart) / MOUSE.resolution);
  const mouseMUT = simulateContactMatrix(mouseConfig, mouseFeatures, mouseBin, 0.5, "other", 42);
  const mouseLSSIM = computeLSSIM(mouseWT, mouseMUT);
  controlResults.push({ mouseLSSIM });
}

const controlMeanLSSIM = controlResults.reduce((s, r) => s + r.mouseLSSIM, 0) / controlResults.length;
const controlConserved = controlResults.filter(r => r.mouseLSSIM < PEARL_THRESHOLD).length;
console.log(`Control positions: ${controlResults.length}`);
console.log(`Control mean LSSIM: ${controlMeanLSSIM.toFixed(4)}`);
console.log(`Control "conserved" (LSSIM < ${PEARL_THRESHOLD}): ${controlConserved}/${controlResults.length}`);
console.log();
console.log(`Pearl vs Control delta: ${(controlMeanLSSIM - mouseMeanLSSIM).toFixed(4)} (positive = pearls more disrupted)`);
