# Sentrya Ops V2 - Security Architecture

Sentrya Ops V2 is an agentic AI operations system designed with layered operational security.

The goal of this architecture is not only to process user requests with AI, but also to protect the system against unsafe inputs, abuse attempts, unauthorized operation, unsafe execution after incidents, and unsafe recovery after security events.

---

## 1. Security Overview

The Sentrya Ops V2 security architecture is based on defense in depth.

The system currently includes:

- Security Gate
- Operator Auth Gate
- Language Router
- Security State Machine
- Security State Integration
- Lockdown Guard
- Security Admin Command Layer
- Telegram Admin Console
- Recovery and Release Flow
- Automated Security Test Suite

The current validated test suite contains:

```text
72 automated tests OK
```

These tests validate input security, runtime state transitions, lockdown behavior, admin commands, recovery flow, Telegram administration, and language routing.

---

## 2. High-Level Security Flow

```text
Operator starts the system
        ↓
Operator Auth Gate
        ↓
Telegram Bot starts
        ↓
User message received
        ↓
Allowed Chat ID check
        ↓
Language Router
        ↓
Security Gate
        ↓
Security State Manager
        ↓
Lockdown Guard
        ↓
Sentrya Agent / LangGraph / LLM
        ↓
Safe response
```

If a malicious or unsafe input is detected:

```text
Unsafe input detected
        ↓
Security Gate blocks request
        ↓
Security event is recorded
        ↓
Security State Machine updates state
        ↓
HIGH / CRITICAL events activate LOCKDOWN
        ↓
Operational execution is blocked
        ↓
Operator manages recovery through Telegram Admin Console
```

---

## 3. Operator Auth Gate

The Operator Auth Gate protects system activation and administrative actions.

It is implemented in:

```text
src/auth.py
```

The system uses a simple centralized operator model:

```text
Login + password
```

The same Operator Auth credentials are used for:

- starting Sentrya Ops V2 from terminal / VS Code
- starting the Telegram Bot
- future Dashboarder login
- authorizing recovery and force release after incidents

The password is not stored in plain text.

The `.env` file stores:

```env
SENTRYA_OPERATOR_AUTH_ENABLED=true
SENTRYA_OPERATOR_USERNAME=your_operator_username
SENTRYA_OPERATOR_PASSWORD_SALT=your_generated_password_salt
SENTRYA_OPERATOR_PASSWORD_HASH=your_generated_password_hash
SENTRYA_OPERATOR_PASSWORD_ITERATIONS=310000
```

The `.env.example` file must contain only placeholders.

The real `.env` file must never be committed to GitHub.

---

## 4. Security Gate

The Security Gate validates external input before it reaches:

- LangGraph
- LLMs
- tools
- APIs
- downstream automation

It is implemented in:

```text
src/security.py
```

The Security Gate validates and blocks multiple classes of threats, including:

- prompt injection
- SQL injection
- command injection
- Windows command payloads
- Linux shell command payloads
- sensitive file access attempts
- internal URL / SSRF attempts
- HTML / script injection
- template injection
- suspicious Base64 payloads
- suspicious hex payloads
- XML / XXE payloads
- LDAP injection
- NoSQL injection
- output schema manipulation
- excessive input size
- excessive repetition
- unsafe secrets in input
- rate limit abuse

If unsafe input is detected, the system returns a public-safe response without exposing:

- internal flags
- raw malicious payloads
- hashes
- secrets
- sensitive metadata
- `.env` values
- API keys
- tokens

Example blocked input:

```text
DROP TABLE users;
```

Expected behavior:

```text
status: blocked
intent: security_block
selected_route: security
model_used: security_guardrails
requires_human_review: true
```

---

## 5. Language Router

The Language Router detects whether the user wrote in Portuguese or English.

It is implemented in:

```text
src/language_router.py
```

The Language Router supports:

- Portuguese input detection
- English input detection
- localized public security responses
- localized lockdown responses
- language instruction injection into the agent input
- `detected_language` in the final result

Expected behavior:

```text
Portuguese input → Portuguese response
English input    → English response
```

Validated example:

```text
Input:
I want to automate my customer support and integrate it with my CRM.

Output:
English labels, English recommended_action, English final_response.
```

This prevents the agent from defaulting to Portuguese when the user writes in English.

