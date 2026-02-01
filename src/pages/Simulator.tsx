import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Settings, Database, LayoutGrid, Dna, List, FlaskConical } from 'lucide-react';
import { GenomeViewer } from '../components/3d/GenomeViewer';
import { SimulationViewer } from '../components/3d/SimulationViewer';
import { DNAHelixViewer } from '../components/3d/DNAHelix';
import { BEDUploader } from '../components/ui/BEDUploader';
import { ENCODEDownloader } from '../components/ui/ENCODEDownloader';
import { ContactMatrixViewer, PSCurveViewer } from '../components/ui/ContactMatrixViewer';
import { AlphaGenomeValidator } from '../components/ui/AlphaGenomeValidator';
import { DebugOverlay } from '../components/ui/DebugOverlay';
import { LoopDashboard } from '../components/dashboard/LoopDashboard';
import { Button } from '../components/ui/Button';
import { Panel } from '../components/ui/Panel';
import { Input } from '../components/ui/Input';
import { Slider } from '../components/ui/Slider';
import { RunButton } from '../components/ui/RunButton';
import { Tooltip } from '../components/ui/Tooltip';
import { LoopExtrusionEngine, loopsToContactMatrix, computePSCurve, fitPSPowerLaw } from '../engines/LoopExtrusionEngine';
import { CTCFSite, createCTCFSite, Loop } from '../domain/models/genome';
import { VISUALIZATION_CONFIG } from '../domain/constants/biophysics';
import { generateSampleBED } from '../parsers/bed';
import { createRunId } from '../domain/models/experiment';
import type { ArchcodeRun } from '../domain/models/experiment';
import { downloadJson, exportRunFilename, buildRunInitial } from '../utils/export-run';
import { ExperimentPanel } from '../components/ui/ExperimentPanel';

type SidebarTab = 'params' | 'data' | 'matrix' | 'alphagenome' | 'legend' | 'experiment';

