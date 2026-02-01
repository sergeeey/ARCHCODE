import { useState, useEffect } from 'react';
import { LoopExtrusionEngine } from '../../engines/LoopExtrusionEngine';
import { CTCFSite } from '../../domain/models/genome';

interface DebugOverlayProps {
    engine: LoopExtrusionEngine;
    ctcfSites: CTCFSite[];
    isRunning: boolean;
}

interface ConvergentCheck {
    step: number;
    cohesinLeft: number;
    cohesinRight: number;
    nearbyCTCF: Array<{
        position: number;
        orientation: string;
        distance: number;
    }>;
    isConvergent: boolean;
    reason: string;
}

export const DebugOverlay = ({ engine, ctcfSites, isRunning }: DebugOverlayProps) => {
    const [debugInfo, setDebugInfo] = useState<{
        step: number;
        loops: number;
        activeCohesin: number;
        lastCheck: ConvergentCheck | null;
        convergentPairs: Array<[CTCFSite, CTCFSite]>;
    }>({
        step: 0,
        loops: 0,
        activeCohesin: 0,
        lastCheck: null,
        convergentPairs: [],
    });

    useEffect(() => {
        // Находим конвергентные пары
        const pairs: Array<[CTCFSite, CTCFSite]> = [];
        const sorted = [...ctcfSites].sort((a, b) => a.position - b.position);
        for (let i = 0; i < sorted.length - 1; i++) {
            for (let j = i + 1; j < sorted.length; j++) {
                const c1 = sorted[i];
                const c2 = sorted[j];
                // F (> ) ... R (< ) = convergent
                if (c1.orientation === 'F' && c2.orientation === 'R') {
                    pairs.push([c1, c2]);
                }
            }
        }

        const interval = setInterval(() => {
            const cohesins = engine.getCohesins();
            const active = cohesins.filter(c => c.active);
            
            // Симулируем проверку для первого активного cohesin
            let lastCheck: ConvergentCheck | null = null;
            if (active.length > 0) {
                const c = active[0];
                const nearby = ctcfSites
                    .map(site => ({
                        position: site.position,
                        orientation: site.orientation,
                        distance: Math.min(
                            Math.abs(site.position - c.leftLeg),
                            Math.abs(site.position - c.rightLeg)
                        ),
                    }))
                    .filter(s => s.distance < 100000) // в пределах 100kb
                    .sort((a, b) => a.distance - b.distance)
                    .slice(0, 4);

                // Проверяем конвергенцию
                const leftR = nearby.find(s => s.orientation === 'R' && s.position <= c.leftLeg);
                const rightF = nearby.find(s => s.orientation === 'F' && s.position >= c.rightLeg);
                
                let reason = 'no_pair';
                if (leftR && rightF) {
                    reason = 'success';
                } else if (!leftR && !rightF) {
                    reason = 'no_nearby';
                } else if (!leftR) {
                    reason = 'no_left_R';
                } else {
                    reason = 'no_right_F';
                }

                lastCheck = {
                    step: engine.getStepCount(),
                    cohesinLeft: c.leftLeg,
                    cohesinRight: c.rightLeg,
                    nearbyCTCF: nearby,
                    isConvergent: !!(leftR && rightF),
                    reason,
                };
            }

            setDebugInfo({
                step: engine.getStepCount(),
                loops: engine.getLoops().length,
                activeCohesin: active.length,
                lastCheck,
                convergentPairs: pairs,
            });
        }, 200); // обновление каждые 200ms

        return () => clearInterval(interval);
    }, [engine, ctcfSites]);

    return (
        <div style={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            width: '400px',
            background: 'rgba(0, 0, 0, 0.9)',
            border: '2px solid #333',
            borderRadius: '8px',
            padding: '15px',
            color: '#0f0',
            fontFamily: 'monospace',
            fontSize: '12px',
            zIndex: 1000,
            maxHeight: '500px',
            overflow: 'auto',
        }}>
            <div style={{ 
                borderBottom: '1px solid #333', 
                paddingBottom: '10px',
                marginBottom: '10px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
            }}>
                <span style={{ fontWeight: 'bold', fontSize: '14px' }}>🔍 DEBUG PANEL</span>
                <span style={{ 
                    color: isRunning ? '#0f0' : '#666',
                    animation: isRunning ? 'pulse 1s infinite' : 'none',
                }}>
                    {isRunning ? '● LIVE' : '○ PAUSED'}
                </span>
            </div>

            {/* Основные метрики */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px' }}>
                <div style={{ background: '#111', padding: '8px', borderRadius: '4px' }}>
                    <div style={{ color: '#888', fontSize: '10px' }}>Step</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{debugInfo.step}</div>
                </div>
                <div style={{ background: '#111', padding: '8px', borderRadius: '4px' }}>
                    <div style={{ color: '#888', fontSize: '10px' }}>Active Cohesin</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: debugInfo.activeCohesin > 0 ? '#0f0' : '#f00' }}>
                        {debugInfo.activeCohesin}
                    </div>
                </div>
                <div style={{ background: '#111', padding: '8px', borderRadius: '4px' }}>
                    <div style={{ color: '#888', fontSize: '10px' }}>Loops Formed</div>
                    <div style={{ 
                        fontSize: '18px', 
                        fontWeight: 'bold', 
                        color: debugInfo.loops > 0 ? '#0f0' : '#f00',
                        animation: debugInfo.loops > 0 ? 'none' : 'blink 1s infinite',
                    }}>
                        {debugInfo.loops}
                    </div>
                </div>
                <div style={{ background: '#111', padding: '8px', borderRadius: '4px' }}>
                    <div style={{ color: '#888', fontSize: '10px' }}>Convergent Pairs</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#ff0' }}>
                        {debugInfo.convergentPairs.length}
                    </div>
                </div>
            </div>

            {/* Список конвергентных пар */}
            <div style={{ marginBottom: '15px' }}>
                <div style={{ color: '#888', marginBottom: '5px' }}>Convergent Pairs (F...R):</div>
                {debugInfo.convergentPairs.length === 0 ? (
                    <div style={{ color: '#f00', background: '#300', padding: '5px', borderRadius: '4px' }}>
                        ⚠️ NO CONVERGENT PAIRS FOUND!
                    </div>
                ) : (
                    debugInfo.convergentPairs.map(([f, r], i) => (
                        <div key={i} style={{ 
                            background: '#111', 
                            padding: '5px', 
                            marginBottom: '3px',
                            borderRadius: '3px',
                            display: 'flex',
                            justifyContent: 'space-between',
                        }}>
                            <span>Pair {i + 1}:</span>
                            <span style={{ color: '#0f0' }}>
                                F@{f.position.toLocaleString()} → R@{r.position.toLocaleString()}
                            </span>
                            <span style={{ color: '#888' }}>
                                ({((r.position - f.position) / 1000).toFixed(1)}kb)
                            </span>
                        </div>
                    ))
                )}
            </div>

            {/* Последняя проверка */}
            {debugInfo.lastCheck && (
                <div style={{ borderTop: '1px solid #333', paddingTop: '10px' }}>
                    <div style={{ color: '#888', marginBottom: '5px' }}>
                        Last Check (Step {debugInfo.lastCheck.step}):
                    </div>
                    <div style={{ background: '#111', padding: '8px', borderRadius: '4px', marginBottom: '10px' }}>
                        <div>Cohesin: {debugInfo.lastCheck.cohesinLeft.toLocaleString()} - {debugInfo.lastCheck.cohesinRight.toLocaleString()}</div>
                        <div style={{ marginTop: '5px', color: '#888' }}>Nearby CTCF:</div>
                        {debugInfo.lastCheck.nearbyCTCF.map((ctcf, i) => (
                            <div key={i} style={{ 
                                paddingLeft: '10px',
                                color: ctcf.distance < 50000 ? '#ff0' : '#666',
                            }}>
                                {ctcf.orientation}@{ctcf.position.toLocaleString()} ({(ctcf.distance / 1000).toFixed(1)}kb)
                            </div>
                        ))}
                    </div>
                    
                    <div style={{ 
                        padding: '8px',
                        borderRadius: '4px',
                        background: debugInfo.lastCheck.isConvergent ? '#030' : '#300',
                        border: `1px solid ${debugInfo.lastCheck.isConvergent ? '#0f0' : '#f00'}`,
                    }}>
                        <div style={{ color: debugInfo.lastCheck.isConvergent ? '#0f0' : '#f00', fontWeight: 'bold' }}>
                            {debugInfo.lastCheck.isConvergent ? '✅ CONVERGENT' : '❌ NOT CONVERGENT'}
                        </div>
                        <div style={{ color: '#888', fontSize: '10px', marginTop: '3px' }}>
                            Reason: {debugInfo.lastCheck.reason}
                        </div>
                    </div>
                </div>
            )}

            {/* Подсказки */}
            <div style={{ 
                marginTop: '15px',
                padding: '10px',
                background: '#221',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#ff8',
            }}>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>💡 Debug Tips:</div>
                <div>• If "Convergent Pairs" = 0, check your CTCF orientations</div>
                <div>• F(+) must be LEFT of R(-) to form loop</div>
                <div>• Distance should be 20-100kb for stable loops</div>
            </div>

            <style>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.3; }
                }
            `}</style>
        </div>
    );
};
