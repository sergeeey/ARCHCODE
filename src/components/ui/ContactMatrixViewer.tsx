import { useMemo } from 'react';
import { ContactMatrix, PSCurve, PowerLawFit } from '../../domain/models/genome';
import { Panel } from './Panel';

interface ContactMatrixViewerProps {
    matrix: ContactMatrix;
    title?: string;
}

interface PSCurveViewerProps {
    psCurve: PSCurve;
    fit: PowerLawFit;
}

export const ContactMatrixViewer = ({ matrix, title = 'Contact Matrix' }: ContactMatrixViewerProps) => {
    const canvasSize = 300;
    const padding = 30;
    const cellSize = (canvasSize - padding * 2) / matrix.length;

    // Find min/max for color scaling
    const { min, max } = useMemo(() => {
        let min = Infinity;
        let max = -Infinity;
        for (const row of matrix) {
            for (const val of row) {
                if (val < min) min = val;
                if (val > max) max = val;
            }
        }
        return { min, max };
    }, [matrix]);

    const getColor = (value: number): string => {
        const normalized = (value - min) / (max - min || 1);
        // Heatmap: black -> blue -> yellow -> red -> white
        const r = Math.min(255, normalized * 4 * 255);
        const g = Math.min(255, Math.max(0, (normalized - 0.25) * 4 * 255));
        const b = Math.min(255, Math.max(0, (normalized - 0.5) * 4 * 255));
        return `rgb(${r},${g},${b})`;
    };

    return (
        <Panel title={title} className="font-mono">
            <svg width={canvasSize} height={canvasSize} className="block">
                {matrix.map((row, i) =>
                    row.map((value, j) => (
                        <rect
                            key={`${i}-${j}`}
                            x={padding + j * cellSize}
                            y={padding + i * cellSize}
                            width={cellSize}
                            height={cellSize}
                            fill={getColor(value)}
                        />
                    ))
                )}
                {/* Axes labels */}
                <text x={padding} y={canvasSize - 5} fill="var(--text-label)" fontSize="10" fontFamily="monospace">0</text>
                <text x={canvasSize - 50} y={canvasSize - 5} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{matrix.length} bins</text>
                <text x={5} y={padding} fill="var(--text-label)" fontSize="10" fontFamily="monospace">0</text>
                <text x={5} y={canvasSize - padding} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{matrix.length}</text>
            </svg>
            <div className="text-[11px] text-[var(--text-label)] mt-2 tabular-nums font-mono">
                Range: {min.toFixed(3)} - {max.toFixed(3)}
            </div>
        </Panel>
    );
};

