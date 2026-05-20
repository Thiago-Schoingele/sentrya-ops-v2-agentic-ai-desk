import type {
  ActivityItem,
  DashboardData,
  LlmDistribution,
  LlmMonitoring,
  ProjectOverview,
  SecuritySnapshot,
  TelegramStatus,
  TimeseriesPoint,
} from "@/types/dashboard";

const nowIso = () => new Date().toISOString();

const jitter = (seed: number, range: number) =>
  Math.round(Math.sin(Date.now() / 90000 + seed) * range);

export const liveOverview: ProjectOverview = {
  projectName: "sentrya-ops-v2-agentic-ai-desk",
  totalTraces: 9184200,
  totalLlmCalls: 3218700,
  successes: 3172900,
  errors: 45800,
  errorRate: 1.42,
  inputTokens: 9184200,
  outputTokens: 3218700,
  totalTokens: 12402900,
  averageTokensPerCall: 287,
  averageLatencyMs: 842,
  lastExecution: nowIso(),
  currentStatus: "operational",
};

export const projectOverview = liveOverview;
export const overview = liveOverview;

export function makeTimeseries(): TimeseriesPoint[] {
  return Array.from({ length: 18 }).map((_, index) => {
    const calls = 820 + index * 16 + jitter(index, 40);
    const errors = Math.max(3, Math.round(calls * (0.011 + (index % 5) / 1000)));
    const inputTokens = calls * (145 + (index % 4) * 9);
    const outputTokens = calls * (62 + (index % 3) * 7);

    return {
      time: `${String(index + 6).padStart(2, "0")}:00`,
      traces: Math.round(calls * 0.43),
      calls,
      successes: calls - errors,
      errors,
      inputTokens,
      outputTokens,
      totalTokens: inputTokens + outputTokens,
      latencyMs: 780 + (index % 6) * 24 + jitter(index + 3, 28),
      errorRate: Number(((errors / calls) * 100).toFixed(2)),
    };
  });
}

export const timeseries = makeTimeseries();

export const llms: LlmMonitoring[] = [
  {
    model: "llama-3.1-8b-instant",
    role: "Fast routing, command triage, lightweight extraction",
    langSmithRuns: 11982,
    llmCalls: 16410,
    successes: 16240,
    errors: 170,
    errorRate: 1.04,
    inputTokens: 2478000,
    outputTokens: 816000,
    totalTokens: 3294000,
    averageTokensPerCall: 201,
    averageLatencyMs: 328,
    lastExecution: nowIso(),
    currentStatus: "operational",
    trend: timeseries.slice(-8),
  },
  {
    model: "openai/gpt-oss-20b",
    role: "Main orchestration, structured JSON, tool routing, operational decisions",
    langSmithRuns: 7821,
    llmCalls: 10226,
    successes: 10084,
    errors: 142,
    errorRate: 1.39,
    inputTokens: 2523000,
    outputTokens: 911000,
    totalTokens: 3434000,
    averageTokensPerCall: 336,
    averageLatencyMs: 764,
    lastExecution: nowIso(),
    currentStatus: "healthy",
    trend: timeseries.slice(-8),
  },
  {
    model: "openai/gpt-oss-120b",
    role: "Deep incident analysis, ambiguity handling, critical reasoning",
    langSmithRuns: 3294,
    llmCalls: 4512,
    successes: 4436,
    errors: 76,
    errorRate: 1.68,
    inputTokens: 1969000,
    outputTokens: 741000,
    totalTokens: 2710000,
    averageTokensPerCall: 601,
    averageLatencyMs: 1428,
    lastExecution: nowIso(),
    currentStatus: "watch",
    trend: timeseries.slice(-8),
  },
  {
    model: "llama-3.3-70b-versatile",
    role: "Natural response, synthesis, executive summary, user-facing communication",
    langSmithRuns: 5524,
    llmCalls: 7208,
    successes: 7091,
    errors: 117,
    errorRate: 1.62,
    inputTokens: 2214200,
    outputTokens: 750700,
    totalTokens: 2964900,
    averageTokensPerCall: 411,
    averageLatencyMs: 1086,
    lastExecution: nowIso(),
    currentStatus: "healthy",
    trend: timeseries.slice(-8),
  },
];