---

## 6. Security State Machine

The Security State Machine controls the operational security state of the system.

It is implemented in:

```text
src/security_state.py
```

The official states are:

```text
NORMAL
WATCH
LOCKDOWN
STAFF_ACTIVE
RECOVERY_PENDING
RECOVERY_VALIDATION
RELEASED_MONITORING
```

### NORMAL

The system is operating normally.

```text
Agent active
Telegram active
Security Gate active
LangGraph active
LLMs active
Operational requests allowed
```

### WATCH

The system detected suspicious activity but has not entered lockdown.

```text
Monitoring increased
Agent remains active
Events are recorded
Operator can review status
```

### LOCKDOWN

The system detected a high or critical security event.

```text
Operational execution blocked
Agent execution blocked
Tools protected
Operator review required
Recovery required
```

### STAFF_ACTIVE

The reinforced incident handling mode is active.

```text
STAFF protocol active
Lockdown remains active
Recovery can be requested
Operator can force release
```

### RECOVERY_PENDING

The operator requested recovery.

```text
System remains locked
Recovery not yet validated
STAFF remains active
```

### RECOVERY_VALIDATION

The recovery validation window is active.

```text
System waits for a safe validation period
New high/critical event blocks release
Normal release requires validation completion
```

### RELEASED_MONITORING

The system has been released but remains under reinforced monitoring.

```text
Operational execution allowed
Lockdown inactive
STAFF still monitoring
New high/critical event can trigger lockdown again
```

---

## 7. Security State Integration

Security State Integration connects the real Security Gate to the Security State Machine.

It is implemented in:

```text
src/security_state_integration.py
```

When the Security Gate blocks a request:

```text
Blocked input
        ↓
Security event created
        ↓
Event written to data/security_events.jsonl
        ↓
State written to data/security_state.json
        ↓
HIGH / CRITICAL event activates LOCKDOWN
```

Generated runtime files:

```text
data/security_state.json
data/security_events.jsonl
```

These files are runtime operational artifacts and must not be committed to GitHub.

They are ignored in `.gitignore`.

---

## 8. Lockdown Guard

The Lockdown Guard prevents normal operational execution when the system is in a blocking security state.

It is implemented in:

```text
src/lockdown_guard.py
```

Blocking states:

```text
LOCKDOWN
STAFF_ACTIVE
RECOVERY_PENDING
RECOVERY_VALIDATION
```

Allowed states:

```text
NORMAL
RELEASED_MONITORING
```

Validated behavior:

```text
System state: LOCKDOWN
User sends normal request
        ↓
Agent does not execute
        ↓
Response: system_lockdown
```

Expected response:

```text
status: blocked
intent: system_lockdown
selected_route: security
model_used: security_state_manager
```

This ensures that the system does not continue operating normally after a critical security event.

---

## 9. Security Admin Command Layer

The Security Admin Command Layer centralizes administrative security commands.

It is implemented in:

```text
src/security_admin.py
```

Supported commands:

```text
status
snapshot
allowed_actions
activate_lockdown
activate_staff
request_recovery
start_recovery_validation
release_after_validation
force_release
complete_monitoring
```

Read-only commands do not require additional operator authentication:

```text
status
snapshot
allowed_actions
```

State-changing commands require Operator Auth or an already authenticated operator session:

```text
activate_lockdown
activate_staff
request_recovery
start_recovery_validation
release_after_validation
force_release
complete_monitoring
```

The command layer is designed to be reused by:

- Telegram Admin Console
- future Dashboarder
- future local control panel
- future API admin routes

---

## 10. Telegram Admin Console

The Telegram Admin Console allows the operator to control security states through Telegram.

It is implemented in:

```text
src/telegram_bot_agent.py
```

Validated Telegram commands:

```text
/status
/security
/actions
/lockdown
/staff
/recovery
/start_recovery_validation
/force_release
/complete_monitoring
```

Validated incident flow:

```text
LOCKDOWN
    ↓ /staff
STAFF_ACTIVE
    ↓ /recovery
RECOVERY_PENDING
    ↓ /start_recovery_validation
RECOVERY_VALIDATION
    ↓ /force_release
RELEASED_MONITORING
    ↓ normal message
Agent execution allowed
```

The Telegram Admin Console is restricted by:

