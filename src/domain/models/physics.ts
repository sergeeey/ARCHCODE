/**
 * ARCHCODE Physics Engine
 * Loop extrusion simulation with biologically accurate CTCF logic
 *
 * NOTE: This module is used by genome.store.ts for visualization.
 * Uses SeededRandom via utils/random: call setGlobalSeed(seed) for reproducibility.
 */

import {
  CohesinLoop,
  GenomeElement,
  CTCFSite,
  LoopStatus,
  CTCFInteraction,
  CTCFOrientation,
} from "./genome";
import {
  COHESIN_PARAMS,
  CTCF_PARAMS,
  HETEROCHROMATIN_PARAMS,
  SIMULATION_CONFIG,
} from "../constants/biophysics";
import { random } from "../../utils/random";

/**
 * Check if CTCF sites are in convergent orientation
 * Convergent: Forward (F, >) on left, Reverse (R, <) on right
 * This creates a "trap" for cohesin
 */
function isConvergent(leftSite: CTCFSite, rightSite: CTCFSite): boolean {
  return leftSite.orientation === "F" && rightSite.orientation === "R";
}

/**
 * Check CTCF blocking interaction
 * Returns whether cohesin should stop and the efficiency of blocking
 */
export function checkCTCFBlocking(
  loop: CohesinLoop,
  ctcfSite: CTCFSite,
  approachDirection: "left" | "right",
): CTCFInteraction {
  // Determine if this is a convergent interaction
  // For left leg approaching: need forward (F, >) CTCF
  // For right leg approaching: need reverse (R, <) CTCF
  const isConvergentOrientation =
    (approachDirection === "left" && ctcfSite.orientation === "F") ||
    (approachDirection === "right" && ctcfSite.orientation === "R");

  if (isConvergentOrientation) {
    // Convergent: high probability of blocking
    return {
      shouldStop: random() < CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY,
      efficiency: CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY,
      isConvergent: true,
    };
  } else {
    // Non-convergent: leaky, low probability of blocking
    return {
      shouldStop: random() < CTCF_PARAMS.NON_CONVERGENT_BLOCKING_EFFICIENCY,
      efficiency: CTCF_PARAMS.NON_CONVERGENT_BLOCKING_EFFICIENCY,
      isConvergent: false,
    };
  }
}

/**
 * Calculate extrusion speed considering friction from heterochromatin
 */
export function calculateExtrusionSpeed(
  position: number,
  elements: Map<string, GenomeElement>,
): number {
  // Check for heterochromatin within detection range
  for (const element of elements.values()) {
    if (element.type === "HETEROCHROMATIN") {
      const distance = Math.abs(element.position - position);
      if (distance < HETEROCHROMATIN_PARAMS.DETECTION_RANGE_BP) {
        return (
          COHESIN_PARAMS.EXTRUSION_SPEED_BP_PER_S *
          HETEROCHROMATIN_PARAMS.FRICTION_FACTOR
        );
      }
    }
  }
  return COHESIN_PARAMS.EXTRUSION_SPEED_BP_PER_S;
}

/**
 * Check if loop should spontaneously unload based on processivity
 */
export function shouldUnload(loop: CohesinLoop): boolean {
  // Probability-based unloading to achieve exponential distribution
  return random() < COHESIN_PARAMS.UNLOADING_PROBABILITY;
}

/**
 * Check if loop should respawn at bookmarking site
 */
export function shouldBookmark(): boolean {
  return random() < COHESIN_PARAMS.BOOKMARKING_EFFICIENCY;
}

/**
 * Create a new cohesin loop at a random position
 */
export function createLoop(
  genomeLength: number,
  existingLoops: CohesinLoop[],
): CohesinLoop {
  const id = `loop-${Date.now()}-${random().toString(36).substr(2, 9)}`;

  // Random loading position
  const startPos = Math.floor(random() * genomeLength);

  // Calculate processivity from exponential distribution
  const meanTicks =
    COHESIN_PARAMS.MEAN_PROCESSIVITY_S /
    SIMULATION_CONFIG.BIOLOGICAL_TIME_SCALE;
  const processivity = Math.floor(-Math.log(random()) * meanTicks);

  return {
    id,
    startPosition: startPos,
    leftAnchor: startPos,
    rightAnchor: startPos + 1, // Start with minimal loop
    status: "growing",
    processivityRemaining: processivity,
    lifetimeTicks: 0,
    strength: 1.0,
  };
}

/**
 * Main physics step: update all loops for one simulation tick
 */
