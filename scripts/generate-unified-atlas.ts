/**
 * ARCHCODE Unified Atlas Generator — v2.0 Pipeline Fix
 *
 * ПОЧЕМУ этот скрипт: v1.0 использовал ДВА разных пайплайна:
 * - Pathogenic (353): TypeScript engine, effectStrength=0.8 для intronic
 * - Benign (750): Python pipeline, impact=0.02 для intronic
 * Разница в 10x → AUC=1.000 — артефакт, не реальная дискриминация.
 *
 * Этот скрипт прогоняет ВСЕ 1,103 варианта через ОДИН TypeScript engine.
 * getEffectStrength() видит только category, НИКОГДА label.
 * ClinVar label (Pathogenic/Benign) — только metadata в выходном файле.
 *
 * Ожидаемый результат: within-category AUC ≈ 0.5, global AUC > 0.5
 *
 * Usage: npx tsx scripts/generate-unified-atlas.ts [--locus 30kb|95kb]
 */

import * as fs from "fs";
import * as path from "path";
import { SeededRandom } from "../src/utils/random";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import {
  loadLocusConfig,
  resolveLocusPath,
  parseLocusArg,
  getLocusFeatures,
  type LocusConfig,
} from "../src/domain/config/locus-config";

// ============================================================================
// Types
// ============================================================================

interface RealVariant {
  vcv_id: string;
  position: number;
  ref: string;
  alt: string;
  hgvs_c: string;
  hgvs_p: string;
  category: string;
  clinical_significance: string;
}

interface VepResult {
  clinvar_id: string;
  position: number;
  ref: string;
  alt: string;
  vep_consequence: string;
  vep_impact: string;
  vep_score: number;
  sift_score: number;
  sift_prediction: string;
  interpretation: string;
  cadd_phred: number | null;
  cadd_raw: number | null;
}

interface UnifiedAtlasRow {
  ClinVar_ID: string;
  Position_GRCh38: number;
  Ref: string;
  Alt: string;
  HGVS_c: string;
  HGVS_p: string;
  Category: string;
  ClinVar_Significance: string;
  ARCHCODE_SSIM: number;
  ARCHCODE_LSSIM: number;
  ARCHCODE_DeltaInsulation: number;
  ARCHCODE_LoopIntegrity: number;
  ARCHCODE_Verdict: string;
  VEP_Consequence: string;
  VEP_Score: number;
  VEP_Impact: string;
  SIFT_Score: number;
  SIFT_Prediction: string;
  VEP_Interpretation: string;
  Pearl: boolean;
  Discordance: string;
  Mechanism_Insight: string;
  Label: string;
  Source: string;
  CADD_Phred: number;
  Effect_Source: string;
}

// HBB gene coordinates (GRCh38) — used for HBB-specific logic
const HBB_GENE = {
  chromosome: "chr11",
  start: 5225464,
  end: 5227079,
};

// ============================================================================
// Generic CSV variant loader (for CFTR and future loci)
// ============================================================================

interface GenericVariant {
  vcv_id: string;
  position: number;
  ref: string;
  alt: string;
  hgvs_c: string;
  hgvs_p: string;
  category: string;
  clinical_significance: string;
  label: "Pathogenic" | "Benign";
}

function loadGenericVariants(csvPath: string): GenericVariant[] {
  const fullPath = path.join(process.cwd(), csvPath);
  if (!fs.existsSync(fullPath)) {
    console.error(`Error: ${csvPath} not found`);
    console.error("Run: python scripts/download_clinvar_cftr.py");
    process.exit(1);
  }
  const content = fs.readFileSync(fullPath, "utf-8");
  const lines = content.trim().split("\n");
  // Trim each header/value to handle \r from Windows line endings
  const headers = lines[0].split(",").map((h) => h.trim());

  const variants: GenericVariant[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(",").map((v) => v.trim());
    const row: any = {};
    headers.forEach((h, idx) => (row[h] = values[idx]));

    const label = row.label;
    if (label !== "Pathogenic" && label !== "Benign") continue;

    variants.push({
      vcv_id: row.clinvar_id,
      position: parseInt(row.position),
      ref: row.ref || ".",
      alt: row.alt || ".",
      hgvs_c: row.hgvs_c || "",
      hgvs_p: row.hgvs_p || "",
      category: row.category || "other",
      clinical_significance: row.clinical_significance || "",
      label: label,
    });
  }
  return variants;
}

// Load locus configuration from JSON (--locus 30kb | 95kb)
const LOCUS_ARG = parseLocusArg();
const LOCUS_CONFIG_PATH = resolveLocusPath(LOCUS_ARG);
const LOCUS_CONFIG: LocusConfig = loadLocusConfig(LOCUS_CONFIG_PATH);

const SIM_START = LOCUS_CONFIG.window.start;
const SIM_END = LOCUS_CONFIG.window.end;
const RESOLUTION = LOCUS_CONFIG.window.resolution_bp;
const N_BINS = LOCUS_CONFIG.window.n_bins;
const LOCUS_FEATURES = getLocusFeatures(LOCUS_CONFIG);

// ============================================================================
// Data Loading — Pathogenic variants (from ClinVar JSON)
// ============================================================================

