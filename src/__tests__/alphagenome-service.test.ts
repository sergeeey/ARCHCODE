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
});