export const PSCurveViewer = ({ psCurve, fit }: PSCurveViewerProps) => {
    const canvasWidth = 350;
    const canvasHeight = 250;
    const padding = { top: 20, right: 30, bottom: 50, left: 60 };
    
    const plotWidth = canvasWidth - padding.left - padding.right;
    const plotHeight = canvasHeight - padding.top - padding.bottom;

    if (psCurve.distances.length === 0) {
        return (
            <Panel title="P(s) Curve" className="font-mono">
                <div className="text-[var(--text-label)] text-sm">No data available</div>
            </Panel>
        );
    }

    // Log scale for both axes
    const logDistances = psCurve.distances.map(d => Math.log10(d));
    const logContacts = psCurve.contacts.map(c => Math.log10(Math.max(c, 1e-10)));
    
    const xMin = Math.min(...logDistances);
    const xMax = Math.max(...logDistances);
    const yMin = Math.min(...logContacts);
    const yMax = Math.max(...logContacts);

    const scaleX = (val: number) => 
        padding.left + ((val - xMin) / (xMax - xMin || 1)) * plotWidth;
    const scaleY = (val: number) => 
        canvasHeight - padding.bottom - ((val - yMin) / (yMax - yMin || 1)) * plotHeight;

    // Create path for data points
    const pathData = logDistances
        .map((x, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(x)} ${scaleY(logContacts[i])}`)
        .join(' ');

    // Create path for fit line
    const fitPathData = [
        [xMin, fit.alpha * xMin + (logContacts[0] - fit.alpha * logDistances[0])],
        [xMax, fit.alpha * xMax + (logContacts[0] - fit.alpha * logDistances[0])],
    ].map(([x, y], i) => `${i === 0 ? 'M' : 'L'} ${scaleX(x)} ${scaleY(y)}`).join(' ');

    return (
        <Panel title="P(s) Curve (log-log)" className="font-mono">
            <svg width={canvasWidth} height={canvasHeight} className="block">
                <defs>
                    <filter id="glow-ps">
                        <feGaussianBlur stdDeviation="1" result="blur" />
                        <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
                    </filter>
                </defs>
                {[0.2, 0.4, 0.6, 0.8].map(t => (
                    <g key={t}>
                        <line x1={padding.left + t * plotWidth} y1={padding.top} x2={padding.left + t * plotWidth} y2={canvasHeight - padding.bottom} stroke="rgba(255,255,255,0.08)" strokeDasharray="2,2" />
                        <line x1={padding.left} y1={padding.top + t * plotHeight} x2={canvasWidth - padding.right} y2={padding.top + t * plotHeight} stroke="rgba(255,255,255,0.08)" strokeDasharray="2,2" />
                    </g>
                ))}
                <line x1={padding.left} y1={canvasHeight - padding.bottom} x2={canvasWidth - padding.right} y2={canvasHeight - padding.bottom} stroke="rgba(255,255,255,0.15)" />
                <line x1={padding.left} y1={padding.top} x2={padding.left} y2={canvasHeight - padding.bottom} stroke="rgba(255,255,255,0.15)" />
                <path d={fitPathData} fill="none" stroke="var(--accent-danger)" strokeWidth={1} strokeDasharray="4,4" />
                <path d={pathData} fill="none" stroke="var(--accent-live)" strokeWidth={1} filter="url(#glow-ps)" />
                <text x={padding.left} y={canvasHeight - 10} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{Math.pow(10, xMin).toFixed(0)}</text>
                <text x={canvasWidth - padding.right - 30} y={canvasHeight - 10} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{Math.pow(10, xMax).toFixed(0)}</text>
                <text x={canvasWidth / 2 - 25} y={canvasHeight - 5} fill="var(--text-label)" fontSize="10" fontFamily="monospace">Distance (bins)</text>
                <text x={10} y={canvasHeight - padding.bottom} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{Math.pow(10, yMin).toExponential(1)}</text>
                <text x={10} y={padding.top + 10} fill="var(--text-label)" fontSize="10" fontFamily="monospace">{Math.pow(10, yMax).toExponential(1)}</text>
                <text x={15} y={canvasHeight / 2} fill="var(--text-label)" fontSize="10" fontFamily="monospace" transform={`rotate(-90, 15, ${canvasHeight / 2})`}>Contact</text>
            </svg>
            <div className="mt-4 p-3 rounded-[var(--radius-sm)] bg-[rgba(0,240,255,0.06)] border border-[rgba(255,255,255,0.08)] text-xs">
                <div className="text-[var(--text-label)]">Power-law: P(s) ~ s^α</div>
                <div className="mt-2 flex gap-4 tabular-nums">
                    <span className="text-[var(--text-label)]">α: <span className="text-[var(--accent-live)] font-medium">{fit.alpha.toFixed(3)}</span></span>
                    <span className="text-[var(--text-label)]">R²: <span className={fit.r2 > 0.9 ? 'text-[var(--accent-live)]' : 'text-[var(--accent-danger)]'}>{fit.r2.toFixed(3)}</span></span>
                </div>
                <div className="mt-1 text-[10px] text-[var(--text-label)]">Expected α ≈ -1.0</div>
            </div>
        </Panel>
    );
};
