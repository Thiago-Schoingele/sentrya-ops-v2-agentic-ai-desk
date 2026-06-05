# LangGraph Studio Setup for Sentrya Ops V2

## Overview

Sentrya Ops V2 supports local graph debugging through LangGraph CLI and Studio.

LangGraph CLI is used to start the local development Agent Server. Studio connects to that Agent Server to visualize, interact with, and debug the graph. LangSmith remains the observability, tracing, debugging, evaluation, and prompt engineering layer for normal agent and LLM executions.

This setup is for local development and debugging only.

## Why Studio Uses a Dedicated Adapter

Studio must not be pointed directly to `run_sentrya_agent()`.

`run_sentrya_agent()` is the public runtime wrapper. It applies production-facing layers such as:

- Security Gate;
- Lockdown Guard;
- Language Router;
- safe public response shaping;
- security state control;
- actor-aware rate limiting when enabled.

For Studio, the project exposes a dedicated adapter:

```text
src/sentrya_graph_studio.py
```

The adapter exports the compiled LangGraph graph as:

```text
agent
```

This keeps the production-safe runtime entrypoint unchanged while allowing local graph visualization and debugging.

## LangGraph CLI, Studio, and LangSmith

| Tool | Purpose in this project |
| --- | --- |
| LangGraph CLI | Runs the local development Agent Server. |
| Studio | Connects to the local Agent Server for graph visualization and interaction. |
| LangSmith | Provides tracing, observability, debugging, evaluation, and prompt engineering support. |

## Configuration

The root `langgraph.json` file points to the dedicated Studio adapter:

```json
{
  "dependencies": ["."],
  "graphs": {
    "sentrya_ops": "./src/sentrya_graph_studio.py:agent"
  },
  "env": ".env"
}
```

Do not change this target to `run_sentrya_agent()`.

## Install LangGraph CLI

Install the local development CLI support:

```powershell
pip install --upgrade "langgraph-cli[inmem]"
```

Verify the CLI is available:

```powershell
langgraph --help
```

On Windows terminals, if the help command fails with a console encoding error, run it with UTF-8 enabled:

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
langgraph --help
```

## Environment Variables

The local Agent Server reads `.env` through `langgraph.json`.

Required local values depend on the graph path being debugged, but the project commonly uses:

- `GROQ_API_KEY`
- `GROQ_MODEL_AGENT`
- `GROQ_MODEL_FAST`
- `GROQ_MODEL_REASONING`
- `GROQ_MODEL_GENERAL`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `LANGSMITH_TRACING`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_ALLOWED_CHAT_ID`

Keep `.env` local and uncommitted. Use `.env.example` only for placeholders.

Do not put secrets in:

- `langgraph.json`;
- documentation files;
- GitHub Actions workflow files;
- tests;
- source code.

## Run the Local Agent Server

From the project root:

```powershell
langgraph dev
```

`langgraph dev` starts a local development Agent Server and provides a Studio URL.

Open the Studio URL printed by the CLI to inspect and interact with the `sentrya_ops` graph.

## Connecting Studio with Localhost

The default local Agent Server URL is usually:

```text
http://127.0.0.1:2024
```

The generated Studio URL usually looks like:

