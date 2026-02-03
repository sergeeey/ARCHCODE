import type { ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'success' | 'danger' | 'muted' | 'purple' | 'secondary';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
}

const variantStyles: Record<ButtonVariant, string> = {
    primary: 'bg-[var(--accent-primary)] hover:opacity-90',
    success: 'bg-[var(--accent-success)] text-black hover:opacity-90',
    danger: 'bg-[var(--accent-danger)] hover:opacity-90',
    muted: 'bg-[var(--accent-muted)] hover:opacity-90',
    purple: 'bg-[var(--accent-purple)] hover:opacity-90',
    secondary: 'bg-[var(--bg-input)] border border-[var(--border-input)] hover:border-[var(--text-muted)]',
};

const sizeStyles: Record<ButtonSize, string> = {
    sm: 'px-2 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
};

export const Button = ({
    variant = 'primary',
    size = 'md',
    className = '',
    disabled,
    children,
    ...props
}: ButtonProps) => {
    return (
        <button
            type="button"
            className={`
                rounded-[var(--radius-md)] font-semibold text-white
                transition-opacity cursor-pointer border-0
                disabled:opacity-60 disabled:cursor-default
                ${variantStyles[variant]} ${sizeStyles[size]} ${className}
            `.trim()}
            disabled={disabled}
            {...props}
        >
            {children}
        </button>
    );
};
