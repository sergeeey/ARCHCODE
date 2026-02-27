/**
 * ARCHCODE Loop Extrusion Engine
 * TypeScript port of MinimalLoopExtrusionEngine from Python
 * 
 * Simulates chromatin loop formation via cohesin extrusion with CTCF barriers.
 */

import {
    CTCFSite,
    CTCFOrientation,
    CohesinComplex,
    Loop,
    createCohesinComplex,
    stepCohesin,
    createLoop,
    ContactMatrix,
} from '../domain/models/genome';
import { SeededRandom } from '../utils/random';
import { loopsToContactMatrix } from './contactMatrix';
import { CTCF_PARAMS } from '../domain/constants/biophysics';

export interface EngineConfig {
    genomeLength: number;
    ctcfSites: CTCFSite[];
    cohesinLoadPosition?: number;
    velocity?: number;
    seed?: number;
    maxCohesins?: number;  // Limit to prevent memory leaks (default: 1000)
}

export class LoopExtrusionEngine {
    readonly genomeLength: number;
    readonly ctcfSites: CTCFSite[];
    readonly velocity: number;
    readonly seed: number;
    readonly maxCohesins: number;
    
    private cohesins: CohesinComplex[];
    private loops: Loop[];
    private stepCount: number;
    private rng: SeededRandom;
    private isDestroyed: boolean = false;

    constructor(config: EngineConfig) {
        this.genomeLength = config.genomeLength;
        this.ctcfSites = [...config.ctcfSites].sort((a, b) => a.position - b.position);
        this.velocity = config.velocity ?? 1000;  // Fixed: was 1.0, should be 1000 bp/s
        this.seed = config.seed ?? 42;
        this.maxCohesins = config.maxCohesins ?? 1000;
        
        this.rng = new SeededRandom(this.seed);
        
        const loadPosition = config.cohesinLoadPosition ?? Math.floor(this.genomeLength / 2);
        
        this.cohesins = [createCohesinComplex(loadPosition, this.velocity)];
        this.loops = [];
        this.stepCount = 0;

        console.log(`[Engine] Created with ${this.ctcfSites.length} CTCF sites, cohesin @ ${loadPosition}, genome: ${this.genomeLength}bp`);
        console.log(`[Engine] CTCF positions:`, this.ctcfSites.map(s => `${s.orientation}@${s.position}`).join(', '));
    }

    /**
     * Find nearest CTCF barrier in specified direction
     */
    private findNearestCTCF(
        position: number,
        direction: 'left' | 'right',
        orientationFilter: CTCFOrientation
    ): CTCFSite | null {
        const candidates = this.ctcfSites.filter(
            site => site.orientation === orientationFilter
        );

        if (direction === 'left') {
            const validCandidates = candidates.filter(s => s.position < position);
            if (validCandidates.length === 0) return null;
            return validCandidates.reduce((max, s) => s.position > max.position ? s : max);
        } else {
            const validCandidates = candidates.filter(s => s.position > position);
            if (validCandidates.length === 0) return null;
            return validCandidates.reduce((min, s) => s.position < min.position ? s : min);
        }
    }


    private isFiniteNumber(value: number): boolean {
        return Number.isFinite(value);
    }

    private isValidCohesinState(cohesin: CohesinComplex): boolean {
        if (!this.isFiniteNumber(cohesin.leftLeg) || !this.isFiniteNumber(cohesin.rightLeg)) {
            console.warn(`[Step ${this.stepCount}] Invalid cohesin state: non-finite legs`, cohesin);
            return false;
        }
        if (cohesin.leftLeg >= cohesin.rightLeg) {
            console.warn(`[Step ${this.stepCount}] Invalid cohesin state: leftLeg >= rightLeg`, cohesin);
            return false;
        }
        return true;
    }

    private isValidLoopAnchors(left: number, right: number): boolean {
        if (!this.isFiniteNumber(left) || !this.isFiniteNumber(right)) {
            return false;
        }
        if (left < 0 || right > this.genomeLength) {
            return false;
        }
        if (left >= right) {
            return false;
        }
        return true;
    }

