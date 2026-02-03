#!/usr/bin/env node
/**
 * CLI script to download CTCF data from ENCODE
 * Usage: node scripts/download-encode.js [file-id]
 * Example: node scripts/download-encode.js ENCFF165MIL
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const DATASETS = [
    { id: 'ENCFF165MIL', cellLine: 'GM12878', url: 'https://www.encodeproject.org/files/ENCFF165MIL/@@download/ENCFF165MIL.bed.gz' },
    { id: 'ENCFF002CEL', cellLine: 'K562', url: 'https://www.encodeproject.org/files/ENCFF002CEL/@@download/ENCFF002CEL.bed.gz' },
    { id: 'ENCFF002CVM', cellLine: 'HeLa-S3', url: 'https://www.encodeproject.org/files/ENCFF002CVM/@@download/ENCFF002CVM.bed.gz' },
    { id: 'ENCFF002CVL', cellLine: 'HepG2', url: 'https://www.encodeproject.org/files/ENCFF002CVL/@@download/ENCFF002CVL.bed.gz' },
    { id: 'ENCFF001TZA', cellLine: 'H1-hESC', url: 'https://www.encodeproject.org/files/ENCFF001TZA/@@download/ENCFF001TZA.bed.gz' },
];

function downloadFile(url, outputPath) {
    return new Promise((resolve, reject) => {
        console.log(`Downloading: ${url}`);
        
        const file = fs.createWriteStream(outputPath + '.gz');
        let downloaded = 0;
        
        https.get(url, (response) => {
            const total = parseInt(response.headers['content-length'] || '0');
            
            response.on('data', (chunk) => {
                downloaded += chunk.length;
                if (total > 0) {
                    const percent = Math.round((downloaded / total) * 100);
                    process.stdout.write(`\rProgress: ${percent}% (${(downloaded/1024/1024).toFixed(1)} MB)`);
                }
            });
            
            response.pipe(file);
            
            file.on('finish', () => {
                file.close();
                console.log('\nDownload complete. Decompressing...');
                
                // Decompress
                const gunzip = zlib.createGunzip();
                const input = fs.createReadStream(outputPath + '.gz');
                const output = fs.createWriteStream(outputPath);
                
                input.pipe(gunzip).pipe(output);
                
                output.on('finish', () => {
                    fs.unlinkSync(outputPath + '.gz');
                    console.log(`Saved to: ${outputPath}`);
                    resolve();
                });
                
                output.on('error', reject);
            });
        }).on('error', (err) => {
            if (fs.existsSync(outputPath + '.gz')) {
                fs.unlinkSync(outputPath + '.gz');
            }
            reject(err);
        });
    });
}

async function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
        console.log(`
ARCHCODE ENCODE Downloader

Usage:
  node scripts/download-encode.js [file-id]
  node scripts/download-encode.js --all

Available datasets:
${DATASETS.map(d => `  ${d.id.padEnd(15)} ${d.cellLine.padEnd(12)}`).join('\n')}

Examples:
  node scripts/download-encode.js ENCFF165MIL    # Download GM12878 CTCF
  node scripts/download-encode.js --all          # Download all datasets
`);
        return;
    }
    
    const outputDir = path.join(__dirname, '..', 'data', 'input', 'ctcf');
    
    // Ensure directory exists
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    if (args[0] === '--all') {
        console.log('Downloading all datasets...\n');
        for (const dataset of DATASETS) {
            const outputPath = path.join(outputDir, `${dataset.cellLine}_CTCF.bed`);
            if (fs.existsSync(outputPath)) {
                console.log(`Skipping ${dataset.cellLine} (already exists)`);
                continue;
            }
            try {
                await downloadFile(dataset.url, outputPath);
            } catch (err) {
                console.error(`Error downloading ${dataset.id}:`, err.message);
            }
        }
        console.log('\nAll downloads complete!');
    } else {
        const fileId = args[0];
        const dataset = DATASETS.find(d => d.id === fileId);
        
        if (!dataset) {
            console.error(`Unknown file ID: ${fileId}`);
            console.log(`Available: ${DATASETS.map(d => d.id).join(', ')}`);
            process.exit(1);
        }
        
        const outputPath = path.join(outputDir, `${dataset.cellLine}_CTCF.bed`);
        
        if (fs.existsSync(outputPath)) {
            console.log(`File already exists: ${outputPath}`);
            return;
        }
        
        try {
            await downloadFile(dataset.url, outputPath);
            console.log('\nDone!');
        } catch (err) {
            console.error('Download failed:', err.message);
            process.exit(1);
        }
    }
}

main().catch(console.error);