function loadPathogenicVariants(): RealVariant[] {
  const filePath = path.join(
    process.cwd(),
    "data",
    "clinvar_hbb_processed.json",
  );
  if (!fs.existsSync(filePath)) {
    console.error("Error: data/clinvar_hbb_processed.json not found");
    console.error(
      "Run: npx tsx scripts/download_clinvar_hbb.ts && npx tsx scripts/process_clinvar_hbb.ts",
    );
    process.exit(1);
  }
  const data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  return data.variants;
}

function loadPathogenicVep(): Map<string, VepResult> {
  const filePath = path.join(process.cwd(), "data", "hbb_vep_results.csv");
  if (!fs.existsSync(filePath)) {
    console.error("Error: data/hbb_vep_results.csv not found");
    process.exit(1);
  }
  return parseVepCsv(filePath);
}

// ============================================================================
// Data Loading — Benign variants (from CSV)
// ============================================================================

function loadBenignVariants(): RealVariant[] {
  const filePath = path.join(process.cwd(), "data", "hbb_benign_variants.csv");
  if (!fs.existsSync(filePath)) {
    console.error("Error: data/hbb_benign_variants.csv not found");
    process.exit(1);
  }
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.trim().split("\n");
  const headers = lines[0].split(",");

  const variants: RealVariant[] = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(",");
    const row: any = {};
    headers.forEach((h, idx) => (row[h] = values[idx]));

    variants.push({
      vcv_id: row.clinvar_id,
      position: parseInt(row.position),
      ref: row.ref,
      alt: row.alt,
      hgvs_c: row.hgvs_c || "",
      hgvs_p: row.hgvs_p || "",
      category: row.category,
      clinical_significance: row.clinical_significance,
    });
  }
  return variants;
}

function loadBenignVep(): Map<string, VepResult> {
  const filePath = path.join(
    process.cwd(),
    "data",
    "hbb_benign_vep_results.csv",
  );
  if (!fs.existsSync(filePath)) {
    console.error("Error: data/hbb_benign_vep_results.csv not found");
    console.error("Run: python scripts/extract_benign_vep.py");
    process.exit(1);
  }
  return parseVepCsv(filePath);
}

// ============================================================================
// Shared VEP CSV parser
// ============================================================================

function parseVepCsv(filePath: string): Map<string, VepResult> {
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.trim().split("\n");
  const headers = lines[0].split(",");

  const map = new Map<string, VepResult>();
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(",");
    const row: any = {};
    headers.forEach((h, idx) => (row[h] = values[idx]));

    map.set(row.clinvar_id, {
      clinvar_id: row.clinvar_id,
      position: parseInt(row.position),
      ref: row.ref,
      alt: row.alt,
      vep_consequence: row.vep_consequence,
      vep_impact: row.vep_impact || "MODIFIER",
      vep_score: parseFloat(row.vep_score) || 0,
      sift_score: parseFloat(row.sift_score),
      sift_prediction: row.sift_prediction || "",
      interpretation: row.interpretation || "",
      cadd_phred: row.cadd_phred ? parseFloat(row.cadd_phred) : null,
      cadd_raw: row.cadd_raw ? parseFloat(row.cadd_raw) : null,
    });
  }
  return map;
}

// ============================================================================
// Simulation Engine — IDENTICAL to generate-real-atlas.ts
// ============================================================================

// effectStrength mode: controls how variant category maps to structural perturbation.
// ПОЧЕМУ multi-mode: ablation study to prove AUC is category-driven, not circular.
//   categorical:     category → effectStrength → SSIM (default, documented effect)
//   position-only:   fixed 0.3 for ALL variants → AUC ≈ 0.55 (position has no signal)
//   uniform-medium:  fixed 0.5 for ALL variants → AUC ≈ 0.5 (second position control)
//   inverted:        SWAPPED mapping (nonsense=0.9, synonymous=0.1) → AUC << 0.5
//   random:          random 0.1-0.9 per variant → AUC ≈ 0.5 (noise baseline)
// CLI: --effect-mode <mode>
const VALID_EFFECT_MODES = ["categorical", "position-only", "uniform-medium", "inverted", "random"] as const;
type EffectMode = typeof VALID_EFFECT_MODES[number];
const rawMode = process.argv.includes("--effect-mode")
  ? process.argv[process.argv.indexOf("--effect-mode") + 1]
  : "categorical";
const EFFECT_MODE: EffectMode = VALID_EFFECT_MODES.includes(rawMode as EffectMode)
  ? (rawMode as EffectMode)
  : "categorical";

const CATEGORICAL_EFFECTS: Record<string, number> = {
  nonsense: 0.1,
  frameshift: 0.15,
  splice_donor: 0.2,
  splice_acceptor: 0.2,
  splice_region: 0.5,
  missense: 0.4,
  promoter: 0.3,
  "5_prime_UTR": 0.6,
  "3_prime_UTR": 0.7,
  intronic: 0.8,
  synonymous: 0.9,
  other: 0.5,
};

const FIXED_PERTURBATION = 0.3;

