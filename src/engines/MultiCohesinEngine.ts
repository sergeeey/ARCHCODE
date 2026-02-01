/**
 * Multi-Cohesin Loop Extrusion Engine
 * Multiple cohesins for ensemble simulation (better AlphaGenome correlation)
 */

import { 
    CTCFSite, 
    Loop, 
    CohesinComplex, 
    createCohesinComplex, 
    createLoop,
    ContactMatrix 
} from '../domain/models/genome';
import { loopsToContactMatrix } from './LoopExtrusionEngine';
import { SeededRandom } from '../utils/random';
import { COHESIN_PARAMS, CTCF_PARAMS } from '../domain/constants/biophysics';

export interface MultiCohesinConfig {
    genomeLength: number;
    ctcfSites: CTCFSite[];
    numCohesins?: number;      // Количество cohesin (default: 10)
    spacing?: number;          // Расстояние между ними (default: 10000)
    velocity?: number;
    seed?: number;
    maxSteps?: number;         // Max steps before auto-stop (default: 10000)
}

export class MultiCohesinEngine {
    readonly genomeLength: number;
    readonly ctcfSites: CTCFSite[];
    readonly velocity: number;
    readonly numCohesins: number;
    readonly maxSteps: number;
    readonly seed: number;
    readonly maxCohesins: number;  // Limit to prevent memory leaks
    
    private cohesins: CohesinComplex[];
    private loops: Loop[];
    private stepCount: number;
    private targetMaxSteps: number;
    private rng: SeededRandom;
    private isDestroyed: boolean = false;

    constructor(config: MultiCohesinConfig) {
        this.genomeLength = config.genomeLength;
        this.ctcfSites = [...config.ctcfSites].sort((a, b) => a.position - b.position);
        this.velocity = config.velocity ?? 1000;
        this.numCohesins = config.numCohesins ?? 10;
        this.targetMaxSteps = config.maxSteps ?? 10000;
        this.maxSteps = this.targetMaxSteps;
        this.seed = config.seed ?? 42;
        this.maxCohesins = config.numCohesins ? config.numCohesins * 5 : 50; // 5x initial pool max
        
        this.rng = new SeededRandom(this.seed);
        
        const spacing = config.spacing ?? Math.floor(config.genomeLength / (this.numCohesins + 2));
        
        // Создаем несколько cohesin равномерно по геному
        this.cohesins = [];
        for (let i = 0; i < this.numCohesins; i++) {
            const pos = spacing * (i + 1);
            if (pos < this.genomeLength) {
                this.cohesins.push(createCohesinComplex(pos, this.velocity));
            }
        }
        
        this.loops = [];
        this.stepCount = 0;

        console.log(`[MultiEngine] Created ${this.cohesins.length} cohesins across ${this.genomeLength}bp`);
        console.log(`[MultiEngine] Positions:`, this.cohesins.map(c => `${c.leftLeg}-${c.rightLeg}`).join(', '));
    }

    step(): boolean {
        if (this.isDestroyed) {
            console.warn('[MultiEngine] Cannot step: engine is destroyed');
            return false;
        }
        
        // Safety: hard limit to prevent infinite loops
        if (this.stepCount >= this.maxSteps) {
            console.warn(`[MultiEngine] Max steps (${this.maxSteps}) reached, stopping`);
            return false;
        }
        
        this.stepCount++;
        
        let anyActive = false;
        const unloadedPositions: number[] = [];
        
        for (const cohesin of this.cohesins) {
            if (!cohesin.active) continue;
            anyActive = true;
            
            // Check spontaneous unloading (processivity limit)
            if (this.shouldUnload()) {
                cohesin.active = false;
                unloadedPositions.push(cohesin.leftLeg);
                continue;
            }
            
            // Двигаем cohesin
            cohesin.leftLeg -= Math.floor(this.velocity);
            cohesin.rightLeg += Math.floor(this.velocity);
            
            // Проверяем CTCF барьеры
            this.checkBarriers(cohesin);
            
            // Проверяем границы генома (with margin to prevent overflow)
            if (cohesin.leftLeg < -this.velocity || cohesin.rightLeg > this.genomeLength + this.velocity) {
                cohesin.active = false;
            }
        }
        
        // Respawn at bookmarking sites or add new cohesin to maintain pool
        this.handleRespawn(unloadedPositions);
        
        // Cleanup: remove old inactive cohesins to prevent memory leak
        // Keep last 100 inactive cohesins for analysis
        if (this.cohesins.length > this.maxCohesins) {
            const inactiveCount = this.cohesins.filter(c => !c.active).length;
            if (inactiveCount > 100) {
                const toRemove = inactiveCount - 100;
                let removed = 0;
                this.cohesins = this.cohesins.filter(c => {
                    if (!c.active && removed < toRemove) {
                        removed++;
                        return false;
                    }
                    return true;
                });
            }
        }
        
        return anyActive && this.stepCount < this.maxSteps;
    }
    
