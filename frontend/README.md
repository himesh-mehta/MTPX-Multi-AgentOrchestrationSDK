<div align="center">

<img src="assets/mtp-logo.png" alt="MTPX Logo" width="120" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(250, 204, 21, 0.2); border: 2px solid rgba(250, 204, 21, 0.4);"/>

# ⚡ MTPX (Model Tool Protocol)
### Protocol-First Python SDK for AI Agent Tool Orchestration

[![PyPI Version](https://img.shields.io/pypi/v/mtpx?style=flat-square&color=facc15&logo=pypi)](https://pypi.org/project/mtpx/)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-purple?style=flat-square)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-cyan?style=flat-square&logo=json)](https://modelcontextprotocol.io)

> **Models reason. MTP executes.**  
> A deterministic execution runtime for AI agents. By strictly separating planning from action, MTPX makes agentic workflows safe, parallelized, stateful, and observable.

[**Documentation Website**](https://github.com/GodBoii/Model-Tool-protocol-) | [**PyPI Package**](https://pypi.org/project/mtpx/)

<br/>

### 🖥️ Interactive Terminal UI (TUI) Dashboard
<img src="assets/mtp-tui-homepage.png" alt="MTP TUI — Interactive Terminal Interface" style="border-radius: 12px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6); max-width: 100%;" />

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Core Architecture](#-core-architecture)
- [Key Features](#-key-features)
- [Supported Providers](#-supported-providers)
- [Installation](#-installation)
- [Quickstart Guide](#-quickstart-guide)
- [Structured DAG Plans & Dependency Injection](#-structured-dag-plans--dependency-injection)
- [Safety Policies & Human Gates](#-safety-policies--human-gates)
- [Interactive Terminal UI (TUI)](#-interactive-terminal-ui-tui)
- [Model Context Protocol (MCP) Interop](#-model-context-protocol-mcp-interop)
- [License](#-license)

---

## 🧠 Overview

Traditional agent frameworks let Large Language Models directly invoke tools in an ad-hoc loop. This introduces severe non-determinism, execution drift, and security risks. 

**MTPX replaces this with a protocol-first architecture:**
1. The LLM acts purely as a **Planner**, generating a structured Directed Acyclic Graph (DAG) Execution Plan in JSON.
2. The **MTPX Runtime Engine** validates this plan, enforces security constraints, and executes the tools in optimal parallel batches.

This strict separation ensures that destructive tools are never called if the plan contains cycles or syntax errors, while maximizing execution speed through safe concurrency.

---

## 🏗️ Core Architecture

MTPX pipelines agent execution through a modular, secure runtime environment:

```
[ User Query / Objective ]
           │
           ▼
   [ Planner (LLM) ] ───▶ Generates structured JSON Execution Plan (DAG)
           │
           ▼
  [ Plan Validator ] ───▶ Cycle Detection & Parameter Schema Check (Dry-run)
           │
           ▼
  [ Policy Engine ]  ───▶ Evaluates Risk Levels (Allow / Ask / Deny)
           │
           ▼
  [ Runtime Engine ] ───▶ Resolves data dependency $refs & Schedules Parallel Waves
           │
           ▼
   [ Tool Executor ] ───▶ Runs local handlers, isolates execution context
           │
           ▼
   [ Event Stream ]  ───▶ Emits real-time diagnostic logs to Event Bus / TUI
```

---

## ✨ Key Features

- ⛓️ **Structured DAG Plans** — Models plan multiple steps ahead. The MTP runtime resolves step-to-step dependencies using the `$ref` syntax and schedules parallel execution.
- ⚡ **13+ Provider Adapters** — Switch between local or cloud providers (Anthropic, OpenAI, Groq, Gemini, etc.) with zero refactoring. All return the same standardized interface.
- 📦 **Lazy Toolkit Loading** — Load heavy capabilities on-demand by prefix (e.g., `github.*`). Speeds up initial startup and reduces token overhead.
- 🛡️ **Safety Policy Engine** — Tag tools with custom risk profiles (`READ`, `WRITE`, `DESTRUCTIVE`). Restrict dangerous operations with explicit human approval gates.
- 💾 **Session Persistence** — Automatically saves conversation history and tool outputs to `JsonSessionStore`, `PostgresSessionStore`, or `MySQLSessionStore`.
- 🔀 **MCP Interoperability** — Exposes the MTPX Tool Registry directly as a Model Context Protocol (MCP) server, compatible with Claude Desktop and other host applications.
- 🤖 **Autoresearch Mode** — Enables autonomous looping where the agent refines plans and investigates outcomes until `agent.terminate()` is called.

---

## 🔌 Supported Providers

MTPX normalizes model differences behind a unified API layer. Swap them instantly via environment variables or mid-session command triggers:

| Provider | Package Extra | Recommended Model | Focus |
|---|---|---|---|
| **Anthropic** | `mtpx[anthropic]` | `claude-3-5-sonnet` | Complex Reasoning |
| **OpenAI** | `mtpx[openai]` | `gpt-4o` / `o1` | Multi-step Planning |
| **Groq** | `mtpx[groq]` | `llama-3.3-70b-versatile` | Ultra-fast LPU Inference |
| **Gemini** | `mtpx[gemini]` | `gemini-2.0-flash` | Multimodal / Large Context |
| **Mistral** | `mtpx[mistral]` | `mistral-large-latest` | European Sovereign AI |
| **Cohere** | `mtpx[cohere]` | `command-r-plus` | Enterprise Search / RAG |
| **Ollama** | `mtpx[ollama]` | Local (e.g. `llama3`) | 100% Offline Execution |
| **LM Studio** | `mtpx[lmstudio]` | Local | Offline Testing |
| **DeepSeek** | *Built-in* | `deepseek-chat` | Highly Cost-Effective |
| **OpenRouter** | *Built-in* | Any router path | Unified Cloud Routing |
| **Together AI** | *Built-in* | Llama / Mixtral | Open-source API Scale |
| **SambaNova** | *Built-in* | Llama-3.1 | High-speed Open Weights |

---

## 📦 Installation

Install the lightweight core runtime, or choose specific extras based on your stack:

```bash
# Core execution protocol only
pip install mtpx

# Bundle specific LLM providers
pip install "mtpx[openai,groq,anthropic]"

# Standard local development suite
pip install "mtpx[all]"
```

Verify your environment variables and dependency health at any time:
```bash
mtp doctor
```

---

## 🚀 Quickstart Guide

Ensure you have your respective API keys configured (e.g., `GROQ_API_KEY`, `OPENAI_API_KEY`).

### 1. Define custom tools and initialize MTPX
```python
import os
from mtp import Agent, tool
from mtp.providers import Groq
from mtp.toolkits import CalculatorToolkit

# 1. Initialize our reasoning adapter (using Groq for speed)
os.environ["GROQ_API_KEY"] = "gsk_your_api_key_here"
provider = Groq(model="llama-3.3-70b-versatile")

# 2. Decorate python functions as tools with metadata
@tool(risk_level="WRITE")
def save_txt(filename: str, content: str) -> str:
    """
    Saves content into a local file.
    
    Args:
        filename: Name of target file (e.g., report.txt).
        content: The text payload to save.
    """
    with open(filename, "w") as f:
        f.write(content)
    return f"Successfully saved to {filename}"

# 3. Register tools inside namespaces
tools = Agent.ToolRegistry()
tools.register_tool(save_txt)
tools.register_toolkit_loader("math", CalculatorToolkit()) # Standard arithmetic suite

# 4. Bind into an MTPX Agent Control Plane
agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions="Use the registered math tools for sums and save outputs to files."
)

# 5. Run a validated, deterministic pipeline
response = agent.run("Calculate (349 * 12) + 402 and save the text result into results.txt")
print(f"\nFinal Answer:\n{response}")
```

---

## ⛓️ Structured DAG Plans & Dependency Injection

When the agent starts, the planner evaluates the request against available tools and constructs a structured plan. Rather than running tasks sequentially, independent steps are run **concurrently**.

Here is an example plan generated by the LLM:

```json
{
  "batches": [
    {
      "execution_mode": "parallel",
      "calls": [
        {
          "id": "fetch_api_data",
          "name": "network.get",
          "arguments": { "url": "https://api.example.com/status" }
        },
        {
          "id": "read_user_config",
          "name": "fs.read_file",
          "arguments": { "path": "./config.json" }
        }
      ]
    },
    {
      "execution_mode": "sequential",
      "calls": [
        {
          "id": "merge_report",
          "name": "utils.merge",
          "arguments": {
            "api_payload": { "$ref": "fetch_api_data" },
            "config_options": { "$ref": "read_user_config" }
          }
        }
      ]
    }
  ]
}
```
*Notice how **MTPX** automatically feeds the outputs of `fetch_api_data` and `read_user_config` directly into `merge_report` arguments using `$ref` pointers. The developer doesn't write any glue code.*

---

## 🛡️ Safety Policies & Human Gates

Production systems cannot allow autonomous agents unrestricted write access. MTPX lets you assign custom risk levels (`READ`, `WRITE`, `DESTRUCTIVE`) to individual tools and define enforcement policies:

```python
from mtp.policies import StrictPolicy, PolicyAction

class EnterpriseSecurity(StrictPolicy):
    def get_action(self, tool_name: str, risk_level: str) -> PolicyAction:
        if risk_level == "DESTRUCTIVE":
            return PolicyAction.DENY  # Shell execution, delete file, etc.
        elif risk_level == "WRITE":
            return PolicyAction.ASK   # Requires human-in-the-loop (HITL) approval
        return PolicyAction.ALLOW     # Safe to execute without interruption
```

When a tool returns `PolicyAction.ASK`, the execution suspends, serializes the current session, and triggers a prompt or dashboard hook requesting human confirmation before resuming.

---

## 🖥️ Interactive Terminal UI (TUI)

MTPX ships with a premium Terminal dashboard for live agent supervision. Start the terminal with the following:

```bash
mtp tui
```

### Key Capabilities:
- **Hot-Swapping Backends** — Switch LLM providers instantly mid-conversation (e.g., `/backend groq` or `/backend claude`).
- **Context Monitoring** — Real-time progress bar tracking prompt tokens vs total context window limits.
- **Event Bus Visualization** — Live execution visualizer showing DAG resolving, parallel tool calls running, and output stream buffers.
- **Retro Terminal Styling** — Phosphor decay text rendering and a friendly retro-animated cat companion that follows cursor interactions!

---

## 🤝 Model Context Protocol (MCP) Interop

Easily share tools between MTPX and other compatible services. You can run your MTPX Tool Registry as an MCP server with a single command:

```bash
mtp mcp-start --port 8000
```

Add the following config to your Claude Desktop configuration file to interact with MTPX-registered tools directly inside the official Claude app:

```json
{
  "mcpServers": {
    "mtpx-agent-hub": {
      "command": "mtp",
      "args": ["mcp-start", "--stdio"]
    }
  }
}
```

---

## 📄 License

MTPX is open-source software licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ⚡ and ❤️ by the MTPX Team.

</div>
