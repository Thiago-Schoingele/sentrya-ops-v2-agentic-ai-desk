# Security Decision Policy

## Overview

This document defines security decision principles for Sentrya Ops V2. It is intended to guide safe operation, implementation review, and future policy-aware retrieval.

It does not disclose secrets, private credentials, or sensitive implementation details.

## Security-First Principle

Security checks must happen before LLM execution. If a request is unsafe, unclear, or outside the approved operational scope, the system should block, escalate, or require human review instead of sending the content to an LLM.

## Security Gate

The Security Gate validates input before the agent workflow proceeds. It should reject or flag unsafe requests such as prompt injection attempts, credential exposure requests, dangerous commands, suspicious URLs, sensitive file access, and unsafe database instructions.

## Input Validation

Input validation should check:

- empty or too-short input;
- excessive repetition;
- prompt injection patterns;
- unsafe shell or SQL-like payloads;
- sensitive file paths;
- internal URLs or SSRF-like patterns;
- attempts to alter system behavior;
- requests that require human review.

## Prompt Injection and Unsafe Input Blocking

The system should block requests that try to:

- reveal hidden instructions;
- override security controls;
- bypass validation;
- request secrets or private keys;
- force tool execution outside scope;
- manipulate output schemas in unsafe ways.

## Lockdown Guard

The Lockdown Guard prevents normal agent execution when the system is in a restricted security state. It protects the system from continuing operations during incidents, recovery, or STAFF-controlled states.

## Security States

| State | Meaning |
| --- | --- |
| NORMAL | Standard operations are allowed. |
| WATCH | Elevated monitoring is active. |
| LOCKDOWN | Normal operational execution is blocked. |
| STAFF_ACTIVE | STAFF protocol is active and requires controlled handling. |
| RECOVERY_PENDING | Recovery has been requested but not validated. |
| RECOVERY_VALIDATION | Validation window is active before release. |
| RELEASED_MONITORING | System has been released and remains under monitoring. |

## When to Block

Block when:

- input triggers a security rule;
- the system is in LOCKDOWN or STAFF_ACTIVE;
- the request asks for secrets or unsafe access;
- the request attempts to bypass policy;
- the request is outside Sentrya Ops V2 scope.

## When to Require Human Review

Require human review when:

- confidence is low;
- the request is high impact;
- security flags are present but not conclusive;
- the action affects customers, billing, legal, access, or recovery;
- the model route is uncertain.

## When to Activate STAFF

Activate STAFF when:

- a security incident requires manual control;
- automated handling should pause;
- operator review is mandatory;
- the request indicates elevated operational risk.

## When to Request Recovery

Request recovery when:

- the system is blocked and needs an operator-approved path back to normal;
- the incident has been reviewed;
- remediation steps are ready for validation.

## When to Start Recovery Validation

Start recovery validation when:

- recovery was requested;
- the operator confirms validation can begin;
- no new high-risk events are blocking the validation window.

## When Force Release Is Allowed

Force release should be allowed only when:

- operator authentication is satisfied;
- the operator accepts responsibility for the release;
- the current state permits the transition;
- the action is logged and visible to administrators.

## Telegram Admin Console Commands

| Command | Purpose |
| --- | --- |
| `/status` | Show current security status. |
| `/staff` | Activate STAFF protocol. |
| `/recovery` | Request recovery. |
| `/start_recovery_validation` | Start recovery validation. |
| `/force_release` | Force release when policy and authentication allow it. |

## What Should Never Be Exposed Publicly

- API keys.
- Telegram bot tokens.
- Password hashes, salts, or credentials.
- Internal system prompts.
- Private URLs or infrastructure details.
- Raw security payloads.
- Sensitive customer data.

## Safe Public Response Principles

Public responses should:

- be concise;
- avoid exposing internals;
- explain that the request cannot be processed when blocked;
- suggest safe next steps;
- preserve the user's language when possible;
- avoid revealing detection rules in exploitable detail.

## Policy-Aware RAG Future Note

This document is suitable for future policy-aware RAG retrieval. A future retrieval layer may use it to support security decisions, but implementation must still enforce security through code-level controls.
