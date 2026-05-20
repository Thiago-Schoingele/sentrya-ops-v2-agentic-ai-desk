"use client";

import { useState } from "react";
import {
  Activity,
  Bot,
  Gauge,
  LockKeyhole,
  MessageSquare,
  RotateCcw,
  Settings,
  Shield,
  Workflow
} from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { label: "Overview", icon: Gauge, targetId: "overview" },
  { label: "Project Monitoring", icon: Activity, targetId: "project-monitoring" },
  { label: "LLM Monitoring", icon: Bot, targetId: "llm-monitoring" },
  { label: "Security Command Center", icon: Shield, targetId: "security-command-center" },
  { label: "Runtime State", icon: Workflow, targetId: "runtime-state" },
  { label: "Telegram Console", icon: MessageSquare, targetId: "telegram-console" },
  { label: "LangSmith Monitoring", icon: LockKeyhole, targetId: "langsmith-monitoring" },
  { label: "Recovery & Release", icon: RotateCcw, targetId: "recovery-release" },
  { label: "Settings", icon: Settings, targetId: "settings" }
];

export function Sidebar() {
  const [activeId, setActiveId] = useState(items[0].targetId);

  const handleNavigate = (targetId: string) => {
    setActiveId(targetId);
    document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <aside className="hidden w-[270px] shrink-0 border-r border-white/10 bg-[#0b0f14]/72 lg:block">
      <div className="surface-grid sticky top-[76px] h-[calc(100vh-76px)] overflow-y-auto p-4">
        <nav className="space-y-1">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.label}
                type="button"
                aria-current={activeId === item.targetId ? "page" : undefined}
                onClick={() => handleNavigate(item.targetId)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md border px-3 py-3 text-left text-sm transition",
                  activeId === item.targetId
                    ? "border-accent/30 bg-accent/10 text-silver shadow-control"
                    : "border-transparent text-muted hover:border-white/10 hover:bg-white/[0.035] hover:text-silver"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
}
