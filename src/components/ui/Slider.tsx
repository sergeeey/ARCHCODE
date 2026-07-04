import type { InputHTMLAttributes } from "react";

interface SliderProps extends Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "type"
> {
  label?: string;
  value: number;
  onValueChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  valueLabel?: string;
}

export const Slider = ({
  label,
  value,
  onValueChange,
  min,
  max,
  step = 1,
  valueLabel,
  className = "",
  ...props
}: SliderProps) => {
  const pct = ((value - min) / (max - min || 1)) * 100;

  return (
    <div className={`w-full ${className}`}>
      {(label !== undefined || valueLabel !== undefined) && (
        <label className="flex justify-between items-baseline gap-2 mb-1.5 text-xs text-[var(--text-label)] font-mono">
          {label != null && <span>{label}</span>}
          {valueLabel != null && (
            <span className="tabular-nums">{valueLabel}</span>
          )}
        </label>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onValueChange(Number(e.target.value))}
        className="slider-optical w-full h-2 appearance-none bg-transparent cursor-pointer"
        style={{
          background: `linear-gradient(to right, var(--accent-live) 0%, var(--accent-live) ${pct}%, rgba(255,255,255,0.2) ${pct}%, rgba(255,255,255,0.2) 100%)`,
          borderRadius: 1,
        }}
        {...props}
      />
      <style>{`
        .slider-optical::-webkit-slider-thumb {
          appearance: none;
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: var(--accent-live);
          border: 1px solid rgba(255,255,255,0.3);
          box-shadow: 0 0 10px var(--accent-live);
          cursor: pointer;
        }
        .slider-optical::-moz-range-thumb {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          background: var(--accent-live);
          border: 1px solid rgba(255,255,255,0.3);
          box-shadow: 0 0 10px var(--accent-live);
          cursor: pointer;
        }
      `}</style>
    </div>
  );
};
