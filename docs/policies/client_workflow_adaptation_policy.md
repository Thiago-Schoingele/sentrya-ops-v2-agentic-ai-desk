# Client Workflow Adaptation Policy

## Overview

This policy defines how Sentrya Ops V2 should be adapted for each client workflow. It supports implementations for customer support, service operations, help desk, backoffice routines, request triage, and business process automation.

Sentrya Ops V2 can be adapted to different businesses, but each implementation must be configured according to the client's operational context.

## Why Adaptation Is Required

Every company has different channels, request types, escalation rules, brand voice, knowledge sources, integrations, and security needs. A useful AI Operations Desk must reflect those realities instead of behaving like a generic chatbot.

## Channel Mapping

| Channel | Adaptation Notes |
| --- | --- |
| Telegram | Define allowed chat ids, admin command users, notification style, and operator workflow. |
| WhatsApp/API | Define webhook format, authentication, message templates, and escalation paths. |
| Web forms | Map form fields to request categories and priorities. |
| CRM | Map customer records, statuses, ownership, and allowed updates. |
| Help desk/ticketing | Map tickets, queues, SLA categories, tags, and assignment rules. |
| Webhooks | Define payload schema, retries, authentication, and safe actions. |

## Request Classification Mapping

Define request categories before implementation.

| Request Type | Description | Example | Default Priority |
| --- | --- | --- | --- |
| Support question |  |  |  |
| Service request |  |  |  |
| Incident |  |  |  |
| Billing or account issue |  |  |  |
| Internal operation |  |  |  |

## Priority Rules

Priority must be tied to business impact.

| Priority | Typical Meaning | Handling |
| --- | --- | --- |
| Low | Simple, low-risk request | AI can classify or draft. |
| Medium | Standard operational request | AI can assist with guardrails. |
| High | Customer, security, or business impact | Human review may be required. |
| Critical | Incident or sensitive operational risk | Escalate and consider lockdown or STAFF. |

## Escalation Logic

Escalate when:

- request confidence is low;
- security flags are present;
- the request is outside the approved workflow;
- customer impact is high;
- a policy decision is required;
- the action would change external systems;
- the client requires human approval.

## Allowed AI Actions

Allowed actions should be explicitly defined.

- Classify requests.
- Summarize context.
- Draft user-facing responses.
- Suggest next steps.
- Generate structured JSON.
- Plan tool/API/webhook calls.
- Trigger approved actions only when the implementation scope allows it.

## Human Handoff Logic

Define:

- who receives escalations;
- where escalations are sent;
- what context must be included;
- expected response time;
- what the AI should tell the user during handoff.

## Integration Mapping

| Integration | Purpose | Required Access | Risk Level |
| --- | --- | --- | --- |
| CRM |  |  |  |
| Help desk |  |  |  |
| Internal API |  |  |  |
| Webhook |  |  |  |
| Knowledge base |  |  |  |

## Knowledge Base Preparation

Knowledge material should be reviewed before use.

- Remove outdated content.
- Separate public and internal content.
- Mark policy-critical content.
- Identify unclear or conflicting rules.
- Define source priority.
- Prepare future RAG-ready document structure.

## Brand Voice Adaptation

Define:

- tone;
- formality level;
- vocabulary;
- phrases to use;
- phrases to avoid;
- language requirements;
- response length expectations.

## Security Policy Adaptation

Client-specific security rules should define:

- unsafe request categories;
- prohibited data exposure;
- high-risk workflows;
- human review triggers;
- audit requirements;
- lockdown criteria;
- recovery and release rules.

## Dashboard Metrics Mapping

Choose metrics that match the workflow.

- Request volume.
- Category distribution.
- Priority distribution.
- Escalation count.
- Human review count.
- Security events.
- LLM calls.
- Latency.
- Error rate.
- Integration success/failure.

## Testing and Validation Checklist

- [ ] Request categories tested.
- [ ] Priority rules tested.
- [ ] Security blocks tested.
- [ ] Human review flow tested.
- [ ] Language behavior tested.
- [ ] Telegram/admin commands tested if included.
- [ ] Integration payloads tested if included.
- [ ] Dashboard expectations reviewed if included.
- [ ] Client acceptance examples reviewed.

## Handoff Checklist

- [ ] Setup instructions.
- [ ] Environment variable checklist.
- [ ] Workflow summary.
- [ ] Security policy summary.
- [ ] Escalation rules.
- [ ] Command reference.
- [ ] Known limitations.
- [ ] Future improvement notes.

## Future RAG Preparation

Sentrya Ops V2 can evolve toward Policy-Aware RAG by preparing:

- clean knowledge base documents;
- policy documents;
- workflow definitions;
- source priority rules;
- retrieval boundaries;
- client-specific governance notes.

Future RAG should be implemented only after the client's policies, knowledge sources, and workflows are reviewed.
