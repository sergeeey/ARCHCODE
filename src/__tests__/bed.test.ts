/**
 * BED parser tests
 */

import { describe, it, expect } from 'vitest';
import {
    loadCTCFFromBED,
    generateSampleBED,
    sitesToBED,
} from '../parsers/bed';

describe('BED Parser', () => {
    describe('loadCTCFFromBED', () => {
        it('should parse valid BED lines', () => {
            const bedContent = [
                '# Comment line',
                'chr11\t500\t1000\tCTCF_1\t900\t+',
                'chr11\t2000\t2500\tCTCF_2\t800\t-',
            ].join('\n');

            const result = loadCTCFFromBED(bedContent);

            expect(result.parsed).toBe(2);
            expect(result.sites[0].chrom).toBe('chr11');
            expect(result.sites[0].position).toBe(750); // midpoint of 500-1000
            expect(result.sites[0].orientation).toBe('F');
            expect(result.sites[1].orientation).toBe('R');
        });

        it('should skip invalid lines', () => {
            const bedContent = [
                '',
                '# Comment',
                'chr11\t500\t1000\tname\t900\t+',
                'invalid line',
                'chr11\t2000\t2500\tname\t800\t-',
                'chr11\t3000\t3500\tname', // Missing columns
            ].join('\n');

            const result = loadCTCFFromBED(bedContent);

            expect(result.parsed).toBe(2);
            expect(result.skipped).toBe(4); // empty, comment, invalid, missing columns
        });

        it('should filter by chromosome', () => {
            const bedContent = [
                'chr11\t500\t1000\tname\t900\t+',
                'chr12\t500\t1000\tname\t800\t-',
                'chr11\t2000\t2500\tname\t700\t+',
            ].join('\n');

            const result = loadCTCFFromBED(bedContent, { chromFilter: 'chr11' });

            expect(result.parsed).toBe(2);
            expect(result.sites.every(s => s.chrom === 'chr11')).toBe(true);
        });

        it('should filter by score', () => {
            const bedContent = [
                'chr11\t500\t1000\tname\t100\t+',  // Low score
                'chr11\t2000\t2500\tname\t900\t-', // High score
            ].join('\n');

            const result = loadCTCFFromBED(bedContent, { minScore: 500 });

            expect(result.parsed).toBe(1);
            expect(result.sites[0].position).toBe(2250); // From second line
        });

        it('should sort by position', () => {
            const bedContent = [
                'chr11\t5000\t5500\tname\t900\t+',
                'chr11\t1000\t1500\tname\t800\t-',
                'chr11\t3000\t3500\tname\t700\t+',
            ].join('\n');

            const result = loadCTCFFromBED(bedContent);

            expect(result.sites[0].position).toBe(1250);
            expect(result.sites[1].position).toBe(3250);
            expect(result.sites[2].position).toBe(5250);
        });

        it('should skip undefined strand', () => {
            const bedContent = [
                'chr11\t500\t1000\tname\t900\t+',
                'chr11\t2000\t2500\tname\t800\t.',
                'chr11\t3000\t3500\tname\t700\t-',
            ].join('\n');

            const result = loadCTCFFromBED(bedContent);

            expect(result.parsed).toBe(2);
        });
    });

    describe('generateSampleBED', () => {
        it('should generate valid BED format', () => {
            const bed = generateSampleBED('chr11', 6);
            const lines = bed.split('\n');

            expect(lines[0]).toContain('#');
            // NOTE: generateSampleBED currently hardcodes 6 sites (3 convergent pairs)
            expect(lines.length).toBe(11); // 5 header lines + 6 sites (3 pairs)

            const result = loadCTCFFromBED(bed);
            expect(result.parsed).toBe(6);
        });

        it('should alternate strand orientation', () => {
            const bed = generateSampleBED('chr11', 4);
            const result = loadCTCFFromBED(bed);

            expect(result.sites[0].orientation).toBe('F');
            expect(result.sites[1].orientation).toBe('R');
            expect(result.sites[2].orientation).toBe('F');
            expect(result.sites[3].orientation).toBe('R');
        });
    });

    describe('sitesToBED', () => {
        it('should convert sites back to BED', () => {
            // Use hardcoded 6 sites from generateSampleBED
            const bedIn = generateSampleBED('chr11', 6);
            const result = loadCTCFFromBED(bedIn);
            const bedOut = sitesToBED(result.sites);
            
            // Should be able to parse it back
            const reparsed = loadCTCFFromBED(bedOut);
            // Both should have the same number of sites (6)
            expect(reparsed.parsed).toBe(result.parsed);
            expect(reparsed.parsed).toBe(6);
        });
    });
});
