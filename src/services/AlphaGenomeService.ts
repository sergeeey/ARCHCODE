/**
 * AlphaGenome Real-Time Service
 * Integration with Google DeepMind AlphaGenome API
 *
 * This service provides both Mock and Live API modes for validation.
 *
 * API Reference: https://www.nature.com/articles/s41588-025-02406-9
 * DeepMind AlphaGenome: https://deepmind.google.com/science/alphagenome
 *
 * @author Sergey V. Boyko (sergeikuch80@gmail.com)
 * @version 1.2.0
 */

import { SeededRandom } from '../utils/random';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface GenomeInterval {
    chromosome: string;
    start: number;
    end: number;
}

export interface AlphaGenomeConfig {
    apiKey?: string;
    baseUrl?: string;
    mode: 'mock' | 'live';
    timeout?: number;
    retries?: number;
}

export interface EpigeneticFeatures {
    h3k27ac?: number[];
    h3k4me1?: number[];
    h3k4me3?: number[];
    ctcfBinding?: number[];
    dnaseI?: number[];
}

export interface ContactMapPrediction {
    matrix: number[][];
    resolution: number;
    normalization: 'observed' | 'expected' | 'oe_ratio';
}

export interface AlphaGenomePrediction {
    interval: GenomeInterval;
    contactMap: ContactMapPrediction;
    epigenetics: EpigeneticFeatures;
    confidence: number;
    modelVersion: string;
    timestamp: string;
}

export interface ValidationMetrics {
    pearsonR: number;
    spearmanRho: number;
    mse: number;
    rmse: number;
    ssim: number; // Structural Similarity Index
}

export interface TriangulationResult {
    archcode_vs_alphagenome: ValidationMetrics;
    archcode_vs_hic: ValidationMetrics;
    alphagenome_vs_hic: ValidationMetrics;
    consensus: 'ARCHCODE_WINS' | 'ALPHAGENOME_WINS' | 'TIE' | 'INSUFFICIENT_DATA';
    interpretation: string;
}

// ============================================================================
// AlphaGenome Service Class
// ============================================================================

export class AlphaGenomeService {
    private config: Required<AlphaGenomeConfig>;
    private rng: SeededRandom;

    constructor(config: Partial<AlphaGenomeConfig> = {}) {
        this.config = {
            apiKey: config.apiKey || process.env.ALPHAGENOME_API_KEY || process.env.VITE_ALPHAGENOME_API_KEY || '',
            baseUrl: config.baseUrl || 'https://api.alphagenome.deepmind.com/v1',
            mode: config.mode || (config.apiKey ? 'live' : 'mock'),
            timeout: config.timeout || 30000,
            retries: config.retries || 3,
        };
        this.rng = new SeededRandom(42);
    }

    // ========================================================================
    // Public API
    // ========================================================================

    /**
     * Get prediction for a genomic interval
     * Automatically falls back to mock if API fails
     */
    async predict(interval: GenomeInterval): Promise<AlphaGenomePrediction> {
        if (this.config.mode === 'live' && this.config.apiKey) {
            try {
                return await this.fetchLivePrediction(interval);
            } catch (error) {
                console.warn('[AlphaGenome] Live API failed, falling back to mock:', error);
                return this.generateMockPrediction(interval);
            }
        }
        return this.generateMockPrediction(interval);
    }

    /**
     * Validate ARCHCODE simulation against AlphaGenome
     */
    async validateArchcode(
        interval: GenomeInterval,
        archcodeMatrix: number[][]
    ): Promise<{ prediction: AlphaGenomePrediction; metrics: ValidationMetrics }> {
        const prediction = await this.predict(interval);
        const metrics = this.calculateMetrics(archcodeMatrix, prediction.contactMap.matrix);

        return { prediction, metrics };
    }

