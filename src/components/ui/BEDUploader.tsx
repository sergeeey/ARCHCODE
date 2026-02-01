import { useState, useCallback } from 'react';
import { CTCFSite } from '../../domain/models/genome';
import { loadCTCFFromBED, BEDParseResult } from '../../parsers/bed';

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
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
        }}>
            <h3 style={{ margin: '0 0 15px 0' }}>📁 Load CTCF Sites (BED)</h3>
            
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{
                    border: `2px dashed ${isDragging ? '#2ecc71' : '#555'}`,
                    borderRadius: '8px',
                    padding: '30px',
                    textAlign: 'center',
                    background: isDragging ? 'rgba(46, 204, 113, 0.1)' : 'transparent',
                    transition: 'all 0.2s',
                    cursor: 'pointer',
                }}
            >
                <input
                    type="file"
                    accept=".bed,.txt"
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                    id="bed-file-input"
                />
                <label htmlFor="bed-file-input" style={{ cursor: 'pointer' }}>
                    <div style={{ fontSize: '24px', marginBottom: '10px' }}>📤</div>
                    <div>Drop BED file here or click to select</div>
                    <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>
                        Format: chrom start end name score strand
                    </div>
                </label>
            </div>

            {error && (
                <div style={{
                    marginTop: '10px',
                    padding: '10px',
                    background: 'rgba(231, 76, 60, 0.2)',
                    border: '1px solid #e74c3c',
                    borderRadius: '4px',
                    color: '#e74c3c',
                    fontSize: '12px',
                }}>
                    ❌ {error}
                </div>
            )}

            {result && (
                <div style={{
                    marginTop: '15px',
                    padding: '15px',
                    background: 'rgba(46, 204, 113, 0.1)',
                    border: '1px solid #2ecc71',
                    borderRadius: '4px',
                }}>
                    <div style={{ color: '#2ecc71', fontWeight: 'bold', marginBottom: '10px' }}>
                        ✅ Loaded successfully
                    </div>
                    <div style={{ fontSize: '13px', display: 'grid', gap: '5px' }}>
                        <div>📊 Parsed: <strong>{result.parsed}</strong> sites</div>
                        <div>⏭️ Skipped: <strong>{result.skipped}</strong> lines</div>
                        <div style={{ marginTop: '5px' }}>
                            <strong>Forward (&gt;):</strong>{' '}
                            {result.sites.filter(s => s.orientation === 'F').length}
                        </div>
                        <div>
                            <strong>Reverse (&lt;):</strong>{' '}
                            {result.sites.filter(s => s.orientation === 'R').length}
                        </div>
                        {result.sites.length > 0 && (
                            <div style={{ marginTop: '5px', fontSize: '11px', color: '#888' }}>
                                Range: {Math.min(...result.sites.map(s => s.position)).toLocaleString()} - {' '}
                                {Math.max(...result.sites.map(s => s.position)).toLocaleString()} bp
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
