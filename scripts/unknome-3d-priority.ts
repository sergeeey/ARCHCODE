/**
 * Unknome + 3D priority: rank genes by ARCHCODE 3D-structural vulnerability.
 * Reads config/unknome_genes_subset.json; for each gene with a matching locus config,
 * runs an in-silico perturbation scan (sample bins, occupancy drop 0.05), computes
 * mean LSSIM; vulnerability score = 1 - mean(LSSIM). Higher = more vulnerable.
 *
 * Usage: npx tsx scripts/unknome-3d-priority.ts
 * Output: results/unknome_3d_priority_<YYYY-MM-DD>.json
 *
 * Claim level: EXPLORATORY (see VALIDATION_PROTOCOL.md, UNKNOME_INTEGRATION.md).
 */

import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

import {
  loadLocusConfig,
  getLocusFeatures,
} from "../src/domain/config/locus-config";
import type { LocusConfig } from "../src/domain/config/locus-config";
import {
  simulatePairedMatrices,
  calculateLocalSSIM,
} from "./lib/analyticalContact";
import type { EnhancerFeature, CtcfSiteFeature } from "./lib/analyticalContact";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SEED = 12345;
const EFFECT_STRENGTH = 0.05;
const SAMPLE_BINS = 30;
const LOCAL_SSIM_WINDOW = 50;

interface GeneEntry {
  symbol: string;
  locus_id: string;
}

interface UnknomeSubsetConfig {
  genes: GeneEntry[];
}

interface GeneResult {
  symbol: string;
  locus_id: string;
  n_bins_sampled: number;
  mean_lssim: number;
  vulnerability_score: number;
  fraction_below_095: number;
}

function sampleBins(nBins: number, maxSamples: number): number[] {
  if (nBins <= maxSamples) {
    return Array.from({ length: nBins }, (_, i) => i);
  }
  const step = nBins / (maxSamples + 1);
  return Array.from({ length: maxSamples }, (_, i) =>
    Math.min(nBins - 1, Math.floor((i + 1) * step)),
  );
}

function computeVulnerabilityForLocus(
  locusConfig: LocusConfig,
): Omit<GeneResult, "symbol" | "locus_id"> {
  const features = getLocusFeatures(locusConfig);
  const { window } = locusConfig;
  const nBins = window.n_bins;
  const geometry = {
    windowStart: window.start,
    resolution: window.resolution_bp,
    nBins,
  };
  const enhancers: EnhancerFeature[] = features.enhancers.map((e) => ({
    position: e.position,
    occupancy: e.occupancy,
    name: e.name,
  }));
  const ctcfSites: CtcfSiteFeature[] = features.ctcfSites.map((c) => ({
    position: c.position,
    orientation: c.orientation,
  }));

  const bins = sampleBins(nBins, SAMPLE_BINS);
  const windowSize = Math.min(LOCAL_SSIM_WINDOW, nBins);
  const lssims: number[] = [];

  for (const bin of bins) {
    const { reference, mutant } = simulatePairedMatrices(
      geometry,
      enhancers,
      ctcfSites,
      bin,
      EFFECT_STRENGTH,
      "promoter",
      SEED + bin,
    );
    const lssim = calculateLocalSSIM(reference, mutant, bin, windowSize);
    lssims.push(lssim);
  }

  const meanLssim =
    lssims.reduce((a, b) => a + b, 0) / lssims.length;
  const fractionBelow095 = lssims.filter((x) => x < 0.95).length / lssims.length;

  return {
    n_bins_sampled: bins.length,
    mean_lssim: Math.round(meanLssim * 1e4) / 1e4,
    vulnerability_score: Math.round((1 - meanLssim) * 1e4) / 1e4,
    fraction_below_095: Math.round(fractionBelow095 * 1e4) / 1e4,
  };
}

function main(): void {
  const repoRoot = path.join(__dirname, "..");
  const configPath = path.join(repoRoot, "config", "unknome_genes_subset.json");
  const raw = fs.readFileSync(configPath, "utf-8");
  const config = JSON.parse(raw) as UnknomeSubsetConfig;
  const locusDir = path.join(repoRoot, "config", "locus");

  const results: GeneResult[] = [];

  for (const gene of config.genes) {
    const locusPath = path.join(locusDir, `${gene.locus_id}.json`);
    if (!fs.existsSync(locusPath)) {
      console.warn(`Locus config not found: ${locusPath}; skipping ${gene.symbol}`);
      continue;
    }
    const locusConfig = loadLocusConfig(locusPath);
    const metrics = computeVulnerabilityForLocus(locusConfig);
    results.push({
      symbol: gene.symbol,
      locus_id: gene.locus_id,
      ...metrics,
    });
  }

  results.sort((a, b) => b.vulnerability_score - a.vulnerability_score);

  const dateStr = new Date().toISOString().slice(0, 10);
  const outPath = path.join(repoRoot, "results", `unknome_3d_priority_${dateStr}.json`);
  const out = {
    analysis: "Unknome 3D-guided priority (prototype)",
    date: dateStr,
    claim_level: "EXPLORATORY",
    provenance: "ARCHCODE in-silico perturbation; config/unknome_genes_subset.json",
    parameters: {
      effect_strength: EFFECT_STRENGTH,
      sample_bins: SAMPLE_BINS,
      local_ssim_window: LOCAL_SSIM_WINDOW,
      seed: SEED,
    },
    genes: results,
  };
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(out, null, 2), "utf-8");
  console.log(`Wrote ${outPath} (${results.length} genes)`);
}

main();
