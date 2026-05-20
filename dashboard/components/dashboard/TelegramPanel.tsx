import type { ReactNode } from "react";
import { Bot, MessageSquareText, ShieldCheck } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { shortTime } from "@/lib/format";
import type { TelegramStatus } from "@/types/dashboard";

export function TelegramPanel({ telegram }: { telegram: TelegramStatus }) {
  return (
    <section className="command-panel rounded-lg p-5">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Telegram Operations</div>
          <h2 className="mt-1 text-xl font-semibold text-silver">Admin console bridge</h2>
        </div>
        <StatusBadge tone={telegram.botStatus === "Online" ? "success" : "warning"}>{telegram.botStatus}</StatusBadge>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Tile icon={<Bot />} label="Telegram Bot Status" value={telegram.botStatus} />
        <Tile icon={<ShieldCheck />} label="Allowed Chat" value={telegram.allowedChatConfigured ? "Configured" : "Missing"} />
        <Tile icon={<MessageSquareText />} label="Last Interaction" value={shortTime(telegram.lastInteraction)} />
        <Tile icon={<MessageSquareText />} label="Recent Commands" value={String(telegram.totalRecentCommands)} />
        <Tile icon={<ShieldCheck />} label="Admin Console" value={telegram.adminConsoleStatus} />
      </div>
    </section>
  );
}

function Tile({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/[0.025] p-3">
      <div className="mb-3 text-accent [&_svg]:h-4 [&_svg]:w-4">{icon}</div>
      <div className="text-[11px] uppercase tracking-[0.12em] text-muted">{label}</div>
      <div className="mt-1 truncate text-sm font-semibold text-silver">{value}</div>
    </div>
  );
}
