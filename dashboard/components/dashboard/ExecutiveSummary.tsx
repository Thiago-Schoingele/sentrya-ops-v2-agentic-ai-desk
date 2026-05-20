import { KpiCard } from "@/components/dashboard/KpiCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { compactNumber, latency, number, percent, shortTime } from "@/lib/format";
import type { ProjectOverview } from "@/types/dashboard";

export function ExecutiveSummary({ overview }: { overview: ProjectOverview }) {
  const cards = [
    ["Total Traces", number(overview.totalTraces), "+4.8%", "success"],
    ["Total LLM Calls", number(overview.totalLlmCalls), "+7.1%", "success"],
    ["Successes", number(overview.successes), "stable", "success"],
    ["Errors", number(overview.errors), "-0.3%", "warning"],
    ["Error Rate", percent(overview.errorRate), "watch", "warning"],
    ["Input Tokens", compactNumber(overview.inputTokens), "+6.2%", "info"],
    ["Output Tokens", compactNumber(overview.outputTokens), "+3.9%", "info"],
    ["Total Tokens", compactNumber(overview.totalTokens), "+5.1%", "info"],
    ["Avg Tokens / Call", number(overview.averageTokensPerCall), "normal", "info"],
    ["Average Latency", latency(overview.averageLatencyMs), "-38ms", "success"],
    ["Last Execution", shortTime(overview.lastExecution), "live", "success"],
    ["Current Status", overview.currentStatus, "ready", "success"]
  ] as const;

  return (
    <section>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Project Overview</div>
          <h2 className="mt-1 text-xl font-semibold text-silver">{overview.projectName}</h2>
        </div>
        <StatusBadge tone="success">{overview.currentStatus}</StatusBadge>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-6">
        {cards.map(([label, value, delta, tone]) => (
          <KpiCard key={label} label={label} value={value} delta={delta} tone={tone} />
        ))}
      </div>
    </section>
  );
}
