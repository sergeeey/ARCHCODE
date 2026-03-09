/**
 * ARCHCODE Multi-Locus BET Inhibitor Sweep
 * ==========================================
 * Tests BET inhibitor effect (enhancer occupancy reduction) across all 9 loci.
 * Prediction: tissue-matched loci (HBB, TERT) show strong BET effect,
 * tissue-mismatch loci (SCN5A, GJB2) show null effect.
 *
 * For each locus: simulate WT vs known pathogenic variant at 5 BET inhibition levels.
 * Measure: does ΔSSIM decrease with BET inhibition?
 *
 * Usage: npx tsx scripts/bet-sweep-multilocus.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus definitions (compact) ──────────────────────────────────

interface LocusConfig {
  name: string;
  chromosome: string;
  simStart: number;
  simEnd: number;
  resolution: number;
  tissue: string;
  tissueMatch: "matched" | "partial" | "mismatch";
  enhancers: Array<{ position: number; occupancy: number; name: string }>;
  ctcfSites: Array<{ position: number }>;
  testVariant: { position: number; effect: number; name: string };
}

const LOCI: LocusConfig[] = [
  {
    name: "HBB",
    chromosome: "chr11",
    simStart: 5210000, simEnd: 5240000, resolution: 600,
    tissue: "K562 (erythroid)", tissueMatch: "matched",
    enhancers: [
      { position: 5227000, occupancy: 0.85, name: "HBB_promoter" },
      { position: 5225500, occupancy: 0.75, name: "3prime_HS1" },
      { position: 5230000, occupancy: 0.70, name: "LCR_HS2_proximal" },
      { position: 5233000, occupancy: 0.65, name: "LCR_HS3_proximal" },
      { position: 5220000, occupancy: 0.50, name: "downstream_enhancer" },
    ],
    ctcfSites: [
      { position: 5212000 }, { position: 5218000 }, { position: 5224000 },
      { position: 5228000 }, { position: 5232000 }, { position: 5236000 },
    ],
    testVariant: { position: 5226796, effect: 0.2, name: "VCV002024192_splice_acceptor" },
  },
  {
    name: "BRCA1",
    chromosome: "chr17",
    simStart: 43040000, simEnd: 43140000, resolution: 1000,
    tissue: "MCF7 (breast)", tissueMatch: "partial",
    enhancers: [
      { position: 43125364, occupancy: 0.90, name: "BRCA1_TSS" },
      { position: 43085710, occupancy: 0.55, name: "intragenic" },
      { position: 43042287, occupancy: 0.45, name: "5prime" },
    ],
    ctcfSites: [
      { position: 43042287 }, { position: 43085710 }, { position: 43124566 },
    ],
    testVariant: { position: 43091434, effect: 0.15, name: "nonsense_BRCA1" },
  },
  {
    name: "TP53",
    chromosome: "chr17",
    simStart: 7661779, simEnd: 7691779, resolution: 600,
    tissue: "K562", tissueMatch: "partial",
    enhancers: [
      { position: 7676594, occupancy: 0.85, name: "TP53_promoter" },
      { position: 7670000, occupancy: 0.60, name: "upstream_enh" },
      { position: 7685000, occupancy: 0.50, name: "downstream_enh" },
    ],
    ctcfSites: [
      { position: 7665000 }, { position: 7675000 }, { position: 7688000 },
    ],
    testVariant: { position: 7674220, effect: 0.1, name: "R175H_hotspot" },
  },
  {
    name: "TERT",
    chromosome: "chr5",
    simStart: 1235000, simEnd: 1335000, resolution: 1000,
    tissue: "K562", tissueMatch: "matched",
    enhancers: [
      { position: 1295228, occupancy: 0.90, name: "TERT_promoter" },
      { position: 1280000, occupancy: 0.65, name: "upstream_enh" },
      { position: 1310000, occupancy: 0.55, name: "downstream_enh" },
    ],
    ctcfSites: [
      { position: 1250000 }, { position: 1275000 }, { position: 1305000 }, { position: 1325000 },
    ],
    testVariant: { position: 1295228, effect: 0.3, name: "C228T_promoter" },
  },
  {
    name: "MLH1",
    chromosome: "chr3",
    simStart: 36993000, simEnd: 37053000, resolution: 600,
    tissue: "K562", tissueMatch: "partial",
    enhancers: [
      { position: 37034840, occupancy: 0.80, name: "MLH1_promoter" },
      { position: 37020000, occupancy: 0.50, name: "intragenic_enh" },
    ],
    ctcfSites: [
      { position: 37000000 }, { position: 37025000 }, { position: 37045000 },
    ],
    testVariant: { position: 37034840, effect: 0.2, name: "promoter_variant" },
  },
  {
    name: "CFTR",
    chromosome: "chr7",
    simStart: 117480000, simEnd: 117670000, resolution: 1000,
    tissue: "K562", tissueMatch: "mismatch",
    enhancers: [
      { position: 117559590, occupancy: 0.75, name: "CFTR_promoter" },
      { position: 117600000, occupancy: 0.45, name: "intragenic_enh" },
    ],
    ctcfSites: [
      { position: 117500000 }, { position: 117540000 }, { position: 117580000 },
      { position: 117620000 }, { position: 117660000 },
    ],
    testVariant: { position: 117559590, effect: 0.2, name: "F508del_region" },
  },
  {
    name: "SCN5A",
    chromosome: "chr3",
    simStart: 38550000, simEnd: 38700000, resolution: 1000,
    tissue: "K562", tissueMatch: "mismatch",
    enhancers: [
      { position: 38589553, occupancy: 0.70, name: "SCN5A_promoter" },
      { position: 38620000, occupancy: 0.35, name: "intragenic" },
    ],
    ctcfSites: [
      { position: 38560000 }, { position: 38600000 }, { position: 38650000 }, { position: 38690000 },
    ],
    testVariant: { position: 38589553, effect: 0.2, name: "promoter_variant" },
  },
  {
    name: "GJB2",
    chromosome: "chr13",
    simStart: 20187000, simEnd: 20207000, resolution: 600,
    tissue: "K562", tissueMatch: "mismatch",
    enhancers: [
      { position: 20197176, occupancy: 0.60, name: "GJB2_promoter" },
    ],
    ctcfSites: [
      { position: 20190000 }, { position: 20200000 },
    ],
    testVariant: { position: 20197176, effect: 0.2, name: "35delG_region" },
  },
  {
    name: "LDLR",
    chromosome: "chr19",
    simStart: 11089000, simEnd: 11139000, resolution: 600,
    tissue: "K562", tissueMatch: "partial",
    enhancers: [
      { position: 11106535, occupancy: 0.80, name: "LDLR_promoter" },
      { position: 11120000, occupancy: 0.50, name: "intragenic_enh" },
    ],
    ctcfSites: [
      { position: 11095000 }, { position: 11110000 }, { position: 11130000 },
    ],
    testVariant: { position: 11106535, effect: 0.2, name: "promoter_variant" },
  },
];

// BET inhibition levels (0 = no inhibition, 1 = full inhibition)
const BET_INHIBITION = [0.0, 0.25, 0.50, 0.75, 1.0];

// ── Simulation engine ────────────────────────────────────────────

function buildOccupancy(
  locus: LocusConfig,
  enhancerScale: number,
): number[] {
  const nBins = Math.ceil((locus.simEnd - locus.simStart) / locus.resolution);
  const rng = new SeededRandom(42);
  const landscape: number[] = [];

  for (let i = 0; i < nBins; i++) {
    const genomicPos = locus.simStart + i * locus.resolution;
    let occ = KRAMER_KINETICS.BACKGROUND_OCCUPANCY + rng.random() * 0.05;
    for (const enh of locus.enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / locus.resolution;
      if (dist < 5) {
        occ += enh.occupancy * enhancerScale * Math.exp(-0.5 * dist * dist);
      }
    }
    landscape.push(Math.min(1, occ));
  }
  return landscape;
}

function simulateContactMap(
  locus: LocusConfig,
  occupancy: number[],
  variantBin: number,
  effectStrength: number,
): number[][] {
  const nBins = Math.ceil((locus.simEnd - locus.simStart) / locus.resolution);
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA } = KRAMER_KINETICS;

  const modOccupancy = occupancy.map((occ, i) => {
    if (variantBin >= 0) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        const reduction = effectStrength + (1 - effectStrength) * (dist / 3);
        return occ * reduction;
      }
    }
    return occ;
  });

  const ctcfBins = locus.ctcfSites
    .map(c => Math.floor((c.position - locus.simStart) / locus.resolution))
    .filter(b => b >= 0 && b < nBins);

  const matrix: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);
      const occFactor = Math.sqrt(modOccupancy[i] * modOccupancy[j]);

      let perm = 1.0;
      for (const ctcf of ctcfBins) {
        if (ctcf > i && ctcf < j) perm *= (1 - 0.85);
      }

      const kramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * Math.pow(Math.max(0.001, occFactor), DEFAULT_GAMMA));
      matrix[i][j] = distFactor * occFactor * perm * kramer;
      matrix[j][i] = matrix[i][j];
    }
  }

  // Normalize
  let maxVal = 0;
  for (let i = 0; i < nBins; i++)
    for (let j = 0; j < nBins; j++)
      if (matrix[i][j] > maxVal) maxVal = matrix[i][j];
  if (maxVal > 0)
    for (let i = 0; i < nBins; i++)
      for (let j = 0; j < nBins; j++)
        matrix[i][j] /= maxVal;

  return matrix;
}

function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat(), flatB = b.flat();
  const muA = flatA.reduce((s, v) => s + v, 0) / flatA.length;
  const muB = flatB.reduce((s, v) => s + v, 0) / flatB.length;
  let sA2 = 0, sB2 = 0, sAB = 0;
  for (let i = 0; i < flatA.length; i++) {
    sA2 += (flatA[i] - muA) ** 2;
    sB2 += (flatB[i] - muB) ** 2;
    sAB += (flatA[i] - muA) * (flatB[i] - muB);
  }
  sA2 /= flatA.length; sB2 /= flatB.length; sAB /= flatA.length;
  const c1 = 0.0001, c2 = 0.0009;
  return ((2 * muA * muB + c1) * (2 * sAB + c2)) /
    ((muA ** 2 + muB ** 2 + c1) * (sA2 + sB2 + c2));
}

// ── Main ─────────────────────────────────────────────────────────

function main() {
  console.log("=".repeat(70));
  console.log("ARCHCODE Multi-Locus BET Inhibitor Sweep");
  console.log("=".repeat(70));
  console.log(`Loci: ${LOCI.map(l => l.name).join(", ")}`);
  console.log(`BET inhibition levels: ${BET_INHIBITION.map(b => `${b * 100}%`).join(", ")}`);
  console.log();

  const results: Array<{
    locus: string;
    tissue: string;
    tissue_match: string;
    bet_inhibition_pct: number;
    enhancer_scale: number;
    ssim_variant: number;
    delta_ssim: number;
    variant_name: string;
  }> = [];

  for (const locus of LOCI) {
    const nBins = Math.ceil((locus.simEnd - locus.simStart) / locus.resolution);
    const variantBin = Math.floor((locus.testVariant.position - locus.simStart) / locus.resolution);

    console.log(`\n--- ${locus.name} (${locus.tissue}, ${locus.tissueMatch}) ---`);
    console.log(`  Window: ${locus.simStart}-${locus.simEnd} (${(locus.simEnd - locus.simStart) / 1000}kb, ${nBins} bins)`);
    console.log(`  Variant: ${locus.testVariant.name} (bin ${variantBin}, effect=${locus.testVariant.effect})`);

    for (const inhibition of BET_INHIBITION) {
      const enhancerScale = 1 - inhibition;
      const occ = buildOccupancy(locus, enhancerScale);
      const refMap = simulateContactMap(locus, occ, -1, 1.0);
      const mutMap = simulateContactMap(locus, occ, variantBin, locus.testVariant.effect);
      const ssimVar = calculateSSIM(refMap, mutMap);

      results.push({
        locus: locus.name,
        tissue: locus.tissue,
        tissue_match: locus.tissueMatch,
        bet_inhibition_pct: Math.round(inhibition * 100),
        enhancer_scale: enhancerScale,
        ssim_variant: Math.round(ssimVar * 10000) / 10000,
        delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
        variant_name: locus.testVariant.name,
      });

      console.log(`  BET ${Math.round(inhibition * 100)}%: ΔSSIM=${(1 - ssimVar).toFixed(4)}`);
    }
  }

  // ── Save CSV ────────────────────────────────────────────────
  const outPath = path.join(process.cwd(), "analysis", "bet_sweep_multilocus.csv");
  const header = "Locus,Tissue,Tissue_Match,BET_Inhibition_Pct,Enhancer_Scale,SSIM_Variant,Delta_SSIM,Variant_Name";
  const rows = results.map(r =>
    `${r.locus},${r.tissue},${r.tissue_match},${r.bet_inhibition_pct},${r.enhancer_scale},${r.ssim_variant},${r.delta_ssim},${r.variant_name}`
  );
  fs.writeFileSync(outPath, [header, ...rows].join("\n"));
  console.log(`\n\nSaved: ${outPath} (${results.length} rows)`);

  // ── Key analysis ────────────────────────────────────────────
  console.log("\n=== BET Effect by Tissue Match ===");

  for (const match of ["matched", "partial", "mismatch"]) {
    const matchResults = results.filter(r => r.tissue_match === match);
    const lociInGroup = [...new Set(matchResults.map(r => r.locus))];

    for (const locusName of lociInGroup) {
      const locusResults = matchResults.filter(r => r.locus === locusName);
      const baseline = locusResults.find(r => r.bet_inhibition_pct === 0)?.delta_ssim || 0;
      const fullInhib = locusResults.find(r => r.bet_inhibition_pct === 100)?.delta_ssim || 0;
      const ratio = baseline > 0 ? fullInhib / baseline : 0;
      const lossPercent = baseline > 0 ? Math.round((1 - ratio) * 100) : 0;

      console.log(`  ${locusName} (${match}): baseline ΔSSIM=${baseline} → full BET=${fullInhib} (${lossPercent}% loss)`);
    }
  }

  // ── Save summary JSON ───────────────────────────────────────
  const summaryPath = path.join(process.cwd(), "analysis", "bet_sweep_multilocus_summary.json");
  const summary: Record<string, {
    tissue_match: string;
    baseline_delta: number;
    full_bet_delta: number;
    loss_pct: number;
  }> = {};

  for (const locus of LOCI) {
    const locusResults = results.filter(r => r.locus === locus.name);
    const baseline = locusResults.find(r => r.bet_inhibition_pct === 0)?.delta_ssim || 0;
    const fullBet = locusResults.find(r => r.bet_inhibition_pct === 100)?.delta_ssim || 0;
    summary[locus.name] = {
      tissue_match: locus.tissueMatch,
      baseline_delta: baseline,
      full_bet_delta: fullBet,
      loss_pct: baseline > 0 ? Math.round((1 - fullBet / baseline) * 100) : 0,
    };
  }

  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
  console.log(`Saved: ${summaryPath}`);
}

main();
