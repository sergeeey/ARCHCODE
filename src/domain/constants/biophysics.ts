/**
 * ARCHCODE Biophysical Constants
 * Source: Literature-based values for loop extrusion simulation
 *
 * References:
 * - Extrusion speed: 0.5 kb/s mean for COHESIN (Davidson et al., Science 2019)
 *   NOTE: Ganji et al. 2018 studied CONDENSIN (up to 1.5 kb/s), not cohesin!
 * - Cohesin processivity: ~33 kb average loop size (Davidson et al., 2019)
 *   MODEL PARAMETER: 600 kb used for domain-scale simulation
 * - Cohesin residence time: ~20 min (Gerlich et al., 2006; Hansen et al., 2017)
 * - CTCF residence time: ~1-5 min (Hansen et al., 2017)
 * - Convergent CTCF efficiency: MODEL PARAMETER estimated from Rao et al. 2014 Hi-C loop enrichment
 *
 * IMPORTANT: Distinguish LITERATURE-BASED (measured) vs MODEL PARAMETER (fit/assumed)
 */

export const COHESIN_KINETICS = {
  // LITERATURE-BASED, NOT FITTED TO A REPOSITORY FRAP DATASET
  // Gerlich et al. (2006) Curr Biol; Hansen et al. (2017) eLife
  residenceTimeSeconds: 1200, // ~20 min conservative baseline
  unloadingProbPerStep: 0.000833, // 1/1200 steps

  // EXPLORATORY PARAMETERS: grid-search estimates, no direct FRAP fit
  alpha: 0.92,
  gamma: 0.8,
} as const;

// Time scaling (separate simulation time from render time)
export const SIMULATION_CONFIG = {
  // Target simulation step in milliseconds (real-time rendering)
  TIME_STEP_MS: 100, // 10 simulation steps per second for UI smoothness

  // Biological time scaling
  // 1 simulation step = 1 second biological time
  // NOTE: This is a tunable mapping parameter, not a physical constant.
  // Steps are discrete simulation events; biological time is approximate.
  BIOLOGICAL_TIME_SCALE: 1, // seconds per simulation step

  // Visual smoothing (interpolation factor)
  INTERPOLATION_FACTOR: 0.3,
} as const;

// Cohesin parameters
// NOTE: These are MODEL PARAMETERS (assumed defaults), not measured constants.
// Calibrate against experimental data (Hi-C, ChIA-PET) for specific cell types.
export const COHESIN_PARAMS = {
  // Extrusion speed
  // LITERATURE: Davidson et al. (2019) Science - human cohesin single-molecule
  //   - Mean rate: 0.5 kb/s (500 bp/s)
  //   - Maximum: ~2.1 kb/s
  // WARNING: Ganji et al. (2018) studied CONDENSIN, not cohesin!
  // MODEL VALUE: 1000 bp/s (upper range for faster dynamics)
  EXTRUSION_SPEED_BP_PER_S: 1000, // base pairs per second (MODEL PARAMETER)

  // Processivity (loop size before unloading)
  // LITERATURE: Davidson et al. (2019) - 33 kb average extruded loop
  // MODEL VALUE: 600 kb (scaled for domain-level simulation)
  // JUSTIFICATION: Higher value compensates for simplified dynamics,
  //   allows formation of large TADs observed in Hi-C
  PROCESSIVITY_KB: 600, // MODEL PARAMETER (literature: ~33 kb single-molecule)

  // Processivity: mean residence time ~20 min (literature range 10-30 min)
  // Source: literature ranges (Gerlich et al., 2006; Hansen et al., 2017)
  // NOTE: Baseline target, not fitted to a local FRAP dataset
  MEAN_PROCESSIVITY_S: 20 * 60, // 20 minutes in seconds

  // Unloading probability (per simulation step)
  // Calculated from: p = 1 / (MEAN_PROCESSIVITY_S / BIOLOGICAL_TIME_SCALE)
  // p = 1 / 1200 ≈ 0.000833 for 20 min at 1s/step
  //
  // EFFECTIVE RESIDENCE TIME IN STEPS: ~1200 steps (not minutes)
  // The mapping to real time depends on BIOLOGICAL_TIME_SCALE
  UNLOADING_PROBABILITY: 0.000833, // baseline for ~20 min at dt=1s

  // Bookmarking efficiency: probability to respawn at unloading site
  // Source: Assumed default (no direct measurement available)
  // Literature suggests "memory" of loading sites but quantitative data limited
  BOOKMARKING_EFFICIENCY: 0.5, // MODEL PARAMETER (assumed)
} as const;