- Operator Auth at bot startup
- allowed Telegram chat ID
- centralized Security Admin Command Layer

---

## 11. Recovery and Release Flow

Sentrya Ops V2 supports two recovery paths.

### Normal Recovery

```text
Operator requests recovery
        ↓
System enters RECOVERY_PENDING
        ↓
Operator starts recovery validation
        ↓
System enters RECOVERY_VALIDATION
        ↓
Validation window must complete without new HIGH / CRITICAL threats
        ↓
System can be released
        ↓
System enters RELEASED_MONITORING
```

### Force Release

```text
Operator requests force release
        ↓
Operator Auth must be valid
        ↓
System exits lockdown immediately
        ↓
System enters RELEASED_MONITORING
```

Force release is intended for administrative or emergency recovery.

---

## 12. Runtime Security Files

The system can generate runtime security files:

```text
data/security_state.json
data/security_events.jsonl
```

These files are useful for:

- local monitoring
- incident analysis
- Telegram Admin Console
- future Dashboarder
- future security metrics

They must not be committed to GitHub.

Recommended `.gitignore` entries:

```gitignore
data/security_state.json
data/security_events.jsonl
```

---

## 13. Automated Test Coverage

Current validated test suite:

```text
72 tests OK
```

Test groups:

```text
30 tests - Security Gate
16 tests - Security State Machine
7 tests  - Lockdown Guard
12 tests - Security Admin Command Layer
7 tests  - Language Router
```

### Security Gate Tests

Validate input-level protection:

- malicious input blocking
- prompt injection detection
- SQL injection detection
- command injection detection
- encoded payload detection
- sensitive data redaction
- schema manipulation blocking
- safe public response

### Security State Machine Tests

Validate operational security state transitions:

- NORMAL
- WATCH
- LOCKDOWN
- STAFF_ACTIVE
- RECOVERY_PENDING
- RECOVERY_VALIDATION
- RELEASED_MONITORING

### Lockdown Guard Tests

Validate that operational execution is blocked during unsafe system states.

### Security Admin Tests

Validate administrative command behavior and Operator Auth requirements.

### Language Router Tests

Validate Portuguese / English detection and localized responses.

---

## 14. Security Design Principles

Sentrya Ops V2 follows these security principles:

```text
Validate before execution
Block before LLM
Do not expose internal security metadata
Do not expose raw malicious payloads
Do not expose secrets
Centralize operator authentication
Record security events
Use explicit runtime state
Block operation during incidents
Require controlled recovery
Keep dashboard data public-safe
```

---

## 15. Dashboarder Readiness

The future Dashboarder should not invent security states.

It should read from the existing security architecture:

```text
src/security_state.py
data/security_state.json
data/security_events.jsonl
src/security_admin.py
```

The future Dashboarder should display:

- current security state
- lockdown status
- STAFF status
- last incident
- event counters
- high / critical event count
- recovery state
- allowed admin actions
- Telegram Bot status
- LangSmith / LLM metrics
- security timeline

The Dashboarder must not expose:

- raw malicious payloads
- real API keys
- Telegram Bot token
- Operator Auth password hash
- Operator Auth salt
- `.env` values
- private LangSmith credentials
- private Langflow credentials

---

## 16. Current Validated Status

Current validated architecture:

```text
Operator Auth Gate: validated
Security Gate: validated
Language Router: validated
Security State Machine: validated
Security State Integration: validated
Lockdown Guard: validated
Security Admin Command Layer: validated
Telegram Admin Console: validated
Automated test suite: 72 tests OK
```

Current validated behavior:

```text
Malicious input is blocked before LLM execution.
High-risk input triggers LOCKDOWN.
Normal requests are blocked while in LOCKDOWN.
Operator can activate STAFF.
Operator can request recovery.
Operator can start recovery validation.
Operator can force release.
Normal requests work again after RELEASED_MONITORING.
Portuguese input receives Portuguese response.
English input receives English response.
```

---

## 17. Summary

Sentrya Ops V2 is not only an AI agent.

It is an agentic AI operations system with:

```text
input protection
operator authentication
runtime state control
lockdown behavior
admin command control
recovery flow
language-aware response handling
automated security validation
```

This architecture prepares the system for a future professional Dashboarder / Security Command Center.
