/**
 * Hi-C Data Downloader
 * Downloads real Hi-C contact matrices for validation against simulation
 *
 * Sources:
 * - 4D Nucleome (4DN) Data Portal - https://data.4dnucleome.org
 * - ENCODE Project - https://www.encodeproject.org
 * - Rao et al. 2014 (GEO: GSE63525) - canonical Hi-C datasets
 *
 * Literature: Rao et al. (2014) Cell - "A 3D Map of the Human Genome"
 */

import { ContactMatrix } from '../domain/models/genome';

export interface HiCDataset {
    id: string;
    source: 'rao2014' | '4dn' | 'encode';
    cellLine: string;
    description: string;
    resolution: number; // bp per bin
    chromosome?: string;
    region?: { start: number; end: number };
    url: string;
    format: 'dense' | 'sparse' | 'hic';
}

// Rao et al. 2014 preprocessed matrices (hosted on public servers)
// These are submatrices extracted for common validation regions
export const RAO_2014_DATASETS: HiCDataset[] = [
    {
        id: 'rao2014_gm12878_chr11_hbb',
        source: 'rao2014',
        cellLine: 'GM12878',
        description: 'β-globin locus (HBB) - classic loop extrusion region',
        resolution: 10000,
        chromosome: 'chr11',
        region: { start: 5200000, end: 5400000 }, // 200kb around HBB
        url: 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_GM12878_insitu_primary_10kb_KRnorm.txt.gz',
        format: 'sparse',
    },
    {
        id: 'rao2014_gm12878_chr21',
        source: 'rao2014',
        cellLine: 'GM12878',
        description: 'Chromosome 21 - small chromosome for testing',
        resolution: 10000,
        chromosome: 'chr21',
        url: 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_GM12878_insitu_primary_10kb_KRnorm.txt.gz',
        format: 'sparse',
    },
    {
        id: 'rao2014_k562_chr11_hbb',
        source: 'rao2014',
        cellLine: 'K562',
        description: 'β-globin locus (HBB) in K562 leukemia cells',
        resolution: 10000,
        chromosome: 'chr11',
        region: { start: 5200000, end: 5400000 },
        url: 'https://ftp.ncbi.nlm.nih.gov/geo/series/GSE63nnn/GSE63525/suppl/GSE63525_K562_10kb_KRnorm.txt.gz',
        format: 'sparse',
    },
];

// 4D Nucleome datasets with REST API access
export const FOURD_NUCLEOME_DATASETS: HiCDataset[] = [
    {
        id: '4dn_gm12878_micro_c',
        source: '4dn',
        cellLine: 'GM12878',
        description: 'Micro-C (higher resolution Hi-C variant)',
        resolution: 5000,
        url: 'https://data.4dnucleome.org/files-processed/4DNFI2TK7L2F/@@download/4DNFI2TK7L2F.mcool',
        format: 'hic',
    },
    {
        id: '4dn_hff_hic',
        source: '4dn',
        cellLine: 'HFF',
        description: 'Human Foreskin Fibroblast Hi-C',
        resolution: 10000,
        url: 'https://data.4dnucleome.org/files-processed/4DNFIMH34R53/@@download/4DNFIMH34R53.mcool',
        format: 'hic',
    },
];

export interface HiCDownloadProgress {
    loaded: number;
    total: number;
    percent: number;
    stage: 'downloading' | 'decompressing' | 'parsing';
}

export interface HiCDownloadResult {
    success: boolean;
    datasetId: string;
    cellLine: string;
    chromosome?: string;
    resolution: number;
    matrix?: ContactMatrix;
    matrixSize?: number;
    error?: string;
}

/**
 * Parse sparse matrix format (row, col, value)
 * Common format for Rao 2014 data
 */
