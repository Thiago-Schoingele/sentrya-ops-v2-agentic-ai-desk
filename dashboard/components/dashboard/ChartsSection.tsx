import { ChartCard } from "@/components/charts/ChartCard";
import type { LlmDistribution, TimeseriesPoint } from "@/types/dashboard";

export function ChartsSection({ timeseries, distribution }: { timeseries: TimeseriesPoint[]; distribution: LlmDistribution[] }) {
const distributionData = distribution.map((item) => ({
  time: (item.model ?? item.name ?? "unknown")
    .replace("openai/", "")
    .replace("llama-", "l-"),
  calls: item.calls ?? 0,
  tokens: Math.round((item.tokens ?? 0) / 1000),
  latencyMs: item.latencyMs ?? 0,
}));

  return (
    <section className="grid gap-4 xl:grid-cols-2">
      <ChartCard title="Traces / Calls over time" subtitle="LangSmith-style live volume" data={timeseries} keys={["traces", "calls"]} />
      <ChartCard title="Success vs Error over time" data={timeseries} keys={["success", "errors"]} type="bar" stacked />
      <ChartCard title="Input / Output / Total tokens" data={timeseries} keys={["inputTokens", "outputTokens", "totalTokens"]} />
      <ChartCard title="Average latency over time" data={timeseries} keys={["latencyMs"]} type="line" />
      <ChartCard title="Error rate trend" data={timeseries} keys={["errorRate"]} type="line" />
      <ChartCard title="LLM usage distribution" data={distributionData} keys={["calls"]} type="bar" />
      <ChartCard title="Tokens by LLM" subtitle="Values shown in thousands" data={distributionData} keys={["tokens"]} type="bar" />
      <ChartCard title="Latency by LLM" data={distributionData} keys={["latencyMs"]} type="bar" />
    </section>
  );
}
