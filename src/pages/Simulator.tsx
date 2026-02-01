import { useState, useCallback, useMemo, useEffect } from 'react';
import { GenomeViewer } from '../components/3d/GenomeViewer';
import { SimulationViewer } from '../components/3d/SimulationViewer';
import { BEDUploader } from '../components/ui/BEDUploader';
import { ENCODEDownloader } from '../components/ui/ENCODEDownloader';
import { ContactMatrixViewer, PSCurveViewer } from '../components/ui/ContactMatrixViewer';
import { AlphaGenomeValidator } from '../components/ui/AlphaGenomeValidator';
import { DebugOverlay } from '../components/ui/DebugOverlay';
import { LoopDashboard } from '../components/dashboard/LoopDashboard';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { LoopExtrusionEngine, loopsToContactMatrix, computePSCurve, fitPSPowerLaw } from '../engines/LoopExtrusionEngine';
import { CTCFSite, createCTCFSite } from '../domain/models/genome';
import { generateSampleBED } from '../parsers/bed';

type SidebarTab = 'params' | 'data' | 'matrix' | 'alphagenome' | 'legend';

export function Simulator() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [sidebarTab, setSidebarTab] = useState<SidebarTab>('params');
    const [viewMode, setViewMode] = useState<'tube' | 'linear'>('tube');
    const [ctcfSites, setCTCFSites] = useState<CTCFSite[]>([]);
    const [genomeLength, setGenomeLength] = useState(100000);
    const [isRunning, setIsRunning] = useState(false);
    const [resolution, setResolution] = useState(1000);
    const [velocity, setVelocity] = useState(1000);
    const [alphaGenomeApiKey, setAlphaGenomeApiKey] = useState(import.meta.env.VITE_ALPHAGENOME_API_KEY || '');
    const [stepCount, setStepCount] = useState(0);

    const engine = useMemo(() => {
        return new LoopExtrusionEngine({
            genomeLength,
            ctcfSites,
            cohesinLoadPosition: Math.floor(genomeLength / 2),
            velocity,
            seed: 42,
        });
    }, [genomeLength, ctcfSites, velocity]);

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

    const handleSitesLoaded = useCallback((sites: CTCFSite[], _cellLine?: string) => {
        setCTCFSites(sites);
        if (sites.length > 0) {
            const maxPos = Math.max(...sites.map(s => s.position));
            setGenomeLength(Math.max(100000, maxPos * 1.2));
        }
    }, []);

    const handleLoadSample = useCallback(() => {
        const sampleBED = generateSampleBED('chr11', 6);
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

        const minPos = Math.min(...rawSites.map(s => s.pos));
        const offset = minPos - 20000;

        const sites = rawSites.map(s => createCTCFSite(
            'chr11',
            s.pos - offset,
            s.strand === '+' ? 'F' : 'R',
            1.0
        ));

        setCTCFSites(sites);
        setGenomeLength(240000);
    }, []);

    const handleReset = useCallback(() => {
        setCTCFSites([]);
        setIsRunning(false);
        engine.reset();
    }, [engine]);

    useEffect(() => {
        let interval: number;
        if (isRunning) {
            interval = window.setInterval(() => {
                for (let i = 0; i < 10; i++) {
                    engine.step();
                }
                setStepCount(engine.getStepCount());
            }, 50);
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

    useEffect(() => {
        handleLoadSample();
    }, []);

    return (
        <div
            className="relative w-screen h-screen flex flex-col md:flex-row"
            style={{ background: 'var(--bg-app)' }}
        >
            <div className="flex-[2] relative min-h-[300px] md:min-h-[500px] h-full w-full md:w-auto">
                {viewMode === 'tube' ? (
                    <GenomeViewer engine={engine} />
                ) : (
                    <SimulationViewer engine={engine} />
                )}
                {/* 3D view mode toggle */}
                <div className="absolute top-5 right-5 flex gap-1 rounded-lg overflow-hidden font-mono text-xs" style={{ background: 'var(--bg-panel-elevated)' }}>
                    <button
                        type="button"
                        onClick={() => setViewMode('tube')}
                        className="px-3 py-2"
                        style={{
                            background: viewMode === 'tube' ? 'var(--accent-primary)' : 'transparent',
                            color: viewMode === 'tube' ? '#fff' : 'var(--text-muted)',
                        }}
                    >
                        Tube
                    </button>
                    <button
                        type="button"
                        onClick={() => setViewMode('linear')}
                        className="px-3 py-2"
                        style={{
                            background: viewMode === 'linear' ? 'var(--accent-primary)' : 'transparent',
                            color: viewMode === 'linear' ? '#fff' : 'var(--text-muted)',
                        }}
                    >
                        Linear
                    </button>
                </div>
                <DebugOverlay engine={engine} ctcfSites={ctcfSites} isRunning={isRunning} />
                <div
                    className="absolute top-5 left-5 p-4 rounded-lg font-mono text-[13px] text-[var(--text-primary)]"
                    style={{ background: 'var(--bg-panel-elevated)', borderRadius: 'var(--radius-md)' }}
                >
                    <h3 className="m-0 mb-2.5 text-sm font-semibold">🔬 ARCHCODE v0.3.1</h3>
                    <div>CTCF Sites: <strong>{ctcfSites.length}</strong></div>
                    <div>Loops Formed: <strong style={{ color: 'var(--accent-success)' }}>{loops.length}</strong></div>
                    <div>Active Cohesin: <strong style={{ color: 'var(--accent-warning)' }}>{activeCohesins}</strong></div>
                    <div>Step: <strong>{engine.getStepCount()}</strong></div>
                    <div className="mt-2.5 text-[11px]" style={{ color: 'var(--text-muted)' }}>
                        Genome: {genomeLength.toLocaleString()} bp
                    </div>
                </div>

                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2.5">
                    <Button variant="success" size="lg" onClick={handleRunSimulation} disabled={isRunning}>
                        ▶ Run
                    </Button>
                    <Button variant="danger" size="lg" onClick={handlePauseSimulation} disabled={!isRunning}>
                        ⏸ Pause
                    </Button>
                    <Button variant="muted" size="lg" onClick={handleStopSimulation}>
                        ⏹ Stop
                    </Button>
                    <Button variant="primary" size="lg" onClick={() => { engine.step(); setStepCount(s => s + 1); }} disabled={isRunning}>
                        ⏭ Step
                    </Button>
                </div>

                {/* Sidebar collapse toggle — desktop only (md+), right edge */}
                <button
                    type="button"
                    onClick={() => setSidebarOpen(!sidebarOpen)}
                    className="hidden md:flex absolute top-1/2 -translate-y-1/2 w-8 h-16 items-center justify-center rounded-l text-sm font-mono border border-r-0 z-10"
                    style={{
                        right: sidebarOpen ? 400 : 0,
                        background: 'var(--bg-panel)',
                        borderColor: 'var(--border-panel)',
                        color: 'var(--text-muted)',
                        transition: 'right 0.3s ease-out',
                    }}
                    aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
                >
                    {sidebarOpen ? '◀' : '▶'}
                </button>
            </div>

            {/* Sidebar: full width below 768px, collapsible right panel on md+ */}
            <div
                className={`
                    flex flex-shrink-0 overflow-hidden relative
                    w-full max-h-[45vh] md:max-h-none md:w-auto
                    transition-[max-width] duration-300 ease-out
                    ${sidebarOpen ? 'md:max-w-[400px] md:min-w-[320px]' : 'md:max-w-0 md:min-w-0'}
                `}
                style={{ background: 'var(--bg-panel)' }}
            >
                <div className="w-full md:w-[400px] md:max-w-[400px] h-full min-h-0 flex flex-col overflow-hidden">
                    {/* Tabs */}
                    <div className="flex border-b flex-shrink-0 font-mono text-xs" style={{ borderColor: 'var(--border-panel)' }}>
                        {([
                            { id: 'params' as const, label: 'Params' },
                            { id: 'data' as const, label: 'Data' },
                            { id: 'matrix' as const, label: 'Matrix' },
                            { id: 'alphagenome' as const, label: 'AlphaGenome' },
                            { id: 'legend' as const, label: 'Legend' },
                        ]).map(({ id, label }) => (
                            <button
                                key={id}
                                type="button"
                                onClick={() => setSidebarTab(id)}
                                className="px-3 py-2 border-b-2 -mb-px transition-colors"
                                style={{
                                    borderColor: sidebarTab === id ? 'var(--accent-primary)' : 'transparent',
                                    color: sidebarTab === id ? 'var(--accent-primary)' : 'var(--text-muted)',
                                }}
                            >
                                {label}
                            </button>
                        ))}
                    </div>
                    <div className="flex-1 overflow-auto p-5 flex flex-col gap-5">
                        {sidebarTab === 'params' && (
                            <Card title="⚙️ Parameters">
                                <div className="mb-4">
                                    <label className="block mb-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                                        Extrusion Speed: {velocity} bp/step
                                    </label>
                                    <input
                                        type="range"
                                        min="100"
                                        max="5000"
                                        value={velocity}
                                        onChange={(e) => setVelocity(Number(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                                <div className="mb-4">
                                    <label className="block mb-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                                        Matrix Resolution: {resolution} bp
                                    </label>
                                    <input
                                        type="range"
                                        min="100"
                                        max="5000"
                                        step="100"
                                        value={resolution}
                                        onChange={(e) => setResolution(Number(e.target.value))}
                                        className="w-full"
                                    />
                                </div>
                                <div className="flex gap-2.5">
                                    <Button variant="purple" size="sm" className="flex-1" onClick={handleLoadSample}>
                                        🔄 Sample
                                    </Button>
                                    <Button variant="muted" size="sm" className="flex-1" onClick={handleReset}>
                                        🗑 Reset
                                    </Button>
                                </div>
                            </Card>
                        )}
                        {sidebarTab === 'data' && (
                            <>
                                <BEDUploader onSitesLoaded={handleSitesLoaded} />
                                <ENCODEDownloader onSitesLoaded={(sites, cellLine) => handleSitesLoaded(sites, cellLine)} />
                                <LoopDashboard loops={loops} isRunning={isRunning} stepCount={engine.getStepCount()} />
                            </>
                        )}
                        {sidebarTab === 'matrix' && (
                            <>
                                {matrix && <ContactMatrixViewer matrix={matrix} />}
                                {psCurve && <PSCurveViewer psCurve={psCurve} fit={fit} />}
                            </>
                        )}
                        {sidebarTab === 'alphagenome' && (
                            <>
                                <AlphaGenomeValidator
                                    engine={engine}
                                    apiKey={alphaGenomeApiKey || undefined}
                                />
                                <Card title="🔑 AlphaGenome API Key">
                                    <Input
                                        type="password"
                                        value={alphaGenomeApiKey}
                                        onChange={(e) => setAlphaGenomeApiKey(e.target.value)}
                                        placeholder="Enter API key..."
                                    />
                                </Card>
                            </>
                        )}
                        {sidebarTab === 'legend' && (
                            <Card title="📋 Legend">
                                <div className="grid gap-1.5 text-xs">
                                    <div><span style={{ color: 'var(--accent-primary)' }}>▶</span> CTCF Forward (F)</div>
                                    <div><span style={{ color: 'var(--accent-danger)' }}>◀</span> CTCF Reverse (R)</div>
                                    <div><span style={{ color: 'var(--accent-success)' }}>╭╮</span> Formed Loop</div>
                                    <div><span style={{ color: 'var(--accent-warning)' }}>●</span> Active Cohesin</div>
                                    <div><span style={{ color: 'var(--accent-muted)' }}>●</span> Inactive Cohesin</div>
                                </div>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