export interface PhysicsStepResult {
  updatedLoops: CohesinLoop[];
  bookmarkingSites: number[]; // Sites where loops unloaded (for respawning)
}

export function stepPhysics(
  loops: CohesinLoop[],
  elements: Map<string, GenomeElement>,
  genomeLength: number,
): PhysicsStepResult {
  const updatedLoops: CohesinLoop[] = [];
  const bookmarkingSites: number[] = [];

  for (const loop of loops) {
    // Skip already unloaded loops
    if (loop.status === "unloaded") continue;

    // 1. Check spontaneous unloading (processivity limit)
    if (shouldUnload(loop)) {
      bookmarkingSites.push(loop.startPosition);
      continue; // Remove this loop
    }

    // 2. Handle stalled loops
    if (loop.status === "stalled_both") {
      updatedLoops.push({
        ...loop,
        lifetimeTicks: loop.lifetimeTicks + 1,
      });
      continue;
    }

    // 3. Extrude loop
    let newLeft = loop.leftAnchor;
    let newRight = loop.rightAnchor;
    let newStatus: LoopStatus = "growing";
    let stalledByLeft: string | undefined = loop.stalledByLeft;
    let stalledByRight: string | undefined = loop.stalledByRight;

    const timeStepSeconds = SIMULATION_CONFIG.BIOLOGICAL_TIME_SCALE;

    // Calculate speeds with friction
    const leftSpeed =
      calculateExtrusionSpeed(newLeft, elements) * timeStepSeconds;
    const rightSpeed =
      calculateExtrusionSpeed(newRight, elements) * timeStepSeconds;

    // Move left leg (if not stalled and not at boundary)
    if (!stalledByLeft && newLeft > 0) {
      let blocked = false;

      // Check for CTCF barriers
      for (const element of elements.values()) {
        if (
          element.type === "CTCF_FORWARD" ||
          element.type === "CTCF_REVERSE"
        ) {
          const ctcf = element as CTCFSite;
          // Check if we would cross this CTCF
          if (ctcf.position < newLeft && ctcf.position >= newLeft - leftSpeed) {
            const interaction = checkCTCFBlocking(loop, ctcf, "left");
            if (interaction.shouldStop) {
              newLeft = ctcf.position;
              stalledByLeft = ctcf.id;
              blocked = true;
              break;
            }
          }
        }
      }

      if (!blocked) {
        newLeft = Math.max(0, newLeft - leftSpeed);
      }
    }

    // Move right leg (if not stalled and not at boundary)
    if (!stalledByRight && newRight < genomeLength) {
      let blocked = false;

      // Check for CTCF barriers
      for (const element of elements.values()) {
        if (
          element.type === "CTCF_FORWARD" ||
          element.type === "CTCF_REVERSE"
        ) {
          const ctcf = element as CTCFSite;
          // Check if we would cross this CTCF
          if (
            ctcf.position > newRight &&
            ctcf.position <= newRight + rightSpeed
          ) {
            const interaction = checkCTCFBlocking(loop, ctcf, "right");
            if (interaction.shouldStop) {
              newRight = ctcf.position;
              stalledByRight = ctcf.id;
              blocked = true;
              break;
            }
          }
        }
      }

      if (!blocked) {
        newRight = Math.min(genomeLength, newRight + rightSpeed);
      }
    }

    // Determine status
    if (stalledByLeft && stalledByRight) {
      newStatus = "stalled_both";
    } else if (stalledByLeft) {
      newStatus = "stalled_left";
    } else if (stalledByRight) {
      newStatus = "stalled_right";
    } else {
      newStatus = "growing";
    }

    updatedLoops.push({
      ...loop,
      leftAnchor: newLeft,
      rightAnchor: newRight,
      status: newStatus,
      stalledByLeft,
      stalledByRight,
      lifetimeTicks: loop.lifetimeTicks + 1,
      processivityRemaining: loop.processivityRemaining - 1,
    });
  }

  return { updatedLoops, bookmarkingSites };
}

/**
 * Respawn loops at bookmarking sites
 */
export function respawnLoops(
  bookmarkingSites: number[],
  existingLoops: CohesinLoop[],
  genomeLength: number,
): CohesinLoop[] {
  const newLoops: CohesinLoop[] = [];

  for (const site of bookmarkingSites) {
    if (shouldBookmark()) {
      const newLoop = createLoop(genomeLength, existingLoops);
      newLoop.startPosition = site;
      newLoop.leftAnchor = site;
      newLoop.rightAnchor = site + 1;
      newLoops.push(newLoop);
    }
  }

  return newLoops;
}
