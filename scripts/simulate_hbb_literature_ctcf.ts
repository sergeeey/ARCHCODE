/**
 * ARCHCODE Simulation with Literature-Based CTCF Sites
 *
 * Uses curated CTCF positions from:
 * - ENCODE ChIP-seq (K562, GM12878)
 * - Bender et al. 2012 (beta-globin CTCF)
 * - Hi-C loop anchors
 *
 * Region: chr11:5,200,000-5,250,000
 * Resolution: 5 KB bins (10x10 matrix)
 *
 * Run: npx tsx scripts/simulate_hbb_literature_ctcf.ts
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createCTCFSite } from '../src/domain/models/genome';
import { MultiCohesinEngine } from '../src/engines/MultiCohesinEngine';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load literature-based CTCF sites
const ctcfDataPath = path.join(__dirname, '..', 'data', 'hbb_ctcf_sites_literature.json');
const ctcfData = JSON.parse(fs.readFileSync(ctcfDataPath, 'utf8'));

console.log('═══════════════════════════════════════════');
console.log('  ARCHCODE Simulation v2');
console.log('  Literature-Based CTCF Sites');
console.log('═══════════════════════════════════════════\n');

console.log('📚 CTCF Source: Literature curation');
console.log(`   Sites loaded: ${ctcfData.ctcf_sites.length}`);
console.log(`   References:`);
for (const ref of ctcfData.metadata.references) {
    console.log(`     - ${ref}`);
}
console.log();

console.log(`📍 Locus: ${ctcfData.locus.chromosome}:${ctcfData.locus.start}-${ctcfData.locus.end}`);
console.log(`📏 Length: ${ctcfData.locus.length / 1000} KB`);
console.log(`📏 Resolution: 5 KB bins\n`);

// Convert to ARCHCODE format
const sites = ctcfData.ctcf_sites.map((site: any) =>
    createCTCFSite(
        ctcfData.locus.chromosome,
        site.position_relative,
        site.orientation as 'F' | 'R',
        site.strength
    )
);

console.log('🧬 CTCF Sites:');
for (let i = 0; i < sites.length; i++) {
    const site = ctcfData.ctcf_sites[i];
    console.log(`   ${i + 1}. ${site.position_relative} bp (${site.orientation}) - ${site.source}`);
}
console.log();

// Configure simulation
const config = {
    genomeLength: ctcfData.locus.length,
    ctcfSites: sites,
    numCohesins: 20,
    velocity: 1000,
    processivity: 600000,
    unloadingProbability: 0.0005,
    seed: 42,
    maxSteps: 10000,
};

console.log('⚙️  Simulation parameters:');
console.log(`   Cohesins: ${config.numCohesins}`);
console.log(`   Velocity: ${config.velocity} bp/step`);
console.log(`   Seed: ${config.seed} (reproducible)`);
console.log(`   Max steps: ${config.maxSteps}\n`);

console.log('🔄 Running simulation...\n');

const startTime = Date.now();
const engine = new MultiCohesinEngine(config);
const loops = engine.run(config.maxSteps);
const elapsedTime = Date.now() - startTime;

console.log(`✅ Simulation complete (${elapsedTime}ms)\n`);

console.log('📊 Results:');
console.log(`   Loops formed: ${loops.length}`);

// List loops
if (loops.length > 0) {
    console.log(`\n   Loop details:`);
    const uniqueLoops = new Map<string, number>();
    for (const loop of loops) {
        const key = `${loop.leftAnchor}-${loop.rightAnchor}`;
        uniqueLoops.set(key, (uniqueLoops.get(key) || 0) + loop.strength);
    }

    Array.from(uniqueLoops.entries())
        .sort((a, b) => b[1] - a[1])
        .forEach(([key, strength], i) => {
            console.log(`     ${i + 1}. ${key} bp (strength: ${strength.toFixed(2)})`);
        });
}
console.log();

// Generate contact matrix
const binSize = 5000;
const numBins = Math.floor(config.genomeLength / binSize);
const matrix: number[][] = Array(numBins).fill(0).map(() => Array(numBins).fill(0));

// Fill from loops
for (const loop of loops) {
    const bin1 = Math.floor(loop.leftAnchor / binSize);
    const bin2 = Math.floor(loop.rightAnchor / binSize);

    if (bin1 >= 0 && bin1 < numBins && bin2 >= 0 && bin2 < numBins) {
        matrix[bin1][bin2] += loop.strength;
        matrix[bin2][bin1] += loop.strength;
    }
}

// Add diagonal
for (let i = 0; i < numBins; i++) {
    matrix[i][i] += 1.0;
}

// Statistics
const flatMatrix = matrix.flat();
const nonZero = flatMatrix.filter(v => v > 0).length;
const min = Math.min(...flatMatrix.filter(v => v > 0));
const max = Math.max(...flatMatrix);
const sum = flatMatrix.reduce((a, b) => a + b, 0);
const mean = sum / nonZero;

console.log(`📊 Contact Matrix:`);
console.log(`   Shape: ${numBins}x${numBins}`);
console.log(`   Non-zero elements: ${nonZero} / ${flatMatrix.length}`);
console.log(`   Min (non-zero): ${min.toFixed(4)}`);
console.log(`   Max: ${max.toFixed(4)}`);
console.log(`   Mean (non-zero): ${mean.toFixed(4)}`);
console.log(`   Total sum: ${sum.toFixed(2)}\n`);

// Save
const outputDir = path.join(__dirname, '..', 'data');
const outputPath = path.join(outputDir, 'archcode_hbb_literature_ctcf_matrix.json');

const output = {
    version: 'v2_literature_ctcf',
    locus: `${ctcfData.locus.chromosome}:${ctcfData.locus.start}-${ctcfData.locus.end}`,
    resolution: binSize,
    matrix: matrix,
    loops: loops.length,
    ctcf_source: 'literature',
    metadata: {
        cohesins: config.numCohesins,
        velocity: config.velocity,
        seed: config.seed,
        ctcf_sites: ctcfData.ctcf_sites.length,
        simulation_time_ms: elapsedTime,
        references: ctcfData.metadata.references,
    }
};

fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
console.log(`💾 Saved to: ${outputPath}\n`);

console.log('✅ Ready for comparison with experimental Hi-C');
console.log('   Run correlation analysis next\n');
