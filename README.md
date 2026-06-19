# MTPX: Multi-Agent Orchestration SDK

[![PyPI version](https://badge.fury.io/py/mtpx.svg)](https://pypi.org/project/mtpx/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/Docs-Live-brightgreen)](https://mtp-frontend-zeta.vercel.app/)

MTPX (Model Tool Protocol Extended) is a protocol-first Python library for advanced agent tool orchestration. It is designed to act as a highly extensible runtime engine for agent-to-tool and agent-to-agent workflows.

---

## 🌐 Live Platform & Documentation

The official documentation, guides, and SDK references are hosted on the live platform:
🔗 **[MTPX Live Documentation Portal](https://mtp-frontend-zeta.vercel.app/)**

### 🖼️ Landing Page & Showcase

![MTPX Landing Page Hero](assets/landing_hero.png)

---

## 📖 Deployed Documentation Quick Links

To help you get started quickly, here is a mapping of key sections from the live docs:

| 🧭 Core Concepts | 🛠️ Developer Guides | 🛡️ Safety & Observability |
| :--- | :--- | :--- |
| • [Introduction](https://mtp-frontend-zeta.vercel.app/docs/introduction)<br>• [Planner vs Runtime](https://mtp-frontend-zeta.vercel.app/docs/planner-vs-runtime)<br>• [Execution Flow](https://mtp-frontend-zeta.vercel.app/docs/execution-flow) | • [Quickstart Guide](https://mtp-frontend-zeta.vercel.app/docs/quickstart)<br>• [Installation Details](https://mtp-frontend-zeta.vercel.app/docs/installation)<br>• [Custom Providers](https://mtp-frontend-zeta.vercel.app/docs/provider-custom) | • [Risk Policies & Levels](https://mtp-frontend-zeta.vercel.app/docs/safety-risk-levels)<br>• [Approval Gates](https://mtp-frontend-zeta.vercel.app/docs/safety-approval)<br>• [Tool Sandboxing](https://mtp-frontend-zeta.vercel.app/docs/safety-sandboxing) |
| • [DAG Resolution](https://mtp-frontend-zeta.vercel.app/docs/dag-resolution)<br>• [State Persistence](https://mtp-frontend-zeta.vercel.app/docs/state-persistence)<br>• [Event Bus Architecture](https://mtp-frontend-zeta.vercel.app/docs/event-bus) | • [SDK Reference: Agent](https://mtp-frontend-zeta.vercel.app/docs/sdk-agent)<br>• [SDK Reference: Runtime](https://mtp-frontend-zeta.vercel.app/docs/sdk-runtime)<br>• [SDK Reference: Session](https://mtp-frontend-zeta.vercel.app/docs/sdk-session) | • [Event Streaming](https://mtp-frontend-zeta.vercel.app/docs/obs-streaming)<br>• [TUI Monitoring](https://mtp-frontend-zeta.vercel.app/docs/obs-tui)<br>• [Execution Traces](https://mtp-frontend-zeta.vercel.app/docs/obs-traces) |

### 📄 Interactive Docs Portal

![MTPX Documentation Interface](assets/docs_landing.png)

---

## ✨ Features

- **Lazy Tool Loading**: Group and load toolkits dynamically by category or risk profile.
- **Dependency-Aware DAG Engine**: Resolve execution order for complex, multi-tool tasks automatically.
- **Policy-Aware Sandbox Execution**: Fine-grained security permissions (`allow`, `ask`, `deny`) for tool execution.
- **Multi-Round Conversation Loops**: Robust state management for model-tool interactions.
- **Extensible Provider Adapters**: Seamless integrations for OpenAI, Anthropic, Gemini, Groq, Ollama, SambaNova, DeepSeek, and more.
- **Transport Primitives**: Stdio, HTTP, and WebSocket transport envelopes.

---

## 🚀 Quickstart

### 1. Installation

Install via PyPI:
```bash
pip install mtpx
```

Or install with specific provider dependencies:
```bash
# OpenAI + Anthropic + dotenv support
pip install "mtpx[openai,anthropic,dotenv]"

# Local model providers (Ollama / LM Studio)
pip install "mtpx[ollama,lmstudio]"

# Groq support
pip install "mtpx[groq,dotenv]"

# Install everything
pip install "mtpx[all]"
```

Verify your installation:
```bash
python -c "import mtp; print(f'MTPX version {mtp.__version__} successfully installed!')"
```

### 2. Basic Usage (Groq example)

Create a file named `run_agent.py` and run:

```python
from mtp import Agent
from mtp.providers import Groq
from mtp.toolkits import CalculatorToolkit, FileToolkit

Agent.load_dotenv_if_available()

# Set up tool registry
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("calculator", CalculatorToolkit())
tools.register_toolkit_loader("file", FileToolkit(base_dir="."))

# Configure LLM provider
provider = Groq(model="llama-3.3-70b-versatile")

# Start Agent loop
agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions="Use tools when appropriate to answer query.",
    debug_mode=True
)

# Run a task
response = agent.run("Calculate 25 * 4 + 10 and list files in current directory.", max_rounds=4)
print(response)
```

---

## 🗄️ Stateful Sessions (Persistence)

Persist conversations out-of-the-box using the built-in database adapters:

```python
from mtp import Agent, JsonSessionStore
from mtp.providers import OpenAI

# Store conversations in a local JSON database
session_store = JsonSessionStore(db_path="tmp/mtp_json_db")
agent = Agent.MTPAgent(
    provider=OpenAI(model="gpt-4o"), 
    tools=tools, 
    session_store=session_store
)

# Run with a session ID
agent.run("Remember this: the secret password is 'Antigravity'.", session_id="session-1", user_id="user-1")
agent.run("What was the password?", session_id="session-1", user_id="user-1")
```

We also support production databases:
```python
from mtp import PostgresSessionStore, MySQLSessionStore

pg_store = PostgresSessionStore(db_url="postgresql://user:pass@localhost:5432/mtp")
mysql_store = MySQLSessionStore(host="localhost", user="root", password="pwd", database="mtp")
```

---

## 🖥️ Running Examples & Interactive TUI

Execute the following examples included in the repository:
```bash
# Simple scripts
python examples/quickstart.py
python examples/groq_agent.py
python examples/lmstudio_agent.py

# Launch the interactive terminal console (TUI)
mtp tui

# Launch the Streamlit Web UI
streamlit run examples/streamlit_groq_agent_chat.py
```

### 🖥️ MTP Interactive Terminal User Interface (TUI)

![MTP Interactive TUI](assets/tui_showcase.png)

---

## 📂 Repository Layout

- `src/mtp/protocol.py`: Standardized protocol entities (`ToolSpec`, `ToolCall`, `ExecutionPlan`).
- `src/mtp/schema.py`: Versioned JSON envelopes and schema verification.
- `src/mtp/policy.py`: Execution security model (`allow` / `ask` / `deny`).
- `src/mtp/runtime.py`: Tool loading registry, cache manager, DAG executor.
- `src/mtp/agent.py`: Principal agent orchestration loop.
- `src/mtp/providers/`: Direct LLM API adapters.
- `src/mtp/toolkits/`: Default tool suites (calculator, file, shell, python execution).
- `docs/`: In-repository documentation files.

For a complete local documentation map, refer to:
- [Quickstart Guide](docs/QUICKSTART.md)
- [Agent API Reference](docs/AGENT_API.md)
- [Storage & Sessions](docs/STORAGE.md)
- [Providers Overview](docs/PROVIDERS.md)
- [Local Inference](docs/LOCAL_INFERENCE.md)
- [Creating Custom Tools](docs/CREATING_TOOLS.md)
- [Architecture Details](docs/ARCHITECTURE.md)

---

## 👥 Contributors

Created by [Prajwal Ghadge](mailto:prajwalghadge2005@gmail.com) with contributions from Himesh Mehta.

Please see [CONTRIBUTORS.md](CONTRIBUTORS.md) for details.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more details.
