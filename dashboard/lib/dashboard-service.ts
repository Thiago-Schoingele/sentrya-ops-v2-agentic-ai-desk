import { makeDashboardData } from "@/data/mockDashboard";
import type {
  ActivityItem,
  DashboardData,
  LlmMonitoring,
  ProjectOverview,
  SecuritySnapshot,
  TelegramStatus,
  TimeseriesPoint
} from "@/types/dashboard";

const wait = (ms = 240) => new Promise((resolve) => setTimeout(resolve, ms));

export interface DashboardAdapter {
  getProjectOverview(): Promise<ProjectOverview>;
  getProjectTimeseries(): Promise<TimeseriesPoint[]>;
  getLLMMonitoring(): Promise<LlmMonitoring[]>;
  getSecurityState(): Promise<SecuritySnapshot>;
  getSecurityEvents(): Promise<ActivityItem[]>;
  getAdminActions(): Promise<ActivityItem[]>;
  getTelegramStatus(): Promise<TelegramStatus>;
  getDashboardSnapshot(): Promise<DashboardData>;
}

export class MockDashboardAdapter implements DashboardAdapter {
  async getDashboardSnapshot() {
    await wait();
    return makeDashboardData();
  }

  async getProjectOverview() {
    return (await this.getDashboardSnapshot()).overview;
  }

  async getProjectTimeseries() {
    return (await this.getDashboardSnapshot()).timeseries;
  }

  async getLLMMonitoring() {
    return (await this.getDashboardSnapshot()).llms;
  }

  async getSecurityState() {
    return (await this.getDashboardSnapshot()).security;
  }

  async getSecurityEvents() {
    return (await this.getDashboardSnapshot()).activity.filter((item) => item.category === "security");
  }

  async getAdminActions() {
    return (await this.getDashboardSnapshot()).activity.filter((item) => item.category === "admin");
  }

  async getTelegramStatus() {
    return (await this.getDashboardSnapshot()).telegram;
  }
}

export const dashboardAdapter: DashboardAdapter = new MockDashboardAdapter();
