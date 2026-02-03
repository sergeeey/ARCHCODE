/**
 * ARCHCODE Unified Genome Store
 * Single source of truth for simulation state
 * Replaces: src/store.ts + src/simulation/store.ts
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import {
    SimulationState,
    SimulationConfig,
    GenomeElement,
    CohesinLoop,
    TAD,
} from '../domain/models/genome';
import {
    stepPhysics,
    respawnLoops,
    createLoop,
} from '../domain/models/physics';
import {
    SIMULATION_CONFIG,
    COHESIN_PARAMS,
    CTCF_PARAMS,
    VISUALIZATION_CONFIG,
    VALIDATION_SCENARIOS,
} from '../domain/constants/biophysics';
import { setGlobalSeed, random } from '../utils/random';

const DEFAULT_PHYSICS_SEED = 42;
// Initialize global RNG so physics.ts uses SeededRandom (reproducible)
setGlobalSeed(DEFAULT_PHYSICS_SEED);

// Default configuration based on biophysical constants
const createDefaultConfig = (): SimulationConfig => ({
    genomeLength: VISUALIZATION_CONFIG.DEFAULT_GENOME_LENGTH_BP,
    timeStepMs: SIMULATION_CONFIG.TIME_STEP_MS,
    biologicalTimeScale: SIMULATION_CONFIG.BIOLOGICAL_TIME_SCALE,
    extrusionSpeed: COHESIN_PARAMS.EXTRUSION_SPEED_BP_PER_S,
    meanProcessivity: COHESIN_PARAMS.MEAN_PROCESSIVITY_S,
    bookmarkingEfficiency: COHESIN_PARAMS.BOOKMARKING_EFFICIENCY,
    convergentEfficiency: CTCF_PARAMS.CONVERGENT_BLOCKING_EFFICIENCY,
    nonConvergentEfficiency: CTCF_PARAMS.NON_CONVERGENT_BLOCKING_EFFICIENCY,
    visualScale: VISUALIZATION_CONFIG.SCALE_BP_TO_VISUAL,
    viewCenter: VISUALIZATION_CONFIG.DEFAULT_VIEW_CENTER_BP,
});

// Initial state
const createInitialState = (): Omit<SimulationState, 'config'> => ({
    elements: new Map(),
    loops: [],
    tads: [],
    timeStep: 0,
    biologicalTime: 0,
    isRunning: false,
});

// Store interface with actions
interface GenomeStore extends SimulationState {
    // Configuration
    setConfig: (config: Partial<SimulationConfig>) => void;
    
    // Element management
    addElement: (element: GenomeElement) => void;
    removeElement: (id: string) => void;
    loadScenario: (scenarioKey: keyof typeof VALIDATION_SCENARIOS) => void;
    clearElements: () => void;
    
    // Loop management
    addLoop: (atPosition?: number) => void;
    removeLoop: (id: string) => void;
    clearLoops: () => void;
    
    // TAD management
    addTAD: (tad: TAD) => void;
    removeTAD: (id: string) => void;
    
    // Simulation control
    toggleSimulation: () => void;
    startSimulation: () => void;
    pauseSimulation: () => void;
    resetSimulation: () => void;
    stepSimulation: () => void;
    
    // State reset
    resetAll: () => void;
}

export const useGenomeStore = create<GenomeStore>()(
    devtools(
        (set, get) => ({
            ...createInitialState(),
            config: createDefaultConfig(),
            
            // Configuration
            setConfig: (configUpdate) => set((state) => ({
                config: { ...state.config, ...configUpdate },
            })),
            
            // Element management
            addElement: (element) => set((state) => {
                const newElements = new Map(state.elements);
                newElements.set(element.id, element);
                return { elements: newElements };
            }),
            
            removeElement: (id) => set((state) => {
                const newElements = new Map(state.elements);
                newElements.delete(id);
                return { elements: newElements };
            }),
            
            loadScenario: (scenarioKey) => {
                const scenario = VALIDATION_SCENARIOS[scenarioKey];
                const newElements = new Map<string, GenomeElement>();
                
                scenario.elements.forEach((el, index) => {
                    newElements.set(`el-${index}`, {
                        id: `el-${index}`,
                        position: el.position,
                        type: el.type,
                    });
                });
                
                set({
                    elements: newElements,
                    loops: [],
                    tads: [],
                    config: {
                        ...get().config,
                        genomeLength: scenario.length,
                        viewCenter: scenario.length / 2,
                    },
                });
            },
            
            clearElements: () => set({ elements: new Map() }),
            
            // Loop management
            addLoop: (atPosition) => set((state) => {
                const position = atPosition ?? Math.floor(random() * state.config.genomeLength);
                const newLoop = createLoop(state.config.genomeLength, state.loops);
                newLoop.startPosition = position;
                newLoop.leftAnchor = position;
                newLoop.rightAnchor = position + 1;
                
                return { loops: [...state.loops, newLoop] };
            }),
            
            removeLoop: (id) => set((state) => ({
                loops: state.loops.filter(l => l.id !== id),
            })),
            
            clearLoops: () => set({ loops: [] }),
            
            // TAD management
            addTAD: (tad) => set((state) => ({
                tads: [...state.tads, tad],
            })),
            
            removeTAD: (id) => set((state) => ({
                tads: state.tads.filter(t => t.id !== id),
            })),
            
            // Simulation control
            toggleSimulation: () => set((state) => ({ 
                isRunning: !state.isRunning 
            })),
            
            startSimulation: () => set({ isRunning: true }),
            pauseSimulation: () => set({ isRunning: false }),
            
            resetSimulation: () => {
                setGlobalSeed(DEFAULT_PHYSICS_SEED);
                set((state) => ({
                    loops: [],
                    tads: [],
                    timeStep: 0,
                    biologicalTime: 0,
                    isRunning: false,
                }));
            },
            
            stepSimulation: () => set((state) => {
                if (!state.isRunning) return {};
                
                // Run physics step
                const { updatedLoops, bookmarkingSites } = stepPhysics(
                    state.loops,
                    state.elements,
                    state.config.genomeLength
                );
                
                // Respawn loops at bookmarking sites
                const newLoops = respawnLoops(
                    bookmarkingSites,
                    updatedLoops,
                    state.config.genomeLength
                );
                
                return {
                    loops: [...updatedLoops, ...newLoops],
                    timeStep: state.timeStep + 1,
                    biologicalTime: state.biologicalTime + state.config.biologicalTimeScale,
                };
            }),
            
            // Full reset
            resetAll: () => {
                setGlobalSeed(DEFAULT_PHYSICS_SEED);
                set({
                    ...createInitialState(),
                    config: createDefaultConfig(),
                });
            },
        }),
        { name: 'GenomeStore' }
    )
);

// Selectors for performance
export const selectElements = (state: GenomeStore) => state.elements;
export const selectLoops = (state: GenomeStore) => state.loops;
export const selectIsRunning = (state: GenomeStore) => state.isRunning;
export const selectTimeStep = (state: GenomeStore) => state.timeStep;
export const selectBiologicalTime = (state: GenomeStore) => state.biologicalTime;
export const selectConfig = (state: GenomeStore) => state.config;
