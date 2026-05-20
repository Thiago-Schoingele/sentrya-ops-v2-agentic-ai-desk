"use client";

import { Bell, CircleUserRound, RefreshCw, ShieldCheck } from "lucide-react";
import { ThreeDButton } from "@/components/ui/ThreeDButton";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { shortTime } from "@/lib/format";

export function Header({ refreshedAt, onRefresh, isLoading }: { refreshedAt: string; onRefresh: () => void; isLoading: boolean }) {
  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0b0f14]/80 backdrop-blur-xl">
      <div className="flex min-h-[76px] items-center justify-between gap-4 px-5 lg:px-7">
        <div className="flex items-center gap-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-white/10 bg-gradient-to-b from-control2 to-steel shadow-control">
            <ShieldCheck className="h-5 w-5 text-accent" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-lg font-semibold tracking-wide text-silver">Sentrya Ops V2</h1>
              <StatusBadge tone="Production">Production</StatusBadge>
            </div>
            <p className="mt-1 text-sm text-muted">AI Operations Engine</p>
          </div>
        </div>

        <div className="hidden items-center gap-3 xl:flex">
          <StatusBadge tone="Operational">System Operational</StatusBadge>
          <div className="text-sm text-muted">Last refresh {shortTime(refreshedAt)}</div>
        </div>

        <div className="flex items-center gap-2">
          <ThreeDButton aria-label="Notifications" variant="quiet" icon={<Bell className="h-4 w-4" />} />
          <ThreeDButton onClick={onRefresh} disabled={isLoading} icon={<RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />}>
            Refresh
          </ThreeDButton>
          <div className="hidden items-center gap-3 rounded-lg border border-white/10 bg-white/[0.035] px-3 py-2 md:flex">
            <CircleUserRound className="h-5 w-5 text-accent" />
            <div>
              <div className="text-xs font-semibold text-silver">Operator</div>
              <div className="text-[11px] text-muted">Command Desk</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
