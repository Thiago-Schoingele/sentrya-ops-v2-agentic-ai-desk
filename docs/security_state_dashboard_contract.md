# Sentrya Ops V2 — Security State Dashboard Contract

This document defines the data structure that the future Dashboarder / Control Panel should use.

## Core idea

The Dashboarder should not invent security states. It should read and display the real state produced by:

- `src/security_state.py`
- `data/security_state.json`
- `data/security_events.jsonl`

## Official states

- `NORMAL`
- `WATCH`
- `LOCKDOWN`
- `STAFF_ACTIVE`
- `RECOVERY_PENDING`
- `RECOVERY_VALIDATION`
- `RELEASED_MONITORING`

## Main dashboard sections

### System

Fields:

- `name`
- `security_state`
- `lockdown_active`
- `staff_active`

### Incident

Fields:

- `last_event_id`
- `last_event_type`
- `last_event_severity`
- `last_event_at_utc`
- `last_high_or_critical_at_utc`
- `lockdown_reason`

### Recovery

Fields:

- `requested_at_utc`
- `validation_started_at_utc`
- `validation_until_utc`
- `released_monitoring_until_utc`
- `can_release_after_validation`

### Metrics

Fields:

- `total_events`
- `total_blocked_events`
- `total_high_or_critical_events`

### Admin actions

The dashboard should display available actions based on the current state:

- `view_status`
- `activate_staff`
- `activate_lockdown`
- `request_recovery`
- `start_recovery_validation`
- `release_after_validation`
- `force_release`

## Future UI requirements

The future panel should include:

- Operator login using the existing Operator Auth Gate
- Security state cards
- Lockdown status
- STAFF status
- Recovery timeline
- Last blocked event
- Blocked events chart
- High/Critical incidents chart
- Telegram Bot status
- LangSmith metrics area
- Admin action buttons

## Visual direction

- Dark tech interface
- Black, graphite, dark gray, deep blue
- Clean SaaS dashboard
- Avoid visual pollution
- Desktop-first layout
- Security command center style

## Dashboard logic

The dashboard should follow this logic:

```text
Security event detected
↓
SecurityStateManager records event
↓
State transitions if needed
↓
Dashboard reads current snapshot
↓
Operator sees allowed admin actions
↓
Operator acts using the same Operator Auth credentials