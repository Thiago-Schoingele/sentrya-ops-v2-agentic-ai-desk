import { Activity, Bot, ShieldAlert, UserCog } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { ActivityItem } from "@/types/dashboard";

const icons = {
  trace: Activity,
  security: ShieldAlert,
  admin: UserCog,
  llm: Bot
};

export function ActivityFeed({ items }: { items: ActivityItem[] }) {
  return (
    <aside className="command-panel rounded-lg p-5">
      <div className="mb-4">
        <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Live Monitoring</div>
        <h2 className="mt-1 text-xl font-semibold text-silver">Activity feed</h2>
      </div>
      {items.length === 0 ? (
        <div className="rounded-md border border-white/10 bg-white/[0.025] p-4 text-sm text-muted">No recent activity to display.</div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const Icon = icons[item.category as keyof typeof icons] ?? icons.trace;
            return (
              <div key={item.id} className="rounded-md border border-white/10 bg-white/[0.025] p-3 transition hover:border-accent/25 hover:bg-white/[0.045]">
                <div className="flex items-start gap-3">
                  <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-white/10 bg-steel text-accent">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="truncate text-sm font-semibold text-silver">{item.title}</h3>
                      <StatusBadge tone={item.severity}>{item.severity}</StatusBadge>
                    </div>
                    <p className="mt-1 text-sm leading-5 text-muted">{item.detail}</p>
                    <div className="mt-2 text-xs text-accent">{item.time}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </aside>
  );
}
