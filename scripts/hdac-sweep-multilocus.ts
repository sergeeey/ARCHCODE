/**
 * ARCHCODE Multi-Locus HDAC Inhibitor Sweep
 * ==========================================
 * Models HDAC inhibitor effects on structural variant discrimination.
 *
 * HDAC inhibitors (vorinostat/SAHA, panobinostat, valproic acid) increase
 * histone acetylation → two structural effects:
 *   1. Enhancer hyperactivation: ↑ H3K27ac → ↑ enhancer occupancy
 *   2. CTCF barrier weakening: open chromatin reduces CTCF binding context
 *
 * This creates a 2D parameter sweep (enhancerBoost × ctcfRetention),
 * complementing the 1D BET inhibitor sweep (enhancerScale ↓ only).
 *
 * BET = suppresses enhancers → structural discrimination ↓
 * HDAC-i = boosts enhancers + weakens barriers → ???
 *
 * MANUALLY CALIBRATED: enhancerBoost 1.0–2.0× and ctcfRetention 0.25–1.0
 * represent plausible ranges, not fitted to experimental dose-response.
 *
 * Usage: npx tsx scripts/hdac-sweep-multilocus.ts
 */

import * as fs from "fs";
import * as path from "path";
import { KRAMER_KINETICS } from "../src/domain/constants/biophysics";
import { SeededRandom } from "../src/utils/random";

// ── Locus definitions (same as BET sweep for comparability) ─────

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

// ── HDAC inhibition parameters ──────────────────────────────────
// MANUALLY CALIBRATED ranges — not fitted to experimental dose-response

// Enhancer boost: HDAC-i → ↑ H3K27ac → enhancer occupancy scales up
// 1.0 = baseline, 1.5 = moderate HDAC-i (e.g. low-dose valproic acid),
// 2.0 = strong HDAC-i (e.g. panobinostat)
const ENHANCER_BOOST_LEVELS = [1.0, 1.25, 1.5, 1.75, 2.0];

// CTCF retention: HDAC-i → open chromatin → CTCF binding context weakens
// 1.0 = full CTCF blocking (baseline), 0.25 = severely weakened
// Literature: CTCF binding is partially acetylation-dependent (Splinter 2006)
const CTCF_RETENTION_LEVELS = [1.0, 0.75, 0.50, 0.25];

const BASE_CTCF_BLOCKING = 0.85; // same as BET sweep and fragility atlas

// ── Simulation engine ───────────────────────────────────────────

