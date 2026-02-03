import { useState, useCallback } from 'react';
import { FileUp } from 'lucide-react';
import { CTCFSite } from '../../domain/models/genome';
import { loadCTCFFromBED, BEDParseResult } from '../../parsers/bed';
import { Panel } from './Panel';

interface BEDUploaderProps {
    onSitesLoaded: (sites: CTCFSite[]) => void;
}

export const BEDUploader = ({ onSitesLoaded }: BEDUploaderProps) => {
    const [isDragging, setIsDragging] = useState(false);
    const [result, setResult] = useState<BEDParseResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        const files = e.dataTransfer.files;
        if (files.length === 0) return;

        const file = files[0];
        if (!file.name.endsWith('.bed') && !file.name.endsWith('.txt')) {
            setError('Please upload a .bed or .txt file');
            return;
        }

        const reader = new FileReader();
        reader.onload = (event) => {
            const content = event.target?.result as string;
            try {
                const parseResult = loadCTCFFromBED(content);
                setResult(parseResult);
                onSitesLoaded(parseResult.sites);
            } catch (err) {
                setError(`Parse error: ${err instanceof Error ? err.message : 'Unknown error'}`);
            }
        };
        reader.readAsText(file);
    }, [onSitesLoaded]);

    const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setError(null);
        const reader = new FileReader();
        reader.onload = (event) => {
            const content = event.target?.result as string;
            try {
                const parseResult = loadCTCFFromBED(content);
                setResult(parseResult);
                onSitesLoaded(parseResult.sites);
            } catch (err) {
                setError(`Parse error: ${err instanceof Error ? err.message : 'Unknown error'}`);
            }
        };
        reader.readAsText(file);
    }, [onSitesLoaded]);

    return (
        <Panel title="Load CTCF Sites (BED)" className="font-mono">
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`rounded-[var(--radius-md)] p-6 text-center cursor-pointer transition-all border-2 border-dashed ${isDragging ? 'border-[var(--accent-live)] bg-[rgba(0,240,255,0.06)]' : 'border-[rgba(255,255,255,0.2)]'}`}
            >
                <input type="file" accept=".bed,.txt" onChange={handleFileInput} className="hidden" id="bed-file-input" />
                <label htmlFor="bed-file-input" className="cursor-pointer block">
                    <FileUp className="mx-auto mb-2 text-[var(--text-label)]" size={24} />
                    <div className="text-[var(--text-heading)] text-sm">Drop BED file or click</div>
                    <div className="text-[11px] text-[var(--text-label)] mt-1">chrom start end name score strand</div>
                </label>
            </div>

            {error && (
                <div className="mt-2 p-2 rounded-[var(--radius-sm)] bg-[rgba(231,76,60,0.15)] border border-[var(--accent-danger)] text-[var(--accent-danger)] text-xs">
                    {error}
                </div>
            )}

            {result && (
                <div className="mt-4 p-4 rounded-[var(--radius-sm)] bg-[rgba(0,240,255,0.06)] border border-[rgba(0,240,255,0.2)]">
                    <div className="text-[var(--accent-live)] font-semibold text-xs mb-2">Loaded</div>
                    <div className="text-xs text-[var(--text-label)] grid gap-1 tabular-nums">
                        <div>Parsed: <span className="text-[var(--text-heading)]">{result.parsed}</span> sites</div>
                        <div>Skipped: <span className="text-[var(--text-heading)]">{result.skipped}</span></div>
                        <div>Forward: {result.sites.filter(s => s.orientation === 'F').length}</div>
                        <div>Reverse: {result.sites.filter(s => s.orientation === 'R').length}</div>
                        {result.sites.length > 0 && (
                            <div className="text-[10px] mt-1">
                                Range: {Math.min(...result.sites.map(s => s.position)).toLocaleString()} - {Math.max(...result.sites.map(s => s.position)).toLocaleString()} bp
                            </div>
                        )}
                    </div>
                </div>
            )}
        </Panel>
    );
};
