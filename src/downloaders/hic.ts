/**
 * Hi-C Data Downloader
 * Downloads real Hi-C loop calls for validation against simulation
 *
 * Sources:
 * - Rao et al. 2014 (GEO: GSE63525) - HiCCUPS loop calls
 * - 4D Nucleome (4DN) Data Portal
 *
 * Literature: Rao et al. (2014) Cell - "A 3D Map of the Human Genome"
 *
 * Strategy: Download HiCCUPS loop lists (text format) rather than raw matrices.
 * This is more appropriate for validating loop extrusion simulations.
 */

import { ContactMatrix, Loop } from "../domain/models/genome";

// ============================================================================
// Loop List Datasets (text format, easy to download)
// ============================================================================

export interface LoopListDataset {
  id: string;
  source: "rao2014" | "4dn" | "encode";
  cellLine: string;
  description: string;
  url: string;
  chromosome?: string;
  region?: { start: number; end: number };
}

export const RAO_2014_LOOP_DATASETS: LoopListDataset[] = [
  {
    id: "rao2014_gm12878_loops",
    source: "rao2014",
    cellLine: "GM12878",
    description: "HiCCUPS loop calls from GM12878 (primary)",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_GM12878_primary_HiCCUPS_looplist.txt.gz",
  },
  {
    id: "rao2014_gm12878_loops_replicate",
    source: "rao2014",
    cellLine: "GM12878",
    description: "HiCCUPS loop calls from GM12878 (replicate)",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_GM12878_replicate_HiCCUPS_looplist.txt.gz",
  },
  {
    id: "rao2014_gm12878_loops_combined",
    source: "rao2014",
    cellLine: "GM12878",
    description: "HiCCUPS loop calls from GM12878 (primary+replicate)",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_GM12878_primary%2Breplicate_HiCCUPS_looplist.txt.gz",
  },
  {
    id: "rao2014_k562_loops",
    source: "rao2014",
    cellLine: "K562",
    description: "HiCCUPS loop calls from K562",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_K562_HiCCUPS_looplist.txt.gz",
  },
  {
    id: "rao2014_imr90_loops",
    source: "rao2014",
    cellLine: "IMR90",
    description: "HiCCUPS loop calls from IMR90 fibroblasts",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_IMR90_HiCCUPS_looplist.txt.gz",
  },
  {
    id: "rao2014_hmec_loops",
    source: "rao2014",
    cellLine: "HMEC",
    description: "HiCCUPS loop calls from HMEC mammary epithelial",
    url: "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_HMEC_HiCCUPS_looplist.txt.gz",
  },
];

// ============================================================================
// Types
// ============================================================================

export interface HiCLoop {
  chr1: string;
  x1: number;
  x2: number;
  chr2: string;
  y1: number;
  y2: number;
  color: string;
  observedValue: number;
  expectedValue: number;
  fdrDonut: number;
  fdrHorizontal: number;
  fdrVertical: number;
  numCollapsed: number;
  centroid1: number;
  centroid2: number;
  radius: number;
}

export interface LoopDownloadProgress {
  loaded: number;
  total: number;
  percent: number;
  stage: "downloading" | "decompressing" | "parsing";
}

export interface LoopDownloadResult {
  success: boolean;
  datasetId: string;
  cellLine: string;
  loops?: HiCLoop[];
  loopCount?: number;
  error?: string;
}

// ============================================================================
// Download Functions
// ============================================================================

/**
 * Decompress gzip data using Web Streams API
 */
async function decompressGzip(data: Uint8Array): Promise<Uint8Array> {
  const stream = new Response(data).body;
  if (!stream) throw new Error("No stream available");

  const decompressed = stream.pipeThrough(new DecompressionStream("gzip"));
  const reader = decompressed.getReader();

  const chunks: Uint8Array[] = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }

  const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const result = new Uint8Array(totalLength);
  let position = 0;
  for (const chunk of chunks) {
    result.set(chunk, position);
    position += chunk.length;
  }

  return result;
}