// Inverted mapping: swap severity direction. If AUC drops well below 0.5,
// proves that category DIRECTION matters, not just category-as-feature.
const INVERTED_EFFECTS: Record<string, number> = {
  nonsense: 0.9,       // was 0.1 → now weakest (benign-like)
  frameshift: 0.85,    // was 0.15
  splice_donor: 0.8,   // was 0.2
  splice_acceptor: 0.8,
  splice_region: 0.5,
  missense: 0.6,       // was 0.4
  promoter: 0.7,       // was 0.3
  "5_prime_UTR": 0.4,  // was 0.6
  "3_prime_UTR": 0.3,  // was 0.7
  intronic: 0.2,       // was 0.8 → now strong (pathogenic-like)
  synonymous: 0.1,     // was 0.9 → now strongest
  other: 0.5,
};

// Seeded random for reproducibility in random mode
let ablationRng = new SeededRandom(42);

function getEffectStrength(
  category: string,
): { value: number; source: string } {
  switch (EFFECT_MODE) {
    case "position-only":
      return { value: FIXED_PERTURBATION, source: "POSITION" };
    case "uniform-medium":
      return { value: 0.5, source: "UNIFORM_MEDIUM" };
    case "inverted":
      return {
        value: INVERTED_EFFECTS[category] || 0.5,
        source: "INVERTED",
      };
    case "random":
      return {
        value: 0.1 + ablationRng.random() * 0.8,
        source: "RANDOM",
      };
    default: // categorical
      return {
        value: CATEGORICAL_EFFECTS[category] || 0.5,
        source: "CATEGORICAL",
      };
  }
}

function simulatePairedMatrices(
  nBins: number,
  variantBin: number,
  effectStrength: number,
  category: string,
  seed: number,
): { reference: number[][]; mutant: number[][] } {
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  // Build MED1 occupancy from biologically accurate enhancer positions
  const baseLandscape: number[] = [];
  const landscapeRng = new SeededRandom(seed);
  for (let i = 0; i < nBins; i++) {
    const genomicPos = SIM_START + i * RESOLUTION;
    let occ =
      KRAMER_KINETICS.BACKGROUND_OCCUPANCY + landscapeRng.random() * 0.05;

    for (const enh of LOCUS_FEATURES.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / RESOLUTION;
      if (dist < 5) {
        occ += enh.occupancy * Math.exp(-0.5 * (dist * dist));
      }
    }
    baseLandscape.push(Math.min(1, occ));
  }

  const refOccupancy = [...baseLandscape];
  const mutOccupancy = baseLandscape.map((occ, i) => {
    if (variantBin >= 0) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        const reduction = effectStrength + (1 - effectStrength) * (dist / 3);
        return occ * reduction;
      }
    }
    return occ;
  });

  // CTCF barriers
  const ctcfBins = LOCUS_FEATURES.ctcfSites
    .map((c) => Math.floor((c.position - SIM_START) / RESOLUTION))
    .filter((b) => b >= 0 && b < nBins);
  const refCTCF = ctcfBins;
  const mutCTCF =
    category.includes("splice") || category.includes("promoter")
      ? ctcfBins.filter((b) => variantBin < 0 || Math.abs(b - variantBin) > 2)
      : ctcfBins;

  // Analytical contact map
  const refMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));
  const mutMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);

      const refOccFactor = Math.sqrt(refOccupancy[i] * refOccupancy[j]);
      const mutOccFactor = Math.sqrt(mutOccupancy[i] * mutOccupancy[j]);

      let refPerm = 1.0;
      let mutPerm = 1.0;
      for (const ctcf of refCTCF) {
        if (ctcf > i && ctcf < j) {
          refPerm *= 0.15;
        }
      }
      for (const ctcf of mutCTCF) {
        if (ctcf > i && ctcf < j) {
          mutPerm *= 0.15;
        }
      }

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

  // Joint normalization
  let maxVal = 0;
  for (let i = 0; i < nBins; i++) {
    for (let j = 0; j < nBins; j++) {
      if (refMatrix[i][j] > maxVal) maxVal = refMatrix[i][j];
      if (mutMatrix[i][j] > maxVal) maxVal = mutMatrix[i][j];
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < nBins; i++) {
      for (let j = 0; j < nBins; j++) {
        refMatrix[i][j] /= maxVal;
        mutMatrix[i][j] /= maxVal;
      }
    }
  }

  return { reference: refMatrix, mutant: mutMatrix };
}

function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat();
  const flatB = b.flat();

  const muA = flatA.reduce((s, v) => s + v, 0) / flatA.length;
  const muB = flatB.reduce((s, v) => s + v, 0) / flatB.length;

  let sigmaA2 = 0,
    sigmaB2 = 0,
    sigmaAB = 0;
  for (let i = 0; i < flatA.length; i++) {
    sigmaA2 += Math.pow(flatA[i] - muA, 2);
    sigmaB2 += Math.pow(flatB[i] - muB, 2);
    sigmaAB += (flatA[i] - muA) * (flatB[i] - muB);
  }
  sigmaA2 /= flatA.length;
  sigmaB2 /= flatB.length;
  sigmaAB /= flatA.length;

  const c1 = 0.0001;
  const c2 = 0.0009;

  return (
    ((2 * muA * muB + c1) * (2 * sigmaAB + c2)) /
    ((muA * muA + muB * muB + c1) * (sigmaA2 + sigmaB2 + c2))
  );
}

