import { describe, it, expect, beforeEach, afterEach } from "vitest";
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
});