function parseSparseMatrix(
    content: string,
    chromosome: string,
    region?: { start: number; end: number },
    resolution: number = 10000
): ContactMatrix {
    const lines = content.trim().split('\n');

    // Determine matrix size from region or data
    let minBin = Infinity;
    let maxBin = -Infinity;
    const entries: { row: number; col: number; value: number }[] = [];

    for (const line of lines) {
        if (line.startsWith('#') || line.trim() === '') continue;

        const parts = line.split(/\s+/);
        if (parts.length < 3) continue;

        // Format: chr1 bin1 chr2 bin2 value OR bin1 bin2 value
        let bin1: number, bin2: number, value: number;

        if (parts.length >= 5) {
            // chr1 bin1 chr2 bin2 value format
            const chr1 = parts[0];
            const chr2 = parts[2];

            // Filter for our chromosome
            if (chr1 !== chromosome && chr2 !== chromosome) continue;
            if (chr1 !== chr2) continue; // Only intra-chromosomal

            bin1 = parseInt(parts[1]);
            bin2 = parseInt(parts[3]);
            value = parseFloat(parts[4]);
        } else {
            // bin1 bin2 value format
            bin1 = parseInt(parts[0]);
            bin2 = parseInt(parts[1]);
            value = parseFloat(parts[2]);
        }

        if (isNaN(bin1) || isNaN(bin2) || isNaN(value)) continue;

        // Convert to bin indices
        const idx1 = Math.floor(bin1 / resolution);
        const idx2 = Math.floor(bin2 / resolution);

        // Filter by region if specified
        if (region) {
            const pos1 = bin1;
            const pos2 = bin2;
            if (pos1 < region.start || pos1 > region.end) continue;
            if (pos2 < region.start || pos2 > region.end) continue;
        }

        minBin = Math.min(minBin, idx1, idx2);
        maxBin = Math.max(maxBin, idx1, idx2);

        entries.push({ row: idx1, col: idx2, value });
    }

    if (entries.length === 0) {
        console.warn('[HiC Parser] No entries found for chromosome:', chromosome);
        return [];
    }

    // Create dense matrix
    const size = maxBin - minBin + 1;
    const matrix: ContactMatrix = Array(size).fill(null).map(() => Array(size).fill(0));

    for (const { row, col, value } of entries) {
        const i = row - minBin;
        const j = col - minBin;
        if (i >= 0 && i < size && j >= 0 && j < size) {
            matrix[i][j] = value;
            matrix[j][i] = value; // Symmetric
        }
    }

    // Normalize diagonal to 1
    for (let i = 0; i < size; i++) {
        if (matrix[i][i] === 0) matrix[i][i] = 1;
    }

    console.log(`[HiC Parser] Parsed ${entries.length} entries into ${size}x${size} matrix`);

    return matrix;
}

/**
 * Parse dense matrix format (full matrix as TSV/CSV)
 */
function parseDenseMatrix(content: string): ContactMatrix {
    const lines = content.trim().split('\n');
    const matrix: ContactMatrix = [];

    for (const line of lines) {
        if (line.startsWith('#') || line.trim() === '') continue;

        const values = line.split(/[\t,]/).map(v => parseFloat(v.trim()));
        if (values.some(isNaN)) continue;

        matrix.push(values);
    }

    return matrix;
}

/**
 * Decompress gzip data using Web Streams API
 */
