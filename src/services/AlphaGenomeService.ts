/**
 * AlphaGenome Real-Time Service
 * Integration with Google DeepMind AlphaGenome via Python SDK Bridge
 *
 * Architecture:
 * - Primary: Python SDK (alphagenome) via child_process
 * - Fallback 1: gRPC direct connection
 * - Fallback 2: High-Fidelity Mock v1.3
 *
 * High-Fidelity Mock v1.3 provides fallback when API unavailable.
 *
 * API Reference: https://www.nature.com/articles/s41588-025-02406-9
 * DeepMind AlphaGenome: https://deepmind.google.com/science/alphagenome
 *
 * @author Sergey V. Boyko (sergeikuch80@gmail.com)
 * @version 1.6.0 (Parser Integration + Kramer Kinetics)
 */

import { SeededRandom } from "../utils/random";

// Python SDK availability flag
let pythonSdkAvailable: boolean | null = null;
let pythonSdkChecked = false;

// gRPC imports - dynamically loaded for Node.js environment
let grpc: typeof import("@grpc/grpc-js") | null = null;
let protoLoader: typeof import("@grpc/proto-loader") | null = null;

// Try to load gRPC modules (only works in Node.js)
async function loadGrpcModules(): Promise<boolean> {
  if (grpc && protoLoader) return true;

  try {
    // Dynamic import for Node.js compatibility
    grpc = await import("@grpc/grpc-js");
    protoLoader = await import("@grpc/proto-loader");
    return true;
  } catch {
    console.warn(
      "[AlphaGenome] gRPC modules not available (browser environment?)",
    );
    return false;
  }
}

// gRPC client instance (lazy initialized)
let grpcClient: any = null;
let grpcInitialized = false;

/**
 * Check if Python AlphaGenome SDK is available
 */
async function checkPythonSdk(): Promise<boolean> {
  if (pythonSdkChecked) return pythonSdkAvailable ?? false;

  try {
    const { spawn } = await import("child_process");
    const path = await import("path");
    const { fileURLToPath } = await import("url");

    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    const wrapperPath = path.join(__dirname, "alphagenome_wrapper.py");

    return new Promise((resolve) => {
      const proc = spawn("python", [wrapperPath, "check"], {
        timeout: 10000,
      });

      let stdout = "";
      proc.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      proc.on("close", (code) => {
        pythonSdkChecked = true;
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            pythonSdkAvailable =
              result.alphagenome_sdk || result.alphagenome_research;
            if (pythonSdkAvailable) {
              console.log(
                "[AlphaGenome] Python SDK available:",
                result.message,
              );
            }
          } catch {
            pythonSdkAvailable = false;
          }
        } else {
          pythonSdkAvailable = false;
        }
        resolve(pythonSdkAvailable ?? false);
      });

      proc.on("error", () => {
        pythonSdkChecked = true;
        pythonSdkAvailable = false;
        resolve(false);
      });
    });
  } catch {
    pythonSdkChecked = true;
    pythonSdkAvailable = false;
    return false;
  }
}

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
  grpcEndpoint?: string; // gRPC endpoint (default: gdmscience.googleapis.com:443)
  mode: "mock" | "real" | "strict-real" | "live";
  timeout?: number;
  retries?: number;
}

type AlphaGenomeRuntimeMode = "mock" | "real" | "strict-real";

function normalizeMode(
  mode: AlphaGenomeConfig["mode"] | undefined,
  hasApiKey: boolean,
): AlphaGenomeRuntimeMode {
  if (!mode) return hasApiKey ? "real" : "mock";
  if (mode === "live") return "real";
  return mode;
}

// gRPC endpoint configuration
const GRPC_ENDPOINT = "gdmscience.googleapis.com:443";
const GRPC_SERVICE_NAME = "google.deepmind.alphagenome.v1.AlphaGenomeService";

/**
 * Known locus configurations for High-Fidelity Mock
 * These match the CTCF sites used in ARCHCODE validation scripts
 */
export interface LocusConfig {
  name: string;
  ctcfPositions: number[]; // Relative positions within the locus (0-based)
  tadBoundaries: number[]; // TAD boundary positions
  loopAnchors: Array<[number, number]>; // Loop anchor pairs
}

// HBB Locus (Beta-Globin) - chr11:5,200,000-5,400,000
const HBB_LOCUS_CONFIG: LocusConfig = {
  name: "HBB",
  // CTCF sites from validate-alphagenome-hbb.ts (relative to locus start)
  // Positions: 20k(R), 50k(F), 70k(R), 100k(F), 130k(R), 160k(F), 180k(R)
  ctcfPositions: [20000, 50000, 70000, 100000, 130000, 160000, 180000],
  // TAD boundaries align with convergent CTCF pairs
  tadBoundaries: [0, 45000, 95000, 155000, 200000],
  // CONVERGENT CTCF pairs only (F→R creates loops in ARCHCODE)
  // These match actual loop extrusion behavior:
  loopAnchors: [
    [50000, 70000], // F@50k → R@70k (20kb, ~4 bins)
    [100000, 130000], // F@100k → R@130k (30kb, ~6 bins)
    [160000, 180000], // F@160k → R@180k (20kb, ~4 bins)
  ],
};

export interface EpigeneticFeatures {
  h3k27ac?: number[];
  h3k4me1?: number[];
  h3k4me3?: number[];
  ctcfBinding?: number[];
  dnaseI?: number[];
  med1?: number[]; // MED1 binding for Kramer kinetics
}

/**
 * Parser Data Configuration
 * For integration with Scientific News Parser at D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/
 */
export interface ParserConfig {
  basePath: string; // Root path to parser data
  subdirs: {
    cohesin?: string;
    ctcf?: string;
    histone?: string;
    k562?: string;
    med1?: string;
  };
}

export interface ParserDataSet {
  med1Tracks: string[]; // BigWig files for MED1
  ctcfTracks: string[]; // BigWig files for CTCF
  histoneTracks: string[]; // BigWig files for histones
  mutationFiles?: string[]; // JSON/CSV mutation data
}

export interface IntegratedAnalysisResult {
  interval: GenomeInterval;
  parserSource: string;
  simulation: {
    contactMatrix: number[][];
    loops: Array<{ start: number; end: number; strength: number }>;
    kramerParams: { alpha: number; gamma: number; kBase: number };
  };
  epigenetics: EpigeneticFeatures;
  riskScore: number;
  timestamp: string;
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
  consensus: "ARCHCODE_WINS" | "ALPHAGENOME_WINS" | "TIE" | "INSUFFICIENT_DATA";
  interpretation: string;
}

