/**
 * ARCHCODE Experiment Run — протокол запуска для воспроизводимости
 * schemaVersion: 1.0
 */

export type ArchcodeRunEventType =
    | 'loop_formed'
    | 'pair_converged'
    | 'cohesin_bind'
    | 'cohesin_release'
    | 'plateau'
    | 'user_stop'
    | 'error';

export interface ArchcodeRunEvent {
    /** Вспомогательное: ms с начала run (wall-clock). Для порядка/replay используй step. */
    t: number;
    /** Источник истины для порядка событий и воспроизведения; два запуска с одним seed — одинаковые события по step. */
    step: number;
    type: ArchcodeRunEventType;
    payload?: Record<string, unknown>;
}

export interface ArchcodeRunStablePair {
    left: number;
    right: number;
    type?: string;
    sizeBp?: number;
    note?: string;
}

export interface ArchcodeRun {
    schemaVersion: '1.0';
    app: { name: 'ARCHCODE'; version: string };
    run: {
        id: string;
        createdAt: string;
        endedAt?: string;
        durationMs?: number;
        seed?: number | string;
        mode: 'tube' | 'linear' | 'helix';
        status: 'running' | 'plateau' | 'stopped' | 'error';
        stopReason?: string;
    };
    params: {
        extrusionSpeed: number;
        matrixResolution: number;
        genomeLengthBp: number;
    };
    model: {
        ctcfSites: Array<{ pos: number; orient: 'F' | 'R'; chrom?: string }>;
        cohesinCount?: number;
        chromosome?: string;
    };
    results: {
        steps: number;
        cycles?: number;
        /** Число событий loop_formed (может расти при повторных попытках). */
        loopsFormed: number;
        /** Уникальные пары по ключу left-right (для отчёта). */
        uniqueLoopsFormed?: number;
        convergentPairs: number;
        stablePairs: ArchcodeRunStablePair[];
        lastState?: {
            activeCohesin: number;
        };
    };
    events: ArchcodeRunEvent[];
    notes?: string;
}

export function createRunId(): string {
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}
