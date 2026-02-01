import { useRef } from 'react';
import { Download, Upload, Copy } from 'lucide-react';
import { Panel } from './Panel';
import { Button } from './Button';
import { Tooltip } from './Tooltip';
import type { ArchcodeRun } from '../../domain/models/experiment';
import { validateImportedRun, formatSummaryMarkdown } from '../../utils/export-run';

interface ExperimentPanelProps {
    currentRun: ArchcodeRun | null;
    loadedRun: ArchcodeRun | null;
    isRunning: boolean;
    onExport: () => void;
    onImport: (run: ArchcodeRun) => void;
    onApplyParams: () => void;
    onClearLoaded: () => void;
}

export function ExperimentPanel({
    currentRun,
    loadedRun,
    isRunning,
    onExport,
    onImport,
    onApplyParams,
    onClearLoaded,
}: ExperimentPanelProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleImportClick = () => fileInputRef.current?.click();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = () => {
            try {
                const data = JSON.parse(reader.result as string);
                if (!validateImportedRun(data)) {
                    alert('Неверный формат файла. Ожидается ARCHCODE Run (schemaVersion 1.0).');
                    return;
                }
                onImport(data);
            } catch {
                alert('Ошибка чтения JSON.');
            }
        };
        reader.readAsText(file);
        e.target.value = '';
    };

    const handleCopySummary = async () => {
        const run = loadedRun ?? currentRun;
        if (!run) {
            alert('Нет данных для копирования. Запустите эксперимент или загрузите run.');
            return;
        }
        const text = formatSummaryMarkdown(run);
        await navigator.clipboard.writeText(text);
        // Краткая обратная связь — можно заменить на toast
        const btn = document.activeElement as HTMLButtonElement;
        if (btn) {
            const prev = btn.textContent;
            btn.textContent = 'Скопировано';
            setTimeout(() => { btn.textContent = prev; }, 1200);
        }
    };

    const runToExport = currentRun;
    const canExport = !!runToExport;

    return (
        <Panel title="Experiment">
            <div className="space-y-4 font-mono text-xs">
                <div className="flex flex-col gap-2">
                    <Tooltip
                        title="Export Run"
                        content="Сохраняет параметры, события и финальные результаты. Для воспроизводимости эксперимента."
                    >
                        <Button
                            variant="primary"
                            size="sm"
                            className="w-full justify-center gap-2"
                            onClick={onExport}
                            disabled={!canExport}
                        >
                            <Download size={14} />
                            Export Run
                        </Button>
                    </Tooltip>
                    {isRunning && canExport && (
                        <span className="text-[var(--accent-warning)] text-[10px]">
                            Симуляция идёт — экспортируется текущее состояние.
                        </span>
                    )}

                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".json,application/json"
                        className="hidden"
                        onChange={handleFileChange}
                    />
                    <Tooltip
                        title="Import Run"
                        content="Загружает прошлый запуск, позволяет применить параметры и сравнить."
                    >
                        <Button
                            variant="muted"
                            size="sm"
                            className="w-full justify-center gap-2"
                            onClick={handleImportClick}
                        >
                            <Upload size={14} />
                            Import Run
                        </Button>
                    </Tooltip>

                    <Button
                        variant="muted"
                        size="sm"
                        className="w-full justify-center gap-2"
                        onClick={handleCopySummary}
                        disabled={!loadedRun && !currentRun}
                    >
                        <Copy size={14} />
                        Copy Summary
                    </Button>
                </div>

                {loadedRun && (
                    <div className="rounded-lg border border-[rgba(255,255,255,0.1)] bg-black/20 p-3 space-y-2">
                        <div className="text-[var(--text-heading)] font-semibold">
                            Loaded run: {loadedRun.run.id.slice(0, 12)}
                        </div>
                        <div className="text-[var(--text-label)] text-[10px]">
                            {loadedRun.run.createdAt.slice(0, 10)} · {loadedRun.run.mode} · {loadedRun.results.loopsFormed} loops
                        </div>
                        <div className="flex gap-2 flex-wrap">
                            <Button variant="primary" size="sm" onClick={onApplyParams}>
                                Apply Params
                            </Button>
                            <Button variant="muted" size="sm" onClick={onClearLoaded}>
                                Clear
                            </Button>
                        </div>
                    </div>
                )}

                {/* Summary (View Summary) — показываем для loaded или current */}
                {(loadedRun ?? currentRun) && (
                    <RunSummary run={loadedRun ?? currentRun!} />
                )}
            </div>
        </Panel>
    );
}

function RunSummary({ run }: { run: ArchcodeRun }) {
    const r = run.run;
    const res = run.results;
    const interpretation =
        res.convergentPairs === 0
            ? 'Устойчивые петли не сформировались при данных условиях.'
            : `Сформировано устойчивых петель: ${res.convergentPairs}`;

    return (
        <div className="rounded-lg border border-[rgba(255,255,255,0.1)] bg-black/20 p-3 space-y-2 text-[var(--text-label)]">
            <div className="font-semibold text-[var(--text-heading)] text-[11px]">Run Summary</div>
            <div className="grid gap-1 text-[10px]">
                <div>ID: {r.id.slice(0, 12)} · {r.createdAt.slice(0, 16)}</div>
                <div>Mode: {r.mode} · Status: {r.status}{r.stopReason ? ` (${r.stopReason})` : ''}</div>
                <div>Steps: {res.steps} · Loops (events): {res.loopsFormed}{res.uniqueLoopsFormed != null ? ` · Unique pairs: ${res.uniqueLoopsFormed}` : ''} · Convergent: {res.convergentPairs}</div>
            </div>
            {res.stablePairs.length > 0 && (
                <div className="text-[10px]">
                    <span className="text-[var(--text-heading)]">Top stable pairs:</span>
                    <ul className="list-disc pl-4 mt-0.5">
                        {res.stablePairs.slice(0, 3).map((p, i) => (
                            <li key={i}>{p.left.toLocaleString()} – {p.right.toLocaleString()} bp{p.sizeBp != null ? ` (${(p.sizeBp / 1000).toFixed(1)} kb)` : ''}</li>
                        ))}
                    </ul>
                </div>
            )}
            <div className="text-[10px] text-[var(--accent-live)] pt-1 border-t border-[rgba(255,255,255,0.1)]">
                {interpretation}
            </div>
        </div>
    );
}
