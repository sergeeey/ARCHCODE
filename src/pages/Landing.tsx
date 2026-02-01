import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export function Landing() {
    return (
        <div className="min-h-screen flex flex-col" style={{ background: 'var(--bg-app)', color: 'var(--text-primary)' }}>
            <header className="p-6 border-b" style={{ borderColor: 'var(--border-panel)' }}>
                <div className="max-w-5xl mx-auto flex items-center justify-between">
                    <span className="font-mono text-xl font-bold">ARCHCODE</span>
                    <Link to="/simulator">
                        <Button variant="primary" size="md">Open Simulator</Button>
                    </Link>
                </div>
            </header>

            <main className="flex-1 flex flex-col items-center justify-center px-6 py-16">
                <section className="text-center max-w-2xl mb-16">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4 font-mono">
                        3D DNA Loop Extrusion Simulator
                    </h1>
                    <p className="text-lg mb-8" style={{ color: 'var(--text-muted)' }}>
                        Chromatin loop extrusion with CTCF boundaries. AlphaGenome-validated, publication-ready.
                    </p>
                    <Link to="/simulator">
                        <Button variant="success" size="lg">Launch Simulator</Button>
                    </Link>
                </section>

                <section className="w-full max-w-3xl grid md:grid-cols-2 gap-6 mb-16">
                    <div
                        className="p-6 rounded-lg font-mono text-sm"
                        style={{ background: 'var(--bg-panel-elevated)', border: 'var(--border-panel)' }}
                    >
                        <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--accent-primary)' }}>
                            3D Loop Extrusion
                        </h3>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Cohesin motors extrude DNA until blocked by convergent CTCF. Real-time WebGL visualization.
                        </p>
                    </div>
                    <div
                        className="p-6 rounded-lg font-mono text-sm"
                        style={{ background: 'var(--bg-panel-elevated)', border: 'var(--border-panel)' }}
                    >
                        <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--accent-success)' }}>
                            AlphaGenome Validation
                        </h3>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Compare contact matrices and P(s) curves against DeepMind AlphaGenome predictions.
                        </p>
                    </div>
                    <div
                        className="p-6 rounded-lg font-mono text-sm"
                        style={{ background: 'var(--bg-panel-elevated)', border: 'var(--border-panel)' }}
                    >
                        <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--accent-purple)' }}>
                            BED & ENCODE
                        </h3>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Load CTCF peaks from BED files or download directly from ENCODE.
                        </p>
                    </div>
                    <div
                        className="p-6 rounded-lg font-mono text-sm"
                        style={{ background: 'var(--bg-panel-elevated)', border: 'var(--border-panel)' }}
                    >
                        <h3 className="text-base font-semibold mb-2" style={{ color: 'var(--accent-warning)' }}>
                            Contact Matrices
                        </h3>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Heatmaps and P(s) power-law fitting for reproducible research.
                        </p>
                    </div>
                </section>
            </main>

            <footer
                className="p-6 border-t"
                style={{ borderColor: 'var(--border-panel)', color: 'var(--text-muted)' }}
            >
                <div className="max-w-5xl mx-auto flex flex-wrap items-center justify-center gap-6 text-sm font-mono">
                    <a href="https://github.com/sergeeey/ARCHCODE" target="_blank" rel="noopener noreferrer" className="hover:underline">
                        GitHub
                    </a>
                    <Link to="/simulator" className="hover:underline">Simulator</Link>
                    <a href="/METHODS.md" target="_blank" rel="noopener noreferrer" className="hover:underline">
                        Methods
                    </a>
                    <a href="/LICENSE" target="_blank" rel="noopener noreferrer" className="hover:underline">
                        License
                    </a>
                </div>
            </footer>
        </div>
    );
}