    /**
     * Check if cohesin should unload based on processivity (stochastic)
     */
    private shouldUnload(): boolean {
        return this.rng.random() < COHESIN_PARAMS.UNLOADING_PROBABILITY;
    }
    
    /**
     * Handle cohesin respawning at bookmarking sites or uniform loading
     */
    private handleRespawn(unloadedPositions: number[]): void {
        // Count active cohesins
        const activeCount = this.cohesins.filter(c => c.active).length;
        const targetCount = this.numCohesins;
        
        if (activeCount >= targetCount) return;
        
        const needed = targetCount - activeCount;
        let spawned = 0;
        
        // Try bookmarking first (respawn at unloaded positions)
        for (const pos of unloadedPositions) {
            if (spawned >= needed) break;
            if (this.rng.random() < COHESIN_PARAMS.BOOKMARKING_EFFICIENCY) {
                this.cohesins.push(createCohesinComplex(pos, this.velocity));
                spawned++;
            }
        }
        
        // Fill remaining with new random positions
        while (spawned < needed) {
            const newPos = this.rng.randomInt(
                Math.floor(this.genomeLength * 0.1),
                Math.floor(this.genomeLength * 0.9)
            );
            this.cohesins.push(createCohesinComplex(newPos, this.velocity));
            spawned++;
        }
        
        if (spawned > 0 && this.stepCount % 100 === 0) {
            console.log(`[Step ${this.stepCount}] Respawned ${spawned} cohesins`);
        }
    }

    private checkBarriers(cohesin: CohesinComplex): void {
        // Left leg: ищем R (< ) слева
        const leftBarriers = this.ctcfSites.filter(
            site => site.orientation === 'R' && site.position <= cohesin.leftLeg
        );
        const leftBarrier = leftBarriers.length > 0
            ? leftBarriers.reduce((max, s) => s.position > max.position ? s : max)
            : null;

        // Right leg: ищем F (> ) справа
        const rightBarriers = this.ctcfSites.filter(
            site => site.orientation === 'F' && site.position >= cohesin.rightLeg
        );
        const rightBarrier = rightBarriers.length > 0
            ? rightBarriers.reduce((min, s) => s.position < min.position ? s : min)
            : null;

        // Конвергентная пара? R...F формирует петлю
        if (leftBarrier && rightBarrier) {
            // Stochastic blocking: convergent efficiency determines if loop forms
            const blockingEfficiency = CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY;
            if (this.rng.random() < blockingEfficiency) {
                cohesin.active = false;
                cohesin.loopFormed = true;

                // Проверяем, нет ли уже такой петли
                const exists = this.loops.some(l => 
                    l.leftAnchor === leftBarrier.position && 
                    l.rightAnchor === rightBarrier.position
                );
                
                if (!exists) {
                    const loop = createLoop(
                        leftBarrier.position,
                        rightBarrier.position,
                        Math.min(leftBarrier.strength, rightBarrier.strength) * blockingEfficiency
                    );
                    this.loops.push(loop);
                    
                    if (this.loops.length <= 5 || this.stepCount % 100 === 0) {
                        console.log(`[Step ${this.stepCount}] Loop #${this.loops.length} (eff=${blockingEfficiency.toFixed(2)}):`,
                            `${leftBarrier.position}-${rightBarrier.position}`,
                            `(${(rightBarrier.position - leftBarrier.position)/1000}kb)`);
                    }
                }
            }
            // If blocking fails, cohesin continues (leaky barrier behavior)
        }
    }

    run(maxSteps: number = this.maxSteps): Loop[] {
        while (this.stepCount < maxSteps) {
            const shouldContinue = this.step();
            if (!shouldContinue) break;
        }
        return this.loops;
    }

    getLoops(): Loop[] {
        return [...this.loops];
    }

    getCohesins(): CohesinComplex[] {
        return this.cohesins.map(c => ({ ...c }));
    }

    getStepCount(): number {
        return this.stepCount;
    }

    getActiveCohesinCount(): number {
        return this.cohesins.filter(c => c.active).length;
    }

    getContactMatrix(resolution: number, backgroundLevel: number = 0.1): ContactMatrix {
        return loopsToContactMatrix(
            this.loops,
            0,
            this.genomeLength,
            resolution,
            backgroundLevel
        );
    }

    reset(): void {
        if (this.isDestroyed) return;
        
        // Reset RNG for reproducibility
        this.rng.reset(this.seed);
        
        const spacing = Math.floor(this.genomeLength / (this.numCohesins + 2));
        this.cohesins = [];
        for (let i = 0; i < this.numCohesins; i++) {
            const pos = spacing * (i + 1);
            if (pos < this.genomeLength) {
                this.cohesins.push(createCohesinComplex(pos, this.velocity));
            }
        }
        this.loops = [];
        this.stepCount = 0;
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