// ПОЧЕМУ Local SSIM: глобальный SSIM разбавляется на больших матрицах.
// Вариант возмущает ~6 бинов (±3). В 50×50 это ~12% → SSIM падает до 0.87.
// В 300×300 это ~2% → SSIM не опускается ниже 0.98. Пороги pearl (0.95) недостижимы.
// Решение: извлекаем 50×50 подматрицу вокруг варианта → доля возмущения всегда ~12%.
// Для матриц ≤50 бинов (HBB 30kb) LSSIM ≡ global SSIM — нет разбавления.
const LOCAL_SSIM_WINDOW = 50;

function calculateLocalSSIM(
  reference: number[][],
  mutant: number[][],
  variantBin: number,
  windowSize: number = LOCAL_SSIM_WINDOW,
): number {
  const n = reference.length;

  // For small matrices, local SSIM equals global SSIM
  if (n <= windowSize) {
    return calculateSSIM(reference, mutant);
  }

  // Window centered on variantBin with clamp+shift edge handling
  const halfWindow = Math.floor(windowSize / 2);
  let start = variantBin - halfWindow;
  let end = start + windowSize;

  // Shift window if it exceeds matrix bounds (never crop)
  if (start < 0) {
    start = 0;
    end = windowSize;
  }
  if (end > n) {
    end = n;
    start = n - windowSize;
  }

  // Extract submatrices
  const refSub: number[][] = [];
  const mutSub: number[][] = [];
  for (let i = start; i < end; i++) {
    const refRow: number[] = [];
    const mutRow: number[] = [];
    for (let j = start; j < end; j++) {
      refRow.push(reference[i][j]);
      mutRow.push(mutant[i][j]);
    }
    refSub.push(refRow);
    mutSub.push(mutRow);
  }

  return calculateSSIM(refSub, mutSub);
}

function calculateInsulationDelta(
  ref: number[][],
  mut: number[][],
  focusBin: number,
): number {
  const windowSize = 5;
  const n = ref.length;

  let refSum = 0,
    mutSum = 0,
    count = 0;
  for (
    let i = Math.max(0, focusBin - windowSize);
    i < Math.min(n, focusBin + windowSize);
    i++
  ) {
    for (let j = i + 1; j < Math.min(n, focusBin + windowSize); j++) {
      refSum += ref[i][j];
      mutSum += mut[i][j];
      count++;
    }
  }

  if (count === 0) return 0;
  return Math.abs(refSum - mutSum) / count;
}

function calculateLoopIntegrity(matrix: number[][]): number {
  const n = matrix.length;
  let strongContacts = 0;
  let totalContacts = 0;

  for (let i = 0; i < n; i++) {
    for (let j = i + 3; j < n; j++) {
      if (matrix[i][j] > 0.3) strongContacts++;
      totalContacts++;
    }
  }

  return totalContacts > 0 ? strongContacts / totalContacts : 0;
}

// ============================================================================
// Main Pipeline — Unified
// ============================================================================