export function Simulator() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [sidebarTab, setSidebarTab] = useState<SidebarTab>('params');
    const [viewMode, setViewMode] = useState<'tube' | 'linear' | 'helix'>('tube');
    const [helixBasePairs, setHelixBasePairs] = useState(24);
    const [helixTwist, setHelixTwist] = useState((2 * Math.PI) / 10.5);
    const [helixScale, setHelixScale] = useState(1);
    const [ctcfSites, setCTCFSites] = useState<CTCFSite[]>([]);
    const [genomeLength, setGenomeLength] = useState(100000);
    const [isRunning, setIsRunning] = useState(false);
    const [resolution, setResolution] = useState(1000);
    const [velocity, setVelocity] = useState(1000);
    const [alphaGenomeApiKey, setAlphaGenomeApiKey] = useState(import.meta.env.VITE_ALPHAGENOME_API_KEY || '');
    const [stepCount, setStepCount] = useState(0);
    const [pulseLoops, setPulseLoops] = useState<Loop[]>([]);
    const prevLoopsLengthRef = useRef(0);
    const pulseTimeoutIdRef = useRef<number | null>(null);
    const [currentRun, setCurrentRun] = useState<ArchcodeRun | null>(null);
    const [loadedRun, setLoadedRun] = useState<ArchcodeRun | null>(null);

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

    // Детекция события loop_formed: новые петли → краткий импульс в 3D (только при isRunning; при Reset/Stop — без импульсов из прошлого).
    // Предохранитель: один таймер сброса — при частых loop_formed очищаем старый, ставим новый, чтобы не сбросить «не тот» импульс.
    const loopPulseMs = VISUALIZATION_CONFIG.LOOP_PULSE_MS;
    useEffect(() => {
        const prev = prevLoopsLengthRef.current;
        if (!isRunning) {
            if (pulseTimeoutIdRef.current !== null) {
                clearTimeout(pulseTimeoutIdRef.current);
                pulseTimeoutIdRef.current = null;
            }
            setPulseLoops([]);
            prevLoopsLengthRef.current = loops.length;
            return;
        }
        if (loops.length > prev) {
            const newlyFormed = loops.slice(prev);
            setPulseLoops(newlyFormed);
            setCurrentRun(prevRun => {
                if (!prevRun || !isRunning) return prevRun;
                const startMs = new Date(prevRun.run.createdAt).getTime();
                // step — источник истины для replay; t — wall-clock ms с начала run (вспомогательный, допускается дрейф)
                const newEvents = newlyFormed.map(loop => ({
                    t: Date.now() - startMs,
                    step: stepCount,
                    type: 'loop_formed' as const,
                    payload: { left: loop.leftAnchor, right: loop.rightAnchor, sizeBp: loop.rightAnchor - loop.leftAnchor },
                }));
                return { ...prevRun, events: [...prevRun.events, ...newEvents] };
            });
            if (pulseTimeoutIdRef.current !== null) {
                clearTimeout(pulseTimeoutIdRef.current);
            }
            const t = window.setTimeout(() => {
                setPulseLoops([]);
                pulseTimeoutIdRef.current = null;
            }, loopPulseMs);
            pulseTimeoutIdRef.current = t;
            prevLoopsLengthRef.current = loops.length;
            return () => {
                clearTimeout(t);
                if (pulseTimeoutIdRef.current === t) pulseTimeoutIdRef.current = null;
            };
        }
        prevLoopsLengthRef.current = loops.length;
    }, [loops, stepCount, isRunning, loopPulseMs]);

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
        if (pulseTimeoutIdRef.current !== null) {
            clearTimeout(pulseTimeoutIdRef.current);
            pulseTimeoutIdRef.current = null;
        }
        engine.reset();
        setStepCount(0);
        setPulseLoops([]);
        prevLoopsLengthRef.current = 0;
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
        const runId = createRunId();
        // Extract chromosome from first CTCF site or use default
        const chromosome = ctcfSites[0]?.chrom ?? 'chr1';
        setCurrentRun(buildRunInitial({
            runId,
            mode: viewMode,
            extrusionSpeed: velocity,
            matrixResolution: resolution,
            genomeLengthBp: genomeLength,
            ctcfSites: ctcfSites.map(s => ({ position: s.position, orientation: s.orientation, chrom: s.chrom })),
            seed: 42,
            chromosome,
        }));
        setIsRunning(true);
        engine.start();
    }, [engine, viewMode, velocity, resolution, genomeLength, ctcfSites]);

    const handlePauseSimulation = useCallback(() => {
        setIsRunning(false);
        engine.pause();
    }, [engine]);

    const handleStopSimulation = useCallback(() => {
        if (pulseTimeoutIdRef.current !== null) {
            clearTimeout(pulseTimeoutIdRef.current);
            pulseTimeoutIdRef.current = null;
        }
        const finalLoops = engine.getLoops();
        const finalStep = engine.getStepCount();
        setCurrentRun(prev => {
            if (!prev) return prev;
            const started = new Date(prev.run.createdAt).getTime();
            const ended = Date.now();
            const stablePairs = finalLoops.map(l => ({
                left: l.leftAnchor,
                right: l.rightAnchor,
                type: 'F-R' as const,
                sizeBp: l.rightAnchor - l.leftAnchor,
            }));
            return {
                ...prev,
                run: {
                    ...prev.run,
                    endedAt: new Date(ended).toISOString(),
                    durationMs: ended - started,
                    status: 'stopped',
                    stopReason: 'user_stop',
                },
                results: {
                    ...prev.results,
                    steps: finalStep,
                    loopsFormed: prev.events.filter(e => e.type === 'loop_formed').length,
                    uniqueLoopsFormed: (() => {
                        const keys = new Set(
                            prev.events
                                .filter(e => e.type === 'loop_formed' && e.payload != null)
                                .map(e => `${(e.payload as { left: number; right: number }).left}-${(e.payload as { left: number; right: number }).right}`)
                        );
                        return keys.size;
                    })(),
                    convergentPairs: finalLoops.length,
                    stablePairs,
                    lastState: { activeCohesin: 0 },
                },
            };
        });
        setIsRunning(false);
        engine.reset();
        setStepCount(0);
        setPulseLoops([]);
        prevLoopsLengthRef.current = 0;
    }, [engine]);

    const handleExportRun = useCallback(() => {
        const run = currentRun;
        if (!run) return;
        const toExport: ArchcodeRun = isRunning
            ? (() => {
                const loopEvents = run.events.filter(e => e.type === 'loop_formed');
                const uniqueKeys = new Set(
                    loopEvents
                        .filter(e => e.payload != null)
                        .map(e => `${(e.payload as { left: number; right: number }).left}-${(e.payload as { left: number; right: number }).right}`)
                );
                return {
                    ...run,
                    results: {
                        ...run.results,
                        steps: engine.getStepCount(),
                        loopsFormed: loopEvents.length,
                        uniqueLoopsFormed: uniqueKeys.size,
                        convergentPairs: engine.getLoops().length,
                        stablePairs: engine.getLoops().map(l => ({
                            left: l.leftAnchor,
                            right: l.rightAnchor,
                            type: 'F-R',
                            sizeBp: l.rightAnchor - l.leftAnchor,
                        })),
                    },
                };
            })()
            : run;
        downloadJson(toExport, exportRunFilename(toExport));
    }, [currentRun, isRunning, engine]);

    const handleApplyParamsFromLoaded = useCallback(() => {
        const run = loadedRun;
        if (!run) return;
        setVelocity(run.params.extrusionSpeed);
        setResolution(run.params.matrixResolution);
        setGenomeLength(run.params.genomeLengthBp);
        setViewMode(run.run.mode);
        // Preserve original chromosome from imported run
        const chromosome = run.model.chromosome ?? run.model.ctcfSites[0]?.chrom ?? 'chr1';
        setCTCFSites(run.model.ctcfSites.map(s => createCTCFSite(s.chrom ?? chromosome, s.pos, s.orient, 1.0)));
        setStepCount(0);
    }, [loadedRun]);

    useEffect(() => {
        handleLoadSample();
    }, []);

    return (
        <div id="genome-viewer" className="relative w-screen h-screen overflow-hidden" style={{ background: 'var(--bg-app)' }}>
            {/* Fullscreen 3D */}
            <div className="absolute inset-0">
                {viewMode === 'tube' && <GenomeViewer engine={engine} stepCount={stepCount} pulseLoops={pulseLoops} />}
                {viewMode === 'linear' && <SimulationViewer engine={engine} pulseLoops={pulseLoops} />}
                {viewMode === 'helix' && (
                    <DNAHelixViewer
                        basePairs={helixBasePairs}
                        twistPerBasePair={helixTwist}
                        risePerBP={0.34}
                        radius={1.2}
                        scale={helixScale}
                    />
                )}
            </div>

            <DebugOverlay engine={engine} ctcfSites={ctcfSites} isRunning={isRunning} />

            {/* Overlay: stats */}
            <motion.div
                className="panel-glass absolute top-5 left-5 p-4 rounded-lg font-mono text-[13px] z-10"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
            >
                <h3 className="m-0 mb-2.5 text-sm font-semibold text-[var(--text-heading)]">ARCHCODE v0.3.1</h3>
                <div className="text-[var(--text-label)]">CTCF Sites: <span className="tabular-nums text-[var(--text-heading)]">{ctcfSites.length}</span></div>
                <Tooltip
                    title="Образовались петли"
                    content={
                        <>
                            Количество событий временной стабилизации хроматиновых петель за время симуляции.
                            <br /><br />
                            ⚠️ Не означает количество одновременно существующих петель.
                        </>
                    }
                >
                    <div className="text-[var(--text-label)]">Loops: <span className="tabular-nums text-[var(--accent-live)]">{loops.length}</span></div>
                </Tooltip>
                <div className="text-[var(--text-label)]">Cohesin: <span className="tabular-nums text-[var(--accent-live)]">{activeCohesins}</span></div>
                <Tooltip
                    title="Шаг симуляции"
                    content="Внутренний дискретный шаг модели экструзии. Используется для пошагового анализа (STEP)."
                >
                    <div className="text-[var(--text-label)]">Step: <span className="tabular-nums text-[var(--text-heading)]">{engine.getStepCount()}</span></div>
                </Tooltip>
                <div className="mt-2.5 text-[11px] text-[var(--text-label)]">Genome: {genomeLength.toLocaleString()} bp</div>
                {/* Мини-статус состояния */}
                <div className="mt-2 text-[11px] text-[var(--text-label)] border-t border-[rgba(255,255,255,0.1)] pt-2">
                    {isRunning && activeCohesins > 0 && <span className="text-[var(--accent-live)]">🟢 Активная экструзия</span>}
                    {isRunning && activeCohesins === 0 && <span className="text-[var(--accent-warning)]">🟡 Стабилизация</span>}
                    {!isRunning && (
                        <Tooltip
                            title="Завершение симуляции"
                            content="Модель достигла состояния без допустимых новых переходов. Это считается корректным завершением эксперимента."
                        >
                            <span className="text-[var(--accent-muted)] cursor-help">🔵 Плато достигнуто — новых петель нет</span>
                        </Tooltip>
                    )}
                </div>
            </motion.div>

            {/* Overlay: view mode toggle */}
            <div className="panel-glass absolute top-5 right-5 flex gap-0.5 rounded-lg overflow-hidden font-mono text-xs z-10">
                {(['tube', 'linear', 'helix'] as const).map((mode) => (
                    <button
                        key={mode}
                        type="button"
                        onClick={() => setViewMode(mode)}
                        className="px-3 py-2 capitalize"
                        style={{
                            background: viewMode === mode ? 'var(--accent-live)' : 'transparent',
                            color: viewMode === mode ? '#050505' : 'var(--text-label)',
                        }}
                    >
                        {mode}
                    </button>
                ))}
            </div>

            {/* Overlay: helix controls (helix mode only) */}
            <AnimatePresence>
                {viewMode === 'helix' && (
                    <motion.div
                        className="panel-glass absolute bottom-24 left-5 right-5 md:left-auto md:right-[420px] md:w-64 p-4 rounded-lg font-mono text-xs z-10"
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 8 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="mb-3 font-semibold text-[var(--text-heading)]">DNA Helix</div>
                        <div className="space-y-3">
                            <Slider label="Base pairs" min={8} max={48} value={helixBasePairs} onValueChange={setHelixBasePairs} valueLabel={String(helixBasePairs)} />
                            <Slider label="Twist" min={0.2} max={1.2} step={0.01} value={helixTwist / ((2 * Math.PI) / 10.5)} onValueChange={(v) => setHelixTwist(v * (2 * Math.PI) / 10.5)} valueLabel={(helixTwist * (10.5 / (2 * Math.PI))).toFixed(2)} />
                            <Slider label="Scale" min={0.5} max={3} step={0.1} value={helixScale} onValueChange={setHelixScale} valueLabel={helixScale.toFixed(2)} />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Overlay: playback */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2.5 z-10">
                <RunButton action="run" isActive={isRunning} disabled={isRunning} onClick={handleRunSimulation} size="lg" />
                <RunButton action="pause" disabled={!isRunning} onClick={handlePauseSimulation} size="lg" />
                <RunButton action="stop" onClick={handleStopSimulation} size="lg" />
                <Button variant="primary" size="lg" onClick={() => { engine.step(); setStepCount(s => s + 1); }} disabled={isRunning}>
                    Step
                </Button>
            </div>

            {/* Sidebar collapse toggle — desktop only */}
            <motion.button
                type="button"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="hidden md:flex absolute top-1/2 -translate-y-1/2 w-8 h-16 items-center justify-center rounded-l border border-r-0 z-20 panel-glass"
                style={{
                    right: sidebarOpen ? 400 : 0,
                    color: 'var(--text-label)',
                }}
                animate={{ right: sidebarOpen ? 400 : 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
                {sidebarOpen ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
            </motion.button>

            {/* Sidebar: floating glass panel */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        className="absolute top-0 right-0 bottom-0 w-full md:w-[400px] md:max-w-[90vw] flex flex-col z-10 md:pt-4 md:pb-4 md:pr-4"
                        initial={{ x: 400 }}
                        animate={{ x: 0 }}
                        exit={{ x: 400 }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                    >
                        <div className="panel-glass flex-1 min-h-0 flex flex-col overflow-hidden rounded-lg">
                            <div className="flex border-b border-[rgba(255,255,255,0.1)] flex-shrink-0 font-mono text-xs">
                                {[
                                    { id: 'params' as const, label: 'Params', Icon: Settings },
                                    { id: 'data' as const, label: 'Data', Icon: Database },
                                    { id: 'matrix' as const, label: 'Matrix', Icon: LayoutGrid },
                                    { id: 'alphagenome' as const, label: 'AlphaGenome', Icon: Dna },
                                    { id: 'legend' as const, label: 'Legend', Icon: List },
                                    { id: 'experiment' as const, label: 'Experiment', Icon: FlaskConical },
                                ].map(({ id, label, Icon }) => (
                                    <button
                                        key={id}
                                        type="button"
                                        onClick={() => setSidebarTab(id)}
                                        className="flex items-center gap-1.5 px-3 py-2 border-b-2 -mb-px transition-colors"
                                        style={{
                                            borderColor: sidebarTab === id ? 'var(--accent-live)' : 'transparent',
                                            color: sidebarTab === id ? 'var(--accent-live)' : 'var(--text-label)',
                                        }}
                                    >
                                        <Icon size={14} />
                                        {label}
                                    </button>
                                ))}
                            </div>
                            <div className="flex-1 overflow-auto p-5 flex flex-col gap-5">
                                {sidebarTab === 'params' && (
                                    <Panel title="Parameters">
                                        <div className="space-y-4">
                                            <Slider label="Extrusion Speed" min={100} max={5000} value={velocity} onValueChange={setVelocity} valueLabel={`${velocity} bp/step`} />
                                            <Slider label="Matrix Resolution" min={100} max={5000} step={100} value={resolution} onValueChange={setResolution} valueLabel={`${resolution} bp`} />
                                            <div className="flex gap-2.5 pt-2">
                                                <Button variant="purple" size="sm" className="flex-1" onClick={handleLoadSample}>Sample</Button>
                                                <Button variant="muted" size="sm" className="flex-1" onClick={handleReset}>Reset</Button>
                                            </div>
                                        </div>
                                    </Panel>
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
                                        <AlphaGenomeValidator engine={engine} apiKey={alphaGenomeApiKey || undefined} />
                                        <Panel title="AlphaGenome API Key">
                                            <Input type="password" value={alphaGenomeApiKey} onChange={(e) => setAlphaGenomeApiKey(e.target.value)} placeholder="Enter API key..." />
                                        </Panel>
                                    </>
                                )}
                                {sidebarTab === 'legend' && (
                                    <Panel title="Legend">
                                        <div className="grid gap-1.5 text-xs text-[var(--text-label)]">
                                            <div><span className="text-[var(--accent-live)]">F</span> CTCF Forward</div>
                                            <div><span className="text-[var(--accent-danger)]">R</span> CTCF Reverse</div>
                                            <div><span className="text-[var(--accent-live)]">Loop</span> Formed</div>
                                            <div><span className="text-[var(--accent-live)]">●</span> Active Cohesin</div>
                                            <div><span className="text-[var(--accent-muted)]">●</span> Inactive Cohesin</div>
                                        </div>
                                    </Panel>
                                )}
                                {sidebarTab === 'experiment' && (
                                    <ExperimentPanel
                                        currentRun={currentRun}
                                        loadedRun={loadedRun}
                                        isRunning={isRunning}
                                        onExport={handleExportRun}
                                        onImport={setLoadedRun}
                                        onApplyParams={handleApplyParamsFromLoaded}
                                        onClearLoaded={() => setLoadedRun(null)}
                                    />
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