```text
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

Use this local URL first. If Studio cannot fetch the local server, try replacing `127.0.0.1` with `localhost`:

```text
https://smith.langchain.com/studio/?baseUrl=http://localhost:2024
```

If PowerShell can call the local API but the hosted Studio UI shows `TypeError: Failed to fetch`, the issue is usually browser or hosted-Studio access to localhost, not the Sentrya Ops graph.

## Connecting Studio with Tunnel Mode

If a browser, extension, VPN, proxy, or network policy blocks the hosted Studio page from fetching the local Agent Server, use tunnel mode:

```powershell
langgraph dev --tunnel
```

`--tunnel` creates a temporary Cloudflare tunnel URL, usually under:

```text
https://<temporary-domain>.trycloudflare.com
```

The tunnel domain may be blocked by Studio until it is manually added to Studio Allowed Origins / allowed domains. This is a Studio/browser security requirement, not a Sentrya Ops code issue.

### Tunnel Connection Steps

1. Start the local Agent Server with tunnel mode:

```powershell
langgraph dev --tunnel
```

2. Copy the generated tunnel URL from the terminal.
3. Open Studio.
4. Click `Configure connection` or `Connect to local server`.
5. Paste the tunnel URL as the base URL.
6. Open `Advanced Settings`.
7. Add the generated tunnel domain to `Allowed Origins` / allowed domains.
8. Click Connect.

The Cloudflare tunnel domain changes when the server is restarted. If a new domain is generated, add the new domain to Allowed Origins again.

## Cloudflare Tunnel Behavior and DNS Troubleshooting

`langgraph dev --tunnel` is a local development/debug workaround. It is not a production deployment method and does not permanently link Cloudflare to Sentrya Ops V2.

Quick tunnel behavior:

- It does not require creating a Cloudflare account for quick local testing.
- It generates a temporary random `trycloudflare.com` domain.
- The generated domain works only while the `langgraph dev --tunnel` terminal remains running.
- If the terminal is stopped, the tunnel URL expires.
- If the command is restarted, a new tunnel URL may be generated.
- Studio must use the current generated tunnel URL as the base URL.
- The generated domain must be added to Studio `Allowed Origins` / allowed domains.
- If the generated domain changes, Studio `Allowed Origins` may need to be updated again.

If DNS fails with `Could not resolve host`, `remote name could not be resolved`, or `DNS_ERROR_RCODE_NAME_ERROR`, this is a local DNS/network resolution issue. It is not a Sentrya Ops code issue, and it should not be solved by changing the graph, `langgraph.json`, or `run_sentrya_agent()`.

### Recommended Tunnel Validation Flow

In the first PowerShell terminal:

```powershell
cd C:\Projetos\sentrya-ops-v2-agentic-ai-desk
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8="1"
langgraph dev --tunnel
```

Keep this terminal open while testing.

In another PowerShell terminal, replace `<generated-domain>` with the current domain printed by `langgraph dev --tunnel`:

```powershell
Resolve-DnsName <generated-domain>.trycloudflare.com
Resolve-DnsName <generated-domain>.trycloudflare.com -Server 1.1.1.1
Resolve-DnsName <generated-domain>.trycloudflare.com -Server 8.8.8.8
curl.exe -v https://<generated-domain>.trycloudflare.com/docs
```

Then test the assistant registry endpoint:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://<generated-domain>.trycloudflare.com/assistants/search `
  -ContentType "application/json" `
  -Body "{}"
```

Expected result:

```text
graph_id: sentrya_ops
name: sentrya_ops
```

### DNS Troubleshooting Guidance

- If explicit DNS servers `1.1.1.1` or `8.8.8.8` resolve the domain but default DNS does not, the issue is local Windows/network DNS.
- `curl.exe` and `Invoke-RestMethod` use the default Windows resolver, so they may fail even when public DNS works.
- Studio/browser may also fail if the browser relies on the same broken DNS resolver.
- This is not a Sentrya Ops code problem.
- Try opening PowerShell as Administrator before changing DNS settings.
- Change DNS manually in Windows network adapter settings if policy allows it.
- Use Cloudflare DNS `1.1.1.1` / `1.0.0.1` or Google DNS `8.8.8.8` / `8.8.4.4`.
- Enable Secure DNS in Chrome or Edge using Cloudflare or Google.
- Confirm the active network adapter:

```powershell
Get-NetAdapter | Where-Object Status -eq "Up" | Select-Object Name, InterfaceDescription
```

- If DNS changes fail with `PermissionDenied` or CIM errors, this is a Windows permission or network policy issue.
- Try another network.
- Temporarily disable VPN or proxy software.
- Temporarily disable browser security extensions that affect network requests.
- Test another browser or browser profile.
- If the tunnel URL does not resolve even with `1.1.1.1` and `8.8.8.8`, stop the tunnel and generate a new one.
- Always keep the `langgraph dev --tunnel` terminal open while testing.

### Optional Local Diagnostic Script