/**
 * Parse HiCCUPS loop list format
 * Format: chr1 x1 x2 chr2 y1 y2 color o e_bl e_donut e_h e_v fdr_bl fdr_donut fdr_h fdr_v num_collapsed centroid1 centroid2 radius
 */
function parseLoopList(content: string): HiCLoop[] {
  const lines = content.trim().split("\n");
  const loops: HiCLoop[] = [];

  for (const line of lines) {
    // Skip header
    if (line.startsWith("chr1") || line.startsWith("#")) continue;

    const parts = line.split("\t");
    if (parts.length < 14) continue;

    try {
      loops.push({
        chr1: parts[0],
        x1: parseInt(parts[1]),
        x2: parseInt(parts[2]),
        chr2: parts[3],
        y1: parseInt(parts[4]),
        y2: parseInt(parts[5]),
        color: parts[6] || "0,0,255",
        observedValue: parseFloat(parts[7]) || 0,
        expectedValue: parseFloat(parts[8]) || 0,
        fdrDonut: parseFloat(parts[9]) || 0,
        fdrHorizontal: parseFloat(parts[10]) || 0,
        fdrVertical: parseFloat(parts[11]) || 0,
        numCollapsed: parseInt(parts[12]) || 1,
        centroid1: parseInt(parts[13]) || 0,
        centroid2: parseInt(parts[14]) || 0,
        radius: parseInt(parts[15]) || 0,
      });
    } catch {
      // Skip malformed lines
    }
  }

  return loops;
}

/**
 * Download loop list from Rao 2014
 */
