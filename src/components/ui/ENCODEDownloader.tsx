import { useState, useCallback } from 'react';
import {
    ENCODE_CTCF_DATASETS,
    downloadENCODEFile,
    listAvailableDatasets,
    DownloadResult,
    compareCellLines,
} from '../../downloaders/encode';
import { CTCFSite } from '../../domain/models/genome';

interface ENCODEDownloaderProps {
    onSitesLoaded: (sites: CTCFSite[], cellLine: string) => void;
}

export const ENCODEDownloader = ({ onSitesLoaded }: ENCODEDownloaderProps) => {
    const [downloading, setDownloading] = useState<string | null>(null);
    const [progress, setProgress] = useState<number>(0);
    const [results, setResults] = useState<DownloadResult[]>([]);
    const [selectedId, setSelectedId] = useState<string>('ENCFF165MIL');

    const datasets = listAvailableDatasets();

    const handleDownload = useCallback(async (fileId: string) => {
        setDownloading(fileId);
        setProgress(0);

        const result = await downloadENCODEFile(fileId, (p) => {
            setProgress(p.percent);
        });

        setResults(prev => [...prev.filter(r => r.fileId !== fileId), result]);
        setDownloading(null);

        if (result.success && result.sites) {
            onSitesLoaded(result.sites, result.cellLine);
        }
    }, [onSitesLoaded]);

    const handleDownloadAll = useCallback(async () => {
        for (const dataset of datasets) {
            await handleDownload(dataset.id);
        }
    }, [datasets, handleDownload]);

    const comparison = results.length > 0 ? compareCellLines(results) : [];

    return (
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
        }}>
            <h3 style={{ margin: '0 0 15px 0' }}>🧬 ENCODE Data Downloader</h3>
            
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '15px' }}>
                Download CTCF ChIP-seq peaks directly from ENCODE Project
            </div>

            {/* Single Download */}
            <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontSize: '12px' }}>
                    Select Cell Line:
                </label>
                <select
                    value={selectedId}
                    onChange={(e) => setSelectedId(e.target.value)}
                    style={{
                        width: '100%',
                        padding: '10px',
                        background: '#222',
                        color: 'white',
                        border: '1px solid #444',
                        borderRadius: '4px',
                        fontSize: '13px',
                        marginBottom: '10px',
                    }}
                >
                    {datasets.map(d => (
                        <option key={d.id} value={d.id}>
                            {d.cellLine} — {d.description}
                        </option>
                    ))}
                </select>

                <button
                    onClick={() => handleDownload(selectedId)}
                    disabled={downloading !== null}
                    style={{
                        width: '100%',
                        padding: '12px',
                        background: downloading ? '#27ae60' : '#2ecc71',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: downloading ? 'default' : 'pointer',
                        fontSize: '14px',
                        fontWeight: 'bold',
                    }}
                >
                    {downloading === selectedId 
                        ? `⏳ Downloading... ${progress}%` 
                        : '⬇ Download CTCF Peaks'}
                </button>
            </div>

            {/* Download All */}
            <button
                onClick={handleDownloadAll}
                disabled={downloading !== null}
                style={{
                    width: '100%',
                    padding: '10px',
                    background: 'transparent',
                    color: '#3498db',
                    border: '1px solid #3498db',
                    borderRadius: '4px',
                    cursor: downloading ? 'default' : 'pointer',
                    fontSize: '12px',
                    marginBottom: '20px',
                }}
            >
                Download All Cell Lines
            </button>

            {/* Results */}
            {results.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '13px' }}>Downloaded Datasets:</h4>
                    {results.map(result => (
                        <div
                            key={result.fileId}
                            style={{
                                padding: '10px',
                                marginBottom: '8px',
                                background: result.success ? 'rgba(46, 204, 113, 0.1)' : 'rgba(231, 76, 60, 0.1)',
                                border: `1px solid ${result.success ? '#2ecc71' : '#e74c3c'}`,
                                borderRadius: '4px',
                                fontSize: '12px',
                            }}
                        >
                            <div style={{ fontWeight: 'bold' }}>
                                {result.cellLine}
                                {result.success ? ' ✅' : ' ❌'}
                            </div>
                            {result.success && result.parseResult ? (
                                <div style={{ color: '#888', marginTop: '4px' }}>
                                    {result.parseResult.parsed} sites 
                                    ({result.parseResult.sites.filter(s => s.orientation === 'F').length} F / {result.parseResult.sites.filter(s => s.orientation === 'R').length} R)
                                </div>
                            ) : (
                                <div style={{ color: '#e74c3c', marginTop: '4px' }}>
                                    {result.error}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Comparison Table */}
            {comparison.length > 1 && (
                <div style={{ marginTop: '20px' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '13px' }}>Comparison:</h4>
                    <table style={{
                        width: '100%',
                        fontSize: '11px',
                        borderCollapse: 'collapse',
                    }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #444' }}>
                                <th style={{ textAlign: 'left', padding: '5px' }}>Cell Line</th>
                                <th style={{ textAlign: 'right', padding: '5px' }}>Sites</th>
                                <th style={{ textAlign: 'right', padding: '5px' }}>F/R</th>
                            </tr>
                        </thead>
                        <tbody>
                            {comparison.map(c => (
                                <tr key={c.cellLine} style={{ borderBottom: '1px solid #333' }}>
                                    <td style={{ padding: '5px' }}>{c.cellLine}</td>
                                    <td style={{ textAlign: 'right', padding: '5px' }}>{c.totalSites.toLocaleString()}</td>
                                    <td style={{ textAlign: 'right', padding: '5px' }}>
                                        {c.forwardSites}/{c.reverseSites}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
