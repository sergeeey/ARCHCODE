/**
 * AlphaGenome validation adapter.
 * Legacy client API is preserved for compatibility, but prediction routing
 * is unified through AlphaGenomeService.
 */

import { AlphaGenomeService } from '../services/AlphaGenomeService';

export interface AlphaGenomeConfig {
    apiKey: string;
    baseUrl?: string;
    mode?: 'mock' | 'real' | 'strict-real';
}

export interface GenomeInterval {
    chromosome: string;
    start: number;
    end: number;
}

export interface AlphaGenomeRequest {
    interval: GenomeInterval;
    genomeAssembly?: 'hg19' | 'hg38';
    cellType?: string;
    outputs: OutputType[];
}

export enum OutputType {
    CONTACT_MAP = 'contact_map',
    CHROMATIN_ACCESSIBILITY = 'chromatin_accessibility',
    CTCF_BINDING = 'ctcf_binding',
    GENE_EXPRESSION = 'gene_expression',
    ENHANCER_PROMOTER = 'enhancer_promoter',
}

export interface AlphaGenomeResponse {
    interval: GenomeInterval;
    resolution: number;
    contactMap?: number[][];
    chromatinAccessibility?: number[];
    ctcfBinding?: CTCFBindingSite[];
    geneExpression?: GeneExpression[];
    timestamp: string;
}

export interface CTCFBindingSite {
    position: number;
    score: number;
    orientation: 'F' | 'R';
    confidence: number;
}

export interface GeneExpression {
    geneId: string;
    geneName: string;
    tpm: number;
}

export interface ValidationResult {
    pearsonCorrelation: number;
    spearmanCorrelation: number;
    mse: number;
    rmse: number;
    alphaGenomeMap: number[][];
    archcodeMap: number[][];
    diffMap: number[][];
}

export class AlphaGenomeClient {
    private apiKey: string;
    private baseUrl: string;
    private service: AlphaGenomeService;
    private mode: 'mock' | 'real' | 'strict-real';

    constructor(config: AlphaGenomeConfig) {
        this.apiKey = config.apiKey;
        this.baseUrl = config.baseUrl || 'https://api.alphagenome.deepmind.com/v1';
        this.mode = config.mode || (this.apiKey ? 'real' : 'mock');
        if (this.mode === 'strict-real' && !this.apiKey) {
            throw new Error('strict-real mode requires API key');
        }

        this.service = new AlphaGenomeService({
            apiKey: this.apiKey,
            mode: this.mode,
        });
    }

    async predict(request: AlphaGenomeRequest): Promise<AlphaGenomeResponse> {
        const prediction = await this.service.predict(request.interval);

        const isMockPrediction = prediction.modelVersion.toLowerCase().includes('mock');
        if (this.mode === 'strict-real' && isMockPrediction) {
            throw new Error('strict-real mode forbids mock fallback');
        }

        return {
            interval: request.interval,
            resolution: prediction.contactMap.resolution,
            contactMap: request.outputs.includes(OutputType.CONTACT_MAP)
                ? prediction.contactMap.matrix
                : undefined,
            ctcfBinding: request.outputs.includes(OutputType.CTCF_BINDING)
                ? this.generateMockCTCF(request.interval)
                : undefined,
            timestamp: prediction.timestamp,
        };
    }

