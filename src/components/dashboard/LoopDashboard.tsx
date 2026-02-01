import { useState, useEffect, useRef } from 'react';
import { useGenomeStore } from '../../store/genome.store';

export const LoopDashboard = () => {
    const store = useGenomeStore();
    const loops = store.loops ?? [];
    const isRunning = store.isRunning ?? false;
    const stepCount = store.stepCount ?? 0;
    const [displayLoops, setDisplayLoops] = useState(0);
    const [lastAdded, setLastAdded] = useState<number | null>(null);
    const [loopRate, setLoopRate] = useState(0);
    
    const historyRef = useRef<number[]>([]);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    
    // Анимируем счетчик
    useEffect(() => {
        const interval = setInterval(() => {
            const current = loops.length;
            if (current > displayLoops) {
                setLastAdded(current - displayLoops);
                setTimeout(() => setLastAdded(null), 600);
            }
            setDisplayLoops(current);
            
            historyRef.current.push(current);
            if (historyRef.current.length > 100) {
                historyRef.current.shift();
            }
            
            const recent = historyRef.current.slice(-10);
            const rate = recent.length > 1 ? (recent[recent.length - 1] - recent[0]) / 10 : 0;
            setLoopRate(rate);
        }, 100);
        return () => clearInterval(interval);
    }, [loops.length, displayLoops]);
    
    // Рисуем sparkline
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        const width = canvas.width;
        const height = canvas.height;
        const history = historyRef.current;
        
        ctx.clearRect(0, 0, width, height);
        
        if (history.length < 2) return;
        
        const maxVal = Math.max(...history, 1);
        
        ctx.beginPath();
        ctx.strokeStyle = loops.length > 0 ? '#00ff00' : '#ffaa00';
        ctx.lineWidth = 2;
        
        history.forEach((val, i) => {
            const x = (i / (history.length - 1)) * width;
            const y = height - (val / maxVal) * height * 0.8 - 5;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
        
        ctx.fillStyle = '#00ff00';
        history.forEach((val, i) => {
            if (val > 0) {
                const x = (i / (history.length - 1)) * width;
                const y = height - (val / maxVal) * height * 0.8 - 5;
                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fill();
            }
        });
    }, [loops.length]);
    
    let statusColor = '#888';
    let statusText = 'Idle';
    let pulse = false;
    
    if (isRunning) {
        if (loops.length > 0) {
            statusColor = '#00ff00';
            statusText = 'Loops Forming';
        } else {
            statusColor = '#ffaa00';
            statusText = 'Running (No Loops)';
            pulse = true;
        }
    }
    
    return (
        <div style={{
            padding: '20px',
            background: 'rgba(0,0,0,0.9)',
            borderRadius: '8px',
            color: 'white',
            fontFamily: 'monospace',
            border: '1px solid #333',
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
                <div style={{ position: 'relative' }}>
                    <div style={{
                        width: 20,
                        height: 20,
                        borderRadius: '50%',
                        background: statusColor,
                        boxShadow: `0 0 15px ${statusColor}`,
                        animation: pulse ? 'pulse-dashboard 1s infinite' : 'none',
                    }} />
                    <style>{`
                        @keyframes pulse-dashboard {
                            0%, 100% { opacity: 1; transform: scale(1); }
                            50% { opacity: 0.6; transform: scale(0.9); }
                        }
                    `}</style>
                </div>
                
                <div>
                    <div style={{ fontSize: '12px', color: '#888' }}>Status</div>
                    <div style={{ fontSize: '14px', fontWeight: 'bold', color: statusColor }}>
                        {statusText}
                    </div>
                </div>
            </div>
            
            <div style={{ 
                background: 'rgba(255,255,255,0.05)',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '15px',
                textAlign: 'center',
            }}>
                <div style={{ fontSize: '12px', color: '#888', marginBottom: '5px' }}>
                    Loops Formed
                </div>
                <div style={{ 
                    fontSize: '48px', 
                    fontWeight: 'bold',
                    color: displayLoops > 0 ? '#00ff00' : '#fff',
                    position: 'relative',
                }}>
                    {displayLoops}
                    {lastAdded !== null && (
                        <span style={{
                            position: 'absolute',
                            right: -30,
                            top: 0,
                            color: '#00ff00',
                            fontSize: '20px',
                            animation: 'fade-up 0.6s ease-out forwards',
                        }}>
                            +{lastAdded}
                        </span>
                    )}
                </div>
                <style>{`
                    @keyframes fade-up {
                        0% { opacity: 1; transform: translateY(0); }
                        100% { opacity: 0; transform: translateY(-20px); }
                    }
                `}</style>
            </div>
            
            <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                marginBottom: '15px',
                fontSize: '12px',
            }}>
                <div>
                    <span style={{ color: '#888' }}>Rate: </span>
                    <span style={{ 
                        color: loopRate > 0 ? '#00ff00' : '#888',
                        fontWeight: 'bold',
                    }}>
                        {(loopRate ?? 0).toFixed(2)} loops/100 steps
                    </span>
                </div>
                <div>
                    <span style={{ color: '#888' }}>Step: </span>
                    <span>{(stepCount ?? 0).toLocaleString()}</span>
                </div>
            </div>
            
            <div style={{ marginBottom: '10px' }}>
                <div style={{ fontSize: '11px', color: '#888', marginBottom: '5px' }}>
                    Loop History (last 100 updates)
                </div>
                <canvas
                    ref={canvasRef}
                    width={300}
                    height={60}
                    style={{
                        width: '100%',
                        height: '60px',
                        background: 'rgba(0,0,0,0.5)',
                        borderRadius: '4px',
                    }}
                />
            </div>
            
            <div style={{ marginTop: '15px' }}>
                <div style={{ 
                    fontSize: '11px', 
                    color: '#888',
                    marginBottom: '5px',
                    display: 'flex',
                    justifyContent: 'space-between',
                }}>
                    <span>Progress to Target (3 loops)</span>
                    <span>{Math.min((displayLoops / 3) * 100, 100).toFixed(0)}%</span>
                </div>
                <div style={{
                    height: '6px',
                    background: '#333',
                    borderRadius: '3px',
                    overflow: 'hidden',
                }}>
                    <div style={{
                        width: `${Math.min((displayLoops / 3) * 100, 100)}%`,
                        height: '100%',
                        background: displayLoops >= 3 ? '#00ff00' : '#3498db',
                        transition: 'width 0.3s ease',
                    }} />
                </div>
            </div>
            
            {!isRunning && displayLoops === 0 && (
                <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    background: 'rgba(52, 152, 219, 0.2)',
                    borderRadius: '4px',
                    fontSize: '11px',
                    color: '#3498db',
                }}>
                    💡 Tip: Load CTCF data and click "Run" to start simulation
                </div>
            )}
            
            {isRunning && displayLoops === 0 && stepCount > 100 && (
                <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    background: 'rgba(231, 76, 60, 0.2)',
                    borderRadius: '4px',
                    fontSize: '11px',
                    color: '#e74c3c',
                }}>
                    ⚠️ No loops forming. Check CTCF orientations (need F...R pairs)
                </div>
            )}
        </div>
    );
};
