/**
 * Seedable Random Number Generator
 * Based on Mulberry32 for fast, deterministic randomness
 *
 * Usage:
 *   const rng = new SeededRandom(42);
 *   const value = rng.random(); // 0-1, deterministic for seed=42
 */

export class SeededRandom {
  private state: number;

  constructor(seed: number = Date.now()) {
    this.state = seed;
  }

  /**
   * Get next random number in [0, 1)
   */
  random(): number {
    // Mulberry32 algorithm
    let t = (this.state += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  /**
   * Random integer in [min, max)
   */
  randomInt(min: number, max: number): number {
    return Math.floor(this.random() * (max - min)) + min;
  }

  /**
   * Random float in [min, max)
   */
  randomFloat(min: number, max: number): number {
    return this.random() * (max - min) + min;
  }

  /**
   * Reset to initial seed
   */
  reset(seed: number): void {
    this.state = seed;
  }

  /**
   * Random number from standard normal distribution (Box-Muller transform)
   * @param mean Mean of the distribution (default: 0)
   * @param std Standard deviation (default: 1)
   */
  gaussian(mean: number = 0, std: number = 1): number {
    // Box-Muller transform
    const u1 = this.random();
    const u2 = this.random();
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    return mean + z0 * std;
  }
}

// Global instance for non-deterministic randomness
let globalRng: SeededRandom | null = null;

/**
 * Get global RNG (lazy initialization)
 */
export function getGlobalRNG(): SeededRandom {
  if (!globalRng) {
    globalRng = new SeededRandom();
  }
  return globalRng;
}

/**
 * Set global seed for reproducibility
 */
export function setGlobalSeed(seed: number): void {
  globalRng = new SeededRandom(seed);
}

/**
 * Deterministic random (uses global RNG if initialized, else Math.random)
 */
export function random(): number {
  return globalRng ? globalRng.random() : Math.random();
}

/**
 * Deterministic random int
 */
export function randomInt(min: number, max: number): number {
  return globalRng
    ? globalRng.randomInt(min, max)
    : Math.floor(Math.random() * (max - min)) + min;
}