export async function downloadLoopList(
  datasetId: string,
  onProgress?: (progress: LoopDownloadProgress) => void,
): Promise<LoopDownloadResult> {
  const dataset = RAO_2014_LOOP_DATASETS.find((d) => d.id === datasetId);

  if (!dataset) {
    return {
      success: false,
      datasetId,
      cellLine: "unknown",
      error: `Unknown dataset: ${datasetId}. Available: ${RAO_2014_LOOP_DATASETS.map((d) => d.id).join(", ")}`,
    };
  }

  try {
    onProgress?.({ loaded: 0, total: 0, percent: 0, stage: "downloading" });

    const response = await fetch(dataset.url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const total = parseInt(response.headers.get("content-length") || "0");
    const reader = response.body?.getReader();

    if (!reader) {
      throw new Error("Response body not available");
    }

    // Read chunks with progress
    const chunks: Uint8Array[] = [];
    let loaded = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      chunks.push(value);
      loaded += value.length;

      if (onProgress && total > 0) {
        onProgress({
          loaded,
          total,
          percent: Math.round((loaded / total) * 100),
          stage: "downloading",
        });
      }
    }

    // Combine chunks
    const allChunks = new Uint8Array(loaded);
    let position = 0;
    for (const chunk of chunks) {
      allChunks.set(chunk, position);
      position += chunk.length;
    }

    onProgress?.({
      loaded,
      total: loaded,
      percent: 100,
      stage: "decompressing",
    });

    // Decompress
    const decompressed = await decompressGzip(allChunks);
    const content = new TextDecoder().decode(decompressed);

    onProgress?.({ loaded, total: loaded, percent: 100, stage: "parsing" });

    // Parse
    const loops = parseLoopList(content);

    console.log(
      `[HiC] Downloaded ${loops.length} loops from ${dataset.cellLine}`,
    );

    return {
      success: true,
      datasetId: dataset.id,
      cellLine: dataset.cellLine,
      loops,
      loopCount: loops.length,
    };
  } catch (error) {
    return {
      success: false,
      datasetId: dataset.id,
      cellLine: dataset.cellLine,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * List all available loop datasets
 */
export function listHiCDatasets(): LoopListDataset[] {
  return [...RAO_2014_LOOP_DATASETS];
}

/**
 * Get loop anchor positions
 * HiCCUPS format: x1-x2 is first anchor, y1-y2 is second anchor
 * For intrachromosomal loops, the loop spans from x1 to y2
 */
export function getLoopAnchors(loop: HiCLoop): {
  left: number;
  right: number;
  size: number;
} {
  // First anchor center
  const anchor1 = (loop.x1 + loop.x2) / 2;
  // Second anchor center
  const anchor2 = (loop.y1 + loop.y2) / 2;

  const left = Math.min(anchor1, anchor2);
  const right = Math.max(anchor1, anchor2);
  const size = right - left;

  return { left, right, size };
}

/**
 * Filter loops by chromosome and region
 */
export function filterLoops(
  loops: HiCLoop[],
  chromosome: string,
  region?: { start: number; end: number },
): HiCLoop[] {
  return loops.filter((loop) => {
    // Check chromosome (handle both chr11 and 11 formats)
    const chr = chromosome.replace("chr", "");
    const loopChr1 = loop.chr1.replace("chr", "");
    const loopChr2 = loop.chr2.replace("chr", "");

    // Only intrachromosomal loops
    if (loopChr1 !== chr || loopChr2 !== chr) return false;

    // Filter by region if specified
    if (region) {
      const { left, right } = getLoopAnchors(loop);
      if (right < region.start || left > region.end) return false;
    }

    return true;
  });
}

// ============================================================================
// Validation Functions
// ============================================================================

export interface LoopValidationResult {
  datasetId: string;
  cellLine: string;
  chromosome: string;
  region?: { start: number; end: number };
  simulatedLoops: number;
  experimentalLoops: number;
  matchedLoops: number;
  precision: number; // matched / simulated
  recall: number; // matched / experimental
  f1Score: number;
  avgSizeSimulated: number;
  avgSizeExperimental: number;
  sizeCorrelation: number;
}

/**
 * Calculate overlap between two loops
 */
function loopOverlap(
  sim: Loop,
  exp: HiCLoop,
  tolerance: number = 20000, // 20kb tolerance (Hi-C resolution)
): boolean {
  const simLeft = sim.leftAnchor;
  const simRight = sim.rightAnchor;
  const { left: expLeft, right: expRight } = getLoopAnchors(exp);

  // Check if anchors match within tolerance
  const leftMatch = Math.abs(simLeft - expLeft) <= tolerance;
  const rightMatch = Math.abs(simRight - expRight) <= tolerance;

  return leftMatch && rightMatch;
}

/**
 * Validate simulated loops against experimental Hi-C loops
 */
export async function validateLoops(
  simulatedLoops: Loop[],
  datasetId: string,
  chromosome: string,
  region?: { start: number; end: number },
  onProgress?: (progress: LoopDownloadProgress) => void,
): Promise<LoopValidationResult> {
  // Download experimental loops
  const downloadResult = await downloadLoopList(datasetId, onProgress);

  if (!downloadResult.success || !downloadResult.loops) {
    throw new Error(downloadResult.error || "Failed to download loop data");
  }

  // Filter to region of interest
  const experimentalLoops = filterLoops(
    downloadResult.loops,
    chromosome,
    region,
  );

  // Count matches
  let matchedCount = 0;
  const matchedSim = new Set<number>();
  const matchedExp = new Set<number>();

  for (let i = 0; i < simulatedLoops.length; i++) {
    for (let j = 0; j < experimentalLoops.length; j++) {
      if (loopOverlap(simulatedLoops[i], experimentalLoops[j])) {
        if (!matchedSim.has(i) && !matchedExp.has(j)) {
          matchedCount++;
          matchedSim.add(i);
          matchedExp.add(j);
        }
      }
    }
  }

  // Calculate metrics
  const precision =
    simulatedLoops.length > 0 ? matchedCount / simulatedLoops.length : 0;
  const recall =
    experimentalLoops.length > 0 ? matchedCount / experimentalLoops.length : 0;
  const f1Score =
    precision + recall > 0
      ? (2 * precision * recall) / (precision + recall)
      : 0;

  // Calculate average sizes
  const avgSizeSim =
    simulatedLoops.length > 0
      ? simulatedLoops.reduce(
          (sum, l) => sum + (l.rightAnchor - l.leftAnchor),
          0,
        ) / simulatedLoops.length
      : 0;
  const avgSizeExp =
    experimentalLoops.length > 0
      ? experimentalLoops.reduce((sum, l) => sum + getLoopAnchors(l).size, 0) /
        experimentalLoops.length
      : 0;

  // Simple size correlation (ratio comparison)
  const sizeCorrelation =
    avgSizeExp > 0
      ? Math.min(avgSizeSim, avgSizeExp) / Math.max(avgSizeSim, avgSizeExp)
      : 0;

  return {
    datasetId,
    cellLine: downloadResult.cellLine,
    chromosome,
    region,
    simulatedLoops: simulatedLoops.length,
    experimentalLoops: experimentalLoops.length,
    matchedLoops: matchedCount,
    precision,
    recall,
    f1Score,
    avgSizeSimulated: avgSizeSim,
    avgSizeExperimental: avgSizeExp,
    sizeCorrelation,
  };
}

// ============================================================================
// Power-law validation (offline, no download required)
// ============================================================================

export interface PowerLawResult {
  pearsonR: number;
  alpha: number;
  alphaError: number;
}

/**
 * Validate simulation matrix against power-law decay model
 * Expected P(s) ~ s^(-1) for chromatin
 */
export function validateAgainstPowerLaw(
  simulationMatrix: ContactMatrix,
  expectedAlpha: number = -1.0,
): PowerLawResult {
  const n = simulationMatrix.length;

  // Generate expected power-law matrix
  const expectedMatrix: ContactMatrix = Array(n)
    .fill(null)
    .map(() => Array(n).fill(0));
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const distance = Math.abs(j - i) + 1;
      expectedMatrix[i][j] = Math.pow(distance, expectedAlpha);
    }
  }

  // Calculate P(s) curve from simulation
  const distances: number[] = [];
  const contacts: number[] = [];

  for (let d = 1; d < n; d++) {
    let sum = 0;
    let count = 0;
    for (let i = 0; i < n - d; i++) {
      sum += simulationMatrix[i][i + d];
      count++;
    }
    if (count > 0) {
      distances.push(d);
      contacts.push(sum / count);
    }
  }

  // Fit power law: log(P) = alpha * log(s) + const
  const logD = distances.map((d) => Math.log(d));
  const logC = contacts.map((c) => Math.log(Math.max(c, 1e-10)));

  const n2 = logD.length;
  const sumX = logD.reduce((a, b) => a + b, 0);
  const sumY = logC.reduce((a, b) => a + b, 0);
  const sumXY = logD.reduce((sum, x, i) => sum + x * logC[i], 0);
  const sumX2 = logD.reduce((sum, x) => sum + x * x, 0);

  const alpha = (n2 * sumXY - sumX * sumY) / (n2 * sumX2 - sumX * sumX);

  // Normalize and calculate correlation
  const simNorm = normalizeMatrix(simulationMatrix);
  const expNorm = normalizeMatrix(expectedMatrix);
  const pearsonR = calculatePearson(simNorm, expNorm);

  return {
    pearsonR,
    alpha,
    alphaError: Math.abs(alpha - expectedAlpha),
  };
}

function normalizeMatrix(matrix: ContactMatrix): ContactMatrix {
  let max = 0;
  for (const row of matrix) {
    for (const val of row) {
      if (val > max) max = val;
    }
  }
  if (max === 0) return matrix;
  return matrix.map((row) => row.map((val) => val / max));
}

function calculatePearson(a: number[][], b: number[][]): number {
  const n = a.length * a[0].length;
  let sumA = 0,
    sumB = 0,
    sumAB = 0,
    sumA2 = 0,
    sumB2 = 0;

  for (let i = 0; i < a.length; i++) {
    for (let j = 0; j < a[0].length; j++) {
      sumA += a[i][j];
      sumB += b[i][j];
      sumAB += a[i][j] * b[i][j];
      sumA2 += a[i][j] * a[i][j];
      sumB2 += b[i][j] * b[i][j];
    }
  }

  const numerator = n * sumAB - sumA * sumB;
  const denominator = Math.sqrt(
    (n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB),
  );

  return denominator === 0 ? 0 : numerator / denominator;
}

// Legacy exports for backward compatibility
export type HiCDataset = LoopListDataset;
export type HiCDownloadProgress = LoopDownloadProgress;
export { validateLoops as validateAgainstHiC };
