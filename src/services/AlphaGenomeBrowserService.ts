import { SeededRandom } from "../utils/random";

export interface GenomeInterval {
  chromosome: string;
  start: number;
  end: number;
}

export interface AlphaGenomeConfig {
  apiKey?: string;
  mode?: "mock" | "real" | "strict-real" | "live";
  timeout?: number;
  retries?: number;
}

type AlphaGenomeRuntimeMode = "mock" | "real" | "strict-real";

export interface LocusConfig {
  name: string;
  ctcfPositions: number[];
  tadBoundaries: number[];
  loopAnchors: Array<[number, number]>;
}

const HBB_LOCUS_CONFIG: LocusConfig = {
  name: "HBB",
  ctcfPositions: [20000, 50000, 70000, 100000, 130000, 160000, 180000],
  tadBoundaries: [0, 45000, 95000, 155000, 200000],
  loopAnchors: [
    [50000, 70000],
    [100000, 130000],
    [160000, 180000],
  ],
};

export interface EpigeneticFeatures {
  h3k27ac?: number[];
  h3k4me1?: number[];
  h3k4me3?: number[];
  ctcfBinding?: number[];
  dnaseI?: number[];
  med1?: number[];
}

export interface ContactMapPrediction {
  matrix: number[][];
  resolution: number;
  normalization: "observed" | "expected" | "oe_ratio";
}

export interface PredictionProvenance {
  mode: AlphaGenomeRuntimeMode;
  source: string;
  apiVersion?: string;
  isFallback: boolean;
}

export interface AlphaGenomePrediction {
  interval: GenomeInterval;
  contactMap: ContactMapPrediction;
  epigenetics: EpigeneticFeatures;
  confidence: number;
  modelVersion: string;
  timestamp: string;
  provenance?: PredictionProvenance;
}

function normalizeMode(
  mode: AlphaGenomeConfig["mode"] | undefined,
  hasApiKey: boolean,
): AlphaGenomeRuntimeMode {
  if (!mode) return hasApiKey ? "real" : "mock";
  if (mode === "live") return "real";
  return mode;
}

export class AlphaGenomeBrowserService {
  private config: Required<Omit<AlphaGenomeConfig, "mode">> & {
    mode: AlphaGenomeRuntimeMode;
  };
  private rng: SeededRandom;
  private predictionCache: Map<string, AlphaGenomePrediction> = new Map();

  constructor(config: Partial<AlphaGenomeConfig> = {}) {
    const resolvedApiKey =
      config.apiKey || (typeof process !== "undefined"
        ? process.env.VITE_ALPHAGENOME_API_KEY || process.env.ALPHAGENOME_API_KEY
        : "") || "";

    this.config = {
      apiKey: resolvedApiKey,
      timeout: config.timeout || 120000,
      retries: config.retries || 3,
      mode: normalizeMode(config.mode, !!resolvedApiKey),
    };
    this.rng = new SeededRandom(42);
  }

  async predict(interval: GenomeInterval): Promise<AlphaGenomePrediction> {
    const cacheKey = `${interval.chromosome}:${interval.start}-${interval.end}`;
    if (this.predictionCache.has(cacheKey)) {
      return this.predictionCache.get(cacheKey)!;
    }

    let prediction: AlphaGenomePrediction;

    if (this.config.mode === "mock") {
      prediction = this.generateMockPrediction(interval);
      prediction.provenance = {
        mode: "mock",
        source: "Local Synthetic Generator",
        isFallback: false,
      };
    } else if (!this.config.apiKey) {
      if (this.config.mode === "strict-real") {
        throw new Error(
          "PR GATE FAILURE [strict-real]: AlphaGenome API key is missing. Execution aborted to prevent mock data leakage.",
        );
      }
      prediction = this.generateMockPrediction(interval);
      prediction.provenance = {
        mode: this.config.mode,
        source: "Local Synthetic Generator",
        isFallback: true,
      };
    } else {
      try {
        // Browser path intentionally avoids Node-only transports (python/gRPC).
        // For now, this endpoint is unavailable in web runtime.
        throw new Error(
          "Browser runtime does not provide direct AlphaGenome live transport.",
        );
      } catch (error) {
        if (this.config.mode === "strict-real") {
          throw new Error(
            `PR GATE FAILURE [strict-real]: API call failed. Fallbacks are disabled. Details: ${(error as Error).message}`,
          );
        }
        prediction = this.generateMockPrediction(interval);
        prediction.provenance = {
          mode: this.config.mode,
          source: "Local Synthetic Generator",
          isFallback: true,
        };
      }
    }

    this.predictionCache.set(cacheKey, prediction);
    return prediction;
  }

