/**
 * ARCHCODE Biophysical Constants
 * Source: Literature-based values for loop extrusion simulation
 * 
 * References:
 * - Extrusion speed: 0.5-2 kb/s (Sanborn et al., PNAS 2015; Ganji et al., Science 2018)
 * - Cohesin processivity: ~20 min average residence time (Gerlich et al., 2006)
 * - CTCF residence time: ~1-5 min (Hansen et al., 2017)
 * - Convergent CTCF efficiency: ~80-95% (Rao et al., Cell 2014)
 */

// Time scaling (separate simulation time from render time)
export const SIMULATION_CONFIG = {
    // Target simulation step in milliseconds (real-time)
    TIME_STEP_MS: 100, // 10 simulation steps per second
    
    // Biological time scaling
    // 1 simulation step = 1 second biological time
    BIOLOGICAL_TIME_SCALE: 1, // seconds per simulation step
    
    // Visual smoothing (interpolation factor)
    INTERPOLATION_FACTOR: 0.3,
} as const;

// Cohesin parameters
export const COHESIN_PARAMS = {
    // Extrusion speed: 0.5-2 kb/s (average ~1 kb/s)
    EXTRUSION_SPEED_BP_PER_S: 1000, // base pairs per second
    
    // Processivity: average residence time ~20 minutes
    // Convert to simulation ticks (at 10 steps/s = 20 min * 60 s / 0.1 s = 12000 ticks)
    MEAN_PROCESSIVITY_S: 20 * 60, // 20 minutes in seconds
    
    // Unloading probability (per simulation step)
    // Calculated to achieve mean residence time
    UNLOADING_PROBABILITY: 0.0005, // ~1/2000 chance per step
    
    // Bookmarking efficiency: probability to respawn at unloading site
    BOOKMARKING_EFFICIENCY: 0.5, // 50% chance to respawn
} as const;

// CTCF parameters
export const CTCF_PARAMS = {
    // Convergent rule efficiency (how often CTCF stops cohesin)
    // Forward (> ) on left, Reverse (< ) on right = Convergent = 80-95% blocking
    CONVERGENT_BLOCKING_EFFICIENCY: 0.85,
    
    // Non-convergent (divergent or tandem) = leaky, ~10-20% blocking
    NON_CONVERGENT_BLOCKING_EFFICIENCY: 0.15,
    
    // Distance threshold for CTCF recognition (base pairs)
    RECOGNITION_DISTANCE_BP: 100,
} as const;

// Genome visualization scaling
export const VISUALIZATION_CONFIG = {
    // 3D scene scaling
    DNA_LENGTH_VISUAL: 1000, // visual units
    SCALE_BP_TO_VISUAL: 0.01, // 1 bp = 0.01 visual units
    
    // Default genome parameters
    DEFAULT_GENOME_LENGTH_BP: 500000, // 500 kb typical TAD
    DEFAULT_VIEW_CENTER_BP: 250000, // Center view at middle
} as const;

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
        name: 'Pcdh Locus',
        description: 'Tests convergent CTCF logic - inversion should switch loop direction',
        length: 100000,
        elements: [
            { position: 30000, type: 'CTCF_FORWARD' as const },
            { position: 70000, type: 'CTCF_REVERSE' as const },
        ],
    },
    HBB: {
        name: 'HBB (Beta-globin)',
        description: 'Tests insulator function - deletion should cause contact leak',
        length: 100000,
        elements: [
            { position: 25000, type: 'CTCF_FORWARD' as const },
            { position: 30000, type: 'HETEROCHROMATIN' as const },
            { position: 75000, type: 'CTCF_REVERSE' as const },
        ],
    },
    SOX2: {
        name: 'Sox2 Locus',
        description: 'Tests structure-function link',
        length: 80000,
        elements: [
            { position: 20000, type: 'CTCF_FORWARD' as const },
            { position: 60000, type: 'CTCF_REVERSE' as const },
            { position: 40000, type: 'ENHANCER' as const },
        ],
    },
} as const;
