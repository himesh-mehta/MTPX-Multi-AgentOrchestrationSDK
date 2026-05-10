"""
🍳 MTP Cookbook — Recipe 01: Hello World Agent
===============================================
The simplest way to get started with MTP.

What you'll learn:
- Loading your API keys from a .env file
- Setting up a ToolRegistry
- Initializing a provider (OpenRouter)
- Creating your first MTPAgent
- Running a basic prompt and printing the response

Prerequisites:
    pip install mtp python-dotenv

Setup:
    Create a .env file in your project root:
        OPENROUTER_API_KEY=your_key_here

Run:
    python cookbook/00_quickstart/01_hello_world_agent.py
"""

from mtp import Agent
from mtp.providers import OpenRouter

# ---------------------------------------------------------------------------
# Step 1: Load API keys from your .env file
# ---------------------------------------------------------------------------
# MTP looks for provider keys automatically (e.g. OPENROUTER_API_KEY).
# Make sure your .env file exists before running.
Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 2: Set up a Tool Registry
# ---------------------------------------------------------------------------
# The ToolRegistry holds all tools your agent can call.
# In this basic example we leave it empty — the agent will rely on
# its language model alone, with no external tools.
tools = Agent.ToolRegistry()

# ---------------------------------------------------------------------------
# Step 3: Choose a provider and model
# ---------------------------------------------------------------------------
# We use OpenRouter with a free model — no credit card needed!
# Swap the model string for any model available on openrouter.ai/models
provider = OpenRouter(model="inclusionai/ring-2.6-1t:free")

# ---------------------------------------------------------------------------
# Step 4: Create your agent
# ---------------------------------------------------------------------------
# MTPAgent is the core object in MTP. It connects the provider (brain)
# to the tools (hands) and manages the conversation loop.
agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
)

# ---------------------------------------------------------------------------
# Step 5: Run the agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 50)
    print("  MTP Cookbook — 01: Hello World Agent")
    print("=" * 50)

    # agent.run() sends a prompt and returns a response object.
    response = agent.run("Hello! Who are you?")

    print(f"\nAgent: {response}")

    print("\n" + "=" * 50)
    print("✅ Done! Next: see 02_custom_tool.py")
    print("=" * 50)


if __name__ == "__main__":
    main()


# =============================================================================
# 📤 Expected Output:
# =============================================================================
"""
==================================================
  MTP Cookbook — 01: Hello World Agent
==================================================

Agent: Hello! I'm an AI assistant powered by the MTP (Model-Tool Protocol)
framework. I'm here to help you with questions, tasks, research, and more.
How can I assist you today?

==================================================
✅ Done! Next: see 02_custom_tool.py
==================================================
"""
