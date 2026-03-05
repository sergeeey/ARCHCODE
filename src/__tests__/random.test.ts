import { describe, it, expect, beforeEach } from "vitest";
import {
  SeededRandom,
  getGlobalRNG,
  setGlobalSeed,
  random,
  randomInt,
} from "../utils/random";

describe("SeededRandom", () => {
  it("produces deterministic sequence for same seed", () => {
    const a = new SeededRandom(42);
    const b = new SeededRandom(42);

    const seqA = Array.from({ length: 10 }, () => a.random());
    const seqB = Array.from({ length: 10 }, () => b.random());

    expect(seqA).toEqual(seqB);
  });

  it("random() stays in [0, 1)", () => {
    const rng = new SeededRandom(7);
    for (let i = 0; i < 200; i++) {
      const v = rng.random();
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });

  it("randomInt() stays in [min, max)", () => {
    const rng = new SeededRandom(99);
    for (let i = 0; i < 200; i++) {
      const v = rng.randomInt(3, 11);
      expect(v).toBeGreaterThanOrEqual(3);
      expect(v).toBeLessThan(11);
      expect(Number.isInteger(v)).toBe(true);
    }
  });

  it("randomFloat() stays in [min, max)", () => {
    const rng = new SeededRandom(5);
    for (let i = 0; i < 200; i++) {
      const v = rng.randomFloat(-2.5, 3.5);
      expect(v).toBeGreaterThanOrEqual(-2.5);
      expect(v).toBeLessThan(3.5);
    }
  });

  it("gaussian() returns finite values", () => {
    const rng = new SeededRandom(123);
    for (let i = 0; i < 200; i++) {
      const v = rng.gaussian(10, 2);
      expect(Number.isFinite(v)).toBe(true);
    }
  });

  it("reset(seed) reproduces sequence", () => {
    const rng = new SeededRandom(17);
    const first = Array.from({ length: 5 }, () => rng.random());
    rng.reset(17);
    const second = Array.from({ length: 5 }, () => rng.random());
    expect(second).toEqual(first);
  });
});

describe("global random helpers", () => {
  beforeEach(() => {
    setGlobalSeed(2026);
  });

  it("random() is deterministic after setGlobalSeed", () => {
    const seqA = Array.from({ length: 8 }, () => random());
    setGlobalSeed(2026);
    const seqB = Array.from({ length: 8 }, () => random());
    expect(seqA).toEqual(seqB);
  });

  it("randomInt() uses global deterministic RNG", () => {
    const seqA = Array.from({ length: 8 }, () => randomInt(10, 20));
    setGlobalSeed(2026);
    const seqB = Array.from({ length: 8 }, () => randomInt(10, 20));
    expect(seqA).toEqual(seqB);
    for (const v of seqA) {
      expect(v).toBeGreaterThanOrEqual(10);
      expect(v).toBeLessThan(20);
    }
  });

  it("getGlobalRNG returns singleton instance until reseeded", () => {
    const a = getGlobalRNG();
    const b = getGlobalRNG();
    expect(a).toBe(b);
  });
});
