/**
 * BED file parser for CTCF sites
 * TypeScript port of load_ctcf_from_bed from Python
 *
 * BED format (tab-separated):
 *   chrom  start  end  name  score  strand
 */

import {
  CTCFSite,
  CTCFOrientation,
  createCTCFSite,
} from "../domain/models/genome";

export interface BEDParseOptions {
  chromFilter?: string;
  minScore?: number;
}

export interface BEDParseResult {
  sites: CTCFSite[];
  skipped: number;
  parsed: number;
}

/**
 * Parse a single BED line
 */
function parseBEDLine(
  line: string,
  lineNum: number,
  options: BEDParseOptions,
): { site?: CTCFSite; skip?: string } {
  const trimmed = line.trim();

  // Skip empty lines and comments
  if (!trimmed || trimmed.startsWith("#")) {
    return { skip: "empty_or_comment" };
  }

  const parts = trimmed.split("\t");

  // BED6 requires at least 6 columns
  if (parts.length < 6) {
    return { skip: " insufficient_columns" };
  }

  const [chrom, startS, endS, _name, scoreS, strand] = parts;

  // Apply chromosome filter
  if (options.chromFilter && chrom !== options.chromFilter) {
    return { skip: "chromosome_filtered" };
  }

  // Parse coordinates
  const start = parseInt(startS, 10);
  const end = parseInt(endS, 10);
  if (isNaN(start) || isNaN(end)) {
    return { skip: "invalid_coordinates" };
  }

  // Parse score (optional filtering)
  const score = parseFloat(scoreS);
  const minScore = options.minScore ?? 0.0;
  if (!isNaN(score) && score < minScore) {
    return { skip: "low_score" };
  }

  // Compute midpoint
  const mid = Math.floor((start + end) / 2);

  // Map strand to orientation
  let orientation: CTCFOrientation;
  if (strand === "+") {
    orientation = "F";
  } else if (strand === "-") {
    orientation = "R";
  } else {
    return { skip: "undefined_strand" };
  }

  const site = createCTCFSite(chrom, mid, orientation, 1.0);
  return { site };
}

/**
 * Load CTCF sites from BED file content
 */
export function loadCTCFFromBED(
  bedContent: string,
  options: BEDParseOptions = {},
): BEDParseResult {
  const sites: CTCFSite[] = [];
  let skipped = 0;

  const lines = bedContent.split("\n");

  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    const result = parseBEDLine(line, lineNum + 1, options);

    if (result.site) {
      sites.push(result.site);
    } else {
      skipped++;
    }
  }

  // Sort by position
  sites.sort((a, b) => a.position - b.position);

  return { sites, skipped, parsed: sites.length };
}

/**
 * Load CTCF sites from BED file (async for file API)
 */
export async function loadCTCFFromBEDFile(
  file: File,
  options: BEDParseOptions = {},
): Promise<BEDParseResult> {
  const content = await file.text();
  return loadCTCFFromBED(content, options);
}

/**
 * Generate sample BED data with CONVERGENT CTCF pairs
 * Format: F (> ) ... R (< ) = convergent, forms loop
 */
export function generateSampleBED(
  chromosome: string = "chr11",
  nSites: number = 6, // 6 sites = 3 convergent pairs
  startPos: number = 5240000, // HBB locus: 5.24-5.34 Mb
  spacing: number = 40000, // 40kb between pairs
): string {
  const lines: string[] = [
    "# Sample CTCF BED file for ARCHCODE testing",
    "# Format: chrom start end name score strand",
    "# Convergent pairs: F (> ) at left, R (< ) at right",
    "# chr11:5,240,000 (+) F -- chr11:5,280,000 (-) R = LOOP",
    "",
  ];

  // Create CONVERGENT pairs: F ... R (forms loop)
  // Pair 1: F@5.24M + R@5.28M = 40kb loop
  lines.push(`${chromosome}\t5239750\t5240250\tCTCF_F_1\t1000\t+`);
  lines.push(`${chromosome}\t5279750\t5280250\tCTCF_R_1\t950\t-`);

  // Pair 2: F@5.30M + R@5.34M = 40kb loop
  lines.push(`${chromosome}\t5299750\t5300250\tCTCF_F_2\t900\t+`);
  lines.push(`${chromosome}\t5339750\t5340250\tCTCF_R_2\t850\t-`);

  // Pair 3: F@5.36M + R@5.40M = 40kb loop
  lines.push(`${chromosome}\t5359750\t5360250\tCTCF_F_3\t800\t+`);
  lines.push(`${chromosome}\t5399750\t5400250\tCTCF_R_3\t750\t-`);

  return lines.join("\n");
}

/**
 * Convert CTCF sites to BED format string
 */
export function sitesToBED(sites: CTCFSite[]): string {
  const lines = sites.map((site) => {
    const start = site.position - 250;
    const end = site.position + 250;
    const strand = site.orientation === "F" ? "+" : "-";
    return `${site.chrom}\t${start}\t${end}\tCTCF_${site.position}\t${Math.floor(site.strength * 1000)}\t${strand}`;
  });

  return lines.join("\n");
}
