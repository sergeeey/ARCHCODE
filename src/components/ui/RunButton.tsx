import { motion } from "framer-motion";
import { Play, Pause, Square } from "lucide-react";

type RunButtonAction = "run" | "pause" | "stop";

interface RunButtonProps {
  action: RunButtonAction;
  isActive?: boolean;
  disabled?: boolean;
  onClick: () => void;
  size?: "sm" | "md" | "lg";
}

const sizeClasses = { sm: "p-2", md: "p-3", lg: "p-4" };
const iconSizes = { sm: 14, md: 18, lg: 22 };

export const RunButton = ({
  action,
  isActive = false,
  disabled = false,
  onClick,
  size = "md",
}: RunButtonProps) => {
  const Icon = action === "run" ? Play : action === "pause" ? Pause : Square;
  const label =
    action === "run" ? "Run" : action === "pause" ? "Pause" : "Stop";

  return (
    <motion.button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`
        rounded-[var(--radius-md)] font-mono text-xs font-semibold
        border border-[rgba(255,255,255,0.15)]
        flex items-center justify-center gap-1.5
        disabled:opacity-50 disabled:cursor-default
        ${sizeClasses[size]}
        ${action === "run" ? "bg-[var(--accent-live)] text-[#050505]" : ""}
        ${action === "pause" ? "bg-[var(--accent-danger)] text-white" : ""}
        ${action === "stop" ? "bg-[var(--accent-muted)] text-white" : ""}
      `}
      animate={
        action === "run" && isActive
          ? {
              scale: [1, 1.02, 1],
              boxShadow: [
                "0 0 0 0 rgba(0, 240, 255, 0)",
                "0 0 20px 2px rgba(0, 240, 255, 0.4)",
                "0 0 0 0 rgba(0, 240, 255, 0)",
              ],
            }
          : {}
      }
      transition={
        action === "run" && isActive
          ? { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
          : { duration: 0.2 }
      }
      whileHover={disabled ? {} : { opacity: 0.9 }}
      whileTap={disabled ? {} : { scale: 0.98 }}
      aria-label={label}
    >
      <Icon size={iconSizes[size]} strokeWidth={2.5} />
      <span>{label}</span>
    </motion.button>
  );
};
