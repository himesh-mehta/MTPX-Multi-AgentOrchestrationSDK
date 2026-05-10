# The Agent Quickstart: Guided Cookbooks

Learn how to build MTP agents with guided cookbooks. We'll go from a simple basic agent to multi-agent teams and step-based workflows through clean, runnable examples.

Each example can be run independently and contains detailed comments to help you understand what's happening under the hood. We'll use OpenRouter (`openai/gpt-oss-120b:free`) by default — it's fast, free, and excellent at tool calling, but you can swap in any model with a one-line change.

## What You'll Build

| # | File | What You'll Learn | Key Features |
| --- | --- | --- | --- |
| 01 | `agent_with_tools.py` | Give an agent tools to fetch real-time data | Tool Calling, Data Fetching |
| 02 | `agent_with_structured_output.py` | Return typed Pydantic objects | Structured Output, Type Safety |
| 03 | `agent_with_typed_input_output.py` | Full type safety on input and output | Input Schema, Output Schema |
| 04 | `agent_with_storage.py` | Persist conversations across runs | Persistent Storage, Session Management |
| 05 | `agent_with_memory.py` | Remember user preferences across sessions | Memory Manager, Personalization |
| 06 | `agent_with_state_management.py` | Track, modify, and persist structured state | Session State, State Management |
| 07 | `agent_search_over_knowledge.py` | Load documents into a knowledge base and search with hybrid search | Chunking, Embedding, Hybrid Search, Agentic Retrieval |
| 08 | `custom_tool_for_self_learning.py` | How to write your own tools and add self-learning capabilities | Custom Tools, Self-Learning |
| 09 | `agent_with_guardrails.py` | Add input validation and safety checks | Guardrails, PII Detection, Prompt Injection |
| 10 | `human_in_the_loop.py` | Require user confirmation before executing tools | Human in the Loop, Tool Confirmation |
| 11 | `multi_agent_team.py` | Coordinate multiple agents by organizing them into a team | Multi-Agent Team, Dynamic Collaboration |
| 12 | `sequential_workflow.py` | Sequentially execute agents/teams/functions | Agentic Workflow, Pipelines |

## Key Concepts

| Concept | What It Does | When to Use |
| --- | --- | --- |
| **Tools** | Let agents take actions | Fetch data, call APIs, run code |
| **Storage** | Persist conversation history | Multi-turn conversations and state management |
| **Knowledge** | Searchable document store | RAG, documentation Q&A |
| **Memory** | Remember user preferences | Personalization |
| **State** | Structured data the agent manages | Tracking progress, managing lists |
| **Teams** | Multiple agents collaborating | Dynamic collaboration of specialized agents |
| **Workflows** | Sequential agent pipelines | Predictable multi-step processes and data flow |
| **Human in the Loop** | Require confirmation for actions | Sensitive operations, safety-critical tools |

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/Model-Tool-Protocol.git
cd Model-Tool-Protocol
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -e .
```

### 4. Set your API key
Create a `.env` file in the root directory and add:
```bash
OPENROUTER_API_KEY=your-openrouter-key
```

### 5. Run any cookbook
```bash
python cookbook/quickstart/basic_agent.py
```

**That's it.** No Docker, no heavy infrastructure — just pure Python.

## Swap Models Anytime

MTP is model-agnostic. Same code, different provider:

```python
# OpenRouter (default in these examples)
from mtp.providers import OpenRouter
provider = OpenRouter(model="openai/gpt-oss-120b:free")

# OpenAI
from mtp.providers import OpenAIProvider
provider = OpenAIProvider(model="gpt-4o")

# Anthropic
from mtp.providers import AnthropicProvider
provider = AnthropicProvider(model="claude-3-5-sonnet")
```

## Run Cookbooks Individually

```bash
# 01 - Basics: Hello World Agent
python cookbook/quickstart/basic_agent.py

# 02 - Instructions: Custom Personas
python cookbook/quickstart/agent_with_instructions.py

# 03 - Tools: Custom Tool Calling
python cookbook/quickstart/agent_with_tools.py

# 04 - Multiple Tools: Combining Toolkits
python cookbook/quickstart/agent_with_multiple_tools.py

# ... run others as you explore them!
```

## Async Patterns

All examples in this Quick Start use synchronous code for simplicity. For async/await patterns (recommended for production), see other modules like `cookbook/workflows` or check the core API.

## Learn More

- [MTP Documentation](../docs/MTP_SDK_API.md)
