import { ChartCard } from "@/components/charts/ChartCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { compactNumber, latency, number, percent, shortTime } from "@/lib/format";
import type { LlmMonitoring } from "@/types/dashboard";

export function LLMMonitoring({ llms }: { llms: LlmMonitoring[] }) {
  return (
    <section>
      <div className="mb-4">
        <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Independent LLM Monitoring</div>
        <h2 className="mt-1 text-xl font-semibold text-silver">Per-model runtime intelligence</h2>
      </div>
      <div className="grid gap-4 xl:grid-cols-2">
        {llms.map((llm) => (
          <article key={llm.model} className="command-panel rounded-lg p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="text-base font-semibold text-silver">{llm.model}</h3>
                <p className="mt-1 max-w-xl text-sm text-muted">{llm.role}</p>
              </div>
              <StatusBadge tone={llm.currentStatus}>{llm.currentStatus}</StatusBadge>
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              <Metric label="LangSmith Runs" value={number(llm.langSmithRuns)} />
              <Metric label="LLM Calls" value={number(llm.llmCalls)} />
              <Metric label="Successes" value={number(llm.successes)} />
              <Metric label="Errors" value={number(llm.errors)} />
              <Metric label="Error Rate" value={percent(llm.errorRate)} />
              <Metric label="Input Tokens" value={compactNumber(llm.inputTokens)} />
              <Metric label="Output Tokens" value={compactNumber(llm.outputTokens)} />
              <Metric label="Total Tokens" value={compactNumber(llm.totalTokens)} />
              <Metric label="Avg Tokens / Call" value={number(llm.averageTokensPerCall)} />
              <Metric label="Avg Latency" value={latency(llm.averageLatencyMs)} />
              <Metric label="Last Execution" value={shortTime(llm.lastExecution)} />
              <Metric label="Current Status" value={llm.currentStatus} />
            </div>

            <ChartCard className="mt-4 border-white/10 bg-transparent shadow-none" title="Model trend" data={llm.trend} keys={["calls", "latencyMs", "errors"]} height={170} />
          </article>
        ))}
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/[0.025] px-3 py-2">
      <div className="text-[11px] uppercase tracking-[0.12em] text-muted">{label}</div>
      <div className="mt-1 truncate text-sm font-semibold text-silver">{value}</div>
    </div>
  );
}