function buildOccupancy(
  locus: LocusConfig,
  enhancerBoost: number,
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
        // HDAC-i boosts enhancer occupancy (more H3K27ac → more MED1/coactivator)
        occ += enh.occupancy * enhancerBoost * Math.exp(-0.5 * dist * dist);
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
  ctcfRetention: number,
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

  // HDAC-i weakens CTCF blocking: effective blocking = base × retention
  const effectiveBlocking = BASE_CTCF_BLOCKING * ctcfRetention;

  const matrix: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);
      const occFactor = Math.sqrt(modOccupancy[i] * modOccupancy[j]);

      let perm = 1.0;
      for (const ctcf of ctcfBins) {
        if (ctcf > i && ctcf < j) perm *= (1 - effectiveBlocking);
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

// ── Main ────────────────────────────────────────────────────────

function main() {
  console.log("=".repeat(70));
  console.log("ARCHCODE Multi-Locus HDAC Inhibitor Sweep (2D Parameter Space)");
  console.log("=".repeat(70));
  console.log(`Loci: ${LOCI.map(l => l.name).join(", ")}`);
  console.log(`Enhancer boost levels: ${ENHANCER_BOOST_LEVELS.map(b => `${b}×`).join(", ")}`);
  console.log(`CTCF retention levels: ${CTCF_RETENTION_LEVELS.map(r => `${Math.round(r * 100)}%`).join(", ")}`);
  console.log(`Total conditions per locus: ${ENHANCER_BOOST_LEVELS.length * CTCF_RETENTION_LEVELS.length}`);
  console.log();

  const results: Array<{
    locus: string;
    tissue: string;
    tissue_match: string;
    enhancer_boost: number;
    ctcf_retention: number;
    effective_ctcf_blocking: number;
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

    for (const boost of ENHANCER_BOOST_LEVELS) {
      for (const retention of CTCF_RETENTION_LEVELS) {
        const occ = buildOccupancy(locus, boost);
        const refMap = simulateContactMap(locus, occ, -1, 1.0, retention);
        const mutMap = simulateContactMap(locus, occ, variantBin, locus.testVariant.effect, retention);
        const ssimVar = calculateSSIM(refMap, mutMap);

        results.push({
          locus: locus.name,
          tissue: locus.tissue,
          tissue_match: locus.tissueMatch,
          enhancer_boost: boost,
          ctcf_retention: retention,
          effective_ctcf_blocking: Math.round(BASE_CTCF_BLOCKING * retention * 1000) / 1000,
          ssim_variant: Math.round(ssimVar * 10000) / 10000,
          delta_ssim: Math.round((1 - ssimVar) * 10000) / 10000,
          variant_name: locus.testVariant.name,
        });
      }
    }

    // Print summary for this locus
    const baseline = results.find(r => r.locus === locus.name && r.enhancer_boost === 1.0 && r.ctcf_retention === 1.0);
    const maxBoost = results.find(r => r.locus === locus.name && r.enhancer_boost === 2.0 && r.ctcf_retention === 0.25);
    if (baseline && maxBoost) {
      const changePct = baseline.delta_ssim > 0
        ? Math.round(((maxBoost.delta_ssim - baseline.delta_ssim) / baseline.delta_ssim) * 100)
        : 0;
      console.log(`  Baseline ΔSSIM=${baseline.delta_ssim} → Max HDAC-i ΔSSIM=${maxBoost.delta_ssim} (${changePct > 0 ? "+" : ""}${changePct}%)`);
    }
  }

  // ── Save CSV ──────────────────────────────────────────────
  const outPath = path.join(process.cwd(), "analysis", "hdac_sweep_multilocus.csv");
  const header = "Locus,Tissue,Tissue_Match,Enhancer_Boost,CTCF_Retention,Effective_CTCF_Blocking,SSIM_Variant,Delta_SSIM,Variant_Name";
  const rows = results.map(r =>
    `${r.locus},${r.tissue},${r.tissue_match},${r.enhancer_boost},${r.ctcf_retention},${r.effective_ctcf_blocking},${r.ssim_variant},${r.delta_ssim},${r.variant_name}`
  );
  fs.writeFileSync(outPath, [header, ...rows].join("\n"));
  console.log(`\n\nSaved: ${outPath} (${results.length} rows)`);

  // ── Comparative analysis: BET vs HDAC ─────────────────────
  console.log("\n" + "=".repeat(70));
  console.log("=== HDAC-i Effect Summary by Tissue Match ===");
  console.log("=".repeat(70));

  const summaryByLocus: Record<string, {
    tissue_match: string;
    baseline_delta: number;
    // Enhancer-only effect (max boost, full CTCF)
    enhancer_only_delta: number;
    enhancer_only_change_pct: number;
    // CTCF-only effect (no boost, min CTCF)
    ctcf_only_delta: number;
    ctcf_only_change_pct: number;
    // Combined max effect
    combined_max_delta: number;
    combined_max_change_pct: number;
    // Dominant axis
    dominant_axis: "enhancer" | "ctcf" | "balanced";
  }> = {};

  for (const locus of LOCI) {
    const locusResults = results.filter(r => r.locus === locus.name);
    const baseline = locusResults.find(r => r.enhancer_boost === 1.0 && r.ctcf_retention === 1.0)!;
    const enhOnly = locusResults.find(r => r.enhancer_boost === 2.0 && r.ctcf_retention === 1.0)!;
    const ctcfOnly = locusResults.find(r => r.enhancer_boost === 1.0 && r.ctcf_retention === 0.25)!;
    const combined = locusResults.find(r => r.enhancer_boost === 2.0 && r.ctcf_retention === 0.25)!;

    const enhChange = baseline.delta_ssim > 0
      ? Math.round(((enhOnly.delta_ssim - baseline.delta_ssim) / baseline.delta_ssim) * 100) : 0;
    const ctcfChange = baseline.delta_ssim > 0
      ? Math.round(((ctcfOnly.delta_ssim - baseline.delta_ssim) / baseline.delta_ssim) * 100) : 0;
    const combChange = baseline.delta_ssim > 0
      ? Math.round(((combined.delta_ssim - baseline.delta_ssim) / baseline.delta_ssim) * 100) : 0;

    const enhMag = Math.abs(enhChange);
    const ctcfMag = Math.abs(ctcfChange);
    const dominant = enhMag > ctcfMag * 1.5 ? "enhancer" as const
      : ctcfMag > enhMag * 1.5 ? "ctcf" as const
      : "balanced" as const;

    summaryByLocus[locus.name] = {
      tissue_match: locus.tissueMatch,
      baseline_delta: baseline.delta_ssim,
      enhancer_only_delta: enhOnly.delta_ssim,
      enhancer_only_change_pct: enhChange,
      ctcf_only_delta: ctcfOnly.delta_ssim,
      ctcf_only_change_pct: ctcfChange,
      combined_max_delta: combined.delta_ssim,
      combined_max_change_pct: combChange,
      dominant_axis: dominant,
    };

    console.log(`\n  ${locus.name} (${locus.tissueMatch}):`);
    console.log(`    Baseline ΔSSIM = ${baseline.delta_ssim}`);
    console.log(`    Enhancer 2.0× only: ΔSSIM = ${enhOnly.delta_ssim} (${enhChange > 0 ? "+" : ""}${enhChange}%)`);
    console.log(`    CTCF 25% only:      ΔSSIM = ${ctcfOnly.delta_ssim} (${ctcfChange > 0 ? "+" : ""}${ctcfChange}%)`);
    console.log(`    Combined max:        ΔSSIM = ${combined.delta_ssim} (${combChange > 0 ? "+" : ""}${combChange}%)`);
    console.log(`    Dominant axis: ${dominant}`);
  }

  // ── BET comparison (load if exists) ───────────────────────
  const betPath = path.join(process.cwd(), "analysis", "bet_sweep_multilocus.csv");
  let betComparison: Record<string, { bet_full_delta: number; bet_loss_pct: number }> = {};

  if (fs.existsSync(betPath)) {
    const betLines = fs.readFileSync(betPath, "utf-8").split("\n").slice(1);
    const betData: Array<{ locus: string; inhibition: number; delta: number }> = [];

    for (const line of betLines) {
      if (!line.trim()) continue;
      const parts = line.split(",");
      betData.push({
        locus: parts[0],
        inhibition: parseFloat(parts[3]),
        delta: parseFloat(parts[6]),
      });
    }

    console.log("\n" + "=".repeat(70));
    console.log("=== BET vs HDAC-i Comparison (Pharmacological Landscape) ===");
    console.log("=".repeat(70));

    for (const locus of LOCI) {
      const betBaseline = betData.find(r => r.locus === locus.name && r.inhibition === 0);
      const betFull = betData.find(r => r.locus === locus.name && r.inhibition === 100);
      const hdacData = summaryByLocus[locus.name];

      if (betBaseline && betFull && hdacData) {
        const betLoss = betBaseline.delta > 0
          ? Math.round((1 - betFull.delta / betBaseline.delta) * 100) : 0;

        betComparison[locus.name] = {
          bet_full_delta: betFull.delta,
          bet_loss_pct: betLoss,
        };

        console.log(`\n  ${locus.name} (${hdacData.tissue_match}):`);
        console.log(`    Baseline:    ΔSSIM = ${hdacData.baseline_delta}`);
        console.log(`    BET 100%:    ΔSSIM = ${betFull.delta} (−${betLoss}% discrimination)`);
        console.log(`    HDAC-i max:  ΔSSIM = ${hdacData.combined_max_delta} (${hdacData.combined_max_change_pct > 0 ? "+" : ""}${hdacData.combined_max_change_pct}% discrimination)`);
        console.log(`    → BET suppresses, HDAC-i ${hdacData.combined_max_change_pct > 0 ? "ENHANCES" : "also suppresses"} structural discrimination`);
      }
    }
  }

  // ── Save summary JSON ─────────────────────────────────────
  const summaryPath = path.join(process.cwd(), "analysis", "hdac_sweep_multilocus_summary.json");
  const summaryJson = {
    analysis: "ARCHCODE Multi-Locus HDAC Inhibitor 2D Sweep",
    version: "v1.0",
    date: new Date().toISOString().split("T")[0],
    parameters: {
      enhancer_boost_levels: ENHANCER_BOOST_LEVELS,
      ctcf_retention_levels: CTCF_RETENTION_LEVELS,
      base_ctcf_blocking: BASE_CTCF_BLOCKING,
      calibration: "MANUALLY CALIBRATED — plausible ranges, not fitted to experimental dose-response",
    },
    n_loci: LOCI.length,
    n_conditions_per_locus: ENHANCER_BOOST_LEVELS.length * CTCF_RETENTION_LEVELS.length,
    total_simulations: results.length,
    per_locus: summaryByLocus,
    bet_comparison: Object.keys(betComparison).length > 0 ? betComparison : "BET sweep data not found — run bet-sweep-multilocus.ts first",
  };
  fs.writeFileSync(summaryPath, JSON.stringify(summaryJson, null, 2));
  console.log(`\nSaved: ${summaryPath}`);
}

main();
