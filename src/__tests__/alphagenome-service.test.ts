import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { AlphaGenomeService } from "../services/AlphaGenomeService";

describe("AlphaGenomeService strict-real contract", () => {
  const interval = { chromosome: "chr11", start: 5200000, end: 5300000 };
  const originalApiKey = process.env.ALPHAGENOME_API_KEY;
  const originalViteApiKey = process.env.VITE_ALPHAGENOME_API_KEY;

  beforeEach(() => {
    delete process.env.ALPHAGENOME_API_KEY;
    delete process.env.VITE_ALPHAGENOME_API_KEY;
  });

  afterEach(() => {
    if (originalApiKey === undefined) delete process.env.ALPHAGENOME_API_KEY;
    else process.env.ALPHAGENOME_API_KEY = originalApiKey;

    if (originalViteApiKey === undefined)
      delete process.env.VITE_ALPHAGENOME_API_KEY;
    else process.env.VITE_ALPHAGENOME_API_KEY = originalViteApiKey;
  });

  it("fails closed in strict-real mode without API key", async () => {
    const service = new AlphaGenomeService({ mode: "strict-real", apiKey: "" });
    await expect(service.predict(interval)).rejects.toThrow(
      /PR GATE FAILURE \[strict-real\]: AlphaGenome API key is missing/i,
    );
  });

  it("marks fallback provenance in real mode without API key", async () => {
    const service = new AlphaGenomeService({ mode: "real", apiKey: "" });
    const prediction = await service.predict(interval);

    expect(prediction.provenance).toBeDefined();
    expect(prediction.provenance?.mode).toBe("real");
    expect(prediction.provenance?.source).toBe("Local Synthetic Generator");
    expect(prediction.provenance?.isFallback).toBe(true);
  });

  it("masks apiKey in getConfig()", () => {
    const service = new AlphaGenomeService({ mode: "real", apiKey: "secret" });
    const cfg = service.getConfig();
    expect(cfg.apiKey).toBe("***");
    expect(cfg.mode).toBe("real");
  });

  it("reports live availability by mode+key", () => {
    const mockSvc = new AlphaGenomeService({ mode: "mock", apiKey: "k" });
    expect(mockSvc.isLiveAvailable()).toBe(false);

    const realWithKey = new AlphaGenomeService({ mode: "real", apiKey: "k" });
    expect(realWithKey.isLiveAvailable()).toBe(true);

    const realNoKey = new AlphaGenomeService({ mode: "real", apiKey: "" });
    expect(realNoKey.isLiveAvailable()).toBe(false);
  });

  it("supports live alias and blocks real/strict-real mode switch without key", () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    service.setMode("live");
    expect(service.getConfig().mode).toBe("mock");

    service.setMode("strict-real");
    expect(service.getConfig().mode).toBe("mock");
  });

  it("setApiKey promotes mode from mock to real", () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    expect(service.getConfig().mode).toBe("mock");
    service.setApiKey("new-key");
    expect(service.getConfig().mode).toBe("real");
  });

  it("caches prediction per interval", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const p1 = await service.predict(interval);
    const p2 = await service.predict(interval);

    expect(p2).toBe(p1);
    expect(p1.provenance?.source).toBe("Local Synthetic Generator");
    expect(p1.provenance?.isFallback).toBe(false);
  });

  it("clearCache forces regeneration for same interval", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const p1 = await service.predict(interval);
    service.clearCache();
    const p2 = await service.predict(interval);
    expect(p2).not.toBe(p1);
  });

  it("validateArchcode returns metrics in range", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const matrix = [
      [1, 0.5, 0.2],
      [0.5, 1, 0.3],
      [0.2, 0.3, 1],
    ];
    const result = await service.validateArchcode(interval, matrix);
    expect(result.prediction.contactMap.matrix.length).toBeGreaterThan(0);
    expect(result.metrics.pearsonR).toBeGreaterThanOrEqual(-1);
    expect(result.metrics.pearsonR).toBeLessThanOrEqual(1);
    expect(result.metrics.spearmanRho).toBeGreaterThanOrEqual(-1);
    expect(result.metrics.spearmanRho).toBeLessThanOrEqual(1);
    expect(result.metrics.mse).toBeGreaterThanOrEqual(0);
    expect(result.metrics.rmse).toBeGreaterThanOrEqual(0);
  });

  it("triangulate returns consensus and pair metrics", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const a = [
      [1, 0.6, 0.1],
      [0.6, 1, 0.4],
      [0.1, 0.4, 1],
    ];
    const h = [
      [1, 0.55, 0.2],
      [0.55, 1, 0.35],
      [0.2, 0.35, 1],
    ];

    const out = await service.triangulate(interval, a, h);
    expect(out.consensus).toMatch(
      /ARCHCODE_WINS|ALPHAGENOME_WINS|TIE|INSUFFICIENT_DATA/,
    );
    expect(out.interpretation.length).toBeGreaterThan(0);
    expect(out.archcode_vs_hic.pearsonR).toBeGreaterThanOrEqual(-1);
    expect(out.archcode_vs_hic.pearsonR).toBeLessThanOrEqual(1);
  });

  it("uses real-mode fallback on live error when apiKey exists", async () => {
    const service = new AlphaGenomeService({ mode: "real", apiKey: "k" });
    (service as any).fetchLivePrediction = vi
      .fn()
      .mockRejectedValue(new Error("boom"));

    const p = await service.predict(interval);
    expect(p.provenance?.mode).toBe("real");
    expect(p.provenance?.isFallback).toBe(true);
    expect(p.provenance?.source).toBe("Local Synthetic Generator");
  });

  it("fails closed in strict-real when live call fails", async () => {
    const service = new AlphaGenomeService({ mode: "strict-real", apiKey: "k" });
    (service as any).fetchLivePrediction = vi
      .fn()
      .mockRejectedValue(new Error("api down"));

    await expect(service.predict(interval)).rejects.toThrow(
      /PR GATE FAILURE \[strict-real\]: API call failed/i,
    );
  });

  it("fails closed in strict-real when live returns mock model", async () => {
    const service = new AlphaGenomeService({ mode: "strict-real", apiKey: "k" });
    (service as any).fetchLivePrediction = vi.fn().mockResolvedValue({
      interval,
      contactMap: {
        matrix: [
          [1, 0.2],
          [0.2, 1],
        ],
        resolution: 5000,
        normalization: "oe_ratio",
      },
      epigenetics: {},
      confidence: 0.9,
      modelVersion: "mock-v1",
      timestamp: new Date().toISOString(),
    });

    await expect(service.predict(interval)).rejects.toThrow(
      /External service returned a mock response/i,
    );
  });

  it("importFromParser works with empty local directory via mock fallbacks", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const result = await service.importFromParser(".", interval);

    expect(result.interval.chromosome).toBe(interval.chromosome);
    expect(result.simulation.contactMatrix.length).toBeGreaterThan(0);
    expect(result.simulation.kramerParams.alpha).toBeCloseTo(0.92, 2);
    expect(result.riskScore).toBeGreaterThanOrEqual(0);
    expect(result.riskScore).toBeLessThanOrEqual(100);
  });

  it("watchParserDirectory returns cleanup function even if dirs are absent", async () => {
    const service = new AlphaGenomeService({ mode: "mock", apiKey: "" });
    const cleanup = await service.watchParserDirectory("__no_such_dir__");
    expect(typeof cleanup).toBe("function");
    cleanup();
  });
});
