import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
    label?: string;
}

export const Input = ({ label, className = '', id, ...props }: InputProps) => {
    const inputId = id ?? `input-${Math.random().toString(36).slice(2, 9)}`;
    return (
        <div className="w-full">
            {label && (
                <label
                    htmlFor={inputId}
                    className="block mb-1.5 text-xs"
                    style={{ color: 'var(--text-muted)' }}
                >
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={`
                    w-full px-2 py-2 rounded-[var(--radius-sm)] font-mono text-sm
                    bg-[var(--bg-input)] text-[var(--text-primary)]
                    border border-[var(--border-input)] outline-none
                    focus:border-[var(--accent-primary)]
                    ${className}
                `.trim()}
                {...props}
            />
        </div>
    );
};
