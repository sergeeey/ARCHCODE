import { describe, it, expect } from 'vitest';
import { AlphaGenomeClient } from '../validation/alphagenome';

describe('AlphaGenome metrics', () => {
    it('should enforce score directionality (anti-inversion)', () => {
        const client = new AlphaGenomeClient({ apiKey: 'mock' });
        const base = [
            [1, 0],
            [0, 1],
        ];
        const same = [
            [1, 0],
            [0, 1],
        ];
        const inverted = [
            [0, 1],
            [1, 0],
        ];

        // Access private method for deterministic metric testing.
        const pearsonSame = (client as unknown as { calculatePearson: (a: number[][], b: number[][]) => number }).calculatePearson(base, same);
        const pearsonInverted = (client as unknown as { calculatePearson: (a: number[][], b: number[][]) => number }).calculatePearson(base, inverted);

        expect(pearsonSame).toBeGreaterThan(0.9);
        expect(pearsonInverted).toBeLessThan(-0.9);
    });
});
