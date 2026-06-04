interface SkillBadgeProps {
  skill: string;
  variant?: "primary" | "success" | "warning" | "error";
  size?: "sm" | "md";
}

const VARIANTS = {
  primary: {
    bg: "rgba(99, 102, 241, 0.15)",
    color: "#a5b4fc",
    border: "rgba(99, 102, 241, 0.2)",
  },
  success: {
    bg: "rgba(34, 197, 94, 0.15)",
    color: "#4ade80",
    border: "rgba(34, 197, 94, 0.2)",
  },
  warning: {
    bg: "rgba(245, 158, 11, 0.15)",
    color: "#fbbf24",
    border: "rgba(245, 158, 11, 0.2)",
  },
  error: {
    bg: "rgba(239, 68, 68, 0.15)",
    color: "#f87171",
    border: "rgba(239, 68, 68, 0.2)",
  },
};

export default function SkillBadge({
  skill,
  variant = "primary",
  size = "md",
}: SkillBadgeProps) {
  const v = VARIANTS[variant];
  const fontSize = size === "sm" ? "0.6875rem" : "0.75rem";
  const padding = size === "sm" ? "3px 8px" : "4px 12px";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding,
        borderRadius: 9999,
        fontSize,
        fontWeight: 500,
        background: v.bg,
        color: v.color,
        border: `1px solid ${v.border}`,
        transition: "var(--transition-fast)",
        whiteSpace: "nowrap",
      }}
    >
      {skill}
    </span>
  );
}
