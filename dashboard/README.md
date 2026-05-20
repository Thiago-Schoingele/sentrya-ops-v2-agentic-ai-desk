# Sentrya Ops V2 Dashboard

Premium operational dashboard UI for a Security + AI Operations Command Center.

## Stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- Recharts
- Lucide icons

## Run

```bash
cd dashboard
npm install
npm run dev
```

Open `http://localhost:3000`.

## Live Data Architecture

The dashboard currently uses `MockDashboardAdapter` in `lib/dashboard-service.ts`.
Replace that adapter with API-backed methods when backend endpoints are ready:

- `getProjectOverview()`
- `getProjectTimeseries()`
- `getLLMMonitoring()`
- `getSecurityState()`
- `getSecurityEvents()`
- `getAdminActions()`
- `getTelegramStatus()`

`components/dashboard/DashboardShell.tsx` polls `getDashboardSnapshot()` every 8 seconds and already exposes manual refresh behavior.
