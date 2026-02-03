/**
 * ARCHCODE - Run All Locus Validations
 *
 * Executes FountainLoader validation on all 4 loci:
 * - MYC (calibration locus)
 * - IGH (blind test)
 * - TCRα (blind test)
 * - SOX2 (blind test)
 *
 * Generates a comprehensive summary report.
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface ValidationResult {
    locus: string;
    chromosome: string;
    length_mb: number;
    beta0: { stepLoadProb: number; avgLoops: number; nonZeroCells: number };
    beta5: { stepLoadProb: number; avgLoops: number; nonZeroCells: number };
    loadingIncrease: number;
    diffCells: number;
    maxEnrichment: number;
    status: 'PASS' | 'FAIL' | 'PENDING';
    duration_sec: number;
}

const LOCI = [
    {
        name: 'MYC',
        script: 'run-fountain-ensemble.ts',
        beta0Out: 'ensemble_myc_beta0.json',
        beta5Out: 'ensemble_myc_beta5.json',
        chromosome: 'chr8',
        length_mb: 1.1
    },
    {
        name: 'IGH',
        script: 'run-fountain-igh.ts',
        beta0Out: 'ensemble_igh_beta0.json',
        beta5Out: 'ensemble_igh_beta5.json',
        chromosome: 'chr14',
        length_mb: 1.1
    },
    {
        name: 'TCRα',
        script: 'run-fountain-tcra.ts',
        beta0Out: 'ensemble_tcra_beta0.json',
        beta5Out: 'ensemble_tcra_beta5.json',
        chromosome: 'chr14',
        length_mb: 1.6
    },
    {
        name: 'SOX2',
        script: 'run-fountain-sox2.ts',
        beta0Out: 'ensemble_sox2_beta0.json',
        beta5Out: 'ensemble_sox2_beta5.json',
        chromosome: 'chr3',
        length_mb: 0.8
    }
];

function runScript(scriptName: string, args: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
        const proc = spawn('npx', ['tsx', path.join(__dirname, scriptName), ...args], {
            stdio: 'inherit',
            shell: true
        });
        proc.on('close', code => {
            if (code === 0) resolve();
            else reject(new Error(`Script ${scriptName} exited with code ${code}`));
        });
        proc.on('error', reject);
    });
}

function loadResult(filename: string): any | null {
    const filepath = path.join(__dirname, '..', 'results', filename);
    try {
        return JSON.parse(fs.readFileSync(filepath, 'utf-8'));
    } catch {
        return null;
    }
}

function computeDiffStats(beta5: any, beta0: any): { diffCells: number; maxEnrichment: number } {
    if (!beta5?.heatmap || !beta0?.heatmap) return { diffCells: 0, maxEnrichment: 0 };

    let diffCells = 0;
    let maxDiff = 0;

    for (let i = 0; i < beta5.heatmap.length; i++) {
        for (let j = 0; j < (beta5.heatmap[i]?.length ?? 0); j++) {
            const diff = (beta5.heatmap[i]?.[j] ?? 0) - (beta0.heatmap[i]?.[j] ?? 0);
            if (Math.abs(diff) > 1e-8) diffCells++;
            if (diff > maxDiff) maxDiff = diff;
        }
    }

    return { diffCells, maxEnrichment: maxDiff };
}

function countNonZero(matrix: number[][]): number {
    let count = 0;
    for (const row of matrix) {
        for (const val of row) {
            if (val > 1e-8) count++;
        }
    }
    return count;
}

async function runLocusValidation(locus: typeof LOCI[0]): Promise<ValidationResult> {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`VALIDATING: ${locus.name} (${locus.chromosome})`);
    console.log('='.repeat(60));

    const startTime = Date.now();

    // Check if results already exist
    const existing0 = loadResult(locus.beta0Out);
    const existing5 = loadResult(locus.beta5Out);

    // Run beta=0 if needed
    if (!existing0) {
        console.log(`\n[${locus.name}] Running beta=0 simulation...`);
        await runScript(locus.script, ['--beta=0', '--runs=20', `--out=${locus.beta0Out}`]);
    } else {
        console.log(`[${locus.name}] Beta=0 results found, skipping...`);
    }

    // Run beta=5 if needed
    if (!existing5) {
        console.log(`\n[${locus.name}] Running beta=5 simulation...`);
        await runScript(locus.script, ['--beta=5', '--runs=20', `--out=${locus.beta5Out}`]);
    } else {
        console.log(`[${locus.name}] Beta=5 results found, skipping...`);
    }

    // Load results
    const beta0 = loadResult(locus.beta0Out);
    const beta5 = loadResult(locus.beta5Out);

    if (!beta0 || !beta5) {
        return {
            locus: locus.name,
            chromosome: locus.chromosome,
            length_mb: locus.length_mb,
            beta0: { stepLoadProb: 0, avgLoops: 0, nonZeroCells: 0 },
            beta5: { stepLoadProb: 0, avgLoops: 0, nonZeroCells: 0 },
            loadingIncrease: 0,
            diffCells: 0,
            maxEnrichment: 0,
            status: 'FAIL',
            duration_sec: (Date.now() - startTime) / 1000
        };
    }

    const beta0StepLoad = beta0.fountainLoader?.stepLoadingProbability ?? beta0.stepLoadingProbability ?? 0;
    const beta5StepLoad = beta5.fountainLoader?.stepLoadingProbability ?? beta5.stepLoadingProbability ?? 0;

    const { diffCells, maxEnrichment } = computeDiffStats(beta5, beta0);

    const result: ValidationResult = {
        locus: locus.name,
        chromosome: locus.chromosome,
        length_mb: locus.length_mb,
        beta0: {
            stepLoadProb: beta0StepLoad,
            avgLoops: beta0.avgLoopsPerRun ?? 0,
            nonZeroCells: countNonZero(beta0.heatmap ?? [])
        },
        beta5: {
            stepLoadProb: beta5StepLoad,
            avgLoops: beta5.avgLoopsPerRun ?? 0,
            nonZeroCells: countNonZero(beta5.heatmap ?? [])
        },
        loadingIncrease: beta0StepLoad > 0 ? beta5StepLoad / beta0StepLoad : 0,
        diffCells,
        maxEnrichment,
        status: diffCells > 100 && maxEnrichment > 1e-6 ? 'PASS' : 'FAIL',
        duration_sec: (Date.now() - startTime) / 1000
    };

    console.log(`\n[${locus.name}] Result: ${result.status}`);
    console.log(`  Loading increase: ${result.loadingIncrease.toFixed(1)}x`);
    console.log(`  Diff cells: ${result.diffCells}`);

    return result;
}

async function main() {
    console.log('\n' + '█'.repeat(60));
    console.log('  ARCHCODE - FountainLoader Multi-Locus Validation');
    console.log('  H2: Mediator-driven cohesin loading hypothesis');
    console.log('█'.repeat(60));
    console.log(`\nDate: ${new Date().toISOString()}`);
    console.log(`Loci to validate: ${LOCI.map(l => l.name).join(', ')}`);

    const results: ValidationResult[] = [];
    const totalStart = Date.now();

    for (const locus of LOCI) {
        try {
            const result = await runLocusValidation(locus);
            results.push(result);
        } catch (error) {
            console.error(`[${locus.name}] ERROR:`, error);
            results.push({
                locus: locus.name,
                chromosome: locus.chromosome,
                length_mb: locus.length_mb,
                beta0: { stepLoadProb: 0, avgLoops: 0, nonZeroCells: 0 },
                beta5: { stepLoadProb: 0, avgLoops: 0, nonZeroCells: 0 },
                loadingIncrease: 0,
                diffCells: 0,
                maxEnrichment: 0,
                status: 'FAIL',
                duration_sec: 0
            });
        }
    }

    // Generate summary
    const totalDuration = (Date.now() - totalStart) / 1000;
    const passCount = results.filter(r => r.status === 'PASS').length;

    console.log('\n' + '█'.repeat(60));
    console.log('  VALIDATION SUMMARY');
    console.log('█'.repeat(60));
    console.log('\n| Locus | Chr | Length | Load↑ | Diff | Status |');
    console.log('|-------|-----|--------|-------|------|--------|');

    for (const r of results) {
        const status = r.status === 'PASS' ? '✓ PASS' : '✗ FAIL';
        console.log(`| ${r.locus.padEnd(5)} | ${r.chromosome.padEnd(5)} | ${r.length_mb.toFixed(1).padStart(4)} Mb | ${r.loadingIncrease.toFixed(1).padStart(4)}x | ${r.diffCells.toString().padStart(4)} | ${status} |`);
    }

    console.log('\n' + '-'.repeat(60));
    console.log(`Total: ${passCount}/${results.length} PASS`);
    console.log(`Duration: ${(totalDuration / 60).toFixed(1)} minutes`);
    console.log('-'.repeat(60));

    // Save summary report
    const summaryReport = {
        title: 'ARCHCODE FountainLoader Multi-Locus Validation',
        hypothesis: 'H2: Mediator-driven cohesin loading',
        date: new Date().toISOString(),
        parameters: {
            beta_baseline: 0,
            beta_optimal: 5,
            num_runs: 20,
            max_steps: 50000,
            num_cohesins: 15,
            resolution_bp: 5000
        },
        results,
        summary: {
            total_loci: results.length,
            passed: passCount,
            failed: results.length - passCount,
            overall_status: passCount === results.length ? 'ALL PASS' : 'PARTIAL',
            total_duration_sec: totalDuration,
            total_duration_min: totalDuration / 60
        },
        conclusion: passCount === results.length
            ? 'FountainLoader hypothesis validated across all tested loci. Mediator-driven spatial cohesin loading produces distinct contact patterns.'
            : `Validation incomplete. ${passCount}/${results.length} loci passed.`
    };

    const summaryPath = path.join(__dirname, '..', 'results', 'validation_summary.json');
    fs.writeFileSync(summaryPath, JSON.stringify(summaryReport, null, 2), 'utf-8');
    console.log(`\nSummary saved to: ${summaryPath}`);

    // Exit with appropriate code
    process.exit(passCount === results.length ? 0 : 1);
}

main().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
