import { useState, useEffect, useRef } from "react";
import { Panel } from "../ui/Panel";

export interface LoopDashboardProps {
  loops: { length: number };
  isRunning: boolean;
  stepCount: number;
}

const LINE_COLOR_LIVE = "#00f0ff";
const LINE_COLOR_IDLE = "rgba(255, 255, 255, 0.35)";

export const LoopDashboard = ({
  loops,
  isRunning,
  stepCount,
}: LoopDashboardProps) => {
  const [displayLoops, setDisplayLoops] = useState(0);
  const [lastAdded, setLastAdded] = useState<number | null>(null);
  const [loopRate, setLoopRate] = useState(0);

  const historyRef = useRef<number[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const current = loops.length;
      if (current > displayLoops) {
        setLastAdded(current - displayLoops);
        setTimeout(() => setLastAdded(null), 600);
      }
      setDisplayLoops(current);
      historyRef.current.push(current);
      if (historyRef.current.length > 100) historyRef.current.shift();
      const recent = historyRef.current.slice(-10);
      const rate =
        recent.length > 1 ? (recent[recent.length - 1] - recent[0]) / 10 : 0;
      setLoopRate(rate);
    }, 100);
    return () => clearInterval(interval);
  }, [loops.length, displayLoops]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const history = historyRef.current;

    ctx.clearRect(0, 0, width, height);
    if (history.length < 2) return;

    const maxVal = Math.max(...history, 1);
    const lineColor = loops.length > 0 ? LINE_COLOR_LIVE : LINE_COLOR_IDLE;

    const getY = (val: number) => height - (val / maxVal) * height * 0.85 - 4;

    ctx.strokeStyle = lineColor;
    ctx.lineWidth = 1;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = lineColor;
    ctx.shadowBlur = 4;
    ctx.beginPath();
    history.forEach((val, i) => {
      const x = (i / (history.length - 1)) * width;
      const y = getY(val);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.shadowBlur = 0;
  }, [loops.length]);

  const statusColor = !isRunning
    ? "var(--text-label)"
    : loops.length > 0
      ? "var(--accent-live)"
      : "var(--accent-muted)";
  const statusText = !isRunning
    ? "Idle"
    : loops.length > 0
      ? "Loops Forming"
      : "Running (No Loops)";

  return (
    <Panel className="font-mono">
      <div className="flex items-center gap-3 mb-4">
        <div
          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
          style={{
            background: statusColor,
            boxShadow:
              isRunning && loops.length > 0
                ? `0 0 8px ${statusColor}`
                : undefined,
          }}
        />
        <div>
          <div className="text-[11px] text-[var(--text-label)]">Status</div>
          <div className="text-sm font-semibold" style={{ color: statusColor }}>
            {statusText}
          </div>
        </div>
      </div>

      <div className="bg-[rgba(255,255,255,0.04)] rounded-[var(--radius-sm)] p-4 mb-4 text-center border border-[rgba(255,255,255,0.06)]">
        <div className="text-[11px] text-[var(--text-label)] mb-1">
          Loops Formed
        </div>
        <div
          className="text-3xl font-bold tabular-nums relative"
          style={{
            color:
              displayLoops > 0 ? "var(--accent-live)" : "var(--text-heading)",
          }}
        >
          {displayLoops}
          {lastAdded !== null && (
            <span className="absolute right-0 top-0 text-sm text-[var(--accent-live)]">
              +{lastAdded}
            </span>
          )}
        </div>
      </div>

      <div className="flex justify-between text-[11px] mb-2 text-[var(--text-label)]">
        <span>
          Rate:{" "}
          <span
            className="tabular-nums font-medium"
            style={{ color: loopRate > 0 ? "var(--accent-live)" : "inherit" }}
          >
            {(loopRate ?? 0).toFixed(2)}
          </span>{" "}
          /100 steps
        </span>
        <span>
          Step:{" "}
          <span className="tabular-nums">
            {(stepCount ?? 0).toLocaleString()}
          </span>
        </span>
      </div>

      <div className="mb-3">
        <div className="text-[10px] text-[var(--text-label)] mb-1">
          Loop History
        </div>
        <canvas
          ref={canvasRef}
          width={300}
          height={56}
          className="w-full h-14 rounded-[var(--radius-sm)] bg-[rgba(0,0,0,0.3)]"
        />
      </div>

      <div className="mb-1">
        <div className="flex justify-between text-[10px] text-[var(--text-label)] mb-1">
          <span>Progress (3 loops)</span>
          <span className="tabular-nums">
            {Math.min((displayLoops / 3) * 100, 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-1 rounded-full bg-[rgba(255,255,255,0.1)] overflow-hidden">
          <div
            className="h-full rounded-full transition-[width] duration-300 ease-out"
            style={{
              width: `${Math.min((displayLoops / 3) * 100, 100)}%`,
              background:
                displayLoops >= 3 ? "var(--accent-live)" : "var(--accent-dna)",
            }}
          />
        </div>
      </div>

      {!isRunning && displayLoops === 0 && (
        <div className="mt-3 py-2 px-3 rounded-[var(--radius-sm)] text-[11px] text-[var(--accent-live)] bg-[rgba(0,240,255,0.08)] border border-[rgba(0,240,255,0.15)]">
          Load CTCF data and click Run to start
        </div>
      )}

      {isRunning && displayLoops === 0 && stepCount > 100 && (
        <div className="mt-3 py-2 px-3 rounded-[var(--radius-sm)] text-[11px] text-[var(--accent-danger)] bg-[rgba(231,76,60,0.1)] border border-[rgba(231,76,60,0.2)]">
          No loops forming. Check CTCF orientations (F...R pairs).
        </div>
      )}
    </Panel>
  );
};
