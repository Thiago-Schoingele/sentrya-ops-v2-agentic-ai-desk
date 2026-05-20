import type { Severity } from "@/types/dashboard";
import { cn } from "@/lib/utils";

const toneMap: Record<Severity, string> = {
  info: "text-accent",
  success: "text-success",
  warning: "text-warning",
  critical: "text-critical",
  low: "text-success",
  medium: "text-warning",
  high: "text-critical",
};

export function KpiCard({
  label,
  value,
  delta,
  tone = "info"
}: {
  label: string;
  value: string;
  delta?: string;
  tone?: Severity;
}) {
  return (
    <article className="command-panel rounded-lg p-4 transition duration-200 hover:-translate-y-0.5 hover:border-accent/30">
      <div className="text-xs font-medium uppercase tracking-[0.14em] text-muted">{label}</div>
      <div className="mt-3 flex items-end justify-between gap-3">
        <div className="text-2xl font-semibold text-silver">{value}</div>
        {delta ? <div className={cn("text-xs font-semibold", toneMap[tone])}>{delta}</div> : null}
      </div>
    </article>
  );
}
