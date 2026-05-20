"use client";

import { useCallback, useEffect, useState } from "react";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { ChartsSection } from "@/components/dashboard/ChartsSection";
import { ExecutiveSummary } from "@/components/dashboard/ExecutiveSummary";
import { Header } from "@/components/dashboard/Header";
import { LLMMonitoring } from "@/components/dashboard/LLMMonitoring";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { SkeletonDashboard } from "@/components/dashboard/Skeleton";
import { TelegramPanel } from "@/components/dashboard/TelegramPanel";
import { SecurityCommandCenter } from "@/components/security/SecurityCommandCenter";
import { dashboardAdapter } from "@/lib/dashboard-service";
import type { DashboardData } from "@/types/dashboard";

export function DashboardShell() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setData(await dashboardAdapter.getDashboardSnapshot());
    } catch {
      setError("Dashboard telemetry is temporarily unavailable.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = window.setInterval(load, 8000);
    return () => window.clearInterval(interval);
  }, [load]);

  return (
    <div className="min-h-screen">
      <Header refreshedAt={data?.refreshedAt ?? new Date().toISOString()} onRefresh={load} isLoading={isLoading} />
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1 px-4 py-5 md:px-6 lg:px-7">
          {error ? (
            <div className="command-panel rounded-lg p-6 text-critical">{error}</div>
          ) : !data ? (
            <SkeletonDashboard />
          ) : (
            <div className="grid gap-5">
              <section id="overview" className="scroll-mt-24">
                <ExecutiveSummary overview={data.overview} />
              </section>
              <div className="grid gap-5 2xl:grid-cols-[minmax(0,1fr)_390px]">
                <div className="grid gap-5">
                  <section id="project-monitoring" className="scroll-mt-24">
                    <div id="langsmith-monitoring" className="scroll-mt-24">
                      <ChartsSection
                        timeseries={data.timeseries}
                        distribution={data.distribution ?? data.llmDistribution}
                      />
                    </div>
                  </section>
                  <section id="llm-monitoring" className="scroll-mt-24">
                    <LLMMonitoring llms={data.llms} />
                  </section>
                  <SecurityCommandCenter security={data.security} />
                  <section id="telegram-console" className="scroll-mt-24">
                    <TelegramPanel telegram={data.telegram} />
                  </section>
                  <SettingsStatusPanel />
                </div>
                <div className="2xl:sticky 2xl:top-[96px] 2xl:h-fit">
                  <ActivityFeed items={data.activity} />
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function SettingsStatusPanel() {
  return (
    <section id="settings" className="command-panel scroll-mt-24 rounded-lg p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Settings</div>
          <h2 className="mt-1 text-xl font-semibold text-silver">Dashboard configuration status</h2>
        </div>
        <div className="rounded-full border border-success/30 bg-success/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-[#9ed6b0]">
          Ready
        </div>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <StatusTile label="Data Adapter" value="Mock real-time" />
        <StatusTile label="Refresh Cadence" value="8 seconds" />
        <StatusTile label="Backend Binding" value="Endpoint-ready" />
      </div>
    </section>
  );
}

function StatusTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/[0.025] px-3 py-3">
      <div className="text-[11px] uppercase tracking-[0.12em] text-muted">{label}</div>
      <div className="mt-1 text-sm font-semibold text-silver">{value}</div>
    </div>
  );
}
