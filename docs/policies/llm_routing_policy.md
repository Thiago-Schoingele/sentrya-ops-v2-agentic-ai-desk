# LLM Routing Policy

## Overview

This policy defines how Sentrya Ops V2 should choose the correct LLM for operational tasks. It documents the intended governance model for multi-LLM routing.

This is documentation only. It is RAG-ready operational documentation, but it does not imply that this policy is already implemented as a RAG retrieval layer.

## Why Multi-LLM Governance Exists

Different LLMs serve different operational purposes. Without role governance, a system may use a fast model for high-risk reasoning, a reasoning model for simple tasks, or a natural language model for routing decisions. That increases cost, latency, and operational risk.

## Global Rule

Each LLM must operate only within its assigned role and only inside the Sentrya Ops V2 operational scope.

## FAST MODEL

| Field | Policy |
| --- | --- |
| Model | `llama-3.1-8b-instant` |
| Use for | Fast classification, lightweight triage, simple validation, low-latency intent detection. |
| Do not use for | Deep reasoning, critical security decisions, final strategic decisions. |

### Typical Uses

- Classify a request category.
- Detect simple intent.
- Run first-pass triage.
- Validate simple low-risk structure.

## AGENT MODEL

| Field | Policy |
| --- | --- |
| Model | `openai/gpt-oss-20b` |
| Use for | Main orchestration, route selection, structured JSON, tool/API/webhook planning, operational decision-making. |
| Do not use for | Deep ambiguity resolution or critical security analysis when the reasoning model is required. |

### Typical Uses

- Select the next workflow step.
- Generate structured JSON.
- Plan tool calls.
- Coordinate LangGraph workflow routing.

## REASONING MODEL

| Field | Policy |
| --- | --- |
| Model | `openai/gpt-oss-120b` |
| Use for | Complex reasoning, ambiguity, risk analysis, security-sensitive review, critical decisions. |
| Do not use for | Simple low-risk requests by default. |

### Typical Uses

- Review ambiguous requests.
- Analyze high-impact operational decisions.
- Support recovery or release decisions.
- Review security-sensitive cases.

## GENERAL MODEL

| Field | Policy |
| --- | --- |
| Model | `llama-3.3-70b-versatile` |
| Use for | Natural language response, summaries, synthesis, executive communication, final explanation. |
| Do not use for | Main routing decisions or security-critical analysis alone. |

### Typical Uses

- Produce a clear user-facing response.
- Summarize a decision.
- Refine executive communication.
- Convert technical decisions into natural language.

## Routing Examples

| Scenario | Preferred Model |
| --- | --- |
| Simple request classification | FAST MODEL |
| Workflow route selection | AGENT MODEL |
| Ambiguous security-sensitive case | REASONING MODEL |
| Final user-facing explanation | GENERAL MODEL |
| Structured API/webhook plan | AGENT MODEL |
| Recovery decision review | REASONING MODEL |

## Escalation Conditions

Escalate from FAST or AGENT to REASONING when:

- confidence is low;
- the request is ambiguous;
- security risk is elevated;
- recovery or release decisions are involved;
- business impact is high;
- human review may be required.

## Direct Response Conditions

Some responses do not require LLM calls:

- `/teste_llms`
- capability questions such as `What can you do?` or `Qual a sua habilidade?`
- static registry explanations;
- local operational policy summaries.

These should be answered directly from local system documentation or registry logic.

## Policy-Aware RAG Future Note

This policy is suitable for future policy-aware RAG retrieval. A future RAG layer may retrieve this policy to guide routing decisions, but the current document is an operational governance reference.
