/**
 * Contact matrix and P(s) curve utilities for ARCHCODE.
 * Converts loop lists to contact matrices and computes power-law fits.
 */

import type { Loop, ContactMatrix, PSCurve, PowerLawFit } from '../domain/models/genome';

/**
 * Convert loops to contact matrix (binned by resolution).
 */
export function loopsToContactMatrix(
    loops: Loop[],
    genomeStart: number,
    genomeEnd: number,
    resolution: number,
    backgroundLevel: number = 0.1
): ContactMatrix {
    if (genomeEnd <= genomeStart) {
        console.warn('[loopsToContactMatrix] Invalid genome range:', genomeStart, '-', genomeEnd);
        return [[1.0]];
    }

    if (resolution <= 0) {
        console.warn('[loopsToContactMatrix] Invalid resolution:', resolution);
        resolution = 1000;
    }

    const nBins = Math.max(1, Math.floor((genomeEnd - genomeStart) / resolution));

    if (nBins > 10000) {
        console.warn(`[loopsToContactMatrix] Matrix too large (${nBins}x${nBins}), capping at 10000`);
        return Array(10000).fill(null).map(() => Array(10000).fill(backgroundLevel));
    }

    const matrix: ContactMatrix = Array(nBins).fill(null).map(() =>
        Array(nBins).fill(backgroundLevel)
    );

    for (let i = 0; i < nBins; i++) {
        matrix[i][i] = 1.0;
    }

    for (let i = 0; i < nBins; i++) {
        for (let j = i + 1; j < nBins; j++) {
            const distance = j - i;
            const decayFactor = 1.0 / (distance + 1);
            const baseline = backgroundLevel * decayFactor;
            matrix[i][j] = baseline;
            matrix[j][i] = baseline;
        }
    }

    for (const loop of loops) {
        if (!isFinite(loop.leftAnchor) || !isFinite(loop.rightAnchor)) {
            console.warn('[loopsToContactMatrix] Invalid loop coordinates:', loop);
            continue;
        }

        const leftBin = Math.floor((loop.leftAnchor - genomeStart) / resolution);
        const rightBin = Math.floor((loop.rightAnchor - genomeStart) / resolution);

        if (leftBin >= 0 && leftBin < nBins && rightBin >= 0 && rightBin < nBins) {
            const enhancement = (loop.strength ?? 1.0) * 10.0;
            matrix[leftBin][rightBin] += enhancement;
            matrix[rightBin][leftBin] += enhancement;
        }
    }

    return matrix;
}

/**
 * Compute P(s) scaling curve from contact matrix.
 */
export function computePSCurve(
    matrix: ContactMatrix,
    maxDistance?: number
): PSCurve {
    if (!matrix || matrix.length === 0 || !matrix[0] || matrix[0].length === 0) {
        console.warn('[computePSCurve] Empty matrix provided');
        return { distances: [], contacts: [] };
    }

    const nBins = matrix.length;
    const maxDist = maxDistance ?? nBins - 1;

    if (maxDist <= 0) {
        console.warn('[computePSCurve] Invalid maxDistance:', maxDist);
        return { distances: [], contacts: [] };
    }

    const distanceContacts: Map<number, number[]> = new Map();

    for (let i = 0; i < nBins; i++) {
        if (!matrix[i] || matrix[i].length !== nBins) {
            console.warn(`[computePSCurve] Invalid row ${i}, skipping`);
            continue;
        }

        for (let j = i + 1; j < Math.min(i + maxDist + 1, nBins); j++) {
            const distance = j - i;
            const contact = matrix[i][j];

            if (!isFinite(contact)) continue;

            if (!distanceContacts.has(distance)) {
                distanceContacts.set(distance, []);
            }
            distanceContacts.get(distance)!.push(contact);
        }
    }

    if (distanceContacts.size === 0) {
        console.warn('[computePSCurve] No valid contacts found in matrix');
        return { distances: [], contacts: [] };
    }

    const distances = Array.from(distanceContacts.keys()).sort((a, b) => a - b);
    const contacts = distances.map(d => {
        const vals = distanceContacts.get(d)!;
        if (!vals || vals.length === 0) return 0;
        return vals.reduce((a, b) => a + b, 0) / vals.length;
    });

    return { distances, contacts };
}

/**
 * Fit power-law to P(s) curve: P(s) = A * s^α
 */
export function fitPSPowerLaw(
    distances: number[],
    contacts: number[]
): PowerLawFit {
    const validPairs: [number, number][] = [];
    for (let i = 0; i < distances.length; i++) {
        if (contacts[i] > 0 && distances[i] > 0) {
            validPairs.push([distances[i], contacts[i]]);
        }
    }

    if (validPairs.length < 2) {
        return { alpha: 0.0, r2: 0.0 };
    }

    const logDistances = validPairs.map(([d]) => Math.log(d));
    const logContacts = validPairs.map(([_, c]) => Math.log(c));

    const n = logDistances.length;
    const meanLogD = logDistances.reduce((a, b) => a + b, 0) / n;
    const meanLogC = logContacts.reduce((a, b) => a + b, 0) / n;

    let numerator = 0;
    let denominator = 0;
    for (let i = 0; i < n; i++) {
        const ld = logDistances[i];
        const lc = logContacts[i];
        numerator += (ld - meanLogD) * (lc - meanLogC);
        denominator += (ld - meanLogD) ** 2;
    }

    if (denominator === 0) {
        return { alpha: 0.0, r2: 0.0 };
    }

    const alpha = numerator / denominator;

    const predictions = logDistances.map(ld => meanLogC + alpha * (ld - meanLogD));
    const ssRes = predictions.reduce((sum, pred, i) =>
        sum + (logContacts[i] - pred) ** 2, 0
    );
    const ssTot = logContacts.reduce((sum, lc) => sum + (lc - meanLogC) ** 2, 0);

    const r2 = ssTot > 0 ? 1.0 - (ssRes / ssTot) : 0.0;

    return { alpha, r2 };
}
