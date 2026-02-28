/**
 * ARCHCODE Domain Models
 * Unified type system for genome simulation
 * Ported from Python ARCHCODE (loop_extrusion_minimal.py)
 */

// ============================================================================
// CTCF (CCCTC-binding factor) - Boundary elements
// ============================================================================

export type CTCFOrientation = "F" | "R";

export interface CTCFSite {
  readonly chrom: string;
  readonly position: number;
  readonly orientation: CTCFOrientation;
  readonly strength: number;
}

export function createCTCFSite(
  chrom: string,
  position: number,
  orientation: CTCFOrientation,
  strength: number = 1.0,
): CTCFSite {
  if (position < 0) {
    throw new Error(`position must be >= 0, got: ${position}`);
  }
  if (strength < 0.0 || strength > 1.0) {
    throw new Error(`strength must be in [0.0, 1.0], got: ${strength}`);
  }
  return { chrom, position, orientation, strength };
}

// ============================================================================
// Cohesin Complex - Loop extrusion motor
// ============================================================================

export interface CohesinComplex {
  leftLeg: number;
  rightLeg: number;
  velocity: number;
  active: boolean;
  loopFormed: boolean;
  /** True when cohesin is holding a loop (not moving, can unload stochastically). */
  loopHolding?: boolean;
  /** Anchors of the loop being held (for recording dissolvedAtStep). */
  loopLeft?: number;
  loopRight?: number;
}

export function createCohesinComplex(
  loadPosition: number,
  velocity: number = 1000, // Default matches biophysics constant
): CohesinComplex {
  // INV-1: leftLeg < rightLeg must hold
  // Initialize with minimal offset to avoid 0-size loop at t=0
  return {
    leftLeg: loadPosition,
    rightLeg: loadPosition + 1, // Minimal offset for INV-1
    velocity,
    active: true,
    loopFormed: false,
  };
}

export function stepCohesin(cohesin: CohesinComplex): void {
  if (cohesin.active) {
    cohesin.leftLeg -= Math.floor(cohesin.velocity);
    cohesin.rightLeg += Math.floor(cohesin.velocity);
  }
}

export function getCohesinLoopSize(cohesin: CohesinComplex): number {
  return cohesin.rightLeg - cohesin.leftLeg;
}

// ============================================================================
// Loop - Formed chromatin loop
// ============================================================================

export interface Loop {
  readonly leftAnchor: number;
  readonly rightAnchor: number;
  readonly strength: number;
  /** Step when loop formed (for duration tracking). */
  formedAtStep?: number;
  /** Step when cohesin unloaded (loop dissolved). */
  dissolvedAtStep?: number;
}

export function createLoop(
  leftAnchor: number,
  rightAnchor: number,
  strength: number = 1.0,
  formedAtStep?: number,
): Loop {
  return { leftAnchor, rightAnchor, strength, formedAtStep };
}

/** Duration in steps (undefined if loop not yet dissolved). */
export function getLoopDurationSteps(loop: Loop): number | undefined {
  if (loop.dissolvedAtStep == null || loop.formedAtStep == null)
    return undefined;
  return loop.dissolvedAtStep - loop.formedAtStep;
}

export function getChromatinLoopSize(loop: Loop): number {
  return loop.rightAnchor - loop.leftAnchor;
}

// ============================================================================
// Contact Matrix
// ============================================================================

export type ContactMatrix = number[][];

export interface PSCurve {
  distances: number[];
  contacts: number[];
}

export interface PowerLawFit {
  alpha: number;
  r2: number;
}

// ============================================================================
// Simulation Configuration
// ============================================================================

export interface SimulationConfig {
  genomeLength: number;
  resolution: number;
  backgroundLevel: number;
  velocity: number;
  maxSteps: number;
}

export const DEFAULT_CONFIG: SimulationConfig = {
  genomeLength: 100000,
  resolution: 1000,
  backgroundLevel: 0.1,
  velocity: 1000, // bp/step (Davidson et al. 2019: 0.5-2 kb/s for cohesin)
  maxSteps: 10000,
};

// ============================================================================
// Legacy types (for backward compatibility)
// ============================================================================

export type ElementType =
  | "CTCF_FORWARD"
  | "CTCF_REVERSE"
  | "ENHANCER"
  | "SILENCER"
  | "PROMOTER"
  | "GENE"
  | "HETEROCHROMATIN"
  | "BOUNDARY"
  | "NONE";

export interface GenomeElement {
  id: string;
  position: number;
  type: ElementType;
  chromosome?: string;
  metadata?: Record<string, unknown>;
}

export interface TAD {
  id: string;
  start: number;
  end: number;
  boundaryLeft: string;
  boundaryRight: string;
  stability: number;
  loops: string[];
}

export interface SimulationState {
  elements: Map<string, GenomeElement>;
  loops: CohesinLoop[];
  tads: TAD[];
  timeStep: number;
  biologicalTime: number;
  isRunning: boolean;
  config: import("../constants/biophysics").SimulationConfig;
}

// ============================================================================
// Cohesin loop state (legacy, for visualization)
// ============================================================================

export type LoopStatus =
  | "growing"
  | "stalled_left"
  | "stalled_right"
  | "stalled_both"
  | "unloaded";

export interface CohesinLoop {
  id: string;
  startPosition: number;
  leftAnchor: number;
  rightAnchor: number;
  status: LoopStatus;
  processivityRemaining: number;
  lifetimeTicks: number;
  stalledByLeft?: string;
  stalledByRight?: string;
  strength: number;
  color?: string;
}
