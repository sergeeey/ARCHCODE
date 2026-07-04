import { useState, useRef, useCallback, ReactNode } from "react";

const DELAY_MS = 400;

interface TooltipProps {
  title: string;
  content: ReactNode;
  children: ReactNode;
  /** Задержка перед показом (мс) */
  delayMs?: number;
}

export function Tooltip({
  title,
  content,
  children,
  delayMs = DELAY_MS,
}: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const timeoutRef = useRef<number | null>(null);

  const show = useCallback(() => {
    timeoutRef.current = window.setTimeout(() => setVisible(true), delayMs);
  }, [delayMs]);

  const hide = useCallback(() => {
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setVisible(false);
  }, []);

  return (
    <span
      className="relative inline-flex items-baseline cursor-help"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      {visible && (
        <div
          className="panel-glass absolute left-0 top-full z-[9999] mt-1.5 max-w-[280px] rounded-lg px-3 py-2 text-left font-mono text-xs shadow-lg"
          style={{ pointerEvents: "none" }}
          role="tooltip"
        >
          <div className="font-semibold text-[var(--text-heading)] mb-1">
            {title}
          </div>
          <div className="text-[var(--text-label)] leading-relaxed whitespace-normal">
            {content}
          </div>
        </div>
      )}
    </span>
  );
}