    /**
     * Check if cohesin legs hit CTCF barriers
     * Returns true if both legs hit convergent barriers (loop formed)
     * Convergent: R (< ) on left, F (> ) on right = forms loop
     */
    private checkBarriers(cohesin: CohesinComplex): boolean {
        // Left leg moves leftward (decreasing), blocked by reverse CTCF (R <)
        const leftBarriers = this.ctcfSites.filter(
            site => site.orientation === 'R' && site.position <= cohesin.leftLeg
        );
        const leftBarrier = leftBarriers.length > 0
            ? leftBarriers.reduce((max, s) => s.position > max.position ? s : max)
            : null;

        // Right leg moves rightward (increasing), blocked by forward CTCF (F >)
        const rightBarriers = this.ctcfSites.filter(
            site => site.orientation === 'F' && site.position >= cohesin.rightLeg
        );
        const rightBarrier = rightBarriers.length > 0
            ? rightBarriers.reduce((min, s) => s.position < min.position ? s : min)
            : null;

        const leftBlocked = leftBarrier !== null;
        const rightBlocked = rightBarrier !== null;

        // Debug logging
        if (leftBarrier || rightBarrier) {
            console.log(`[Step ${this.stepCount}] LEF @ ${cohesin.leftLeg}-${cohesin.rightLeg}`, 
                `Left: ${leftBarrier ? 'R@' + leftBarrier.position : 'none'}`,
                `Right: ${rightBarrier ? 'F@' + rightBarrier.position : 'none'}`,
                `Convergent: ${leftBlocked && rightBlocked}`);
        }

        // Loop forms when both legs are blocked (convergent: R...F where R=left, F=right)
        if (leftBlocked && rightBlocked && leftBarrier && rightBarrier) {
            // Stochastic blocking: use convergent efficiency (85% default)
            const blockingEfficiency = CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY;
            if (this.rng.random() < blockingEfficiency) {
                cohesin.active = false;
                cohesin.loopFormed = true;

                const leftPos = leftBarrier.position;
                const rightPos = rightBarrier.position;
                if (!this.isValidLoopAnchors(leftPos, rightPos)) {
                    console.warn(`[Step ${this.stepCount}] Invalid loop anchors: ${leftPos}-${rightPos}`);
                    return false;
                }

                const loop = createLoop(
                    leftPos,
                    rightPos,
                    Math.min(leftBarrier.strength, rightBarrier.strength) * blockingEfficiency
                );
                this.loops.push(loop);

                console.log(`[Step ${this.stepCount}] ✅ LOOP FORMED (eff=${blockingEfficiency}):`,
                    `${leftBarrier.position} - ${rightBarrier.position}`,
                    `(${rightBarrier.position - leftBarrier.position} bp)`);

                return true;
            }
            // If blocking fails, cohesin continues (leaky barrier)
            console.log(`[Step ${this.stepCount}] ⚡ Leaky pass-through at convergent pair`);
        }

        return false;
    }

    /**
     * Check if cohesin hit genome boundaries
     */
    private checkBoundaries(cohesin: CohesinComplex): boolean {
        if (cohesin.leftLeg < 0 || cohesin.rightLeg > this.genomeLength) {
            cohesin.active = false;
            return true;
        }
        return false;
    }

