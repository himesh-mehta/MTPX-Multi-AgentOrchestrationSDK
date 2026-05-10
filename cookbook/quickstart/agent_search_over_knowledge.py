"""
🍳 MTP Cookbook — Agentic Search over Knowledge
============================================================
This example shows how to give an agent a searchable knowledge base.
The agent can search through documents (PDFs, text, URLs) to answer questions.

Key concepts:
- Knowledge: A searchable collection of documents
- Agentic search: The agent decides when to search the knowledge base
- RAG: Retrieval-Augmented Generation

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_search_over_knowledge.py
"""

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Simple Knowledge Base Implementation (Mock)
# ---------------------------------------------------------------------------
# In a real app, this would use ChromaDB or another VectorDB.
class SimpleKnowledgeBase:
    def __init__(self, name: str):
        self.name = name
        self.documents = {}

    def insert(self, name: str, content: str):
        self.documents[name] = content
        print(f"[*] Loaded document: '{name}' into {self.name}")

    def get_search_tool(self):
        @mtp_tool(description=f"Search the {self.name} for information.")
        def search_knowledge_base(query: str) -> str:
            # Simple keyword matching mock for demonstration
            query = query.lower()
            results = []
            for doc_name, text in self.documents.items():
                if query in text.lower() or any(word in text.lower() for word in query.split()):
                    # Return a snippet
                    results.append(f"--- Document: {doc_name} ---\n{text[:500]}...")
            
            if not results:
                return f"No results found for '{query}'."
            return "\n\n".join(results)
            
        return search_knowledge_base

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
knowledge = SimpleKnowledgeBase(name="MTP Documentation")

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are an expert on the MTP framework and building AI agents.

## Workflow

1. Search
   - For questions about MTP, always search your knowledge base first.
   - Extract key concepts from the query to search effectively.

2. Synthesize
   - Combine information from multiple search results.
   - Prioritize official documentation.

3. Present
   - Lead with a direct answer.
   - Keep it practical and actionable.

## Rules
- Always search knowledge before answering MTP questions.
- If the answer isn't in the knowledge base, say so.
- Be concise — developers want answers, not essays.\
"""

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

# We get the search tool from the knowledge base and register it
search_tool = knowledge.get_search_tool()
knowledge_kit = Agent.toolkit_from_functions("knowledge", search_tool)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("knowledge", knowledge_kit)

agent_with_knowledge = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
)

# ---------------------------------------------------------------------------
# Run Agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Agentic Search over Knowledge")
    print("=" * 60)

    # Load simulated documentation
    mtp_intro_doc = (
        "MTP (Model Tool Protocol) is a lightweight Python framework designed to "
        "bridge the gap between Large Language Models and external tools. It provides "
        "a simple @mtp_tool decorator for exposing Python functions to AI models, "
        "a ToolRegistry for managing toolkits, and an MTPAgent class that handles "
        "the complex multi-turn execution and planning layer automatically. "
        "MTP supports persistent sessions, structured inputs/outputs, and works "
        "with multiple providers like OpenRouter, OpenAI, and Anthropic."
    )
    
    knowledge.insert(name="MTP Introduction", content=mtp_intro_doc)
    
    print("\n[User]: What is MTP and what does it support?")
    print("-" * 30)
    
    response = agent_with_knowledge.run("What is MTP and what does it support?")
    print(f"Agent: {response}")

    print("\n" + "=" * 60)
    print("✅ Done! Next: Check out Custom Tools for Self Learning.")
    print("=" * 60)

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Agentic Search over Knowledge
============================================================
[*] Loaded document: 'MTP Introduction' into MTP Documentation

[User]: What is MTP and what does it support?
------------------------------
Agent: MTP (Model Tool Protocol) is a lightweight Python framework designed to connect Large Language Models with external tools. 

**Key Features:**
- **Easy Tool Creation:** Uses an `@mtp_tool` decorator to expose Python functions to AI models.
- **Tool Management:** Provides a `ToolRegistry` for organizing toolkits.
- **Automated Execution:** The `MTPAgent` class handles complex multi-turn execution and planning.

**What it Supports:**
- Persistent sessions (memory).
- Structured inputs and outputs.
- Multiple LLM providers, including OpenRouter, OpenAI, and Anthropic.

============================================================
✅ Done! Next: Check out Custom Tools for Self Learning.
============================================================
"""