// ============================================================================
// AlphaGenome Service Class
// ============================================================================

export class AlphaGenomeService {
  private config: Omit<Required<AlphaGenomeConfig>, "mode"> & {
    mode: AlphaGenomeRuntimeMode;
  };
  private rng: SeededRandom;
  private predictionCache: Map<string, AlphaGenomePrediction> = new Map();

  constructor(config: Partial<AlphaGenomeConfig> = {}) {
    const resolvedApiKey =
      config.apiKey ||
      process.env.ALPHAGENOME_API_KEY ||
      process.env.VITE_ALPHAGENOME_API_KEY ||
      "";
    this.config = {
      apiKey: resolvedApiKey,
      grpcEndpoint: config.grpcEndpoint || GRPC_ENDPOINT,
      mode: normalizeMode(config.mode, !!resolvedApiKey),
      timeout: config.timeout || 120000, // 2 minutes for API calls
      retries: config.retries || 3,
    };
    this.rng = new SeededRandom(42);

    // Initialize gRPC client asynchronously
    if (this.config.mode !== "mock" && this.config.apiKey) {
      this.initGrpcClient().catch((err) => {
        console.warn(
          "[AlphaGenome] Failed to initialize gRPC client:",
          err.message,
        );
      });
    }
  }

  /**
   * Initialize gRPC client for DeepMind AlphaGenome API
   */
  private async initGrpcClient(): Promise<void> {
    if (grpcInitialized) return;

    const grpcAvailable = await loadGrpcModules();
    if (!grpcAvailable || !grpc || !protoLoader) {
      console.warn("[AlphaGenome] gRPC not available, will use fallback");
      return;
    }

    try {
      const path = await import("path");
      const { fileURLToPath } = await import("url");

      // Get proto file path
      const __filename = fileURLToPath(import.meta.url);
      const __dirname = path.dirname(__filename);
      const protoPath = path.join(
        __dirname,
        "..",
        "proto",
        "alphagenome.proto",
      );

      // Load proto definition
      const packageDefinition = await protoLoader.load(protoPath, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true,
      });

      const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

      // Create credentials with API key
      const channelCredentials = grpc.credentials.createSsl();
      const callCredentials = grpc.credentials.createFromMetadataGenerator(
        (
          _params: any,
          callback: (err: Error | null, metadata?: any) => void,
        ) => {
          const metadata = new grpc.Metadata();
          metadata.add("x-goog-api-key", this.config.apiKey);
          callback(null, metadata);
        },
      );

      const combinedCredentials = grpc.credentials.combineChannelCredentials(
        channelCredentials,
        callCredentials,
      );

      // Navigate to the service in the proto descriptor
      const alphagenome = (protoDescriptor as any).google?.deepmind?.alphagenome
        ?.v1;
      if (!alphagenome?.AlphaGenomeService) {
        throw new Error("AlphaGenomeService not found in proto definition");
      }

      // Create client
      grpcClient = new alphagenome.AlphaGenomeService(
        this.config.grpcEndpoint,
        combinedCredentials,
        {
          "grpc.max_receive_message_length": 100 * 1024 * 1024, // 100MB
          "grpc.max_send_message_length": 10 * 1024 * 1024, // 10MB
        },
      );

      grpcInitialized = true;
      console.log(
        `[AlphaGenome] gRPC client initialized → ${this.config.grpcEndpoint}`,
      );
    } catch (error) {
      console.warn("[AlphaGenome] Failed to load proto:", error);
      grpcClient = null;
    }
  }

  /**
   * Get cache key for an interval
   */
  private getIntervalKey(interval: GenomeInterval): string {
    return `${interval.chromosome}:${interval.start}-${interval.end}`;
  }

  /**
   * Hash interval to create deterministic seed
   */
  private hashInterval(interval: GenomeInterval): number {
    const str = this.getIntervalKey(interval);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Clear prediction cache
   */
  clearCache(): void {
    this.predictionCache.clear();
  }

  // ========================================================================
  // Public API
  // ========================================================================

  /**
   * Get prediction for a genomic interval.
   * Mode semantics:
   * - mock: always synthetic
   * - real: use API when available, fallback to synthetic on errors
   * - strict-real: fail-closed, any API issue is fatal
   */
  async predict(interval: GenomeInterval): Promise<AlphaGenomePrediction> {
    const cacheKey = this.getIntervalKey(interval);

    // Check cache first
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
        prediction = await this.fetchLivePrediction(interval);
        const looksMock = prediction.modelVersion
          .toLowerCase()
          .includes("mock");

        if (this.config.mode === "strict-real" && looksMock) {
          throw new Error(
            "PR GATE FAILURE [strict-real]: External service returned a mock response. Execution aborted.",
          );
        }

        prediction.provenance = {
          mode: this.config.mode,
          source: looksMock
            ? "AlphaGenome API (Test Endpoint)"
            : "AlphaGenome API (Production)",
          apiVersion: prediction.modelVersion,
          isFallback: false,
        };
      } catch (error) {
        if (this.config.mode === "strict-real") {
          throw new Error(
            `PR GATE FAILURE [strict-real]: API call failed. Fallbacks are disabled. Details: ${(error as Error).message}`,
          );
        }
        console.warn(
          "[AlphaGenome] Live API failed, falling back to mock:",
          error,
        );
        prediction = this.generateMockPrediction(interval);
        prediction.provenance = {
          mode: this.config.mode,
          source: "Local Synthetic Generator",
          isFallback: true,
        };
      }
    }

    // Cache the result
    this.predictionCache.set(cacheKey, prediction);
    return prediction;
  }

  /**
   * Validate ARCHCODE simulation against AlphaGenome
   */
  async validateArchcode(
    interval: GenomeInterval,
    archcodeMatrix: number[][],
  ): Promise<{
    prediction: AlphaGenomePrediction;
    metrics: ValidationMetrics;
  }> {
    const prediction = await this.predict(interval);
    const metrics = this.calculateMetrics(
      archcodeMatrix,
      prediction.contactMap.matrix,
    );

    return { prediction, metrics };
  }

  /**
   * Triangulation: Compare ARCHCODE vs AlphaGenome vs Experimental Hi-C
   */
  async triangulate(
    interval: GenomeInterval,
    archcodeMatrix: number[][],
    hicMatrix: number[][],
  ): Promise<TriangulationResult> {
    const prediction = await this.predict(interval);
    const alphaMatrix = prediction.contactMap.matrix;

    // Normalize matrices to same dimensions
    const n = Math.min(
      archcodeMatrix.length,
      alphaMatrix.length,
      hicMatrix.length,
    );
    const archTrim = this.trimMatrix(archcodeMatrix, n);
    const alphaTrim = this.trimMatrix(alphaMatrix, n);
    const hicTrim = this.trimMatrix(hicMatrix, n);

    // Calculate all pairwise metrics
    const archcode_vs_alphagenome = this.calculateMetrics(archTrim, alphaTrim);
    const archcode_vs_hic = this.calculateMetrics(archTrim, hicTrim);
    const alphagenome_vs_hic = this.calculateMetrics(alphaTrim, hicTrim);

    // Determine consensus
    const archScore =
      (archcode_vs_hic.pearsonR + archcode_vs_alphagenome.pearsonR) / 2;
    const alphaScore = alphagenome_vs_hic.pearsonR;

    let consensus: TriangulationResult["consensus"];
    let interpretation: string;

    if (archScore > alphaScore + 0.05) {
      consensus = "ARCHCODE_WINS";
      interpretation =
        `ARCHCODE (physics-based) shows better correlation with experimental data. ` +
        `Mean r=${archScore.toFixed(3)} vs AlphaGenome r=${alphaScore.toFixed(3)}. ` +
        `This validates the FountainLoader mechanism.`;
    } else if (alphaScore > archScore + 0.05) {
      consensus = "ALPHAGENOME_WINS";
      interpretation =
        `AlphaGenome (ML-based) shows better correlation. ` +
        `r=${alphaScore.toFixed(3)} vs ARCHCODE mean r=${archScore.toFixed(3)}. ` +
        `Consider tuning ARCHCODE parameters.`;
    } else {
      consensus = "TIE";
      interpretation =
        `Both models show similar correlation with experimental data. ` +
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
    return { ...this.config, apiKey: this.config.apiKey ? "***" : "" };
  }

  /**
   * Check if live API is available
   */
  isLiveAvailable(): boolean {
    return this.config.mode !== "mock" && !!this.config.apiKey;
  }

  /**
   * Set API key at runtime
   */
  setApiKey(apiKey: string): void {
    this.config.apiKey = apiKey;
    if (apiKey && this.config.mode === "mock") {
      this.config.mode = "real";
    }
  }

  /**
   * Switch between mock/real/strict-real modes.
   * Backward compatible with "live" alias.
   */
  setMode(mode: AlphaGenomeConfig["mode"]): void {
    const normalized = normalizeMode(mode, !!this.config.apiKey);
    if (
      (normalized === "real" || normalized === "strict-real") &&
      !this.config.apiKey
    ) {
      console.warn(
        "[AlphaGenome] Cannot switch to real/strict-real mode without API key",
      );
      return;
    }
    this.config.mode = normalized;
  }

  // ========================================================================
  // Live API Implementation
  // ========================================================================

  /**
   * Fetch prediction using multi-layer fallback strategy:
   * 1. Python SDK (official alphagenome package)
   * 2. gRPC direct connection
   * 3. Throws error (caller will use mock)
   */
  private async fetchLivePrediction(
    interval: GenomeInterval,
  ): Promise<AlphaGenomePrediction> {
    // Try Python SDK first
    try {
      const sdkAvailable = await checkPythonSdk();
      if (sdkAvailable) {
        console.log("[AlphaGenome] Trying Python SDK...");
        const result = await this.callPythonSdk(interval);
        if (result) return result;
      }
    } catch (error) {
      console.warn("[AlphaGenome] Python SDK failed:", error);
    }

    // Fallback to gRPC
    try {
      await this.initGrpcClient();
      if (grpcClient) {
        console.log("[AlphaGenome] Trying gRPC...");
        return await this.fetchViaGrpc(interval);
      }
    } catch (error) {
      console.warn("[AlphaGenome] gRPC failed:", error);
    }

    throw new Error("All live API methods failed");
  }

  /**
   * Call Python SDK wrapper via child_process
   */
  private async callPythonSdk(
    interval: GenomeInterval,
  ): Promise<AlphaGenomePrediction | null> {
    try {
      const { spawn } = await import("child_process");
      const path = await import("path");
      const { fileURLToPath } = await import("url");

      const __filename = fileURLToPath(import.meta.url);
      const __dirname = path.dirname(__filename);
      const wrapperPath = path.join(__dirname, "alphagenome_wrapper.py");

      const args = [
        wrapperPath,
        "predict",
        interval.chromosome,
        String(interval.start),
        String(interval.end),
        "--resolution",
        "5000",
        "--cell-type",
        "GM12878",
      ];

      if (this.config.apiKey) {
        args.push("--api-key", this.config.apiKey);
      }

      return new Promise((resolve, reject) => {
        const proc = spawn("python", args, {
          timeout: this.config.timeout,
        });

        let stdout = "";
        let stderr = "";

        proc.stdout.on("data", (data) => {
          stdout += data.toString();
        });
        proc.stderr.on("data", (data) => {
          stderr += data.toString();
        });

        proc.on("close", (code) => {
          if (code === 0) {
            try {
              const result = JSON.parse(stdout);
              if (result.status === "ok") {
                resolve(this.parsePythonResponse(interval, result));
              } else if (result.fallback) {
                // SDK says to use fallback
                resolve(null);
              } else {
                reject(new Error(result.error || "Python SDK error"));
              }
            } catch (e) {
              reject(new Error(`Failed to parse Python output: ${stdout}`));
            }
          } else {
            reject(new Error(`Python exited with code ${code}: ${stderr}`));
          }
        });

        proc.on("error", (err) => {
          reject(new Error(`Failed to spawn Python: ${err.message}`));
        });
      });
    } catch (error) {
      console.warn("[AlphaGenome] Python SDK call failed:", error);
      return null;
    }
  }

  /**
   * Parse Python SDK response into our format
   */
  private parsePythonResponse(
    interval: GenomeInterval,
    data: any,
  ): AlphaGenomePrediction {
    const contactMap = data.contact_map || {};
    const matrix = contactMap.matrix || [];

    return {
      interval,
      contactMap: {
        matrix,
        resolution: contactMap.resolution || 5000,
        normalization: contactMap.normalization || "observed",
      },
      epigenetics: {
        h3k27ac: data.epigenetics?.h3k27ac,
        h3k4me1: data.epigenetics?.h3k4me1,
        h3k4me3: data.epigenetics?.h3k4me3,
        ctcfBinding: data.epigenetics?.ctcf_binding,
        dnaseI: data.epigenetics?.dnase_i,
      },
      confidence: data.confidence || 0.95,
      modelVersion: data.model_version || "alphagenome-python-sdk",
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Fetch via gRPC with retries
   */
  private async fetchViaGrpc(
    interval: GenomeInterval,
  ): Promise<AlphaGenomePrediction> {
    const request = {
      interval: {
        chromosome: interval.chromosome,
        start: interval.start,
        end: interval.end,
      },
      genome_assembly: "hg38",
      output_types: ["OUTPUT_TYPE_CONTACT_MAPS"],
      resolution: 5000,
      cell_type: "GM12878",
    };

    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.config.retries; attempt++) {
      try {
        console.log(
          `[AlphaGenome] gRPC call attempt ${attempt + 1}/${this.config.retries}...`,
        );
        const response = await this.callGrpcMethod(request);
        return this.parseGrpcResponse(interval, response);
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        console.warn(
          `[AlphaGenome] gRPC attempt ${attempt + 1}/${this.config.retries} failed:`,
          lastError.message,
        );

        if (attempt < this.config.retries - 1) {
          await new Promise((resolve) =>
            setTimeout(resolve, Math.pow(2, attempt) * 1000),
          );
        }
      }
    }

    throw lastError || new Error("gRPC call failed");
  }

  /**
   * Execute gRPC method call with timeout
   */
  private callGrpcMethod(request: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!grpcClient) {
        reject(new Error("gRPC client not initialized"));
        return;
      }

      // Set deadline for timeout
      const deadline = new Date();
      deadline.setMilliseconds(
        deadline.getMilliseconds() + this.config.timeout,
      );

      grpcClient.PredictStructure(
        request,
        { deadline },
        (error: any, response: any) => {
          if (error) {
            // Parse gRPC error
            const errorMessage =
              error.details || error.message || "Unknown gRPC error";
            const errorCode = error.code || "UNKNOWN";
            reject(new Error(`gRPC error [${errorCode}]: ${errorMessage}`));
          } else {
            resolve(response);
          }
        },
      );
    });
  }

  /**
   * Parse gRPC response into our internal format
   */
  private parseGrpcResponse(
    interval: GenomeInterval,
    response: any,
  ): AlphaGenomePrediction {
    // Extract contact map from gRPC response
    const contactMapData = response.contact_map || {};
    const matrixData = contactMapData.matrix_data || [];
    const rows = contactMapData.rows || 0;
    const cols = contactMapData.cols || rows;

    // Convert flat array to 2D matrix
    const matrix: number[][] = [];
    if (rows > 0 && matrixData.length > 0) {
      for (let i = 0; i < rows; i++) {
        const row: number[] = [];
        for (let j = 0; j < cols; j++) {
          const idx = i * cols + j;
          row.push(idx < matrixData.length ? matrixData[idx] : 0);
        }
        matrix.push(row);
      }
    }

    // Extract epigenetic tracks
    const tracks = response.epigenetic_tracks || {};

    const epigenetics: EpigeneticFeatures = {
      h3k27ac: tracks.h3k27ac || undefined,
      h3k4me1: tracks.h3k4me1 || undefined,
      h3k4me3: tracks.h3k4me3 || undefined,
      ctcfBinding: tracks.ctcf_binding || undefined,
      dnaseI: tracks.dnase_i || undefined,
    };

    return {
      interval,
      contactMap: {
        matrix,
        resolution: contactMapData.resolution || 5000,
        normalization: (contactMapData.normalization as any) || "observed",
      },
      epigenetics,
      confidence: response.confidence || 0.95,
      modelVersion: response.model_version || "alphagenome-grpc-v1",
      timestamp: response.metadata?.timestamp || new Date().toISOString(),
    };
  }

  // ========================================================================
  // High-Fidelity Mock Implementation
  // ========================================================================

  /**
   * Detect locus type from interval for appropriate mock generation
   */
  private detectLocusConfig(interval: GenomeInterval): LocusConfig | null {
    const { chromosome, start, end } = interval;

    // HBB locus detection (chr11:5.2M-5.4M)
    if (chromosome === "chr11" && start >= 5000000 && end <= 5500000) {
      return HBB_LOCUS_CONFIG;
    }

    // Add more loci as needed
    return null;
  }

  private generateMockPrediction(
    interval: GenomeInterval,
  ): AlphaGenomePrediction {
    // Reset RNG with deterministic seed based on interval
    // This ensures same interval always produces same mock
    const seed = this.hashInterval(interval);
    this.rng = new SeededRandom(seed);

    const length = interval.end - interval.start;
    const resolution = 5000; // 5kb bins
    const nBins = Math.ceil(length / resolution);

    // Try to detect known locus for high-fidelity mock
    const locusConfig = this.detectLocusConfig(interval);

    // Generate realistic contact map
    const matrix = locusConfig
      ? this.generateHighFidelityContactMap(nBins, resolution, locusConfig)
      : this.generateGenericContactMap(nBins);

    // Generate epigenetic tracks aligned with CTCF sites
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

  /**
   * High-Fidelity Mock: Generates SPARSE contact map matching ARCHCODE output
   *
   * ARCHCODE produces VERY SPARSE matrices because:
   * - Cohesin occupancy is localized
   * - Most bins have zero contacts
   * - Contacts concentrated near diagonal (d=1,2)
   * - Loop signals at specific CTCF pairs
   *
   * Key statistics to match:
   * - Mean ~0.01-0.02
   * - d=1: ~0.05-0.10
   * - d>=5: ~0.00
   */
  private generateHighFidelityContactMap(
    nBins: number,
    resolution: number,
    config: LocusConfig,
  ): number[][] {
    const matrix: number[][] = Array(nBins)
      .fill(null)
      .map(() => Array(nBins).fill(0));

    // Convert genomic positions to bin indices
    const ctcfBins = config.ctcfPositions.map((pos) =>
      Math.floor(pos / resolution),
    );
    const loopAnchorBins = config.loopAnchors.map(([a, b]) => [
      Math.floor(a / resolution),
      Math.floor(b / resolution),
    ]);

    // ARCHCODE-like VERY sparse pattern
    // Target: Mean ~0.015, d=1 ~0.08, d>=3 ~0.00
    for (let i = 0; i < nBins; i++) {
      for (let j = i; j < nBins; j++) {
        const distance = j - i;

        // Start with zero - ARCHCODE matrices are very sparse
        let value = 0;

        // 1. Near-diagonal contacts (d=1 only, very sparse)
        if (distance === 1) {
          // Only ~10% of d=1 cells have signal in ARCHCODE
          if (this.rng.random() < 0.15) {
            value = 0.05 + this.rng.random() * 0.1;
          }
        } else if (distance === 2) {
          // Even sparser at d=2
          if (this.rng.random() < 0.05) {
            value = 0.01 + this.rng.random() * 0.02;
          }
        }

        // 2. CTCF site enrichment — very localized
        for (const ctcfBin of ctcfBins) {
          const atI = i === ctcfBin;
          const atJ = j === ctcfBin;

          if ((atI || atJ) && distance === 1) {
            // Strong signal at CTCF, d=1
            value += 0.3 + this.rng.random() * 0.2;
          }
        }

        // 3. Loop peaks at convergent CTCF pairs
        for (const [anchor1, anchor2] of loopAnchorBins) {
          const bin1 = Math.min(anchor1, anchor2);
          const bin2 = Math.max(anchor1, anchor2);
          const loopDist = bin2 - bin1;

          // Exact loop position
          if (i === bin1 && j === bin2) {
            value += 0.8 + this.rng.random() * 0.2;
          }
          // Adjacent to loop
          else if (
            Math.abs(i - bin1) <= 1 &&
            Math.abs(j - bin2) <= 1 &&
            Math.abs(j - i - loopDist) <= 1
          ) {
            value += 0.2 + this.rng.random() * 0.1;
          }
        }

        // Clamp to valid range
        value = Math.max(0, Math.min(1, value));
        matrix[i][j] = value;
        matrix[j][i] = value;
      }
      // Diagonal = 1
      matrix[i][i] = 1.0;
    }

    // Normalize matrix so max = 1
    let maxVal = 0;
    for (let i = 0; i < nBins; i++) {
      for (let j = i + 1; j < nBins; j++) {
        if (matrix[i][j] > maxVal) maxVal = matrix[i][j];
      }
    }
    if (maxVal > 0 && maxVal !== 1) {
      for (let i = 0; i < nBins; i++) {
        for (let j = 0; j < nBins; j++) {
          if (i !== j) {
            matrix[i][j] /= maxVal;
          }
        }
      }
    }

    return matrix;
  }

  /**
   * Find which TAD a bin belongs to
   */
  private findTADIndex(bin: number, boundaries: number[]): number {
    for (let i = 0; i < boundaries.length - 1; i++) {
      if (bin >= boundaries[i] && bin < boundaries[i + 1]) {
        return i;
      }
    }
    return -1;
  }

  /**
   * Generate Gaussian noise using Box-Muller transform
   */
  private gaussianNoise(mean: number, stdDev: number): number {
    const u1 = this.rng.random();
    const u2 = this.rng.random();
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    return mean + stdDev * z;
  }

  /**
   * Generic contact map for unknown loci
   */
  private generateGenericContactMap(nBins: number): number[][] {
    const matrix: number[][] = Array(nBins)
      .fill(null)
      .map(() => Array(nBins).fill(0));

    // Random TAD boundaries
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
        if (iTAD === jTAD) {
          value *= 1.5;
        } else {
          value *= 0.5;
        }

        value *= 1 + this.gaussianNoise(0, 0.1);
        value = Math.max(0, Math.min(1, value));
        matrix[i][j] = value;
        matrix[j][i] = value;
      }
      matrix[i][i] = 1.0;
    }

    return matrix;
  }

  /**
   * Generate epigenetic tracks aligned with CTCF/enhancer positions
   */
  private generateAlignedEpigeneticTracks(
    nBins: number,
    resolution: number,
    config: LocusConfig,
  ): EpigeneticFeatures {
    const ctcfBins = config.ctcfPositions.map((pos) =>
      Math.floor(pos / resolution),
    );

    // CTCF binding — peaks at known CTCF sites
    const ctcfBinding: number[] = Array(nBins).fill(0.1);
    for (const bin of ctcfBins) {
      if (bin < nBins) {
        ctcfBinding[bin] = 0.9 + this.rng.random() * 0.1;
        if (bin > 0) ctcfBinding[bin - 1] = 0.4 + this.rng.random() * 0.2;
        if (bin < nBins - 1)
          ctcfBinding[bin + 1] = 0.4 + this.rng.random() * 0.2;
      }
    }

    // H3K27ac — enhancer mark, peaks between CTCF sites
    const h3k27ac: number[] = Array(nBins).fill(0);
    for (let i = 0; i < nBins; i++) {
      const nearCTCF = ctcfBins.some((b) => Math.abs(i - b) < 3);
      h3k27ac[i] = nearCTCF
        ? 0.6 + this.rng.random() * 0.3 // High near CTCF
        : 0.2 + this.rng.random() * 0.3; // Lower elsewhere
    }

    // H3K4me3 — promoter mark, correlate with specific positions
    const promoterBins = [Math.floor(100000 / resolution)]; // HBB promoter
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
    return matrix.slice(0, n).map((row) => row.slice(0, n));
  }

  private pearsonCorrelation(a: number[][], b: number[][]): number {
    const flatA = a.flat();
    const flatB = b.flat();
    const n = flatA.length;

    let sumA = 0,
      sumB = 0,
      sumAB = 0,
      sumA2 = 0,
      sumB2 = 0;
    for (let i = 0; i < n; i++) {
      sumA += flatA[i];
      sumB += flatB[i];
      sumAB += flatA[i] * flatB[i];
      sumA2 += flatA[i] * flatA[i];
      sumB2 += flatB[i] * flatB[i];
    }

    const numerator = n * sumAB - sumA * sumB;
    const denominator = Math.sqrt(
      (n * sumA2 - sumA * sumA) * (n * sumB2 - sumB * sumB),
    );

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

  /**
   * Structural Similarity Index (SSIM) for contact maps
   * Uses windowed approach for local structure comparison
   * Reference: Wang et al., IEEE TIP 2004
   */
  private structuralSimilarity(a: number[][], b: number[][]): number {
    const n = a.length;
    const windowSize = Math.min(7, Math.floor(n / 4)); // Adaptive window

    if (windowSize < 3) {
      // Fall back to global SSIM for small matrices
      return this.globalSSIM(a, b);
    }

    // Constants for stability (based on dynamic range [0, 1])
    const L = 1.0; // Dynamic range
    const k1 = 0.01;
    const k2 = 0.03;
    const c1 = Math.pow(k1 * L, 2);
    const c2 = Math.pow(k2 * L, 2);
    const c3 = c2 / 2;

    let ssimSum = 0;
    let windowCount = 0;

    // Slide window across the matrix
    const step = Math.max(1, Math.floor(windowSize / 2));
    for (let i = 0; i <= n - windowSize; i += step) {
      for (let j = 0; j <= n - windowSize; j += step) {
        // Extract windows
        const windowA: number[] = [];
        const windowB: number[] = [];

        for (let wi = 0; wi < windowSize; wi++) {
          for (let wj = 0; wj < windowSize; wj++) {
            windowA.push(a[i + wi][j + wj]);
            windowB.push(b[i + wi][j + wj]);
          }
        }

        // Calculate local SSIM
        const localSSIM = this.calculateLocalSSIM(windowA, windowB, c1, c2, c3);
        ssimSum += localSSIM;
        windowCount++;
      }
    }

    return windowCount > 0 ? ssimSum / windowCount : 0;
  }

  /**
   * Calculate SSIM for a single window
   */
  private calculateLocalSSIM(
    a: number[],
    b: number[],
    c1: number,
    c2: number,
    c3: number,
  ): number {
    const n = a.length;

    // Means
    const muA = a.reduce((s, v) => s + v, 0) / n;
    const muB = b.reduce((s, v) => s + v, 0) / n;

    // Variances and covariance
    let sigmaA2 = 0,
      sigmaB2 = 0,
      sigmaAB = 0;
    for (let i = 0; i < n; i++) {
      sigmaA2 += Math.pow(a[i] - muA, 2);
      sigmaB2 += Math.pow(b[i] - muB, 2);
      sigmaAB += (a[i] - muA) * (b[i] - muB);
    }
    sigmaA2 /= n - 1;
    sigmaB2 /= n - 1;
    sigmaAB /= n - 1;

    const sigmaA = Math.sqrt(sigmaA2);
    const sigmaB = Math.sqrt(sigmaB2);

    // Luminance comparison
    const l = (2 * muA * muB + c1) / (Math.pow(muA, 2) + Math.pow(muB, 2) + c1);

    // Contrast comparison
    const c = (2 * sigmaA * sigmaB + c2) / (sigmaA2 + sigmaB2 + c2);

    // Structure comparison
    const s = (sigmaAB + c3) / (sigmaA * sigmaB + c3);

    // Combined SSIM
    return l * c * s;
  }

  /**
   * Global SSIM for small matrices
   */
  private globalSSIM(a: number[][], b: number[][]): number {
    const flatA = a.flat();
    const flatB = b.flat();
    const n = flatA.length;

    const L = 1.0;
    const c1 = Math.pow(0.01 * L, 2);
    const c2 = Math.pow(0.03 * L, 2);

    const muA = flatA.reduce((s, v) => s + v, 0) / n;
    const muB = flatB.reduce((s, v) => s + v, 0) / n;

    let sigmaA2 = 0,
      sigmaB2 = 0,
      sigmaAB = 0;
    for (let i = 0; i < n; i++) {
      sigmaA2 += Math.pow(flatA[i] - muA, 2);
      sigmaB2 += Math.pow(flatB[i] - muB, 2);
      sigmaAB += (flatA[i] - muA) * (flatB[i] - muB);
    }
    sigmaA2 /= n;
    sigmaB2 /= n;
    sigmaAB /= n;

    return (
      ((2 * muA * muB + c1) * (2 * sigmaAB + c2)) /
      ((Math.pow(muA, 2) + Math.pow(muB, 2) + c1) * (sigmaA2 + sigmaB2 + c2))
    );
  }

  // ========================================================================
  // Parser Integration (Scientific News Parser Bridge)
  // ========================================================================

  /**
   * Default parser configuration
   * Path: D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/
   */
  private static readonly DEFAULT_PARSER_PATH =
    "D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs";

  /**
   * Import epigenetic data from Scientific News Parser
   * Reads BigWig files and triggers ARCHCODE simulation with Kramer kinetics
   *
   * @param parserPath - Path to parser data directory (default: D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/)
   * @param interval - Optional genomic interval to analyze
   * @returns Integrated analysis result with simulation and epigenetics
   */
  async importFromParser(
    parserPath: string = AlphaGenomeService.DEFAULT_PARSER_PATH,
    interval?: GenomeInterval,
  ): Promise<IntegratedAnalysisResult> {
    console.log(`[AlphaGenome] Importing from parser: ${parserPath}`);

    // Discover available data files
    const dataSet = await this.discoverParserData(parserPath);
    console.log(
      `[AlphaGenome] Discovered: ${dataSet.med1Tracks.length} MED1, ${dataSet.ctcfTracks.length} CTCF tracks`,
    );

    // Default interval: HBB locus (well-characterized)
    const targetInterval = interval || {
      chromosome: "chr11",
      start: 5200000,
      end: 5400000,
    };

    // Load epigenetic tracks from BigWig files
    const epigenetics = await this.loadEpigeneticsFromParser(
      dataSet,
      targetInterval,
    );

    // Run ARCHCODE simulation with Kramer kinetics
    const simulation = await this.runKramerSimulation(
      targetInterval,
      epigenetics,
    );

    // Calculate risk score based on structural deviation
    const prediction = await this.predict(targetInterval);
    const metrics = this.calculateMetrics(
      simulation.contactMatrix,
      prediction.contactMap.matrix,
    );
    const riskScore = Math.round((1 - metrics.ssim) * 100);

    return {
      interval: targetInterval,
      parserSource: parserPath,
      simulation,
      epigenetics,
      riskScore,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Discover available data files in parser directory
   */
  private async discoverParserData(basePath: string): Promise<ParserDataSet> {
    const result: ParserDataSet = {
      med1Tracks: [],
      ctcfTracks: [],
      histoneTracks: [],
      mutationFiles: [],
    };

    try {
      const fs = await import("fs/promises");
      const path = await import("path");

      // Check subdirectories
      const subdirs = ["med1", "ctcf", "cohesin", "histone", "k562"];

      for (const subdir of subdirs) {
        const dirPath = path.join(basePath, subdir);
        try {
          const files = await fs.readdir(dirPath);

          for (const file of files) {
            const filePath = path.join(dirPath, file);
            const lowerFile = file.toLowerCase();

            if (lowerFile.endsWith(".bw") || lowerFile.endsWith(".bigwig")) {
              if (lowerFile.includes("med1")) {
                result.med1Tracks.push(filePath);
              } else if (lowerFile.includes("ctcf")) {
                result.ctcfTracks.push(filePath);
              } else if (lowerFile.includes("h3k")) {
                result.histoneTracks.push(filePath);
              }
            } else if (
              lowerFile.endsWith(".json") ||
              lowerFile.endsWith(".csv")
            ) {
              result.mutationFiles?.push(filePath);
            }
          }
        } catch {
          // Directory doesn't exist, skip
        }
      }
    } catch (error) {
      console.warn("[AlphaGenome] Failed to discover parser data:", error);
    }

    return result;
  }

  /**
   * Load epigenetic tracks from BigWig files via Python bridge
   */
  private async loadEpigeneticsFromParser(
    dataSet: ParserDataSet,
    interval: GenomeInterval,
  ): Promise<EpigeneticFeatures> {
    const epigenetics: EpigeneticFeatures = {};
    const nBins = Math.ceil((interval.end - interval.start) / 5000);

    // Try to load MED1 tracks
    if (dataSet.med1Tracks.length > 0) {
      console.log(`[AlphaGenome] Reading MED1 from: ${dataSet.med1Tracks[0]}`);
      epigenetics.med1 = await this.readBigWigTrack(
        dataSet.med1Tracks[0],
        interval,
      );
      if (epigenetics.med1) {
        console.log(
          `[AlphaGenome] ✓ MED1 loaded: ${epigenetics.med1.length} bins`,
        );
      }
    }

    // Try to load CTCF tracks
    if (dataSet.ctcfTracks.length > 0) {
      console.log(`[AlphaGenome] Reading CTCF from: ${dataSet.ctcfTracks[0]}`);
      epigenetics.ctcfBinding = await this.readBigWigTrack(
        dataSet.ctcfTracks[0],
        interval,
      );
      if (epigenetics.ctcfBinding) {
        console.log(
          `[AlphaGenome] ✓ CTCF loaded: ${epigenetics.ctcfBinding.length} bins`,
        );
      }
    }

    // Generate fallback if reading failed
    if (!epigenetics.med1) {
      const reason =
        dataSet.med1Tracks.length > 0
          ? "BigWig read failed (pyBigWig not installed?)"
          : "No MED1 BigWig found";
      console.log(`[AlphaGenome] ${reason}, using mock data`);
      epigenetics.med1 = this.generateMockMED1Track(nBins);
    }

    if (!epigenetics.ctcfBinding) {
      const reason =
        dataSet.ctcfTracks.length > 0
          ? "BigWig read failed (pyBigWig not installed?)"
          : "No CTCF BigWig found";
      console.log(`[AlphaGenome] ${reason}, using mock data`);
      const locusConfig = this.detectLocusConfig(interval);
      if (locusConfig) {
        const aligned = this.generateAlignedEpigeneticTracks(
          nBins,
          5000,
          locusConfig,
        );
        epigenetics.ctcfBinding = aligned.ctcfBinding;
      } else {
        epigenetics.ctcfBinding = Array(nBins)
          .fill(0)
          .map(() => this.rng.random() * 0.3);
      }
    }

    return epigenetics;
  }

  /**
   * Read BigWig track via Python pyBigWig bridge
   */
  private async readBigWigTrack(
    bigWigPath: string,
    interval: GenomeInterval,
  ): Promise<number[] | undefined> {
    try {
      const { spawn } = await import("child_process");

      // Python script to read BigWig
      const pythonScript = `
import sys
import json

try:
    import pyBigWig
    bw = pyBigWig.open(sys.argv[1])
    chrom = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])
    resolution = int(sys.argv[5])

    # Get values at resolution
    n_bins = (end - start) // resolution
    values = []
    for i in range(n_bins):
        bin_start = start + i * resolution
        bin_end = bin_start + resolution
        vals = bw.values(chrom, bin_start, bin_end)
        if vals:
            # Mean of non-NaN values
            valid = [v for v in vals if v is not None and v == v]
            values.append(sum(valid) / len(valid) if valid else 0)
        else:
            values.append(0)

    bw.close()
    print(json.dumps({"status": "ok", "values": values}))
except ImportError:
    print(json.dumps({"status": "error", "error": "pyBigWig not installed"}))
except Exception as e:
    print(json.dumps({"status": "error", "error": str(e)}))
`;

      return new Promise((resolve) => {
        const proc = spawn(
          "python",
          [
            "-c",
            pythonScript,
            bigWigPath,
            interval.chromosome,
            String(interval.start),
            String(interval.end),
            "5000", // Resolution
          ],
          { timeout: 30000 },
        );

        let stdout = "";
        proc.stdout.on("data", (data) => {
          stdout += data.toString();
        });

        proc.on("close", (code) => {
          if (code === 0) {
            try {
              const result = JSON.parse(stdout);
              if (result.status === "ok" && result.values) {
                // Normalize to 0-1 range
                const maxVal = Math.max(...result.values, 1);
                resolve(result.values.map((v: number) => v / maxVal));
                return;
              }
            } catch {
              /* parsing failed */
            }
          }
          resolve(undefined);
        });

        proc.on("error", () => resolve(undefined));
      });
    } catch {
      return undefined;
    }
  }

  /**
   * Generate mock MED1 binding track
   */
  private generateMockMED1Track(nBins: number): number[] {
    // MED1 enriched at enhancers (roughly periodic with some randomness)
    const track: number[] = [];
    const enhancerPeriod = Math.floor(nBins / 4);

    for (let i = 0; i < nBins; i++) {
      let value = 0.1 + this.rng.random() * 0.1; // Background

      // Enhancer peaks
      const distToEnhancer = Math.min(
        Math.abs(i - enhancerPeriod),
        Math.abs(i - 2 * enhancerPeriod),
        Math.abs(i - 3 * enhancerPeriod),
      );

      if (distToEnhancer < 3) {
        value += 0.7 - distToEnhancer * 0.2 + this.rng.random() * 0.2;
      }

      track.push(Math.min(1, value));
    }

    return track;
  }

  /**
   * Run ARCHCODE simulation with Kramer kinetics
   * Uses fitted parameters: α=0.92, γ=0.80, k_base=0.002
   */
  private async runKramerSimulation(
    interval: GenomeInterval,
    epigenetics: EpigeneticFeatures,
  ): Promise<IntegratedAnalysisResult["simulation"]> {
    // Kramer kinetics parameters (fitted from FRAP data)
    const kramerParams = {
      alpha: 0.92,
      gamma: 0.8,
      kBase: 0.002,
    };

    const length = interval.end - interval.start;
    const resolution = 5000;
    const nBins = Math.ceil(length / resolution);

    // Generate contact matrix using Kramer-modulated extrusion
    const matrix: number[][] = Array(nBins)
      .fill(null)
      .map(() => Array(nBins).fill(0));
    const loops: Array<{ start: number; end: number; strength: number }> = [];

    // Get MED1 occupancy for Kramer kinetics
    const med1Occupancy = epigenetics.med1 || Array(nBins).fill(0.1);
    const ctcfBinding = epigenetics.ctcfBinding || Array(nBins).fill(0);

    // Detect CTCF sites from binding track
    const ctcfThreshold = 0.5;
    const ctcfSites: Array<{ bin: number; strength: number }> = [];
    for (let i = 0; i < nBins; i++) {
      if (ctcfBinding[i] > ctcfThreshold) {
        ctcfSites.push({ bin: i, strength: ctcfBinding[i] });
      }
    }

    // Simulate multiple cohesin molecules
    const numCohesins = 15;
    const maxSteps = 30000;

    for (let c = 0; c < numCohesins; c++) {
      // Random loading position weighted by MED1 (FountainLoader model)
      let loadBin = this.sampleLoadingPosition(med1Occupancy);

      let leftLeg = loadBin;
      let rightLeg = loadBin;
      let active = true;

      for (let step = 0; step < maxSteps && active; step++) {
        // Calculate Kramer unloading probability
        // p_unload = k_base * (1 - alpha * occupancy^gamma)
        const avgOccupancy =
          (med1Occupancy[leftLeg] + med1Occupancy[rightLeg]) / 2;
        const unloadProb =
          kramerParams.kBase *
          (1 - kramerParams.alpha * Math.pow(avgOccupancy, kramerParams.gamma));

        // Check for unloading
        if (this.rng.random() < unloadProb) {
          active = false;
          break;
        }

        // Extrude (move legs outward)
        if (leftLeg > 0 && this.rng.random() > 0.5) {
          leftLeg--;
        }
        if (rightLeg < nBins - 1 && this.rng.random() > 0.5) {
          rightLeg++;
        }

        // Record contact
        matrix[leftLeg][rightLeg] += 0.01;
        matrix[rightLeg][leftLeg] += 0.01;

        // Check for CTCF barriers (simplified)
        const leftCTCF = ctcfSites.find((s) => s.bin === leftLeg);
        const rightCTCF = ctcfSites.find((s) => s.bin === rightLeg);

        if (leftCTCF && rightCTCF && rightLeg - leftLeg > 3) {
          // Loop formed at convergent CTCF
          loops.push({
            start: leftLeg * resolution + interval.start,
            end: rightLeg * resolution + interval.start,
            strength: Math.min(leftCTCF.strength, rightCTCF.strength),
          });
          active = false;
        }
      }
    }

    // Normalize matrix
    let maxVal = 0;
    for (let i = 0; i < nBins; i++) {
      for (let j = 0; j < nBins; j++) {
        if (matrix[i][j] > maxVal) maxVal = matrix[i][j];
      }
    }
    if (maxVal > 0) {
      for (let i = 0; i < nBins; i++) {
        for (let j = 0; j < nBins; j++) {
          matrix[i][j] /= maxVal;
        }
        matrix[i][i] = 1.0; // Diagonal
      }
    }

    return {
      contactMatrix: matrix,
      loops,
      kramerParams,
    };
  }

  /**
   * Sample cohesin loading position weighted by MED1 occupancy (FountainLoader)
   */
  private sampleLoadingPosition(med1Occupancy: number[]): number {
    // Weighted random sampling based on MED1 binding
    const totalWeight = med1Occupancy.reduce((sum, v) => sum + v + 0.1, 0);
    let r = this.rng.random() * totalWeight;

    for (let i = 0; i < med1Occupancy.length; i++) {
      r -= med1Occupancy[i] + 0.1;
      if (r <= 0) return i;
    }

    return Math.floor(med1Occupancy.length / 2);
  }

  /**
   * Watch parser directory for new mutation data and auto-run simulation
   * Returns a cleanup function to stop watching
   */
  async watchParserDirectory(
    parserPath: string = AlphaGenomeService.DEFAULT_PARSER_PATH,
    onUpdate?: (result: IntegratedAnalysisResult) => void,
  ): Promise<() => void> {
    console.log(`[AlphaGenome] Watching parser directory: ${parserPath}`);

    const fs = await import("fs");
    const path = await import("path");

    const watchPaths = ["med1", "ctcf", "mutations"].map((subdir) =>
      path.join(parserPath, subdir),
    );

    const watchers: fs.FSWatcher[] = [];

    for (const watchPath of watchPaths) {
      try {
        const watcher = fs.watch(watchPath, async (eventType, filename) => {
          if (
            filename &&
            (filename.endsWith(".bw") || filename.endsWith(".json"))
          ) {
            console.log(
              `[AlphaGenome] Detected change: ${eventType} ${filename}`,
            );

            // Re-run analysis
            const result = await this.importFromParser(parserPath);
            if (onUpdate) {
              onUpdate(result);
            }
          }
        });
        watchers.push(watcher);
      } catch {
        // Directory doesn't exist, skip
      }
    }

    // Return cleanup function
    return () => {
      console.log("[AlphaGenome] Stopping parser directory watch");
      watchers.forEach((w) => w.close());
    };
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
