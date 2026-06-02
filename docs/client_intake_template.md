# Sentrya Ops V2 Client Intake Template

This intake document collects the information required to configure Sentrya Ops V2 for a specific company, workflow, and operational context.

Sentrya Ops V2 is a configurable AI Operations Desk architecture. It is not a universal plug-and-play chatbot. Each implementation must be adapted to the client's channels, rules, workflows, integrations, knowledge base, brand voice, priorities, and security needs.

Sensitive credentials must be provided only through secure channels. Do not paste real passwords, API keys, tokens, private URLs, or production secrets into this document.

## 1. Client Overview

| Field | Answer |
| --- | --- |
| Company name |  |
| Industry |  |
| Main website |  |
| Primary contact |  |
| Technical contact |  |
| Time zone |  |
| Preferred communication channel |  |

Briefly describe the company and the operation that Sentrya Ops V2 should support:

```text

```

## 2. Business Goals

What should this implementation improve?

- [ ] Faster response times
- [ ] Better request triage
- [ ] Reduced manual workload
- [ ] More consistent answers
- [ ] Safer AI-assisted operations
- [ ] Better internal workflow visibility
- [ ] Integration with existing tools
- [ ] Other:

Describe the main success criteria:

```text

```

## 3. Primary Use Case

Select the main use case:

- [ ] Customer support
- [ ] Help desk
- [ ] Service workflow triage
- [ ] Internal operations
- [ ] Backoffice routine automation
- [ ] Request classification
- [ ] Business process automation
- [ ] Other:

What should the first version of the AI Operations Desk handle?

```text

```

## 4. Support or Operations Context

| Question | Answer |
| --- | --- |
| Who sends requests? |  |
| Who reviews or approves AI-assisted actions? |  |
| What teams are involved? |  |
| What hours should the workflow support? |  |
| Are there seasonal or peak-volume periods? |  |

## 5. Input Channels

Which channels should be considered?

- [ ] Telegram
- [ ] WhatsApp/API
- [ ] Web forms
- [ ] CRM
- [ ] Help desk/ticketing
- [ ] Email
- [ ] Webhooks
- [ ] Internal tools
- [ ] Other:

For each selected channel, describe the expected input format and where requests currently arrive:

| Channel | Current tool/system | Notes |
| --- | --- | --- |
|  |  |  |

## 6. Request Types

List the main request types the system should classify or support.

| Request type | Description | Example |
| --- | --- | --- |
|  |  |  |

## 7. Priority Levels

Define priority levels for requests.

| Priority | Meaning | Example | Expected handling |
| --- | --- | --- | --- |
| Low |  |  |  |
| Medium |  |  |  |
| High |  |  |  |
| Critical |  |  |  |

## 8. Escalation Rules

When should the system escalate to a human?

- [ ] Low confidence
- [ ] Security-sensitive request
- [ ] Customer complaint
- [ ] Refund or billing issue
- [ ] Legal, medical, financial, or compliance-sensitive topic
- [ ] Request outside approved workflow
- [ ] VIP or strategic customer
- [ ] Other:

Describe escalation rules:

```text

```

## 9. Allowed AI Actions

What may the AI assistant do?

- [ ] Classify requests
- [ ] Draft responses
- [ ] Summarize conversations
- [ ] Suggest next steps
- [ ] Create structured JSON
- [ ] Plan tool/API/webhook calls
- [ ] Trigger approved workflows after validation
- [ ] Other:

What must the AI never do without approval?

```text

```

## 10. Human Review Rules

When is human review mandatory?

| Condition | Human reviewer | Required action |
| --- | --- | --- |
|  |  |  |

## 11. Integrations Required

List systems that may need integration.

| System | Purpose | API available? | Documentation available? |
| --- | --- | --- | --- |
| CRM |  | Yes / No | Yes / No |
| Help desk |  | Yes / No | Yes / No |
| Database |  | Yes / No | Yes / No |
| Internal API |  | Yes / No | Yes / No |
| Webhook |  | Yes / No | Yes / No |

## 12. Knowledge Base / FAQ / Documents

What materials should guide responses?

- [ ] FAQ
- [ ] Help center
- [ ] SOPs
- [ ] Product documentation
- [ ] Pricing or plan rules
- [ ] Internal policies
- [ ] Troubleshooting guides
- [ ] Other:

Provide links or attach sanitized documents. Do not include confidential secrets.

## 13. Brand Voice and Response Style

Describe the preferred tone:

- [ ] Formal
- [ ] Friendly
- [ ] Concise
- [ ] Technical
- [ ] Executive
- [ ] Support-oriented
- [ ] Other:

Words or phrases to use:

```text

```

Words or phrases to avoid:

```text

```

## 14. Security Requirements

Which security rules matter for this workflow?

- [ ] Block prompt injection attempts
- [ ] Block sensitive file/path requests
- [ ] Block credential exposure
- [ ] Block unsafe URLs or internal network access
- [ ] Require human review for high-risk requests
- [ ] Enable lockdown behavior
- [ ] Maintain audit logs
- [ ] Other:

Describe any compliance or internal policy requirements:

```text

```

## 15. Dashboard and Metrics Expectations

Which metrics should be visible?

- [ ] Total requests
- [ ] Request categories
- [ ] Priority distribution
- [ ] LLM calls
- [ ] Errors
- [ ] Error rate
- [ ] Latency
- [ ] Security events
- [ ] Escalations
- [ ] Human review queue
- [ ] Other:

## 16. Handoff Requirements

What should be included at handoff?

- [ ] Configuration summary
- [ ] Workflow map
- [ ] Environment variable checklist
- [ ] Run instructions
- [ ] Telegram command reference
- [ ] Dashboard instructions
- [ ] Testing notes
- [ ] Known limitations

## 17. Access and Credentials Checklist

Do not paste credentials into this document. Confirm how access will be provided securely.

| Item | Needed? | Secure delivery method | Owner |
| --- | --- | --- | --- |
| Groq API key | Yes / No |  |  |
| LangSmith API key | Yes / No |  |  |
| Telegram bot token | Yes / No |  |  |
| Telegram allowed chat id | Yes / No |  |  |
| CRM/API credentials | Yes / No |  |  |
| Webhook credentials | Yes / No |  |  |
| Operator credentials | Yes / No |  |  |

## 18. Final Implementation Notes

Use this section for constraints, risks, deadlines, and implementation notes.

```text

```
