/**
 * Super-Enhancer Identification from BigWig files.
 *
 * Implements the ROSE algorithm concept:
 * 1. Identify peaks (regions with signal above threshold)
 * 2. Stitch nearby peaks within 12.5kb
 * 3. Rank by total signal
 * 4. Find inflection point (hockey stick) to separate SE from typical enhancers
 *
 * Input: H3K27ac BigWig (primary) + MED1 BigWig (optional validation)
 * Output: BED file with Super-Enhancer coordinates
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// Configuration
// ============================================================================

const DEFAULT_H3K27AC = 'D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/histone/H3K27ac_GM12878.bw';
const DEFAULT_MED1 = 'D:/ПАРСИНГ НАУЧНЫХ НОВОСТЕЙ/data/inputs/med1/MED1_GM12878_Rep1.bw';
const OUTPUT_DIR = path.join(__dirname, '..', 'results');

const RESOLUTION = 1000;  // 1kb bins
const STITCH_DISTANCE = 12500;  // 12.5kb in bp
const PEAK_THRESHOLD_PERCENTILE = 75;  // Lower threshold
const MIN_ENHANCER_SIZE = 2000;  // 2kb minimum

// Main chromosomes to process
const MAIN_CHROMS = [
    'chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8',
    'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15',
    'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX'
];

// ============================================================================
// Types
// ============================================================================

interface Peak {
    chrom: string;
    start: number;
    end: number;
    signal: number;
}

interface Enhancer extends Peak {
    type: 'SE' | 'TE';
    rank?: number;
}

// ============================================================================
// BigWig Processing
// ============================================================================

async function processChromosome(bwPath: string, chrom: string, chromSize: number): Promise<Peak[]> {
    const { BigWig } = await import('@gmod/bbi');
    const bw = new BigWig({ path: bwPath });
    await bw.getHeader();

    const peaks: Peak[] = [];
    const GAP_TOLERANCE = 500;  // Allow gaps up to 500bp between high-signal features

    // Process in chunks to handle large chromosomes
    const chunkSize = 10_000_000;  // 10Mb chunks

    for (let chunkStart = 0; chunkStart < chromSize; chunkStart += chunkSize) {
        const chunkEnd = Math.min(chunkStart + chunkSize, chromSize);

        try {
            const features = await bw.getFeatures(chrom, chunkStart, chunkEnd, { scale: 1 });

            if (features.length === 0) continue;

            // Calculate threshold for this chunk (use 90th percentile for stricter peaks)
            const scores = features.map((f: any) => f.score || 0).filter((s: number) => s > 0);
            if (scores.length === 0) continue;

            scores.sort((a: number, b: number) => a - b);
            const thresholdIdx = Math.floor(scores.length * PEAK_THRESHOLD_PERCENTILE / 100);
            const threshold = scores[thresholdIdx] || 0;

            // Collect high-signal features
            const highSignalFeatures: Array<{ start: number; end: number; score: number }> = [];
            for (const feat of features as any[]) {
                if (feat.score > threshold) {
                    highSignalFeatures.push({
                        start: feat.start,
                        end: feat.end,
                        score: feat.score
                    });
                }
            }

            if (highSignalFeatures.length === 0) continue;

            // Sort by start position
            highSignalFeatures.sort((a, b) => a.start - b.start);

            // Merge nearby high-signal features into peaks (allow gaps up to GAP_TOLERANCE)
            let peakStart = highSignalFeatures[0].start;
            let peakEnd = highSignalFeatures[0].end;
            let peakSignal = highSignalFeatures[0].score * (highSignalFeatures[0].end - highSignalFeatures[0].start);

            for (let i = 1; i < highSignalFeatures.length; i++) {
                const feat = highSignalFeatures[i];

                if (feat.start - peakEnd <= GAP_TOLERANCE) {
                    // Extend peak
                    peakEnd = feat.end;
                    peakSignal += feat.score * (feat.end - feat.start);
                } else {
                    // Save current peak if large enough
                    if (peakEnd - peakStart >= MIN_ENHANCER_SIZE) {
                        peaks.push({
                            chrom,
                            start: peakStart,
                            end: peakEnd,
                            signal: peakSignal
                        });
                    }
                    // Start new peak
                    peakStart = feat.start;
                    peakEnd = feat.end;
                    peakSignal = feat.score * (feat.end - feat.start);
                }
            }

            // Don't forget last peak
            if (peakEnd - peakStart >= MIN_ENHANCER_SIZE) {
                peaks.push({
                    chrom,
                    start: peakStart,
                    end: peakEnd,
                    signal: peakSignal
                });
            }
        } catch (e) {
            // Skip this chunk on error
        }
    }

    return peaks;
}

function stitchPeaks(peaks: Peak[]): Peak[] {
    if (peaks.length === 0) return [];

    // Sort by chromosome and start position
    const sorted = [...peaks].sort((a, b) => {
        if (a.chrom !== b.chrom) return a.chrom.localeCompare(b.chrom);
        return a.start - b.start;
    });

    const stitched: Peak[] = [];
    let current = { ...sorted[0] };

    for (let i = 1; i < sorted.length; i++) {
        const peak = sorted[i];

        if (peak.chrom === current.chrom && peak.start - current.end <= STITCH_DISTANCE) {
            // Stitch together
            current.end = peak.end;
            current.signal += peak.signal;
        } else {
            // Save current and start new
            stitched.push(current);
            current = { ...peak };
        }
    }

    // Don't forget the last one
    stitched.push(current);

    return stitched;
}

function findInflectionPoint(signals: number[]): number {
    if (signals.length < 3) return signals[0] || 0;

    // Sort descending
    const sorted = [...signals].sort((a, b) => b - a);
    const maxSignal = sorted[0];
    if (maxSignal === 0) return 0;

    // Hockey stick method: find point with max distance from diagonal
    let maxDistance = 0;
    let inflectionIdx = 0;

    for (let i = 0; i < sorted.length; i++) {
        const x = i / sorted.length;
        const y = sorted[i] / maxSignal;
        const diagonal = 1 - x;
        const distance = Math.abs(y - diagonal);

        if (distance > maxDistance) {
            maxDistance = distance;
            inflectionIdx = i;
        }
    }

    return sorted[inflectionIdx];
}

// ============================================================================
// Main
// ============================================================================

async function main() {
    console.log('');
    console.log('█'.repeat(70));
    console.log('  SUPER-ENHANCER IDENTIFICATION (ROSE-like algorithm)');
    console.log('█'.repeat(70));
    console.log('');

    const h3k27acPath = DEFAULT_H3K27AC;
    const med1Path = DEFAULT_MED1;
    const outputBed = path.join(OUTPUT_DIR, 'super_enhancers_GM12878.bed');

    console.log(`H3K27ac: ${h3k27acPath}`);
    console.log(`MED1:    ${med1Path}`);
    console.log(`Output:  ${outputBed}`);
    console.log('');

    // Check files exist
    if (!fs.existsSync(h3k27acPath)) {
        console.error(`ERROR: H3K27ac file not found: ${h3k27acPath}`);
        process.exit(1);
    }

    // Get chromosome sizes
    const { BigWig } = await import('@gmod/bbi');
    const bw = new BigWig({ path: h3k27acPath });
    const header = await bw.getHeader();
    const chromSizes = new Map<string, number>();

    // refsByNumber contains {name, id, length} for each chromosome
    for (const [, info] of Object.entries(header.refsByNumber as Record<string, { name: string; id: number; length: number }>)) {
        chromSizes.set(info.name, info.length);
    }

    console.log(`Found ${chromSizes.size} chromosomes`);
    console.log('');

    // Process each chromosome
    const allPeaks: Peak[] = [];

    for (const chrom of MAIN_CHROMS) {
        const size = chromSizes.get(chrom);
        if (!size) {
            console.log(`${chrom}: not found in BigWig`);
            continue;
        }

        process.stdout.write(`${chrom}...`);
        const peaks = await processChromosome(h3k27acPath, chrom, size);
        allPeaks.push(...peaks);
        console.log(` ${peaks.length} peaks`);
    }

    console.log('');
    console.log(`Total peaks before stitching: ${allPeaks.length}`);

    // Stitch peaks
    const stitched = stitchPeaks(allPeaks);
    console.log(`After stitching (${STITCH_DISTANCE / 1000}kb): ${stitched.length} regions`);

    if (stitched.length === 0) {
        console.log('WARNING: No enhancers found!');
        process.exit(1);
    }

    // Find inflection point
    const signals = stitched.map(p => p.signal);
    const inflectionSignal = findInflectionPoint(signals);
    console.log(`Inflection point signal: ${inflectionSignal.toFixed(2)}`);

    // Classify
    const enhancers: Enhancer[] = stitched.map(p => ({
        ...p,
        type: p.signal >= inflectionSignal ? 'SE' as const : 'TE' as const
    }));

    // Sort by signal
    enhancers.sort((a, b) => b.signal - a.signal);

    // Add ranks
    enhancers.forEach((e, i) => e.rank = i + 1);

    const superEnhancers = enhancers.filter(e => e.type === 'SE');
    const typicalEnhancers = enhancers.filter(e => e.type === 'TE');

    console.log('');
    console.log(`Super-Enhancers (SE): ${superEnhancers.length}`);
    console.log(`Typical Enhancers (TE): ${typicalEnhancers.length}`);

    // Write BED file for Super-Enhancers
    const bedLines: string[] = [
        '#chrom\tstart\tend\tname\tscore\tstrand\tsignal\trank'
    ];

    for (const se of superEnhancers) {
        const name = `SE_${se.rank}_${se.chrom}`;
        const score = Math.min(1000, Math.round(se.signal / 100));
        bedLines.push(`${se.chrom}\t${se.start}\t${se.end}\t${name}\t${score}\t.\t${se.signal.toFixed(2)}\t${se.rank}`);
    }

    fs.writeFileSync(outputBed, bedLines.join('\n'), 'utf-8');
    console.log(`\nSuper-Enhancers written to: ${outputBed}`);

    // Write all enhancers
    const allBed = outputBed.replace('.bed', '_all.bed');
    const allLines: string[] = [
        '#chrom\tstart\tend\tname\tscore\tstrand\tsignal\ttype\trank'
    ];

    for (const e of enhancers) {
        const name = `${e.type}_${e.rank}_${e.chrom}`;
        const score = Math.min(1000, Math.round(e.signal / 100));
        allLines.push(`${e.chrom}\t${e.start}\t${e.end}\t${name}\t${score}\t.\t${e.signal.toFixed(2)}\t${e.type}\t${e.rank}`);
    }

    fs.writeFileSync(allBed, allLines.join('\n'), 'utf-8');
    console.log(`All enhancers written to: ${allBed}`);

    // Print top 20
    console.log('');
    console.log('═'.repeat(75));
    console.log('TOP 20 SUPER-ENHANCERS');
    console.log('═'.repeat(75));
    console.log(`${'Rank'.padEnd(6)}${'Chrom'.padEnd(8)}${'Start'.padEnd(12)}${'End'.padEnd(12)}${'Length'.padEnd(10)}${'Signal'.padEnd(14)}`);
    console.log('-'.repeat(75));

    for (const se of superEnhancers.slice(0, 20)) {
        const length = se.end - se.start;
        console.log(
            `${(se.rank || 0).toString().padEnd(6)}` +
            `${se.chrom.padEnd(8)}` +
            `${se.start.toLocaleString().padEnd(12)}` +
            `${se.end.toLocaleString().padEnd(12)}` +
            `${(length / 1000).toFixed(1).padStart(6)}kb   ` +
            `${se.signal.toFixed(1).padEnd(14)}`
        );
    }

    // Validate top SE with MED1
    if (fs.existsSync(med1Path)) {
        console.log('');
        console.log('═'.repeat(75));
        console.log('MED1 SIGNAL VALIDATION (Top 10 SE)');
        console.log('═'.repeat(75));

        const med1Bw = new BigWig({ path: med1Path });
        await med1Bw.getHeader();

        for (const se of superEnhancers.slice(0, 10)) {
            try {
                const feats = await med1Bw.getFeatures(se.chrom, se.start, se.end, { scale: 1 });
                let sum = 0;
                for (const f of feats as any[]) {
                    sum += (f.score || 0) * (f.end - f.start);
                }
                console.log(`SE_${se.rank} (${se.chrom}:${se.start.toLocaleString()}-${se.end.toLocaleString()}): MED1 = ${sum.toFixed(2)}`);
            } catch {
                console.log(`SE_${se.rank}: MED1 unavailable`);
            }
        }
    }

    console.log('');
    console.log('═'.repeat(75));
    console.log(`COMPLETE: ${superEnhancers.length} Super-Enhancers identified`);
    console.log('═'.repeat(75));
}

main().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
