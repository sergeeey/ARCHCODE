import { useMemo } from 'react';
import { ContactMatrix, PSCurve, PowerLawFit } from '../../domain/models/genome';

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
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
        }}>
            <h4 style={{ margin: '0 0 15px 0' }}>{title}</h4>
            <svg width={canvasSize} height={canvasSize}>
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
                <text x={padding} y={canvasSize - 5} fill="#888" fontSize="10">0</text>
                <text x={canvasSize - 50} y={canvasSize - 5} fill="#888" fontSize="10">
                    {matrix.length} bins
                </text>
                <text x={5} y={padding} fill="#888" fontSize="10">0</text>
                <text x={5} y={canvasSize - padding} fill="#888" fontSize="10">
                    {matrix.length}
                </text>
            </svg>
            <div style={{ fontSize: '11px', color: '#888', marginTop: '10px' }}>
                Range: {min.toFixed(3)} - {max.toFixed(3)}
            </div>
        </div>
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
            <div style={{
                padding: '20px',
                background: 'rgba(0,0,0,0.8)',
                borderRadius: '8px',
                color: '#888',
                fontFamily: 'monospace',
            }}>
                <h4 style={{ margin: '0 0 15px 0' }}>P(s) Curve</h4>
                <div>No data available</div>
            </div>
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
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
        }}>
            <h4 style={{ margin: '0 0 15px 0' }}>P(s) Curve (log-log)</h4>
            
            <svg width={canvasWidth} height={canvasHeight}>
                {/* Grid lines */}
                {[0.2, 0.4, 0.6, 0.8].map(t => (
                    <g key={t}>
                        <line
                            x1={padding.left + t * plotWidth}
                            y1={padding.top}
                            x2={padding.left + t * plotWidth}
                            y2={canvasHeight - padding.bottom}
                            stroke="#333"
                            strokeDasharray="2,2"
                        />
                        <line
                            x1={padding.left}
                            y1={padding.top + t * plotHeight}
                            x2={canvasWidth - padding.right}
                            y2={padding.top + t * plotHeight}
                            stroke="#333"
                            strokeDasharray="2,2"
                        />
                    </g>
                ))}

                {/* Axes */}
                <line
                    x1={padding.left}
                    y1={canvasHeight - padding.bottom}
                    x2={canvasWidth - padding.right}
                    y2={canvasHeight - padding.bottom}
                    stroke="#555"
                />
                <line
                    x1={padding.left}
                    y1={padding.top}
                    x2={padding.left}
                    y2={canvasHeight - padding.bottom}
                    stroke="#555"
                />

                {/* Fit line */}
                <path
                    d={fitPathData}
                    fill="none"
                    stroke="#e74c3c"
                    strokeWidth={2}
                    strokeDasharray="5,5"
                />

                {/* Data points */}
                <path
                    d={pathData}
                    fill="none"
                    stroke="#3498db"
                    strokeWidth={2}
                />
                
                {logDistances.map((x, i) => (
                    <circle
                        key={i}
                        cx={scaleX(x)}
                        cy={scaleY(logContacts[i])}
                        r={3}
                        fill="#3498db"
                    />
                ))}

                {/* X axis labels */}
                <text x={padding.left} y={canvasHeight - 10} fill="#888" fontSize="10">
                    {Math.pow(10, xMin).toFixed(0)}
                </text>
                <text x={canvasWidth - padding.right - 30} y={canvasHeight - 10} fill="#888" fontSize="10">
                    {Math.pow(10, xMax).toFixed(0)}
                </text>
                <text x={canvasWidth / 2 - 20} y={canvasHeight - 5} fill="#888" fontSize="10">
                    Distance (bins)
                </text>

                {/* Y axis labels */}
                <text x={10} y={canvasHeight - padding.bottom} fill="#888" fontSize="10">
                    {Math.pow(10, yMin).toExponential(1)}
                </text>
                <text x={10} y={padding.top + 10} fill="#888" fontSize="10">
                    {Math.pow(10, yMax).toExponential(1)}
                </text>
                <text x={15} y={canvasHeight / 2} fill="#888" fontSize="10" transform={`rotate(-90, 15, ${canvasHeight / 2})`}>
                    Contact
                </text>
            </svg>

            <div style={{ 
                marginTop: '15px', 
                padding: '10px', 
                background: 'rgba(52, 152, 219, 0.1)',
                borderRadius: '4px',
                fontSize: '13px',
            }}>
                <div><strong>Power-law fit:</strong> P(s) ~ s^α</div>
                <div style={{ marginTop: '5px', display: 'flex', gap: '20px' }}>
                    <div>α (alpha): <strong style={{ color: '#3498db' }}>{fit.alpha.toFixed(3)}</strong></div>
                    <div>R²: <strong style={{ color: fit.r2 > 0.9 ? '#2ecc71' : '#e74c3c' }}>{fit.r2.toFixed(3)}</strong></div>
                </div>
                <div style={{ marginTop: '5px', fontSize: '11px', color: '#888' }}>
                    Expected: α ≈ -1.0 for Hi-C data
                </div>
            </div>
        </div>
    );
};
