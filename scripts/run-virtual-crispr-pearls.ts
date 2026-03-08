/**
 * Virtual CRISPR (V-CRISPR): in silico knockout of top-3 HBB pearl variants.
 * Uses analytical contact simulation (same as unified atlas); computes
 * promoter–LCR contact drop and LSSIM for each pearl.
 *
 * Usage: npx tsx scripts/run-virtual-crispr-pearls.ts
 * Output: results/virtual_crispr_pearls.json, manuscript/TABLE_VCRISPR_TOP3.md
 */

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

import {
  loadLocusConfig,
  resolveLocusPath,
  getLocusFeatures,
} from "../src/domain/config/locus-config";
import type { LocusConfig } from "../src/domain/config/locus-config";
import {
  simulatePairedMatrices,
  calculateLocalSSIM,
  computePromoterLCRContact,
  type EnhancerFeature,
  type CtcfSiteFeature,
} from "./lib/analyticalContact";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const VCRISPR_SEED = 42;
const KO_EFFECT_STRENGTH = 0.05; // 95% occupancy reduction at variant bin
const LOCAL_SSIM_WINDOW = 50;

interface PearlInput {
  position: number;
  hgvs_c: string;
  clinvar_id: string;
  category: string;
}

interface PearlResult {
  position: number;
  hgvs_c: string;
  clinvar_id: string;
  category: string;
  variant_bin: number;
  contact_wt: number;
  contact_ko: number;
  contact_drop_pct: number;
  lssim: number;
}

function posToBin(position: number, windowStart: number, resolution: number): number {
  return Math.max(0, Math.floor((position - windowStart) / resolution));
}

function main(): void {
  const repoRoot = path.join(__dirname, "..");
  const locusPath = resolveLocusPath("95kb");
  const locusConfig: LocusConfig = loadLocusConfig(locusPath);
  const features = getLocusFeatures(locusConfig);

  const windowStart = locusConfig.window.start;
  const resolution = locusConfig.window.resolution_bp;
  const nBins = locusConfig.window.n_bins;

  const geometry = { windowStart, resolution, nBins };
  const enhancers: EnhancerFeature[] = features.enhancers.map((e) => ({
    position: e.position,
    occupancy: e.occupancy,
    name: e.name,
  }));
  const ctcfSites: CtcfSiteFeature[] = features.ctcfSites.map((c) => ({
    position: c.position,
    orientation: c.orientation,
  }));

  // Promoter = HBB_promoter (5226268); LCR = HS2, HS3 from config
  const promoterPos = 5226268;
  const lcrPositions = [5280700, 5284800]; // HS2, HS3
  const promoterBin = posToBin(promoterPos, windowStart, resolution);
  const lcrBins = lcrPositions.map((p) => posToBin(p, windowStart, resolution));

  const pearlsPath = path.join(repoRoot, "config", "pearls_vcrispr_top3.json");
  const pearlsConfig = JSON.parse(
    fs.readFileSync(pearlsPath, "utf-8"),
  ) as { pearls: PearlInput[] };
  const pearls: PearlInput[] = pearlsConfig.pearls;

  const results: PearlResult[] = [];

  for (const pearl of pearls) {
    const variantBin = posToBin(pearl.position, windowStart, resolution);
    if (variantBin < 0 || variantBin >= nBins) {
      console.warn(
        `Pearl ${pearl.clinvar_id} position ${pearl.position} outside window; skipping`,
      );
      continue;
    }

    // WT: no variant (variantBin = -1, effectStrength not used for ref)
    const { reference: refMatrix, mutant: mutMatrix } = simulatePairedMatrices(
      geometry,
      enhancers,
      ctcfSites,
      -1,
      1,
      "other",
      VCRISPR_SEED,
    );

    // KO: virtual knockout at variant bin (95% occupancy reduction, promoter category for CTCF removal near variant)
    const { mutant: koMatrix } = simulatePairedMatrices(
      geometry,
      enhancers,
      ctcfSites,
      variantBin,
      KO_EFFECT_STRENGTH,
      pearl.category,
      VCRISPR_SEED,
    );

    const contactWt = computePromoterLCRContact(refMatrix, promoterBin, lcrBins);
    const contactKo = computePromoterLCRContact(koMatrix, promoterBin, lcrBins);
    const contactDropPct =
      contactWt > 0 ? ((contactWt - contactKo) / contactWt) * 100 : 0;
    const lssim = calculateLocalSSIM(
      refMatrix,
      koMatrix,
      variantBin,
      LOCAL_SSIM_WINDOW,
    );

    results.push({
      position: pearl.position,
      hgvs_c: pearl.hgvs_c,
      clinvar_id: pearl.clinvar_id,
      category: pearl.category,
      variant_bin: variantBin,
      contact_wt: contactWt,
      contact_ko: contactKo,
      contact_drop_pct: contactDropPct,
      lssim,
    });
  }

  const report = {
    experiment: "Virtual CRISPR (V-CRISPR) — top-3 HBB pearls",
    generated_at_utc: new Date().toISOString(),
    parameters: {
      locus: "95kb",
      locus_id: locusConfig.id,
      window: locusConfig.window,
      ko_effect_strength: KO_EFFECT_STRENGTH,
      seed: VCRISPR_SEED,
      promoter_bin: promoterBin,
      promoter_position: promoterPos,
      lcr_bins: lcrBins,
      lcr_positions: lcrPositions,
    },
    results,
    note: "In silico prediction. Wet-lab validation remains required (CLAUDE.md).",
  };

  const outDir = path.join(repoRoot, "results");
  fs.mkdirSync(outDir, { recursive: true });
  const jsonPath = path.join(outDir, "virtual_crispr_pearls.json");
  fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2), "utf-8");
  console.log(`Written: ${jsonPath}`);

  // Table for manuscript
  const tableLines = [
    "| ClinVar ID | HGVS_c | Position | Contact drop (%) | LSSIM (KO vs WT) |",
    "| ---------- | ------ | -------- | ----------------- | ----------------- |",
    ...results.map(
      (r) =>
        `| ${r.clinvar_id} | ${r.hgvs_c} | ${r.position} | ${r.contact_drop_pct.toFixed(1)} | ${r.lssim.toFixed(4)} |`,
    ),
  ];
  const tableMd = [
    "# Table: Virtual CRISPR (V-CRISPR) — Top-3 HBB Pearl Variants",
    "",
    "In silico knockout: occupancy reduced to 5% at variant bin (95% reduction).",
    "Contact = mean promoter–LCR (HBB_promoter ↔ HS2, HS3) contact frequency.",
    "LSSIM = local SSIM (50×50 window) between WT and KO matrices.",
    "",
    ...tableLines,
    "",
    "_Source: results/virtual_crispr_pearls.json. In silico prediction; wet-lab validation required._",
  ].join("\n");

  const manuscriptDir = path.join(repoRoot, "manuscript");
  const tablePath = path.join(manuscriptDir, "TABLE_VCRISPR_TOP3.md");
  fs.mkdirSync(manuscriptDir, { recursive: true });
  fs.writeFileSync(tablePath, tableMd, "utf-8");
  console.log(`Written: ${tablePath}`);

  console.log("");
  console.log("V-CRISPR summary:");
  for (const r of results) {
    console.log(
      `  ${r.clinvar_id} ${r.hgvs_c}: contact drop ${r.contact_drop_pct.toFixed(1)}%, LSSIM ${r.lssim.toFixed(4)}`,
    );
  }
}

main();