async function decompressGzip(data: Uint8Array): Promise<Uint8Array> {
    const stream = new Response(data).body;
    if (!stream) throw new Error('No stream available');

    const decompressed = stream.pipeThrough(new DecompressionStream('gzip'));
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
 * Download Hi-C data from a specific dataset
 */
export async function downloadHiCData(
    datasetId: string,
    onProgress?: (progress: HiCDownloadProgress) => void
): Promise<HiCDownloadResult> {
    // Find dataset
    const allDatasets = [...RAO_2014_DATASETS, ...FOURD_NUCLEOME_DATASETS];
    const dataset = allDatasets.find(d => d.id === datasetId);

    if (!dataset) {
        return {
            success: false,
            datasetId,
            cellLine: 'unknown',
            resolution: 0,
            error: `Unknown dataset: ${datasetId}. Available: ${allDatasets.map(d => d.id).join(', ')}`,
        };
    }

    // .hic format requires specialized library (hic-straw)
    if (dataset.format === 'hic') {
        return {
            success: false,
            datasetId: dataset.id,
            cellLine: dataset.cellLine,
            resolution: dataset.resolution,
            error: 'HIC format requires hic-straw library. Use sparse/dense format or install: npm install hic-straw',
        };
    }

    try {
        onProgress?.({ loaded: 0, total: 0, percent: 0, stage: 'downloading' });

        const response = await fetch(dataset.url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const total = parseInt(response.headers.get('content-length') || '0');
        const reader = response.body?.getReader();

        if (!reader) {
            throw new Error('Response body not available');
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
                    stage: 'downloading',
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

        onProgress?.({ loaded, total: loaded, percent: 100, stage: 'decompressing' });

        // Decompress if gzipped
        let content: string;
        if (dataset.url.endsWith('.gz')) {
            const decompressed = await decompressGzip(allChunks);
            content = new TextDecoder().decode(decompressed);
        } else {
            content = new TextDecoder().decode(allChunks);
        }

        onProgress?.({ loaded, total: loaded, percent: 100, stage: 'parsing' });

        // Parse matrix
        let matrix: ContactMatrix;
        if (dataset.format === 'sparse') {
            matrix = parseSparseMatrix(
                content,
                dataset.chromosome || 'chr11',
                dataset.region,
                dataset.resolution
            );
        } else {
            matrix = parseDenseMatrix(content);
        }

        return {
            success: true,
            datasetId: dataset.id,
            cellLine: dataset.cellLine,
            chromosome: dataset.chromosome,
            resolution: dataset.resolution,
            matrix,
            matrixSize: matrix.length,
        };

    } catch (error) {
        return {
            success: false,
            datasetId: dataset.id,
            cellLine: dataset.cellLine,
            resolution: dataset.resolution,
            error: error instanceof Error ? error.message : 'Unknown error',
        };
    }
}

/**
 * List all available Hi-C datasets
 */
export function listHiCDatasets(): HiCDataset[] {
    return [...RAO_2014_DATASETS, ...FOURD_NUCLEOME_DATASETS];
}

/**
 * Get datasets for a specific cell line
 */
export function getHiCDatasetsForCellLine(cellLine: string): HiCDataset[] {
    return listHiCDatasets().filter(d =>
        d.cellLine.toLowerCase() === cellLine.toLowerCase()
    );
}

/**
 * Validate simulation matrix against real Hi-C data
 */
export interface HiCValidationResult {
    datasetId: string;
    cellLine: string;
    resolution: number;
    pearsonR: number;
    spearmanRho: number;
    rmse: number;
    matrixSizeSimulation: number;
    matrixSizeReference: number;
    passesThreshold: boolean; // r >= 0.7
}

function calculatePearson(a: number[][], b: number[][]): number {
    const n = a.length * a[0].length;
    let sumA = 0, sumB = 0, sumAB = 0, sumA2 = 0, sumB2 = 0;

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
    const denominator = Math.sqrt((n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB));

    return denominator === 0 ? 0 : numerator / denominator;
}

function getRanks(arr: number[]): number[] {
    const sorted = [...arr].map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
    const ranks = new Array(arr.length);
    sorted.forEach((item, rank) => {
        ranks[item.i] = rank + 1;
    });
    return ranks;
}

function calculateSpearman(a: number[][], b: number[][]): number {
    const flatA = a.flat();
    const flatB = b.flat();

    const ranksA = getRanks(flatA);
    const ranksB = getRanks(flatB);

    const n = ranksA.length;
    let sumD2 = 0;
    for (let i = 0; i < n; i++) {
        const d = ranksA[i] - ranksB[i];
        sumD2 += d * d;
    }

    return 1 - (6 * sumD2) / (n * (n * n - 1));
}

function calculateRMSE(a: number[][], b: number[][]): number {
    let sum = 0;
    let count = 0;
    for (let i = 0; i < a.length; i++) {
        for (let j = 0; j < a[0].length; j++) {
            const diff = a[i][j] - b[i][j];
            sum += diff * diff;
            count++;
        }
    }
    return count === 0 ? 0 : Math.sqrt(sum / count);
}

/**
 * Normalize matrix to [0, 1] range for comparison
 */
function normalizeMatrix(matrix: ContactMatrix): ContactMatrix {
    let max = 0;
    for (const row of matrix) {
        for (const val of row) {
            if (val > max) max = val;
        }
    }

    if (max === 0) return matrix;

    return matrix.map(row => row.map(val => val / max));
}

/**
 * Resize matrix to match target size (bilinear interpolation)
 */
function resizeMatrix(matrix: ContactMatrix, targetSize: number): ContactMatrix {
    const sourceSize = matrix.length;
    const result: ContactMatrix = Array(targetSize).fill(null).map(() => Array(targetSize).fill(0));

    const scale = sourceSize / targetSize;

    for (let i = 0; i < targetSize; i++) {
        for (let j = 0; j < targetSize; j++) {
            const srcI = i * scale;
            const srcJ = j * scale;

            const i0 = Math.floor(srcI);
            const j0 = Math.floor(srcJ);
            const i1 = Math.min(i0 + 1, sourceSize - 1);
            const j1 = Math.min(j0 + 1, sourceSize - 1);

            const di = srcI - i0;
            const dj = srcJ - j0;

            result[i][j] =
                matrix[i0][j0] * (1 - di) * (1 - dj) +
                matrix[i1][j0] * di * (1 - dj) +
                matrix[i0][j1] * (1 - di) * dj +
                matrix[i1][j1] * di * dj;
        }
    }

    return result;
}

export async function validateAgainstHiC(
    simulationMatrix: ContactMatrix,
    datasetId: string,
    onProgress?: (progress: HiCDownloadProgress) => void
): Promise<HiCValidationResult> {
    // Download reference Hi-C data
    const downloadResult = await downloadHiCData(datasetId, onProgress);

    if (!downloadResult.success || !downloadResult.matrix) {
        throw new Error(downloadResult.error || 'Failed to download Hi-C data');
    }

    const referenceMatrix = downloadResult.matrix;

    // Resize matrices to same dimensions
    const targetSize = Math.min(simulationMatrix.length, referenceMatrix.length);
    const simResized = simulationMatrix.length !== targetSize
        ? resizeMatrix(simulationMatrix, targetSize)
        : simulationMatrix;
    const refResized = referenceMatrix.length !== targetSize
        ? resizeMatrix(referenceMatrix, targetSize)
        : referenceMatrix;

    // Normalize both matrices
    const simNorm = normalizeMatrix(simResized);
    const refNorm = normalizeMatrix(refResized);

    // Calculate metrics
    const pearsonR = calculatePearson(simNorm, refNorm);
    const spearmanRho = calculateSpearman(simNorm, refNorm);
    const rmse = calculateRMSE(simNorm, refNorm);

    return {
        datasetId,
        cellLine: downloadResult.cellLine,
        resolution: downloadResult.resolution,
        pearsonR,
        spearmanRho,
        rmse,
        matrixSizeSimulation: simulationMatrix.length,
        matrixSizeReference: referenceMatrix.length,
        passesThreshold: pearsonR >= 0.7,
    };
}

/**
 * Quick validation using local demo data (no download required)
 * Uses power-law decay model as synthetic reference
 */
export function validateAgainstPowerLaw(
    simulationMatrix: ContactMatrix,
    expectedAlpha: number = -1.0 // Expected P(s) exponent
): { pearsonR: number; alpha: number; alphaError: number } {
    const n = simulationMatrix.length;

    // Generate expected power-law matrix
    const expectedMatrix: ContactMatrix = Array(n).fill(null).map(() => Array(n).fill(0));
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
    const logD = distances.map(d => Math.log(d));
    const logC = contacts.map(c => Math.log(Math.max(c, 1e-10)));

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
