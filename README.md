# Sentrya Ops V2 — Agentic AI Operations Desk

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Workflows-1f2937?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1f2937?style=flat-square)
![LangSmith](https://img.shields.io/badge/LangSmith-Observability-1f2937?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-Dashboard-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-UI-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-85%20passing-2ea44f?style=flat-square)
![Security](https://img.shields.io/badge/Security--focused-Reference%20Architecture-7f1d1d?style=flat-square)

Sentrya Ops V2 is a portfolio-grade agentic AI operations desk built as a reference architecture for secure AI workflow orchestration. It combines LangGraph, LangChain, LangSmith tracing, Groq-hosted LLMs, Telegram operations, runtime security controls, multi-LLM role governance, and a Next.js dashboard UI.

The project models how an internal AI operations command center can route requests across multiple LLM roles while enforcing security boundaries before any LLM execution. It includes a Telegram bot interface, an admin console, a security state machine, recovery and release workflows, bilingual response handling, and a dashboard for operational visibility.

This repository is not presented as a deployed commercial product. It is a technical portfolio project and reference implementation intended to demonstrate architecture, security thinking, orchestration patterns, and full-stack AI operations design.

Repository: [github.com/Thiago-Schoingele/sentrya-ops-v2-agentic-ai-desk](https://github.com/Thiago-Schoingele/sentrya-ops-v2-agentic-ai-desk)

## Why This Project Exists

AI agents need more than model calls. Practical agentic systems need orchestration, input validation, security boundaries, model role governance, observability, recovery paths, and clear operational interfaces.

Sentrya Ops V2 explores these concerns through a concrete operations desk pattern:

- requests enter through Telegram or local execution paths;
- security checks run before LLM execution;
- runtime lockdown states can block unsafe operations;
- LLMs are assigned strict operational roles;
- traces are observable through LangSmith when configured;
- operators have a dashboard-style view of system activity and controls.

## Core Capabilities

- **Agentic workflow orchestration** with LangGraph-based execution.
- **Security-first execution** through pre-LLM validation and runtime guards.
- **Multi-LLM routing and role governance** through a strict LLM Role Registry.
- **Telegram operations interface** for interacting with the agent and admin commands.
- **Telegram Admin Console** for status, lockdown, STAFF, recovery, and release commands.
- **LangSmith observability** for normal agent and LLM executions when environment variables are configured.
- **Next.js dashboard UI** for KPI cards, charts, LLM monitoring, security state, Telegram status, and activity feeds.
- **Recovery and release flow** with validation and operator-controlled transitions.
- **Language-aware responses** for Portuguese and English user messages.
- **Direct capability answers** for questions such as `Qual a sua habilidade?` and `What can you do?`, without spending LLM calls.

## Architecture

```text
User / Telegram
    ↓
Telegram Bot Interface
    ↓
Security Gate
    ↓
Lockdown Guard / Security State Machine
    ↓
Language Router
    ↓
LangGraph Agent Core
    ↓
Multi-LLM Role Registry
    ↓
Groq LLMs
    ↓
Structured Operational Response
    ↓
LangSmith Tracing + Dashboard Visibility
```

## Multi-LLM Role Registry

Sentrya Ops V2 defines a strict operational role for each LLM. Each model is restricted to its assigned function and must not operate outside the Sentrya Ops V2 scope.

| Role | Model | Operational Function |
| --- | --- | --- |
| FAST MODEL | `llama-3.1-8b-instant` | Fast classification, lightweight triage, preprocessing, simple validation, and low-latency intent detection. |
| AGENT MODEL | `openai/gpt-oss-20b` | Main orchestration, route selection, structured JSON, tool/API/webhook planning, and operational decision-making. |
| REASONING MODEL | `openai/gpt-oss-120b` | Deep analysis, ambiguity resolution, critical review, risk analysis, security-sensitive reasoning, and complex decision support. |
| GENERAL MODEL | `llama-3.3-70b-versatile` | Natural language response, final explanation, synthesis, summary, executive communication, and user-facing answer refinement. |

The Telegram command `/teste_llms` exposes the LLM Role Registry in a readable operational format.

## Security Architecture

Sentrya Ops V2 includes multiple security-oriented layers:

- **Security Gate**: validates input before LLM execution.
- **Prompt injection protection**: blocks attempts to override system behavior or bypass controls.
- **Input validation**: detects unsafe payloads, sensitive file paths, SQL-like attacks, shell commands, SSRF-like URLs, and other suspicious patterns.
- **Lockdown Guard**: blocks operational agent execution when the system is in restricted states.
- **Security State Machine**: tracks states such as `NORMAL`, `WATCH`, `LOCKDOWN`, `STAFF_ACTIVE`, `RECOVERY_PENDING`, `RECOVERY_VALIDATION`, and `RELEASED_MONITORING`.
- **Operator Authentication Gate**: protects sensitive local entrypoints and administrative operations.
- **Recovery validation**: supports controlled release flows after elevated security states.
- **Telegram Admin Console**: exposes authorized operational commands for status, lockdown, STAFF, recovery, validation, and release.

Sensitive credentials and hashes are not stored in the README. They must be configured locally through environment variables.

## Telegram Commands

Telegram commands depend on the authorized chat configuration in `.env`, especially `TELEGRAM_ALLOWED_CHAT_ID`.

| Command | Purpose |
| --- | --- |
| `/teste_llms` | Shows the LLM Role Registry and model responsibilities. |
| `/status` | Shows current security and operations status. |
| `/staff` | Activates the STAFF protocol through the admin console. |
| `/recovery` | Requests the recovery workflow. |
| `/start_recovery_validation` | Starts the recovery validation window. |
| `/force_release` | Forces release when operator authentication and state rules allow it. |

Capability questions are handled directly without calling an LLM:

- `Qual a sua habilidade?`
- `Quais são suas habilidades?`
- `O que você sabe fazer?`
- `What can you do?`
- `What are your capabilities?`

## Dashboard UI

The dashboard is located in [`dashboard/`](dashboard/).

It is built with Next.js, TypeScript, Tailwind CSS, Recharts, and lucide-react. The UI is designed as a dark enterprise Security + AI Operations Command Center.

Dashboard sections include:

- project-level KPI cards;
- LangSmith-style monitoring charts;
- per-LLM monitoring cards;
- Security Command Center;
- Telegram Operations Panel;
- Live Activity Feed;
- sidebar navigation across dashboard sections.

Validated dashboard status:

- `npm run build` passes.
- `npm audit` returned `found 0 vulnerabilities`.

## Repository Structure

```text
.
├── src/
├── tests/
├── docs/
├── data/
├── dashboard/
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Local Setup

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment template and configure local credentials:

```powershell
Copy-Item .env.example .env
```

The `.env.example` file contains placeholders. Do not commit real credentials.

## Environment Variables

Configure the required values locally in `.env`.

| Category | Variables |
| --- | --- |
| Groq | `GROQ_API_KEY` |
| LangSmith / LangChain | `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_ID` |
| Operator authentication | `SENTRYA_OPERATOR_AUTH_ENABLED`, `SENTRYA_OPERATOR_USERNAME`, `SENTRYA_OPERATOR_PASSWORD_SALT`, `SENTRYA_OPERATOR_PASSWORD_HASH`, `SENTRYA_OPERATOR_PASSWORD_ITERATIONS` |

## Running Tests

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Current validated result:

```text
85 tests passing
```

## Running the Telegram Bot

```powershell
python -m src.telegram_bot_agent
```

The Telegram bot requires `.env` configuration, including the bot token and authorized chat id.

## Running the Dashboard

```powershell
cd dashboard
npm install
npm run build
npm run dev
```

Open:

```text
http://localhost:3000
```

## LangSmith Observability

When LangSmith and LangChain environment variables are configured, normal agent and LLM executions create LangSmith traces.

Direct capability answers and `/teste_llms` do not generate LLM traces by design because they do not call an LLM. They are handled through local registry logic to avoid unnecessary model usage.

## Current Project Status

- Portfolio/reference architecture.
- Local validation completed.
- 85 Python tests passing.
- Dashboard build passing.
- `npm audit` returned 0 vulnerabilities.
- LangSmith tracing validated for normal agent execution when environment variables are configured.

## Roadmap

- Add a real RAG pipeline.
- Add Firecrawl ingestion.
- Harden production deployment settings.
- Connect the dashboard to live backend metrics.
- Add persistent event storage.
- Add a CI pipeline.
- Add a Docker deployment profile.

## Disclaimer

This is a portfolio/reference architecture. It should be reviewed, secured, and hardened before any production use.

## Author

Thiago Schoingele

- GitHub: [Thiago-Schoingele](https://github.com/Thiago-Schoingele)
- LinkedIn: [linkedin.com/in/schoingele](https://www.linkedin.com/in/schoingele)
- Email: [thiagoschoingele@gmail.com](mailto:thiagoschoingele@gmail.com)
