/**
 * Сравнение fountain_test_v1.json и baseline_sabaté_v1.json.
 * Diff = fountain.heatmap - baseline.heatmap.
 * Сохраняет: results/diff_map_fountain_vs_baseline.json и HTML-визуализацию.
 */

import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const FOUNTAIN_PATH = path.join(__dirname, '..', 'results', 'fountain_test_v1.json');
const BASELINE_PATH = path.join(__dirname, '..', 'results', 'baseline_sabaté_v1.json');
const OUT_JSON = path.join(__dirname, '..', 'results', 'diff_map_fountain_vs_baseline.json');
const OUT_HTML = path.join(__dirname, '..', 'results', 'diff_map_fountain_vs_baseline.html');

interface RunResult {
    heatmap: number[][];
    locus?: { chrom: string; start: number; end: number; length_bp: number };
    params?: { beta?: number; resolution?: number };
}

function loadJson(p: string): RunResult {
    const raw = fs.readFileSync(p, 'utf-8');
    return JSON.parse(raw) as RunResult;
}

function main(): void {
    const fountain = loadJson(FOUNTAIN_PATH);
    const baseline = loadJson(BASELINE_PATH);

    const A = fountain.heatmap;
    const B = baseline.heatmap;

    const rows = A.length;
    const cols = A[0]?.length ?? 0;
    if (rows !== B.length || cols !== (B[0]?.length ?? 0)) {
        throw new Error(`Matrix size mismatch: fountain ${rows}x${cols}, baseline ${B.length}x${B[0]?.length ?? 0}`);
    }

    const diff: number[][] = [];
    let minD = Infinity;
    let maxD = -Infinity;
    let sumD = 0;
    let count = 0;

    for (let i = 0; i < rows; i++) {
        const row: number[] = [];
        for (let j = 0; j < cols; j++) {
            const d = (A[i]![j] ?? 0) - (B[i]![j] ?? 0);
            row.push(d);
            if (d < minD) minD = d;
            if (d > maxD) maxD = d;
            sumD += d;
            count++;
        }
        diff.push(row);
    }

    const meanD = count > 0 ? sumD / count : 0;
    const locus = fountain.locus ?? baseline.locus;

    const payload = {
        description: 'Diff Map: fountain_test_v1 (beta=2) minus baseline_sabaté_v1 (beta=0)',
        locus,
        resolution: fountain.params?.resolution ?? 5000,
        stats: { min: minD, max: maxD, mean: meanD, rows, cols },
        diff,
    };

    const resultsDir = path.dirname(OUT_JSON);
    if (!fs.existsSync(resultsDir)) fs.mkdirSync(resultsDir, { recursive: true });

    fs.writeFileSync(OUT_JSON, JSON.stringify(payload, null, 2), 'utf-8');
    console.log('[compare] Written', OUT_JSON);
    console.log('[compare] Diff stats: min=', minD, 'max=', maxD, 'mean=', meanD, 'shape=', rows, 'x', cols);

    // HTML: diverging heatmap (red = positive, blue = negative)
    const maxAbs = Math.max(Math.abs(minD), Math.abs(maxD), 1e-10);
    const isZeroDiff = minD === 0 && maxD === 0;
    const diffJs = JSON.stringify(diff);
    const html = `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Diff Map: Fountain (β=2) − Baseline (β=0)</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 1rem; background: #1a1a1a; color: #eee; }
    h1 { font-size: 1.1rem; }
    .meta { font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }
    #canvas { display: block; border: 1px solid #444; background: #111; }
    .legend { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; font-size: 0.8rem; }
    .legend span { flex: 0 0 auto; }
    .legend div { height: 12px; border-radius: 2px; flex: 1 1 200px; max-width: 300px; }
  </style>
</head>
<body>
  <h1>Diff Map: Fountain (β=2) − Baseline (β=0)</h1>
  <p class="meta">MYC chr8:127.7–128.8 Mb · resolution 5 kb · red = больше контактов при β=2, синий = меньше</p>
  ${isZeroDiff ? '<p class="meta" style="color:#fa0;">Разница матриц = 0 (одинаковый seed/шаги → одинаковые траектории).</p>' : ''}
  <canvas id="canvas" width="520" height="520"></canvas>
  <div class="legend">
    <span>−</span>
    <div id="legendBar"></div>
    <span>+</span>
    <span id="legendRange"></span>
  </div>
  <script>
    const diff = ${diffJs};
    const maxAbs = ${maxAbs};
    const rows = diff.length;
    const cols = diff[0]?.length || 0;
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const cellW = canvas.width / cols;
    const cellH = canvas.height / rows;

    function valueToRgb(v) {
      const t = v / maxAbs;
      if (t <= 0) {
        const u = Math.max(0, 1 + t);
        return [Math.round(80 * (1 - u)), Math.round(80 * (1 - u)), Math.round(255 * u)];
      } else {
        const u = Math.min(1, t);
        return [Math.round(255 * u), Math.round(80 * (1 - u)), Math.round(80 * (1 - u))];
      }
    }

    for (let i = 0; i < rows; i++) {
      for (let j = 0; j < cols; j++) {
        const v = diff[i][j];
        const [r,g,b] = valueToRgb(v);
        ctx.fillStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
        ctx.fillRect(j * cellW, i * cellH, Math.ceil(cellW) + 1, Math.ceil(cellH) + 1);
      }
    }

    const leg = document.getElementById('legendBar');
    leg.style.background = 'linear-gradient(to right, rgb(0,0,255), rgb(80,80,80), rgb(255,80,80))';
    document.getElementById('legendRange').textContent = 'min=' + (${minD}).toFixed(4) + ' max=' + (${maxD}).toFixed(4);
  </script>
</body>
</html>`;

    fs.writeFileSync(OUT_HTML, html, 'utf-8');
    console.log('[compare] Written', OUT_HTML);
}

main();