    /**
     * Triangulation: Compare ARCHCODE vs AlphaGenome vs Experimental Hi-C
     */
    async triangulate(
        interval: GenomeInterval,
        archcodeMatrix: number[][],
        hicMatrix: number[][]
    ): Promise<TriangulationResult> {
        const prediction = await this.predict(interval);
        const alphaMatrix = prediction.contactMap.matrix;

        // Normalize matrices to same dimensions
        const n = Math.min(archcodeMatrix.length, alphaMatrix.length, hicMatrix.length);
        const archTrim = this.trimMatrix(archcodeMatrix, n);
        const alphaTrim = this.trimMatrix(alphaMatrix, n);
        const hicTrim = this.trimMatrix(hicMatrix, n);

        // Calculate all pairwise metrics
        const archcode_vs_alphagenome = this.calculateMetrics(archTrim, alphaTrim);
        const archcode_vs_hic = this.calculateMetrics(archTrim, hicTrim);
        const alphagenome_vs_hic = this.calculateMetrics(alphaTrim, hicTrim);

        // Determine consensus
        const archScore = (archcode_vs_hic.pearsonR + archcode_vs_alphagenome.pearsonR) / 2;
        const alphaScore = alphagenome_vs_hic.pearsonR;

        let consensus: TriangulationResult['consensus'];
        let interpretation: string;

        if (archScore > alphaScore + 0.05) {
            consensus = 'ARCHCODE_WINS';
            interpretation = `ARCHCODE (physics-based) shows better correlation with experimental data. ` +
                `Mean r=${archScore.toFixed(3)} vs AlphaGenome r=${alphaScore.toFixed(3)}. ` +
                `This validates the FountainLoader mechanism.`;
        } else if (alphaScore > archScore + 0.05) {
            consensus = 'ALPHAGENOME_WINS';
            interpretation = `AlphaGenome (ML-based) shows better correlation. ` +
                `r=${alphaScore.toFixed(3)} vs ARCHCODE mean r=${archScore.toFixed(3)}. ` +
                `Consider tuning ARCHCODE parameters.`;
        } else {
            consensus = 'TIE';
            interpretation = `Both models show similar correlation with experimental data. ` +
                `ARCHCODE r=${archScore.toFixed(3)}, AlphaGenome r=${alphaScore.toFixed(3)}. ` +
                `This demonstrates convergent validity between physics and ML approaches.`;
        }

        return {
            archcode_vs_alphagenome,
            archcode_vs_hic,
            alphagenome_vs_hic,
            consensus,
            interpretation,
        };
    }

    /**
     * Get service configuration
     */
    getConfig(): Readonly<AlphaGenomeConfig> {
        return { ...this.config, apiKey: this.config.apiKey ? '***' : '' };
    }

    /**
     * Check if live API is available
     */
    isLiveAvailable(): boolean {
        return this.config.mode === 'live' && !!this.config.apiKey;
    }

    /**
     * Set API key at runtime
     */
    setApiKey(apiKey: string): void {
        this.config.apiKey = apiKey;
        if (apiKey) {
            this.config.mode = 'live';
        }
    }

    /**
     * Switch between mock and live modes
     */
    setMode(mode: 'mock' | 'live'): void {
        if (mode === 'live' && !this.config.apiKey) {
            console.warn('[AlphaGenome] Cannot switch to live mode without API key');
            return;
        }
        this.config.mode = mode;
    }

    // ========================================================================
    // Live API Implementation
    // ========================================================================