export const llmDistribution: LlmDistribution[] = [
  {
    name: "Fast",
    model: "llama-3.1-8b-instant",
    value: 43,
    calls: 16410,
    tokens: 3294000,
    latencyMs: 328,
    color: "#7E8FA8",
  },
  {
    name: "Agent",
    model: "openai/gpt-oss-20b",
    value: 27,
    calls: 10226,
    tokens: 3434000,
    latencyMs: 764,
    color: "#5FAE7B",
  },
  {
    name: "Reasoning",
    model: "openai/gpt-oss-120b",
    value: 12,
    calls: 4512,
    tokens: 2710000,
    latencyMs: 1428,
    color: "#D0A25A",
  },
  {
    name: "General",
    model: "llama-3.3-70b-versatile",
    value: 18,
    calls: 7208,
    tokens: 2964900,
    latencyMs: 1086,
    color: "#C96B6B",
  },
];

export const distribution = llmDistribution;

export const securitySnapshot: SecuritySnapshot = {
  currentState: "RELEASED_MONITORING",
  lockdownActive: false,
  staffActive: true,
  recoveryRequested: false,
  recoveryValidationInProgress: false,
  releasedMonitoringActive: true,
  lastEventType: "input_blocked",
  lastEventSeverity: "high",
  totalBlockedEvents: 17,
  totalHighCriticalEvents: 6,
  canReleaseAfterValidation: false,
  lastEventTimestamp: nowIso(),
  recommendedAction:
    "Continue monitoring elevated prompt-injection attempts across Telegram, runtime security events, and LangSmith traces.",
};

export const security = securitySnapshot;

export const telegramStatus: TelegramStatus = {
  botStatus: "online",
  allowedChatConfigured: true,
  lastInteraction: nowIso(),
  totalRecentCommands: 12,
  adminConsoleStatus: "active",
};

export const telegram = telegramStatus;

export const activityFeed: ActivityItem[] = [
  {
    id: "a1",
    time: "14:33:24",
    timestamp: nowIso(),
    title: "Security state released",
    detail: "Force release completed by authenticated operator.",
    description: "Force release completed by authenticated operator.",
    category: "security",
    type: "security",
    severity: "success",
    source: "security_admin",
  },
  {
    id: "a2",
    time: "14:31:49",
    timestamp: nowIso(),
    title: "LLM execution",
    detail: "openai/gpt-oss-120b completed incident synthesis in 1.42s.",
    description: "openai/gpt-oss-120b completed incident synthesis in 1.42s.",
    category: "llm",
    type: "llm",
    severity: "info",
    source: "langsmith",
  },
  {
    id: "a3",
    time: "14:29:10",
    timestamp: nowIso(),
    title: "Admin action queued",
    detail: "Recovery validation dry-run prepared for release gate.",
    description: "Recovery validation dry-run prepared for release gate.",
    category: "admin",
    type: "admin",
    severity: "info",
    source: "telegram_admin_console",
  },
  {
    id: "a4",
    time: "14:27:54",
    timestamp: nowIso(),
    title: "High severity event",
    detail: "Unauthorized command sequence rejected by policy guard.",
    description: "Unauthorized command sequence rejected by policy guard.",
    category: "security",
    type: "security",
    severity: "warning",
    source: "security_gate",
  },
];

export const activity = activityFeed;


export function makeDashboardData(): DashboardData {
  const refreshedTimeseries = makeTimeseries();

  const refreshedLlms: LlmMonitoring[] = llms.map((llm) => ({
    ...llm,
    lastExecution: nowIso(),
    trend: refreshedTimeseries.slice(-8),
  }));

  const refreshedSecurity: SecuritySnapshot = {
    ...securitySnapshot,
    lastEventTimestamp: nowIso(),
  };

  const refreshedTelegram: TelegramStatus = {
    ...telegramStatus,
    lastInteraction: nowIso(),
  };

  return {
    overview: liveOverview,
    projectOverview: liveOverview,
    timeseries: refreshedTimeseries,
    llms: refreshedLlms,
    llmDistribution,
    distribution: llmDistribution,
    security: refreshedSecurity,
    securitySnapshot: refreshedSecurity,
    telegram: refreshedTelegram,
    telegramStatus: refreshedTelegram,
    activity: activityFeed,
    activityFeed,
    refreshedAt: nowIso(),
  };
}

export const dashboardData: DashboardData = makeDashboardData();

export const mockDashboard = dashboardData;

export default dashboardData;