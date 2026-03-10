/**
 * Locus configuration loader for ARCHCODE.
 *
 * ПОЧЕМУ выносим в конфиг: один пайплайн (generate-unified-atlas.ts)
 * должен работать для разных геномных окон (30kb, 95kb) без
 * дублирования кода. JSON конфиг содержит source provenance
 * на каждой feature (Scientific Integrity Protocol).
 */

import * as fs from "fs";
import * as path from "path";

// ============================================================================
// Types
// ============================================================================

export interface EnhancerFeature {
  position: number;
  occupancy: number;
  name: string;
  source: string;
  note?: string;
}

export interface CtcfFeature {
  position: number;
  orientation: string;
  source: string;
  signal?: number;
  name?: string;
  encode_accession?: string;
  note?: string;
}

export interface GeneFeature {
  name: string;
  start: number;
  end: number;
  strand: string;
}

export interface SsimThresholds {
  ssim_pathogenic: number;
  ssim_likely_pathogenic: number;
  ssim_vus: number;
  ssim_likely_benign: number;
  note?: string;
}

export interface LocusConfig {
  id: string;
  name: string;
  description: string;
  genome_assembly: string;
  window: {
    chromosome: string;
    start: number;
    end: number;
    resolution_bp: number;
    n_bins: number;
  };
  features: {
    enhancers: EnhancerFeature[];
    ctcf_sites: CtcfFeature[];
    genes: GeneFeature[];
  };
  thresholds: SsimThresholds | null;
}

// ============================================================================
// Aliases for backward compatibility with existing code shape
// ============================================================================

/** Maps config ctcf_sites to the { position, orientation } shape used by the simulation engine */
export function getLocusFeatures(config: LocusConfig) {
  return {
    enhancers: config.features.enhancers.map((e) => ({
      position: e.position,
      occupancy: e.occupancy,
      name: e.name,
    })),
    ctcfSites: config.features.ctcf_sites.map((c) => ({
      position: c.position,
      orientation: c.orientation,
    })),
  };
}

// ============================================================================
// Config resolution
// ============================================================================

const CONFIG_DIR = path.join(process.cwd(), "config", "locus");

const ALIASES: Record<string, string> = {
  "30kb": "hbb_30kb_v2.json",
  "95kb": "hbb_95kb_subTAD.json",
  cftr: "cftr_317kb.json",
  tp53: "tp53_300kb.json",
  brca1: "brca1_400kb.json",
  mlh1: "mlh1_300kb.json",
  mlh1_hct116: "mlh1_hct116_300kb.json",
  cftr_a549: "cftr_a549_317kb.json",
  tert_skn_sh: "tert_skn_sh_300kb.json",
  tp53_imr90: "tp53_imr90_300kb.json",
  ldlr: "ldlr_300kb.json",
  scn5a: "scn5a_400kb.json",
  scn5a_cardiac: "scn5a_cardiac_250kb.json",
  ldlr_k562: "ldlr_k562_300kb.json",
  brca1_k562: "brca1_k562_400kb.json",
  tert: "tert_300kb.json",
  gjb2: "gjb2_300kb.json",
  mouse_hbb: "mouse_hbb_130kb.json",
  hba1: "hba1_300kb.json",
  gata1: "gata1_300kb.json",
  bcl11a: "bcl11a_300kb.json",
  pten: "pten_300kb.json",
};

/**
 * Resolve a locus shorthand ("30kb", "95kb") or filename to a full path.
 */
export function resolveLocusPath(arg: string): string {
  const filename = ALIASES[arg] ?? arg;
  const fullPath =
    filename.includes(path.sep) || filename.includes("/")
      ? filename
      : path.join(CONFIG_DIR, filename);

  if (!fs.existsSync(fullPath)) {
    throw new Error(
      `Locus config not found: ${fullPath}\n` +
        `Available aliases: ${Object.keys(ALIASES).join(", ")}`,
    );
  }
  return fullPath;
}

/**
 * Load and validate a locus configuration from JSON.
 */
export function loadLocusConfig(filePath: string): LocusConfig {
  const raw = fs.readFileSync(filePath, "utf-8");
  const config = JSON.parse(raw) as LocusConfig;

  // Validate n_bins matches window geometry
  const expectedBins = Math.ceil(
    (config.window.end - config.window.start) / config.window.resolution_bp,
  );
  if (config.window.n_bins !== expectedBins) {
    throw new Error(
      `n_bins mismatch in ${filePath}: declared ${config.window.n_bins}, ` +
        `computed ${expectedBins} from (${config.window.end}-${config.window.start})/${config.window.resolution_bp}`,
    );
  }

  return config;
}

/**
 * Parse --locus argument from process.argv.
 * Returns the alias string (default: "30kb").
 */
export function parseLocusArg(argv: string[] = process.argv): string {
  const idx = argv.indexOf("--locus");
  if (idx === -1 || idx + 1 >= argv.length) {
    return "30kb";
  }
  return argv[idx + 1];
}
