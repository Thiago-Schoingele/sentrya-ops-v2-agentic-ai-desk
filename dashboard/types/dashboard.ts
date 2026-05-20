export type LlmStatus =
  | "operational"
  | "healthy"
  | "watch"
  | "degraded"
  | "offline"
  | "critical";

export type SecurityState =
  | "NORMAL"
  | "WATCH"
  | "LOCKDOWN"
  | "STAFF_ACTIVE"
  | "RECOVERY_PENDING"
  | "RECOVERY_VALIDATION"
  | "RELEASED_MONITORING";

export type Severity =
  | "info"
  | "success"
  | "warning"
  | "low"
  | "medium"
  | "high"
  | "critical";

export interface TimeseriesPoint {
  time: string;
  traces: number;
  calls: number;
  successes: number;
  errors: number;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  latencyMs: number;
  errorRate: number;
  [key: string]: string | number;
}

export interface ProjectOverview {
  projectName: string;
  totalTraces: number;
  totalLlmCalls: number;
  successes: number;
  errors: number;
  errorRate: number;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  averageTokensPerCall: number;
  averageLatencyMs: number;
  lastExecution: string;
  currentStatus: string;
}

export interface LlmMonitoring {
  model: string;
  role: string;
  langSmithRuns: number;
  llmCalls: number;
  successes: number;
  errors: number;
  errorRate: number;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  averageTokensPerCall: number;
  averageLatencyMs: number;
  lastExecution: string;
  currentStatus: LlmStatus;
  trend: TimeseriesPoint[];
}

export interface LlmDistribution {
  name: string;
  model?: string;
  value: number;
  calls?: number;
  tokens?: number;
  latencyMs?: number;
  color?: string;
  [key: string]: string | number | undefined;
}

export interface SecuritySnapshot {
  currentState: SecurityState;
  lockdownActive: boolean;
  staffActive: boolean;
  recoveryRequested: boolean;
  recoveryValidationInProgress: boolean;
  releasedMonitoringActive: boolean;
  lastEventType: string;
  lastEventSeverity: Severity;
  totalBlockedEvents: number;
  totalHighCriticalEvents: number;
  canReleaseAfterValidation: boolean;
  lastEventTimestamp: string;
  recommendedAction?: string;
}

export interface TelegramStatus {
  botStatus: string;
  allowedChatConfigured: boolean;
  lastInteraction: string;
  totalRecentCommands: number;
  adminConsoleStatus: string;
}

export interface ActivityItem {
  id: string;
  time: string;
  timestamp?: string;
  title: string;
  detail?: string;
  description?: string;
  category: string;
  type?: string;
  severity: Severity;
  source?: string;
}

export interface DashboardData {
  overview: ProjectOverview;
  projectOverview?: ProjectOverview;
  timeseries: TimeseriesPoint[];
  llms: LlmMonitoring[];
  llmDistribution: LlmDistribution[];
  distribution?: LlmDistribution[];
  security: SecuritySnapshot;
  securitySnapshot?: SecuritySnapshot;
  telegram: TelegramStatus;
  telegramStatus?: TelegramStatus;
  activity: ActivityItem[];
  activityFeed?: ActivityItem[];
  refreshedAt?: string;
}