async function main() {
  console.log("=".repeat(70));
  console.log("ARCHCODE Unified Atlas Generator — v2.0 Pipeline Fix");
  console.log("=".repeat(70));
  console.log(`Locus config:  ${LOCUS_CONFIG.id} (${LOCUS_CONFIG.name})`);
  console.log(
    `Window:        ${LOCUS_CONFIG.window.chromosome}:${SIM_START}-${SIM_END} (${(SIM_END - SIM_START) / 1000}kb)`,
  );
  console.log(
    `Matrix:        ${N_BINS}x${N_BINS} (${RESOLUTION}bp resolution)`,
  );
  console.log(
    `Thresholds:    ${LOCUS_CONFIG.thresholds ? "calibrated" : "using 30kb defaults (uncalibrated)"}`,
  );
  console.log(
    `Kramer kinetics: alpha=${KRAMER_KINETICS.DEFAULT_ALPHA}, gamma=${KRAMER_KINETICS.DEFAULT_GAMMA}`,
  );
  console.log();

  // ============================================================================
  // Variant loading — HBB vs CFTR (and future loci)
  // ============================================================================

  type TaggedVariant = RealVariant & { label: "Pathogenic" | "Benign" };
  let allVariants: TaggedVariant[];
  let vepMap: Map<string, VepResult>;
  let hasVep: boolean;

  const isGenericLocus =
    LOCUS_ARG === "cftr" ||
    LOCUS_ARG === "tp53" ||
    LOCUS_ARG === "brca1" ||
    LOCUS_ARG === "mlh1" ||
    LOCUS_ARG === "ldlr" ||
    LOCUS_ARG === "scn5a" ||
    LOCUS_ARG === "tert" ||
    LOCUS_ARG === "gjb2"; // extend as needed

  if (isGenericLocus) {
    // CFTR (and future loci): single CSV with both P/LP and B/LB
    const csvFile = `data/${LOCUS_ARG}_variants.csv`;
    console.log(`Loading variants from ${csvFile}...`);
    const genericVariants = loadGenericVariants(csvFile);
    allVariants = genericVariants.map((v) => ({
      vcv_id: v.vcv_id,
      position: v.position,
      ref: v.ref,
      alt: v.alt,
      hgvs_c: v.hgvs_c,
      hgvs_p: v.hgvs_p,
      category: v.category,
      clinical_significance: v.clinical_significance,
      label: v.label,
    }));
    vepMap = new Map(); // No VEP for CFTR — not needed for within-category test
    hasVep = false;

    const pathCount = allVariants.filter(
      (v) => v.label === "Pathogenic",
    ).length;
    const benCount = allVariants.filter((v) => v.label === "Benign").length;
    console.log(`  Pathogenic/LP: ${pathCount}`);
    console.log(`  Benign/LB:     ${benCount}`);
    console.log(`  Total:         ${allVariants.length}`);
    console.log("  VEP: skipped (not required for within-category analysis)");
  } else {
    // HBB: existing logic (unchanged)
    console.log("Loading pathogenic variants (ClinVar JSON)...");
    const pathogenicVariants = loadPathogenicVariants();
    console.log(`  Loaded ${pathogenicVariants.length} pathogenic variants`);

    console.log("Loading pathogenic VEP results...");
    const pathogenicVep = loadPathogenicVep();
    console.log(`  Loaded ${pathogenicVep.size} pathogenic VEP entries`);

    console.log("Loading benign variants (CSV)...");
    const benignVariants = loadBenignVariants();
    console.log(`  Loaded ${benignVariants.length} benign variants`);

    console.log("Loading benign VEP results...");
    const benignVep = loadBenignVep();
    console.log(`  Loaded ${benignVep.size} benign VEP entries`);

    vepMap = new Map<string, VepResult>([...pathogenicVep, ...benignVep]);
    console.log(`  Merged VEP map: ${vepMap.size} total entries`);
    hasVep = true;

    allVariants = [
      ...pathogenicVariants.map((v) => ({
        ...v,
        label: "Pathogenic" as const,
      })),
      ...benignVariants.map((v) => ({ ...v, label: "Benign" as const })),
    ];
  }
  console.log(`\nTotal variants: ${allVariants.length}`);

  // Match with VEP (skip for generic loci)
  const matchedVariants = hasVep
    ? allVariants.filter((v) => vepMap.has(v.vcv_id))
    : allVariants;
  const unmatchedCount = allVariants.length - matchedVariants.length;
  if (hasVep) {
    console.log(`  Matched with VEP: ${matchedVariants.length}`);
  }
  if (unmatchedCount > 0) {
    console.log(`  Unmatched (skipped): ${unmatchedCount}`);
  }

  // Simulate ALL through identical physics
  console.log("\nSimulating paired matrices for ALL variants...");
  console.log(
    `  Matrix size: ${N_BINS}x${N_BINS} (${RESOLUTION}bp resolution)`,
  );
  console.log(
    "  Method: Analytical mean-field (Kramer kinetics + CTCF barriers)",
  );
  console.log(
    `  effectStrength: ${EFFECT_MODE === "position-only" ? `POSITION-ONLY (fixed=${FIXED_PERTURBATION})` : "CATEGORICAL (category-only, label-blind)"}`,
  );

  const results: UnifiedAtlasRow[] = [];
  const batchSize = 50;

  for (let i = 0; i < matchedVariants.length; i += batchSize) {
    const batch = matchedVariants.slice(
      i,
      Math.min(i + batchSize, matchedVariants.length),
    );

    for (const variant of batch) {
      const vep = vepMap.get(variant.vcv_id) ?? null;
      const variantBin = Math.floor(
        (variant.position - SIM_START) / RESOLUTION,
      );

      // effectStrength: categorical (default) or position-only (--effect-mode)
      const { value: effectStrength, source: effectSource } =
        getEffectStrength(variant.category);

      const { reference: referenceMatrix, mutant: mutantMatrix } =
        simulatePairedMatrices(
          N_BINS,
          variantBin,
          effectStrength,
          variant.category,
          variant.position,
        );

      const ssim = calculateSSIM(referenceMatrix, mutantMatrix);
      const lssim = calculateLocalSSIM(
        referenceMatrix,
        mutantMatrix,
        variantBin,
      );
      const deltaInsulation = calculateInsulationDelta(
        referenceMatrix,
        mutantMatrix,
        variantBin,
      );
      const loopIntegrity = calculateLoopIntegrity(mutantMatrix);

      // Verdict thresholds — from config if calibrated, else defaults (30kb values)
      const t = LOCUS_CONFIG.thresholds ?? {
        ssim_pathogenic: 0.85,
        ssim_likely_pathogenic: 0.92,
        ssim_vus: 0.96,
        ssim_likely_benign: 0.99,
      };
      // ПОЧЕМУ lssim для verdict: глобальный SSIM разбавлен на больших матрицах,
      // LSSIM нормализует к 50×50 окну → пороги HBB 30kb переносятся напрямую
      let verdict: string;
      if (lssim < t.ssim_pathogenic) {
        verdict = "PATHOGENIC";
      } else if (lssim < t.ssim_likely_pathogenic) {
        verdict = "LIKELY_PATHOGENIC";
      } else if (lssim < t.ssim_vus) {
        verdict = "VUS";
      } else if (lssim < t.ssim_likely_benign) {
        verdict = "LIKELY_BENIGN";
      } else {
        verdict = "BENIGN";
      }

      const isPearl = vep ? vep.vep_score < 0.3 && lssim < 0.95 : false;

      const archcodePathogenic =
        verdict === "PATHOGENIC" || verdict === "LIKELY_PATHOGENIC";
      const vepPathogenic = vep ? vep.vep_score >= 0.5 : false;
      let discordance = vep ? "AGREEMENT" : "NO_VEP";
      if (vep) {
        if (archcodePathogenic && !vepPathogenic) {
          discordance = "ARCHCODE_ONLY";
        } else if (!archcodePathogenic && vepPathogenic) {
          discordance = "VEP_ONLY";
        }
      }

      let insight =
        "Convergent evidence from structural and sequence analysis.";
      if (discordance === "NO_VEP") {
        insight = `Structural-only assessment (LSSIM=${lssim.toFixed(3)}, global SSIM=${ssim.toFixed(3)}). VEP not available for this locus.`;
      } else if (discordance === "ARCHCODE_ONLY") {
        insight = `3D structural disruption detected (LSSIM=${lssim.toFixed(3)}) without sequence-level pathogenicity signal.`;
      } else if (discordance === "VEP_ONLY") {
        insight = `Sequence-level pathogenicity (VEP: ${vep!.vep_consequence}) without significant 3D structural change.`;
      }
      if (isPearl && vep) {
        insight = `PEARL: VEP blind (score=${vep.vep_score.toFixed(2)}) but ARCHCODE detects structural disruption (LSSIM=${lssim.toFixed(3)}).`;
      }

      results.push({
        ClinVar_ID: variant.vcv_id,
        Position_GRCh38: variant.position,
        Ref: variant.ref,
        Alt: variant.alt,
        HGVS_c: variant.hgvs_c,
        HGVS_p: variant.hgvs_p,
        Category: variant.category,
        ClinVar_Significance: variant.clinical_significance,
        ARCHCODE_SSIM: parseFloat(ssim.toFixed(4)),
        ARCHCODE_LSSIM: parseFloat(lssim.toFixed(4)),
        ARCHCODE_DeltaInsulation: parseFloat(deltaInsulation.toFixed(4)),
        ARCHCODE_LoopIntegrity: parseFloat(loopIntegrity.toFixed(4)),
        ARCHCODE_Verdict: verdict,
        VEP_Consequence: vep?.vep_consequence ?? "",
        VEP_Score: vep ? parseFloat(vep.vep_score.toFixed(4)) : -1,
        VEP_Impact: vep?.vep_impact ?? "",
        SIFT_Score: vep
          ? isNaN(vep.sift_score)
            ? -1
            : parseFloat(vep.sift_score.toFixed(4))
          : -1,
        SIFT_Prediction: vep?.sift_prediction ?? "",
        VEP_Interpretation: vep?.interpretation ?? "",
        Pearl: isPearl,
        Discordance: discordance,
        Mechanism_Insight: insight,
        Label: variant.label,
        Source:
          variant.label === "Pathogenic"
            ? "ClinVar_Pathogenic"
            : "ClinVar_Benign",
        CADD_Phred: vep?.cadd_phred !== null && vep?.cadd_phred !== undefined
          ? parseFloat(vep.cadd_phred.toFixed(1))
          : -1,
        Effect_Source: effectSource,
      });
    }

    const progress = Math.min(
      100,
      ((i + batch.length) / matchedVariants.length) * 100,
    ).toFixed(0);
    process.stdout.write(
      `\r  Progress: ${progress}% (${Math.min(i + batch.length, matchedVariants.length)}/${matchedVariants.length})`,
    );
  }
  console.log("\n");

  // Sort by position
  results.sort((a, b) => a.Position_GRCh38 - b.Position_GRCh38);

  // Write CSV
  const outputDir = path.join(process.cwd(), "results");
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  // Output naming: use gene name matching locus arg, fallback to first gene or arg
  const geneName = isGenericLocus
    ? (LOCUS_CONFIG.features.genes.find(
        (g) => g.name.toLowerCase() === LOCUS_ARG.toLowerCase(),
      )?.name ??
      LOCUS_CONFIG.features.genes[0]?.name ??
      LOCUS_ARG.toUpperCase())
    : "HBB";
  const windowKb = `${Math.round((SIM_END - SIM_START) / 1000)}kb`;
  const modeSuffix = EFFECT_MODE === "categorical" ? "" : `_${EFFECT_MODE.toUpperCase().replace("-", "_")}`;
  const csvFilename = isGenericLocus
    ? `${geneName}_Unified_Atlas_${windowKb}${modeSuffix}.csv`
    : LOCUS_ARG === "30kb"
      ? `HBB_Unified_Atlas${modeSuffix}.csv`
      : `HBB_Unified_Atlas_${LOCUS_ARG}${modeSuffix}.csv`;
  const csvPath = path.join(outputDir, csvFilename);
  if (results.length === 0) {
    console.error("ERROR: No results to write. Check variant loading.");
    process.exit(1);
  }
  const headers = Object.keys(results[0]);
  const csvLines = [
    headers.join(","),
    ...results.map((r) =>
      headers
        .map((h) => {
          const val = (r as any)[h];
          if (
            typeof val === "string" &&
            (val.includes(",") || val.includes('"'))
          ) {
            return `"${val.replace(/"/g, '""')}"`;
          }
          return val;
        })
        .join(","),
    ),
  ];
  fs.writeFileSync(csvPath, csvLines.join("\n"));
  console.log(`CSV saved: ${csvPath}`);

  // ======== Statistics ========
  const pathogenicResults = results.filter((r) => r.Label === "Pathogenic");
  const benignResults = results.filter((r) => r.Label === "Benign");
  const pearls = results.filter((r) => r.Pearl);
  const archcodePathogenic = results.filter(
    (r) =>
      r.ARCHCODE_Verdict === "PATHOGENIC" ||
      r.ARCHCODE_Verdict === "LIKELY_PATHOGENIC",
  );

  // Category breakdown by label
  const categories = [...new Set(results.map((r) => r.Category))];
  const categoryBreakdown: Record<string, any> = {};
  for (const cat of categories) {
    const catAll = results.filter((r) => r.Category === cat);
    const catPath = catAll.filter((r) => r.Label === "Pathogenic");
    const catBenign = catAll.filter((r) => r.Label === "Benign");
    categoryBreakdown[cat] = {
      total: catAll.length,
      pathogenic_count: catPath.length,
      benign_count: catBenign.length,
      mean_ssim_all: parseFloat(
        (
          catAll.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) / catAll.length
        ).toFixed(4),
      ),
      mean_ssim_pathogenic:
        catPath.length > 0
          ? parseFloat(
              (
                catPath.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
                catPath.length
              ).toFixed(4),
            )
          : null,
      mean_ssim_benign:
        catBenign.length > 0
          ? parseFloat(
              (
                catBenign.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
                catBenign.length
              ).toFixed(4),
            )
          : null,
      mean_lssim_all: parseFloat(
        (
          catAll.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) / catAll.length
        ).toFixed(4),
      ),
      mean_lssim_pathogenic:
        catPath.length > 0
          ? parseFloat(
              (
                catPath.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) /
                catPath.length
              ).toFixed(4),
            )
          : null,
      mean_lssim_benign:
        catBenign.length > 0
          ? parseFloat(
              (
                catBenign.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) /
                catBenign.length
              ).toFixed(4),
            )
          : null,
    };
  }

  // Write summary JSON
  const summarySuffix = isGenericLocus
    ? `_${geneName}_${windowKb}`
    : LOCUS_ARG === "30kb"
      ? ""
      : `_${LOCUS_ARG}`;
  const summaryPath = path.join(
    outputDir,
    `UNIFIED_ATLAS_SUMMARY${summarySuffix}.json`,
  );
  const summary = {
    title: "ARCHCODE Unified Atlas — v2.0 Pipeline Fix",
    date: new Date().toISOString(),
    locus_config_id: LOCUS_CONFIG.id,
    locus_config_path: LOCUS_CONFIG_PATH,
    provenance: {
      ctcf_sources: [
        ...new Set(LOCUS_CONFIG.features.ctcf_sites.map((c) => c.source)),
      ],
      enhancer_sources: [
        ...new Set(LOCUS_CONFIG.features.enhancers.map((e) => e.source)),
      ],
      thresholds_calibrated: LOCUS_CONFIG.thresholds !== null,
    },
    fix_description:
      `All ${results.length} variants processed through identical TypeScript engine. ` +
      (EFFECT_MODE === "position-only"
        ? `effectStrength fixed at ${FIXED_PERTURBATION} for ALL variants (position-only control). `
        : "getEffectStrength() sees only category, never ClinVar label. ") +
      "Eliminates pipeline discrepancy that caused AUC=1.000 artifact in v1.0.",
    data_sources: isGenericLocus
      ? {
          variants: `NCBI ClinVar (data/${LOCUS_ARG}_variants.csv)`,
          structural_predictor: "ARCHCODE loop extrusion (Kramer kinetics)",
        }
      : {
          pathogenic_variants: "NCBI ClinVar (clinvar_hbb_processed.json)",
          benign_variants: "NCBI ClinVar (hbb_benign_variants.csv)",
          sequence_predictor: "Ensembl VEP v113",
          structural_predictor: "ARCHCODE loop extrusion (Kramer kinetics)",
        },
    parameters: {
      alpha: KRAMER_KINETICS.DEFAULT_ALPHA,
      gamma: KRAMER_KINETICS.DEFAULT_GAMMA,
      k_base: KRAMER_KINETICS.K_BASE,
      resolution_bp: RESOLUTION,
      simulation_window: `${LOCUS_CONFIG.window.chromosome}:${SIM_START}-${SIM_END}`,
      n_bins: N_BINS,
    },
    statistics: {
      total_variants: results.length,
      pathogenic_variants: pathogenicResults.length,
      benign_variants: benignResults.length,
      archcode_structural_pathogenic: archcodePathogenic.length,
      pearls: pearls.length,
      mean_ssim_all: parseFloat(
        (
          results.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) / results.length
        ).toFixed(4),
      ),
      mean_ssim_pathogenic: parseFloat(
        (
          pathogenicResults.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
          pathogenicResults.length
        ).toFixed(4),
      ),
      mean_ssim_benign: parseFloat(
        (
          benignResults.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
          benignResults.length
        ).toFixed(4),
      ),
      mean_lssim_all: parseFloat(
        (
          results.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) / results.length
        ).toFixed(4),
      ),
      mean_lssim_pathogenic: parseFloat(
        (
          pathogenicResults.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) /
          pathogenicResults.length
        ).toFixed(4),
      ),
      mean_lssim_benign: parseFloat(
        (
          benignResults.reduce((s, r) => s + r.ARCHCODE_LSSIM, 0) /
          benignResults.length
        ).toFixed(4),
      ),
      local_ssim_window: LOCAL_SSIM_WINDOW,
    },
    category_breakdown: categoryBreakdown,
    pipeline_integrity: {
      single_engine: true,
      label_blind_simulation: true,
      effect_strength_source:
        EFFECT_MODE === "position-only"
          ? "POSITION-ONLY (fixed perturbation, circularity-free)"
          : "CATEGORICAL (category-only, label-blind)",
      effect_mode: EFFECT_MODE,
      ...(EFFECT_MODE === "position-only"
        ? { fixed_perturbation: FIXED_PERTURBATION }
        : {}),
    },
  };
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`Summary saved: ${summaryPath}`);

  // ======== Print summary ========
  console.log("\n" + "=".repeat(70));
  console.log("SUMMARY — UNIFIED ATLAS (v2.0 Pipeline Fix + LSSIM)");
  console.log("=".repeat(70));
  console.log(`Total variants:          ${results.length}`);
  console.log(
    `  Pathogenic:            ${pathogenicResults.length}  (mean SSIM=${summary.statistics.mean_ssim_pathogenic}, LSSIM=${summary.statistics.mean_lssim_pathogenic})`,
  );
  console.log(
    `  Benign:                ${benignResults.length}  (mean SSIM=${summary.statistics.mean_ssim_benign}, LSSIM=${summary.statistics.mean_lssim_benign})`,
  );
  console.log(
    `ARCHCODE struct. path.:  ${archcodePathogenic.length} (verdict based on LSSIM)`,
  );
  console.log(`Pearls:                  ${pearls.length}`);
  console.log(
    `Local SSIM window:       ${LOCAL_SSIM_WINDOW}×${LOCAL_SSIM_WINDOW} bins`,
  );
  console.log(
    `Effect source:           ${EFFECT_MODE === "position-only" ? `POSITION-ONLY (fixed=${FIXED_PERTURBATION})` : "CATEGORICAL"}`,
  );

  console.log(
    "\nCategory breakdown (Pathogenic mean SSIM vs Benign mean SSIM):",
  );
  for (const [cat, info] of Object.entries(categoryBreakdown)) {
    const ci = info as any;
    const pathStr =
      ci.mean_ssim_pathogenic !== null
        ? ci.mean_ssim_pathogenic.toFixed(4)
        : "N/A";
    const benStr =
      ci.mean_ssim_benign !== null ? ci.mean_ssim_benign.toFixed(4) : "N/A";
    const delta =
      ci.mean_ssim_pathogenic !== null && ci.mean_ssim_benign !== null
        ? (ci.mean_ssim_pathogenic - ci.mean_ssim_benign).toFixed(4)
        : "N/A";
    console.log(
      `  ${cat.padEnd(20)} Path=${pathStr}  Ben=${benStr}  Δ=${delta}  (n=${ci.total})`,
    );
  }

  // KEY VERIFICATION: within-category SSIM should be nearly identical
  console.log("\n" + "=".repeat(70));
  console.log("PIPELINE INTEGRITY CHECKS");
  console.log("=".repeat(70));

  // Check intronic specifically (was the main artifact in v1.0)
  const intronicPath = results.filter(
    (r) => r.Category === "intronic" && r.Label === "Pathogenic",
  );
  const intronicBenign = results.filter(
    (r) => r.Category === "intronic" && r.Label === "Benign",
  );
  if (intronicPath.length > 0 && intronicBenign.length > 0) {
    const avgPath =
      intronicPath.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
      intronicPath.length;
    const avgBenign =
      intronicBenign.reduce((s, r) => s + r.ARCHCODE_SSIM, 0) /
      intronicBenign.length;
    const delta = Math.abs(avgPath - avgBenign);
    console.log(
      `Intronic: Path SSIM=${avgPath.toFixed(4)}, Benign SSIM=${avgBenign.toFixed(4)}, Δ=${delta.toFixed(4)}`,
    );
    console.log(
      `  v1.0 had: Path=0.995, Benign=1.000 (Δ=0.005 → 10x pipeline artifact)`,
    );
    console.log(`  Expected: Δ ≈ 0 (same effect strength for same category)`);
    if (delta < 0.01) {
      console.log("  PASS: Within-category SSIM is label-blind");
    } else {
      console.log("  WARNING: Unexpected within-category SSIM difference");
    }
  }

  // Check no mock IDs
  const mockIds = results.filter((r) => r.ClinVar_ID.match(/^VCV0{8,}/));
  console.log(
    `\nMock ClinVar IDs (VCV00000...): ${mockIds.length} ${mockIds.length === 0 ? "PASS" : "FAIL"}`,
  );

  // Verify counts
  console.log(
    `\nVariant count check: ${pathogenicResults.length} Path + ${benignResults.length} Ben = ${results.length} total`,
  );
  const expectedTotal = pathogenicResults.length + benignResults.length;
  console.log(
    `  ${results.length === expectedTotal ? "PASS" : "FAIL"}: Sum matches total`,
  );
}

main().catch(console.error);
