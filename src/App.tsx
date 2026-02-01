import { useState, useCallback, useMemo, useEffect } from 'react';
import { GenomeViewer } from './components/3d/GenomeViewer';
import { BEDUploader } from './components/ui/BEDUploader';
import { ENCODEDownloader } from './components/ui/ENCODEDownloader';
import { ContactMatrixViewer, PSCurveViewer } from './components/ui/ContactMatrixViewer';
import { AlphaGenomeValidator } from './components/ui/AlphaGenomeValidator';
import { DebugOverlay } from './components/ui/DebugOverlay';
import { LoopDashboard } from './components/dashboard/LoopDashboard';
import { LoopExtrusionEngine, loopsToContactMatrix, computePSCurve, fitPSPowerLaw } from './engines/LoopExtrusionEngine';
import { CTCFSite, createCTCFSite } from './domain/models/genome';
import { generateSampleBED } from './parsers/bed';

function App() {
    // State
    const [ctcfSites, setCTCFSites] = useState<CTCFSite[]>([]);
    const [genomeLength, setGenomeLength] = useState(100000);
    const [isRunning, setIsRunning] = useState(false);
    const [resolution, setResolution] = useState(1000);
    const [velocity, setVelocity] = useState(1000);
    const [alphaGenomeApiKey, setAlphaGenomeApiKey] = useState(import.meta.env.VITE_ALPHAGENOME_API_KEY || '');
    const [stepCount, setStepCount] = useState(0); // Force re-render on simulation step
    
    // Create engine
    const engine = useMemo(() => {
        return new LoopExtrusionEngine({
            genomeLength,
            ctcfSites,
            cohesinLoadPosition: Math.floor(genomeLength / 2),
            velocity,
            seed: 42,
        });
    }, [genomeLength, ctcfSites, velocity]);

    // Derived data - use stepCount to force re-render
    const loops = useMemo(() => engine.getLoops(), [engine, stepCount]);
    const activeCohesins = useMemo(() => engine.getCohesins().filter(c => c.active).length, [engine, stepCount]);
    const matrix = useMemo(() => {
        if (loops.length === 0) return null;
        return loopsToContactMatrix(loops, 0, genomeLength, resolution);
    }, [loops, genomeLength, resolution]);

    const psCurve = useMemo(() => {
        if (!matrix) return null;
        return computePSCurve(matrix);
    }, [matrix]);

    const fit = useMemo(() => {
        if (!psCurve) return { alpha: 0, r2: 0 };
        return fitPSPowerLaw(psCurve.distances, psCurve.contacts);
    }, [psCurve]);

    // Handlers
    const handleSitesLoaded = useCallback((sites: CTCFSite[], cellLine?: string) => {
        setCTCFSites(sites);
        // Auto-adjust genome length based on sites
        if (sites.length > 0) {
            const maxPos = Math.max(...sites.map(s => s.position));
            setGenomeLength(Math.max(100000, maxPos * 1.2));
        }
    }, []);

    const handleLoadSample = useCallback(() => {
        const sampleBED = generateSampleBED('chr11', 6);
        // Parse it manually
        const lines = sampleBED.split('\n').filter(l => !l.startsWith('#') && l.trim() !== '');
        const rawSites: { pos: number; strand: string }[] = [];
        
        for (const line of lines) {
            const parts = line.split('\t');
            if (parts.length >= 6) {
                const start = parseInt(parts[1]);
                const end = parseInt(parts[2]);
                const strand = parts[5];
                rawSites.push({
                    pos: Math.floor((start + end) / 2),
                    strand
                });
            }
        }
        
        // НОРМАЛИЗАЦИЯ: сдвигаем координаты чтобы они были в пределах 0-200kb
        const minPos = Math.min(...rawSites.map(s => s.pos));
        const offset = minPos - 20000; // Небольшой отступ слева
        
        const sites = rawSites.map(s => createCTCFSite(
            'chr11',
            s.pos - offset, // Сдвигаем в 0-200kb диапазон
            s.strand === '+' ? 'F' : 'R',
            1.0
        ));
        
        console.log('[Sample] CTCF sites normalized:', sites.map(s => `${s.orientation}@${s.position}`).join(', '));
        
        setCTCFSites(sites);
        setGenomeLength(240000); // 200kb + отступы
    }, []);

    const handleReset = useCallback(() => {
        setCTCFSites([]);
        setIsRunning(false);
        engine.reset();
    }, [engine]);

    // Run simulation loop while isRunning
    useEffect(() => {
        let interval: number;
        if (isRunning) {
            interval = window.setInterval(() => {
                // Выполняем несколько шагов за один тик для ускорения
                for (let i = 0; i < 10; i++) {
                    engine.step();
                }
                setStepCount(engine.getStepCount()); // Синхронизируем с движком
            }, 50); // 20 раз в секунду = 200 шагов/сек
        }
        return () => clearInterval(interval);
    }, [isRunning, engine]);

    const handleRunSimulation = useCallback(() => {
        setIsRunning(true);
        engine.start();
    }, [engine]);

    const handlePauseSimulation = useCallback(() => {
        setIsRunning(false);
        engine.pause();
    }, [engine]);

    const handleStopSimulation = useCallback(() => {
        setIsRunning(false);
        engine.reset();
        setStepCount(0);
    }, [engine]);

    // Load sample on mount
    useEffect(() => {
        handleLoadSample();
    }, []);

    return (
        <div style={{ 
            position: 'relative', 
            width: '100vw', 
            height: '100vh',
            display: 'flex',
        }}>
            {/* Main 3D View */}
            <div style={{ flex: 2, position: 'relative' }}>
                <GenomeViewer engine={engine} />
                
                {/* Debug Overlay */}
                <DebugOverlay engine={engine} ctcfSites={ctcfSites} isRunning={isRunning} />
                
                {/* Overlay Stats */}
                <div style={{
                    position: 'absolute',
                    top: 20,
                    left: 20,
                    background: 'rgba(0,0,0,0.8)',
                    padding: '15px',
                    borderRadius: '8px',
                    color: 'white',
                    fontFamily: 'monospace',
                    fontSize: '13px',
                }}>
                    <h3 style={{ margin: '0 0 10px 0' }}>🔬 ARCHCODE v0.3.1</h3>
                    <div>CTCF Sites: <strong>{ctcfSites.length}</strong></div>
                    <div>Loops Formed: <strong style={{ color: '#00ff88' }}>{loops.length}</strong></div>
                    <div>Active Cohesin: <strong style={{ color: '#f39c12' }}>{activeCohesins}</strong></div>
                    <div>Step: <strong>{engine.getStepCount()}</strong></div>
                    <div style={{ marginTop: '10px', fontSize: '11px', color: '#888' }}>
                        Genome: {genomeLength.toLocaleString()} bp
                    </div>
                </div>

                {/* Playback Controls */}
                <div style={{
                    position: 'absolute',
                    bottom: 30,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    gap: '10px',
                }}>
                    <button
                        onClick={handleRunSimulation}
                        disabled={isRunning}
                        style={{
                            padding: '12px 24px',
                            background: isRunning ? '#2ecc71' : '#27ae60',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: isRunning ? 'default' : 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold',
                        }}
                    >
                        ▶ Run
                    </button>
                    <button
                        onClick={handlePauseSimulation}
                        disabled={!isRunning}
                        style={{
                            padding: '12px 24px',
                            background: !isRunning ? '#95a5a6' : '#e74c3c',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: !isRunning ? 'default' : 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold',
                        }}
                    >
                        ⏸ Pause
                    </button>
                    <button
                        onClick={handleStopSimulation}
                        style={{
                            padding: '12px 24px',
                            background: '#7f8c8d',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 'bold',
                        }}
                    >
                        ⏹ Stop
                    </button>
                    <button
                        onClick={() => { engine.step(); setStepCount(s => s + 1); }}
                        disabled={isRunning}
                        style={{
                            padding: '12px 24px',
                            background: '#3498db',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '14px',
                        }}
                    >
                        ⏭ Step
                    </button>
                </div>
            </div>

            {/* Side Panel */}
            <div style={{
                flex: 1,
                maxWidth: '400px',
                background: '#1a1a1a',
                overflow: 'auto',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
            }}>
                {/* Controls */}
                <div style={{
                    background: 'rgba(0,0,0,0.8)',
                    padding: '20px',
                    borderRadius: '8px',
                    color: 'white',
                    fontFamily: 'monospace',
                }}>
                    <h3 style={{ margin: '0 0 15px 0' }}>⚙️ Parameters</h3>
                    
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>
                            Extrusion Speed: {velocity} bp/step
                        </label>
                        <input
                            type="range"
                            min="100"
                            max="5000"
                            value={velocity}
                            onChange={(e) => setVelocity(Number(e.target.value))}
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>
                            Matrix Resolution: {resolution} bp
                        </label>
                        <input
                            type="range"
                            min="100"
                            max="5000"
                            step="100"
                            value={resolution}
                            onChange={(e) => setResolution(Number(e.target.value))}
                            style={{ width: '100%' }}
                        />
                    </div>

                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                            onClick={handleLoadSample}
                            style={{
                                flex: 1,
                                padding: '8px',
                                background: '#9b59b6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                            }}
                        >
                            🔄 Sample
                        </button>
                        <button
                            onClick={handleReset}
                            style={{
                                flex: 1,
                                padding: '8px',
                                background: '#7f8c8d',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                            }}
                        >
                            🗑 Reset
                        </button>
                    </div>
                </div>

                {/* BED Uploader */}
                <BEDUploader onSitesLoaded={handleSitesLoaded} />

                {/* Real-time Dashboard */}
                <LoopDashboard />

                {/* Contact Matrix */}
                {matrix && <ContactMatrixViewer matrix={matrix} />}

                {/* P(s) Curve */}
                {psCurve && <PSCurveViewer psCurve={psCurve} fit={fit} />}

                {/* AlphaGenome Validation */}
                <AlphaGenomeValidator 
                    engine={engine} 
                    apiKey={alphaGenomeApiKey || undefined}
                />
                
                {/* API Key Input */}
                <div style={{
                    background: 'rgba(0,0,0,0.8)',
                    padding: '15px',
                    borderRadius: '8px',
                    color: 'white',
                    fontFamily: 'monospace',
                    fontSize: '12px',
                }}>
                    <h4 style={{ margin: '0 0 10px 0' }}>🔑 AlphaGenome API Key</h4>
                    <input
                        type="password"
                        value={alphaGenomeApiKey}
                        onChange={(e) => setAlphaGenomeApiKey(e.target.value)}
                        placeholder="Enter API key..."
                        style={{
                            width: '100%',
                            padding: '8px',
                            background: '#222',
                            color: 'white',
                            border: '1px solid #444',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontFamily: 'monospace',
                        }}
                    />
                </div>
                
                {/* Legend */}
                <div style={{
                    background: 'rgba(0,0,0,0.8)',
                    padding: '15px',
                    borderRadius: '8px',
                    color: 'white',
                    fontFamily: 'monospace',
                    fontSize: '12px',
                }}>
                    <h4 style={{ margin: '0 0 10px 0' }}>📋 Legend</h4>
                    <div style={{ display: 'grid', gap: '5px' }}>
                        <div><span style={{ color: '#3498db' }}>▶</span> CTCF Forward (F)</div>
                        <div><span style={{ color: '#e74c3c' }}>◀</span> CTCF Reverse (R)</div>
                        <div><span style={{ color: '#00ff88' }}>╭╮</span> Formed Loop</div>
                        <div><span style={{ color: '#f39c12' }}>●</span> Active Cohesin</div>
                        <div><span style={{ color: '#7f8c8d' }}>●</span> Inactive Cohesin</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