    /**
     * Execute one simulation step
     */
    step(): boolean {
        if (this.isDestroyed) {
            console.warn('[Engine] Cannot step: engine is destroyed');
            return false;
        }
        
        this.stepCount++;

        // Debug: log if no cohesins
        if (this.cohesins.length === 0) {
            console.warn(`[Step ${this.stepCount}] ⚠️ NO COHESINS!`);
            return false;
        }

        // Debug: log active cohesins count (every 100 steps)
        if (this.stepCount % 100 === 0) {
            const activeCount = this.cohesins.filter(c => c.active).length;
            console.log(`[Step ${this.stepCount}] Active: ${activeCount}/${this.cohesins.length}, Loops: ${this.loops.length}`);
        }

        // Cleanup: remove old inactive cohesins to prevent memory leak
        // Keep last 100 inactive cohesins for analysis
        if (this.cohesins.length > this.maxCohesins) {
            const inactiveCount = this.cohesins.filter(c => !c.active).length;
            if (inactiveCount > 100) {
                // Remove oldest inactive cohesins
                const toRemove = inactiveCount - 100;
                let removed = 0;
                this.cohesins = this.cohesins.filter(c => {
                    if (!c.active && removed < toRemove) {
                        removed++;
                        return false;
                    }
                    return true;
                });
                console.log(`[Step ${this.stepCount}] Cleanup: removed ${removed} inactive cohesins`);
            }
        }

        for (const cohesin of this.cohesins) {
            if (!cohesin.active) continue;

            stepCohesin(cohesin);
            if (!this.isValidCohesinState(cohesin)) {
                cohesin.active = false;
                continue;
            }
            this.checkBarriers(cohesin);
            this.checkBoundaries(cohesin);
        }

        const hasActive = this.cohesins.some(c => c.active);

        // Auto-respawn: если все cohesin неактивны, добавляем новый
        if (!hasActive && this.cohesins.length < this.maxCohesins) {
            if (this.loops.length === 0) {
                console.warn(`[Step ${this.stepCount}] ⚠️ All cohesins inactive, no loops formed!`);
            }
            // Use seedable RNG for reproducibility
            const newPos = this.rng.randomInt(
                Math.floor(this.genomeLength * 0.1),
                Math.floor(this.genomeLength * 0.9)
            );
            this.cohesins.push(createCohesinComplex(newPos, this.velocity));
            console.log(`[Step ${this.stepCount}] 🔄 Respawned cohesin @ ${newPos}`);
            return true;
        }

        return hasActive;
    }

    /**
     * Run simulation until completion or max_steps reached
     */
    run(maxSteps: number = 10000): Loop[] {
        while (this.stepCount < maxSteps) {
            const shouldContinue = this.step();
            if (!shouldContinue) break;
        }
        return this.loops;
    }

    /**
     * Generate contact matrix from simulation results
     */
    getContactMatrix(resolution: number, backgroundLevel: number = 0.1): ContactMatrix {
        return loopsToContactMatrix(
            this.loops,
            0,
            this.genomeLength,
            resolution,
            backgroundLevel
        );
    }

    getLoops(): Loop[] {
        return [...this.loops];
    }

    getStepCount(): number {
        return this.stepCount;
    }

    getCohesins(): CohesinComplex[] {
        return this.cohesins.map(c => ({ ...c }));
    }

    // Control methods for UI integration
    start(): void {
        if (this.isDestroyed) return;
        
        // Mark all inactive cohesins as active again (reload)
        for (const cohesin of this.cohesins) {
            if (!cohesin.active && !cohesin.loopFormed) {
                cohesin.active = true;
            }
        }
        // If all stopped, add new cohesin
        if (!this.cohesins.some(c => c.active) && this.cohesins.length < this.maxCohesins) {
            const loadPosition = Math.floor(this.genomeLength / 2);
            this.cohesins.push(createCohesinComplex(loadPosition, this.velocity));
        }
    }

    pause(): void {
        // No-op for this implementation - step() controls execution
    }

    reset(): void {
        if (this.isDestroyed) return;
        
        this.loops = [];
        this.stepCount = 0;
        this.rng.reset(this.seed);
        const loadPosition = Math.floor(this.genomeLength / 2);
        this.cohesins = [createCohesinComplex(loadPosition, this.velocity)];
    }

    /**
     * Cleanup resources (call on component unmount)
     */
    destroy(): void {
        this.isDestroyed = true;
        this.cohesins = [];
        this.loops = [];
    }

    /**
     * Check if engine is destroyed
     */
    getIsDestroyed(): boolean {
        return this.isDestroyed;
    }
}

export { loopsToContactMatrix, computePSCurve, fitPSPowerLaw } from './contactMatrix';
