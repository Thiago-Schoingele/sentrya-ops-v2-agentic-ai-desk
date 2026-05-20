import { cn } from "@/lib/utils";
import type { LlmStatus, SecurityState, Severity } from "@/types/dashboard";

type BadgeTone = Severity | LlmStatus | SecurityState | "Operational" | "Degraded" | "Investigating" | "Production" | "Monitoring";

const toneClass: Record<string, string> = {
  success: "border-success/35 bg-success/10 text-[#9ed6b0]",
  healthy: "border-success/35 bg-success/10 text-[#9ed6b0]",
  Operational: "border-success/35 bg-success/10 text-[#9ed6b0]",
  Degraded: "border-critical/35 bg-critical/10 text-[#e1a0a0]",
  Investigating: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  info: "border-accent/35 bg-accent/10 text-[#c6d0df]",
  Production: "border-accent/35 bg-accent/10 text-[#c6d0df]",
  Monitoring: "border-accent/35 bg-accent/10 text-[#c6d0df]",
  warning: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  watch: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  WATCH: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  critical: "border-critical/35 bg-critical/10 text-[#e1a0a0]",
  degraded: "border-critical/35 bg-critical/10 text-[#e1a0a0]",
  LOCKDOWN: "border-critical/35 bg-critical/10 text-[#e1a0a0]",
  offline: "border-white/15 bg-white/5 text-muted",
  NORMAL: "border-success/35 bg-success/10 text-[#9ed6b0]",
  STAFF_ACTIVE: "border-accent/35 bg-accent/10 text-[#c6d0df]",
  RECOVERY_PENDING: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  RECOVERY_VALIDATION: "border-warning/35 bg-warning/10 text-[#e2c27f]",
  RELEASED_MONITORING: "border-accent/35 bg-accent/10 text-[#c6d0df]"
};

export function StatusBadge({ tone, children }: { tone: BadgeTone; children: React.ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em]",
        toneClass[tone] ?? toneClass.info
      )}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {children}
    </span>
  );
}
