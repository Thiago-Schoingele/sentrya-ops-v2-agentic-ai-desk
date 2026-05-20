import { AlertTriangle, CheckCircle2, Lock, RadioTower, ShieldAlert, ShieldCheck } from "lucide-react";
import { ThreeDButton } from "@/components/ui/ThreeDButton";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { number, shortTime } from "@/lib/format";
import type { SecuritySnapshot, SecurityState } from "@/types/dashboard";

const states: SecurityState[] = ["NORMAL", "WATCH", "LOCKDOWN", "STAFF_ACTIVE", "RECOVERY_PENDING", "RECOVERY_VALIDATION", "RELEASED_MONITORING"];

export function SecurityCommandCenter({ security }: { security: SecuritySnapshot }) {
  return (
    <section id="security-command-center" className="grid scroll-mt-24 gap-4 2xl:grid-cols-[1.2fr_.8fr]">
      <div id="runtime-state" className="command-panel scroll-mt-24 rounded-lg p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Security Command Center</div>
            <h2 className="mt-1 text-xl font-semibold text-silver">Security State Machine</h2>
          </div>
          <StatusBadge tone={security.currentState}>{security.currentState}</StatusBadge>
        </div>

        <div className="mt-5 grid gap-2 md:grid-cols-7">
          {states.map((state) => (
            <div key={state} className={`rounded-md border px-2 py-3 text-center text-[11px] font-semibold ${state === security.currentState ? "border-accent/45 bg-accent/15 text-silver" : "border-white/10 bg-white/[0.025] text-muted"}`}>
              {state.replace("_", " ")}
            </div>
          ))}
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Flag label="Lockdown Active" value={security.lockdownActive} />
          <Flag label="STAFF Active" value={security.staffActive} />
          <Flag label="Recovery Requested" value={security.recoveryRequested} />
          <Flag label="Validation In Progress" value={security.recoveryValidationInProgress} />
          <Flag label="Released Monitoring" value={security.releasedMonitoringActive} />
          <Info label="Last Event Type" value={security.lastEventType} />
          <Info label="Last Severity" value={security.lastEventSeverity} />
          <Info label="Blocked Events" value={number(security.totalBlockedEvents)} />
          <Info label="High / Critical Events" value={number(security.totalHighCriticalEvents)} />
          <Flag label="Can Release" value={security.canReleaseAfterValidation} />
          <Info label="Last Event" value={shortTime(security.lastEventTimestamp)} />
        </div>

        <div className="mt-5 rounded-md border border-warning/20 bg-warning/10 p-4">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-warning">Recommended Action</div>
          <p className="mt-2 text-sm leading-6 text-silver">{security.recommendedAction}</p>
        </div>
      </div>

      <div id="recovery-release" className="command-panel scroll-mt-24 rounded-lg p-5">
        <div className="mb-4">
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">Security Admin Controls</div>
          <h2 className="mt-1 text-xl font-semibold text-silver">Release and recovery console</h2>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-1">
          <ThreeDButton icon={<RadioTower className="h-4 w-4" />}>View Status</ThreeDButton>
          <ThreeDButton variant="critical" icon={<Lock className="h-4 w-4" />}>Activate Lockdown</ThreeDButton>
          <ThreeDButton icon={<ShieldAlert className="h-4 w-4" />}>Activate STAFF</ThreeDButton>
          <ThreeDButton icon={<AlertTriangle className="h-4 w-4" />}>Request Recovery</ThreeDButton>
          <ThreeDButton icon={<ShieldCheck className="h-4 w-4" />}>Start Recovery Validation</ThreeDButton>
          <ThreeDButton variant="critical" icon={<CheckCircle2 className="h-4 w-4" />}>Force Release</ThreeDButton>
          <ThreeDButton icon={<CheckCircle2 className="h-4 w-4" />}>Complete Monitoring</ThreeDButton>
        </div>
      </div>
    </section>
  );
}

function Flag({ label, value }: { label: string; value: boolean }) {
  return <Info label={label} value={value ? "Active" : "Inactive"} tone={value ? "text-success" : "text-muted"} />;
}

function Info({ label, value, tone = "text-silver" }: { label: string; value: string; tone?: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-white/[0.025] px-3 py-3">
      <div className="text-[11px] uppercase tracking-[0.12em] text-muted">{label}</div>
      <div className={`mt-1 truncate text-sm font-semibold capitalize ${tone}`}>{value}</div>
    </div>
  );
}