This repository includes a safe diagnostic helper:

```powershell
.\scripts\check_langgraph_tunnel.ps1 -TunnelUrl https://<generated-domain>.trycloudflare.com
```

The script checks DNS resolution and local tunnel API reachability. It does not change DNS settings, does not require administrator privileges, does not start or stop LangGraph, and does not modify project files.

When default DNS fails but public DNS works, the script also runs diagnostic-only `curl.exe --resolve` checks. This can confirm whether the tunnel/API is reachable when DNS is forced for curl. It does not fix Studio/browser DNS resolution and must not be used as a production path.

## Test the Graph Locally

Use Studio for interactive graph inspection and local test inputs.

For automated validation, prefer offline-safe unit tests:

```powershell
python -m unittest discover tests
```

Do not use live Telegram, production webhooks, or deployment-only integrations as part of Studio smoke checks.

## Local API Smoke Checks

While `langgraph dev` is running, the local API should respond from PowerShell:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:2024/assistants/search `
  -ContentType "application/json" `
  -Body "{}"
```

The result should include an assistant with:

```text
graph_id: sentrya_ops
name: sentrya_ops
created_by: system
version: 1
```

The API docs should also open at:

```text
http://127.0.0.1:2024/docs
```

## Troubleshooting Studio: Failed to Fetch

If the local API works from PowerShell but Studio shows `TypeError: Failed to fetch` or `TypeError: Falha ao buscar`, the problem is usually browser, localhost, CORS, private-network access, cache, extension, VPN, or proxy related rather than an empty graph.

Validated project-side checks:

- `langgraph.json` points to `./src/sentrya_graph_studio.py:agent`.
- The Studio adapter exports a real `CompiledStateGraph`.
- The graph contains the expected nodes: `classify_input` and `generate_structured_response`.
- `langgraph validate` reports the configuration as valid.

Recommended steps:

1. Use the exact Studio URL printed by `langgraph dev`.
2. Try `http://localhost:2024` instead of `http://127.0.0.1:2024` in the Studio `baseUrl`.
3. Try the generated URL with `127.0.0.1` if `localhost` fails.
4. Open Studio in an incognito/private browser window.
5. Temporarily disable browser extensions that affect requests, privacy, CORS, VPN, proxy, or ad blocking.
6. Clear any saved Studio connection settings and reconnect.
7. Open browser DevTools and inspect the Network tab for the failing request.
8. Try another browser.
9. If browser/private-network restrictions continue, run:

```powershell
langgraph dev --tunnel
```

10. Copy the generated `trycloudflare.com` tunnel URL.
11. Add the generated tunnel domain to Studio `Advanced Settings` under `Allowed Origins` / allowed domains.
12. Reconnect using the tunnel URL.

Do not solve this by changing `langgraph.json` to target `run_sentrya_agent()`. That wrapper is the production/public runtime path and must remain separate from Studio graph debugging.

## Final Validation Checklist

- [ ] `python -m unittest discover tests` passes.
- [ ] `langgraph validate` passes.
- [ ] `langgraph dev` starts the local Agent Server.
- [ ] `POST /assistants/search` returns `sentrya_ops`.
- [ ] Studio opens with either the local URL or tunnel URL.
- [ ] If tunnel mode is used, the generated tunnel domain is added to Allowed Origins.
- [ ] `git status --short` does not show `.env`, `.venv`, `.langgraph_api`, runtime state files, or generated cache files.

## Development Safety Notes

- The Studio adapter is development/debug-only.
- Production runtime should continue to use `run_sentrya_agent()`.
- Telegram integration should continue to use the existing bot flow.
- Do not commit `.env`, `.venv`, `.langgraph_api`, runtime state files, traces, or generated caches.
- Do not expose API keys, Telegram tokens, password hashes, salts, or production URLs.
- Studio graph loading may require local placeholder or real development credentials, depending on the graph path being tested.

## Current Graph Target

```text
./src/sentrya_graph_studio.py:agent
```

This target exposes the compiled LangGraph graph for local Studio debugging while preserving the existing public runtime wrapper.
