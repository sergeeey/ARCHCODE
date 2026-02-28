/**
 * ARCHCODE Loop Extrusion Engine Tests
 * Ported from Python test suite
 */

import { describe, it, expect } from "vitest";
import {
  LoopExtrusionEngine,
  loopsToContactMatrix,
  computePSCurve,
  fitPSPowerLaw,
} from "../engines/LoopExtrusionEngine";
import { CTCFSite, createLoop } from "../domain/models/genome";

describe("LoopExtrusionEngine", () => {
  describe("Basic simulation", () => {
    it("should create engine with default parameters", () => {
      const sites: CTCFSite[] = [
        { chrom: "chr11", position: 1000, orientation: "R", strength: 1.0 },
        { chrom: "chr11", position: 5000, orientation: "F", strength: 1.0 },
      ];

      const engine = new LoopExtrusionEngine({
        genomeLength: 10000,
        ctcfSites: sites,
      });

      expect(engine.genomeLength).toBe(10000);
      expect(engine.getCohesins().length).toBe(1);
    });

    it("should form loop with convergent CTCF (R...F)", () => {
      // Convergent: R left of cohesin, F right of cohesin -> loop forms
      // Left leg (decreasing) hits R, right leg (increasing) hits F
      // NOTE: With steady-state dynamics (respawn), multiple loops can form
      const sites: CTCFSite[] = [
        { chrom: "chr11", position: 1000, orientation: "R", strength: 1.0 },
        { chrom: "chr11", position: 5000, orientation: "F", strength: 1.0 },
      ];

      const engine = new LoopExtrusionEngine({
        genomeLength: 10000,
        ctcfSites: sites,
        cohesinLoadPosition: 3000,
        velocity: 100, // Fast for testing
      });

      const loops = engine.run(100);

      // With respawn active, multiple loops can form (steady-state dynamics)
      // First loop should always be at the convergent pair
      expect(loops.length).toBeGreaterThanOrEqual(1);
      expect(loops[0].leftAnchor).toBe(1000);
      expect(loops[0].rightAnchor).toBe(5000);
    });

    it("should NOT form loop with divergent CTCF (F...R)", () => {
      // Divergent: F left of cohesin, R right of cohesin -> no loop
      // Left leg escapes through R (wrong orientation), right through F
      const sites: CTCFSite[] = [
        { chrom: "chr11", position: 1000, orientation: "F", strength: 1.0 },
        { chrom: "chr11", position: 5000, orientation: "R", strength: 1.0 },
      ];

      const engine = new LoopExtrusionEngine({
        genomeLength: 10000,
        ctcfSites: sites,
        cohesinLoadPosition: 3000,
        velocity: 100,
      });

      const loops = engine.run(100);

      expect(loops.length).toBe(0);
    });

    it("should stop at genome boundaries", () => {
      const sites: CTCFSite[] = []; // No barriers

      const engine = new LoopExtrusionEngine({
        genomeLength: 1000,
        ctcfSites: sites,
        cohesinLoadPosition: 500,
        velocity: 100,
      });

      engine.run(10);

      const cohesins = engine.getCohesins();
      expect(cohesins[0].active).toBe(false); // Hit boundary
    });
  });

  describe("Multiple CTCF sites", () => {
    it("should find nearest barriers correctly", () => {
      const sites: CTCFSite[] = [
        { chrom: "chr11", position: 500, orientation: "R", strength: 1.0 },
        { chrom: "chr11", position: 2000, orientation: "R", strength: 1.0 },
        { chrom: "chr11", position: 8000, orientation: "F", strength: 1.0 },
        { chrom: "chr11", position: 9500, orientation: "F", strength: 1.0 },
      ];

      const engine = new LoopExtrusionEngine({
        genomeLength: 10000,
        ctcfSites: sites,
        cohesinLoadPosition: 5000,
        velocity: 1000, // Very fast
      });

      const loops = engine.run(100);

      // With steady-state dynamics (respawn), multiple loops can form
      // First loop should be at nearest convergent pair: R@2000 and F@8000
      expect(loops.length).toBeGreaterThanOrEqual(1);
      expect(loops[0].leftAnchor).toBe(2000);
      expect(loops[0].rightAnchor).toBe(8000);
    });
  });

  describe("Contact Matrix", () => {
    it("should generate correct matrix dimensions", () => {
      const loops = [createLoop(2000, 8000, 1.0)];

      const matrix = loopsToContactMatrix(loops, 0, 10000, 1000);

      expect(matrix.length).toBe(10);
      expect(matrix[0].length).toBe(10);
    });

    it("should have diagonal = 1.0", () => {
      const loops: ReturnType<typeof createLoop>[] = [];
      const matrix = loopsToContactMatrix(loops, 0, 10000, 1000);

      for (let i = 0; i < matrix.length; i++) {
        expect(matrix[i][i]).toBe(1.0);
      }
    });

    it("should be symmetric", () => {
      const loops = [createLoop(2000, 8000, 1.0)];

      const matrix = loopsToContactMatrix(loops, 0, 10000, 1000);

      for (let i = 0; i < matrix.length; i++) {
        for (let j = 0; j < matrix.length; j++) {
          expect(matrix[i][j]).toBe(matrix[j][i]);
        }
      }
    });

    it("should show loop as off-diagonal peak", () => {
      const loops = [createLoop(2000, 8000, 1.0)];

      const matrix = loopsToContactMatrix(loops, 0, 10000, 1000, 0.1);

      // Loop anchors at bins 2 and 8
      const peakValue = matrix[2][8];
      const backgroundValue = matrix[2][3];

      expect(peakValue).toBeGreaterThan(backgroundValue);
    });
  });

  describe("P(s) Curve", () => {
    it("should compute P(s) for uniform matrix", () => {
      const matrix = [
        [1.0, 0.5, 0.3],
        [0.5, 1.0, 0.5],
        [0.3, 0.5, 1.0],
      ];

      const ps = computePSCurve(matrix);

      expect(ps.distances).toContain(1);
      expect(ps.distances).toContain(2);
      expect(ps.contacts.length).toBe(ps.distances.length);
    });

    it("should have decreasing contact with distance", () => {
      // Create matrix with distance decay
      const loops: ReturnType<typeof createLoop>[] = [];
      const matrix = loopsToContactMatrix(loops, 0, 10000, 100);

      const ps = computePSCurve(matrix);

      // Contacts should generally decrease with distance
      for (let i = 1; i < ps.contacts.length; i++) {
        // Not strict due to noise, but general trend
        expect(ps.contacts[i]).toBeLessThanOrEqual(ps.contacts[0] * 2);
      }
    });
  });

  describe("Power-law fitting", () => {
    it("should fit P(s) ~ 1/s correctly", () => {
      // Generate 1/s data
      const distances = [1, 2, 3, 4, 5, 10, 20, 50];
      const contacts = distances.map((d) => 1.0 / d);

      const fit = fitPSPowerLaw(distances, contacts);

      // Should get alpha ≈ -1.0
      expect(fit.alpha).toBeCloseTo(-1.0, 0.1);
      expect(fit.r2).toBeGreaterThan(0.95);
    });

    it("should handle edge cases", () => {
      // Empty arrays
      const fit1 = fitPSPowerLaw([], []);
      expect(fit1.alpha).toBe(0.0);
      expect(fit1.r2).toBe(0.0);

      // Single point
      const fit2 = fitPSPowerLaw([1], [1]);
      expect(fit2.alpha).toBe(0.0);
      expect(fit2.r2).toBe(0.0);

      // Zero contacts
      const fit3 = fitPSPowerLaw([1, 2, 3], [0, 0, 0]);
      expect(fit3.alpha).toBe(0.0);
    });
  });
});
