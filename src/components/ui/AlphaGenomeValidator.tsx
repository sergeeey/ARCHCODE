import { useState, useCallback } from 'react';
import {
    AlphaGenomeClient,
    ValidationResult,
    OutputType,
    GenomeInterval,
} from '../../validation/alphagenome';
import { LoopExtrusionEngine, loopsToContactMatrix } from '../../engines/LoopExtrusionEngine';
import { ContactMatrixViewer } from './ContactMatrixViewer';

interface AlphaGenomeValidatorProps {
    engine: LoopExtrusionEngine;
    apiKey?: string;
}

export const AlphaGenomeValidator = ({ engine, apiKey }: AlphaGenomeValidatorProps) => {
    const [validating, setValidating] = useState(false);
    const [result, setResult] = useState<ValidationResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [activeView, setActiveView] = useState<'alphagenome' | 'archcode' | 'diff'>('diff');

    const handleValidate = useCallback(async () => {
        if (!apiKey) {
            setError('Please set AlphaGenome API key');
            return;
        }

        setValidating(true);
        setError(null);

        try {
            const client = new AlphaGenomeClient({ apiKey });
            
            const interval: GenomeInterval = {
                chromosome: 'chr11',
                start: 5200000,
                end: 5350000,
            };

            // Get ARCHCODE matrix
            const loops = engine.getLoops();
            const archcodeMatrix = loopsToContactMatrix(
                loops,
                interval.start,
                interval.end,
                10000
            );

            // Validate against AlphaGenome
            const validation = await client.validateArchcode(interval, archcodeMatrix);
            setResult(validation);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Validation failed');
        } finally {
            setValidating(false);
        }
    }, [apiKey, engine]);

    const getCurrentMatrix = () => {
        if (!result) return null;
        switch (activeView) {
            case 'alphagenome': return result.alphaGenomeMap;
            case 'archcode': return result.archcodeMap;
            case 'diff': return result.diffMap;
            default: return null;
        }
    };

    const getCorrelationColor = (r: number) => {
        if (r > 0.8) return '#2ecc71'; // Green - excellent
        if (r > 0.6) return '#f39c12'; // Orange - good
        return '#e74c3c'; // Red - poor
    };

    return (
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
        }}>
            <h3 style={{ margin: '0 0 15px 0' }}>🔬 AlphaGenome Validation</h3>
            
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '15px' }}>
                Compare ARCHCODE simulation with DeepMind AlphaGenome predictions
            </div>

            {!apiKey && (
                <div style={{
                    padding: '10px',
                    background: 'rgba(231, 76, 60, 0.2)',
                    border: '1px solid #e74c3c',
                    borderRadius: '4px',
                    color: '#e74c3c',
                    fontSize: '12px',
                    marginBottom: '15px',
                }}>
                    ⚠️ Set AlphaGenome API key to enable validation
                </div>
            )}

            <button
                onClick={handleValidate}
                disabled={validating || !apiKey}
                style={{
                    width: '100%',
                    padding: '12px',
                    background: validating ? '#27ae60' : '#2ecc71',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: validating || !apiKey ? 'default' : 'pointer',
                    fontSize: '14px',
                    fontWeight: 'bold',
                    marginBottom: '15px',
                }}
            >
                {validating ? '⏳ Validating...' : '🔍 Validate with AlphaGenome'}
            </button>

            {error && (
                <div style={{
                    padding: '10px',
                    background: 'rgba(231, 76, 60, 0.2)',
                    border: '1px solid #e74c3c',
                    borderRadius: '4px',
                    color: '#e74c3c',
                    fontSize: '12px',
                    marginBottom: '15px',
                }}>
                    ❌ {error}
                </div>
            )}

            {result && (
                <>
                    {/* Metrics */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '10px',
                        marginBottom: '20px',
                    }}>
                        <div style={{
                            padding: '15px',
                            background: 'rgba(52, 152, 219, 0.1)',
                            borderRadius: '4px',
                            textAlign: 'center',
                        }}>
                            <div style={{ fontSize: '11px', color: '#888' }}>Pearson r</div>
                            <div style={{
                                fontSize: '24px',
                                fontWeight: 'bold',
                                color: getCorrelationColor(result.pearsonCorrelation),
                            }}>
                                {result.pearsonCorrelation.toFixed(3)}
                            </div>
                        </div>
                        <div style={{
                            padding: '15px',
                            background: 'rgba(52, 152, 219, 0.1)',
                            borderRadius: '4px',
                            textAlign: 'center',
                        }}>
                            <div style={{ fontSize: '11px', color: '#888' }}>Spearman ρ</div>
                            <div style={{
                                fontSize: '24px',
                                fontWeight: 'bold',
                                color: getCorrelationColor(result.spearmanCorrelation),
                            }}>
                                {result.spearmanCorrelation.toFixed(3)}
                            </div>
                        </div>
                        <div style={{
                            padding: '15px',
                            background: 'rgba(155, 89, 182, 0.1)',
                            borderRadius: '4px',
                            textAlign: 'center',
                        }}>
                            <div style={{ fontSize: '11px', color: '#888' }}>RMSE</div>
                            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                {result.rmse.toFixed(4)}
                            </div>
                        </div>
                        <div style={{
                            padding: '15px',
                            background: 'rgba(155, 89, 182, 0.1)',
                            borderRadius: '4px',
                            textAlign: 'center',
                        }}>
                            <div style={{ fontSize: '11px', color: '#888' }}>MSE</div>
                            <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                {result.mse.toFixed(4)}
                            </div>
                        </div>
                    </div>

                    {/* Interpretation */}
                    <div style={{
                        padding: '10px',
                        background: result.pearsonCorrelation > 0.7 ? 'rgba(46, 204, 113, 0.1)' : 'rgba(243, 156, 18, 0.1)',
                        border: `1px solid ${result.pearsonCorrelation > 0.7 ? '#2ecc71' : '#f39c12'}`,
                        borderRadius: '4px',
                        fontSize: '12px',
                        marginBottom: '15px',
                    }}>
                        {result.pearsonCorrelation > 0.8 ? (
                            <>✅ <strong>Excellent agreement!</strong> Your simulation closely matches AlphaGenome predictions.</>
                        ) : result.pearsonCorrelation > 0.6 ? (
                            <>⚠️ <strong>Good agreement.</strong> Some differences observed. Check parameters.</>
                        ) : (
                            <>❌ <strong>Poor agreement.</strong> Simulation may need tuning.</>
                        )}
                    </div>

                    {/* View Toggle */}
                    <div style={{
                        display: 'flex',
                        gap: '5px',
                        marginBottom: '15px',
                    }}>
                        {(['alphagenome', 'archcode', 'diff'] as const).map((view) => (
                            <button
                                key={view}
                                onClick={() => setActiveView(view)}
                                style={{
                                    flex: 1,
                                    padding: '8px',
                                    background: activeView === view ? '#3498db' : 'transparent',
                                    color: activeView === view ? 'white' : '#888',
                                    border: '1px solid #444',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '11px',
                                }}
                            >
                                {view === 'alphagenome' ? 'AlphaGenome' : 
                                 view === 'archcode' ? 'ARCHCODE' : 'Difference'}
                            </button>
                        ))}
                    </div>

                    {/* Matrix View */}
                    {getCurrentMatrix() && (
                        <ContactMatrixViewer 
                            matrix={getCurrentMatrix()!}
                            title={activeView === 'diff' ? 'Difference Map (A - B)' : 
                                   activeView === 'alphagenome' ? 'AlphaGenome Prediction' : 
                                   'ARCHCODE Simulation'}
                        />
                    )}
                </>
            )}
        </div>
    );
};
