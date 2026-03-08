/**
 * Analytical contact matrix simulation for V-CRISPR and reuse by atlas pipeline.
 * Logic extracted from scripts/generate-unified-atlas.ts (simulatePairedMatrices, SSIM).
 * Same formula: Kramer kinetics + CTCF barriers + MED1 occupancy landscape.
 */

import { SeededRandom } from "../../src/utils/random";
import { KRAMER_KINETICS } from "../../src/domain/constants/biophysics";

export interface EnhancerFeature {
  position: number;
  occupancy: number;
  name?: string;
}

export interface CtcfSiteFeature {
  position: number;
  orientation: string;
}

export interface LocusGeometry {
  windowStart: number;
  resolution: number;
  nBins: number;
}

/**
 * Build reference and mutant contact matrices (analytical mean-field).
 * When variantBin < 0, no variant is applied (ref and mut occupancy identical).
 */
export function simulatePairedMatrices(
  geometry: LocusGeometry,
  enhancers: EnhancerFeature[],
  ctcfSites: CtcfSiteFeature[],
  variantBin: number,
  effectStrength: number,
  category: string,
  seed: number,
): { reference: number[][]; mutant: number[][] } {
  const { windowStart, resolution, nBins } = geometry;
  const { K_BASE, DEFAULT_ALPHA, DEFAULT_GAMMA, BACKGROUND_OCCUPANCY } =
    KRAMER_KINETICS;

  const landscapeRng = new SeededRandom(seed);
  const baseLandscape: number[] = [];
  for (let i = 0; i < nBins; i++) {
    const genomicPos = windowStart + i * resolution;
    let occ = BACKGROUND_OCCUPANCY + landscapeRng.random() * 0.05;
    for (const enh of enhancers) {
      const dist = Math.abs(genomicPos - enh.position) / resolution;
      if (dist < 5) {
        occ += enh.occupancy * Math.exp(-0.5 * (dist * dist));
      }
    }
    baseLandscape.push(Math.min(1, occ));
  }

  const refOccupancy = [...baseLandscape];
  const mutOccupancy = baseLandscape.map((occ, i) => {
    if (variantBin >= 0) {
      const dist = Math.abs(i - variantBin);
      if (dist < 3) {
        const reduction = effectStrength + (1 - effectStrength) * (dist / 3);
        return occ * reduction;
      }
    }
    return occ;
  });

  const ctcfBins = ctcfSites
    .map((c) => Math.floor((c.position - windowStart) / resolution))
    .filter((b) => b >= 0 && b < nBins);
  const refCTCF = ctcfBins;
  const mutCTCF =
    category.includes("splice") || category.includes("promoter")
      ? ctcfBins.filter((b) => variantBin < 0 || Math.abs(b - variantBin) > 2)
      : ctcfBins;

  const refMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));
  const mutMatrix: number[][] = Array(nBins)
    .fill(null)
    .map(() => Array(nBins).fill(0));

  for (let i = 0; i < nBins; i++) {
    for (let j = i + 1; j < nBins; j++) {
      const dist = j - i;
      const distFactor = Math.pow(dist, -1.0);
      const refOccFactor = Math.sqrt(refOccupancy[i]! * refOccupancy[j]!);
      const mutOccFactor = Math.sqrt(mutOccupancy[i]! * mutOccupancy[j]!);
      let refPerm = 1.0;
      let mutPerm = 1.0;
      for (const ctcf of refCTCF) {
        if (ctcf > i && ctcf < j) refPerm *= 0.15;
      }
      for (const ctcf of mutCTCF) {
        if (ctcf > i && ctcf < j) mutPerm *= 0.15;
      }
      const refKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, refOccFactor), DEFAULT_GAMMA));
      const mutKramer =
        1 -
        K_BASE *
          (1 -
            DEFAULT_ALPHA *
              Math.pow(Math.max(0.001, mutOccFactor), DEFAULT_GAMMA));
      refMatrix[i]![j] =
        distFactor * refOccFactor * refPerm * refKramer;
      refMatrix[j]![i] = refMatrix[i]![j]!;
      mutMatrix[i]![j] =
        distFactor * mutOccFactor * mutPerm * mutKramer;
      mutMatrix[j]![i] = mutMatrix[i]![j]!;
    }
  }

  let maxVal = 0;
  for (let i = 0; i < nBins; i++) {
    for (let j = 0; j < nBins; j++) {
      if (refMatrix[i]![j]! > maxVal) maxVal = refMatrix[i]![j]!;
      if (mutMatrix[i]![j]! > maxVal) maxVal = mutMatrix[i]![j]!;
    }
  }
  if (maxVal > 0) {
    for (let i = 0; i < nBins; i++) {
      for (let j = 0; j < nBins; j++) {
        refMatrix[i]![j]! /= maxVal;
        mutMatrix[i]![j]! /= maxVal;
      }
    }
  }
  return { reference: refMatrix, mutant: mutMatrix };
}

export function calculateSSIM(a: number[][], b: number[][]): number {
  const flatA = a.flat();
  const flatB = b.flat();
  const muA = flatA.reduce((s, v) => s + v, 0) / flatA.length;
  const muB = flatB.reduce((s, v) => s + v, 0) / flatB.length;
  let sigmaA2 = 0,
    sigmaB2 = 0,
    sigmaAB = 0;
  for (let i = 0; i < flatA.length; i++) {
    sigmaA2 += Math.pow(flatA[i]! - muA, 2);
    sigmaB2 += Math.pow(flatB[i]! - muB, 2);
    sigmaAB += (flatA[i]! - muA) * (flatB[i]! - muB);
  }
  sigmaA2 /= flatA.length;
  sigmaB2 /= flatB.length;
  sigmaAB /= flatA.length;
  const c1 = 0.0001;
  const c2 = 0.0009;
  return (
    ((2 * muA * muB + c1) * (2 * sigmaAB + c2)) /
    ((muA * muA + muB * muB + c1) * (sigmaA2 + sigmaB2 + c2))
  );
}

const LOCAL_SSIM_WINDOW = 50;

export function calculateLocalSSIM(
  reference: number[][],
  mutant: number[][],
  variantBin: number,
  windowSize: number = LOCAL_SSIM_WINDOW,
): number {
  const n = reference.length;
  if (n <= windowSize) return calculateSSIM(reference, mutant);
  const halfWindow = Math.floor(windowSize / 2);
  let start = variantBin - halfWindow;
  let end = start + windowSize;
  if (start < 0) {
    start = 0;
    end = windowSize;
  }
  if (end > n) {
    end = n;
    start = n - windowSize;
  }
  const refSub: number[][] = [];
  const mutSub: number[][] = [];
  for (let i = start; i < end; i++) {
    const refRow: number[] = [];
    const mutRow: number[] = [];
    for (let j = start; j < end; j++) {
      refRow.push(reference[i]![j]!);
      mutRow.push(mutant[i]![j]!);
    }
    refSub.push(refRow);
    mutSub.push(mutRow);
  }
  return calculateSSIM(refSub, mutSub);
}

/**
 * Mean contact frequency between promoter bin and LCR bins (upper triangle).
 */
export function computePromoterLCRContact(
  matrix: number[][],
  promoterBin: number,
  lcrBins: number[],
): number {
  if (lcrBins.length === 0) return 0;
  let sum = 0;
  for (const lcrBin of lcrBins) {
    const i = Math.min(promoterBin, lcrBin);
    const j = Math.max(promoterBin, lcrBin);
    sum += matrix[i]![j]! ?? 0;
  }
  return sum / lcrBins.length;
}