    async validateArchcode(
        interval: GenomeInterval,
        archcodeMatrix: number[][]
    ): Promise<ValidationResult> {
        const prediction = await this.predict({
            interval,
            outputs: [OutputType.CONTACT_MAP],
        });

        if (!prediction.contactMap) {
            throw new Error('No contact map in AlphaGenome response');
        }

        const alphaMap = prediction.contactMap;
        const n = Math.min(alphaMap.length, archcodeMatrix.length);
        const alphaMapTrimmed = alphaMap.slice(0, n).map(row => row.slice(0, n));
        const archcodeMapTrimmed = archcodeMatrix.slice(0, n).map(row => row.slice(0, n));

        const pearson = this.calculatePearson(alphaMapTrimmed, archcodeMapTrimmed);
        const spearman = this.calculateSpearman(alphaMapTrimmed, archcodeMapTrimmed);
        const mse = this.calculateMSE(alphaMapTrimmed, archcodeMapTrimmed);
        const rmse = Math.sqrt(mse);

        const diffMap = alphaMapTrimmed.map((row, i) =>
            row.map((val, j) => val - archcodeMapTrimmed[i][j])
        );

        return {
            pearsonCorrelation: pearson,
            spearmanCorrelation: spearman,
            mse,
            rmse,
            alphaGenomeMap: alphaMapTrimmed,
            archcodeMap: archcodeMapTrimmed,
            diffMap,
        };
    }

    compareCTCF(
        alphaGenomeSites: CTCFBindingSite[],
        archcodeSites: { position: number; orientation: 'F' | 'R' }[]
    ): {
        matched: number;
        alphaOnly: number;
        archcodeOnly: number;
        orientationAgreement: number;
    } {
        const tolerance = 500;

        let matched = 0;
        let orientationAgreement = 0;
        const matchedAlpha = new Set<number>();
        const matchedArchcode = new Set<number>();

        for (let i = 0; i < alphaGenomeSites.length; i++) {
            const alpha = alphaGenomeSites[i];
            for (let j = 0; j < archcodeSites.length; j++) {
                const arch = archcodeSites[j];
                if (Math.abs(alpha.position - arch.position) < tolerance) {
                    matched++;
                    matchedAlpha.add(i);
                    matchedArchcode.add(j);
                    if (alpha.orientation === arch.orientation) {
                        orientationAgreement++;
                    }
                    break;
                }
            }
        }

        return {
            matched,
            alphaOnly: alphaGenomeSites.length - matchedAlpha.size,
            archcodeOnly: archcodeSites.length - matchedArchcode.size,
            orientationAgreement: matched > 0 ? orientationAgreement / matched : 0,
        };
    }

    private generateMockCTCF(interval: GenomeInterval): CTCFBindingSite[] {
        const sites: CTCFBindingSite[] = [];
        const spacing = 50000;

        for (let pos = interval.start + 25000; pos < interval.end; pos += spacing) {
            sites.push({
                position: pos,
                score: 0.8,
                orientation: sites.length % 2 === 0 ? 'F' : 'R',
                confidence: 0.9,
            });
        }

        return sites;
    }

    private calculatePearson(a: number[][], b: number[][]): number {
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

    private calculateSpearman(a: number[][], b: number[][]): number {
        const flatA = a.flat();
        const flatB = b.flat();
        const ranksA = this.getRanks(flatA);
        const ranksB = this.getRanks(flatB);

        const n = ranksA.length;
        let sumD2 = 0;
        for (let i = 0; i < n; i++) {
            const d = ranksA[i] - ranksB[i];
            sumD2 += d * d;
        }

        return 1 - (6 * sumD2) / (n * (n * n - 1));
    }

    private getRanks(arr: number[]): number[] {
        const sorted = [...arr].map((v, i) => ({ v, i })).sort((x, y) => x.v - y.v);
        const ranks = new Array(arr.length);
        sorted.forEach((item, rank) => {
            ranks[item.i] = rank + 1;
        });
        return ranks;
    }

    private calculateMSE(a: number[][], b: number[][]): number {
        let sum = 0;
        let count = 0;
        for (let i = 0; i < a.length; i++) {
            for (let j = 0; j < a[0].length; j++) {
                const diff = a[i][j] - b[i][j];
                sum += diff * diff;
                count++;
            }
        }
        return count === 0 ? 0 : sum / count;
    }
}

export const alphaGenome = new AlphaGenomeClient({ apiKey: '' });

export function setAlphaGenomeApiKey(apiKey: string): void {
    (alphaGenome as unknown as { apiKey: string }).apiKey = apiKey;
}


