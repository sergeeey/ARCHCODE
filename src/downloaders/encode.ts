/**
 * ENCODE Data Downloader
 * Downloads CTCF ChIP-seq peaks and other genomic data from ENCODE Project
 */

import { loadCTCFFromBED, BEDParseResult } from '../parsers/bed';
import { CTCFSite } from '../domain/models/genome';

export interface ENCODEFile {
    id: string;
    cellLine: string;
    description: string;
    url: string;
    size?: number;
}

// Curated list of verified CTCF datasets
export const ENCODE_CTCF_DATASETS: ENCODEFile[] = [
    {
        id: 'ENCFF165MIL',
        cellLine: 'GM12878',
        description: 'B-lymphocyte, immortalized (standard Hi-C cell line)',
        url: 'https://www.encodeproject.org/files/ENCFF165MIL/@@download/ENCFF165MIL.bed.gz',
    },
    {
        id: 'ENCFF002CEL',
        cellLine: 'K562',
        description: 'Chronic myelogenous leukemia (myeloid)',
        url: 'https://www.encodeproject.org/files/ENCFF002CEL/@@download/ENCFF002CEL.bed.gz',
    },
    {
        id: 'ENCFF002CVM',
        cellLine: 'HeLa-S3',
        description: 'Cervical carcinoma (epithelial)',
        url: 'https://www.encodeproject.org/files/ENCFF002CVM/@@download/ENCFF002CVM.bed.gz',
    },
    {
        id: 'ENCFF002CVL',
        cellLine: 'HepG2',
        description: 'Hepatocellular carcinoma (liver)',
        url: 'https://www.encodeproject.org/files/ENCFF002CVL/@@download/ENCFF002CVL.bed.gz',
    },
    {
        id: 'ENCFF001TZA',
        cellLine: 'H1-hESC',
        description: 'Human embryonic stem cells (pluripotent)',
        url: 'https://www.encodeproject.org/files/ENCFF001TZA/@@download/ENCFF001TZA.bed.gz',
    },
];

export interface DownloadProgress {
    loaded: number;
    total: number;
    percent: number;
}

export interface DownloadResult {
    success: boolean;
    fileId: string;
    cellLine: string;
    content?: string;
    sites?: CTCFSite[];
    parseResult?: BEDParseResult;
    error?: string;
}

/**
 * Download and decompress gzipped BED file from ENCODE
 */
export async function downloadENCODEFile(
    fileId: string,
    onProgress?: (progress: DownloadProgress) => void
): Promise<DownloadResult> {
    const dataset = ENCODE_CTCF_DATASETS.find(d => d.id === fileId);
    
    if (!dataset) {
        return {
            success: false,
            fileId,
            cellLine: 'unknown',
            error: `Unknown file ID: ${fileId}. Available: ${ENCODE_CTCF_DATASETS.map(d => d.id).join(', ')}`,
        };
    }

    try {
        // Fetch with progress tracking
        const response = await fetch(dataset.url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const total = parseInt(response.headers.get('content-length') || '0');
        const reader = response.body?.getReader();
        
        if (!reader) {
            throw new Error('Response body not available');
        }

        // Read chunks
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

        // Decompress using DecompressionStream
        const decompressed = await decompressGzip(allChunks);
        const content = new TextDecoder().decode(decompressed);

        // Parse BED
        const parseResult = loadCTCFFromBED(content);
        
        return {
            success: true,
            fileId: dataset.id,
            cellLine: dataset.cellLine,
            content,
            sites: parseResult.sites,
            parseResult,
        };

    } catch (error) {
        return {
            success: false,
            fileId: dataset.id,
            cellLine: dataset.cellLine,
            error: error instanceof Error ? error.message : 'Unknown error',
        };
    }
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

    // Combine
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
 * Get metadata about available datasets
 */
export function listAvailableDatasets(): ENCODEFile[] {
    return [...ENCODE_CTCF_DATASETS];
}

/**
 * Download all datasets (for batch processing)
 */
export async function downloadAllDatasets(
    onFileComplete?: (result: DownloadResult) => void,
    onProgress?: (fileId: string, progress: DownloadProgress) => void
): Promise<DownloadResult[]> {
    const results: DownloadResult[] = [];

    for (const dataset of ENCODE_CTCF_DATASETS) {
        const result = await downloadENCODEFile(dataset.id, 
            (progress) => onProgress?.(dataset.id, progress)
        );
        results.push(result);
        onFileComplete?.(result);
    }

    return results;
}

/**
 * Compare CTCF sites between cell lines
 */
export interface ComparisonResult {
    cellLine: string;
    totalSites: number;
    forwardSites: number;
    reverseSites: number;
    avgPosition: number;
    genomeCoverage: number; // bp covered by CTCF
}

export function compareCellLines(results: DownloadResult[]): ComparisonResult[] {
    return results
        .filter(r => r.success && r.sites)
        .map(r => {
            const sites = r.sites!;
            const positions = sites.map(s => s.position);
            const minPos = Math.min(...positions);
            const maxPos = Math.max(...positions);
            
            return {
                cellLine: r.cellLine,
                totalSites: sites.length,
                forwardSites: sites.filter(s => s.orientation === 'F').length,
                reverseSites: sites.filter(s => s.orientation === 'R').length,
                avgPosition: positions.reduce((a, b) => a + b, 0) / sites.length,
                genomeCoverage: maxPos - minPos,
            };
        });
}