  private hashInterval(interval: GenomeInterval): number {
    let hash = 0;
    const s = `${interval.chromosome}:${interval.start}-${interval.end}`;
    for (let i = 0; i < s.length; i++) {
      hash = (hash << 5) - hash + s.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }

  private detectLocusConfig(interval: GenomeInterval): LocusConfig | null {
    const { chromosome, start, end } = interval;
    if (chromosome === "chr11" && start >= 5000000 && end <= 5500000) {
      return HBB_LOCUS_CONFIG;
    }
    return null;
  }

  private generateMockPrediction(interval: GenomeInterval): AlphaGenomePrediction {
    const seed = this.hashInterval(interval);
    this.rng = new SeededRandom(seed);

    const length = interval.end - interval.start;
    const resolution = 5000;
    const nBins = Math.ceil(length / resolution);
    const locusConfig = this.detectLocusConfig(interval);

    const matrix = locusConfig
      ? this.generateHighFidelityContactMap(nBins, resolution, locusConfig)
      : this.generateGenericContactMap(nBins);

    const epigenetics = locusConfig
      ? this.generateAlignedEpigeneticTracks(nBins, resolution, locusConfig)
      : this.generateGenericEpigeneticTracks(nBins);

    return {
      interval,
      contactMap: {
        matrix,
        resolution,
        normalization: "observed",
      },
      epigenetics,
      confidence: locusConfig ? 0.95 : 0.85,
      modelVersion: locusConfig ? "hifi-mock-v1.3" : "generic-mock-v1.3",
      timestamp: new Date().toISOString(),
    };
  }

  private generateHighFidelityContactMap(
    nBins: number,
    resolution: number,
    config: LocusConfig,
  ): number[][] {
    const matrix: number[][] = Array(nBins)
      .fill(null)
      .map(() => Array(nBins).fill(0));

    const ctcfBins = config.ctcfPositions.map((pos) =>
      Math.floor(pos / resolution),
    );
    const loopAnchorBins = config.loopAnchors.map(([a, b]) => [
      Math.floor(a / resolution),
      Math.floor(b / resolution),
    ]);

    for (let i = 0; i < nBins; i++) {
      for (let j = i; j < nBins; j++) {
        const distance = j - i;
        let value = 0;

        if (distance === 1) {
          if (this.rng.random() < 0.15) {
            value = 0.05 + this.rng.random() * 0.1;
          }
        } else if (distance === 2) {
          if (this.rng.random() < 0.05) {
            value = 0.01 + this.rng.random() * 0.02;
          }
        }

        for (const ctcfBin of ctcfBins) {
          const atI = i === ctcfBin;
          const atJ = j === ctcfBin;
          if ((atI || atJ) && distance === 1) {
            value += 0.3 + this.rng.random() * 0.2;
          }
        }

        for (const [anchor1, anchor2] of loopAnchorBins) {
          const bin1 = Math.min(anchor1, anchor2);
          const bin2 = Math.max(anchor1, anchor2);
          const loopDist = bin2 - bin1;
          if (i === bin1 && j === bin2) {
            value += 0.8 + this.rng.random() * 0.2;
          } else if (
            Math.abs(i - bin1) <= 1 &&
            Math.abs(j - bin2) <= 1 &&
            Math.abs(j - i - loopDist) <= 1
          ) {
            value += 0.2 + this.rng.random() * 0.1;
          }
        }

        value = Math.max(0, Math.min(1, value));
        matrix[i][j] = value;
        matrix[j][i] = value;
      }
      matrix[i][i] = 1.0;
    }

    let maxVal = 0;
    for (let i = 0; i < nBins; i++) {
      for (let j = i + 1; j < nBins; j++) {
        if (matrix[i][j] > maxVal) maxVal = matrix[i][j];
      }
    }
    if (maxVal > 0 && maxVal !== 1) {
      for (let i = 0; i < nBins; i++) {
        for (let j = 0; j < nBins; j++) {
          if (i !== j) matrix[i][j] /= maxVal;
        }
      }
    }

    return matrix;
  }

  private findTADIndex(bin: number, boundaries: number[]): number {
    for (let i = 0; i < boundaries.length - 1; i++) {
      if (bin >= boundaries[i] && bin < boundaries[i + 1]) return i;
    }
    return -1;
  }

  private gaussianNoise(mean: number, stdDev: number): number {
    const u1 = this.rng.random();
    const u2 = this.rng.random();
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    return mean + stdDev * z;
  }

  private generateGenericContactMap(nBins: number): number[][] {
    const matrix: number[][] = Array(nBins)
      .fill(null)
      .map(() => Array(nBins).fill(0));

    const tadBoundaries: number[] = [0];
    for (let i = 8; i < nBins; i += Math.floor(6 + this.rng.random() * 8)) {
      tadBoundaries.push(i);
    }
    tadBoundaries.push(nBins);

    for (let i = 0; i < nBins; i++) {
      for (let j = i; j < nBins; j++) {
        const distance = j - i;
        let value = 1.0 / Math.pow(distance + 1, 1.0);
        const iTAD = this.findTADIndex(i, tadBoundaries);
        const jTAD = this.findTADIndex(j, tadBoundaries);
        value *= iTAD === jTAD ? 1.5 : 0.5;
        value *= 1 + this.gaussianNoise(0, 0.1);
        value = Math.max(0, Math.min(1, value));
        matrix[i][j] = value;
        matrix[j][i] = value;
      }
      matrix[i][i] = 1.0;
    }

    return matrix;
  }

  private generateAlignedEpigeneticTracks(
    nBins: number,
    resolution: number,
    config: LocusConfig,
  ): EpigeneticFeatures {
    const ctcfBins = config.ctcfPositions.map((pos) =>
      Math.floor(pos / resolution),
    );

    const ctcfBinding: number[] = Array(nBins).fill(0.1);
    for (const bin of ctcfBins) {
      if (bin < nBins) {
        ctcfBinding[bin] = 0.9 + this.rng.random() * 0.1;
        if (bin > 0) ctcfBinding[bin - 1] = 0.4 + this.rng.random() * 0.2;
        if (bin < nBins - 1) ctcfBinding[bin + 1] = 0.4 + this.rng.random() * 0.2;
      }
    }

    const h3k27ac: number[] = Array(nBins).fill(0);
    for (let i = 0; i < nBins; i++) {
      const nearCTCF = ctcfBins.some((b) => Math.abs(i - b) < 3);
      h3k27ac[i] = nearCTCF
        ? 0.6 + this.rng.random() * 0.3
        : 0.2 + this.rng.random() * 0.3;
    }

    const promoterBins = [Math.floor(100000 / resolution)];
    const h3k4me3: number[] = Array(nBins).fill(0.1);
    for (const bin of promoterBins) {
      if (bin < nBins) {
        h3k4me3[bin] = 0.95;
        if (bin > 0) h3k4me3[bin - 1] = 0.5;
        if (bin < nBins - 1) h3k4me3[bin + 1] = 0.5;
      }
    }

    return {
      h3k27ac,
      h3k4me1: h3k27ac.map((v) => v * 0.8 + this.rng.random() * 0.1),
      h3k4me3,
      ctcfBinding,
      dnaseI: h3k27ac.map((v) => v * 0.9 + this.rng.random() * 0.1),
    };
  }

  private generateGenericEpigeneticTracks(nBins: number): EpigeneticFeatures {
    const generateTrack = (peakFreq: number, peakHeight: number): number[] => {
      const track: number[] = [];
      for (let i = 0; i < nBins; i++) {
        let value = 0.1 + this.rng.random() * 0.2;
        if (this.rng.random() < peakFreq) {
          value += peakHeight * (0.5 + this.rng.random() * 0.5);
        }
        track.push(value);
      }
      return track;
    };

    return {
      h3k27ac: generateTrack(0.15, 0.8),
      h3k4me1: generateTrack(0.2, 0.6),
      h3k4me3: generateTrack(0.1, 0.9),
      ctcfBinding: generateTrack(0.08, 1.0),
      dnaseI: generateTrack(0.25, 0.7),
    };
  }
}

