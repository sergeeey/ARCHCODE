import { afterEach, describe, expect, it, vi } from "vitest";

import {
  DEFAULT_CONFIG,
  createCTCFSite,
  createCohesinComplex,
  createLoop,
  getChromatinLoopSize,
  getCohesinLoopSize,
  getLoopDurationSteps,
  stepCohesin,
} from "../domain/models/genome";
import { computePSCurve, loopsToContactMatrix } from "../engines/contactMatrix";

describe("genome model helpers", () => {
  it("validates CTCF site position and strength bounds", () => {
    expect(() => createCTCFSite("chr11", -1, "F")).toThrow(
      "position must be >= 0",
    );
    expect(() => createCTCFSite("chr11", 10, "R", 1.5)).toThrow(
      "strength must be in [0.0, 1.0]",
    );
  });

  it("steps active cohesin and preserves inactive cohesin coordinates", () => {
    const active = createCohesinComplex(500, 12.9);
    stepCohesin(active);

    expect(active.leftLeg).toBe(488);
    expect(active.rightLeg).toBe(513);
    expect(getCohesinLoopSize(active)).toBe(25);

    const inactive = createCohesinComplex(1000, 50);
    inactive.active = false;
    stepCohesin(inactive);

    expect(inactive.leftLeg).toBe(1000);
    expect(inactive.rightLeg).toBe(1001);
  });

  it("computes loop duration only after dissolution and exposes default config", () => {
    const activeLoop = createLoop(100, 250, 0.8, 10);
    expect(getLoopDurationSteps(activeLoop)).toBeUndefined();

    const dissolvedLoop = { ...activeLoop, dissolvedAtStep: 17 };
    expect(getLoopDurationSteps(dissolvedLoop)).toBe(7);
    expect(getChromatinLoopSize(dissolvedLoop)).toBe(150);

    expect(DEFAULT_CONFIG).toMatchObject({
      genomeLength: 100000,
      resolution: 1000,
      backgroundLevel: 0.1,
      velocity: 1000,
      maxSteps: 10000,
    });
  });
});

describe("contact matrix guard rails", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("falls back on invalid ranges and resolutions", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    expect(loopsToContactMatrix([], 5000, 1000, 1000)).toEqual([[1.0]]);

    const matrix = loopsToContactMatrix([], 0, 5000, 0);
    expect(matrix.length).toBe(5);
    expect(matrix[0][0]).toBe(1.0);
    expect(warn).toHaveBeenCalled();
  });

  it("ignores invalid loop coordinates and handles empty P(s) inputs", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    const matrix = loopsToContactMatrix(
      [{ leftAnchor: Number.NaN, rightAnchor: 100, strength: 1.0 }],
      0,
      5000,
      1000,
    );
    expect(matrix[0][1]).toBe(0.05);

    expect(computePSCurve([])).toEqual({ distances: [], contacts: [] });
    expect(computePSCurve([[1], [2, 3]])).toEqual({
      distances: [],
      contacts: [],
    });

    expect(warn).toHaveBeenCalled();
  });
});
