import type { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
}

export const Card = ({
  title,
  className = "",
  children,
  ...props
}: CardProps) => {
  return (
    <div
      className={`rounded-[var(--radius-md)] p-5 text-[var(--text-primary)] font-mono ${className}`}
      style={{
        background: "var(--bg-panel-elevated)",
        border: "var(--border-panel)",
      }}
      {...props}
    >
      {title && (
        <h3
          className="m-0 mb-4 text-sm font-semibold"
          style={{ color: "var(--text-primary)" }}
        >
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};
