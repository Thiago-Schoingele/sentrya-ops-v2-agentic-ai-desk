"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { cn } from "@/lib/utils";

type ChartType = "area" | "line" | "bar";

interface ChartCardProps {
  title: string;
  subtitle?: string;
  data: any[];
  keys: string[];
  type?: "line" | "bar" | "area";
  stacked?: boolean;
  className?: string;
  height?: number;
}

const colors = ["#7E8FA8", "#5FAE7B", "#C96B6B", "#D0A25A"];

export function ChartCard({ title, subtitle, data, keys, type = "area", height = 230, stacked, className }: ChartCardProps) {
  const commonAxis = {
    axisLine: false,
    tickLine: false,
    tick: { fill: "#7f8b9a", fontSize: 11 }
  };

  return (
    <section className={cn("command-panel rounded-lg p-4", className)}>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-silver">{title}</h3>
          {subtitle ? <p className="mt-1 text-xs text-muted">{subtitle}</p> : null}
        </div>
      </div>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          {type === "bar" ? (
            <BarChart data={data} margin={{ top: 8, right: 0, left: -22, bottom: 0 }}>
              <CartesianGrid stroke="rgba(126,143,168,.11)" vertical={false} />
              <XAxis dataKey="time" {...commonAxis} />
              <YAxis {...commonAxis} />
              <Tooltip content={<PremiumTooltip />} cursor={{ fill: "rgba(126,143,168,.06)" }} />
              {keys.map((key, index) => (
                <Bar key={key} dataKey={key} stackId={stacked ? "stack" : undefined} fill={colors[index % colors.length]} radius={[5, 5, 0, 0]}>
                  {keys.length === 1
                    ? data.map((_, cellIndex) => <Cell key={cellIndex} fill={colors[cellIndex % colors.length]} />)
                    : null}
                </Bar>
              ))}
            </BarChart>
          ) : type === "line" ? (
            <LineChart data={data} margin={{ top: 8, right: 0, left: -22, bottom: 0 }}>
              <CartesianGrid stroke="rgba(126,143,168,.11)" vertical={false} />
              <XAxis dataKey="time" {...commonAxis} />
              <YAxis {...commonAxis} />
              <Tooltip content={<PremiumTooltip />} />
              {keys.map((key, index) => (
                <Line key={key} type="monotone" dataKey={key} stroke={colors[index % colors.length]} strokeWidth={2} dot={false} />
              ))}
            </LineChart>
          ) : (
            <AreaChart data={data} margin={{ top: 8, right: 0, left: -22, bottom: 0 }}>
              <defs>
                {keys.map((key, index) => (
                  <linearGradient key={key} id={`fill-${title.replace(/\W/g, "")}-${key}`} x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor={colors[index % colors.length]} stopOpacity={0.33} />
                    <stop offset="100%" stopColor={colors[index % colors.length]} stopOpacity={0.02} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid stroke="rgba(126,143,168,.11)" vertical={false} />
              <XAxis dataKey="time" {...commonAxis} />
              <YAxis {...commonAxis} />
              <Tooltip content={<PremiumTooltip />} />
              {keys.map((key, index) => (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  fill={`url(#fill-${title.replace(/\W/g, "")}-${key})`}
                  dot={false}
                />
              ))}
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function PremiumTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-md border border-white/10 bg-[#101722]/95 px-3 py-2 text-xs shadow-panel">
      <div className="mb-1 font-semibold text-silver">{label}</div>
      {payload.map((entry: any) => (
        <div key={entry.dataKey} className="flex min-w-32 items-center justify-between gap-4 text-muted">
          <span>{entry.dataKey}</span>
          <span style={{ color: entry.color }} className="font-semibold">
            {Intl.NumberFormat("en").format(entry.value)}
          </span>
        </div>
      ))}
    </div>
  );
}
