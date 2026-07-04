import type { HTMLAttributes } from "react";

interface PanelProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
}

export const Panel = ({
  title,
  className = "",
  children,
  ...props
}: PanelProps) => {
  return (
    <div
      className={`panel-glass rounded-[var(--radius-md)] p-5 font-mono ${className}`}
      {...props}
    >
      {title && (
        <h3 className="m-0 mb-4 text-sm font-semibold text-[var(--text-heading)] border-b border-[rgba(255,255,255,0.1)] pb-2">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};