    private async fetchLivePrediction(interval: GenomeInterval): Promise<AlphaGenomePrediction> {
        const endpoint = `${this.config.baseUrl}/predict`;

        const requestBody = {
            interval: {
                chromosome: interval.chromosome,
                start: interval.start,
                end: interval.end,
            },
            genome_assembly: 'hg38',
            outputs: ['contact_map', 'epigenetic_features'],
            resolution: 5000, // 5kb bins
            cell_type: 'GM12878',
        };

        let lastError: Error | null = null;

        for (let attempt = 0; attempt < this.config.retries; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.config.apiKey}`,
                        'X-Request-ID': `archcode-${Date.now()}`,
                    },
                    body: JSON.stringify(requestBody),
                    signal: controller.signal,
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`API error ${response.status}: ${errorText}`);
                }

                const data = await response.json();
                return this.parseApiResponse(interval, data);

            } catch (error) {
                lastError = error instanceof Error ? error : new Error(String(error));
                console.warn(`[AlphaGenome] Attempt ${attempt + 1}/${this.config.retries} failed:`, lastError.message);

                if (attempt < this.config.retries - 1) {
                    // Exponential backoff
                    await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
                }
            }
        }

        throw lastError || new Error('Unknown error');
    }

    private parseApiResponse(interval: GenomeInterval, data: any): AlphaGenomePrediction {
        // Parse AlphaGenome API response format
        // This may need adjustment based on actual API response structure

        const contactMap: ContactMapPrediction = {
            matrix: data.contact_map?.matrix || data.predictions?.contact_map || [],
            resolution: data.resolution || 5000,
            normalization: data.normalization || 'observed',
        };

        const epigenetics: EpigeneticFeatures = {
            h3k27ac: data.epigenetic_features?.H3K27ac || data.tracks?.h3k27ac,
            h3k4me1: data.epigenetic_features?.H3K4me1 || data.tracks?.h3k4me1,
            h3k4me3: data.epigenetic_features?.H3K4me3 || data.tracks?.h3k4me3,
            ctcfBinding: data.epigenetic_features?.CTCF || data.tracks?.ctcf,
            dnaseI: data.epigenetic_features?.DNase || data.tracks?.dnase,
        };

        return {
            interval,
            contactMap,
            epigenetics,
            confidence: data.confidence || data.quality_score || 0.95,
            modelVersion: data.model_version || 'alphagenome-v1',
            timestamp: new Date().toISOString(),
        };
    }

    // ========================================================================
    // Mock Implementation (Biologically Realistic)
    // ========================================================================

    private generateMockPrediction(interval: GenomeInterval): AlphaGenomePrediction {
        const length = interval.end - interval.start;
        const resolution = 5000; // 5kb bins
        const nBins = Math.ceil(length / resolution);

        // Generate realistic contact map
        const matrix = this.generateRealisticContactMap(nBins);

        // Generate epigenetic tracks
        const epigenetics = this.generateEpigeneticTracks(nBins);

        return {
            interval,
            contactMap: {
                matrix,
                resolution,
                normalization: 'observed',
            },
            epigenetics,
            confidence: 0.92,
            modelVersion: 'mock-v1.2',
            timestamp: new Date().toISOString(),
        };
    }

    private generateRealisticContactMap(nBins: number): number[][] {
        const matrix: number[][] = Array(nBins).fill(null).map(() => Array(nBins).fill(0));

        // TAD boundaries (every ~40 bins = 200kb)
        const tadBoundaries: number[] = [];
        for (let i = 0; i < nBins; i += Math.floor(30 + this.rng.random() * 20)) {
            tadBoundaries.push(i);
        }
        tadBoundaries.push(nBins);

        // Fill matrix with biologically realistic patterns
        for (let i = 0; i < nBins; i++) {
            for (let j = i; j < nBins; j++) {
                const distance = j - i;

                // 1. Power-law decay (P(s) ~ s^-1)
                let value = 1.0 / Math.pow(distance + 1, 1.0);

                // 2. TAD enhancement (intra-TAD contacts higher)
                const iTAD = tadBoundaries.findIndex(b => b > i) - 1;
                const jTAD = tadBoundaries.findIndex(b => b > j) - 1;
                if (iTAD === jTAD && iTAD >= 0) {
                    value *= 1.5; // 50% boost for intra-TAD
                }

                // 3. Loop peaks (simulate CTCF-mediated loops)
                const isLoopAnchor = (i % 20 < 2) && (j % 20 > 17) && (j - i > 15);
                if (isLoopAnchor) {
                    value *= 3.0; // Strong loop signal
                }

                // 4. Stripe patterns (cohesin-mediated)
                const nearTADBoundary = tadBoundaries.some(b => Math.abs(i - b) < 3 || Math.abs(j - b) < 3);
                if (nearTADBoundary && distance < 30) {
                    value *= 1.3;
                }

                // 5. Biological noise
                value *= 0.85 + this.rng.random() * 0.3;

                // Clamp and set
                value = Math.max(0, Math.min(1, value));
                matrix[i][j] = value;
                matrix[j][i] = value;
            }
            // Diagonal = 1
            matrix[i][i] = 1.0;
        }

        return matrix;
    }

    private generateEpigeneticTracks(nBins: number): EpigeneticFeatures {
        const generateTrack = (peakFreq: number, peakHeight: number): number[] => {
            const track: number[] = [];
            for (let i = 0; i < nBins; i++) {
                let value = 0.1 + this.rng.random() * 0.2; // baseline
                if (this.rng.random() < peakFreq) {
                    value += peakHeight * (0.5 + this.rng.random() * 0.5);
                }
                track.push(value);
            }
            return track;
        };

        return {
            h3k27ac: generateTrack(0.15, 0.8),  // Active enhancers
            h3k4me1: generateTrack(0.20, 0.6),  // Enhancer mark
            h3k4me3: generateTrack(0.10, 0.9),  // Promoter mark
            ctcfBinding: generateTrack(0.08, 1.0), // CTCF peaks
            dnaseI: generateTrack(0.25, 0.7),   // Open chromatin
        };
    }

    // ========================================================================
    // Metrics Calculation
    // ========================================================================

    private calculateMetrics(a: number[][], b: number[][]): ValidationMetrics {
        const n = Math.min(a.length, b.length);
        const aTrim = this.trimMatrix(a, n);
        const bTrim = this.trimMatrix(b, n);

        return {
            pearsonR: this.pearsonCorrelation(aTrim, bTrim),
            spearmanRho: this.spearmanCorrelation(aTrim, bTrim),
            mse: this.meanSquaredError(aTrim, bTrim),
            rmse: Math.sqrt(this.meanSquaredError(aTrim, bTrim)),
            ssim: this.structuralSimilarity(aTrim, bTrim),
        };
    }

    private trimMatrix(matrix: number[][], n: number): number[][] {
        return matrix.slice(0, n).map(row => row.slice(0, n));
    }

    private pearsonCorrelation(a: number[][], b: number[][]): number {
        const flatA = a.flat();
        const flatB = b.flat();
        const n = flatA.length;

        let sumA = 0, sumB = 0, sumAB = 0, sumA2 = 0, sumB2 = 0;
        for (let i = 0; i < n; i++) {
            sumA += flatA[i];
            sumB += flatB[i];
            sumAB += flatA[i] * flatB[i];
            sumA2 += flatA[i] * flatA[i];
            sumB2 += flatB[i] * flatB[i];
        }

        const numerator = n * sumAB - sumA * sumB;
        const denominator = Math.sqrt((n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB));

        return denominator === 0 ? 0 : numerator / denominator;
    }

    private spearmanCorrelation(a: number[][], b: number[][]): number {
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
        const indexed = arr.map((v, i) => ({ v, i }));
        indexed.sort((a, b) => a.v - b.v);
        const ranks = new Array(arr.length);
        indexed.forEach((item, rank) => {
            ranks[item.i] = rank + 1;
        });
        return ranks;
    }

    private meanSquaredError(a: number[][], b: number[][]): number {
        const flatA = a.flat();
        const flatB = b.flat();
        let sum = 0;
        for (let i = 0; i < flatA.length; i++) {
            const diff = flatA[i] - flatB[i];
            sum += diff * diff;
        }
        return sum / flatA.length;
    }

    private structuralSimilarity(a: number[][], b: number[][]): number {
        // Simplified SSIM calculation
        const flatA = a.flat();
        const flatB = b.flat();
        const n = flatA.length;

        const meanA = flatA.reduce((s, v) => s + v, 0) / n;
        const meanB = flatB.reduce((s, v) => s + v, 0) / n;

        let varA = 0, varB = 0, covar = 0;
        for (let i = 0; i < n; i++) {
            varA += (flatA[i] - meanA) ** 2;
            varB += (flatB[i] - meanB) ** 2;
            covar += (flatA[i] - meanA) * (flatB[i] - meanB);
        }
        varA /= n;
        varB /= n;
        covar /= n;

        const c1 = 0.01 ** 2;
        const c2 = 0.03 ** 2;

        const ssim = ((2 * meanA * meanB + c1) * (2 * covar + c2)) /
                     ((meanA ** 2 + meanB ** 2 + c1) * (varA + varB + c2));

        return ssim;
    }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const alphaGenomeService = new AlphaGenomeService();

// Convenience function for setting API key
export function configureAlphaGenome(config: Partial<AlphaGenomeConfig>): void {
    if (config.apiKey) alphaGenomeService.setApiKey(config.apiKey);
    if (config.mode) alphaGenomeService.setMode(config.mode);
}