// CTCF parameters
// NOTE: These are MODEL PARAMETERS estimated from ensemble data, not single-molecule constants.
// Convergent efficiency represents population-average blocking across many cohesin-CTCF encounters.
export const CTCF_PARAMS = {
  // Convergent rule efficiency (probability that convergent CTCF stops cohesin)
  // Convergent = Reverse (< ) on left, Forward (> ) on right
  //
  // Source: Rao et al. (2014) Cell - convergent CTCF pairs enriched at loop anchors
  // Interpretation: ~85% of convergent pairs form loops in wild-type (estimated from Hi-C)
  // NOTE: Single-molecule efficiency may differ; this is ensemble parameter
  CONVERGENT_BLOCKING_EFFICIENCY: 0.85, // MODEL PARAMETER (ensemble average)

  // Non-convergent blocking efficiency (leaky barriers)
  // Non-convergent = divergent (F...R) or tandem (F...F, R...R)
  // Source: de Wit et al. (2015) Cell - some loops form without convergent CTCF
  // Interpretation: ~15% of non-convergent pairs may still block (leaky)
  NON_CONVERGENT_BLOCKING_EFFICIENCY: 0.15, // MODEL PARAMETER (leakiness)

  // Distance threshold for CTCF recognition (base pairs)
  RECOGNITION_DISTANCE_BP: 100,
} as const;

/**
 * Kramer kinetics parameters for Mediator-dependent cohesin unloading.
 * Formula: P_unload = K_BASE × (1 - α × MED1_occupancy^γ)
 *
 * CALIBRATION STATUS:
 * - K_BASE: derived from literature residence time (~20 min, Gerlich 2006)
 * - DEFAULT_ALPHA, DEFAULT_GAMMA: grid-search estimates, NOT fitted to FRAP data
 * - Occupancy levels: MODEL PARAMETERS (assumed from ChIP-seq enrichment patterns)
 */
export const KRAMER_KINETICS = {
  K_BASE: 0.002, // base unloading probability per step
  DEFAULT_ALPHA: 0.92, // MED1 sensitivity (grid-search estimate)
  DEFAULT_GAMMA: 0.8, // nonlinearity exponent (grid-search estimate)
  BACKGROUND_OCCUPANCY: 0.1, // MED1 at non-enhancer regions (assumed)
  ENHANCER_OCCUPANCY: 0.8, // MED1 at active enhancers (assumed from ChIP-seq)
  INSULATOR_OCCUPANCY: 0.05, // MED1 at insulator/CTCF regions (assumed)
} as const;

// Genome visualization scaling
export const VISUALIZATION_CONFIG = {
  // 3D scene scaling
  DNA_LENGTH_VISUAL: 1000, // visual units
  SCALE_BP_TO_VISUAL: 0.01, // 1 bp = 0.01 visual units

  // Default genome parameters
  DEFAULT_GENOME_LENGTH_BP: 500000, // 500 kb typical TAD
  DEFAULT_VIEW_CENTER_BP: 250000, // Center view at middle

  /** Длительность импульса «loop_formed» (мс): и таймаут сброса pulseLoops, и анимация эмиссии в 3D */
  LOOP_PULSE_MS: 850,
} as const;

/**
 * Blind-test validation parameters
 * Source: Sabaté et al., 2024 (bioRxiv, DOI: 10.1101/2024.08.09.605990)
 * NOTE: bioRxiv preprint, NOT a Nature Genetics 2025 publication (which does not exist).
 * Loop duration target: 6–19 min (experimental range from literature)
 * Time mapping: 1 simulation step = 1 second
 */
export const SABATE_BIORXIV_2024 = {
  EXTRUSION_SPEED_BP_PER_STEP: 300, // 0.3 kb/s
  UNLOADING_PROBABILITY: 0.001, // 1/1000, T_res ≈ 16.67 min
  LOADING_PROBABILITY_PER_STEP: 1 / 3600, // ~1 event per hour per TAD
  MEAN_RESIDENCE_STEPS: 1000, // 16.67 min at 1s/step
  LOOP_DURATION_TARGET_MIN_STEPS: 360, // 6 min
  LOOP_DURATION_TARGET_MAX_STEPS: 1140, // 19 min
} as const;

/** @deprecated Use SABATE_BIORXIV_2024 instead. Kept for import compatibility during cleanup. */
export const SABATE_NATURE_2025 = SABATE_BIORXIV_2024;

// Heterochromatin (friction) parameters
export const HETEROCHROMATIN_PARAMS = {
  // Speed reduction when cohesin encounters heterochromatin
  FRICTION_FACTOR: 0.1, // 10% of normal speed

  // Detection range (base pairs)
  DETECTION_RANGE_BP: 500,
} as const;

// Test scenarios (from validation document)
export const VALIDATION_SCENARIOS = {
  PCDH: {
    name: "Pcdh Locus",
    description:
      "Tests convergent CTCF logic - inversion should switch loop direction",
    length: 100000,
    elements: [
      { position: 30000, type: "CTCF_FORWARD" as const },
      { position: 70000, type: "CTCF_REVERSE" as const },
    ],
  },
  HBB: {
    name: "HBB (Beta-globin)",
    description:
      "Tests insulator function - deletion should cause contact leak",
    length: 100000,
    elements: [
      { position: 25000, type: "CTCF_FORWARD" as const },
      { position: 30000, type: "HETEROCHROMATIN" as const },
      { position: 75000, type: "CTCF_REVERSE" as const },
    ],
  },
  SOX2: {
    name: "Sox2 Locus",
    description: "Tests structure-function link",
    length: 80000,
    elements: [
      { position: 20000, type: "CTCF_FORWARD" as const },
      { position: 60000, type: "CTCF_REVERSE" as const },
      { position: 40000, type: "ENHANCER" as const },
    ],
  },
} as const;
